*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# ステップ実行コンテキストがJdbcExecutionContextDaoによってロードされない

**課題番号**: #5117

**状態**: closed | **作成者**: cppwfs | **作成日**: 2025-11-26

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5117

**関連リンク**:
- Commits:
  - [48e84cc](https://github.com/spring-projects/spring-batch/commit/48e84ccf044f85c88e6de16e18f6a78be4769ffd)

## 内容

**バグの説明**
ステップ実行がデータベースから読み込まれる際、実行コンテキストが読み込まれません。

**環境**
- Spring Batch 6.0.0
- Spring Boot 4.0.0
- Java 21

**最小限の再現例**
次のサンプルアプリケーションを実行してください：
https://github.com/spring-projects/spring-batch/files/16047467/demo.zip

**期待される動作**
実行コンテキストは`JobOperator.stepExecutionSummaries(long instanceId)`が呼び出された時にロードされるべきです。

**実際の動作**
実行コンテキストはロードされません。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-04

サンプルをありがとうございます！バグであることを確認できました。次のパッチリリースで修正します。

