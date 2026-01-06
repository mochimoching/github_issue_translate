*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobOperatorをJobLauncherの拡張とする

**Issue番号**: #4832

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-07

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4832

**関連リンク**:
- Commits:
  - [fc4a665](https://github.com/spring-projects/spring-batch/commit/fc4a66516ac7048e610065628793c62dcc646db5)

## 内容

`JobOperator`は、より多くの機能を持つ`JobLauncher`に過ぎません（その`start`メソッドは内部で`JobLauncher#run`を使用しています）。したがって、技術的には`JobLauncher`の拡張であるべきで、ジョブの実行に加えて停止/再起動機能を追加するものです。

この課題は、`JobOperator`を`JobLauncher`の拡張とすることで、2つのBeanを定義する代わりに1つで済むようにして、デフォルトのバッチ設定を大幅に簡素化するためのものです。
