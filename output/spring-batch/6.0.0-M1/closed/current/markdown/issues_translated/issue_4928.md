*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# RemoteStepExecutionAggregatorでのJobExplorerの使用をJobRepositoryに置き換え

**Issue番号**: #4928

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4928

**関連リンク**:
- Commits:
  - [4b2586d](https://github.com/spring-projects/spring-batch/commit/4b2586d90c3059045ebb7e2383f50f70cff1b23e)

## 内容

`JobExplorer`の非推奨化後、`RemoteStepExecutionAggregator`は代わりに`JobRepository`を使用するよう更新すべきです。
