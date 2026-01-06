*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5139: ResourcelessJobRepositoryの並行実行制御の改善

## 課題概要

Spring Batchのテストや軽量実行に使われる`ResourcelessJobRepository`において、並行実行時のスレッドセーフ性を改善する提案です。現在の実装は`synchronized`キーワードでスレッド制御を行っていますが、より洗練された並行実行制御の仕組みに置き換えることで、パフォーマンスと保守性を向上させることができます。

### 用語解説

- **ResourcelessJobRepository**: データベースを使用せず、メモリ上でジョブ・ステップの実行情報を管理する`JobRepository`の実装。テスト用途や軽量実行に使用される
- **JobRepository**: ジョブとステップの実行情報（実行ID、ステータス、実行時刻など）を保存・取得するコンポーネント
- **synchronized**: Javaのキーワードで、メソッドやブロックを同期化し、複数のスレッドから同時にアクセスされないようにする
- **java.util.concurrent**: Javaの並行処理ライブラリ。`ConcurrentHashMap`、`AtomicLong`、`ReentrantLock`など、より高度なスレッドセーフなクラスを提供
- **ConcurrentHashMap**: スレッドセーフなHashMapの実装。複数のスレッドが同時にアクセスしても安全に動作する
- **AtomicLong**: スレッドセーフなlong型の値。カウンタの増減を安全に行える

### 問題のシナリオ

#### テストでの使用例

```java
@SpringBatchTest
@SpringBootTest
public class JobTest {
    
    @Autowired
    private Job job;
    
    @Autowired
    private JobLauncher jobLauncher;
    
    @Test
    public void testJob() throws Exception {
        // ResourcelessJobRepositoryが使用される
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("date", "2024-01-05")
                .toJobParameters();
        
        JobExecution jobExecution = jobLauncher.run(job, jobParameters);
        
        assertEquals(BatchStatus.COMPLETED, jobExecution.getStatus());
    }
}
```

#### 並行実行でのパフォーマンス問題

```java
// 複数のスレッドから同時にジョブを実行
ExecutorService executor = Executors.newFixedThreadPool(10);

for (int i = 0; i < 100; i++) {
    final int jobId = i;
    executor.submit(() -> {
        JobParameters params = new JobParametersBuilder()
                .addLong("id", (long) jobId)
                .toJobParameters();
        
        // ❌ synchronized により、実行が直列化される
        // 並行実行のメリットが失われる
        jobLauncher.run(job, params);
    });
}
```

### 現在の実装の問題点

1. **粗粒度のロック**: メソッド全体を`synchronized`でロックしているため、必要以上に広範囲がロックされる
2. **並行性の制限**: すべての操作が直列化され、並行実行のパフォーマンス向上が得られない
3. **保守性**: `synchronized`は古い並行制御の手法で、現代的な`java.util.concurrent`パッケージの方が明示的で保守しやすい

## 原因

`ResourcelessJobRepository`の初期実装（Spring Batch 2.0時代）では、シンプルな`synchronized`キーワードでスレッド制御を実装していました。しかし、Java 5以降で登場した`java.util.concurrent`パッケージの高度な並行制御の仕組みが普及した現在、より効率的な実装が可能になっています。

### 詳細な実装比較

#### 現在の実装（修正前）

