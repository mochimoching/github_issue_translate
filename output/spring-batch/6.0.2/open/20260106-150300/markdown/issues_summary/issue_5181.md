*（このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました）*

## 課題概要

`@SpringBatchTest`アノテーションを使用したテスト環境において、`StepScopeTestUtils`を利用する際に`StepContext`の競合が発生し、カスタム`JobParameters`が正しく注入されない問題です。

**@SpringBatchTestとは**: Spring Batch 4.0から導入されたテスト支援機能で、`StepScope`や`JobScope`のBeanを簡単にテストできるよう、必要なコンポーネント（`JobLauncherTestUtils`、`JobRepositoryTestUtils`など）を自動的にセットアップするアノテーションです。

### 問題の発生状況

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam minClassWidth 150

participant "テストコード" as Test
participant "StepScopeTestUtils" as Utils
participant "MetaDataInstanceFactory" as Factory
participant "StepSynchronizationManager" as Manager
participant "StepScopeTestExecutionListener" as Listener

Test -> Listener: @SpringBatchTest初期化
activate Listener
Listener -> Manager: StepContextを登録\n(stepName="", jobExecutionId=-1L, id=1234L)
note right: リスナーがデフォルト値で\nコンテキストを作成
deactivate Listener

Test -> Factory: createStepExecution(jobParameters)
activate Factory
Factory --> Test: StepExecution返却\n(stepName="dummy", jobExecutionId=-1L, id=1234L)
note right: 同じID値を使用
deactivate Factory

Test -> Utils: doInStepScope(stepExecution, ...)
activate Utils
Utils -> Manager: computeIfAbsent(stepExecution, ...)
note right: stepName, jobExecutionId, idで等価判定
Manager --> Manager: 既存コンテキスト発見
note right: リスナーが登録した\nコンテキスト（JobParameters無し）を返却
Manager --> Utils: 既存コンテキスト返却
Utils -> Test: 実行（間違ったコンテキスト使用）
note right: カスタムJobParametersが注入されない\n→テスト失敗
deactivate Utils

@enduml
```

### 問題の核心

| コンポーネント | 使用する値 | stepName | jobExecutionId | id |
|--------------|----------|----------|---------------|-----|
| StepScopeTestExecutionListener | デフォルト値 | "" | -1L | 1234L |
| MetaDataInstanceFactory | デフォルト値 | "dummy" | -1L | 1234L |
| 等価性判定 | - | ✓ 一致 | ✓ 一致 | ✓ 一致 |

**結果**: `SynchronizationManagerSupport.contexts`マップ内で同一キーとして扱われる

## 原因

### 1. StepExecutionの等価性判定

`StepExecution`クラスは、以下の3つのフィールドで等価性を判断します：

```java
public class StepExecution {
    private String stepName;
    private Long jobExecutionId;
    private Long id;
    
    @Override
    public boolean equals(Object obj) {
        // stepName、jobExecutionId、idの3つで判定
        // ...
    }
}
```

### 2. MetaDataInstanceFactoryの静的デフォルト値

`MetaDataInstanceFactory`は、すべてのフィールドに静的なデフォルト値を提供します：

```java
public class MetaDataInstanceFactory {
    public static StepExecution createStepExecution(JobParameters jobParameters) {
        return new StepExecution(
            "dummy",  // 固定値
            new JobExecution(
                new JobInstance(-1L, "job"), // 固定値
                jobParameters
            )
        );
        // stepExecution.setId(1234L); // 固定値
    }
}
```

### 3. コンテキストマップの動作

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam componentStyle rectangle

package "SynchronizationManagerSupport" {
  component "contexts: Map<StepExecution, StepContext>" as Map
  
  note right of Map
    キー: StepExecution (equals/hashCode判定)
    値: StepContext (JobParameters含む)
  end note
}

package "StepScopeTestExecutionListener登録" as Reg1 {
  component "StepExecution\n(stepName='', id=1234L)" as SE1
  component "StepContext\n(JobParameters=空)" as SC1
  
  SE1 -down-> SC1
}

package "StepScopeTestUtils登録試行" as Reg2 {
  component "StepExecution\n(stepName='dummy', id=1234L)" as SE2
  component "StepContext\n(JobParameters=カスタム値)" as SC2
  
  SE2 -down-> SC2
}

Reg1 -right-> Map: ① computeIfAbsent()\n新規登録成功
note on link
  キーが存在しないため
  新しいエントリーを作成
end note

Reg2 -right-> Map: ② computeIfAbsent()\n既存キー発見
note on link
  equals()がtrueを返すため
  既存のエントリー(SC1)を返却
  SC2は登録されない
end note

@enduml
```

### 問題の流れ

```plantuml
@startuml
skinparam backgroundColor transparent

:@SpringBatchTest初期化;

:StepScopeTestExecutionListener起動;

:デフォルトStepContextを\nSynchronizationManagerに登録;
note right
  StepExecution(id=1234L)
  StepContext(JobParameters=空)
end note

:テストメソッド実行開始;

:MetaDataInstanceFactory.createStepExecution()\nカスタムJobParametersで呼び出し;

:StepScopeTestUtils.doInStepScope()実行;

:computeIfAbsent()でコンテキスト取得;

if (キーが既に存在?) then (yes)
  :既存コンテキスト返却;
  note right
    JobParameters無しの
    古いコンテキスト
  end note
else (no)
  :新規コンテキスト作成;
endif

:StepScope Beanの初期化試行;

:JobParameters注入失敗;
note right
  #{jobParameters['testParam']}
  → null
end note

:テスト失敗;

@enduml
```

