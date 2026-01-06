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