```java
public class ResourcelessJobRepository implements JobRepository {
    
    // ❌ 通常のHashMapとlongカウンタ
    private final Map<Long, JobExecution> jobExecutions = new HashMap<>();
    private final Map<Long, StepExecution> stepExecutions = new HashMap<>();
    private long currentJobExecutionId = 0;
    private long currentStepExecutionId = 0;
    
    // ❌ メソッド全体をsynchronizedでロック
    @Override
    public synchronized JobExecution createJobExecution(String jobName, JobParameters jobParameters) {
        // ID生成（スレッドセーフでない）
        currentJobExecutionId++;
        
        JobExecution jobExecution = new JobExecution(currentJobExecutionId);
        jobExecution.setJobParameters(jobParameters);
        
        // マップに保存（スレッドセーフでない）
        jobExecutions.put(currentJobExecutionId, jobExecution);
        
        return jobExecution;
    }
    
    // ❌ メソッド全体をsynchronizedでロック
    @Override
    public synchronized void update(JobExecution jobExecution) {
        Long id = jobExecution.getId();
        JobExecution persistedExecution = jobExecutions.get(id);
        
        if (persistedExecution == null) {
            throw new NoSuchJobExecutionException("JobExecution not found: " + id);
        }
        
        // 更新処理
        jobExecutions.put(id, jobExecution);
    }
    
    // ❌ メソッド全体をsynchronizedでロック
    @Override
    public synchronized StepExecution addStepExecution(JobExecution jobExecution) {
        // ID生成（スレッドセーフでない）
        currentStepExecutionId++;
        
        StepExecution stepExecution = new StepExecution("step", jobExecution, currentStepExecutionId);
        
        // マップに保存（スレッドセーフでない）
        stepExecutions.put(currentStepExecutionId, stepExecution);
        
        return stepExecution;
    }
}
```

#### 問題点の詳細

```
【問題1: 粗粒度のロック】
synchronized メソッド
  → メソッド全体がロックされる
  → 不要な処理もロック対象になる
  → 並行性が低下

【問題2: 並行性の制限】
スレッドA: createJobExecution() 実行中
  ↓ synchronized により待機
スレッドB: update() を実行したい
  ↓ ロック解除を待つ
スレッドC: getLastJobExecution() を実行したい
  ↓ ロック解除を待つ
  
→ すべての操作が直列化される

【問題3: スケーラビリティ】
スレッド数が増えるほど、待機時間が増加
  → CPUリソースを有効活用できない
```

## 対応方針

`java.util.concurrent`パッケージの並行制御の仕組みを活用して、より効率的でスレッドセーフな実装に改善されました。

### 修正内容

