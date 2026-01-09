*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

リモートパーティショニング用のステップを構築するためのビルダー`RemotePartitioningWorkerStepBuilder`において、必要なメソッドが欠落しているというバグです。

**欠落している機能**:
1. `build()`メソッド: ステップを最終的に生成するためのメソッド
2. 親クラス（`StepBuilder`など）から継承・オーバーライドすべき設定メソッド群
    - `inputChannel`
    - `outputChannel`
    - `stepOperations`
    - `beanFactory`

**影響**:
- このビルダーを使用しても、ワーカーステップを流暢なAPI（Fluent API）で構築・完了させることができず、使い勝手が悪い（またはコンパイルエラーになる）。

## 原因

`RemotePartitioningWorkerStepBuilder`の実装時に、必要なメソッドの公開やオーバーライドが漏れていたため。

## 対応方針

`RemotePartitioningWorkerStepBuilder`クラスに欠落しているメソッド（`build()`および各種設定メソッド）を追加・実装し、他のビルダーと同様に使用できるように修正します。
