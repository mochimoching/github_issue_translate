# 完了したジョブ実行に対するJobRepository.findRunningJobExecutionsでのEmptyResultDataAccessException

**Issue番号**: #5104

**状態**: closed | **作成者**: A1exL | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5104

**関連リンク**:
- Commits:
  - [5750492](https://github.com/spring-projects/spring-batch/commit/57504927d912947ad1d15079b00d0969060db664)

## 内容

**バグの説明**
指定されたジョブ名に対して実行中のジョブ実行がなく、BATCH_JOB_EXECUTIONテーブルにCOMPLETEDまたはFAILEDレコードのみが含まれている場合(BATCH_JOB_EXECUTION.STATUS列の値)、`JobRepository.findRunningJobExecutions`がEmptyResultDataAccessExceptionをスローします。

**環境**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25
- 組み込みH2データベース(すべてのデータベースで再現)

**再現手順**
前提条件:
JdbcJobExecutionDaoが使用されています。BATCH_JOB_EXECUTIONおよびBATCH_JOB_INSTANCEテーブルが空です。
"SuccessfulJob"という名前のSpring Batchジョブがあります。

1. このジョブを実行し、正常に完了するまで待ちます。
実行後、BATCH_JOB_INSTANCEテーブルに1件のレコードが作成されます。
また、BATCH_JOB_EXECUTIONテーブルにSTATUS=COMPLETEDのレコードが1件作成されます。
2. `org.springframework.batch.core.repository.JobRepository.findRunningJobExecutions("SuccessfulJob")`を呼び出します。

**期待される動作**
空のセットが返されます。

**実際の動作**
EmptyResultDataAccessExceptionがスローされます。


**課題の原因**
課題の根本原因は、`JdbcJobExecutionDao.findRunningJobExecutions`メソッドのコードです:
このコードフラグメント
`getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE), Long.class, jobInstanceId)`
は、指定されたjobInstanceIdに対してBATCH_JOB_EXECUTIONテーブルにCOMPLETED(またはFAILED)レコード**のみ**がある場合に失敗します。
`org.springframework.batch.core.repository.dao.jdbc.JdbcJobExecutionDao`のコード
```				
private static final String GET_RUNNING_EXECUTION_FOR_INSTANCE = """
		SELECT E.JOB_EXECUTION_ID
		FROM %PREFIX%JOB_EXECUTION E, %PREFIX%JOB_INSTANCE I
		WHERE E.JOB_INSTANCE_ID=I.JOB_INSTANCE_ID AND I.JOB_INSTANCE_ID=? AND E.STATUS IN ('STARTING', 'STARTED', 'STOPPING')
		""";
		

public Set<JobExecution> findRunningJobExecutions(String jobName) {
	final Set<JobExecution> result = new HashSet<>();
	List<Long> jobInstanceIds = this.jobInstanceDao.getJobInstanceIds(jobName);
	for (long jobInstanceId : jobInstanceIds) {

		// 何も見つからない場合、EmptyResultDataAccessExceptionをスロー
		long runningJobExecutionId = getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE),
				Long.class, jobInstanceId);

		JobExecution runningJobExecution = getJobExecution(runningJobExecutionId);
		result.add(runningJobExecution);
	}
	return result;
}
```

**最小限の再現可能な例**
https://github.com/A1exL/spring-batch6-bugs
`JobRepositoryTests`を起動して結果を確認してください。


## コメント

### コメント 1 by darckyn

**作成日**: 2025-11-26

こんにちは。

私も同じエラーが発生しています!
私のデータベースでは、BATCH_JOB_EXECUTION.STATUSがすべての行でCOMPLETEのみになっています。

環境

- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 21
- SqlServer 2019

ソースコードでは、スケジュール内で`findRunningJobExecutions`を使用しています:

    @Scheduled(cron = CronConst.EVERY_FIVE_SECONDS, zone = SystemConst.ZONE_DEFAULT)
    public void launchValidateGarantiaJob() throws JobExecutionAlreadyRunningException, JobInstanceAlreadyCompleteException,
            InvalidJobParametersException, JobRestartException {
        var runningJobs = jobRepository.findRunningJobExecutions(validateGarantiaJob.getName());
        if (EmptyUtil.isEmpty(runningJobs)) {
            jobOperator.start(validateGarantiaJob, JobUtil.createJobParameters());
        } else {
            throw new JobExecutionAlreadyRunningException(validateGarantiaJob.getName());
        }
    }

### コメント 2 by fmbenhassine

**作成日**: 2025-12-04

この課題の報告とサンプルの提供をありがとうございます! これは確かにバグです。今後のパッチリリースで修正を予定します。

