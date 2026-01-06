*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# MapJobRegistryにBean名ではなくジョブ名でジョブを登録すると問題が発生する

**課題番号**: #5122

**状態**: closed | **作成者**: mminella | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5122

**関連リンク**:
- Commits:
  - [69ff97d](https://github.com/spring-projects/spring-batch/commit/69ff97dea77f97a5f74cfd1bad2f03c4c41b3862)

## 内容

**バグの説明**
Spring Batch 6のチュートリアルで、Bean名が提供されない場合は`MapJobRegistry`がジョブ名でジョブを登録していることに気付きました。この動作は、Bean名による登録が期待される場合に課題を引き起こします。例えば、`@SpringBatchTest`を使用してSpring Batchのテストユーティリティを活用する場合、ジョブがBean名で登録されていることを前提としているため、テストのセットアップが期待通りに動作しません。

**環境**
- 最新のmain（6.0.0の開発中）
- Spring Batch 6.0.0
- Spring Boot 4.0.0
- Java 21

