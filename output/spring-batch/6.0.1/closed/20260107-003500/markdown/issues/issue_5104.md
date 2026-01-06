# EmptyResultDataAccessException in JobRepository.findRunningJobExecutions for a completed job execution

**Issue番号**: #5104

**状態**: closed | **作成者**: A1exL | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5104

**関連リンク**:
- Commits:
  - [5750492](https://github.com/spring-projects/spring-batch/commit/57504927d912947ad1d15079b00d0969060db664)

## 内容

**Bug description**
`JobRepository.findRunningJobExecutions` throws an EmptyResultDataAccessException if there are no running job executions for a given job name and BATCH_JOB_EXECUTION table contains only COMPLETED or FAILED records (BATCH_JOB_EXECUTION.STATUS column value).

**Environment**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25
- Embedded H2 database (reproduces on any database)

**Steps to reproduce**
Preconditions:
JdbcJobExecutionDao is used. BATCH_JOB_EXECUTION and BATCH_JOB_INSTANCE tables are empty.
Have Spring Batch Job with name "SuccessfulJob".

1. Run this job, wait until it completes successfully.
After execution one record in BATCH_JOB_INSTANCE table will be created.
Also one record with STATUS=COMPLETED will be created in BATCH_JOB_EXECUTION table.
2. call `org.springframework.batch.core.repository.JobRepository.findRunningJobExecutions("SuccessfulJob")`

**Expected behavior**
An empty set is returned.

**Actual behavior**
An EmptyResultDataAccessException is thrown.


**Cause of the issue**
Root cause of the issue is the code in `JdbcJobExecutionDao.findRunningJobExecutions` method:
This code fragment
`getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE), Long.class, jobInstanceId)`
fails if there are **only** COMPLETED (or FAILED) records in BATCH_JOB_EXECUTION table for a given jobInstanceId
Code in `org.springframework.batch.core.repository.dao.jdbc.JdbcJobExecutionDao`
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

		// throws EmptyResultDataAccessException if nothing is found
		long runningJobExecutionId = getJdbcTemplate().queryForObject(getQuery(GET_RUNNING_EXECUTION_FOR_INSTANCE),
				Long.class, jobInstanceId);

		JobExecution runningJobExecution = getJobExecution(runningJobExecutionId);
		result.add(runningJobExecution);
	}
	return result;
}
```

**Minimal Complete Reproducible example**
https://github.com/A1exL/spring-batch6-bugs
Please launch `JobRepositoryTests` and see the results


## コメント

### コメント 1 by darckyn

**作成日**: 2025-11-26

Hi.

Same error here!
My database has BATCH_JOB_EXECUTION.STATUS with only COMPLETE in all lines

Environment

- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 21
- SqlServer 2019

In my source code, I use `findRunningJobExecutions` inside a Scheduled:

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

Thank you for reporting this issue and for providing a sample! Indeed this is a bug. I will plan the fix for the upcoming patch release.

