*（このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました）*

## 課題概要

Spring Batch 6.0で導入された`ChunkOrientedStep`において、マルチスレッド（`TaskExecutor`）設定を使用する際、`@StepScope`で定義された`ItemProcessor`がワーカースレッド内で正しく解決されず、`ScopeNotActiveException`が発生する問題です。

**@StepScopeとは**: Spring Batchが提供するカスタムスコープで、ステップ実行ごとにBeanのインスタンスを作成します。`JobParameters`や`ExecutionContext`の値を遅延評価で注入できるため、動的な設定が可能になります。

**TaskExecutorとは**: Spring Frameworkが提供する非同期タスク実行の抽象化インターフェースです。マルチスレッド処理を実現するために使用され、Spring Batchではチャンク処理の並列化に利用されます。

### 問題の発生状況

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam minClassWidth 150

participant "メインスレッド" as Main
participant "TaskExecutor" as Executor
participant "ワーカースレッド" as Worker
participant "StepSynchronizationManager" as Manager
participant "@StepScope Processor" as Processor

Main -> Manager: StepContextを登録
activate Main
note right: メインスレッドのThreadLocalに保存

Main -> Executor: submit(処理タスク)
activate Executor

Executor -> Worker: 新しいスレッドで実行
activate Worker

Worker -> Processor: process(item) 呼び出し
activate Processor
note right: @StepScopeプロキシ

Processor -> Manager: StepContextを取得
note right: ワーカースレッドのThreadLocalから検索

Manager --> Processor: ❌コンテキスト未登録
note right: ThreadLocalは\nスレッドごとに独立

Processor --> Worker: ❌ScopeNotActiveException
deactivate Processor
note right
  Error: Scope 'step' is not active
  for the current thread
end note

Worker --> Executor: 例外返却
deactivate Worker

Executor --> Main: 処理失敗
deactivate Executor
deactivate Main

@enduml
```

### エラーの詳細

```
Caused by: org.springframework.beans.factory.support.ScopeNotActiveException: 
  Error creating bean with name 'scopedTarget.issueReproductionProcessor': 
  Scope 'step' is not active for the current thread
  at AbstractBeanFactory.doGetBean()
  at $Proxy134.process()
  at ChunkOrientedStep.doProcess()

Caused by: java.lang.IllegalStateException: 
  No context holder available for step scope
  at StepScope.getContext()
```

### マルチスレッド設定の例

```java
@Bean
public Step issueReproductionStep(
        JobRepository jobRepository,
        ItemReader<TestItem> reader,
        ItemProcessor<TestItem, TestItem> itemProcessor, // @StepScope
        ItemWriter<TestItem> writer
) {
    return new StepBuilder(jobRepository)
            .<TestItem, TestItem>chunk(1)
            .reader(reader)
            .processor(itemProcessor)
            .writer(writer)
            .taskExecutor(new SimpleAsyncTaskExecutor()) // マルチスレッド有効
            .build();
}

@Bean
@StepScope
public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
    return item -> {
        log.info("[Thread: {}] Processing item: {}", 
                 Thread.currentThread().getName(), item.getName());
        return item;
    };
}
```

## 原因

### ThreadLocalの仕組み

`StepSynchronizationManager`は、`StepContext`を`ThreadLocal`変数に保存します。`ThreadLocal`は各スレッドごとに独立した値を保持するため、別スレッドからはアクセスできません。

```plantuml
@startuml
skinparam backgroundColor transparent

package "メインスレッド (Thread-1)" {
  component "ThreadLocal<StepContext>" as TL1
  component "StepContext" as SC1
  TL1 --> SC1: 保持
}

package "ワーカースレッド (Thread-2)" {
  component "ThreadLocal<StepContext>" as TL2
  component "null" as SC2
  TL2 --> SC2: 未初期化
}

note right of SC2
  ワーカースレッドでは
  StepContextが登録されていない
  →ScopeNotActiveException
end note

