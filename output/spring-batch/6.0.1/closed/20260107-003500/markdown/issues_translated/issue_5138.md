*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# パーティショナーが生成したステップ実行がメタデータストアに永続化されない

**課題番号**: #5138

**状態**: closed | **作成者**: A1exL | **作成日**: 2025-12-02

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5138

**関連リンク**:
- Commits:
  - [25f1f81](https://github.com/spring-projects/spring-batch/commit/25f1f8156a8ed86c6dcaf9c39b2046e1ef9cf9e6)

## 内容

**バグの説明**
`PartitionStep`が`Partitioner`を使用してパーティションを生成しますが、`PartitionHandler`（例：`TaskExecutorPartitionHandler`）によって実際に処理される前に、それらのステップ実行がメタデータストアに保存されません。ただし、`PartitionStep`がこのステップ実行を保存する責任を持っていないことも理解しています。それはパーティションハンドラーの責任です。

その結果、メタデータストアに保存されるステップ実行の`RowMapper`が、`Partitioner`によって提供された入力パラメータ（`StepExecution.ExecutionContext`）を欠いた不完全なデータを持つことになります。

**環境**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25
- 組み込みH2データベース

**再現手順**
1. `Partitioner`を持つ`PartitionStep`を含むジョブを作成します
2. ジョブを実行します
3. デバッガーで、`TaskExecutorPartitionHandler.handle()`メソッドが（新しいスレッドで）呼び出される前に、`PartitionStep.doExecute()`メソッドによって`JdbcStepExecutionDao.saveStepExecution(StepExecution stepExecution)`が呼び出されることを確認できます

**期待される動作**
`Partitioner`によって提供された入力パラメータはメタデータストアに永続化されるべきです。

**実際の動作**
`JdbcStepExecutionDao`の`saveStepExecution(StepExecution stepExecution)`メソッドは、パーティション実行が`PartitionHandler`に渡される前に呼び出されます。つまり、`TaskExecutorPartitionHandler`のケースでは、`JdbcStepExecutionDao.saveStepExecution(StepExecution stepExecution)`がこのステップ実行の`RowMapper`を作成します。しかし、その時点では、`Partitioner`によって提供された入力パラメータはまだ`StepExecution`に設定されていません。

**最小限の再現例**
https://github.com/A1exL/spring-batch6-bugs (branch: reproduce_partition_step_issue)

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-04

この課題を報告し、サンプルを提供していただきありがとうございます！確かにバグですね。次のパッチリリースで修正します。

