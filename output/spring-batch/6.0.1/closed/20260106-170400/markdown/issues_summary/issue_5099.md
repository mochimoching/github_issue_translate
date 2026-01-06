*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5099: パーティションステップの最初のパーティションが終了すると処理が停止する問題

## 課題概要

Spring Batch 6の新しいチャンク処理実装において、ローカルパーティション機能を使用する際に重大な不具合が発生していました。複数のパーティション（データの分割処理単位）を持つステップで、各パーティションのアイテム数が異なる場合、最初のパーティションが完了した時点でステップ全体が終了してしまい、他のパーティションの未処理データが残ってしまう問題です。

### 用語解説

- **パーティション**: 大量データを複数の小さなグループに分割して並列処理する仕組み。例えば、1000件のデータを100件ずつ10個のパーティションに分けて処理する
- **チャンク処理**: データを一定の単位（チャンク）ごとにまとめて処理する方法。トランザクション管理を効率的に行える
- **ローカルパーティション**: 同一プロセス内で複数スレッドを使って並列処理を行う方式

### 問題の具体例

以下のような状況で問題が発生します：

| パーティション | アイテム数 | 処理状況 |
|--------------|----------|---------|
| パーティション1 | 10件 | ✅ 完了 |
| パーティション2 | 50件 | ❌ 途中で停止 |
| パーティション3 | 30件 | ❌ 未処理 |

パーティション1が完了した時点でステップ全体が終了してしまうため、パーティション2と3のデータが処理されません。

## 原因

新しいチャンク処理実装における`ChunkTracker`（チャンクの処理状態を追跡するクラス）の管理方法に問題がありました。

### 詳細な原因

1. **ChunkTrackerのスコープ問題**: 
   - `ChunkTracker`がステップインスタンスごとに1つだけ作成されていた
   - 本来はスレッドごと（パーティションごと）に独立したインスタンスが必要

2. **状態の共有**:
   ```java
   // 問題のあったコード構造（イメージ）
   class ChunkOrientedStep {
       private ChunkTracker chunkTracker = new ChunkTracker(); // 全パーティションで共有
       
       void doExecute(StepExecution execution) {
           // パーティション1が完了すると...
           chunkTracker.noMoreItems(); // ここで「もうアイテムはない」とマーク
           
           // パーティション2, 3も同じchunkTrackerを見てしまう
       }
   }
   ```

3. **早期終了の発生**:
   - パーティション1が完了して`noMoreItems()`を呼び出す
   - パーティション2, 3が処理を始めようとするが、既に`noMoreItems()`が設定されているため即座に終了してしまう

### 追加の問題点

初期の修正では`ThreadLocal`（スレッドごとに独立した変数を持つ仕組み）を使用しましたが、ライフサイクル管理が不十分で以下の問題がありました：

- 同じスレッドで2回目のジョブを実行した際、前回の状態が残ってしまう
- `ThreadLocal`のクリーンアップが行われず、メモリリークの可能性

## 対応方針

`ChunkTracker`をスレッドローカル変数として管理し、適切なライフサイクル制御を実装しました。

### 修正内容

[コミット a2d61f8](https://github.com/spring-projects/spring-batch/commit/a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69)、[コミット 69665d8](https://github.com/spring-projects/spring-batch/commit/69665d83d8556d9c23a965ee553972a277221d83)

```java
// 修正後のコード構造（イメージ）
class ChunkOrientedStep {
    // スレッドごとに独立したChunkTrackerを持つ
    private ThreadLocal<ChunkTracker> chunkTracker = ThreadLocal.withInitial(ChunkTracker::new);
    
    @Override
    protected void open(ExecutionContext executionContext) {
        this.compositeItemStream.open(executionContext);
        // ステップ開始時に状態をリセット（2回目の実行に備える）
        this.chunkTracker.get().moreItems = true;
    }
    
    @Override
    protected void close(ExecutionContext executionContext) {
        // スレッドローカル変数をクリーンアップ（メモリリーク防止）
        this.chunkTracker.remove();
        this.compositeItemStream.close();
    }
}
```

### 修正のポイント

1. **ThreadLocalの導入**: 各スレッド（パーティション）が独立した`ChunkTracker`を持つ
2. **open()での初期化**: ステップ開始時に状態を確実にリセット
3. **close()でのクリーンアップ**: スレッドローカル変数を削除してメモリリークを防止

### 修正後の動作

| パーティション | アイテム数 | 処理状況 |
|--------------|----------|---------|
| パーティション1 | 10件 | ✅ 完了 |
| パーティション2 | 50件 | ✅ 完了 |
| パーティション3 | 30件 | ✅ 完了 |

すべてのパーティションが独立して正しく処理されます。

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `ChunkOrientedStep` - チャンク指向のステップ実装
  - `ChunkTracker` - チャンク処理の状態を追跡
- **関連課題**: [#5126](https://github.com/spring-projects/spring-batch/issues/5126) - 同じ根本原因による別の問題
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5099
