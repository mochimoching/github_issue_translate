*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

同じステップを複数のジョブインスタンスで再利用する際、前回のジョブで使用された`ChunkTracker`がリセットされず、次のジョブが正しく動作しない問題を修正しました。

**関連Issue**: この問題は [#5099](https://github.com/spring-projects/spring-batch/issues/5099)（ChunkTrackerのスレッドローカル化）とは異なります。[#5099](https://github.com/spring-projects/spring-batch/issues/5099) は同一ジョブ内のパーティション並行処理の問題でしたが、本件は異なるジョブインスタンス間の問題です。

### 問題の発生条件

```java
// 同じステップを複数ジョブで使用
@Configuration
public class JobConfig {
    @Bean
    public Step sharedStep(JobRepository jobRepository) {
        return new StepBuilder("sharedStep", jobRepository)
            .chunk(10)
            .reader(...)
            .processor(...)
            .writer(...)
            .build();
    }
    
    @Bean
    public Job job1(JobRepository jobRepository, Step sharedStep) {
        return new JobBuilder("job1", jobRepository)
            .start(sharedStep)
            .build();
    }
    
    @Bean
    public Job job2(JobRepository jobRepository, Step sharedStep) {
        return new JobBuilder("job2", jobRepository)
            .start(sharedStep)
            .build();
    }
}

// 実行
jobLauncher.run(job1, params1);  // 正常終了
jobLauncher.run(job2, params2);  // ❌ job1のChunkTrackerが残っているため異常動作
```

## 原因

`ChunkTracker`がステップ実行完了後にリセットされず、次のジョブで再利用されていました。

### 問題の構造

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

participant "Job1" as J1
participant "sharedStep" as SS
participant "ChunkTracker" as CT

J1 -> SS: 実行
activate SS
SS -> CT: チャンク処理
note right
  ChunkTracker状態：
  - currentChunk = 5
  - itemsProcessed = 50
end note
SS --> J1: 完了
deactivate SS
note right #FFB6C1
  問題：ChunkTrackerが
  リセットされない
end note

participant "Job2" as J2

J2 -> SS: 実行
activate SS
SS -> CT: チャンク処理
note right #FF6B6B
  ChunkTracker状態（誤）：
  - currentChunk = 5（前回の値）
  - itemsProcessed = 50（前回の値）
  
  正しくは0から開始すべき
end note
SS --> J2: 異常動作
deactivate SS

@enduml
```

### 状態遷移図

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam state {
  MinimumWidth 400
}

state "未実行" as IDLE
state "Job1実行中" as JOB1
state "Job1完了" as JOB1_DONE
state "Job2実行中" as JOB2

[*] --> IDLE
IDLE --> JOB1 : job1.start(sharedStep)
JOB1 : ChunkTracker初期化
JOB1 : chunks = [1, 2, 3, 4, 5]

JOB1 --> JOB1_DONE : 完了
JOB1_DONE : ChunkTracker状態維持（問題）
JOB1_DONE : chunks = [1, 2, 3, 4, 5]
note right #FFB6C1
  リセットされない
end note

JOB1_DONE --> JOB2 : job2.start(sharedStep)
JOB2 : ChunkTracker引き継ぎ（誤）
JOB2 : chunks = [1, 2, 3, 4, 5]（前回の値）
note right #FF6B6B
  0から開始すべき
end note

@enduml
```

## 対応方針

**コミット**: [2faf66a](https://github.com/spring-projects/spring-batch/commit/2faf66a0ead5f3e28d165c48862b87fe81fbd03d)

ステップ実行完了後に、`ChunkTracker`をリセットするメソッドを追加しました。

### 修正内容

```java
// v6.0.0（問題のあるコード）
public class FaultTolerantChunkProcessor<I, O> {
    private ThreadLocal<ChunkTracker> chunkTrackers = new ThreadLocal<>();
    
    public void process(StepContribution contribution, Chunk<I> inputs) {
        ChunkTracker tracker = chunkTrackers.get();
        if (tracker == null) {
            tracker = new ChunkTracker();
            chunkTrackers.set(tracker);
        }
        // チャンク処理
    }
    
    // ❌ リセットメソッドなし
}

// v6.0.1（修正後）
public class FaultTolerantChunkProcessor<I, O> {
    private ThreadLocal<ChunkTracker> chunkTrackers = new ThreadLocal<>();
    
    public void process(StepContribution contribution, Chunk<I> inputs) {
        ChunkTracker tracker = chunkTrackers.get();
        if (tracker == null) {
            tracker = new ChunkTracker();
            chunkTrackers.set(tracker);
        }
        // チャンク処理
    }
    
    // ✅ リセットメソッドを追加
    public void reset() {
        chunkTrackers.remove();  // ThreadLocalをクリア
    }
}

// ステップ実行完了時に呼び出し
public class TaskletStep {
    @Override
    protected void doExecute(StepExecution stepExecution) {
        try {
            // ステップ実行
        } finally {
            // ✅ 実行完了後にリセット
            if (chunkProcessor instanceof FaultTolerantChunkProcessor) {
                ((FaultTolerantChunkProcessor) chunkProcessor).reset();
            }
        }
    }
}
```

### 修正後の動作

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam minClassWidth 150

participant "Job1" as J1
participant "sharedStep" as SS
participant "ChunkTracker" as CT

J1 -> SS: 実行
activate SS
SS -> CT: チャンク処理
note right
  ChunkTracker状態：
  - currentChunk = 5
  - itemsProcessed = 50
end note
SS -> CT: reset()
note right #90EE90
  修正：リセット実行
  - currentChunk = 0
  - itemsProcessed = 0
end note
SS --> J1: 完了
deactivate SS

participant "Job2" as J2

J2 -> SS: 実行
activate SS
SS -> CT: チャンク処理
note right #90EE90
  ChunkTracker状態（正）：
  - currentChunk = 0（初期値）
  - itemsProcessed = 0（初期値）
  
  正しく0から開始
end note
SS --> J2: 正常動作
deactivate SS

@enduml
```

### ThreadLocalライフサイクル

| フェーズ | v6.0.0 | v6.0.1 |
|---------|--------|--------|
| ステップ開始 | ThreadLocal生成 | ThreadLocal生成 |
| チャンク処理 | 状態を蓄積 | 状態を蓄積 |
| ステップ完了 | ❌ 状態保持 | ✅ reset()でクリア |
| 次のジョブ開始 | ❌ 古い状態を使用 | ✅ 新しいTrackerを生成 |

### 使用例

```java
// 同じステップを複数ジョブで共有
@Configuration
public class JobConfig {
    @Bean
    public Step importStep(JobRepository jobRepository,
                          PlatformTransactionManager transactionManager) {
        return new StepBuilder("importStep", jobRepository)
            .<String, String>chunk(10, transactionManager)
            .reader(itemReader())
            .processor(itemProcessor())
            .writer(itemWriter())
            .faultTolerant()
            .build();
    }
    
    @Bean
    public Job dailyImportJob(JobRepository jobRepository, Step importStep) {
        return new JobBuilder("dailyImportJob", jobRepository)
            .start(importStep)
            .build();
    }
    
    @Bean
    public Job weeklyImportJob(JobRepository jobRepository, Step importStep) {
        return new JobBuilder("weeklyImportJob", jobRepository)
            .start(importStep)
            .build();
    }
}

// 実行
jobLauncher.run(dailyImportJob, new JobParametersBuilder()
    .addString("date", "2026-01-06")
    .toJobParameters());

// v6.0.1では正常動作
jobLauncher.run(weeklyImportJob, new JobParametersBuilder()
    .addString("date", "2026-01-06")
    .toJobParameters());
```

### メリット

| 項目 | v6.0.0 | v6.0.1 |
|------|--------|--------|
| ステップ再利用 | 異常動作 | 正常動作 |
| ChunkTrackerのリセット | なし | あり |
| メモリリーク | 可能性あり | なし |
| 予測可能性 | 低い | 高い |

この修正により、同じステップを複数のジョブで安全に再利用できるようになりました。
