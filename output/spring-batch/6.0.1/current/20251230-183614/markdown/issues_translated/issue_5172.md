# ローカルチャンキング: ワーカースレッドの書き込み失敗時にBatchStatusがCOMPLETEDのまま残る

**Issue番号**: #5172

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-17

**ラベル**: type: bug, in: integration

**URL**: https://github.com/spring-projects/spring-batch/issues/5172

**関連リンク**:
- Commits:
  - [82121a5](https://github.com/spring-projects/spring-batch/commit/82121a59872e018b1c98cbe68345fde716cd2e60)

## 内容

Spring Batchチームの皆様、こんにちは。

Spring Batch 6.0と新しいローカルチャンキング機能への素晴らしい取り組みに感謝します! `ChunkTaskExecutorItemWriter`をテスト中に、書き込み操作中にワーカースレッドが失敗した際のステータス管理に関する潜在的な課題に気づきました。

**バグの説明**
ローカルチャンキングに`ChunkTaskExecutorItemWriter`を使用している場合、書き込み操作中にワーカースレッドが失敗すると、ステップの`BatchStatus`が誤って`COMPLETED`のまま残りますが、`ExitStatus`は正しく`FAILED`に設定されます。これにより、ステップ実行メタデータに不整合が生じます。


**根本原因**
`AbstractStep.execute()`(322行目付近)で、`afterStep()`を呼び出した後、`ExitStatus`のみが明示的に設定されます:
```java
exitStatus = exitStatus.and(getCompositeListener().afterStep(stepExecution));
stepExecution.setExitStatus(exitStatus);  // ExitStatusのみが更新される
```

`BatchStatus`は`afterStep()`の結果に基づいて更新されません。tryブロックで以前に設定された`COMPLETED`のまま残り、`afterStep()`が`FAILED`を返した場合でもそのままです。

**現在の実装 (ChunkTaskExecutorItemWriter.java)**
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        // 欠落: stepExecution.setStatus(BatchStatus.FAILED);
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

**期待される動作**

`afterStep()`が`ExitStatus.FAILED`を返す場合、`ExitStatus`と`BatchStatus`の一貫性を維持するために、`BatchStatus`も`FAILED`に設定されるべきです。

**提案される修正**
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        stepExecution.setStatus(BatchStatus.FAILED);  // この行を追加
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

**再現手順**
1. `ChunkTaskExecutorItemWriter`を使用するステップを設定
2. 書き込み操作中に例外をスローする`ChunkProcessor`を作成
3. ジョブを実行
4. データベースの`BATCH_STEP_EXECUTION`テーブルを確認


**観察された結果:**
- `EXIT_CODE`: FAILED ✓
- `STATUS`: COMPLETED ✗ (期待: FAILED)


**最小限の再現可能な例**
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


実行後、メタデータをクエリ:
```sql
SELECT STEP_NAME, STATUS, EXIT_CODE, EXIT_MESSAGE
FROM BATCH_STEP_EXECUTION;

-- 結果: 
-- STEP_NAME            | STATUS    | EXIT_CODE | EXIT_MESSAGE
-- issueReproductionStep| COMPLETED | FAILED    | java.lang.RuntimeException: Simulated write failure ...
--                        ^^^^^^^^^   ^^^^^^
--                        不整合!
```


**提案される解決策**

ワーカースレッドが失敗した際に`BatchStatus.FAILED`を明示的に設定するように`ChunkTaskExecutorItemWriter.afterStep()`を更新します:
```java
@Override
public ExitStatus afterStep(StepExecution stepExecution) {
    try {
        for (StepContribution contribution : getStepContributions()) {
            stepExecution.apply(contribution);
        }
    }
    catch (ExecutionException | InterruptedException e) {
        stepExecution.setStatus(BatchStatus.FAILED);  // 一貫性を維持するためにBatchStatusを設定
        return ExitStatus.FAILED.addExitDescription(e);
    }
    return ExitStatus.COMPLETED.addExitDescription("Waited for " + this.responses.size() + " results.");
}
```

これにより、ワーカースレッドの実行が失敗した際に`BatchStatus`と`ExitStatus`の両方が一貫して`FAILED`に設定され、ジョブの再起動ロジックと監視システムに影響を与える可能性のあるメタデータの不整合が防止されます。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-17

この課題を提起し、例を提供していただきありがとうございます! 本当に一流のバグ報告です 👌

これは確かに有効な課題です。提案されたようにcatchブロックでステップ実行を失敗としてマークすることに加えて、ワーカーの1つが失敗したかどうかも確認する必要があります(失敗したコントリビューションは成功したものの前に適用される可能性があり、したがってワーカーの1つが失敗した場合でもステップは完了としてマークされます)。

