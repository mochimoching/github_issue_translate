*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

`JobOperator.stop()`を使用してジョブを停止しようとすると、`OptimisticLockingFailureException`（楽観的ロックの失敗）が発生することがある問題です。

**発生メカニズム**:
1. ユーザーが`stop()`を呼び出す
2. 非同期にジョブの状態更新（STATUS=STOPPINGなど）が行われ、DB上のバージョン番号が増加する
3. その直後、`stop()`処理の中で`jobRepository.update()`またはそれに類する更新処理が、**古いバージョン番号**を持ったジョブ実行オブジェクトで行われる
4. DB上のバージョンと一致せず、楽観的ロック例外が発生

## 原因

`SimpleJobOperator`の`stop()`メソッドなどの処理フローにおいて、停止処理を行うスレッドと、ジョブを実行中のスレッドが競合し、手元のジョブ実行オブジェクトの状態（バージョン）がDBの最新状態と同期されていないためです。

## 対応方針

**選択されたアプローチ**:
`SimpleJobOperator.stop(executionId)`メソッド内で、保存・更新を行う前にジョブ実行オブジェクトの`version`を`null`に設定します。

- `version`を`null`にすると、`JdbcJobExecutionDao`はバージョンチェックを行わずにステータスのみを更新するSQLを発行します。
- これにより、他のスレッドによる更新（バージョンアップ）があっても、強制的にステータス更新を成功させ、ロック例外を回避します。

```java
// コンセプトイメージ
jobExecution.setVersion(null); 
jobRepository.update(jobExecution); // バージョンチェックなしで更新
```