@enduml
```

### ChunkOrientedStep.processChunkConcurrentlyの実装

```java
private void processChunkConcurrently(Chunk<I> chunk, 
                                     StepContribution contribution) throws Exception {
    List<Future<O>> futures = new ArrayList<>();
    
    for (I item : chunk.getItems()) {
        // ❌問題: StepContextを伝播せずにタスクを投入
        Future<O> future = this.taskExecutor.submit(() -> {
            return processItem(item, contribution);
            // ↑ここで@StepScope Beanにアクセス
            // →StepSynchronizationManager.getContext()が呼ばれる
            // →ワーカースレッドにはコンテキストが無い
            // →ScopeNotActiveException
        });
        futures.add(future);
    }
    
    // 結果を収集
    for (Future<O> future : futures) {
        O processedItem = future.get(); // 例外が伝播される
        // ...
    }
}
```

### コンテキスト伝播の不足

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 200
}
:メインスレッド開始;

:StepSynchronizationManager.register();
note right
  StepContext登録
  （メインスレッドのThreadLocal）
end note

partition "TaskExecutor.submit()" {
  fork
    :ワーカースレッド1起動;
    :❌StepContext未登録;
    :@StepScope Bean取得試行;
    :❌ScopeNotActiveException;
  fork again
    :ワーカースレッド2起動;
    :❌StepContext未登録;
    :@StepScope Bean取得試行
    :❌ScopeNotActiveException;
  end fork
}

:処理失敗;

@enduml
```

### Spring Batch 5.xとの違い

Spring Batch 5.xでは`TaskletStep`が使用されており、マルチスレッド処理時のスコープ伝播が考慮されていました。Spring Batch 6.0で導入された`ChunkOrientedStep`では、この伝播メカニズムが実装されていません。

```plantuml
@startuml
skinparam backgroundColor transparent

state "Spring Batch 5.x\n(TaskletStep)" as V5 {
  [*] -> StepContext登録
  StepContext登録 -> マルチスレッド処理
  マルチスレッド処理: ✓コンテキスト伝播機能あり
  マルチスレッド処理 -> 正常動作
}

state "Spring Batch 6.0\n(ChunkOrientedStep)" as V6 {
  [*] -> StepContext登録
  StepContext登録 -> マルチスレッド処理
  マルチスレッド処理: ❌コンテキスト伝播機能なし
  マルチスレッド処理 -> ScopeNotActiveException
}

@enduml
```

## 対応方針

### 提案される修正案

`ChunkOrientedStep.processChunkConcurrently()`メソッドで、ワーカースレッドに`StepContext`を伝播させるよう修正します。

#### 修正前のコード

```java
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    return processItem(item, contribution);
    // ❌StepContextが無い
});
```

#### 修正後のコード（提案）

```java
Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> {
    try {
        // ✅現在のワーカースレッドのStepSynchronizationManagerにステップ実行を登録
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // ✅メモリリークを防ぐため、処理後にコンテキストをクリア
        StepSynchronizationManager.close();
    }
});
```

### 修正後の動作フロー

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam minClassWidth 150

participant "メインスレッド" as Main
participant "TaskExecutor" as Executor
participant "ワーカースレッド" as Worker
participant "StepSynchronizationManager" as Manager
participant "@StepScope Processor" as Processor

Main -> Manager: StepContextを登録\n(メインスレッド用)
activate Main

Main -> Executor: submit(処理タスク)
activate Executor

Executor -> Worker: 新しいスレッドで実行
activate Worker

Worker -> Manager: ✅StepContextを登録\n(ワーカースレッド用)
activate Manager
note right: stepExecutionを伝播

Worker -> Processor: process(item) 呼び出し
activate Processor

Processor -> Manager: StepContextを取得
Manager --> Processor: ✅コンテキスト返却
note right: ワーカースレッドの\nThreadLocalから取得成功

Processor -> Processor: 処理実行
Processor --> Worker: ✅処理結果返却
deactivate Processor

Worker -> Manager: ✅close()\nコンテキストクリア
deactivate Manager
note right: メモリリーク防止

Worker --> Executor: ✅成功
deactivate Worker

Executor --> Main: ✅完了
deactivate Executor
deactivate Main

@enduml
```

### コンテキスト伝播のライフサイクル

```plantuml
@startuml
skinparam backgroundColor transparent

:メインスレッド\nStepContext登録<#LightBlue>;

fork
  :ワーカースレッド1<#LightGreen>;
  :✅StepContext登録;
  :@StepScope Bean利用可能;
  :処理実行;
  :✅StepContext解放;
fork again
  :ワーカースレッド2<#LightGreen>;
  :✅StepContext登録;
  :@StepScope Bean利用可能;
  :処理実行;
  :✅StepContext解放;
fork again
  :ワーカースレッド3<#LightGreen>;
  :✅StepContext登録;
  :@StepScope Bean利用可能;
  :処理実行;
  :✅StepContext解放;
end fork

:すべてのワーカー完了;

:メインスレッド継続<#LightBlue>;

@enduml
```

### 修正の影響範囲

```plantuml
@startuml
skinparam componentStyle rectangle
skinparam backgroundColor transparent

