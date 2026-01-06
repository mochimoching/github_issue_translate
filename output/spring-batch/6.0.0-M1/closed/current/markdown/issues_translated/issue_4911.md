*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobParametersBuilderからJobExplorerへの依存を削除

**Issue番号**: #4911

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-16

**ラベル**: in: core, status: for-internal-team, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4911

**関連リンク**:
- Commits:
  - [9209fb4](https://github.com/spring-projects/spring-batch/commit/9209fb476d7c18d65716c92e5fa1431263b8f143)

## 内容

これは課題 [#4910](https://github.com/spring-projects/spring-batch/issues/4910) に関連しています。`JobParametersBuilder`の`JobExplorer`への依存は、`getNextJobParameters(Job job)`でジョブの次のパラメータを計算するためにのみ使用されています。

課題 [#4910](https://github.com/spring-projects/spring-batch/issues/4910) で説明されているように、連続内の次のインスタンスのジョブパラメータの計算は、前のインスタンスのパラメータのみに基づいて行われるべきです。したがって、そのメソッドのロジックは`JobOperator#startNextInstance(Job)`メソッドに移動すべきです。
