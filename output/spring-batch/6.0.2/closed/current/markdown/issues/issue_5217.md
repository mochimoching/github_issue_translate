# OptimisticLockingFailureException due to race condition in graceful shutdown

**Issue番号**: #5217

**状態**: closed | **作成者**: KMGeon | **作成日**: 2026-01-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5217

**関連リンク**:
- Commits:
  - [4034f26](https://github.com/spring-projects/spring-batch/commit/4034f269cb96c55ee1fd1a80666fb087d07b9526)
  - [7f742a5](https://github.com/spring-projects/spring-batch/commit/7f742a5933473e5a6768db583f78bf68aa942641)

## 内容

## Bug Description

`GracefulShutdownFunctionalTests.testStopJob` fails intermittently due to a race condition (Flaky Test).

## Affects Version

- Spring Batch 6.0.1

## Error Message

```
OptimisticLockingFailureException: Attempt to update step execution id=0
with wrong version (1), where current version is 2
```

## Reproducibility

> **Note**: This is a very rare flaky test. In my local environment (Mac), it occurred approximately **1 in 100 runs**. This issue is highly timing-sensitive due to the race condition, so the failure rate varies depending on CPU load and thread scheduling.
>
> I'm reporting this just in case it might be helpful. **Feel free to close this issue if it's not considered a priority** - I completely understand that rare flaky tests may not warrant immediate attention.

## Failed Build Links

CI Failure:
- https://github.com/spring-projects/spring-batch/actions/runs/21092150808/job/60664875427

```
04:48:43.282 [batch-executor1] INFO  - Job: [SimpleJob: [name=job]] launched
04:48:43.293 [batch-executor1] INFO  - Executing step: [chunkOrientedStep]
04:48:44.343 [main] INFO  - Stopping job execution: status=STARTED
04:48:44.345 [main] INFO  - Upgrading job execution status from STOPPING to STOPPED

org.springframework.dao.OptimisticLockingFailureException:
Attempt to update step execution id=0 with wrong version (1), where current version is 2
    at JdbcStepExecutionDao.updateStepExecution(JdbcStepExecutionDao.java:254)
    at SimpleJobRepository.update(SimpleJobRepository.java:174)
    at SimpleJobOperator.stop(SimpleJobOperator.java:375)
    at GracefulShutdownFunctionalTests.testStopJob(GracefulShutdownFunctionalTests.java:80)
```

## Root Cause Analysis

### 1. Race Condition Scenario

```
[batch-executor1 Thread]              [main Thread]
          │                                 │
          │ Processing chunk                │
          │ update(stepExecution)           │
          │ version: 1 → 2                  │
          │                                 │
          │                                 │ stop() called
          │                                 │ Attempts update with version 1
          │                                 │ ❌ FAILS! (DB already has version 2)
```

### 2. Root Cause

In `SimpleJobRepository.update(StepExecution)`, only `isStopped()` is checked, but `isStopping()` is not:

```java
// SimpleJobRepository.java - line 166
if (latestStepExecution.getJobExecution().isStopped()) {  // ← Only checks STOPPED!
    stepExecution.setVersion(latestStepExecution.getVersion());
}
```

When `stop()` is called, the `JobExecution` status changes to `STOPPING`, but `isStopped()` only returns `true` for `STOPPED` status. Therefore, version synchronization does not occur in the `STOPPING` state.

## Proposed Solution

```java
// SimpleJobRepository.java - line 166

// Before
if (latestStepExecution.getJobExecution().isStopped()) {

// After
if (latestStepExecution.getJobExecution().isStopped()
    || latestStepExecution.getJobExecution().isStopping()) {
```

Adding the `isStopping()` check ensures version synchronization occurs during the `STOPPING` state, preventing the race condition.

## Related Code

- `SimpleJobRepository.update(StepExecution)`
- `SimpleJobOperator.stop()`
- `JdbcStepExecutionDao.updateStepExecution()`

---

## Final Note

As mentioned above, this is an extremely rare issue that is difficult to reproduce consistently. I wanted to report it in case it provides useful information, but I fully understand if this is closed as low priority or "won't fix". Thank you for your time reviewing this!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-19

Thank you for reporting this issue and for providing a fix!

Indeed, I was aware of that flaky test but I just didn't have time yet to trace the race condition down. So thank you very much for doing that. I will plan the fix for 6.0.2.

