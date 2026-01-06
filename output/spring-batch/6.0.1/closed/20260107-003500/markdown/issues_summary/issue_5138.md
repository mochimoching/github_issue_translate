*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

パーティショナー（Partitioner）がステップ実行のメタデータを返しても、それらが`PartitionHandler`で処理される前にメタデータストアに永続化されない問題を修正しました。

**Partitionerとは**: 大量データを複数の小さなパーティションに分割し、並行処理するための機能です。各パーティションは独立したステップ実行として処理されます。

### 問題の発生条件

```java
@Bean
public Partitioner myPartitioner() {
    return gridSize -> {
        Map<String, ExecutionContext> partitions = new HashMap<>();
        for (int i = 0; i < gridSize; i++) {
            ExecutionContext context = new ExecutionContext();
            context.putString("partition", "partition-" + i);
            // パーティション固有のデータを設定
            partitions.put("partition" + i, context);
        }
        return partitions;
    };
}
```

**期待される動作**: パーティション情報がデータベースに保存されてから、`PartitionHandler`が処理を開始
**実際の動作**: パーティション情報がデータベースに保存される前に、`PartitionHandler`が処理を開始

## 原因

パーティショナーステップの実行フローにおいて、`ExecutionContext`の永続化タイミングが遅すぎました。

### 問題のシーケンス

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam minClassWidth 175

participant "PartitionStep" as PS
participant "Partitioner" as P
participant "JobRepository" as JR
participant "PartitionHandler" as PH
participant "Worker Steps" as WS

PS -> P: partition(gridSize)
activate P
P --> PS: Map<String, ExecutionContext>
note right
  partition0: {...}
  partition1: {...}
  partition2: {...}
end note
deactivate P

PS -> PS: StepExecutionを作成
note right
  partition0 -> stepExecution0
  partition1 -> stepExecution1
  partition2 -> stepExecution2
end note

PS -> PH: handle(partitions)
note right #FFB6C1
  問題：ExecutionContextが
  まだ保存されていない
end note
activate PH

PH -> WS: 並行実行開始
note right #FF6B6B
  Workerが起動時に
  ExecutionContextを取得しようとするが
  データベースに存在しない
end note

deactivate PH

PS -> JR: saveStepExecutions(stepExecutions)
note right #FFB6C1
  問題：ハンドラー起動後に
  ExecutionContextを保存
end note

@enduml
```

### タイミング図

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

start
:PartitionStep: partition()でコンテキスト生成;
:PartitionStep: StepExecution作成;
:PartitionStep: PartitionHandler.handle()呼び出し;

fork
  :PartitionHandler: Workerプロセス起動;
  :Worker: ExecutionContextを取得しようとする;
  note right
    問題：まだDBに存在しない
  end note
fork again
  :PartitionStep: JobRepository.saveStepExecutions();
  :Database: ExecutionContextを保存;
end fork

:Worker: ExecutionContextが見つからない;
:Worker: エラーまたは不完全な処理;

stop

@enduml
```

## 対応方針

