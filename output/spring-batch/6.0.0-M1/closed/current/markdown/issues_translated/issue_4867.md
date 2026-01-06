*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# リスナーAPIをcore.listenerパッケージ配下に移動

**Issue番号**: #4867

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-09

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4867

**関連リンク**:
- Commits:
  - [90f7398](https://github.com/spring-projects/spring-batch/commit/90f7398222e22aef57b3207be3daa11f0b2fd668)

## 内容

v5.2時点で、すべてのリスナーAPIは`core`パッケージ配下に定義されていますが、（現在存在する）`core.listener`パッケージ配下にあるべきです。
