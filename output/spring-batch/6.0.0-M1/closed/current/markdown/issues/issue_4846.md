# Rename JobExplorerFactoryBean to JdbcJobExplorerFactoryBean

**Issue番号**: #4846

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4846

**関連リンク**:
- Commits:
  - [d6ce07b](https://github.com/spring-projects/spring-batch/commit/d6ce07ba8359083a36cef4df2a578b1928ab8e63)

## 内容

After the introduction of `MongoJobExplorerFactoryBean` in v5.2, `JobExplorerFactoryBean` should be renamed to `JdbcJobExplorerFactoryBean ` to reflect the fact that it configures a JDBC-based job explorer.


