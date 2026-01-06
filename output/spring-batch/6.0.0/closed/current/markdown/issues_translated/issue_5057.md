*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# CommandLineJobOperatorの再起動/放棄の状態検証を改善し、ロギングを強化

**Issue番号**: #5057

**状態**: closed | **作成者**: ch200203 | **作成日**: 2025-10-29

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5057

## 内容


### 期待される動作
- **Abandon(放棄)**: 実行が**STOPPED**の場合のみ許可します。それ以外の場合は現在のステータスをログに記録し、汎用エラー終了コードを返します。
- **Restart(再起動)**: 実行が**FAILED**または**STOPPED**の場合のみ許可します。それ以外の場合は現在のステータスをログに記録し、汎用エラー終了コードを返します。
- 廃止された例外に依存せずに、CLIレイヤーで明示的な事前条件チェックを実行することで、`CommandLineJobOperator`のTODOを解決します。

### 現在の動作
- `abandon(jobExecutionId)`: CLIレベルで**STOPPED**を強制せずに`JobOperator#abandon`に委譲します。TODOでは`JobExecutionNotStoppedException`をスローすることが言及されていますが、その例外は廃止されています。
- `restart(jobExecutionId)`: ジョブ実行が「失敗しなかった」場合にチェック/ログを記録するTODOが含まれていますが、CLIレベルで有効な再起動状態を強制していません。

### コンテキスト
- **動機**: CLIの事前条件チェックをSpring BatchのセマンティクスとインラインのTODOに合わせ、無効な操作を早期に防止し、現在のステータスを含む明確なエラーログで可観測性を向上させます。
- **検討した代替案**: `JobExecutionNotStoppedException`をスローすることですが、これは廃止されています。CLIは代わりに終了コードとロギングを使用すべきです。
- **互換性**: APIの変更はありません。動作が明示的で予測可能になります。無効な操作は下流の例外に依存するのではなく、`JVM_EXITCODE_GENERIC_ERROR`を返します。

### 提案する変更
- `spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/CommandLineJobOperator.java`内で:
    - `restart(long jobExecutionId)`: `FAILED`または`STOPPED`を強制します。それ以外の場合は現在のステータスをログに記録し、汎用エラーを返します。
    - `abandon(long jobExecutionId)`: `STOPPED`を強制します。それ以外の場合は現在のステータスをログに記録し、汎用エラーを返します。

### 変更前のコード
- `restart(long jobExecutionId)`: TODOのみが存在し、状態チェックなし。直接`jobOperator.restart(jobExecution)`に委譲します。

```java
// TODO ジョブ実行が失敗しなかった場合、チェックしてエラーをログに記録すべき
JobExecution restartedExecution = this.jobOperator.restart(jobExecution);
return this.exitCodeMapper.intValue(restartedExecution.getExitStatus().getExitCode());
```

- `abandon(long jobExecutionId)`: TODOのみが存在し、状態チェックなし。直接`jobOperator.abandon(jobExecution)`に委譲します。

```java
// TODO ジョブ実行が停止していない場合、JobExecutionNotStoppedExceptionをスローすべき
JobExecution abandonedExecution = this.jobOperator.abandon(jobExecution);
return this.exitCodeMapper.intValue(abandonedExecution.getExitStatus().getExitCode());
```

この改善を実証するために、対応するプルリクエストが慎重に準備されています。
チームがレビューして、可能な時にフィードバックを提供していただければ幸いです。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

#5058で解決しました


