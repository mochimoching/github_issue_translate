# Spring Batch GitHub Issues

取得日時: 2026年01月06日 17:33:32

取得件数: 40件

---

## Issue #4514: Write Skip Count Not Updated in Chunk Processing

**状態**: closed | **作成者**: thilotanner | **作成日**: 2023-12-14

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4514

**関連リンク**:
- Commits:
  - [1fe91eb](https://github.com/spring-projects/spring-batch/commit/1fe91eb6fc80f79720c6036d1fc257d7217832ae)
  - [61d446e](https://github.com/spring-projects/spring-batch/commit/61d446e71f63c6b1d15826fb5e68aef7403b8702)

### 内容

**Bug description**
It seems, the write skip count is not incremented / updated if items are removed from chunks during write (in case an item cannot be successfully written)

**Environment**
Spring Batch 5.0.3 / Spring Boot 3.1.5 / Java 17

**Steps to reproduce**
```
public class MemberWriter implements ItemStreamWriter<String> {

    @Override
    public void write(Chunk<? extends String> memberChunk) {
        Chunk<? extends String>.ChunkIterator iterator = memberChunk.iterator();
        ...
        iterator.remove(new RuntimeException());
    }
```


**Expected behavior**
According to documentation of class Chunk, the writeSkipCount in the corresponding StepExecution object should be incremented for every item removed from ChunkIterator:
`Encapsulation of a list of items to be processed and possibly a list of failed items to be skipped. To mark an item as skipped clients should iterate over the chunk using the iterator() method, and if there is a failure call Chunk.ChunkIterator.remove() on the iterator. The skipped items are then available through the chunk.`

**Workaround**
It's possible to circumvent the issue by creating a combined SkipListener / StepExecutionListener:

```
public class SkipTestListener implements SkipListener<String, String>, StepExecutionListener {
    private StepExecution stepExecution;

    @Override
    public void beforeStep(StepExecution stepExecution) {
        this.stepExecution = stepExecution;
    }

    @Override
    public void onSkipInWrite(String item, Throwable t) {
        stepExecution.setWriteSkipCount(stepExecution.getWriteSkipCount() + 1);
        log.warn("Skipped item: {}", item);
    }
}
```
and register it accordingly in the step:
```
        SkipTestListener testListener = new SkipTestListener();

        new StepBuilder("process-step", jobRepository)
                .<String, String>chunk(chunkSize, transactionManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .faultTolerant()
                .listener((StepExecutionListener) testListener)
                .listener((SkipListener<? super String, ? super String>) testListener)
                .build();
```

### コメント

#### コメント 1 by Hydrawisk793

**作成日**: 2024-10-12

I think that a manual adjustment of write count should also be added in `onSkipInWrite` method of @thilotanner's workaround like this:

```Java
@Override
public void onSkipInWrite(String item, Throwable t) {
    stepExecution.setWriteCount(stepExecution.getWriteCount() - 1);
    stepExecution.setWriteSkipCount(stepExecution.getWriteSkipCount() + 1);
    log.warn("Skipped item: {}", item);
}
```

#### コメント 2 by florianhof

**作成日**: 2025-05-06

In my experience (Spring Batch 3.4.3), the _write count_ correctly don't report skipped item. Only the _write skip count_ is not correct.

I'm only a simple Spring Batch user, not a developer there. After a quick look, it seams `SimpleChunkProcessor.write` and `FaultTolerantChunkProcessor.write` should not only do `contribution.incrementWriteCount` but also `incrementWriteSkipCount`. 

#### コメント 3 by florianhof

**作成日**: 2025-05-28

Proposition of correction in pull request https://github.com/spring-projects/spring-batch/pull/4852

---

## Issue #4718: improve experience when configuring an alternative `JobRepository` 

**状態**: closed | **作成者**: joshlong | **作成日**: 2024-11-24

**ラベル**: type: bug, in: core, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4718

**関連リンク**:
- Commits:
  - [f7fcfaa](https://github.com/spring-projects/spring-batch/commit/f7fcfaa4fdb1f762a3bc16c30750d646dc52a6ed)

### 内容

improve experience when configuring an alternative `JobRepository`, as the DefaultBatchConfiguration, upon which Spring Boot in turn relies, assumes only JDBC-based infrastructure. This means that, when using Spring Boot, you can't simply replace one bean of type `JobRepository` and have things work. Everything must be redone from scratch, as we used to do before Spring Boot existed.  

This will be a problem for users of Spring Batch who want to avail themselves of the new "resourceless" and MongoDB job repository alternatives.

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2024-12-03

`@EnableBatchProcessing` (and in turn `DefaultBatchConfiguration`) was designed as the Java counterpart of the XML element `job-repository` from the batch namespace where a datasource is required:

```xml
<batch:job-repository id="jobRepository" data-source="dataSource" transaction-manager="transactionManager"/>
```

So yes, `@EnableBatchProcessing` assumes a JDBC infrastructure, and this should change now that we introduced the mongo job repository and the resourceless job repository.

I have a couple ideas on how we can address this issue and of course I am open to any thoughts about this as well. I will share these ideas with the community when we start working on this design issue for the next major release. This comment is only to validate and acknowledge the issue. Thank you for reporting it, @joshlong !

#### コメント 2 by krewetka

**作成日**: 2025-03-10

Hi @fmbenhassine as proper fix is planned for next major version is there any earlier workaround solution? 🤔 

I mean especially to overcome shutdown problem. It is quite a  big deal to be honest for production usage and as fixing it not in 5.3 but in 6 seems like it will be not fixed for at least few years 🤔 

Unless we simply are doing something wrong but we didn't manage to configure proper shutdown despite many attempts .

We moved from starting the job in regular container to starting it with AWS batch so at least regular CI/CD deployment is not breaking long running jobs but let's say it is only workaround we found.

#### コメント 3 by fmbenhassine

**作成日**: 2025-03-11

@krewetka which shutdown problem are you referring to? How is that related to this issue? Please open a separate [discussion](https://github.com/spring-projects/spring-batch/discussions) to explain your problem and I will be happy to help there.

FTR, v6 is planned for November this year and there is no plan for v5.3 at the moment. In the meantime and for those who want to use a non-jdbc job repository with v5.2, please check this [SO thread](https://stackoverflow.com/a/79492398/5019386) in which I attached a complete example.

#### コメント 4 by krewetka

**作成日**: 2025-03-12

Hi, sorry my bad. I am referring to https://github.com/spring-projects/spring-batch/issues/4728#issuecomment-2578356238 which was marked as duplicate of this issue.  Should I still open another one then?🤔

We have mongo setup running properly (but with H2 still there).

We did try to exclude DataSourceAutoConfiguration.class but then we were still facing some issues but let me try again one more time and see the exact results.

#### コメント 5 by fmbenhassine

**作成日**: 2025-03-12

@krewetka 

> Should I still open another one then?

Yes please. The shutdown lifecycle issue is different than requiring h2 for a mongo setup.

#### コメント 6 by krewetka

**作成日**: 2025-03-12

Ok, will try to provide full example in new issue when it comes to shutdown. Maybe it will be solved when I manage to get rid of h2 in my code finally 🤞 

Btw, I checked  [SO thread](https://stackoverflow.com/a/79492398/5019386)  and noticed it is not using `EnableBatchProcessing`

We have it in our code still and when we remove H2 we are facing:
`Error creating bean with name 'jobExplorer': Cannot resolve reference to bean 'dataSource' while setting bean property 'dataSource'`
with added:`@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`

I guess we need to not use `EnableBatchProcessing` then but still somehow setup somewhere almost all other piecies from it like `tablePrefix` , `isolationLevelForCreate` , `taskExecutorRef` etc.

Do you have any recommendation for it how do to proper workaround for the time-being? 

I did copy of EnableBatchProcessing  with ` String dataSourceRef() default "";` and used this one but there are imports on not public packages  like `AutomaticJobRegistrarBeanPostProcessor` and  `BatchRegistrar` ( which then define `registerJobExplorer` ) etc. which I could not keep in custom version.

I skiped them and it seems to work and the jobs are run but not sure if this is good idea as some important parts of sprint batch internal logic are not missing ( for example jobExplorer is not wired-up) 🤔 

After doing it I realized that it can be even still with `String dataSourceRef() default "dataSource";` as it is not used anymore when there is no import of `BatchRegistrar` which is creating jobExplorer 😆 

#### コメント 7 by fmbenhassine

**作成日**: 2025-05-21

@krewetka Thank you for your feedback, really appreciated! I understand, that's confusing. And I must admit that the default configuration of Spring Batch is not ideal, especially after the introduction of the resourceless job repository and the mongo job repository. I believe the introduction of these two new implementations has made the issues with previous design decisions more visible (ie the fact the default batch configuration assumes a JDBC infrastructure, the requirement of a `JobExplorer`, etc).

I started working on the next major release and wanted to share a few things:

- When using a `ResourcelessJobRepository`, there are no metadata to explore (there is no `ResourcelessJobExplorer`, this does not make sense). Therefore, the default batch configuration should not require a `JobExplorer`. This was fixed in https://github.com/spring-projects/spring-batch/issues/4825
- With Spring Boot, using `ResourcelessJobRepository` or `MongoJobRepository` should not require the user to exclude `DataSourceAutoConfiguration` or have to add a dependency to H2 or HSQLDB. Therefore, I think the resourceless job repository is a better default than the JDBC one in Spring Boot. I will discuss that with the Boot team.
- `EnableBatchProcessing` should not be tied to a JDBC infrastructure (this is historical, see my [previous comment](https://github.com/spring-projects/spring-batch/issues/4718#issuecomment-2514623019)). Therefore, all attributes related to the configuration of the JDBC job repository should be moved elsewhere. My idea is to follow the same approach of configuring Spring Security's session store with `@EnableJdbcHttpSession`, `@EnableRedisHttpSession`, etc. We could have the same for Spring Batch with `@EnableJdbcJobRepository`, `@EnableMongoJobRepository`, etc where each annotation have specific attributes to configure the metadata store.

And more generally, and after gathering feedback from the community over the years, I believe we need to simplify the API "surface" that batch users have to deal with. Currently, there are many different APIs to do the same things, which is confusing. I will open a separate issue for that with more details.

---

## Issue #4757: Enhancement : FlatFileItemReaderBuilder : raise check exception on build

**状態**: closed | **作成者**: frigaux | **作成日**: 2025-02-03

**ラベル**: in: infrastructure, type: bug, type: feature, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4757

### 内容

### Given concrete use case (X as record class)
`FlatFileItemReaderBuilder<X>()`
`...`
`.targetType(X::class.java)`
`.fieldSetMapper(myFieldSetMapper)`
`.build()`

**Expected Behavior**
When both **fieldSetMapper** and **targetType** are defined, a "BuildCheckException" should be raised in build method with "you cannot define both FieldSetMapper and targetType"

**Current Behavior**
FieldSetMapper is ignored and result in misunderstanding at runtime

Best regard


---

## Issue #4817: Remove dependency to JobExplorer in SimpleJobOperator

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-28

**ラベル**: type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4817

**関連リンク**:
- Commits:
  - [6992b79](https://github.com/spring-projects/spring-batch/commit/6992b79b8dc6f6e87f1dd75548328f9011ec699e)

### 内容

As of v5, `SimpleJobRepository` requires a `JobExplorer` in addition to a `JobRepository`. However, since `JobExplorer` is designed to be a read-only version of `JobRepository`, then the dependency to a `JobExplorer` does not make sense. In other words, since `SimpleJobOperator` depends on a `JobRepository` (which has read/write access to the meta-data store), it should not have a dependency to the read-only API. Ideally, `JobRepository` should be an extension of `JobExplorer` to add write/update operations.

This issue is a pre-requisite to making the default batch configuration work with any job repository (and not assume/require a JDBC infrastructure).

---

## Issue #4819: Remove deprecated APIs scheduled for removal in v6

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-29

**ラベル**: type: task, api: removal

**URL**: https://github.com/spring-projects/spring-batch/issues/4819

**関連リンク**:
- Commits:
  - [43ac1f1](https://github.com/spring-projects/spring-batch/commit/43ac1f12cfd651abe68a94c3fdde235e3ca5135f)

### 内容

This issue is to remove all deprecated APIs scheduled for removal in v6.

---

## Issue #4821: Redundant methods in JobExplorer/JobInstanceDao APIs

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-29

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4821

**関連リンク**:
- Commits:
  - [bf53794](https://github.com/spring-projects/spring-batch/commit/bf53794d6a1f1ab08d3fbc18cc40e1048e376e9c)

### 内容

As of v5.2, the JobExplorer/JobInstanceDao APIs contain two similar methods:

```java
List<JobInstance> getJobInstances(String jobName, int start, int count);

List<JobInstance> findJobInstancesByJobName(String jobName, int start, int count);
```

Both methods return the same result. `findJobInstancesByJobName` is not used and should be deprecated in v6.0 for removal in v6.2.

---

## Issue #4824: Make JobRepository extend JobExplorer

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-05

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4824

**関連リンク**:
- Commits:
  - [b8c93d6](https://github.com/spring-projects/spring-batch/commit/b8c93d677ed86130262042fb8565ce30816c2270)

### 内容

As of v5.2, `JobRepository` and `JobExplorer` have similar/same methods with different signatures/names doing the same thing (ie duplicate implementations). Here are some examples:

| JobRepository | JobExplorer |
|--------|--------|
| findJobExecutions | getJobExecutions |
| getLastJobExecution | getLastJobExecution |
| getJobNames | getJobNames |
| getJobInstance | getJobInstance |
| findJobInstancesByName | findJobInstancesByJobName |

Maintaining duplicate implementations is obviously not ideal. Moreover, `JobExplorer` is designed to be a read-only version of `JobRepository`, therefore `JobRepository` can technically be an extension of `JobExplorer`.

Finally, this would also make the batch configuration easier for users as they would not need to configure an additional bean (the `JobExplorer`) once they configured a `JobRepository`, which is almost always needed anyway.



---

## Issue #4825: Remove JobExplorer bean registration from the default batch configuration

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4825

**関連リンク**:
- Commits:
  - [ae2df53](https://github.com/spring-projects/spring-batch/commit/ae2df5396baa25cc5abe68e43508f6d0981dcf68)

### 内容

After #4824 and #4817  , there is no need to auto-configure an additional `JobExplorer` in the default batch configuration since a `JobRepository` is already defined.

This is required to make the default batch configuration work with a `ResourcelessJobRepository` (where there is no meta-data to explore).

---

## Issue #4827: Move core.explore package under core.repository

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-06

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4827

**関連リンク**:
- Commits:
  - [d7e13fb](https://github.com/spring-projects/spring-batch/commit/d7e13fb7f50dd19a85f8ce76f765b45e39a54846)

### 内容

The package `org.springframework.batch.core.explore` is really about exploring the job repository and therefore should be under `org.springframework.batch.core.repository`.

This issue is to move that package without any functional modification.


---

## Issue #4829: Rename JobRepositoryFactoryBean to JdbcJobRepositoryFactoryBean

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-06

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4829

**関連リンク**:
- Commits:
  - [46d42ab](https://github.com/spring-projects/spring-batch/commit/46d42ab757941d6dd56dc32fd6e468b6eb347642)

### 内容

After the introduction of `MongoJobRepositoryFactoryBean` in v5.2, `JobRepositoryFactoryBean` should be renamed to `JdbcJobRepositoryFactoryBean` to reflect the fact that it configures a JDBC-based job repository.


### コメント

#### コメント 1 by minkukjo

**作成日**: 2025-05-06

@fmbenhassine 
If it's just a name change, I'd like to work on it. Can I take it?

#### コメント 2 by fmbenhassine

**作成日**: 2025-05-06

@minkukjo Thank you for your offer to help! but this is already done. I just need to push the change set.

---

## Issue #4832: Make JobOperator extend JobLauncher

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4832

**関連リンク**:
- Commits:
  - [fc4a665](https://github.com/spring-projects/spring-batch/commit/fc4a66516ac7048e610065628793c62dcc646db5)

### 内容

`JobOperator` is nothing more than a `JobLauncher` with more capabilities (it's `start` method uses `JobLauncher#run` behind the scenes). Therefore, it should technically be an extension of `JobLauncher`, adding stop/restart functionality on top of just running jobs.

This issue is to make `JobOperator` extend `JobLauncher`, which will greatly simplify the default batch configuration by removing the requirement to define two beans instead of one.

---

## Issue #4833: Improve JobOperator by reducing its scope to job operations only

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4833

**関連リンク**:
- Commits:
  - [afdd842](https://github.com/spring-projects/spring-batch/commit/afdd842bc3e6d599e475f597f8becc12cc685fbd)

### 内容

As of v5.2, the `JobOperator` interface is exposing functionality that is out of its initial scope (ie operating batch jobs like start/stop/restart, etc).

Several methods like `getJobInstance`, `getExecutions` and similar methods have duplicate implementations in `JobRepository` and `JobExplorer` which is not ideal from a maintenance perspective . Moreover, some methods deal with job parameters conversion from string literals to domain objects which is not correct in a high-level API like `JobOperator` (those could be part of `CommandLineJobRunner` for example).

Those methods should be deprecated in v6.0 and removed in v6.2 or later.

---

## Issue #4834: Rename SimpleJobOperator to TaskExecutorJobOperator

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4834

**関連リンク**:
- Commits:
  - [e5bda0d](https://github.com/spring-projects/spring-batch/commit/e5bda0d40ae4ae1dedaca4d9339b29488225db83)

### 内容

After #4832 , `SimpleJobOperator` should be renamed to `TaskExecutorJobOperator` to reflect the fact that it is based on a task executor for starting jobs.

---

## Issue #4844: Update GraalVM runtime hints

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-22

**ラベル**: type: task, in: core, related-to: native

**URL**: https://github.com/spring-projects/spring-batch/issues/4844

**関連リンク**:
- Commits:
  - [580bd30](https://github.com/spring-projects/spring-batch/commit/580bd307a31726fa5e119a86161f05a290b44cef)
  - [f6f31ca](https://github.com/spring-projects/spring-batch/commit/f6f31cacc779f06cafb9cac275720f2a46831086)
  - [369652c](https://github.com/spring-projects/spring-batch/commit/369652cc73d227690de065d0fe3c16a14631774f)

### 内容

Related to https://github.com/spring-projects/spring-framework/issues/33847, runtime hints for Spring Batch should be updated accordingly.

See https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes#graalvm-native-applications

### コメント

#### コメント 1 by goafabric

**作成日**: 2025-08-04

@fmbenhassine 
As an fyi, while trying out boot 4.0.0-M1 in combination with GraalVM 24 (both local and paketo),
the native compile now breaks with the exception below.
With GraalVM 21 the compile works, but already with simple Spring Boot Apps, the Application wont start, due to another issue.

While the build will work, when overriding the CoreRuntimeHints and escaping the curly braces "\\{", the compile works.
Though i am not sure if this is the correct way to do it.


--- cut ---
Error: Error: invalid glob patterns found:
Pattern ALL_UNNAMED/org/springframework/batch/core/schema-{h2,derby,hsqldb,sqlite,db2,hana,mysql,mariadb,oracle,postgresql,sqlserver,sybase}.sql : Pattern contains unescaped character {. Pattern contains unescaped character }. 



#### コメント 2 by fmbenhassine

**作成日**: 2025-08-04

@goafabric Thank you for reporting this! I created #4937 to track this failure and planned to fix it in the upcoming 6.0.0-M2. FYI, I have planned to add a CI build against GraalVM to avoid this kind of issues (#3871).

#### コメント 3 by goafabric

**作成日**: 2025-08-04

> [@goafabric](https://github.com/goafabric) Thank you for reporting this! I created [#4937](https://github.com/spring-projects/spring-batch/issues/4937) to track this failure and planned to fix it in the upcoming 6.0.0-M2. FYI, I have planned to add a CI build against GraalVM to avoid this kind of issues ([#3871](https://github.com/spring-projects/spring-batch/issues/3871)).

thank you for the very fast reply and creating the issue !
i was unsure at first if to report this, due to the milestone and how .. but its awesome that it was so easy

---

## Issue #4845: Improve JobOperator API by using domain types instead of primitive types

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-22

**ラベル**: in: core, type: enhancement, api: breaking-change, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4845

**関連リンク**:
- Commits:
  - [8dde852](https://github.com/spring-projects/spring-batch/commit/8dde8529d36b646b33a1711219a1b1e8a046345a)

### 内容

`JobOperator` is the main high-level API to operate batch jobs. However, it is currently designed as a low-level API by using primitive types in most method signatures. This makes implementations deal with concerns that should not addressed there in the first place.

For example, starting a job with `start(String jobName, Properties parameters)` requires finding a job from a `JobRegistry` and using a `JobParametersConverter` to convert properties to `JobParameters`. This design makes the implementation require two collaborators (`JobRegistry` and `JobParametersConverter`), which could have been avoided by using domain types in the method signature like `#start(Job job, JobParameters parameters)`.

Another example is `stop(long jobExecutionId)` which requires to find the job execution by id, from which get the job name, then get the job itself from the registry, to finally being able to stop the job. This can be avoided by using `stop(JobExecution jobExecution)` instead.

Parameters conversion, job retrieval and other concerns should be part of a low level APIs like `CommandLineJobLauncher` or `JmxConsoleAdapter`, but not `JobOperator`. Core domain APIs should be designed with domain types in method signatures.

---

## Issue #4846: Rename JobExplorerFactoryBean to JdbcJobExplorerFactoryBean

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4846

**関連リンク**:
- Commits:
  - [d6ce07b](https://github.com/spring-projects/spring-batch/commit/d6ce07ba8359083a36cef4df2a578b1928ab8e63)

### 内容

After the introduction of `MongoJobExplorerFactoryBean` in v5.2, `JobExplorerFactoryBean` should be renamed to `JdbcJobExplorerFactoryBean ` to reflect the fact that it configures a JDBC-based job explorer.


---

## Issue #4847: Core API simplification

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4847

**関連リンク**:
- Commits:
  - [c872a12](https://github.com/spring-projects/spring-batch/commit/c872a12ad5fdc191a2637ed04775160f8fe7632e)
  - [bfe487c](https://github.com/spring-projects/spring-batch/commit/bfe487ccccfd2b5d7f82b07386094fdaaddd06c1)
  - [bcf4f72](https://github.com/spring-projects/spring-batch/commit/bcf4f724addc96c5beed2447ad9423008a3d6da8)

### 内容

This issue is to try to simplify and reduce the API surface for a typical Spring Batch application. I have been collecting feedback from the community over the years and the common pain points are:

### The API is too large and overwhelming

This has been raised several times in the past (#3242, #2901). A lot of accidental complexity has been added over the years for no real added value. The typical example is supporting modularity through `@EnableBatchProcessing(modular = true)` to avoid job name collisions in the `JobRegistry`. The amount of classes and interfaces needed for this feature (`JobFactory`, `ApplicationContextFactory`, `ApplicationContextJobFactory`, `ReferenceJobFactory`, `AbstractApplicationContextFactory` (with its two extensions), `JobLoader`, `JobFactoryRegistrationListener` and others) does not justify the real gain. This could have been left to the user by leveraging `GroupAwareJob`s or using a simple naming convention like `namespace.jobName`.

### The need to define a lot of beans and configurations for a typical app

From core infrastructure components to custom scopes to batch artefacts, the number of beans required to run a simple job is overwhelming. For example, there are two entry points to run a job: `JobOperator#start` and `JobLauncher#run` with different method signatures. `JobOperator` is sufficient, there is no need to have a functional interface to only run a job (and probably another one to stop a job, etc). `JobLauncher` is an example of unnecessary complexity (it was not retained in the Batch JSR for a good reason).

Similar case for `JobRepository` and `JobExplorer`. #4824 explains with details the confusion around these two beans. It is almost impossible to have a Spring Batch app without a `JobRepository` (unless it is a tool app to explore the meta-data). So having to define a `JobExplorer` *in addition* to a `JobRepository` is counter-intuitive. By the way, the `JobExplorer` concept is another example of unnecessary complexity (FTR, this too was not retained in the Batch JSR).

### Several ways to do the same thing which can be confusing

Some examples:

- There are at least three ways to populate a `JobRegistry`: a `JobRegistryBeanPostProcessor` (recently replaced with `JobRegistrySmartInitializingBean`), `AutomaticJobRegistrar` and manual job registration.
- There are two ways to launch a job: by using a `JobLauncher` or a `JobOperator` each with its own set of configurations and different method signatures.

Ideally, there should be only one way to do things.

Some of these issues have been addressed in v5.0 (like the removal of `JobBuilderFactory`, `StepBuilderFactory` and some other APIs), but there are still some duplicate functionalities. I believe the next major version is a good opportunity to address these issues.


---

## Issue #4848: Move DAOs implementations to separate packages

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, related-to: job-repository, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4848

**関連リンク**:
- Commits:
  - [9eafb31](https://github.com/spring-projects/spring-batch/commit/9eafb31af4b5a0b019ca3d03a0dfb0278d378883)

### 内容

After the introduction of the MongoDB job repository in v5.2, the JDBC and Mongo DAOs implementations should be moved to dedicated packages.

---

## Issue #4849: Move core partitioning APIs under org.springframework.batch.core.partition

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4849

**関連リンク**:
- Commits:
  - [08c4cb1](https://github.com/spring-projects/spring-batch/commit/08c4cb16b854b773f974eeb2073a04c56a0eb6ab)

### 内容

Several core partitioning APIs like `Partitioner`, `StepExecutionAggregator` and `PartitionStep` are currently under the `org.springframework.batch.core.partition.support` package. Those are not "support" interfaces and classes and should be moved to the `org.springframework.batch.core.partition` package.


---

## Issue #4854: Remove usage of JobFactory in JobRegistry

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4854

**関連リンク**:
- Commits:
  - [ce5ef2f](https://github.com/spring-projects/spring-batch/commit/ce5ef2f8b69ecd3bfe81ce218284b2710706a101)
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

### 内容

Along the lines of #4847 , this issue is to remove the usage of `JobFactory` from `JobRegistry` (and `MapJobRegistry`).

The API change is as follows:

```diff
-- void register(JobFactory jobFactory) throws DuplicateJobException;
++ void register(Job job) throws DuplicateJobException;
```

`JobFactory` is not a public (but not "user facing") API, but is still used in a user facing API. To simplify things, registering a job in a registry should not be done through a factory.


---

## Issue #4855: Make MapJobRegistry smart enough to auto register jobs defined in the application context

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4855

**関連リンク**:
- Commits:
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

### 内容

As of v5.2, it is required to populate the  job registry with a different component (like a bean post processor, or smart initializing bean or something similar) before being able to use it with the `JobOperator`.

This feature request is to make the `MapJobRegistry` smart enough to auto register jobs defined in the application context. This would remove the need for a distinct component to populate the registry and therefore simplifies the configuration. While this could be done by creating a `SmartMapJobRegistry` that extends `MapJobRegistry`, I would keep things simple along the lines of #4847 and make `MapJobRegistry` itself a `SmartInitializingSingleton`.

Other jobs defined outside the application context could be registered manually by the user (same as before).

---

## Issue #4856: Deprecate JobRegistrySmartInitializingSingleton

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4856

**関連リンク**:
- Commits:
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

### 内容

`JobRegistrySmartInitializingSingleton` was introduced in v5.1.1 as an "ad-hoc" solution to #4519 and #4489.

After #4855 , this component is redundant and should be deprecated for removal.


---

## Issue #4858: Add ability to use bean names for jobs and steps

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-03

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4858

**関連リンク**:
- Commits:
  - [bb2440f](https://github.com/spring-projects/spring-batch/commit/bb2440fea3a1a4685acba66261bebd49fa8c382d)

### 内容

As of v5.2, both `AbstractJob` and `AbstractStep` implement `BeanNameAware`. So it could be possible to use the bean name as a default job/step name in order to avoid duplication:

``` diff
@Bean
public Job job(JobRepository jobRepository, Step step) {
--	return new JobBuilder("job", jobRepository)
++	return new JobBuilder(jobRepository)
                           .start(step)
                           .build();
}
```

Obviously, the current constructor that takes the job/step name should remain to be able to specify a different name if needed.

cc @joshlong

---

## Issue #4866: Deprecate modular job configuration through EnableBatchProcessing

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-09

**ラベル**: type: task, in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4866

**関連リンク**:
- Commits:
  - [bcf4f72](https://github.com/spring-projects/spring-batch/commit/bcf4f724addc96c5beed2447ad9423008a3d6da8)

### 内容

The support of job configuration modularity through `@EnableBatchProcessing(modular = true)` to avoid job name collisions in the `JobRegistry` requires an unnecessary amount of accidental complexity both in terms of APIs the user has to provide as well as implementation details. The amount of classes and interfaces needed for this feature (`JobFactory`, `ApplicationContextFactory`, `ApplicationContextJobFactory`, `ReferenceJobFactory`, `AbstractApplicationContextFactory` (with its two extensions), `JobLoader`, `JobFactoryRegistrationListener` and others) does not justify the real gain. This feature could be achieved by leveraging `GroupAwareJob`s or  by using a simple naming convention like `namespace.jobName`.

This feature should be deprecated in v6 and removed in 6.2 or later.

### コメント

#### コメント 1 by kzander91

**作成日**: 2025-10-23

@fmbenhassine Can we get some guidance on what `GroupAwareJob` is and how to use it? The reference documentation doesn't mention that at all, and searching through the source code didn't really tell me how to use that as well.

I was using modular configuration to get some nice isolation between my jobs, where each job was running in it's own context and could use the same name for the various reader/writer beans and such.

The migration guide is not helpful here either, it basically just states to "use `GroupAwareJob` or context hierarchies", but doesn't give any hints on how that would work (particularly in a Spring Boot app, but I'm sure that non-Boot folks would appreciate that as well).

#### コメント 2 by fmbenhassine

**作成日**: 2025-10-23

Yes, I will update the migration guide with a practical example.

Can you please share your use case with a code example? 

Also, I personally never used that feature (and [seems like I am not the only one](https://github.com/spring-projects/spring-batch/discussions/4871)) so I am genuinely curious to have some feedback from real users of it. How would you address your requirement if Spring Batch did not provide that feature?

#### コメント 3 by kzander91

**作成日**: 2025-10-28

> Yes, I will update the migration guide with a practical example.

Thank you 🙏

> Can you please share your use case with a code example?

Sure. I have structured my app like this:
```
com.acme/
├── main/
│   └── @SpringBootApplication(scanBasePackages= "com.acme.config.common")
└── config/
    ├── common/
    │   ├── @Configuration SomeCommonConfiguration.java
    │   ├── @Component SomeSharedComponent.java
    │   └── @EnableBatchProcessing(modular = true) @Configuration JobContextsConfiguration.java
    └── jobs/
        ├── foojob/
        │   ├── @ComponentScan @Configuration FooJobConfiguration.java
        │   ├── @Component Reader.java
        │   ├── @Component Processor.java
        │   └── @Component Writer.java
        └── barjob/
            ├── @ComponentScan @Configuration BarJobConfiguration.java
            ├── @Component Reader.java
            ├── @Component Processor.java
            └── @Component Writer.java
```
* Common configuration classes and components shared across all jobs reside in a `config.common` package that is being component-scanned.
* Individual job configurations and beans specific for those jobs reside in their own packages and are not included in Spring Boot's component scan.
* `JobContextsConfiguration` (included in Boot's component scan) defines one bean like this for each job:
  ```java
  @Bean
  @Profile("!test")
  ApplicationContextFactory fooJobContextFactory() {
      return new GenericApplicationContextFactory(FooJobConfiguration.class);
  }
  ```
* The job-specific configuration classes (`FooJobConfiguration` and `BarJobConfiguration`) component-scan their package (and sub-packages).
  Each of them also defines a single `Job` bean, so
  ```java
  @Bean Job fooJob() { ... }
  ```
* Most of my jobs are pretty simple and structured similarly: They mostly fetch data from one source, _maybe_ transform it slightly and then write it to a sink. My reader and writer bean definitions are thus very similar and simple bean names like `reader` and `writer` are used.
* Because each job runs in its own application context, autowiring by type and using the same bean names just works and makes the entire setup pretty simple to understand and extend (new job? Just create a new package and define a new `ApplicationContextFactory`).

As you can see, I'm using the modular configuration mostly for convenience. As such _not_ having it wouldn't be the end of the world, but makes the effort to migrate to Spring Batch 6 way more involved than it would otherwise have been.

This structure also simplifies testing using `@SpringBatchTest`, because the `JobLauncherTestUtils` bean expects _a single_ `Job` bean. For example, the tests for the foo job use `@SpringBootTest @SpringBatchTest @ActiveProfiles("test") @Import(FooJobConfiguration.class)`, to get the same context as the job itself, and since the `test` profile disables the `ApplicationContextFactory` beans, the resulting test context only knows a single `Job`, so `JobLauncherTestUtils` is happy.

#### コメント 4 by fmbenhassine

**作成日**: 2025-10-30

Thank you for the feedback! I am really keen to help here. Can you please package that in a GitHub repo or a zip I can work on? I will create a diff patch to illustrate the migration path in a practical way. Many thanks upfront.

#### コメント 5 by kzander91

**作成日**: 2025-11-02

[demo9.zip](https://github.com/user-attachments/files/23290944/demo9.zip)

This is a project with a structure similar to what I have described above.

#### コメント 6 by fmbenhassine

**作成日**: 2025-11-02

@kzander91 Thank you very much for providing a sample app! Since this ticket is closed, I created #5072 to track the documentation improvement. Let's continue there.

#### コメント 7 by marbon87

**作成日**: 2025-11-12

Hi @fmbenhassine,

we are also using the AutomaticJobRegistrar in our company internal framework for about 100 batch apps to create a separate context for each job with the same benefits @kzander91 already mentioned. 
Can you give some information why AutomaticJobRegistrar and the corresponding classes are deprecated?
From my point of view it is a useful feature and i do not undestand why it should be removed.

Regards,
Mark

#### コメント 8 by fmbenhassine

**作成日**: 2025-11-19

Hi @marbon87 ,

> Can you give some information why AutomaticJobRegistrar and the corresponding classes are deprecated?

The rationale behind this decision is explained in the description of this issue: https://github.com/spring-projects/spring-batch/issues/4866#issue-3129848683

FTR, I added an example of how to migrate this feature to v6 here: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide#changes-related-to-the-modular-batch-configurations-through-enablebatchprocessingmodular--true. Using Spring's context hierarchies is more straightforward and way easier to think about than the ton of classes that are needed to implement and use that feature prior to v6. 

Please let me know if you need support in migrating your Spring Batch jobs to v6, I would be happy to help!

Best regards,
Mahmoud

#### コメント 9 by marbon87

**作成日**: 2025-11-25

Hi @fmbenhassine ,

thanks for your support. We have a webmvc-controller for starting jobs and use the jobregistry with a logic like this:
```
	@NonNull
	public Optional<JobExecution> start(@NonNull String jobName,
										@NonNull JobParameters jobParameters)
		throws JobInstanceAlreadyCompleteException, JobExecutionAlreadyRunningException, JobParametersConversionException, JobRestartException, InvalidJobParametersException {
		Job job = jobRegistry.getJob(jobName);
		if (job == null) {
			return Optional.empty();
		}
		JobParametersIncrementer jobParametersIncrementer = job.getJobParametersIncrementer();
		if (jobParametersIncrementer != null) {
			jobParameters = jobParametersIncrementer.getNext(jobParameters);
		}
		return jobOperator.start(job, jobParameters);
	}
```

Do you have an advice how this can be implemented without AutomaticJobRegistrar and JobLoader.

Best regards, Mark

#### コメント 10 by fmbenhassine

**作成日**: 2025-11-25

@marbon87 Since this ticket is closed, please open a "Migration Support" request in [GitHub Discussions](https://github.com/spring-projects/spring-batch/discussions/categories/migration-support) (with all the details and the code sample to migrate)  and I will help there. Thank you upfront.

#### コメント 11 by fmbenhassine

**作成日**: 2025-12-09

@marbon87 I created #5154 for your support request here: https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3575452892. Let's continue there.

---

## Issue #4867: Move listener APIs under core.listener package

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-09

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4867

**関連リンク**:
- Commits:
  - [90f7398](https://github.com/spring-projects/spring-batch/commit/90f7398222e22aef57b3207be3daa11f0b2fd668)

### 内容

As of v5.2, all listeners APIs are defined under the `core` package while they should be under the (currently existing) `core.listener` package.


---

## Issue #4877: Move core APIs in dedicated packages

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-12

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4877

**関連リンク**:
- Commits:
  - [d95397f](https://github.com/spring-projects/spring-batch/commit/d95397faf023ee3293ee10b41977231734a0f5d1)

### 内容

As of v5.2, all APIs related to jobs and steps are mixed and defined under the same package `org.springframework.batch.core`, even though there are already sub-packages `core.job` and `core.step`.

For better consistency and cohesion, job/step related APIs should be moved to their dedicated sub-packages.

---

## Issue #4886: Remove unnecessary generic from JobKeyGenerator interface

**状態**: closed | **作成者**: patrickwinti | **作成日**: 2025-06-13

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4886

### 内容

The `JobKeyGenerator<T>` interface currently uses a generic type parameter `<T>` to represent the source used to generate a job key. However, in practice, the implementations and usages of this interface rely on JobParameters as the source type.

Since the generic parameter is not providing meaningful flexibility and introduces unnecessary complexity (e.g., requiring casts or wildcard types in consumers), it would be cleaner to refactor the interface to:

```
public interface JobKeyGenerator {
    String generateKey(JobParameters source);
}
```


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-07-14

I agree, thank you for raising this!

This is a good candidate for a major release so I will plan it for v6.

#### コメント 2 by fmbenhassine

**作成日**: 2025-07-14

Resolved with #4887.

---

## Issue #4899: Introduce a modern command line batch operator

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-04

**ラベル**: type: feature, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4899

**関連リンク**:
- Commits:
  - [e6a8088](https://github.com/spring-projects/spring-batch/commit/e6a80889cb74409105e5df4fd092ff52f994b527)

### 内容

Spring Batch provided a `CommandLineJobRunner` since version 1. While this runner served its purpose well over the years, it started to show some limitations when it comes to extensibility and customisation. Many issues like static initialisation, non-standard way of handling options and parameters, lack of extensibility, etc have been reported like #1309 and #1666.

Moreover, all these issues made it impossible to reuse that runner in Spring Boot, which resulted in duplicate code in both projects as well behaviour divergence (like job parameters incrementer behaviour differences) that is confusing to many users.

The goal of this issue is to create a modern version of CommandLineJobRunner that is customisable, extensible and updated to the new changes introduced in Spring Batch 6.

---

## Issue #4910: Incorrect handling of job parameters when using a JobParametersIncrementer

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-16

**ラベル**: type: bug, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4910

**関連リンク**:
- Commits:
  - [72cd7bc](https://github.com/spring-projects/spring-batch/commit/72cd7bcbeec3097d2e5828dda6c2daf0b8b41d85)
  - [eb42128](https://github.com/spring-projects/spring-batch/commit/eb42128f448a4417600a96141b4299cbefe95eb5)

### 内容

The `JobParametersIncrementer` concept is a useful abstraction to use when there is a natural sequence of job instances (hourly, daily, etc). The goal of this abstraction is to bootstrap the initial set of job parameters and let the framework calculate the parameters of the next instance in the sequence. This was clear since the initial design of the `JobOperator#startNextInstance(String jobName)` method (notice the lack of job parameters in the signature). The concept is similar to database sequences that are initialized once by the user and incremented automatically by the database system (ie not altered by the user anymore).Therefore, it does not make sense to provide job parameters when using an incrementer.

Unfortunately, this feature has been incorrectly used through the command line runners of Spring Batch and Spring Boot for many years and I have seen users messing with job parameters between sequences, which goes against the initial intent of the incrementer concept, and which in turn caused several confusing issues like #882, https://github.com/spring-projects/spring-boot/issues/22602 and https://github.com/spring-projects/spring-boot/issues/14484. If someone starts to modify the sequence's logic and altering job parameters in between instances, (s)he should not use an incrementer in the first place.

v6 is a good opportunity to fix that. When a job parameters incrementer is attached to a job definition, the parameters of the next instance should be calculated by the framework, and any additional parameters supplied by the user should be ignored with a warning.

---

## Issue #4911: Remove JobExplorer dependency in JobParametersBuilder

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-16

**ラベル**: in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4911

**関連リンク**:
- Commits:
  - [9209fb4](https://github.com/spring-projects/spring-batch/commit/9209fb476d7c18d65716c92e5fa1431263b8f143)

### 内容

This is related to #4910 . The dependency to a JobExplorer in JobParametersBuilder is only used to calculate the next parameters of a job in the `getNextJobParameters(Job job)`.

As explained in #4910, the calculation of the job parameters of the next instance in a sequence should be based solely on the parameters of the previous instance. Therefore, the logic of that method should be moved to the `JobOperator#startNextInstance(Job)` method.

---

## Issue #4914: Incorrect warning when starting a job with an empty parameters set

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-18

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4914

**関連リンク**:
- Commits:
  - [980ff7b](https://github.com/spring-projects/spring-batch/commit/980ff7b8d72bba7f8cfa0aa62fc057bc27a4aba0)
  - [e2dcee1](https://github.com/spring-projects/spring-batch/commit/e2dcee113dfe78627e1adbf12dfe2a91e89f306c)

### 内容

After the introduction of #4910 , starting a job having an incrementer with an empty set of parameters results into an unnecessary  warning:

```
[main] WARN org.springframework.batch.core.launch.support.TaskExecutorJobOperator -  COMMONS-LOGGING Attempting to launch job 'job' which defines an incrementer with additional parameters={{}}. Those additional parameters will be ignored.
```

This warning should be removed when the parameters set is empty.

---

## Issue #4917: MessageChannelPartitionHandler not usable with non-jdbc job repository implementations

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: feature, in: integration, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4917

**関連リンク**:
- Commits:
  - [61fc226](https://github.com/spring-projects/spring-batch/commit/61fc22652c9c1f3da38aea9b22cf80da4c5c7ea2)

### 内容

As of v5.2, in a remote partitioning setup with repository polling, the `MessageChannelPartitionHandler` is not usable with MongoDB as it requires a data source.

This handler should work against the job repository interface.

---

## Issue #4918: Replace usage of JobExplorer with JobRepository in StepExecutionRequestHandler

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4918

**関連リンク**:
- Commits:
  - [ce89612](https://github.com/spring-projects/spring-batch/commit/ce896128424e7673d1a9f2b884bb5866d296f8c4)

### 内容

`StepExecutionRequestHandler` currently uses a `JobExplorer` which is now deprecated.

This issue is to replace the usage of `JobExplorer` with a `JobRepository`.

---

## Issue #4919: Remove usage of JobExplorer in BatchIntegrationConfiguration

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4919

**関連リンク**:
- Commits:
  - [9b7323f](https://github.com/spring-projects/spring-batch/commit/9b7323f58000c3465f5a70afb9cbbc58612c2c2f)

### 内容

The configuration of the batch integration module (mainly the remote partitioning setup) programmatically and through `@EnableBatchIntegration` currently requires both a job repository and a job explorer.

After #4824 , there is no need to configure a job explorer anymore. This issue is to remove the usage of `JobExplorer` in the `BatchIntegrationConfiguration` class and related APIs (`RemotePartitioningManagerStepBuilder[Factory]` and `RemotePartitioningWorkerStepBuilder[Factory]`).

---

## Issue #4920: Rename JobLauncherTestUtils to JobOperatorTestUtils

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: in: test, type: task, status: for-internal-team, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4920

**関連リンク**:
- Commits:
  - [020c24a](https://github.com/spring-projects/spring-batch/commit/020c24a92925f108c038f464201ae868ed58b570)

### 内容

After the deprecation of `JobLauncher` in favor of `JobOperator`, the utility `JobLauncherTestUtils` should be renamed to `JobOperatorTestUtils`.

Methods starting with `launch*` should be renamed to `start*` to follow the name convention in the `JobOperator` interface.


---

## Issue #4921: Deprecate StepRunner

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: in: test, type: task, status: for-internal-team, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4921

**関連リンク**:
- Commits:
  - [0aae4e9](https://github.com/spring-projects/spring-batch/commit/0aae4e91089df70f6f9e9750c95a3c9c30a7ff73)

### 内容

`org.springframework.batch.test.StepRunner` has no added value except a single method to run a step in a surrounding "fake" single-step job. This class is not typically used by users, and contains similar/duplicate code found in `JobLauncherTestUtils` (`makeUniqueJobParameters()` vs `getUniqueJobParameters()`).

In the same spirit as #4847 , this class should be deprecated in v6 and marked for removal in v6.2.

---

## Issue #4923: Replace usage of JobLauncher with JobOperator in JobStep

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4923

**関連リンク**:
- Commits:
  - [b105c8e](https://github.com/spring-projects/spring-batch/commit/b105c8e422a8d8b7f86c56746c8533c2dcae6a20)

### 内容

After the deprecation of `JobLauncher`, `JobStep` should be updated to use a `JobOperator` instead.


---

## Issue #4924: Replace usage of JobLauncher with JobOperator in JobLaunchingGateway and JobLaunchingMessageHandler

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: integration, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4924

**関連リンク**:
- Commits:
  - [c34a1fc](https://github.com/spring-projects/spring-batch/commit/c34a1fc73d632bc9990169333c8ca47355c8b077)

### 内容

After the deprecation of `JobLauncher`, `JobLaunchingGateway` and `JobLaunchingMessageHandler` should be updated to use `JobOperator` instead.

---

## Issue #4927: Replace usage of JobExplorer with JobRepository in SystemCommandTasklet

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4927

**関連リンク**:
- Commits:
  - [a8e138c](https://github.com/spring-projects/spring-batch/commit/a8e138cbf488596f48e9c8f49522fa7235a32943)

### 内容

After the deprecation of `JobExplorer`, `SystemCommandTasklet` should be updated to use `JobRepository` instead.


---

## Issue #4928: Replace usage of JobExplorer with JobRepository in RemoteStepExecutionAggregator

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-22

**ラベル**: type: task, in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4928

**関連リンク**:
- Commits:
  - [4b2586d](https://github.com/spring-projects/spring-batch/commit/4b2586d90c3059045ebb7e2383f50f70cff1b23e)

### 内容

After the deprecation of `JobExplorer`, `RemoteStepExecutionAggregator` should be updated to use `JobRepository` instead.

---

