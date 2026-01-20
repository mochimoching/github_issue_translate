*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

## 課題概要

Spring Batch 6.xの`ChunkOrientedStep`が、チャンク処理が失敗してロールバックした場合でも`ExecutionContext`を更新してしまい、再起動時にデータ損失が発生するバグです。

### ChunkOrientedStepとは
Spring Batch 6.0で新しく導入されたチャンク指向のステップ実装です。データをチャンク（まとまり）単位で読み込み、処理し、書き込むバッチ処理パターンを実現します。

### ExecutionContextとは
バッチ処理の実行状態（読み込み位置、処理済みアイテム数など）を保持するコンテキストです。再起動時にこの情報を使って前回の続きから処理を再開できます。

### 問題の詳細

```plantuml
@startuml
title トランザクションとExecutionContext更新の関係

participant "ChunkOrientedStep" as Step
participant "Transaction" as Tx
participant "ItemStream" as Stream
participant "JobRepository" as Repo
database "DB" as DB

== Spring Batch 5.x (正常動作) ==
Step -> Tx: begin
Tx -> DB: chunk処理
Tx -> DB: commit成功
Step -> Stream: update()
Step -> Repo: updateExecutionContext()
note right: トランザクション成功後のみ更新

== Spring Batch 6.x (バグあり) ==
Step -> Tx: begin
Tx -> DB: chunk処理
Tx -> DB: rollback (失敗)
Step -> Stream: update() [finallyブロック]
Step -> Repo: updateExecutionContext() [finallyブロック]
note right #pink: ロールバック後も更新されてしまう！

@enduml
```

| バージョン | 動作 |
|------------|------|
| Spring Batch 5.x (TaskletStep) | トランザクション成功後のみ`ExecutionContext`更新 |
| Spring Batch 6.x (ChunkOrientedStep) | finallyブロックで常に更新（バグ） |

### 影響

1. **トランザクションの不整合**: ビジネスデータはロールバックされるが、バッチメタデータ（インデックス/オフセット）は更新される
2. **データ損失**: 再起動時に失敗したチャンクの位置から再開されず、そのチャンクのデータが処理されない

```plantuml
@startuml
title 再起動時のデータ損失

rectangle "初回実行" {
  rectangle "Chunk 1\n(成功)" as C1 #lightgreen
  rectangle "Chunk 2\n(失敗)" as C2 #pink
  rectangle "Chunk 3\n(未処理)" as C3 #lightgray
}

note bottom of C2
  ExecutionContextが
  Chunk 3の位置で保存される
end note

rectangle "再起動" {
  rectangle "Chunk 1" as R1 #lightgray
  rectangle "Chunk 2" as R2 #pink
  rectangle "Chunk 3\n(再開)" as R3 #lightyellow
}

note bottom of R2
  Chunk 2がスキップされ
  データ損失発生！
end note

@enduml
```

## 原因

`ChunkOrientedStep`の`processChunkSequentially`および`processChunkConcurrently`メソッドで、`itemStream.update()`と`jobRepository.updateExecutionContext()`がfinallyブロック内で呼び出されているため、トランザクションがロールバックしても状態が更新されてしまいます。

## 対応方針

**修正PR**: [#5195](https://github.com/spring-projects/spring-batch/pull/5195)

`processChunkSequentially`と`processChunkConcurrently`のfinallyブロックから`ExecutionContext`更新処理を削除し、`doExecute`メソッド内でトランザクション成功後に更新するよう変更しました：

```java
// 修正前 (processChunkSequentially/processChunkConcurrently内)
finally {
    // apply contribution and update streams
    stepExecution.apply(contribution);
    compositeItemStream.update(stepExecution.getExecutionContext());
    getJobRepository().updateExecutionContext(stepExecution);
}
```

```java
// 修正後 (doExecute内、トランザクション完了後)
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    // process next chunk
});
getJobRepository().update(stepExecution);
// トランザクション成功後のみ更新
this.compositeItemStream.update(stepExecution.getExecutionContext());
getJobRepository().updateExecutionContext(stepExecution);
```

また、チャンクがロールバックした場合に`ItemStream.update()`が呼び出されないことを確認するテストケースも追加されました。

## バグの発生タイミング

- **バグが発生したSpring Batchのバージョン**: 6.0.0, 6.0.1

---

## 更新履歴

- 2026-01-20: 初版作成
