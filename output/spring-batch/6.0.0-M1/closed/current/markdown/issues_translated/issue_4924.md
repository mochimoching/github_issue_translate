*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobLaunchingGatewayとJobLaunchingMessageHandlerでのJobLauncherの使用をJobOperatorに置き換え

**Issue番号**: #4924

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4924

**関連リンク**:
- Commits:
  - [c34a1fc](https://github.com/spring-projects/spring-batch/commit/c34a1fc73d632bc9990169333c8ca47355c8b077)

## 内容

`JobLauncher`の非推奨化後、`JobLaunchingGateway`と`JobLaunchingMessageHandler`は代わりに`JobOperator`を使用するよう更新すべきです。
