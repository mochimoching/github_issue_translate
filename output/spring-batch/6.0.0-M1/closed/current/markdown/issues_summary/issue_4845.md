*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

`JobOperator`のメソッドシグネチャで、プリミティブ型（String、Long等）の代わりにドメイン型（Job、JobExecution等）を使用するよう改善し、APIを高レベル化する提案です。

### v5.2の問題

```java
// 低レベルなAPI設計（プリミティブ型）
public interface JobOperator {
    Long start(String jobName, Properties parameters);  // ❌
    boolean stop(long jobExecutionId);                   // ❌
    Long restart(long jobExecutionId);                   // ❌
}
```

この設計では、実装が以下の低レベル処理を行う必要があります：

```java
public Long start(String jobName, Properties parameters) {
    // 1. JobRegistryからジョブを検索
    Job job = jobRegistry.getJob(jobName);
    // 2. PropertiesをJobParametersに変換
    JobParameters jobParams = converter.convert(parameters);
    // 3. ようやくジョブ起動
    JobExecution execution = run(job, jobParams);
    // 4. IDを返す
    return execution.getId();
}
```

## 原因

`JobOperator`は当初、JMXやコマンドライン等の外部インターフェースを想定して、文字列ベースのAPIとして設計されました。しかし、これにより：

1. **不要な依存**: `JobRegistry`や`JobParametersConverter`への依存が発生
2. **責務の混在**: 変換・検索ロジックが高レベルAPIに混入
3. **使いにくさ**: プログラマティックな使用時に冗長

## 対応方針

**コミット**: [8dde852](https://github.com/spring-projects/spring-batch/commit/8dde8529d36b646b33a1711219a1b1e8a046345a)

ドメイン型を使用する新しいメソッドを追加し、プリミティブ型のメソッドを非推奨化しました。

### v6.0の改善されたAPI

```java
public interface JobOperator extends JobLauncher {
    // ✅ 新しい高レベルAPI（ドメイン型）
    JobExecution run(Job job, JobParameters parameters);
    JobExecution startNextInstance(Job job);
    JobExecution restart(JobExecution jobExecution);
    boolean stop(JobExecution jobExecution);
    
    // ❌ 非推奨（プリミティブ型）
    @Deprecated(since = "6.0", forRemoval = true)
    Long start(String jobName, Properties parameters);
    
    @Deprecated(since = "6.0", forRemoval = true)
    boolean stop(long jobExecutionId);
}
```

### 使用例の比較

```java
// v5.2（プリミティブ型）
@Autowired JobOperator jobOperator;
@Autowired JobRegistry jobRegistry;

Properties props = new Properties();
props.setProperty("date", "2026-01-06");
Long executionId = jobOperator.start("myJob", props);  // 文字列変換が必要

// v6.0（ドメイン型）
@Autowired JobOperator jobOperator;
@Autowired Job myJob;  // DIで直接注入

JobParameters params = new JobParametersBuilder()
    .addLocalDate("date", LocalDate.of(2026, 1, 6))
    .toJobParameters();
JobExecution execution = jobOperator.run(myJob, params);  // 型安全
```

### メリット

| 項目 | プリミティブ型 | ドメイン型 |
|------|-------------|----------|
| 型安全性 | 低い（実行時エラー） | 高い（コンパイル時チェック） |
| 依存関係 | 多い（Registry, Converter） | 少ない（Repositoryのみ） |
| 責務の明確性 | 低い（変換処理が混入） | 高い（操作のみ） |
| IDEサポート | 限定的 | 充実（補完、型推論） |

低レベルの変換処理は`CommandLineJobRunner`や`JmxConsoleAdapter`等の専用クラスに移動されます。
