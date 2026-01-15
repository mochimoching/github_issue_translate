*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

# DB2LUW向けspring-batch 6.xへのデータベースマイグレーションが誤っている

**Issue番号**: [#5166](https://github.com/spring-projects/spring-batch/issues/5166)

**状態**: open | **作成者**: bekoenig | **作成日**: 2025-12-15

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5166

## 内容

こんにちは、

[このマイグレーション](https://github.com/spring-projects/spring-batch/blob/98c10cd981b5f4ddc65e7071f6a603a3781514fd/spring-batch-core/src/main/resources/org/springframework/batch/core/migration/6.0/migration-db2.sql#L2)はInformixサーバーにのみ適用可能です。IBM DB2 LUW（10.1+）はシーケンスのリネームをサポートしていません（[リファレンス](https://www.ibm.com/docs/en/db2/12.1.x?topic=statements-rename)を参照）。

このサポートの欠如に対応するため、最後のシーケンス番号を取得し、その値から開始する新しいシーケンスを作成するJavaベースのマイグレーションを実装しました。

よろしくお願いいたします、
Ben

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-13

報告ありがとうございます！

> このサポートの欠如に対応するため、最後のシーケンス番号を取得し、その値から開始する新しいシーケンスを作成するJavaベースのマイグレーションを実装しました。

確かに、IBM DB2 LUW（10.1+）がシーケンスのリネームをサポートしていない場合、ユーザーは前のシーケンスの最後の値から開始する新しいシーケンスを作成する方法を見つける必要があります。マイグレーションスクリプトにこの点についての注記を追加します。
