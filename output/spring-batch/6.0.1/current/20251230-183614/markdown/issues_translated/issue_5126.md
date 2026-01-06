# `ChunkOrientedStep.ChunkTracker`がステップ後にリセットされず、特定のステップの単一実行のみが許可される

**Issue番号**: #5126

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-03

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5126

**関連リンク**:
- Commits:
  - [69665d8](https://github.com/spring-projects/spring-batch/commit/69665d83d8556d9c23a965ee553972a277221d83)

## 内容

**バグの説明**
`ChunkOrientedStep.doExecute()`は`chunkTracker.moreItems()`が`true`を返さなくなるまでループします:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L359-L375

リーダーが枯渇すると、`chunkTracker`は`false`に切り替わりますが、このフラグは`true`にリセットされません。その結果、ステップの2回目の呼び出しから、`chunkTracker.moreItems()`がまだ`false`を返すため、すぐに終了し、何もしなくなります。

**環境**
Spring Batch 6.0.0

**再現手順**
1. チャンク指向のステップを持つジョブを設定します。
2. ジョブを実行します。
3. ジョブを再度実行します。

**期待される動作**
ステップが両方の実行で実行されるはずです。

**最小限の再現可能な例**
[demo14.zip](https://github.com/user-attachments/files/23903365/demo14.zip)
`./mvnw test`で実行

再現プログラムには、ジョブを3回呼び出すテストがあります。最初の呼び出しはチャンク処理を開始しますが、その後の両方の呼び出しはそれをスキップします。これはログにも表示され、最初の実行では次のようなログが出力されます:
```
Job: [SimpleJob: [name=job]] launched with the following parameters: [{JobParameter{name='batch.random', value=7960112850225085599, type=class java.lang.Long, identifying=true}}]
Executing step: [step]
Reader was called, returning item
Reader was called, returning null
Writing chunk: [items=[item], skips=[]]
Step: [step] executed in 5ms
Job: [SimpleJob: [name=job]] completed with the following parameters: [{JobParameter{name='batch.random', value=7960112850225085599, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 22ms
```

その後の呼び出しでは次のようなログが出力されます:
```
Job: [SimpleJob: [name=job]] launched with the following parameters: [{JobParameter{name='batch.random', value=-1299334786035736075, type=class java.lang.Long, identifying=true}}]
Executing step: [step]
Step: [step] executed in
Job: [SimpleJob: [name=job]] completed with the following parameters: [{JobParameter{name='batch.random', value=-1299334786035736075, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 6ms
```

(細かい点: ステップの実行時間がゼロの場合、実行時間が欠落したメッセージが表示されます: `Step: [step] executed in`) -> 課題 [#5037](https://github.com/spring-projects/spring-batch/issues/5037)

---

現在の回避策は、すべての`Job`および`Step` Beanを`@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)`で宣言することです。その後、各実行で新しいインスタンスが使用されるように、`BeanFactory`から各ジョブをオンデマンドで取得する独自の`JobRegistry`を実装しました。

## コメント

### コメント 1 by abstiger

**作成日**: 2025-12-03

https://github.com/spring-projects/spring-batch/issues/5099#issuecomment-3588361319

### コメント 2 by Jaraxxuss

**作成日**: 2025-12-04

テストメソッドで同じジョブを複数回起動すると同じ課題が発生します。

### コメント 3 by fmbenhassine

**作成日**: 2025-12-04

この課題を報告し、最小限の例を提供していただきありがとうございます。確かに、課題 [#5099](https://github.com/spring-projects/spring-batch/issues/5099) で導入したときのスレッドバインドチャンクトラッカーのライフサイクルが正しくありませんでした。今後のパッチリリースで修正します。

余談ですが: v6についていくつかの課題を報告し、フィードバックを共有していただき、感謝しています🙏 6.0.0でいくつかの不具合やエッジケースが出ることは予想していました(すべての大幅な改訂と同様に)が、6.0.1で安定化を優先しています。また、あなたの[モジュール化リクエスト](https://github.com/spring-projects/spring-batch/issues/5072#issuecomment-3575523924)についてもできるだけ早くお手伝いします。ご理解ありがとうございます。

### コメント 4 by kzander91

**作成日**: 2025-12-04

@fmbenhassine もちろんです! 通常、マイルストーンフェーズ中に早めにフィードバックを提供するようにしていますが、今回はモジュール化で基本的に行き詰まっていたため、実現できませんでした。
個人的には既に単一コンテキストの使用に移行しましたが(もちろん他の方はまだガイダンスが必要かもしれません)、そのおかげでv6をより徹底的にテストできるようになりました。

### コメント 5 by fmbenhassine

**作成日**: 2025-12-04

@kzander91 提供していただいた再現プログラムは、これを作成するインスピレーションになりました: b58c8429bcad782702fd4f1015b9dcc984b3de2b。インスピレーションをありがとう 😉

