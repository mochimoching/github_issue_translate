# ChunkOrientedStep: Unnecessary ItemReader.read() calls when chunk size exceeds item count

**Issue番号**: #5048

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5048

**関連リンク**:
- Commits:
  - [706add7](https://github.com/spring-projects/spring-batch/commit/706add77b8259f51ae8cf7f9d6dfec6dcdb424b2)

## 内容

Hi Spring Batch team! 
First of all, thank you for the amazing work on Spring Batch 6 and New ChunkOrientedStep. I really appreciate this improvements.

I discovered what appears to be a bug in the chunk reading logic. 


## Bug description
When the chunk size is larger than the number of available items, `ItemReader.read()` and `ItemReadListener.beforeRead()` continue to be called for the remaining chunk size even after `read()` returns `null`. This results in unnecessary method invocations and potential side effects.

**Example:**
- Chunk size: 10
- Available items: 5
- Expected `read()` calls: 6 (5 items + 1 null)
- **Actual `read()` calls: 10** (5 items + 5 nulls)

## Environment
- **Spring Batch version:** 6.0.0-RC1

## Steps to reproduce
1. Configure a chunk-oriented step with chunk size larger than available items
2. Use any ItemReader that returns null when exhausted
3. Add an ItemReadListener to track method calls
4. Run the job and observe the logs

## Expected behavior
Once `ItemReader.read()` returns `null`, the chunk reading loop should terminate immediately:
- `beforeRead()` should be called: **6 times** (5 items + 1 null check)
- `read()` should be called: **6 times** (5 items + 1 null)
- Loop should break after first `null` return

## Actual behavior
The loop continues for the entire chunk size:
- `beforeRead()` is called: **10 times** (5 items + 5 unnecessary null checks)
- `read()` is called: **10 times** (5 items + 5 unnecessary null returns)
- Unnecessary method invocations waste resources and may trigger unintended side effects


## Root cause
In `ChunkOrientedStep.readChunk()` method (line 478-487), the for loop continues for the entire chunk size without breaking when `item` is `null`:
```java
private Chunk readChunk(StepContribution contribution) throws Exception {
    Chunk chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        }
        // Missing break when item is null!
    }
    return chunk;
}
```

## Impact
1. **Performance degradation**: Especially severe when chunk size is large
   - Chunk size 1000, Items 10 → 990 unnecessary calls
2. **ItemReadListener miscounts**: `beforeRead()` called more times than actual reads
3. **Potential side effects**: If `read()` implementation has side effects (logging, metrics, connection checks, API calls), they execute unnecessarily
4. **Resource waste**: Unnecessary method invocations and stack operations



## Minimal Complete Reproducible example
@Slf4j
@Configuration
public class ChunkSizeIssueReproductionJobConfiguration {
    
    @Bean
    public Job reproductionJob(JobRepository jobRepository, Step reproductionStep) {
        return new JobBuilder(jobRepository)
                .start(reproductionStep)
                .build();
    }

    @Bean
    public Step reproductionStep(
            JobRepository jobRepository,
            CountingListItemReader countingListItemReader) {
        return new StepBuilder(jobRepository)
                .chunk(10)  // Chunk size: 10
                .reader(countingListItemReader)
                .writer(chunk -> {
                    log.info("=== Writer: Processing {} items ===", chunk.size());
                    chunk.forEach(item -> log.info("Writing item: {}", item));
                })
                .listener(new ReadCountListener())
                .build();
    }

    @Bean
    public CountingListItemReader countingListItemReader() {
        // Only 5 items (less than chunk size of 10)
        return new CountingListItemReader(List.of(
                "Item-1",
                "Item-2",
                "Item-3",
                "Item-4",
                "Item-5"
        ));
    }

    @Slf4j
    static class CountingListItemReader extends ListItemReader {
        private int readCallCount = 0;

        public CountingListItemReader(List list) {
            super(list);
        }

        @Override
        public String read() {
            readCallCount++;
            String item = super.read();

            if (item == null) {
                log.warn(">>> read() #{}: Returned NULL <<>> read() #{}: {}", readCallCount, item);
            }

            return item;
        }
    }

    @Slf4j
    static class ReadCountListener implements ItemReadListener {
        private int beforeReadCount = 0;
        private int afterReadCount = 0;

        @Override
        public void beforeRead() {
            beforeReadCount++;
            log.info(">>> beforeRead() #{} called", beforeReadCount);
        }

        @Override
        public void afterRead(String item) {
            afterReadCount++;
            log.info(">>> afterRead() #{} called for: {}", afterReadCount, item);
        }
    }
}

**Console output:**
```
>>> beforeRead() #1 called
>>> read() #1: Item-1
>>> afterRead() #1 called for: Item-1
>>> beforeRead() #2 called
>>> read() #2: Item-2
>>> afterRead() #2 called for: Item-2
>>> beforeRead() #3 called
>>> read() #3: Item-3
>>> afterRead() #3 called for: Item-3
>>> beforeRead() #4 called
>>> read() #4: Item-4
>>> afterRead() #4 called for: Item-4
>>> beforeRead() #5 called
>>> read() #5: Item-5
>>> afterRead() #5 called for: Item-5
>>> beforeRead() #6 called
>>> read() #6: Returned NULL <
>>> beforeRead() #7 called        ← Unnecessary
>>> read() #7: Returned NULL <<<  ← Unnecessary
>>> beforeRead() #8 called        ← Unnecessary
>>> read() #8: Returned NULL <<<  ← Unnecessary
>>> beforeRead() #9 called        ← Unnecessary
>>> read() #9: Returned NULL <<<  ← Unnecessary
>>> beforeRead() #10 called       ← Unnecessary
>>> read() #10: Returned NULL <<< ← Unnecessary
=== Writer: Processing 5 items ===
Writing item: Item-1
Writing item: Item-2
Writing item: Item-3
Writing item: Item-4
Writing item: Item-5
```

## Proposed fix
Add a `break` statement when `item` is `null`:
```java
private Chunk readChunk(StepContribution contribution) throws Exception {
    Chunk chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else {
            break;  // Stop reading when null is returned
        }
    }
    return chunk;
}
```

Let me know if you need any additional information or if I should submit a PR for this fix. Thanks again for your great work on Spring Batch!


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-10-28

Thank you for your early feedback on 6.0 RC1!

This is indeed a bug, I planned the fix for the upcoming RC2.

