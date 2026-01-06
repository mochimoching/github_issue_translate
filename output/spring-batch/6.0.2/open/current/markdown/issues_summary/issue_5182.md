*（このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました）*

## 課題概要

Spring Batch 6.xで新たに導入された`ChunkOrientedStep`において、チャンクの処理がトランザクションでロールバックされた場合でも、`ItemStream`の状態と`ExecutionContext`が永続化されてしまう問題です。この結果、ジョブを再起動した際に、失敗したチャンク内のレコードがスキップされ、**データ損失**が発生します。

**ItemStreamとは**: Spring Batchでリソース（ファイル、データベースカーソルなど）のライフサイクル管理を行うインターフェースです。`open()`、`update()`、`close()`メソッドを持ち、現在の読み取り位置やオフセットなどの状態を`ExecutionContext`に保存します。

**ExecutionContextとは**: ステップ実行間で状態を永続化するためのキー・バリュー形式のストレージです。ジョブの再起動時に前回の状態を復元するために使用されます。

### 問題の具体例

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 200
}

state "チャンク処理" as Chunk {
  [*] -> レコード読み取り
  レコード読み取り: ItemReader.read()
  レコード読み取り: オフセット: 0→3
  
  レコード読み取り -> レコード処理
  レコード処理: ItemProcessor.process()
  
  レコード処理 -> レコード書き込み
  レコード書き込み: ItemWriter.write()
  レコード書き込み: ❌例外発生
  
  レコード書き込み -> トランザクションロールバック
  トランザクションロールバック: ビジネスデータは元に戻る
  
  トランザクションロールバック -> finally節実行
  finally節実行: ❌問題: ItemStream.update()
  finally節実行: ❌問題: jobRepository.updateExecutionContext()
  finally節実行: オフセット3を永続化
}

state "ジョブ再起動" as Restart {
  [*] -> 前回の状態復元
  前回の状態復元: オフセット3から再開  
  前回の状態復元 -> レコード4から読み取り
  レコード4から読み取り: ❌データ損失 

}

Chunk --> Restart: ジョブ再起動

@enduml
```

### データ損失のシナリオ

| タイミング | チャンク | 読み取り範囲 | 処理結果 | オフセット保存 | 再起動後の動作 |
|----------|--------|-----------|---------|-------------|--------------|
| 初回実行 | チャンク1 | レコード0-2 | ❌例外発生→ロールバック | ✓ オフセット3保存（問題） | - |
| 再起動 | チャンク1 | レコード3-5 | 処理継続 | ✓ オフセット6保存 | レコード0-2が**永久にスキップ** |

## 原因

### コード構造の変更（Spring Batch 5.x → 6.x）

#### Spring Batch 5.x (TaskletStep.java) - 正常な動作

```java
// TaskletStep.java (Line 452)
// 成功した処理フロー内でのみ状態更新
if (chunk.isComplete()) {
    stream.update(stepExecution.getExecutionContext());
    getJobRepository().updateExecutionContext(stepExecution);
    stepExecution.incrementCommitCount();
}
```

**ポイント**: トランザクションが成功した場合にのみ状態を更新

#### Spring Batch 6.x (ChunkOrientedStep.java) - 問題のある動作

```java
// ChunkOrientedStep.java
private void processChunkSequentially(...) {
    try {
        // チャンクの読み取り/処理/書き込みロジック
        // トランザクション内で実行
    } catch (Exception e) {
        // 例外処理
        throw e; // トランザクションロールバック
    } finally {
        // ❌バグ: トランザクションがロールバックされても必ず実行される
        this.compositeItemStream.update(stepExecution.getExecutionContext());
        getJobRepository().updateExecutionContext(stepExecution);
    }
}
```

**ポイント**: `finally`節で無条件に状態を更新→トランザクションの一貫性が失われる

### トランザクションの不整合

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 200
}

partition "ビジネストランザクション" {
  :レコード0-2を読み取り<#LightBlue>;
  :ItemReader内部状態:\noffset=3;
  
  :レコードを処理;
  
  :❌レコード書き込み失敗;
  
  :トランザクションロールバック;
  note right
    データベースのビジネスデータは
    更新前の状態に戻る
  end note
}

partition "メタデータトランザクション（別トランザクション）" {
  :finally節実行
  
  :ItemStream.update();
  note right
    offset=3を
    ExecutionContextに保存
  end note
  
  :jobRepository.updateExecutionContext();
  note right
    BATCH_STEP_EXECUTION_CONTEXT
    テーブルに永続化
  end note
  
  :❌コミット成功;
  note right
    ビジネスデータとメタデータの
    不整合が発生
  end note
}

@enduml
```

### 処理フローの比較

```plantuml
@startuml
skinparam backgroundColor transparent

|Spring Batch 5.x|
:チャンク処理開始;
if (処理成功?) then (yes)
  :状態更新;
  :コミット;
else (no)
  :ロールバック;
  note right
    状態更新なし
    →再起動時に
    同じレコードから再開
  end note
endif

|Spring Batch 6.x|
:チャンク処理開始;
if (処理成功?) then (yes)
  :トランザクションコミット;
else (no)
  :トランザクションロールバック;
endif
:finally節実行;
:❌状態更新（必ず実行）;
:❌メタデータコミット;
note right
  ロールバック後も
  状態が進む
  →再起動時に
  レコードがスキップ
end note

@enduml
```

