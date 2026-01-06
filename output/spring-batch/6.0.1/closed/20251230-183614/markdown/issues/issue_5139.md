# Enhance `ResourcelessJobRepository` implementation for testing

**Issue番号**: #5139

**状態**: closed | **作成者**: benelog | **作成日**: 2025-12-07

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5139

## 内容

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


## コメント

### コメント 1 by arey

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

### コメント 2 by benelog

**作成日**: 2025-12-10

@arey
I had the same thought and have incorporated it into the following pull request:
https://github.com/spring-projects/spring-batch/pull/5140

### コメント 3 by fmbenhassine

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

### コメント 4 by benelog

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


### コメント 5 by fmbenhassine

**作成日**: 2025-12-11

Resolved with #5140. Thank you for raising the issue and contributing a PR 🙏

### コメント 6 by phactum-mnestler

**作成日**: 2025-12-15

For anyone finding this issue the same way as me:
We're using the Spring Boot auto configuration, and after the upgrade to Spring Boot 4 we suddenly had both this issue and #5108, as the framework suddenly provided `ResourcelessJobRepository` instead of `SimpleJobRepository`. Adding an additional dependency for `spring-boot-starter-batch-jdbc` fixed the issue for us.

