*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5150: RemotePartitioningWorkerStepBuilderの汎用メソッドを公開

## 課題概要

Spring Batchのリモートパーティショニング機能において、ワーカーステップの設定を行う`RemotePartitioningWorkerStepBuilder`クラスに、汎用的な設定メソッド（`repository()`、`transactionManager()`、`listener()`など）が提供されていない問題です。これらのメソッドを公開することで、より柔軟なワーカーステップの設定が可能になります。

### 用語解説

- **リモートパーティショニング**: パーティション処理を複数のJVMやマシンに分散して実行する機能。マネージャーとワーカーが別プロセスで動作し、メッセージング（JMSなど）を介して通信する
- **マネージャー**: パーティションを作成し、ワーカーに処理を依頼する側
- **ワーカー**: マネージャーから受け取ったパーティションを実際に処理する側
- **JobRepository**: ジョブ・ステップの実行情報を管理するコンポーネント
- **TransactionManager**: トランザクション管理を行うコンポーネント
- **StepExecutionListener**: ステップの開始・終了時に処理を実行するリスナー
- **ビルダーパターン**: オブジェクトの生成を段階的に行うデザインパターン。メソッドチェーンで設定を追加できる

### 問題のシナリオ

リモートパーティショニングのワーカーステップを設定する際、以下のような制限がありました：

```java
@Configuration
public class WorkerConfiguration {
    
    @Bean
    public Step workerStep(JobRepository jobRepository,
                          PlatformTransactionManager transactionManager,
                          StepExecutionListener listener) {
        
        return new RemotePartitioningWorkerStepBuilder("workerStep")
                .inputChannel(inputChannel)
                .outputChannel(outputChannel)
                .chunk(100)
                .reader(itemReader())
                .writer(itemWriter())
                // ❌ 以下のメソッドが使えない
                // .repository(customJobRepository)
                // .transactionManager(customTransactionManager)
                // .listener(listener)
                .build();
    }
}
```

### 利用できなかった設定

| メソッド | 用途 | 問題 |
|---------|------|------|
| `repository()` | カスタムJobRepositoryの設定 | ❌ メソッドが存在しない |
| `transactionManager()` | カスタムTransactionManagerの設定 | ❌ メソッドが存在しない |
| `listener()` | StepExecutionListenerの追加 | ❌ メソッドが存在しない |
| `taskExecutor()` | TaskExecutorの設定 | ❌ メソッドが存在しない |

### 影響

1. **カスタマイズの制限**: デフォルト以外の`JobRepository`や`TransactionManager`を使いたい場合に設定できない

2. **リスナーの追加不可**: ステップの開始・終了時に独自の処理を追加できない

3. **通常のステップビルダーとの不整合**: 他の`StepBuilder`では使えるメソッドが、`RemotePartitioningWorkerStepBuilder`では使えない

### 回避策（修正前）

```java
// ❌ ビルダーで設定できないため、手動で設定する必要がある
@Bean
public Step workerStep() {
    RemotePartitioningWorkerStepBuilder builder = 
        new RemotePartitioningWorkerStepBuilder("workerStep");
    
    Step step = builder
            .inputChannel(inputChannel)
            .outputChannel(outputChannel)
            .chunk(100)
            .reader(itemReader())
            .writer(itemWriter())
            .build();
    
    // ❌ リスナーを後から追加（ビルダーパターンの利点が失われる）
    ((AbstractStep) step).registerStepExecutionListener(listener);
    
    return step;
}
```

## 原因

`RemotePartitioningWorkerStepBuilder`の実装において、親クラス（`AbstractTaskletStepBuilder`や`StepBuilder`）で定義されている汎用的な設定メソッドが公開されていませんでした。これらのメソッドは`protected`や`private`として定義されており、外部から呼び出すことができない状態でした。

### 詳細な原因

#### クラス階層

```
Object
  ↓
StepBuilderHelper (抽象クラス)
  ├─ repository, transactionManager などの基本設定を保持
  ↓
AbstractTaskletStepBuilder (抽象クラス)
  ├─ listener, taskExecutor などの設定を保持
  ↓
RemotePartitioningWorkerStepBuilder
  ├─ inputChannel, outputChannel などの設定
  ❌ 親クラスのメソッドが公開されていない
```

#### 修正前の実装（イメージ）

