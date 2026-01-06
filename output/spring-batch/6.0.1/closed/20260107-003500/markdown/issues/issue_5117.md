# ExecutionContext not loaded when step execution is queried from the job repository

**Issue番号**: #5117

**状態**: closed | **作成者**: ruudkenter | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5117

## 内容

In Spring Batch 5.2.x the StepExecution returned from the SimpleJobExplorer returned a fully populated StepExecution, including the ExecutionContext.
 
Spring Batch 6.0.0,  is using a JobRepository for the same task [fetching the StepExecution](https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-integration/src/main/java/org/springframework/batch/integration/partition/StepExecutionRequestHandler.java#L48), however, that doesn't seem to populate the ExecutionContext for the StepExecution. It ultimately delegates to: [JdbcStepExecutionDao](https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/dao/jdbc/JdbcStepExecutionDao.java#L299) without loading the ExecutionContext from the BATCH_STEP_EXECUTION_CONTEXT table. Failing my remote partitioned batch job.
 
Not sure if this is intentional and I am missing out on something, but to me this seems to be an issue.

[Demonstration of the issue](https://github.com/ruudkenter/spring-batch-6-demo). 

NOTE: It does work when you switch to using ResourcelessJobRepository.
 
Regards
Ruud

## コメント

### コメント 1 by ruudkenter

**作成日**: 2025-12-09

Issue is resolved by (https://github.com/spring-projects/spring-batch/pull/5147)

### コメント 2 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue, which is valid! And indeed, #5147 resolves it and was merged.

The fix will be part of the upcoming 6.0.1 planned for next week.

