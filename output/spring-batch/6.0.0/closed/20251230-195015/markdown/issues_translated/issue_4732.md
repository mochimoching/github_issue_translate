*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ResourcelessJobRepositoryをパーティション化されたステップで使用した際の不正確なエラーメッセージ

**Issue番号**: #4732

**状態**: closed | **作成者**: monnetchr | **作成日**: 2024-12-10

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4732

**関連リンク**:
- Commits:
  - [69331c5](https://github.com/spring-projects/spring-batch/commit/69331c516dbb95cc23d4340fe083460fc376551e)

## 内容

**バグの説明**

`ResourcelessJobRepository`は`Partitioner`と併用できません。

```

[main] ERROR org.springframework.batch.core.step.AbstractStep - Encountered an error executing step step in job partitionJob

org.springframework.batch.core.JobExecutionException: Cannot restart step from STARTING status.  The old execution may still be executing, so you may need to verify manually that this is the case.

```



**再現手順**

`spring-batch-samples/src/main/resources/simple-job-launcher-context.xml`を`ResourcelessJobRepository`を使用するように変更し、`spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/file/PartitionFileJobFunctionalTests.java`を実行してください。





## コメント

### コメント 1 by fmbenhassine

**作成日**: 2024-12-10

リソースレスジョブリポジトリは、実行コンテキストを含む機能(パーティション化されたステップを含む)をサポートしていません。これはクラスのJavadoc(https://docs.spring.io/spring-batch/docs/current/api/org/springframework/batch/core/repository/support/ResourcelessJobRepository.html)とリファレンスドキュメント(https://docs.spring.io/spring-batch/reference/whatsnew.html#new-resourceless-job-repository)に記載されています。



バッチメタデータをサポートする別のジョブリポジトリ実装を設定する必要があります。この説明でご質問に回答できたと考えておりますので、今回はこのissueをクローズしますが、さらにサポートが必要な場合はコメントを追加してください。ありがとうございます。

### コメント 2 by fmbenhassine

**作成日**: 2024-12-10

エラーメッセージが紛らわしいことは認めざるを得ません。そのサンプルには再起動がないにもかかわらず、メッセージでは再起動について言及しています。このissueを再度オープンし、機能強化に変更します。

### コメント 3 by kwondh5217

**作成日**: 2025-03-18

こんにちは @fmbenhassine、このissueに貢献したいと思います。

明確性を向上させるために、`ResourcelessJobRepository`をパーティション化されたステップで使用することを明示的に防ぐために例外をスローすることは意味があるでしょうか?

提案する変更:
```java
@Override
public Set<StepExecution> split(StepExecution stepExecution, int gridSize) throws JobExecutionException {
    if (jobRepository instanceof ResourcelessJobRepository) {
        throw new JobExecutionException("ResourcelessJobRepository cannot be used with partitioned steps "
                                        + "as it does not support execution context.");
    }
    ...

### コメント 4 by fmbenhassine

**作成日**: 2025-11-14

これは90d895955d951156849ba6fa018676273fdbe2c4の一部として修正されました。

> **再現手順**
> `spring-batch-samples/src/main/resources/simple-job-launcher-context.xml`を`ResourcelessJobRepository`を使用するように変更し、`spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/file/PartitionFileJobFunctionalTests.java`を実行してください。

6.0.0-RC2でそのサンプルを試したところ、次のように出力されました:

```
12:27:34.354 [main] INFO  o.s.b.c.c.x.CoreNamespaceHandler - DEPRECATION NOTE: The batch XML namespace is deprecated as of Spring Batch 6.0 and will be removed in version 7.0.
12:27:34.566 [main] INFO  o.s.b.c.s.i.ChunkOrientedTasklet - DEPRECATION NOTE: The legacy implementation of the chunk-oriented processing model is deprecated as of Spring Batch 6.0 and will be removed in version 7.0.
12:27:35.250 [main] INFO  o.s.b.c.l.s.TaskExecutorJobLauncher - Job: [FlowJob: [name=partitionJob]] launched with the following parameters: [{JobParameter{name='random', value=1393027390114809605, type=class java.lang.Long, identifying=true}}]
12:27:35.254 [main] INFO  o.s.b.c.j.SimpleStepHandler - Executing step: [step]
12:27:35.286 [SimpleAsyncTaskExecutor-2] INFO  o.s.b.c.s.AbstractStep - Step: [step1:partition1] executed in 28ms
12:27:35.286 [SimpleAsyncTaskExecutor-1] INFO  o.s.b.c.s.AbstractStep - Step: [step1:partition0] executed in 28ms
12:27:35.287 [main] INFO  o.s.b.c.s.AbstractStep - Step: [step] executed in 32ms
12:27:35.288 [main] INFO  o.s.b.c.l.s.TaskExecutorJobLauncher - Job: [FlowJob: [name=partitionJob]] completed with the following parameters: [{JobParameter{name='random', value=1393027390114809605, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 34ms
```

紛らわしいエラーメッセージはもう記録されていません。

