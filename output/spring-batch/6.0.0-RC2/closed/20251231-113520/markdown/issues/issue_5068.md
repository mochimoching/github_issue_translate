# ChunkOrientedStepBuilder throws IllegalArgumentException when retry() is used(configured) without retryLimit()

**Issue番号**: #5068

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-31

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5068

**関連リンク**:
- Commits:
  - [6fdc225](https://github.com/spring-projects/spring-batch/commit/6fdc22521564234630f4e6ae021b466a22cc29be)

## 内容

Hello Spring Batch team,

Thank you for your continued work on Spring Batch. I believe I've found a bug or documentational enhencement in the `ChunkOrientedStepBuilder` related to retry configuration.


**Bug description**
When using ChunkOrientedStepBuilder.retry() to specify retryable exceptions without calling retryLimit(), the step builder fails with an IllegalArgumentException during the build phase. This occurs because retryLimit defaults to -1, which is rejected by RetryPolicy.Builder.maxAttempts().


**Environment**
Spring Batch version: 6.0.0-RC1
Spring Framework version: 7.0.0-RC2

**Steps to reproduce**
Create a chunk-oriented step using StepBuilder
Call .retry(SomeException.class) without calling .retryLimit()
Attempt to build the step

**Expected behavior**
The step should build successfully without throwing an exception.

**Actual behavior**
Exception thrown:
```
Caused by: java.lang.IllegalArgumentException: Invalid maxAttempts (-1): must be positive or zero for no retry.
	at org.springframework.util.Assert.isTrue(Assert.java:136)
	at org.springframework.core.retry.RetryPolicy.assertMaxAttemptsIsNotNegative(RetryPolicy.java:105)
	at org.springframework.core.retry.RetryPolicy$Builder.maxAttempts(RetryPolicy.java:200)
	at org.springframework.batch.core.step.builder.ChunkOrientedStepBuilder.build(ChunkOrientedStepBuilder.java:404)
```


**Minimal Complete Reproducible example**
```java
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        AtomicInteger counter = new AtomicInteger(0);

        return new StepBuilder(jobRepository)
                .<String, String>chunk(5)
                .reader(() -> {
                    int count = counter.incrementAndGet();
                    if (count <= 5) {
                        return "kill-" + count;
                    }
                    return null;
                })
                .writer(items -> items.forEach(item ->
                        System.out.println("💀 Terminated: " + item)
                ))
                .faultTolerant()
                .retry(IOException.class)
                //.retryLimit(1)  // ← This must be added for proper operation
                .build();  // ← IllegalArgumentException thrown here
    }
}
```

## Root cause analysis

In `ChunkOrientedStepBuilder`:
```java
private long retryLimit = -1;  // Default value

public ChunkOrientedStep build() {
    // ...
    if (this.retryPolicy == null) {
        // This condition uses OR, so it's true when only retryableExceptions is set
        if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
            this.retryPolicy = RetryPolicy.builder()
                .maxAttempts(this.retryLimit)  // ← Passes -1 here
                .includes(this.retryableExceptions)
                .build();  // ← Fails here
        }
        else {
            this.retryPolicy = throwable -> false;
        }
    }
    // ...
}
```

In `RetryPolicy.Builder`:
```java
public Builder maxAttempts(long maxAttempts) {
    assertMaxAttemptsIsNotNegative(maxAttempts);  // ← Rejects -1
    this.maxAttempts = maxAttempts;
    return this;
}
private static void assertMaxAttemptsIsNotNegative(long maxAttempts) {
    Assert.isTrue(maxAttempts >= 0,
        () -> "Invalid maxAttempts (%d): must be positive or zero for no retry."
              .formatted(maxAttempts));
}
```


## Suggested fixes
### Option 1: Change default value
private long retryLimit = 0;  // Change from -1 to 0

### Option 2: Add documentation
Add JavaDoc to `retry()`  method stating that `retryLimit()`  must be called with a positive value (greater than 0) respectively.


Thank you for reviewing this issue. Please let me know if you need any additional information or clarification.



## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-04

Thank you for reporting this valid issue! Similar to #5069, I will change the default value of retry limit as it was in v5 (which is 0).

