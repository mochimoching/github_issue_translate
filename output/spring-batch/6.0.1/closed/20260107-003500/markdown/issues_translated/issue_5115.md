*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# MetaDataInstanceFactory.createJobParameters()が現在のジョブパラメータではなく、渡されたものを使用してしまう

**課題番号**: #5115

**状態**: closed | **作成者**: cppwfs | **作成日**: 2025-11-26

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5115

**関連リンク**:
- Commits:
  - [84e0afe](https://github.com/spring-projects/spring-batch/commit/84e0afe15da6f8ebfd0af8a38b4c6fa5fea30d08)

## 内容

**バグの説明**
ユーザーが`jobOperator.restart(long instanceId)`を実行すると、再起動可能な実行が取得されます。その後、`MetaDataInstanceFactory`の`createJobParameters`メソッドが呼び出されます。このメソッドは、リスタート対象のジョブ実行に基づいてジョブパラメータを生成する必要があります。しかし実際には、`MetaDataInstanceFactory`のコンストラクタで渡されたジョブパラメータが使用されてしまいます。

**環境**
- Spring Batch 6.0.0
- Spring Boot 4.0.0
- Java 21

**最小限の再現例**
次の例を実行すると、再起動されたジョブは最新のジョブ実行のパラメータではなく、元のジョブのパラメータで実行されます。
https://github.com/spring-projects/spring-batch/files/16045173/demo.zip

**実際の動作**
```
2025-11-26T10:42:15.324-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] launched with the following parameters: [{'sample':'Glenn1'}]
2025-11-26T10:42:15.361-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T10:42:15.375-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 13ms
2025-11-26T10:42:15.385-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] completed with the following parameters: [{'sample':'Glenn1'}] and the following status: [STOPPED]
2025-11-26T10:42:15.403-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] launched with the following parameters: [{'sample':'Glenn1'}]
2025-11-26T10:42:15.410-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T10:42:15.418-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 7ms
2025-11-26T10:42:15.419-06:00  INFO 49254 --- [demo] [           main] com.example.demo.DemoApplication         : Running Step 2
2025-11-26T10:42:15.420-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step2]
2025-11-26T10:42:15.425-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step2] executed in 5ms
2025-11-26T10:42:15.431-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] completed with the following parameters: [{'sample':'Glenn1'}] and the following status: [COMPLETED]
```

**期待される動作**
再起動では`{'sample':'Glenn2'}`が使用されるはずです：
```
2025-11-26T10:42:15.324-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] launched with the following parameters: [{'sample':'Glenn1'}]
2025-11-26T10:42:15.361-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T10:42:15.375-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 13ms
2025-11-26T10:42:15.385-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] completed with the following parameters: [{'sample':'Glenn1'}] and the following status: [STOPPED]
2025-11-26T10:42:15.403-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] launched with the following parameters: [{'sample':'Glenn2'}]
2025-11-26T10:42:15.410-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step1]
2025-11-26T10:42:15.418-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step1] executed in 7ms
2025-11-26T10:42:15.419-06:00  INFO 49254 --- [demo] [           main] com.example.demo.DemoApplication         : Running Step 2
2025-11-26T10:42:15.420-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.job.SimpleStepHandler     : Executing step: [step2]
2025-11-26T10:42:15.425-06:00  INFO 49254 --- [demo] [           main] o.s.batch.core.step.AbstractStep         : Step: [step2] executed in 5ms
2025-11-26T10:42:15.431-06:00  INFO 49254 --- [demo] [           main] o.s.b.c.l.support.SimpleJobLauncher      : Job: [SimpleJob: [name=sample]] completed with the following parameters: [{'sample':'Glenn2'}] and the following status: [COMPLETED]
```

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-04

サンプルをありがとうございます！間違いなくバグですね。次のパッチで修正します。

