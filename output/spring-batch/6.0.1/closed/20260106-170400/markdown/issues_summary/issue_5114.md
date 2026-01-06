*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5114: COMPLETED状態のジョブに対してstop()を呼び出してもステップの実行を防げない

## 課題概要

ジョブの実行中に`JobOperator.stop()`を呼び出してジョブを停止しようとしても、ステップ間のタイミングによっては次のステップが実行されてしまう問題です。また、停止されたジョブがリスタート不可能としてマークされないという問題もありました。

### 用語解説

- **JobOperator**: ジョブの起動、停止、再起動などの操作を行うインターフェース
- **StepExecution**: ステップの実行情報を保持するオブジェクト。ステップの開始時刻、終了時刻、ステータスなどを管理
- **STOPPED_UNEXPECTEDLY**: ジョブが予期せず停止されたことを示すフラグ

### 問題のシナリオ

以下のような2ステップのジョブで問題が発生します：

```java
Job job = new JobBuilder("sample", jobRepository)
    .start(step1)
    .next(step2)
    .build();
```

```
【実行の流れ】
1. ジョブ開始
2. step1実行中
3. step1完了（STATUS=COMPLETED）
4. JobOperator.stop()呼び出し ← ここでstopを実行
5. step2が実行されてしまう ← 期待: step2はスキップされるべき
6. step2完了
7. ジョブ完了（STATUS=COMPLETED） ← 期待: STATUS=STOPPEDになるべき
```

### 実際の動作ログ

```
2025-11-26T09:45:40.018  INFO  o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T09:45:40.046  INFO  o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 8ms
2025-11-26T09:45:40.047  INFO  com.example.demo.DemoApplication         : Running Step 2
2025-11-26T09:45:40.048  INFO  o.s.batch.core.job.SimpleStepHandler     : Executing step: [step2]
2025-11-26T09:45:40.054  INFO  o.s.batch.core.step.AbstractStep         : Step: [step2] executed in 6ms
2025-11-26T09:45:40.060  INFO  o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] completed with the following parameters: [{}] and the following status: [COMPLETED]
```

step1の後に`stop()`が呼ばれているにもかかわらず、step2が実行され、ジョブステータスが`COMPLETED`になっています。

## 原因

`JobOperator.stop()`が呼ばれた時点でジョブ実行に「予期せず停止された」というマーキングを行っていなかったため、後続のステップ実行前にチェックする仕組みがありませんでした。

### 詳細な原因

#### 1. stop()呼び出し後の状態管理不足

```java
// SimpleJobOperator.stop()呼び出し後
// → JobExecution.stoppedUnexpectedly フラグが設定されていない
// → 次のステップ実行前にチェックする仕組みがない
```

#### 2. ステップ実行前のチェック不足

```java
// AbstractJob（修正前のイメージ）
protected void doExecute(JobExecution execution) {
    for (Step step : steps) {
        // stop()が呼ばれたかのチェックがない
        stepExecution = handleStep(step, execution);
        if (stepExecution.getStatus() != BatchStatus.COMPLETED) {
            break;
        }
    }
}
```

#### 3. タイミングの問題

```
【時系列】
T1: step1開始
T2: step1完了 → JobExecution.status = COMPLETED
T3: JobOperator.stop()呼び出し
T4: AbstractJob.doExecute()がstep2を実行開始
    ↑ この時点でstop()が呼ばれたことを検知できない
```

## 対応方針

`JobOperator.stop()`が呼ばれた際に`stoppedUnexpectedly`フラグを設定し、ステップ実行前に必ずこのフラグをチェックするように修正されました。

### 修正内容

