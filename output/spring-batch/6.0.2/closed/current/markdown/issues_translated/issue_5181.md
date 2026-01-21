*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月21日に生成されました）*

# @SpringBatchTest使用時にMetaDataInstanceFactoryのデフォルト値がStepScopeTestUtilsでStepContextの衝突を引き起こす

**Issue番号**: #5181

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5181

**関連リンク**:
- コミット:
  - [4f8609b](https://github.com/spring-projects/spring-batch/commit/4f8609bf5c7e65a7cb4eccf70730b8c33072d185)

## 内容

## バグの説明
`@SpringBatchTest`で管理されたテスト環境で`StepScopeTestUtils`を使用すると、`StepSynchronizationManager`で論理的な衝突が発生します。

`StepExecution`の等価性は、`stepName`、`jobExecutionId`、および`id`に基づいて判定されます。`MetaDataInstanceFactory`はこれらすべてのフィールドに静的なデフォルト値を設定するため、このファクトリで作成された複数のインスタンスが`SynchronizationManagerSupport.contexts`マップ内で同一キーとして扱われてしまいます。

その結果、`StepScopeTestUtils`でカスタム`JobParameters`を持つ新しいコンテキストを登録できなくなります。`computeIfAbsent`のロジックが、`StepScopeTestExecutionListener`（`@SpringBatchTest`の一部）によって既に登録されたコンテキストを検出してしまうためです。

## 再現手順
1. テストクラスに`@SpringBatchTest`アノテーションを付与します。
2. テストメソッド内で、`MetaDataInstanceFactory.createStepExecution(jobParameters)`で作成した`StepExecution`を使って`StepScopeTestUtils.doInStepScope()`を呼び出します。
3. スコープ内の`Tasklet`や`ItemStream`が`jobParameters`を参照できず失敗します。これはリスナーが登録した初期コンテキストにバインドされているためです。

## 失敗する例
サンプルジョブ
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            Tasklet issueReproductionTasklet
    ) {
        return new StepBuilder(jobRepository)
                .tasklet(issueReproductionTasklet)
                .build();
    }

    @Bean
    @StepScope
    public Tasklet issueReproductionTasklet(@Value("#{jobParameters['testParam']}") String testParam) {
        return (contribution, chunkContext) -> {
            contribution.getStepExecution().getExecutionContext().putString("result", testParam);
            return RepeatStatus.FINISHED;
        };
    }
}
```

テストクラス
```java
@SpringBatchTest
@SpringBootTest
@ActiveProfiles("test")
@Import(TestBatchConfiguration.class)
public class IssueReproductionTest {
    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactoryのID衝突によりJobParameterインジェクションが失敗する")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // 6.x（おそらく5.2.3以降も）のMetadataInstanceFactoryは固定ID 1234LでStepExecutionを作成する
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // この検証は失敗する。'actualValue'がnullになるため。
        // ID衝突（1234L）により、StepScopeTestUtilsで渡したコンテキストではなく、
        // リスナーのコンテキスト（JobParametersなし）をTaskletが取得してしまう。
        assertEquals(expectedValue, actualValue);
    }
}

@TestConfiguration
public class TestBatchConfiguration extends DefaultBatchConfiguration {
}
```

application-test.yml
```yaml
spring:
  batch:
    job:
      enabled: false
```
テスト結果:
```bash
Value for key=[result] is not of type: [class java.lang.String], it is [null]
java.lang.ClassCastException: Value for key=[result] is not of type: [class java.lang.String], it is [null]
```

## 期待される動作
`StepScopeTestUtils.doInStepScope()`内で作成された`StepExecution`とそれに対応する`StepContext`は、`@SpringBatchTest`が有効な場合でも、`StepSynchronizationManager`に正しく登録されてアクセスできるべきです。

（注: 最適な修正方法の決定は簡単ではないと思います。`MetaDataInstanceFactory`でのID生成戦略の変更、またはテスト環境で重複した登録を`StepSynchronizationManager`がどう処理するかの調整が考えられます。）

## 回避策
現在の衝突を回避するには、テストクラス内で`getStepExecution()`メソッドを明示的に定義します。一意の名前または異なるID（例: -1L）を持つ`StepExecution`を返すことで、`StepScopeTestExecutionListener`がデフォルトID（1234L）を占有することを防ぎ、`StepScopeTestUtils`が意図通りに動作するようになります:

```java
/**
 * 回避策: テストクラスでgetStepExecution()を定義してID衝突を回避する。
 * デフォルト以外のIDまたは名前を指定することで、リスナーが登録したコンテキストと
 * StepScopeTestUtilsで作成したコンテキストが衝突しないようにする。
 */
