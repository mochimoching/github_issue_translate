# Remove usage of JobExplorer in BatchIntegrationConfiguration

**Issue番号**: #4919

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4919

**関連リンク**:
- Commits:
  - [9b7323f](https://github.com/spring-projects/spring-batch/commit/9b7323f58000c3465f5a70afb9cbbc58612c2c2f)

## 内容

The configuration of the batch integration module (mainly the remote partitioning setup) programmatically and through `@EnableBatchIntegration` currently requires both a job repository and a job explorer.

After #4824 , there is no need to configure a job explorer anymore. This issue is to remove the usage of `JobExplorer` in the `BatchIntegrationConfiguration` class and related APIs (`RemotePartitioningManagerStepBuilder[Factory]` and `RemotePartitioningWorkerStepBuilder[Factory]`).

