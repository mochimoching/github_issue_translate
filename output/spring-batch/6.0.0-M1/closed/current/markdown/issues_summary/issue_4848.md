*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

v5.2でMongoDBジョブリポジトリが導入されたことに伴い、JDBCとMongoDBのDAO実装を専用のパッケージに分離する構造改善です。

### 変更内容

```
org.springframework.batch.core.repository.dao
├── (共通インターフェース)
├── jdbc/                    ← JDBCベースDAO
│   ├── JdbcJobInstanceDao
│   ├── JdbcJobExecutionDao
│   └── ...
└── mongo/                   ← MongoDBベースDAO
    ├── MongoJobInstanceDao
    ├── MongoJobExecutionDao
    └── ...
```

## 原因

v5.2以前は、すべてのDAO実装が同じパッケージに混在していました。MongoDBサポート追加後、JDBC実装とMongoDB実装を明確に分離する必要が出てきました。

## 対応方針

**コミット**: [9eafb31](https://github.com/spring-projects/spring-batch/commit/9eafb31af4b5a0b019ca3d03a0dfb0278d378883)

DAO実装を`jdbc/`と`mongo/`サブパッケージに移動し、ストレージ技術ごとに整理しました。

### メリット

- パッケージ構造がストレージ実装を明確に反映
- 新しいストレージ実装（例：Cassandra）の追加が容易
- コードナビゲーションと保守性の向上
