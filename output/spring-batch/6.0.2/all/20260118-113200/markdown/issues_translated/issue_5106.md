*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# asyncTaskExecutorを使用したjobOperator.start()でジョブを開始すると断続的にOptimisticLockingFailureExceptionが発生する

**課題番号**: [#5106](https://github.com/spring-projects/spring-batch/issues/5106)

**状態**: closed | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

**関連リンク**:
- コミット:
  - [b024116](https://github.com/spring-projects/spring-batch/commit/b024116968ac5dd89ea84a8a3048d0e4a39d7519)
  - [76e723e](https://github.com/spring-projects/spring-batch/commit/76e723e41939b1ab6910f9ce8d61053abb1d0575)

## 内容

**バグの説明**
`asyncTaskExecutor`を使用して`jobOperator.start()`でジョブを開始すると、`OptimisticLockingFailureException`が断続的に発生します。

**環境**
Spring Boot 4.0.0
Spring Batch 6.0.0
Java 21

**再現手順**
1) Spring Initializrで、Spring BatchとSpring Data Jpaを選択して新しいSpring Bootプロジェクトを作成します。
2) 設定クラスを作成し、`@EnableBatchProcessing`と`@EnableJdbcJobRepository`アノテーションを付与します。
3) シンプルなジョブを実装し、`asyncTaskExecutor`を使用して`jobOperator`を作成します。
4) `jobOperator.start()`を使用してジョブを開始します。
5) `JdbcJobExecutionDao.updateJobExecution()`で断続的に`OptimisticLockingFailureException`が発生します。
6) デバッグの結果、ジョブインスタンスが`BATCH_JOB_EXECUTION`テーブルに挿入されていないにもかかわらず、`asyncTaskExecutor`を使用して新しいスレッドでジョブ実行が開始されていることがわかりました（これは`TaskExecutorJobLauncher`クラスで発生します）。テーブルにジョブ実行レコードが見つからないため、`OptimisticLockingFailureException`が発生します。

**期待される動作**
ジョブは常に問題なく実行されるべきです。


## コメント

### コメント 1 by ahoehma

**作成日**: 2025-12-01

私が取り組んでいる問題とは正確には一致しませんが、このフィードバックも注視していきます :-)

（こちらのディスカッションを開始しました: https://github.com/spring-projects/spring-batch/discussions/5121）

### コメント 2 by phactum-mnestler

**作成日**: 2025-12-17

報告されている問題と同じ現象が発生しています。最小限の再現コードをこちらに作成しました: https://github.com/phactum-mnestler/spring-batch-reproducer

スタックトレースを見ると、`TaskExecutorJobLauncher`の非同期Runnableと、それを囲む`finally`句の間でレースコンディションが発生しているようです:
```
org.springframework.dao.OptimisticLockingFailureException: Attempt to update job execution id=1 with wrong version (0), where current version is 1
	at org.springframework.batch.core.repository.dao.jdbc.JdbcJobExecutionDao.updateJobExecution(JdbcJobExecutionDao.java:302) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.repository.support.SimpleJobRepository.update(SimpleJobRepository.java:152) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103) ~[na:na]
        ----- AOP traces skipped ---
	at jdk.proxy3/jdk.proxy3.$Proxy85.update(Unknown Source) ~[na:na]
	at org.springframework.batch.core.job.AbstractJob.updateStatus(AbstractJob.java:420) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.job.AbstractJob.execute(AbstractJob.java:289) ~[spring-batch-core-6.0.1.jar:6.0.1]
	at org.springframework.batch.core.launch.support.TaskExecutorJobLauncher$1.run(TaskExecutorJobLauncher.java:220) ~[spring-batch-core-6.0.1.jar:6.0.1]
```
この`finally`句はSpring Batch 5.xには存在せず、`Runnable`のスケジュールに失敗した場合にのみジョブ実行を更新していました。

新しくリリースされた6.0.1バージョンでもこの問題が継続していることを確認しています。

### コメント 3 by licenziato

**作成日**: 2025-12-17

同じ問題と根本原因を確認しました。回避策として、`JobOperator`で使用する`ThreadPoolTaskExecutor`をシングルスレッドエグゼキュータに設定することで、正式な修正を待つ間、レースコンディションを解消できました:

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

残念ながら、Spring Batch 6.0.1、MongoDB、`ThreadPoolTaskExecutor`の組み合わせで同じ問題が発生しています。

`jobOperator.start(job, new JobParameters())`を使用してジョブを開始すると、すぐに`DataIntegrityViolationException`が発生します。

`org.springframework.batch.core.launch.support.TaskExecutorJobLauncher#launchJobExecution`メソッドのfinallyブロック内の`this.jobRepository.update(jobExecution);`呼び出しが問題の原因であることを確認しました。

再現コードをMongoDBで作成しました: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

### コメント 5 by banseok1216

**作成日**: 2025-12-21

`TaskExecutorJobLauncher.launchJobExecution(..)`において、`TaskExecutor`への正常なサブミット後の無条件の`jobRepository.update(jobExecution)`を削除し、`TaskRejectedException`パスでのみ更新を維持することを検討してください。

受け入れられたタスクについては、ジョブスレッドがいずれにせよ`JobExecution`を更新するため、ランチャースレッドからの追加の更新はレースを引き起こし、`OptimisticLockingFailureException`を回避できる可能性があります。

```java
catch (TaskRejectedException e) {
    jobExecution.upgradeStatus(BatchStatus.FAILED);
    if (ExitStatus.UNKNOWN.equals(jobExecution.getExitStatus())) {
        jobExecution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
    }
    // これは維持: この場合、ジョブスレッドは実行されない
    this.jobRepository.update(jobExecution);
}

// ここでの無条件の更新は不要: 受け入れられたタスクの場合、ジョブスレッドがJobExecutionの更新を永続化する
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-21

この課題を報告し、分析や再現コードを提供いただいた皆様、ありがとうございます！

これは [#3637](https://github.com/spring-projects/spring-batch/issues/3637) でのリグレッションのようです。次のパッチバージョン6.0.2で修正を予定します。

### コメント 7 by StefanMuellerCH

**作成日**: 2026-01-05

こちらでも同じ問題が発生していますが、上記の[licenziato](https://github.com/licenziato)さんの修正は効果がありませんでした。`ThreadPoolTaskExecutor`はサイズを1にしても、`TaskExecutorJobLauncher`が更新を呼び出すスレッドとは別のスレッドでジョブ自体を実行するためです。バグを解消するには`SyncTaskExecutor`に切り替える必要がありました:


```
@Bean
public JobOperatorFactoryBean jobOperator(JobRepository jobRepository) {
  var taskExecutor = new SyncTaskExecutor();
  var jobOperatorFactoryBean = new JobOperatorFactoryBean();
  jobOperatorFactoryBean.setJobRepository(jobRepository);
  jobOperatorFactoryBean.setTaskExecutor(taskExecutor);
  return jobOperatorFactoryBean;
}
```

`SyncTaskExecutor`の使用にはかなりの欠点があり、本番環境では使用できないため、修正を待つ必要があります。
