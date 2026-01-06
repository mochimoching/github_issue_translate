*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5138: パーティションステップの実行情報が永続化されない

## 課題概要

Spring Batch 6.0.0以降、パーティションステップを使用する際に、`PartitionStep`のワーカーステップ実行情報（`StepExecution`）が`JobRepository`に正しく永続化されず、データベースに保存されない問題です。

### 用語解説

- **パーティションステップ**: 大量データを複数の小さな塊（パーティション）に分割して並列処理するステップ
- **マネージャーステップ**: パーティションを作成・管理する親ステップ
- **ワーカーステップ**: 各パーティションを実際に処理する子ステップ
- **StepExecution**: ステップの実行情報（開始時刻、終了時刻、ステータス、実行コンテキストなど）を保持するオブジェクト
- **JobRepository**: ジョブとステップの実行情報をデータベースに保存・取得するコンポーネント
- **ExecutionContext**: ステップやジョブの実行中に状態を保持するためのKey-Valueストア

### 問題のシナリオ

以下のような構成で問題が発生します：

```java
@Configuration
@EnableBatchProcessing
public class JobConfiguration {
    
    @Bean
    public Job partitionJob(JobRepository jobRepository, Step managerStep) {
        return new JobBuilder("partitionJob", jobRepository)
                .start(managerStep)
                .build();
    }
    
    @Bean
    public Step managerStep(JobRepository jobRepository,
                           Partitioner partitioner,
                           Step workerStep,
                           TaskExecutor taskExecutor) {
        return new StepBuilder("managerStep", jobRepository)
                .partitioner("workerStep", partitioner)
                .step(workerStep)
                .gridSize(10)  // 10個のパーティション
                .taskExecutor(taskExecutor)
                .build();
    }
    
    @Bean
    public Step workerStep(JobRepository jobRepository,
                          PlatformTransactionManager transactionManager) {
        return new StepBuilder("workerStep", jobRepository)
                .<String, String>chunk(100, transactionManager)
                .reader(itemReader())
                .writer(itemWriter())
                .build();
    }
}
```

### 実行時の動作

```
【期待される動作】
ジョブ実行
 └─ managerStep開始
     ├─ workerStep#0実行 → データベースに永続化 ✅
     ├─ workerStep#1実行 → データベースに永続化 ✅
     ├─ workerStep#2実行 → データベースに永続化 ✅
     ...
     └─ workerStep#9実行 → データベースに永続化 ✅
     
データベースクエリ:
SELECT * FROM BATCH_STEP_EXECUTION WHERE STEP_NAME LIKE 'workerStep:%';
→ 10件のレコードが取得できる

【実際の動作（バグ）】
ジョブ実行
 └─ managerStep開始
     ├─ workerStep#0実行 → データベースに永続化されない ❌
     ├─ workerStep#1実行 → データベースに永続化されない ❌
     ├─ workerStep#2実行 → データベースに永続化されない ❌
     ...
     └─ workerStep#9実行 → データベースに永続化されない ❌
     
データベースクエリ:
SELECT * FROM BATCH_STEP_EXECUTION WHERE STEP_NAME LIKE 'workerStep:%';
→ 0件（レコードが存在しない）❌

マネージャーステップのExecutionContextには保存される:
managerStepExecution.getExecutionContext()
  → workerステップの実行結果は保持されている
  → しかしデータベースには保存されていない
```

### 影響

1. **ステップ実行履歴が失われる**: ワーカーステップの実行情報がデータベースに記録されないため、以下の情報が永続化されない
   - 各パーティションの処理開始・終了時刻
   - 読み込み件数、書き込み件数、スキップ件数
   - エラー情報
   - ExecutionContextに保存した状態

2. **リスタート時の問題**: ジョブが失敗してリスタートする場合、どのパーティションまで完了したか分からない

3. **監視・分析が困難**: どのパーティションの処理に時間がかかったか、どこで失敗したかなどの分析ができない

