# パーティショナーがコンテキストを作成した後、ステップ実行が永続化されなくなった

**Issue番号**: #5138

**状態**: closed | **作成者**: brian-mcnamara | **作成日**: 2025-12-05

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5138

**関連リンク**:
- Commits:
  - [a8961a6](https://github.com/spring-projects/spring-batch/commit/a8961a6770a78cf94eee2f5d270f280751d2092d)
  - [1da2f28](https://github.com/spring-projects/spring-batch/commit/1da2f28b4c1a855feed5f10ad70b708ead061305)
  - [412158a](https://github.com/spring-projects/spring-batch/commit/412158afd9f8576b323d445212ed9e8f76c4bd84)
  - [e64383d](https://github.com/spring-projects/spring-batch/commit/e64383d8eeab77a5894657cfa2b343bffca54979)
  - [60bf5b4](https://github.com/spring-projects/spring-batch/commit/60bf5b42bb6bee89a180ad321397c09b1c3999dc)
  - [d983f71](https://github.com/spring-projects/spring-batch/commit/d983f71da9cf8fa014d5cb2657174a84e966c17c)
  - [cc2d57f](https://github.com/spring-projects/spring-batch/commit/cc2d57fde1cc603fc6d18defcc3eee1807e2adcd)

## 内容

**バグの説明**
[この変更](https://github.com/spring-projects/spring-batch/commit/90d895955d951156849ba6fa018676273fdbe2c4#diff-1ccc98868257080253b51baded74a755478f3f85f754e0dc8ef05144ecd7dc02)により、SimpleStepExecutionSplitter.java内でステップのコンテキストが永続化されなくなり、パーティショナーによって作成された実行コンテキストが失われ、リモートワーカーが作成されたコンテキストを読み込めなくなりました。具体的には、batch 6以前の`jobRepository.addAll`の呼び出しによってコンテキストが永続化されていました。

具体的には、コンテキストが作成された後、`MessageChannelPartitionHandler.doHandle`がメッセージの作成と送信を担当します。リモートワーカーがメッセージを受信すると、ジョブリポジトリを介してステップを読み込みます。

**環境**
Spring boot 4.0.0, batch 6.0.0, batch-integration 6.0.0, JDK21

**再現手順**

https://github.com/brian-mcnamara/SpringBatch6/blob/main/src/main/java/com/example/batchpartitionbug/BatchPartitionBugApplication.java を参照

(`./gradlew run`で実行可能) 特に、197行目のパーティショナーからコンテキストを取得する91行目に注目してください。

このバグは、配信にメッセージチャネルを使用し、jobRepositoryに永続化レイヤーを使用するパーティション化されたステップで確認されます。


**期待される動作**

パーティショナーはコントローラー上でステップコンテキストを初期化し、リポジトリ内のステップを更新するべきです。これにより、ワーカーがリポジトリからステップを読み込み、以前に作成されたコンテキストを使用できるようになります。


## コメント

### コメント 1 by quaff

**作成日**: 2025-12-08

Spring Boot 4.0へのアップグレード後、`@Value("#{stepExecutionContext['xxx']}")`がnullになり、アプリケーションの起動に失敗しました。

### コメント 2 by fmbenhassine

**作成日**: 2025-12-10

この課題を報告し、例を提供していただきありがとうございます! これは有効な課題です。リモートパーティショニングの[テスト](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/remote)に不足があるようです。確認します。今後の6.0.1リリースで修正を予定しています。

### コメント 3 by brian-mcnamara

**作成日**: 2025-12-10

お二人とも迅速な対応とすべてのご尽力に感謝します!

