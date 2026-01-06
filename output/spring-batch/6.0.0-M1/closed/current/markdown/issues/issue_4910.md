# Incorrect handling of job parameters when using a JobParametersIncrementer

**Issue番号**: #4910

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-16

**ラベル**: type: bug, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4910

**関連リンク**:
- Commits:
  - [72cd7bc](https://github.com/spring-projects/spring-batch/commit/72cd7bcbeec3097d2e5828dda6c2daf0b8b41d85)
  - [eb42128](https://github.com/spring-projects/spring-batch/commit/eb42128f448a4417600a96141b4299cbefe95eb5)

## 内容

The `JobParametersIncrementer` concept is a useful abstraction to use when there is a natural sequence of job instances (hourly, daily, etc). The goal of this abstraction is to bootstrap the initial set of job parameters and let the framework calculate the parameters of the next instance in the sequence. This was clear since the initial design of the `JobOperator#startNextInstance(String jobName)` method (notice the lack of job parameters in the signature). The concept is similar to database sequences that are initialized once by the user and incremented automatically by the database system (ie not altered by the user anymore).Therefore, it does not make sense to provide job parameters when using an incrementer.

Unfortunately, this feature has been incorrectly used through the command line runners of Spring Batch and Spring Boot for many years and I have seen users messing with job parameters between sequences, which goes against the initial intent of the incrementer concept, and which in turn caused several confusing issues like #882, https://github.com/spring-projects/spring-boot/issues/22602 and https://github.com/spring-projects/spring-boot/issues/14484. If someone starts to modify the sequence's logic and altering job parameters in between instances, (s)he should not use an incrementer in the first place.

v6 is a good opportunity to fix that. When a job parameters incrementer is attached to a job definition, the parameters of the next instance should be calculated by the framework, and any additional parameters supplied by the user should be ignored with a warning.