component "ChunkOrientedStep" as Step {
  component "processChunkConcurrently()" as Concurrent
}

component "TaskExecutor" as Executor
component "StepSynchronizationManager" as Manager
component "@StepScope Beans" as Beans

Step --> Executor: submit()
note on link
  ✅修正箇所:
  タスク実行前に
  StepContext登録
end note

Executor --> Manager: register(stepExecution)
Manager --> Executor: コンテキスト有効化

Executor --> Beans: アクセス可能
note on link
  ✅@StepScope Bean
  正常に解決
end note

Executor --> Manager: close()
note on link
  finally節で
  必ずクリア
end note

@enduml
```

### 注意点とベストプラクティス

#### 1. メモリリークの防止

```java
Future<O> future = this.taskExecutor.submit(() -> {
    try {
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } finally {
        // ✅重要: 必ずclose()を呼ぶ
        // ThreadLocalに残ったStepContextを解放しないと
        // スレッドプールのスレッドが再利用される際に
        // 古いコンテキストが残り続ける
        StepSynchronizationManager.close();
    }
});
```

#### 2. StepExecutionの伝播

```plantuml
@startuml
skinparam backgroundColor transparent

package "processChunkConcurrently()メソッド" {
  component "stepExecution\n(メソッドパラメータ)" as SE
  component "ワーカータスク" as Task
  
  SE --> Task: キャプチャして渡す
  note on link
    ラムダ式で
    stepExecutionを参照
  end note
}

package "ワーカースレッド" {
  component "StepSynchronizationManager" as Manager
  component "@StepScope Bean" as Bean
  
  Manager --> Bean: コンテキスト提供
}

Task --> Manager: register(stepExecution)
note on link
  メインスレッドから
  受け取った値を使用
end note

@enduml
```

#### 3. 例外処理

```java
Future<O> future = this.taskExecutor.submit(() -> {
    try {
        StepSynchronizationManager.register(stepExecution);
        return processItem(item, contribution);
    } catch (Exception e) {
        // 例外が発生してもfinallyでcloseされる
        throw e;
    } finally {
        StepSynchronizationManager.close();
    }
});

try {
    O result = future.get(); // 例外は再スローされる
    // ...
} catch (ExecutionException e) {
    // ワーカースレッドでの例外を処理
    throw (Exception) e.getCause();
}
```

### 代替アプローチ: TaskDecorator使用

より汎用的な解決策として、`TaskDecorator`を使用してコンテキスト伝播を自動化する方法もあります：

```java
public class StepContextTaskDecorator implements TaskDecorator {
    private final StepExecution stepExecution;
    
    public StepContextTaskDecorator(StepExecution stepExecution) {
        this.stepExecution = stepExecution;
    }
    
    @Override
    public Runnable decorate(Runnable runnable) {
        return () -> {
            try {
                StepSynchronizationManager.register(stepExecution);
                runnable.run();
            } finally {
                StepSynchronizationManager.close();
            }
        };
    }
}

// TaskExecutor設定
ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
executor.setTaskDecorator(new StepContextTaskDecorator(stepExecution));
```

**メリット**: 各タスクで個別にregister/closeを呼ぶ必要がない
**デメリット**: `ChunkOrientedStep`の内部実装に依存

### 期待される最終的な動作

| 項目 | 修正前 | 修正後 |
|-----|-------|-------|
| シングルスレッド | ✓ 動作 | ✓ 動作 |
| マルチスレッド | ❌ ScopeNotActiveException | ✓ 動作 |
| @StepScope Bean | ❌ 解決失敗 | ✓ 正常に解決 |
| JobParameters注入 | ❌ 失敗 | ✓ 成功 |
| メモリリーク | - | ✓ 防止 |

### 関連機能への影響

```plantuml
@startuml
skinparam backgroundColor transparent

component "修正後の恩恵を受ける機能" as Benefits {
  [ItemProcessor (@StepScope)]
  [ItemReader (@StepScope)]
  [ItemWriter (@StepScope)]
  [@Value (jobParameters) 注入]
  [@Value (stepExecutionContext) 注入]
}

component "ChunkOrientedStep\n(マルチスレッド)" as Step

Step --> Benefits: すべて正常動作

note right of Benefits
  ワーカースレッドでも
  StepScopeが機能
end note

@enduml
```

**現在のステータス**: 開発チームへの問題報告済み。具体的な修正案が提示されており、実装待ちの状態です。コミュニティから動作する再現リポジトリの提供も可能との申し出があります。
