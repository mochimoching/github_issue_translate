# Improve JobOperator API by using domain types instead of primitive types

**Issue番号**: #4845

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-22

**ラベル**: in: core, type: enhancement, api: breaking-change, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4845

**関連リンク**:
- Commits:
  - [8dde852](https://github.com/spring-projects/spring-batch/commit/8dde8529d36b646b33a1711219a1b1e8a046345a)

## 内容

`JobOperator` is the main high-level API to operate batch jobs. However, it is currently designed as a low-level API by using primitive types in most method signatures. This makes implementations deal with concerns that should not addressed there in the first place.

For example, starting a job with `start(String jobName, Properties parameters)` requires finding a job from a `JobRegistry` and using a `JobParametersConverter` to convert properties to `JobParameters`. This design makes the implementation require two collaborators (`JobRegistry` and `JobParametersConverter`), which could have been avoided by using domain types in the method signature like `#start(Job job, JobParameters parameters)`.

Another example is `stop(long jobExecutionId)` which requires to find the job execution by id, from which get the job name, then get the job itself from the registry, to finally being able to stop the job. This can be avoided by using `stop(JobExecution jobExecution)` instead.

Parameters conversion, job retrieval and other concerns should be part of a low level APIs like `CommandLineJobLauncher` or `JmxConsoleAdapter`, but not `JobOperator`. Core domain APIs should be designed with domain types in method signatures.

