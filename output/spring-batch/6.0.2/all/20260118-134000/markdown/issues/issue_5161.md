# OptimisticLockingFailureException in JobRepositoryTestUtils.removeJobExecutions() since Spring Batch 5.2.3

**Issue番号**: #5161

**状態**: open | **作成者**: szopal24 | **作成日**: 2025-12-11

**ラベル**: in: test, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5161

**関連リンク**:
- Commits:
  - [12b16b3](https://github.com/spring-projects/spring-batch/commit/12b16b32adbbf35ead57b5e3b8d0ec84c56789ec)

## 内容

Since Spring Batch 5.2.3, calling JobRepositoryTestUtils.removeJobExecutions() in test cleanup methods throws OptimisticLockingFailureException when trying to delete job executions.

Environment
Spring Batch: 5.2.3, 5.2.4
Spring Boot: 3.4.5, 3.5.8
Java: 17
Database: PostgreSQL (with table prefix BOOT3_BATCH_)

**Test Code Example:**
```

    @Test
    public void testJob() throws Exception {
        JobExecution jobExecution = jobLauncherTestUtils.launchJob(defaultJobParameters());
        jobExecutionList.add(jobExecution);
        
        assertThat(jobExecution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);
    }

    @After
    public void cleanUp() {
        // This throws OptimisticLockingFailureException since 5.2.3
        jobRepositoryTestUtils.removeJobExecutions(jobExecutionList);
    }
```

Result:

```
org.springframework.dao.OptimisticLockingFailureException: Attempt to delete step execution id=95106 with wrong version (1)

	at org.springframework.batch.core.repository.dao.JdbcStepExecutionDao.deleteStepExecution(JdbcStepExecutionDao.java:386)
	at org.springframework.batch.core.repository.support.SimpleJobRepository.deleteStepExecution(SimpleJobRepository.java:316)
	at org.springframework.batch.core.repository.support.SimpleJobRepository.deleteJobExecution(SimpleJobRepository.java:324)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(AopUtils.java:360)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.invokeJoinpoint(ReflectiveMethodInvocation.java:196)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:163)
	at org.springframework.transaction.interceptor.TransactionAspectSupport.invokeWithinTransaction(TransactionAspectSupport.java:380)
	at org.springframework.transaction.interceptor.TransactionInterceptor.invoke(TransactionInterceptor.java:119)
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184)
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:223)
	at jdk.proxy2/jdk.proxy2.$Proxy126.deleteJobExecution(Unknown Source)
	at org.springframework.batch.test.JobRepositoryTestUtils.removeJobExecution(JobRepositoryTestUtils.java:156)
	at org.springframework.batch.test.JobRepositoryTestUtils.removeJobExecutions(JobRepositoryTestUtils.java:138)
	at xx.yyyyy.xx.aaaa.vvvv.bbbb.wwwww.SpringBatchIntegrationTest.cleanUp(SpringBatchIntegrationTest.java:82)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at org.springframework.test.context.junit4.statements.RunAfterTestMethodCallbacks.evaluate(RunAfterTestMethodCallbacks.java:86)
	at org.springframework.test.context.junit4.statements.SpringRepeat.evaluate(SpringRepeat.java:84)
	at org.springframework.test.context.junit4.SpringJUnit4ClassRunner.runChild(SpringJUnit4ClassRunner.java:252)
	at org.springframework.test.context.junit4.SpringJUnit4ClassRunner.runChild(SpringJUnit4ClassRunner.java:97)
	at org.springframework.test.context.junit4.statements.RunBeforeTestClassCallbacks.evaluate(RunBeforeTestClassCallbacks.java:61)
	at org.springframework.test.context.junit4.statements.RunAfterTestClassCallbacks.evaluate(RunAfterTestClassCallbacks.java:70)
	at org.springframework.test.context.junit4.SpringJUnit4ClassRunner.run(SpringJUnit4ClassRunner.java:191)
```

This breaks all existing Spring Batch integration tests that use JobRepositoryTestUtils.removeJobExecutions() in cleanup methods. This is a breaking change that affects any project upgrading from 5.2.2 to 5.2.3+. The Spring Batch documentation and Javadocs for JobRepositoryTestUtils.removeJobExecutions() do not mention this breaking change or provide guidance on how to update existing tests.

## コメント

### コメント 1 by quaff

**作成日**: 2025-12-12

It's introduced by #4793, you should query each `JobExecution` from `jobExecutionList` to get latest version for delete.

### コメント 2 by szopal24

**作成日**: 2025-12-17

Thank you, I managed to resolve the problem. Unfortunately, this means I now have to apply changes in more than 100 Spring Batch applications that were using this method to clean up the BATCH_JOB_EXECUTION table. While I understand the reasoning behind the change, it does have a significant impact on existing test setups.

### コメント 3 by quaff

**作成日**: 2025-12-18

@szopal24 I created #5173 to fix it.

### コメント 4 by szopal24

**作成日**: 2025-12-18

Thank you!

### コメント 5 by fmbenhassine

**作成日**: 2026-01-13

@szopal24  Thank you for reporting this issue and thank you @quaff for the PR.

I will plan the fix in 6.0.2 and back port it to 5.2.5

