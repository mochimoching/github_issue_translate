*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# SQL ServerメタデータテーブルのDDLは暗黙的な変換によるパフォーマンス低下とデッドロックを防ぐためにNVARCHARを使用すべき

**Issue番号**: #5064

**状態**: closed | **作成者**: Chienlin1014 | **作成日**: 2025-10-30

**ラベル**: in: core, type: enhancement, related-to: ddl-scripts

**URL**: https://github.com/spring-projects/spring-batch/issues/5064

**関連リンク**:
- Commits:
  - [ee050d6](https://github.com/spring-projects/spring-batch/commit/ee050d66b0f00f7e03365835f160d4a3f133bda1)
  - [525d9b0](https://github.com/spring-projects/spring-batch/commit/525d9b0ee640898a6cf11f844e365adfb19b6dee)

## 内容

 こんにちは、Spring Batchチームの皆さん、

  Spring BatchをSQL Serverデータベースで使用する際の重大なパフォーマンス問題とデッドロックの可能性について報告します。根本原因は、デフォルトのSpring Batchスキーマと
  Microsoft JDBCドライバーのデフォルト動作との間のデータ型の不一致です。

  問題

  SQL Serverメタデータテーブル(例: BATCH_JOB_INSTANCEのJOB_NAME、JOB_KEY)のデフォルトDDLは、これらのカラムを`VARCHAR`として定義しています。しかし、Microsoft JDBC Driver for SQL Serverは
  デフォルトで文字列パラメータを`NVARCHAR`として送信します。

  この不一致により、SQL Serverは比較ごとに`VARCHAR`カラムに対して暗黙的なデータ型変換(CONVERT_IMPLICIT)を実行せざるを得なくなります。

  影響: パフォーマンス低下とデッドロック

  この暗黙的な変換は効率的なインデックスの使用を妨げます。クエリオプティマイザーはIndex Seek操作を示していますが、WHERE句内の`CONVERT_IMPLICIT`と検索範囲を定義するための
  GetRangeThroughConvertの使用により、実際にはコストのかかる範囲スキャンを実行します。この動作はデータの増加に伴い線形に悪化する大幅なパフォーマンス低下につながります。

  この深刻なパフォーマンス低下により、トランザクションがロックをはるかに長く保持します。高い並行性の下では、これによりロック競合とデッドロックのリスクが劇的に増加します。範囲スキャンがより広い範囲ロックを取得し、INSERT試行時に相互待機が発生するため、READ COMMITTEDの分離レベルでもこれらのデッドロックが発生することを確認しました。

  提案する解決策

  これを根本的に解決するために、`schema-sqlserver.sql`ファイルを更新して、メタデータテーブルのすべての関連する文字列カラムを`VARCHAR`から`NVARCHAR`に変更することを提案します。これにより、
  データベーススキーマがJDBCドライバーのデフォルト動作と整合し、効率的なインデックスの使用が保証され、これらのパフォーマンスとデッドロックの問題が防止されます。

  ご検討いただきありがとうございます。



