# ChunkOrientedStep#doExecute updates the StepExecution outside of the chunk transaction boundary.

**Issue番号**: #5199

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2026-01-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5199

## 内容

Hi Spring Batch team 👋
First of all, thank you for your continued work on Spring Batch.

## Description
This issue is related to a past change in PR #5165: https://github.com/spring-projects/spring-batch/pull/5165

This was my mistake, and I wanted to report it properly after noticing an unintended side effect in Spring Batch 6.0.1.

In Spring Batch 6, ChunkOrientedStep#doExecute updates the StepExecution outside of the chunk transaction boundary.
Because of this, if JobRepository.update(stepExecution) fails, the chunk transaction has already been completed, which can leave batch metadata in an inconsistent state.

In other words, chunk processing and step execution persistence are no longer atomic in ChunkOrientedStep.

## Environment
spring batch 6.0.1
ChunkOrientedStep#doExecute()

## expected behavior
The update of StepExecution via JobRepository.update(stepExecution) should occur within the same transaction boundary as chunk processing.

If the metadata update fails, the chunk transaction should be rolled back accordingly, preserving consistency between:
processed data and batch metadata.

This is the behavior historically provided by TaskletStep, where JobRepository.update() is invoked before transaction commit, not after.

## Additional context
The current implementation of ChunkOrientedStep#doExecute looks like this (simplified):
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
});

// transaction already completed here
getJobRepository().update(stepExecution);

```

## Proposed fix
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
    getJobRepository().update(stepExecution);
});
```

so that chunk processing and metadata updates share the same transactional boundary.

please let me know if you’d like me to provide a reproducer or a failing test for this issue. 🙏


