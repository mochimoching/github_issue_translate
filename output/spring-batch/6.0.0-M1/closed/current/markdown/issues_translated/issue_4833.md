*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobOperatorの範囲をジョブ操作のみに限定して改善

**Issue番号**: #4833

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4833

**関連リンク**:
- Commits:
  - [afdd842](https://github.com/spring-projects/spring-batch/commit/afdd842bc3e6d599e475f597f8becc12cc685fbd)

## 内容

v5.2時点で、`JobOperator`インターフェースは、その本来の範囲（バッチジョブの開始/停止/再起動などの操作）を超えた機能を公開しています。

`getJobInstance`、`getExecutions`などのいくつかのメソッドは、`JobRepository`や`JobExplorer`に重複した実装があり、保守の観点から理想的ではありません。さらに、一部のメソッドは文字列リテラルからドメインオブジェクトへのジョブパラメータ変換を扱っていますが、`JobOperator`のような高レベルAPIでこれは適切ではありません（これらは例えば`CommandLineJobRunner`の一部であるべきです）。

これらのメソッドはv6.0で非推奨とし、v6.2以降で削除すべきです。
