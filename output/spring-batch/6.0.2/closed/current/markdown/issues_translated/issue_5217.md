*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# グレースフルシャットダウン時のレースコンディションによるOptimisticLockingFailureException

**Issue番号**: #5217

**状態**: closed | **作成者**: KMGeon | **作成日**: 2026-01-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5217

**関連リンク**:
- コミット:
  - [4034f26](https://github.com/spring-projects/spring-batch/commit/4034f269cb96c55ee1fd1a80666fb087d07b9526)
  - [7f742a5](https://github.com/spring-projects/spring-batch/commit/7f742a5933473e5a6768db583f78bf68aa942641)

## 内容

## バグの説明

`GracefulShutdownFunctionalTests.testStopJob`がレースコンディションにより断続的に失敗します（不安定なテスト）。

## 影響バージョン

- Spring Batch 6.0.1

## エラーメッセージ

```
OptimisticLockingFailureException: Attempt to update step execution id=0
with wrong version (1), where current version is 2
```

## 再現性

> **注意**: これは非常にまれな不安定テストです。私のローカル環境（Mac）では、約**100回に1回**の割合で発生しました。この問題はレースコンディションのためタイミングに非常に敏感であり、失敗率はCPU負荷やスレッドスケジューリングによって異なります。
>
> 役立つかもしれないと思い報告しています。**優先度が高くないと判断された場合は、このIssueをクローズしていただいて構いません** - まれに発生する不安定テストがすぐに対応を必要としない場合があることは十分理解しています。

## 失敗したビルドリンク

CI失敗:
- https://github.com/spring-projects/spring-batch/actions/runs/21092150808/job/60664875427

```
04:48:43.282 [batch-executor1] INFO  - Job: [SimpleJob: [name=job]] launched
04:48:43.293 [batch-executor1] INFO  - Executing step: [chunkOrientedStep]
04:48:44.343 [main] INFO  - Stopping job execution: status=STARTED
04:48:44.345 [main] INFO  - Upgrading job execution status from STOPPING to STOPPED

org.springframework.dao.OptimisticLockingFailureException:
Attempt to update step execution id=0 with wrong version (1), where current version is 2
    at JdbcStepExecutionDao.updateStepExecution(JdbcStepExecutionDao.java:254)
    at SimpleJobRepository.update(SimpleJobRepository.java:174)
    at SimpleJobOperator.stop(SimpleJobOperator.java:375)
    at GracefulShutdownFunctionalTests.testStopJob(GracefulShutdownFunctionalTests.java:80)
```

## 根本原因の分析

### 1. レースコンディションのシナリオ

```
[batch-executor1スレッド]              [mainスレッド]
          │                                 │
          │ チャンク処理中                   │
          │ update(stepExecution)           │
          │ バージョン: 1 → 2               │
          │                                 │
          │                                 │ stop()呼び出し
          │                                 │ バージョン1で更新を試行
          │                                 │ ❌ 失敗！（DBにはすでにバージョン2）
```

### 2. 根本原因

`SimpleJobRepository.update(StepExecution)`では、`isStopped()`のみがチェックされ、`isStopping()`はチェックされていません:

```java
// SimpleJobRepository.java - line 166
if (latestStepExecution.getJobExecution().isStopped()) {  // ← STOPPEDのみをチェック！
    stepExecution.setVersion(latestStepExecution.getVersion());
}
```

`stop()`が呼び出されると、`JobExecution`のステータスは`STOPPING`に変わりますが、`isStopped()`は`STOPPED`ステータスの場合のみ`true`を返します。したがって、`STOPPING`状態ではバージョン同期が行われません。

## 修正案

```java
// SimpleJobRepository.java - line 166

// 修正前
if (latestStepExecution.getJobExecution().isStopped()) {

// 修正後
if (latestStepExecution.getJobExecution().isStopped()
    || latestStepExecution.getJobExecution().isStopping()) {
```

`isStopping()`チェックを追加することで、`STOPPING`状態でもバージョン同期が行われ、レースコンディションを防止できます。

## 関連コード

- `SimpleJobRepository.update(StepExecution)`
- `SimpleJobOperator.stop()`
- `JdbcStepExecutionDao.updateStepExecution()`

---

## 最後に

上記の通り、これは一貫して再現することが困難な非常にまれな問題です。有用な情報を提供できるかもしれないと思い報告しましたが、優先度が低い、または「修正しない」としてクローズされても十分に理解しています。レビューにお時間をいただきありがとうございます！

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-19

この問題を報告し、修正を提供していただきありがとうございます！

実際、その不安定なテストについては認識していましたが、レースコンディションを追跡する時間がまだありませんでした。そのため、それを行っていただき大変感謝しています。6.0.2で修正を計画します。
