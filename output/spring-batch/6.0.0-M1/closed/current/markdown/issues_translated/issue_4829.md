*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobRepositoryFactoryBeanをJdbcJobRepositoryFactoryBeanに名称変更

**Issue番号**: #4829

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-06

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4829

**関連リンク**:
- Commits:
  - [46d42ab](https://github.com/spring-projects/spring-batch/commit/46d42ab757941d6dd56dc32fd6e468b6eb347642)

## 内容

v5.2で`MongoJobRepositoryFactoryBean`が導入されたため、`JobRepositoryFactoryBean`はJDBCベースのジョブリポジトリを設定することを反映して、`JdbcJobRepositoryFactoryBean`に名称変更すべきです。

## コメント

### コメント 1 by minkukjo

**作成日**: 2025-05-06

@fmbenhassine 
単なる名前の変更であれば、私が作業したいです。担当してもよろしいでしょうか？

### コメント 2 by fmbenhassine

**作成日**: 2025-05-06

@minkukjo ご協力のお申し出ありがとうございます！しかし、これはすでに完了しています。変更セットをプッシュする必要があるだけです。
