*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# COMPLETED状態のジョブに対してJobOperator.stop()を呼び出してもステップの実行を防げない

**課題番号**: #5114

**状態**: closed | **作成者**: cppwfs | **作成日**: 2025-11-26

**ラベル**: type: bug, in: core, status: pending-design-work

**URL**: https://github.com/spring-projects/spring-batch/issues/5114

**関連リンク**:
- Commits:
  - [acac0bc](https://github.com/spring-projects/spring-batch/commit/acac0bc0d52e3c3eebaefe39f1a7e3c2fa34e4c7)

## 内容

**バグの説明**
開発者が`COMPLETED`状態のジョブに対して`JobOperator.stop()`を呼び出すと、ジョブ実行は`STOPPED`に更新されません。しかし、後続のステップはまだ実行されます。開発者は、ジョブが停止状態に変更されればステップが実行されないことを期待します。

また、`JobOperator.stop(long executionId)`を実行した後のジョブは、リスタート不可能としてマークされるべきです。

**環境**
- Spring Batch 6.0.0
- Spring Boot 4.0.0
- Java 21

**再現手順**
次の例を使用してください：
https://github.com/spring-projects/spring-batch/files/16045042/demo.zip

**期待される動作**
ジョブが停止として記録され、ステップが実行されない。

**実際の動作**
ジョブは`COMPLETED`の状態のままですが、次のステップは実行されます：
```
2025-11-26T09:45:40.018-06:00  INFO 47730 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T09:45:40.028-06:00  INFO 47730 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] launched with the following parameters: [{}]
2025-11-26T09:45:40.031-06:00  INFO 47730 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T09:45:40.046-06:00  INFO 47730 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 8ms
2025-11-26T09:45:40.047-06:00  INFO 47730 --- [demo] [           main] com.example.demo.DemoApplication         : Running Step 2
2025-11-26T09:45:40.048-06:00  INFO 47730 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step2]
2025-11-26T09:45:40.054-06:00  INFO 47730 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step2] executed in 6ms
2025-11-26T09:45:40.060-06:00  INFO 47730 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] completed with the following parameters: [{}] and the following status: [COMPLETED]
```

### コメント 1 by cppwfs

**作成日**: 2025-11-26

修正の提案：

1. `JobOperator.stop(long executionId)`のjavaドキュメントを更新し、停止されたジョブがリスタート不可能であることを記載します。

2. `JobOperator.stop(long executionId)`が呼び出されたときに、ジョブ実行の`STOPPED_UNEXPECTEDLY=true`を設定します。
   `SimpleJobOperator`内で行います。
   
3. ジョブの実行処理において、`STOPPED_UNEXPECTEDLY`が`true`の場合、次のステップの起動を防ぎます。以下の場所に実装：
   * `AbstractJob`の`runSteps`内：次のステップを実行する前にチェック
   * `FlowJob`の`doExecute`内：次のステップを実行する前にチェック
   
4. ステップが実行されなかった場合（上記のif文に該当した場合）、`FlowJob`内の`JobExecution.Status`を`STOPPED`に更新します。

5. `AbstractJob`と`FlowJob`のコード変更については、デザインレビューを行います。

### コメント 2 by cppwfs

**作成日**: 2025-12-12

`stepExecuted`フラグをフローを通して渡す必要があります。これにより、ステップが実行されたかどうかを判断できます。このコードを再訪する必要があります。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-12

良い点です。`stepExecution`フラグを渡すのは良いアプローチだと思いますが、これはそのようなフラグを導入しないための別のアプローチもあるかもしれません（まだ確認していません）。

いずれにせよ、同じステップを2回実行する可能性があるという事実を回避する必要があると思います。次のステップ（があれば）を実行する前に、`JobOperator#stop`呼び出しによってジョブが予期せず停止されたかどうかをチェックする必要があります。現時点では、ステップ2を実行する前にジョブが停止されたかどうかをチェックしていません。

### コメント 2 by cppwfs

**作成日**: 2025-12-12

@fmbenhassine 良い点です！
次のような動作になるはずです：
- step1を実行する前に、ジョブが予期せず停止されたかチェック
- step1を実行
- step2を実行する前に、ジョブが予期せず停止されたかチェック（ここでstopが呼ばれていた）
- 予期せず停止されていたのでstep2をスキップ

flowを通してフラグを渡すことを避け、各ステップの実行前にチェックする方が良いと思います。

### コメント 3 by fmbenhassine

**作成日**: 2025-12-12

> flowを通してフラグを渡すことを避け、各ステップの実行前にチェックする方が良いと思います。

同意します。コードスニペットを作成してデザインを確認し、優先順位を調整し、6.0.1にマージするために新しいブランチに移動します。

### コメント 4 by fmbenhassine

**作成日**: 2025-12-12

ここに私が考えているスニペットがあります：

```java
/**
 * AbstractJob
 */

@Override
public final void execute(JobExecution execution) {
    Assert.notNull(execution, "jobExecution must not be null");

    logger.debug("Job execution starting: {}", execution);
    execution.setStartTime(this.jobRepository.getSystemClock().instant());
    updateStatus(execution, BatchStatus.STARTED);
    listener.beforeJob(execution);

    try {
        jobParametersValidator.validate(execution.getJobParameters());
        if (execution.getStatus() != BatchStatus.STOPPING && !execution.isStoppedUnexpectedly()) {
            doExecute(execution);
        }
        else {
            // ステップを実行する前に停止リクエストを検出
            execution.setStatus(BatchStatus.STOPPED);
            execution.setExitStatus(ExitStatus.COMPLETED);
            logger.debug("Job execution was stopped before executing any steps");
        }
    }
    catch (JobInterruptedException e) {
        logger.info("Encountered interruption executing job: {}", e.getMessage());
        if (logger.isDebugEnabled()) {
            logger.debug("Full exception", e);
        }
        execution.setExitStatus(getDefaultExitStatusForFailure(e, execution));
        execution.setStatus(
                BatchStatus.max(BatchStatus.STOPPED, e.getStatus()));
    }
    ...
}

/**
 * SimpleJobを実行する際、AbstractJobの最初のチェック
 * に加えてステップを実行する前に追加のチェックを行う。
 */
protected void doExecute(JobExecution execution)
        throws JobInterruptedException {
    StepExecution stepExecution = null;
    for (Step step : steps) {
        if (!execution.isStoppedUnexpectedly()) { // <========== ステップを実行する前にチェック
            stepExecution = handleStep(step, execution);
            if (stepExecution.getStatus() != BatchStatus.COMPLETED) {
                break;
            }
        }
    }

    //
    // すべてのステップを実行しなかった場合に状態を更新
    //
    if (execution.getStepExecutions().isEmpty() && execution.isStoppedUnexpectedly()) {
        execution.setStatus(BatchStatus.STOPPED);
        execution.setExitStatus(ExitStatus.COMPLETED);
        logger.debug(
                "Job execution was stopped before executing any steps");
    }
    ...
}

/**
 * FlowJobを実行する際、AbstractJobの最初のチェック
 * に加えてステップを実行する前に追加のチェックを行う。
 */
protected void doExecute(JobExecution execution)
        throws JobExecutionException {
    try {
        if (!execution.isStoppedUnexpectedly()) { // <========== flowを実行する前にチェック
            JobFlowExecutor executor = new JobFlowExecutor(this.jobRepository,
                    new SimpleStepHandler(this.jobRepository), execution);
            executor.updateJobExecutionStatus(this.flow.start(executor).getStatus());
        }
        else {
            // ステップを実行する前に停止リクエストを検出
            execution.setStatus(BatchStatus.STOPPED);
            execution.setExitStatus(ExitStatus.COMPLETED);
            logger.debug("Job execution was stopped before executing the flow");
        }
    }
    ...
}
```

最初のチェックで`AbstractJob#execute`内にいるかどうかは不明ですが、これで重複した`SimpleJob#doExecute`チェックを回避できます。しかし、`FlowJob#doExecute`内では別のチェックが必要です。なぜなら、`JobOperator#stop`の呼び出しはすでに`AbstractJob#execute`を通過しており、`FlowJob#doExecute`ではフロー内の最初のステップを実行する直前に呼び出される可能性があるからです。

さらに、`SimpleJob#doExecute`と`FlowJob#doExecute`の終わりでチェックを行い、何も実行されなかった場合（ステップまたはフロー）にジョブステータスを更新する必要があります。

これが良い方向性であれば、ブランチにコミットします。ご意見をお聞かせください。よろしくお願いします。

### コメント 5 by cppwfs

**作成日**: 2025-12-12

> これが良い方向性であれば、ブランチにコミットします。ご意見をお聞かせください。よろしくお願いします。

@fmbenhassine これは素晴らしいです！気に入りました！ありがとうございます。

### コメント 6 by fmbenhassine

**作成日**: 2025-12-12

ありがとう@cppwfs！コミットしてみます。準備ができたらレビューをお願いします。

### コメント 7 by fmbenhassine

**作成日**: 2025-12-12

修正は以下のコミットにあります：https://github.com/spring-projects/spring-batch/commit/acac0bc0d52e3c3eebaefe39f1a7e3c2fa34e4c7

@cppwfs さん、お時間のある時に確認していただけますか？このコミットにはテスト、javadocの更新、リファレンスドキュメントへのメモが含まれています。

