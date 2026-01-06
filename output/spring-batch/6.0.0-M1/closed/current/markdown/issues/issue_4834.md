# Rename SimpleJobOperator to TaskExecutorJobOperator

**Issue番号**: #4834

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4834

**関連リンク**:
- Commits:
  - [e5bda0d](https://github.com/spring-projects/spring-batch/commit/e5bda0d40ae4ae1dedaca4d9339b29488225db83)

## 内容

After #4832 , `SimpleJobOperator` should be renamed to `TaskExecutorJobOperator` to reflect the fact that it is based on a task executor for starting jobs.

