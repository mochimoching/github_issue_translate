*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# デフォルトのバッチ設定からJobExplorer Beanの登録を削除

**Issue番号**: #4825

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4825

**関連リンク**:
- Commits:
  - [ae2df53](https://github.com/spring-projects/spring-batch/commit/ae2df5396baa25cc5abe68e43508f6d0981dcf68)

## 内容

課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824) と課題 [#4817](https://github.com/spring-projects/spring-batch/issues/4817) の後、`JobRepository`が既に定義されているため、デフォルトのバッチ設定で追加の`JobExplorer`を自動設定する必要はありません。

これは、`ResourcelessJobRepository`（探索すべきメタデータがない）でデフォルトのバッチ設定を動作させるために必要です。
