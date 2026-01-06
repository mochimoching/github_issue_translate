*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# コアAPIを専用パッケージに移動

**Issue番号**: #4877

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-12

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4877

**関連リンク**:
- Commits:
  - [d95397f](https://github.com/spring-projects/spring-batch/commit/d95397faf023ee3293ee10b41977231734a0f5d1)

## 内容

v5.2時点で、ジョブとステップに関連するすべてのAPIは混在しており、`core.job`や`core.step`のサブパッケージが既にあるにもかかわらず、同じパッケージ`org.springframework.batch.core`配下に定義されています。

一貫性と凝集性を向上させるために、ジョブ/ステップ関連のAPIは専用のサブパッケージに移動すべきです。
