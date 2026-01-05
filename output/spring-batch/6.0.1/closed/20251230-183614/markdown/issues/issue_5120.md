# StepExecution Update in SimpleJobOperator.stop() Causes JobExecution.BatchStatus.UNKNOWN after graceful stop

**Issue番号**: #5120

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-01

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5120

**関連リンク**:
- Commits:
  - [29f5ecf](https://github.com/spring-projects/spring-batch/commit/29f5ecf567cc21b5ce3dd9a41283d227a85c3667)
  - [f62da2b](https://github.com/spring-projects/spring-batch/commit/f62da2bd6a7a9459d809e86065877ac440130b70)
  - [78ba896](https://github.com/spring-projects/spring-batch/commit/78ba896caa7020f1f7f972ae7b3dd469699a4922)
  - [984a057](https://github.com/spring-projects/spring-batch/commit/984a057f86c92b326782b964f949c0eb0eb805d4)
  - [0feafa1](https://github.com/spring-projects/spring-batch/commit/0feafa15a73c4be4f990b627c914bb918118e96e)
  - [09b0783](https://github.com/spring-projects/spring-batch/commit/09b07834ed86f4a11a51e118e665dc20156352c9)
  - [644d7e6](https://github.com/spring-projects/spring-batch/commit/644d7e6997c4e29822be580dab8e6f65713e17be)

## 内容

Hello Spring Batch Team,

I am reporting an issue where using JobOperator.stop() to gracefully stop a running ChunkOrientedStep results in an OptimisticLockingFailureException and setting UNKNOWN state

## Bug description 
In Spring Batch version 6.0.0, calling SimpleJobOperator.stop(jobExecution) on an executing ChunkOrientedStep causes an Optimistic Locking version conflict.

This happens because the SimpleJobOperator.stop() method, after calling stoppableStep.stop() at line #374 proceeds to explicitly call jobRepository.update(stepExecution). 

This update prematurely increments the database version of the StepExecution. 

Consequently, the main batch execution thread, which holds an outdated version of the StepExecution in memory, fails with an OptimisticLockingFailureException during its final persistence call in AbstractStep.execute().

## Environment
Spring Batch Version: 6.0.0
Spring Boot 4.0.0

## Steps to reproduce
1) Start a Spring Batch application with a long-running ChunkOrientedStep.
2) While the step is actively processing a chunk (inside the chunk transaction), call JobOperator.stop(jobExecution) from a separate thread or API endpoint.
3) The SimpleJobOperator.stop() call updates the DB, increasing the StepExecution version.(at line 375)
~4) The batch execution thread(Chunk processing thread) detects the terminateOnly flag and attempts a graceful exit from the chunk processing loop. (at ChunkOrientedStep.doExecute() line 362)~ ChunkOrientedStep doExecute() completed(not stopped - this is related https://github.com/spring-projects/spring-batch/issues/5114) 
5) The AbstractStep.execute() method attempts to save the final status of the step.(at line 327)
6) The job fails with an OptimisticLockingFailureException. and JobExecution.BatchStatus & ExitStatus set UNKNOWN 
7) so this JobExecution cannot restarted


## Expected behavior 
When JobOperator.stop() is called, the job should safely stop and transition to the STOPPED status without causing an OptimisticLockingFailureException or setting UNKNOWN status for restartability


## Actual Stack Trace
```java
org.springframework.dao.OptimisticLockingFailureException: Attempt to update step execution id=9 with wrong version (1), where current version is 2
	at org.springframework.batch.core.repository.dao.jdbc.JdbcStepExecutionDao.updateStepExecution(JdbcStepExecutionDao.java:254) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.repository.support.SimpleJobRepository.update(SimpleJobRepository.java:154) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
	at java.base/java.lang.reflect.Method.invoke(Method.java:580) ~[na:na]
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:359) ~[spring-aop-7.0.1.jar:7.0.1]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:190) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:158) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:370) ~[spring-tx-7.0.1.jar:spring-tx-7.0.1]
	at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:118) ~[spring-tx-7.0.1.jar:spring-tx-7.0.1]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:179) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:222) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at jdk.proxy2/jdk.proxy2.$Proxy117.update(Unknown Source) ~[na:na]
	at org.springframework.batch.core.step.AbstractStep.execute(AbstractStep.java:327) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.SimpleStepHandler.handleStep(SimpleStepHandler.java:131) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.AbstractJob.handleStep(AbstractJob.java:397) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.SimpleJob.doExecute(SimpleJob.java:129) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.AbstractJob.execute(AbstractJob.java:293) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.launch.support.TaskExecutorJobLauncher$1.run(TaskExecutorJobLauncher.java:220) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at java.base/java.lang.Thread.run(Thread.java:1583) ~[na:na]
```

I believe this flow analysis and stack trace strongly indicate a bug introduced by the implementation of StoppableStep on AbstractStep in Spring Batch 6. We hope this report is helpful in identifying and resolving the issue in future releases.

If you require any further information, such as a Minimal Complete Reproducible Example (MCRE) code or assistance with testing, please do not hesitate to ask!

Thank you for your hard work and for maintaining such a valuable framework.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-05

Thank you for reporting this! 

Is this the same as (or similar to) #5114?

### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-12-05

Thank you for the quick response!

No, my issue (#5120) is not the same as #5114

i'm anayizing  #5114 and found additional issue
I will leave a comment on https://github.com/spring-projects/spring-batch/issues/5114 

Please let me know if any additional information!

### コメント 3 by fmbenhassine

**作成日**: 2025-12-05

OK thank you for your quick feedback!

I will check both issues in details.

### コメント 4 by KILL9-NO-MERCY

**作成日**: 2025-12-05

Hi,

I have been analyzing the details of this issue further, specifically concerning the behavior described in spring-projects/spring-batch/issues/5114, and I needed to make a small correction regarding the Step execution.

I have updated step #4 in the "Steps to reproduce" section:
**AS-IS**: The batch execution thread (Chunk processing thread) detects the terminateOnly flag and attempts a graceful exit from the chunk processing loop. (at ChunkOrientedStep.doExecute() line 362)

**TO-BE**: ChunkOrientedStep.doExecute() completed (not stopped - this is related to stop() does not prevent upcoming steps to be executed anymore #5114)

While this specific behavioral detail doesn't change the immediate bug related to the stop() logic we discussed, it is an important clarification on how the ChunkOrientedStep terminates.

Also, I previously mentioned that this issue was unrelated to #5114. After re-evaluating, I must correct that statement: The resolution of this issue is indeed closely tied to the direction chosen in the comments of #5114. The solution path for our current problem hinges directly on which of the two scenarios is adopted, which commented in Issue #5114. Therefore, it's not accurate to say they are entirely disconnected.

### コメント 5 by KILL9-NO-MERCY

**作成日**: 2025-12-15

@fmbenhassine 
I've submitted PR #5165 to address this optimistic locking issue.

The changes synchronize the StepExecution version by fetching the latest state from the database before update, which prevents the version conflict between the stopping thread and the executing thread.

In my testing, the issue is resolved for both TaskletStep and ChunkOrientedStep during stop operations. However, I would appreciate it if you could cross-check for any potential side effects I might have missed.

Thank you!

