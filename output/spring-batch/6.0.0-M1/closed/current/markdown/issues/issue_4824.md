# Make JobRepository extend JobExplorer

**Issue番号**: #4824

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-05

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4824

**関連リンク**:
- Commits:
  - [b8c93d6](https://github.com/spring-projects/spring-batch/commit/b8c93d677ed86130262042fb8565ce30816c2270)

## 内容

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



