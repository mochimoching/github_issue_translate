# Intermittent OptimisticLockingFailureException when starting job using jobOperator.start() with asyncTaskExecutor

**Issue番号**: #5106

**状態**: closed | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

**関連リンク**:
- Commits:
  - [b024116](https://github.com/spring-projects/spring-batch/commit/b024116968ac5dd89ea84a8a3048d0e4a39d7519)
  - [76e723e](https://github.com/spring-projects/spring-batch/commit/76e723e41939b1ab6910f9ce8d61053abb1d0575)

## 内容

**Bug description**
Intermittent OptimisticLockingFailureException when starting job using jobOperator.start() with asyncTaskExecutor

**Environment**
Spring Boot 4.0.0
Spring Batch 6.0.0
Java 21

**Steps to reproduce**
1) Create a new Spring Boot project through the Initializr with Spring Batch and Spring Data Jpa selected.
2) Create a configuration class and annotate it with @EnableBatchProcessing and @EnableJdbcJobRepository
3) Implement a simple job and create jobOperator using asyncTaskExecutor 
4) Using jobOperator.start() to start the job 
5) Intermittent OptimisticLockingFailureException happend in the JdbcJobExecutionDao.updateJobExecution() 
6) Based on my debug, I found that Job instance is not inserted in the BATCH_JOB_EXECUTION table sometimes but job execution is launched in a new Thread using the asyncTaskExecutor (this is in the TaskExecutorJobLauncher class),  and unable to find the job execution record in table then OptimisticLockingFailureException is happend. 

**Expected behavior**
Job should run without issue always. 


## コメント

### コメント 1 by ahoehma

**作成日**: 2025-12-01

Not exactly what I'm fighting with :-) But I will watch the feedback here as well.

(I started this discussion: https://github.com/spring-projects/spring-batch/discussions/5121)

### コメント 2 by phactum-mnestler

**作成日**: 2025-12-17

We're seeing the same issue as described. I created a minimal reproducer here: https://github.com/phactum-mnestler/spring-batch-reproducer
Based on the stacktrace, it appears the issue is a race condition between the async runnable of the `TaskExecutorJobLauncher` and the enclosing `finally` clause:
```
org.springframework.dao.OptimisticLockingFailureException: Attempt to update job execution id=1 with wrong version (0), where current version is 1
	at org.springframework.batch.core.repository.dao.jdbc.JdbcJobExecutionDao.updateJobExecution(JdbcJobExecutionDao.java:302) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.repository.support.SimpleJobRepository.update(SimpleJobRepository.java:152) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
        ----- AOP traces skipped ---
	at jdk.proxy3/jdk.proxy3.$Proxy85.update(Unknown Source) ~[na:na]
	at org.springframework.batch.core.job.AbstractJob.updateStatus(AbstractJob.java:420) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.job.AbstractJob.execute(AbstractJob.java:289) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.launch.support.TaskExecutorJobLauncher$1.run(TaskExecutorJobLauncher.java:220) ~[spring-batch-core-6.0.1.jar:6.0.1]
```
The `finally`-clause was not present in Spring Batch 5.x, which only updated the job execution if the `Runnable` wasn't able to be scheduled.

We're seeing this issue persist even with the newly released 6.0.1 version

### コメント 3 by licenziato

**作成日**: 2025-12-17

I saw the same issue and the same root cause, as workaround setting the `ThreadPoolTaskExecutor` used by `JobOperator` as a single thread executor solved the race condition, waiting for a proper fix:

```
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

### コメント 4 by kizombaDev

**作成日**: 2025-12-19

We are currently unfortunately running into the same problem with Spring Batch 6.0.1, MongoDB, and a `ThreadPoolTaskExecutor`.

I start a job using `jobOperator.start(job, new JobParameters())` and immediately get a `DataIntegrityViolationException`.

I can confirm that the problem is caused by the call to `this.jobRepository.update(jobExecution);` in the finally block of the method
`org.springframework.batch.core.launch.support.TaskExecutorJobLauncher#launchJobExecution`.

I created a reproducer with a mongoDB: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

### コメント 5 by banseok1216

**作成日**: 2025-12-21

In TaskExecutorJobLauncher.launchJobExecution(..), consider removing the unconditional jobRepository.update(jobExecution) after successful submission to the TaskExecutor, and keep the update only in the TaskRejectedException path.

For accepted tasks, the job thread will update the JobExecution anyway; the extra launcher-thread update can race and avoid trigger OptimisticLockingFailureException.

```java
catch (TaskRejectedException e) {
    jobExecution.upgradeStatus(BatchStatus.FAILED);
    if (ExitStatus.UNKNOWN.equals(jobExecution.getExitStatus())) {
        jobExecution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
    }
    // keep this: the job thread will never run in this case
    this.jobRepository.update(jobExecution);
}

// no unconditional update here: for accepted tasks, the job thread persists JobExecution updates
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-21

Thank you all for reporting this issue and for providing analysis / reproducer!

This seems like a regression in #3637. I will plan the fix for the next patch version 6.0.2.

### コメント 7 by StefanMuellerCH

**作成日**: 2026-01-05

Same problem here, but the fix from [licenziato](https://github.com/licenziato) above did not help, as the `ThreadPoolTaskExecutor`, even with size 1, executes the job itself in another thread as the `TaskExecutorJobLauncher `calls the update. I had to switch to the `SyncTaskExecutor` for the bug to be solved:


```
@Bean
public JobOperatorFactoryBean jobOperator(JobRepository jobRepository) {
  var taskExecutor = new SyncTaskExecutor();
  var jobOperatorFactoryBean = new JobOperatorFactoryBean();
  jobOperatorFactoryBean.setJobRepository(jobRepository);
  jobOperatorFactoryBean.setTaskExecutor(taskExecutor);
  return jobOperatorFactoryBean;
}
```

Using the SyncTaskExecutor has considerable drawbacks, we cannot use this for production, so we have to wait for the fix.

