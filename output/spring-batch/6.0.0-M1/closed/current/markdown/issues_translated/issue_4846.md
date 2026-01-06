*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobExplorerFactoryBeanをJdbcJobExplorerFactoryBeanに名称変更

**Issue番号**: #4846

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4846

**関連リンク**:
- Commits:
  - [d6ce07b](https://github.com/spring-projects/spring-batch/commit/d6ce07ba8359083a36cef4df2a578b1928ab8e63)

## 内容

v5.2で`MongoJobExplorerFactoryBean`が導入されたため、`JobExplorerFactoryBean`はJDBCベースのジョブエクスプローラを設定することを反映して、`JdbcJobExplorerFactoryBean`に名称変更すべきです。