## 原因

Spring Batch 6.0.0で`PartitionStep`の実装が変更された際、ワーカーステップの`StepExecution`を`JobRepository`に保存する処理が欠落していました。

### 詳細な原因

#### Spring Batch 5までの動作

```java
// PartitionStep（Spring Batch 5）
public class PartitionStep extends AbstractStep {
    
    @Override
    protected void doExecute(StepExecution stepExecution) {
        // パーティション作成
        Map<String, ExecutionContext> partitions = 
            partitionHandler.partition(gridSize);
        
        // 各パーティションを実行
        for (Entry<String, ExecutionContext> entry : partitions.entrySet()) {
            String partitionName = entry.getKey();
            ExecutionContext context = entry.getValue();
            
            // ワーカーステップ実行情報を作成
            StepExecution workerStepExecution = 
                stepExecution.createStepExecution(partitionName);
            workerStepExecution.setExecutionContext(context);
            
            // ✅ データベースに保存
            jobRepository.add(workerStepExecution);
            
            // ワーカーステップ実行
            step.execute(workerStepExecution);
            
            // ✅ 実行結果を更新
            jobRepository.update(workerStepExecution);
        }
    }
}
```

#### Spring Batch 6での変更（バグ）

```java
// PartitionStep（Spring Batch 6.0.0）
public class PartitionStep extends AbstractStep {
    
    @Override
    protected void doExecute(StepExecution stepExecution) {
        // パーティション作成
        Map<String, ExecutionContext> partitions = 
            partitionHandler.partition(gridSize);
        
        // 各パーティションを実行
        for (Entry<String, ExecutionContext> entry : partitions.entrySet()) {
            String partitionName = entry.getKey();
            ExecutionContext context = entry.getValue();
            
            // ワーカーステップ実行情報を作成
            StepExecution workerStepExecution = 
                stepExecution.createStepExecution(partitionName);
            workerStepExecution.setExecutionContext(context);
            
            // ❌ データベース保存の処理が欠落
            // jobRepository.add(workerStepExecution); ← この行がない
            
            // ワーカーステップ実行
            step.execute(workerStepExecution);
            
            // ❌ 実行結果の更新も欠落
            // jobRepository.update(workerStepExecution); ← この行もない
        }
        
        // マネージャーステップのExecutionContextには保存
        stepExecution.getExecutionContext()
            .put("partition.results", workerStepExecutions);
    }
}
```

### 問題の整理

```
【Spring Batch 5】
ワーカーStepExecution作成
  ↓
jobRepository.add() ✅ データベースに保存
  ↓
ワーカーステップ実行
  ↓
jobRepository.update() ✅ 実行結果を更新
  ↓
マネージャーのExecutionContextにも保存

【Spring Batch 6.0.0（バグ）】
ワーカーStepExecution作成
  ↓
❌ jobRepository.add()がない
  ↓
ワーカーステップ実行
  ↓
❌ jobRepository.update()もない
  ↓
マネージャーのExecutionContextにのみ保存
```

## 対応方針

`PartitionStep`の実装を修正し、ワーカーステップの`StepExecution`を`JobRepository`に正しく永続化するように変更されました。

### 修正内容

