# Incorrect warning when starting a job with an empty parameters set

**Issue番号**: #4914

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-18

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4914

**関連リンク**:
- Commits:
  - [980ff7b](https://github.com/spring-projects/spring-batch/commit/980ff7b8d72bba7f8cfa0aa62fc057bc27a4aba0)
  - [e2dcee1](https://github.com/spring-projects/spring-batch/commit/e2dcee113dfe78627e1adbf12dfe2a91e89f306c)

## 内容

After the introduction of #4910 , starting a job having an incrementer with an empty set of parameters results into an unnecessary  warning:

```
[main] WARN org.springframework.batch.core.launch.support.TaskExecutorJobOperator -  COMMONS-LOGGING Attempting to launch job 'job' which defines an incrementer with additional parameters={{}}. Those additional parameters will be ignored.
```

This warning should be removed when the parameters set is empty.

