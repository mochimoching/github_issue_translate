# Core API simplification

**Issue番号**: #4847

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4847

**関連リンク**:
- Commits:
  - [c872a12](https://github.com/spring-projects/spring-batch/commit/c872a12ad5fdc191a2637ed04775160f8fe7632e)
  - [bfe487c](https://github.com/spring-projects/spring-batch/commit/bfe487ccccfd2b5d7f82b07386094fdaaddd06c1)
  - [bcf4f72](https://github.com/spring-projects/spring-batch/commit/bcf4f724addc96c5beed2447ad9423008a3d6da8)

## 内容

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


