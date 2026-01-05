# Clarify MongoDB job repository configuration in reference documentation

**Issue番号**: #4859

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-03

**ラベル**: in: documentation, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4859

**関連リンク**:
- Commits:
  - [17bc8f7](https://github.com/spring-projects/spring-batch/commit/17bc8f70087e9e264c65551f47c1ea6601c53905)

## 内容

As of v5.2, the prerequisite for using MongoDB as a job repository is not documented in details in the [Configuring a JobRepository](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html) section. There is a note about that in the [What’s new in Spring Batch 5.2](https://docs.spring.io/spring-batch/reference/whatsnew.html#mongodb-job-repository-support) section but that is not clear enough.

The reference documentation should clarify the DDL script to execute against MongoDB before running jobs as well any other necessary configuration for things to work correctly (thinking about the `MapKeyDotReplacement` that has to be defined in the mongo converter for instance).

