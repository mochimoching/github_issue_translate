# Compatibility issues between v5 and v6 when Migrating from `CommandLineJobRunner` to `CommandLineJobOperator`

**Issue番号**: #5227

**状態**: open | **作成者**: fmbenhassine | **作成日**: 2026-01-21

**ラベル**: type: bug, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5227

## 内容


### Discussed in https://github.com/spring-projects/spring-batch/discussions/5213

<div type='discussions-op-text'>

<sup>Originally posted by **takahashihrzg** November 21, 2025</sup>
Starting with Spring Batch 6.0.0-M1, `CommandLineJobRunner` was deprecated and `CommandLineJobOperator` was introduced.
We are planning to migrate from `CommandLineJobRunner` to `CommandLineJobOperator`.

However, We found several incompatibilities during migration and are not sure how to handle them.
Could you please explain the reasons for these incompatible changes and how we should migrate?

1. Error output destination differs when starting a job without required arguments.
2. Validation exceptions at job startup are not logged.
3. We cannot customize `ExitCodeMapper` or `JobParametersConverter`.
4. The parameters required to stop or restart a job are different.

---

## 1) Error output destination differs when starting a job without required arguments

With `CommandLineJobRunner`, if we started a job without arguments such as `jobPath` or `jobIdentifier`, the exception was written to the **log**.

With `CommandLineJobOperator`, if we start a job without arguments such as `jobPath` or `jobIdentifier`, all exceptions are caught inside `CommandLineJobOperator` and printed only to the console via `System.err.printf`.

Why was this changed from logging exceptions (in `CommandLineJobRunner`) to printing them to standard error (in `CommandLineJobOperator`)? From an operations/monitoring point of view, exceptions are generally expected to be recorded in logs.

**Request:** printing exceptions only to standard error adds complexity to monitoring. Could you also log these exceptions?

---

## 2) Validation exceptions at job startup are not logged

With `CommandLineJobRunner`, if validation failed at job startup, the exception was thrown as-is and also logged.

With `CommandLineJobOperator`, if validation fails at startup, the exception is caught inside the `start` method and an exit code of 1 is returned.

As a result, when validation fails at startup with `CommandLineJobOperator`, the exception is neither stored in the `batch_job_execution` table nor written to the log.  
How can we verify that startup validation is actually running?

**Request:** please record validation failures in the logs.

**Example:**

Job definition
```java
@Bean
public Job testJob(JobRepository jobRepository,
                                    Step step01) {
    return new JobBuilder("testJob",
            jobRepository)
            .start(step01)
            .validator(new TestValidator())
            .build();
}
```

`TestValidator` code
```java
import org.springframework.batch.core.job.parameters.JobParameter;
import org.springframework.batch.core.job.parameters.JobParameters;
import org.springframework.batch.core.job.parameters.JobParametersInvalidException;
import org.springframework.batch.core.job.parameters.JobParametersValidator;

import java.util.Map;

public class TestValidator implements JobParametersValidator {
    @Override
    public void validate(JobParameters parameters) throws JobParametersInvalidException {
        Map<String, JobParameter<?>> params = parameters.getParameters();

        String str = params.get("str").getValue().toString();
        int num = Integer.parseInt(params.get("num").getValue().toString());

        if (str.length() > num) {
            throw new JobParametersInvalidException("The str must be less than or equal to num. [str:" + str + "][num:" + num + "]");
        }
    }
}
```

Run with the following parameters:
```
$ java CommandLineJobOperator TestJobConfig start testJob str=Hello num=4
```

We expect an exception from `TestValidator` to appear in the log (this is what `CommandLineJobRunner` does), e.g.:
```
[2025/11/05 10:33:21] [main] [o.h.v.i.util.Version  ] [INFO ] HV000001: Hibernate Validator 9.0.1.Final
[2025/11/05 10:33:21] [main] [o.s.b.c.l.s.CommandLineJobRunner] [ERROR] Job Terminated in error: The str must be less than or equal to num. [str:Hello][num:4]
org.springframework.batch.core.JobParametersInvalidException: The str must be less than or equal to num. [str:Hello][num:4]
```

But with `CommandLineJobOperator`, the exception from `TestValidator` is not shown, so we cannot confirm validation is working:
```
[2025/11/05 10:45:55] [main] [o.h.v.i.util.Version  ] [INFO ] HV000001: Hibernate Validator 9.0.1.Final
[2025/11/05 10:45:55] [main] [o.s.b.c.l.s.CommandLineJobOperator] [INFO ] Starting job with name 'job01' and parameters: {str=Hello, num=4}
```

---

## 3) Unable to customize `ExitCodeMapper` or `JobParametersConverter`

With `CommandLineJobRunner`, we could customize behavior by defining beans like `ExitCodeMapper` and `JobParametersConverter`, for example:

