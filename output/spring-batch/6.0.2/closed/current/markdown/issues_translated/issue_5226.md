*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月22日に生成されました）*

# v6におけるChunkListenerの変更点を明確化

**Issue番号**: [#5226](https://github.com/spring-projects/spring-batch/issues/5226)

**状態**: closed | **作成者**: cho-heidi | **作成日**: 2026-01-20

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5226

**関連リンク**:
- コミット:
  - [20eaa7b](https://github.com/spring-projects/spring-batch/commit/20eaa7b696c94a1432feb94e6d452cd959ad571f)

## 内容

**バグの説明**

Spring Batch 5.xから6.xにアップグレードした後、`ItemReader`に定義した`ChunkListener`のコールバックが呼び出されなくなりました。

以下の両方のアプローチで問題が発生しています：

* `ItemReader`に直接`ChunkListener`を実装する方法
* `@BeforeChunk`アノテーションを使用する方法

どちらのアプローチもSpring Batch 5.xでは期待通りに動作していましたが、Spring Batch 6.xでは`beforeChunk`も`@BeforeChunk`でアノテーションされたメソッドも呼び出されません。
ステップ自体は正常に実行され、`read()`は呼び出されますが、チャンクのライフサイクルコールバックは警告なく無視されます。
マイグレーションガイドやリファレンスドキュメントで、この動作変更に関する記述を見つけることができませんでした。

**環境**

- Spring Batchバージョン: 6.x 
- Spring Bootバージョン: 4.0.1
- Javaバージョン: 21 
- 言語: Kotlin 

**再現手順**
1. `@StepScope`でアノテーションされた`ItemReader`のBeanを作成
2. 以下のいずれかの方法でチャンクライフサイクルのロジックを定義：
	•	`ChunkListener#beforeChunk`
	•	`@BeforeChunk`でアノテーションされたメソッド
3. チャンク指向ステップにリーダーを通常通り登録
4. ジョブを実行

ChunkListenerを使用した例
```kotlin
@Component
@StepScope
class TestReader() : ItemReader<Long>, ChunkListener<Long, Long> {
    private val logger = LoggerFactory.getLogger(this::class.simpleName)

    override fun beforeChunk(chunk: Chunk<Long>) {
           logger.info("before chunk") // Spring Batch 6.xでは呼び出されない
    }

    override fun read(): Long? {
        return 10000L
    }
}
```

**期待される動作**
Spring Batch 5.xと同様に、チャンクライフサイクルのコールバック（`beforeChunk`、`@BeforeChunk`）は各チャンクの前に呼び出されるべきです。


## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2026-01-21

こんにちは！
おそらくステップの設定時に非推奨の`chunk`メソッドを使用しているのではないでしょうか（違う場合はお知らせください）：
```java
chunk(int chunkSize, PlatformTransactionManager transactionManager)
```

この非推奨メソッドを使用すると、Spring Batchはレガシー（6.0以前）のステップ実装を使用します。レガシーのステップでは、あなたが実装している`beforeChunk`メソッドのシグネチャは呼び出されません：
```java
beforeChunk(Chunk<I> chunk)  // これはレガシーステップでは呼び出されません
```

レガシーのステップ実装は、古い`beforeChunk`メソッドのシグネチャのみを呼び出します：
```java
beforeChunk(ChunkContext context)  // これがレガシーステップが期待するものです
```

これを修正するには、以下のいずれかを行う必要があります：
- Spring Batch 6.x用の新しいステップビルダーAPIに移行する
- ステップのバージョンに合わせて、レガシーのメソッドシグネチャを使用するように`ChunkListener`の実装を更新する

### コメント 2 by fmbenhassine

**作成日**: 2026-01-21

これはより大きな変更の一部でした（[#3950](https://github.com/spring-projects/spring-batch/issues/3950) を参照）。Javadocには記載されていましたが、リファレンスドキュメントやマイグレーションガイドには記載されていませんでした。混乱を招いて申し訳ありません。それらを更新しますが、この変更の背景を説明します：

`ChunkContext`の概念は、[repeatフレームワーク](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-infrastructure/src/main/java/org/springframework/batch/infrastructure/repeat)の一部として、チャンク指向処理モデルのレガシー実装（v5）でのみ使用されています。しかし、新しい実装ではこの概念を使用しないため、`ChunkContext`を受け取るチャンクリスナーメソッドは削除予定として非推奨になりました（これらはレガシー実装でのみ使用するために残されており、レガシー実装と同時に、つまりv7で削除されます）。

`ChunkListener`のメソッドは、新しい実装に合わせて`Chunk`のアイテムを受け取るように変更されました（`ChunkContext`は使用しなくなりました）。考えてみると、チャンクを読み込む前にはチャンクはまだ存在しないため、その時点で`beforeChunk(Chunk chunk)`にパラメータとして渡すことはできません。そのため、`beforeChunk`は実際にはチャンクが処理準備完了になった時点（つまり、データソースから読み込まれた後）にのみ呼び出されます。これは[ChunkListener.html#beforeChunkのJavadoc](https://docs.spring.io/spring-batch/reference/api/org/springframework/batch/core/listener/ChunkListener.html#beforeChunk(org.springframework.batch.infrastructure.item.Chunk))に記載されています：「チャンクが処理される前のコールバック」。

さらに、新しいインターフェースを設計する際に、パラメータなしの`ChunkListener#beforeChunk()`を残すことも考えましたが、これは私には意味がないと思いました（ユーザーとして、コンテキストもアイテムのチャンクもない状態でそのメソッドで何ができるでしょうか？）。

これで状況がより明確になれば幸いです。

@KILL9-NO-MERCY フォローアップありがとうございます！確かに、レガシー実装か新しい実装かを選択できますが、適切なリスナーコールバックを使用する必要があります。

### コメント 3 by cho-heidi

**作成日**: 2026-01-22

@KILL9-NO-MERCY @fmbenhassine 理解できました。明確な説明をいただきありがとうございます。
