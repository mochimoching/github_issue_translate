*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました。*

## 課題概要

Spring Batch 6.0において、`JobOperator.start()`と非同期タスクエグゼキューターを組み合わせてジョブを起動する際、間欠的に`OptimisticLockingFailureException`が発生する問題です。

**OptimisticLockingFailureExceptionとは**: データベースの楽観的ロック機能を使用する際、既存レコードを更新しようとした時点で、そのレコードのバージョン番号が想定と異なる（他の処理によって既に更新された）場合にスローされる例外です。

**問題の状況**:
- `jobOperator.start()`を使用してジョブを起動
- 非同期タスクエグゼキューター（`ThreadPoolTaskExecutor`など）を使用
- ジョブ起動時に`OptimisticLockingFailureException`が間欠的に発生

**具体的な事象**:
```
OptimisticLockingFailureException: Attempt to update job execution id=1 
with wrong version (0), where current version is 1
```

**再現環境**:
- Spring Boot 4.0.0
- Spring Batch 6.0.0/6.0.1
- Java 21
- 複数のユーザーが同じ問題を再現環境を作成して確認
  - JDBC環境: https://github.com/phactum-mnestler/spring-batch-reproducer
  - MongoDB環境: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

## 原因

`TaskExecutorJobLauncher`クラスの実装において、非同期タスクエグゼキューターへのジョブ実行タスクの送信と、その後の処理に競合状態（race condition）が存在することが原因です。

**詳細な原因分析**:

1. **Spring Batch 6.xでの変更**: `TaskExecutorJobLauncher.launchJobExecution()`メソッドにおいて、finally節が新たに追加されました（5.xには存在しない）

2. **競合状態の発生箇所**:
```java
// TaskExecutorJobLauncher.java
try {
    taskExecutor.execute(() -> {
        // ジョブ実行（非同期で別スレッドで実行）
        job.execute(jobExecution);
        // ジョブスレッドでJobExecutionを更新（version 0 → 1）
    });
} finally {
    // ランチャースレッドでJobExecutionを更新しようとする
    // しかし、ジョブスレッドが既に更新している可能性がある
    this.jobRepository.update(jobExecution); // ← 競合発生！
}
```

3. **問題の流れ**:
   - ランチャースレッド: `BATCH_JOB_EXECUTION`テーブルに初期レコード（version=0）を登録
   - ランチャースレッド: タスクエグゼキューターにジョブ実行を送信（非同期）
   - **ジョブスレッド**: すぐに実行開始し、`JobExecution`を更新（version 0→1）
   - **ランチャースレッド**: finally節で`JobExecution`を更新しようとする
   - この時点で、ランチャースレッドが持つ`JobExecution`オブジェクトのversionは0だが、データベース上はversionが1になっている
   - 結果: `OptimisticLockingFailureException`が発生

**Spring Batch 5.xとの違い**:
- 5.xでは、`taskExecutor.execute()`の送信が失敗した場合（`TaskRejectedException`）のみ`jobRepository.update()`を呼び出していた
- 6.xでは、finally節により成功時も無条件に`jobRepository.update()`を呼び出すため、競合が発生

## 対応方針

Spring Batchメンテナーが確認し、バージョン6.0.2で修正予定です（コメント6、fmbenhassine氏）。

[#3637](https://github.com/spring-projects/spring-batch/issues/3637)のリグレッション（退行バグ）として認識されています。

**推奨される修正内容** (コメント5、banseok1216氏の提案):
```java
// TaskExecutorJobLauncher.launchJobExecution(..)メソッド
try {
    taskExecutor.execute(() -> {
        job.execute(jobExecution);
    });
} catch (TaskRejectedException e) {
    // タスク送信が拒否された場合のみJobExecutionを更新
    jobExecution.upgradeStatus(BatchStatus.FAILED);
    if (ExitStatus.UNKNOWN.equals(jobExecution.getExitStatus())) {
        jobExecution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
    }
    this.jobRepository.update(jobExecution);
}
// finally節での無条件更新を削除
// → 受け入れられたタスクの場合、ジョブスレッドがJobExecutionを更新するため、
//    ランチャースレッドからの追加更新は不要
```

**コミュニティ提案の回避策**:

1. **シングルスレッドエグゼキューター使用** (licenziato氏の回避策):
```java
@Bean
public JobOperatorFactoryBean jobOperator(JobRepository jobRepository) {
    ThreadPoolTaskExecutor taskExecutor = new ThreadPoolTaskExecutor();
    taskExecutor.setCorePoolSize(1);
    taskExecutor.setMaxPoolSize(1);
    taskExecutor.afterPropertiesSet();
    
    JobOperatorFactoryBean jobOperatorFactoryBean = new JobOperatorFactoryBean();
    jobOperatorFactoryBean.setJobRepository(jobRepository);
    jobOperatorFactoryBean.setTaskExecutor(taskExecutor);
    return jobOperatorFactoryBean;
}
```
ただし、この方法は環境によっては効果がないことが報告されています。

2. **SyncTaskExecutor使用** (StefanMuellerCH氏の回避策):
```java
@Bean
public JobOperatorFactoryBean jobOperator(JobRepository jobRepository) {
    var taskExecutor = new SyncTaskExecutor();
    var jobOperatorFactoryBean = new JobOperatorFactoryBean();
    jobOperatorFactoryBean.setJobRepository(jobRepository);
    jobOperatorFactoryBean.setTaskExecutor(taskExecutor);
    return jobOperatorFactoryBean;
}
```
**注意**: `SyncTaskExecutor`は同期実行となるため、パフォーマンスへの影響が大きく、本番環境での使用は推奨されません。

**まとめ**: 
正式な修正がリリースされるまで、一時的な回避策として`SyncTaskExecutor`を使用することは可能ですが、本番環境では6.0.2のリリースを待つことが推奨されます。
