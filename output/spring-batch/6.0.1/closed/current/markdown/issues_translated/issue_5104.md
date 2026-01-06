*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# 完了したジョブ実行に対してJobRepository.findRunningJobExecutionsがEmptyResultDataAccessExceptionをスローする

**課題番号**: #5104

**状態**: closed | **作成者**: A1exL | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5104

**関連リンク**:
- Commits:
  - [5750492](https://github.com/spring-projects/spring-batch/commit/57504927d912947ad1d15079b00d0969060db664)

## 内容

**バグの説明**
`JobRepository.findRunningJobExecutions`は、指定されたジョブ名に対して実行中のジョブ実行がなく、`BATCH_JOB_EXECUTION`テーブルに`COMPLETED`または`FAILED`のレコードのみが含まれている場合（`BATCH_JOB_EXECUTION.STATUS`列の値）、`EmptyResultDataAccessException`をスローします。

**環境**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25
- 組み込みH2データベース（すべてのデータベースで再現可能）

**再現手順**
前提条件：
`JdbcJobExecutionDao`が使用されています。`BATCH_JOB_EXECUTION`および`BATCH_JOB_INSTANCE`テーブルは空です。
"SuccessfulJob"という名前のSpring Batchジョブがあります。

1. このジョブを実行し、正常に完了するまで待ちます。
実行後、`BATCH_JOB_INSTANCE`テーブルに1つのレコードが作成されます。
また、`BATCH_JOB_EXECUTION`テーブルに`STATUS=COMPLETED`のレコードが1つ作成されます。
2. `org.springframework.batch.core.repository.JobRepository.findRunningJobExecutions("SuccessfulJob")`を呼び出します

**期待される動作**
空のセットが返されます。

**実際の動作**
`EmptyResultDataAccessException`がスローされます。


**課題の原因**
根本原因は、`JdbcJobExecutionDao.findRunningJobExecutions`メソッド内のコードです：
このコード断片
`getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE), Long.class, jobInstanceId)`
は、指定された`jobInstanceId`に対して`BATCH_JOB_EXECUTION`テーブルに**完了**（または失敗）レコード**のみ**がある場合に失敗します。
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

		// 何も見つからない場合はEmptyResultDataAccessExceptionをスローする
		long runningJobExecutionId = getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE),
				Long.class, jobInstanceId);

		JobExecution runningJobExecution = getJobExecution(runningJobExecutionId);
		result.add(runningJobExecution);
	}
	return result;
}
```

**最小限の再現例**
https://github.com/A1exL/spring-batch6-bugs
`JobRepositoryTests`を実行して結果を確認してください


## コメント

### コメント 1 by darckyn

**作成日**: 2025-11-26

こんにちは。

同じエラーがここでも発生しています！
私のデータベースでは、`BATCH_JOB_EXECUTION.STATUS`のすべての行がCOMPLETEのみです

環境

- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 21
- SqlServer 2019

ソースコードでは、スケジュール内で`findRunningJobExecutions`を使用しています：

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

この課題を報告し、サンプルを提供していただきありがとうございます！確かにこれはバグです。次のパッチリリースで修正を予定します。

