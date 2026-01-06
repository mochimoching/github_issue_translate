*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# StepExecutionRequestHandlerでのJobExplorerの使用をJobRepositoryに置き換え

**Issue番号**: #4918

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4918

**関連リンク**:
- Commits:
  - [ce89612](https://github.com/spring-projects/spring-batch/commit/ce896128424e7673d1a9f2b884bb5866d296f8c4)

## 内容

`StepExecutionRequestHandler`は現在、非推奨となった`JobExplorer`を使用しています。

この課題は、`JobExplorer`の使用を`JobRepository`に置き換えるためのものです。
