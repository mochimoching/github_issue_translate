# ChunkOrientedStepBuilder throws IllegalArgumentException when skip() is used(configured) without skipLimit()

**Issue番号**: #5069

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-31

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5069

**関連リンク**:
- Commits:
  - [3df1f34](https://github.com/spring-projects/spring-batch/commit/3df1f34b7363954d1718737c8386afad85eb82af)

## 内容

Hello Spring Batch team

**Bug description**
When using `ChunkOrientedStepBuilder.skip()` to specify skippable exceptions without calling `skipLimit()`, the step builder fails with an `IllegalArgumentException` during the build phase. This occurs because `skipLimit` defaults to `-1`, which is rejected by `LimitCheckingExceptionHierarchySkipPolicy` constructor.

This is the same root cause as the retry configuration issue (https://github.com/spring-projects/spring-batch/issues/5068), where the default value is `-1` and the validation logic rejects it.


**Environment**
- Spring Batch version: 6.0.0-RC1
- Spring Framework version: 7.0.0-RC2

**Steps to reproduce**
1. Create a chunk-oriented step using `StepBuilder`
2. Call `.skip(SomeException.class)` without calling `.skipLimit()`
3. Attempt to build the step
4. 
**Expected behavior**
The step should build successfully without throwing an exception.


**Actual behavior**
Exception thrown:
```
Caused by: java.lang.IllegalArgumentException: The skipLimit must be greater than zero
	at org.springframework.util.Assert.isTrue(Assert.java:117)
	at org.springframework.batch.core.step.skip.LimitCheckingExceptionHierarchySkipPolicy.<init>(LimitCheckingExceptionHierarchySkipPolicy.java:45)
	at org.springframework.batch.core.step.builder.ChunkOrientedStepBuilder.build(ChunkOrientedStepBuilder.java:415)
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
                .chunk(5)
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
                .skip(IOException.class)
                //.skipLimit(1)  // ← This must be added for proper operation
                .build();  // ← IllegalArgumentException thrown here
    }
}
```

## Root cause analysis
In `ChunkOrientedStepBuilder`:
```java
private long skipLimit = -1;  // Default value

public ChunkOrientedStep build() {
    // ...
    if (this.skipPolicy == null) {
        // This condition uses OR, so it's true when only skippableExceptions is set
        if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
            this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(
                this.skippableExceptions,
                this.skipLimit  // ← Passes -1 here
            );  // ← Fails here
        }
        else {
            this.skipPolicy = new AlwaysSkipItemSkipPolicy();
        }
    }
    // ...
}
```
In `LimitCheckingExceptionHierarchySkipPolicy`:
```java
public LimitCheckingExceptionHierarchySkipPolicy(
        Set<Class> skippableExceptions,
        long skipLimit) {
    Assert.notEmpty(skippableExceptions, "The skippableExceptions must not be empty");
    Assert.isTrue(skipLimit > 0, "The skipLimit must be greater than zero");  // ← Rejects -1
    this.skippableExceptions = skippableExceptions;
    this.skipLimit = skipLimit;
}
```


## Suggested fixes
### Option 1: Change default value
```java
private long skipLimit = 0;  // Change from -1 to 0
```

### Option 2: Add documentation
Add JavaDoc to `skip()` method stating that `skipLimit()` must be called with a positive value (greater than 0).
```java
/**
 * Configure exceptions that should be skipped.
 * Note: {@link #skipLimit(long)} must be called with a positive value 
 * before building the step when using this method.
 * @param skippableExceptions exceptions to skip
 * @return this for fluent chaining
 */
@SafeVarargs
public final ChunkOrientedStepBuilder skip(Class... skippableExceptions)
```

---
Thank you for reviewing this issue. Please let me know if you need any additional information or clarification.



## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-04

Thank you for reporting this! Indeed, the step configuration fails when the skip limit is omitted. The default value in the previous implementation [was set to 10](https://github.com/spring-projects/spring-batch/blob/82bd3a2bad3d43771d0df5cdd190c1ebd2a8e5f7/spring-batch-core/src/main/java/org/springframework/batch/core/step/builder/FaultTolerantStepBuilder.java#L133), so I will change the new implementation with similar default values to facilitate the migration to v6.

