*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# SimpleJobOperatorのJobExplorerへの依存を削除

**Issue番号**: #4817

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-28

**ラベル**: type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4817

**関連リンク**:
- Commits:
  - [6992b79](https://github.com/spring-projects/spring-batch/commit/6992b79b8dc6f6e87f1dd75548328f9011ec699e)

## 内容

v5時点で、`SimpleJobOperator`は`JobRepository`に加えて`JobExplorer`を必要としています。しかし、`JobExplorer`は`JobRepository`の読み取り専用版として設計されているため、`JobExplorer`への依存は理にかなっていません。言い換えれば、`SimpleJobOperator`は（メタデータストアへの読み取り/書き込みアクセスを持つ）`JobRepository`に依存しているので、読み取り専用APIへの依存を持つべきではありません。理想的には、`JobRepository`は`JobExplorer`を拡張して書き込み/更新操作を追加するべきです。

この課題は、デフォルトのバッチ設定がどのJobRepositoryでも動作するようにする（JDBCインフラストラクチャを前提/要求しない）ための前提条件です。
