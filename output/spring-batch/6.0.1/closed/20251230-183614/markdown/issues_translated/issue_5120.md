# SimpleJobOperator.stop()内のStepExecution更新がグレースフルストップ後にJobExecution.BatchStatus.UNKNOWNを引き起こす

**Issue番号**: #5120

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-01

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5120

**関連リンク**:
- Commits:
  - [29f5ecf](https://github.com/spring-projects/spring-batch/commit/29f5ecf567cc21b5ce3dd9a41283d227a85c3667)
  - [f62da2b](https://github.com/spring-projects/spring-batch/commit/f62da2bd6a7a9459d809e86065877ac440130b70)
  - [78ba896](https://github.com/spring-projects/spring-batch/commit/78ba896caa7020f1f7f972ae7b3dd469699a4922)
  - [984a057](https://github.com/spring-projects/spring-batch/commit/984a057f86c92b326782b964f949c0eb0eb805d4)
  - [0feafa1](https://github.com/spring-projects/spring-batch/commit/0feafa15a73c4be4f990b627c914bb918118e96e)
  - [09b0783](https://github.com/spring-projects/spring-batch/commit/09b07834ed86f4a11a51e118e665dc20156352c9)
  - [644d7e6](https://github.com/spring-projects/spring-batch/commit/644d7e6997c4e29822be580dab8e6f65713e17be)

## 内容

Spring Batchチームの皆様、こんにちは。

実行中の`ChunkOrientedStep`を`JobOperator.stop()`でグレースフルに停止すると、`OptimisticLockingFailureException`が発生し、UNKNOWNステータスが設定される課題を報告します。

## バグの説明
Spring Batchバージョン6.0.0では、実行中の`ChunkOrientedStep`に対して`SimpleJobOperator.stop(jobExecution)`を呼び出すと、楽観的ロックのバージョン競合が発生します。

これは、`SimpleJobOperator.stop()`メソッドが374行目で`stoppableStep.stop()`を呼び出した後、明示的に`jobRepository.update(stepExecution)`を呼び出すために発生します。

この更新により、`StepExecution`のデータベースバージョンが早期にインクリメントされます。

その結果、メモリ内に古いバージョンの`StepExecution`を保持しているメインバッチ実行スレッドは、`AbstractStep.execute()`での最終的な永続化呼び出し時に`OptimisticLockingFailureException`で失敗します。

## 環境
Spring Batchバージョン: 6.0.0
Spring Boot 4.0.0

## 再現手順
1) 長時間実行される`ChunkOrientedStep`を持つSpring Batchアプリケーションを起動します。
2) ステップがチャンクをアクティブに処理している間(チャンクトランザクション内)、別のスレッドまたはAPIエンドポイントから`JobOperator.stop(jobExecution)`を呼び出します。
3) `SimpleJobOperator.stop()`呼び出しがDBを更新し、`StepExecution`のバージョンを増加させます。(375行目で)
~4) バッチ実行スレッド(チャンク処理スレッド)がterminateOnlyフラグを検出し、チャンク処理ループから正常に終了しようとします。(ChunkOrientedStep.doExecute()の362行目で)~ ChunkOrientedStep.doExecute()が完了します(停止されない - これは https://github.com/spring-projects/spring-batch/issues/5114 に関連)
5) `AbstractStep.execute()`メソッドがステップの最終ステータスを保存しようとします。(327行目で)
6) ジョブが`OptimisticLockingFailureException`で失敗します。そしてJobExecution.BatchStatusとExitStatusがUNKNOWNに設定されます。
7) そのため、このJobExecutionは再起動できません。


## 期待される動作
`JobOperator.stop()`が呼び出されると、ジョブは安全に停止し、`OptimisticLockingFailureException`を引き起こしたり、再起動可能性のためにUNKNOWNステータスを設定したりせずに、STOPPEDステータスに移行するはずです。


## 実際のスタックトレース
```java
org.springframework.dao.OptimisticLockingFailureException: Attempt to update step execution id=9 with wrong version (1), where current version is 2
	at org.springframework.batch.core.repository.dao.jdbc.JdbcStepExecutionDao.updateStepExecution(JdbcStepExecutionDao.java:254) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.repository.support.SimpleJobRepository.update(SimpleJobRepository.java:154) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
	at java.base/java.lang.reflect.Method.invoke(Method.java:580) ~[na:na]
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:359) ~[spring-aop-7.0.1.jar:7.0.1]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:190) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:158) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:370) ~[spring-tx-7.0.1.jar:spring-tx-7.0.1]
	at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:118) ~[spring-tx-7.0.1.jar:spring-tx-7.0.1]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:179) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:222) ~[spring-aop-7.0.1.jar:spring-aop-7.0.1]
	at jdk.proxy2/jdk.proxy2.$Proxy117.update(Unknown Source) ~[na:na]
	at org.springframework.batch.core.step.AbstractStep.execute(AbstractStep.java:327) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.SimpleStepHandler.handleStep(SimpleStepHandler.java:131) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.AbstractJob.handleStep(AbstractJob.java:397) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.SimpleJob.doExecute(SimpleJob.java:129) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.job.AbstractJob.execute(AbstractJob.java:293) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at org.springframework.batch.core.launch.support.TaskExecutorJobLauncher$1.run(TaskExecutorJobLauncher.java:220) ~[spring-batch-core-6.0.0.jar:6.0.0]
	at java.base/java.lang.Thread.run(Thread.java:1583) ~[na:na]
```

このフロー分析とスタックトレースは、Spring Batch 6でAbstractStepにStoppableStepを実装したことによって導入されたバグを強く示していると思います。このレポートが今後のリリースで課題を特定し解決するのに役立つことを願っています。

最小限の再現可能な例(MCRE)コードやテストの支援など、さらなる情報が必要な場合は、遠慮なくお尋ねください!

ハードワークとこのような貴重なフレームワークの維持に感謝します。


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-05

報告ありがとうございます!

これは課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114) と同じ(または類似)ですか?

### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-12-05

迅速なご返信ありがとうございます!

いいえ、私の課題(#5120)は課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114) とは異なります。

課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114) を分析し、追加の課題を発見しました。
https://github.com/spring-projects/spring-batch/issues/5114 にコメントを残します。

追加情報が必要な場合はお知らせください!

### コメント 3 by fmbenhassine

**作成日**: 2025-12-05

迅速なフィードバックありがとうございます!

両方の課題を詳しく確認します。

### コメント 4 by KILL9-NO-MERCY

**作成日**: 2025-12-05

こんにちは、

この課題の詳細をさらに分析してきましたが、特に spring-projects/spring-batch/issues/5114 で説明されている動作に関して、Step実行について小さな修正が必要でした。

「再現手順」セクションのステップ#4を更新しました:
**AS-IS**: バッチ実行スレッド(チャンク処理スレッド)がterminateOnlyフラグを検出し、チャンク処理ループから正常に終了しようとします。(ChunkOrientedStep.doExecute()の362行目で)

**TO-BE**: ChunkOrientedStep.doExecute()が完了します(停止されない - これは stop() does not prevent upcoming steps to be executed anymore [#5114](https://github.com/spring-projects/spring-batch/issues/5114) に関連)

この特定の動作の詳細は、私たちが議論したstop()ロジックに関連する直接のバグを変更するものではありませんが、ChunkOrientedStepがどのように終了するかについての重要な明確化です。

また、以前この課題は課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114) とは無関係だと述べました。再評価した結果、その発言を訂正しなければなりません: この課題の解決は、確かに課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114) のコメントで選択された方向性と密接に結びついています。現在の問題の解決パスは、課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114) でコメントされた2つのシナリオのうちどちらが採用されるかに直接依存しています。したがって、それらが完全に切り離されていると言うのは正確ではありません。

### コメント 5 by KILL9-NO-MERCY

**作成日**: 2025-12-15

@fmbenhassine
この楽観的ロックの課題に対処するためにPR [#5165](https://github.com/spring-projects/spring-batch/pull/5165) を提出しました。

変更は、更新前にデータベースから最新の状態を取得することで`StepExecution`のバージョンを同期し、停止スレッドと実行スレッド間のバージョン競合を防ぎます。

私のテストでは、停止操作中に`TaskletStep`と`ChunkOrientedStep`の両方で課題が解決されました。ただし、私が見落としている可能性のある副作用がないか、確認していただけると幸いです。

ありがとうございます!

