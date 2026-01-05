# ChunkOrientedStep: Regression from #5048 - breaks on skip in fault-tolerant mode

**Issue番号**: #5084

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-11

**ラベル**: type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5084

**関連リンク**:
- Commits:
  - [4c9fe94](https://github.com/spring-projects/spring-batch/commit/4c9fe94bb12d6a9679848221abbadbbaa1b494f8)

## 内容

Hi Spring Batch team, Thank you for the great work on Spring Batch 6.


**Bug description**
When Issue [#5048](https://github.com/spring-projects/spring-batch/issues/5048) was reported, I made a mistake in my proposed fix that added `else { break; } `to the read loop.

The fix didn't account for the distinction between two different scenarios where readItem() returns null:
1) End-of-data (EOF): No more items available → Should break ✅
2) Skip in fault-tolerant mode: Exception skipped → Should continue reading ❌

The current loop termination condition in readChunk() treats both cases identically, causing premature read loop termination when skips occur.

**Example scenario:**
Chunk size: 3
Item-2 throws exception → Skip occurs
Expected: Skip Item-2 and continue reading Item-3 (2 items in chunk: Item-1, Item-3)
Actual: Read loop breaks after Item-1 (1 item in chunk)

**Environment**
Spring Batch version: 6.0.0-RC2 (after #5048 fix in commit 706add7)


**Steps to reproduce**
Configure a chunk-oriented step with:
Chunk size: 3
Fault-tolerant: true
Skip policy configured (e.g., AlwaysSkipItemSkipPolicy)

Use an ItemReader that throws exception on the 2nd item
Run the job and observe chunk sizes in the logs

**Expected behavior**
When a skip occurs during item reading in fault-tolerant mode:

The problematic item should be skipped
The read loop should continue to fill the chunk up to the configured chunk size
Expected chunk: [Item-1, Item-3] (2 items, Item-2 skipped)


**Expected console output:**
```bash
>>>> Read: Item-1
>>>> EXCEPTION on Item-2!
>>>> Skip occurred on reader
>>>> Read: Item-3
>>>> EOF: No more items
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-3
```
→ Both Item-1 and Item-3 processed in the same chunk

**Actual behavior**
When a skip occurs, the read loop terminates immediately:
Actual chunk 1: [Item-1] (1 item only)
Actual chunk 2: [Item-3] (remaining item in next chunk)

**Actual console output:**
```bash
>>>> Read: Item-1
>>>> EXCEPTION on Item-2!
>>>> Skip occurred on reader
>>>> Successfully processed: Item-1
>>>> Writing items: Item-1
>>>> Read: Item-3
>>>> EOF: No more items
>>>> Successfully processed: Item-3
>>>> Writing items: Item-3
```
→ Item-1 and Item-3 processed in different chunks ❌

Minimal Complete Reproducible example
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
    public Step issueReproductionStep(JobRepository jobRepository, DataSource dataSource) {
        return new StepBuilder(jobRepository)
                .<TestItem, TestItem>chunk(3)
                .reader(issueReproductionReader(dataSource))
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .skipPolicy(new AlwaysSkipItemSkipPolicy())
                .skipListener(skipListener())
                .build();
    }

    @Bean
    public ItemReader<TestItem> issueReproductionReader(DataSource dataSource) {
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
            }
        };
    }

    private SkipListener<TestItem, TestItem> skipListener() {
        return new SkipListener<>() {
            @Override
            public void onSkipInRead(Throwable t) {
                log.info(">>>> Skip occurred on reader");
            }
        };
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    @Slf4j
    static class SkippableItemReader implements ItemReader<TestItem> {
        private int count = 0;
        private final List<TestItem> items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (count >= items.size()) {
                log.info(">>>> EOF: No more items");
                return null;
            }

            TestItem item = items.get(count);
            count++;

            // Throw exception on 2nd item (Item-2)
            if (count == 2) {
                log.error(">>>> EXCEPTION on Item-2!");
                throw new RuntimeException("Simulated read error on Item-2");
            }

            log.info(">>>> Read: {}", item.getName());
            return item;
        }
    }
}
```


**Root Cause Analysis**
In readItem() method (lines ~508-545)

When a skip occurs:
```java
catch (Exception exception) {
    this.compositeItemReadListener.onReadError(exception);
    if (this.faultTolerant && exception instanceof RetryException retryException) {
        doSkipInRead(retryException, contribution);
        // ⚠️ Returns null, but chunkTracker.moreItems() is still true!
    }
    // ...
}
return item;  // Returns null for skip
```
The chunkTracker.noMoreItems() is only called on actual end-of-data:
```java
item = doRead();
if (item == null) {
    this.chunkTracker.noMoreItems();  // Only set on EOF
}
```
So we have two distinct null return cases:
EOF: null returned + moreItems() == false
Skip: null returned + moreItems() == true

**In readChunk() method (lines ~478-487)**
Current problematic code(my mistake):
```java
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else {
            break;  // ❌ Breaks on BOTH EOF and skip!
        }
    }
    return chunk;
}
```
The `else { break; }` added in #5048 cannot distinguish between EOF and skip.

**Proposed Fix**
Change the break condition to check ChunkTracker state instead of blindly breaking on null:
**Fix for readChunk():**
```java
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else if (!chunkTracker.moreItems()) {  // ✅ Only break on actual EOF
            break;
        }
        // else: skip occurred, continue to next item
    }
    return chunk;
}
```

**Priority Note**
While this issue affects chunk size, the step continues to function correctly - all items are processed successfully, just with more transactions than intended. This can be addressed at your convenience based on priority.

**And**
The additional issue also exists in processChunkConcurrently() method

In concurrent processing mode, the same problem occurs but it was not addressed in the original #5048 fix.
**In processChunkConcurrently() method (lines ~431-438)**
Current code:
```java
// read items and submit concurrent item processing tasks
for (int i = 0; i < this.chunkSize; i++) {
    I item = readItem(contribution);
    if (item != null) {
        Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> processItem(item, contribution));
        itemProcessingTasks.add(itemProcessingFuture);
    }
    // ❌ No else clause - continues loop even after EOF, causing unnecessary read() calls
}
```
This method has TWO issues:
1) Original #5048 issue: No break on EOF → unnecessary readItem() calls continue
2) This issue: Even when fixed with else { break; }, it will break on skip (same as readChunk())


**Fix for processChunkConcurrently():**
```java
// read items and submit concurrent item processing tasks
for (int i = 0; i < this.chunkSize; i++) {
    I item = readItem(contribution);
    if (item != null) {
        Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> processItem(item, contribution));
        itemProcessingTasks.add(itemProcessingFuture);
    } else if (!chunkTracker.moreItems()) {  // ✅ Only break on actual EOF
        break;
    }
    // else: skip occurred, continue to next item
}
```
This fix addresses both issues:
- Prevents unnecessary reads after EOF (same with #5048 issue)
- Allows chunk to continue filling after skip (this issue)

If you have any questions about this issue or need additional information, please let me know.

Thank you for your continued responsiveness to issues despite your busy schedule. Please feel free to address this at your convenience based on priority.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-13

This is a valid issue. It was expected to have some bumps and edge cases in this new implementation of the chunk-oriented processing model, so thank you very much for reporting this issue (and others!) early in the RC phase 🙏 We clearly have a gap in our test suite for these edge cases and I will fix that for the GA.

### コメント 2 by fmbenhassine

**作成日**: 2025-11-13

> Change the break condition to check ChunkTracker state instead of blindly breaking on null:
> **Fix for readChunk():**

Thank you for the suggested fix! This is actually equivalent to:

```diff
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
--    for (int i = 0; i < chunkSize; i++) {
++    for (int i = 0; i < chunkSize && this.chunkTracker.moreItems(); i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
--        } else if (!chunkTracker.moreItems()) {  // ✅ Only break on actual EOF
--           break;
          }
    }
    return chunk;
}
```

which I find easier to think about, and which actually fixes both issues (the one in #5048 and this one, #5084) Amazing how #5084 is a regression of #5048 😉. I added `testSkipInReadInSequentialMode` and `testSkipInReadInConcurrentMode` in `ChunkOrientedStepFaultToleranceIntegrationTests` to cover those cases.

> The additional issue also exists in processChunkConcurrently() method

I fixed that as well and added `ChunkOrientedStepTests#testReadNoMoreThanAvailableItemsInConcurrentMode` to cover that case (similar to `ChunkOrientedStepTests#testReadNoMoreThanAvailableItemsInSequentialMode` that was added in #5048 )

---

Thanks again for reporting this issue!

