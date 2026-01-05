# Cannot deserialize TopicPartition from JobRepository

**Issue番号**: #3797

**状態**: closed | **作成者**: MinJunKweon | **作成日**: 2020-11-02

**ラベル**: in: infrastructure, type: bug, has: votes, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/3797

**関連リンク**:
- Commits:
  - [bab03c1](https://github.com/spring-projects/spring-batch/commit/bab03c1d7317c2ac27c6938c0b4cbf577542963a)
  - [a5e43a0](https://github.com/spring-projects/spring-batch/commit/a5e43a02b0708a707d41f4c1b3e5436e67845ddd)

## 内容

Hi.

I use MySQL for JobRepository. It serialize ExecutionContext as String by JacksonObjectMapper.
It seems to forcing to `Map`'s key type must be `String`. (`Map<String, Object>`)
You can see [this](https://github.com/spring-projects/spring-batch/blob/master/spring-batch-core/src/main/java/org/springframework/batch/core/repository/dao/Jackson2ExecutionContextStringSerializer.java#L130).

For Example, `SHORT_CONTEXT` in `BATCH_STEP_EXECUTION_CONTEXT`:
```
{"batch.taskletType":"org.springframework.batch.core.step.item.ChunkOrientedTasklet","topic.partition.offsets":["java.util.HashMap",{"test-topic":["java.lang.Long",42]}],"batch.stepType":"org.springframework.batch.core.step.tasklet.TaskletStep"}
```

However, `KafkaItemReader` uses `TopicPartition` as key. So It has problem in deserializing `ExecutionContext`. You can see [this](https://github.com/spring-projects/spring-batch/blob/master/spring-batch-infrastructure/src/main/java/org/springframework/batch/item/kafka/KafkaItemReader.java#L168).

```java
        @Override
	public void open(ExecutionContext executionContext) {
		...
		if (this.saveState && executionContext.containsKey(TOPIC_PARTITION_OFFSETS)) {
			Map<TopicPartition, Long> offsets = (Map<TopicPartition, Long>) executionContext.get(TOPIC_PARTITION_OFFSETS);
			for (Map.Entry<TopicPartition, Long> entry : offsets.entrySet()) {
				this.partitionOffsets.put(entry.getKey(), entry.getValue() == 0 ? 0 : entry.getValue() + 1);
			}
		}
                ...
	}
```

```
2020-11-02 14:30:50 [main] ERROR o.s.batch.core.step.AbstractStep - Encountered an error executing step testStep in job testJob
java.lang.ClassCastException: java.lang.String incompatible with org.apache.kafka.common.TopicPartition
	at org.springframework.batch.item.kafka.KafkaItemReader$$Lambda$911/00000000EF270020.accept(Unknown Source)
	at java.base/java.util.LinkedHashMap.forEach(LinkedHashMap.java:684)
	at org.springframework.batch.item.kafka.KafkaItemReader.open(KafkaItemReader.java:174)
	at org.springframework.batch.item.kafka.KafkaItemReader$$FastClassBySpringCGLIB$$9111feb4.invoke(<generated>)
	at org.springframework.cglib.proxy.MethodProxy.invoke(MethodProxy.java:218)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.invokeJoinpoint(CglibAopProxy.java:769)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.proceed(CglibAopProxy.java:747)
	at org.springframework.aop.support.DelegatingIntroductionInterceptor.doProceed(DelegatingIntroductionInterceptor.java:136)
	at org.springframework.aop.support.DelegatingIntroductionInterceptor.invoke(DelegatingIntroductionInterceptor.java:124)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at org.springframework.aop.framework.CglibAopProxy$CglibMethodInvocation.proceed(CglibAopProxy.java:747)
	at org.springframework.aop.framework.CglibAopProxy$DynamicAdvisedInterceptor.intercept(CglibAopProxy.java:689)
	at org.springframework.batch.item.kafka.KafkaItemReader$$EnhancerBySpringCGLIB$$314cf4f9.open(<generated>)
	at org.springframework.batch.item.support.CompositeItemStream.open(CompositeItemStream.java:104)
	at org.springframework.batch.core.step.tasklet.TaskletStep.open(TaskletStep.java:311)
	at org.springframework.batch.core.step.AbstractStep.execute(AbstractStep.java:205)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:344)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:198)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.aop.support.DelegatingIntroductionInterceptor.doProceed(DelegatingIntroductionInterceptor.java:136)
	at org.springframework.aop.support.DelegatingIntroductionInterceptor.invoke(DelegatingIntroductionInterceptor.java:124)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:212)
	at com.sun.proxy.$Proxy92.execute(Unknown Source)
	at org.springframework.batch.core.job.SimpleStepHandler.handleStep(SimpleStepHandler.java:148)
	at org.springframework.batch.core.job.AbstractJob.handleStep(AbstractJob.java:410)
	at org.springframework.batch.core.job.SimpleJob.doExecute(SimpleJob.java:136)
	at org.springframework.batch.core.job.AbstractJob.execute(AbstractJob.java:319)
	at org.springframework.batch.core.launch.support.SimpleJobLauncher$1.run(SimpleJobLauncher.java:147)
	at org.springframework.core.task.SyncTaskExecutor.execute(SyncTaskExecutor.java:50)
	at org.springframework.batch.core.launch.support.SimpleJobLauncher.run(SimpleJobLauncher.java:140)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:566)
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:344)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:198)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.batch.core.configuration.annotation.SimpleBatchConfiguration$PassthruAdvice.invoke(SimpleBatchConfiguration.java:127)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:186)
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:212)
	at com.sun.proxy.$Proxy129.run(Unknown Source)
	at org.springframework.boot.autoconfigure.batch.JobLauncherCommandLineRunner.execute(JobLauncherCommandLineRunner.java:192)
	at org.springframework.boot.autoconfigure.batch.JobLauncherCommandLineRunner.executeLocalJobs(JobLauncherCommandLineRunner.java:166)
	at org.springframework.boot.autoconfigure.batch.JobLauncherCommandLineRunner.launchJobFromProperties(JobLauncherCommandLineRunner.java:153)
	at org.springframework.boot.autoconfigure.batch.JobLauncherCommandLineRunner.run(JobLauncherCommandLineRunner.java:148)
	at org.springframework.boot.SpringApplication.callRunner(SpringApplication.java:784)
	at org.springframework.boot.SpringApplication.callRunners(SpringApplication.java:768)
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:322)
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1226)
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1215)
        ...
```

I think It should be deserialize by String first.
And then, convert `String` to `TopicPartition` in `KafkaItemReader`.

Like this,
```java
Map<String, Long> offsets = (Map<String, Long>) executionContext.get(TOPIC_PARTITION_OFFSETS);
for (Map.Entry<String, Long> entry : offsets.entrySet()) {
        TopicPartition topicPartition = getTopicPartitionFromString(entry.getKey());
	this.partitionOffsets.put(topicPartition, entry.getValue() == 0 ? 0 : entry.getValue() + 1);
}
```

## コメント

### コメント 1 by langzime

**作成日**: 2021-08-13

same question

### コメント 2 by noojung

**作成日**: 2024-12-23

same question too

### コメント 3 by noojung

**作成日**: 2025-06-02

Jackson2ExecutionContextStringSerializer always forces all map keys to be String.
So we can't use Map<TopicPartition, Long> directly. 

Instead, I think we can store only the partition number (as a String) in update(),nd then reconstruct the full TopicPartition in open() by using the topic name provided to the constructor.

For example:

```
	@Override
	public void update(ExecutionContext executionContext) {
		if (this.saveState) {
			Map<String, Long> offsets = new HashMap<>();
			for (Map.Entry<TopicPartition, Long> entry : this.partitionOffsets.entrySet()) {
				offsets.put(String.valueOf(entry.getKey().partition()), entry.getValue());
			}
			executionContext.put(TOPIC_PARTITION_OFFSETS, offsets);
		}
		this.kafkaConsumer.commitSync();
	}

```

```
	@Override
	public void open(ExecutionContext executionContext) {
		this.kafkaConsumer = new KafkaConsumer<>(this.consumerProperties);
		if (this.partitionOffsets == null) {
			this.partitionOffsets = new HashMap<>();
			for (TopicPartition topicPartition : this.topicPartitions) {
				this.partitionOffsets.put(topicPartition, 0L);
			}
		}
		if (this.saveState && executionContext.containsKey(TOPIC_PARTITION_OFFSETS)) {
			Map<String, Long> offsets = (Map<String, Long>) executionContext.get(TOPIC_PARTITION_OFFSETS);
			for (Map.Entry<String, Long> entry : offsets.entrySet()) {
				String topicName = this.topicPartitions.get(0).topic();
				this.partitionOffsets.put(new TopicPartition(topicName, Integer.parseInt(entry.getKey())), entry.getValue() == 0 ? 0 : entry.getValue() + 1);
			}
		}
		this.kafkaConsumer.assign(this.topicPartitions);
		this.partitionOffsets.forEach(this.kafkaConsumer::seek);
	}
```



### コメント 4 by noojung

**作成日**: 2025-06-04

Could I work on this issue?

### コメント 5 by fmbenhassine

**作成日**: 2025-09-17

@MinJunKweon Thank you for reporting this! I wonder if this will be the same case with Jackson 3 coming in v6, see #4842.

@noojung Thank you for the PR! I was planning to back port this to v5.2.3 but I am not sure the fix will be the same for Jackson 2 and Jackson 3 (as I did not start working on #4842 yet).

If the fix is the same for both Jackson versions, I will back port it as is to v5.2.x. Otherwise, I will still fix the issues in both branches even differently.

EDIT: I would be grateful if someone can provide an integration test that illustrates this issue, we have MySQL and Kafka-based integration tests for inspiration in `MySQLJobRepositoryIntegrationTests` and `KafkaItemReaderIntegrationTests`.

### コメント 6 by noojung

**作成日**: 2025-09-19

@fmbenhassine Here is a sample test case on my branch: https://github.com/noojung/spring-batch/commit/aa1c358cc508e7c558a09431cb5213428feee570

Let me know if you have any feedback on this.

### コメント 7 by fmbenhassine

**作成日**: 2025-11-03

Resolved with #4863

