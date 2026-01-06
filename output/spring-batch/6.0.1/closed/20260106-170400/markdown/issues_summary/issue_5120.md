*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5120: JobOperator.stop()呼び出し中に楽観的ロック失敗が発生する

## 課題概要

`JobOperator.stop()`を呼び出してジョブを停止しようとすると、`OptimisticLockingFailureException`（楽観的ロックの失敗）が発生してジョブを停止できない問題です。

### 用語解説

- **楽観的ロック**: データベースで同時更新を制御する仕組み。レコードにバージョン番号を持たせ、更新時にバージョンが一致しない場合は他のプロセスが更新したと判断してエラーにする
- **JobExecution.version**: ジョブ実行の楽観的ロック用バージョン番号。更新のたびにインクリメントされる
- **StepExecution.version**: ステップ実行の楽観的ロック用バージョン番号

### 問題のシナリオ

以下のような状況で問題が発生します：

```java
// ジョブを起動
Long executionId = jobOperator.start("myJob", parameters);

// 別スレッドでジョブを停止しようとする
jobOperator.stop(executionId);

// 例外が発生:
// OptimisticLockingFailureException: 
// Attempt to update step execution id=1 with wrong version (2), where current version is 3
```

### 詳細なエラーメッセージ

```
org.springframework.dao.OptimisticLockingFailureException: 
  Attempt to update step execution id=1 with wrong version (2), where current version is 3
```

このエラーは、「バージョン2でステップ実行を更新しようとしたが、データベースの現在のバージョンは既に3になっている」という意味です。

## 原因

`JobOperator.stop()`とジョブの実行処理が並行して動作するため、ジョブ実行オブジェクトのバージョン番号が非同期に更新され、`stop()`が保持している古いバージョン番号で更新しようとして失敗していました。

### 詳細な原因

#### 1. 並行処理の流れ

```
【時系列】
T1: ジョブ実行開始 (version=1)
T2: ステップ1実行中 → version=2に更新
T3: JobOperator.stop()呼び出し
    - この時点でのJobExecutionを取得 (version=2)
T4: ステップ1完了 → version=3に更新（バックグラウンドで）
T5: stop()がJobExecutionを更新しようとする
    - 保持しているversion=2で更新を試みる
    - データベースのversionは既に3
    - OptimisticLockingFailureException発生
```

#### 2. 問題のコード構造

```java
// SimpleJobOperator.stop()（問題のあった実装イメージ）
public void stop(long executionId) {
    // T3: この時点でのJobExecutionを取得
    JobExecution jobExecution = getJobExecution(executionId);
    // jobExecution.version = 2
    
    jobExecution.setStatus(BatchStatus.STOPPING);
    
    // T5: 更新を試みる
    // しかし、バックグラウンドでversionが3に更新されている
    jobRepository.update(jobExecution);  // ❌ version=2で更新しようとして失敗
}
```

#### 3. バージョン更新のタイミング

```
【JobExecutionのバージョン更新】
起動: version=1
  ↓
ステップ1開始: version=2 に更新
  ↓
ステップ1完了: version=3 に更新  ← stop()と並行して実行される
  ↓
ステップ2開始: version=4 に更新
```

`stop()`メソッドが呼ばれた時点（T3）のバージョンと、実際に更新しようとする時点（T5）のバージョンが異なってしまいます。

### 選択肢の検討

開発チームは以下の2つの選択肢を検討しました：

#### 選択肢1: stop()メソッド内でversionをnullに設定

```java
public void stop(long executionId) {
    JobExecution jobExecution = getJobExecution(executionId);
    jobExecution.setVersion(null);  // versionをnullに
    jobExecution.setStatus(BatchStatus.STOPPING);
    jobRepository.update(jobExecution);
}
```

**利点**: 
- 他のコア実行フローに影響しない
- stop()メソッドだけの変更で済む

**欠点**:
- 他のメソッドも同じ問題に直面する可能性がある

#### 選択肢2: コア実行ロジック全体を変更

