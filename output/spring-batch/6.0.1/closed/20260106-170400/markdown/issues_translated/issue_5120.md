*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobOperator.stop()の呼び出し中にoptimistic locking failureが発生する

**課題番号**: #5120

**状態**: closed | **作成者**: cppwfs | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5120

**関連リンク**:
- Commits:
  - [9bcc1e9](https://github.com/spring-projects/spring-batch/commit/9bcc1e9f7e1adb5aaec36d91b3d2b1cf0ca8c0a3)

## 内容

**バグの説明**
`JobOperator.stop(long executionId)`を呼び出すと、`JobRepository.update`メソッドによって楽観的ロックの失敗が発生します。これは、`JobOperator.stop(long executionId)`の後に実行が更新され、バージョン番号が増加するためです。

**環境**
- Spring Batch 6.0.0
- Spring Boot 4.0.0
- Java 21

**最小限の再現例**
次のサンプルを実行してください：
https://github.com/spring-projects/spring-batch/files/16053939/demo.zip

**実際の動作**
以下のような例外が発生します：
```
org.springframework.dao.OptimisticLockingFailureException: Attempt to update step execution id=1 with wrong version (2), where current version is 3
```

### コメント 1 by cppwfs

**作成日**: 2025-11-27

`stop(long executionId)`を呼び出した後は、`jobRepository.update(jobExecution)`を実行する前に、`SimpleJobRepository`の`createJobExecution`メソッドによって関連するジョブ実行が取得されるべきです。

### コメント 2 by fmbenhassine

**作成日**: 2025-12-04

サンプルと提案をありがとうございます！このバグは次のパッチリリースで修正します。

### コメント 3 by cppwfs

**作成日**: 2025-12-11

`SimpleJobOperator.stop(long executionId)`と`JobRepository.createJobExecution`メソッドの実行を連携させる必要があります。それらは2つの異なるスレッドで実行される可能性があります。

### コメント 4 by cppwfs

**作成日**: 2025-12-11

**問題**
ジョブ実行が停止される際、そのジョブ実行が最新の更新情報を持っていることを保証する必要があります。なぜなら、ジョブ実行のロック中に他のプロセスまたはスレッドが更新を行った可能性があるからです。これらの更新にはジョブ実行およびステップ実行のステータスの変更が含まれます。これは、後続のロジックがこれらの最新の状態に基づいて動作する必要があるためです。

**注意事項**
現在のSpring Batchのジョブ実行コア処理は、起動されたジョブ実行のコピーを保持しており、リポジトリと同期されていない可能性があります。したがって、複数の実行ポイントを同期させることは、すぐにできることではありません。

**ソリューション**
代わりに、バージョンがジョブ実行を適切に更新できるほど最新でない場合、`version`を`null`に設定することができます。これにより、`JdbcJobExecutionDao.synchronizeStatus`メソッドは最新のバージョン番号を使用してデータベース内のジョブ実行を更新します。ジョブ実行の`version`を`null`に設定すると、`JdbcJobExecutionDao.synchronizeStatus`メソッドは以下のクエリを実行します：

```java
private static final String UPDATE_JOB_EXECUTION_STATUS_ONLY = """
		UPDATE %PREFIX%JOB_EXECUTION SET STATUS = ?, LAST_UPDATED = ?
		WHERE JOB_EXECUTION_ID = ?
		""";
```

バージョンに依存する更新ではなく、このクエリを使用します。

**実装方法**
以下の2つの選択肢があります：

1. `SimpleJobOperator.stop(executionId)`メソッド内で、ジョブ実行の`version`を`null`に設定します。

**利点**：
- 他のコア実行フローには影響しません

**欠点**：
- 他のメソッドも同じ問題に直面する可能性がありますが、現在はこの問題に気付いていない可能性があります
- `SimpleJobOperator.stop(executionId)`から`SimpleJobOperator.stop(executionId, boolean force)`を抽出し、`JobOperator`に公開する必要がある場合があります

2. Spring Batchのコア実行ロジックを、ジョブ実行の更新処理前に毎回最新バージョンを取得するように変更します。

**利点**：
- すべてのジョブ実行の操作でバージョンが更新されます

**欠点**：
- 各ステップの実行ごとにリポジトリへの問い合わせが増えます

**デザインレビューでの決定事項**：
選択肢1を選びます。

**実装**
`SimpleJobOperator`が提供する可能性のある`stop(long executionId, boolean force)`署名を持つ新しいメソッドは、現時点では実装しません。問題#5114の修正によって、同じ実行を2回停止することが不可能になったためです。将来的に必要になった場合は、その時点で追加できます。

### コメント 5 by fmbenhassine

**作成日**: 2025-12-11

@cppwfs 詳細な分析をありがとうございます！選択肢1で進めましょう。

### コメント 6 by cppwfs

**作成日**: 2025-12-11

ありがとうございます@fmbenhassine

### コメント 7 by fmbenhassine

**作成日**: 2025-12-12

修正は以下のコミットにあります：https://github.com/spring-projects/spring-batch/commit/9bcc1e9f7e1adb5aaec36d91b3d2b1cf0ca8c0a3

@cppwfs さん、お時間のある時に確認していただけますか？テストを追加しました。

### コメント 8 by cppwfs

**作成日**: 2025-12-12

@fmbenhassine 素晴らしいです！ありがとうございます。

