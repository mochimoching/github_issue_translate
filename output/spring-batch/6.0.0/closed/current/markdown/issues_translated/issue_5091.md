*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ChunkOrientedStep: ItemWriterでリトライが枯渇すると、スキップ可否に関係なく常にチャンクスキャンがトリガーされる

**Issue番号**: #5091

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5091

**関連リンク**:
- Commits:
  - [cb55ccc](https://github.com/spring-projects/spring-batch/commit/cb55ccc44b30790385ed49f8ee1ed1b1f4978288)

## 内容

こんにちは、Spring Batchチームの皆さん、
まず、プロジェクトの維持と改善に継続的に取り組んでいただきありがとうございます。
Spring Batch 6の`ChunkOrientedStep`のフォールトトレラントな書き込みフローに関する問題を報告したいと思います。

**バグの説明**

Spring Batch 6では、`ItemWriter`で例外が発生し、リトライポリシーが枯渇した場合(`RetryException`)、例外がスキップ可能かどうかに関係なく、`ChunkOrientedStep`は常にチャンクスキャンを実行します。

問題は、スキャンに入る前に`SkipPolicy`の事前評価が行われないことです。つまり:

- 例外がスキップ不可能な場合でも、`scan()`が呼び出されます
- チャンク内の正常な(失敗していない)アイテムが再度書き込まれ(スキャンによって)、意図しない重複書き込みが発生します
- 最終的には、スキャン内で`NonSkippableWriteException`がスローされますが、それは意図しない書き込みが既に試行された後です

Spring Batch 5(`FaultTolerantChunkProcessor`)では、フレームワークがチャンクをスキャンする前に`SkipPolicy`チェックを実行していたため、スキップ不可能な例外に対する不必要なスキャンを防いでいました。

```java
RecoveryCallback<Object> recoveryCallback = context -> {
    /*
     * If the last exception was not skippable we don't need to do any
     * scanning. We can just bomb out with a retry exhausted.
     */
    if (!shouldSkip(itemWriteSkipPolicy, context.getLastThrowable(), -1)) {
        throw new ExhaustedRetryException(
                "Retry exhausted after last attempt in recovery path, but exception is not skippable.",
                context.getLastThrowable());
    }

    inputs.setBusy(true);
    data.scanning(true);
    scan(contribution, inputs, outputs, chunkMonitor, true);
    return null;
};
```

これにより、不正な動作が発生し、Spring Batch 5からの機能的なリグレッションとなっています。

**環境**

- Spring Batchバージョン: 6.0.0-RC2

**最小限の再現可能な例**

```java
@Configuration
@Slf4j
public class IssueReproductionJobConfiguration {

    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        return new StepBuilder(jobRepository)
                .<TestItem, TestItem>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .build();
    }

    @Bean
    public ItemReader<TestItem> issueReproductionReader() {
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
                if (item.id == 2) {
                    log.error(">>>> EXCEPTION on Item-2!");
                    throw new RuntimeException("Simulated write error on Item-2");
                }
            }
        };
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    static class SkippableItemReader implements ItemReader<TestItem> {
        private int index = 0;
        private final List<TestItem> items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (index >= items.size()) return null;
            return items.get(index++);
        }
    }
}
```

この例は問題を明確に示しています: リトライが枯渇した後、フレームワークは例外がスキップ不可能であるにもかかわらずチャンクスキャンに入り、重複書き込みと最終的な`NonSkippableWriteException`を引き起こします。

**期待される動作**

1. Writerで例外が発生
2. リトライ試行が枯渇
3. 例外に対して`SkipPolicy`を評価
   - スキップ可能な場合 → スキャンに進む
   - スキップ不可能な場合 → スキャンせずに即座に失敗
4. 重複書き込みや意図しない追加書き込み試行を回避

**実際の動作**

```bash
>>>> Read: Item-1
>>>> Read: Item-2
>>>> Read: Item-3
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-2
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> EXCEPTION on Item-2!
ChunkOrientedStep: Retry exhausted while attempting to write items, scanning the chunk

org.springframework.core.retry.RetryException: Retry policy for operation 'Retryable write operation' exhausted; aborting execution

...

>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> EXCEPTION on Item-2!
ChunkOrientedStep: Failed to write item: IssueReproductionJobConfiguration.TestItem(id=2, name=Item-2, description=Second item - will throw exception)

...

java.lang.RuntimeException: Simulated write error on Item-2
...

ChunkOrientedStep   : Rolling back chunk transaction

org.springframework.batch.core.step.skip.NonSkippableWriteException: Skip policy rejected skipping item

...

AbstractStep         : Encountered an error executing step issueReproductionStep in job issueReproductionJob

...
```

**提案される修正**

不必要なチャンクスキャンを防ぐため、`writeChunk()`は`RetryException`がスローされたときに、Spring Batch 5の`FaultTolerantChunkProcessor`の従来の動作と同様に、スキャン前の`SkipPolicy`チェックを実行すべきです。

具体的には、`writeChunk()`の`catch`ブロック内で、`scan()`をトリガーする前に`SkipPolicy`検証を追加できます:

```java
catch (Exception exception) {
    ...

    if (this.faultTolerant && exception instanceof RetryException retryException) {

        // 💡 提案されるスキャン前のSkipPolicyチェック
        if (!this.skipPolicy.shouldSkip(exception, -1)) {
            // 例外がスキップ不可能な場合、スキャンをスキップして即座に失敗
            throw exception;
        }

        logger.info("Retry exhausted while attempting to write items, scanning the chunk", retryException);

        ChunkScanEvent chunkScanEvent = new ChunkScanEvent(
            contribution.getStepExecution().getStepName(),
            contribution.getStepExecution().getId()
        );

        chunkScanEvent.begin();
        scan(chunk, contribution);
        chunkScanEvent.skipCount = contribution.getSkipCount();
        chunkScanEvent.commit();

        logger.info("Chunk scan completed");
    }
    else {
        throw exception;
    }
}
```

この問題をレビューしていただきありがとうございます!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

> まず、プロジェクトの維持と改善に継続的に取り組んでいただきありがとうございます。

こちらこそ、Spring Batch 6をテストし、貴重なフィードバックを継続的に提供していただきありがとうございます! 素晴らしいバグレポートで、本当に感謝しています 🙏

これは有効な問題です。次回のGAで修正を計画します。


