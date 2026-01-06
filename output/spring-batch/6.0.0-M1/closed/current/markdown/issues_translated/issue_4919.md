*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# BatchIntegrationConfigurationにおけるJobExplorerの使用削除

**Issue番号**: #4919

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4919

**関連リンク**:
- Commits:
  - [9b7323f](https://github.com/spring-projects/spring-batch/commit/9b7323f58000c3465f5a70afb9cbbc58612c2c2f)

## 内容

バッチ統合モジュールの設定（主にリモートパーティショニング設定）は、プログラム的にも`@EnableBatchIntegration`を通じても、現在ジョブリポジトリとジョブエクスプローラの両方を必要としています。

課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824) の後、もはやジョブエクスプローラを設定する必要はありません。この課題は、`BatchIntegrationConfiguration`クラスおよび関連API（`RemotePartitioningManagerStepBuilder[Factory]`と`RemotePartitioningWorkerStepBuilder[Factory]`）から`JobExplorer`の使用を削除するためのものです。
