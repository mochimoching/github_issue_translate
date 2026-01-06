# Rename JobLauncherTestUtils to JobOperatorTestUtils

**Issue番号**: #4920

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: in: test, type: task, status: for-internal-team, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4920

**関連リンク**:
- Commits:
  - [020c24a](https://github.com/spring-projects/spring-batch/commit/020c24a92925f108c038f464201ae868ed58b570)

## 内容

After the deprecation of `JobLauncher` in favor of `JobOperator`, the utility `JobLauncherTestUtils` should be renamed to `JobOperatorTestUtils`.

Methods starting with `launch*` should be renamed to `start*` to follow the name convention in the `JobOperator` interface.


