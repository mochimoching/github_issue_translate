*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# DAO実装を別々のパッケージに移動

**Issue番号**: #4848

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, related-to: job-repository, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4848

**関連リンク**:
- Commits:
  - [9eafb31](https://github.com/spring-projects/spring-batch/commit/9eafb31af4b5a0b019ca3d03a0dfb0278d378883)

## 内容

v5.2でMongoDBジョブリポジトリが導入された後、JDBCとMongoのDAO実装は専用のパッケージに移動すべきです。
