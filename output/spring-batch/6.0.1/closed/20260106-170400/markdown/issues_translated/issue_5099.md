*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# 新しいチャンク処理実装において、パーティションステップの最初のパーティションが終了すると処理が停止する問題

**課題番号**: #5099

**状態**: closed | **作成者**: marbon87 | **作成日**: 2025-11-21

**ラベル**: type: bug, in: core, has: minimal-example, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5099

**関連リンク**:
- Commits:
  - [a2d61f8](https://github.com/spring-projects/spring-batch/commit/a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69)

## 内容

ローカルパーティションを使用するステップにおいて、各パーティションのアイテム数が異なる場合、最初のパーティションが処理を完了した時点でステップ全体が終了してしまいます。これにより、他のパーティションに未処理のアイテムが残ってしまいます。

以下は、ステップとテストの例です。新しいチャンク処理実装ではこのテストが失敗します：

[partition-example.tar.gz](https://github.com/user-attachments/files/23675568/partition-example.tar.gz)

古いチャンク実装に切り替えると、テストは正常に実行されます。

## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2025-11-21

偶然この課題に遭遇し、調査を行いました。

根本原因を完全に特定できたかどうかは確信が持てませんが、以下の観察結果を共有します：
`ChunkOrientedStep.doExecute(StepExecution)`は各パーティションに対して実行されるため、合計3回呼び出されます。しかし、読み取るアイテムがなくなった際に呼び出される`ChunkTracker.noMoreItems()`は、すべての実行を通じて1回しか呼び出されていません。

各パーティション実行には、独自の`ChunkTracker`インスタンスが必要なようです。

私が間違っている可能性もありますので、ご確認ください。

### コメント 2 by fmbenhassine

**作成日**: 2025-11-24

この課題を報告し、サンプルを提供していただきありがとうございます！サンプルは`ResourcelessJobRepository`（Spring Batch 6 / Spring Boot 4のデフォルト）を使用しています。このジョブリポジトリの実装は、実行コンテキストを何らかの形で使用するユースケースには適していません（ローカルパーティショニングを含む。javadocおよび[リファレンスドキュメント](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html#_configuring_a_resourceless_jobrepository)を参照してください）。

とはいえ、JDBCジョブリポジトリの実装を使用した場合でも、`ChunkOrientedStep`に問題があります。チャンクトラッカーが現在インスタンスごとに定義されているのに対し、スレッドごとであるべきだからです（現在、ローカルパーティショニングを単純なタスクレットでテストしており、チャンク指向のタスクレットではテストしていないため、テストスイートにギャップがあるようです）。次のパッチリリースで修正を予定しています。

### コメント 3 by zhaozhiguang

**作成日**: 2025-11-28

私も同じ問題に遭遇しました。`Partitioner`と`JdbcPageItemReaderBuilder`を使用した際に発生しました。

### コメント 4 by abstiger

**作成日**: 2025-11-28

スレッドローカルへの切り替えでは問題が解決しないと思います。同じスレッドでジョブステップが2回実行された場合はどうなるでしょうか？

私も似たような課題に遭遇しました。あるジョブには1つのステップしかなく、リーダーは`JdbcCursorItemReader`（すべてのユーザーを読み込み、10人のユーザーがいると仮定）で、チャンクサイズは1です。

このジョブを2回実行します：

最初の実行では、10人のユーザーを正常に読み込み、後続の処理を実行しました（この時点で、`chunkTracker`は`noMoreItems()`を設定しています）。

2回目の実行では、`noMoreItems()`が既に設定されているため、直接スキップされました。

おそらく、`ChunkOrientedStep`のステップオープン時にtrueに設定するべきでしょうか？

```java
	@Override
	protected void open(ExecutionContext executionContext) throws Exception {
		this.compositeItemStream.open(executionContext);
		// ステップオープンのたびにtrueに設定
		this.chunkTracker.get().moreItems = true;
	}

```



### コメント 5 by kzander91

**作成日**: 2025-12-03

このバグは [#5126](https://github.com/spring-projects/spring-batch/issues/5126) の原因でもあり、ここでコミットされた修正では解決しません。@abstiger が説明した通りです。
修正のもう1つの問題は、`ThreadLocal`が再びクリアされないことです。そのため、`open()`でフラグを反転させる代わりに、`close()`でクリアすることをお勧めします：
```java
	@Override
	protected void close(ExecutionContext executionContext) throws Exception {
		this.chunkTracker.remove(); // 次の呼び出しで新しいインスタンスをインスタンス化し、リークを回避することを保証
		this.compositeItemStream.close();
	}
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-04

フィードバックをありがとうございます！

@abstiger 

> スレッドローカルへの切り替えでは問題が解決しないと思います。同じスレッドでジョブステップが2回実行された場合はどうなるでしょうか？
 
実際に解決します。ただ、[a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69](https://github.com/spring-projects/spring-batch/commit/a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69)でスレッドバウンドのチャンクトラッカーを導入した際に、そのライフサイクルが正しく管理されていませんでした。[69665d83d8556d9c23a965ee553972a277221d83](https://github.com/spring-projects/spring-batch/commit/69665d83d8556d9c23a965ee553972a277221d83)でそれに対処しました。

