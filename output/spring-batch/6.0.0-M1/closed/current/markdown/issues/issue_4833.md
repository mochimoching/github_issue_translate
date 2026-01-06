# Improve JobOperator by reducing its scope to job operations only

**Issue番号**: #4833

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4833

**関連リンク**:
- Commits:
  - [afdd842](https://github.com/spring-projects/spring-batch/commit/afdd842bc3e6d599e475f597f8becc12cc685fbd)

## 内容

As of v5.2, the `JobOperator` interface is exposing functionality that is out of its initial scope (ie operating batch jobs like start/stop/restart, etc).

Several methods like `getJobInstance`, `getExecutions` and similar methods have duplicate implementations in `JobRepository` and `JobExplorer` which is not ideal from a maintenance perspective . Moreover, some methods deal with job parameters conversion from string literals to domain objects which is not correct in a high-level API like `JobOperator` (those could be part of `CommandLineJobRunner` for example).

Those methods should be deprecated in v6.0 and removed in v6.2 or later.

