# Deprecate modular job configuration through EnableBatchProcessing

**Issue番号**: #4866

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-09

**ラベル**: type: task, in: core, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4866

**関連リンク**:
- Commits:
  - [bcf4f72](https://github.com/spring-projects/spring-batch/commit/bcf4f724addc96c5beed2447ad9423008a3d6da8)

## 内容

The support of job configuration modularity through `@EnableBatchProcessing(modular = true)` to avoid job name collisions in the `JobRegistry` requires an unnecessary amount of accidental complexity both in terms of APIs the user has to provide as well as implementation details. The amount of classes and interfaces needed for this feature (`JobFactory`, `ApplicationContextFactory`, `ApplicationContextJobFactory`, `ReferenceJobFactory`, `AbstractApplicationContextFactory` (with its two extensions), `JobLoader`, `JobFactoryRegistrationListener` and others) does not justify the real gain. This feature could be achieved by leveraging `GroupAwareJob`s or  by using a simple naming convention like `namespace.jobName`.

This feature should be deprecated in v6 and removed in 6.2 or later.

## コメント

### コメント 1 by kzander91

**作成日**: 2025-10-23

@fmbenhassine Can we get some guidance on what `GroupAwareJob` is and how to use it? The reference documentation doesn't mention that at all, and searching through the source code didn't really tell me how to use that as well.

I was using modular configuration to get some nice isolation between my jobs, where each job was running in it's own context and could use the same name for the various reader/writer beans and such.

The migration guide is not helpful here either, it basically just states to "use `GroupAwareJob` or context hierarchies", but doesn't give any hints on how that would work (particularly in a Spring Boot app, but I'm sure that non-Boot folks would appreciate that as well).

### コメント 2 by fmbenhassine

**作成日**: 2025-10-23

Yes, I will update the migration guide with a practical example.

Can you please share your use case with a code example? 

