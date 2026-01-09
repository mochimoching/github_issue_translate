*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# ステップ完了後にChunkTrackerがリセットされない

**課題番号**: #5126

**状態**: closed | **作成者**: A1exL | **作成日**: 2025-11-28

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5126

**関連リンク**:
- Commits:
  - [ced3ed5](https://github.com/spring-projects/spring-batch/commit/ced3ed50b76f48a0e2a20c89d08fb70a36513e11)

## 内容

**バグの説明**
Spring Batchの新しいチャンク処理実装では、チャンク処理の開始前に`ChunkTracker`がステップ実行コンテキストから復元されます。ただし、ステップが完了しても`ChunkTracker`がリセットされません。その結果、次にこのステップが実行される際（同じジョブインスタンス内、同じステップ実行内）、チャンク処理をスキップしてしまい、チャンクが処理されません。

**環境**
- Spring Boot 4.0.0
- Spring Batch 6.0.0
- Java 25
- 組み込みH2データベース

**再現手順**
前提条件：
JDBCジョブリポジトリが使用されています。
`step1`という名前のステップを持つ`TestJob`という名前のジョブがあります。
このステップはチャンクベースのアイテム処理を行っており、複数のアイテムがあります（5つなど）。

1. このジョブを実行します。ステップは正常に完了し、すべてのアイテムが処理されます。
2. 同じジョブを、`incrementer`を使用して新しいパラメータで再実行します。
3. 結果を確認します：`step1`では、前回実行時にチャンク処理が完了したところから処理が再開されます。しかし、実際には前のジョブインスタンスとは関係のない新しいジョブインスタンスであるため、最初から処理が開始されるべきです。

**期待される動作**
`step1`は、前回実行時のチャンク処理の続きではなく、アイテム処理を最初から開始するべきです。

**実際の動作**
`step1`は、前回実行時のチャンクの続きから処理を再開します（つまり、新しいジョブインスタンスであるにもかかわらず、古いチャンクトラッカーのインデックスが使用されます）。

以下は、2つ目のジョブ実行を実行した際のログです：
```
2025-11-28T14:16:44.166+03:00  INFO 17048 --- [BatchApplication] [           main] c.b.BatchApplication                     : Started BatchApplication in 3.127 seconds (process running for 3.732)
2025-11-28T14:16:44.168+03:00  INFO 17048 --- [BatchApplication] [           main] o.s.b.a.b.JobLauncherApplicationRunner   : Running default command line with: []
2025-11-28T14:16:44.367+03:00  INFO 17048 --- [BatchApplication] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=TestJob]] launched with the following parameters: [{'RunIdIncrementer.run.id':'2'}]
2025-11-28T14:16:44.444+03:00  INFO 17048 --- [BatchApplication] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-28T14:16:44.644+03:00  INFO 17048 --- [BatchApplication] [           main] com.batch.BatchApplication               : Step 1 WRITER method called with items.size = 0
2025-11-28T14:16:44.712+03:00  INFO 17048 --- [BatchApplication] [           main] o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 266ms
2025-11-28T14:16:44.750+03:00  INFO 17048 --- [BatchApplication] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=TestJob]] completed with the following parameters: [{'RunIdIncrementer.run.id':'2'}] and the following status: [COMPLETED]
2025-11-28T14:16:44.768+03:00  INFO 17048 --- [BatchApplication] [ionShutdownHook] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Shutdown initiated...
```

メッセージ「Step 1 WRITER method called with items.size = 0」は、新しいジョブインスタンスで処理すべきアイテムがあるにもかかわらず、ステップのライターメソッドが空のリストで呼び出されたことを示しています。

**最小限の再現例**
https://github.com/A1exL/spring-batch6-bugs (branch: reproduce_chunk_issue)
`main`メソッドを実行すると、説明されている動作が再現されます。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-04

この課題を報告し、サンプルを提供していただきありがとうございます！バグであることを確認できました。このメカニズムはフォールトトレランスのために設計されており、ステップが再実行されるシナリオを想定していましたが、問題の原因は`ChunkTracker`がステップ完了時に`StepExecutionContext`からクリアされていないことです。次のパッチで修正します。

### コメント 2 by A1exL

**作成日**: 2025-12-04

ご確認いただきありがとうございます。お忙しい中恐縮ですが、このバグによって我々のソフトウェアリリースが遅れています。修正がいつ頃提供される見込みか、ご存知でしたら教えていただけますでしょうか？ありがとうございます！

### コメント 3 by fmbenhassine

**作成日**: 2025-12-04

修正を既に実装しました（https://github.com/spring-projects/spring-batch/commit/ced3ed50b76f48a0e2a20c89d08fb70a36513e11）。ただし、6.0.1のリリース日はまだ決定していません。決まり次第、このスレッドで共有しますが、おそらく来週末の最初のRCとなるでしょう。

なお、パッチリリースは通常、3〜4週間の窓で行われます。6.0.0は11月29日にリリースされましたので、6.0.1は12月末頃になると予想しています。ただし、6.0.1のマイルストーン（https://github.com/spring-projects/spring-batch/milestone/153）で報告されたすべての課題が解決され次第、早めにリリースを実施する可能性もあります。できる限り早くリリースできるよう努めています。

### コメント 4 by A1exL

**作成日**: 2025-12-04

迅速なご対応と情報のご共有、誠にありがとうございます！

