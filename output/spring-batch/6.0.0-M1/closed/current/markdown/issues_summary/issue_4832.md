*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

`JobOperator`を`JobLauncher`の拡張（サブインターフェース）として再設計し、2つのBeanを1つに統合してバッチ設定を簡素化する提案です。

**JobLauncherとは**: ジョブを起動するための基本的なAPIです。`run(Job, JobParameters)`メソッドでジョブを実行します。

**JobOperatorとは**: ジョブの起動に加えて、停止・再起動などの操作機能を提供する高レベルAPIです。

### v5.2の構造

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

interface "JobLauncher" {
  + run(Job, JobParameters): JobExecution
}

interface "JobOperator" {
  + start(String, Properties): Long
  + restart(Long): Long
  + stop(Long): Boolean
}

class "SimpleJobLauncher" {
  - taskExecutor
  + run()
}

class "SimpleJobOperator" {
  - jobLauncher
  - jobRepository
  + start()
  + restart()
  + stop()
}

SimpleJobLauncher ..|> JobLauncher
SimpleJobOperator ..|> JobOperator
SimpleJobOperator --> JobLauncher: 内部で使用

note bottom of SimpleJobOperator #FF6B6B
  問題：Operatorの start() は
  内部で Launcher の run() を呼んでいる
  
  OperatorはLauncherの拡張版なのに
  継承関係がない
end note

@enduml
```

### 実装の重複

```java
// SimpleJobOperator.start() の内部実装
public Long start(String jobName, Properties parameters) {
    // 1. ジョブを取得
    Job job = jobRegistry.getJob(jobName);
    // 2. パラメータを変換
    JobParameters jobParameters = converter.getJobParameters(properties);
    // 3. JobLauncherを呼び出し ← ここで依存
    JobExecution execution = jobLauncher.run(job, jobParameters);
    return execution.getId();
}
```

## 原因

v5.2では、`JobLauncher`と`JobOperator`が独立したインターフェースとして設計されていました。しかし、実際には：

1. **機能的な重複**: `JobOperator`の`start()`メソッドは、内部で`JobLauncher.run()`を呼び出している
2. **拡張の関係**: `JobOperator`は`JobLauncher`に停止/再起動機能を追加したもの
3. **設定の複雑化**: ユーザーは両方のBeanを設定する必要がある

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

package "ユーザー設定 (v5.2)" {
  component [JobLauncher Bean] as Launcher
  component [JobOperator Bean] as Operator
  component [JobRepository Bean] as Repo
  component [JobRegistry Bean] as Registry
  
  Operator --> Launcher
  Operator --> Repo
  Operator --> Registry
  
  note right of Launcher #FF6B6B
    問題：
    ・2つのBean設定が必要
    ・Operator → Launcherの依存
    ・概念的には1つで良いはず
  end note
}

@enduml
```

## 対応方針

