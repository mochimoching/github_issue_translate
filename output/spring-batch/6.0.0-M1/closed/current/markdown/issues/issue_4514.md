# Write Skip Count Not Updated in Chunk Processing

**Issue番号**: #4514

**状態**: closed | **作成者**: thilotanner | **作成日**: 2023-12-14

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4514

**関連リンク**:
- Commits:
  - [1fe91eb](https://github.com/spring-projects/spring-batch/commit/1fe91eb6fc80f79720c6036d1fc257d7217832ae)
  - [61d446e](https://github.com/spring-projects/spring-batch/commit/61d446e71f63c6b1d15826fb5e68aef7403b8702)

## 内容

**Bug description**
It seems, the write skip count is not incremented / updated if items are removed from chunks during write (in case an item cannot be successfully written)

**Environment**
Spring Batch 5.0.3 / Spring Boot 3.1.5 / Java 17

**Steps to reproduce**
```
public class MemberWriter implements ItemStreamWriter<String> {

    @Override
    public void write(Chunk<? extends String> memberChunk) {
        Chunk<? extends String>.ChunkIterator iterator = memberChunk.iterator();
        ...
        iterator.remove(new RuntimeException());
    }
```


**Expected behavior**
According to documentation of class Chunk, the writeSkipCount in the corresponding StepExecution object should be incremented for every item removed from ChunkIterator:
`Encapsulation of a list of items to be processed and possibly a list of failed items to be skipped. To mark an item as skipped clients should iterate over the chunk using the iterator() method, and if there is a failure call Chunk.ChunkIterator.remove() on the iterator. The skipped items are then available through the chunk.`

**Workaround**
It's possible to circumvent the issue by creating a combined SkipListener / StepExecutionListener:

```
public class SkipTestListener implements SkipListener<String, String>, StepExecutionListener {
    private StepExecution stepExecution;

    @Override
    public void beforeStep(StepExecution stepExecution) {
        this.stepExecution = stepExecution;
    }

    @Override
    public void onSkipInWrite(String item, Throwable t) {
        stepExecution.setWriteSkipCount(stepExecution.getWriteSkipCount() + 1);
        log.warn("Skipped item: {}", item);
    }
}
```
and register it accordingly in the step:
```
        SkipTestListener testListener = new SkipTestListener();

        new StepBuilder("process-step", jobRepository)
                .<String, String>chunk(chunkSize, transactionManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .faultTolerant()
                .listener((StepExecutionListener) testListener)
                .listener((SkipListener<? super String, ? super String>) testListener)
                .build();
```

## コメント

### コメント 1 by Hydrawisk793

**作成日**: 2024-10-12

I think that a manual adjustment of write count should also be added in `onSkipInWrite` method of @thilotanner's workaround like this:

```Java
@Override
public void onSkipInWrite(String item, Throwable t) {
    stepExecution.setWriteCount(stepExecution.getWriteCount() - 1);
    stepExecution.setWriteSkipCount(stepExecution.getWriteSkipCount() + 1);
    log.warn("Skipped item: {}", item);
}
```

### コメント 2 by florianhof

**作成日**: 2025-05-06

In my experience (Spring Batch 3.4.3), the _write count_ correctly don't report skipped item. Only the _write skip count_ is not correct.

I'm only a simple Spring Batch user, not a developer there. After a quick look, it seams `SimpleChunkProcessor.write` and `FaultTolerantChunkProcessor.write` should not only do `contribution.incrementWriteCount` but also `incrementWriteSkipCount`. 

### コメント 3 by florianhof

**作成日**: 2025-05-28

Proposition of correction in pull request https://github.com/spring-projects/spring-batch/pull/4852

