*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月21日に生成されました）*

# CommandLineJobRunnerからCommandLineJobOperatorへの移行時におけるv5とv6間の互換性の課題

**Issue番号**: #5227

**状態**: open | **作成者**: fmbenhassine | **作成日**: 2026-01-21

**ラベル**: type: bug, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5227

## 内容


### ディスカッション https://github.com/spring-projects/spring-batch/discussions/5213 より

<div type='discussions-op-text'>

<sup>投稿者: **takahashihrzg** 2025年11月21日</sup>

Spring Batch 6.0.0-M1から、`CommandLineJobRunner`が非推奨となり、`CommandLineJobOperator`が導入されました。
私たちは`CommandLineJobRunner`から`CommandLineJobOperator`への移行を計画しています。

しかし、移行中にいくつかの非互換性を発見し、どのように対処すべきか分かりません。
これらの非互換な変更の理由と、どのように移行すべきかご説明いただけますでしょうか？

1. 必須引数なしでジョブを起動した際のエラー出力先が異なる
2. ジョブ起動時のバリデーション例外がログに記録されない
3. `ExitCodeMapper`や`JobParametersConverter`をカスタマイズできない
4. ジョブの停止や再起動に必要なパラメータが異なる

---

## 1) 必須引数なしでジョブを起動した際のエラー出力先が異なる

`CommandLineJobRunner`では、`jobPath`や`jobIdentifier`などの引数なしでジョブを起動すると、例外は**ログ**に書き込まれていました。

`CommandLineJobOperator`では、`jobPath`や`jobIdentifier`などの引数なしでジョブを起動すると、すべての例外が`CommandLineJobOperator`内部でキャッチされ、`System.err.printf`経由でコンソールにのみ出力されます。

なぜ例外のログ出力（`CommandLineJobRunner`）から標準エラー出力への出力（`CommandLineJobOperator`）に変更されたのでしょうか？運用・監視の観点からは、例外は一般的にログに記録されることが期待されています。

**要望:** 例外を標準エラー出力にのみ出力すると、監視が複雑になります。これらの例外もログに記録していただけないでしょうか？

---

## 2) ジョブ起動時のバリデーション例外がログに記録されない

`CommandLineJobRunner`では、ジョブ起動時にバリデーションが失敗すると、例外がそのままスローされ、ログにも記録されていました。

`CommandLineJobOperator`では、起動時にバリデーションが失敗すると、例外は`start`メソッド内でキャッチされ、終了コード1が返されます。

その結果、`CommandLineJobOperator`で起動時のバリデーションが失敗しても、例外は`batch_job_execution`テーブルにも保存されず、ログにも書き込まれません。
起動時のバリデーションが実際に動作していることをどのように確認すればよいのでしょうか？

**要望:** バリデーション失敗をログに記録してください。

**例:**

ジョブ定義
```java
@Bean
public Job testJob(JobRepository jobRepository,
                                    Step step01) {
    return new JobBuilder("testJob",
            jobRepository)
            .start(step01)
            .validator(new TestValidator())
            .build();
}
```

`TestValidator`のコード
```java
import org.springframework.batch.core.job.parameters.JobParameter;
import org.springframework.batch.core.job.parameters.JobParameters;
import org.springframework.batch.core.job.parameters.JobParametersInvalidException;
import org.springframework.batch.core.job.parameters.JobParametersValidator;

import java.util.Map;

public class TestValidator implements JobParametersValidator {
    @Override
    public void validate(JobParameters parameters) throws JobParametersInvalidException {
        Map<String, JobParameter<?>> params = parameters.getParameters();

        String str = params.get("str").getValue().toString();
        int num = Integer.parseInt(params.get("num").getValue().toString());

        if (str.length() > num) {
            throw new JobParametersInvalidException("The str must be less than or equal to num. [str:" + str + "][num:" + num + "]");
        }
    }
}
```

以下のパラメータで実行:
```
$ java CommandLineJobOperator TestJobConfig start testJob str=Hello num=4
```

`TestValidator`からの例外がログに表示されることを期待しています（これは`CommandLineJobRunner`の動作です）。例:
```
[2025/11/05 10:33:21] [main] [o.h.v.i.util.Version  ] [INFO ] HV000001: Hibernate Validator 9.0.1.Final
[2025/11/05 10:33:21] [main] [o.s.b.c.l.s.CommandLineJobRunner] [ERROR] Job Terminated in error: The str must be less than or equal to num. [str:Hello][num:4]
org.springframework.batch.core.JobParametersInvalidException: The str must be less than or equal to num. [str:Hello][num:4]
```

しかし`CommandLineJobOperator`では、`TestValidator`からの例外が表示されないため、バリデーションが動作していることを確認できません:
```
[2025/11/05 10:45:55] [main] [o.h.v.i.util.Version  ] [INFO ] HV000001: Hibernate Validator 9.0.1.Final
[2025/11/05 10:45:55] [main] [o.s.b.c.l.s.CommandLineJobOperator] [INFO ] Starting job with name 'job01' and parameters: {str=Hello, num=4}
```

---

## 3) ExitCodeMapperやJobParametersConverterをカスタマイズできない

`CommandLineJobRunner`では、以下のように`ExitCodeMapper`や`JobParametersConverter`などのBeanを定義することで動作をカスタマイズできました:

