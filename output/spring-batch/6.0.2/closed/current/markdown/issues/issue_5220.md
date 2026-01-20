# MongoStepExecutionDao.countStepExecutions() ignores stepName parameter

**Issue番号**: #5220

**状態**: closed | **作成者**: KMGeon | **作成日**: 2026-01-18

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5220

**関連リンク**:
- Commits:
  - [b0105f8](https://github.com/spring-projects/spring-batch/commit/b0105f8fd027aebf7a4e2afa29d1b249aa979794)
  - [fe421d0](https://github.com/spring-projects/spring-batch/commit/fe421d0dced93f8a05f5b09be8493f957fa2a0b7)

## 内容

## Bug Description

`MongoStepExecutionDao.countStepExecutions(JobInstance jobInstance, String stepName)` does not use the `stepName` parameter in the query.

- **Current behavior**: Returns count of all StepExecutions for the JobInstance
- **Expected behavior**: Returns count of StepExecutions filtered by `stepName`

## Affected Code

```java
// MongoStepExecutionDao.java (Line 165-177)
@Override
public long countStepExecutions(JobInstance jobInstance, String stepName) {
    Query query = query(where("jobInstanceId").is(jobInstance.getId()));
    List jobExecutions = this.mongoOperations.find(...);
    return this.mongoOperations.count(
            query(where("jobExecutionId").in(jobExecutions.stream()
                .map(JobExecution::getJobExecutionId)
                .toList())),  // stepName parameter is ignored
            StepExecution.class, STEP_EXECUTIONS_COLLECTION_NAME);
}
```

## Comparison with JdbcStepExecutionDao

`JdbcStepExecutionDao` correctly filters by `stepName`:

```sql
-- JdbcStepExecutionDao.java (Line 106-111)
SELECT COUNT(*)
FROM BATCH_JOB_EXECUTION JE
    JOIN BATCH_STEP_EXECUTION SE ON SE.JOB_EXECUTION_ID = JE.JOB_EXECUTION_ID
WHERE JE.JOB_INSTANCE_ID = ? AND SE.STEP_NAME = ?
```

## Impact

This bug affects `startLimit` functionality. `SimpleStepHandler.shouldStart()` calls `countStepExecutions()` to validate `startLimit`:

```java
// SimpleStepHandler.java (Line 205-221)
long stepExecutionCount = jobRepository.getStepExecutionCount(jobInstance, step.getName());
if (stepExecutionCount < step.getStartLimit()) {
    return true;
} else {
    throw new StartLimitExceededException(...);
}
```

**Example:**

| Step  | Actual Executions | startLimit | Bug Returns     | Result                                    |
|-------|-------------------|------------|-----------------|-------------------------------------------|
| stepA | 2                 | 3          | 7 (total count) | `StartLimitExceededException` (incorrect) |
| stepB | 5                 | 10         | 7 (total count) | Pass (accidentally correct)               |

## Test to Reproduce

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
    assertEquals(2, countA);  // Bug: returns 4
    assertEquals(1, countB);  // Bug: returns 4
    assertEquals(1, countC);  // Bug: returns 4
    assertEquals(0, countNonExistent);  // Bug: returns 4
}
```

## Suggested Fix

Add `.and("name").is(stepName)` to the query:

```java
return this.mongoOperations.count(
        query(where("jobExecutionId").in(jobExecutions.stream()
            .map(JobExecution::getJobExecutionId)
            .toList())
            .and("name").is(stepName)),  // Added stepName filter
        StepExecution.class, STEP_EXECUTIONS_COLLECTION_NAME);
```

---

## Additional Note

While investigating this issue, I noticed that there seem to be several areas where the MongoDB implementation is not fully synchronized with the JDBC implementation. For example:

- Optimistic locking behavior
- Other DAO method implementations

Would it be helpful if I do a broader review of the MongoDB module to identify other inconsistencies with the JDBC implementation? I'd be happy to contribute fixes for any issues found.

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-19

Thank you for reporting this issue and for providing a fix! This seems like a regression from ddbb6174c522999fc697a1603ac4e2c69a676a49 (the step name is used in 5.2.x).

I will plan the fix in 6.0.2

