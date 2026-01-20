*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# マルチスレッドChunkOrientedStepで@StepScope ItemProcessorを使用するとScopeNotActiveExceptionが発生する

**Issue番号**: #5183

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5183

**関連リンク**:
- コミット:
  - [2382908](https://github.com/spring-projects/spring-batch/commit/2382908f404a4de714b0be9aa0023f25716e63bd)
  - [5642911](https://github.com/spring-projects/spring-batch/commit/564291127752f0c107508f853131fc4d8acfd4bd)

## 内容

Spring Batchチームの皆さん、こんにちは。

バージョン6.0で導入された新しい`ChunkOrientedStep`に関する問題を報告します。ステップがマルチスレッドとして構成されている場合、`@StepScope`で定義された`ItemProcessor`がワーカースレッド内で正しく解決されないようです。

## バグの説明
`ChunkOrientedStep`の実装において、特に`processChunkConcurrently`を使用する場合、`StepContext`が`TaskExecutor`によって管理されるワーカースレッドに伝播されないようです。

その結果、ワーカースレッドが`ItemProcessor`（`@StepScope`プロキシ）を呼び出そうとすると、そのスレッドの`StepSynchronizationManager`にアクティブなコンテキストがないため`ScopeNotActiveException`がスローされます。

## 環境
Spring Batchバージョン: v6
Step実装: ChunkOrientedStep
構成: TaskExecutor（例: SimpleAsyncTaskExecutor）+ @StepScope ItemProcessor

## 再現可能な構成
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
            .taskExecutor(new SimpleAsyncTaskExecutor()) // マルチスレッド有効
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

## 実際の結果（スタックトレース）
ワーカースレッドがスコープ付きの`ItemProcessor`にアクセスしようとするとエラーが発生します:
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

## 期待される動作
これが新実装における意図的なアーキテクチャ変更なのか見落としなのかは不明です。ただし、バグであれば、`@StepScope` `ItemProcessor`は以前のバージョンと同様にワーカースレッド内で正しく機能するべきです。


## ChunkOrientedStep.processChunkConcurrentlyでの修正案:
```java
// processChunkConcurrentlyメソッド内
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    try {
        // 現在のワーカースレッドのStepSynchronizationManagerにステップ実行を登録
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // メモリリーク防止のため処理後にコンテキストをクリア
        StepSynchronizationManager.close();
    }
});
```

お時間をいただきありがとうございます。このプロジェクトをメンテナンスいただき感謝しています！さらに情報が必要な場合や動作する再現リポジトリが必要な場合はお知らせください！

## コメント

### コメント 1 by LeeHyungGeol

**作成日**: 2026-01-07

@fmbenhassine さん、こんにちは。

この問題に取り組んでみても大丈夫でしょうか？

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@KILL9-NO-MERCY この問題を報告いただきありがとうございます！

> これが新実装における意図的なアーキテクチャ変更なのか見落としなのかは不明です。

これは新実装における見落としです。実際、`org.springframework.batch.core.step.item.ChunkOrientedStepIntegrationTests#testConcurrentChunkOrientedStepSuccess`は[このItemProcessor](https://github.com/spring-projects/spring-batch/blob/a6a53c46fca3aa920f4f07ac7ddbf39493081f66/spring-batch-core/src/test/java/org/springframework/batch/core/step/item/TestConfiguration.java#L56)がステップスコープの場合に失敗します。提案された変更で問題ありません（それにより、ステップスコープのItemProcessorでテストが通過します）。ご提案ありがとうございます。

@LeeHyungGeol もちろんです！お手伝いいただけるとのこと、ありがとうございます 🙏 ここで提案された変更と、先ほど言及したItemProcessorをステップスコープにするPRを作成していただけると助かります。次回の6.0.2で修正を計画します。

### コメント 3 by LeeHyungGeol

**作成日**: 2026-01-14

@fmbenhassine 確認ありがとうございます！

提案された修正でPRを作成し、ステップスコープのItemProcessorを使用するよう統合テストを更新します。

このIssueを私にアサインしていただけますか？

### コメント 4 by LeeHyungGeol

**作成日**: 2026-01-18

@fmbenhassine 
この問題に対応するためにPR https://github.com/spring-projects/spring-batch/pull/5218 を作成しました！
お時間のある時にご確認ください 🙇 ありがとうございます！
