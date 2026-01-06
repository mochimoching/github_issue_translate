# Make JobOperator extend JobLauncher

**Issue番号**: #4832

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4832

**関連リンク**:
- Commits:
  - [fc4a665](https://github.com/spring-projects/spring-batch/commit/fc4a66516ac7048e610065628793c62dcc646db5)

## 内容

`JobOperator` is nothing more than a `JobLauncher` with more capabilities (it's `start` method uses `JobLauncher#run` behind the scenes). Therefore, it should technically be an extension of `JobLauncher`, adding stop/restart functionality on top of just running jobs.

This issue is to make `JobOperator` extend `JobLauncher`, which will greatly simplify the default batch configuration by removing the requirement to define two beans instead of one.

