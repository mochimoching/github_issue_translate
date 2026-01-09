# stop() does not prevent upcoming steps to be executed anymore

**Issue番号**: #5114

**状態**: closed | **作成者**: andre-bugay | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5114

**関連リンク**:
- Commits:
  - [e5fbc2a](https://github.com/spring-projects/spring-batch/commit/e5fbc2a0387858f5f95009e3a032d2864398f9ac)
  - [29f5ecf](https://github.com/spring-projects/spring-batch/commit/29f5ecf567cc21b5ce3dd9a41283d227a85c3667)
  - [644d7e6](https://github.com/spring-projects/spring-batch/commit/644d7e6997c4e29822be580dab8e6f65713e17be)

## 内容

It seems like Spring Batch 6 cannot stop a Job anymore.
After calling stop(), all steps are executed and later the job is marked as FAILED.

In Spring Batch 5 the flow was:
`STARTED` -> `STOPPING` -> mark step executions as terminateOnly -> `STOPPED`

In Spring Batch 6 it is:
`STARTED` -> `STOPPING` -> `STOPPED` -> `FAILED`

If I am right then the root cause of this change is the following new line in 


https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/SimpleJobOperator.java#L348

Directly afterwards the 
`jobRepository.update(jobExecution);`
checks
https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/support/SimpleJobRepository.java#L139

This will always be false as the endTime was set just before.
The jobState will be set from `STOPPING` to `STOPPED` directly.

**Consequence**
Inside `SimpleJobRepository#update(StepExecution)` -> `checkForInterruption(stepExecution)` the check in
https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/support/SimpleJobRepository.java#L186-L188
will never be true and the steps are not marked for terminateOnly.

Is this intended and how can I prevent running the unstarted steps once the job is stopped?


## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2025-12-05

Hi, I also have reviewed the root cause of this issue. I'd like to share my findings for your reference.

As you pointed out, the commit e5fbc2a introduced:
```java
jobExecution.setEndTime(LocalDateTime.now());
```

This change causes the following logic within SimpleJobRepository to execute:
```java
if (jobExecution.getStatus() == BatchStatus.STOPPING && jobExecution.getEndTime() != null) {
    if (logger.isInfoEnabled()) {
       logger.info("Upgrading job execution status from STOPPING to STOPPED since it has already ended.");
    }
    jobExecution.upgradeStatus(BatchStatus.STOPPED);
}
```
Looking at the history, this seems to be an intentional change (though I am uncertain of the exact reasoning for setting the status to STOPPED at this specific point). The solution will depend on whether Spring Batch Team decide to retain or revert this code modification.

## Scenario 1: Retaining jobExecution.setEndTime(LocalDateTime.now()) (Current Batch 6 Behavior)
If we must keep jobExecution.setEndTime(LocalDateTime.now()), then the following is the issue:

Unless you are creating and using a custom Step implementation, and instead use the provided TaskletStep or the newly added ChunkOrientedStep (in Batch 6), the following logic in SimpleJobOperator at Line #374 is executed:
```java
stoppableStep.stop(stepExecution);
// default void stop(StepExecution stepExecution) {
//     stepExecution.setTerminateOnly();
//     stepExecution.setStatus(BatchStatus.STOPPED);
//     stepExecution.setExitStatus(ExitStatus.STOPPED);
//     stepExecution.setEndTime(LocalDateTime.now());
// }
```
This sets the StepExecution to terminateOnly, and then at Line #375 of SimpleJobOperator, it is persisted to the database (metadata repository).

The core problem is that the StepExecution object being updated by the SimpleJobOperator.stop() call is not the same object instance currently being used by the actively executing Step thread. Therefore, to make interruption work, logic should be added to the executing Step (in both TaskletStep and ChunkOrientedStep) to fetch the latest status of the StepExecution from the metadata repository before every chunk transaction commit & after the ItemStream.update() call (or at a similar boundary, based on the historical TaskletStep logic).


## Scenario 2: Reverting the Code Added in e5fbc2a (Returning to Legacy Behavior)
If Spring Batch Team choose to revert the code added in e5fbc2a, the logic you mentioned will appropriately interrupt the Step. However, only TaskletStep will be correctly interrupted.

If you look at `TaskletStep.doExecute()`, it calls `getJobRepository().update(stepExecution);` right before every transaction commit (after `Tasklet.execute()` completes - around line #464). This update triggers the logic you cited:
```java
private void checkForInterruption(StepExecution stepExecution) {
    JobExecution jobExecution = stepExecution.getJobExecution();
    jobExecutionDao.synchronizeStatus(jobExecution); // <--- Reads the updated JobExecution status from DB
    if (jobExecution.isStopping()) {
       logger.info("Parent JobExecution is stopped, so passing message on to StepExecution");
       stepExecution.setTerminateOnly(); // <--- Sets terminateOnly
    }
}
```
This allows the running Step to read the latest JobExecution status modified by JobOperator and set terminateOnly.

The issue is that ChunkOrientedStep does not have this same logic. It only calls `JobRepository.updateExecutionContext()`.

Therefore, if Spring Batch Team proceed with Scenario 2, a call to `getJobRepository().update(stepExecution);` must also be added to the ChunkOrientedStep implementation to ensure proper interruption.

I hope this analysis is helpful for your ongoing work!

### コメント 2 by fmbenhassine

**作成日**: 2025-12-05

@andre-bugay @KILL9-NO-MERCY Thank you for raising this issue and for taking the time to analyse the root cause! Indeed, stopping a job seems to be broken, even though the [graceful shutdown sample](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/shutdown) was working as expected when I introduced it in d4a7dfd25f2782fba7a1563ab62aa116b4f6d33f. There seems to be a commit after that that broke the stop feature.. What bothers me is that that sample involves a manual step (sending the interruption signal to the process) which makes it difficult to detect regressions automatically on CI.

I will check that and plan the fix for the upcoming 6.0.1.

### コメント 3 by fmbenhassine

**作成日**: 2025-12-12

> The solution will depend on whether Spring Batch Team decide to retain or revert this code modification.

I am not against reverting a change if it has introduced a regression. 

> As you pointed out, the commit [e5fbc2a](https://github.com/spring-projects/spring-batch/commit/e5fbc2a0387858f5f95009e3a032d2864398f9ac) introduced:

Reverting e5fbc2a0387858f5f95009e3a032d2864398f9ac does not seem to fix the issue, so probably scenario 1 is not the best option. I think this commit is the culprit: db6ef7b067e0daeee59c1baea03a0acfed4f5cfc, but I am still investigating.

> Therefore, if Spring Batch Team proceed with Scenario 2, a call to getJobRepository().update(stepExecution); must also be added to the ChunkOrientedStep implementation to ensure proper interruption.

@KILL9-NO-MERCY  Have you tried this patch? Because I also tried this and does not seem to help neither.

I would appreciate a patch in a PR if someone managed to fix the issue already (and avoid duplicate efforts).

### コメント 4 by fmbenhassine

**作成日**: 2025-12-12

Just to give a bit more context: the attempts I shared in my previous comment led to optimistic locking exceptions (I used [this example](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/shutdown) for tests), so I have a doubt something related to locking could be involved (I am thinking of #5020, but I am probably wrong). cc @quaff . Probably a database sync in missing here: https://github.com/spring-projects/spring-batch/blob/main/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L476.

I will continue to investigate, but if someone managed to fix the issue already, then I would appreciate a patch in a PR to avoid duplicate efforts. Many thanks upfront 🙏

### コメント 5 by quaff

**作成日**: 2025-12-15

> so I have a doubt something related to locking could be involved (I am thinking of [#5020](https://github.com/spring-projects/spring-batch/issues/5020), but I am probably wrong).

#5020 is related to multi-process which this issue doesn't mention.

### コメント 6 by KILL9-NO-MERCY

**作成日**: 2025-12-15

@andre-bugay @fmbenhassine 

I've submitted PR #5165 to address this issue.

The PR fixes the `terminateOnly` flag setting by:
1. Detecting externally stopped StepExecution via `getStepExecution()` and checking `isStopped()` status
2. Synchronizing version and setting `terminateOnly` in `JobRepository.update(StepExecution)`
3. Adding `JobRepository.update(stepExecution)` call in ChunkOrientedStep to match TaskletStep behavior

As mentioned in #5120, my testing shows both #5120 (OptimisticLockingFailureException) and #5114 (terminateOnly not set) are resolved with these changes.

However, I would appreciate it if you could cross-check for any potential side effects I may have overlooked. Thank you!

