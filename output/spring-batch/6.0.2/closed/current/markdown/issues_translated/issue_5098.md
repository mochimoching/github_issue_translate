*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月22日に生成されました）*

# StaxEventItemWriterとMultiResourceItemWriterを組み合わせた際にClosedChannelExceptionが発生する

**Issue番号**: [#5098](https://github.com/spring-projects/spring-batch/issues/5098)

**状態**: closed | **作成者**: g00glen00b | **作成日**: 2025-11-21

**ラベル**: in: infrastructure, type: bug, has: minimal-example, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5098

**関連リンク**:
- コミット:
  - [5dc40a6](https://github.com/spring-projects/spring-batch/commit/5dc40a6b97dfb2dd3f556913d5ec60f0ba94acfb)

## 内容

**バグの説明**
`StaxEventItemWriter`を`MultiResourceItemWriter`と組み合わせて使用すると、以下のスタックトレースで`ClosedChannelException`がスローされます：

```
Caused by: java.nio.channels.ClosedChannelException: null
    at java.base/sun.nio.ch.FileChannelImpl.ensureOpen(FileChannelImpl.java:160) ~[na:na]
    at java.base/sun.nio.ch.FileChannelImpl.write(FileChannelImpl.java:284) ~[na:na]
    at org.springframework.batch.support.transaction.TransactionAwareBufferedWriter$1.complete(TransactionAwareBufferedWriter.java:121) ~[spring-batch-infrastructure-5.2.4.jar:5.2.4]
    at org.springframework.batch.support.transaction.TransactionAwareBufferedWriter$1.beforeCommit(TransactionAwareBufferedWriter.java:106) ~[spring-batch-infrastructure-5.2.4.jar:5.2.4]
    ... 44 common frames omitted
```

この問題は`StaxEventItemWriter`がトランザクション対応として設定されている場合にのみ発生します。デバッグを進めたところ、ライターがクローズされた後に`endDocument()`メソッドが実行されることが原因のようですが、確実ではありません。

**環境**
Java 21上の複数のSpring Batchバージョン（5.2.3、6.0.0を含む）で再現可能

**再現手順**
1. `StaxEventItemWriter`を定義：

    ```java
    @Bean
    public StaxEventItemWriter<Foo> fooWriter() {
        return new StaxEventItemWriterBuilder<Foo>()
            .name("fooWriter")
            .marshaller(marshaller())
            .rootTagName("foos")
            // 注意：Spring Batch 6.0では、`MultiResourceItemWriter`によって上書きされるにもかかわらず、
            // ビルダー内で`resource`を渡す必要があるようです
            .resource(new FileSystemResource("foo/foo.xml"))
            .build();
    }
    ```

2. `MultiResourceItemWriter`を定義：

    ```java
    @Bean
    public MultiResourceItemWriter<Foo> multiFooWriter() {
        return new MultiResourceItemWriterBuilder<Foo>()
            .name("multiFooWriter")
            .delegate(fooWriter())
            .itemCountLimitPerResource(100)
            .resourceSuffixCreator(index -> "-" + index + ".xml")
            .resource(new FileSystemResource("foo"))
            .build();
    }
    ```

3. この`MultiResourceItemWriter`を使用する`Job`を定義して実行します。前述のスタックトレースが発生します。`StaxEventItemWriter`で`.transactional(false)`を設定すると、バッチは正常に完了します。

**期待される動作**
100個のXMLファイルが作成されることを期待しています（リーダーが10,000アイテムを生成し、ライターが100アイテムごとに別ファイルを作成）。

**最小限の再現可能なサンプル**
[GitHubリポジトリ](https://github.com/g00glen00b/spring-batch-multiresource-stax-reader-transactional-issue/)

**補足情報**
関連するStack Overflowスレッド：[リンク](https://stackoverflow.com/q/79825366)
このStack Overflowスレッドでは、これが意図された動作である可能性について議論されました。もしそうであれば、ドキュメントのどこかにこの点を記載するPRを送ることもできます。


## コメント

### コメント 1 by banseok1216

**作成日**: 2025-12-20

こんにちは。

説明がコメントに収まりきらなかったため、より完全な再現手順と詳細なメモを含む別のIssueを作成し、修正を含むPRを提出しました。
- https://github.com/spring-projects/spring-batch/issues/5176

### コメント 2 by fmbenhassine

**作成日**: 2026-01-21

@g00glen00b このIssueを作成し、サンプルを提供していただきありがとうございます！これはドキュメントの問題ではなく、バグです。

この問題を修正する正しい方向性の[#5177](https://github.com/spring-projects/spring-batch/issues/5177)をレビュー中です。修正が含まれるバージョンについて、こちらにコメントで更新します。

@banseok1216 [#5176](https://github.com/spring-projects/spring-batch/issues/5176)での素晴らしい分析とPRをありがとうございます。本当に感謝しています 🙏

> 説明がコメントに収まりきらなかったため

同じ問題に対する説明でしたので、このIssueの重複としてクローズします。
