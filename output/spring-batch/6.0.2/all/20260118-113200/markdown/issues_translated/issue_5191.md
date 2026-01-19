*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# Jackson2ExecutionContextStringSerializerがJobStepでジョブパラメータのシリアライズに失敗する

**課題番号**: [#5191](https://github.com/spring-projects/spring-batch/issues/5191)

**状態**: closed | **作成者**: andrianov17 | **作成日**: 2025-12-30

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5191

**関連リンク**:
- コミット:
  - [0116494](https://github.com/spring-projects/spring-batch/commit/0116494b54a92bde25966071a56adf50ec198d64)
  - [2a5646a](https://github.com/spring-projects/spring-batch/commit/2a5646a2dee92e4556c71c39719e3cfed34d0a74)
  - [72c4aa2](https://github.com/spring-projects/spring-batch/commit/72c4aa2779184528aca9b97b4c8f4a6fa3473add)
  - [0bb92d5](https://github.com/spring-projects/spring-batch/commit/0bb92d54504dfcc2dcb17989f5120f29a9a23261)
  - [79f679f](https://github.com/spring-projects/spring-batch/commit/79f679f9ed91f399c67f3f56b07d8a61c742ab47)

## 内容

**バグの説明**
Spring Batch 5.2.3からSpring Batch 6.0.1にアップグレードし、以前の`org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer`シリアライザを維持した後、`JobStep`が以下の例外で失敗します:

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

デバッグしたところ、最初の`JobParameter`をシリアライズしようとした際に失敗しています。

**環境**
Spring Batch 6.0.1、SQL Server 2022

**再現手順**
- `JobStep`ステップを使用するジョブを用意する
- いくつかのパラメータを渡してジョブを実行する

**期待される動作**
ジョブが正常に実行され、ステップ実行コンテキストが以下のように保存される（5.2.3での動作と同様）:
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

また、`org.springframework.batch.core.repository.dao.Jackson2ExecutionContextStringSerializer.JobParametersModule.JobParameterSerializer#serialize`がパラメータ名をシリアライズするように調整されていないことにもご注意ください。

**最小限の完全な再現例**
非常にシンプルです - 上記の再現手順を参照してください


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-12

この課題を開いていただきありがとうございます。v6にアップグレードする場合は、`Jackson2ExecutionContextStringSerializer`ではなく`JacksonExecutionContextStringSerializer`を使用すべきです。それに応じて設定を更新しましたか？

課題が5.2.xの`Jackson2ExecutionContextStringSerializer`に関連する場合は、最小限の例または失敗するテストを提供していただければ、5.2.xの次のパッチリリースで修正を予定します。

### コメント 2 by andrianov17

**作成日**: 2026-01-13

`Jackson2ExecutionContextStringSerializer`は5.xでは正常に動作していますが、6.xでは適切に調整されておらず、シリアライゼーション（およびデシリアライゼーション）が壊れています。

これは非推奨となり、Jackson 3への移行が推奨されていますが、削除されるまでは、すぐにJackson 3に移行できない人やもう少し時間が必要な人のために機能すべきです。

`JacksonExecutionContextStringSerializer`（Jackson 3）が修正されたら、個人的には`Jackson2ExecutionContextStringSerializer`は必要なくなりますが、上記の理由から他の人はまだ必要とする可能性があります。

したがって、`Jackson2ExecutionContextStringSerializer`をどう進めるかはあなた次第です。今すぐ修正したくない場合は、別の同様の課題を待ってください。

ただし、PRはマージしてください。そうしないと`JacksonExecutionContextStringSerializer`が意味のないノイズをシリアライズしてしまいます。ちなみに、同じPRで6.xの`Jackson2ExecutionContextStringSerializer`の修正も提供しています。

### コメント 3 by fmbenhassine

**作成日**: 2026-01-13

> Jackson2ExecutionContextStringSerializerは5.xでは正常に動作していますが、6.xでは適切に調整されておらず、シリアライゼーション（およびデシリアライゼーション）が壊れています。

どのデシリアライゼーションが壊れていますか？v5でシリアライズされたものをv6でデシリアライズしようとしていますか？v5で開始されたすべてのジョブは、v5で完了まで実行する必要があります（v5でジョブが失敗した場合、v6ではなくv5で再起動する必要があります）。v6にアップグレードする前に、すべてのジョブをv5で完了させてください。

v6でジョブを開始すれば、デシリアライゼーションは正常に動作します。Spring Batch 5 / Jackson 2とSpring Batch 6 / Jackson 3の間では、シリアライゼーション/デシリアライゼーションに互換性がありません（Jacksonの仕様によるものです）。

> これは非推奨となり、Jackson 3への移行が推奨されていますが、削除されるまでは、すぐにJackson 3に移行できない人やもう少し時間が必要な人のために機能すべきです。

前のポイントで説明したように、シリアライズされたコンテキストをデシリアライズするために使用すれば機能します。

> したがって、Jackson2ExecutionContextStringSerializerをどう進めるかはあなた次第です。今すぐ修正したくない場合は、別の同様の課題を待ってください。

したくないというわけではありません（前のメッセージでそのような印象を与えていなければ良いのですが）。どのブランチ/バージョンで修正するかについてです。https://github.com/spring-projects/spring-batch/pull/5193#issuecomment-3740260690 で説明したとおりです。

> PRはマージしてください。そうしないとJacksonExecutionContextStringSerializerが意味のないノイズをシリアライズしてしまいます。ちなみに、同じPRで6.xのJackson2ExecutionContextStringSerializerの修正も提供しています。

はい、そのPRは良さそうですが、`Jackson2ExecutionContextStringSerializer`の修正は`main`ではなく`5.2.x`に入れるべきです。v6では非推奨のAPIを維持するための追加の努力はしませんが、必要であればv5で修正できます。

### コメント 4 by andrianov17

**作成日**: 2026-01-13

元の課題に戻りましょう。

環境がSpring 5からSpring 6にアップグレードされました。既存の`Jackson2ExecutionContextStringSerializer`を使用しています（Jackson 3への移行は後で行います）。それだけです。

さて、定義に`JobStep`（ネストされたジョブ）を持つジョブを実行しようとすると、上記のスタックトレースにあるように、シリアライゼーションですぐに失敗します。

### コメント 5 by fmbenhassine

**作成日**: 2026-01-14

フィードバックをいただきありがとうございます。課題が`JobStep`に関するものという詳細を見落としていました、申し訳ありません。だからこそ、失敗する例を提供することが常に良いのです（私たちは包括的な[課題報告ガイド](https://github.com/spring-projects/spring-batch/blob/main/ISSUE_REPORTING.md)を提供しており、プロジェクトテンプレートと課題を報告するために必要なすべてが含まれており、できるだけ簡単にして皆の時間を節約できるようにしています）。

以下のサンプルは報告されたとおりに失敗します:

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

課題を完全に理解したので、`Jackson2ExecutionContextStringSerializer`もv6で対応する必要があります。[#5193](https://github.com/spring-projects/spring-batch/pull/5193) をマージします。
