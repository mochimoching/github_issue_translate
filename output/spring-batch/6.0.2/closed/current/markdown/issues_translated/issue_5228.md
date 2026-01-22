*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月22日に生成されました）*

# v6における並行ステップに関するドキュメントの誤り

**Issue番号**: [#5228](https://github.com/spring-projects/spring-batch/issues/5228)

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2026-01-21

**ラベル**: in: documentation, type: bug, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5228

**関連リンク**:
- コミット:
  - [9ccbafa](https://github.com/spring-projects/spring-batch/commit/9ccbafa0cf387b36e22462921c53aab055f9cd64)

## 内容

### https://github.com/spring-projects/spring-batch/discussions/5214 での議論

<div type='discussions-op-text'>

<sup>**ctrung** による投稿（2026年1月14日）</sup>
こんにちは。

Spring Batch 6の新しい並行処理モデルでは、`ItemReader.read()`はメインスレッドからアクセスされるようになりました。以前は`taskExecutor`のスレッドからアクセスされていました。

このため、リーダーはスレッドセーフである必要がなくなったようです（私自身で検証しましたが、スレッドセーフなリーダーを使用してもしなくても動作は同じでした）。

リファレンスドキュメントの https://docs.spring.io/spring-batch/reference/scalability.html#multithreadedStep のセクションでは、依然としてスレッドセーフなリーダーが必要であると記載されています。

スレッドセーフなリーダーが依然として必要となる他のユースケースはありますか？

私のステップ定義：

```java
var step = new StepBuilder("my_step", jobRepository)
                         .<I, O>chunk(5)
                         .transactionManeger(transactionManager)
                         .reader(reader)
                         .writer(writer)
                         .taskExecutor(taskExecutor)
                         .build();
```
</div>

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-21

はい、新しい並行処理モデルでは、リーダーは単一のスレッドからのみ呼び出されるため、スレッドセーフである必要はありません。詳細についてはこちらで説明しています：https://github.com/spring-projects/spring-batch/issues/4955#issuecomment-3423549722

> リファレンスドキュメントの https://docs.spring.io/spring-batch/reference/scalability.html#multithreadedStep のセクションでは、依然としてスレッドセーフなリーダーが必要であると記載されています。

これは記載漏れでした。ドキュメントを修正します。

> スレッドセーフなリーダーが依然として必要となる他のユースケースはありますか？

Spring Batchが提供するステップ実装では必要ありません。同期ラッパーを残しているのは、カスタムステップを実装する方がリーダーやライターを同期デコレーターでラップする必要がある場合に備えてのことです。

> 私のステップ定義

このステップはデータの読み込みと書き込みのみを行っています（加工、変換、バリデーションなし）。そのため、並行処理を行う必要性があるようには見えません。複数スレッドを使用することでスループットが向上するかどうかは不明です（ベンチマークが必要です。おそらく逆効果となり、バイト転送よりも並行処理のオーバーヘッドに時間を費やすことになるでしょう）。
