# Replace usage of JobLauncher with JobOperator in JobLaunchingGateway and JobLaunchingMessageHandler

**Issue番号**: #4924

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4924

**関連リンク**:
- Commits:
  - [c34a1fc](https://github.com/spring-projects/spring-batch/commit/c34a1fc73d632bc9990169333c8ca47355c8b077)

## 内容

After the deprecation of `JobLauncher`, `JobLaunchingGateway` and `JobLaunchingMessageHandler` should be updated to use `JobOperator` instead.

