*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

別のジョブを実行するステップである`JobStep`で、非推奨となった`JobLauncher`の使用を`JobOperator`に置き換えました。

**JobStepとは**: ジョブ内で別のジョブを実行できる特殊なステップです。親ジョブのステップとして子ジョブを実行する際に使用します。

### v5.2の実装

```java
public class JobStep extends AbstractStep {
    private JobLauncher jobLauncher;  // 非推奨API
    
    @Override
    protected void doExecute(StepExecution stepExecution) {
        jobLauncher.run(job, parameters);  // 子ジョブを起動
    }
}
```

## 原因

課題 [#4832](https://github.com/spring-projects/spring-batch/issues/4832) で`JobLauncher`が非推奨化され、`JobOperator`が統一されたエントリーポイントになったため、`JobStep`も移行する必要がありました。

## 対応方針

**コミット**: [b105c8e](https://github.com/spring-projects/spring-batch/commit/b105c8e422a8d8b7f86c56746c8533c2dcae6a20)

`JobStep`の内部実装を`JobOperator`を使用するように変更しました。

### v6.0の改善

```java
public class JobStep extends AbstractStep {
    private JobOperator jobOperator;  // 統一API
    
    @Override
    protected void doExecute(StepExecution stepExecution) {
        jobOperator.start(job, parameters);  // 統一されたAPI
    }
}
```

### 使用例

```java
// 親ジョブの定義（使用方法は変わらない）
@Bean
public Job parentJob(JobRepository jobRepository, Step childJobStep) {
    return new JobBuilder(jobRepository)
        .start(childJobStep)
        .build();
}

@Bean
public Step childJobStep(JobOperator jobOperator, Job childJob) {
    return new JobStepBuilder(new StepBuilder(jobRepository))
        .job(childJob)
        .launcher(jobOperator)  // v6.0ではJobOperator
        .build();
}
```

### メリット

- APIの一貫性向上
- 統一されたジョブ起動インターフェース
- 将来的な保守性の向上