**コミット**: [fc4a665](https://github.com/spring-projects/spring-batch/commit/fc4a66516ac7048e610065628793c62dcc646db5)

`JobOperator`を`JobLauncher`の拡張として設計し直し、継承関係を明確化しました。

### v6.0の改善された構造

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

interface "JobLauncher" {
  .. 基本的なジョブ起動 ..
  + run(Job, JobParameters): JobExecution
}

interface "JobOperator" {
  .. 追加のジョブ操作 ..
  + startNextInstance(Job): JobExecution
  + restart(JobExecution): JobExecution
  + stop(JobExecution): Boolean
}

JobOperator -up-|> JobLauncher

note on link #90EE90
  継承関係
  
  JobOperator =
    ジョブ起動(Launcher) +
    停止・再起動機能
end note

class "TaskExecutorJobOperator" {
  - taskExecutor
  - jobRepository
  + run() ← JobLauncherから継承
  + startNextInstance()
  + restart()
  + stop()
}

TaskExecutorJobOperator ..|> JobOperator
TaskExecutorJobOperator ..|> JobLauncher

@enduml
```

### 設定の簡素化

#### v5.2（変更前）

```java
@Configuration
@EnableBatchProcessing
public class BatchConfig {
    
    @Bean
    public JobLauncher jobLauncher(JobRepository jobRepository) {
        SimpleJobLauncher launcher = new SimpleJobLauncher();
        launcher.setJobRepository(jobRepository);
        launcher.setTaskExecutor(new SyncTaskExecutor());
        return launcher;
    }
    
    @Bean
    public JobOperator jobOperator(JobRepository jobRepository,
                                   JobRegistry jobRegistry,
                                   JobLauncher jobLauncher) {
        SimpleJobOperator operator = new SimpleJobOperator();
        operator.setJobRepository(jobRepository);
        operator.setJobRegistry(jobRegistry);
        operator.setJobLauncher(jobLauncher); // Launcherへの依存
        return operator;
    }
}
```

#### v6.0（変更後）

```java
@Configuration
@EnableBatchProcessing
public class BatchConfig {
    
    @Bean
    public JobOperator jobOperator(JobRepository jobRepository) {
        TaskExecutorJobOperator operator = new TaskExecutorJobOperator();
        operator.setJobRepository(jobRepository);
        operator.setTaskExecutor(new SyncTaskExecutor());
        return operator;
        // JobOperatorはJobLauncherを継承しているので、
        // これ1つでジョブ起動も操作も可能
    }
    
    // JobLauncher Beanの定義は不要！
}
```

### 使用シーンの整理

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

actor "開発者" as Dev

== シンプルなジョブ起動 ==
Dev -> "JobOperator": run(job, parameters)
note right
  JobLauncherとしても使える
  基本的な起動機能
end note

== 次のインスタンスを起動 ==
Dev -> "JobOperator": startNextInstance(job)
note right
  Operator固有の機能
  前回の続きを自動起動
end note

== ジョブの停止 ==
Dev -> "JobOperator": stop(jobExecution)
note right
  Operator固有の機能
  実行中のジョブを停止
end note

== ジョブの再起動 ==
Dev -> "JobOperator": restart(jobExecution)
note right
  Operator固有の機能
  失敗したジョブを再実行
end note

@enduml
```

### APIの比較

| 機能 | v5.2 | v6.0 |
|------|------|------|
| 必要なBean数 | 2個（Launcher + Operator） | 1個（Operatorのみ） |
| ジョブ起動 | `JobLauncher.run()` | `JobOperator.run()` ← 継承 |
| ジョブ停止 | `JobOperator.stop()` | `JobOperator.stop()` |
| ジョブ再起動 | `JobOperator.restart()` | `JobOperator.restart()` |
| 設定の複雑さ | 高い | 低い |

### 型の互換性

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

package "v6.0の型階層" {
  interface "JobLauncher" as Launcher
  interface "JobOperator" as Operator
  class "TaskExecutorJobOperator" as Impl
  
  Operator -up-|> Launcher
  Impl .up.|> Operator
  Impl .up.|> Launcher
  
  note right of Impl #90EE90
    1つのインスタンスで
    両方の型として利用可能
    
    // どちらの型でも注入可能
    @Autowired
    JobLauncher launcher;
    
    @Autowired
    JobOperator operator;
  end note
}

@enduml
```

### メリット

1. **設定の簡素化**: Bean定義が1つで済む
2. **概念の明確化**: OperatorがLauncherの拡張であることが明示的
3. **依存関係の削減**: Operator内でLauncherへの依存が不要
4. **一貫性の向上**: `JobRepository` extends `JobExplorer`と同じパターン（課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824)）

### 関連する変更

- 課題 [#4834](https://github.com/spring-projects/spring-batch/issues/4834): `SimpleJobOperator` → `TaskExecutorJobOperator`への名称変更
- 課題 [#4833](https://github.com/spring-projects/spring-batch/issues/4833): `JobOperator`の範囲をジョブ操作のみに限定

この再設計により、Spring Batchのコアアーキテクチャがよりシンプルかつ直感的になりました。
