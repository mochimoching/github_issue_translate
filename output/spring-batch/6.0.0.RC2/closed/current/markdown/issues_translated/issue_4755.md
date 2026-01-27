*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月27日に生成されました）*

# 識別用ジョブパラメータがない場合のリスタート動作が不正

**Issue番号**: #4755

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-01-31

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/4755

**関連リンク**:
- Commits:
  - [1c28dac](https://github.com/spring-projects/spring-batch/commit/1c28daccf0958e2cdcfd1a784e3f7110e73881e4)
  - [250bfff](https://github.com/spring-projects/spring-batch/commit/250bfff1b6e8f2cf4e9219564c3f1d2719f0d17d)
  - [5225249](https://github.com/spring-projects/spring-batch/commit/5225249585fec7e479bf4b3194974d96a848c3c0)
  - [0564ce6](https://github.com/spring-projects/spring-batch/commit/0564ce6293e5178b12aa95b7bce5a461a38e4eb0)
  - [f888ebb](https://github.com/spring-projects/spring-batch/commit/f888ebb43f70d925c028721db0b3d71306089038)

## 内容


### https://github.com/spring-projects/spring-batch/discussions/4694 での議論

<div type='discussions-op-text'>

<sup>元投稿者：**ELMORABITYounes** 2024年10月28日</sup>
現在、ジョブが正常に完了した場合でも、非識別パラメータのみを含む場合はSpring Batchがリスタートを許可してしまいます。該当コードは以下の通りです：

```				
if (!identifyingJobParameters.isEmpty()                                                        
		&& (status == BatchStatus.COMPLETED || status == BatchStatus.ABANDONED)) {            
	throw new JobInstanceAlreadyCompleteException(                                             
			"A job instance already exists and is complete for identifying parameters="       
					+ identifyingJobParameters + ".  If you want to run this job again, "    
					+ "change the parameters.");                                             
}                                                                                              
```

なぜこのような実装になっているのでしょうか？ジョブが既に完了しているなら、`JobInstanceAlreadyCompleteException`をスローすべきではないでしょうか？パラメータなしの2回目のジョブインスタンスは同一のものとみなされ、既に成功している場合はリスタートを許可すべきではないと思うのですが。
</div>

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-01-31

この問題を報告していただきありがとうございます！以下のサンプルコードで問題を再現できました：

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
		jobLauncher.run(job, jobParameters2); // 期待される動作: JobInstanceAlreadyCompleteException
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

	// インフラストラクチャBean

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

デフォルトのジョブキージェネレータは期待通りに動作しています（同じ入力、つまり空の識別用ジョブパラメータセットに対して同じハッシュを生成します）。しかし、Spring Batchはこれを異なるジョブインスタンスとみなして実行してしまいます。本来はそうあるべきではありません。

---

参考までに、デフォルトのジョブキージェネレータは期待通りに動作しています（以下のテストは5.2.1で成功します）：

```java
// org.springframework.batch.core.DefaultJobKeyGeneratorTests に追加

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

### コメント 2 by baezzys

**作成日**: 2025-04-29

@fmbenhassine この課題に取り組んでもよろしいでしょうか？

### コメント 3 by isanghaessi

**作成日**: 2025-08-15

@fmbenhassine こんにちは👋
この課題に対するPR [#4946](https://github.com/spring-projects/spring-batch/pull/4946) を作成しました！
レビューをお願いします。できるだけ早く確認いたします💨
