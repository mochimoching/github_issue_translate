# Jackson2ExecutionContextStringSerializer fails to serialize job parameters with JobStep

**Issue番号**: #5191

**状態**: closed | **作成者**: andrianov17 | **作成日**: 2025-12-30

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5191

**関連リンク**:
- Commits:
  - [0116494](https://github.com/spring-projects/spring-batch/commit/0116494b54a92bde25966071a56adf50ec198d64)
  - [2a5646a](https://github.com/spring-projects/spring-batch/commit/2a5646a2dee92e4556c71c39719e3cfed34d0a74)
  - [72c4aa2](https://github.com/spring-projects/spring-batch/commit/72c4aa2779184528aca9b97b4c8f4a6fa3473add)
  - [0bb92d5](https://github.com/spring-projects/spring-batch/commit/0bb92d54504dfcc2dcb17989f5120f29a9a23261)
  - [79f679f](https://github.com/spring-projects/spring-batch/commit/79f679f9ed91f399c67f3f56b07d8a61c742ab47)

## 内容

**Bug description**
After upgrade from Spring Batch 5.2.3 to Spring Batch 6.0.1 and preserving previous org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer serializer, JobStep fails with the exception:

```
Caused by: com.fasterxml.jackson.databind.JsonMappingException: Can not write a field name, expecting a value (through reference chain: java.util.HashMap["org.springframework.batch.core.step.job.JobStep.JOB_PARAMETERS"]->org.springframework.batch.core.job.parameters.JobParameters["parameters"]->java.util.Collections$UnmodifiableSet[0])
	at com.fasterxml.jackson.databind.JsonMappingException.wrapWithPath(JsonMappingException.java:400)
	at com.fasterxml.jackson.databind.JsonMappingException.wrapWithPath(JsonMappingException.java:371)
	at com.fasterxml.jackson.databind.ser.std.StdSerializer.wrapAndThrow(StdSerializer.java:346)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContentsUsing(CollectionSerializer.java:186)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContents(CollectionSerializer.java:120)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContents(CollectionSerializer.java:25)
	at com.fasterxml.jackson.databind.ser.std.AsArraySerializerBase.serializeWithType(AsArraySerializerBase.java:265)
	at com.fasterxml.jackson.databind.ser.BeanPropertyWriter.serializeAsField(BeanPropertyWriter.java:734)
	at com.fasterxml.jackson.databind.ser.std.BeanSerializerBase.serializeFields(BeanSerializerBase.java:760)
	at com.fasterxml.jackson.databind.ser.std.BeanSerializerBase.serializeWithType(BeanSerializerBase.java:643)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeTypedFields(MapSerializer.java:1026)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeFields(MapSerializer.java:778)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeWithoutTypeInfo(MapSerializer.java:763)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeWithType(MapSerializer.java:732)
	at com.fasterxml.jackson.databind.ser.std.MapSerializer.serializeWithType(MapSerializer.java:34)
	at com.fasterxml.jackson.databind.ser.impl.TypeWrappedSerializer.serialize(TypeWrappedSerializer.java:32)
	at com.fasterxml.jackson.databind.ser.DefaultSerializerProvider._serialize(DefaultSerializerProvider.java:503)
	at com.fasterxml.jackson.databind.ser.DefaultSerializerProvider.serializeValue(DefaultSerializerProvider.java:342)
	at com.fasterxml.jackson.databind.ObjectMapper._writeValueAndClose(ObjectMapper.java:4926)
	at com.fasterxml.jackson.databind.ObjectMapper.writeValue(ObjectMapper.java:4105)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:165)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:114)
	at org.springframework.batch.core.repository.dao.jdbc.JdbcExecutionContextDao.serializeContext(JdbcExecutionContextDao.java:361)
	... 28 more
Caused by: com.fasterxml.jackson.core.JsonGenerationException: Can not write a field name, expecting a value
	at com.fasterxml.jackson.core.JsonGenerator._constructWriteException(JsonGenerator.java:2937)
	at com.fasterxml.jackson.core.JsonGenerator._reportError(JsonGenerator.java:2921)
	at com.fasterxml.jackson.core.json.UTF8JsonGenerator.writeFieldName(UTF8JsonGenerator.java:217)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer$JobParametersModule$JobParameterSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:213)
	at org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer$JobParametersModule$JobParameterSerializer.serialize(Jackson2ExecutionContextStringSerializer.java:195)
	at com.fasterxml.jackson.databind.ser.std.CollectionSerializer.serializeContentsUsing(CollectionSerializer.java:179)
	... 49 more
```

Upon debugging, it fails trying to serialize the first JobParameter.

**Environment**
Spring Batch 6.0.1, SQL Server 2022

**Steps to reproduce**
- Have a job using JobStep step
- Run the job passing some parameters to it

**Expected behavior**
Job runs successfully, saving step execution context like this (as it was in 5.2.3):
```
{
	"@class": "java.util.HashMap",
	"childJobExecId": [
		"java.lang.Long",
		3480
	],
	"org.springframework.batch.core.step.job.JobStep.JOB_PARAMETERS": {
		"@class": "org.springframework.batch.core.JobParameters",
		"parameters": {
			"@class": "java.util.Collections$UnmodifiableMap",
			"queueItemId": {
				"@class": "org.springframework.batch.core.JobParameter",
				"value": "250702",
				"type": "java.lang.String",
				"identifying": false
			},
			"execType": {
				"@class": "org.springframework.batch.core.JobParameter",
				"value": "MANUAL",
				"type": "java.lang.String",
				"identifying": false
			},
			"user": {
				"@class": "org.springframework.batch.core.JobParameter",
				"value": "system",
				"type": "java.lang.String",
				"identifying": false
			}
		}
	},
	"batch.version": "5.2.3"
}
```

Please also notice that org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.JobParametersModule.JobParameterSerializer#serialize is not adjusted to serialize parameter name.

**Minimal Complete Reproducible example**
Pretty straightforward - see steps to reproduce above


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-12

Thank you for opening this issue. If you upgrade to v6, you should be using `JacksonExecutionContextStringSerializer` and not `Jackson2ExecutionContextStringSerializer`. Did you update your configuration accordingly?

If your issue is related to `Jackson2ExecutionContextStringSerializer` in 5.2.x, please provide a minimal example or a failing test and I will plan the fix in the next patch release of 5.2.x.

### コメント 2 by andrianov17

**作成日**: 2026-01-13

Jackson2ExecutionContextStringSerializer is working fine in 5.x, but was not adjusted accordingly in 6.x and serialization (and deserialization) was broken.

It is just deprecated and recommended to migrate to Jackson 3, so until removed it should be functional for those how cannot migrate to Jackson 3 right away and need some time.

Once JacksonExecutionContextStringSerializer (Jackson 3) has been fixed, personally we don't need Jackson2ExecutionContextStringSerializer anymore, but others could still need for the reason mentioned above.

So, it's up to you how to proceed with Jackson2ExecutionContextStringSerializer. If you don't want to fix it now - wait for another similar issue.

Please however merge the PR because otherwise JacksonExecutionContextStringSerializer serializes some noise with doesn't make sense. BTW, the same PR offers fix for Jackson2ExecutionContextStringSerializer in 6.x

### コメント 3 by fmbenhassine

**作成日**: 2026-01-13

> Jackson2ExecutionContextStringSerializer is working fine in 5.x, but was not adjusted accordingly in 6.x and serialization (and deserialization) was broken.

Which deserialisation was broken? Are you trying to deserialise something with v6 that was serialised with v5? All jobs that were started with v5 should be run to completion (success or failure) with v5 (if a job failed with v5, it should be restarted with v5, not v6). Please make sure to run all your jobs to completion with v5 before upgrading to v6.

Now if you start a job with v6, the deserialisation will work fine. The serialisation/deserialization is not compatible between Spring Batch 5 / Jackson 2 and Spring Batch 6 / Jackson 3 (due to Jackson).

> It is just deprecated and recommended to migrate to Jackson 3, so until removed it should be functional for those how cannot migrate to Jackson 3 right away and need some time.

It is functional if you use it to deserialise a context that was serialised with it, as explained in the previous point

> So, it's up to you how to proceed with Jackson2ExecutionContextStringSerializer. If you don't want to fix it now - wait for another similar issue.

It's not that I don't want (I hope my previous message did not imply that), it's about in which branch/version to fix it, as explained in https://github.com/spring-projects/spring-batch/pull/5193#issuecomment-3740260690.

> Please however merge the PR because otherwise JacksonExecutionContextStringSerializer serializes some noise with doesn't make sense. BTW, the same PR offers fix for Jackson2ExecutionContextStringSerializer in 6.x

Yes that PR LGTM, but the fix of `Jackson2ExecutionContextStringSerializer` should go in `5.2.x`, not in `main`. We do not put additional effort to maintain deprecated APIs in v6, but we can fix them in v5 if needed.

### コメント 4 by andrianov17

**作成日**: 2026-01-13

Let's get back to the original issue.

Environment has been upgraded from Spring 5 to Spring 6. Existing Jackson2ExecutionContextStringSerializer was used (Jackson 3 migration to be done later). That's it.

Now, when you attempt to run a job having JobStep (nested job in its definition), it fails right away on SERIALIZATION - see stack trace above.

### コメント 5 by fmbenhassine

**作成日**: 2026-01-14

Thank you for the feedback. I don't know how I missed the detail that the issue is about `JobStep`, my bad, apologies. That's why it's always better to provide a failing example (we provide a comprehensive [issue reporting guide](https://github.com/spring-projects/spring-batch/blob/main/ISSUE_REPORTING.md) with a project template and everything needed to make reporting issues as easy as possible and save everyone's time).

The following sample fails as reported:

```java
package org.springframework.batch.samples.helloworld;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.EnableJdbcJobRepository;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.ExecutionContextSerializer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.infrastructure.repeat.RepeatStatus;
import org.springframework.batch.samples.common.DataSourceConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

@Configuration
@EnableBatchProcessing
@EnableJdbcJobRepository
@Import(DataSourceConfiguration.class)
public class HelloWorldJobConfiguration {

	@Bean
	public Step outerStep(JobRepository jobRepository) {
		Step innerStep = new StepBuilder("inner-step", jobRepository).tasklet((contribution, chunkContext) -> {
			System.out.println("Hello from inner step!");
			return RepeatStatus.FINISHED;
		}).build();
		Job innerJob = new JobBuilder("inner-job", jobRepository).start(innerStep).build();
		return new StepBuilder("outer-step", jobRepository).job(innerJob).build();
	}

	@Bean
	public Job outerJob(JobRepository jobRepository, Step outerStep) {
		return new JobBuilder("outer-job", jobRepository).start(outerStep).build();
	}

	@Bean
	public ExecutionContextSerializer executionContextSerializer() {
		return new Jackson2ExecutionContextStringSerializer();
	}

}
```

Now that I fully understand the issue, `Jackson2ExecutionContextStringSerializer` should be adapted in v6 as well. I will merge #5193 for that.