Also, I personally never used that feature (and [seems like I am not the only one](https://github.com/spring-projects/spring-batch/discussions/4871)) so I am genuinely curious to have some feedback from real users of it. How would you address your requirement if Spring Batch did not provide that feature?

### コメント 3 by kzander91

**作成日**: 2025-10-28

> Yes, I will update the migration guide with a practical example.

Thank you 🙏

> Can you please share your use case with a code example?

Sure. I have structured my app like this:
```
com.acme/
├── main/
│   └── @SpringBootApplication(scanBasePackages= "com.acme.config.common")
└── config/
    ├── common/
    │   ├── @Configuration SomeCommonConfiguration.java
    │   ├── @Component SomeSharedComponent.java
    │   └── @EnableBatchProcessing(modular = true) @Configuration JobContextsConfiguration.java
    └── jobs/
        ├── foojob/
        │   ├── @ComponentScan @Configuration FooJobConfiguration.java
        │   ├── @Component Reader.java
        │   ├── @Component Processor.java
        │   └── @Component Writer.java
        └── barjob/
            ├── @ComponentScan @Configuration BarJobConfiguration.java
            ├── @Component Reader.java
            ├── @Component Processor.java
            └── @Component Writer.java
```
* Common configuration classes and components shared across all jobs reside in a `config.common` package that is being component-scanned.
* Individual job configurations and beans specific for those jobs reside in their own packages and are not included in Spring Boot's component scan.
* `JobContextsConfiguration` (included in Boot's component scan) defines one bean like this for each job:
  ```java
  @Bean
  @Profile("!test")
  ApplicationContextFactory fooJobContextFactory() {
      return new GenericApplicationContextFactory(FooJobConfiguration.class);
  }
  ```
* The job-specific configuration classes (`FooJobConfiguration` and `BarJobConfiguration`) component-scan their package (and sub-packages).
  Each of them also defines a single `Job` bean, so
  ```java
  @Bean Job fooJob() { ... }
  ```
* Most of my jobs are pretty simple and structured similarly: They mostly fetch data from one source, _maybe_ transform it slightly and then write it to a sink. My reader and writer bean definitions are thus very similar and simple bean names like `reader` and `writer` are used.
* Because each job runs in its own application context, autowiring by type and using the same bean names just works and makes the entire setup pretty simple to understand and extend (new job? Just create a new package and define a new `ApplicationContextFactory`).

As you can see, I'm using the modular configuration mostly for convenience. As such _not_ having it wouldn't be the end of the world, but makes the effort to migrate to Spring Batch 6 way more involved than it would otherwise have been.

This structure also simplifies testing using `@SpringBatchTest`, because the `JobLauncherTestUtils` bean expects _a single_ `Job` bean. For example, the tests for the foo job use `@SpringBootTest @SpringBatchTest @ActiveProfiles("test") @Import(FooJobConfiguration.class)`, to get the same context as the job itself, and since the `test` profile disables the `ApplicationContextFactory` beans, the resulting test context only knows a single `Job`, so `JobLauncherTestUtils` is happy.

### コメント 4 by fmbenhassine

**作成日**: 2025-10-30

Thank you for the feedback! I am really keen to help here. Can you please package that in a GitHub repo or a zip I can work on? I will create a diff patch to illustrate the migration path in a practical way. Many thanks upfront.

### コメント 5 by kzander91

**作成日**: 2025-11-02

[demo9.zip](https://github.com/user-attachments/files/23290944/demo9.zip)

This is a project with a structure similar to what I have described above.

### コメント 6 by fmbenhassine

**作成日**: 2025-11-02

@kzander91 Thank you very much for providing a sample app! Since this ticket is closed, I created #5072 to track the documentation improvement. Let's continue there.

### コメント 7 by marbon87

**作成日**: 2025-11-12

Hi @fmbenhassine,

we are also using the AutomaticJobRegistrar in our company internal framework for about 100 batch apps to create a separate context for each job with the same benefits @kzander91 already mentioned. 
Can you give some information why AutomaticJobRegistrar and the corresponding classes are deprecated?
From my point of view it is a useful feature and i do not undestand why it should be removed.

Regards,
Mark

### コメント 8 by fmbenhassine

**作成日**: 2025-11-19

Hi @marbon87 ,

> Can you give some information why AutomaticJobRegistrar and the corresponding classes are deprecated?

The rationale behind this decision is explained in the description of this issue: https://github.com/spring-projects/spring-batch/issues/4866#issue-3129848683

FTR, I added an example of how to migrate this feature to v6 here: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide#changes-related-to-the-modular-batch-configurations-through-enablebatchprocessingmodular--true. Using Spring's context hierarchies is more straightforward and way easier to think about than the ton of classes that are needed to implement and use that feature prior to v6. 

Please let me know if you need support in migrating your Spring Batch jobs to v6, I would be happy to help!

Best regards,
Mahmoud

### コメント 9 by marbon87

**作成日**: 2025-11-25

Hi @fmbenhassine ,

thanks for your support. We have a webmvc-controller for starting jobs and use the jobregistry with a logic like this:
```
	@NonNull
	public Optional<JobExecution> start(@NonNull String jobName,
										@NonNull JobParameters jobParameters)
		throws JobInstanceAlreadyCompleteException, JobExecutionAlreadyRunningException, JobParametersConversionException, JobRestartException, InvalidJobParametersException {
		Job job = jobRegistry.getJob(jobName);
		if (job == null) {
			return Optional.empty();
		}
		JobParametersIncrementer jobParametersIncrementer = job.getJobParametersIncrementer();
		if (jobParametersIncrementer != null) {
			jobParameters = jobParametersIncrementer.getNext(jobParameters);
		}
		return jobOperator.start(job, jobParameters);
	}
```

Do you have an advice how this can be implemented without AutomaticJobRegistrar and JobLoader.

Best regards, Mark

### コメント 10 by fmbenhassine

**作成日**: 2025-11-25

@marbon87 Since this ticket is closed, please open a "Migration Support" request in [GitHub Discussions](https://github.com/spring-projects/spring-batch/discussions/categories/migration-support) (with all the details and the code sample to migrate)  and I will help there. Thank you upfront.

### コメント 11 by fmbenhassine

**作成日**: 2025-12-09

@marbon87 I created #5154 for your support request here: https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3575452892. Let's continue there.

