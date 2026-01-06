*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5172: ローカルチャンキングにおけるBatchStatus一貫性の改善

## 課題概要

Spring Batchのリモートチャンキング機能において、ローカルチャンキング（マネージャーとワーカーが同じJVM内で動作する構成）を使用する際に、マネージャーステップとワーカーステップの`BatchStatus`（実行ステータス）が一貫しない問題が発生していました。この不整合を改善し、両者のステータスが正しく同期されるようにする提案です。

### 用語解説

- **リモートチャンキング**: アイテムの読み込みはマネージャーが行い、処理・書き込みはワーカーが行う分散処理パターン
- **ローカルチャンキング**: リモートチャンキングの構成で、マネージャーとワーカーが同じJVM内で動作する設定。テストや開発時に使用
- **マネージャー**: アイテムを読み込み、チャンクとしてワーカーに送信する側
- **ワーカー**: マネージャーから受け取ったチャンクを処理・書き込みする側
- **BatchStatus**: ステップやジョブの実行状態（COMPLETED、FAILED、STOPPEDなど）
- **StepExecution**: ステップの実行情報（ステータス、開始時刻、終了時刻、処理件数など）を保持

### 問題のシナリオ

#### 構成例

```java
@Configuration
@EnableBatchProcessing
public class LocalChunkingConfiguration {
    
    @Bean
    public Job job(JobRepository jobRepository, Step managerStep) {
        return new JobBuilder("job", jobRepository)
                .start(managerStep)
                .build();
    }
    
    @Bean
    public Step managerStep(JobRepository jobRepository,
                           PlatformTransactionManager transactionManager,
                           ItemReader<String> itemReader) {
        
        // ローカルチャンキングの設定
        return new RemoteChunkingManagerStepBuilder("managerStep", jobRepository)
                .chunk(10, transactionManager)
                .reader(itemReader)
                .outputChannel(requests())  // ローカルチャネル
                .inputChannel(replies())     // ローカルチャネル
                .build();
    }
    
    @Bean
    public IntegrationFlow workerFlow(ItemProcessor processor, ItemWriter writer) {
        return IntegrationFlow
                .from(requests())
                .handle(chunkProcessorChunkHandler(processor, writer))
                .channel(replies())
                .get();
    }
    
    // ローカルチャネル（同じJVM内）
    @Bean
    public QueueChannel requests() {
        return new QueueChannel();
    }
    
    @Bean
    public QueueChannel replies() {
        return new QueueChannel();
    }
}
```

#### 実行時の問題

```
【シナリオ: ワーカーで例外が発生】
1. マネージャーがアイテムを読み込み
   └─ reader.read() → item1, item2, item3

2. マネージャーがチャンクをワーカーに送信
   └─ outputChannel.send(chunk[item1, item2, item3])

3. ワーカーがチャンク処理
   ├─ processor.process(item1) → 成功
   ├─ processor.process(item2) → 例外発生 ❌
   └─ ワーカーのステータス: FAILED

4. ワーカーが失敗レスポンスを返す
   └─ replyChannel.send(ChunkResponse.failed())

5. マネージャーがレスポンスを受信
   └─ ❌ ステータスを更新しない
   └─ マネージャーのステータス: COMPLETED（誤り）

【結果】
マネージャー: COMPLETED ✅
ワーカー: FAILED ❌
  → ステータスが不整合 ❌
```

#### 期待される動作

```
【期待される動作】
ワーカーがFAILED
  ↓
マネージャーもFAILED ✅
  ↓
ジョブもFAILED ✅

【実際の動作（修正前）】
ワーカーがFAILED
  ↓
マネージャーはCOMPLETED ❌
  ↓
ジョブはCOMPLETED ❌（問題を検知できない）
```

### ステータスの不整合による影響

| 問題 | 影響 |
|------|------|
| ジョブが成功したように見える | 実際は失敗しているのに、監視システムで検知できない |
| リスタートが正しく動作しない | 失敗したジョブとして認識されないため、リスタートできない |
| エラー追跡が困難 | ワーカーのログを確認しないと失敗に気づかない |
| データ不整合 | 処理が失敗しているのに成功として扱われる |

## 原因

