*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# Spring Batch 5.2.3以降でJobRepositoryTestUtils.removeJobExecutions()がOptimisticLockingFailureExceptionをスローする

**Issue番号**: #5161

**状態**: closed | **作成者**: szopal24 | **作成日**: 2025-12-11

**ラベル**: in: test, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5161

**関連リンク**:
- コミット:
  - [1d9536c](https://github.com/spring-projects/spring-batch/commit/1d9536cfbabf54b921f5a522beef62e5d0793a97)
  - [12b16b3](https://github.com/spring-projects/spring-batch/commit/12b16b32adbbf35ead57b5e3b8d0ec84c56789ec)

## 内容

Spring Batch 5.2.3以降、テストのクリーンアップメソッドで`JobRepositoryTestUtils.removeJobExecutions()`を呼び出すと、ジョブ実行の削除時に`OptimisticLockingFailureException`がスローされるようになりました。

**環境**
Spring Batch: 5.2.3, 5.2.4
Spring Boot: 3.4.5, 3.5.8
Java: 17
データベース: PostgreSQL（テーブルプレフィックス BOOT3_BATCH_）

**テストコード例:**
```

    @Test
    public void testJob() throws Exception {
        JobExecution jobExecution = jobLauncherTestUtils.launchJob(defaultJobParameters());
        jobExecutionList.add(jobExecution);
        
        assertThat(jobExecution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);
    }

    @After
    public void cleanUp() {
        // 5.2.3以降ここでOptimisticLockingFailureExceptionがスローされる
        jobRepositoryTestUtils.removeJobExecutions(jobExecutionList);
    }
```

**結果:**

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

これにより、クリーンアップメソッドで`JobRepositoryTestUtils.removeJobExecutions()`を使用している既存のSpring Batch統合テストがすべて動作しなくなります。これは5.2.2から5.2.3以降にアップグレードするプロジェクトに影響を与える破壊的変更です。Spring BatchのドキュメントやJobRepositoryTestUtils.removeJobExecutions()のJavadocには、この破壊的変更や既存テストの更新方法に関するガイダンスが記載されていません。

## コメント

### コメント 1 by quaff

**作成日**: 2025-12-12

これは[#4793](https://github.com/spring-projects/spring-batch/issues/4793)で導入されました。削除のために最新バージョンを取得するには、`jobExecutionList`から各`JobExecution`をクエリする必要があります。

### コメント 2 by szopal24

**作成日**: 2025-12-17

ありがとうございます。問題を解決できました。残念ながら、このメソッドを使用してBATCH_JOB_EXECUTIONテーブルをクリーンアップしていた100以上のSpring Batchアプリケーションに変更を適用する必要があります。変更の理由は理解していますが、既存のテスト設定への影響は大きいです。

### コメント 3 by quaff

**作成日**: 2025-12-18

@szopal24 修正のために[#5173](https://github.com/spring-projects/spring-batch/issues/5173)を作成しました。

### コメント 4 by szopal24

**作成日**: 2025-12-18

ありがとうございます！

### コメント 5 by fmbenhassine

**作成日**: 2026-01-13

@szopal24 この問題を報告いただきありがとうございます。また @quaff さんPRをありがとうございます。

6.0.2で修正を計画し、5.2.5にバックポートする予定です。
