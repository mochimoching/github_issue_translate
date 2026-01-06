*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# core.exploreパッケージをcore.repository配下に移動

**Issue番号**: #4827

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-06

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4827

**関連リンク**:
- Commits:
  - [d7e13fb](https://github.com/spring-projects/spring-batch/commit/d7e13fb7f50dd19a85f8ce76f765b45e39a54846)

## 内容

`org.springframework.batch.core.explore`パッケージは、実際にはジョブリポジトリの探索に関するものであるため、`org.springframework.batch.core.repository`配下にあるべきです。

この課題は、機能的な変更なしにそのパッケージを移動するためのものです。
