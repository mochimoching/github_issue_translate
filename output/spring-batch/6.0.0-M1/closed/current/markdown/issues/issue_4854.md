# Remove usage of JobFactory in JobRegistry

**Issue番号**: #4854

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4854

**関連リンク**:
- Commits:
  - [ce5ef2f](https://github.com/spring-projects/spring-batch/commit/ce5ef2f8b69ecd3bfe81ce218284b2710706a101)
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

## 内容

Along the lines of #4847 , this issue is to remove the usage of `JobFactory` from `JobRegistry` (and `MapJobRegistry`).

The API change is as follows:

```diff
-- void register(JobFactory jobFactory) throws DuplicateJobException;
++ void register(Job job) throws DuplicateJobException;
```

`JobFactory` is not a public (but not "user facing") API, but is still used in a user facing API. To simplify things, registering a job in a registry should not be done through a factory.


