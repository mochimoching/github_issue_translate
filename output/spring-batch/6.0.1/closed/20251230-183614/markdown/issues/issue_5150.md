# `RemotePartitioningWorkerStepBuilder` doesn't override all configuration methods from `StepBuilder`

**Issue番号**: #5150

**状態**: closed | **作成者**: quaff | **作成日**: 2025-12-09

**ラベル**: type: bug, in: integration

**URL**: https://github.com/spring-projects/spring-batch/issues/5150

**関連リンク**:
- Commits:
  - [37a39e2](https://github.com/spring-projects/spring-batch/commit/37a39e2d5d02f02ee4e73400a4ff5a9cf6f850be)
  - [f04f663](https://github.com/spring-projects/spring-batch/commit/f04f6636362fad92c0a741b0785af699535a5d99)
  - [5e3df33](https://github.com/spring-projects/spring-batch/commit/5e3df332ab1831ac90d4e8234b52d3ce05601244)

## 内容

**Bug description**

`MessageDispatchingException` raised after migration:

```
2025-12-09T11:03:05.207+08:00 ERROR 26960 --- [        task-12] o.s.integration.handler.LoggingHandler   : org.springframework.integration.MessageDispatchingException: Dispatcher has no subscribers, failedMessage=GenericMessage [payload=StepExecutionRequest: [stepExecutionId=14, stepName=importCustomerWorkerStep], headers={sequenceNumber=9, kafka_offset=3, sequenceSize=10, kafka_consumer=org.springframework.kafka.core.DefaultKafkaConsumerFactory$ExtendedKafkaConsumer@b5009fc, kafka_timestampType=CREATE_TIME, correlationId=1:importCustomerWorkerStep, id=ff913842-1559-3203-f6ad-d1af28690380, kafka_receivedPartitionId=2, kafka_receivedTopic=worker, kafka_receivedTimestamp=1765249385033, kafka_groupId=spring-batch-remote-partitioning-kafka, timestamp=1765249385206}]
	at org.springframework.integration.dispatcher.UnicastingDispatcher.doDispatch(UnicastingDispatcher.java:156)
	at org.springframework.integration.dispatcher.UnicastingDispatcher$1.run(UnicastingDispatcher.java:131)
	at org.springframework.integration.util.ErrorHandlingTaskExecutor.lambda$execute$0(ErrorHandlingTaskExecutor.java:64)
```

**Steps to reproduce**

Upgrade from deprecated

```java
stepBuilderFactory.get(stepName).inputChannel(inputChannel).chunk(CHUNK_SIZE, transactionManager)
```
to

```java
stepBuilderFactory.get(stepName).inputChannel(inputChannel).chunk(CHUNK_SIZE).transactionManager(transactionManager)
```


