# ChunkOrientedStep updates ExecutionContext even when a chunk fails, leading to data loss on restart

**Issue番号**: #5182

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

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

