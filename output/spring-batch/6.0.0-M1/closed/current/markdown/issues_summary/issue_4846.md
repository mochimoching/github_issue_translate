*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

課題 [#4829](https://github.com/spring-projects/spring-batch/issues/4829) と同様に、`JobExplorerFactoryBean`を`JdbcJobExplorerFactoryBean`に名称変更し、命名規則を統一する提案です。

### 命名の不統一

| ストレージ | v5.2のクラス名 | 問題 |
|---------|------------|------|
| JDBC | `JobExplorerFactoryBean` | ストレージ種別が不明 ❌ |
| MongoDB | `MongoJobExplorerFactoryBean` | 明確 ✅ |

## 原因

`JobExplorerFactoryBean`は、MongoDBサポート追加前に作成され、JDBCが唯一のストレージだったため、「JDBC」を明示する必要がありませんでした。しかし、`MongoJobExplorerFactoryBean`の追加により命名規則が不統一になりました。

## 対応方針

**コミット**: [d6ce07b](https://github.com/spring-projects/spring-batch/commit/d6ce07ba8359083a36cef4df2a578b1928ab8e63)

`JobExplorerFactoryBean`を`JdbcJobExplorerFactoryBean`に名称変更しました。

### v6.0の統一された命名規則

| ストレージ | v6.0のクラス名 | 明確性 |
|---------|------------|-------|
| JDBC | `JdbcJobExplorerFactoryBean` | ✅ |
| MongoDB | `MongoJobExplorerFactoryBean` | ✅ |

### 移行例

```java
// v5.2（変更前）
JobExplorerFactoryBean factory = new JobExplorerFactoryBean();
factory.setDataSource(dataSource);

// v6.0（変更後）
JdbcJobExplorerFactoryBean factory = new JdbcJobExplorerFactoryBean();
factory.setDataSource(dataSource);
```

### メリット

- 命名規則の一貫性向上
- ストレージ種別が一目瞭然
- 課題 [#4829](https://github.com/spring-projects/spring-batch/issues/4829)（Repository側）との対称性

この変更により、すべてのファクトリーBeanが`<ストレージ>Job{Repository|Explorer}FactoryBean`パターンに統一されました。
