# ChunkOrientedStepがチャンク失敗時にもExecutionContextを更新し、再起動時にデータ損失を引き起こす

**課題番号**: #5182

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5182

## 内容

Spring Batchチームの皆様、こんにちは！

## バグの説明: 
Spring Batch 6.xで新たに導入された`ChunkOrientedStep`は、`processChunkSequentially`と`processChunkConcurrently`の両方で、`finally`節内で`itemStream.update()`と`jobRepository.updateExecutionContext()`を呼び出します。これは従来の`TaskletStep`の実装とは異なります。

この結果、チャンクのトランザクションが失敗してロールバックされた場合でも、`ItemStream`の状態（例：読み取り件数、現在のインデックス）が永続化されてしまいます。その結果、再起動時にステップが「失敗した」オフセットから再開され、失敗したチャンク内のレコードがサイレントに失われることになります。


## コード比較（根本原因）

#### Spring Batch 5.x (TaskletStep.java)
バージョン5では、チャンクが正常に処理されてコミットされた後にのみ状態が更新されます。

```java

// TaskletStep.java (Line 452)
// このロジックは成功した処理フロー内にあります
stream.update(stepExecution.getExecutionContext());
getJobRepository().updateExecutionContext(stepExecution);
stepExecution.incrementCommitCount();
```


#### Spring Batch 6.x (ChunkOrientedStep.java)
バージョン6では、更新ロジックが`finally`節に移動され、ロールバック時にも強制的に更新されます。
```java
// ChunkOrientedStep.java
private void processChunkSequentially(...) {
    try {
        // チャンクの読み取り/処理/書き込みロジック
    } catch (Exception e) {
        // 例外処理
        throw e;
    } finally {
        // バグ: トランザクションがロールバックされても必ず実行される！
        this.compositeItemStream.update(stepExecution.getExecutionContext());
        getJobRepository().updateExecutionContext(stepExecution);
    }
}
```

## 影響
トランザクションの不整合: ビジネスデータはロールバックされますが、バッチメタデータ（インデックス/オフセット）はコミット/更新されます。

データ損失: 再起動時に、`ItemReader`が失敗したチャンクの後の位置から再開するため、失敗したチャンク内のレコードが再処理されることはありません。

## 環境
Spring Batchバージョン: 6.0.1
コンポーネント: ChunkOrientedStep 

## 期待される動作
`ExecutionContext`と`ItemStream`の状態は、チャンクのトランザクションが成功した場合にのみ更新されるべきです。例外が発生した場合、`finally`節で進んだ状態を`JobRepository`に永続化すべきではありません。


## 修正案
状態更新ロジックは、`processChunkXXX`メソッドの`finally`節から`doExecute`メソッドに移動し、具体的にはトランザクションが正常に完了した後に配置すべきです。

`ChunkOrientedStep.java`での提案変更：
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
       
       // 修正: トランザクションコミット成功後にのみItemStreamとExecutionContextを更新
       this.compositeItemStream.update(stepExecution.getExecutionContext());
       getJobRepository().updateExecutionContext(stepExecution);
    }
}
```
注：重複または時期尚早な更新を防ぐため、`processChunkSequentially`と`processChunkConcurrently`の`finally`節内の対応する更新呼び出しは削除する必要があります。


お時間を割いていただき、またこの素晴らしいプロジェクトをメンテナンスしていただきありがとうございます！さらに詳細やサンプルが必要な場合はお知らせください！
