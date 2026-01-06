# ChunkOrientedStepBuilder: Default SkipPolicy should be NeverSkipItemSkipPolicy when only retry is configured (not AlwaysSkipItemSkipPolicy)

**Issue番号**: #5077

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5077

**関連リンク**:
- Commits:
  - [ce7e03a](https://github.com/spring-projects/spring-batch/commit/ce7e03acf9766983019be34e3b2a633756b5669f)
  - [e77e21c](https://github.com/spring-projects/spring-batch/commit/e77e21cb7926f4689b9903bb65ae81bc80a56e7a)

## 内容

Hi Spring Batch team,

I think I've found an unexpected behavior change in Spring Batch 6 regarding the default skip policy when only retry is configured.


**Bug description**

When configuring only retry settings without any skip configuration, the default `SkipPolicy` is set to `AlwaysSkipItemSkipPolicy`. This causes all items that fail after exhausting retry attempts to be silently skipped instead of failing the step, which seems unintended.


**Environment**

- Spring Batch version: 6.0.0-RC2


**Steps to reproduce**
1. Configure a chunk-oriented step with retry but WITHOUT skip configuration:


2. Throw an exception from processor that exceeds retry limit

4. Observe that the item is skipped instead of failing the step


**Expected behavior**
When only retry is configured without any skip settings, items that fail after exhausting all retry attempts should **fail the step**, not be skipped.

The default `SkipPolicy` should be `NeverSkipItemSkipPolicy` (or equivalent) when skip is not explicitly configured.

**Root cause **

In `ChunkOrientedStepBuilder`:
```java
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new AlwaysSkipItemSkipPolicy(); // ← This seems wrong
    }
}
```

When neither `skippableExceptions` nor `skipLimit` is configured, it defaults to `AlwaysSkipItemSkipPolicy`, causing unexpected skip behavior.


**Comparison with Spring Batch 5**

In Spring Batch 5's `FaultTolerantStepBuilder`:
```java
if (skipPolicy == null) { // default == null
    if (skippableExceptionClasses.isEmpty() && skipLimit > 0) {
        logger.debug(String.format(
            "A skip limit of %s is set but no skippable exceptions are defined.",
            skipLimit));
    }
    skipPolicy = limitCheckingItemSkipPolicy; 
}
```

This would result in step failure when retry is exhausted without skip configuration.


**Suggested fix**
Change the default `SkipPolicy` to `NeverSkipItemSkipPolicy` when skip is not configured:
```java
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new NeverSkipItemSkipPolicy(); // ← Should be this
    }
}
```

**Minimal Complete Reproducible example**
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
    public Step issueReproductionStep(
            JobRepository jobRepository
    ) {
        return new StepBuilder(jobRepository)
                .<String, String>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retry(ProcessingException.class)
                .retryLimit(2)
                // No skip configuration - expecting step to fail after retry exhausted
                .build();
    }

    @Bean
    public ItemReader<String> issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor<String, String> issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("Exception thrown for: {}", item);
                throw new ProcessingException("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter<String> issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }

    public static class ProcessingException extends RuntimeException {
        public ProcessingException(String message) {
            super(message);
        }
    }

}

**Actual behavior **

```bash
Executing step: [issueReproductionStep]
Successfully processed: Item_1
Successfully processed: Item_2
Exception thrown for: Item_3
Exception thrown for: Item_3
Exception thrown for: Item_3
Writing items: [Item_1, Item_2]
Written: Item_1
Written: Item_2
Step: [issueReproductionStep] executed in 2s13ms
```

Could you please review this behavior? If you have any questions or need additional information, please feel free to let me know.

Thank you for your time and consideration!





## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-13

That's correct, by default we should never skip items until explicitly requested by the user. Should be fixed now. Thank you for raising this!

