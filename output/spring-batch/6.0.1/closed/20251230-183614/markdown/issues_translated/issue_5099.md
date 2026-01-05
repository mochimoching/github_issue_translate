# 新しいチャンク処理実装において、最初のパーティションが完了するとパーティション化されたステップが処理を停止する

**Issue番号**: #5099

**状態**: closed | **作成者**: marbon87 | **作成日**: 2025-11-21

**ラベル**: type: bug, in: core, has: minimal-example, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5099

**関連リンク**:
- Commits:
  - [a2d61f8](https://github.com/spring-projects/spring-batch/commit/a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69)

## 内容

ローカルパーティションを使用するステップで、各パーティションのアイテム数が異なる場合、最初のパーティションが作業を完了した時点でステップが終了してしまいます。これにより、他のパーティションのアイテムが未処理のまま残ります。

以下は、新しいチャンク処理実装で失敗するステップとテストの例です:

[partition-example.tar.gz](https://github.com/user-attachments/files/23675568/partition-example.tar.gz)

古いチャンク実装に切り替えると、テストは正常に実行されます。

## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2025-11-21

偶然この課題に遭遇し、調査を行いました。

根本原因を見つけられたか完全には確信できませんが、以下のことを観察しました:
`ChunkOrientedStep.doExecute(StepExecution)`は各パーティションに対して実行されるため、合計3回呼び出されます。しかし、読み取るアイテムがなくなったときに呼び出される`ChunkTracker.noMoreItems()`は、すべての実行を通じて1回しか呼び出されません。

各パーティションの実行には、それぞれ独自の`ChunkTracker`インスタンスが必要なようです。

間違っている可能性があるので、確認してください。

### コメント 2 by fmbenhassine

**作成日**: 2025-11-24

この課題の報告と例の提供、ありがとうございます! サンプルは`ResourcelessJobRepository`(Spring Batch 6 / Spring Boot 4のデフォルト)を使用しています。このジョブリポジトリ実装は、実行コンテキストを何らかの形で使用するユースケース(ローカルパーティショニングを含む)には適していません。そのjavadocおよび[リファレンスドキュメント](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html#_configuring_a_resourceless_jobrepository)を参照してください。

とはいえ、JDBCジョブリポジトリ実装を使用しても`ChunkOrientedStep`に問題があります。チャンクトラッカーが現在インスタンスごとに定義されていますが、スレッドごとに定義されるべきです(テストスイートに不足があるようです。現在、ローカルパーティショニングをシンプルなタスクレットでテストしており、チャンク指向のタスクレットではテストしていません)。次のパッチリリースで修正を予定しています。

### コメント 3 by zhaozhiguang

**作成日**: 2025-11-28

私も同じ問題に遭遇しました。PartitionerとJdbcPageItemReaderBuilderを使用したときです。

### コメント 4 by abstiger

**作成日**: 2025-11-28

スレッドローカルへの切り替えでは問題が解決しないと思います。同じスレッドでジョブステップが2回実行された場合はどうなるでしょうか?

私も同様の課題に遭遇しました。ジョブには1つのステップしかなく、リーダーはJdbcCursorItemReader(すべてのユーザーを読み取る、10人のユーザーがいると仮定)で、チャンクサイズは1です。

このジョブを2回実行します:

最初の実行では、10人のユーザーを正常に読み取り、後続の処理を実行しました(この時点で、chunkTrackerは`noMoreItems()`を設定しました)。

2回目の実行では、`noMoreItems()`がすでに設定されていたため、直接スキップされました。

`ChunkOrientedStep`でステップのオープン時にtrueに設定するのはどうでしょうか?

```java
	@Override
	protected void open(ExecutionContext executionContext) throws Exception {
		this.compositeItemStream.open(executionContext);
		// ステップのオープンごとにtrueに設定
		this.chunkTracker.get().moreItems = true;
	}

```



### コメント 5 by kzander91

**作成日**: 2025-12-03

このバグは課題 [#5126](https://github.com/spring-projects/spring-batch/issues/5126) の原因でもあり、@abstigerが説明したように、ここでコミットされた修正では解決しません。
修正にはもう1つ問題があり、`ThreadLocal`が再びクリアされないため、`open()`でフラグを反転させる代わりに、`close()`でクリアすることを提案します:
```java
	@Override
	protected void close(ExecutionContext executionContext) throws Exception {
		this.chunkTracker.remove(); // 次の呼び出しで新しいインスタンスをインスタンス化し、リークを回避する
		this.compositeItemStream.close();
	}
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-04

皆さん、フィードバックありがとうございます!

@abstiger

> スレッドローカルへの切り替えでは問題が解決しないと思います。同じスレッドでジョブステップが2回実行された場合はどうなるでしょうか?

解決します。単に、a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69で導入したスレッドバインドチャンクトラッカーのライフサイクルが正しく管理されていなかっただけです。69665d83d8556d9c23a965ee553972a277221d83でそれに対処しました。

