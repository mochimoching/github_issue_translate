*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobStepでのJobLauncherの使用をJobOperatorに置き換え

**Issue番号**: #4923

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4923

**関連リンク**:
- Commits:
  - [b105c8e](https://github.com/spring-projects/spring-batch/commit/b105c8e422a8d8b7f86c56746c8533c2dcae6a20)

## 内容

`JobLauncher`の非推奨化後、`JobStep`は代わりに`JobOperator`を使用するよう更新すべきです。
