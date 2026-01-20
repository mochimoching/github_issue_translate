# Spring Batch GitHub Issues

取得日時: 2026年01月20日 11:52:37

取得件数: 12件

---

## Issue #5106: Intermittent OptimisticLockingFailureException when starting job using jobOperator.start() with asyncTaskExecutor

**状態**: closed | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

**関連リンク**:
- Commits:
  - [b024116](https://github.com/spring-projects/spring-batch/commit/b024116968ac5dd89ea84a8a3048d0e4a39d7519)
  - [76e723e](https://github.com/spring-projects/spring-batch/commit/76e723e41939b1ab6910f9ce8d61053abb1d0575)

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

## Issue #5109: Incorrect resource cleanup order in AbstractCursorItemReader#doClose leads to inconsistent behavior

**状態**: closed | **作成者**: banseok1216 | **作成日**: 2025-11-25

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5109

### 内容

**Bug description**
AbstractCursorItemReader#doClose closes JDBC resources in an incorrect order

**Environment**
Spring Batch: 6.0.0
java: Java 21
**Steps to reproduce**
Steps to reproduce the issue.

**Expected behavior**
1. Create a simple JdbcCursorItemReader that opens a cursor.
2. Call `reader.open(executionContext)`.
3. Call `reader.close()`.
4. Observe that:
   - `cleanupOnClose(connection)` is invoked after the connection is already closed.
   - `setAutoCommit(initialAutoCommit)` is never executed because the connection is closed.

Example of the problematic execution order:

```java
JdbcUtils.closeConnection(this.con);   // connection is closed here

cleanupOnClose(this.con);              // executed after close
// con.isClosed() == true

if (this.con != null && !this.con.isClosed()) {
    this.con.setAutoCommit(initialConnectionAutoCommit);  // skipped
}
```

**Additional note on responsibility**

Currently, `doClose()` ends up closing the `Connection` even though the
connection is created and owned by `AbstractCursorItemReader`. This leads to a
mixed ownership model:

- the parent opens the connection,
- the child performs cursor-level cleanup,
- but the child also closes the connection.

It is more consistent for the component that creates the connection to be the
one responsible for closing it. The reader subclass should only release
cursor-related resources such as the `ResultSet` and `PreparedStatement`.

The proposed change aligns the close behavior with that ownership model.

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2026-01-15

Thank you for reporting this issue and for contributing a fix!

---

## Issue #5136: The implementation of jumpToItem(int itemLastIndex) in AbstractPaginatedDataItemReader does not handle restart behavior correctly.

**状態**: closed | **作成者**: banseok1216 | **作成日**: 2025-12-05

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5136

**関連リンク**:
- Commits:
  - [d5fbb54](https://github.com/spring-projects/spring-batch/commit/d5fbb5493b78844fc8f8cf03a5eaafca380b34e1)

### 内容

**Bug description**

The `jumpToItem(int itemLastIndex)` implementation in `AbstractPaginatedDataItemReader` does not correctly restore the reader position when a step is restarted. In practice, this leads to skipped items or the reader resuming from an unexpected location.

While the method is intended to position the reader so that the next call to `read()` returns the item at the given index, the current implementation does not behave that way.

### Parent class implementation

```java
protected void jumpToItem(int itemIndex) throws Exception {
    for (int i = 0; i < itemIndex; i++) {
        read();
    }
}
```

This implementation ensures:

- After calling `jumpToItem(n)`, invoking `read()` returns the **nth item**.

---

### Overridden implementation in AbstractPaginatedDataItemReader

```java
@Override
protected void jumpToItem(int itemLastIndex) throws Exception {
    this.lock.lock();
    try {
        page = itemLastIndex / pageSize;
        int current = itemLastIndex % pageSize;

        Iterator<T> initialPage = doPageRead();

        for (; current >= 0; current--) {
            initialPage.next();
        }
    }
    finally {
        this.lock.unlock();
    }
}
```



There are two main issues:

---

### 1. Off-by-one advancement

Because the loop condition uses `current >= 0`, the iterator advances one time too many.  
For example, calling `jumpToItem(7)` causes the next `read()` to return the item at index 8 instead of 7.

| Call | Expected | Actual |
|------|----------|--------|
| `jumpToItem(7)` → `read()` | 7 | 8 |

This breaks the expectation that the reader should restart exactly at the stored index.

---

### 2. Iterator not assigned to the reader state

The method advances an iterator but never assigns it to `results`. On the next `read()` call, a new page is loaded, undoing any positioning work done inside `jumpToItem`. This makes the restart position unreliable and can result in the first page being re-read or the reader landing on the wrong item.

---

**Environment**

- Spring Batch: 5.x  
- Java: 17  

---

**Steps to reproduce**

1. Implement a paginated reader similar to the one in the test below.
2. Call `open(new ExecutionContext())`.
3. Invoke `jumpToItem(n)`.
4. Call `read()`.
5. The value returned will not match the expected item at index `n`.

---

**Expected behavior**

After calling `jumpToItem(n)`, the following `read()` call should return the item located at index `n`.

---

**Minimal Complete Reproducible example**

```java
package org.springframework.batch.infrastructure.item.data;

import org.junit.jupiter.api.Test;
import org.springframework.batch.infrastructure.item.ExecutionContext;

import java.util.Iterator;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class AbstractPaginatedDataItemReaderTests {

  static class PaginatedDataItemReader extends AbstractPaginatedDataItemReader<Integer> {

    private final List<Integer> data = List.of(
        0,1,2,3,4,5,6,7,8,9,
        10,11,12,13,14,15,16,17,18,19
    );

    @Override
    protected Iterator<Integer> doPageRead() {
      int start = page * pageSize;
      int end = Math.min(start + pageSize, data.size());
      return data.subList(start, end).iterator();
    }
  }

  @Test
  void jumpToItem_shouldReadExactItem_afterJump() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(7);

    Integer value = reader.read();
    assertEquals(7, value);
  }

  @Test
  void jumpToItem_zeroIndex() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(0);

    Integer value = reader.read();
    assertEquals(0, value);
  }

  @Test
  void jumpToItem_lastItemInPage() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(9);

    Integer value = reader.read();
    assertEquals(9, value);
  }

  @Test
  void jumpToItem_firstItemOfNextPage() throws Exception {
    PaginatedDataItemReader reader = new PaginatedDataItemReader();
    reader.open(new ExecutionContext());

    reader.jumpToItem(10);

    Integer value = reader.read();
    assertEquals(10, value);
  }

}
```

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2026-01-15

Thank you for reporting this issue and for contributing a fix!

---

## Issue #5161: OptimisticLockingFailureException in JobRepositoryTestUtils.removeJobExecutions() since Spring Batch 5.2.3

**状態**: closed | **作成者**: szopal24 | **作成日**: 2025-12-11

**ラベル**: in: test, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5161

**関連リンク**:
- Commits:
  - [1d9536c](https://github.com/spring-projects/spring-batch/commit/1d9536cfbabf54b921f5a522beef62e5d0793a97)
  - [12b16b3](https://github.com/spring-projects/spring-batch/commit/12b16b32adbbf35ead57b5e3b8d0ec84c56789ec)

### 内容

Since Spring Batch 5.2.3, calling JobRepositoryTestUtils.removeJobExecutions() in test cleanup methods throws OptimisticLockingFailureException when trying to delete job executions.

Environment
Spring Batch: 5.2.3, 5.2.4
Spring Boot: 3.4.5, 3.5.8
Java: 17
Database: PostgreSQL (with table prefix BOOT3_BATCH_)

**Test Code Example:**
```

    @Test
    public void testJob() throws Exception {
        JobExecution jobExecution = jobLauncherTestUtils.launchJob(defaultJobParameters());
        jobExecutionList.add(jobExecution);
        
        assertThat(jobExecution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);
    }

    @After
    public void cleanUp() {
        // This throws OptimisticLockingFailureException since 5.2.3
        jobRepositoryTestUtils.removeJobExecutions(jobExecutionList);
    }
```

Result:

```
org.springframework.dao.OptimisticLockingFailureException: Attempt to delete step execution id=95106 with wrong version (1)

	at org.springframework.batch.core.repository.dao.JdbcStepExecutionDao.deleteStepExecution(JdbcStepExecutionDao.java:386)
	at org.springframework.batch.core.repository.support.SimpleJobRepository.deleteStepExecution(SimpleJobRepository.java:316)
	at org.springframework.batch.core.repository.support.SimpleJobRepository.deleteJobExecution(SimpleJobRepository.java:324)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:360)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:196)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:380)
	at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:119)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184)
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:223)
	at jdk.proxy2/jdk.proxy2.$Proxy126.deleteJobExecution(Unknown Source)
	at org.springframework.batch.test.JobRepositoryTestUtils.removeJobExecution(JobRepositoryTestUtils.java:156)
	at org.springframework.batch.test.JobRepositoryTestUtils.removeJobExecutions(JobRepositoryTestUtils.java:138)
	at xx.yyyyy.xx.aaaa.vvvv.bbbb.wwwww.SpringBatchIntegrationTest.cleanUp(SpringBatchIntegrationTest.java:82)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at org.springframework.test.context.junit4.statements.RunAfterTestMethodCallbacks.evaluate(RunAfterTestMethodCallbacks.java:86)
	at org.springframework.test.context.junit4.statements.SpringRepeat.evaluate(SpringRepeat.java:84)
	at org.springframework.test.context.junit4.SpringJUnit4ClassRunner.runChild(SpringJUnit4ClassRunner.java:252)
	at org.springframework.test.context.junit4.SpringJUnit4ClassRunner.runChild(SpringJUnit4ClassRunner.java:97)
	at org.springframework.test.context.junit4.statements.RunBeforeTestClassCallbacks.evaluate(RunBeforeTestClassCallbacks.java:61)
	at org.springframework.test.context.junit4.statements.RunAfterTestClassCallbacks.evaluate(RunAfterTestClassCallbacks.java:70)
	at org.springframework.test.context.junit4.SpringJUnit4ClassRunner.run(SpringJUnit4ClassRunner.java:191)
```

This breaks all existing Spring Batch integration tests that use JobRepositoryTestUtils.removeJobExecutions() in cleanup methods. This is a breaking change that affects any project upgrading from 5.2.2 to 5.2.3+. The Spring Batch documentation and Javadocs for JobRepositoryTestUtils.removeJobExecutions() do not mention this breaking change or provide guidance on how to update existing tests.

### コメント

#### コメント 1 by quaff

**作成日**: 2025-12-12

It's introduced by #4793, you should query each `JobExecution` from `jobExecutionList` to get latest version for delete.

#### コメント 2 by szopal24

**作成日**: 2025-12-17

Thank you, I managed to resolve the problem. Unfortunately, this means I now have to apply changes in more than 100 Spring Batch applications that were using this method to clean up the BATCH_JOB_EXECUTION table. While I understand the reasoning behind the change, it does have a significant impact on existing test setups.

#### コメント 3 by quaff

**作成日**: 2025-12-18

@szopal24 I created #5173 to fix it.

#### コメント 4 by szopal24

**作成日**: 2025-12-18

Thank you!

#### コメント 5 by fmbenhassine

**作成日**: 2026-01-13

@szopal24  Thank you for reporting this issue and thank you @quaff for the PR.

I will plan the fix in 6.0.2 and back port it to 5.2.5

---

## Issue #5178: Add ZonedDateTime and OffsetDateTime support to JobParametersConverter

**状態**: closed | **作成者**: thswlsqls | **作成日**: 2025-12-21

**ラベル**: type: feature, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5178

**関連リンク**:
- Commits:
  - [077a332](https://github.com/spring-projects/spring-batch/commit/077a33238b8990e6993fb29a35dc9204b315a339)
  - [868849e](https://github.com/spring-projects/spring-batch/commit/868849e9911782899affd01d4a70b7b31d18c242)

### 内容

**Expected Behavior**

`ZonedDateTime` and `OffsetDateTime` should be supported as JobParameters types, similar to `LocalDateTime`, `LocalDate`, and `LocalTime`.

Example usage:
```java
ZonedDateTime scheduleTime = ZonedDateTime.of(2023, 12, 25, 10, 30, 0, 0, ZoneId.of("Asia/Seoul"));
JobParameters parameters = new JobParametersBuilder()
    .addJobParameter("schedule.time", scheduleTime, ZonedDateTime.class, true)
    .toJobParameters();
```

**Current Behavior**

Spring Batch currently only provides converters for `LocalDateTime`, `LocalDate`, and `LocalTime`. 
`ZonedDateTime` and `OffsetDateTime` cannot be used as JobParameters because there are no converters available.

**Context**

**How has this issue affected you?**
When working with global services or multi-timezone applications, we need to pass timezone-aware date/time values as JobParameters, but currently only timezone-naive types (`LocalDateTime`, `LocalDate`, `LocalTime`) are supported.

**What are you trying to accomplish?**
- Execute batch jobs based on specific timezones in global services
- Require both UTC and local timezone in log analysis
- Include timezone information for each country in multi-country services

**What other alternatives have you considered?**
- Converting to `LocalDateTime` and storing timezone separately (loses timezone information)
- Using `String` type and parsing manually (error-prone, not type-safe)
- Using `Date` with timezone offset (legacy API, not recommended)

**Are you aware of any workarounds?**
Currently, there is no clean workaround. Users must convert to `LocalDateTime` and lose timezone information, or use `String` type which is not type-safe.

**Proposed Implementation:**
- Add `ZonedDateTimeToStringConverter` and `StringToZonedDateTimeConverter`
- Add `OffsetDateTimeToStringConverter` and `StringToOffsetDateTimeConverter`
- Register new converters in `DefaultJobParametersConverter`
- Add related test code

### コメント

#### コメント 1 by scordio

**作成日**: 2025-12-21

> Currently, there is no clean workaround. Users must convert to `LocalDateTime` and lose timezone information, or use `String` type which is not type-safe.  

That's not entirely true. In an average Spring Boot application, this conversion capability could be obtained out of the box when defining a [`DefaultFormattingConversionService`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/format/support/DefaultFormattingConversionService.html) bean in the Spring context:

```java
import org.springframework.format.support.DefaultFormattingConversionService;

@Bean
DefaultFormattingConversionService conversionService() {
  return new DefaultFormattingConversionService();
}
```

This allows the use of job parameters like the following:

```java
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.format.annotation.DateTimeFormat.ISO;

@Bean
@StepScope
ItemReader<Item> itemReader(@Value("#{jobParameters['targetDate']}") @DateTimeFormat(iso = ISO.DATE) LocalDate targetDate) {
  ...
}
```

The same should also work with [`ZonedDateTime`](https://github.com/spring-projects/spring-framework/blob/0b2bb7e751d5effd798adaf545c64a7342657ecc/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L180-L182) and [`OffsetDateTime`](https://github.com/spring-projects/spring-framework/blob/0b2bb7e751d5effd798adaf545c64a7342657ecc/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L184-L186).

Nevertheless, it would be nice if Spring Batch would offer this out of the box.
 
> * Register new converters in `DefaultJobParametersConverter`

As Spring Batch already depends on `spring-context`, what about instantiating a `DefaultFormattingConversionService` instead of `DefaultConversionService` in the `DefaultJobParametersConverter` constructor?

https://github.com/spring-projects/spring-batch/blob/2cc7890be100034f66bab9b4297de93dfbfad3a3/spring-batch-core/src/main/java/org/springframework/batch/core/converter/DefaultJobParametersConverter.java#L79

Some existing custom converters in Spring Batch might also become obsolete.

#### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@thswlsqls Thank you for opening this issue and contributing a PR!

@scordio Thank you for the follow up and for the PR as well!

Both PRs LGTM 👍  I think we can merge #5179 for 6.0.2 and then #5186 in 6.1.0 so that users don't have to wait a year or more to get these two converters (and indeed, it's better to leverage converters from Spring Framework as in #5186). 

#### コメント 3 by scordio

**作成日**: 2026-01-13

I'll rebase #5186 once #5179 is merged.

#### コメント 4 by fmbenhassine

**作成日**: 2026-01-15

@scordio FYI, #5179 was merged.

---

## Issue #5182: ChunkOrientedStep updates ExecutionContext even when a chunk fails, leading to data loss on restart

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

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

### コメント

#### コメント 1 by KILL9-NO-MERCY

**作成日**: 2026-01-06

Hi Spring Batch team!
I wanted to add some follow-up context related to this issue.

I recently opened another issue (#5199) regarding the transaction boundary of JobRepository.update(stepExecution) in ChunkOrientedStep#doExecute.

If the fix proposed in #5199 is applied (moving JobRepository.update(stepExecution) inside the chunk transaction), then the proposed fix in this issue (#5182) should be slightly adjusted as well.

the past proposed fix suggests moving those updates to doExecute, after the transaction completes. but If `JobRepository.update(stepExecution)` itself is moved inside the transaction (as proposed in #5199), then to preserve full consistency, the following operations should also be aligned with the same transaction boundary
- JobRepository.update(stepExecution)
- ItemStream.update(stepExecution.getExecutionContext())
- JobRepository.updateExecutionContext(stepExecution)

## Suggested alignment
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // process next chunk in its own transaction
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
           processNextChunk(transactionStatus, contribution, stepExecution);
           // FIX: Update ItemStream and ExecutionContext
           this.compositeItemStream.update(stepExecution.getExecutionContext());
           getJobRepository().updateExecutionContext(stepExecution);
           // FIX #5199
           getJobRepository().update(stepExecution);
       });
    }
}
```

Just wanted to point this out so both issues can be addressed consistently. Happy to help with a unified fix or a test if needed. Thanks again!

#### コメント 2 by fmbenhassine

**作成日**: 2026-01-12

Thank you for your continuous feedback on v6.

> Happy to help with a unified fix or a test if needed.

Yes please. That would be helpful! Many thanks upfront.

EDIT: It looks like we have a PR for this issue: #5195. Can you please check if it suggests the same/similar fix that you have in mind?

#### コメント 3 by KILL9-NO-MERCY

**作成日**: 2026-01-14

Thanks for the information! I'll check PR #5195 and leave a comment there.

#### コメント 4 by fmbenhassine

**作成日**: 2026-01-15

Resolved with #5195

---

## Issue #5183: ScopeNotActiveException with @StepScope ItemProcessor in Multi-threaded ChunkOrientedStep

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5183

**関連リンク**:
- Commits:
  - [2382908](https://github.com/spring-projects/spring-batch/commit/2382908f404a4de714b0be9aa0023f25716e63bd)
  - [5642911](https://github.com/spring-projects/spring-batch/commit/564291127752f0c107508f853131fc4d8acfd4bd)

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

### コメント

#### コメント 1 by LeeHyungGeol

**作成日**: 2026-01-07

Hello @fmbenhassine.

Would it be okay if i give it a try on this issue?

#### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@KILL9-NO-MERCY Thank you for reporting this issue!

> I am not certain whether this is an intended architectural change or an oversight in the new implementation.

This is an oversight in the new implementation. In fact `org.springframework.batch.core.step.item.ChunkOrientedStepIntegrationTests#testConcurrentChunkOrientedStepSuccess` fails when [this item processor](https://github.com/spring-projects/spring-batch/blob/a6a53c46fca3aa920f4f07ac7ddbf39493081f66/spring-batch-core/src/test/java/org/springframework/batch/core/step/item/TestConfiguration.java#L56) is step-scoped. The suggested change LGTM (with it, the test passes with a step-scoped item processor). Thank you for the suggestion.

@LeeHyungGeol Sure! Thank you for your offer to help 🙏 You are welcome to contribute a PR with the suggested change here and making the item processor that I mentioned earlier step-scoped. I will plan the fix for the upcoming 6.0.2.

#### コメント 3 by LeeHyungGeol

**作成日**: 2026-01-14

 @fmbenhassine Thank you for the confirmation!

  I'll work on a PR with the suggested fix and update the integration test
  to use a step-scoped item processor.

  Could you please assign this issue to me?

#### コメント 4 by LeeHyungGeol

**作成日**: 2026-01-18

@fmbenhassine 
I opened PR https://github.com/spring-projects/spring-batch/pull/5218 to address this!
PTAL when you have time. 🙇 thanks!

---

## Issue #5191: Jackson2ExecutionContextStringSerializer fails to serialize job parameters with JobStep

**状態**: closed | **作成者**: andrianov17 | **作成日**: 2025-12-30

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5191

**関連リンク**:
- Commits:
  - [72c4aa2](https://github.com/spring-projects/spring-batch/commit/72c4aa2779184528aca9b97b4c8f4a6fa3473add)
  - [0bb92d5](https://github.com/spring-projects/spring-batch/commit/0bb92d54504dfcc2dcb17989f5120f29a9a23261)
  - [0116494](https://github.com/spring-projects/spring-batch/commit/0116494b54a92bde25966071a56adf50ec198d64)
  - [79f679f](https://github.com/spring-projects/spring-batch/commit/79f679f9ed91f399c67f3f56b07d8a61c742ab47)
  - [2a5646a](https://github.com/spring-projects/spring-batch/commit/2a5646a2dee92e4556c71c39719e3cfed34d0a74)

### 内容

**Bug description**
After upgrade from Spring Batch 5.2.3 to Spring Batch 6.0.1 and preserving previous org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer serializer, JobStep fails with the exception:

```
Caused by: com.fasterxml.jackson.databind.JsonMappingException: Can not write a field name, expecting a value (through reference chain: java.util.HashMap["org.springframework.batch.core.step.job.JobStep.JOB_PARAMETERS"]->org.springframework.batch.core.job.parameters.JobParameters["parameters"]->java.util.Collections$UnmodifiableSet[0])
	at com.fasterxml.jackson.databind.JsonMappingException.wrapWithPath(JsonMappingException.java:400)
	at com.fasterxml.jackson.databind.JsonMappingException.wrapWithPath(JsonMappingException.java:371)
	at com.fasterxml.jackson.databind.ser.std.StdSerializer.wrapAndThrow(StdSerializer.java:346)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContentsUsing(CollectionSerializer.java:186)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContents(CollectionSerializer.java:120)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContents(CollectionSerializer.java:25)
	at com.fasterxml.jackson.databind.ser.std.AsArraySerializerBase.serializeWithType(AsArraySerializerBase.java:265)
	at com.fasterxml.jackson.databind.ser.BeanPropertyWriter.serializeAsField(BeanPropertyWriter.java:734)
	at com.fasterxml.jackson.databind.ser.std.BeanSerializerBase.serializeFields(BeanSerializerBase.java:760)
	at com.fasterxml.jackson.databind.ser.std.BeanSerializerBase.serializeWithType(BeanSerializerBase.java:643)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeTypedFields(MapSerializer.java:1026)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeFields(MapSerializer.java:778)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeWithoutTypeInfo(MapSerializer.java:763)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeWithType(MapSerializer.java:732)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeWithType(MapSerializer.java:34)
	at com.fasterxml.jackson.databind.ser.impl.TypeWrappedSerializer.serialize(TypeWrappedSerializer.java:32)
	at com.fasterxml.jackson.databind.ser.DefaultSerializerProvider._serialize(DefaultSerializerProvider.java:503)
	at com.fasterxml.jackson.databind.ser.DefaultSerializerProvider.serializeValue(DefaultSerializerProvider.java:342)
	at com.fasterxml.jackson.databind.ObjectMapper._writeValueAndClose(ObjectMapper.java:4926)
	at com.fasterxml.jackson.databind.ObjectMapper.writeValue(ObjectMapper.java:4105)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:165)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:114)
	at org.springframework.batch.core.repository.dao.jdbc.JdbcExecutionContextDao.serializeContext(JdbcExecutionContextDao.java:361)
	... 28 more
Caused by: com.fasterxml.jackson.core.JsonGenerationException: Can not write a field name, expecting a value
	at com.fasterxml.jackson.core.JsonGenerator._constructWriteException(JsonGenerator.java:2937)
	at com.fasterxml.jackson.core.JsonGenerator._reportError(JsonGenerator.java:2921)
	at com.fasterxml.jackson.core.json.UTF8JsonGenerator.writeFieldName(UTF8JsonGenerator.java:217)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer$JobParametersModule$JobParameterSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:213)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer$JobParametersModule$JobParameterSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:195)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContentsUsing(CollectionSerializer.java:179)
	... 49 more
```

Upon debugging, it fails trying to serialize the first JobParameter.

**Environment**
Spring Batch 6.0.1, SQL Server 2022

**Steps to reproduce**
- Have a job using JobStep step
- Run the job passing some parameters to it

**Expected behavior**
Job runs successfully, saving step execution context like this (as it was in 5.2.3):
```
{
	"@class": "java.util.HashMap",
	"childJobExecId": [
		"java.lang.Long",
		3480
	],
	"org.springframework.batch.core.step.job.JobStep.JOB_PARAMETERS": {
		"@class": "org.springframework.batch.core.JobParameters",
		"parameters": {
			"@class": "java.util.Collections$UnmodifiableMap",
			"queueItemId": {
				"@class": "org.springframework.batch.core.JobParameter",
				"value": "250702",
				"type": "java.lang.String",
				"identifying": false
			},
			"execType": {
				"@class": "org.springframework.batch.core.JobParameter",
				"value": "MANUAL",
				"type": "java.lang.String",
				"identifying": false
			},
			"user": {
				"@class": "org.springframework.batch.core.JobParameter",
				"value": "system",
				"type": "java.lang.String",
				"identifying": false
			}
		}
	},
	"batch.version": "5.2.3"
}
```

Please also notice that org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.JobParametersModule.JobParameterSerializer#serialize is not adjusted to serialize parameter name.

**Minimal Complete Reproducible example**
Pretty straightforward - see steps to reproduce above


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2026-01-12

Thank you for opening this issue. If you upgrade to v6, you should be using `JacksonExecutionContextStringSerializer` and not `Jackson2ExecutionContextStringSerializer`. Did you update your configuration accordingly?

If your issue is related to `Jackson2ExecutionContextStringSerializer` in 5.2.x, please provide a minimal example or a failing test and I will plan the fix in the next patch release of 5.2.x.

#### コメント 2 by andrianov17

**作成日**: 2026-01-13

Jackson2ExecutionContextStringSerializer is working fine in 5.x, but was not adjusted accordingly in 6.x and serialization (and deserialization) was broken.

It is just deprecated and recommended to migrate to Jackson 3, so until removed it should be functional for those how cannot migrate to Jackson 3 right away and need some time.

Once JacksonExecutionContextStringSerializer (Jackson 3) has been fixed, personally we don't need Jackson2ExecutionContextStringSerializer anymore, but others could still need for the reason mentioned above.

So, it's up to you how to proceed with Jackson2ExecutionContextStringSerializer. If you don't want to fix it now - wait for another similar issue.

Please however merge the PR because otherwise JacksonExecutionContextStringSerializer serializes some noise with doesn't make sense. BTW, the same PR offers fix for Jackson2ExecutionContextStringSerializer in 6.x

#### コメント 3 by fmbenhassine

**作成日**: 2026-01-13

> Jackson2ExecutionContextStringSerializer is working fine in 5.x, but was not adjusted accordingly in 6.x and serialization (and deserialization) was broken.

Which deserialisation was broken? Are you trying to deserialise something with v6 that was serialised with v5? All jobs that were started with v5 should be run to completion (success or failure) with v5 (if a job failed with v5, it should be restarted with v5, not v6). Please make sure to run all your jobs to completion with v5 before upgrading to v6.

Now if you start a job with v6, the deserialisation will work fine. The serialisation/deserialization is not compatible between Spring Batch 5 / Jackson 2 and Spring Batch 6 / Jackson 3 (due to Jackson).

> It is just deprecated and recommended to migrate to Jackson 3, so until removed it should be functional for those how cannot migrate to Jackson 3 right away and need some time.

It is functional if you use it to deserialise a context that was serialised with it, as explained in the previous point

> So, it's up to you how to proceed with Jackson2ExecutionContextStringSerializer. If you don't want to fix it now - wait for another similar issue.

It's not that I don't want (I hope my previous message did not imply that), it's about in which branch/version to fix it, as explained in https://github.com/spring-projects/spring-batch/pull/5193#issuecomment-3740260690.

> Please however merge the PR because otherwise JacksonExecutionContextStringSerializer serializes some noise with doesn't make sense. BTW, the same PR offers fix for Jackson2ExecutionContextStringSerializer in 6.x

Yes that PR LGTM, but the fix of `Jackson2ExecutionContextStringSerializer` should go in `5.2.x`, not in `main`. We do not put additional effort to maintain deprecated APIs in v6, but we can fix them in v5 if needed.

#### コメント 4 by andrianov17

**作成日**: 2026-01-13

Let's get back to the original issue.

Environment has been upgraded from Spring 5 to Spring 6. Existing Jackson2ExecutionContextStringSerializer was used (Jackson 3 migration to be done later). That's it.

Now, when you attempt to run a job having JobStep (nested job in its definition), it fails right away on SERIALIZATION - see stack trace above.

#### コメント 5 by fmbenhassine

**作成日**: 2026-01-14

Thank you for the feedback. I don't know how I missed the detail that the issue is about `JobStep`, my bad, apologies. That's why it's always better to provide a failing example (we provide a comprehensive [issue reporting guide](https://github.com/spring-projects/spring-batch/blob/main/ISSUE_REPORTING.md) with a project template and everything needed to make reporting issues as easy as possible and save everyone's time).

The following sample fails as reported:

```java
package org.springframework.batch.samples.helloworld;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.EnableJdbcJobRepository;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.ExecutionContextSerializer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.infrastructure.repeat.RepeatStatus;
import org.springframework.batch.samples.common.DataSourceConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

@Configuration
@EnableBatchProcessing
@EnableJdbcJobRepository
@Import(DataSourceConfiguration.class)
public class HelloWorldJobConfiguration {

	@Bean
	public Step outerStep(JobRepository jobRepository) {
		Step innerStep = new StepBuilder("inner-step", jobRepository).tasklet((contribution, chunkContext) -> {
			System.out.println("Hello from inner step!");
			return RepeatStatus.FINISHED;
		}).build();
		Job innerJob = new JobBuilder("inner-job", jobRepository).start(innerStep).build();
		return new StepBuilder("outer-step", jobRepository).job(innerJob).build();
	}

	@Bean
	public Job outerJob(JobRepository jobRepository, Step outerStep) {
		return new JobBuilder("outer-job", jobRepository).start(outerStep).build();
	}

	@Bean
	public ExecutionContextSerializer executionContextSerializer() {
		return new Jackson2ExecutionContextStringSerializer();
	}

}
```

Now that I fully understand the issue, `Jackson2ExecutionContextStringSerializer` should be adapted in v6 as well. I will merge #5193 for that.

---

## Issue #5199: ChunkOrientedStep#doExecute updates the StepExecution outside of the chunk transaction boundary.

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2026-01-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5199

**関連リンク**:
- Commits:
  - [563abdb](https://github.com/spring-projects/spring-batch/commit/563abdb29d26884c32f18e5d548fd079e6aad057)

### 内容

Hi Spring Batch team 👋
First of all, thank you for your continued work on Spring Batch.

## Description
This issue is related to a past change in PR #5165: https://github.com/spring-projects/spring-batch/pull/5165

This was my mistake, and I wanted to report it properly after noticing an unintended side effect in Spring Batch 6.0.1.

In Spring Batch 6, ChunkOrientedStep#doExecute updates the StepExecution outside of the chunk transaction boundary.
Because of this, if JobRepository.update(stepExecution) fails, the chunk transaction has already been completed, which can leave batch metadata in an inconsistent state.

In other words, chunk processing and step execution persistence are no longer atomic in ChunkOrientedStep.

## Environment
spring batch 6.0.1
ChunkOrientedStep#doExecute()

## expected behavior
The update of StepExecution via JobRepository.update(stepExecution) should occur within the same transaction boundary as chunk processing.

If the metadata update fails, the chunk transaction should be rolled back accordingly, preserving consistency between:
processed data and batch metadata.

This is the behavior historically provided by TaskletStep, where JobRepository.update() is invoked before transaction commit, not after.

## Additional context
The current implementation of ChunkOrientedStep#doExecute looks like this (simplified):
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
});

// transaction already completed here
getJobRepository().update(stepExecution);

```

## Proposed fix
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
    getJobRepository().update(stepExecution);
});
```

so that chunk processing and metadata updates share the same transactional boundary.

please let me know if you’d like me to provide a reproducer or a failing test for this issue. 🙏


---

## Issue #5207: Fix typo in whatsnew.adoc and in integration tests

**状態**: closed | **作成者**: wocks1123 | **作成日**: 2026-01-10

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5207

### 内容

fixed typo in the test method and an example code in the 'whatsnew.adoc' document

- wrong : faultToleranChunkOrientedStep, nonRetrybaleExceptions
- correct : faultToleran**t**ChunkOrientedStep, nonRetry**ab**leExceptions


### コメント

#### コメント 1 by wocks1123

**作成日**: 2026-01-10

fix this issue in this PR #5206

#### コメント 2 by fmbenhassine

**作成日**: 2026-01-12

Resolved with #5206 . Thank you for opening the issue and for providing a fix 🙏

---

## Issue #5217: OptimisticLockingFailureException due to race condition in graceful shutdown

**状態**: closed | **作成者**: KMGeon | **作成日**: 2026-01-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5217

**関連リンク**:
- Commits:
  - [4034f26](https://github.com/spring-projects/spring-batch/commit/4034f269cb96c55ee1fd1a80666fb087d07b9526)
  - [7f742a5](https://github.com/spring-projects/spring-batch/commit/7f742a5933473e5a6768db583f78bf68aa942641)

### 内容

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

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2026-01-19

Thank you for reporting this issue and for providing a fix!

Indeed, I was aware of that flaky test but I just didn't have time yet to trace the race condition down. So thank you very much for doing that. I will plan the fix for 6.0.2.

---

## Issue #5220: MongoStepExecutionDao.countStepExecutions() ignores stepName parameter

**状態**: closed | **作成者**: KMGeon | **作成日**: 2026-01-18

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5220

**関連リンク**:
- Commits:
  - [b0105f8](https://github.com/spring-projects/spring-batch/commit/b0105f8fd027aebf7a4e2afa29d1b249aa979794)
  - [fe421d0](https://github.com/spring-projects/spring-batch/commit/fe421d0dced93f8a05f5b09be8493f957fa2a0b7)

### 内容

## Bug Description

`MongoStepExecutionDao.countStepExecutions(JobInstance jobInstance, String stepName)` does not use the `stepName` parameter in the query.

- **Current behavior**: Returns count of all StepExecutions for the JobInstance
- **Expected behavior**: Returns count of StepExecutions filtered by `stepName`

## Affected Code

```java
// MongoStepExecutionDao.java (Line 165-177)
@Override
public long countStepExecutions(JobInstance jobInstance, String stepName) {
    Query query = query(where("jobInstanceId").is(jobInstance.getId()));
    List jobExecutions = this.mongoOperations.find(...);
    return this.mongoOperations.count(
            query(where("jobExecutionId").in(jobExecutions.stream()
                .map(JobExecution::getJobExecutionId)
                .toList())),  // stepName parameter is ignored
            StepExecution.class, STEP_EXECUTIONS_COLLECTION_NAME);
}
```

## Comparison with JdbcStepExecutionDao

`JdbcStepExecutionDao` correctly filters by `stepName`:

```sql
-- JdbcStepExecutionDao.java (Line 106-111)
SELECT COUNT(*)
FROM BATCH_JOB_EXECUTION JE
    JOIN BATCH_STEP_EXECUTION SE ON SE.JOB_EXECUTION_ID = JE.JOB_EXECUTION_ID
WHERE JE.JOB_INSTANCE_ID = ? AND SE.STEP_NAME = ?
```

## Impact

This bug affects `startLimit` functionality. `SimpleStepHandler.shouldStart()` calls `countStepExecutions()` to validate `startLimit`:

```java
// SimpleStepHandler.java (Line 205-221)
long stepExecutionCount = jobRepository.getStepExecutionCount(jobInstance, step.getName());
if (stepExecutionCount < step.getStartLimit()) {
    return true;
} else {
    throw new StartLimitExceededException(...);
}
```

**Example:**

| Step  | Actual Executions | startLimit | Bug Returns     | Result                                    |
|-------|-------------------|------------|-----------------|-------------------------------------------|
| stepA | 2                 | 3          | 7 (total count) | `StartLimitExceededException` (incorrect) |
| stepB | 5                 | 10         | 7 (total count) | Pass (accidentally correct)               |

## Test to Reproduce

```java
@Test
void testCountStepExecutionsFiltersByStepName() {
    // given
    dao.createStepExecution("stepA", jobExecution);
    dao.createStepExecution("stepA", jobExecution);
    dao.createStepExecution("stepB", jobExecution);
    dao.createStepExecution("stepC", jobExecution);

    // when
    long countA = dao.countStepExecutions(jobInstance, "stepA");
    long countB = dao.countStepExecutions(jobInstance, "stepB");
    long countC = dao.countStepExecutions(jobInstance, "stepC");
    long countNonExistent = dao.countStepExecutions(jobInstance, "nonExistentStep");

    // then
    assertEquals(2, countA);  // Bug: returns 4
    assertEquals(1, countB);  // Bug: returns 4
    assertEquals(1, countC);  // Bug: returns 4
    assertEquals(0, countNonExistent);  // Bug: returns 4
}
```

## Suggested Fix

Add `.and("name").is(stepName)` to the query:

```java
return this.mongoOperations.count(
        query(where("jobExecutionId").in(jobExecutions.stream()
            .map(JobExecution::getJobExecutionId)
            .toList())
            .and("name").is(stepName)),  // Added stepName filter
        StepExecution.class, STEP_EXECUTIONS_COLLECTION_NAME);
```

---

## Additional Note

While investigating this issue, I noticed that there seem to be several areas where the MongoDB implementation is not fully synchronized with the JDBC implementation. For example:

- Optimistic locking behavior
- Other DAO method implementations

Would it be helpful if I do a broader review of the MongoDB module to identify other inconsistencies with the JDBC implementation? I'd be happy to contribute fixes for any issues found.

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2026-01-19

Thank you for reporting this issue and for providing a fix! This seems like a regression from ddbb6174c522999fc697a1603ac4e2c69a676a49 (the step name is used in 5.2.x).

I will plan the fix in 6.0.2

---

