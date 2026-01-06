*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# StepRunnerの非推奨化

**Issue番号**: #4921

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: in: test, type: task, status: for-internal-team, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4921

**関連リンク**:
- Commits:
  - [0aae4e9](https://github.com/spring-projects/spring-batch/commit/0aae4e91089df70f6f9e9750c95a3c9c30a7ff73)

## 内容

`org.springframework.batch.test.StepRunner`は、ステップを囲む「偽の」単一ステップジョブ内で実行する単一のメソッドを除けば、付加価値がありません。このクラスは通常ユーザーには使用されず、`JobLauncherTestUtils`にある類似/重複したコード（`makeUniqueJobParameters()`対`getUniqueJobParameters()`）を含んでいます。

課題 [#4847](https://github.com/spring-projects/spring-batch/issues/4847) と同じ精神で、このクラスはv6で非推奨化し、v6.2での削除対象としてマークすべきです。