```java
@Bean
public ExitCodeMapper exitCodeMapper() {
    final SimpleJvmExitCodeMapper simpleJvmExitCodeMapper = new SimpleJvmExitCodeMapper();
    final Map<String, Integer> exitCodeMapper = new HashMap<>();
    exitCodeMapper.put("NOOP", 0);
    exitCodeMapper.put("COMPLETED", 0);
    exitCodeMapper.put("STOPPED", 255);
    exitCodeMapper.put("FAILED", 255);
    exitCodeMapper.put("UNKNOWN", 255);
    exitCodeMapper.put("COMPLETED_CUSTOM", 200);
    exitCodeMapper.put("STOPPED_CUSTOM", 201);
    exitCodeMapper.put("FAILED_CUSTOM", 202);
    simpleJvmExitCodeMapper.setMapping(exitCodeMapper);
    return simpleJvmExitCodeMapper;
}

@Bean
public JobParametersConverter jobParametersConverter(
        @Qualifier("adminDataSource") DataSource adminDataSource) {
    return new JobParametersConverterImpl(adminDataSource);
}
```

`CommandLineJobOperator`では、このようなBeanを定義しても動作は変わりません。

これは`CommandLineJobRunner#start`と`CommandLineJobOperator#main`の実装の違いによるものと考えられます。
`CommandLineJobRunner`は`ApplicationContext.getAutowireCapableBeanFactory().autowireBeanProperties`を使用していますが、`CommandLineJobOperator`はDIコンテナから3つのBean（`JobOperator`、`JobRepository`、`JobRegistry`）のみを取得しています。

このため、`ExitCodeMapper`や`JobParametersConverter`がBeanとして存在していても、`CommandLineJobOperator`によって無視されているようです。

コード抜粋:

```java
// CommandLineJobRunner#start
int start(String jobPath, String jobIdentifier, String[] parameters, Set<String> opts) {

    ConfigurableApplicationContext context = null;
    // 省略
        try {
            context = new AnnotationConfigApplicationContext(Class.forName(jobPath));
        }
    // 省略
        context.getAutowireCapableBeanFactory()
            .autowireBeanProperties(this, AutowireCapableBeanFactory.AUTOWIRE_BY_TYPE, false);
    // 省略
}
```

```java
// CommandLineJobOperator#main
public static void main(String[] args) {
    // 省略
    ConfigurableApplicationContext context = null;
    try {
        Class<?> jobConfigurationClass = Class.forName(jobConfigurationClassName);
        context = new AnnotationConfigApplicationContext(jobConfigurationClass);
    }
    // 省略
    try {
        jobOperator = context.getBean(JobOperator.class);
        jobRepository = context.getBean(JobRepository.class);
        jobRegistry = context.getBean(JobRegistry.class);
    }
    // 省略
    CommandLineJobOperator operator = new CommandLineJobOperator(jobOperator, jobRepository, jobRegistry);
    // 省略
}
```

これらの実装変更は意図的なものでしょうか？もしそうであれば、その理由は何でしょうか？

**要望:** `CommandLineJobOperator`でも`ExitCodeMapper`と`JobParametersConverter`のカスタマイズを可能にしてください。

---

## 4) ジョブの停止や再起動に必要なパラメータが異なる

`CommandLineJobRunner`では、`jobName`または`jobExecutionId`を指定してジョブを停止または再起動できました。

`CommandLineJobOperator`では、`jobExecutionId`を指定することでのみ停止または再起動が可能です。

実際の運用では、ジョブを実行するユーザーは通常、自分が指定した`jobName`しか知りません。

`CommandLineJobOperator`でジョブを停止または再起動する必要がある場合、まず何らかの方法で`jobExecutionId`を取得しなければなりません。
コマンドラインから`jobExecutionId`を取得する推奨方法は何でしょうか？

**要望:** `CommandLineJobOperator`でも`jobName`による停止と再起動をサポートしてください。
</div>

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-21

ご報告いただきありがとうございます！

> 1) 必須引数なしでジョブを起動した際のエラー出力先が異なる
> 要望: 例外を標準エラー出力にのみ出力すると、監視が複雑になります。これらの例外もログに記録していただけないでしょうか？

これは見落としでした。修正します。

> 2) ジョブ起動時のバリデーション例外がログに記録されない
> 要望: バリデーション失敗をログに記録してください。

こちらも同様です。新しいオペレーターを適宜更新します。

> 3) ExitCodeMapperやJobParametersConverterをカスタマイズできない
> これらの実装変更は意図的なものでしょうか？もしそうであれば、その理由は何でしょうか？

はい、意図的なものです。理由は以下の通りです。これが動作するためには:

```
context.getAutowireCapableBeanFactory().autowireBeanProperties(this, AutowireCapableBeanFactory.AUTOWIRE_BY_TYPE, false);
```

コマンドラインジョブランナーがアプリケーションコンテキスト内でBeanとして定義されている必要があります。しかし、アプリケーションコンテキストの外部で使用したい場合はどうでしょうか？これは単純に不可能です。`autowireBeanProperties`の最初の引数の`this`参照に注目してください。新しいランナーにはこの制限（および[#4899](https://github.com/spring-projects/spring-batch/issues/4899)で説明されているその他の制限）がありません。とはいえ、（オペレーターをインスタンス化する`main`メソッド内で）アプリケーションコンテキスト内にカスタムの`ExitCodeMapper`や`JobParametersConverter`が存在するかどうかを確認し、オペレーターに設定する必要があります。

次のリリースでこれを予定し、移行ガイドを適宜更新します。

> 4) ジョブの停止や再起動に必要なパラメータが異なる

ジョブ名による停止や再起動は混乱を招いていました。ジョブが2つ（またはそれ以上）の異なるインスタンスを並列実行していて、そのうち1つだけを停止したい場合はどうでしょうか？同様に、ジョブに2つの失敗したジョブインスタンスがあり、1つだけを再起動したい場合はどうでしょうか？再起動したい実行を指定することで、この曖昧さは生じません。失敗した実行のIDを取得することは`JobRepository` APIで可能です。とはいえ、`JobRepository#getLastJobInstance(jobName)`を使用して、失敗した実行を再起動することで、ジョブ名による再起動は引き続き可能です。
