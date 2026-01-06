# Rename JobRepositoryFactoryBean to JdbcJobRepositoryFactoryBean

**Issue番号**: #4829

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-06

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4829

**関連リンク**:
- Commits:
  - [46d42ab](https://github.com/spring-projects/spring-batch/commit/46d42ab757941d6dd56dc32fd6e468b6eb347642)

## 内容

After the introduction of `MongoJobRepositoryFactoryBean` in v5.2, `JobRepositoryFactoryBean` should be renamed to `JdbcJobRepositoryFactoryBean` to reflect the fact that it configures a JDBC-based job repository.


## コメント

### コメント 1 by minkukjo

**作成日**: 2025-05-06

@fmbenhassine 
If it's just a name change, I'd like to work on it. Can I take it?

### コメント 2 by fmbenhassine

**作成日**: 2025-05-06

@minkukjo Thank you for your offer to help! but this is already done. I just need to push the change set.

