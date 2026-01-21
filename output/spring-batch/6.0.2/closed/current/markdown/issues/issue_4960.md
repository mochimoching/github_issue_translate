# WriteConflict in MongoSequenceIncrementer during parallel job executions

**Issue番号**: #4960

**状態**: closed | **作成者**: benoit-charpiepruvost | **作成日**: 2025-08-21

**ラベル**: type: bug, in: core, has: minimal-example, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4960

**関連リンク**:
- Commits:
  - [d0aef64](https://github.com/spring-projects/spring-batch/commit/d0aef64e33ae3f9189ac447bed730c2c714bd82b)
  - [eac1ff5](https://github.com/spring-projects/spring-batch/commit/eac1ff5e85b5b22d841dcfce62afc87e233ce762)
  - [efbce13](https://github.com/spring-projects/spring-batch/commit/efbce13f0faf512f22281f8e54c3d637b2eacd5c)

## 内容

**Bug Description**
When executing multiple Spring Batch jobs in parallel using `MongoDBJobRepository`, write conflicts occur in the sequence generation for job instance IDs. The `MongoSequenceIncrementer.nextLongValue()` method attempts to find and modify the sequence document atomically, but concurrent executions cause MongoDB WriteConflict errors.

Root Cause: The `findAndModify` operation in `MongoSequenceIncrementer` is not properly handling concurrent access patterns.
Impact: Prevents parallel job execution, causing job failures with `DataIntegrityViolationException`.

```
2025-08-21T08:42:16.167+02:00 ERROR 1 --- [Container#1-223] .d.a.f.s.s.MaterializedCollectionService : Cannot execute job sync job correctly
org.springframework.dao.DataIntegrityViolationException: Command failed with error 112 (WriteConflict): 'Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.' on server xxx.mongodb.net:1026. The full response is {"errorLabels": ["TransientTransactionError"], "ok": 0.0, "errmsg": "Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.", "code": 112, "codeName": "WriteConflict", "$clusterTime": {"clusterTime": {"$timestamp": {"t": 1755758536, "i": 4}}, "signature": {"hash": {"$binary": {"base64": "xxx=", "subType": "00"}}, "keyId": xxx}}, "operationTime": {"$timestamp": {"t": 1755758536, "i": 4}}}
    at org.springframework.data.mongodb.core.MongoExceptionTranslator.doTranslateException(MongoExceptionTranslator.java:141) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.data.mongodb.core.MongoExceptionTranslator.translateExceptionIfPossible(MongoExceptionTranslator.java:74) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.data.mongodb.core.MongoTemplate.potentiallyConvertRuntimeException(MongoTemplate.java:3033) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.data.mongodb.core.MongoTemplate.execute(MongoTemplate.java:609) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.batch.core.repository.dao.MongoSequenceIncrementer.nextLongValue(MongoSequenceIncrementer.java:47) ~[spring-batch-core-5.2.2.jar:5.2.2]
    at org.springframework.batch.core.repository.dao.MongoJobInstanceDao.createJobInstance(MongoJobInstanceDao.java:80) ~[spring-batch-core-5.2.2.jar:5.2.2]
    at org.springframework.batch.core.repository.support.SimpleJobRepository.createJobExecution(SimpleJobRepository.java:168) ~[spring-batch-core-5.2.2.jar:5.2.2]
    at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
    at java.base/java.lang.reflect.Method.invoke(Method.java:580) ~[na:na]
    at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:359) ~[spring-aop-6.2.7.jar:6.2.7]
    at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:196) ~[spring-aop-6.2.7.jar:6.2.7]
    at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163) ~[spring-aop-6.2.7.jar:6.2.7]
    at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:380) ~[spring-tx-6.2.7.jar:6.2.7]
    at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:119) ~[spring-tx-6.2.7.jar:6.2.7]
    at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184) ~[spring-aop-6.2.7.jar:6.2.7]
    at org.springframework.batch.core.repository.support.AbstractJobRepositoryFactoryBean.lambda$getObject$0(AbstractJobRepositoryFactoryBean.java:204) ~[spring-batch-core-5.2.2.jar:5.2.2]
    at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184) ~[spring-aop-6.2.7.jar:6.2.7]
    at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:223) ~[spring-aop-6.2.7.jar:6.2.7]
    at jdk.proxy2/jdk.proxy2.$Proxy125.createJobExecution(Unknown Source) ~[na:na]
    at org.springframework.batch.core.launch.support.TaskExecutorJobLauncher.run(TaskExecutorJobLauncher.java:143) ~[spring-batch-core-5.2.2.jar:5.2.2]
...
    at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
    at java.base/java.lang.reflect.Method.invoke(Method.java:580) ~[na:na]
    at org.springframework.messaging.handler.invocation.InvocableHandlerMethod.doInvoke(InvocableHandlerMethod.java:169) ~[spring-messaging-6.2.7.jar:6.2.7]
    at org.springframework.messaging.handler.invocation.InvocableHandlerMethod.invoke(InvocableHandlerMethod.java:119) ~[spring-messaging-6.2.7.jar:6.2.7]
    at io.awspring.cloud.sqs.listener.adapter.AbstractMethodInvokingListenerAdapter.invokeHandler(AbstractMethodInvokingListenerAdapter.java:56) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.adapter.MessagingMessageListenerAdapter.onMessage(MessagingMessageListenerAdapter.java:41) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.AsyncComponentAdapters$AbstractThreadingComponentAdapter.lambda$withConsumerThreadLocalScope$3(AsyncComponentAdapters.java:206) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.AsyncComponentAdapters$AbstractThreadingComponentAdapter.runInSameThread(AsyncComponentAdapters.java:136) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.AsyncComponentAdapters$AbstractThreadingComponentAdapter.execute(AsyncComponentAdapters.java:127) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.AsyncComponentAdapters$BlockingMessageListenerAdapter.onMessage(AsyncComponentAdapters.java:262) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.pipeline.MessageListenerExecutionStage.process(MessageListenerExecutionStage.java:49) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.pipeline.MessageProcessingPipelineBuilder$ComposingMessagePipelineStage.lambda$process$0(MessageProcessingPipelineBuilder.java:80) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at java.base/java.util.concurrent.CompletableFuture.uniComposeStage(CompletableFuture.java:1187) ~[na:na]
    at java.base/java.util.concurrent.CompletableFuture.thenCompose(CompletableFuture.java:2341) ~[na:na]
    at io.awspring.cloud.sqs.listener.pipeline.MessageProcessingPipelineBuilder$ComposingMessagePipelineStage.process(MessageProcessingPipelineBuilder.java:80) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.pipeline.MessageProcessingPipelineBuilder$FutureComposingMessagePipelineStage.process(MessageProcessingPipelineBuilder.java:104) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.pipeline.MessageProcessingPipelineBuilder$FutureComposingMessagePipelineStage.process(MessageProcessingPipelineBuilder.java:104) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.pipeline.MessageProcessingPipelineBuilder$FutureComposingMessagePipelineStage.process(MessageProcessingPipelineBuilder.java:104) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.pipeline.MessageProcessingPipelineBuilder$FutureComposingMessagePipelineStage.process(MessageProcessingPipelineBuilder.java:104) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at io.awspring.cloud.sqs.listener.sink.AbstractMessageProcessingPipelineSink.lambda$execute$0(AbstractMessageProcessingPipelineSink.java:135) ~[spring-cloud-aws-sqs-3.4.0.jar:3.4.0]
    at java.base/java.util.concurrent.CompletableFuture$AsyncSupply.run(CompletableFuture.java:1768) ~[na:na]
    at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1144) ~[na:na]
    at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:642) ~[na:na]
    at java.base/java.lang.Thread.run(Thread.java:1583) ~[na:na]
Caused by: com.mongodb.MongoCommandException: Command failed with error 112 (WriteConflict): 'Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.' on server xxx.mongodb.net:1026. The full response is {"errorLabels": ["TransientTransactionError"], "ok": 0.0, "errmsg": "Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.", "code": 112, "codeName": "WriteConflict", "$clusterTime": {"clusterTime": {"$timestamp": {"t": 1755758536, "i": 4}}, "signature": {"hash": {"$binary": {"base64": "xxx=", "subType": "00"}}, "keyId": xxx}}, "operationTime": {"$timestamp": {"t": 1755758536, "i": 4}}}
    at com.mongodb.internal.connection.ProtocolHelper.getCommandFailureException(ProtocolHelper.java:210) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.InternalStreamConnection.receiveCommandMessageResponse(InternalStreamConnection.java:520) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.InternalStreamConnection.sendAndReceiveInternal(InternalStreamConnection.java:448) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.InternalStreamConnection.lambda$sendAndReceive$0(InternalStreamConnection.java:375) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.InternalStreamConnection.sendAndReceive(InternalStreamConnection.java:378) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.UsageTrackingInternalConnection.sendAndReceive(UsageTrackingInternalConnection.java:111) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.DefaultConnectionPool$PooledConnection.sendAndReceive(DefaultConnectionPool.java:747) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.CommandProtocolImpl.execute(CommandProtocolImpl.java:61) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.DefaultServer$DefaultServerProtocolExecutor.execute(DefaultServer.java:208) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.DefaultServerConnection.executeProtocol(DefaultServerConnection.java:112) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.DefaultServerConnection.command(DefaultServerConnection.java:82) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.DefaultServerConnection.command(DefaultServerConnection.java:74) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.connection.DefaultServer$OperationCountTrackingConnection.command(DefaultServer.java:298) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.lambda$executeRetryableWrite$10(SyncOperationHelper.java:267) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.lambda$withSourceAndConnection$0(SyncOperationHelper.java:131) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.withSuppliedResource(SyncOperationHelper.java:156) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.lambda$withSourceAndConnection$1(SyncOperationHelper.java:130) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.withSuppliedResource(SyncOperationHelper.java:156) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.withSourceAndConnection(SyncOperationHelper.java:129) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.lambda$executeRetryableWrite$11(SyncOperationHelper.java:252) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperationHelper.lambda$decorateWriteWithRetries$12(SyncOperationHelper.java:308) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.async.function.RetryingSyncSupplier.get(RetryingSyncSupplier.java:67) ~[mongodb-driver-core-5.4.0.jar:na]
    at com.mongodb.internal.operation.SyncOperat...
```

**Environment**
Spring boot 3.5.0
Spring batch 5.2.2
Spring Data MongoDB 3.5.0
MongoDB Driver: 5.4.0
Java 21
MongoDB Server Version: 8.x
MongoDB Cluster Type: Atlas

**Steps to reproduce**
Just start several threads that are launching one job

**Minimal Complete Reproducible example**
Add the following test in MongoDBJobRepositoryIntegrationTests
```java
@Test
	void testParallelJobExecution(@Autowired JobOperator jobOperator, @Autowired Job job) throws Exception {
		int parallelJobs = 10;
		Thread[] threads = new Thread[parallelJobs];
		JobExecution[] executions = new JobExecution[parallelJobs];

		for (int i = 0; i < parallelJobs; i++) {
			final int idx = i;
			threads[i] = new Thread(() -> {
				JobParameters jobParameters = new JobParametersBuilder()
					.addString("name", "foo" + idx)
					.addLocalDateTime("runtime", LocalDateTime.now())
					.toJobParameters();
				try {
					executions[idx] = jobOperator.start(job, jobParameters);
				} catch (Exception e) {
					throw new RuntimeException(e);
				}
			});
			threads[i].start();
		}

		for (Thread t : threads) {
			t.join();
		}

		for (JobExecution exec : executions) {
			Assertions.assertNotNull(exec);
			Assertions.assertEquals(ExitStatus.COMPLETED, exec.getExitStatus());
		}

		MongoCollection<Document> jobInstancesCollection = mongoTemplate.getCollection("BATCH_JOB_INSTANCE");
		MongoCollection<Document> jobExecutionsCollection = mongoTemplate.getCollection("BATCH_JOB_EXECUTION");
		MongoCollection<Document> stepExecutionsCollection = mongoTemplate.getCollection("BATCH_STEP_EXECUTION");

		Assertions.assertEquals(parallelJobs, jobInstancesCollection.countDocuments());
		Assertions.assertEquals(parallelJobs, jobExecutionsCollection.countDocuments());
		Assertions.assertEquals(parallelJobs * 2, stepExecutionsCollection.countDocuments());

		// dump results for inspection
		dump(jobInstancesCollection, "job instance = ");
		dump(jobExecutionsCollection, "job execution = ");
		dump(stepExecutionsCollection, "step execution = ");
	}
```



## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-18

Thank you for reporting this issue and for providing a failing test!

This is a valid issue. What's surprising to me is that even an `Isolation.SERIALIZABLE` at the job repository level the issue still happens (I will review this as part of #4956 ). What is even more surprising is that synchronizing thread access to `MongoSequenceIncrementer#nextLongValue` does not seem to have an effect neither. I will also check with the MongoDB experts regarding the best practices of write concern configuration in MongoDB and see what we can do to improve the defaults in Spring Batch.

### コメント 2 by diydriller

**作成日**: 2025-12-05

@fmbenhassine 
I'm looking at this issue with interest, can I work on it?

### コメント 3 by fmbenhassine

**作成日**: 2025-12-05

@diydriller Sure! Thank you for your offer to help 🙏

### コメント 4 by quaff

**作成日**: 2025-12-08

@diydriller FYI, I proposed #5145 which doesn't introduce new ID algorithm, keep id backward-compatibility.

### コメント 5 by diydriller

**作成日**: 2025-12-08

@quaff 
Thank you for your feedback. 
I ran the `testParallelJobExecution` test code with the PR you provided and confirmed that the write conflict still occurred. 
Write conflicts occur because multiple threads access the same document and perform inc operations, and it seems that retry logic alone cannot resolve them.

### コメント 6 by quaff

**作成日**: 2025-12-09

> I ran the `testParallelJobExecution` test code with the PR you provided and confirmed that the write conflict still occurred. Write conflicts occur because multiple threads access the same document and perform inc operations, and it seems that retry logic alone cannot resolve them.

My PR mitigate not eliminate the write conflict, it's recommended retry limited times for optimistic locking failure.

### コメント 7 by banseok1216

**作成日**: 2025-12-09

I’m also running into this with MongoDBJobRepository.

To me #5145 and #5144 serve different purposes: #5145 is a small, backwards-compatible fix (keep the current numeric sequence IDs and just add retry on transient write conflicts), while #5144 is a bigger change (TSID, some people might rely on).

Since 6.0.0 is already out, I’d really like to see #5145 go into a 6.x bugfix release (and maybe backported to the latest 5.2.x), and have #5144 targeted at the next major version where the ID change can be treated as a breaking change.

### コメント 8 by fmbenhassine

**作成日**: 2026-01-21

> Since 6.0.0 is already out, I’d really like to see [#5145](https://github.com/spring-projects/spring-batch/pull/5145) go into a 6.x bugfix release (and maybe backported to the latest 5.2.x), and have [#5144](https://github.com/spring-projects/spring-batch/pull/5144) targeted at the next major version where the ID change can be treated as a breaking change.

@banseok1216 you nailed it! I will merge #5145 in 6.0.2 and back port it to 5.2.5, and schedule #5144 for v7.

@diydriller Thank you for your PR! I will keep it open and review it when we start working on v7.

