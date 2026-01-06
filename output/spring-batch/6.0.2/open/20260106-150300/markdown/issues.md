# Spring Batch GitHub Issues

取得日時: 2026年01月06日 15:03:02

取得件数: 4件

---

## Issue #5106: Intermittent OptimisticLockingFailureException when starting job using jobOperator.start() with asyncTaskExecutor

**状態**: open | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

### 内容

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


### コメント

#### コメント 1 by ahoehma

**作成日**: 2025-12-01

Not exactly what I'm fighting with :-) But I will watch the feedback here as well.

(I started this discussion: https://github.com/spring-projects/spring-batch/discussions/5121)

#### コメント 2 by phactum-mnestler

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

#### コメント 3 by licenziato

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

#### コメント 4 by kizombaDev

**作成日**: 2025-12-19

We are currently unfortunately running into the same problem with Spring Batch 6.0.1, MongoDB, and a `ThreadPoolTaskExecutor`.

I start a job using `jobOperator.start(job, new JobParameters())` and immediately get a `DataIntegrityViolationException`.

I can confirm that the problem is caused by the call to `this.jobRepository.update(jobExecution);` in the finally block of the method
`org.springframework.batch.core.launch.support.TaskExecutorJobLauncher#launchJobExecution`.

I created a reproducer with a mongoDB: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

#### コメント 5 by banseok1216

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

#### コメント 6 by fmbenhassine

**作成日**: 2025-12-21

Thank you all for reporting this issue and for providing analysis / reproducer!

This seems like a regression in #3637. I will plan the fix for the next patch version 6.0.2.

#### コメント 7 by StefanMuellerCH

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

---

## Issue #5181: MetaDataInstanceFactory default values cause StepContext collision in StepScopeTestUtils when @SpringBatchTest is active

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5181

### 内容

## Bug description: 
There is a logical collision in StepSynchronizationManager when using StepScopeTestUtils in a test environment managed by @SpringBatchTest.

StepExecution determines equality based on stepName, jobExecutionId, and id. Since MetaDataInstanceFactory provides static default values for all these fields, multiple instances created by the factory are treated as identical keys in the SynchronizationManagerSupport.contexts map.

This prevents StepScopeTestUtils from registering a new context with custom JobParameters, as the computeIfAbsent logic finds the existing context registered by StepScopeTestExecutionListener (which is part of @SpringBatchTest).

## Steps to reproduce:
Annotate a test class with @SpringBatchTest.

Inside a test method, use StepScopeTestUtils.doInStepScope() with a StepExecution created via MetaDataInstanceFactory.createStepExecution(jobParameters).

The Tasklet or ItemStream inside the scope will fail to see the jobParameters because it is bound to the listener's initial context.

## Failing Example: 
example job
```java
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
            Tasklet issueReproductionTasklet
    ) {
        return new StepBuilder(jobRepository)
                .tasklet(issueReproductionTasklet)
                .build();
    }

    @Bean
    @StepScope
    public Tasklet issueReproductionTasklet(@Value("#{jobParameters['testParam']}") String testParam) {
        return (contribution, chunkContext) -> {
            contribution.getStepExecution().getExecutionContext().putString("result", testParam);
            return RepeatStatus.FINISHED;
        };
    }
}
```

test class
```java
@SpringBatchTest
@SpringBootTest
@ActiveProfiles("test")
@Import(TestBatchConfiguration.class)
public class IssueReproductionTest {
    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactory ID collision causes JobParameter injection failure")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // MetadataInstanceFactory in 6.x / maybe after 5.2.3?? creates StepExecution with fixed ID 1234L
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // This will FAIL because 'actualValue' will be null.
        // The Tasklet retrieved the listener's context (which has no JobParameters)
        // instead of the one passed via StepScopeTestUtils due to ID collision (1234L).
        assertEquals(expectedValue, actualValue);
    }
}

@TestConfiguration
public class TestBatchConfiguration extends DefaultBatchConfiguration {
}
```

application-test.yml
```yaml
spring:
  batch:
    job:
      enabled: false
```
test result:
```bash
Value for key=[result] is not of type: [class java.lang.String], it is [null]
java.lang.ClassCastException: Value for key=[result] is not of type: [class java.lang.String], it is [null]
```

## Expected behavior:
The StepExecution and its corresponding StepContext created within StepScopeTestUtils.doInStepScope() should be correctly registered and accessible through the StepSynchronizationManager, even when @SpringBatchTest is active.

(Note: Deciding on the best fix seems non-trivial to me, as it could involve changing the ID generation strategy in MetaDataInstanceFactory or adjusting how StepSynchronizationManager handles overlapping registrations in a test environment.)
Workaround: Users must manually provide a unique name or ID to bypass the equals/hashCode collision:

## Workaround: 
To bypass the current collision, users can explicitly define a getStepExecution() method within their test class. By returning a StepExecution with a unique name or a different ID (e.g., -1L), you can prevent the StepScopeTestExecutionListener from occupying the default ID (1234L), thus allowing StepScopeTestUtils to work as intended:

```java
/**
 * Workaround: Define getStepExecution() in the test class to avoid ID collision.
 * By providing a non-default ID or name, we ensure that the listener-registered 
 * context does not conflict with the one created in StepScopeTestUtils.
 */
public StepExecution getStepExecution() {
    return MetaDataInstanceFactory.createStepExecution("uniqueStep", -1L);
}
```

test result:
```bash
> Task :test
BUILD SUCCESSFUL in 3s
```

Thanks for your time and for maintaining this great project!

---

## Issue #5182: ChunkOrientedStep updates ExecutionContext even when a chunk fails, leading to data loss on restart

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5182

### 内容

Hello Spring Batch Team!

## Bug description: 
In Spring Batch 6.x, the newly introduced ChunkOrientedStep calls itemStream.update() and jobRepository.updateExecutionContext() within a finally block in both processChunkSequentially and processChunkConcurrently. Unlike the traditional TaskletStep implementation.

This causes the ItemStream state (e.g., read count, current index) to be persisted even when a chunk transaction fails and rolls back. Consequently, upon restart, the step resumes from the "failed" offset, leading to silent data loss of the records within the failed chunk.


## Code Comparison (The Root Cause)

#### Spring Batch 5.x (TaskletStep.java)
In version 5, the state is updated only after the chunk is successfully processed and committed.

```java

// TaskletStep.java (Line 452)
// This logic is inside the successful processing flow
stream.update(stepExecution.getExecutionContext());
getJobRepository().updateExecutionContext(stepExecution);
stepExecution.incrementCommitCount();
```


#### Spring Batch 6.x (ChunkOrientedStep.java)
In version 6, the update logic was moved to a finally block, forcing the update even during a rollback.
```java
// ChunkOrientedStep.java
private void processChunkSequentially(...) {
    try {
        // chunk read/process/write logic
    } catch (Exception e) {
        // exception handling
        throw e;
    } finally {
        // BUG: Always executed even if the transaction is rolled back!
        this.compositeItemStream.update(stepExecution.getExecutionContext());
        getJobRepository().updateExecutionContext(stepExecution);
    }
}
```

## Impact
Transaction Inconsistency: The business data is rolled back, but the Batch Metadata (index/offset) is committed/updated.

Data Loss: On restart, the ItemReader resumes from the position after the failed chunk, meaning the records in the failed chunk are never re-processed.

## Environment
Spring Batch version: 6.0.1
Components: ChunkOrientedStep 

## Expected behavior
ExecutionContext and ItemStream state should only be updated if the chunk transaction is successful. If an exception occurs, the finally block should not persist the advanced state to the JobRepository.


## Suggested Fix
The state update logic should be moved from the finally block of processChunkXXX methods to the doExecute method, specifically after the transaction has successfully completed.

Proposed change in ChunkOrientedStep.java:
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // process next chunk in its own transaction
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
          // process next chunk
       });
       getJobRepository().update(stepExecution);
       
       // FIX: Update ItemStream and ExecutionContext ONLY after successful transaction commit
       this.compositeItemStream.update(stepExecution.getExecutionContext());
       getJobRepository().updateExecutionContext(stepExecution);
    }
}
```
Note: The corresponding update calls inside processChunkSequentially and processChunkConcurrently's finally blocks must be removed to prevent duplicate or premature updates.


Thanks for your time and for maintaining this great project! If you need more details or sample please tell me!

---

## Issue #5183: ScopeNotActiveException with @StepScope ItemProcessor in Multi-threaded ChunkOrientedStep

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5183

### 内容

Hello Spring Batch Team,

I am reporting an issue regarding the new ChunkOrientedStep introduced in version 6.0. It appears that when a step is configured as multi-threaded, an ItemProcessor defined with @StepScope fails to resolve correctly within the worker threads.

## Bug Description
In the ChunkOrientedStep implementation, specifically when using processChunkConcurrently, the StepContext does not seem to be propagated to the worker threads managed by the TaskExecutor.

As a result, when the worker thread attempts to invoke the ItemProcessor (which is a @StepScope proxy), it throws a ScopeNotActiveException because the StepSynchronizationManager on that specific thread has no active context.

## Environment
Spring Batch version: v6
Step Implementation: ChunkOrientedStep
Configuration: TaskExecutor (e.g., SimpleAsyncTaskExecutor) + @StepScope ItemProcessor

## Reproducible Configuration
```java
@Bean
public Step issueReproductionStep(
        JobRepository jobRepository,
        ItemReader<TestItem> reader,
        ItemProcessor<TestItem, TestItem> itemProcessor, // @StepScope Bean
        ItemWriter<TestItem> writer
) {
    return new StepBuilder(jobRepository)
            .<TestItem, TestItem>chunk(1)
            .reader(reader)
            .processor(itemProcessor)
            .writer(writer)
            .taskExecutor(new SimpleAsyncTaskExecutor()) // Multi-threading enabled
            .build();
}

