# Incorrect restart behaviour with no identifying job parameters

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

## コメント

### コメント 1 by fmbenhassine

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

### コメント 2 by baezzys

**作成日**: 2025-04-29

Hi @fmbenhassine Can I work on this?

### コメント 3 by isanghaessi

**作成日**: 2025-08-15

Hi @fmbenhassine 👋
I opened PR for this issue #4946!
Please review and I will check ASAP💨

