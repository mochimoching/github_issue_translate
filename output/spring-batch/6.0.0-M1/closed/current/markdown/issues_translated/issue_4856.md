*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobRegistrySmartInitializingSingletonを非推奨化

**Issue番号**: #4856

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4856

**関連リンク**:
- Commits:
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

## 内容

`JobRegistrySmartInitializingSingleton`は、課題 [#4519](https://github.com/spring-projects/spring-batch/issues/4519) と課題 [#4489](https://github.com/spring-projects/spring-batch/issues/4489) への「アドホック」ソリューションとしてv5.1.1で導入されました。

課題 [#4855](https://github.com/spring-projects/spring-batch/issues/4855) の後、このコンポーネントは冗長であり、削除のために非推奨とすべきです。
