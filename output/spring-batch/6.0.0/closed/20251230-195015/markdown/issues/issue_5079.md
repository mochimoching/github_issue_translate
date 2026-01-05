# ChunkOrientedStep does not throw exception when skipPolicy.shouldSkip() returns false

**Issue番号**: #5079

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-07

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5079

**関連リンク**:
- Commits:
  - [946f788](https://github.com/spring-projects/spring-batch/commit/946f78825414b872f3d27110ff53347a86d362e5)
  - [97065fc](https://github.com/spring-projects/spring-batch/commit/97065fc40256ac18388f8ebdd157e7c744bc1a6a)

## 内容

Hi Spring Batch team,

I think, I’ve discovered a bug in `ChunkOrientedStep` where failed items are silently discarded when the skip policy rejects skipping.

## Bug description

When retry is exhausted in fault-tolerant mode, `ChunkOrientedStep` calls `skipPolicy.shouldSkip()` to determine whether the failed item should be skipped. However, when `skipPolicy.shouldSkip()` returns `false` (meaning the item should NOT be skipped), the code does not throw an exception. This causes the failed item to be silently lost, and the job continues as if nothing happened.

This affects three methods in `ChunkOrientedStep`:
- `doSkipInRead()` (line 528)
- `doSkipInProcess()` (line 656)
- `scan()` (line 736)

## Environment

- Spring Batch version: 6.0.0-RC2

## Steps to reproduce
1. Configure a fault-tolerant step with a skip policy that always returns `false` (never skip)
2. Configure retry with a limited number of attempts (e.g., retryLimit = 2)
3. Process items where one item consistently fails
4. After retry exhaustion, observe that the failed item is silently discarded instead of causing the job to fail

## Expected behavior

When `skipPolicy.shouldSkip()` returns `false`, the exception should be re-thrown to:
- Roll back the transaction
- Mark the step as FAILED
- Prevent silent data loss

The job should fail with a clear error indicating that the skip limit was exceeded or skip policy rejected skipping.

## Minimal Complete Reproducible example
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
                .<String, String>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retryLimit(2)
                .skipPolicy(new NeverSkipItemSkipPolicy())  
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
```

**Actual output:**
Step COMPLETED

```
Job: [SimpleJob: [name=issueReproductionJob]] launched with the following parameters: [{}]
Executing step: [issueReproductionStep]
Successfully processed: Item_1
Successfully processed: Item_2
Exception thrown for: Item_3
Exception thrown for: Item_3
Exception thrown for: Item_3
Writing items: [Item_1, Item_2]
Written: Item_1
Written: Item_2
Step: [issueReproductionStep] executed in 2s18ms
Job: [SimpleJob: [name=issueReproductionJob]] completed with the following parameters: [{}] and the following status: [COMPLETED] in 2s20ms
```

As you can see, `Item_3` failed 3 times (initial attempt + 2 retries), but was silently discarded. The job completed successfully with status `COMPLETED`, even though `NeverSkipItemSkipPolicy` should have rejected skipping.

**Expected output:**
The job should fail with status `FAILED` because the skip policy does not allow skipping the failed item.

---

**Proposed fix:**

The three affected methods should throw an exception when `skipPolicy.shouldSkip()` returns `false`:
```java
private void doSkipInRead(RetryException retryException, StepContribution contribution) {
    Throwable cause = retryException.getCause();
    if (this.skipPolicy.shouldSkip(cause, contribution.getStepSkipCount())) {
        this.compositeSkipListener.onSkipInRead(cause);
        contribution.incrementReadSkipCount();
    } else {
        throw new NonSkippableReadException("Skip policy rejected skipping", cause);
    }
}
```

Similar changes should be applied to `doSkipInProcess()` and the catch block in `scan()`.

Thank you for your attention to this issue!

## コメント

### コメント 1 by JunggiKim

**作成日**: 2025-11-08

Created pull request #5081 to fix this issue

### コメント 2 by fmbenhassine

**作成日**: 2025-11-13

I think I misunderstood this bug report when I reacted with 👍 on the issue description.

> when `skipPolicy.shouldSkip()` returns `false` (meaning the item should NOT be skipped), the code does not throw an exception

Why should it throw an exception in that case? That is not an exceptional behaviour. Skipping an item means calling the `SkipListener` for it. Not skipping an item means discarding it (ie ignore it without calling the `SkipListener` for it).

The example you shared uses a `NeverSkipItemSkipPolicy`, which means never call `SkipListener` for any item that exhausted the retry policy, which effectively means ignore all these items (it is not a data loss, it is an explicit ask to not skip items but rather to ignore them). 

Therefore, and unless I am missing something, I think the current behaviour is correct. Do you agree?



### コメント 3 by KILL9-NO-MERCY

**作成日**: 2025-11-14

@fmbenhassine 

Based on my understanding of Spring Batch 5’s FaultTolerantChunkProvider and FaultTolerantChunkProcessor, 

the behavior was as follows:
- With skipping off, exceptions in ItemReader / ItemProcessor / ItemWriter are propagated to the step, causing it to fail.
- With skipping on, if the SkipPolicy allows skipping, the exception is swallowed for that item only, and processing continues.
- With skipping on, if the SkipPolicy disallows skipping, the exception is propagated(actually wrapped in a RetryException), causing the step to fail.

This aligns with my expectation when raising this issue (even in Batch 5, non-skippable exceptions could be ignored only by explicitly using the noRollback() method on the FaultTolerantStepBuilder).

In Batch 6, while changes to the behavior are understandable as a design decision, I am concerned that failed items may be silently discarded when the SkipPolicy disallows skipping, potentially causing data loss. I would expect the step to fail in such cases, consistent with Batch 5 behavior.

### コメント 4 by fmbenhassine

**作成日**: 2025-11-14

Thank you for the clarification! I previously said "unless I am missing something, I think the current behaviour is correct", and indeed I was missing an important detail: the skip policy contract clearly mentions that when the method `shouldSkip` returns false, the processing should NOT continue (ie the step should fail):

```
@FunctionalInterface
public interface SkipPolicy {

	/**
	 * Returns true or false, indicating whether or not processing should continue with the given throwable. 
	 * [...]
	 * @return true if processing should continue, false otherwise.
         [...]
	 */
	boolean shouldSkip(Throwable t, long skipCount) throws SkipLimitExceededException;

}
```

So this is a valid issue and should be fixed. The PR #5081 LGTM and I will merge it for the GA.

Thank you for your feedback!



### コメント 5 by KILL9-NO-MERCY

**作成日**: 2025-11-14

Thank you for the quick feedback! I’m glad my report could be of some help, even in the few days remaining before the GA. I really appreciate your time and attention on this.

