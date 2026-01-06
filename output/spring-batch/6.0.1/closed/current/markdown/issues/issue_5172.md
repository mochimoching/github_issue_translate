# Local Chunking: BatchStatus remains COMPLETED when worker thread write fails

**Issue番号**: #5172

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-17

**ラベル**: type: bug, in: integration

**URL**: https://github.com/spring-projects/spring-batch/issues/5172

**関連リンク**:
- Commits:
  - [82121a5](https://github.com/spring-projects/spring-batch/commit/82121a59872e018b1c98cbe68345fde716cd2e60)

## 内容

Hi Spring Batch team,

Thank you for your great work on Spring Batch 6.0 and the new local chunking feature! While testing `ChunkTaskExecutorItemWriter`, I noticed a potential issue with status management when worker threads fail during write operations.

**Bug description**
When using `ChunkTaskExecutorItemWriter` for local chunking, if a worker thread fails during the write operation, the step's `BatchStatus` incorrectly remains `COMPLETED` while the `ExitStatus` is correctly set to `FAILED`. This creates an inconsistency in the step execution metadata.


**Root Cause**
In `AbstractStep.execute()` (around line 322), after calling `afterStep()`, only the `ExitStatus` is explicitly set:
```java
exitStatus = exitStatus.and(getCompositeListener().afterStep(stepExecution));
stepExecution.setExitStatus(exitStatus);  // Only ExitStatus is updated
```

The `BatchStatus` is not updated based on the `afterStep()` result. It remains as `COMPLETED` (set earlier in the try block) even when `afterStep()` returns `FAILED`.

**Current Implementation (ChunkTaskExecutorItemWriter.java)**
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        // Missing: stepExecution.setStatus(BatchStatus.FAILED);
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

**Expected behavior**

When `afterStep()` returns `ExitStatus.FAILED`, the `BatchStatus` should also be set to `FAILED` to maintain consistency between `ExitStatus` and `BatchStatus`.

**Proposed Fix**
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        stepExecution.setStatus(BatchStatus.FAILED);  // Add this line
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

**Steps to reproduce**
1. Configure a step using `ChunkTaskExecutorItemWriter`
2. Create a `ChunkProcessor` that throws an exception during write operation
3. Execute the job
4. Check the `BATCH_STEP_EXECUTION` table in the database


**Observed Result:**
- `EXIT_CODE`: FAILED ✓
- `STATUS`: COMPLETED ✗ (Expected: FAILED)


**Minimal Complete Reproducible example**
```java
package com.example.batch;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.batch.core.ExitStatus;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.job.parameters.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.core.step.item.ChunkProcessor;
import org.springframework.batch.infrastructure.item.ItemReader;
import org.springframework.batch.infrastructure.item.ItemWriter;
import org.springframework.batch.infrastructure.item.support.ListItemReader;
import org.springframework.batch.integration.chunk.ChunkTaskExecutorItemWriter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.SimpleAsyncTaskExecutor;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.List;

@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager,
            ChunkTaskExecutorItemWriter issueReproductionWriter
    ) {
        return new StepBuilder(jobRepository)
                .chunk(3)
                .transactionManager(transactionManager)
                .reader(issueReproductionReader())
                .writer(issueReproductionWriter)
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new ListItemReader<>(List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        ));
    }

    @Bean
    public ChunkTaskExecutorItemWriter issueReproductionWriter(
            ChunkProcessor chunkProcessor
    ) {
        return new ChunkTaskExecutorItemWriter<>(chunkProcessor, new SimpleAsyncTaskExecutor());
    }

    @Bean
    public ChunkProcessor chunkProcessor(PlatformTransactionManager transactionManager) {
        TransactionTemplate txTemplate = new TransactionTemplate(transactionManager);
        ItemWriter writer = chunk -> {
            for (TestItem testItem : chunk.getItems()) {
                log.info("Writing: {}", testItem);

                if ("Item-2".equals(testItem.getName())) {
                    throw new RuntimeException("Simulated write failure");
                }
            }
        };

        return (chunk, contribution) -> txTemplate.executeWithoutResult(status -> {
            try {
                writer.write(chunk);
                contribution.setExitStatus(ExitStatus.COMPLETED);
            } catch (Exception e) {
                status.setRollbackOnly();
                contribution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
                throw e;
            }
        });
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }
}
```


After execution, query the metadata:
```sql
SELECT STEP_NAME, STATUS, EXIT_CODE, EXIT_MESSAGE
FROM BATCH_STEP_EXECUTION;

-- Result: 
-- STEP_NAME            | STATUS    | EXIT_CODE | EXIT_MESSAGE
-- issueReproductionStep| COMPLETED | FAILED    | java.lang.RuntimeException: Simulated write failure ...
--                        ^^^^^^^^^   ^^^^^^
--                        Inconsistent!
```


**Proposed Solution**

Update `ChunkTaskExecutorItemWriter.afterStep()` to explicitly set `BatchStatus.FAILED` when worker threads fail:
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        stepExecution.setStatus(BatchStatus.FAILED);  // Set BatchStatus to maintain consistency
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

This ensures that both `BatchStatus` and `ExitStatus` are consistently set to `FAILED` when worker thread execution fails, preventing metadata inconsistencies that can affect job restart logic and monitoring systems.

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-17

Thank you for raising this issue and for providing an example! Really top notch bug reporting here 👌

This is indeed a valid issue. In addition to marking the step execution as failed in the catch block as suggested , we also need to check if one of the workers has failed (as failed contributions could be applied before successful ones and therefore the step will be marked as completed even if one of the workers has failed).