public StepExecution getStepExecution() {
    return MetaDataInstanceFactory.createStepExecution("uniqueStep", -1L);
}
```

テスト結果:
```bash
> Task :test
BUILD SUCCESSFUL in 3s
```

この素晴らしいプロジェクトをメンテナンスしていただき、お時間をいただきありがとうございます！

## コメント

### コメント 1 by injae-kim

**作成日**: 2026-01-11

参考情報）修正PR: https://github.com/spring-projects/spring-batch/pull/5208 👍

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

この課題を再現しようとしていますが、再現できていません。共有いただいたテストはSpring Bootを使用していますが、まずSpring Batchのみを使用して、これが有効な課題であることを確認したいと考えています。

9ae777572a0978572e25f04d4cb93c0ad02b9a0fの時点で、以下のクラス（共有いただいたものからSpring Bootを除いたもの）を`org.springframework.batch.test`パッケージに追加すると、ご指摘のテストは成功します:

```java
package org.springframework.batch.test;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.job.parameters.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.infrastructure.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableBatchProcessing
public class IssueReproductionJobConfiguration {

    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            Tasklet issueReproductionTasklet
    ) {
        return new StepBuilder(jobRepository)
                .tasklet(issueReproductionTasklet)
                .build();
    }

    @Bean
    @StepScope
    public Tasklet issueReproductionTasklet(@Value("#{jobParameters['testParam']}") String testParam) {
        return (contribution, chunkContext) -> {
            contribution.getStepExecution().getExecutionContext().putString("result", testParam);
            return RepeatStatus.FINISHED;
        };
    }
}
```

```java
package org.springframework.batch.test;

import java.io.IOException;
import java.util.Objects;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.springframework.batch.core.job.parameters.JobParameters;
import org.springframework.batch.core.job.parameters.JobParametersBuilder;
import org.springframework.batch.core.step.StepExecution;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;

@ContextConfiguration(classes = IssueReproductionJobConfiguration.class)
@ExtendWith(SpringExtension.class)
public class IssueReproductionTest {

    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactory ID collision causes JobParameter injection failure")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // MetadataInstanceFactory in 6.x / maybe after 5.2.3?? creates StepExecution with fixed ID 1234L
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // This will FAIL because 'actualValue' will be null.
        // The Tasklet retrieved the listener's context (which has no JobParameters)
        // instead of the one passed via StepScopeTestUtils due to ID collision (1234L).
        assertEquals(expectedValue, actualValue);
    }
}
```

ご確認いただけますか？

### コメント 3 by KILL9-NO-MERCY

**作成日**: 2026-01-15

@fmbenhassine さん、こんにちは。
この課題を調査していただき、ありがとうございます！

最初の報告が紛らわしかったことをお詫びします。回避策を適用した状態でテストされたため、お手元の環境ではテストが成功したようです。

### 課題について
テストされたコードには、IDとして-1Lを使用する`getStepExecution()`メソッドが含まれています:
```java
public StepExecution getStepExecution() throws IOException {
    return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
}
```
これは実際、ID衝突を回避するために私が言及した回避策です。-1Lを使用すると、リスナーが登録したコンテキスト（ID: 1234L）とテストで作成したコンテキスト（ID: -1L）が衝突しないため、テストが正しく動作します。

#### バグを再現するには
実際のバグを再現するには、以下のいずれかを行う必要があります:

`getStepExecution()`メソッドを完全に削除する、または
-1Lの代わりにデフォルトID（1234L）を使用する

以下は、ID衝突を明確に示すテストケースです:
```java
@SpringBatchTest
@ContextConfiguration(classes = IssueReproductionJobConfiguration.class)
@ExtendWith(SpringExtension.class)
public class IssueReproductionTest {

    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        String expectedValue = "HelloBatch2";
        JobParameters jobParameters = new JobParametersBuilder()
            .addString("testParam", expectedValue)
            .toJobParameters();

        return MetaDataInstanceFactory.createStepExecution(jobParameters);
    }

    @Test
    void reproduceIdCollisionBug() throws Exception {
        String expectedValue = "HelloBatch1";
        JobParameters jobParameters = new JobParametersBuilder()
            .addString("testParam", expectedValue)
            .toJobParameters();

        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        StepScopeTestUtils.doInStepScope(stepExecution,
            () -> issueReproductionTasklet.execute(stepExecution.createStepContribution(), null));

        String actualValue = stepExecution.getExecutionContext().getString("result");
        // このアサーションは成功するが、バグの証明になる！
        // Taskletは"HelloBatch1"（テストのStepExecutionから）ではなく、
        // "HelloBatch2"（リスナーのコンテキストから）を受け取る
        assertEquals("HelloBatch2", actualValue);
    }
}
```
このテストでは:
リスナーが`testParam="HelloBatch2"`（ID: 1234L）で`StepExecution`を作成
テストが`testParam="HelloBatch1"`（ID: 1234L）で`StepExecution`を作成しようとする
ID衝突により、リスナーのコンテキストが使用され、Taskletは"HelloBatch1"ではなく"HelloBatch2"を受け取る
`assertEquals("HelloBatch2", actualValue)`で成功するが、これは間違ったコンテキストが使用されていることを証明している！

#### 根本原因
`StepScopeTestExecutionListener`（`@SpringBatchTest`で有効化される）と`MetaDataInstanceFactory.createStepExecution(jobParameters)`の両方が同じデフォルトID（1234L）を使用しています。`StepExecution.equals()`はIDのみを比較するため、`StepSynchronizationManager`はこれらを同じキーとして扱い、コンテキストの衝突が発生します。

#### 再現を確認
Spring Batchコードベースでこのバグを正常に再現しました:
環境: Spring Batch 6.0.1-SNAPSHOT（コミット 9ae7775）、JDK 22

追加情報や説明が必要な場合はお知らせください。

### コメント 4 by fmbenhassine

**作成日**: 2026-01-21

詳細なフィードバックをありがとうございます！理解できました。最初の説明を誤解していて申し訳ありません。

[#5208](https://github.com/spring-projects/spring-batch/pull/5208) は問題なさそうなので、次回の6.0.2で修正を予定します。
