*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# コアパーティショニングAPIをorg.springframework.batch.core.partition配下に移動

**Issue番号**: #4849

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4849

**関連リンク**:
- Commits:
  - [08c4cb1](https://github.com/spring-projects/spring-batch/commit/08c4cb16b854b773f974eeb2073a04c56a0eb6ab)

## 内容

`Partitioner`、`StepExecutionAggregator`、`PartitionStep`などのいくつかのコアパーティショニングAPIは、現在`org.springframework.batch.core.partition.support`パッケージ配下にあります。これらは「サポート」インターフェースやクラスではないため、`org.springframework.batch.core.partition`パッケージに移動すべきです。
