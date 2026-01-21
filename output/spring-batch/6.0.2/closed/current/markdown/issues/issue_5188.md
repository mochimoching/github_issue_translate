# StepContribution counters are not thread-safe during parallel chunk processing

**Issue番号**: #5188

**状態**: closed | **作成者**: KMGeon | **作成日**: 2025-12-29

**ラベル**: type: bug, in: core, related-to: multi-threading

**URL**: https://github.com/spring-projects/spring-batch/issues/5188

**関連リンク**:
- Commits:
  - [6bd771a](https://github.com/spring-projects/spring-batch/commit/6bd771ab6c87fdec1ce98f773865a07394624cfc)
  - [0868c02](https://github.com/spring-projects/spring-batch/commit/0868c02574ee7920c60b3dc20da5aa75615bfeb3)
  - [b9587c7](https://github.com/spring-projects/spring-batch/commit/b9587c72f126bdaedb013c738b30accd9f0262bc)
  - [cc06132](https://github.com/spring-projects/spring-batch/commit/cc06132c31f760156de69e16bf93828f74a48c21)

## 内容

# Bug Description

When `ChunkOrientedStep` runs in concurrent mode (with `TaskExecutor` configured), `StepContribution.incrementFilterCount()` and `StepContribution.incrementProcessSkipCount()` suffer from race conditions, causing counts to be under-counted. This is because multiple worker threads concurrently call these methods on the same `StepContribution` instance, and both `filterCount` and `processSkipCount` fields use non-thread-safe `long` types with `+=` or `++` operations.

## Environment

- Spring Batch version: 6.0.1
- Java version: 22
- OS: macOS (also reproducible on Linux/Windows)

## Steps to Reproduce

1. Configure a `ChunkOrientedStep` with a `TaskExecutor` to enable concurrent mode
2. Use an `ItemProcessor` that filters all items (returns null)
3. Process a large number of items
4. Check `StepExecution.getFilterCount()` and `StepExecution.getProcessSkipCount()` after execution

## Expected Behavior

`filterCount` and `processSkipCount` should accurately reflect the number of filtered/skipped items.

## Root Cause Analysis

The issue is in `StepContribution.java`:

```java
// Current implementation - NOT thread-safe
private long filterCount = 0;
private long processSkipCount = 0;

public void incrementFilterCount(long count) {
    filterCount += count; // Race condition!
}

public void incrementProcessSkipCount() {
    processSkipCount++; // Race condition!
}
```

In `ChunkOrientedStep.processChunkConcurrently()`, multiple tasks are submitted to the `TaskExecutor`, all sharing the same contribution object:

```java
Future itemProcessingFuture = this.taskExecutor.submit(
    () -> processItem(item, contribution) // Same contribution shared
);
```

Each worker thread calls `contribution.incrementFilterCount()` or `contribution.incrementProcessSkipCount()` when processing items, causing the race condition.

### The Problem with `long +=` and `++` operations

These operations are **not atomic** and consist of multiple steps:

1. Read current value
2. Increment by count
3. Write back to memory

Multiple threads performing these steps simultaneously can cause lost updates:

```
Thread 1: Read (100) → Increment → Write (101)
Thread 2: Read (100) → Increment → Write (101)  ← Lost update!
Expected: 102, Actual: 101
```

## Proposed Solution

Change `filterCount` and `processSkipCount` to `AtomicLong`:

```java
private final AtomicLong filterCount = new AtomicLong(0);
private final AtomicLong processSkipCount = new AtomicLong(0);

public void incrementFilterCount(long count) {
    filterCount.addAndGet(count);
}

public void incrementProcessSkipCount() {
    processSkipCount.incrementAndGet();
}

public long getFilterCount() {
    return filterCount.get();
}

public long getProcessSkipCount() {
    return processSkipCount.get();
}
```

## Alternative Approaches Considered

### Approach 1: Partial AtomicLong Application (Current Implementation)

This approach changes only filterCount and processSkipCount to AtomicLong in the StepContribution class, which maintains lock-free performance and API compatibility with minimal code changes, but having only some fields as AtomicLong while others remain long may reduce code consistency and cause confusion for other developers.


### Approach 2: Aggregate Results in Main Thread

Modify `processChunkConcurrently()` to collect processing results and update counts in the main thread only.

```java
record ProcessingResult<O>(@Nullable O item, boolean filtered, boolean skipped) {}

private void processChunkConcurrently(...) {
    List<Future<ProcessingResult<O>>> tasks = new LinkedList<>();

    for (...) {
        Future<ProcessingResult<O>> future = this.taskExecutor.submit(
            () -> processItemWithResult(item)  // Don't pass contribution
        );
        tasks.add(future);
    }

    // Aggregate results in main thread - no race condition
    for (Future<ProcessingResult<O>> future : tasks) {
        ProcessingResult<O> result = future.get();
        if (result.filtered()) ...
        if (result.skipped())...
        if (result.item() != null) ...
    }
}
```

I believe **Approach 1 (AtomicLong)** is the simplest and most practical solution, but I'm open to feedback. If you prefer **Approach 2** or have other suggestions, please let me know and I'll revise accordingly.

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-13

Thank you for opening this issue. A step execution can be shared between worker threads, but a step contribution should not. In fact, that is the idea behind these APIs, each thread should have its own contribution to the overall step execution (ie each one will come up with its own read count, write count, etc and the manager step will aggregate those counters).

Can you please share your example? I can follow the steps you mentioned, but since you did not share all the code, I cannot be sure to be in the same configuration as you.

Thank you upfront!

### コメント 2 by KMGeon

**作成日**: 2026-01-14


Thank you for your interest in this issue!

Here is the sample project: [sample_code](https://github.com/KMGeon/spring-batch-issue-5188)


### コメント 3 by KMGeon

**作成日**: 2026-01-16

## Correction

I apologize for my mistake in the previous comment. I initially shared a GitHub repository link, but for MCVE (Minimal Complete Verifiable Example) submissions in Spring Batch issues, I should provide a zip file instead.

I have now attached the sample project as a zip file: [spring-batch-mcve.zip](https://github.com/user-attachments/files/24661198/spring-batch-mcve.zip)


### コメント 4 by KMGeon

**作成日**: 2026-01-20

> Thank you for opening this issue. A step execution can be shared between worker threads, but a step contribution should not. In fact, that is the idea behind these APIs, each thread should have its own contribution to the overall step execution (ie each one will come up with its own read count, write count, etc and the manager step will aggregate those counters).
> 
> Can you please share your example? I can follow the steps you mentioned, but since you did not share all the code, I cannot be sure to be in the same configuration as you.
> 
> Thank you upfront!

@fmbenhassine 

  Thank you for your feedback.                                                                                                    
                                                                                                                                  
  When I initially created this issue, I proposed two possible solutions:                                                         
  - Approach 1: Change filterCount and processSkipCount to AtomicLong                                                             
  - Approach 2: Aggregate processing results from each worker thread in the main thread                                           
                                                                                                                                  
  At that time, I thought Approach 1 was simpler with fewer code changes, so I submitted PR #5189 using the AtomicLong approach.  
                                                                                                                                  
  However, your feedback helped me understand the design philosophy of Spring Batch:                                              
                                                                                                                                  
  "A step contribution should not be shared between worker threads. Each thread should have its own contribution to the overall   
  step execution, and the manager step will aggregate those counters."                                                            
                                                                                                                                  
  Based on this design intent, I have submitted PR #5224 using Approach 2 instead of Approach 1.                                  
                                                                                                                                  
  Changes:                                                                                                                        
  - Create a separate StepContribution instance for each worker thread                                                            
  - Aggregate filterCount and processSkipCount in the main thread after all futures complete                                      
  - No modifications to the StepContribution class itself                                                                         
                                                                                                                                  
  Please review when you have a chance. Thank you!      

### コメント 5 by fmbenhassine

**作成日**: 2026-01-20

Thank you for your feedback and PRs!

My previous [comment](https://github.com/spring-projects/spring-batch/issues/5188#issuecomment-3742868170) was **not** accurate. In fact, that approach is only true for local chunking ([here](https://github.com/spring-projects/spring-batch/blob/82121a59872e018b1c98cbe68345fde716cd2e60/spring-batch-integration/src/main/java/org/springframework/batch/integration/chunk/ChunkTaskExecutorItemWriter.java#L90-L96) is where the aggregation of step contributions is done, we have an example [here](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/chunking/local)). Apologies for the confusion that led you to contribute Approach 2. But approach 1 is actually the way to go.

I will merge the PR that uses approach 1 and close the other one.