[コミット b7b9055](https://github.com/spring-projects/spring-batch/commit/b7b90556f4bdf2a798d7ba4f03e25c574a2ca4bd)

```java
public class ResourcelessJobRepository implements JobRepository {
    
    // ✅ スレッドセーフなコレクションとカウンタ
    private final ConcurrentMap<Long, JobExecution> jobExecutions = new ConcurrentHashMap<>();
    private final ConcurrentMap<Long, StepExecution> stepExecutions = new ConcurrentHashMap<>();
    private final AtomicLong currentJobExecutionId = new AtomicLong(0);
    private final AtomicLong currentStepExecutionId = new AtomicLong(0);
    
    // ✅ synchronizedを削除
    @Override
    public JobExecution createJobExecution(String jobName, JobParameters jobParameters) {
        // ✅ アトミックにID生成（スレッドセーフ）
        long id = currentJobExecutionId.incrementAndGet();
        
        JobExecution jobExecution = new JobExecution(id);
        jobExecution.setJobParameters(jobParameters);
        
        // ✅ ConcurrentHashMapで保存（スレッドセーフ）
        jobExecutions.put(id, jobExecution);
        
        return jobExecution;
    }
    
    // ✅ synchronizedを削除
    @Override
    public void update(JobExecution jobExecution) {
        Long id = jobExecution.getId();
        
        // ✅ ConcurrentHashMapで取得（スレッドセーフ）
        JobExecution persistedExecution = jobExecutions.get(id);
        
        if (persistedExecution == null) {
            throw new NoSuchJobExecutionException("JobExecution not found: " + id);
        }
        
        // ✅ ConcurrentHashMapで更新（スレッドセーフ）
        jobExecutions.put(id, jobExecution);
    }
    
    // ✅ synchronizedを削除
    @Override
    public StepExecution addStepExecution(JobExecution jobExecution) {
        // ✅ アトミックにID生成（スレッドセーフ）
        long id = currentStepExecutionId.incrementAndGet();
        
        StepExecution stepExecution = new StepExecution("step", jobExecution, id);
        
        // ✅ ConcurrentHashMapで保存（スレッドセーフ）
        stepExecutions.put(id, stepExecution);
        
        return stepExecution;
    }
}
```

### 改善のポイント

#### 1. スレッドセーフなデータ構造

| 修正前 | 修正後 | 利点 |
|-------|-------|------|
| `HashMap` | `ConcurrentHashMap` | 複数スレッドから同時アクセス可能 |
| `long` | `AtomicLong` | アトミックな増減操作が可能 |
| `synchronized`メソッド | ロックなし | 並行実行が可能 |

#### 2. 細粒度の並行制御

```
【修正前: synchronized】
スレッドA: createJobExecution()
  ↓ メソッド全体をロック
スレッドB: 待機 ❌
スレッドC: 待機 ❌

【修正後: ConcurrentHashMap】
スレッドA: createJobExecution()
  ↓ 必要な部分だけロック
スレッドB: update() 実行可能 ✅
スレッドC: getLastJobExecution() 実行可能 ✅
```

#### 3. パフォーマンスの向上

```java
// ベンチマーク例（イメージ）
ExecutorService executor = Executors.newFixedThreadPool(10);

// 100個のジョブを並行実行
for (int i = 0; i < 100; i++) {
    executor.submit(() -> {
        jobLauncher.run(job, params);
    });
}

【修正前】
実行時間: 約10秒
（ほぼ直列実行になる）

【修正後】
実行時間: 約1.5秒
（並行実行のメリットが得られる）
```

### ConcurrentHashMapの動作

```
【内部の仕組み】
ConcurrentHashMap
  ├─ セグメント0（ロック独立）
  ├─ セグメント1（ロック独立）
  ├─ セグメント2（ロック独立）
  ...
  └─ セグメントN（ロック独立）

スレッドA → セグメント0にアクセス
スレッドB → セグメント1にアクセス（同時実行可能 ✅）
スレッドC → セグメント0にアクセス（待機が必要）

→ 異なるセグメントへのアクセスは並行実行可能
```

### AtomicLongの動作

```java
// 修正前: synchronized が必要
synchronized long getNextId() {
    return ++currentId;  // スレッドセーフでない
}

// 修正後: AtomicLongで安全
AtomicLong currentId = new AtomicLong(0);
long getNextId() {
    return currentId.incrementAndGet();  // スレッドセーフ ✅
}
```

```
【AtomicLongの内部動作】
incrementAndGet()
  ↓
CAS（Compare-And-Swap）命令
  ↓
CPUレベルでアトミック性を保証
  ↓
ロック不要で高速
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.1で改善
- **関連クラス**:
  - `ResourcelessJobRepository` - メモリベースのJobRepository実装
  - `ConcurrentHashMap` - スレッドセーフなMap実装
  - `AtomicLong` - アトミックなlong値
  - `java.util.concurrent.*` - 並行処理ユーティリティ
- **Java並行処理の基礎**:
  - **synchronized**: オブジェクト単位のロック。シンプルだが粗粒度
  - **ConcurrentHashMap**: セグメント単位のロック。細粒度で高性能
  - **AtomicLong**: CAS命令を使用。ロック不要で高速
  - **Compare-And-Swap (CAS)**: CPUの命令レベルでアトミック性を保証
- **使用シーン**:
  - ユニットテスト: `@SpringBatchTest`で自動的に使用される
  - 統合テスト: データベース不要の軽量テスト
  - 開発環境: クイックな動作確認
  - デモ・プロトタイプ: データベースセットアップ不要
- **パフォーマンスの考慮**:
  - 読み取り操作: synchronizedよりも大幅に高速
  - 書き込み操作: synchronizedと同等か若干高速
  - 並行スレッド数が多いほど改善効果が大きい
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5139
