# Introduce a modern command line batch operator

**Issue番号**: #4899

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-04

**ラベル**: type: feature, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4899

**関連リンク**:
- Commits:
  - [e6a8088](https://github.com/spring-projects/spring-batch/commit/e6a80889cb74409105e5df4fd092ff52f994b527)

## 内容

Spring Batch provided a `CommandLineJobRunner` since version 1. While this runner served its purpose well over the years, it started to show some limitations when it comes to extensibility and customisation. Many issues like static initialisation, non-standard way of handling options and parameters, lack of extensibility, etc have been reported like #1309 and #1666.

Moreover, all these issues made it impossible to reuse that runner in Spring Boot, which resulted in duplicate code in both projects as well behaviour divergence (like job parameters incrementer behaviour differences) that is confusing to many users.

The goal of this issue is to create a modern version of CommandLineJobRunner that is customisable, extensible and updated to the new changes introduced in Spring Batch 6.

