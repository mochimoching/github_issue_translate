*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# @EnableMongoJobRepositoryが「Invalid transaction attribute token: [SERIALIZABLE]」で失敗する

**課題番号**: #5105

**状態**: closed | **作成者**: br05s | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5105

## 内容

**バグの説明**
`@EnableMongoJobRepository`を`@EnableBatchProcessing`と共に使用すると、「Invalid transaction attribute token: [SERIALIZABLE]」というエラーが発生します。

**環境**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25

**再現手順**
1. Spring Initializrを使用して、Spring BatchとSpring Data MongoDBを選択した新しいSpring Bootプロジェクトを作成します。
2. 設定クラスを作成し、`@EnableBatchProcessing`および`@EnableMongoJobRepository`アノテーションを付与します
3. シンプルなジョブを実装します
4. `application.yml`にMongoDBのプロパティを追加します

**期待される動作**
ジョブは問題なく実行されるはずです

**最小限の再現例**
`SimpleJobConfig.java`
```java
@EnableBatchProcessing
@EnableMongoJobRepository
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
    Step simpleStep(Tasklet simpleTasklet, PlatformTransactionManager transactionManager, JobRepository jobRepository) {
        return new StepBuilder("simpleStep", jobRepository)
                .tasklet(simpleTasklet, transactionManager)
                .build();
    }

    @Bean
    Tasklet simpleTasklet() {
        return (contribution, chunkContext) -> {
            println("test");
            return RepeatStatus.FINISHED;
        };
    }

    @Bean
    MongoTransactionManager transactionManager(MongoDatabaseFactory mongoDatabaseFactory) {
        return new MongoTransactionManager(mongoDatabaseFactory);
    }

}
```

`application.yml`
```yaml
spring:
  application:
    name: batch-mongo-demo
  mongodb:
    host: (removed)
    port: 27017
    database: batch
```

## コメント

### コメント 1 by br05s

**作成日**: 2025-11-24

問題の原因は、JDBCバージョンのように`setIsolationLevelForCreateEnum`ではなく、`BatchRegistrar`がMongoジョブリポジトリを設定する際に`isolationLevelForCreate`プロパティを設定していることのようです。

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

### コメント 2 by banseok1216

**作成日**: 2025-12-07

`@EnableBatchProcessing` + `@EnableMongoJobRepository`で同じ問題が発生しています。

`BatchRegistrar`での指摘された根本原因（`Isolation`列挙型を`isolationLevelForCreateEnum`ではなく`isolationLevelForCreate`にバインド）を確認できます。また、Mongoデフォルト設定からいくつかの追加証拠があります。

`MongoDefaultBatchConfiguration`は次のように`MongoJobRepositoryFactoryBean`を設定します：

```java
@Bean
@Override
public JobRepository jobRepository() throws BatchConfigurationException {
    MongoJobRepositoryFactoryBean jobRepositoryFactoryBean = new MongoJobRepositoryFactoryBean();
    try {
        jobRepositoryFactoryBean.setMongoOperations(getMongoOperations());
        jobRepositoryFactoryBean.setTransactionManager(getTransactionManager());
        jobRepositoryFactoryBean.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
        jobRepositoryFactoryBean.setValidateTransactionState(getValidateTransactionState());
        jobRepositoryFactoryBean.setJobKeyGenerator(getJobKeyGenerator());
        jobRepositoryFactoryBean.setJobInstanceIncrementer(getJobInstanceIncrementer());
        jobRepositoryFactoryBean.setJobExecutionIncrementer(getJobExecutionIncrementer());
        jobRepositoryFactoryBean.setStepExecutionIncrementer(getStepExecutionIncrementer());
        jobRepositoryFactoryBean.afterPropertiesSet();
        return jobRepositoryFactoryBean.getObject();
    }
    catch (Exception e) {
        throw new BatchConfigurationException("Unable to configure the default job repository", e);
    }
}
```

ここでは、分離レベルは列挙型ベースのセッターを介して渡されています：

```java
jobRepositoryFactoryBean.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
```

したがって、`Isolation`値は明らかに`setIsolationLevelForCreateEnum`を通過することが意図されています。

一方、`BatchRegistrar.registerMongoJobRepository`では、`@EnableMongoJobRepository#isolationLevelForCreate`からの値（これは`Isolation`列挙型です）が現在**文字列**プロパティ`isolationLevelForCreate`にバインドされています：

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

これは内部的に`setIsolationLevelForCreate(String)`を呼び出し、`ISOLATION_SERIALIZABLE`のようなトークンを期待する`TransactionAttributeEditor`を経由します。列挙型が「SERIALIZABLE」に変換されると、次のようになります：

> Invalid transaction attribute token: [SERIALIZABLE]

JDBCの場合、レジストラーは既に列挙型ベースのプロパティを使用しています：

```java
Isolation isolationLevelForCreate = jdbcJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

そして、デフォルトのMongo設定（`MongoDefaultBatchConfiguration`）も`setIsolationLevelForCreateEnum`を使用しています。

したがって、Mongoレジストラーも同じ列挙型ベースのプロパティを使用すべきのようです。次のように変更すると：

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

この変更で問題が修正されました。

リグレッションを防ぐために、`BatchRegistrarTests`に小さなテストも追加しました。以下の設定でコンテキストをブートストラップします：

```java
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
```

そして、単純に`JobRepository`が作成されることをアサートします：

```java
@Test
@DisplayName("Mongo job repository should be configured successfully with @EnableMongoJobRepository")
void testMongoJobRepositoryConfiguredWithEnableMongoJobRepository() {
    AnnotationConfigApplicationContext context =
            new AnnotationConfigApplicationContext(MongoJobConfiguration.class);

    JobRepository jobRepository = context.getBean(JobRepository.class);
```
