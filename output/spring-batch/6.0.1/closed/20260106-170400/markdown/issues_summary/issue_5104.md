*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5104: findRunningJobExecutionsがEmptyResultDataAccessExceptionをスローする

## 課題概要

Spring Batchで実行中のジョブを検索する`JobRepository.findRunningJobExecutions()`メソッドを呼び出した際、実行中のジョブが存在しない場合に空のセットを返すべきところ、`EmptyResultDataAccessException`（データが見つからない例外）をスローしてしまう問題です。

### 用語解説

- **JobRepository**: Spring Batchのジョブ実行情報を管理するリポジトリ。データベースにジョブの実行状態などを保存・取得する
- **BATCH_JOB_EXECUTION テーブル**: ジョブ実行の履歴を記録するデータベーステーブル。`STATUS`列には`STARTING`, `STARTED`, `STOPPING`, `COMPLETED`, `FAILED`などの状態が保存される

### 問題のシナリオ

以下の状況で例外が発生します：

1. "SuccessfulJob"という名前のジョブを実行し、正常に完了する
2. データベースには以下の状態が記録される：
   - `BATCH_JOB_INSTANCE`: 1件のレコード
   - `BATCH_JOB_EXECUTION`: `STATUS='COMPLETED'`のレコードが1件
3. `jobRepository.findRunningJobExecutions("SuccessfulJob")`を呼び出す
4. **期待される動作**: 実行中のジョブがないため、空のセット`{}`が返される
5. **実際の動作**: `EmptyResultDataAccessException`がスローされる

### 実用例での影響

スケジューラーなどで定期的にジョブの実行状態をチェックする際に問題になります：

```java
@Scheduled(cron = "*/5 * * * * *")  // 5秒ごとに実行
public void launchJob() {
    var runningJobs = jobRepository.findRunningJobExecutions("myJob");
    if (runningJobs.isEmpty()) {
        jobOperator.start("myJob", parameters);  // ジョブを起動
    } else {
        throw new JobExecutionAlreadyRunningException("myJob");
    }
}
```

このコードは、実行中のジョブがない時に例外が発生してしまい、正常に動作しません。

## 原因

`JdbcJobExecutionDao.findRunningJobExecutions()`メソッド内のSQLクエリ実行に問題がありました。

### 詳細な原因

```java
// JdbcJobExecutionDao.java
private static final String GET_RUNNING_EXECUTION_FOR_INSTANCE = """
    SELECT E.JOB_EXECUTION_ID
    FROM %PREFIX%JOB_EXECUTION E, %PREFIX%JOB_INSTANCE I
    WHERE E.JOB_INSTANCE_ID=I.JOB_INSTANCE_ID 
      AND I.JOB_INSTANCE_ID=? 
      AND E.STATUS IN ('STARTING', 'STARTED', 'STOPPING')
    """;

public Set<JobExecution> findRunningJobExecutions(String jobName) {
    final Set<JobExecution> result = new HashSet<>();
    List<Long> jobInstanceIds = this.jobInstanceDao.getJobInstanceIds(jobName);
    
    for (long jobInstanceId : jobInstanceIds) {
        // 問題のコード: queryForObject()は結果が0件の時に例外をスローする
        long runningJobExecutionId = getJdbcTemplate()
            .queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE), 
                           Long.class, jobInstanceId);
        
        JobExecution runningJobExecution = getJobExecution(runningJobExecutionId);
        result.add(runningJobExecution);
    }
    return result;
}
```

### 問題のポイント

1. **queryForObject()の仕様**: このメソッドは必ず1件の結果を期待する
   - 結果が0件の場合 → `EmptyResultDataAccessException`をスローする
   - 結果が2件以上の場合 → `IncorrectResultSizeDataAccessException`をスローする

2. **実行中ジョブがない場合のSQL結果**:
   ```sql
   -- STATUS='COMPLETED'のレコードしかない場合
   SELECT E.JOB_EXECUTION_ID ... AND E.STATUS IN ('STARTING', 'STARTED', 'STOPPING')
   -- → 結果0件 → queryForObject()が例外をスロー
   ```

3. **本来の意図**: 実行中のジョブがない場合は空のセットを返すべき

## 対応方針

`queryForObject()`の代わりに、結果が0件でも例外をスローしない`query()`メソッドを使用するように修正されました。

### 修正内容

[コミット 5750492](https://github.com/spring-projects/spring-batch/commit/57504927d912947ad1d15079b00d0969060db664)

```java
// 修正後のコード（イメージ）
public Set<JobExecution> findRunningJobExecutions(String jobName) {
    final Set<JobExecution> result = new HashSet<>();
    List<Long> jobInstanceIds = this.jobInstanceDao.getJobInstanceIds(jobName);
    
    for (long jobInstanceId : jobInstanceIds) {
        // query()を使用：結果が0件の場合は空のListを返す
        List<Long> runningJobExecutionIds = getJdbcTemplate()
            .query(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE),
                  (rs, rowNum) -> rs.getLong("JOB_EXECUTION_ID"),
                  jobInstanceId);
        
        // 結果がある場合のみJobExecutionを取得
        for (long executionId : runningJobExecutionIds) {
            JobExecution runningJobExecution = getJobExecution(executionId);
            result.add(runningJobExecution);
        }
    }
    return result;
}
```

### 修正のポイント

| 項目 | 修正前 | 修正後 |
|-----|-------|-------|
| メソッド | `queryForObject()` | `query()` |
| 結果が0件の場合 | 例外をスロー | 空のListを返す |
| 結果が複数件の場合 | 例外をスロー | すべての結果を返す |

### 修正後の動作

```java
// 実行中のジョブがない場合
var runningJobs = jobRepository.findRunningJobExecutions("SuccessfulJob");
// → 空のSet {} が返される（例外は発生しない）

// 実行中のジョブがある場合
var runningJobs = jobRepository.findRunningJobExecutions("RunningJob");
// → 実行中のJobExecutionのSetが返される
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `JdbcJobExecutionDao` - JDBC経由でジョブ実行情報にアクセスするDAO
  - `JdbcTemplate` - SpringのJDBCテンプレートクラス
- **影響するデータベース**: すべてのデータベース（H2、MySQL、PostgreSQL、SQL Serverなど）
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5104