ローカルチャンキングの実装において、ワーカーからの失敗レスポンスを受け取った際に、マネージャーステップの`BatchStatus`を更新する処理が不足していました。

### 詳細な原因

#### メッセージフロー（修正前）

```
【マネージャー側】
1. アイテム読み込み
   └─ ItemReader.read()

2. チャンクを作成
   └─ Chunk<String> chunk = new Chunk<>(items)

3. ワーカーに送信
   └─ outputChannel.send(new ChunkRequest<>(chunk))

4. レスポンス待機
   └─ ChunkResponse response = inputChannel.receive()

5. ❌ レスポンスのステータスを確認するが、
      マネージャーのステータスは更新しない
   
   if (response.isSuccessful()) {
       // 何もしない
   } else {
       // ❌ ステータスを更新しない
       log.error("Worker failed");
   }

6. マネージャーステップ終了
   └─ status: COMPLETED（誤り）
```

```
【ワーカー側】
1. チャンクを受信
   └─ ChunkRequest request = inputChannel.receive()

2. チャンク処理
   try {
       processor.process(item)
       writer.write(items)
   } catch (Exception e) {
       // ✅ ワーカー側のステータスはFAILEDに設定される
       status = BatchStatus.FAILED
   }

3. レスポンス送信
   └─ replyChannel.send(ChunkResponse.failed())
```

#### 問題の整理

```java
// RemoteChunkingManagerStepBuilder（修正前のイメージ）
class RemoteChunkingManagerStepBuilder {
    
    void handleChunkResponse(StepExecution stepExecution, ChunkResponse response) {
        
        if (!response.isSuccessful()) {
            // ❌ ログは出力するが、ステータスは更新しない
            logger.error("Worker step failed: " + response.getMessage());
            
            // ❌ この処理が欠落している
            // stepExecution.setStatus(BatchStatus.FAILED);
            // stepExecution.addFailureException(response.getException());
        }
        
        // マネージャーステップは正常終了してしまう
    }
}
```

### ステータス更新の比較

| 状況 | マネージャーステータス（修正前） | マネージャーステータス（修正後） |
|------|------------------------------|------------------------------|
| ワーカー成功 | COMPLETED ✅ | COMPLETED ✅ |
| ワーカー失敗 | COMPLETED ❌ | FAILED ✅ |
| ワーカータイムアウト | COMPLETED ❌ | FAILED ✅ |
| ワーカー停止 | COMPLETED ❌ | STOPPED ✅ |

## 対応方針

ワーカーからの失敗レスポンスを受け取った際に、マネージャーステップの`BatchStatus`を適切に更新するように修正されました。

### 修正内容

