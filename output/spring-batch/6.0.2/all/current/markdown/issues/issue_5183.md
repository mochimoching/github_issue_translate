# ScopeNotActiveException with @StepScope ItemProcessor in Multi-threaded ChunkOrientedStep

**Issue番号**: #5183

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5183

## 内容

Hello Spring Batch Team,

I am reporting an issue regarding the new ChunkOrientedStep introduced in version 6.0. It appears that when a step is configured as multi-threaded, an ItemProcessor defined with @StepScope fails to resolve correctly within the worker threads.

## Bug Description
In the ChunkOrientedStep implementation, specifically when using processChunkConcurrently, the StepContext does not seem to be propagated to the worker threads managed by the TaskExecutor.

As a result, when the worker thread attempts to invoke the ItemProcessor (which is a @StepScope proxy), it throws a ScopeNotActiveException because the StepSynchronizationManager on that specific thread has no active context.

## Environment
Spring Batch version: v6
Step Implementation: ChunkOrientedStep
Configuration: TaskExecutor (e.g., SimpleAsyncTaskExecutor) + @StepScope ItemProcessor

## Reproducible Configuration
```java
@Bean
public Step issueReproductionStep(
        JobRepository jobRepository,
        ItemReader<TestItem> reader,
        ItemProcessor<TestItem, TestItem> itemProcessor, // @StepScope Bean
        ItemWriter<TestItem> writer
) {
    return new StepBuilder(jobRepository)
            .<TestItem, TestItem>chunk(1)
            .reader(reader)
            .processor(itemProcessor)
            .writer(writer)
            .taskExecutor(new SimpleAsyncTaskExecutor()) // Multi-threading enabled
            .build();
}

@Bean
@StepScope
public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
    return item -> {
        log.info("[Thread: {}] Processing item: {}", Thread.currentThread().getName(), item.getName());
        return item;
    };
}
```

## Actual Result (Stacktrace)
The error occurs when the worker thread tries to access the scoped ItemProcessor:
```bash
Caused by: org.springframework.beans.factory.support.ScopeNotActiveException: Error creating bean with name 'scopedTarget.issueReproductionProcessor': Scope 'step' is not active for the current thread
    at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:381)
    ...
    at jdk.proxy2/jdk.proxy2.$Proxy134.process(Unknown Source)
    at org.springframework.batch.core.step.item.ChunkOrientedStep.doProcess(ChunkOrientedStep.java:655)
    ...
Caused by: java.lang.IllegalStateException: No context holder available for step scope
    at org.springframework.batch.core.scope.StepScope.getContext(StepScope.java:167)
```

## Expected Behavior
I am not certain whether this is an intended architectural change or an oversight in the new implementation. However, if this is a bug, the @StepScope ItemProcessor should function correctly within worker threads, as it did in previous versions.


## Proposed change in ChunkOrientedStep.processChunkConcurrently:
```java
// Inside processChunkConcurrently method
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    try {
        // Register step execution to the current worker thread's StepSynchronizationManager
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // Clear the context after processing to prevent memory leaks
        StepSynchronizationManager.close();
    }
});
```

Thanks for your time and for maintaining this project! Please let me know if you need any further information or a working reproduction repository!

## コメント

### コメント 1 by LeeHyungGeol

**作成日**: 2026-01-07

Hello @fmbenhassine.

Would it be okay if i give it a try on this issue?

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@KILL9-NO-MERCY Thank you for reporting this issue!

> I am not certain whether this is an intended architectural change or an oversight in the new implementation.

This is an oversight in the new implementation. In fact `org.springframework.batch.core.step.item.ChunkOrientedStepIntegrationTests#testConcurrentChunkOrientedStepSuccess` fails when [this item processor](https://github.com/spring-projects/spring-batch/blob/a6a53c46fca3aa920f4f07ac7ddbf39493081f66/spring-batch-core/src/test/java/org/springframework/batch/core/step/item/TestConfiguration.java#L56) is step-scoped. The suggested change LGTM (with it, the test passes with a step-scoped item processor). Thank you for the suggestion.

@LeeHyungGeol Sure! Thank you for your offer to help 🙏 You are welcome to contribute a PR with the suggested change here and making the item processor that I mentioned earlier step-scoped. I will plan the fix for the upcoming 6.0.2.

### コメント 3 by LeeHyungGeol

**作成日**: 2026-01-14

 @fmbenhassine Thank you for the confirmation!

  I'll work on a PR with the suggested fix and update the integration test
  to use a step-scoped item processor.

  Could you please assign this issue to me?

