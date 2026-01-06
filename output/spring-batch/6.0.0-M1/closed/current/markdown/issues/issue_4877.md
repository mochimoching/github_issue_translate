# Move core APIs in dedicated packages

**Issue番号**: #4877

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-12

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4877

**関連リンク**:
- Commits:
  - [d95397f](https://github.com/spring-projects/spring-batch/commit/d95397faf023ee3293ee10b41977231734a0f5d1)

## 内容

As of v5.2, all APIs related to jobs and steps are mixed and defined under the same package `org.springframework.batch.core`, even though there are already sub-packages `core.job` and `core.step`.

For better consistency and cohesion, job/step related APIs should be moved to their dedicated sub-packages.

