*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# MongoStepExecutionDao.countStepExecutions()がstepNameパラメータを無視する

**Issue番号**: #5220

**状態**: closed | **作成者**: KMGeon | **作成日**: 2026-01-18

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5220

**関連リンク**:
- コミット:
  - [b0105f8](https://github.com/spring-projects/spring-batch/commit/b0105f8fd027aebf7a4e2afa29d1b249aa979794)
  - [fe421d0](https://github.com/spring-projects/spring-batch/commit/fe421d0dced93f8a05f5b09be8493f957fa2a0b7)

## 内容

## バグの説明

`MongoStepExecutionDao.countStepExecutions(JobInstance jobInstance, String stepName)`がクエリで`stepName`パラメータを使用していません。

- **現在の動作**: JobInstanceのすべてのStepExecutionのカウントを返す
- **期待される動作**: `stepName`でフィルタリングされたStepExecutionのカウントを返す

## 影響を受けるコード

```java
// MongoStepExecutionDao.java (Line 165-177)
@Override
public long countStepExecutions(JobInstance jobInstance, String stepName) {
    Query query = query(where("jobInstanceId").is(jobInstance.getId()));
    List jobExecutions = this.mongoOperations.find(...);
    return this.mongoOperations.count(
            query(where("jobExecutionId").in(jobExecutions.stream()
                .map(JobExecution::getJobExecutionId)
                .toList())),  // stepNameパラメータが無視されている
            StepExecution.class, STEP_EXECUTIONS_COLLECTION_NAME);
}
```

## JdbcStepExecutionDaoとの比較

`JdbcStepExecutionDao`は正しく`stepName`でフィルタリングしています:

```sql
-- JdbcStepExecutionDao.java (Line 106-111)
SELECT COUNT(*)
FROM BATCH_JOB_EXECUTION JE
    JOIN BATCH_STEP_EXECUTION SE ON SE.JOB_EXECUTION_ID = JE.JOB_EXECUTION_ID
WHERE JE.JOB_INSTANCE_ID = ? AND SE.STEP_NAME = ?
```

## 影響

このバグは`startLimit`機能に影響します。`SimpleStepHandler.shouldStart()`は`startLimit`を検証するために`countStepExecutions()`を呼び出します:

```java
// SimpleStepHandler.java (Line 205-221)
long stepExecutionCount = jobRepository.getStepExecutionCount(jobInstance, step.getName());
if (stepExecutionCount < step.getStartLimit()) {
    return true;
} else {
    throw new StartLimitExceededException(...);
}
```

**例:**

| Step  | 実際の実行回数 | startLimit | バグが返す値    | 結果                                      |
|-------|----------------|------------|-----------------|-------------------------------------------|
| stepA | 2              | 3          | 7（合計カウント）| `StartLimitExceededException`（不正確）    |
| stepB | 5              | 10         | 7（合計カウント）| パス（偶然正しい）                         |

## 再現用テスト

```java
@Test
void testCountStepExecutionsFiltersByStepName() {
    // given
    dao.createStepExecution("stepA", jobExecution);
    dao.createStepExecution("stepA", jobExecution);
    dao.createStepExecution("stepB", jobExecution);
    dao.createStepExecution("stepC", jobExecution);

    // when
    long countA = dao.countStepExecutions(jobInstance, "stepA");
    long countB = dao.countStepExecutions(jobInstance, "stepB");
    long countC = dao.countStepExecutions(jobInstance, "stepC");
    long countNonExistent = dao.countStepExecutions(jobInstance, "nonExistentStep");

    // then
    assertEquals(2, countA);  // バグ: 4を返す
    assertEquals(1, countB);  // バグ: 4を返す
    assertEquals(1, countC);  // バグ: 4を返す
    assertEquals(0, countNonExistent);  // バグ: 4を返す
}
```

## 修正案

クエリに`.and("name").is(stepName)`を追加:

```java
return this.mongoOperations.count(
        query(where("jobExecutionId").in(jobExecutions.stream()
            .map(JobExecution::getJobExecutionId)
            .toList())
            .and("name").is(stepName)),  // stepNameフィルタを追加
        StepExecution.class, STEP_EXECUTIONS_COLLECTION_NAME);
```

---

## 追加メモ

この問題を調査中に、MongoDB実装がJDBC実装と完全に同期していない箇所がいくつかあるようです。例えば:

- 楽観的ロックの動作
- 他のDAOメソッドの実装

MongoDBモジュールのより広範なレビューを行い、JDBC実装との他の不整合を特定することは役立つでしょうか？発見された問題の修正に貢献できれば嬉しいです。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-19

この問題を報告し、修正を提供していただきありがとうございます！これはddbb6174c522999fc697a1603ac4e2c69a676a49からのリグレッションのようです（5.2.xではstep nameが使用されています）。

6.0.2で修正を計画します。