**コミット**: [be464a6](https://github.com/spring-projects/spring-batch/commit/be464a6adfd655b4dbae0b798a3e9a2a4db43bc5)

`PartitionHandler.handle()`を呼び出す前に、パーティションのステップ実行とそのコンテキストをデータベースに保存するように修正しました。

### 修正内容

```java
// v6.0.0（問題のあるコード）
public class PartitionStep extends AbstractStep {
    @Override
    protected void doExecute(StepExecution stepExecution) {
        // 1. パーティション生成
        Map<String, ExecutionContext> partitions = partitioner.partition(gridSize);
        
        // 2. StepExecution作成
        Set<StepExecution> stepExecutions = createStepExecutions(partitions);
        
        // 3. ハンドラーで処理（❌ 保存前に実行）
        partitionHandler.handle(stepExecutions);
        
        // 4. StepExecutionを保存（❌ タイミングが遅い）
        jobRepository.saveStepExecutions(stepExecutions);
    }
}

// v6.0.1（修正後）
public class PartitionStep extends AbstractStep {
    @Override
    protected void doExecute(StepExecution stepExecution) {
        // 1. パーティション生成
        Map<String, ExecutionContext> partitions = partitioner.partition(gridSize);
        
        // 2. StepExecution作成
        Set<StepExecution> stepExecutions = createStepExecutions(partitions);
        
        // 3. StepExecutionを保存（✅ ハンドラー起動前に保存）
        jobRepository.saveStepExecutions(stepExecutions);
        
        // 4. ハンドラーで処理（✅ 保存後に実行）
        partitionHandler.handle(stepExecutions);
    }
}
```

### 修正後のシーケンス

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam minClassWidth 180

participant "PartitionStep" as PS
participant "Partitioner" as P
participant "JobRepository" as JR
participant "Database" as DB
participant "PartitionHandler" as PH
participant "Worker Steps" as WS

PS -> P: partition(gridSize)
activate P
P --> PS: Map<String, ExecutionContext>
deactivate P

PS -> PS: StepExecutionを作成

PS -> JR: saveStepExecutions(stepExecutions)
note right #90EE90
  修正：ハンドラー起動前に
  ExecutionContextを保存
end note
activate JR
JR -> DB: INSERT STEP_EXECUTION
JR -> DB: INSERT EXECUTION_CONTEXT
DB --> JR: 成功
deactivate JR

PS -> PH: handle(partitions)
note right #90EE90
  修正：ExecutionContextが
  既にDBに存在
end note
activate PH

PH -> WS: 並行実行開始
activate WS
WS -> DB: SELECT EXECUTION_CONTEXT
note right #90EE90
  ExecutionContextが
  正しく取得できる
end note
DB --> WS: ExecutionContext
WS -> WS: 処理実行
deactivate WS

deactivate PH

@enduml
```

### 使用例

```java
@Configuration
public class PartitionJobConfig {
    @Bean
    public Partitioner rangePartitioner() {
        return gridSize -> {
            Map<String, ExecutionContext> result = new HashMap<>();
            int range = 1000;
            for (int i = 0; i < gridSize; i++) {
                ExecutionContext context = new ExecutionContext();
                context.putInt("minValue", i * range);
                context.putInt("maxValue", (i + 1) * range);
                context.putString("name", "partition-" + i);
                result.put("partition" + i, context);
            }
            return result;
        };
    }
    
    @Bean
    public Step managerStep(JobRepository jobRepository,
                           Partitioner partitioner,
                           PartitionHandler partitionHandler) {
        return new StepBuilder("managerStep", jobRepository)
            .partitioner("workerStep", partitioner)
            .partitionHandler(partitionHandler)
            .build();
    }
    
    @Bean
    public Step workerStep(JobRepository jobRepository,
                          PlatformTransactionManager transactionManager) {
        return new StepBuilder("workerStep", jobRepository)
            .<Integer, Integer>chunk(100, transactionManager)
            .reader(new ItemReader<Integer>() {
                @Autowired
                private StepExecution stepExecution;
                
                @Override
                public Integer read() {
                    // v6.0.1では正しくExecutionContextが取得できる
                    ExecutionContext context = stepExecution.getExecutionContext();
                    int minValue = context.getInt("minValue");
                    int maxValue = context.getInt("maxValue");
                    // パーティション固有の処理
                }
            })
            .processor(item -> item * 2)
            .writer(items -> System.out.println(items))
            .build();
    }
}
```

### メリット

| 項目 | v6.0.0 | v6.0.1 |
|------|--------|--------|
| ExecutionContextの永続化 | ハンドラー起動後 | ハンドラー起動前 |
| Workerの起動時エラー | あり | なし |
| リモートパーティション対応 | 不完全 | 完全 |
| データ整合性 | 低い | 高い |

### リモートパーティショニングへの影響

特に、リモートパーティショニング（各パーティションが別プロセスで実行される）環境では、この問題の影響が顕著でした：

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

node "Manager Process" {
  [PartitionStep]
  [JobRepository]
  database "Database" as DB
}

node "Worker Process 1" {
  [Worker Step 1]
}

node "Worker Process 2" {
  [Worker Step 2]
}

[PartitionStep] --> DB : v6.0.0: 保存が遅い
[Worker Step 1] --> DB : ExecutionContext取得（❌ 失敗）
[Worker Step 2] --> DB : ExecutionContext取得（❌ 失敗）

@enduml
```

v6.0.1では、Workerプロセスが起動する前に必ずExecutionContextがデータベースに保存されているため、リモート環境でも正しく動作します。

この修正により、パーティション処理の信頼性が向上しました。
