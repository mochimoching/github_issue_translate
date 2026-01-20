*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# ChunkOrientedStepがチャンク失敗時もExecutionContextを更新するため、リスタート時にデータ損失が発生する

**Issue番号**: #5182

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5182

## 内容

Spring Batchチームの皆さん、こんにちは！

## バグの説明:
Spring Batch 6.xでは、新しく導入された`ChunkOrientedStep`が`processChunkSequentially`と`processChunkConcurrently`の両方でfinallyブロック内で`itemStream.update()`と`jobRepository.updateExecutionContext()`を呼び出します。これは従来の`TaskletStep`実装とは異なります。

このため、チャンクトランザクションが失敗してロールバックされても、`ItemStream`の状態（読み取りカウント、現在のインデックスなど）が永続化されます。結果として、リスタート時にステップが「失敗した」オフセットから再開し、失敗したチャンク内のレコードがサイレントにデータ損失となります。


## コード比較（根本原因）

#### Spring Batch 5.x (TaskletStep.java)
バージョン5では、チャンクが正常に処理されコミットされた後にのみ状態が更新されます。

```java

// TaskletStep.java (Line 452)
// このロジックは成功した処理フロー内にあります
stream.update(stepExecution.getExecutionContext());
getJobRepository().updateExecutionContext(stepExecution);
stepExecution.incrementCommitCount();
```


#### Spring Batch 6.x (ChunkOrientedStep.java)
バージョン6では、更新ロジックがfinallyブロックに移動し、ロールバック時でも更新が強制されます。
```java
// ChunkOrientedStep.java
private void processChunkSequentially(...) {
    try {
        // チャンクの読み取り/処理/書き込みロジック
    } catch (Exception e) {
        // 例外処理
        throw e;
    } finally {
        // バグ: トランザクションがロールバックされても常に実行される！
        this.compositeItemStream.update(stepExecution.getExecutionContext());
        getJobRepository().updateExecutionContext(stepExecution);
    }
}
```

## 影響
トランザクションの不整合: ビジネスデータはロールバックされますが、Batchメタデータ（インデックス/オフセット）はコミット/更新されます。

データ損失: リスタート時に`ItemReader`は失敗したチャンクの後の位置から再開するため、失敗したチャンク内のレコードは再処理されません。

## 環境
Spring Batchバージョン: 6.0.1
コンポーネント: ChunkOrientedStep 

## 期待される動作
`ExecutionContext`と`ItemStream`の状態は、チャンクトランザクションが成功した場合にのみ更新されるべきです。例外が発生した場合、finallyブロックは進んだ状態を`JobRepository`に永続化すべきではありません。


## 修正案
状態更新ロジックを`processChunkXXX`メソッドのfinallyブロックから`doExecute`メソッドに移動し、具体的にはトランザクションが正常に完了した後に配置すべきです。

ChunkOrientedStep.javaでの提案される変更:
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // 独自のトランザクションで次のチャンクを処理
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
          // 次のチャンクを処理
       });
       getJobRepository().update(stepExecution);
       
       // 修正: トランザクションのコミット成功後にのみItemStreamとExecutionContextを更新
       this.compositeItemStream.update(stepExecution.getExecutionContext());
       getJobRepository().updateExecutionContext(stepExecution);
    }
}
```
注意: `processChunkSequentially`と`processChunkConcurrently`のfinallyブロック内の対応する更新呼び出しは、重複または早期の更新を防ぐために削除する必要があります。


この素晴らしいプロジェクトをメンテナンスしていただきありがとうございます！詳細やサンプルが必要な場合はお知らせください！

## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2026-01-06

Spring Batchチームの皆さん、こんにちは！
この問題に関連するフォローアップの背景を追加したいと思います。

最近、`ChunkOrientedStep#doExecute`における`JobRepository.update(stepExecution)`のトランザクション境界に関する別の問題（[#5199](https://github.com/spring-projects/spring-batch/issues/5199)）を報告しました。

[#5199](https://github.com/spring-projects/spring-batch/issues/5199)で提案された修正（`JobRepository.update(stepExecution)`をチャンクトランザクション内に移動する）が適用される場合、この問題（[#5182](https://github.com/spring-projects/spring-batch/issues/5182)）で提案された修正も若干調整する必要があります。

以前の修正案では、トランザクション完了後に`doExecute`でこれらの更新を移動することを提案しました。しかし、`JobRepository.update(stepExecution)`自体がトランザクション内に移動される（[#5199](https://github.com/spring-projects/spring-batch/issues/5199)で提案されている通り）場合、完全な整合性を保つために、以下の操作も同じトランザクション境界に合わせる必要があります:
- `JobRepository.update(stepExecution)`
- `ItemStream.update(stepExecution.getExecutionContext())`
- `JobRepository.updateExecutionContext(stepExecution)`

## 提案される調整
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // 独自のトランザクションで次のチャンクを処理
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
           processNextChunk(transactionStatus, contribution, stepExecution);
           // 修正: ItemStreamとExecutionContextを更新
           this.compositeItemStream.update(stepExecution.getExecutionContext());
           getJobRepository().updateExecutionContext(stepExecution);
           // #5199の修正
           getJobRepository().update(stepExecution);
       });
    }
}
```

両方の問題が一貫して対処されるようにこれを指摘したかったです。統一された修正やテストが必要であれば喜んでお手伝いします。よろしくお願いします！

### コメント 2 by fmbenhassine

**作成日**: 2026-01-12

v6に対する継続的なフィードバックをありがとうございます。

> 統一された修正やテストが必要であれば喜んでお手伝いします。

ぜひお願いします。とても助かります！事前に感謝します。

編集: この問題について[#5195](https://github.com/spring-projects/spring-batch/issues/5195)というPRがあるようです。あなたが考えている修正と同じ/類似の修正を提案しているかどうか確認していただけますか？

### コメント 3 by KILL9-NO-MERCY

**作成日**: 2026-01-14

情報ありがとうございます！PR [#5195](https://github.com/spring-projects/spring-batch/issues/5195)を確認して、そちらにコメントします。
