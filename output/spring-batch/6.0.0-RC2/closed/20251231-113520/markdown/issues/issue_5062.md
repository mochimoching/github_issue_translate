# Incorrect ordering when retrieving job executions with JobExecutionDao

**Issue番号**: #5062

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-29

**ラベル**: type: bug, in: core, related-to: job-repository, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5062

**関連リンク**:
- Commits:
  - [0125b19](https://github.com/spring-projects/spring-batch/commit/0125b19af19c64c67c5961ca36fa321713ad3c94)

## 内容

`JobExecutionDao#findJobExecutions` states that the returned job executions should be sorted backwards by creation order (the first element is the most recent).

As of v5.2.4 / v6.0.0-RC1, this is not the case both in the JDBC and MongoDB implementations.

