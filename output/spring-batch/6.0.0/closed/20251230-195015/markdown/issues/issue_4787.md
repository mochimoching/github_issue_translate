# Elaborate usage of PlatformTransactionManager

**Issue番号**: #4787

**状態**: closed | **作成者**: quaff | **作成日**: 2025-03-19

**ラベル**: in: documentation, type: enhancement, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4787

**関連リンク**:
- Commits:
  - [4e5b7d2](https://github.com/spring-projects/spring-batch/commit/4e5b7d26d802afaadac4c4d00e50f71883423e41)

## 内容

There are many places to configure `transactionManager`, it's unclear whether it's mandatory or not, from my understanding, it's should be optional since `dataSource` is mandatory, Spring Batch could create `DataSourceTransactionManager()` as default, correct me if I'm wrong.

And it's unclear whether it's used for batch metadata operations or JDBC reader/writer of step, if [Spring Boot](https://docs.spring.io/spring-boot/how-to/batch.html)'s `@BatchDataSource` and `@BatchTransactionManager` are used for separated DataSource, which `transactionManager` should be used for `StepBuilder::chunk`?

https://github.com/spring-projects/spring-batch/blob/e1b0f156e4db9ae2c3b60b83ec372dac8bddad68/spring-batch-core/src/main/java/org/springframework/batch/core/step/builder/StepBuilder.java#L118

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-05-22

> Spring Batch could create `DataSourceTransactionManager()` as default, correct me if I'm wrong.

Spring Batch used to do that, but it was causing issues like #816.

> it's unclear whether it's used for batch metadata operations or JDBC reader/writer of step

Those can be different: one can use a `ResourcelessTransactionManager` for meta-data and a `JdbcTransactionManager` for business data.

I will plan to clarify the docs with a note about this.

### コメント 2 by quaff

**作成日**: 2025-05-30

> > Spring Batch could create `DataSourceTransactionManager()` as default, correct me if I'm wrong.
> 
> Spring Batch used to do that, but it was causing issues like [#816](https://github.com/spring-projects/spring-batch/issues/816).


We could use `@Bean(defaultCandidate = false)` now, it will not back off Spring Boot's auto-configured `PlatformTransactionManager`.



### コメント 3 by fmbenhassine

**作成日**: 2025-11-19

> We could use `@Bean(defaultCandidate = false)` now, it will not back off Spring Boot's auto-configured `PlatformTransactionManager`.

For now, there is no plan to make Spring Batch define a transaction manager this way, but I will update the docs to elaborate the usage of this component (the fact that it is optional and that it does not necessarily have to be the same in the step and the job repository).



