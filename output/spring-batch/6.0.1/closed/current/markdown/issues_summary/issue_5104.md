*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

`JobRepository.findRunningJobExecutions`メソッドが、特定の条件下で`EmptyResultDataAccessException`をスローするというバグです。

**発生条件**:
1. 指定したジョブ名のジョブ実行履歴が存在する
2. しかし、**実行中（STARTING, STARTED, STOPPING）**のジョブ実行は存在しない
3. 全ての履歴が**完了（COMPLETED, FAILED）**状態である

**期待される動作**:
- 実行中のジョブがない場合、例外ではなく空のセット（`Set<JobExecution>`）を返すべきです。

## 原因

`JdbcJobExecutionDao`の実装において、`queryForObject`の使用方法に問題があります。

```java
// 問題のコード
long runningJobExecutionId = getJdbcTemplate().queryForObject(
    getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE),
    Long.class, 
    jobInstanceId);
```

ループ内で各ジョブインスタンスに対して「実行中の実行ID」を問い合わせていますが、そのインスタンスに「実行中の実行」が存在しない（つまり完了している）場合、SQLクエリが結果を返さず、`EmptyResultDataAccessException`が発生します。

## 対応方針

クエリが結果を返さない場合（例外発生時）のハンドリングを追加し、例外をスローせずに処理を続行（空の結果として扱う）するように修正が必要です。
