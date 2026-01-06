*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

Spring BatchをMongoDBで使用する際、`@EnableMongoJobRepository`と`@EnableBatchProcessing`を併用すると、「Invalid transaction attribute token: [SERIALIZABLE]」というエラーが発生し、起動に失敗する問題です。

**発生する構成**:
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- MongoDBをジョブリポジトリとして使用

## 原因

`BatchRegistrar`クラスがMongoDBのジョブリポジトリを設定する際、トランザクション分離レベルのプロパティ設定に誤りがあります。

- **誤**: `isolationLevelForCreate`（文字列型プロパティ）に、`Isolation`列挙型を設定しようとしている
- **正**: `isolationLevelForCreateEnum`（列挙型用プロパティ）を使用すべき、または文字列変換を適切に行うべき

現状の実装では、列挙型の`Isolation.SERIALIZABLE`が渡され、それが文字列プロパティとして処理される際、期待される形式と一致せずエラーになっています。

```java
// 現在の実装（MongoDB用）
beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);

// 正しい実装（JDBC用やすべき実装）
beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
```

## 対応方針

`BatchRegistrar`クラスの修正を行い、MongoDBのリポジトリ設定時にも`isolationLevelForCreateEnum`プロパティを使用して列挙型の値を渡すように変更します。これにより、JDBC実装と同様に正しく設定が反映されるようになります。