[コミット 8a44b5e](https://github.com/spring-projects/spring-batch/commit/8a44b5e949b8c8f85b8f56f5c11de29fe6fca83a)

```java
// PartitionStep（修正後）
public class PartitionStep extends AbstractStep {
    
    @Override
    protected void doExecute(StepExecution stepExecution) {
        // パーティション作成
        Map<String, ExecutionContext> partitions = 
            partitionHandler.partition(gridSize);
        
        // 各パーティションを実行
        for (Entry<String, ExecutionContext> entry : partitions.entrySet()) {
            String partitionName = entry.getKey();
            ExecutionContext context = entry.getValue();
            
            // ワーカーステップ実行情報を作成
            StepExecution workerStepExecution = 
                stepExecution.createStepExecution(partitionName);
            workerStepExecution.setExecutionContext(context);
            
            // ✅ 修正: データベースに保存
            jobRepository.add(workerStepExecution);
            
            // ワーカーステップ実行
            step.execute(workerStepExecution);
            
            // ✅ 修正: 実行結果を更新
            jobRepository.update(workerStepExecution);
        }
        
        // マネージャーステップのExecutionContextにも保存
        stepExecution.getExecutionContext()
            .put("partition.results", workerStepExecutions);
    }
}
```

### 修正後の動作

```
【修正後】
ジョブ実行
 └─ managerStep開始
     ├─ workerStep#0
     │   ├─ StepExecution作成
     │   ├─ jobRepository.add() ✅ データベースに保存
     │   ├─ ステップ実行
     │   └─ jobRepository.update() ✅ 実行結果を更新
     │
     ├─ workerStep#1
     │   ├─ StepExecution作成
     │   ├─ jobRepository.add() ✅
     │   ├─ ステップ実行
     │   └─ jobRepository.update() ✅
     ...
     └─ workerStep#9
         ├─ StepExecution作成
         ├─ jobRepository.add() ✅
         ├─ ステップ実行
         └─ jobRepository.update() ✅

データベースクエリ:
SELECT * FROM BATCH_STEP_EXECUTION WHERE STEP_NAME LIKE 'workerStep:%';
→ 10件のレコードが正しく取得できる ✅
```

### 永続化される情報

修正後、以下の情報がデータベースに正しく保存されるようになります：

| カラム名 | 内容 | 例 |
|---------|------|-----|
| STEP_EXECUTION_ID | ステップ実行ID | 2, 3, 4, ... |
| STEP_NAME | ステップ名 | workerStep:partition0, workerStep:partition1, ... |
| JOB_EXECUTION_ID | ジョブ実行ID | 1 |
| START_TIME | 開始時刻 | 2024-01-05 10:00:00 |
| END_TIME | 終了時刻 | 2024-01-05 10:05:23 |
| STATUS | ステータス | COMPLETED, FAILED, etc. |
| READ_COUNT | 読み込み件数 | 1000 |
| WRITE_COUNT | 書き込み件数 | 1000 |
| COMMIT_COUNT | コミット回数 | 10 |
| ROLLBACK_COUNT | ロールバック回数 | 0 |
| FILTER_COUNT | フィルタ件数 | 0 |
| READ_SKIP_COUNT | 読み込みスキップ件数 | 0 |
| WRITE_SKIP_COUNT | 書き込みスキップ件数 | 5 |

### リスタート時の動作

```java
// ジョブ再実行時
JobExecution jobExecution = jobLauncher.run(job, jobParameters);

// ✅ 前回の実行状態を取得できる
Collection<StepExecution> stepExecutions = 
    jobExecution.getStepExecutions();

for (StepExecution stepExecution : stepExecutions) {
    if (stepExecution.getStepName().startsWith("workerStep:")) {
        // 各パーティションの実行状態を確認できる
        System.out.println("Partition: " + stepExecution.getStepName());
        System.out.println("Status: " + stepExecution.getStatus());
        System.out.println("Read count: " + stepExecution.getReadCount());
    }
}
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `PartitionStep` - パーティションステップの実装
  - `PartitionHandler` - パーティションの実行を管理
  - `StepExecution` - ステップ実行情報
  - `JobRepository` - ジョブ・ステップ情報の永続化
  - `ExecutionContext` - 実行コンテキスト
- **影響する機能**:
  - パーティションステップの実行履歴
  - ジョブのリスタート機能
  - ステップ実行の監視・分析
- **データベーステーブル**:
  - `BATCH_STEP_EXECUTION` - ステップ実行情報
  - `BATCH_STEP_EXECUTION_CONTEXT` - ステップ実行コンテキスト
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5138
