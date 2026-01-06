# MetaDataInstanceFactory.createStepExecution(JobParameters) does not propagate JobParameters to StepExecution

**Issue番号**: #5115

**状態**: closed | **作成者**: benelog | **作成日**: 2025-11-27

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5115

**関連リンク**:
- Commits:
  - [1a5b8d0](https://github.com/spring-projects/spring-batch/commit/1a5b8d0321fd6efd02c589b0711260f93fe9315f)
  - [da16f6b](https://github.com/spring-projects/spring-batch/commit/da16f6b92ecc1b4d5ed0acb947df1dad923e590a)
  - [8264ab1](https://github.com/spring-projects/spring-batch/commit/8264ab11b9fa1905da648f454a050dd058b3fda0)

## 内容

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


## コメント

### コメント 1 by benelog

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


