*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月22日に生成されました）*

# DB2LUWにおけるSpring Batch 6.xへのデータベースマイグレーションの問題

**Issue番号**: [#5166](https://github.com/spring-projects/spring-batch/issues/5166)

**状態**: closed | **作成者**: bekoenig | **作成日**: 2025-12-15

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5166

**関連リンク**:
- コミット:
  - [b9a96a6](https://github.com/spring-projects/spring-batch/commit/b9a96a64386139f433881ffffe1895a616bdcce0)

## 内容

こんにちは。

[このマイグレーションスクリプト](https://github.com/spring-projects/spring-batch/blob/98c10cd981b5f4ddc65e7071f6a603a3781514fd/spring-batch-core/src/main/resources/org/springframework/batch/core/migration/6.0/migration-db2.sql#L2)はInformixサーバー専用であり、IBM DB2 LUW（10.1以降）には適用できません。DB2 LUWはシーケンスのリネームをサポートしていないためです（[リファレンス](https://www.ibm.com/docs/en/db2/12.1.x?topic=statements-rename)を参照）。

この制限に対応するため、私たちは最後のシーケンス番号を取得し、その値から開始する新しいシーケンスを作成するJavaベースのマイグレーション処理を実装しました。

よろしくお願いいたします。
Ben

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-13

ご報告いただきありがとうございます！

> この制限に対応するため、私たちは最後のシーケンス番号を取得し、その値から開始する新しいシーケンスを作成するJavaベースのマイグレーション処理を実装しました。

おっしゃる通り、IBM DB2 LUW（10.1以降）がシーケンスのリネームをサポートしていない場合、ユーザーは前のシーケンスの最後の値から開始する新しいシーケンスを作成する方法を見つける必要があります。マイグレーションスクリプトにこの点に関する注記を追加します。

### コメント 2 by fmbenhassine

**作成日**: 2026-01-21

スクリプト自体に注記を追加しました（https://github.com/spring-projects/spring-batch/commit/b9a96a64386139f433881ffffe1895a616bdcce0）。また、[マイグレーションガイド](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide/f46f3703ae89f7996be06d058883bdf6bb1fec06#database-schema-changes)にも同様の情報を追記しました。