@Bean
@StepScope
public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
    return item -> {
        log.info("[Thread: {}] Processing item: {}", Thread.currentThread().getName(), item.getName());
        return item;
    };
}
```

## Actual Result (Stacktrace)
The error occurs when the worker thread tries to access the scoped ItemProcessor:
```bash
Caused by: org.springframework.beans.factory.support.ScopeNotActiveException: Error creating bean with name 'scopedTarget.issueReproductionProcessor': Scope 'step' is not active for the current thread
    at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:381)
    ...
    at jdk.proxy2/jdk.proxy2.$Proxy134.process(Unknown Source)
    at org.springframework.batch.core.step.item.ChunkOrientedStep.doProcess(ChunkOrientedStep.java:655)
    ...
Caused by: java.lang.IllegalStateException: No context holder available for step scope
    at org.springframework.batch.core.scope.StepScope.getContext(StepScope.java:167)
```

## Expected Behavior
I am not certain whether this is an intended architectural change or an oversight in the new implementation. However, if this is a bug, the @StepScope ItemProcessor should function correctly within worker threads, as it did in previous versions.


## Proposed change in ChunkOrientedStep.processChunkConcurrently:
```java
// Inside processChunkConcurrently method
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    try {
        // Register step execution to the current worker thread's StepSynchronizationManager
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // Clear the context after processing to prevent memory leaks
        StepSynchronizationManager.close();
    }
});
```

Thanks for your time and for maintaining this project! Please let me know if you need any further information or a working reproduction repository!

---