```java
// 親クラス: StepBuilderHelper
public abstract class StepBuilderHelper<B extends StepBuilderHelper<B>> {
    
    protected JobRepository jobRepository;
    protected PlatformTransactionManager transactionManager;
    
    // ❌ protectedメソッド（サブクラスでオーバーライドして公開する必要がある）
    protected B repository(JobRepository jobRepository) {
        this.jobRepository = jobRepository;
        return self();
    }
    
    protected B transactionManager(PlatformTransactionManager transactionManager) {
        this.transactionManager = transactionManager;
        return self();
    }
}

// 親クラス: AbstractTaskletStepBuilder
public abstract class AbstractTaskletStepBuilder<B extends AbstractTaskletStepBuilder<B>> 
        extends StepBuilderHelper<B> {
    
    protected List<StepExecutionListener> listeners = new ArrayList<>();
    
    // ❌ protectedメソッド
    protected B listener(StepExecutionListener listener) {
        this.listeners.add(listener);
        return self();
    }
}

// RemotePartitioningWorkerStepBuilder（修正前）
public class RemotePartitioningWorkerStepBuilder 
        extends AbstractTaskletStepBuilder<RemotePartitioningWorkerStepBuilder> {
    
    private MessageChannel inputChannel;
    private MessageChannel outputChannel;
    
    // ✅ リモートパーティショニング固有のメソッドは公開
    public RemotePartitioningWorkerStepBuilder inputChannel(MessageChannel inputChannel) {
        this.inputChannel = inputChannel;
        return this;
    }
    
    public RemotePartitioningWorkerStepBuilder outputChannel(MessageChannel outputChannel) {
        this.outputChannel = outputChannel;
        return this;
    }
    
    // ❌ 親クラスのメソッドを公開していない
    // repository(), transactionManager(), listener() などが使えない
}
```

### 問題の整理

```
【他のStepBuilderの場合】
StepBuilder
  ├─ 汎用メソッドを公開 ✅
  ├─ .repository() ✅
  ├─ .transactionManager() ✅
  └─ .listener() ✅

【RemotePartitioningWorkerStepBuilderの場合（修正前）】
RemotePartitioningWorkerStepBuilder
  ├─ リモートパーティショニング固有のメソッドのみ公開
  ├─ .inputChannel() ✅
  ├─ .outputChannel() ✅
  ├─ .repository() ❌ 使えない
  ├─ .transactionManager() ❌ 使えない
  └─ .listener() ❌ 使えない
```

## 対応方針

親クラスで定義されている汎用的な設定メソッドを、`RemotePartitioningWorkerStepBuilder`でオーバーライドして公開するように修正されました。

### 修正内容

