# stop()が今後実行されるステップの実行を防げなくなった

**Issue番号**: #5114

**状態**: closed | **作成者**: andre-bugay | **作成日**: 2025-11-27

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5114

**関連リンク**:
- Commits:
  - [29f5ecf](https://github.com/spring-projects/spring-batch/commit/29f5ecf567cc21b5ce3dd9a41283d227a85c3667)
  - [e5fbc2a](https://github.com/spring-projects/spring-batch/commit/e5fbc2a0387858f5f95009e3a032d2864398f9ac)
  - [644d7e6](https://github.com/spring-projects/spring-batch/commit/644d7e6997c4e29822be580dab8e6f65713e17be)

## 内容

Spring Batch 6ではジョブを停止できなくなったようです。
`stop()`を呼び出した後、すべてのステップが実行され、その後ジョブがFAILEDとしてマークされます。

Spring Batch 5でのフローは:
`STARTED` -> `STOPPING` -> ステップ実行をterminateOnlyとしてマーク -> `STOPPED`

Spring Batch 6でのフローは:
`STARTED` -> `STOPPING` -> `STOPPED` -> `FAILED`

私の理解が正しければ、この変更の根本原因は以下の新しい行です:


https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/SimpleJobOperator.java#L348

その直後の
`jobRepository.update(jobExecution);`
が以下をチェックします:
https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/support/SimpleJobRepository.java#L139

endTimeがその直前に設定されているため、これは常にfalseになります。
jobStateは`STOPPING`から`STOPPED`に直接設定されます。

**結果**
`SimpleJobRepository#update(StepExecution)` -> `checkForInterruption(stepExecution)`内で、以下のチェックは
https://github.com/spring-projects/spring-batch/blob/c8a0528bf1ee3ff8015ae1ddaaef368355f32ed3/spring-batch-core/src/main/java/org/springframework/batch/core/repository/support/SimpleJobRepository.java#L186-L188
決してtrueにならず、ステップはterminateOnlyとしてマークされません。

これは意図されたものでしょうか?また、ジョブが停止されたら未開始のステップの実行を防ぐにはどうすればよいでしょうか?


## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2025-12-05

こんにちは。私もこの課題の根本原因を確認しました。参考のため、私の調査結果を共有したいと思います。

ご指摘の通り、コミットe5fbc2aが以下を導入しました:
```java
jobExecution.setEndTime(LocalDateTime.now());
```

この変更により、SimpleJobRepository内の以下のロジックが実行されます:
```java
if (jobExecution.getStatus() == BatchStatus.STOPPING && jobExecution.getEndTime() != null) {
    if (logger.isInfoEnabled()) {
       logger.info("Upgrading job execution status from STOPPING to STOPPED since it has already ended.");
    }
    jobExecution.upgradeStatus(BatchStatus.STOPPED);
}
```
履歴を見ると、これは意図的な変更のようです(ただし、この特定のポイントでステータスをSTOPPEDに設定する正確な理由は不明です)。解決策は、Spring Batchチームがこのコード変更を保持するか元に戻すかによって異なります。

## シナリオ1: jobExecution.setEndTime(LocalDateTime.now())を保持する(現在のBatch 6の動作)
`jobExecution.setEndTime(LocalDateTime.now())`を保持する必要がある場合、以下が課題となります:

カスタムStep実装を作成して使用していない限り、提供されているTaskletStepまたは新しく追加されたChunkOrientedStep(Batch 6)を使用している場合、SimpleJobOperatorの374行目で以下のロジックが実行されます:
```java
stoppableStep.stop(stepExecution);
// default void stop(StepExecution stepExecution) {
//     stepExecution.setTerminateOnly();
//     stepExecution.setStatus(BatchStatus.STOPPED);
//     stepExecution.setExitStatus(ExitStatus.STOPPED);
//     stepExecution.setEndTime(LocalDateTime.now());
// }
```
これにより、StepExecutionがterminateOnlyに設定され、SimpleJobOperatorの375行目でデータベース(メタデータリポジトリ)に永続化されます。

核心的な問題は、`SimpleJobOperator.stop()`呼び出しによって更新されるStepExecutionオブジェクトが、現在アクティブに実行されているStepスレッドで使用されているオブジェクトインスタンスと同じではないことです。したがって、中断を機能させるには、すべてのチャンクトランザクションコミット前およびItemStream.update()呼び出し後(または履歴的なTaskletStepロジックに基づく同様の境界)に、メタデータリポジトリから最新のStepExecutionステータスを取得するロジックを実行中のStep(TaskletStepとChunkOrientedStepの両方)に追加する必要があります。


## シナリオ2: e5fbc2aで追加されたコードを元に戻す(レガシー動作に戻る)
Spring Batchチームがe5fbc2aで追加されたコードを元に戻すことを選択した場合、あなたが言及したロジックはStepを適切に中断します。ただし、TaskletStepのみが正しく中断されます。

`TaskletStep.doExecute()`を見ると、すべてのトランザクションコミットの直前(`Tasklet.execute()`の完了後 - 464行目付近)に`getJobRepository().update(stepExecution);`を呼び出しています。この更新により、あなたが引用したロジックがトリガーされます:
```java
private void checkForInterruption(StepExecution stepExecution) {
    JobExecution jobExecution = stepExecution.getJobExecution();
    jobExecutionDao.synchronizeStatus(jobExecution); // <--- DBから更新されたJobExecutionステータスを読み取る
    if (jobExecution.isStopping()) {
       logger.info("Parent JobExecution is stopped, so passing message on to StepExecution");
       stepExecution.setTerminateOnly(); // <--- terminateOnlyを設定
    }
}
```
これにより、実行中のStepがJobOperatorによって変更された最新のJobExecutionステータスを読み取り、terminateOnlyを設定できます。

問題は、ChunkOrientedStepには同じロジックがないことです。`JobRepository.updateExecutionContext()`のみを呼び出します。

したがって、Spring Batchチームがシナリオ2を進める場合、適切な中断を確保するために、ChunkOrientedStep実装にも`getJobRepository().update(stepExecution);`の呼び出しを追加する必要があります。

この分析が継続中の作業に役立つことを願っています!

### コメント 2 by fmbenhassine

**作成日**: 2025-12-05

@andre-bugay @KILL9-NO-MERCY この課題を提起し、根本原因を分析する時間を取っていただき、ありがとうございます! 確かに、ジョブの停止が機能していないようですが、d4a7dfd25f2782fba7a1563ab62aa116b4f6d33fで導入した[グレースフルシャットダウンサンプル](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/shutdown)は期待通りに動作していました。その後のコミットでstop機能を壊したようです。このサンプルには手動ステップ(プロセスへの割り込み信号の送信)が含まれており、CI上で自動的にリグレッションを検出することが困難になっている点が気になります。

これを確認し、今後の6.0.1で修正を予定します。

### コメント 3 by fmbenhassine

**作成日**: 2025-12-12

> 解決策は、Spring Batchチームがこのコード変更を保持するか元に戻すかによって異なります。

リグレッションを引き起こした変更を元に戻すことには反対ではありません。

> ご指摘の通り、コミット [e5fbc2a](https://github.com/spring-projects/spring-batch/commit/e5fbc2a0387858f5f95009e3a032d2864398f9ac) が以下を導入しました:

e5fbc2a0387858f5f95009e3a032d2864398f9acを元に戻しても課題は解決しないようですので、おそらくシナリオ1は最良の選択肢ではありません。このコミットが原因だと思います: db6ef7b067e0daeee59c1baea03a0acfed4f5cfc、しかしまだ調査中です。

> したがって、Spring Batchチームがシナリオ2を進める場合、適切な中断を確保するために、ChunkOrientedStep実装にもgetJobRepository().update(stepExecution);の呼び出しを追加する必要があります。

@KILL9-NO-MERCY このパッチを試されましたか? 私もこれを試しましたが、どちらも役に立たなかったようです。

すでに課題を修正された方がいらっしゃれば、PRでパッチをいただけると幸いです(重複作業を避けるため)。

### コメント 4 by fmbenhassine

**作成日**: 2025-12-12

もう少し文脈を説明すると: 前回のコメントで共有した試みは楽観的ロック例外を引き起こしました(テストには[この例](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/shutdown)を使用しました)。課題 [#5020](https://github.com/spring-projects/spring-batch/issues/5020) に関連する何かが関与している可能性があると疑っていますが、おそらく間違っているでしょう。cc @quaff。おそらく、ここでデータベース同期が欠けています: https://github.com/spring-projects/spring-batch/blob/main/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L476。

調査を続けますが、すでに課題を修正された方がいらっしゃれば、重複作業を避けるためにPRでパッチをいただけると幸いです。よろしくお願いします 🙏

### コメント 5 by quaff

**作成日**: 2025-12-15

> 課題 [#5020](https://github.com/spring-projects/spring-batch/issues/5020) に関連する何かが関与している可能性があると疑っていますが、おそらく間違っているでしょう。

課題 [#5020](https://github.com/spring-projects/spring-batch/issues/5020) はマルチプロセスに関連していますが、この課題ではそれについて言及されていません。

### コメント 6 by KILL9-NO-MERCY

**作成日**: 2025-12-15

@andre-bugay @fmbenhassine

この課題に対処するためにPR [#5165](https://github.com/spring-projects/spring-batch/pull/5165) を提出しました。

このPRは以下の方法で`terminateOnly`フラグの設定を修正します:
1. `getStepExecution()`を介して外部から停止されたStepExecutionを検出し、`isStopped()`ステータスをチェック
2. `JobRepository.update(StepExecution)`でバージョンを同期し、`terminateOnly`を設定
3. TaskletStepの動作に合わせてChunkOrientedStepに`JobRepository.update(stepExecution)`呼び出しを追加

課題 [#5120](https://github.com/spring-projects/spring-batch/issues/5120) で述べたように、私のテストでは課題 [#5120](https://github.com/spring-projects/spring-batch/issues/5120)(OptimisticLockingFailureException)と課題 [#5114](https://github.com/spring-projects/spring-batch/issues/5114)(terminateOnlyが設定されない)の両方がこれらの変更で解決されました。

ただし、私が見落としている可能性のある副作用がないか、確認していただけると幸いです。ありがとうございます!

