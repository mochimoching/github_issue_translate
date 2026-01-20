# MetaDataInstanceFactory default values cause StepContext collision in StepScopeTestUtils when @SpringBatchTest is active

**Issue番号**: #5181

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: in: test, status: waiting-for-reporter, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5181

## 内容

## Bug description: 
There is a logical collision in StepSynchronizationManager when using StepScopeTestUtils in a test environment managed by @SpringBatchTest.

StepExecution determines equality based on stepName, jobExecutionId, and id. Since MetaDataInstanceFactory provides static default values for all these fields, multiple instances created by the factory are treated as identical keys in the SynchronizationManagerSupport.contexts map.

This prevents StepScopeTestUtils from registering a new context with custom JobParameters, as the computeIfAbsent logic finds the existing context registered by StepScopeTestExecutionListener (which is part of @SpringBatchTest).

## Steps to reproduce:
Annotate a test class with @SpringBatchTest.

Inside a test method, use StepScopeTestUtils.doInStepScope() with a StepExecution created via MetaDataInstanceFactory.createStepExecution(jobParameters).

The Tasklet or ItemStream inside the scope will fail to see the jobParameters because it is bound to the listener's initial context.

## Failing Example: 
example job
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            Tasklet issueReproductionTasklet
    ) {
        return new StepBuilder(jobRepository)
                .tasklet(issueReproductionTasklet)
                .build();
    }

    @Bean
    @StepScope
    public Tasklet issueReproductionTasklet(@Value("#{jobParameters['testParam']}") String testParam) {
        return (contribution, chunkContext) -> {
            contribution.getStepExecution().getExecutionContext().putString("result", testParam);
            return RepeatStatus.FINISHED;
        };
    }
}
```

test class
```java
@SpringBatchTest
@SpringBootTest
@ActiveProfiles("test")
@Import(TestBatchConfiguration.class)
public class IssueReproductionTest {
    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactory ID collision causes JobParameter injection failure")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // MetadataInstanceFactory in 6.x / maybe after 5.2.3?? creates StepExecution with fixed ID 1234L
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // This will FAIL because 'actualValue' will be null.
        // The Tasklet retrieved the listener's context (which has no JobParameters)
        // instead of the one passed via StepScopeTestUtils due to ID collision (1234L).
        assertEquals(expectedValue, actualValue);
    }
}

@TestConfiguration
public class TestBatchConfiguration extends DefaultBatchConfiguration {
}
```

application-test.yml
```yaml
spring:
  batch:
    job:
      enabled: false
```
test result:
```bash
Value for key=[result] is not of type: [class java.lang.String], it is [null]
java.lang.ClassCastException: Value for key=[result] is not of type: [class java.lang.String], it is [null]
```

## Expected behavior:
The StepExecution and its corresponding StepContext created within StepScopeTestUtils.doInStepScope() should be correctly registered and accessible through the StepSynchronizationManager, even when @SpringBatchTest is active.

(Note: Deciding on the best fix seems non-trivial to me, as it could involve changing the ID generation strategy in MetaDataInstanceFactory or adjusting how StepSynchronizationManager handles overlapping registrations in a test environment.)
Workaround: Users must manually provide a unique name or ID to bypass the equals/hashCode collision:

## Workaround: 
To bypass the current collision, users can explicitly define a getStepExecution() method within their test class. By returning a StepExecution with a unique name or a different ID (e.g., -1L), you can prevent the StepScopeTestExecutionListener from occupying the default ID (1234L), thus allowing StepScopeTestUtils to work as intended:

```java
/**
 * Workaround: Define getStepExecution() in the test class to avoid ID collision.
 * By providing a non-default ID or name, we ensure that the listener-registered 
 * context does not conflict with the one created in StepScopeTestUtils.
 */
public StepExecution getStepExecution() {
    return MetaDataInstanceFactory.createStepExecution("uniqueStep", -1L);
}
```

test result:
```bash
> Task :test
BUILD SUCCESSFUL in 3s
```

Thanks for your time and for maintaining this great project!

## コメント

### コメント 1 by injae-kim

**作成日**: 2026-01-11

FYI) Fix PR: https://github.com/spring-projects/spring-batch/pull/5208 👍

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

I am trying to reproduce this issue but I am not able to. The test you shared uses Spring Boot, but I want to make sure this is a valid issue by only using Spring Batch first.

At 9ae777572a0978572e25f04d4cb93c0ad02b9a0f, when I add the following classes (the same you shared but without Spring Boot) in the `org.springframework.batch.test` package, the test you mentioned passes:

```java
package org.springframework.batch.test;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.job.parameters.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.infrastructure.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableBatchProcessing
public class IssueReproductionJobConfiguration {

    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            Tasklet issueReproductionTasklet
    ) {
        return new StepBuilder(jobRepository)
                .tasklet(issueReproductionTasklet)
                .build();
    }

    @Bean
    @StepScope
    public Tasklet issueReproductionTasklet(@Value("#{jobParameters['testParam']}") String testParam) {
        return (contribution, chunkContext) -> {
            contribution.getStepExecution().getExecutionContext().putString("result", testParam);
            return RepeatStatus.FINISHED;
        };
    }
}
```

```java
package org.springframework.batch.test;

import java.io.IOException;
import java.util.Objects;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.springframework.batch.core.job.parameters.JobParameters;
import org.springframework.batch.core.job.parameters.JobParametersBuilder;
import org.springframework.batch.core.step.StepExecution;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;

@ContextConfiguration(classes = IssueReproductionJobConfiguration.class)
@ExtendWith(SpringExtension.class)
public class IssueReproductionTest {

    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactory ID collision causes JobParameter injection failure")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // MetadataInstanceFactory in 6.x / maybe after 5.2.3?? creates StepExecution with fixed ID 1234L
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // This will FAIL because 'actualValue' will be null.
        // The Tasklet retrieved the listener's context (which has no JobParameters)
        // instead of the one passed via StepScopeTestUtils due to ID collision (1234L).
        assertEquals(expectedValue, actualValue);
    }
}
```

Can you please check?

