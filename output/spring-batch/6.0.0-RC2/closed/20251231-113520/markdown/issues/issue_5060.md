# Add support for delete operations in MongoDB DAOs

**Issue番号**: #5060

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-29

**ラベル**: type: feature, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5060

**関連リンク**:
- Commits:
  - [3079925](https://github.com/spring-projects/spring-batch/commit/3079925af8bb2c58563afb57a2c4e455327ac4bc)

## 内容

As of v5.2.4, 6.0.0-RC1, the following methods are not implemented in MongoDB DAOs:

- `org.springframework.batch.core.repository.dao.JobInstanceDao#deleteJobInstance`
- `org.springframework.batch.core.repository.dao.JobExecutionDao#deleteJobExecution`
- `org.springframework.batch.core.repository.dao.JobExecutionDao#deleteJobExecutionParameters`
- `org.springframework.batch.core.repository.dao.StepExecutionDao#deleteStepExecution`
- `org.springframework.batch.core.repository.dao.ExecutionContextDao#deleteExecutionContext(JobExecution)`
- `org.springframework.batch.core.repository.dao.ExecutionContextDao#deleteExecutionContext(StepExecution)`


