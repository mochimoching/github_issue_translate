# マルチスレッドChunkOrientedStepで@StepScopeのItemProcessorを使用するとScopeNotActiveExceptionが発生する

**課題番号**: #5183

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5183

## 内容

Spring Batchチームの皆様、こんにちは。

バージョン6.0で導入された新しい`ChunkOrientedStep`に関する問題を報告します。ステップがマルチスレッドとして設定されている場合、`@StepScope`で定義された`ItemProcessor`がワーカースレッド内で正しく解決されない問題が発生しているようです。

## バグの説明
`ChunkOrientedStep`の実装、特に`processChunkConcurrently`を使用する場合、`TaskExecutor`によって管理されるワーカースレッドに`StepContext`が伝播されないようです。

その結果、ワーカースレッドが（`@StepScope`プロキシである）`ItemProcessor`を呼び出そうとすると、その特定のスレッドの`StepSynchronizationManager`にアクティブなコンテキストがないため、`ScopeNotActiveException`がスローされます。

## 環境
Spring Batchバージョン: v6
ステップ実装: ChunkOrientedStep
設定: TaskExecutor（例：SimpleAsyncTaskExecutor）+ @StepScope ItemProcessor

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
ワーカースレッドがスコープ化された`ItemProcessor`にアクセスしようとするときにエラーが発生します：
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
これが意図的なアーキテクチャの変更なのか、新しい実装での見落としなのかは確信が持てません。しかし、もしこれがバグであれば、`@StepScope`の`ItemProcessor`は以前のバージョンと同様に、ワーカースレッド内で正しく機能すべきです。


## ChunkOrientedStep.processChunkConcurrentlyでの提案変更：
```java
// processChunkConcurrentlyメソッド内
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    try {
        // 現在のワーカースレッドのStepSynchronizationManagerにステップ実行を登録
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // メモリリークを防ぐため、処理後にコンテキストをクリア
        StepSynchronizationManager.close();
    }
});
```

お時間を割いていただき、またこのプロジェクトをメンテナンスしていただきありがとうございます！さらなる情報や動作する再現リポジトリが必要な場合はお知らせください！
