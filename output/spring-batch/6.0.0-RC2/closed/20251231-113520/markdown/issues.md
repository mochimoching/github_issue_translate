# Spring Batch GitHub Issues

取得日時: 2025年12月31日 11:35:20

取得件数: 16件

---

## Issue #808: Errors are not propagated from job execution

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2019-03-21

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/808

**関連リンク**:
- Commits:
  - [b251512](https://github.com/spring-projects/spring-batch/commit/b251512ee40f9104e1f64daf9d390f956dd3838e)
  - [7f375c6](https://github.com/spring-projects/spring-batch/commit/7f375c662769f0a680cd03badd2fc2ac30d5163b)

### 内容

**[Paolo](https://jira.spring.io/secure/ViewProfile.jspa?name=pdv_)** opened **[BATCH-2800](https://jira.spring.io/browse/BATCH-2800?redirect=false)** and commented

The piece of code below in the AbstractJob class is catching Throwable, thus preventing the JVM to crash on any Error like it should.
Is there a good reason for this ? If so, shouldn't this be documented somewhere ?
It can be really surprising and upsetting when you find this out in a production environment.
See details in the linked StackOverflow thread.

```java
@Override
public final void execute(JobExecution execution) {
    [...]
    try {
            [...]
    } catch (Throwable t) {
            logger.error("Encountered fatal error executing job", t);
            execution.setExitStatus(getDefaultExitStatusForFailure(t, execution));
            execution.setStatus(BatchStatus.FAILED);
            execution.addFailureException(t);
    }
```



---

**Affects:** 4.1.1

**Reference URL:** https://stackoverflow.com/questions/54811702/spring-batch-doesnt-propagate-errors


### コメント

#### コメント 1 by Agniswar123

**作成日**: 2025-10-28

Quick qes. If a heapdump is needed can't visualVM be used? A project can have multiple job, so maybe some alert by execution listener will help, but stopping entire application, is it ideal?

---

## Issue #3797: Cannot deserialize TopicPartition from JobRepository

**状態**: closed | **作成者**: MinJunKweon | **作成日**: 2020-11-02

**ラベル**: in: infrastructure, type: bug, has: votes, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/3797

**関連リンク**:
- Commits:
  - [bab03c1](https://github.com/spring-projects/spring-batch/commit/bab03c1d7317c2ac27c6938c0b4cbf577542963a)
  - [a5e43a0](https://github.com/spring-projects/spring-batch/commit/a5e43a02b0708a707d41f4c1b3e5436e67845ddd)

### 内容

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

### コメント

#### コメント 1 by langzime

**作成日**: 2021-08-13

same question

#### コメント 2 by noojung

**作成日**: 2024-12-23

same question too

#### コメント 3 by noojung

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



#### コメント 4 by noojung

**作成日**: 2025-06-04

Could I work on this issue?

#### コメント 5 by fmbenhassine

**作成日**: 2025-09-17

@MinJunKweon Thank you for reporting this! I wonder if this will be the same case with Jackson 3 coming in v6, see #4842.

@noojung Thank you for the PR! I was planning to back port this to v5.2.3 but I am not sure the fix will be the same for Jackson 2 and Jackson 3 (as I did not start working on #4842 yet).

If the fix is the same for both Jackson versions, I will back port it as is to v5.2.x. Otherwise, I will still fix the issues in both branches even differently.

EDIT: I would be grateful if someone can provide an integration test that illustrates this issue, we have MySQL and Kafka-based integration tests for inspiration in `MySQLJobRepositoryIntegrationTests` and `KafkaItemReaderIntegrationTests`.

#### コメント 6 by noojung

**作成日**: 2025-09-19

@fmbenhassine Here is a sample test case on my branch: https://github.com/noojung/spring-batch/commit/aa1c358cc508e7c558a09431cb5213428feee570

Let me know if you have any feedback on this.

#### コメント 7 by fmbenhassine

**作成日**: 2025-11-03

Resolved with #4863

---

## Issue #4362: Incorrect Step status in StepExecutionListener#afterStep

**状態**: closed | **作成者**: cezarykluczynski | **作成日**: 2023-05-01

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4362

**関連リンク**:
- Commits:
  - [db6ef7b](https://github.com/spring-projects/spring-batch/commit/db6ef7b067e0daeee59c1baea03a0acfed4f5cfc)
  - [36068b5](https://github.com/spring-projects/spring-batch/commit/36068b5db84ff242032e9b00515454a84e0745d2)

### 内容

I'm looking for a way to execute a callback when step is completed. `StepExecutionListener` does not work, because in `afterStep`, step is not acutally completed yet, because it's exit status can still be changed, and status in the DB table is not COMPLETED, but STARTED. 

I'm looking for a way to do it, because after every step, I want to fire an automatic backup of a completed step. For that, it is required that all steps are completed, because if state is later recreated from this backup, Spring Batch would not process further.

I haven't found any way to do it in a clean manner. There is no listener that will execute after one step is completed, but next step is not yet started. If there is one, please point me out, and otherwise, would you consider adding a listener like that? I could probably try and make the PR if this feature is accepted.


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2023-06-15

Thank you for opening this issue.

> `StepExecutionListener` does not work, because in `afterStep`, step is not acutally completed yet, because it's exit status can still be changed, and status in the DB table is not COMPLETED, but STARTED.

The issue is with the current implementation of that callback listener in Spring Batch, which is incorrect. According to the contract of that method which states that that method is `Called after execution of the step's processing logic (whether successful or failed)`, the status (both in memory and in the DB) should not be `STARTED` at that point, but rather a non-running status. The end time should be set at that point as well (as reported in #3846). So I believe this is a bug and not a feature that should be requested.

Once this is fixed, I think you can implement your requirement with a `StepExecutionListener`. Do you agree?

#### コメント 2 by cezarykluczynski

**作成日**: 2023-06-22

@fmbenhassine Yes, if status was non-running in both memory and DB, that would solve my problem. However, the `afterStep` method returns `an {@link ExitStatus} to combine with the normal value`, which gives the chance to overwrite the original exit status. Therefore, if non-null status is returned, one more save in the `AbstractStep` around line 268 is needed (hopefully it's that simple). I'm also not sure if that would not break some assumptions other people are making about how Spring Batch works here, even if they rely on a bug.

#### コメント 3 by gdupontf

**作成日**: 2023-08-16

Forgive me if I'm wrong, but isn't the same problem present at the job level?
I had the same behaviour using `JobExecutionListener`s.

#### コメント 4 by fmbenhassine

**作成日**: 2025-11-03

> Yes, if status was non-running in both memory and DB, that would solve my problem

@cezarykluczynski the step execution status is now persisted before calling listeners, so it should be seen as a non-running status in both memory and job repository (even though I believe one should not query the job repository at that point, but only use the reference to the step execution that the listener provides).

That said, in hindsight, I don't understand why `afterStep` returns an `ExitStatus`.. The javadoc mentions to "give a listener a chance to modify the exit status from a step"  but I don't see any use case for that (I might be missing something). I personally never used that "feature". Moreover, this is not consistent with `JobExecutionListener#afterJob` which returns `void` and not an `ExitStatus`. Why is one able to change the step's execution status in `StepExecutionListener#afterStep`, but is not able to change the job's execution status in `JobExecutionListener#afterJob` ?

Unless there is a good reason / use case for that, I believe that that method should be deprecated and replaced with one that returns `void`. I opened #5074 to discuss this and gather feedback, so please share your thoughts there. Many thanks upfront.

@gdupontf 

> Forgive me if I'm wrong, but isn't the same problem present at the job level? I had the same behaviour using JobExecutionListeners.

You are right, I fixed that for job listeners as well, 36068b5db84ff242032e9b00515454a84e0745d2.


---

## Issue #4755: Incorrect restart behaviour with no identifying job parameters

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-01-31

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/4755

**関連リンク**:
- Commits:
  - [f888ebb](https://github.com/spring-projects/spring-batch/commit/f888ebb43f70d925c028721db0b3d71306089038)
  - [1c28dac](https://github.com/spring-projects/spring-batch/commit/1c28daccf0958e2cdcfd1a784e3f7110e73881e4)
  - [5225249](https://github.com/spring-projects/spring-batch/commit/5225249585fec7e479bf4b3194974d96a848c3c0)
  - [250bfff](https://github.com/spring-projects/spring-batch/commit/250bfff1b6e8f2cf4e9219564c3f1d2719f0d17d)
  - [0564ce6](https://github.com/spring-projects/spring-batch/commit/0564ce6293e5178b12aa95b7bce5a461a38e4eb0)

### 内容


### Discussed in https://github.com/spring-projects/spring-batch/discussions/4694

<div type='discussions-op-text'>

<sup>Originally posted by **ELMORABITYounes** October 28, 2024</sup>
Right now even if a job was completed successfuly, spring batch allow It to be restarted if It contains non identifying params as shown here:

```				
if (!identifyingJobParameters.isEmpty()                                                        
		&& (status == BatchStatus.COMPLETED || status == BatchStatus.ABANDONED)) {            
	throw new JobInstanceAlreadyCompleteException(                                             
			"A job instance already exists and is complete for identifying parameters="       
					+ identifyingJobParameters + ".  If you want to run this job again, "    
					+ "change the parameters.");                                             
}                                                                                              
```

I am wondering why is that done like this? I mean if the job already completed why It does not throw JobInstanceAlreadyCompleteException? Shouldn't the second job instance without parameters  considered the same and hence not allow It to be restarted if already succeeded?
</div>

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-01-31

Thank you for reporting this issue! I was able to isolate the case in this example:

```java
package org.springframework.batch.samples.helloworld;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;
import org.springframework.jdbc.support.JdbcTransactionManager;

import javax.sql.DataSource;

@Configuration
@EnableBatchProcessing
public class HelloWorldJobConfiguration {

	public static void main(String[] args) throws Exception {
		ApplicationContext context = new AnnotationConfigApplicationContext(HelloWorldJobConfiguration.class);
		JobLauncher jobLauncher = (JobLauncher) context.getBean("jobLauncher");
		Job job = (Job) context.getBean("job");
		JobParameters jobParameters1 = new JobParametersBuilder().addString("name", "foo", false).toJobParameters();
		JobParameters jobParameters2 = new JobParametersBuilder().addString("name", "bar", false).toJobParameters();
		jobLauncher.run(job, jobParameters1);
		jobLauncher.run(job, jobParameters2); // expected: JobInstanceAlreadyCompleteException
	}

	@Bean
	public Job job(JobRepository jobRepository, Step step) {
		return new JobBuilder("job", jobRepository).start(step).build();
	}

	@Bean
	public Step step(JobRepository jobRepository, JdbcTransactionManager transactionManager) {
		return new StepBuilder("step", jobRepository).tasklet((contribution, chunkContext) -> {
			System.out.println("Hello world!");
			return RepeatStatus.FINISHED;
		}, transactionManager).build();
	}

	// infra beans

	@Bean
	public DataSource dataSource() {
		return new EmbeddedDatabaseBuilder()
				.addScript("/org/springframework/batch/core/schema-hsqldb.sql")
				.build();
	}

	@Bean
	public JdbcTransactionManager transactionManager(DataSource dataSource) {
		return new JdbcTransactionManager(dataSource);
	}

}
```

while the default job key generator works as expected (it gives the same hash for the same input, ie an empty identifying job parameters set), spring batch still considers this as a different job instance and runs it, which should not be the case.

---

Just FTR,  the default job key generator is working as expected (the following tests pass with 5.2.1):

```java
// to add in org.springframework.batch.core.DefaultJobKeyGeneratorTests

	@Test
	public void testCreateJobKeyForEmptyParameters() {
		JobParameters jobParameters1 = new JobParameters();
		JobParameters jobParameters2 = new JobParameters();
		String key1 = jobKeyGenerator.generateKey(jobParameters1);
		String key2 = jobKeyGenerator.generateKey(jobParameters2);
		assertEquals(key1, key2);
	}

	@Test
	public void testCreateJobKeyForEmptyParametersAndNonIdentifying() {
		JobParameters jobParameters1 = new JobParameters();
		JobParameters jobParameters2 = new JobParametersBuilder()
				.addString("name", "foo", false)
				.toJobParameters();
		String key1 = jobKeyGenerator.generateKey(jobParameters1);
		String key2 = jobKeyGenerator.generateKey(jobParameters2);
		assertEquals(key1, key2);
	}
```

#### コメント 2 by baezzys

**作成日**: 2025-04-29

Hi @fmbenhassine Can I work on this?

#### コメント 3 by isanghaessi

**作成日**: 2025-08-15

Hi @fmbenhassine 👋
I opened PR for this issue #4946!
Please review and I will check ASAP💨

---

## Issue #4818: Use contextual lambdas to configure batch artefacts

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-28

**ラベル**: in: infrastructure, type: feature, related-to: item-readers-writers

**URL**: https://github.com/spring-projects/spring-batch/issues/4818

**関連リンク**:
- Commits:
  - [24a464f](https://github.com/spring-projects/spring-batch/commit/24a464fab859008ec54e7de34915f29d71763b3b)

### 内容

This request is about improving the builders of item readers and writers to use Lambdas for configuration options:

Current API:

```java
var reader = new FlatFileItemReaderBuilder()
 .resource(...)
 .delimited()
 .delimiter(",")
 .quoteCharacter('"')
 ...
 .build();
```

Proposal:

```java
var reader = new FlatFileItemReaderBuilder()
 .resource(...)
 .delimited ( config -> config.delimiter(',').quoteCharcter( '"' ))
 ...
 .build();
```

cc @joshlong



### コメント

#### コメント 1 by kwondh5217

**作成日**: 2025-04-29

Hi @fmbenhassine,

This looks like a great improvement!
I would love to work on this issue. Could you please assign it to me if that's fine?

#### コメント 2 by fmbenhassine

**作成日**: 2025-05-06

@kwondh5217 Sure! Thank you for your offer to help!

I believe Spring Security pioneered this configuration approach in the portfolio, so you can take a look there for inspiration.

#### コメント 3 by kwondh5217

**作成日**: 2025-05-06

Hi @fmbenhassine, thank you for your guidance earlier!

I’d like to clarify the intended direction of the enhancement.

From what I understand, the idea is not just to support lambda-based configuration in FlatFileItemReaderBuilder, but to establish a general DSL-style configuration approach across all ItemReader and ItemWriter builders.

Would you recommend introducing a shared abstraction (e.g. a ConfigurerAwareBuilder base class similar to AbstractConfiguredSecurityBuilder in Spring Security) to support this pattern?

Also, in terms of behavior:

Should we throw an exception when both chaining and lambda styles are used?

Or should we allow overriding?

Or should we allow both and apply in order?

I want to align with the broader design direction before proceeding. Thank you again for your support.

#### コメント 4 by fmbenhassine

**作成日**: 2025-05-08

I don't think we need new builders. My initial thinking was about adding new methods to existing builders that accept `Consumer<Spec>`, similar to the one in SF here: https://github.com/spring-projects/spring-framework/blob/main/spring-beans/src/main/java/org/springframework/beans/factory/BeanRegistry.java#L96

Here is also the original issue in Spring Security: https://github.com/spring-projects/spring-security/issues/5557

So we can imagine new configuration specifications like `DelimitedSpec`, `FixedLengthSpec`, etc and use them in current builders.

#### コメント 5 by kwondh5217

**作成日**: 2025-05-08

Thanks for the detailed guidance @fmbenhassine !
The direction is clear now. I’ll proceed with adding Consumer<Spec>-based configuration methods to the existing builders using DelimitedSpec and FixedLengthSpec style objects as discussed.

I’ll share a draft PR soon for feedback. Appreciate your support!

#### コメント 6 by kwondh5217

**作成日**: 2025-05-12

Hi @fmbenhassine,
I’ve submitted a pull request that addresses this issue.
Could you take a look? 🙇‍♂️
Thank you !

#### コメント 7 by kwondh5217

**作成日**: 2025-10-31

Hi @fmbenhassine,
I’ve submitted a new pull request.
Could you take a look? 🙇‍♂️
Thank you !

---

## Issue #5047: JsonObjectReader fails to read JSON array format due to Jackson 3.0 FAIL_ON_TRAILING_TOKENS default change

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-24

**ラベル**: in: infrastructure, type: bug, related-to: item-readers-writers

**URL**: https://github.com/spring-projects/spring-batch/issues/5047

**関連リンク**:
- Commits:
  - [c534e6c](https://github.com/spring-projects/spring-batch/commit/c534e6c367ad705163a825d3d9ebee73f4f87e4c)

### 内容

Hi Spring Batch team!
First of all, thank you for your amazing work on Spring Batch 6.0

I've encountered an issue when reading JSON array files with JsonItemReader in Spring Batch 6.0 with Spring Boot 4(use jackson 3.0), and I wanted to report it in case it affects other users migrating to this version.




**Bug description**
`JacksonJsonObjectReader`(used by JsonItemReader) cannot read JSON array format `[{...}, {...}]` when using the default constructor in Spring Batch 6.0 with Jackson 3.0. 

This appears to be caused by Jackson 3.0's change where `DeserializationFeature.FAIL_ON_TRAILING_TOKENS` default was changed from `false` to `true` ([Jackson JSTEP-2](https://github.com/FasterXML/jackson-future-ideas/wiki/JSTEP-2#deserializationfeature)).

When reading a JSON array, after parsing the first object, the second object's start token `{` is detected as a "trailing token", causing a `MismatchedInputException`.

**Environment**
- Spring Boot: 4.0.0-SNAPSHOT / spring-boot-starter-json 4.0.0-SNAPSHOT
- Spring Batch: 6.0.0-RC1
- Jackson: 3.0.1
- Java: 21

**Steps to reproduce**
1. Create a JSON array file:
```bash
echo '[
{"command": "destroy", "cpu": 99, "status": "memory overflow"},
{"command": "explode", "cpu": 100, "status": "cpu meltdown"},
{"command": "collapse", "cpu": 95, "status": "disk burnout"}
]' > system_death.json
```

2. Configure `JsonItemReader` with default `JacksonJsonObjectReader`:
```java
@Bean
@StepScope
public JsonItemReader systemFailureItemReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new JsonItemReaderBuilder()
            .name("systemFailureItemReader")
            .jsonObjectReader(new JacksonJsonObjectReader<>(SystemFailure.class))
            .resource(new FileSystemResource(inputFile))
            .build();
}

public record SystemFailure(String command, int cpu, String status) {}
```

3. Run the job with the JSON array file



**Expected behavior**

`JsonItemReader` should successfully read all objects from the JSON array `[{...}, {...}, {...}]` without requiring manual Jackson configuration, as JSON arrays are a common input format for batch processing.

**Actual behavior**

Job fails with:
```
tools.jackson.databind.exc.MismatchedInputException: Trailing token (JsonToken.START_OBJECT) found after value (bound as SystemFailure): not allowed as per DeserializationFeature.FAIL_ON_TRAILING_TOKENS
```

**Minimal Complete Reproducible example**

Here's the complete configuration that reproduces the issue:
```java
@Bean
public Job systemFailureJob(Step systemFailureStep) {
    return new JobBuilder("systemFailureJob", jobRepository)
            .start(systemFailureStep)
            .build();
}

@Bean
public Step systemFailureStep(JsonItemReader systemFailureItemReader) {
    return new StepBuilder("systemFailureStep", jobRepository)
            .chunk(10)
            .reader(systemFailureItemReader)
            .writer(items -> items.forEach(item -> log.info("{}", item)))
            .build();
}

@Bean
@StepScope
public JsonItemReader systemFailureItemReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new JsonItemReaderBuilder()
            .name("systemFailureItemReader")
            .jsonObjectReader(new JacksonJsonObjectReader<>(SystemFailure.class))
            .resource(new FileSystemResource(inputFile))
            .build();
}

public record SystemFailure(String command, int cpu, String status) {}
```

**Current Workaround**

manually creating a `JsonMapper` with `FAIL_ON_TRAILING_TOKENS` disabled resolves the issue:
```java
@Bean
@StepScope
public JsonItemReader systemFailureItemReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    
    JsonMapper jsonMapper = JsonMapper.builder()
            .disable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS)
            .build();
    
    JacksonJsonObjectReader jsonReader =
            new JacksonJsonObjectReader<>(jsonMapper, SystemFailure.class);
    
    return new JsonItemReaderBuilder()
            .name("systemFailureItemReader")
            .jsonObjectReader(jsonReader)
            .resource(new FileSystemResource(inputFile))
            .build();
}
```

**Suggested Solutions**

I'd like to humbly suggest two possible approaches:

1. **Update `JacksonJsonObjectReader` default constructor** to create a `JsonMapper` with `FAIL_ON_TRAILING_TOKENS` disabled by default, since JSON array reading is a fundamental use case for `JsonItemReader`

2. **Update the documentation** to clearly guide users that manual `JsonMapper` configuration with `FAIL_ON_TRAILING_TOKENS` disabled is required when reading JSON arrays in Spring Batch 6.0+


Thank you again for maintaining Spring Batch! Please let me know if you need any additional information or clarification.


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-10-28

Thank you for raising this issue! Indeed, it was expected that the user disables `FAIL_ON_TRAILING_TOKENS` before passing the Jackson mapper to `JacksonJsonItemReader` (see [here](https://github.com/spring-projects/spring-batch/blob/main/spring-batch-infrastructure/src/test/java/org/springframework/batch/infrastructure/item/json/JacksonJsonItemReaderFunctionalTests.java#L34)), but you are right, it's better to make that the default since the `JsonItemReader` is expected to correctly read json files having the `[{...}, {...}, {...}]` format.

I will plan that change for the upcoming 6.0.0-RC2.

---

## Issue #5048: ChunkOrientedStep: Unnecessary ItemReader.read() calls when chunk size exceeds item count

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5048

**関連リンク**:
- Commits:
  - [706add7](https://github.com/spring-projects/spring-batch/commit/706add77b8259f51ae8cf7f9d6dfec6dcdb424b2)

### 内容

Hi Spring Batch team! 
First of all, thank you for the amazing work on Spring Batch 6 and New ChunkOrientedStep. I really appreciate this improvements.

I discovered what appears to be a bug in the chunk reading logic. 


## Bug description
When the chunk size is larger than the number of available items, `ItemReader.read()` and `ItemReadListener.beforeRead()` continue to be called for the remaining chunk size even after `read()` returns `null`. This results in unnecessary method invocations and potential side effects.

**Example:**
- Chunk size: 10
- Available items: 5
- Expected `read()` calls: 6 (5 items + 1 null)
- **Actual `read()` calls: 10** (5 items + 5 nulls)

## Environment
- **Spring Batch version:** 6.0.0-RC1

## Steps to reproduce
1. Configure a chunk-oriented step with chunk size larger than available items
2. Use any ItemReader that returns null when exhausted
3. Add an ItemReadListener to track method calls
4. Run the job and observe the logs

## Expected behavior
Once `ItemReader.read()` returns `null`, the chunk reading loop should terminate immediately:
- `beforeRead()` should be called: **6 times** (5 items + 1 null check)
- `read()` should be called: **6 times** (5 items + 1 null)
- Loop should break after first `null` return

## Actual behavior
The loop continues for the entire chunk size:
- `beforeRead()` is called: **10 times** (5 items + 5 unnecessary null checks)
- `read()` is called: **10 times** (5 items + 5 unnecessary null returns)
- Unnecessary method invocations waste resources and may trigger unintended side effects


## Root cause
In `ChunkOrientedStep.readChunk()` method (line 478-487), the for loop continues for the entire chunk size without breaking when `item` is `null`:
```java
private Chunk readChunk(StepContribution contribution) throws Exception {
    Chunk chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        }
        // Missing break when item is null!
    }
    return chunk;
}
```

## Impact
1. **Performance degradation**: Especially severe when chunk size is large
   - Chunk size 1000, Items 10 → 990 unnecessary calls
2. **ItemReadListener miscounts**: `beforeRead()` called more times than actual reads
3. **Potential side effects**: If `read()` implementation has side effects (logging, metrics, connection checks, API calls), they execute unnecessarily
4. **Resource waste**: Unnecessary method invocations and stack operations



## Minimal Complete Reproducible example
@Slf4j
@Configuration
public class ChunkSizeIssueReproductionJobConfiguration {
    
    @Bean
    public Job reproductionJob(JobRepository jobRepository, Step reproductionStep) {
        return new JobBuilder(jobRepository)
                .start(reproductionStep)
                .build();
    }

    @Bean
    public Step reproductionStep(
            JobRepository jobRepository,
            CountingListItemReader countingListItemReader) {
        return new StepBuilder(jobRepository)
                .chunk(10)  // Chunk size: 10
                .reader(countingListItemReader)
                .writer(chunk -> {
                    log.info("=== Writer: Processing {} items ===", chunk.size());
                    chunk.forEach(item -> log.info("Writing item: {}", item));
                })
                .listener(new ReadCountListener())
                .build();
    }

    @Bean
    public CountingListItemReader countingListItemReader() {
        // Only 5 items (less than chunk size of 10)
        return new CountingListItemReader(List.of(
                "Item-1",
                "Item-2",
                "Item-3",
                "Item-4",
                "Item-5"
        ));
    }

    @Slf4j
    static class CountingListItemReader extends ListItemReader {
        private int readCallCount = 0;

        public CountingListItemReader(List list) {
            super(list);
        }

        @Override
        public String read() {
            readCallCount++;
            String item = super.read();

            if (item == null) {
                log.warn(">>> read() #{}: Returned NULL <<>> read() #{}: {}", readCallCount, item);
            }

            return item;
        }
    }

    @Slf4j
    static class ReadCountListener implements ItemReadListener {
        private int beforeReadCount = 0;
        private int afterReadCount = 0;

        @Override
        public void beforeRead() {
            beforeReadCount++;
            log.info(">>> beforeRead() #{} called", beforeReadCount);
        }

        @Override
        public void afterRead(String item) {
            afterReadCount++;
            log.info(">>> afterRead() #{} called for: {}", afterReadCount, item);
        }
    }
}

**Console output:**
```
>>> beforeRead() #1 called
>>> read() #1: Item-1
>>> afterRead() #1 called for: Item-1
>>> beforeRead() #2 called
>>> read() #2: Item-2
>>> afterRead() #2 called for: Item-2
>>> beforeRead() #3 called
>>> read() #3: Item-3
>>> afterRead() #3 called for: Item-3
>>> beforeRead() #4 called
>>> read() #4: Item-4
>>> afterRead() #4 called for: Item-4
>>> beforeRead() #5 called
>>> read() #5: Item-5
>>> afterRead() #5 called for: Item-5
>>> beforeRead() #6 called
>>> read() #6: Returned NULL <
>>> beforeRead() #7 called        ← Unnecessary
>>> read() #7: Returned NULL <<<  ← Unnecessary
>>> beforeRead() #8 called        ← Unnecessary
>>> read() #8: Returned NULL <<<  ← Unnecessary
>>> beforeRead() #9 called        ← Unnecessary
>>> read() #9: Returned NULL <<<  ← Unnecessary
>>> beforeRead() #10 called       ← Unnecessary
>>> read() #10: Returned NULL <<< ← Unnecessary
=== Writer: Processing 5 items ===
Writing item: Item-1
Writing item: Item-2
Writing item: Item-3
Writing item: Item-4
Writing item: Item-5
```

## Proposed fix
Add a `break` statement when `item` is `null`:
```java
private Chunk readChunk(StepContribution contribution) throws Exception {
    Chunk chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else {
            break;  // Stop reading when null is returned
        }
    }
    return chunk;
}
```

Let me know if you need any additional information or if I should submit a PR for this fix. Thanks again for your great work on Spring Batch!


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-10-28

Thank you for your early feedback on 6.0 RC1!

This is indeed a bug, I planned the fix for the upcoming RC2.

---

## Issue #5049: JobParameter constructor validates wrong parameter (value instead of name)

**状態**: closed | **作成者**: KMGeon | **作成日**: 2025-10-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5049

**関連リンク**:
- Commits:
  - [b5c10c2](https://github.com/spring-projects/spring-batch/commit/b5c10c2301a5f58805c3a670261b07321fd0ac7d)

### 内容

## Issue Description

### Summary
The `JobParameter` record's compact constructor has a bug in parameter validation. It validates the `value` parameter twice instead of validating both `name` and `value` parameters.

---

## Current Behavior

```java
public record JobParameter<T>(String name, T value, Class<T> type, boolean identifying) implements Serializable {
    public JobParameter {
        Assert.notNull(value, "name must not be null");  // ❌ Bug: validates 'value' but message says 'name'
        Assert.notNull(value, "value must not be null"); // ❌ Bug: validates 'value' twice
        Assert.notNull(type, "type must not be null");
    }
}
```

---

## Expected Behavior

```java
public record JobParameter<T>(String name, T value, Class<T> type, boolean identifying) implements Serializable {
    public JobParameter {
        Assert.notNull(name, "name must not be null");   // ✅ Correct: validates 'name'
        Assert.notNull(value, "value must not be null"); // ✅ Correct: validates 'value'
        Assert.notNull(type, "type must not be null");
    }
}
```

---


## Steps to Reproduce

### 1. Create Test Case

```java
@Test
void testNameParameterIsNull() {
    JobParameter<String> jobParameter = new JobParameter<>(null, "test", String.class, true);
    assertEquals("param", jobParameter.name());
    assertEquals("test", jobParameter.value());
    assertEquals(String.class, jobParameter.type());
    assertTrue(jobParameter.identifying());
}
```

### 2. Test Result

The test demonstrates that a `JobParameter` can be created with a `null` name, which should not be allowed:

```
[ERROR] Failures: 
[ERROR]   JobParameterTests.testNameParameterIsNull:37 expected: <param> but was: <null>
[INFO] 
[ERROR] Tests run: 7, Failures: 1, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.049 s
[INFO] Finished at: 2025-10-25T01:43:01+09:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.5.3:test (default-test) on project spring-batch-core: There are test failures.
```

### 3. Analysis

The test fails because:
1. **No exception is thrown** when `name` is `null` during object construction (due to the validation bug)
2. The object is created successfully with `name = null`
3. The assertion `assertEquals("param", jobParameter.name())` fails because the actual value is `null`

This proves that the validation is not working correctly.

---

## Environment

- **Spring Batch Version:** 6.0.0-SNAPSHOT
- **Java Version:** 21
- **File:** `org.springframework.batch.core.job.parameters.JobParameter`

---

## Proposed Fix

### Change Required

**Line 41** - Change from:
```java
Assert.notNull(value, "name must not be null");
```

**To:**
```java
Assert.notNull(name, "name must not be null");
```

### Complete Fixed Constructor

```java
public JobParameter {
    Assert.notNull(name, "name must not be null");   // ✅ Fixed: validates 'name' correctly
    Assert.notNull(value, "value must not be null");
    Assert.notNull(type, "type must not be null");
}
```

---

## Issue #5051: Incorrect error message in JobOperatorTestUtils constructor

**状態**: closed | **作成者**: KMGeon | **作成日**: 2025-10-26

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5051

**関連リンク**:
- Commits:
  - [8a598dc](https://github.com/spring-projects/spring-batch/commit/8a598dc8300873fee55421b9dac5bc7cc0c9a8d3)
  - [b848638](https://github.com/spring-projects/spring-batch/commit/b848638e5798a19d847798891b586908426487b0)

### 内容

## Issue Description

- The constructor of `JobOperatorTestUtils` has an incorrect error message for the `jobOperator` parameter validation.


## Current Behavior

```java
public JobOperatorTestUtils(JobOperator jobOperator, JobRepository jobRepository) {
	Assert.notNull(jobOperator, "JobRepository must not be null");
	Assert.notNull(jobRepository, "JobRepository must not be null");
	this.jobOperator = jobOperator;
	this.jobRepository = jobRepository;
}
```

## Expected Behavior

```java
public JobOperatorTestUtils(JobOperator jobOperator, JobRepository jobRepository) {
	Assert.notNull(jobOperator, "JobOperator must not be null");
	Assert.notNull(jobRepository, "JobRepository must not be null");
	this.jobOperator = jobOperator;
	this.jobRepository = jobRepository;
}
```

## File

`spring-batch-test/src/main/java/org/springframework/batch/test/JobOperatorTestUtils.java`

---

## Issue #5055: Change configuration log level to debug

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-28

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5055

**関連リンク**:
- Commits:
  - [c1ec7cc](https://github.com/spring-projects/spring-batch/commit/c1ec7cc9d8de3633718d99526d2dcade056c3aad)
  - [136bc8a](https://github.com/spring-projects/spring-batch/commit/136bc8a81a4329054c776ae6614f8d1b9bd40b65)

### 内容

Currently, the log level for batch infrastructure configuration is set to `INFO`, which makes the output quite verbose for no real added value. Configuration details should be logged at `DEBUG` level.

---

## Issue #5060: Add support for delete operations in MongoDB DAOs

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-29

**ラベル**: type: feature, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5060

**関連リンク**:
- Commits:
  - [3079925](https://github.com/spring-projects/spring-batch/commit/3079925af8bb2c58563afb57a2c4e455327ac4bc)

### 内容

As of v5.2.4, 6.0.0-RC1, the following methods are not implemented in MongoDB DAOs:

- `org.springframework.batch.core.repository.dao.JobInstanceDao#deleteJobInstance`
- `org.springframework.batch.core.repository.dao.JobExecutionDao#deleteJobExecution`
- `org.springframework.batch.core.repository.dao.JobExecutionDao#deleteJobExecutionParameters`
- `org.springframework.batch.core.repository.dao.StepExecutionDao#deleteStepExecution`
- `org.springframework.batch.core.repository.dao.ExecutionContextDao#deleteExecutionContext(JobExecution)`
- `org.springframework.batch.core.repository.dao.ExecutionContextDao#deleteExecutionContext(StepExecution)`


---

## Issue #5061: Optimize step executions counting in MongoStepExecutionDao

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-29

**ラベル**: in: core, type: enhancement, related-to: performance, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5061

### 内容

As of v5.2.4 / v6.0.0-RC1, the method `MongoStepExecutionDao#countStepExecutions` is not optimized, it uses nested loops to count step executions.

This method should be optimized to perform a count query using a `MongoOperations#count` operation.


### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-05

Resolved in ddbb6174c522999fc697a1603ac4e2c69a676a49, many thanks to @quaff !

---

## Issue #5062: Incorrect ordering when retrieving job executions with JobExecutionDao

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-29

**ラベル**: type: bug, in: core, related-to: job-repository, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5062

**関連リンク**:
- Commits:
  - [0125b19](https://github.com/spring-projects/spring-batch/commit/0125b19af19c64c67c5961ca36fa321713ad3c94)

### 内容

`JobExecutionDao#findJobExecutions` states that the returned job executions should be sorted backwards by creation order (the first element is the most recent).

As of v5.2.4 / v6.0.0-RC1, this is not the case both in the JDBC and MongoDB implementations.

---

## Issue #5063: MongoJobExecutionDao doesn't handle temporal job parameter types correctly

**状態**: closed | **作成者**: quaff | **作成日**: 2025-10-30

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5063

### 内容

`JobExecution` retrieved from MongoDB contains incorrect temporal job parameter:

```java
LocalDate localDateParameter = LocalDate.now();
JobParameters jobParameters = new JobParametersBuilder().addLocalDate("localDate", localDateParameter).toJobParameters();
JobExecution execution = dao.createJobExecution(jobInstance, jobParameters);
JobParameters persistedParameters = dao.getJobExecution(execution.getId()).getJobParameters();
System.out.println(persistedParameters.getLocalDate("localDate").getClass()); // -> java.util.Date instead of expected java.time.LocalDate
```

### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-05

Resolved in f1cf52963e949f7bc59964859bcc115824cc62ae, many thanks @quaff for reporting the issue and contributing a fix!

---

## Issue #5068: ChunkOrientedStepBuilder throws IllegalArgumentException when retry() is used(configured) without retryLimit()

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-31

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5068

**関連リンク**:
- Commits:
  - [6fdc225](https://github.com/spring-projects/spring-batch/commit/6fdc22521564234630f4e6ae021b466a22cc29be)

### 内容

Hello Spring Batch team,

Thank you for your continued work on Spring Batch. I believe I've found a bug or documentational enhencement in the `ChunkOrientedStepBuilder` related to retry configuration.


**Bug description**
When using ChunkOrientedStepBuilder.retry() to specify retryable exceptions without calling retryLimit(), the step builder fails with an IllegalArgumentException during the build phase. This occurs because retryLimit defaults to -1, which is rejected by RetryPolicy.Builder.maxAttempts().


**Environment**
Spring Batch version: 6.0.0-RC1
Spring Framework version: 7.0.0-RC2

**Steps to reproduce**
Create a chunk-oriented step using StepBuilder
Call .retry(SomeException.class) without calling .retryLimit()
Attempt to build the step

**Expected behavior**
The step should build successfully without throwing an exception.

**Actual behavior**
Exception thrown:
```
Caused by: java.lang.IllegalArgumentException: Invalid maxAttempts (-1): must be positive or zero for no retry.
	at org.springframework.util.Assert.isTrue(Assert.java:136)
	at org.springframework.core.retry.RetryPolicy.assertMaxAttemptsIsNotNegative(RetryPolicy.java:105)
	at org.springframework.core.retry.RetryPolicy$Builder.maxAttempts(RetryPolicy.java:200)
	at org.springframework.batch.core.step.builder.ChunkOrientedStepBuilder.build(ChunkOrientedStepBuilder.java:404)
```


**Minimal Complete Reproducible example**
```java
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        AtomicInteger counter = new AtomicInteger(0);

        return new StepBuilder(jobRepository)
                .<String, String>chunk(5)
                .reader(() -> {
                    int count = counter.incrementAndGet();
                    if (count <= 5) {
                        return "kill-" + count;
                    }
                    return null;
                })
                .writer(items -> items.forEach(item ->
                        System.out.println("💀 Terminated: " + item)
                ))
                .faultTolerant()
                .retry(IOException.class)
                //.retryLimit(1)  // ← This must be added for proper operation
                .build();  // ← IllegalArgumentException thrown here
    }
}
```

## Root cause analysis

In `ChunkOrientedStepBuilder`:
```java
private long retryLimit = -1;  // Default value

public ChunkOrientedStep build() {
    // ...
    if (this.retryPolicy == null) {
        // This condition uses OR, so it's true when only retryableExceptions is set
        if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
            this.retryPolicy = RetryPolicy.builder()
                .maxAttempts(this.retryLimit)  // ← Passes -1 here
                .includes(this.retryableExceptions)
                .build();  // ← Fails here
        }
        else {
            this.retryPolicy = throwable -> false;
        }
    }
    // ...
}
```

In `RetryPolicy.Builder`:
```java
public Builder maxAttempts(long maxAttempts) {
    assertMaxAttemptsIsNotNegative(maxAttempts);  // ← Rejects -1
    this.maxAttempts = maxAttempts;
    return this;
}
private static void assertMaxAttemptsIsNotNegative(long maxAttempts) {
    Assert.isTrue(maxAttempts >= 0,
        () -> "Invalid maxAttempts (%d): must be positive or zero for no retry."
              .formatted(maxAttempts));
}
```


## Suggested fixes
### Option 1: Change default value
private long retryLimit = 0;  // Change from -1 to 0

### Option 2: Add documentation
Add JavaDoc to `retry()`  method stating that `retryLimit()`  must be called with a positive value (greater than 0) respectively.


Thank you for reviewing this issue. Please let me know if you need any additional information or clarification.



### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-04

Thank you for reporting this valid issue! Similar to #5069, I will change the default value of retry limit as it was in v5 (which is 0).

---

## Issue #5069: ChunkOrientedStepBuilder throws IllegalArgumentException when skip() is used(configured) without skipLimit()

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-31

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5069

**関連リンク**:
- Commits:
  - [3df1f34](https://github.com/spring-projects/spring-batch/commit/3df1f34b7363954d1718737c8386afad85eb82af)

### 内容

Hello Spring Batch team

**Bug description**
When using `ChunkOrientedStepBuilder.skip()` to specify skippable exceptions without calling `skipLimit()`, the step builder fails with an `IllegalArgumentException` during the build phase. This occurs because `skipLimit` defaults to `-1`, which is rejected by `LimitCheckingExceptionHierarchySkipPolicy` constructor.

This is the same root cause as the retry configuration issue (https://github.com/spring-projects/spring-batch/issues/5068), where the default value is `-1` and the validation logic rejects it.


**Environment**
- Spring Batch version: 6.0.0-RC1
- Spring Framework version: 7.0.0-RC2

**Steps to reproduce**
1. Create a chunk-oriented step using `StepBuilder`
2. Call `.skip(SomeException.class)` without calling `.skipLimit()`
3. Attempt to build the step
4. 
**Expected behavior**
The step should build successfully without throwing an exception.


**Actual behavior**
Exception thrown:
```
Caused by: java.lang.IllegalArgumentException: The skipLimit must be greater than zero
	at org.springframework.util.Assert.isTrue(Assert.java:117)
	at org.springframework.batch.core.step.skip.LimitCheckingExceptionHierarchySkipPolicy.<init>(LimitCheckingExceptionHierarchySkipPolicy.java:45)
	at org.springframework.batch.core.step.builder.ChunkOrientedStepBuilder.build(ChunkOrientedStepBuilder.java:415)
```

**Minimal Complete Reproducible example**
```java
@Configuration
public class IssueReproductionJobConfiguration {
    
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        AtomicInteger counter = new AtomicInteger(0);

        return new StepBuilder(jobRepository)
                .chunk(5)
                .reader(() -> {
                    int count = counter.incrementAndGet();
                    if (count <= 5) {
                        return "kill-" + count;
                    }
                    return null;
                })
                .writer(items -> items.forEach(item ->
                        System.out.println("💀 Terminated: " + item)
                ))
                .faultTolerant()
                .skip(IOException.class)
                //.skipLimit(1)  // ← This must be added for proper operation
                .build();  // ← IllegalArgumentException thrown here
    }
}
```

## Root cause analysis
In `ChunkOrientedStepBuilder`:
```java
private long skipLimit = -1;  // Default value

public ChunkOrientedStep build() {
    // ...
    if (this.skipPolicy == null) {
        // This condition uses OR, so it's true when only skippableExceptions is set
        if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
            this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(
                this.skippableExceptions,
                this.skipLimit  // ← Passes -1 here
            );  // ← Fails here
        }
        else {
            this.skipPolicy = new AlwaysSkipItemSkipPolicy();
        }
    }
    // ...
}
```
In `LimitCheckingExceptionHierarchySkipPolicy`:
```java
public LimitCheckingExceptionHierarchySkipPolicy(
        Set<Class> skippableExceptions,
        long skipLimit) {
    Assert.notEmpty(skippableExceptions, "The skippableExceptions must not be empty");
    Assert.isTrue(skipLimit > 0, "The skipLimit must be greater than zero");  // ← Rejects -1
    this.skippableExceptions = skippableExceptions;
    this.skipLimit = skipLimit;
}
```


## Suggested fixes
### Option 1: Change default value
```java
private long skipLimit = 0;  // Change from -1 to 0
```

### Option 2: Add documentation
Add JavaDoc to `skip()` method stating that `skipLimit()` must be called with a positive value (greater than 0).
```java
/**
 * Configure exceptions that should be skipped.
 * Note: {@link #skipLimit(long)} must be called with a positive value 
 * before building the step when using this method.
 * @param skippableExceptions exceptions to skip
 * @return this for fluent chaining
 */
@SafeVarargs
public final ChunkOrientedStepBuilder skip(Class... skippableExceptions)
```

---
Thank you for reviewing this issue. Please let me know if you need any additional information or clarification.



### コメント

#### コメント 1 by fmbenhassine

**作成日**: 2025-11-04

Thank you for reporting this! Indeed, the step configuration fails when the skip limit is omitted. The default value in the previous implementation [was set to 10](https://github.com/spring-projects/spring-batch/blob/82bd3a2bad3d43771d0df5cdd190c1ebd2a8e5f7/spring-batch-core/src/main/java/org/springframework/batch/core/step/builder/FaultTolerantStepBuilder.java#L133), so I will change the new implementation with similar default values to facilitate the migration to v6.

---