## 対応方針

### 提案される修正アプローチ

現時点では開発チームからの公式な修正はありませんが、以下の修正方法が考えられます：

#### 修正案1: MetaDataInstanceFactoryのID生成をランダム化

```java
public class MetaDataInstanceFactory {
    public static StepExecution createStepExecution(JobParameters jobParameters) {
        StepExecution stepExecution = new StepExecution(
            "test-step-" + UUID.randomUUID().toString(), // ユニーク化
            new JobExecution(
                new JobInstance(System.nanoTime(), "test-job"), // ユニーク化
                jobParameters
            )
        );
        stepExecution.setId(System.nanoTime()); // ユニーク化
        return stepExecution;
    }
}
```

**メリット**: 
- ID競合が確実に回避される
- 各テストケースで独立したコンテキストが作成される

**デメリット**:
- 既存のテストコードへの影響が大きい可能性

#### 修正案2: StepScopeTestUtilsでコンテキストを強制上書き

```java
public class StepScopeTestUtils {
    public static <T> T doInStepScope(StepExecution stepExecution, Callable<T> callable) {
        // 既存コンテキストを削除してから新規登録
        StepSynchronizationManager.close();
        StepSynchronizationManager.register(stepExecution);
        try {
            return callable.call();
        } finally {
            StepSynchronizationManager.close();
        }
    }
}
```

**メリット**:
- テストコードへの影響が少ない
- 意図したJobParametersが確実に使用される

**デメリット**:
- 既存のコンテキストが破棄される動作が副作用として残る

#### 修正案3: StepScopeTestExecutionListenerの登録タイミング変更

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam state {
  MinimumWidth 200
}

state "現在の動作" as Current {
  state "テストクラス初期化" as CI1
  state "リスナー実行" as L1
  state "テストメソッド実行" as T1
  
  CI1 --> L1: @SpringBatchTest
  L1: デフォルトコンテキスト登録
  L1 --> T1
}

state "修正後の動作" as Fixed {
  state "テストクラス初期化" as CI2
  state "テストメソッド実行" as T2
  
  CI2 --> T2: @SpringBatchTest
  T2: 必要に応じて\nコンテキスト登録
  note right of T2
    StepScopeTestUtils呼び出し時に
    初めてコンテキストを作成
  end note
}

@enduml
```

**メリット**:
- 根本的な競合を回避
- より柔軟なテスト設定が可能

**デメリット**:
- `@SpringBatchTest`の動作変更が大きい
- 既存テストへの影響が不明

### 回避策（ユーザー側での対処）

開発チームの修正を待つ間、以下の回避策が利用できます：

```java
@SpringBatchTest
@SpringBootTest
public class WorkaroundTest {
    
    @Autowired
    private Tasklet myTasklet;
    
    @Test
    void workaroundTest() throws Exception {
        // 回避策: StepScopeTestExecutionListenerを使わず、
        // 手動でコンテキストを管理
        
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", "HelloBatch")
                .toJobParameters();
        
        StepExecution stepExecution = new StepExecution(
                "test-step-" + System.nanoTime(), // ユニークな名前
                new JobExecution(
                        new JobInstance(System.nanoTime(), "test-job"),
                        jobParameters
                )
        );
        stepExecution.setId(System.nanoTime()); // ユニークなID
        
        // 既存コンテキストをクリアしてから登録
        StepSynchronizationManager.close();
        StepSynchronizationManager.register(stepExecution);
        
        try {
            myTasklet.execute(stepExecution.createStepContribution(), null);
            String result = stepExecution.getExecutionContext().getString("result");
            assertEquals("HelloBatch", result);
        } finally {
            StepSynchronizationManager.close();
        }
    }
}
```

### 影響範囲の比較

| 修正案 | 影響コンポーネント | 既存テストへの影響 | 実装難易度 |
|-------|-----------------|-----------------|----------|
| 修正案1: ID生成ランダム化 | MetaDataInstanceFactory | 中 | 低 |
| 修正案2: コンテキスト強制上書き | StepScopeTestUtils | 低 | 低 |
| 修正案3: リスナー登録タイミング変更 | StepScopeTestExecutionListener | 高 | 中 |
| 回避策: 手動コンテキスト管理 | ユーザーコード | なし | 低 |

### 期待される最終的な動作

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam minClassWidth 150

participant "テストコード" as Test
participant "StepScopeTestUtils" as Utils
participant "MetaDataInstanceFactory" as Factory
participant "StepSynchronizationManager" as Manager

Test -> Factory: createStepExecution(jobParameters)
activate Factory
Factory --> Test: StepExecution返却\n(ユニークなID)
note right: 毎回異なるIDを生成
deactivate Factory

Test -> Utils: doInStepScope(stepExecution, ...)
activate Utils
Utils -> Manager: register(stepExecution)
note right: 新しいコンテキストを登録
Manager --> Manager: 新規コンテキスト作成
note right: カスタムJobParametersを含む
Utils -> Test: 実行（正しいコンテキスト使用）
note right: JobParameters正常に注入\n→テスト成功
deactivate Utils

@enduml
```

**現在のステータス**: 開発チームへの問題報告済み。修正方針の決定待ちの状態です。
