*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました。*

# Issue #5093: ChunkOrientedStepBuilderがStepBuilderHelperのプロパティを適用しない問題の修正

## 課題概要

`ChunkOrientedStepBuilder`が、親クラス`StepBuilderHelper`で設定されたプロパティ(リスナー、トランザクション属性など)を適切に適用していない問題が報告されました。

**StepBuilderHelperとは**: Step構築時の共通プロパティ(名前、リスナー、トランザクション設定など)を保持する抽象基底クラスです。様々なStepBuilderで共通の設定を提供します。

## 問題の詳細

### 期待される動作

```java
Step step = new StepBuilder("myStep", jobRepository)
    .listener(myStepListener)  // ← StepBuilderHelperで設定
    .<String, String>chunk(10, transactionManager)
    .reader(reader())
    .writer(writer())
    .build();

// myStepListenerが適用されることを期待
```

### 実際の動作

`listener()`などの`StepBuilderHelper`で設定されたプロパティが、最終的な`Step`オブジェクトに適用されません。

## 原因

`ChunkOrientedStepBuilder`の`build()`メソッドが、`StepBuilderHelper`のプロパティを適切に引き継いでいませんでした:

```java
// 問題のあるコード
@Override
public TaskletStep build() {
    TaskletStep step = new TaskletStep(this.name);
    super.enhance(step);  // ← このメソッドの呼び出しが不完全
    
    // ChunkOrientedStepBuilder固有の設定
    step.setTasklet(this.tasklet);
    step.setChunkSize(this.chunkSize);
    
    return step;
    // ← StepBuilderHelperのリスナーやトランザクション属性が適用されない!
}
```

## 対応方針

```java
// 修正後のコード
@Override
public TaskletStep build() {
    TaskletStep step = new TaskletStep(this.name);
    
    // ✅ StepBuilderHelperのプロパティを適用
    super.enhance(step);
    
    // ChunkOrientedStepBuilder固有の設定
    step.setTasklet(this.tasklet);
    step.setChunkSize(this.chunkSize);
    
    // ✅ StepBuilderHelperで設定されたリスナーを適用
    if (this.listeners != null) {
        for (StepExecutionListener listener : this.listeners) {
            step.registerStepExecutionListener(listener);
        }
    }
    
    // ✅ トランザクション属性を適用
    if (this.transactionAttribute != null) {
        step.setTransactionAttribute(this.transactionAttribute);
    }
    
    return step;
}
```

## 使用例

### リスナーの適用

```java
@Bean
public Step myStep(JobRepository jobRepository,
                   PlatformTransactionManager transactionManager,
                   StepExecutionListener myListener) {
    return new StepBuilder("myStep", jobRepository)
        .listener(myListener)  // ← StepBuilderHelperメソッド
        .<String, String>chunk(10, transactionManager)
        .reader(reader())
        .processor(processor())
        .writer(writer())
        .build();
    // 修正後: myListenerが正しく適用される ✅
}
```

### トランザクション属性の設定

```java
@Bean
public Step myStep(JobRepository jobRepository,
                   PlatformTransactionManager transactionManager) {
    
    DefaultTransactionAttribute txAttribute = new DefaultTransactionAttribute();
    txAttribute.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRED);
    txAttribute.setIsolationLevel(TransactionDefinition.ISOLATION_READ_COMMITTED);
    txAttribute.setTimeout(30);
    
    return new StepBuilder("myStep", jobRepository)
        .transactionAttribute(txAttribute)  // ← StepBuilderHelperメソッド
        .<Order, Order>chunk(100, transactionManager)
        .reader(orderReader())
        .writer(orderWriter())
        .build();
    // 修正後: トランザクション属性が正しく適用される ✅
}
```

### 複数のリスナー登録

```java
@Bean
public Step importStep(JobRepository jobRepository,
                       PlatformTransactionManager transactionManager) {
    return new StepBuilder("importStep", jobRepository)
        .listener(loggingListener())      // ログ記録
        .listener(metricsListener())      // メトリクス収集
        .listener(notificationListener()) // 通知送信
        .<Customer, Customer>chunk(50, transactionManager)
        .reader(customerReader())
        .writer(customerWriter())
        .build();
    // 修正後: すべてのリスナーが正しく適用される ✅
}
```

