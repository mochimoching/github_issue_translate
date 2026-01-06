*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# MessageChannelPartitionHandlerが非JDBCジョブリポジトリ実装で使用できない

**Issue番号**: #4917

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: feature, in: integration, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4917

**関連リンク**:
- Commits:
  - [61fc226](https://github.com/spring-projects/spring-batch/commit/61fc22652c9c1f3da38aea9b22cf80da4c5c7ea2)

## 内容

v5.2時点で、リポジトリポーリングを使用したリモートパーティショニング設定において、`MessageChannelPartitionHandler`はデータソースを必要とするため、MongoDBで使用できません。

このハンドラーはジョブリポジトリインターフェースに対して動作すべきです。
