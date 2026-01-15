*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# マルチスレッドのChunkOrientedStepで@StepScopeのItemProcessorを使用するとScopeNotActiveExceptionが発生する

**課題番号**: [#5183](https://github.com/spring-projects/spring-batch/issues/5183)

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5183

## 内容

Spring Batchチームの皆さん、こんにちは。

バージョン6.0で導入された新しい`ChunkOrientedStep`に関する課題を報告します。ステップがマルチスレッドとして設定されている場合、`@StepScope`で定義された`ItemProcessor`がワーカースレッド内で正しく解決されないようです。

## バグの説明
`ChunkOrientedStep`の実装、特に`processChunkConcurrently`を使用する場合、`StepContext`が`TaskExecutor`で管理されるワーカースレッドに伝播されていないようです。

その結果、ワーカースレッドが`ItemProcessor`（`@StepScope`プロキシ）を呼び出そうとすると、その特定のスレッドの`StepSynchronizationManager`にアクティブなコンテキストがないため、`ScopeNotActiveException`がスローされます。

## 環境
Spring Batchバージョン: v6
ステップ実装: `ChunkOrientedStep`
設定: `TaskExecutor`（例: `SimpleAsyncTaskExecutor`）+ `@StepScope` `ItemProcessor`

## 再現可能な設定
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
            .taskExecutor(new SimpleAsyncTaskExecutor()) // マルチスレッドが有効
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
ワーカースレッドがスコープされた`ItemProcessor`にアクセスしようとするとエラーが発生します:
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
これが意図されたアーキテクチャの変更なのか、新しい実装での見落としなのか確信がありません。ただし、これがバグであれば、`@StepScope`の`ItemProcessor`は以前のバージョンと同様にワーカースレッド内で正しく機能すべきです。


## ChunkOrientedStep.processChunkConcurrentlyでの提案変更:
```java
// processChunkConcurrentlyメソッド内
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    try {
        // 現在のワーカースレッドのStepSynchronizationManagerにステップ実行を登録
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // メモリリークを防ぐために処理後にコンテキストをクリア
        StepSynchronizationManager.close();
    }
});
```

お時間をいただき、このプロジェクトをメンテナンスしていただきありがとうございます！さらに情報や動作する再現リポジトリが必要な場合はお知らせください！

## コメント

### コメント 1 by LeeHyungGeol

**作成日**: 2026-01-07

@fmbenhassine さん、こんにちは。

この課題に取り組んでもよろしいでしょうか？

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@KILL9-NO-MERCY この課題を報告いただきありがとうございます！

> これが意図されたアーキテクチャの変更なのか、新しい実装での見落としなのか確信がありません。

これは新しい実装での見落としです。実際、`org.springframework.batch.core.step.item.ChunkOrientedStepIntegrationTests#testConcurrentChunkOrientedStepSuccess`は、[このアイテムプロセッサ](https://github.com/spring-projects/spring-batch/blob/a6a53c46fca3aa920f4f07ac7ddbf39493081f66/spring-batch-core/src/test/java/org/springframework/batch/core/step/item/TestConfiguration.java#L56)がステップスコープされている場合に失敗します。提案された変更は良さそうです（これにより、ステップスコープのアイテムプロセッサでテストが成功します）。ご提案いただきありがとうございます。

@LeeHyungGeol もちろんです！ご協力いただきありがとうございます 🙏 ここで提案された変更と、先ほど言及したアイテムプロセッサをステップスコープにしたPRを提供いただければ幸いです。次期6.0.2で修正を予定します。

### コメント 3 by LeeHyungGeol

**作成日**: 2026-01-14

@fmbenhassine 確認いただきありがとうございます！

提案された修正でPRを作成し、統合テストを更新して
ステップスコープのアイテムプロセッサを使用するようにします。

この課題を私にアサインしていただけますか？
