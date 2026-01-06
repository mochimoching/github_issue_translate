*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5126: ステップ完了後にChunkTrackerがリセットされない

## 課題概要

Spring Batch 6の新しいチャンク処理実装において、ステップが完了しても`ChunkTracker`（チャンク処理の進行状況を追跡するクラス）がリセットされず、同じジョブを再実行した際にチャンクがスキップされてしまい、データが処理されない問題です。

### 用語解説

- **ChunkTracker**: チャンク処理の進行状況（どこまで処理したか、まだアイテムがあるかなど）を追跡するクラス
- **StepExecutionContext**: ステップ実行の状態情報を保存するコンテキスト。処理の途中状態をデータベースに永続化できる
- **RunIdIncrementer**: ジョブパラメータに実行ごとのユニークなIDを追加するクラス。同じジョブを繰り返し実行できるようにする

### 問題のシナリオ

以下のようなジョブで問題が発生します：

```java
@Bean
public Job testJob(JobRepository jobRepository, Step step1) {
    return new JobBuilder("TestJob", jobRepository)
        .incrementer(new RunIdIncrementer())  // 毎回異なるパラメータで実行
        .start(step1)
        .build();
}

@Bean  
public Step step1(JobRepository jobRepository, 
                  PlatformTransactionManager transactionManager) {
    return new StepBuilder("step1", jobRepository)
        .<String, String>chunk(10, transactionManager)
        .reader(itemReader())  // 5件のアイテムを読み込む
        .writer(itemWriter())
        .build();
}
```

```
【実行の流れ】
1回目の実行:
  - パラメータ: {'run.id':'1'}
  - step1が5件のアイテムを処理
  - ChunkTrackerに「処理完了」が記録される
  - ジョブ完了（STATUS=COMPLETED）

2回目の実行:
  - パラメータ: {'run.id':'2'}  （新しいジョブインスタンス）
  - step1開始
  - ChunkTrackerが前回の「処理完了」状態のまま
  - アイテムが処理されない（スキップされる）
  - Writer が空のリストで呼ばれる: items.size = 0
  - ジョブ完了（STATUS=COMPLETED）
```

### 実際のログ

```
【1回目の実行】
2025-11-28T14:16:44.166  INFO  : Started BatchApplication
2025-11-28T14:16:44.367  INFO  : Job: [TestJob] launched with parameters: [{'run.id':'1'}]
2025-11-28T14:16:44.444  INFO  : Executing step: [step1]
2025-11-28T14:16:44.500  INFO  : Step 1 WRITER method called with items.size = 5
2025-11-28T14:16:44.712  INFO  : Step: [step1] executed in 266ms
2025-11-28T14:16:44.750  INFO  : Job: [TestJob] completed with status: [COMPLETED]

【2回目の実行】
2025-11-28T14:16:45.166  INFO  : Started BatchApplication
2025-11-28T14:16:45.367  INFO  : Job: [TestJob] launched with parameters: [{'run.id':'2'}]
2025-11-28T14:16:45.444  INFO  : Executing step: [step1]
2025-11-28T14:16:45.644  INFO  : Step 1 WRITER method called with items.size = 0  ← ❌ アイテムが0件
2025-11-28T14:16:45.712  INFO  : Step: [step1] executed in 266ms
2025-11-28T14:16:45.750  INFO  : Job: [TestJob] completed with status: [COMPLETED]
```

2回目の実行で`items.size = 0`となり、アイテムが処理されていません。

## 原因

`ChunkTracker`の状態がステップ実行コンテキストに保存されており、ステップ完了時にクリアされていませんでした。そのため、次回のステップ実行時に前回の状態が復元され、「既に処理済み」と判断されてしまいました。

### 詳細な原因

#### 1. ChunkTrackerのライフサイクル

```java
// ChunkOrientedStep（問題のあった実装イメージ）
public class ChunkOrientedStep {
    private ThreadLocal<ChunkTracker> chunkTracker = 
        ThreadLocal.withInitial(ChunkTracker::new);
    
    @Override
    protected void open(ExecutionContext context) {
        // ステップ開始時: コンテキストから状態を復元
        ChunkTracker tracker = chunkTracker.get();
        tracker.restoreFrom(context);  // 前回の状態を読み込む
    }
    
    protected void doExecute(StepExecution execution) {
        // チャンク処理
        while (chunkTracker.get().hasMoreItems()) {
            // アイテムを処理...
        }
        
        // 処理完了時
        chunkTracker.get().noMoreItems();  // 「完了」マーク
        
        // ❌ ここで状態がコンテキストに保存される
        execution.getExecutionContext().put("chunkTracker", chunkTracker.get());
    }
    
    @Override
    protected void close(ExecutionContext context) {
        // ❌ 問題: ChunkTrackerの状態がクリアされない
        // コンテキストには「完了」状態が残ったまま
    }
}
```

#### 2. 問題の流れ