```java
@Bean
public ExitCodeMapper exitCodeMapper() {
    final SimpleJvmExitCodeMapper simpleJvmExitCodeMapper = new SimpleJvmExitCodeMapper();
    final Map<String, Integer> exitCodeMapper = new HashMap<>();
    exitCodeMapper.put("NOOP", 0);
    exitCodeMapper.put("COMPLETED", 0);
    exitCodeMapper.put("STOPPED", 255);
    exitCodeMapper.put("FAILED", 255);
    exitCodeMapper.put("UNKNOWN", 255);
    exitCodeMapper.put("COMPLETED_CUSTOM", 200);
    exitCodeMapper.put("STOPPED_CUSTOM", 201);
    exitCodeMapper.put("FAILED_CUSTOM", 202);
    simpleJvmExitCodeMapper.setMapping(exitCodeMapper);
    return simpleJvmExitCodeMapper;
}

@Bean
public JobParametersConverter jobParametersConverter(
        @Qualifier("adminDataSource") DataSource adminDataSource) {
    return new JobParametersConverterImpl(adminDataSource);
}
```

With `CommandLineJobOperator`, even if we define such beans, behavior does not change.

We believe this is due to implementation differences between `CommandLineJobRunner#start` and `CommandLineJobOperator#main`.  
`CommandLineJobRunner` uses `ApplicationContext.getAutowireCapableBeanFactory().autowireBeanProperties`, but `CommandLineJobOperator` only gets three beans (`JobOperator`, `JobRepository`, `JobRegistry`) from the DI container.

Because of this, even if `ExitCodeMapper` or `JobParametersConverter` exist as beans, they appear to be ignored by `CommandLineJobOperator`.

Code excerpts:

```java
// CommandLineJobRunner#start
int start(String jobPath, String jobIdentifier, String[] parameters, Set<String> opts) {

    ConfigurableApplicationContext context = null;
    // omitted
        try {
            context = new AnnotationConfigApplicationContext(Class.forName(jobPath));
        }
    // omitted
        context.getAutowireCapableBeanFactory()
            .autowireBeanProperties(this, AutowireCapableBeanFactory.AUTOWIRE_BY_TYPE, false);
    // omitted
}
```

```java
// CommandLineJobOperator#main
public static void main(String[] args) {
    // omitted
    ConfigurableApplicationContext context = null;
    try {
        Class<?> jobConfigurationClass = Class.forName(jobConfigurationClassName);
        context = new AnnotationConfigApplicationContext(jobConfigurationClass);
    }
    // omitted
    try {
        jobOperator = context.getBean(JobOperator.class);
        jobRepository = context.getBean(JobRepository.class);
        jobRegistry = context.getBean(JobRegistry.class);
    }
    // omitted
    CommandLineJobOperator operator = new CommandLineJobOperator(jobOperator, jobRepository, jobRegistry);
    // omitted
}
```

Were these implementation changes intentional? If so, what was the reasoning?

**Request:** please allow customization of `ExitCodeMapper` and `JobParametersConverter` with `CommandLineJobOperator` as well.

---

## 4) Different parameters needed to stop or restart a job

With `CommandLineJobRunner`, we could stop or restart a job by specifying either `jobName` or `jobExecutionId`.

With `CommandLineJobOperator`, we can only stop or restart by specifying `jobExecutionId`.

In practice, the user running the job typically only knows the `jobName` they provided.

If we need to stop or restart a job with `CommandLineJobOperator`, we first have to obtain the `jobExecutionId` somehow.
What is the recommended way to get `jobExecutionId` from the command line?

**Request:** please support stopping and restarting by `jobName` with `CommandLineJobOperator` as well.
</div>

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-21

Thank you for reporting this!

> 1) Error output destination differs when starting a job without required arguments
> Request: printing exceptions only to standard error adds complexity to monitoring. Could you also log these exceptions?

That's an oversight, I will fix it.

> 2) Validation exceptions at job startup are not logged
> Request: please record validation failures in the logs.

Same here. I will update the new operator accordingly.

> 3) Unable to customize ExitCodeMapper or JobParametersConverter
> Were these implementation changes intentional? If so, what was the reasoning?

Yes it was intentional and the reason is the following: for this to work:

```
context.getAutowireCapableBeanFactory().autowireBeanProperties(this, AutowireCapableBeanFactory.AUTOWIRE_BY_TYPE, false);
```

the command line job runner has to be defined as a bean in an application context. But what if I want to use it outside an application context? This is just impossible, note the `this` reference in the first argument to `autowireBeanProperties`. The new runner does not suffer from this limitation (and other limitations as explained in #4899). That said, we need to check (in the `main` method when we instantiate the operator) for the presence of any custom `ExitCodeMapper` or `JobParametersConverter` in the application context and set them on the operator.

I will plan that for the next release and update the migration guide accordingly.

> 4) Different parameters needed to stop or restart a job

Stopping or restarting a job by name was confusing. What if the job has two (or more) different instances running in parallel and you want to stop only one of them? Similarly, what if the job has two failed job instances and you only want to restart a single one? By specifying the execution you want to restart, this ambiguity is not possible. Getting the id of the failed execution is possible with a the `JobRepository` API. That said, you can still restart a job by name by using `JobRepository#getLastJobInstance(jobName)` and restarting the failed execution.