[コミット acac0bc](https://github.com/spring-projects/spring-batch/commit/acac0bc0d52e3c3eebaefe39f1a7e3c2fa34e4c7)

#### 1. SimpleJobOperatorでのフラグ設定

```java
// SimpleJobOperator.stop()（修正後のイメージ）
public void stop(long executionId) {
    JobExecution jobExecution = getJobExecution(executionId);
    jobExecution.setStoppedUnexpectedly(true);  // フラグを設定
    jobRepository.update(jobExecution);
}
```

#### 2. AbstractJob.execute()での初期チェック

```java
// AbstractJob.execute()（修正後のイメージ）
public final void execute(JobExecution execution) {
    execution.setStartTime(Instant.now());
    updateStatus(execution, BatchStatus.STARTED);
    
    try {
        jobParametersValidator.validate(execution.getJobParameters());
        
        // 最初にstop()が呼ばれていないかチェック
        if (execution.getStatus() != BatchStatus.STOPPING 
            && !execution.isStoppedUnexpectedly()) {
            doExecute(execution);
        } else {
            // ステップを実行する前に停止リクエストを検出
            execution.setStatus(BatchStatus.STOPPED);
            execution.setExitStatus(ExitStatus.COMPLETED);
        }
    }
    // ...
}
```

#### 3. SimpleJob.doExecute()での各ステップ実行前チェック

```java
// SimpleJob.doExecute()（修正後のイメージ）
protected void doExecute(JobExecution execution) {
    for (Step step : steps) {
        // 各ステップ実行前にチェック
        if (!execution.isStoppedUnexpectedly()) {
            stepExecution = handleStep(step, execution);
            if (stepExecution.getStatus() != BatchStatus.COMPLETED) {
                break;
            }
        }
    }
    
    // すべてのステップを実行しなかった場合に状態を更新
    if (execution.getStepExecutions().isEmpty() 
        && execution.isStoppedUnexpectedly()) {
        execution.setStatus(BatchStatus.STOPPED);
        execution.setExitStatus(ExitStatus.COMPLETED);
    }
}
```

#### 4. FlowJob.doExecute()でのフロー実行前チェック

```java
// FlowJob.doExecute()（修正後のイメージ）
protected void doExecute(JobExecution execution) {
    try {
        // フロー実行前にチェック
        if (!execution.isStoppedUnexpectedly()) {
            JobFlowExecutor executor = new JobFlowExecutor(...);
            executor.updateJobExecutionStatus(this.flow.start(executor).getStatus());
        } else {
            // ステップを実行する前に停止リクエストを検出
            execution.setStatus(BatchStatus.STOPPED);
            execution.setExitStatus(ExitStatus.COMPLETED);
        }
    }
    // ...
}
```

### 修正のポイント

| チェックポイント | 目的 | タイミング |
|---------------|------|----------|
| AbstractJob.execute() | ジョブ開始時の初期チェック | doExecute()呼び出し前 |
| SimpleJob.doExecute() | 各ステップ実行前のチェック | handleStep()呼び出し前 |
| FlowJob.doExecute() | フロー実行前のチェック | flow.start()呼び出し前 |

### 修正後の動作

```
【実行の流れ】
1. ジョブ開始
2. step1実行中
3. step1完了（STATUS=COMPLETED）
4. JobOperator.stop()呼び出し
   → execution.stoppedUnexpectedly = true に設定
5. step2実行前のチェック
   → execution.isStoppedUnexpectedly() == true を検知
   → step2をスキップ
6. execution.status = STOPPED に更新
7. ジョブ完了（STATUS=STOPPED）
```

実際のログ：
```
2025-11-26T09:45:40.018  INFO  : Executing step: [step1]
2025-11-26T09:45:40.046  INFO  : Step: [step1] executed in 8ms
// JobOperator.stop()呼び出し
2025-11-26T09:45:40.047  DEBUG : Job execution was stopped before executing the next step
2025-11-26T09:45:40.060  INFO  : Job: [SimpleJob: [name=sample]] completed with status: [STOPPED]
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `SimpleJobOperator` - ジョブ操作のインターフェース実装
  - `AbstractJob` - ジョブの基底クラス
  - `SimpleJob` - シンプルなジョブ実装
  - `FlowJob` - フロー型ジョブ実装
  - `JobExecution` - ジョブ実行情報を保持
- **関連する変更**: リファレンスドキュメントとJavaDocも更新され、停止されたジョブはリスタート不可能であることが明記されました
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5114
