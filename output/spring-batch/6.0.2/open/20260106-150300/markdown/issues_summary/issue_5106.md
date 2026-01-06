*（このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました）*

## 課題概要

`JobOperator.start()`と非同期タスクエグゼキューターを併用してジョブを起動する際、`OptimisticLockingFailureException`が断続的に発生する問題です。

**OptimisticLockingFailureExceptionとは**: Spring Frameworkのデータアクセス層で使用される楽観的ロック機能において、レコードのバージョンが期待値と異なる場合にスローされる例外です。通常、複数のトランザクションが同じレコードを同時に更新しようとした際に発生します。

### 問題の状況

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam minClassWidth 150

participant "アプリケーション" as App
participant "JobOperator" as JO
participant "TaskExecutorJobLauncher" as Launcher
participant "非同期スレッド" as Async
database "BATCH_JOB_EXECUTION" as DB

App -> JO: start()
JO -> Launcher: launchJobExecution()
Launcher -> DB: ジョブインスタンス作成開始

note over Launcher, Async: 競合状態発生

Launcher -> Async: 非同期タスク起動
Async -> DB: updateJobExecution() 呼び出し
note right of Async: レコードが未登録なので\nOptimisticLockingFailureException発生

Launcher -> DB: ジョブインスタンス登録完了
note over Launcher: タイミングにより成功/失敗が決まる
@enduml
```

### 発生パターン

| 状況 | レコード登録 | 非同期スレッド起動 | 結果 |
|------|------------|-----------------|------|
| 正常ケース | 先に完了 | 後に実行 | ✓ 成功 |
| 異常ケース | 実行中 | 先に実行 | ✗ OptimisticLockingFailureException |

**影響範囲**:
- Spring Batch 6.0.0以降
- Spring Boot 4.0.0以降
- 非同期タスクエグゼキューター使用時

## 原因

`TaskExecutorJobLauncher.launchJobExecution()`メソッド内での競合状態が根本原因です。

### コード構造の問題点

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 250
}

state "TaskExecutorJobLauncher.launchJobExecution()" as Main {
  state "try節" as Try {
    [*] -> ジョブ実行準備
    ジョブ実行準備 -> 非同期タスク起動: taskExecutor.execute()
  }
  
  state "finally節" as Finally {
    [*] -> updateJobExecution: 必ず実行される
    updateJobExecution: jobRepository.update(jobExecution)
  }
  
  Try --> Finally: 例外発生有無に関わらず
}

state "非同期スレッド" as Async {
  [*] -> ジョブ実行
  ジョブ実行 -> DB更新: updateJobExecution()
  DB更新 : version=0 → version=1
}

note left of Async
  finally節より先に
  DB更新を試みる可能性
end note

note right of Finally
  version=0を期待して更新
  実際はversion=1（既に更新済み）
  → OptimisticLockingFailureException
end note
@enduml
```

### Spring Batch 5.xとの違い

**Spring Batch 5.x**:
- 非同期タスクのスケジュール設定が失敗した場合のみジョブ実行を更新
- `finally`節でのDB更新処理なし

**Spring Batch 6.x**:
- `finally`節で必ずジョブ実行を更新
- 非同期タスク内での更新と競合する可能性

具体的なスタックトレース:
```
org.springframework.dao.OptimisticLockingFailureException: 
  Attempt to update job execution id=1 with wrong version (0), 
  where current version is 1
  at JdbcJobExecutionDao.updateJobExecution()
  at SimpleJobRepository.update()
  at AbstractJob.updateStatus()
  at AbstractJob.execute()
  at TaskExecutorJobLauncher$1.run()
```

### 問題の本質

```plantuml
@startuml
skinparam backgroundColor transparent

:jobOperator.start() 呼び出し;

fork
  :メインスレッド;
  :JobRepository.update()\nversion=0;
fork again
  :非同期ワーカースレッド;
  :JobRepository.update()\nversion=0;
end fork

:楽観的ロック競合;
note right
  両方のスレッドが
  version=0を期待
  →OptimisticLockingFailureException
end note

@enduml
```

## 対応方針

現時点では開発チームからの公式な修正はリリースされていませんが、コミュニティから以下の回避策が提案されています。

### 回避策1: シングルスレッドエグゼキューター使用

`ThreadPoolTaskExecutor`のスレッド数を1に制限することで、競合状態を回避します。

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

**メリット**: 簡単に実装可能
**デメリット**: 並行実行の利点が失われる

### 想定される根本修正アプローチ

```plantuml
@startuml
skinparam backgroundColor transparent

:ジョブ起動要求;

:BATCH_JOB_EXECUTION\nレコード登録完了まで待機;
note right
  確実にレコードが
  作成されてから次へ
end note

:非同期タスク起動 ;

:ジョブ実行;

:DB更新\n（レコード確実に存在）;

:完了;
@enduml
```

### 期待される修正内容

1. **`TaskExecutorJobLauncher`の修正**:
   - `finally`節での無条件更新ロジックを見直し
   - 非同期タスク起動前にジョブ実行レコードの登録を完了
   - Spring Batch 5.xの動作（スケジュール失敗時のみ更新）に戻す

2. **同期ポイントの追加**:
   - ジョブ実行レコードの登録完了を確認してから非同期タスクを起動
   - カウントダウンラッチなどの同期機構の導入

### 影響するコンポーネント

| コンポーネント | 影響内容 |
|--------------|---------|
| `TaskExecutorJobLauncher` | finally節のDB更新ロジック |
| `JobOperator` | 非同期タスクエグゼキューター設定 |
| JDBCベースのJobRepository | 楽観的ロック機構 |
| MongoDBベースのJobRepository | データ整合性制約 |

### 関連する課題とディスカッション

- [Discussion #5121](https://github.com/spring-projects/spring-batch/discussions/5121) - 関連する問題の議論
- 最小再現環境: https://github.com/phactum-mnestler/spring-batch-reproducer
- MongoDB環境での再現: https://github.com/kizombaDev/spring-batch-async-bug-reproducer

**現在のステータス**: Spring Batch 6.0.1でも未解決。開発チームの修正待ちの状態です。
