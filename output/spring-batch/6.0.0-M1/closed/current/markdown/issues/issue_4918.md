# Replace usage of JobExplorer with JobRepository in StepExecutionRequestHandler

**Issue番号**: #4918

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4918

**関連リンク**:
- Commits:
  - [ce89612](https://github.com/spring-projects/spring-batch/commit/ce896128424e7673d1a9f2b884bb5866d296f8c4)

## 内容

`StepExecutionRequestHandler` currently uses a `JobExplorer` which is now deprecated.

This issue is to replace the usage of `JobExplorer` with a `JobRepository`.

