*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# SystemCommandTaskletでのJobExplorerの使用をJobRepositoryに置き換え

**Issue番号**: #4927

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4927

**関連リンク**:
- Commits:
  - [a8e138c](https://github.com/spring-projects/spring-batch/commit/a8e138cbf488596f48e9c8f49522fa7235a32943)

## 内容

`JobExplorer`の非推奨化後、`SystemCommandTasklet`は代わりに`JobRepository`を使用するよう更新すべきです。
