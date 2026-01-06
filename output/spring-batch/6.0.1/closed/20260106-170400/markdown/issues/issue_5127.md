# Fault-tolerant step: `retry(Class)` traverses exception causes, `skip(Class)` does not

**Issue番号**: #5127

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-03

**ラベル**: type: bug, in: core, has: minimal-example, related-to: fault-tolerance

**URL**: https://github.com/spring-projects/spring-batch/issues/5127

**関連リンク**:
- Commits:
  - [8cade4d](https://github.com/spring-projects/spring-batch/commit/8cade4d656f79646ed99ba68cd6e8b77ee0fe862)
  - [2c57f8d](https://github.com/spring-projects/spring-batch/commit/2c57f8d13e6f8fda7b89cfaa9b9668209bc6ee54)
  - [5edb62f](https://github.com/spring-projects/spring-batch/commit/5edb62f0c818f4505804b46b45f5843556e6e826)

## 内容

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

## コメント

### コメント 1 by kzander91

**作成日**: 2025-12-03

After more debugging, I'm getting more confused, perhaps the logic here is inverted as well?
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L688-L702
Why is `this.skipPolicy.shouldSkip()` negated? This error, which is logged when the `SkipPolicy` _does_ indicate a skip, also indicates that the inverse was intended:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L700


### コメント 2 by fmbenhassine

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

### コメント 3 by therepanic

**作成日**: 2025-12-16

Hi, @fmbenhassine! Thank you for all your work on this project!

You wrote that you probably won't have time to work on this, so I decided to do PR today. Maybe you'll be able to review it and, if necessary, polish it up and release it directly in the new 6.0.1 release. In any case, I think it needs to be fixed in 6.0.2. I also left a couple of comments. PTAL https://github.com/spring-projects/spring-batch/pull/5171.


### コメント 4 by fmbenhassine

**作成日**: 2025-12-16

> You wrote that you probably won't have time to work on this, so I decided to do PR today.

This is so kind! Thank you very much for your help 🙏

I will take a loop at your PR.

