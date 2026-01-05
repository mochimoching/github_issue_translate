# ジョブリポジトリからステップ実行を照会した際にExecutionContextが読み込まれない

**Issue番号**: #5117

**状態**: closed | **作成者**: ruudkenter | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5117

## 内容

Spring Batch 5.2.xでは、SimpleJobExplorerから返される`StepExecution`には、`ExecutionContext`を含む完全に設定された`StepExecution`が含まれていました。

Spring Batch 6.0.0では、同じタスク[StepExecutionの取得](https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-integration/src/main/java/org/springframework/batch/integration/partition/StepExecutionRequestHandler.java#L48)に`JobRepository`を使用していますが、`StepExecution`の`ExecutionContext`を設定していないようです。最終的には[JdbcStepExecutionDao](https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/dao/jdbc/JdbcStepExecutionDao.java#L299)に委譲されますが、BATCH_STEP_EXECUTION_CONTEXTテーブルから`ExecutionContext`を読み込みません。これにより、リモートパーティション化されたバッチジョブが失敗します。

これが意図的なものなのか、私が何か見落としているのか分かりませんが、私にはこれは課題のように思えます。

[課題のデモンストレーション](https://github.com/ruudkenter/spring-batch-6-demo)。

注: ResourcelessJobRepositoryの使用に切り替えると動作します。

よろしくお願いします
Ruud

## コメント

### コメント 1 by ruudkenter

**作成日**: 2025-12-09

課題は(https://github.com/spring-projects/spring-batch/pull/5147)によって解決されました。

### コメント 2 by fmbenhassine

**作成日**: 2025-12-10

この有効な課題を報告していただき、ありがとうございます! 確かに、課題 [#5147](https://github.com/spring-projects/spring-batch/pull/5147) がこれを解決し、マージされました。

修正は来週予定されている6.0.1に含まれる予定です。

