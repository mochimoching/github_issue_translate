# ChunkOrientedStepBuilder: All Throwables (including Errors) are retried when only retryLimit() is configured without retry()

**Issue番号**: #5078

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5078

**関連リンク**:
- Commits:
  - [4d6a5fa](https://github.com/spring-projects/spring-batch/commit/4d6a5fa39b223226a73330498024857cb34d6046)
  - [638c183](https://github.com/spring-projects/spring-batch/commit/638c1834fa1e88ed5017c3081f94e61205289e92)
  - [f606e6f](https://github.com/spring-projects/spring-batch/commit/f606e6f31c9ce6334183384485f14422e124a685)
  - [8ed93d1](https://github.com/spring-projects/spring-batch/commit/8ed93d1900b5a6d0a17e8a1ad1355c1d30e5c918)

## 内容

Hello Spring Batch team,
Following up on previous issue #5068, I discovered a related but opposite scenario that poses a potential risk.

While reviewing the fix for #5068, I realized that when `retryLimit()` is configured **without** `retry()`, all Throwables (including critical Errors like `OutOfMemoryError`, `StackOverflowError`) become retryable. It would have been great to catch this alongside the previous issue.


**Bug description**
When configuring `retryLimit()` without specifying `retry()` in Spring Batch 6, the retry mechanism attempts to retry **all Throwables**, including critical JVM Errors. This occurs because `ExceptionTypeFilter`(used by `DefaultRetryPolicy`) uses `matchIfEmpty = true` when both `includes`(configured by retry()) and `excludes` are empty.


**Environment**
- Spring Batch version: 6.0.0-RC2


**Steps to reproduce**
1. Configure a chunk-oriented step with `retryLimit()` but WITHOUT `retry()`:
@Bean
public Step step() {
    return new StepBuilder("step", jobRepository)
        .chunk(10, transactionManager)
        .reader(reader())
        .processor(processor())
        .writer(writer())
        .faultTolerant()
        .retryLimit(3)
        // No retry() configuration
        .build();
}

2. Throw a critical Error (e.g., `OutOfMemoryError`) from any component(ItemReader or ItemProcessor etc)
3. Observe that even critical Errors are being retried



**Expected behavior**
When only `retryLimit()` is configured without `retry()`:
- Either no exceptions should be retried
- Or only `Exception` and its subclasses should be retried (excluding `Error`)

**Actual behavior**
All Throwables (including Errors) are retried due to `matchIfEmpty = true`.

**Minimal Complete Reproducible example**
```java
@Slf4j
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
        return new StepBuilder(jobRepository)
                .chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retryLimit(2)
                // No retry() - expecting no retry or Exception-only retry
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("OutOfMemoryError thrown for: {}", item);
                throw new OutOfMemoryError("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }
}
```


**Actual output:**
```
Successfully processed: Item_1
Successfully processed: Item_2
OutOfMemoryError thrown for: Item_3
OutOfMemoryError thrown for: Item_3  ← Retry 1
OutOfMemoryError thrown for: Item_3  ← Retry 2
Writing items: [Item_1, Item_2] ← Item_3 is skipped and writer proceeds (reported separately in #5077)
Written: Item_1
Written: Item_2


The `OutOfMemoryError` is retried 2 times, which could worsen the system state.

**Root cause analysis**
In `ChunkOrientedStepBuilder`:
```java
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(this.retryableExceptions)  // ← Empty set!
          .build();
    }
    else {
       this.retryPolicy = throwable -> false;
    }
}

When `retryableExceptions` is empty, `DefaultRetryPolicy` uses `ExceptionTypeFilter` with both `includes` and `excludes` empty.
In `ExceptionTypeFilter.matchTraversingCauses()`:
```java
private boolean matchTraversingCauses(Throwable exception) {
    boolean emptyIncludes = super.includes.isEmpty();
    boolean emptyExcludes = super.excludes.isEmpty();

    if (emptyIncludes && emptyExcludes) {
        return super.matchIfEmpty;  // ← Returns true!
    }
    // ...
}
```

Since `matchIfEmpty = true`, **all Throwables match**, including critical Errors.

**Suggested fix**

When `retryLimit()` is configured without `retry()`, default to `Exception.class` to exclude Errors:
```java
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       Set<Class> exceptions = this.retryableExceptions.isEmpty()
             ? Set.of(Exception.class)
             : this.retryableExceptions;

       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(exceptions)
          .build();
    }
    else {
       this.retryPolicy = throwable -> false;
    }
}
```

This ensures:
- Only `Exception` and its subclasses are retried by default
- Critical JVM Errors are not retried
- Users can still explicitly include specific exceptions via `retry()`



Could you please review this behavior? This seems like a potential risk when users configure retry limits without specifying which exceptions to retry.

Thank you for your time and consideration!

