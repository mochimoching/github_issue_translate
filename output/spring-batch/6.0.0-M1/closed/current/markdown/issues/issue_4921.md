# Deprecate StepRunner

**Issue番号**: #4921

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: in: test, type: task, status: for-internal-team, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4921

**関連リンク**:
- Commits:
  - [0aae4e9](https://github.com/spring-projects/spring-batch/commit/0aae4e91089df70f6f9e9750c95a3c9c30a7ff73)

## 内容

`org.springframework.batch.test.StepRunner` has no added value except a single method to run a step in a surrounding "fake" single-step job. This class is not typically used by users, and contains similar/duplicate code found in `JobLauncherTestUtils` (`makeUniqueJobParameters()` vs `getUniqueJobParameters()`).

In the same spirit as #4847 , this class should be deprecated in v6 and marked for removal in v6.2.

