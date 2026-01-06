# Deprecate JobRegistrySmartInitializingSingleton

**Issue番号**: #4856

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4856

**関連リンク**:
- Commits:
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

## 内容

`JobRegistrySmartInitializingSingleton` was introduced in v5.1.1 as an "ad-hoc" solution to #4519 and #4489.

After #4855 , this component is redundant and should be deprecated for removal.