[コミット 2e42862](https://github.com/spring-projects/spring-batch/commit/2e428628af6ad2ba6cfaa96aae5eba1c7bd7e3e1)

```java
// RemotePartitioningWorkerStepBuilder（修正後）
public class RemotePartitioningWorkerStepBuilder 
        extends AbstractTaskletStepBuilder<RemotePartitioningWorkerStepBuilder> {
    
    private MessageChannel inputChannel;
    private MessageChannel outputChannel;
    
    // ✅ リモートパーティショニング固有のメソッド
    public RemotePartitioningWorkerStepBuilder inputChannel(MessageChannel inputChannel) {
        this.inputChannel = inputChannel;
        return this;
    }
    
    public RemotePartitioningWorkerStepBuilder outputChannel(MessageChannel outputChannel) {
        this.outputChannel = outputChannel;
        return this;
    }
    
    // ✅ 修正: 親クラスのメソッドをオーバーライドして公開
    @Override
    public RemotePartitioningWorkerStepBuilder repository(JobRepository jobRepository) {
        return super.repository(jobRepository);
    }
    
    @Override
    public RemotePartitioningWorkerStepBuilder transactionManager(
            PlatformTransactionManager transactionManager) {
        return super.transactionManager(transactionManager);
    }
    
    @Override
    public RemotePartitioningWorkerStepBuilder listener(StepExecutionListener listener) {
        return super.listener(listener);
    }
    
    @Override
    public RemotePartitioningWorkerStepBuilder taskExecutor(TaskExecutor taskExecutor) {
        return super.taskExecutor(taskExecutor);
    }
    
    // その他の汎用メソッドも同様に公開...
}
```

### 修正後の使い方

```java
@Configuration
public class WorkerConfiguration {
    
    @Bean
    public Step workerStep(JobRepository customJobRepository,
                          PlatformTransactionManager customTransactionManager,
                          StepExecutionListener customListener,
                          TaskExecutor taskExecutor) {
        
        return new RemotePartitioningWorkerStepBuilder("workerStep")
                // ✅ リモートパーティショニング固有の設定
                .inputChannel(inputChannel)
                .outputChannel(outputChannel)
                
                // ✅ 修正後: 汎用的な設定が可能になった
                .repository(customJobRepository)
                .transactionManager(customTransactionManager)
                .listener(customListener)
                .taskExecutor(taskExecutor)
                
                // ✅ チャンク設定
                .chunk(100)
                .reader(itemReader())
                .writer(itemWriter())
                
                .build();
    }
}
```

### 公開されたメソッドの一覧

| メソッド | 用途 | 例 |
|---------|------|-----|
| `repository()` | カスタムJobRepositoryの設定 | `.repository(myJobRepository)` |
| `transactionManager()` | カスタムTransactionManagerの設定 | `.transactionManager(myTxManager)` |
| `listener()` | StepExecutionListenerの追加 | `.listener(myListener)` |
| `taskExecutor()` | TaskExecutorの設定 | `.taskExecutor(myTaskExecutor)` |
| `exceptionHandler()` | 例外ハンドラーの設定 | `.exceptionHandler(myHandler)` |
| `stepOperations()` | StepOperationsの設定 | `.stepOperations(myOperations)` |

### 実装例: カスタムリスナー

```java
// カスタムリスナーの実装
@Component
public class WorkerStepListener implements StepExecutionListener {
    
    private static final Logger log = LoggerFactory.getLogger(WorkerStepListener.class);
    
    @Override
    public void beforeStep(StepExecution stepExecution) {
        log.info("Worker step started: {}", stepExecution.getStepName());
        log.info("Partition: {}", stepExecution.getExecutionContext().get("partition"));
    }
    
    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        log.info("Worker step completed: {}", stepExecution.getStepName());
        log.info("Read count: {}", stepExecution.getReadCount());
        log.info("Write count: {}", stepExecution.getWriteCount());
        return stepExecution.getExitStatus();
    }
}

// ビルダーで設定
@Bean
public Step workerStep(WorkerStepListener listener) {
    return new RemotePartitioningWorkerStepBuilder("workerStep")
            .inputChannel(inputChannel)
            .outputChannel(outputChannel)
            .listener(listener)  // ✅ リスナーを追加
            .chunk(100)
            .reader(itemReader())
            .writer(itemWriter())
            .build();
}
```

### 実装例: カスタムTransactionManager

```java
// 複数データソースのシナリオ
@Configuration
public class WorkerConfiguration {
    
    @Bean
    public PlatformTransactionManager primaryTransactionManager(
            @Qualifier("primaryDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
    
    @Bean
    public PlatformTransactionManager secondaryTransactionManager(
            @Qualifier("secondaryDataSource") DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
    
    @Bean
    public Step workerStep(
            @Qualifier("secondaryTransactionManager") 
            PlatformTransactionManager txManager) {
        
        return new RemotePartitioningWorkerStepBuilder("workerStep")
                .inputChannel(inputChannel)
                .outputChannel(outputChannel)
                .transactionManager(txManager)  // ✅ セカンダリDBのトランザクションマネージャーを使用
                .chunk(100)
                .reader(itemReader())
                .writer(itemWriter())
                .build();
    }
}
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.1で改善
- **関連クラス**:
  - `RemotePartitioningWorkerStepBuilder` - ワーカーステップのビルダー
  - `RemotePartitioningManagerStepBuilder` - マネージャーステップのビルダー
  - `AbstractTaskletStepBuilder` - ステップビルダーの基底クラス
  - `StepBuilderHelper` - ステップビルダーの共通処理
  - `StepExecutionListener` - ステップリスナーのインターフェース
- **リモートパーティショニングの構成**:
  - **マネージャー側**: パーティションを作成し、メッセージで送信
  - **ワーカー側**: メッセージを受信し、パーティションを処理
  - **メッセージング**: JMS、RabbitMQ、Kafkaなどを使用
- **ビルダーパターンのメリット**:
  - メソッドチェーンで直感的に設定できる
  - 型安全な設定が可能
  - 設定の順序に依存しない
- **設定の優先順位**:
  1. ビルダーで明示的に設定した値
  2. Spring Beanとして登録されたデフォルト値
  3. フレームワークのデフォルト値
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5150