## 学習ポイント

### StepBuilder階層構造

```
StepBuilderHelper (抽象基底クラス)
├── 共通プロパティ
│   ├── name (Step名)
│   ├── listeners (リスナーリスト)
│   ├── transactionAttribute (トランザクション設定)
│   ├── allowStartIfComplete (完了済み再実行許可)
│   └── startLimit (開始回数制限)
│
├── TaskletStepBuilder (Tasklet用)
├── SimpleStepBuilder (基本Chunk処理用)
└── ChunkOrientedStepBuilder (高度なChunk処理用)
    ├── faultTolerant設定
    ├── retry設定
    └── skip設定
```

### StepBuilderHelperの主要メソッド

| メソッド | 用途 | 例 |
|---------|------|---|
| listener() | StepExecutionListenerを追加 | `.listener(myListener)` |
| transactionAttribute() | トランザクション属性を設定 | `.transactionAttribute(attr)` |
| allowStartIfComplete() | 完了済みStepの再実行を許可 | `.allowStartIfComplete(true)` |
| startLimit() | Step開始回数の上限を設定 | `.startLimit(3)` |

### ビルダーパターンとメソッドチェーン

```java
// メソッドチェーンで設定を積み上げる
Step step = new StepBuilder("myStep", jobRepository)
    // StepBuilderHelperのメソッド
    .listener(listener1)
    .listener(listener2)
    .allowStartIfComplete(true)
    .startLimit(5)
    
    // ChunkOrientedStepBuilderのメソッド
    .<Input, Output>chunk(100, transactionManager)
    .reader(reader)
    .processor(processor)
    .writer(writer)
    
    // フォールトトレラント設定
    .faultTolerant()
    .retry(SQLException.class)
    .retryLimit(3)
    .skip(ValidationException.class)
    .skipLimit(10)
    
    // 最終的なビルド
    .build();
```

### StepExecutionListenerの実装例

```java
@Component
public class CustomStepListener implements StepExecutionListener {
    
    private static final Logger logger = LoggerFactory.getLogger(CustomStepListener.class);
    
    @Override
    public void beforeStep(StepExecution stepExecution) {
        logger.info("Step開始: {}", stepExecution.getStepName());
        stepExecution.getExecutionContext().putLong("startTime", System.currentTimeMillis());
    }
    
    @Override
    public ExitStatus afterStep(StepExecution stepExecution) {
        long startTime = stepExecution.getExecutionContext().getLong("startTime");
        long duration = System.currentTimeMillis() - startTime;
        
        logger.info("Step完了: {}, 所要時間: {}ms, 読み込み: {}, 書き込み: {}, スキップ: {}",
            stepExecution.getStepName(),
            duration,
            stepExecution.getReadCount(),
            stepExecution.getWriteCount(),
            stepExecution.getSkipCount());
        
        return stepExecution.getExitStatus();
    }
}
```

### トランザクション属性のカスタマイズ

```java
@Bean
public Step heavyProcessingStep(JobRepository jobRepository,
                                PlatformTransactionManager transactionManager) {
    
    // 長時間実行される処理用のトランザクション設定
    DefaultTransactionAttribute txAttr = new DefaultTransactionAttribute();
    txAttr.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRED);
    txAttr.setIsolationLevel(TransactionDefinition.ISOLATION_READ_COMMITTED);
    txAttr.setTimeout(300);  // 5分
    txAttr.setReadOnly(false);
    
    return new StepBuilder("heavyProcessingStep", jobRepository)
        .transactionAttribute(txAttr)  // ✅ カスタム設定を適用
        .<LargeData, ProcessedData>chunk(10, transactionManager)  // 小さいChunk
        .reader(largeDataReader())
        .processor(heavyProcessor())
        .writer(processedDataWriter())
        .build();
}
```

## 注意点

- この修正により、既存のコードで意図せずリスナーが二重登録される可能性があります
- 修正前の回避策として手動で設定していた場合、重複を削除してください
- トランザクション属性を明示的に設定しない場合、デフォルト設定が使用されます
