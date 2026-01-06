# Redundant methods in JobExplorer/JobInstanceDao APIs

**Issue番号**: #4821

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-29

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4821

**関連リンク**:
- Commits:
  - [bf53794](https://github.com/spring-projects/spring-batch/commit/bf53794d6a1f1ab08d3fbc18cc40e1048e376e9c)

## 内容

As of v5.2, the JobExplorer/JobInstanceDao APIs contain two similar methods:

```java
List<JobInstance> getJobInstances(String jobName, int start, int count);

List<JobInstance> findJobInstancesByJobName(String jobName, int start, int count);
```

Both methods return the same result. `findJobInstancesByJobName` is not used and should be deprecated in v6.0 for removal in v6.2.