毎回最新のバージョンをデータベースから取得してから更新する。

**利点**:
- すべてのジョブ実行操作でバージョンが正しく管理される

**欠点**:
- 各ステップ実行ごとにデータベース問い合わせが増える
- パフォーマンスへの影響

**採用された選択肢**: 選択肢1（stop()メソッド内でversionをnullに設定）

## 対応方針

`stop()`メソッド内でジョブ実行のバージョンを`null`に設定することで、楽観的ロックチェックをスキップし、常に最新のバージョン番号で更新するように修正されました。

### 修正内容

[コミット 9bcc1e9](https://github.com/spring-projects/spring-batch/commit/9bcc1e9f7e1adb5aaec36d91b3d2b1cf0ca8c0a3)

```java
// SimpleJobOperator.stop()（修正後）
public void stop(long executionId) {
    JobExecution jobExecution = getJobExecution(executionId);
    
    // ✅ 修正: versionをnullに設定
    jobExecution.setVersion(null);
    
    jobExecution.setStatus(BatchStatus.STOPPING);
    jobRepository.update(jobExecution);
}
```

#### JdbcJobExecutionDaoでのversion=nullの扱い

```java
// JdbcJobExecutionDao.synchronizeStatus()
public void synchronizeStatus(JobExecution jobExecution) {
    if (jobExecution.getVersion() == null) {
        // versionがnullの場合: バージョンチェックなしで更新
        jdbcTemplate.update(UPDATE_JOB_EXECUTION_STATUS_ONLY,
            jobExecution.getStatus().toString(),
            Timestamp.from(jobExecution.getLastUpdated()),
            jobExecution.getId());
    } else {
        // versionがある場合: 通常の楽観的ロックで更新
        jdbcTemplate.update(UPDATE_JOB_EXECUTION,
            // ... version付きの更新
        );
    }
}
```

使用されるSQLクエリ：

```sql
-- version=nullの場合（バージョンチェックなし）
UPDATE BATCH_JOB_EXECUTION 
SET STATUS = ?, LAST_UPDATED = ?
WHERE JOB_EXECUTION_ID = ?

-- version指定の場合（バージョンチェックあり）
UPDATE BATCH_JOB_EXECUTION 
SET STATUS = ?, LAST_UPDATED = ?, VERSION = VERSION + 1
WHERE JOB_EXECUTION_ID = ? AND VERSION = ?
```

### 修正のポイント

| 項目 | 修正前 | 修正後 |
|-----|-------|-------|
| version値 | 取得時のバージョン番号 | `null` |
| 更新SQL | `WHERE VERSION = ?`付き | `WHERE VERSION = ?`なし |
| 楽観的ロックチェック | あり | なし |
| 更新の成功率 | 並行処理で失敗する可能性あり | 常に成功 |

### 修正後の動作

```
【時系列】
T1: ジョブ実行開始 (version=1)
T2: ステップ1実行中 → version=2に更新
T3: JobOperator.stop()呼び出し
    - JobExecutionを取得
    - version=nullに設定 ✅
T4: ステップ1完了 → version=3に更新（バックグラウンドで）
T5: stop()がJobExecutionを更新
    - version=nullなのでバージョンチェックなし ✅
    - 現在のversionに関係なく更新成功 ✅
```

結果：
```
✅ OptimisticLockingFailureException は発生しない
✅ ジョブは正常に停止される
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `SimpleJobOperator` - ジョブ操作の実装
  - `JdbcJobExecutionDao` - ジョブ実行のJDBCアクセス
  - `JobExecution` - ジョブ実行情報を保持
  - `SimpleJobRepository` - ジョブリポジトリの実装
- **関連する概念**:
  - 楽観的ロック (Optimistic Locking)
  - 並行処理制御
  - データベーストランザクション
- **影響範囲**: 実行中のジョブを`JobOperator.stop()`で停止しようとするすべてのケース
- **関連課題**: [#5114](https://github.com/spring-projects/spring-batch/issues/5114) - stop()の動作に関する別の問題
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5120
