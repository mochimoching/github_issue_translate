# ChunkOrientedStep updates ExecutionContext even when a chunk fails, leading to data loss on restart

**Issue番号**: #5182

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5182

## 内容

Hello Spring Batch Team!

## Bug description: 
In Spring Batch 6.x, the newly introduced ChunkOrientedStep calls itemStream.update() and jobRepository.updateExecutionContext() within a finally block in both processChunkSequentially and processChunkConcurrently. Unlike the traditional TaskletStep implementation.

This causes the ItemStream state (e.g., read count, current index) to be persisted even when a chunk transaction fails and rolls back. Consequently, upon restart, the step resumes from the "failed" offset, leading to silent data loss of the records within the failed chunk.


## Code Comparison (The Root Cause)

#### Spring Batch 5.x (TaskletStep.java)
In version 5, the state is updated only after the chunk is successfully processed and committed.

```java

// TaskletStep.java (Line 452)
// This logic is inside the successful processing flow
stream.update(stepExecution.getExecutionContext());
getJobRepository().updateExecutionContext(stepExecution);
stepExecution.incrementCommitCount();
```


#### Spring Batch 6.x (ChunkOrientedStep.java)
In version 6, the update logic was moved to a finally block, forcing the update even during a rollback.
```java
// ChunkOrientedStep.java
private void processChunkSequentially(...) {
    try {
        // chunk read/process/write logic
    } catch (Exception e) {
        // exception handling
        throw e;
    } finally {
        // BUG: Always executed even if the transaction is rolled back!
        this.compositeItemStream.update(stepExecution.getExecutionContext());
        getJobRepository().updateExecutionContext(stepExecution);
    }
}
```

## Impact
Transaction Inconsistency: The business data is rolled back, but the Batch Metadata (index/offset) is committed/updated.

Data Loss: On restart, the ItemReader resumes from the position after the failed chunk, meaning the records in the failed chunk are never re-processed.

## Environment
Spring Batch version: 6.0.1
Components: ChunkOrientedStep 

## Expected behavior
ExecutionContext and ItemStream state should only be updated if the chunk transaction is successful. If an exception occurs, the finally block should not persist the advanced state to the JobRepository.


## Suggested Fix
The state update logic should be moved from the finally block of processChunkXXX methods to the doExecute method, specifically after the transaction has successfully completed.

Proposed change in ChunkOrientedStep.java:
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // process next chunk in its own transaction
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
          // process next chunk
       });
       getJobRepository().update(stepExecution);
       
       // FIX: Update ItemStream and ExecutionContext ONLY after successful transaction commit
       this.compositeItemStream.update(stepExecution.getExecutionContext());
       getJobRepository().updateExecutionContext(stepExecution);
    }
}
```
Note: The corresponding update calls inside processChunkSequentially and processChunkConcurrently's finally blocks must be removed to prevent duplicate or premature updates.


Thanks for your time and for maintaining this great project! If you need more details or sample please tell me!

## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2026-01-06

Hi Spring Batch team!
I wanted to add some follow-up context related to this issue.

I recently opened another issue (#5199) regarding the transaction boundary of JobRepository.update(stepExecution) in ChunkOrientedStep#doExecute.

If the fix proposed in #5199 is applied (moving JobRepository.update(stepExecution) inside the chunk transaction), then the proposed fix in this issue (#5182) should be slightly adjusted as well.

the past proposed fix suggests moving those updates to doExecute, after the transaction completes. but If `JobRepository.update(stepExecution)` itself is moved inside the transaction (as proposed in #5199), then to preserve full consistency, the following operations should also be aligned with the same transaction boundary
- JobRepository.update(stepExecution)
- ItemStream.update(stepExecution.getExecutionContext())
- JobRepository.updateExecutionContext(stepExecution)

## Suggested alignment
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // process next chunk in its own transaction
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
           processNextChunk(transactionStatus, contribution, stepExecution);
           // FIX: Update ItemStream and ExecutionContext
           this.compositeItemStream.update(stepExecution.getExecutionContext());
           getJobRepository().updateExecutionContext(stepExecution);
           // FIX #5199
           getJobRepository().update(stepExecution);
       });
    }
}
```

Just wanted to point this out so both issues can be addressed consistently. Happy to help with a unified fix or a test if needed. Thanks again!

### コメント 2 by fmbenhassine

**作成日**: 2026-01-12

Thank you for your continuous feedback on v6.

> Happy to help with a unified fix or a test if needed.

Yes please. That would be helpful! Many thanks upfront.

EDIT: It looks like we have a PR for this issue: #5195. Can you please check if it suggests the same/similar fix that you have in mind?

### コメント 3 by KILL9-NO-MERCY

**作成日**: 2026-01-14

Thanks for the information! I'll check PR #5195 and leave a comment there.

### コメント 4 by fmbenhassine

**作成日**: 2026-01-15

Resolved with #5195

