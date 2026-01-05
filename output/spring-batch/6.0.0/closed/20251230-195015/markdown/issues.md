# Spring Batch GitHub Issues

取得日時: 2025年12月30日 19:50:15

取得件数: 21件

---

## Issue #4289: Add integration tests for DDL migration scripts

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2023-02-08

**ラベル**: type: task, in: core, related-to: ddl-scripts

**URL**: https://github.com/spring-projects/spring-batch/issues/4289

**関連リンク**:
- Commits:
  - [d79971b](https://github.com/spring-projects/spring-batch/commit/d79971b8a5d44e32bb5ea08c6389b2d20b468396)
  - [b095f10](https://github.com/spring-projects/spring-batch/commit/b095f10caa88c68ea72d2b93af02065a754c199a)
  - [45c175b](https://github.com/spring-projects/spring-batch/commit/45c175b1ba2f4a3488e67e5af0546a597789937e)
  - [1f11625](https://github.com/spring-projects/spring-batch/commit/1f11625d35143495603ddedf10aa8d8acfcdd179)
  - [8608e18](https://github.com/spring-projects/spring-batch/commit/8608e18de568e4f54efe886dec56076180d3f1c1)
  - [ced1cbf](https://github.com/spring-projects/spring-batch/commit/ced1cbf246121f85d771b8d851102cb8d1967c46)
  - [01619c6](https://github.com/spring-projects/spring-batch/commit/01619c6f2d4826962162181d96b2837b204a32e1)
  - [b2c63d3](https://github.com/spring-projects/spring-batch/commit/b2c63d3233f6429bb4990f396975b135ca241a38)
  - [9a422fa](https://github.com/spring-projects/spring-batch/commit/9a422fa57cfea2cf1eda7ece09d0bab776cb6d50)

### 内容

To avoid issues like #4260 and #4271, we need to create integration tests to validate migration scripts. For PostgreSQL, it could be something like this:

```java
/*
 * Copyright 2020-2023 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.batch.core.test.repository;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.postgresql.ds.PGSimpleDataSource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

/**
 * @author Mahmoud Ben Hassine
 */
@Testcontainers
class PostgreSQLMigrationScriptIntegrationTests {

	@Container
	public static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(DockerImageName.parse("postgres:13.3"));

	@Test
	void migrationScriptShouldBeValid() {
		PGSimpleDataSource datasource = new PGSimpleDataSource();
		datasource.setURL(postgres.getJdbcUrl());
		datasource.setUser(postgres.getUsername());
		datasource.setPassword(postgres.getPassword());

		ResourceDatabasePopulator databasePopulator = new ResourceDatabasePopulator();
		databasePopulator.addScript(new ClassPathResource("/org/springframework/batch/core/schema-postgresql-4.sql"));
		databasePopulator.addScript(new ClassPathResource("/org/springframework/batch/core/migration/5.0/migration-postgresql.sql"));

		Assertions.assertDoesNotThrow(() -> databasePopulator.execute(datasource));
	}


}

```

For embedded databases, it could be something like this:

```java
/*
 * Copyright 2020-2023 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.batch.core.repository;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabase;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

/**
 * @author Mahmoud Ben Hassine
 */
class H2MigrationScriptIntegrationTests {

	@Test
	void migrationScriptShouldBeValid() {
		EmbeddedDatabase datasource = new EmbeddedDatabaseBuilder()
				.setType(EmbeddedDatabaseType.H2)
				.addScript("/org/springframework/batch/core/schema-h2-v4.sql")
				.build();

		ResourceDatabasePopulator databasePopulator = new ResourceDatabasePopulator();
		databasePopulator.addScript(new ClassPathResource("/org/springframework/batch/core/migration/5.0/migration-h2.sql"));

		Assertions.assertDoesNotThrow(() -> databasePopulator.execute(datasource));
	}


}
```

NB: Those tests should *not* be part of the CI/CD build. They can be used on demand to validate a migration script when needed.

### コメント

#### コメント 1 by baezzys

**作成日**: 2025-08-04

Hi @fmbenhassine,

I'd like to work on this issue. I can implement integration tests for all databases that have migration scripts (PostgreSQL, H2, MySQL, Oracle, SQL Server, etc.) using TestContainers for external databases and EmbeddedDatabaseBuilder for embedded ones.

#### コメント 2 by fmbenhassine

**作成日**: 2025-08-04

Hi @baezzys ,

Sure! Thank you for your offer to help 🙏

---

## Issue #4732: Inaccurate error message when using ResourcelessJobRepository with a partitioned step

**状態**: closed | **作成者**: monnetchr | **作成日**: 2024-12-10

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4732

**関連リンク**:
- Commits:
  - [69331c5](https://github.com/spring-projects/spring-batch/commit/69331c516dbb95cc23d4340fe083460fc376551e)

### 内容

**Bug description**
The ResourcelessJobRepository cannot be used with a Partitioner:
```
[main] ERROR org.springframework.batch.core.step.AbstractStep - Encountered an error executing step step in job partitionJob
org.springframework.batch.core.JobExecutionException: Cannot restart step from STARTING status.  The old execution may still be executing, so you may need to verify manually that this is the case.
```

**Steps to reproduce**
Simply change `spring-batch-samples/src/main/resources/simple-job-launcher-context.xml` to use `ResourcelessJobRepository` and then run `spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/file/PartitionFileJobFunctionalTests.java`



### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2024-12-10

The resourceless job repository does not support features involving the execution context (including partitioned steps). This is mentioned in the javadocs of the class: https://docs.spring.io/spring-batch/docs/current/api/org/springframework/batch/core/repository/support/ResourcelessJobRepository.html and in the reference docs here: https://docs.spring.io/spring-batch/reference/whatsnew.html#new-resourceless-job-repository

You need to configure another job repository implementation that supports batch-metadata. I am closing this issue now as I believe it answers your concern, but please add a comment if you need more support on this. Thank you.

#### コメント 2 by fmbenhassine

**作成日**: 2024-12-10

I must admit the error message is confusing, there is no restart in that sample yet the message is mentioning restart. I will re-open this issue and change it into an enhancement.

#### コメント 3 by kwondh5217

**作成日**: 2025-03-18

Hi @fmbenhassine, I would like to contribute to this issue.

To improve clarity, would it make sense to explicitly prevent the use of `ResourcelessJobRepository` with partitioned steps by throwing an exception? 

Proposed change:
```java
@Override
public Set<StepExecution> split(StepExecution stepExecution, int gridSize) throws JobExecutionException {
    if (jobRepository instanceof ResourcelessJobRepository) {
        throw new JobExecutionException("ResourcelessJobRepository cannot be used with partitioned steps "
                                        + "as it does not support execution context.");
    }
    ...

#### コメント 4 by fmbenhassine

**作成日**: 2025-11-14

This was fixed as part of 90d895955d951156849ba6fa018676273fdbe2c4.

> **Steps to reproduce**
> Simply change `spring-batch-samples/src/main/resources/simple-job-launcher-context.xml` to use `ResourcelessJobRepository` and then run `spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/file/PartitionFileJobFunctionalTests.java`

I tried that sample with 6.0.0-RC2 and now it prints:

```
12:27:34.354 [main] INFO  o.s.b.c.c.x.CoreNamespaceHandler - DEPRECATION NOTE: The batch XML namespace is deprecated as of Spring Batch 6.0 and will be removed in version 7.0.
12:27:34.566 [main] INFO  o.s.b.c.s.i.ChunkOrientedTasklet - DEPRECATION NOTE: The legacy implementation of the chunk-oriented processing model is deprecated as of Spring Batch 6.0 and will be removed in version 7.0.
12:27:35.250 [main] INFO  o.s.b.c.l.s.TaskExecutorJobLauncher - Job: [FlowJob: [name=partitionJob]] launched with the following parameters: [{JobParameter{name='random', value=1393027390114809605, type=class java.lang.Long, identifying=true}}]
12:27:35.254 [main] INFO  o.s.b.c.j.SimpleStepHandler - Executing step: [step]
12:27:35.286 [SimpleAsyncTaskExecutor-2] INFO  o.s.b.c.s.AbstractStep - Step: [step1:partition1] executed in 28ms
12:27:35.286 [SimpleAsyncTaskExecutor-1] INFO  o.s.b.c.s.AbstractStep - Step: [step1:partition0] executed in 28ms
12:27:35.287 [main] INFO  o.s.b.c.s.AbstractStep - Step: [step] executed in 32ms
12:27:35.288 [main] INFO  o.s.b.c.l.s.TaskExecutorJobLauncher - Job: [FlowJob: [name=partitionJob]] completed with the following parameters: [{JobParameter{name='random', value=1393027390114809605, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 34ms
```

which does not log the confusing error message anymore.

---

## Issue #4787: Elaborate usage of PlatformTransactionManager

**状態**: closed | **作成者**: quaff | **作成日**: 2025-03-19

**ラベル**: in: documentation, type: enhancement, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4787

**関連リンク**:
- Commits:
  - [4e5b7d2](https://github.com/spring-projects/spring-batch/commit/4e5b7d26d802afaadac4c4d00e50f71883423e41)

### 内容

There are many places to configure `transactionManager`, it's unclear whether it's mandatory or not, from my understanding, it's should be optional since `dataSource` is mandatory, Spring Batch could create `DataSourceTransactionManager()` as default, correct me if I'm wrong.

And it's unclear whether it's used for batch metadata operations or JDBC reader/writer of step, if [Spring Boot](https://docs.spring.io/spring-boot/how-to/batch.html)'s `@BatchDataSource` and `@BatchTransactionManager` are used for separated DataSource, which `transactionManager` should be used for `StepBuilder::chunk`?

https://github.com/spring-projects/spring-batch/blob/e1b0f156e4db9ae2c3b60b83ec372dac8bddad68/spring-batch-core/src/main/java/org/springframework/batch/core/step/builder/StepBuilder.java#L118

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-05-22

> Spring Batch could create `DataSourceTransactionManager()` as default, correct me if I'm wrong.

Spring Batch used to do that, but it was causing issues like #816.

> it's unclear whether it's used for batch metadata operations or JDBC reader/writer of step

Those can be different: one can use a `ResourcelessTransactionManager` for meta-data and a `JdbcTransactionManager` for business data.

I will plan to clarify the docs with a note about this.

#### コメント 2 by quaff

**作成日**: 2025-05-30

> > Spring Batch could create `DataSourceTransactionManager()` as default, correct me if I'm wrong.
> 
> Spring Batch used to do that, but it was causing issues like [#816](https://github.com/spring-projects/spring-batch/issues/816).


We could use `@Bean(defaultCandidate = false)` now, it will not back off Spring Boot's auto-configured `PlatformTransactionManager`.



#### コメント 3 by fmbenhassine

**作成日**: 2025-11-19

> We could use `@Bean(defaultCandidate = false)` now, it will not back off Spring Boot's auto-configured `PlatformTransactionManager`.

For now, there is no plan to make Spring Batch define a transaction manager this way, but I will update the docs to elaborate the usage of this component (the fact that it is optional and that it does not necessarily have to be the same in the step and the job repository).



---

## Issue #4791: Unclear reference to example about job parameters in reference documentation

**状態**: closed | **作成者**: quaff | **作成日**: 2025-03-26

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/4791

**関連リンク**:
- Commits:
  - [8020331](https://github.com/spring-projects/spring-batch/commit/8020331dc0a0950f3f759bb520490c9a0ab611fc)

### 内容

https://docs.spring.io/spring-batch/reference/domain.html#jobParameters

>> In the preceding example, where there are two instances, one for January 1st and another for January 2nd, there is really only one Job, but it has two JobParameter objects: one that was started with a job parameter of 01-01-2017 and another that was started with a parameter of 01-02-2017. 

The figure doesn't show two instances of 01-01-2017 and 01-02-2017.

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-19

I think the text references the preceding example from the previous section [JobInstance](https://docs.spring.io/spring-batch/reference/domain.html#jobinstance) to continue the explanation in the current section. Here is the text from the previous section:

```
For example, there is a January 1st run, a January 2nd run, and so on. If the January 1st run fails the first time and is run again the next day, it is still the January 1st run. (Usually, this corresponds with the data it is processing as well, meaning the January 1st run processes data for January 1st). Therefore, each JobInstance can have multiple executions (JobExecution is discussed in more detail later in this chapter), and only one JobInstance (which corresponds to a particular Job and identifying JobParameters) can run at a given time.
```

The text doesn't say "In the preceding figure" or "In this figure, there are two instances". I will update the text with a link to the previous section where the example is first introduced.

---

## Issue #4859: Clarify MongoDB job repository configuration in reference documentation

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-03

**ラベル**: in: documentation, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4859

**関連リンク**:
- Commits:
  - [17bc8f7](https://github.com/spring-projects/spring-batch/commit/17bc8f70087e9e264c65551f47c1ea6601c53905)

### 内容

As of v5.2, the prerequisite for using MongoDB as a job repository is not documented in details in the [Configuring a JobRepository](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html) section. There is a note about that in the [What’s new in Spring Batch 5.2](https://docs.spring.io/spring-batch/reference/whatsnew.html#mongodb-job-repository-support) section but that is not clear enough.

The reference documentation should clarify the DDL script to execute against MongoDB before running jobs as well any other necessary configuration for things to work correctly (thinking about the `MapKeyDotReplacement` that has to be defined in the mongo converter for instance).

---

## Issue #4916: RecordFieldExtractor in FlatFileItemWriterBuilder doesn't reflect names() setting

**状態**: closed | **作成者**: kyb4312 | **作成日**: 2025-07-18

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4916

**関連リンク**:
- Commits:
  - [8f56f93](https://github.com/spring-projects/spring-batch/commit/8f56f9379149ee3d8ac08910be2cdf3125cc1d0f)
  - [0eeacd5](https://github.com/spring-projects/spring-batch/commit/0eeacd583ffbb2d47dd6ed9bc76f914fd320b496)

### 内容

This is related to [spring-projects/spring-batch#4908](https://github.com/spring-projects/spring-batch/issues/4908), which points out that using names() with a record type and sourceType() might seem redundant. While that discussion raises a valid concern, this issue is coming from a slightly different angle: it would be helpful if the names() setting actually worked when a record is used with sourceType(). That way, developers wouldn't be surprised when their field selections are silently ignored.

---
### **Bug description**
When using FlatFileItemWriterBuilder’s build() method with sourceType() set to a record class and specifying field names via names(), the RecordFieldExtractor used internally ignores the names() configuration.
In contrast, when sourceType() is not specified, the BeanWrapperFieldExtractor honors the names() configuration as expected.

This inconsistency can cause confusion, as the same record type behaves differently depending on whether sourceType() is provided.

---
### **Steps to reproduce**
```
public record MyRecord(String name, int age, String address) {}

FlatFileItemWriter<MyRecord> writer = new FlatFileItemWriterBuilder<MyRecord>()
    .name("myRecordWriter")
    .resource(new FileSystemResource("output.csv"))
    .sourceType(MyRecord.class)  // triggers RecordFieldExtractor
    .names("name", "age")        // currently ignored
    .delimited()
    .build();
```
Expected output: name, age
Actual output: name, age, address

---
### **Suggested Fix**

Update the builder to pass names into RecordFieldExtractor:

FlatFileItemWriterBuilder.build()

Before:
```
if (this.sourceType != null && this.sourceType.isRecord()) {
    this.fieldExtractor = new RecordFieldExtractor<>(this.sourceType);
}
```

After:
```
if (this.sourceType != null && this.sourceType.isRecord()) {
    RecordFieldExtractor<T> extractor = new RecordFieldExtractor<>(this.sourceType);
    extractor.setNames(this.names.toArray(new String[this.names.size()]));
    this.fieldExtractor = extractor;
}
```
This would make the behavior consistent and avoid surprises.

---
Let me know if you'd like a pull request with this change - I'd be happy to help!

powerd by KILL-9 💀

### コメント

#### コメント 1 by LeeHyungGeol

**作成日**: 2025-10-04

Hello @fmbenhassine.

Would it be okay if i give it a try on this issue?

#### コメント 2 by fmbenhassine

**作成日**: 2025-10-04

@LeeHyungGeol Sure! thank you for your offer to help 🙏

#### コメント 3 by LeeHyungGeol

**作成日**: 2025-10-04

@fmbenhassine 

I've created a PR https://github.com/spring-projects/spring-batch/pull/5009 to address this issue. Could you please assign this issue to me?

Also, I noticed this issue is closely related to https://github.com/spring-projects/spring-batch/issues/4908. I'd greatly appreciate it if you could review them together.

Thank you!

---

## Issue #4983: Add migration scripts for v6

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-09-23

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-batch/issues/4983

**関連リンク**:
- Commits:
  - [2c30f14](https://github.com/spring-projects/spring-batch/commit/2c30f147c2ea3e741fb0a262fd03b90eecaaa16b)

### 内容

Currently, here are the issues that might require a migration script:

- #4977

---

## Issue #5026: Document requirements of CommandLineJobOperator in the reference docs

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-15

**ラベル**: in: documentation, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5026

**関連リンク**:
- Commits:
  - [acc48a3](https://github.com/spring-projects/spring-batch/commit/acc48a3a3bc76ae85e0d936f260e5e6594c7ba9a)

### 内容

Hello Spring Batch team,

Thank you for all your great work on Spring Batch 6! I've been testing the milestone releases and came across what might be an issue or a documentation gap regarding `CommandLineJobOperator` and `JobRegistry` configuration.


**Bug description**
After [#4971](https://github.com/spring-projects/spring-batch/issues/4971), `JobRegistry` was made optional and is no longer automatically registered as a bean in Spring Batch configuration. 

However, `CommandLineJobOperator` (introduced in [#4899](https://github.com/spring-projects/spring-batch/issues/4899)) explicitly requires a `JobRegistry` bean from the `ApplicationContext`, causing it to fail with both `@EnableBatchProcessing` and `DefaultBatchConfiguration`.

**Environment**
- Spring Batch version: 6.0.0-M4


**Steps to reproduce** / **Minimal Complete Reproducible example**
**With `DefaultBatchConfiguration`:**
```java
@Configuration
public class BatchConfig extends DefaultBatchConfiguration {
    // No JobRegistry bean
}
```

**Or with `@EnableBatchProcessing`:**
```java
@Configuration
@EnableBatchProcessing
public class BatchConfig {
    // No JobRegistry bean
}
```

**Then run:**
```bash
java CommandLineJobOperator my.package.BatchConfig start myJob
```

**Result:** Application fails with error.

**Expected behavior**
`CommandLineJobOperator` should work with the default Spring Batch configuration, or the documentation should clearly state that manual `JobRegistry` bean registration is required.

**Actual behavior**
Application fails with:
```
A required bean was not found in the application context: 
No qualifying bean of type 'org.springframework.batch.core.configuration.JobRegistry' available
```

**Error location:**
The error occurs in `CommandLineJobOperator.main()` at line 314:
```java
public static void main(String[] args) {
    ...
    jobRegistry = context.getBean(JobRegistry.class);  // ← Fails here (line 314)
    ...
}

**Current Workaround**
Users must manually register `JobRegistry` as a bean:

**With `DefaultBatchConfiguration`:**
```java
@Configuration
public class BatchConfig extends DefaultBatchConfiguration {
    
    @Bean
    public JobRegistry jobRegistry() {
        return new MapJobRegistry();
    }
    
    @Override
    protected JobRegistry getJobRegistry() {
        return applicationContext.getBean(JobRegistry.class);
    }
}
```

**Question**
Is this the intended behavior? Since #4971 made `JobRegistry` optional, we're wondering if `CommandLineJobOperator` is expected to require manual `JobRegistry` bean registration, or if this is an unintended side effect.

If manual registration is the intended approach, it would be very helpful to have this documented with examples for both configuration styles (`@EnableBatchProcessing` and `DefaultBatchConfiguration`).

would appreciate any clarification on the expected usage pattern. Thank you!


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

Thank you for reporting this issue. I think this is documented in the Javadoc of the class, here is an excerpt:

```
This utility requires a Spring application context to be set up with the necessary batch infrastructure, including a `JobOperator`, a `JobRepository`, and a `JobRegistry` populated with the jobs to operate.
```

When the job registry bean is not defined in the context, the user should get this message (see [here](https://github.com/spring-projects/spring-batch/blob/4646a4479a44ae1d836f7053c41c4af09f7a9e1a/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/CommandLineJobOperator.java#L319-L330)):

```
A required bean was not found in the application context: [...]
```



> I've been testing the milestone releases and came across what might be an issue or a documentation gap regarding `CommandLineJobOperator` and `JobRegistry` configuration.

So I guess this is not an issue but a documentation gap, we need to update the reference docs in addition to the javadoc. I will turn this into a documentation enhancement.

#### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-11-17

Thank you for your clear response.

I agree with your assessment that this is a documentation gap rather than a technical issue, and I appreciate you turning it into a documentation enhancement ticket!

---

## Issue #5057: `CommandLineJobOperator` improve state validation for restart/abandon and enhance logging

**状態**: closed | **作成者**: ch200203 | **作成日**: 2025-10-29

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5057

### 内容


### Expected Behavior
- **Abandon**: Only allow when execution is **STOPPED**; otherwise log the current status and return a generic error exit code.
- **Restart**: Only allow when execution is **FAILED** or **STOPPED**; otherwise log the current status and return a generic error exit code.
- Resolve the TODOs in `CommandLineJobOperator` by performing explicit precondition checks at the CLI layer without relying on deprecated exceptions.

### Current Behavior
- `abandon(jobExecutionId)`: Delegates to `JobOperator#abandon` without enforcing **STOPPED** at the CLI level. A TODO mentions throwing `JobExecutionNotStoppedException`, but that exception is deprecated.
- `restart(jobExecutionId)`: Contains a TODO to check/log when the job execution “did not fail,” but does not enforce valid restart states at the CLI level.

### Context
- **Motivation**: Align CLI precondition checks with Spring Batch semantics and the inline TODOs, prevent invalid operations earlier, and improve observability with clear error logs that include the current status.
- **Alternative considered**: Throwing `JobExecutionNotStoppedException`, but it is deprecated; the CLI should use exit codes and logging instead.
- **Compatibility**: No API change; behavior becomes explicit and predictable. Invalid operations return `JVM_EXITCODE_GENERIC_ERROR` rather than relying on downstream exceptions.

### Proposed Change
- In `spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/CommandLineJobOperator.java`:
    - `restart(long jobExecutionId)`: Enforce `FAILED` or `STOPPED`; otherwise log current status and return generic error.
    - `abandon(long jobExecutionId)`: Enforce `STOPPED`; otherwise log current status and return generic error.

### Previous Code (before change)
- `restart(long jobExecutionId)`: Only TODO present; no state check; directly delegates to `jobOperator.restart(jobExecution)`.

```java
// TODO should check and log error if the job execution did not fail
JobExecution restartedExecution = this.jobOperator.restart(jobExecution);
return this.exitCodeMapper.intValue(restartedExecution.getExitStatus().getExitCode());
```

- `abandon(long jobExecutionId)`: Only TODO present; no state check; directly delegates to `jobOperator.abandon(jobExecution)`.

```java
// TODO should throw JobExecutionNotStoppedException if the job execution is
// not stopped
JobExecution abandonedExecution = this.jobOperator.abandon(jobExecution);
return this.exitCodeMapper.intValue(abandonedExecution.getExitStatus().getExitCode());
```

A corresponding pull request has been carefully prepared to demonstrate this improvement.  
I would appreciate it if the team could review and provide feedback when possible.

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

Resolved with #5058

---

## Issue #5064: SQL Server DDL for metadata tables should use NVARCHAR to prevent performance degradation and deadlocks from implicit conversion

**状態**: closed | **作成者**: Chienlin1014 | **作成日**: 2025-10-30

**ラベル**: in: core, type: enhancement, related-to: ddl-scripts

**URL**: https://github.com/spring-projects/spring-batch/issues/5064

**関連リンク**:
- Commits:
  - [ee050d6](https://github.com/spring-projects/spring-batch/commit/ee050d66b0f00f7e03365835f160d4a3f133bda1)
  - [525d9b0](https://github.com/spring-projects/spring-batch/commit/525d9b0ee640898a6cf11f844e365adfb19b6dee)

### 内容

 Hello Spring Batch Team,

  I'm reporting a significant performance issue and a potential for deadlocks when using Spring Batch with a SQL Server database. The root cause is a data type mismatch between the default
   Spring Batch schema and the default behavior of the Microsoft JDBC driver.

  The Problem

  The default DDL for SQL Server metadata tables (e.g., BATCH_JOB_INSTANCE's JOB_NAME, JOB_KEY) defines these columns as VARCHAR. However, the Microsoft JDBC Driver for SQL Server sends
  string parameters as NVARCHAR by default.

  This mismatch forces SQL Server to perform an implicit data type conversion (CONVERT_IMPLICIT) on the VARCHAR column for every comparison.

  Impact: Performance Degradation and Deadlocks

  This implicit conversion prevents efficient index usage. The query optimizer, despite showing an Index Seek operation, actually performs a costly range scan due to the CONVERT_IMPLICIT
  in the WHERE clause and the use of GetRangeThroughConvert to define a search range. This behavior leads to substantial performance degradation that worsens linearly with data growth.

  This severe performance degradation causes transactions to hold locks for much longer. Under high concurrency, this dramatically increases lock contention and the risk of deadlocks. We
  have confirmed these deadlocks occur even at the READ COMMITTED isolation level, as the range scan acquires broader range locks, leading to mutual waiting during INSERT attempts.

  Proposed Solution

  To resolve this at its root, I propose updating the schema-sqlserver.sql file to change all relevant string columns in the metadata tables from `VARCHAR` to `NVARCHAR`. This aligns the
  database schema with the JDBC driver's default behavior, ensuring efficient index usage and preventing these performance and deadlock issues.

  Thank you for your consideration.


---

## Issue #5072: Document how to migrate usage of EnableBatchProcessing(modular = true) to v6

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-11-02

**ラベル**: in: documentation, type: task

**URL**: https://github.com/spring-projects/spring-batch/issues/5072

### 内容

This is related to #4866. The goal is to document how to migrate the use of `EnableBatchProcessing(modular = true)` to  Spring's context hierarchies and `GroupAwareJob`s (as mentioned in the javadoc of `EnableBatchProcessing`).

cc @kzander91 (who provided a starting point in https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3478015935, thank you for that!)


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-19

Added example here: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide#changes-related-to-the-modular-batch-configurations-through-enablebatchprocessingmodular--true

#### コメント 2 by kzander91

**作成日**: 2025-11-25

@fmbenhassine I just had a chance to take a look at the example, and I find it a bit lacking:
* The old, modular implementation was also managing the lifecycle of the child contexts, properly shutting everything down when the parent context was closed. I would now have to reimplement that myself.
* Previously, through the parent context's `JobLocator`, I was able to retrieve the child context's `Job` by name. This is now no longer possible and my logic that is launching jobs would somehow need to get a hold of the child contexts... Especially this issue is I believe also relevant for @marbon87's [case in their app](https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3575452892).

I feel like the only proper migration path for all but the simplest of apps is either to _not_ use separate contexts and define all Job's in a shared context (likely they way I will be going), or to copy-paste Spring Batch's implementation from the previous version.

#### コメント 3 by fmbenhassine

**作成日**: 2025-12-08

@kzander91 Thank you looking into that and for your feedback!

> * The old, modular implementation was also managing the lifecycle of the child contexts, properly shutting everything down when the parent context was closed. I would now have to reimplement that myself.

That feature is already implemented in Spring Boot and was duplicated in Spring Batch for no reason. Have you tried `new SpringApplicationBuilder(ParentConfig.class).child(ChildConfig.class).run(args);` from Boot? This will handle the lifecycle of the contexts for you.

>  Previously, through the parent context's JobLocator, I was able to retrieve the child context's Job by name. This is now no longer possible and my logic that is launching jobs would somehow need to get a hold of the child contexts

I think that that was due to #5122 which I already fixed and planned for the upcoming v6.0.1. With that fix in place, the `MapJobRegistry` can be populated with jobs from all contexts and the registration will be based on the job names (which should be globally unique anyway) and not the bean name (which could be the same in child contexts).

---

Another option I forgot about is using Spring profiles. I believe this is suitable for this kind of setup. Have you tried that approach? I can help with an example here as well. Just let me know if you need support on that.


#### コメント 4 by kzander91

**作成日**: 2025-12-08

> Have you tried new `SpringApplicationBuilder(ParentConfig.class).child(ChildConfig.class).run(args);` from Boot?

I have, but that doesn't really work in my scenario, because I'm running an embedded Tomcat in my parent context, which Spring Boot doesn't support: https://github.com/spring-projects/spring-boot/blob/1c0e08b4c434b0e77a83098267b2a0f5a3fc56d7/core/spring-boot/src/main/java/org/springframework/boot/builder/SpringApplicationBuilder.java#L207-L210
Now I _could_ put the rest of my project in another child context, but again in both of these cases I wouldn't be able to see the Job beans from the child or sibling contexts (I'm launching jobs by name from a central service bean, and that bean thus needs to know all Jobs).

> With that fix in place, the `MapJobRegistry` can be populated with jobs from all contexts

I don't think that's true. Parent contexts are not aware of their child contexts, it's a unidirectional relationship (unless I'm missing something). `MapJobRegistry` _could_ get Job beans from its own _and its parent context(s)_, but it isn't because it's using `getBeansOfType()` which isn't considering beans from parent contexts: https://github.com/spring-projects/spring-batch/blob/088487bb803c6a7a9139228ea973035a1698d864/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/support/MapJobRegistry.java#L63-L66
Docs of `getBeansOfType()`: https://github.com/spring-projects/spring-framework/blob/b038beb85490c8a80711b1a6c8cfffbb21276b3e/spring-beans/src/main/java/org/springframework/beans/factory/ListableBeanFactory.java#L267-L269
But in any case: This would only find beans from the context that `MapJobRegistry` is running in and its parent(s), but not children/siblings.

> Another option I forgot about is using Spring profiles.

Are you talking about putting all beans in a single context and guarding each job's configuration with a profile? 🤔 I don't really see how this would help. At runtime, my app needs to know all Jobs anyways and so would need to enable all these profiles...

#### コメント 5 by fmbenhassine

**作成日**: 2025-12-09

> that doesn't really work in my scenario, because I'm running an embedded Tomcat in my parent context, which Spring Boot doesn't support

OK I see. The fact that you are embedding Tomcat in the parent context is an important detail, which was not mentioned in your initial request nor present in the minimal example you shared (all my previous answers were based on the assumption that you have a non-web setup). But no problem, I will provide guidance for your case.

First thing: modularisation of Spring contexts to avoid bean name clashes is definitely NOT a Spring Batch concern. Trying to do this in Spring Batch with `EnableBatchProcessing(modular = true)` or any other way would definitely lead to an overly complex code to maintain or at best, worse than any solution provided by Spring Framework or Spring Boot. And BTW, this problem is not specific to Spring Batch per se, and could be encountered in any other project where users can define project-specific named artefacts as Spring beans (Like integration flows in Spring Integration or shell commands in Spring Shell, etc).

Now the fact that Spring Boot does not support your use case becomes a Spring Boot issue, not a Spring Batch issue. And more importantly, I believe it is this setup of running several batch jobs in a servlet container within a single JVM that makes things difficult (I personally never recommended that setup, and always promoted the "single job per context per jar" packaging/deployment model). That monolithic model was used in Spring Batch Admin which had several issues that led the project to be deprecated in favor of the modular approach in SCDF (see issues and migration recommendations [here](https://github.com/spring-attic/spring-batch-admin/blob/master/MIGRATION.md)).

That said, you can still continue to use the web model you have, but you definitely need a smarter job registry than the one provided by Spring Batch. 

> Parent contexts are not aware of their child contexts, it's a unidirectional relationship (unless I'm missing something). MapJobRegistry could get Job beans from its own and its parent context(s), but it isn't because it's using getBeansOfType() which isn't considering beans from parent contexts

I am open to making `MapJobResgitry` smarter to handle bidirectional relationships if this does not break things for most typical use cases. But if this will make the code on the framework side overly complex for a very specific use case, then I would leave that to users to provide their own custom smart registry. I always try to control how much accidental complexity goes in the framework (which is one of the main themes of v6 BTW).

> Are you talking about putting all beans in a single context and guarding each job's configuration with a profile? 🤔 I don't really see how this would help. At runtime, my app needs to know all Jobs anyways and so would need to enable all these profiles...

Please forget about profiles for your use case, it won't work with a web setup. As mentioned, I was assuming a non-web setup and thought you would spin up each job in its own context/JVM, and in which case you would specify the profile at startup to only load the bean definitions for that specific job.

---

Looking forward to your feedback and if I can help further.


#### コメント 6 by kzander91

**作成日**: 2025-12-10

Thank you for your continued input and your explanations! 🙏

> The fact that you are embedding Tomcat in the parent context is an important detail, which was not mentioned in your initial request nor present in the minimal example you shared

True, sorry about that. I wasn't aware that this particular detail would be an issue (and therefore relevant), I just found out about that limitation when trying your suggestion with Boot's `SpringApplicationBuilder#child`.

> Looking forward to your feedback

Given the additional context and reasoning you provided I can understand better _why_ you have decided to remove that support. Before, it just seemed that a feature that was working perfectly fine (and on the surface didn't appear to be _that_ complex) was "just" removed to reduce complexity.

Regarding the other points, I want to say again (see https://github.com/spring-projects/spring-batch/issues/5126#issuecomment-3611770749) that I have already refactored my app to define all jobs in a single context.
Thus, I _personally_ have no further need for migration help regarding the removed support for modularized contexts and am fine with stopping things here.

For others that are considering doing the same: I basically just removed my `ApplicationContextFactory` beans and adjusted my root component scan to include all my job configurations.
Inside those, I renamed beans to ensure that no bean name clashes exist.
A few additional adjustments were needed in some places that are specific to my particular app, so YMMV.

---

## Issue #5077: ChunkOrientedStepBuilder: Default SkipPolicy should be NeverSkipItemSkipPolicy when only retry is configured (not AlwaysSkipItemSkipPolicy)

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5077

**関連リンク**:
- Commits:
  - [ce7e03a](https://github.com/spring-projects/spring-batch/commit/ce7e03acf9766983019be34e3b2a633756b5669f)
  - [e77e21c](https://github.com/spring-projects/spring-batch/commit/e77e21cb7926f4689b9903bb65ae81bc80a56e7a)

### 内容

Hi Spring Batch team,

I think I've found an unexpected behavior change in Spring Batch 6 regarding the default skip policy when only retry is configured.


**Bug description**

When configuring only retry settings without any skip configuration, the default `SkipPolicy` is set to `AlwaysSkipItemSkipPolicy`. This causes all items that fail after exhausting retry attempts to be silently skipped instead of failing the step, which seems unintended.


**Environment**

- Spring Batch version: 6.0.0-RC2


**Steps to reproduce**
1. Configure a chunk-oriented step with retry but WITHOUT skip configuration:


2. Throw an exception from processor that exceeds retry limit

4. Observe that the item is skipped instead of failing the step


**Expected behavior**
When only retry is configured without any skip settings, items that fail after exhausting all retry attempts should **fail the step**, not be skipped.

The default `SkipPolicy` should be `NeverSkipItemSkipPolicy` (or equivalent) when skip is not explicitly configured.

**Root cause **

In `ChunkOrientedStepBuilder`:
```java
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new AlwaysSkipItemSkipPolicy(); // ← This seems wrong
    }
}
```

When neither `skippableExceptions` nor `skipLimit` is configured, it defaults to `AlwaysSkipItemSkipPolicy`, causing unexpected skip behavior.


**Comparison with Spring Batch 5**

In Spring Batch 5's `FaultTolerantStepBuilder`:
```java
if (skipPolicy == null) { // default == null
    if (skippableExceptionClasses.isEmpty() && skipLimit > 0) {
        logger.debug(String.format(
            "A skip limit of %s is set but no skippable exceptions are defined.",
            skipLimit));
    }
    skipPolicy = limitCheckingItemSkipPolicy; 
}
```

This would result in step failure when retry is exhausted without skip configuration.


**Suggested fix**
Change the default `SkipPolicy` to `NeverSkipItemSkipPolicy` when skip is not configured:
```java
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new NeverSkipItemSkipPolicy(); // ← Should be this
    }
}
```

**Minimal Complete Reproducible example**
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository
    ) {
        return new StepBuilder(jobRepository)
                .<String, String>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retry(ProcessingException.class)
                .retryLimit(2)
                // No skip configuration - expecting step to fail after retry exhausted
                .build();
    }

    @Bean
    public ItemReader<String> issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor<String, String> issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("Exception thrown for: {}", item);
                throw new ProcessingException("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter<String> issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }

    public static class ProcessingException extends RuntimeException {
        public ProcessingException(String message) {
            super(message);
        }
    }

}

**Actual behavior **

```bash
Executing step: [issueReproductionStep]
Successfully processed: Item_1
Successfully processed: Item_2
Exception thrown for: Item_3
Exception thrown for: Item_3
Exception thrown for: Item_3
Writing items: [Item_1, Item_2]
Written: Item_1
Written: Item_2
Step: [issueReproductionStep] executed in 2s13ms
```

Could you please review this behavior? If you have any questions or need additional information, please feel free to let me know.

Thank you for your time and consideration!





### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-13

That's correct, by default we should never skip items until explicitly requested by the user. Should be fixed now. Thank you for raising this!

---

## Issue #5078: ChunkOrientedStepBuilder: All Throwables (including Errors) are retried when only retryLimit() is configured without retry()

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5078

**関連リンク**:
- Commits:
  - [4d6a5fa](https://github.com/spring-projects/spring-batch/commit/4d6a5fa39b223226a73330498024857cb34d6046)
  - [638c183](https://github.com/spring-projects/spring-batch/commit/638c1834fa1e88ed5017c3081f94e61205289e92)
  - [f606e6f](https://github.com/spring-projects/spring-batch/commit/f606e6f31c9ce6334183384485f14422e124a685)
  - [8ed93d1](https://github.com/spring-projects/spring-batch/commit/8ed93d1900b5a6d0a17e8a1ad1355c1d30e5c918)

### 内容

Hello Spring Batch team,
Following up on previous issue #5068, I discovered a related but opposite scenario that poses a potential risk.

While reviewing the fix for #5068, I realized that when `retryLimit()` is configured **without** `retry()`, all Throwables (including critical Errors like `OutOfMemoryError`, `StackOverflowError`) become retryable. It would have been great to catch this alongside the previous issue.


**Bug description**
When configuring `retryLimit()` without specifying `retry()` in Spring Batch 6, the retry mechanism attempts to retry **all Throwables**, including critical JVM Errors. This occurs because `ExceptionTypeFilter`(used by `DefaultRetryPolicy`) uses `matchIfEmpty = true` when both `includes`(configured by retry()) and `excludes` are empty.


**Environment**
- Spring Batch version: 6.0.0-RC2


**Steps to reproduce**
1. Configure a chunk-oriented step with `retryLimit()` but WITHOUT `retry()`:
@Bean
public Step step() {
    return new StepBuilder("step", jobRepository)
        .chunk(10, transactionManager)
        .reader(reader())
        .processor(processor())
        .writer(writer())
        .faultTolerant()
        .retryLimit(3)
        // No retry() configuration
        .build();
}

2. Throw a critical Error (e.g., `OutOfMemoryError`) from any component(ItemReader or ItemProcessor etc)
3. Observe that even critical Errors are being retried



**Expected behavior**
When only `retryLimit()` is configured without `retry()`:
- Either no exceptions should be retried
- Or only `Exception` and its subclasses should be retried (excluding `Error`)

**Actual behavior**
All Throwables (including Errors) are retried due to `matchIfEmpty = true`.

**Minimal Complete Reproducible example**
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        return new StepBuilder(jobRepository)
                .chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retryLimit(2)
                // No retry() - expecting no retry or Exception-only retry
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("OutOfMemoryError thrown for: {}", item);
                throw new OutOfMemoryError("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }
}
```


**Actual output:**
```
Successfully processed: Item_1
Successfully processed: Item_2
OutOfMemoryError thrown for: Item_3
OutOfMemoryError thrown for: Item_3  ← Retry 1
OutOfMemoryError thrown for: Item_3  ← Retry 2
Writing items: [Item_1, Item_2] ← Item_3 is skipped and writer proceeds (reported separately in #5077)
Written: Item_1
Written: Item_2


The `OutOfMemoryError` is retried 2 times, which could worsen the system state.

**Root cause analysis**
In `ChunkOrientedStepBuilder`:
```java
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(this.retryableExceptions)  // ← Empty set!
          .build();
    }
    else {
       this.retryPolicy = throwable -> false;
    }
}

When `retryableExceptions` is empty, `DefaultRetryPolicy` uses `ExceptionTypeFilter` with both `includes` and `excludes` empty.
In `ExceptionTypeFilter.matchTraversingCauses()`:
```java
private boolean matchTraversingCauses(Throwable exception) {
    boolean emptyIncludes = super.includes.isEmpty();
    boolean emptyExcludes = super.excludes.isEmpty();

    if (emptyIncludes && emptyExcludes) {
        return super.matchIfEmpty;  // ← Returns true!
    }
    // ...
}
```

Since `matchIfEmpty = true`, **all Throwables match**, including critical Errors.

**Suggested fix**

When `retryLimit()` is configured without `retry()`, default to `Exception.class` to exclude Errors:
```java
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       Set<Class> exceptions = this.retryableExceptions.isEmpty()
             ? Set.of(Exception.class)
             : this.retryableExceptions;

       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(exceptions)
          .build();
    }
    else {
       this.retryPolicy = throwable -> false;
    }
}
```

This ensures:
- Only `Exception` and its subclasses are retried by default
- Critical JVM Errors are not retried
- Users can still explicitly include specific exceptions via `retry()`



Could you please review this behavior? This seems like a potential risk when users configure retry limits without specifying which exceptions to retry.

Thank you for your time and consideration!

---

## Issue #5079: ChunkOrientedStep does not throw exception when skipPolicy.shouldSkip() returns false

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-07

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5079

**関連リンク**:
- Commits:
  - [946f788](https://github.com/spring-projects/spring-batch/commit/946f78825414b872f3d27110ff53347a86d362e5)
  - [97065fc](https://github.com/spring-projects/spring-batch/commit/97065fc40256ac18388f8ebdd157e7c744bc1a6a)

### 内容

Hi Spring Batch team,

I think, I’ve discovered a bug in `ChunkOrientedStep` where failed items are silently discarded when the skip policy rejects skipping.

## Bug description

When retry is exhausted in fault-tolerant mode, `ChunkOrientedStep` calls `skipPolicy.shouldSkip()` to determine whether the failed item should be skipped. However, when `skipPolicy.shouldSkip()` returns `false` (meaning the item should NOT be skipped), the code does not throw an exception. This causes the failed item to be silently lost, and the job continues as if nothing happened.

This affects three methods in `ChunkOrientedStep`:
- `doSkipInRead()` (line 528)
- `doSkipInProcess()` (line 656)
- `scan()` (line 736)

## Environment

- Spring Batch version: 6.0.0-RC2

## Steps to reproduce
1. Configure a fault-tolerant step with a skip policy that always returns `false` (never skip)
2. Configure retry with a limited number of attempts (e.g., retryLimit = 2)
3. Process items where one item consistently fails
4. After retry exhaustion, observe that the failed item is silently discarded instead of causing the job to fail

## Expected behavior

When `skipPolicy.shouldSkip()` returns `false`, the exception should be re-thrown to:
- Roll back the transaction
- Mark the step as FAILED
- Prevent silent data loss

The job should fail with a clear error indicating that the skip limit was exceeded or skip policy rejected skipping.

## Minimal Complete Reproducible example
```java

@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        return new StepBuilder(jobRepository)
                .<String, String>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retryLimit(2)
                .skipPolicy(new NeverSkipItemSkipPolicy())  
                .build();
    }

    @Bean
    public ItemReader<String> issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor<String, String> issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("Exception thrown for: {}", item);
                throw new ProcessingException("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter<String> issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }

    public static class ProcessingException extends RuntimeException {
        public ProcessingException(String message) {
            super(message);
        }
    }
}
```

**Actual output:**
Step COMPLETED

```
Job: [SimpleJob: [name=issueReproductionJob]] launched with the following parameters: [{}]
Executing step: [issueReproductionStep]
Successfully processed: Item_1
Successfully processed: Item_2
Exception thrown for: Item_3
Exception thrown for: Item_3
Exception thrown for: Item_3
Writing items: [Item_1, Item_2]
Written: Item_1
Written: Item_2
Step: [issueReproductionStep] executed in 2s18ms
Job: [SimpleJob: [name=issueReproductionJob]] completed with the following parameters: [{}] and the following status: [COMPLETED] in 2s20ms
```

As you can see, `Item_3` failed 3 times (initial attempt + 2 retries), but was silently discarded. The job completed successfully with status `COMPLETED`, even though `NeverSkipItemSkipPolicy` should have rejected skipping.

**Expected output:**
The job should fail with status `FAILED` because the skip policy does not allow skipping the failed item.

---

**Proposed fix:**

The three affected methods should throw an exception when `skipPolicy.shouldSkip()` returns `false`:
```java
private void doSkipInRead(RetryException retryException, StepContribution contribution) {
    Throwable cause = retryException.getCause();
    if (this.skipPolicy.shouldSkip(cause, contribution.getStepSkipCount())) {
        this.compositeSkipListener.onSkipInRead(cause);
        contribution.incrementReadSkipCount();
    } else {
        throw new NonSkippableReadException("Skip policy rejected skipping", cause);
    }
}
```

Similar changes should be applied to `doSkipInProcess()` and the catch block in `scan()`.

Thank you for your attention to this issue!

### コメント

#### コメント 1 by JunggiKim

**作成日**: 2025-11-08

Created pull request #5081 to fix this issue

#### コメント 2 by fmbenhassine

**作成日**: 2025-11-13

I think I misunderstood this bug report when I reacted with 👍 on the issue description.

> when `skipPolicy.shouldSkip()` returns `false` (meaning the item should NOT be skipped), the code does not throw an exception

Why should it throw an exception in that case? That is not an exceptional behaviour. Skipping an item means calling the `SkipListener` for it. Not skipping an item means discarding it (ie ignore it without calling the `SkipListener` for it).

The example you shared uses a `NeverSkipItemSkipPolicy`, which means never call `SkipListener` for any item that exhausted the retry policy, which effectively means ignore all these items (it is not a data loss, it is an explicit ask to not skip items but rather to ignore them). 

Therefore, and unless I am missing something, I think the current behaviour is correct. Do you agree?



#### コメント 3 by KILL9-NO-MERCY

**作成日**: 2025-11-14

@fmbenhassine 

Based on my understanding of Spring Batch 5’s FaultTolerantChunkProvider and FaultTolerantChunkProcessor, 

the behavior was as follows:
- With skipping off, exceptions in ItemReader / ItemProcessor / ItemWriter are propagated to the step, causing it to fail.
- With skipping on, if the SkipPolicy allows skipping, the exception is swallowed for that item only, and processing continues.
- With skipping on, if the SkipPolicy disallows skipping, the exception is propagated(actually wrapped in a RetryException), causing the step to fail.

This aligns with my expectation when raising this issue (even in Batch 5, non-skippable exceptions could be ignored only by explicitly using the noRollback() method on the FaultTolerantStepBuilder).

In Batch 6, while changes to the behavior are understandable as a design decision, I am concerned that failed items may be silently discarded when the SkipPolicy disallows skipping, potentially causing data loss. I would expect the step to fail in such cases, consistent with Batch 5 behavior.

#### コメント 4 by fmbenhassine

**作成日**: 2025-11-14

Thank you for the clarification! I previously said "unless I am missing something, I think the current behaviour is correct", and indeed I was missing an important detail: the skip policy contract clearly mentions that when the method `shouldSkip` returns false, the processing should NOT continue (ie the step should fail):

```
@FunctionalInterface
public interface SkipPolicy {

	/**
	 * Returns true or false, indicating whether or not processing should continue with the given throwable. 
	 * [...]
	 * @return true if processing should continue, false otherwise.
         [...]
	 */
	boolean shouldSkip(Throwable t, long skipCount) throws SkipLimitExceededException;

}
```

So this is a valid issue and should be fixed. The PR #5081 LGTM and I will merge it for the GA.

Thank you for your feedback!



#### コメント 5 by KILL9-NO-MERCY

**作成日**: 2025-11-14

Thank you for the quick feedback! I’m glad my report could be of some help, even in the few days remaining before the GA. I really appreciate your time and attention on this.

---

## Issue #5084: ChunkOrientedStep: Regression from #5048 - breaks on skip in fault-tolerant mode

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-11

**ラベル**: type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5084

**関連リンク**:
- Commits:
  - [4c9fe94](https://github.com/spring-projects/spring-batch/commit/4c9fe94bb12d6a9679848221abbadbbaa1b494f8)

### 内容

Hi Spring Batch team, Thank you for the great work on Spring Batch 6.


**Bug description**
When Issue [#5048](https://github.com/spring-projects/spring-batch/issues/5048) was reported, I made a mistake in my proposed fix that added `else { break; } `to the read loop.

The fix didn't account for the distinction between two different scenarios where readItem() returns null:
1) End-of-data (EOF): No more items available → Should break ✅
2) Skip in fault-tolerant mode: Exception skipped → Should continue reading ❌

The current loop termination condition in readChunk() treats both cases identically, causing premature read loop termination when skips occur.

**Example scenario:**
Chunk size: 3
Item-2 throws exception → Skip occurs
Expected: Skip Item-2 and continue reading Item-3 (2 items in chunk: Item-1, Item-3)
Actual: Read loop breaks after Item-1 (1 item in chunk)

**Environment**
Spring Batch version: 6.0.0-RC2 (after #5048 fix in commit 706add7)


**Steps to reproduce**
Configure a chunk-oriented step with:
Chunk size: 3
Fault-tolerant: true
Skip policy configured (e.g., AlwaysSkipItemSkipPolicy)

Use an ItemReader that throws exception on the 2nd item
Run the job and observe chunk sizes in the logs

**Expected behavior**
When a skip occurs during item reading in fault-tolerant mode:

The problematic item should be skipped
The read loop should continue to fill the chunk up to the configured chunk size
Expected chunk: [Item-1, Item-3] (2 items, Item-2 skipped)


**Expected console output:**
```bash
>>>> Read: Item-1
>>>> EXCEPTION on Item-2!
>>>> Skip occurred on reader
>>>> Read: Item-3
>>>> EOF: No more items
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-3
```
→ Both Item-1 and Item-3 processed in the same chunk

**Actual behavior**
When a skip occurs, the read loop terminates immediately:
Actual chunk 1: [Item-1] (1 item only)
Actual chunk 2: [Item-3] (remaining item in next chunk)

**Actual console output:**
```bash
>>>> Read: Item-1
>>>> EXCEPTION on Item-2!
>>>> Skip occurred on reader
>>>> Successfully processed: Item-1
>>>> Writing items: Item-1
>>>> Read: Item-3
>>>> EOF: No more items
>>>> Successfully processed: Item-3
>>>> Writing items: Item-3
```
→ Item-1 and Item-3 processed in different chunks ❌

Minimal Complete Reproducible example
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository, DataSource dataSource) {
        return new StepBuilder(jobRepository)
                .<TestItem, TestItem>chunk(3)
                .reader(issueReproductionReader(dataSource))
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .skipPolicy(new AlwaysSkipItemSkipPolicy())
                .skipListener(skipListener())
                .build();
    }

    @Bean
    public ItemReader<TestItem> issueReproductionReader(DataSource dataSource) {
        return new SkippableItemReader();
    }

    @Bean
    public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
        return item -> {
            log.info(">>>> Successfully processed: {}", item.getName());
            return item;
        };
    }

    @Bean
    public ItemWriter<TestItem> issueReproductionWriter() {
        return items -> {
            for (TestItem item : items) {
                log.info(">>>> Writing items: {}", item.getName());
            }
        };
    }

    private SkipListener<TestItem, TestItem> skipListener() {
        return new SkipListener<>() {
            @Override
            public void onSkipInRead(Throwable t) {
                log.info(">>>> Skip occurred on reader");
            }
        };
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    @Slf4j
    static class SkippableItemReader implements ItemReader<TestItem> {
        private int count = 0;
        private final List<TestItem> items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (count >= items.size()) {
                log.info(">>>> EOF: No more items");
                return null;
            }

            TestItem item = items.get(count);
            count++;

            // Throw exception on 2nd item (Item-2)
            if (count == 2) {
                log.error(">>>> EXCEPTION on Item-2!");
                throw new RuntimeException("Simulated read error on Item-2");
            }

            log.info(">>>> Read: {}", item.getName());
            return item;
        }
    }
}
```


**Root Cause Analysis**
In readItem() method (lines ~508-545)

When a skip occurs:
```java
catch (Exception exception) {
    this.compositeItemReadListener.onReadError(exception);
    if (this.faultTolerant && exception instanceof RetryException retryException) {
        doSkipInRead(retryException, contribution);
        // ⚠️ Returns null, but chunkTracker.moreItems() is still true!
    }
    // ...
}
return item;  // Returns null for skip
```
The chunkTracker.noMoreItems() is only called on actual end-of-data:
```java
item = doRead();
if (item == null) {
    this.chunkTracker.noMoreItems();  // Only set on EOF
}
```
So we have two distinct null return cases:
EOF: null returned + moreItems() == false
Skip: null returned + moreItems() == true

**In readChunk() method (lines ~478-487)**
Current problematic code(my mistake):
```java
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else {
            break;  // ❌ Breaks on BOTH EOF and skip!
        }
    }
    return chunk;
}
```
The `else { break; }` added in #5048 cannot distinguish between EOF and skip.

**Proposed Fix**
Change the break condition to check ChunkTracker state instead of blindly breaking on null:
**Fix for readChunk():**
```java
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else if (!chunkTracker.moreItems()) {  // ✅ Only break on actual EOF
            break;
        }
        // else: skip occurred, continue to next item
    }
    return chunk;
}
```

**Priority Note**
While this issue affects chunk size, the step continues to function correctly - all items are processed successfully, just with more transactions than intended. This can be addressed at your convenience based on priority.

**And**
The additional issue also exists in processChunkConcurrently() method

In concurrent processing mode, the same problem occurs but it was not addressed in the original #5048 fix.
**In processChunkConcurrently() method (lines ~431-438)**
Current code:
```java
// read items and submit concurrent item processing tasks
for (int i = 0; i < this.chunkSize; i++) {
    I item = readItem(contribution);
    if (item != null) {
        Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> processItem(item, contribution));
        itemProcessingTasks.add(itemProcessingFuture);
    }
    // ❌ No else clause - continues loop even after EOF, causing unnecessary read() calls
}
```
This method has TWO issues:
1) Original #5048 issue: No break on EOF → unnecessary readItem() calls continue
2) This issue: Even when fixed with else { break; }, it will break on skip (same as readChunk())


**Fix for processChunkConcurrently():**
```java
// read items and submit concurrent item processing tasks
for (int i = 0; i < this.chunkSize; i++) {
    I item = readItem(contribution);
    if (item != null) {
        Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> processItem(item, contribution));
        itemProcessingTasks.add(itemProcessingFuture);
    } else if (!chunkTracker.moreItems()) {  // ✅ Only break on actual EOF
        break;
    }
    // else: skip occurred, continue to next item
}
```
This fix addresses both issues:
- Prevents unnecessary reads after EOF (same with #5048 issue)
- Allows chunk to continue filling after skip (this issue)

If you have any questions about this issue or need additional information, please let me know.

Thank you for your continued responsiveness to issues despite your busy schedule. Please feel free to address this at your convenience based on priority.


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-13

This is a valid issue. It was expected to have some bumps and edge cases in this new implementation of the chunk-oriented processing model, so thank you very much for reporting this issue (and others!) early in the RC phase 🙏 We clearly have a gap in our test suite for these edge cases and I will fix that for the GA.

#### コメント 2 by fmbenhassine

**作成日**: 2025-11-13

> Change the break condition to check ChunkTracker state instead of blindly breaking on null:
> **Fix for readChunk():**

Thank you for the suggested fix! This is actually equivalent to:

```diff
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
--    for (int i = 0; i < chunkSize; i++) {
++    for (int i = 0; i < chunkSize && this.chunkTracker.moreItems(); i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
--        } else if (!chunkTracker.moreItems()) {  // ✅ Only break on actual EOF
--           break;
          }
    }
    return chunk;
}
```

which I find easier to think about, and which actually fixes both issues (the one in #5048 and this one, #5084) Amazing how #5084 is a regression of #5048 😉. I added `testSkipInReadInSequentialMode` and `testSkipInReadInConcurrentMode` in `ChunkOrientedStepFaultToleranceIntegrationTests` to cover those cases.

> The additional issue also exists in processChunkConcurrently() method

I fixed that as well and added `ChunkOrientedStepTests#testReadNoMoreThanAvailableItemsInConcurrentMode` to cover that case (similar to `ChunkOrientedStepTests#testReadNoMoreThanAvailableItemsInSequentialMode` that was added in #5048 )

---

Thanks again for reporting this issue!

---

## Issue #5085: Missing Javadoc site for 6.0.0-RC2

**状態**: closed | **作成者**: scordio | **作成日**: 2025-11-11

**ラベル**: in: documentation, in: build, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5085

### 内容

https://docs.spring.io/spring-batch/docs/6.0.0-RC2/api/ does not exist, while https://docs.spring.io/spring-batch/docs/6.0.0-RC1/api/ exists.


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-12

Thank you for reporting this, seems like a regression of c266075e5eb695da1316087c217264c302d277f8. This is not the first time I have issues with Javadocs.. apologies for the inconvenience 😔

I will fix that for the GA planned for next week.

#### コメント 2 by fmbenhassine

**作成日**: 2025-11-18

Hi @scordio ,

FYI, the Javadocs for 6.0.0-RC2 are now available online: https://docs.spring.io/spring-batch/reference/6.0/api/index.html.

However, notice the difference in the URL from now onwards:

```
Before: https://docs.spring.io/spring-batch/docs/6.0.0-RC1/api/index.html
After : https://docs.spring.io/spring-batch/reference/6.0/api/index.html
```
The patch version number is not in the URL anymore, but can be picked up from the top left navigation menu of the home page. This change is related to our portfolio-wise goal to use Antora-based documentation process (centralised docs, SEO friendly URLs, multi-version search capabilities, etc). This URL change will be documented in the release notes.

#### コメント 3 by scordio

**作成日**: 2025-11-18

> The patch version number is not in the URL anymore

I noticed that there is a redirection from https://docs.spring.io/spring-batch/reference/6.0.0-RC2/api/ to the new URL, which would allow me to still use the [`spring-batch.version`](https://github.com/spring-projects/spring-batch-extensions/blob/e4b2130053a442c5bfd7d062a6199013f0e41040/spring-batch-notion/pom.xml#L204) property from `spring-boot-dependencies`.

However, `javadoc` considers the redirection to be a [warning](https://github.com/spring-projects/spring-batch-extensions/actions/runs/19467873075/job/55707152839?pr=191#step:4:460):

```
[WARNING] Javadoc Warnings
[WARNING] warning: URL https://docs.spring.io/spring-batch/reference/6.0.0-RC2/api/element-list was redirected to https://docs.spring.io/spring-batch/reference/6.0/api/element-list -- Update the command-line options to suppress this warning.
[WARNING] 1 warning
```

Given that my build is configured to fail with javadoc warnings, I checked if I could suppress this one specifically, but I don't see such a granularity in the [DocLint groups](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javadoc.html#groups), which leaves me with three options:
* Remove failing in case of warnings (not really my preference)
* Hardcode `6.0` in the URL
* Fall back to the [Spring Batch Javadoc](https://javadoc.io/doc/org.springframework.batch/spring-batch-core/latest/index.html) hosted at [javadoc.io](https://javadoc.io/)

For now, I went with the last option at https://github.com/spring-projects/spring-batch-extensions/pull/191/commits/6bbcf83780bf1ae510ffad1685c7fec67fc199fc.

#### コメント 4 by fmbenhassine

**作成日**: 2025-11-19

This server-side redirection is portfolio-wise and I don't see what we can do on the Spring Batch side, but I am open to suggestions.

#### コメント 5 by scordio

**作成日**: 2025-11-19

I see that the Framework still works with explicit RC or patch versions, for example:
* https://docs.spring.io/spring-framework/docs/7.0.0-RC3/javadoc-api
* https://docs.spring.io/spring-framework/docs/7.0.0/javadoc-api

Could it be that they still need to migrate to the new way?

#### コメント 6 by fmbenhassine

**作成日**: 2025-11-19

Yes, it could be. I will ask the team and get back to you.

BTW, the Boot javadocs have the redirection in place (similar to Batch):

https://docs.spring.io/spring-boot/4.0.0-RC2/api/java/index.html redirects to
https://docs.spring.io/spring-boot/4.0/api/java/index.html

#### コメント 7 by scordio

**作成日**: 2025-11-19

Since the entire portfolio is moving in this direction, I'll ask on the [javadoc-dev](https://mail.openjdk.org/mailman/listinfo/javadoc-dev) mailing list how this use case should be addressed.

---

## Issue #5087: Proposal: Automatically register ItemHandler as StepListener instead of only StepExecutionListener in ChunkOrientedStepBuilder

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-14

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5087

**関連リンク**:
- Commits:
  - [bf282b4](https://github.com/spring-projects/spring-batch/commit/bf282b4eef318796b3295c1846d400208b395364)

### 内容

Hello, Spring Batch team! I would like to submit a proposal regarding how item handlers are automatically registered as listeners on ChunkOrientedStepBuilder


**Context**
Starting from commit 52875e7, an ItemReader, ItemProcessor, or ItemWriter is automatically registered  to stepListeners(as a StepExecutionListener) only when it directly implements *StepExecutionListener*:

```java
if (this.reader instanceof StepExecutionListener listener) {
    this.stepListeners.add(listener);
}
if (this.writer instanceof StepExecutionListener listener) {
    this.stepListeners.add(listener);
}
if (this.processor instanceof StepExecutionListener listener) {
    this.stepListeners.add(listener);
}
```

In Batch 5, however, these components were automatically registered as listeners if:

1) they implemented *StepListener*, or
2) they had methods annotated with any listener annotation defined in StepListenerMetaData
(handled internally by `StepListenerFactoryBean.isListener(itemHandler)` in `SimpleStepBuilder#registerAsStreamsAndListeners()`)

This allowed ItemReader/ItemProcessor/ItemWriter to be detected as a listener even when implementing more specific listener interfaces (e.g., ItemReadListener, ItemProcessListener, etc.) or when using listener annotations such as @BeforeRead, @AfterRead, @OnReadError, etc.


**Proposal**
Although I haven’t personally used this pattern extensively, allowing item handlers that implement ItemReadListener/ItemProcessListener/ItemWriteListener to be automatically registered via the StepListener interface could increase their practical utility, as the listener could access internal state of the item handler directly.

```java
if (this.reader instanceof StepListener listener) {
    this.stepListeners.add(listener);
}
if (this.writer instanceof StepListener listener) {
    this.stepListeners.add(listener);
}
if (this.processor instanceof StepListener listener) {
    this.stepListeners.add(listener);
}
```

Thank you for your time and consideration!

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-14

Thank you for the proposal! I think that was targeted at polymorphic objects, which act for example as an item reader and an item read listener at the same time. I have no objection to add this in v6 to reduce the gap with v5 and make migrations as smooth as possible.

#### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-11-15

Thank you for the quick review and decision to include this in v6! I am happy that this change will help smooth out migrations for v5 users.

---

## Issue #5088: Potential parameter key collision in `.getUniqueJobParameters()`

**状態**: closed | **作成者**: PENEKhun | **作成日**: 2025-11-16

**ラベル**: in: documentation, in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5088

### 内容

**Expected Behavior**

<!--- Tell us how it should work. Add a code example to explain what you think the feature should look like. This is optional, but it would help up understand your expectations. -->

The key used for the job parameter generated by getUniqueJobParameters() should never conflict with parameter names defined in a user’s job. Users should be able to call getUniqueJobParametersBuilder() and add any parameter name freely, without the risk of overwriting the framework-generated unique parameter.

**Current Behavior**

Currently, `getUniqueJobParameters()` uses a hardcoded `"random"` key.

```java
public JobParameters getUniqueJobParameters() {
    return new JobParameters(Set.of(
        new JobParameter<>("random", this.secureRandom.nextLong(), Long.class)
    ));
}
```

This creates a collision risk because

```java
JobParameters params = jobOperatorTestUtils.getUniqueJobParametersBuilder()
    .addLong("random", 12345L)  // Overwrites the unique parameter!
    .toJobParameters();
```

The current behavior makes it impossible to safely use getUniqueJobParametersBuilder() when a user’s job already defines a parameter named "random". In this case, the user-provided "random" parameter overwrites the framework-generated one, creating an unintended collision.

**Context**

<!--- 
How has this issue affected you?
What are you trying to accomplish?
What other alternatives have you considered?
Are you aware of any workarounds?
-->

- Q: What other alternatives have you considered?
  - 1. **Use a namespaced key** (e.g., `spring.batch.test.unique`) instead `random` key.
  - 2. **UUID as key + descriptive value** (e.g., `{UUID="Auto-generated by Spring Batch Test for unique job parameters"}`)






### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

> The key used for the job parameter generated by getUniqueJobParameters() should never conflict with parameter names defined in a user’s job.

It is the opposite: user defined parameter names should never conflict with those provided by the framework. The method `getUniqueJobParameters` mentions that it adds a random number but does not specify the parameter name (which is `random`). Two things:

- Parameters provided by the framework should be prefixed with `batch.` (similar to execution context attributes)
- The method `getUniqueJobParameters` should be updated to add the `batch.` prefix to the `random` parameter and mentions that clearly in the Javadoc.

#### コメント 2 by PENEKhun

**作成日**: 2025-11-17

> > The key used for the job parameter generated by getUniqueJobParameters() should never conflict with parameter names defined in a user’s job.
> 
> It is the opposite: user defined parameter names should never conflict with those provided by the framework. The method `getUniqueJobParameters` mentions that it adds a random number but does not specify the parameter name (which is `random`). Two things:
> 
> * Parameters provided by the framework should be prefixed with `batch.` (similar to execution context attributes)
> * The method `getUniqueJobParameters` should be updated to add the `batch.` prefix to the `random` parameter and mentions that clearly in the Javadoc.

I applied at https://github.com/spring-projects/spring-batch/pull/5089 . Thank you!

#### コメント 3 by fmbenhassine

**作成日**: 2025-11-18

Resolved in #5089. Thank you for your contribution 🙏

---

## Issue #5090: JobLauncherTestUtils throws an NPE at getJobLauncher() in Batch 6 RC2

**状態**: closed | **作成者**: lucas-gautier | **作成日**: 2025-11-17

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5090

**関連リンク**:
- Commits:
  - [5b80510](https://github.com/spring-projects/spring-batch/commit/5b8051001475d4529239390820a419ff4aceb792)

### 内容

**Bug description**
The just-deprecated JobLauncherTestUtils throws an NPE at getJobLauncher() in Batch 6 RC2 in unit tests.
Tests using JobLauncherTestUtils fail while tests using the new JobOperatorTestUtils work as expected in RC2.

**Environment**
Spring Boot 4.0.0 RC2
Spring Batch 6.0.0 RC2
Mandrel/Temurin JDK 25.0.1+8

**Steps to reproduce**
1. Open "batch-rc2" reproducible example and run the tests `./gradlew test` to see the failing tests
    - Stacktrace here: `build/reports/tests/test/index.html`
2. Build the project skipping tests `./gradlew build -x test` and run the jobs specified in the example section
3. Optionally, see the "batch5" project to see passing tests using JobLauncherTestUtils on boot 3.5.7 and batch 5.2.4.

**Expected behavior**
Tests written using the deprecated JobLauncherTestUtils should still work correctly until removal in Batch 7.

**Minimal Complete Reproducible example**
The "batch6-rc2" project contains the failing tests using JobLauncherTestUtils and passing tests using the new JobOperatorTestUtils.
The "batch5" project has passing tests using JobLauncherTestUtils.

Both projects have the same 2 jobs that be ran via the jar (skip tests in the batch6-rc2 project):
```
java -jar build/libs/*jar --spring.batch.job.name=HelloJob
java -jar build/libs/*jar --spring.batch.job.name=GoodbyeJob
```

[batch5.tgz](https://github.com/user-attachments/files/23571876/batch5.tgz)
[batch6-rc2.tgz](https://github.com/user-attachments/files/23571878/batch6-rc2.tgz)

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

That's a valid issue, thank you for reporting it! I will plan the fix for the upcoming GA.

#### コメント 2 by lucas-gautier

**作成日**: 2025-11-17

Thanks so much, Ben!

---

## Issue #5091: ChunkOrientedStep: Retry exhausted in ItemWriter always triggers Chunk Scanning regardless of skip eligibility

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5091

**関連リンク**:
- Commits:
  - [cb55ccc](https://github.com/spring-projects/spring-batch/commit/cb55ccc44b30790385ed49f8ee1ed1b1f4978288)

### 内容

Hello Spring Batch team,
first of all, thank you for your continued effort in maintaining and improving the project.
I would like to report an issue in Spring Batch 6's ChunkOrientedStep fault-tolerant write flow.

**Bug description**
In Spring Batch 6, when an exception occurs in the ItemWriter and the retry policy becomes exhausted (RetryException),
ChunkOrientedStep always performs a chunk scanning, regardless of whether the exception is skip-eligible.

The issue is that there is no preliminary SkipPolicy evaluation before entering the scan, meaning:
- Even if the exception is not skippable, scan() is still invoked.
- Normal (non-failing) items in the chunk get written again(by sacnning), resulting in unintended duplicate writes.
- Ultimately, a NonSkippableWriteException is thrown inside the scan, but only after unintended writes have already been attempted.

In Spring Batch 5 (FaultTolerantChunkProcessor), this did not happen because the framework performed a SkipPolicy check before scanning the chunk, preventing unnecessary scanning for non-skippable exceptions.
like:
```java
RecoveryCallback<Object> recoveryCallback = context -> {
				/*
				 * If the last exception was not skippable we don't need to do any
				 * scanning. We can just bomb out with a retry exhausted.
				 */
				if (!shouldSkip(itemWriteSkipPolicy, context.getLastThrowable(), -1)) {
					throw new ExhaustedRetryException(
							"Retry exhausted after last attempt in recovery path, but exception is not skippable.",
							context.getLastThrowable());
				}

				inputs.setBusy(true);
				data.scanning(true);
				scan(contribution, inputs, outputs, chunkMonitor, true);
				return null;
			};
```

This results in incorrect behavior and is a functional regression from Spring Batch 5.




**Environment**
Spring Batch version: 6.0.0-RC2



**Minimal Complete Reproducible example**
```java
@Configuration
@Slf4j
public class IssueReproductionJobConfiguration {

    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        return new StepBuilder(jobRepository)
                .<TestItem, TestItem>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .build();
    }

    @Bean
    public ItemReader<TestItem> issueReproductionReader() {
        return new SkippableItemReader();
    }

    @Bean
    public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
        return item -> {
            log.info(">>>> Successfully processed: {}", item.getName());
            return item;
        };
    }

    @Bean
    public ItemWriter<TestItem> issueReproductionWriter() {
        return items -> {
            for (TestItem item : items) {
                log.info(">>>> Writing items: {}", item.getName());
                if (item.id == 2) {
                    log.error(">>>> EXCEPTION on Item-2!");
                    throw new RuntimeException("Simulated write error on Item-2");
                }
            }
        };
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    static class SkippableItemReader implements ItemReader<TestItem> {
        private int index = 0;
        private final List<TestItem> items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (index >= items.size()) return null;
            return items.get(index++);
        }
    }
}
```
This example demonstrates the issue clearly:
after retry exhaustion, the framework enters chunk scan even though the thrown exception is not skippable, causing duplicate writes and an eventual NonSkippableWriteException


**Expected behavior**
Exception happens in writer
Retry attempts exhausted

Evaluate SkipPolicy for the exception

If skippable → proceed to scan

If not skippable → do not scan; fail immediately

Avoid duplicate writes and unintended extra write attempts.

**Actual behavior**
```bash
>>>> Read: Item-1
>>>> Read: Item-2
>>>> Read: Item-3
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-2
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> EXCEPTION on Item-2!
ChunkOrientedStep: Retry exhausted while attempting to write items, scanning the chunk

org.springframework.core.retry.RetryException: Retry policy for operation 'Retryable write operation' exhausted; aborting execution

...

>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> EXCEPTION on Item-2!
ChunkOrientedStep: Failed to write item: IssueReproductionJobConfiguration.TestItem(id=2, name=Item-2, description=Second item - will throw exception)

...

java.lang.RuntimeException: Simulated write error on Item-2
...

ChunkOrientedStep   : Rolling back chunk transaction

org.springframework.batch.core.step.skip.NonSkippableWriteException: Skip policy rejected skipping item

...

AbstractStep         : Encountered an error executing step issueReproductionStep in job issueReproductionJob

...


```

**Proposed fix**
To prevent unnecessary chunk scanning,
writeChunk() should perform a pre-scan SkipPolicy check when a RetryException is thrown, similar to the legacy behavior of FaultTolerantChunkProcessor in Spring Batch 5.

Specifically, inside the catch block of writeChunk(), a SkipPolicy validation can be added before triggering scan():
```java
catch (Exception exception) {
    ...

    if (this.faultTolerant && exception instanceof RetryException retryException) {

        // 💡 Proposed pre-scan SkipPolicy check
        if (!this.skipPolicy.shouldSkip(exception, -1)) {
            // If the exception is not skippable, skip scanning and fail immediately
            throw exception;
        }

        logger.info("Retry exhausted while attempting to write items, scanning the chunk", retryException);

        ChunkScanEvent chunkScanEvent = new ChunkScanEvent(
            contribution.getStepExecution().getStepName(),
            contribution.getStepExecution().getId()
        );

        chunkScanEvent.begin();
        scan(chunk, contribution);
        chunkScanEvent.skipCount = contribution.getSkipCount();
        chunkScanEvent.commit();

        logger.info("Chunk scan completed");
    }
    else {
        throw exception;
    }
}

```


Thank you for reviewing this issue!

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

> first of all, thank you for your continued effort in maintaining and improving the project.

Thank YOU for your continued effort in testing Spring Batch 6 and providing invaluable feedback to us! Amazing bug reporting BTW, really appreciated 🙏

This is a valid issue, I will plan the fix for the upcoming GA.

---

## Issue #5093: ChunkOrientedStepBuilder does not apply StepBuilderHelper properties (allowStartIfComplete, startLimit, stepExecutionListeners)

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5093

**関連リンク**:
- Commits:
  - [2d5c703](https://github.com/spring-projects/spring-batch/commit/2d5c7039e8d1f393c3616b0aeb0101956af31c97)

### 内容

Hello Spring Batch team,
I've found an issue where `ChunkOrientedStepBuilder` does not properly apply properties from its parent class `StepBuilderHelper` to the built step. I've searched existing issues but couldn't find a duplicate, so I'm reporting it here.

**Bug description**

When using `StepBuilder.chunk()`, properties set through `StepBuilderHelper` methods are not applied to the resulting `ChunkOrientedStep`. Specifically:
- `allowStartIfComplete(boolean)`
- `startLimit(int)`
- `listener(StepExecutionListener)`


These properties are correctly stored in the parent class's `properties` object, but they are never transferred to the actual step instance.


**Root cause**

The parent class `StepBuilderHelper` provides an `enhance(AbstractStep step)` method that applies all properties to a step:
```java
protected void enhance(AbstractStep step) {
    step.setJobRepository(properties.getJobRepository());

    ObservationRegistry observationRegistry = properties.getObservationRegistry();
    if (observationRegistry != null) {
       step.setObservationRegistry(observationRegistry);
    }

    Boolean allowStartIfComplete = properties.allowStartIfComplete;
    if (allowStartIfComplete != null) {
       step.setAllowStartIfComplete(allowStartIfComplete);
    }

    step.setStartLimit(properties.startLimit);

    List<StepExecutionListener> listeners = properties.stepExecutionListeners;
    if (!listeners.isEmpty()) {
       step.setStepExecutionListeners(listeners.toArray(new StepExecutionListener[0]));
    }
}
```

However, `ChunkOrientedStepBuilder.build()` does not call this `enhance()` method, nor does it manually set these properties on the step.

The builder should either:
1. Call `enhance(step)` to apply all properties from `StepBuilderHelper`, OR
2. Explicitly set `allowStartIfComplete`, `startLimit`, and `stepExecutionListeners` on the step (if avoiding `enhance()` for code organization reasons)

Currently, neither approach is implemented, resulting in these properties being silently ignored.


**Environment**
- Spring Batch version: 6.0.0-RC2

**Steps to reproduce**
1. Create a chunk-oriented step using `StepBuilder.chunk()`
2. Set `allowStartIfComplete(true)` or `startLimit(5)` or add a `StepExecutionListener`
3. Build and run the step
4. Observe that these properties have no effect on the step's behavior


**Expected behavior**
Properties configured through `StepBuilderHelper` methods should be applied to the built step, regardless of the step type.


**Minimal Complete Reproducible example**
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        return new StepBuilder(jobRepository)
                .chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .listener(new StepExecutionListener() {
                    @Override
                    public void beforeStep(StepExecution stepExecution) {
                        System.out.println(">>>> This message is NEVER printed");
                    }
                    
                    @Override
                    public ExitStatus afterStep(StepExecution stepExecution) {
                        System.out.println(">>>> This message is NEVER printed either");
                        return stepExecution.getExitStatus();
                    }
                })
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new SkippableItemReader();
    }

    @Bean
    public ItemProcessor issueReproductionProcessor() {
        return item -> {
            log.info(">>>> Successfully processed: {}", item.getName());
            return item;
        };
    }

    @Bean
    public ItemWriter issueReproductionWriter() {
        return items -> {
            for(TestItem item: items) {
                log.info(">>>> Writing items: {}", item.getName());
            }
        };
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    @Slf4j
    static class SkippableItemReader implements ItemReader {
        private int count = 0;
        private final List items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (count >= items.size()) {
                log.info(">>>> EOF: No more items");
                return null;
            }

            TestItem item = items.get(count);
            count++;

            log.info(">>>> Read: {}", item.getName());
            return item;
        }
    }
}
```

**Actual output:**

```
Job: [SimpleJob: [name=issueReproductionJob]] launched with the following parameters: [{}]
Executing step: [issueReproductionStep]
>>>> Read: Item-1
>>>> Read: Item-2
>>>> Read: Item-3
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-2
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> Writing items: Item-3
>>>> EOF: No more items
Step: [issueReproductionStep] executed in 2ms
```

Notice that the beforeStep() and afterStep() messages never appear.


Workaround

For StepExecutionListener, explicitly casting to StepListener works because it routes to the child class's listener(StepListener) method, which adds to stepListeners collection:

```java
.listener((StepListener) new StepExecutionListener() {
    @Override
    public void beforeStep(StepExecution stepExecution) {
        System.out.println(">>>> Now this IS printed!");
    }
})
```

For allowStartIfComplete and startLimit, there is currently no workaround via the builder API.


Proposed fix

if there's a reason to avoid calling enhance(), explicitly set these properties:

```java
public ChunkOrientedStep build() {

    ChunkOrientedStep step = // ... create step ...
    
    // Manually apply StepBuilderHelper properties
  this.stepListeners.addAll(properties.getStepExecutionListeners());

    if (properties.allowStartIfComplete != null) {
        step.setAllowStartIfComplete(properties.allowStartIfComplete);
    }
    step.setStartLimit(properties.startLimit);

    …

    return step;
}
```

It would resolve this issue and ensure that all StepBuilderHelper properties are properly applied to chunk-oriented steps.

Thank you for looking into this issue! Please let me know if you need any additional information.

---

