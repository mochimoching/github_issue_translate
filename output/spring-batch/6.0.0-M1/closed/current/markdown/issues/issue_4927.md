# Replace usage of JobExplorer with JobRepository in SystemCommandTasklet

**Issue番号**: #4927

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4927

**関連リンク**:
- Commits:
  - [a8e138c](https://github.com/spring-projects/spring-batch/commit/a8e138cbf488596f48e9c8f49522fa7235a32943)

## 内容

After the deprecation of `JobExplorer`, `SystemCommandTasklet` should be updated to use `JobRepository` instead.


