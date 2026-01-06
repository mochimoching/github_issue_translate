*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5105: @EnableMongoJobRepositoryで「Invalid transaction attribute token」エラーが発生

## 課題概要

Spring BatchでMongoDBをジョブリポジトリとして使用する際、`@EnableMongoJobRepository`アノテーションを使うと「Invalid transaction attribute token: [SERIALIZABLE]」というエラーが発生してアプリケーションが起動できない問題です。

### 用語解説

- **JobRepository**: Spring Batchのジョブ実行情報（ジョブの状態、実行履歴など）を保存するリポジトリ。通常はRDBMS（JDBCリポジトリ）を使うが、MongoDBなども使用可能
- **@EnableMongoJobRepository**: MongoDBをジョブリポジトリとして使用するための設定アノテーション
- **トランザクション分離レベル**: データベーストランザクションの独立性を制御する設定。`SERIALIZABLE`は最も厳格な分離レベル

### 問題のシナリオ

以下の設定で起動すると例外が発生します：

```java
@EnableBatchProcessing
@EnableMongoJobRepository  // MongoDB用のジョブリポジトリを有効化
@Configuration
public class SimpleJobConfig {
    @Bean
    Job simpleJob(Step simpleStep, JobRepository jobRepository) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(simpleStep)
                .build();
    }
    
    @Bean
    MongoTransactionManager transactionManager(MongoDatabaseFactory factory) {
        return new MongoTransactionManager(factory);
    }
}
```

起動時のエラー：
```
Invalid transaction attribute token: [SERIALIZABLE]
```

## 原因

`BatchRegistrar`クラスがMongoDBジョブリポジトリを設定する際、トランザクション分離レベルを誤ったプロパティ名で設定していたため、Spring Frameworkのトランザクション設定パーサーがエラーを起こしていました。

### 詳細な原因

#### 1. 正しい設定方法（MongoDefaultBatchConfiguration）

デフォルト設定では、列挙型を受け取る正しいセッターメソッドを使用しています：

```java
// MongoDefaultBatchConfiguration.java（正しい実装）
@Bean
public JobRepository jobRepository() throws BatchConfigurationException {
    MongoJobRepositoryFactoryBean factory = new MongoJobRepositoryFactoryBean();
    
    // 正しい: 列挙型ベースのセッターを使用
    factory.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
    
    return factory.getObject();
}
```

#### 2. 問題のあったコード（BatchRegistrar）

一方、`@EnableMongoJobRepository`アノテーションを処理する`BatchRegistrar`では、誤ったプロパティ名を使用していました：

```java
// BatchRegistrar.java（問題のあった実装）
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    // 誤り: 文字列ベースのプロパティに列挙型を設定
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

#### 3. 問題のメカニズム

```
【データの流れ】
@EnableMongoJobRepository
  ↓
isolationLevelForCreate = Isolation.SERIALIZABLE（列挙型）
  ↓
beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", ...)
  ↓
内部でsetIsolationLevelForCreate(String)が呼ばれる
  ↓
TransactionAttributeEditorが"SERIALIZABLE"をパース
  ↓
"ISOLATION_SERIALIZABLE"というトークンを期待しているが、"SERIALIZABLE"が渡される
  ↓
Invalid transaction attribute token: [SERIALIZABLE] エラー
```

#### 4. JDBC版との比較

JDBC版のレジストラーは正しく実装されていました：

```java
// BatchRegistrar.java（JDBC版 - 正しい実装）
Isolation isolationLevelForCreate = jdbcJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    // 正しい: 列挙型ベースのプロパティを使用
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

### 問題の整理

| 実装箇所 | プロパティ名 | 期待する型 | 状態 |
|---------|------------|----------|-----|
| MongoDefaultBatchConfiguration | `isolationLevelForCreateEnum` | `Isolation`（列挙型） | ✅ 正しい |
| BatchRegistrar（JDBC） | `isolationLevelForCreateEnum` | `Isolation`（列挙型） | ✅ 正しい |
| BatchRegistrar（Mongo） | `isolationLevelForCreate` | `String` | ❌ 誤り |

## 対応方針

`BatchRegistrar`のMongo設定部分を、JDBC設定と同様に列挙型ベースのプロパティ名を使用するように修正されました。

### 修正内容

```java
// BatchRegistrar.java（修正後）
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    // 修正: 列挙型ベースのプロパティ名に変更
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

### 修正のポイント

1. **プロパティ名の変更**: `isolationLevelForCreate` → `isolationLevelForCreateEnum`
2. **型の一致**: `Isolation`列挙型を直接`setIsolationLevelForCreateEnum(Isolation)`に渡す
3. **JDBC実装との統一**: MongoとJDBCの両方で同じパターンを使用

### テストの追加

リグレッション防止のため、新しいテストも追加されました：

```java
@Test
@DisplayName("Mongo job repository should be configured successfully with @EnableMongoJobRepository")
void testMongoJobRepositoryConfiguredWithEnableMongoJobRepository() {
    @Configuration
    @EnableBatchProcessing
    @EnableMongoJobRepository
    static class MongoJobConfiguration {
        @Bean
        MongoOperations mongoTemplate() {
            return Mockito.mock(MongoOperations.class);
        }
        
        @Bean
        MongoTransactionManager transactionManager() {
            return Mockito.mock(MongoTransactionManager.class);
        }
    }
    
    AnnotationConfigApplicationContext context =
        new AnnotationConfigApplicationContext(MongoJobConfiguration.class);
    
    JobRepository jobRepository = context.getBean(JobRepository.class);
    assertThat(jobRepository).isNotNull();  // 正常に作成されることを確認
}
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `BatchRegistrar` - アノテーションベースの設定を処理するクラス
  - `MongoJobRepositoryFactoryBean` - MongoDBジョブリポジトリのファクトリBean
  - `TransactionAttributeEditor` - トランザクション属性文字列をパースするエディター
- **影響範囲**: `@EnableMongoJobRepository`を使用しているすべてのプロジェクト
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5105
