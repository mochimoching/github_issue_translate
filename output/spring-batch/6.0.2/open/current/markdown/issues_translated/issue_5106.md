# jobOperator.start()とasyncTaskExecutorを使用したジョブ起動時に発生する間欠的なOptimisticLockingFailureException

**課題番号**: #5106

**状態**: open | **作成者**: scottgongsg | **作成日**: 2025-11-25

**ラベル**: type: bug, in: core, has: votes, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5106

## 内容

**バグの説明**
`jobOperator.start()`と非同期タスクエグゼキューターを使用してジョブを起動する際に、`OptimisticLockingFailureException`が時々発生する問題があります。

**環境**
Spring Boot 4.0.0
Spring Batch 6.0.0
Java 21

**再現手順**
1) Spring InitializrでSpring BatchとSpring Data Jpaを選択し、新しいSpring Bootプロジェクトを作成します
2) 設定クラスを作成し、`@EnableBatchProcessing`と`@EnableJdbcJobRepository`アノテーションを付与します
3) シンプルなジョブを実装し、非同期タスクエグゼキューターを使用して`JobOperator`を作成します
4) `jobOperator.start()`を使用してジョブを起動します
5) `JdbcJobExecutionDao.updateJobExecution()`の処理中に、間欠的に`OptimisticLockingFailureException`が発生します
6) デバッグした結果、`BATCH_JOB_EXECUTION`テーブルにジョブインスタンスが登録される前に、`TaskExecutorJobLauncher`クラスで非同期タスクエグゼキューターによって新しいスレッドでジョブ実行が開始されることがあり、テーブルからジョブ実行レコードが見つからないため`OptimisticLockingFailureException`が発生することがわかりました。

**期待される動作**
ジョブは常にエラーなく正常に実行されるべきです。


## コメント

### コメント 1 by ahoehma

**作成日**: 2025-12-01

私が遭遇している問題とは完全に同じではありませんが、ここでのフィードバックも注視しています。

（この議論を始めました: https://github.com/spring-projects/spring-batch/discussions/5121）

### コメント 2 by phactum-mnestler

**作成日**: 2025-12-17

私たちも説明されている同じ問題に遭遇しています。最小限の再現環境を作成しました: https://github.com/phactum-mnestler/spring-batch-reproducer
スタックトレースから判断すると、この問題は`TaskExecutorJobLauncher`の非同期ランナブルと、それを囲む`finally`節の間の競合状態のようです：
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
この`finally`節はSpring Batch 5.xには存在せず、5.xでは`Runnable`のスケジュール設定ができなかった場合にのみジョブ実行を更新していました。

新しくリリースされた6.0.1バージョンでもこの問題は解決されていません

### コメント 3 by licenziato

**作成日**: 2025-12-17

私も同じ問題と根本原因を確認しました。回避策として、`JobOperator`で使用される`ThreadPoolTaskExecutor`をシングルスレッドエグゼキューターに設定することで競合状態が解消されました。適切な修正を待っています：

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

私たちも現在、Spring Batch 6.0.1、MongoDB、および`ThreadPoolTaskExecutor`を使用した環境で同じ問題に直面しています。

`jobOperator.start(job, new JobParameters())`を使用してジョブを起動すると、すぐに`DataIntegrityViolationException`が発生します。

この問題は、`org.springframework.batch.core.launch.support.TaskExecutorJobLauncher#launchJobExecution`メソッドのfinally節内で呼び出される`this.jobRepository.update(jobExecution);`によって引き起こされていることを確認しました。

MongoDBを使用した再現環境を作成しました: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

### コメント 5 by banseok1216

**作成日**: 2025-12-21

`TaskExecutorJobLauncher.launchJobExecution(..)`メソッドにおいて、タスクエグゼキューターへの送信が成功した後の無条件の`jobRepository.update(jobExecution)`を削除し、`TaskRejectedException`パスでのみ更新を維持することを検討してください。

受け入れられたタスクについては、ジョブスレッドが`JobExecution`を更新するため、ランチャースレッドからの追加更新は競合を引き起こし、`OptimisticLockingFailureException`をトリガーする可能性があります。

```java
catch (TaskRejectedException e) {
    jobExecution.upgradeStatus(BatchStatus.FAILED);
    if (ExitStatus.UNKNOWN.equals(jobExecution.getExitStatus())) {
        jobExecution.setExitStatus(ExitStatus.FAILED.addExitDescription(e));
    }
    // これは維持: この場合、ジョブスレッドは実行されません
    this.jobRepository.update(jobExecution);
}

// ここでは無条件更新なし: 受け入れられたタスクの場合、ジョブスレッドがJobExecution更新を永続化します
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-21

この問題の報告と分析・再現環境の提供をありがとうございます！

これは [#3637](https://github.com/spring-projects/spring-batch/issues/3637) のリグレッションのようです。次のパッチバージョン6.0.2で修正を予定しています。

### コメント 7 by StefanMuellerCH

**作成日**: 2026-01-05

私たちも同じ問題に遭遇しましたが、上記の [licenziato](https://github.com/licenziato) による修正は効果がありませんでした。サイズ1の`ThreadPoolTaskExecutor`でも、`TaskExecutorJobLauncher`が更新を呼び出す際に、ジョブ自体が別のスレッドで実行されるためです。このバグを解決するには、`SyncTaskExecutor`に切り替える必要がありました：


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

`SyncTaskExecutor`の使用にはかなりのデメリットがあり、本番環境では使用できないため、修正を待つ必要があります。
