*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# asyncTaskExecutorを使用したjobOperator.start()でジョブ起動時に断続的にOptimisticLockingFailureExceptionが発生する

**Issue番号**: #5106

**状態**: closed | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

**関連リンク**:
- コミット:
  - [b024116](https://github.com/spring-projects/spring-batch/commit/b024116968ac5dd89ea84a8a3048d0e4a39d7519)
  - [76e723e](https://github.com/spring-projects/spring-batch/commit/76e723e41939b1ab6910f9ce8d61053abb1d0575)

## 内容

**バグの説明**
`asyncTaskExecutor`を使用して`jobOperator.start()`でジョブを起動すると、断続的に`OptimisticLockingFailureException`が発生します。

**環境**
Spring Boot 4.0.0
Spring Batch 6.0.0
Java 21

**再現手順**
1) Spring InitializrでSpring BatchとSpring Data Jpaを選択して新しいSpring Bootプロジェクトを作成します。
2) 設定クラスを作成し、`@EnableBatchProcessing`と`@EnableJdbcJobRepository`アノテーションを付与します。
3) シンプルなジョブを実装し、`asyncTaskExecutor`を使用して`jobOperator`を作成します。
4) `jobOperator.start()`でジョブを起動します。
5) `JdbcJobExecutionDao.updateJobExecution()`で断続的に`OptimisticLockingFailureException`が発生します。
6) デバッグの結果、ジョブインスタンスが`BATCH_JOB_EXECUTION`テーブルに挿入されないことがあり、その状態で`asyncTaskExecutor`を使用して新しいスレッドでジョブ実行が開始され（これは`TaskExecutorJobLauncher`クラス内）、テーブル内のジョブ実行レコードが見つからず`OptimisticLockingFailureException`が発生することがわかりました。

**期待される動作**
ジョブは常に問題なく実行されるべきです。


## コメント

### コメント 1 by ahoehma

**作成日**: 2025-12-01

私が直面している問題とは完全に同じではありませんが :-)、このフィードバックも注視していきます。

（私はこちらでディスカッションを開始しました: https://github.com/spring-projects/spring-batch/discussions/5121）

### コメント 2 by phactum-mnestler

**作成日**: 2025-12-17

私たちも同じ問題に遭遇しています。最小限の再現環境をこちらに作成しました: https://github.com/phactum-mnestler/spring-batch-reproducer
スタックトレースから判断すると、この問題は`TaskExecutorJobLauncher`の非同期実行可能オブジェクトとそれを囲む`finally`句の間のレースコンディションが原因のようです:
```
org.springframework.dao.OptimisticLockingFailureException: Attempt to update job execution id=1 with wrong version (0), where current version is 1
	at org.springframework.batch.core.repository.dao.jdbc.JdbcJobExecutionDao.updateJobExecution(JdbcJobExecutionDao.java:302) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.repository.support.SimpleJobRepository.update(SimpleJobRepository.java:152) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
        ----- AOPトレースは省略 ---
	at jdk.proxy3/jdk.proxy3.$Proxy85.update(Unknown Source) ~[na:na]
	at org.springframework.batch.core.job.AbstractJob.updateStatus(AbstractJob.java:420) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.job.AbstractJob.execute(AbstractJob.java:289) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.launch.support.TaskExecutorJobLauncher$1.run(TaskExecutorJobLauncher.java:220) ~[spring-batch-core-6.0.1.jar:6.0.1]
```
この`finally`句はSpring Batch 5.xには存在せず、5.xでは`Runnable`がスケジュールできなかった場合にのみジョブ実行を更新していました。

新しくリリースされた6.0.1バージョンでもこの問題が継続していることを確認しています。

### コメント 3 by licenziato

**作成日**: 2025-12-17

同じ問題と同じ根本原因を確認しました。回避策として、`JobOperator`が使用する`ThreadPoolTaskExecutor`をシングルスレッドエグゼキューターに設定することでレースコンディションを解決しました。正式な修正を待っています:

```
    @Bean
    public JobOperatorFactoryBean jobOperator(JobRepository jobRepository) {
        ThreadPoolTaskExecutor taskExecutor = new ThreadPoolTaskExecutor();
        taskExecutor.setCorePoolSize(1);
        taskExecutor.setMaxPoolSize(1);
        taskExecutor.afterPropertiesSet();

        JobOperatorFactoryBean jobOperatorFactoryBean = new JobOperatorFactoryBean();
        jobOperatorFactoryBean.setJobRepository(jobRepository);
        jobOperatorFactoryBean.setTaskExecutor(taskExecutor);
        return jobOperatorFactoryBean;
    }

```

### コメント 4 by kizombaDev

**作成日**: 2025-12-19

残念ながら、私たちもSpring Batch 6.0.1、MongoDB、および`ThreadPoolTaskExecutor`で同じ問題に直面しています。

`jobOperator.start(job, new JobParameters())`を使用してジョブを起動すると、すぐに`DataIntegrityViolationException`が発生します。

`org.springframework.batch.core.launch.support.TaskExecutorJobLauncher#launchJobExecution`メソッドの`finally`ブロック内の`this.jobRepository.update(jobExecution);`の呼び出しが問題の原因であることを確認しました。
