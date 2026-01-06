# Remove JobExplorer dependency in JobParametersBuilder

**Issue番号**: #4911

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-16

**ラベル**: in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4911

**関連リンク**:
- Commits:
  - [9209fb4](https://github.com/spring-projects/spring-batch/commit/9209fb476d7c18d65716c92e5fa1431263b8f143)

## 内容

This is related to #4910 . The dependency to a JobExplorer in JobParametersBuilder is only used to calculate the next parameters of a job in the `getNextJobParameters(Job job)`.

As explained in #4910, the calculation of the job parameters of the next instance in a sequence should be based solely on the parameters of the previous instance. Therefore, the logic of that method should be moved to the `JobOperator#startNextInstance(Job)` method.