## 対応方針

### 提案される修正案

`ChunkOrientedStep.doExecute()`メソッドで、トランザクションコミット成功後にのみ状態を更新するよう変更します。

#### 修正前のコード構造

```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
        this.transactionTemplate.executeWithoutResult(transactionStatus -> {
            // processChunkSequentially() または processChunkConcurrently()
            // ↓↓↓ finally節で必ず実行される ↓↓↓
            // this.compositeItemStream.update(stepExecution.getExecutionContext());
            // getJobRepository().updateExecutionContext(stepExecution);
        });
        getJobRepository().update(stepExecution);
    }
}
```

#### 修正後のコード構造（提案）

```java
@Override
protected void doExecute(StepExecution stepExecution) throws Exception {
    stepExecution.getExecutionContext().put(STEP_TYPE_KEY, this.getClass().getName());
    
    while (this.chunkTracker.get().moreItems() && !interrupted(stepExecution)) {
        // 次のチャンクを独自のトランザクションで処理
        this.transactionTemplate.executeWithoutResult(transactionStatus -> {
            // processChunkSequentially()またはprocessChunkConcurrently()
            // finally節から状態更新処理を削除
        });
        
        getJobRepository().update(stepExecution);
        
        // ✅修正: トランザクションコミット成功後にのみItemStreamとExecutionContextを更新
        this.compositeItemStream.update(stepExecution.getExecutionContext());
        getJobRepository().updateExecutionContext(stepExecution);
    }
}
```

#### processChunkSequentiallyの修正

```java
private void processChunkSequentially(...) {
    try {
        // チャンクの読み取り/処理/書き込みロジック
    } catch (Exception e) {
        // 例外処理
        throw e;
    }
    // ✅修正: finally節を削除
    // 状態更新はdoExecute()で行う
}
```

### 修正後の動作フロー

```plantuml
@startuml
skinparam backgroundColor transparent

:チャンク処理開始;

partition "ビジネストランザクション" {
  :レコード読み取り;
  :ItemReader内部状態更新;
  
  if (処理成功?) then (yes)
    :レコード書き込み;
    :トランザクションコミット;
  else (no)
    :❌例外発生;
    :トランザクションロールバック;
    stop
  endif
}

:JobRepository.update();
note right
  チャンクのステータス更新
end note

:✅ItemStream.update();
note right
  トランザクション成功後のみ
  オフセットを保存
end note

:✅ExecutionContext永続化;

:次のチャンクへ;

@enduml
```

### 期待される効果

| 項目 | 修正前 | 修正後 |
|-----|-------|-------|
| トランザクション成功時 | 状態更新 | 状態更新 |
| トランザクション失敗時 | ❌状態更新（不整合） | ✓ 状態更新なし |
| 再起動時の動作 | 失敗チャンクをスキップ | 失敗チャンクから再開 |
| データ整合性 | ❌不整合 | ✓ 整合性維持 |
| データ損失リスク | ❌高い | ✓ なし |

### 修正の影響範囲

```plantuml
@startuml
skinparam componentStyle rectangle
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 200
}
component "ChunkOrientedStep" as Step {
  component "doExecute()" as DoExecute
  component "processChunkSequentially()" as Sequential
  component "processChunkConcurrently()" as Concurrent
}

component "CompositeItemStream" as Stream
component "JobRepository" as Repo
database "BATCH_STEP_EXECUTION_CONTEXT" as DB

DoExecute --> Sequential: 呼び出し
DoExecute --> Concurrent: 呼び出し

DoExecute ..> Stream: ✅修正: コミット後に移動\nupdate()
DoExecute ..> Repo: ✅修正: コミット後に移動\nupdateExecutionContext()

Sequential .up.> Stream: ❌削除: finally節の\nupdate()
Sequential .up.> Repo: ❌削除: finally節の\nupdateExecutionContext()

Concurrent .up.> Stream: ❌削除: finally節の\nupdate()
Concurrent .up.> Repo: ❌削除: finally節の\nupdateExecutionContext()

Stream --> DB: 状態永続化
Repo --> DB: メタデータ永続化

note right of Sequential
  finally節内の
  状態更新処理を削除
end note

note right of DoExecute
  トランザクション成功後に
  状態更新処理を追加
end note

@enduml
```

### 注意点

**重複更新の防止**: `processChunkSequentially()`と`processChunkConcurrently()`の`finally`節から状態更新呼び出しを削除する必要があります。削除しない場合、以下の問題が発生します：

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 200
}
:トランザクションコミット;

if (finally節に更新処理が残っている?) then (yes)
  :finally節で1回目の更新;
  :doExecute()で2回目の更新;
  note right
    ❌二重更新
    パフォーマンス低下
    潜在的な競合リスク
  end note
else (no)
  :doExecute()で1回のみ更新;
  note right
    ✅正常
  end note
endif

@enduml
```

### 関連課題

この修正により、以下の副次的な問題も解決されます：

- トランザクション境界とメタデータ永続化のタイミングが一致
- 楽観的ロック例外のリスク低減
- ジョブ再起動時の予測可能性向上

**現在のステータス**: 開発チームへの問題報告済み。コミュニティから具体的な修正案が提示されており、修正実装待ちの状態です。
