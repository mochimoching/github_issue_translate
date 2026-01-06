# ChunkOrientedStep: Retry exhausted in ItemWriter always triggers Chunk Scanning regardless of skip eligibility

**Issue番号**: #5091

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5091

**関連リンク**:
- Commits:
  - [cb55ccc](https://github.com/spring-projects/spring-batch/commit/cb55ccc44b30790385ed49f8ee1ed1b1f4978288)

## 内容

Hello Spring Batch team,
first of all, thank you for your continued effort in maintaining and improving the project.
I would like to report an issue in Spring Batch 6's ChunkOrientedStep fault-tolerant write flow.

**Bug description**
In Spring Batch 6, when an exception occurs in the ItemWriter and the retry policy becomes exhausted (RetryException),
ChunkOrientedStep always performs a chunk scanning, regardless of whether the exception is skip-eligible.

The issue is that there is no preliminary SkipPolicy evaluation before entering the scan, meaning:
- Even if the exception is not skippable, scan() is still invoked.
- Normal (non-failing) items in the chunk get written again(by sacnning), resulting in unintended duplicate writes.
- Ultimately, a NonSkippableWriteException is thrown inside the scan, but only after unintended writes have already been attempted.

In Spring Batch 5 (FaultTolerantChunkProcessor), this did not happen because the framework performed a SkipPolicy check before scanning the chunk, preventing unnecessary scanning for non-skippable exceptions.
like:
```java
RecoveryCallback<Object> recoveryCallback = context -> {
				/*
				 * If the last exception was not skippable we don't need to do any
				 * scanning. We can just bomb out with a retry exhausted.
				 */
				if (!shouldSkip(itemWriteSkipPolicy, context.getLastThrowable(), -1)) {
					throw new ExhaustedRetryException(
							"Retry exhausted after last attempt in recovery path, but exception is not skippable.",
							context.getLastThrowable());
				}

				inputs.setBusy(true);
				data.scanning(true);
				scan(contribution, inputs, outputs, chunkMonitor, true);
				return null;
			};
```

This results in incorrect behavior and is a functional regression from Spring Batch 5.




**Environment**
Spring Batch version: 6.0.0-RC2



**Minimal Complete Reproducible example**
```java
@Configuration
@Slf4j
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
                .<TestItem, TestItem>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .build();
    }

    @Bean
    public ItemReader<TestItem> issueReproductionReader() {
        return new SkippableItemReader();
    }

    @Bean
    public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
        return item -> {
            log.info(">>>> Successfully processed: {}", item.getName());
            return item;
        };
    }

    @Bean
    public ItemWriter<TestItem> issueReproductionWriter() {
        return items -> {
            for (TestItem item : items) {
                log.info(">>>> Writing items: {}", item.getName());
                if (item.id == 2) {
                    log.error(">>>> EXCEPTION on Item-2!");
                    throw new RuntimeException("Simulated write error on Item-2");
                }
            }
        };
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    static class SkippableItemReader implements ItemReader<TestItem> {
        private int index = 0;
        private final List<TestItem> items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (index >= items.size()) return null;
            return items.get(index++);
        }
    }
}
```
This example demonstrates the issue clearly:
after retry exhaustion, the framework enters chunk scan even though the thrown exception is not skippable, causing duplicate writes and an eventual NonSkippableWriteException


**Expected behavior**
Exception happens in writer
Retry attempts exhausted

Evaluate SkipPolicy for the exception

If skippable → proceed to scan

If not skippable → do not scan; fail immediately

Avoid duplicate writes and unintended extra write attempts.

**Actual behavior**
```bash
>>>> Read: Item-1
>>>> Read: Item-2
>>>> Read: Item-3
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-2
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> EXCEPTION on Item-2!
ChunkOrientedStep: Retry exhausted while attempting to write items, scanning the chunk

org.springframework.core.retry.RetryException: Retry policy for operation 'Retryable write operation' exhausted; aborting execution

...

>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> EXCEPTION on Item-2!
ChunkOrientedStep: Failed to write item: IssueReproductionJobConfiguration.TestItem(id=2, name=Item-2, description=Second item - will throw exception)

...

java.lang.RuntimeException: Simulated write error on Item-2
...

ChunkOrientedStep   : Rolling back chunk transaction

org.springframework.batch.core.step.skip.NonSkippableWriteException: Skip policy rejected skipping item

...

AbstractStep         : Encountered an error executing step issueReproductionStep in job issueReproductionJob

...


```

**Proposed fix**
To prevent unnecessary chunk scanning,
writeChunk() should perform a pre-scan SkipPolicy check when a RetryException is thrown, similar to the legacy behavior of FaultTolerantChunkProcessor in Spring Batch 5.

Specifically, inside the catch block of writeChunk(), a SkipPolicy validation can be added before triggering scan():
```java
catch (Exception exception) {
    ...

    if (this.faultTolerant && exception instanceof RetryException retryException) {

        // 💡 Proposed pre-scan SkipPolicy check
        if (!this.skipPolicy.shouldSkip(exception, -1)) {
            // If the exception is not skippable, skip scanning and fail immediately
            throw exception;
        }

        logger.info("Retry exhausted while attempting to write items, scanning the chunk", retryException);

        ChunkScanEvent chunkScanEvent = new ChunkScanEvent(
            contribution.getStepExecution().getStepName(),
            contribution.getStepExecution().getId()
        );

        chunkScanEvent.begin();
        scan(chunk, contribution);
        chunkScanEvent.skipCount = contribution.getSkipCount();
        chunkScanEvent.commit();

        logger.info("Chunk scan completed");
    }
    else {
        throw exception;
    }
}

```


Thank you for reviewing this issue!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

> first of all, thank you for your continued effort in maintaining and improving the project.

Thank YOU for your continued effort in testing Spring Batch 6 and providing invaluable feedback to us! Amazing bug reporting BTW, really appreciated 🙏

This is a valid issue, I will plan the fix for the upcoming GA.

