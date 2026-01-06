*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobExplorer/JobInstanceDao APIの冗長なメソッド

**Issue番号**: #4821

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-29

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4821

**関連リンク**:
- Commits:
  - [bf53794](https://github.com/spring-projects/spring-batch/commit/bf53794d6a1f1ab08d3fbc18cc40e1048e376e9c)

## 内容

v5.2時点で、`JobExplorer`/`JobInstanceDao`のAPIには2つの類似したメソッドが含まれています：

```java
List<JobInstance> getJobInstances(String jobName, int start, int count);

List<JobInstance> findJobInstancesByJobName(String jobName, int start, int count);
```

両方のメソッドは同じ結果を返します。`findJobInstancesByJobName`は使用されていないため、v6.0で非推奨とし、v6.2で削除すべきです。
