*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# ChunkOrientedStepがチャンク失敗時にもExecutionContextを更新するため、リスタート時にデータ損失が発生する

**課題番号**: [#5182](https://github.com/spring-projects/spring-batch/issues/5182)

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5182

## 内容

Spring Batchチームの皆さん、こんにちは！

## バグの説明: 
Spring Batch 6.xでは、新しく導入された`ChunkOrientedStep`が、`processChunkSequentially`と`processChunkConcurrently`の両方でfinallyブロック内で`itemStream.update()`と`jobRepository.updateExecutionContext()`を呼び出しています。これは従来の`TaskletStep`実装とは異なります。

これにより、チャンクトランザクションが失敗してロールバックされた場合でも、`ItemStream`の状態（読み取りカウント、現在のインデックスなど）が永続化されてしまいます。その結果、リスタート時にステップは「失敗した」オフセットから再開され、失敗したチャンク内のレコードが暗黙的にデータ損失となります。


## コード比較（根本原因）

#### Spring Batch 5.x（TaskletStep.java）
バージョン5では、チャンクが正常に処理されコミットされた後にのみ状態が更新されます。

```java

// TaskletStep.java（452行目）
// このロジックは正常な処理フロー内にある
stream.update(stepExecution.getExecutionContext());
getJobRepository().updateExecutionContext(stepExecution);
stepExecution.incrementCommitCount();
```


#### Spring Batch 6.x（ChunkOrientedStep.java）
バージョン6では、更新ロジックがfinallyブロックに移動され、ロールバック時でも強制的に更新されます。
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
トランザクションの不整合: ビジネスデータはロールバックされるが、バッチメタデータ（インデックス/オフセット）はコミット/更新される。

データ損失: リスタート時、`ItemReader`は失敗したチャンクの後の位置から再開するため、失敗したチャンク内のレコードが再処理されることはない。

## 環境
Spring Batchバージョン: 6.0.1
コンポーネント: `ChunkOrientedStep`

## 期待される動作
`ExecutionContext`と`ItemStream`の状態は、チャンクトランザクションが成功した場合にのみ更新されるべきです。例外が発生した場合、finallyブロックは進行した状態を`JobRepository`に永続化すべきではありません。


## 推奨される修正
状態の更新ロジックは、`processChunkXXX`メソッドのfinallyブロックから`doExecute`メソッドに移動し、具体的にはトランザクションが正常に完了した後に配置すべきです。

ChunkOrientedStep.javaでの提案変更:
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // 次のチャンクを独自のトランザクションで処理
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
注意: 重複または早すぎる更新を防ぐために、`processChunkSequentially`と`processChunkConcurrently`のfinallyブロック内の対応する更新呼び出しを削除する必要があります。


お時間をいただき、この素晴らしいプロジェクトをメンテナンスしていただきありがとうございます！詳細やサンプルが必要な場合はお知らせください！

## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2026-01-06

Spring Batchチームの皆さん、こんにちは！
この課題に関連するフォローアップのコンテキストを追加したいと思います。

先日、`ChunkOrientedStep#doExecute`における`JobRepository.update(stepExecution)`のトランザクション境界に関して別の課題（[#5199](https://github.com/spring-projects/spring-batch/issues/5199)）を開きました。

[#5199](https://github.com/spring-projects/spring-batch/issues/5199) で提案された修正（`JobRepository.update(stepExecution)`をチャンクトランザクション内に移動する）が適用される場合、この課題（[#5182](https://github.com/spring-projects/spring-batch/issues/5182)）で提案された修正も若干調整する必要があります。

以前の提案された修正は、これらの更新をトランザクション完了後に`doExecute`に移動することを提案しています。しかし、`JobRepository.update(stepExecution)`自体がトランザクション内に移動される場合（[#5199](https://github.com/spring-projects/spring-batch/issues/5199) で提案されているように）、完全な一貫性を維持するために、以下の操作も同じトランザクション境界に合わせる必要があります:
- `JobRepository.update(stepExecution)`
- `ItemStream.update(stepExecution.getExecutionContext())`
- `JobRepository.updateExecutionContext(stepExecution)`

## 提案する調整
```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
       // 次のチャンクを独自のトランザクションで処理
       this.transactionTemplate.executeWithoutResult(transactionStatus -> {
           processNextChunk(transactionStatus, contribution, stepExecution);
           // 修正: ItemStreamとExecutionContextを更新
           this.compositeItemStream.update(stepExecution.getExecutionContext());
           getJobRepository().updateExecutionContext(stepExecution);
           // 修正 #5199
           getJobRepository().update(stepExecution);
       });
    }
}
```

両方の課題が一貫して対処されるようにこれを指摘したかっただけです。統一された修正やテストが必要であればお手伝いします。ありがとうございます！

### コメント 2 by fmbenhassine

**作成日**: 2026-01-12

v6に関する継続的なフィードバックをいただきありがとうございます。

> 統一された修正やテストが必要であればお手伝いします。

はい、お願いします。大変助かります！事前にありがとうございます。

編集: この課題に対するPRがあるようです: [#5195](https://github.com/spring-projects/spring-batch/pull/5195)。考えているのと同じ/類似の修正を提案しているか確認していただけますか？

### コメント 3 by KILL9-NO-MERCY

**作成日**: 2026-01-14

情報をいただきありがとうございます！PR [#5195](https://github.com/spring-projects/spring-batch/pull/5195) を確認し、そちらにコメントを残します。
