# @EnableMongoJobRepository fails with Invalid transaction attribute token: [SERIALIZABLE]

**Issue番号**: #5105

**状態**: closed | **作成者**: br05s | **作成日**: 2025-11-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5105

## 内容

**Bug description**
When using `@EnableMongoJobRepository` with `@EnableBatchProcessing`, you will receive an error saying `Invalid transaction attribute token: [SERIALIZABLE]`

**Environment**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25

**Steps to reproduce**
1. Create a new Spring Boot project through the Initializr with Spring Batch and Spring Data MongoDB selected.
2. Create a configuration class and annotate it with `@EnableBatchProcessing` and `@EnableMongoJobRepository`
3. Implement a simple job
4. Add MongoDB properties to `application.yml`

**Expected behavior**
Job should run without issue

**Minimal Complete Reproducible example**
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

It looks like the problem is `BatchRegistrar` sets the property `isolationLevelForCreate` when configuring the Mongo job repository instead of `setIsolationLevelForCreateEnum` like the JDBC version does.

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

### コメント 2 by banseok1216

**作成日**: 2025-12-07

I’m seeing the same issue with `@EnableBatchProcessing` + `@EnableMongoJobRepository`.

I can confirm that the root cause is the one you pointed out in `BatchRegistrar` (binding the `Isolation` enum to `isolationLevelForCreate` instead of the enum-based property), and there is some additional evidence from the Mongo default configuration.

`MongoDefaultBatchConfiguration` configures the `MongoJobRepositoryFactoryBean` like this:

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

Here the isolation level is passed via the enum-based setter:

```java
jobRepositoryFactoryBean.setIsolationLevelForCreateEnum(getIsolationLevelForCreate());
```

So the `Isolation` value is clearly meant to go through `setIsolationLevelForCreateEnum`.

On the other hand, in `BatchRegistrar.registerMongoJobRepository`, the value from `@EnableMongoJobRepository#isolationLevelForCreate` (which is an `Isolation` enum) is currently bound to the **String** property `isolationLevelForCreate`:

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreate", isolationLevelForCreate);
}
```

This ends up invoking `setIsolationLevelForCreate(String)` internally and going through `TransactionAttributeEditor`, which expects tokens like `ISOLATION_SERIALIZABLE`. With the enum being converted to `"SERIALIZABLE"`, this leads to:

> Invalid transaction attribute token: [SERIALIZABLE]

For JDBC, the registrar already uses the enum-based property:

```java
Isolation isolationLevelForCreate = jdbcJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

and the default Mongo configuration (`MongoDefaultBatchConfiguration`) also uses `setIsolationLevelForCreateEnum`.

So it looks like the Mongo registrar should be using the same enum-based property. Changing it to:

```java
Isolation isolationLevelForCreate = mongoJobRepositoryAnnotation.isolationLevelForCreate();
if (isolationLevelForCreate != null) {
    beanDefinitionBuilder.addPropertyValue("isolationLevelForCreateEnum", isolationLevelForCreate);
}
```

fixes the issue for me.

To guard against regressions, I also added a small test in `BatchRegistrarTests` that bootstraps a context with:

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

and simply asserts that a `JobRepository` is created:

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

With the current code this test fails with `Invalid transaction attribute token: [SERIALIZABLE]`, and with the change to `isolationLevelForCreateEnum` it passes. I’ll open a PR with this change and the test.


### コメント 3 by fmbenhassine

**作成日**: 2025-12-15

@br05s This is valid issue, thank you for reporting it.

Resolved in #5141 and will be shipped in the upcoming v6.0.1. Many thanks to @banseok1216 for the fix 🙏