[コミット e5c1b5a](https://github.com/spring-projects/spring-batch/commit/e5c1b5a0c5e0cb71bbb764e95154e20c6c5d79c3)

```java
// RemoteChunkingManagerStepBuilder（修正後）
class RemoteChunkingManagerStepBuilder {
    
    void handleChunkResponse(StepExecution stepExecution, ChunkResponse response) {
        
        if (!response.isSuccessful()) {
            logger.error("Worker step failed: " + response.getMessage());
            
            // ✅ 修正: マネージャーのステータスを更新
            stepExecution.setStatus(BatchStatus.FAILED);
            
            // ✅ 修正: 例外情報を記録
            if (response.getException() != null) {
                stepExecution.addFailureException(response.getException());
            }
            
            // ✅ 修正: 終了メッセージを設定
            stepExecution.setExitStatus(
                new ExitStatus(ExitStatus.FAILED.getExitCode(), response.getMessage())
            );
        }
    }
}
```

### 修正後の動作フロー

```
【シナリオ: ワーカーで例外が発生】
1. マネージャーがアイテムを読み込み
   └─ reader.read() → item1, item2, item3

2. マネージャーがチャンクをワーカーに送信
   └─ outputChannel.send(chunk[item1, item2, item3])

3. ワーカーがチャンク処理
   ├─ processor.process(item1) → 成功
   ├─ processor.process(item2) → 例外発生 ❌
   └─ ワーカーのステータス: FAILED

4. ワーカーが失敗レスポンスを返す
   └─ replyChannel.send(ChunkResponse.failed(exception))

5. ✅ マネージャーがレスポンスを受信し、ステータスを更新
   ├─ stepExecution.setStatus(FAILED)
   ├─ stepExecution.addFailureException(exception)
   └─ マネージャーのステータス: FAILED

6. ジョブのステータスも更新
   └─ jobExecution.setStatus(FAILED)

【結果】
マネージャー: FAILED ✅
ワーカー: FAILED ✅
ジョブ: FAILED ✅
  → ステータスが一貫 ✅
```

### ステータス同期の詳細

#### 成功ケース

```
【ワーカーが成功】
ワーカー: COMPLETED
  ↓ ChunkResponse.successful()
マネージャー: COMPLETED ✅
  ↓
ジョブ: COMPLETED ✅
```

#### 失敗ケース

```
【ワーカーが失敗】
ワーカー: FAILED
  ↓ ChunkResponse.failed(exception)
マネージャー: FAILED ✅
  ├─ status = FAILED
  ├─ exception = チェーンされた例外
  └─ exitStatus = FAILED: "Worker processing failed"
  ↓
ジョブ: FAILED ✅
```

#### 停止ケース

```
【ワーカーが停止】
ワーカー: STOPPED
  ↓ ChunkResponse.stopped()
マネージャー: STOPPED ✅
  └─ status = STOPPED
  ↓
ジョブ: STOPPED ✅
```

### ログとデバッグ情報

```
【修正後のログ出力例】
2024-01-05 10:15:23.456 INFO  --- [main] o.s.b.core.job.SimpleStepHandler
  : Executing step: [managerStep]

2024-01-05 10:15:24.123 INFO  --- [worker-thread] o.s.b.integration.chunk.ChunkHandler
  : Processing chunk with 10 items

2024-01-05 10:15:24.567 ERROR --- [worker-thread] o.s.b.integration.chunk.ChunkHandler
  : Error processing item: item5
  java.lang.IllegalStateException: Invalid data
      at com.example.MyProcessor.process(MyProcessor.java:25)
      ...

2024-01-05 10:15:24.890 ERROR --- [main] o.s.b.integration.chunk.RemoteChunkingManager
  : Worker step failed: Error processing item: item5

2024-01-05 10:15:24.892 INFO  --- [main] o.s.b.core.step.AbstractStep
  : Step: [managerStep] executed with status: FAILED

2024-01-05 10:15:24.895 INFO  --- [main] o.s.b.core.job.AbstractJob
  : Job: [job] completed with status: FAILED
```

### リスタート動作の改善

```java
// ジョブ実行
JobExecution jobExecution1 = jobLauncher.run(job, jobParameters);

// 修正前: ワーカー失敗時
assertEquals(BatchStatus.COMPLETED, jobExecution1.getStatus());  // ❌ 誤った成功

// 修正後: ワーカー失敗時
assertEquals(BatchStatus.FAILED, jobExecution1.getStatus());  // ✅ 正しく失敗

// ✅ リスタートが可能になる
JobExecution jobExecution2 = jobLauncher.run(job, jobParameters);
assertEquals(BatchStatus.COMPLETED, jobExecution2.getStatus());  // リスタート成功
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.1で改善
- **関連クラス**:
  - `RemoteChunkingManagerStepBuilder` - リモートチャンキングマネージャーのビルダー
  - `ChunkRequest` - チャンク処理リクエスト
  - `ChunkResponse` - チャンク処理レスポンス
  - `ChunkHandler` - ワーカー側のチャンク処理ハンドラー
  - `StepExecution` - ステップ実行情報
  - `BatchStatus` - 実行ステータス（COMPLETED、FAILED、STOPPEDなど）
- **リモートチャンキングの構成**:
  - **リモートチャンキング**: マネージャーとワーカーが異なるJVM/マシンで動作
  - **ローカルチャンキング**: 同じJVM内で動作（テスト・開発用）
- **ステータスの種類**:
  - `COMPLETED`: 正常終了
  - `FAILED`: 失敗（例外発生）
  - `STOPPED`: 停止（stop()メソッド呼び出し）
  - `STARTED`: 実行中
  - `STARTING`: 開始前
  - `STOPPING`: 停止中
- **ローカルチャンキングの用途**:
  - 開発時の動作確認
  - 単体テスト
  - 統合テスト
  - プロトタイプ作成
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5172
