*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月9日に生成されました）*

## 課題概要

`ChunkOrientedStep` の `ChunkTracker` がステップ実行後にリセットされないため、同じステップを2回以上実行すると、2回目以降の実行でチャンク処理が全くスキップされてしまうバグです。

**`ChunkTracker`とは**: Spring Batch 6.0で導入された内部クラスで、チャンク処理においてまだ読み取るアイテムがあるかどうかを追跡するためのフラグを管理します。

### 問題の状況

```plantuml
@startuml
title ChunkTrackerのリセット問題

state "1回目のジョブ実行" as Job1 {
    state "ステップ開始" as S1_Start
    state "チャンク処理" as S1_Chunk
    state "リーダー枯渇" as S1_NoMore
    state "ステップ終了" as S1_End
    
    S1_Start --> S1_Chunk : moreItems=true
    S1_Chunk --> S1_Chunk : アイテム読み取り
    S1_Chunk --> S1_NoMore : item=null
    S1_NoMore --> S1_End : noMoreItems()\nmoreItems=false
}

state "2回目のジョブ実行" as Job2 {
    state "ステップ開始" as S2_Start
    state "即座に終了" as S2_End
    
    S2_Start --> S2_End : moreItems=false\n(リセットされていない!)
    note right of S2_End : チャンク処理が\n全くスキップされる
}

Job1 --> Job2 : moreItems=falseのまま
@enduml
```

### ログ出力の比較

| 実行回数 | ログ出力 | 問題 |
|---------|---------|------|
| 1回目 | `Reader was called, returning item`<br/>`Reader was called, returning null`<br/>`Writing chunk...`<br/>`Step: [step] executed in 5ms` | 正常 |
| **2回目** | `Executing step: [step]`<br/>`Step: [step] executed in` | チャンク処理なし！ |
| **3回目** | `Executing step: [step]`<br/>`Step: [step] executed in` | チャンク処理なし！ |

## 原因

`ChunkTracker` クラスのフラグ `moreItems` が、ステップの終了時にリセットされていませんでした。Issue #5099 で ThreadLocal 化された際に、ライフサイクル管理が不完全でした。

**問題のコード（修正前）**:
```java
private static class ChunkTracker {
    private boolean moreItems = true;  // 初期値true
    
    void noMoreItems() {
        this.moreItems = false;  // 一度falseになると戻らない
    }
    
    boolean moreItems() {
        return this.moreItems;
    }
}
```

## 対応方針

### 変更内容

`ChunkTracker` に `init()` と `reset()` メソッドを追加し、ステップの開始時と終了時に適切にフラグを管理するように修正しました。

**修正後のコード**:
```java
private static class ChunkTracker {
    private boolean moreItems;  // デフォルトfalse
    
    void init() {
        this.moreItems = true;  // ステップ開始時にtrueに設定
    }
    
    void reset() {
        this.moreItems = false;  // リーダー枯渇時またはステップ終了時にfalseに設定
    }
    
    boolean moreItems() {
        return this.moreItems;
    }
}

// ChunkOrientedStep内での使用
@Override
protected void open(ExecutionContext executionContext) throws Exception {
    this.compositeItemStream.open(executionContext);
    this.chunkTracker.get().init();  // ステップ開始時に初期化
}

@Override
protected void close(ExecutionContext executionContext) throws Exception {
    this.chunkTracker.get().reset();  // ステップ終了時にリセット
    this.compositeItemStream.close();
}
```

### 追加されたテスト

同じジョブを複数回実行しても正しく動作することを確認するテスト：

```java
@Test
void testChunkOrientedStepReExecution() throws Exception {
    // given
    ApplicationContext context = new AnnotationConfigApplicationContext(StepConfiguration.class);
    JobOperator jobOperator = context.getBean(JobOperator.class);
    Job job = context.getBean(Job.class);

    // when - 2回実行
    jobOperator.start(job, new JobParametersBuilder().addLong("run.id", 1L).toJobParameters());
    jobOperator.start(job, new JobParametersBuilder().addLong("run.id", 2L).toJobParameters());

    // then - 両方とも書き込まれていることを確認
    ListItemWriter<String> itemWriter = context.getBean(ListItemWriter.class);
    Assertions.assertEquals(2, itemWriter.getWrittenItems().size());
}
```

### 修正後の状態遷移

```plantuml
@startuml
title 修正後のChunkTrackerライフサイクル

state "ステップ実行前" as Before {
    state "moreItems = false" as MF1
}

state "ステップ実行中" as Running {
    state "open() → init()" as Init : moreItems = true
    state "チャンク処理" as Chunk
    state "リーダー枯渇 → reset()" as Exhausted : moreItems = false
    state "close() → reset()" as Close : moreItems = false
    
    [*] --> Init
    Init --> Chunk
    Chunk --> Chunk : アイテムあり
    Chunk --> Exhausted : item = null
    Exhausted --> Close
}

state "ステップ実行後" as After {
    state "moreItems = false" as MF2
}

Before --> Running : open()
Running --> After : close()
After --> Running : 次回実行時open()

note right of After : 次回実行時に\ninit()で再初期化される
@enduml
```

---

**関連リンク**:
- [Issue #5126](https://github.com/spring-projects/spring-batch/issues/5126)
- [Commit 69665d8](https://github.com/spring-projects/spring-batch/commit/69665d83d8556d9c23a965ee553972a277221d83)
- 関連Issue: [#5099](https://github.com/spring-projects/spring-batch/issues/5099) (ChunkTrackerのThreadLocal化)
