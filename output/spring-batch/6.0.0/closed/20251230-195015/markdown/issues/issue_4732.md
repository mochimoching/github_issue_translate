# Inaccurate error message when using ResourcelessJobRepository with a partitioned step

**Issue番号**: #4732

**状態**: closed | **作成者**: monnetchr | **作成日**: 2024-12-10

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4732

**関連リンク**:
- Commits:
  - [69331c5](https://github.com/spring-projects/spring-batch/commit/69331c516dbb95cc23d4340fe083460fc376551e)

## 内容

**Bug description**
The ResourcelessJobRepository cannot be used with a Partitioner:
```
[main] ERROR org.springframework.batch.core.step.AbstractStep - Encountered an error executing step step in job partitionJob
org.springframework.batch.core.JobExecutionException: Cannot restart step from STARTING status.  The old execution may still be executing, so you may need to verify manually that this is the case.
```

**Steps to reproduce**
Simply change `spring-batch-samples/src/main/resources/simple-job-launcher-context.xml` to use `ResourcelessJobRepository` and then run `spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/file/PartitionFileJobFunctionalTests.java`



## コメント

### コメント 1 by fmbenhassine

**作成日**: 2024-12-10

The resourceless job repository does not support features involving the execution context (including partitioned steps). This is mentioned in the javadocs of the class: https://docs.spring.io/spring-batch/docs/current/api/org/springframework/batch/core/repository/support/ResourcelessJobRepository.html and in the reference docs here: https://docs.spring.io/spring-batch/reference/whatsnew.html#new-resourceless-job-repository

You need to configure another job repository implementation that supports batch-metadata. I am closing this issue now as I believe it answers your concern, but please add a comment if you need more support on this. Thank you.

### コメント 2 by fmbenhassine

**作成日**: 2024-12-10

I must admit the error message is confusing, there is no restart in that sample yet the message is mentioning restart. I will re-open this issue and change it into an enhancement.

### コメント 3 by kwondh5217

**作成日**: 2025-03-18

Hi @fmbenhassine, I would like to contribute to this issue.

To improve clarity, would it make sense to explicitly prevent the use of `ResourcelessJobRepository` with partitioned steps by throwing an exception? 

Proposed change:
```java
@Override
public Set<StepExecution> split(StepExecution stepExecution, int gridSize) throws JobExecutionException {
    if (jobRepository instanceof ResourcelessJobRepository) {
        throw new JobExecutionException("ResourcelessJobRepository cannot be used with partitioned steps "
                                        + "as it does not support execution context.");
    }
    ...

### コメント 4 by fmbenhassine

**作成日**: 2025-11-14

This was fixed as part of 90d895955d951156849ba6fa018676273fdbe2c4.

> **Steps to reproduce**
> Simply change `spring-batch-samples/src/main/resources/simple-job-launcher-context.xml` to use `ResourcelessJobRepository` and then run `spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/file/PartitionFileJobFunctionalTests.java`

I tried that sample with 6.0.0-RC2 and now it prints:

```
12:27:34.354 [main] INFO  o.s.b.c.c.x.CoreNamespaceHandler - DEPRECATION NOTE: The batch XML namespace is deprecated as of Spring Batch 6.0 and will be removed in version 7.0.
12:27:34.566 [main] INFO  o.s.b.c.s.i.ChunkOrientedTasklet - DEPRECATION NOTE: The legacy implementation of the chunk-oriented processing model is deprecated as of Spring Batch 6.0 and will be removed in version 7.0.
12:27:35.250 [main] INFO  o.s.b.c.l.s.TaskExecutorJobLauncher - Job: [FlowJob: [name=partitionJob]] launched with the following parameters: [{JobParameter{name='random', value=1393027390114809605, type=class java.lang.Long, identifying=true}}]
12:27:35.254 [main] INFO  o.s.b.c.j.SimpleStepHandler - Executing step: [step]
12:27:35.286 [SimpleAsyncTaskExecutor-2] INFO  o.s.b.c.s.AbstractStep - Step: [step1:partition1] executed in 28ms
12:27:35.286 [SimpleAsyncTaskExecutor-1] INFO  o.s.b.c.s.AbstractStep - Step: [step1:partition0] executed in 28ms
12:27:35.287 [main] INFO  o.s.b.c.s.AbstractStep - Step: [step] executed in 32ms
12:27:35.288 [main] INFO  o.s.b.c.l.s.TaskExecutorJobLauncher - Job: [FlowJob: [name=partitionJob]] completed with the following parameters: [{JobParameter{name='random', value=1393027390114809605, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 34ms
```

which does not log the confusing error message anymore.

