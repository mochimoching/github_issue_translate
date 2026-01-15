*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

# asyncTaskExecutorを使用したjobOperator.start()でジョブ起動時に断続的なOptimisticLockingFailureExceptionが発生する

**Issue番号**: [#5106](https://github.com/spring-projects/spring-batch/issues/5106)

**状態**: open | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

## 内容

**バグの説明**
asyncTaskExecutorを使用して`jobOperator.start()`でジョブを起動する際、断続的に`OptimisticLockingFailureException`が発生します。

**環境**
Spring Boot 4.0.0
Spring Batch 6.0.0
Java 21

**再現手順**
1) InitializrでSpring BatchとSpring Data Jpaを選択して新しいSpring Bootプロジェクトを作成
2) 設定クラスを作成し、`@EnableBatchProcessing`と`@EnableJdbcJobRepository`アノテーションを付与
3) シンプルなジョブを実装し、asyncTaskExecutorを使用して`jobOperator`を作成
4) `jobOperator.start()`を使用してジョブを起動
5) `JdbcJobExecutionDao.updateJobExecution()`で断続的に`OptimisticLockingFailureException`が発生
6) デバッグの結果、ジョブインスタンスが`BATCH_JOB_EXECUTION`テーブルに挿入されていない場合があることが判明しました。しかし、ジョブ実行はasyncTaskExecutorを使用して新しいスレッドで起動されており（`TaskExecutorJobLauncher`クラス内）、テーブル内のジョブ実行レコードが見つからず、`OptimisticLockingFailureException`が発生します。

**期待される動作**
ジョブは常に問題なく実行されるべきです。


## コメント

### コメント 1 by ahoehma

**作成日**: 2025-12-01

私が直面している問題とは正確には一致しませんが :-)、こちらのフィードバックも注視していきます。

（このディスカッションを開始しました: https://github.com/spring-projects/spring-batch/discussions/5121）

### コメント 2 by phactum-mnestler

**作成日**: 2025-12-17

説明されているものと同じ問題が発生しています。最小限の再現コードをこちらに作成しました: https://github.com/phactum-mnestler/spring-batch-reproducer
スタックトレースから判断すると、この問題は`TaskExecutorJobLauncher`の非同期Runnableと、それを囲む`finally`句の間の競合状態が原因のようです:
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
この`finally`句はSpring Batch 5.xには存在せず、`Runnable`がスケジュールできなかった場合にのみジョブ実行を更新していました。

新しくリリースされた6.0.1バージョンでもこの問題が継続していることを確認しています。

### コメント 3 by licenziato

**作成日**: 2025-12-17

同じ問題と同じ根本原因を確認しました。回避策として、`JobOperator`で使用する`ThreadPoolTaskExecutor`をシングルスレッドエグゼキューターに設定することで競合状態が解消されました。正式な修正を待っています:

```java
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

残念ながら、Spring Batch 6.0.1、MongoDB、および`ThreadPoolTaskExecutor`を使用して、現在同じ問題に直面しています。

`jobOperator.start(job, new JobParameters())`を使用してジョブを開始すると、すぐに`DataIntegrityViolationException`が発生します。

`org.springframework.batch.core.launch.support.TaskExecutorJobLauncher#launchJobExecution`メソッドのfinallyブロックで`this.jobRepository.update(jobExecution);`を呼び出していることが問題の原因であることを確認できます。

MongoDBを使用した再現コードをこちらに作成しました: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

### コメント 5 by banseok1216

**作成日**: 2025-12-21

`TaskExecutorJobLauncher.launchJobExecution(..)`において、`TaskExecutor`へのタスク送信が成功した後の無条件の`jobRepository.update(jobExecution)`呼び出しを削除し、`TaskRejectedException`パスでのみ更新を維持することを検討してください。

受け入れられたタスクの場合、ジョブスレッドがいずれにせよ`JobExecution`を更新します。ランチャースレッドからの追加の更新は競合を引き起こし、`OptimisticLockingFailureException`を発生させる可能性があります。

```java
catch (TaskRejectedException e) {
    jobExecution.upgradeStatus(BatchStatus.FAILED);
    if (ExitStatus.UNKNOWN.equals(jobExecution.getExitStatus())) {
        jobExecution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
    }
    // これを維持: ジョブスレッドはこのケースでは実行されないため
    this.jobRepository.update(jobExecution);
}

// ここでの無条件の更新はなし: 受け入れられたタスクの場合、ジョブスレッドがJobExecutionの更新を永続化する
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-21

この問題の報告と、分析/再現コードの提供ありがとうございます！

これは[#3637](https://github.com/spring-projects/spring-batch/issues/3637)でのリグレッションのようです。次のパッチバージョン6.0.2で修正を予定します。

### コメント 7 by StefanMuellerCH

**作成日**: 2026-01-05

同じ問題が発生していますが、上記の[licenziato](https://github.com/licenziato)さんの修正は役に立ちませんでした。サイズ1の`ThreadPoolTaskExecutor`でも、`TaskExecutorJobLauncher`が更新を呼び出すのとは別のスレッドでジョブを実行するためです。バグを解決するには`SyncTaskExecutor`に切り替える必要がありました:

```java
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
