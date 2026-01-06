# Incorrect error message in JobOperatorTestUtils constructor

**Issue番号**: #5051

**状態**: closed | **作成者**: KMGeon | **作成日**: 2025-10-26

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5051

**関連リンク**:
- Commits:
  - [8a598dc](https://github.com/spring-projects/spring-batch/commit/8a598dc8300873fee55421b9dac5bc7cc0c9a8d3)
  - [b848638](https://github.com/spring-projects/spring-batch/commit/b848638e5798a19d847798891b586908426487b0)

## 内容

## Issue Description

- The constructor of `JobOperatorTestUtils` has an incorrect error message for the `jobOperator` parameter validation.


## Current Behavior

```java
public JobOperatorTestUtils(JobOperator jobOperator, JobRepository jobRepository) {
	Assert.notNull(jobOperator, "JobRepository must not be null");
	Assert.notNull(jobRepository, "JobRepository must not be null");
	this.jobOperator = jobOperator;
	this.jobRepository = jobRepository;
}
```

## Expected Behavior

```java
public JobOperatorTestUtils(JobOperator jobOperator, JobRepository jobRepository) {
	Assert.notNull(jobOperator, "JobOperator must not be null");
	Assert.notNull(jobRepository, "JobRepository must not be null");
	this.jobOperator = jobOperator;
	this.jobRepository = jobRepository;
}
```

## File

`spring-batch-test/src/main/java/org/springframework/batch/test/JobOperatorTestUtils.java`

