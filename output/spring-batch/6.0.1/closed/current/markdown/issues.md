# Spring Batch GitHub Issues

取得日時: 2026年01月06日 17:04:49

取得件数: 17件

---

## Issue #5037: Minor logging issue when a step or job completes instantly

**状態**: closed | **作成者**: janossch | **作成日**: 2025-10-20

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5037

**関連リンク**:
- Commits:
  - [249330b](https://github.com/spring-projects/spring-batch/commit/249330b2718492424c2df9b452279c9601c2802e)
  - [f3ccc74](https://github.com/spring-projects/spring-batch/commit/f3ccc7405c9d8f1c1f8a33fdfbbcbe143799e8f7)
  - [1d50d82](https://github.com/spring-projects/spring-batch/commit/1d50d829907a580fe3aea5b6a17859a418e478b9)

### 内容

**Bug description**
We found such below log lines in our production environment, which misses the duration information at the end of the line.

... `Job: [FlowJob: [name=...]] completed with the following parameters: [...] and the following status: [FAILED] in `

Digging into a little bit of the code, I found that when a job is finished
https://github.com/spring-projects/spring-batch/blob/11ec7f12e8e4477ae802a02ee72f69f78afbf25b/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/TaskExecutorJobLauncher.java#L221-L228

an info level log entry gets emitted by the framework. However if the start and the end date is essentially the same, the `BatchMetrics.formatDuration` method returns an empty `String` because of the `duration.isZero()` condition.

https://github.com/spring-projects/spring-batch/blob/11ec7f12e8e4477ae802a02ee72f69f78afbf25b/spring-batch-core/src/main/java/org/springframework/batch/core/observability/BatchMetrics.java#L69-L72

**Environment**
Java21 (temurin)
Spring Batch 5.2.2
File based H2 DB is used

**Steps to reproduce**
Start a lot of batch jobs which completes fast.

**Expected behavior**
Honestly I don't know, but at least a `0ms` would be better than nothing. Something like this:
`Job: [FlowJob: [name=...]] completed with the following parameters: [...] and the following status: [FAILED] in 0ms`

**Minimal Complete Reproducible example**

The below test fails for 5.2.2:
```
    @Test
    void testFormatDurationWhenCalculationReturnsZeroDuration() {
        var startDate = LocalDateTime.now();
        // create end date from the string representation of start date to ensure both dates are equal, but different references.
        // In reality there is another LocalDateTime.now() call, but that could return a different time, which could cause flaky tests.
        var endDate = LocalDateTime.parse(startDate.toString());
        var calculateDuration = BatchMetrics.calculateDuration(startDate, endDate);
        Assertions.assertNotNull(calculateDuration, "Calculated duration is a null reference!");
        var formattedDurationString = BatchMetrics.formatDuration(calculateDuration);
        Assertions.assertTrue(StringUtils.hasText(formattedDurationString), formattedDurationString);
    }
```


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-21

Thank you for reporting this!

> **Expected behavior**
> Honestly I don't know, but at least a `0ms` would be better than nothing.

Sure, makes sense. I planned the fix for the next patch release. Thank you for the PR as well 🙏

---

## Issue #5099: Partitioned step stops processing when first partition is finished in new chunk processing implementation

**状態**: closed | **作成者**: marbon87 | **作成日**: 2025-11-21

**ラベル**: type: bug, in: core, has: minimal-example, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5099

**関連リンク**:
- Commits:
  - [a2d61f8](https://github.com/spring-projects/spring-batch/commit/a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69)

### 内容

When using a step with local partitions, that have different amount of items, the step is finished when the first partition has done it's work. That lead's to unprocessed items in the other partitions.

Here is an example with a step and a test, that is failing with the new chunk processing implementation:

[partition-example.tar.gz](https://github.com/user-attachments/files/23675568/partition-example.tar.gz)

If you switch to the old chunk implemenation the test runs successfully.

### コメント

#### コメント 1 by KILL9-NO-MERCY

**作成日**: 2025-11-21

I happened to come across this issue and did some digging.

I'm not entirely sure if I've found the root cause, but here's what I observed:
Since ChunkOrientedStep.doExecute(StepExecution) is executed for each partition, it gets called 3 times in total. However, ChunkTracker.noMoreItems() — which is called when there are no more items to read — is only invoked once across all executions.

It seems like each partition execution might need its own ChunkTracker instance.

I could be wrong, so please verify this.

#### コメント 2 by fmbenhassine

**作成日**: 2025-11-24

Thank you for reporting this issue and for providing an example! The sample uses a `ResourcelessJobRepository` (the default in Spring Batch 6 / Spring Boot 4). This job repository implementation is not suitable for use cases involving the execution context in any way (including local partitioning, see its javadoc as well as the [reference docs](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html#_configuring_a_resourceless_jobrepository)).

That said, even with a JDBC job repository implementation there is an issue in `ChunkOrientedStep` as the chunk tracker is currently defined per instance while it should per thread (seems like we have a gap in our test suite as we currently test local partitioning with a simple tasklet and not with a chunk-oriented tasklet). I planned the fix for the next patch release.

#### コメント 3 by zhaozhiguang

**作成日**: 2025-11-28

I also encountered the same problem,When using Partitioner and JdbcPageItemReaderBuilder

#### コメント 4 by abstiger

**作成日**: 2025-11-28

I don’t think switching to thread-local solves the problem. What if a job-step is executed twice in the same thread?

I have encountered a similar issue. In a job, there is only one step, and the reader is JdbcCursorItemReader (which reads all users, assuming there are ten users), with a chunk size of 1.

run this job twice:

The first execution was successfully reading ten users and performing subsequent processing (at this point, the chunkTracker set `noMoreItems()`;).

The second execution skipped directly because `noMoreItems()`; had already been set.

maybe set it to true while step open in `ChunkOrientedStep` ?

```java
	@Override
	protected void open(ExecutionContext executionContext) throws Exception {
		this.compositeItemStream.open(executionContext);
		// set to true on every step open
		this.chunkTracker.get().moreItems = true;
	}

```



#### コメント 5 by kzander91

**作成日**: 2025-12-03

This bug is also the cause of #5126, and the fix committed here won't solve it, as explained by @abstiger.
There's another issue with the fix in that the `ThreadLocal` is never cleared again, so instead of flipping flags in `open()`, I would suggest to clear it in `close()`:
```java
	@Override
	protected void close(ExecutionContext executionContext) throws Exception {
		this.chunkTracker.remove(); // ensure that the next invocation instantiates a new instance, and avoid leaks
		this.compositeItemStream.close();
	}
```

#### コメント 6 by fmbenhassine

**作成日**: 2025-12-04

Thank you all for the feedback! 

@abstiger 

> I don’t think switching to thread-local solves the problem. What if a job-step is executed twice in the same thread?
 
It does, it is just the lifecycle of the thread bound chunk tracker that was not correctly managed when I introduced it in a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69. I have addressed that in 69665d83d8556d9c23a965ee553972a277221d83.

---

## Issue #5104: EmptyResultDataAccessException in JobRepository.findRunningJobExecutions for a completed job execution

**状態**: closed | **作成者**: A1exL | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5104

**関連リンク**:
- Commits:
  - [5750492](https://github.com/spring-projects/spring-batch/commit/57504927d912947ad1d15079b00d0969060db664)

### 内容

**Bug description**
`JobRepository.findRunningJobExecutions` throws an EmptyResultDataAccessException if there are no running job executions for a given job name and BATCH_JOB_EXECUTION table contains only COMPLETED or FAILED records (BATCH_JOB_EXECUTION.STATUS column value).

**Environment**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25
- Embedded H2 database (reproduces on any database)

**Steps to reproduce**
Preconditions:
JdbcJobExecutionDao is used. BATCH_JOB_EXECUTION and BATCH_JOB_INSTANCE tables are empty.
Have Spring Batch Job with name "SuccessfulJob".

1. Run this job, wait until it completes successfully.
After execution one record in BATCH_JOB_INSTANCE table will be created.
Also one record with STATUS=COMPLETED will be created in BATCH_JOB_EXECUTION table.
2. call `org.springframework.batch.core.repository.JobRepository.findRunningJobExecutions("SuccessfulJob")`

**Expected behavior**
An empty set is returned.

**Actual behavior**
An EmptyResultDataAccessException is thrown.


**Cause of the issue**
Root cause of the issue is the code in `JdbcJobExecutionDao.findRunningJobExecutions` method:
This code fragment
`getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE), Long.class, jobInstanceId)`
fails if there are **only** COMPLETED (or FAILED) records in BATCH_JOB_EXECUTION table for a given jobInstanceId
Code in `org.springframework.batch.core.repository.dao.jdbc.JdbcJobExecutionDao`
```				
private static final String GET_RUNNING_EXECUTION_FOR_INSTANCE = """
		SELECT E.JOB_EXECUTION_ID
		FROM %PREFIX%JOB_EXECUTION E, %PREFIX%JOB_INSTANCE I
		WHERE E.JOB_INSTANCE_ID=I.JOB_INSTANCE_ID AND I.JOB_INSTANCE_ID=? AND E.STATUS IN ('STARTING', 'STARTED', 'STOPPING')
		""";
		

public Set<JobExecution> findRunningJobExecutions(String jobName) {
	final Set<JobExecution> result = new HashSet<>();
	List<Long> jobInstanceIds = this.jobInstanceDao.getJobInstanceIds(jobName);
	for (long jobInstanceId : jobInstanceIds) {

		// throws EmptyResultDataAccessException if nothing is found
		long runningJobExecutionId = getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE),
				Long.class, jobInstanceId);

		JobExecution runningJobExecution = getJobExecution(runningJobExecutionId);
		result.add(runningJobExecution);
	}
	return result;
}
```

**Minimal Complete Reproducible example**
https://github.com/A1exL/spring-batch6-bugs
Please launch `JobRepositoryTests` and see the results


### コメント

#### コメント 1 by darckyn

**作成日**: 2025-11-26

Hi.

Same error here!
My database has BATCH_JOB_EXECUTION.STATUS with only COMPLETE in all lines

Environment

- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 21
- SqlServer 2019

In my source code, I use `findRunningJobExecutions` inside a Scheduled:

    @Scheduled(cron = CronConst.EVERY_FIVE_SECONDS, zone = SystemConst.ZONE_DEFAULT)
    public void launchValidateGarantiaJob() throws JobExecutionAlreadyRunningException, JobInstanceAlreadyCompleteException,
            InvalidJobParametersException, JobRestartException {
        var runningJobs = jobRepository.findRunningJobExecutions(validateGarantiaJob.getName());
        if (EmptyUtil.isEmpty(runningJobs)) {
            jobOperator.start(validateGarantiaJob, JobUtil.createJobParameters());
        } else {
            throw new JobExecutionAlreadyRunningException(validateGarantiaJob.getName());
        }
    }

#### コメント 2 by fmbenhassine

**作成日**: 2025-12-04

Thank you for reporting this issue and for providing a sample! Indeed this is a bug. I will plan the fix for the upcoming patch release.

---

## Issue #5105: @EnableMongoJobRepository fails with Invalid transaction attribute token: [SERIALIZABLE]

**状態**: closed | **作成者**: br05s | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5105

### 内容

**Bug description**
When using `@EnableMongoJobRepository` with `@EnableBatchProcessing`, you will receive an error saying `Invalid transaction attribute token: [SERIALIZABLE]`

**Environment**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25

**Steps to reproduce**
1. Create a new Spring Boot project through the Initializr with Spring Batch and Spring Data MongoDB selected.
2. Create a configuration class and annotate it with `@EnableBatchProcessing` and `@EnableMongoJobRepository`
3. Implement a simple job
4. Add MongoDB properties to `application.yml`

**Expected behavior**
Job should run without issue

**Minimal Complete Reproducible example**
`SimpleJobConfig.java`
```java
@EnableBatchProcessing
@EnableMongoJobRepository
@Configuration
public class SimpleJobConfig {

    @Bean
    Job simpleJob(Step simpleStep, JobRepository jobRepository) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(simpleStep)
                .build();
    }

    @Bean
    Step simpleStep(Tasklet simpleTasklet, PlatformTransactionManager transactionManager, JobRepository jobRepository) {
        return new StepBuilder("simpleStep", jobRepository)
                .tasklet(simpleTasklet, transactionManager)
                .build();
    }

    @Bean
    Tasklet simpleTasklet() {
        return (contribution, chunkContext) -> {
            println("test");
            return RepeatStatus.FINISHED;
        };
    }

    @Bean
    MongoTransactionManager transactionManager(MongoDatabaseFactory mongoDatabaseFactory) {
        return new MongoTransactionManager(mongoDatabaseFactory);
    }

}
```

`application.yml`
```yaml
spring:
  application:
    name: batch-mongo-demo
  mongodb:
    host: (removed)
    port: 27017
    database: batch
```

### コメント

#### コメント 1 by br05s

**作成日**: 2025-11-24

It looks like the problem is `BatchRegistrar` sets the property `isolationLevelForCreate` when configuring the Mongo job repository instead of `setIsolationLevelForCreateEnum` like the JDBC version does.

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

#### コメント 2 by banseok1216

**作成日**: 2025-12-07

I’m seeing the same issue with `@EnableBatchProcessing` + `@EnableMongoJobRepository`.

I can confirm that the root cause is the one you pointed out in `BatchRegistrar` (binding the `Isolation` enum to `isolationLevelForCreate` instead of the enum-based property), and there is some additional evidence from the Mongo default configuration.

`MongoDefaultBatchConfiguration` configures the `MongoJobRepositoryFactoryBean` like this:

```java
@Bean
@Override
public JobRepository jobRepository() throws BatchConfigurationException {
    MongoJobRepositoryFactoryBean jobRepositoryFactoryBean = new MongoJobRepositoryFactoryBean();
    try {
        jobRepositoryFactoryBean.setMongoOperations(getMongoOperations());
        jobRepositoryFactoryBean.setTransactionManager(getTransactionManager());
        jobRepositoryFactoryBean.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
        jobRepositoryFactoryBean.setValidateTransactionState(getValidateTransactionState());
        jobRepositoryFactoryBean.setJobKeyGenerator(getJobKeyGenerator());
        jobRepositoryFactoryBean.setJobInstanceIncrementer(getJobInstanceIncrementer());
        jobRepositoryFactoryBean.setJobExecutionIncrementer(getJobExecutionIncrementer());
        jobRepositoryFactoryBean.setStepExecutionIncrementer(getStepExecutionIncrementer());
        jobRepositoryFactoryBean.afterPropertiesSet();
        return jobRepositoryFactoryBean.getObject();
    }
    catch (Exception e) {
        throw new BatchConfigurationException("Unable to configure the default job repository", e);
    }
}
```

Here the isolation level is passed via the enum-based setter:

```java
jobRepositoryFactoryBean.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
```

So the `Isolation` value is clearly meant to go through `setIsolationLevelForCreateEnum`.

On the other hand, in `BatchRegistrar.registerMongoJobRepository`, the value from `@EnableMongoJobRepository#isolationLevelForCreate` (which is an `Isolation` enum) is currently bound to the **String** property `isolationLevelForCreate`:

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

This ends up invoking `setIsolationLevelForCreate(String)` internally and going through `TransactionAttributeEditor`, which expects tokens like `ISOLATION_SERIALIZABLE`. With the enum being converted to `"SERIALIZABLE"`, this leads to:

> Invalid transaction attribute token: [SERIALIZABLE]

For JDBC, the registrar already uses the enum-based property:

```java
Isolation isolationLevelForCreate = jdbcJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

and the default Mongo configuration (`MongoDefaultBatchConfiguration`) also uses `setIsolationLevelForCreateEnum`.

So it looks like the Mongo registrar should be using the same enum-based property. Changing it to:

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

fixes the issue for me.

To guard against regressions, I also added a small test in `BatchRegistrarTests` that bootstraps a context with:

```java
@Configuration
@EnableBatchProcessing
@EnableMongoJobRepository
static class MongoJobConfiguration {

    @Bean
    MongoOperations mongoTemplate() {
        return Mockito.mock(MongoOperations.class);
    }

    @Bean
    MongoTransactionManager transactionManager() {
        return Mockito.mock(MongoTransactionManager.class);
    }
}
```

and simply asserts that a `JobRepository` is created:

```java
@Test
@DisplayName("Mongo job repository should be configured successfully with @EnableMongoJobRepository")
void testMongoJobRepositoryConfiguredWithEnableMongoJobRepository() {
    AnnotationConfigApplicationContext context =
            new AnnotationConfigApplicationContext(MongoJobConfiguration.class);

    JobRepository jobRepository = context.getBean(JobRepository.class);
    Assertions.assertNotNull(jobRepository);
}
```

With the current code this test fails with `Invalid transaction attribute token: [SERIALIZABLE]`, and with the change to `isolationLevelForCreateEnum` it passes. I’ll open a PR with this change and the test.


#### コメント 3 by fmbenhassine

**作成日**: 2025-12-15

@br05s This is valid issue, thank you for reporting it.

Resolved in #5141 and will be shipped in the upcoming v6.0.1. Many thanks to @banseok1216 for the fix 🙏

---

## Issue #5114: stop() does not prevent upcoming steps to be executed anymore

**状態**: closed | **作成者**: andre-bugay | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5114

**関連リンク**:
- Commits:
  - [e5fbc2a](https://github.com/spring-projects/spring-batch/commit/e5fbc2a0387858f5f95009e3a032d2864398f9ac)
  - [29f5ecf](https://github.com/spring-projects/spring-batch/commit/29f5ecf567cc21b5ce3dd9a41283d227a85c3667)
  - [644d7e6](https://github.com/spring-projects/spring-batch/commit/644d7e6997c4e29822be580dab8e6f65713e17be)

### 内容

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


### コメント

#### コメント 1 by KILL9-NO-MERCY

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

#### コメント 2 by fmbenhassine

**作成日**: 2025-12-05

@andre-bugay @KILL9-NO-MERCY Thank you for raising this issue and for taking the time to analyse the root cause! Indeed, stopping a job seems to be broken, even though the [graceful shutdown sample](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/shutdown) was working as expected when I introduced it in d4a7dfd25f2782fba7a1563ab62aa116b4f6d33f. There seems to be a commit after that that broke the stop feature.. What bothers me is that that sample involves a manual step (sending the interruption signal to the process) which makes it difficult to detect regressions automatically on CI.

I will check that and plan the fix for the upcoming 6.0.1.

#### コメント 3 by fmbenhassine

**作成日**: 2025-12-12

> The solution will depend on whether Spring Batch Team decide to retain or revert this code modification.

I am not against reverting a change if it has introduced a regression. 

> As you pointed out, the commit [e5fbc2a](https://github.com/spring-projects/spring-batch/commit/e5fbc2a0387858f5f95009e3a032d2864398f9ac) introduced:

Reverting e5fbc2a0387858f5f95009e3a032d2864398f9ac does not seem to fix the issue, so probably scenario 1 is not the best option. I think this commit is the culprit: db6ef7b067e0daeee59c1baea03a0acfed4f5cfc, but I am still investigating.

> Therefore, if Spring Batch Team proceed with Scenario 2, a call to getJobRepository().update(stepExecution); must also be added to the ChunkOrientedStep implementation to ensure proper interruption.

@KILL9-NO-MERCY  Have you tried this patch? Because I also tried this and does not seem to help neither.

I would appreciate a patch in a PR if someone managed to fix the issue already (and avoid duplicate efforts).

#### コメント 4 by fmbenhassine

**作成日**: 2025-12-12

Just to give a bit more context: the attempts I shared in my previous comment led to optimistic locking exceptions (I used [this example](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/shutdown) for tests), so I have a doubt something related to locking could be involved (I am thinking of #5020, but I am probably wrong). cc @quaff . Probably a database sync in missing here: https://github.com/spring-projects/spring-batch/blob/main/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L476.

I will continue to investigate, but if someone managed to fix the issue already, then I would appreciate a patch in a PR to avoid duplicate efforts. Many thanks upfront 🙏

#### コメント 5 by quaff

**作成日**: 2025-12-15

> so I have a doubt something related to locking could be involved (I am thinking of [#5020](https://github.com/spring-projects/spring-batch/issues/5020), but I am probably wrong).

#5020 is related to multi-process which this issue doesn't mention.

#### コメント 6 by KILL9-NO-MERCY

**作成日**: 2025-12-15

@andre-bugay @fmbenhassine 

I've submitted PR #5165 to address this issue.

The PR fixes the `terminateOnly` flag setting by:
1. Detecting externally stopped StepExecution via `getStepExecution()` and checking `isStopped()` status
2. Synchronizing version and setting `terminateOnly` in `JobRepository.update(StepExecution)`
3. Adding `JobRepository.update(stepExecution)` call in ChunkOrientedStep to match TaskletStep behavior

As mentioned in #5120, my testing shows both #5120 (OptimisticLockingFailureException) and #5114 (terminateOnly not set) are resolved with these changes.

However, I would appreciate it if you could cross-check for any potential side effects I may have overlooked. Thank you!

---

## Issue #5115: MetaDataInstanceFactory.createStepExecution(JobParameters) does not propagate JobParameters to StepExecution

**状態**: closed | **作成者**: benelog | **作成日**: 2025-11-27

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5115

**関連リンク**:
- Commits:
  - [da16f6b](https://github.com/spring-projects/spring-batch/commit/da16f6b92ecc1b4d5ed0acb947df1dad923e590a)
  - [1a5b8d0](https://github.com/spring-projects/spring-batch/commit/1a5b8d0321fd6efd02c589b0711260f93fe9315f)
  - [8264ab1](https://github.com/spring-projects/spring-batch/commit/8264ab11b9fa1905da648f454a050dd058b3fda0)

### 内容

## Bug description
`StepExecution` instances created via `MetaDataInstanceFactory.createStepExecution(JobParameters)` do not reference the provided `JobParameters`.

This appears to be a side effect introduced by the following commit:

https://github.com/spring-projects/spring-batch/commit/90d895955d951156849ba6fa018676273fdbe2c4

## Environment
Spring Batch  v6.0.0

## Steps to reproduce
The following test case reproduces the bug:

```java
@Test
void testCreateStepExecutionJobParameters() {
    JobParameters parameters = new JobParametersBuilder()
        .addString("foo", "bar")
        .toJobParameters();

    StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(parameters);
    String paramValue = stepExecution.getJobExecution().getJobParameters().getString("foo");

    assertEquals("bar", paramValue);
}
```


### コメント

#### コメント 1 by benelog

**作成日**: 2025-12-13

@fmbenhassine

This issue did not occur in Spring Batch v5.2.x but newly appeared after upgrading to v6.0.0.

I am currently resolving it with the following workaround:

(When using Spring Batch v5.2.x)
```java
StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);
````

\-\>

(After upgrading to Spring Batch v6.0.0)

```java
JobExecution jobExecution = MetaDataInstanceFactory.createJobExecution("testJob", 0L, 0L, jobParameters);
StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobExecution, "testStep", 0L);
```

If the following PR is included in Spring Batch v6.0.1, it would help reduce the trial and error experienced by users upgrading the version and contribute to users feeling that v6.0.x is stable.

https://github.com/spring-projects/spring-batch/pull/5116


---

## Issue #5117: ExecutionContext not loaded when step execution is queried from the job repository

**状態**: closed | **作成者**: ruudkenter | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5117

### 内容

In Spring Batch 5.2.x the StepExecution returned from the SimpleJobExplorer returned a fully populated StepExecution, including the ExecutionContext.
 
Spring Batch 6.0.0,  is using a JobRepository for the same task [fetching the StepExecution](https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-integration/src/main/java/org/springframework/batch/integration/partition/StepExecutionRequestHandler.java#L48), however, that doesn't seem to populate the ExecutionContext for the StepExecution. It ultimately delegates to: [JdbcStepExecutionDao](https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/dao/jdbc/JdbcStepExecutionDao.java#L299) without loading the ExecutionContext from the BATCH_STEP_EXECUTION_CONTEXT table. Failing my remote partitioned batch job.
 
Not sure if this is intentional and I am missing out on something, but to me this seems to be an issue.

[Demonstration of the issue](https://github.com/ruudkenter/spring-batch-6-demo). 

NOTE: It does work when you switch to using ResourcelessJobRepository.
 
Regards
Ruud

### コメント

#### コメント 1 by ruudkenter

**作成日**: 2025-12-09

Issue is resolved by (https://github.com/spring-projects/spring-batch/pull/5147)

#### コメント 2 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue, which is valid! And indeed, #5147 resolves it and was merged.

The fix will be part of the upcoming 6.0.1 planned for next week.

---

## Issue #5120: StepExecution Update in SimpleJobOperator.stop() Causes JobExecution.BatchStatus.UNKNOWN after graceful stop

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-01

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5120

**関連リンク**:
- Commits:
  - [29f5ecf](https://github.com/spring-projects/spring-batch/commit/29f5ecf567cc21b5ce3dd9a41283d227a85c3667)
  - [f62da2b](https://github.com/spring-projects/spring-batch/commit/f62da2bd6a7a9459d809e86065877ac440130b70)
  - [644d7e6](https://github.com/spring-projects/spring-batch/commit/644d7e6997c4e29822be580dab8e6f65713e17be)
  - [09b0783](https://github.com/spring-projects/spring-batch/commit/09b07834ed86f4a11a51e118e665dc20156352c9)
  - [0feafa1](https://github.com/spring-projects/spring-batch/commit/0feafa15a73c4be4f990b627c914bb918118e96e)
  - [78ba896](https://github.com/spring-projects/spring-batch/commit/78ba896caa7020f1f7f972ae7b3dd469699a4922)
  - [984a057](https://github.com/spring-projects/spring-batch/commit/984a057f86c92b326782b964f949c0eb0eb805d4)

### 内容

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


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-12-05

Thank you for reporting this! 

Is this the same as (or similar to) #5114?

#### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-12-05

Thank you for the quick response!

No, my issue (#5120) is not the same as #5114

i'm anayizing  #5114 and found additional issue
I will leave a comment on https://github.com/spring-projects/spring-batch/issues/5114 

Please let me know if any additional information!

#### コメント 3 by fmbenhassine

**作成日**: 2025-12-05

OK thank you for your quick feedback!

I will check both issues in details.

#### コメント 4 by KILL9-NO-MERCY

**作成日**: 2025-12-05

Hi,

I have been analyzing the details of this issue further, specifically concerning the behavior described in spring-projects/spring-batch/issues/5114, and I needed to make a small correction regarding the Step execution.

I have updated step #4 in the "Steps to reproduce" section:
**AS-IS**: The batch execution thread (Chunk processing thread) detects the terminateOnly flag and attempts a graceful exit from the chunk processing loop. (at ChunkOrientedStep.doExecute() line 362)

**TO-BE**: ChunkOrientedStep.doExecute() completed (not stopped - this is related to stop() does not prevent upcoming steps to be executed anymore #5114)

While this specific behavioral detail doesn't change the immediate bug related to the stop() logic we discussed, it is an important clarification on how the ChunkOrientedStep terminates.

Also, I previously mentioned that this issue was unrelated to #5114. After re-evaluating, I must correct that statement: The resolution of this issue is indeed closely tied to the direction chosen in the comments of #5114. The solution path for our current problem hinges directly on which of the two scenarios is adopted, which commented in Issue #5114. Therefore, it's not accurate to say they are entirely disconnected.

#### コメント 5 by KILL9-NO-MERCY

**作成日**: 2025-12-15

@fmbenhassine 
I've submitted PR #5165 to address this optimistic locking issue.

The changes synchronize the StepExecution version by fetching the latest state from the database before update, which prevents the version conflict between the stopping thread and the executing thread.

In my testing, the issue is resolved for both TaskletStep and ChunkOrientedStep during stop operations. However, I would appreciate it if you could cross-check for any potential side effects I might have missed.

Thank you!

---

## Issue #5122: `MapJobRegistry` registers discovered Jobs by their bean name instead of their job name

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-02

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5122

**関連リンク**:
- Commits:
  - [184ac31](https://github.com/spring-projects/spring-batch/commit/184ac31f704935c6d49865839713cd3126ce7cd3)

### 内容

The changes made with #4855 ignore the _names_ of the discovered Jobs:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/support/MapJobRegistry.java#L63-L67
We see that the bean names are used instead of `Job#getName()`.
This should probably be changed to something like this:
```java
	@Override
	public void afterSingletonsInstantiated() {
		this.applicationContext.getBeansOfType(Job.class).values().forEach(this::register);
	}
```
Since `register()` throws a checked exception, the exact logic may need to be changed a bit.

---

My workaround:
```java
@Bean
MapJobRegistry jobRegistry(ObjectProvider<Job> jobs) {
    return new MapJobRegistry() {

        // Workaround for https://github.com/spring-projects/spring-batch/issues/5122
        @Override
        public void afterSingletonsInstantiated() {
            for (Job job : jobs) {
                try {
                    register(job);
                } catch (DuplicateJobException e) {
                    throw new IllegalStateException(e);
                }
            }
        }
    };
}
```

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-12-05

Thank you for reporting this issue. In fact, jobs should be registered by their name and not their bean name. This is an oversight from my side, I will fix that in 6.0.1.

---

## Issue #5123: Incorrect deprecation warning in `JobOperatorTestUtils.getJob()`

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-02

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5123

**関連リンク**:
- Commits:
  - [4216a0a](https://github.com/spring-projects/spring-batch/commit/4216a0a5834d90f0063cfe6ec32bc45c1e9d260b)

### 内容

`JobOperatorTestUtils` does not override and "un-deprecate" `getJob()`.
This causes unnecessary deprecation warnings to be raised for clients.

---

## Issue #5126: `ChunkOrientedStep.ChunkTracker` is not reset after step, allowing only a single execution of a particular step

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-03

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5126

**関連リンク**:
- Commits:
  - [69665d8](https://github.com/spring-projects/spring-batch/commit/69665d83d8556d9c23a965ee553972a277221d83)

### 内容

**Bug description**
`ChunkOrientedStep.doExecute()` loops until `chunkTracker.moreItems()` no longer returns `true`:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L359-L375

After the reader is exhausted, the `chunkTracker` switches to `false`, but that flag is never reset back to `true`. The consequence is that starting with the second invocation of the step, it will exit immediately and never do anything because `chunkTracker.moreItems()` still returns `false`.

**Environment**
Spring Batch 6.0.0

**Steps to reproduce**
1. Configure a job with a chunk-oriented step.
2. Run the job.
3. Run the job again.

**Expected behavior**
The step is executed both times.

**Minimal Complete Reproducible example**
[demo14.zip](https://github.com/user-attachments/files/23903365/demo14.zip)
Run with `./mvnw test`

The reproducer has a test that invokes the job three times. The first invocation starts chunk processing, both subsequent invocations skip it. This is also shown in the logs, where the first execution prints logs like this:
```
Job: [SimpleJob: [name=job]] launched with the following parameters: [{JobParameter{name='batch.random', value=7960112850225085599, type=class java.lang.Long, identifying=true}}]
Executing step: [step]
Reader was called, returning item
Reader was called, returning null
Writing chunk: [items=[item], skips=[]]
Step: [step] executed in 5ms
Job: [SimpleJob: [name=job]] completed with the following parameters: [{JobParameter{name='batch.random', value=7960112850225085599, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 22ms
```

While the subsequent invocations print logs like this:
```
Job: [SimpleJob: [name=job]] launched with the following parameters: [{JobParameter{name='batch.random', value=-1299334786035736075, type=class java.lang.Long, identifying=true}}]
Executing step: [step]
Step: [step] executed in
Job: [SimpleJob: [name=job]] completed with the following parameters: [{JobParameter{name='batch.random', value=-1299334786035736075, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 6ms
```

(Nitpick: When the step duration is zero, we get a message with a missing duration: `Step: [step] executed in`) -> #5037

---

My current workaround is to declare all `Job` and `Step` beans with `@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)`. I then implemented my own `JobRegistry` that retrieves each job on demand from the `BeanFactory` to ensure that fresh instances are used for each run.

### コメント

#### コメント 1 by abstiger

**作成日**: 2025-12-03

https://github.com/spring-projects/spring-batch/issues/5099#issuecomment-3588361319

#### コメント 2 by Jaraxxuss

**作成日**: 2025-12-04

facing same issue when launching same job multiple times in test method

#### コメント 3 by fmbenhassine

**作成日**: 2025-12-04

Thank you for reporting this issue and for providing a minimal example. Indeed, the lifecycle of the thread bound chunk tracker is incorrect when I introduced it in #5099. I will fix that in the upcoming patch release.

Just a side note: you have reported a couple issues and shared feedback on v6 and I appreciate that🙏 I was expecting some bumps and edge cases in 6.0.0 (as with every overhaul), but I am priortizing to stabilise things in 6.0.1. I will also come back to you asap to help on your [modularisation request](https://github.com/spring-projects/spring-batch/issues/5072#issuecomment-3575523924) . Thank you for your comprehension.

#### コメント 4 by kzander91

**作成日**: 2025-12-04

@fmbenhassine sure thing! Usually I'm trying to give feedback earlier during the milestone phases, but this time it wasn't feasible for me due to the modularisation, where I was basically stuck.
I personally have already migrated to using a single context (but other's may still need guidance of course), which is why I have been able to test the v6 more thoroughly now.

#### コメント 5 by fmbenhassine

**作成日**: 2025-12-04

@kzander91 The reproducer you provided inspired me to create this: b58c8429bcad782702fd4f1015b9dcc984b3de2b. Thank you for the inspiration 😉

---

## Issue #5127: Fault-tolerant step: `retry(Class)` traverses exception causes, `skip(Class)` does not

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-03

**ラベル**: type: bug, in: core, has: minimal-example, related-to: fault-tolerance

**URL**: https://github.com/spring-projects/spring-batch/issues/5127

**関連リンク**:
- Commits:
  - [8cade4d](https://github.com/spring-projects/spring-batch/commit/8cade4d656f79646ed99ba68cd6e8b77ee0fe862)
  - [2c57f8d](https://github.com/spring-projects/spring-batch/commit/2c57f8d13e6f8fda7b89cfaa9b9668209bc6ee54)
  - [5edb62f](https://github.com/spring-projects/spring-batch/commit/5edb62f0c818f4505804b46b45f5843556e6e826)

### 内容

**Bug description**
`skip(Class)` and `retry(Class)` behave inconsistently in that `skip(SkippableException.class)` does _not_ cause `throw new RuntimeException(new SkippableException())` to be skipped, but `retry(SkippableException.class)` _does_ inspect the cause and causes the same expression to be retried.

The expectation would be that exception matching in both `RetryPolicy` and `SkipPolicy` behave consistently (ideally aligned with `RetryPolicy`, in that causes are traversed).

The underlying reason for that is the switch to the new retry support from Framework, which always traverses causes (as it happens, a feature that I have requested myself 🙃): spring-projects/spring-framework#35583

**Environment**
Spring Batch 6.0.0

**Steps to reproduce**
1. Configure fault-tolerant step that skips and retries the same exception type.
2. Throw another exception with a skippable exception as the cause.

**Expected behavior**
The exception is both retried and then skipped (after retry exhaustion).

**Minimal Complete Reproducible example**
Reproducer: [demo14.zip](https://github.com/user-attachments/files/23907601/demo14.zip)
Run with `./mvnw test`

The project has a step like this:
```java
@Bean
Step step() {
    return new StepBuilder("step", jobRepository)
            .chunk(5)
            .transactionManager(transactionManager)
            .faultTolerant()
            .retry(SkippableException.class)
            .retryLimit(1)
            .skip(SkippableException.class)
            .skipLimit(1)
            .reader(new ListItemReader<>(List.of("item")))
            .writer(_ -> {
                throw new RuntimeException(new SkippableException());
            })
            .build();
}

static class SkippableException extends RuntimeException {

}
```

A test then launches and expects successful completion and a skip count of 1.

---
With Spring Batch 5, I was using a `LimitCheckingItemSkipPolicy` with a `BinaryExceptionClassifier` (from spring-retry) that was configured to traverse causes. However this is now deprecated and no equivalent replacement exists (apart from fully reimplementing my own `SkipPolicy`.

---

While debugging this, I found another, likely related issue:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/skip/LimitCheckingExceptionHierarchySkipPolicy.java#L50-L54
Note how the logic is inverted in the case of `skipCount < 0` (which is the case when the `SkipPolicy` is queried directly after a retryable exception happend). In that case, non-skippable exceptions are classified as skippable, due to `!isSkippable(t)`.

### コメント

#### コメント 1 by kzander91

**作成日**: 2025-12-03

After more debugging, I'm getting more confused, perhaps the logic here is inverted as well?
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L688-L702
Why is `this.skipPolicy.shouldSkip()` negated? This error, which is logged when the `SkipPolicy` _does_ indicate a skip, also indicates that the inverse was intended:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L700


#### コメント 2 by fmbenhassine

**作成日**: 2025-12-16

Thank you for reporting this issue and for providing an example! Indeed, that negation in `LimitCheckingExceptionHierarchySkipPolicy` and its inversion in `ChunkOrientedStep` are confusing and should be fixed.

I will try to fix that for tomorrow's planned 6.0.1 release (which is unlikely given how busy my day is today), otherwise I will plan it for 6.0.2, unless someone manages to contribute a fix in a timely manner. Here is a failing test with the latest main to add in `ChunkOrientedStepTests`:


```java
@Test
void testSkippableExceptionsTraversal() throws Exception {
	// given
	class SkippableException extends RuntimeException {

	}
	ItemReader<String> reader = new ListItemReader<>(List.of("item1"));
	ItemWriter<String> writer = chunk -> {
		throw new RuntimeException(new SkippableException());
	};

	JobRepository jobRepository = new ResourcelessJobRepository();
	ChunkOrientedStep<String, String> step = new StepBuilder("step", jobRepository).<String, String>chunk(1)
		.reader(reader)
		.writer(writer)
		.faultTolerant()
		.retry(SkippableException.class)
		.retryLimit(1)
		.skip(SkippableException.class)
		.skipLimit(1)
		.build();

	JobInstance jobInstance = new JobInstance(1L, "job");
	JobExecution jobExecution = new JobExecution(1L, jobInstance, new JobParameters());
	StepExecution stepExecution = new StepExecution(1L, "step", jobExecution);

	// when - execute step
	step.execute(stepExecution);

	// then - should skip the exception thrown by the writer
	ExitStatus stepExecutionExitStatus = stepExecution.getExitStatus();
	assertEquals(ExitStatus.COMPLETED.getExitCode(), stepExecutionExitStatus.getExitCode());
	assertEquals(1, stepExecution.getSkipCount());
}
```

---

> The underlying reason for that is the switch to the new retry support from Framework, which always traverses causes (as it happens, a feature that I have requested myself 🙃) : https://github.com/spring-projects/spring-framework/issues/35583

Yes I saw that congrats ! You are doing an amazing job with all your contributions across the portfolio, really appreciated 🙏

> The underlying reason for that is the switch to the new retry support from Framework

as it happens, a feature that I have contributed myself 🙃: https://github.com/spring-projects/spring-framework/pull/34716

#### コメント 3 by therepanic

**作成日**: 2025-12-16

Hi, @fmbenhassine! Thank you for all your work on this project!

You wrote that you probably won't have time to work on this, so I decided to do PR today. Maybe you'll be able to review it and, if necessary, polish it up and release it directly in the new 6.0.1 release. In any case, I think it needs to be fixed in 6.0.2. I also left a couple of comments. PTAL https://github.com/spring-projects/spring-batch/pull/5171.


#### コメント 4 by fmbenhassine

**作成日**: 2025-12-16

> You wrote that you probably won't have time to work on this, so I decided to do PR today.

This is so kind! Thank you very much for your help 🙏

I will take a loop at your PR.

---

## Issue #5138: Step execution no longer persisted after partitioner creates the context

**状態**: closed | **作成者**: brian-mcnamara | **作成日**: 2025-12-05

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5138

**関連リンク**:
- Commits:
  - [d983f71](https://github.com/spring-projects/spring-batch/commit/d983f71da9cf8fa014d5cb2657174a84e966c17c)
  - [1da2f28](https://github.com/spring-projects/spring-batch/commit/1da2f28b4c1a855feed5f10ad70b708ead061305)
  - [412158a](https://github.com/spring-projects/spring-batch/commit/412158afd9f8576b323d445212ed9e8f76c4bd84)
  - [60bf5b4](https://github.com/spring-projects/spring-batch/commit/60bf5b42bb6bee89a180ad321397c09b1c3999dc)
  - [cc2d57f](https://github.com/spring-projects/spring-batch/commit/cc2d57fde1cc603fc6d18defcc3eee1807e2adcd)
  - [a8961a6](https://github.com/spring-projects/spring-batch/commit/a8961a6770a78cf94eee2f5d270f280751d2092d)
  - [e64383d](https://github.com/spring-projects/spring-batch/commit/e64383d8eeab77a5894657cfa2b343bffca54979)

### 内容

**Bug description**
With [this change](https://github.com/spring-projects/spring-batch/commit/90d895955d951156849ba6fa018676273fdbe2c4#diff-1ccc98868257080253b51baded74a755478f3f85f754e0dc8ef05144ecd7dc02), a steps context is no longer persisted inside SimpleStepExecutionSplitter.java, causing the execution context created by a partitioner to be lost, preventing a remote worker from loading the created context. Specifically the call to jobRepository.addAll prior to batch 6 ensured the context was persisted

Specifically, after the contexts are created, MessageChannelPartitionHandler.doHandle is responsible to create and send the message, when the remote worker receives the message, it loads the steps through the job repository.

**Environment**
Spring boot 4.0.0, batch 6.0.0, batch-integration 6.0.0, JDK21

**Steps to reproduce**

See https://github.com/brian-mcnamara/SpringBatch6/blob/main/src/main/java/com/example/batchpartitionbug/BatchPartitionBugApplication.java

(can be run with `./gradlew run`) Specifically note line 91 which should get the context from the partitioner on line 197

This bug is seen with a partitioned step using message channels for delivery and a persistence layer for the jobRepository. 


**Expected behavior**

The partitioner should initialize the step contexts on the controller and update the step in the repository. This enabling the worker to load the step from the repository and use the context created earlier


### コメント

#### コメント 1 by quaff

**作成日**: 2025-12-08

My application failed to start due to `@Value("#{stepExecutionContext['xxx']}")` is null after upgrade to Spring Boot 4.0.

#### コメント 2 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue and for providing an example! This is a valid issue. It seems like we have a gap in our remote partitioning [tests](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/remote).. I will check that. I planned the fix for the upcoming 6.0.1 release.

#### コメント 3 by brian-mcnamara

**作成日**: 2025-12-10

Thank you both for the quick turn around, and all your work!

---

## Issue #5139: Enhance `ResourcelessJobRepository` implementation for testing

**状態**: closed | **作成者**: benelog | **作成日**: 2025-12-07

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5139

### 内容

## Background

I understand the design intent behind `ResourcelessJobRepository`, based on the following issue:

* [https://github.com/spring-projects/spring-batch/issues/4679](https://github.com/spring-projects/spring-batch/issues/4679)

 However, I believe there are a few targeted enhancements that would make this class much more useful in tests, without violating the original design goals.

In a single application context, `ResourcelessJobRepository` cannot run the same job multiple times. This limitation is acceptable as long as users understand it, but in tests it can become a constraint.

For example, the following test runs the same job with different `JobParameters` using `JobOperatorTestUtils`, but cannot rely on `ResourcelessJobRepository`:

```java
@SpringBootTest("spring.batch.job.enabled=false")
@SpringBatchTest
class HelloParamJobTest {

  @Autowired
  JobOperatorTestUtils testUtils;

  @BeforeEach
  void prepareTestUtils(@Autowired @Qualifier("helloParamJob") Job helloParamJob) {
    testUtils.setJob(helloParamJob);
  }

  @Test
  void startJob() throws Exception {
    JobParameters params = testUtils.getUniqueJobParametersBuilder()
        .addLocalDate("helloDate", LocalDate.of(2025, 7, 28))
        .toJobParameters();
    JobExecution execution = testUtils.startJob(params);
    assertThat(execution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);
  }

  @Test
  void startJobWithInvalidJobParameters() {
    JobParameters params = testUtils.getUniqueJobParametersBuilder()
        .addLocalDate("goodDate", LocalDate.of(2025, 7, 28))
        .toJobParameters();
    assertThatExceptionOfType(InvalidJobParametersException.class)
        .isThrownBy(() -> testUtils.startJob(params))
        .withMessageContaining("do not contain required keys: [helloDate]");
  }
}
```

## Known solutions

I am aware of several existing workarounds for this limitation:

* Register `ResourcelessJobRepository` as a prototype-scoped bean.
* Use an in-memory database together with a JDBC-based `JobRepository`.
* Use `@DirtiesContext` (or similar) to refresh the `ApplicationContext` before each test.

However, all of these come with trade-offs, such as:

* Additional complexity in object wiring and dependencies.
* Extra configuration overhead.
* Slower test execution due to frequent context refreshes.

In particular, as mentioned in this comment:

* [https://github.com/spring-projects/spring-batch/issues/5118#issuecomment-3604092261](https://github.com/spring-projects/spring-batch/issues/5118#issuecomment-3604092261)

calls to `ResourcelessJobRepository#getJobInstance(String, JobParameters)` have caused test scenarios that worked well with  Spring Batch v5.2 to become impossible when upgrading to v6.0.

In such cases, users may see an error like:

```text
Message: A job instance already exists and is complete for identifying parameters={JobParameter{name='batch.random', value=4546055881725385948}
```

This can be confusing because the job name and/or `JobParameters` are actually different, yet the repository still resolves them to the same `JobInstance`. This also feels misaligned with Spring Batch's conceptual model, where a `JobInstance` is uniquely identified by a job name and its `JobParameters`.

## Proposed enhancements

To address these issues while preserving the original design, I would like to propose the following enhancements to `ResourcelessJobRepository`:

### 1. Filter return values based on job name, IDs, and parameters

For the methods below, compare the incoming arguments (`jobName`, `instanceId`, `executionId`, `JobParameters`, etc.) with the values held in the internal `JobInstance` and `JobExecution` fields, and filter return values accordingly:

* `getJobInstances(String jobName, int start, int count)`
* `findJobInstances(String jobName)`
* `getJobInstance(long instanceId)`
* `getLastJobInstance(String jobName)`
* `getJobInstance(String jobName, JobParameters jobParameters)`
* `getJobInstanceCount(String jobName)`
* `getJobExecution(long executionId)`
* `getLastJobExecution(String jobName, JobParameters jobParameters)`
* `getLastJobExecution(JobInstance jobInstance)`
* `getJobExecutions(JobInstance jobInstance)`

Some methods already have comments like `// FIXME should return null if the id is not matching`, which suggest that this kind of filtering was already considered. Even if only a subset of these methods were updated, the observable behavior might be acceptable in practice. However, for conceptual consistency and to future-proof the implementation, I believe it would be better to have a systematic comparison of `jobName`, `jobInstanceId`, etc., across the class.

### 2. Add methods to delete the current JobInstance and JobExecution

Add the ability to drop the currently held `JobInstance` and `JobExecution` from `ResourcelessJobRepository`:

* `deleteJobInstance(JobInstance jobInstance)`
* `deleteJobExecution(JobExecution jobExecution)`

If these methods are introduced, tests could intentionally delete the just-run `JobInstance` or `JobExecution` to reuse the same `ResourcelessJobRepository` instance in a more flexible way. For example:

```java
@Autowired
JobOperatorTestUtils testUtils;

@Autowired
JobRepository repository;

@BeforeEach
void prepareTestUtils(@Autowired @Qualifier("helloParamJob") Job helloParamJob) {
  testUtils.setJob(helloParamJob);
}

@Test
void startJob() throws Exception {
  JobParameters params = testUtils.getUniqueJobParametersBuilder()
      .addLocalDate("helloDate", LocalDate.of(2025, 7, 28))
      .toJobParameters();
  JobExecution execution = testUtils.startJob(params);
  assertThat(execution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);

  // Explicitly clear the current JobInstance for the next test
  repository.deleteJobInstance(execution.getJobInstance());
}
```

These two enhancements together would:

* Make the implementation more faithful to the JobRepository interface contract.
  * Reduce surprising behavior where different jobs/parameters map to the same `JobInstance`.
* Make `ResourcelessJobRepository` more useful in test scenarios, especially when upgrading from Spring Batch 5.x to 6.x.
* Maintain the original in-memory, single-instance nature of `ResourcelessJobRepository`.

I would be happy to open a PR or further refine this proposal based on feedback from the maintainers.


### コメント

#### コメント 1 by arey

**作成日**: 2025-12-09

When I migrated from Spring Batch 5.x to 6.0.0, I encountered the same issue as @benelog :

> Message: A job instance already exists and is complete for identifying parameters={JobParameter{name='batch.random', value=4546055881725385948}

My unit tests using `SpringBatchTest` failed when I tried to execute more than one job.

To avoid the context becoming dirty between the two test methods, I used some tricks to bypass the limitation of the `ResourcelessJobRepository` and override the `deleteJobExecution` method. 

I hope we could improve the `ResourcelessJobRepository` implementation and remove by removing the `FIXME` and implementing `UnsupportedOperationException` of the `JobRepository` interface.

```java
    @BeforeEach
     void setUp() throws IOException {
      var currentJobExecution =jobRepository.getJobExecution(1L);  // arbitrary ID
        if (currentJobExecution != null) {
            jobRepository.deleteJobExecution(currentJobExecution);
        }
    }

  @Configuration
    static class ProgrammaticTestConfiguration extends DefaultBatchConfiguration {

        @Override
        @Bean
        public @NonNull JobRepository jobRepository() {
            return new MyResourcelessJobRepository();
        }

    }

    static class MyResourcelessJobRepository extends ResourcelessJobRepository {

        @Override
        public void deleteJobExecution(@org.jspecify.annotations.Nullable JobExecution jobExecution) {
            try {
                var jobExecutionField = ResourcelessJobRepository.class.getDeclaredField("jobExecution");
                jobExecutionField.setAccessible(true);
                jobExecutionField.set(this, null);

                var jobInstanceField = ResourcelessJobRepository.class.getDeclaredField("jobInstance");
                jobInstanceField.setAccessible(true);
                jobInstanceField.set(this, null);
            } catch (NoSuchFieldException | IllegalAccessException e) {
                throw new RuntimeException(e);
            }
        }
    }
```

#### コメント 2 by benelog

**作成日**: 2025-12-10

@arey
I had the same thought and have incorporated it into the following pull request:
https://github.com/spring-projects/spring-batch/pull/5140

#### コメント 3 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue! There is no doubt, `ResourcelessJobRepository` should be updated to fix the FIXMEs (😅) and implement default methods from the `JobRepository` interface (including meta-data deletion methods). I will merge #5140  which LGTM 👍 

Once that in place, and since you are using test utilities provided by Spring Batch, you should use the `JobRepositoryTestUtils` instead of the `JobRepository` directly (similar to using `JobOperatorTestUtils` instead of `JobOperator`):

```diff
@Autowired
JobOperatorTestUtils testUtils;

@Autowired
--JobRepository repository;
++JobRepositoryTestUtils repositoryUtils;

@BeforeEach
void prepareTestUtils(@Autowired @Qualifier("helloParamJob") Job helloParamJob) {
  testUtils.setJob(helloParamJob);
++  repositoryUtils.removeJobExecutions();
}

@Test
void startJob() throws Exception {
  JobParameters params = testUtils.getUniqueJobParametersBuilder()
      .addLocalDate("helloDate", LocalDate.of(2025, 7, 28))
      .toJobParameters();
  JobExecution execution = testUtils.startJob(params);
  assertThat(execution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);

--  // Explicitly clear the current JobInstance for the next test
-- repository.deleteJobInstance(execution.getJobInstance());
}
```

That said, the `ResourcelessJobRepository` is designed for a very specific use case: a single execution of a Spring Batch job. It does exactly that (and I believe it does it very well as it performs two orders of magnitude better than any other repository implementation). This is mentioned in its Javadoc as well as the [reference docs](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html#_configuring_a_resourceless_jobrepository). So using it for anything else than what it was designed for is incorrect, including using it in tests without proper lifecycle management. In fact, the `ResourcelessJobRepository` is very lightweight and can be defined as a prototype bean in your test context. Every job can use a different instance of it and this is completely fine. I think of it like a virtual thread but for jobs: you can have as many disposable resourcessless job repositories as needed, no need to reuse them or pool them, etc. They will be GCed anyway. 

#### コメント 4 by benelog

**作成日**: 2025-12-10

@fmbenhassine
Thank you for your feedback and for considering my PR favorably.

First of all, this is quite straightforward, but I wanted to leave a note here for people who might refer to this issue when using `JobRepositoryTestUtils.removeJobExecutions()` with Spring Batch 6.0.0.

[`JobRepositoryTestUtils.removeJobExecutions()`](https://github.com/spring-projects/spring-batch/blob/main/spring-batch-test/src/main/java/org/springframework/batch/test/JobRepositoryTestUtils.java#L154) eventually calls [`JobRepository.removeJobExecution(JobExecution)`](https://github.com/spring-projects/spring-batch/blob/main/spring-batch-core/src/main/java/org/springframework/batch/core/repository/JobRepository.java#L326). 
In v6.0.0, `ResourcelessJobRepository` does not implement `removeJobExecution(JobExecution)`, so the default method implementation in `JobRepository` is invoked and an `UnsupportedOperationException` is thrown. 

Therefore, unless `removeJobExecution(JobExecution)` is implemented as in [https://github.com/spring-projects/spring-batch/pull/5140](https://github.com/spring-projects/spring-batch/pull/5140), calling `JobRepositoryTestUtils.removeJobExecutions()` will result in an `UnsupportedOperationException`. 
I initially tried that approach as well, and it failed for this reason. In the example code in the description, I chose not to use `JobRepositoryTestUtils` so that the call chain would be expressed more directly.

Also, if we think ahead to a future where the `JobRepository` used in tests might be switched from `ResourcelessJobRepository` to another implementation,  I believe there are cases where it is beneficial to delete only the single `JobExecution` created by the current test instead of clearing all executions.
In an environment where the database used for tests is shared across multiple developers, wiping all `JobExecution` records could lead to unintended side effects.

Adding an implementation of methods such as `ResourcelessJobRepository.removeJobExecution(JobExecution)` would, as described above, improve the usability of `JobRepositoryTestUtils` and at the same time make the `JobRepository` contract more fully implemented.

Thank you as well for reiterating the design intent that `ResourcelessJobRepository` can be registered as a prototype bean for testing.
It is certainly possible to define a separate `ApplicationContext` for tests where the same job needs to be executed repeatedly, but I feel there are trade-offs in terms of convenience. 
If the implementation of `ResourcelessJobRepository.removeJobExecution(JobExecution)` proposed in this PR is adopted, I expect it will help address these concerns.


#### コメント 5 by fmbenhassine

**作成日**: 2025-12-11

Resolved with #5140. Thank you for raising the issue and contributing a PR 🙏

#### コメント 6 by phactum-mnestler

**作成日**: 2025-12-15

For anyone finding this issue the same way as me:
We're using the Spring Boot auto configuration, and after the upgrade to Spring Boot 4 we suddenly had both this issue and #5108, as the framework suddenly provided `ResourcelessJobRepository` instead of `SimpleJobRepository`. Adding an additional dependency for `spring-boot-starter-batch-jdbc` fixed the issue for us.

---

## Issue #5150: `RemotePartitioningWorkerStepBuilder` doesn't override all configuration methods from `StepBuilder`

**状態**: closed | **作成者**: quaff | **作成日**: 2025-12-09

**ラベル**: type: bug, in: integration

**URL**: https://github.com/spring-projects/spring-batch/issues/5150

**関連リンク**:
- Commits:
  - [5e3df33](https://github.com/spring-projects/spring-batch/commit/5e3df332ab1831ac90d4e8234b52d3ce05601244)
  - [f04f663](https://github.com/spring-projects/spring-batch/commit/f04f6636362fad92c0a741b0785af699535a5d99)
  - [37a39e2](https://github.com/spring-projects/spring-batch/commit/37a39e2d5d02f02ee4e73400a4ff5a9cf6f850be)

### 内容

**Bug description**

`MessageDispatchingException` raised after migration:

```
2025-12-09T11:03:05.207+08:00 ERROR 26960 --- [        task-12] o.s.integration.handler.LoggingHandler   : org.springframework.integration.MessageDispatchingException: Dispatcher has no subscribers, failedMessage=GenericMessage [payload=StepExecutionRequest: [stepExecutionId=14, stepName=importCustomerWorkerStep], headers={sequenceNumber=9, kafka_offset=3, sequenceSize=10, kafka_consumer=org.springframework.kafka.core.DefaultKafkaConsumerFactory$ExtendedKafkaConsumer@b5009fc, kafka_timestampType=CREATE_TIME, correlationId=1:importCustomerWorkerStep, id=ff913842-1559-3203-f6ad-d1af28690380, kafka_receivedPartitionId=2, kafka_receivedTopic=worker, kafka_receivedTimestamp=1765249385033, kafka_groupId=spring-batch-remote-partitioning-kafka, timestamp=1765249385206}]
	at org.springframework.integration.dispatcher.UnicastingDispatcher.doDispatch(UnicastingDispatcher.java:156)
	at org.springframework.integration.dispatcher.UnicastingDispatcher$1.run(UnicastingDispatcher.java:131)
	at org.springframework.integration.util.ErrorHandlingTaskExecutor.lambda$execute$0(ErrorHandlingTaskExecutor.java:64)
```

**Steps to reproduce**

Upgrade from deprecated

```java
stepBuilderFactory.get(stepName).inputChannel(inputChannel).chunk(CHUNK_SIZE, transactionManager)
```
to

```java
stepBuilderFactory.get(stepName).inputChannel(inputChannel).chunk(CHUNK_SIZE).transactionManager(transactionManager)
```


---

## Issue #5152: Class JobParametersInvalidException mentioned in "Spring Batch 6.0 Migration Guide" but is not available in 6.0.0

**状態**: closed | **作成者**: sebeichholz | **作成日**: 2025-12-09

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5152

### 内容

The [Spring Batch 6.0 Migration Guide](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide) says that the class **JobParametersInvalidException** was moved to a new package.

The class was in 6.0.0-M3 , but in 6.0.0 the class appears to have been renamed to "InvalidJobParametersException".

So perhaps the Migration Guide should be updated. Thanks!

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue! Indeed, that class was renamed as part of #5013.

I fixed the migration guide accordingly.

---

## Issue #5172: Local Chunking: BatchStatus remains COMPLETED when worker thread write fails

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-17

**ラベル**: type: bug, in: integration

**URL**: https://github.com/spring-projects/spring-batch/issues/5172

**関連リンク**:
- Commits:
  - [82121a5](https://github.com/spring-projects/spring-batch/commit/82121a59872e018b1c98cbe68345fde716cd2e60)

### 内容

Hi Spring Batch team,

Thank you for your great work on Spring Batch 6.0 and the new local chunking feature! While testing `ChunkTaskExecutorItemWriter`, I noticed a potential issue with status management when worker threads fail during write operations.

**Bug description**
When using `ChunkTaskExecutorItemWriter` for local chunking, if a worker thread fails during the write operation, the step's `BatchStatus` incorrectly remains `COMPLETED` while the `ExitStatus` is correctly set to `FAILED`. This creates an inconsistency in the step execution metadata.


**Root Cause**
In `AbstractStep.execute()` (around line 322), after calling `afterStep()`, only the `ExitStatus` is explicitly set:
```java
exitStatus = exitStatus.and(getCompositeListener().afterStep(stepExecution));
stepExecution.setExitStatus(exitStatus);  // Only ExitStatus is updated
```

The `BatchStatus` is not updated based on the `afterStep()` result. It remains as `COMPLETED` (set earlier in the try block) even when `afterStep()` returns `FAILED`.

**Current Implementation (ChunkTaskExecutorItemWriter.java)**
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        // Missing: stepExecution.setStatus(BatchStatus.FAILED);
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

**Expected behavior**

When `afterStep()` returns `ExitStatus.FAILED`, the `BatchStatus` should also be set to `FAILED` to maintain consistency between `ExitStatus` and `BatchStatus`.

**Proposed Fix**
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        stepExecution.setStatus(BatchStatus.FAILED);  // Add this line
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

**Steps to reproduce**
1. Configure a step using `ChunkTaskExecutorItemWriter`
2. Create a `ChunkProcessor` that throws an exception during write operation
3. Execute the job
4. Check the `BATCH_STEP_EXECUTION` table in the database


**Observed Result:**
- `EXIT_CODE`: FAILED ✓
- `STATUS`: COMPLETED ✗ (Expected: FAILED)


**Minimal Complete Reproducible example**
```java
package com.example.batch;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.batch.core.ExitStatus;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.job.parameters.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.core.step.item.ChunkProcessor;
import org.springframework.batch.infrastructure.item.ItemReader;
import org.springframework.batch.infrastructure.item.ItemWriter;
import org.springframework.batch.infrastructure.item.support.ListItemReader;
import org.springframework.batch.integration.chunk.ChunkTaskExecutorItemWriter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.SimpleAsyncTaskExecutor;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.List;

@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            ChunkTaskExecutorItemWriter issueReproductionWriter
    ) {
        return new StepBuilder(jobRepository)
                .chunk(3)
                .transactionManager(transactionManager)
                .reader(issueReproductionReader())
                .writer(issueReproductionWriter)
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new ListItemReader<>(List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        ));
    }

    @Bean
    public ChunkTaskExecutorItemWriter issueReproductionWriter(
            ChunkProcessor chunkProcessor
    ) {
        return new ChunkTaskExecutorItemWriter<>(chunkProcessor, new SimpleAsyncTaskExecutor());
    }

    @Bean
    public ChunkProcessor chunkProcessor(PlatformTransactionManager transactionManager) {
        TransactionTemplate txTemplate = new TransactionTemplate(transactionManager);
        ItemWriter writer = chunk -> {
            for (TestItem testItem : chunk.getItems()) {
                log.info("Writing: {}", testItem);

                if ("Item-2".equals(testItem.getName())) {
                    throw new RuntimeException("Simulated write failure");
                }
            }
        };

        return (chunk, contribution) -> txTemplate.executeWithoutResult(status -> {
            try {
                writer.write(chunk);
                contribution.setExitStatus(ExitStatus.COMPLETED);
            } catch (Exception e) {
                status.setRollbackOnly();
                contribution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
                throw e;
            }
        });
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }
}
```


After execution, query the metadata:
```sql
SELECT STEP_NAME, STATUS, EXIT_CODE, EXIT_MESSAGE
FROM BATCH_STEP_EXECUTION;

-- Result: 
-- STEP_NAME            | STATUS    | EXIT_CODE | EXIT_MESSAGE
-- issueReproductionStep| COMPLETED | FAILED    | java.lang.RuntimeException: Simulated write failure ...
--                        ^^^^^^^^^   ^^^^^^
--                        Inconsistent!
```


**Proposed Solution**

Update `ChunkTaskExecutorItemWriter.afterStep()` to explicitly set `BatchStatus.FAILED` when worker threads fail:
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        stepExecution.setStatus(BatchStatus.FAILED);  // Set BatchStatus to maintain consistency
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

This ensures that both `BatchStatus` and `ExitStatus` are consistently set to `FAILED` when worker thread execution fails, preventing metadata inconsistencies that can affect job restart logic and monitoring systems.

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-12-17

Thank you for raising this issue and for providing an example! Really top notch bug reporting here 👌

This is indeed a valid issue. In addition to marking the step execution as failed in the catch block as suggested , we also need to check if one of the workers has failed (as failed contributions could be applied before successful ones and therefore the step will be marked as completed even if one of the workers has failed).

---