```
【1回目の実行】
open(context)
  → context は空（新規実行）
  → chunkTracker.moreItems = true

doExecute()
  → 5件のアイテムを処理
  → chunkTracker.noMoreItems() 呼び出し
  → chunkTracker.moreItems = false

close(context)
  → context に chunkTracker の状態を保存
  → context["chunkTracker.moreItems"] = false
  ❌ ここでクリアすべきだった

【2回目の実行（新しいジョブインスタンス）】
open(context)
  → context から前回の状態を復元してしまう
  → chunkTracker.moreItems = false  ← ❌ 前回の「完了」状態

doExecute()
  → while (chunkTracker.hasMoreItems())  ← false
  → ループに入らない
  → アイテムが処理されない
```

#### 3. 本来の意図

`ChunkTracker`の永続化は、ステップが失敗した際の**再実行（リスタート）**のためのものでした：

```
【意図されたシナリオ】
1. ステップ実行開始（100件のアイテム）
2. 50件処理したところで失敗
   → ChunkTrackerに「50件まで処理済み」を保存
3. リスタート
   → ChunkTrackerから「50件まで処理済み」を復元
   → 51件目から処理を再開 ✅
```

しかし、ステップが**正常に完了**した場合は、次回の実行時にクリアすべきでした。

## 対応方針

ステップの`close()`メソッドで、`ChunkTracker`の状態を`StepExecutionContext`から削除するように修正されました。

### 修正内容

[コミット ced3ed5](https://github.com/spring-projects/spring-batch/commit/ced3ed50b76f48a0e2a20c89d08fb70a36513e11)

```java
// ChunkOrientedStep（修正後）
public class ChunkOrientedStep {
    private ThreadLocal<ChunkTracker> chunkTracker = 
        ThreadLocal.withInitial(ChunkTracker::new);
    
    @Override
    protected void open(ExecutionContext context) {
        // ステップ開始時: コンテキストから状態を復元
        ChunkTracker tracker = chunkTracker.get();
        tracker.restoreFrom(context);
    }
    
    protected void doExecute(StepExecution execution) {
        // チャンク処理
        while (chunkTracker.get().hasMoreItems()) {
            // アイテムを処理...
        }
        
        // 処理完了時
        chunkTracker.get().noMoreItems();
        
        // 状態をコンテキストに保存（再実行のため）
        execution.getExecutionContext().put("chunkTracker", chunkTracker.get());
    }
    
    @Override
    protected void close(ExecutionContext context) {
        // ✅ 修正: ChunkTrackerの状態をクリア
        context.remove("chunkTracker");
        context.remove("chunkTracker.moreItems");
        // その他のChunkTracker関連の状態もすべてクリア
    }
}
```

### 修正のポイント

| フェーズ | 修正前 | 修正後 |
|---------|-------|-------|
| ステップ開始 (open) | コンテキストから復元 | コンテキストから復元 |
| ステップ実行中 | コンテキストに保存 | コンテキストに保存 |
| ステップ完了 (close) | ❌ 何もしない | ✅ コンテキストからクリア |

### 修正後の動作

```
【1回目の実行】
open(context)
  → context は空
  → chunkTracker.moreItems = true

doExecute()
  → 5件のアイテムを処理
  → chunkTracker.moreItems = false

close(context)
  → ✅ context から chunkTracker の状態を削除
  → context["chunkTracker"] = null

【2回目の実行（新しいジョブインスタンス）】
open(context)
  → context は空（前回の状態がクリアされている）✅
  → chunkTracker.moreItems = true  ✅

doExecute()
  → while (chunkTracker.hasMoreItems())  ← true ✅
  → 5件のアイテムを処理 ✅
```

実際のログ：
```
【2回目の実行（修正後）】
2025-11-28T14:16:45.367  INFO  : Job: [TestJob] launched with parameters: [{'run.id':'2'}]
2025-11-28T14:16:45.444  INFO  : Executing step: [step1]
2025-11-28T14:16:45.644  INFO  : Step 1 WRITER method called with items.size = 5  ← ✅ 正しく処理
2025-11-28T14:16:45.712  INFO  : Step: [step1] executed in 266ms
2025-11-28T14:16:45.750  INFO  : Job: [TestJob] completed with status: [COMPLETED]
```

### リスタート時の動作

ステップが失敗した場合のリスタート動作は維持されます：

```
【リスタートシナリオ】
1回目の実行:
  → 50件処理後に失敗
  → close()は呼ばれない（失敗したため）
  → ChunkTrackerの状態が保存されたまま

リスタート:
  → open()でChunkTrackerを復元
  → 51件目から処理を再開 ✅
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `ChunkOrientedStep` - チャンク指向のステップ実装
  - `ChunkTracker` - チャンク処理の進行状況を追跡
  - `StepExecutionContext` - ステップ実行の状態情報
- **関連課題**: 
  - [#5099](https://github.com/spring-projects/spring-batch/issues/5099) - ChunkTrackerのThreadLocal化に関連
- **影響範囲**: 
  - 同じステップを複数回実行する場合
  - `RunIdIncrementer`などで新しいジョブインスタンスを作成する場合
- **フォールトトレランス**: ステップ失敗時の再実行機能は正常に動作します
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5126
