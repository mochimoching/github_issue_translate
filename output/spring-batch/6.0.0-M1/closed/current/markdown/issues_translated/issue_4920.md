*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobLauncherTestUtilsをJobOperatorTestUtilsに名称変更

**Issue番号**: #4920

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: in: test, type: task, status: for-internal-team, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4920

**関連リンク**:
- Commits:
  - [020c24a](https://github.com/spring-projects/spring-batch/commit/020c24a92925f108c038f464201ae868ed58b570)

## 内容

`JobLauncher`が`JobOperator`に置き換えられて非推奨化された後、ユーティリティ`JobLauncherTestUtils`も`JobOperatorTestUtils`に名称変更すべきです。

`launch*`で始まるメソッドは、`JobOperator`インターフェースの命名規則に従って`start*`に名称変更すべきです。
