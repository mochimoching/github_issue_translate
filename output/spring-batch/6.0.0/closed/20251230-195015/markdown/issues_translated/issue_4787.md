*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# PlatformTransactionManagerの使用方法を詳細に説明

**Issue番号**: #4787

**状態**: closed | **作成者**: quaff | **作成日**: 2025-03-19

**ラベル**: in: documentation, type: enhancement, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4787

**関連リンク**:
- Commits:
  - [4e5b7d2](https://github.com/spring-projects/spring-batch/commit/4e5b7d26d802afaadac4c4d00e50f71883423e41)

## 内容

`transactionManager`を設定する箇所が多数ありますが、それが必須なのかオプションなのかが不明確です。私の理解では、`dataSource`が必須である以上、Spring Batchはデフォルトとして`DataSourceTransactionManager()`を作成できるはずなので、オプションであるべきだと考えています。間違っていれば訂正してください。

また、それがバッチメタデータ操作に使用されるのか、ステップのJDBCリーダー/ライターに使用されるのかが不明確です。[Spring Boot](https://docs.spring.io/spring-boot/how-to/batch.html)の`@BatchDataSource`と`@BatchTransactionManager`が分離されたDataSourceに使用される場合、`StepBuilder::chunk`にはどちらの`transactionManager`を使用すべきでしょうか?

https://github.com/spring-projects/spring-batch/blob/e1b0f156e4db9ae2c3b60b83ec372dac8bddad68/spring-batch-core/src/main/java/org/springframework/batch/core/step/builder/StepBuilder.java#L118

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-05-22

> Spring Batchはデフォルトとして`DataSourceTransactionManager()`を作成できるはずなので、オプションであるべきだと考えています。間違っていれば訂正してください。

Spring Batchは以前そうしていましたが、#816のような問題を引き起こしていました。

> それがバッチメタデータ操作に使用されるのか、ステップのJDBCリーダー/ライターに使用されるのかが不明確です

これらは異なる場合があります。メタデータには`ResourcelessTransactionManager`を使用し、ビジネスデータには`JdbcTransactionManager`を使用することができます。

この点についてドキュメントに注記を追加して明確化する予定です。

### コメント 2 by quaff

**作成日**: 2025-05-30

> > Spring Batchはデフォルトとして`DataSourceTransactionManager()`を作成できるはずなので、オプションであるべきだと考えています。間違っていれば訂正してください。
> 
> Spring Batchは以前そうしていましたが、[#816](https://github.com/spring-projects/spring-batch/issues/816)のような問題を引き起こしていました。


現在は`@Bean(defaultCandidate = false)`を使用できます。これはSpring Bootが自動設定する`PlatformTransactionManager`を無効化しません。



### コメント 3 by fmbenhassine

**作成日**: 2025-11-19

> 現在は`@Bean(defaultCandidate = false)`を使用できます。これはSpring Bootが自動設定する`PlatformTransactionManager`を無効化しません。

現時点では、Spring Batchがこの方法でトランザクションマネージャーを定義する計画はありませんが、このコンポーネントの使用方法(オプションであることと、ステップとジョブリポジトリで必ずしも同じである必要がないこと)を詳細に説明するためにドキュメントを更新する予定です。



