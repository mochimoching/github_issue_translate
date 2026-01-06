# Make MapJobRegistry smart enough to auto register jobs defined in the application context

**Issue番号**: #4855

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4855

**関連リンク**:
- Commits:
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

## 内容

As of v5.2, it is required to populate the  job registry with a different component (like a bean post processor, or smart initializing bean or something similar) before being able to use it with the `JobOperator`.

This feature request is to make the `MapJobRegistry` smart enough to auto register jobs defined in the application context. This would remove the need for a distinct component to populate the registry and therefore simplifies the configuration. While this could be done by creating a `SmartMapJobRegistry` that extends `MapJobRegistry`, I would keep things simple along the lines of #4847 and make `MapJobRegistry` itself a `SmartInitializingSingleton`.

Other jobs defined outside the application context could be registered manually by the user (same as before).

