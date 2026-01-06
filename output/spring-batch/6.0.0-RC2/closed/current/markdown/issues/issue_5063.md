# MongoJobExecutionDao doesn't handle temporal job parameter types correctly

**Issue番号**: #5063

**状態**: closed | **作成者**: quaff | **作成日**: 2025-10-30

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5063

## 内容

`JobExecution` retrieved from MongoDB contains incorrect temporal job parameter:

```java
LocalDate localDateParameter = LocalDate.now();
JobParameters jobParameters = new JobParametersBuilder().addLocalDate("localDate", localDateParameter).toJobParameters();
JobExecution execution = dao.createJobExecution(jobInstance, jobParameters);
JobParameters persistedParameters = dao.getJobExecution(execution.getId()).getJobParameters();
System.out.println(persistedParameters.getLocalDate("localDate").getClass()); // -> java.util.Date instead of expected java.time.LocalDate
```

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-05

Resolved in f1cf52963e949f7bc59964859bcc115824cc62ae, many thanks @quaff for reporting the issue and contributing a fix!

