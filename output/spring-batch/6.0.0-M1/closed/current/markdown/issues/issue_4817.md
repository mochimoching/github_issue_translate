# Remove dependency to JobExplorer in SimpleJobOperator

**Issue番号**: #4817

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-28

**ラベル**: type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4817

**関連リンク**:
- Commits:
  - [6992b79](https://github.com/spring-projects/spring-batch/commit/6992b79b8dc6f6e87f1dd75548328f9011ec699e)

## 内容

As of v5, `SimpleJobRepository` requires a `JobExplorer` in addition to a `JobRepository`. However, since `JobExplorer` is designed to be a read-only version of `JobRepository`, then the dependency to a `JobExplorer` does not make sense. In other words, since `SimpleJobOperator` depends on a `JobRepository` (which has read/write access to the meta-data store), it should not have a dependency to the read-only API. Ideally, `JobRepository` should be an extension of `JobExplorer` to add write/update operations.

This issue is a pre-requisite to making the default batch configuration work with any job repository (and not assume/require a JDBC infrastructure).

