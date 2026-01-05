# @EnableMongoJobRepositoryがInvalid transaction attribute token: [SERIALIZABLE]で失敗する

**Issue番号**: #5105

**状態**: closed | **作成者**: br05s | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5105

## 内容

**バグの説明**
`@EnableBatchProcessing`と一緒に`@EnableMongoJobRepository`を使用すると、`Invalid transaction attribute token: [SERIALIZABLE]`というエラーが発生します。

**環境**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25

**再現手順**
1. InitializrでSpring BatchとSpring Data MongoDBを選択して新しいSpring Bootプロジェクトを作成します。
2. 設定クラスを作成し、`@EnableBatchProcessing`と`@EnableMongoJobRepository`でアノテーションを付けます。
3. シンプルなジョブを実装します。
4. `application.yml`にMongoDBプロパティを追加します。

**期待される動作**
ジョブが問題なく実行されるはずです。

**最小限の再現可能な例**
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

問題は、JDBCバージョンのように`setIsolationLevelForCreateEnum`の代わりに、`BatchRegistrar`がMongoジョブリポジトリを設定する際に`isolationLevelForCreate`プロパティを設定していることが原因のようです。

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

### コメント 2 by banseok1216

**作成日**: 2025-12-07

私も`@EnableBatchProcessing` + `@EnableMongoJobRepository`で同じ課題を確認しています。

根本原因は、あなたが`BatchRegistrar`で指摘したもの(enumベースのプロパティではなく、`Isolation` enumを`isolationLevelForCreate`にバインドしている)であることを確認でき、Mongoのデフォルト設定からの追加の証拠があります。

`MongoDefaultBatchConfiguration`は次のように`MongoJobRepositoryFactoryBean`を設定します:

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

ここでは、分離レベルはenumベースのセッターを介して渡されます:

```java
jobRepositoryFactoryBean.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
```

したがって、`Isolation`値は明らかに`setIsolationLevelForCreateEnum`を経由することを意図しています。

一方、`BatchRegistrar.registerMongoJobRepository`では、`@EnableMongoJobRepository#isolationLevelForCreate`からの値(`Isolation` enum)が現在**String**プロパティ`isolationLevelForCreate`にバインドされています:

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

これは内部的に`setIsolationLevelForCreate(String)`を呼び出し、`ISOLATION_SERIALIZABLE`のようなトークンを期待する`TransactionAttributeEditor`を経由することになります。enumが`"SERIALIZABLE"`に変換されるため、次のエラーが発生します:

> Invalid transaction attribute token: [SERIALIZABLE]

JDBCの場合、レジストラは既にenumベースのプロパティを使用しています:

```java
Isolation isolationLevelForCreate = jdbcJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

そして、デフォルトのMongo設定(`MongoDefaultBatchConfiguration`)も`setIsolationLevelForCreateEnum`を使用しています。

したがって、Mongoレジストラも同じenumベースのプロパティを使用すべきのようです。次のように変更すると:

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

私の環境では問題が解決します。

リグレッションを防ぐために、`BatchRegistrarTests`に以下のような小さなテストも追加しました:

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

そして、単に`JobRepository`が作成されることを確認します:

```java
@Test
@DisplayName("Mongo job repository should be configured successfully with @EnableMongoJobRepository")
void testMongoJobRepositoryConfiguredWithEnableMongoJobRepository() {
    AnnotationConfigApplicationContext context =
            new AnnotationConfigApplicationContext(MongoJobConfiguration.class);

    JobRepository jobRepository = context.getBean(JobRepository.class);
    Assertions.assertNotNull(jobRepository);
}
```

現在のコードではこのテストは`Invalid transaction attribute token: [SERIALIZABLE]`で失敗し、`isolationLevelForCreateEnum`への変更では成功します。この変更とテストを含むPRを開きます。


### コメント 3 by fmbenhassine

**作成日**: 2025-12-15

@br05s これは有効な課題です。報告ありがとうございます。

課題 [#5141](https://github.com/spring-projects/spring-batch/issues/5141) で解決され、今後のv6.0.1で提供されます。@banseok1216による修正に感謝します 🙏

