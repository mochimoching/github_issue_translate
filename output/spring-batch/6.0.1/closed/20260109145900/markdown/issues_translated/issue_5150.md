*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# RemotePartitioningWorkerStepBuilderでビルドメソッドが欠落している

**課題番号**: #5150

**状態**: closed | **作成者**: daninelAli | **作成日**: 2025-12-09

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5150

**関連リンク**:
- Commits:
  - [b75f42e](https://github.com/spring-projects/spring-batch/commit/b75f42e5c35abb46bf51df1d1c1d39d4879f58f3)

## 内容

**バグの説明**
`RemotePartitioningWorkerStepBuilder`には、デリゲートする`StepBuilder`から`inputChannel`、`outputChannel`、`stepOperations`、`beanFactory`のオーバーライドが欠落しており、このビルダーで簡単にワーカーステップを構築できるべき`build()`メソッドも欠けています。

**再現手順**
リモートパーティショニングワーカーのステップ設定で、提供されているすべてのビルダーメソッドが使えるかチェックする。

**環境**
- Spring Batch 6.0.0

