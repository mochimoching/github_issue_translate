*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました。*

## 課題概要

Spring Batchのテスト機能において、`@SpringBatchTest`アノテーションと`StepScopeTestUtils`を併用した際に、`StepContext`の競合が発生する問題です。

**`@SpringBatchTest`とは**: Spring Batchのテストを簡単に行うためのアノテーションで、テストクラスに付与することで、`StepScope`や`JobScope`のBeanを自動的にテストできる環境を提供します。

**`StepScope`とは**: Spring BatchにおけるSpringのスコープの一つで、ステップ実行中のみ有効なBeanを定義するために使用されます。`JobParameters`などのステップ実行時の情報にアクセスできます。

**`StepScopeTestUtils`とは**: `StepScope` Beanを単体テストする際に、ステップコンテキストを手動で設定するユーティリティクラスです。

**問題の状況**:
- テストクラスに`@SpringBatchTest`を付与
- テストメソッド内で`StepScopeTestUtils.doInStepScope()`を使用
- `StepScope`で定義されたBeanが正しく動作せず、`JobParameters`を参照できない

**具体的な事象**:
```java
@Test
void reproduceIdCollisionBug() throws Exception {
    String expectedValue = "HelloBatch";
    JobParameters jobParameters = new JobParametersBuilder()
        .addString("testParam", expectedValue)
        .toJobParameters();
    
    StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);
    
    StepScopeTestUtils.doInStepScope(stepExecution, () ->
        issueReproductionTasklet.execute(...)
    );
    
    String actualValue = stepExecution.getExecutionContext().getString("result");
    assertEquals(expectedValue, actualValue); // 失敗: actualValueがnull
}
```

```bash
エラー: Value for key=[result] is not of type: [class java.lang.String], it is [null]
```

## 原因

`MetaDataInstanceFactory`がすべての`StepExecution`インスタンスに対して固定のデフォルト値（ID=1234L）を使用するため、`SynchronizationManagerSupport.contexts`マップ内でキーの競合が発生することが原因です。

**詳細な原因分析**:

1. **StepExecutionの等価性判定**:
```java
// StepExecutionは以下の3つのフィールドで等価性を判断
- stepName
- jobExecutionId
- id
```

2. **MetaDataInstanceFactoryのデフォルト値**:
```java
// MetaDataInstanceFactory.java
public static StepExecution createStepExecution() {
    return new StepExecution("step", new JobExecution(1234L), 1234L);
    // すべてのインスタンスが同じID（1234L）を使用
}
```

3. **競合の発生メカニズム**:

| タイミング | 処理 | StepSynchronizationManager.contexts |
|----------|------|-------------------------------------|
| 1. テスト開始 | `@SpringBatchTest`の`StepScopeTestExecutionListener`が起動 | `{StepExecution(id=1234L) → Context_A}` |
| 2. テストメソッド実行 | `MetaDataInstanceFactory.createStepExecution(jobParameters)`を作成 | - |
| 3. StepScopeTestUtils実行 | 新しいコンテキストを登録しようとする | `computeIfAbsent(StepExecution(id=1234L), ...)` |
| 4. **競合発生** | 同じキー（id=1234L）が既に存在するため、Context_A（リスナーが登録したもの）が返される | `{StepExecution(id=1234L) → Context_A}` のまま |
| 5. Tasklet実行 | `JobParameters`を参照しようとするが、Context_Aには`JobParameters`が含まれていない | `testParam`がnullとして解決される |

4. **なぜContext_AにJobParametersがないのか**:
   - `StepScopeTestExecutionListener`は、テスト開始時に空の`JobParameters`でコンテキストを初期化
   - `StepScopeTestUtils`は、カスタム`JobParameters`を含む新しいコンテキストを登録しようとする
   - しかし、ID競合により既存のContext_A（空の`JobParameters`）が使用される

**Spring Batch 5.xと6.xの違い**:
- Spring Batch 6.x以降、`MetaDataInstanceFactory`がデフォルトID（1234L）を使用するようになった
- 5.2.3以降で同様の問題が発生

## 対応方針

**現在の回避策**:

テストクラス内で`getStepExecution()`メソッドを明示的に定義し、デフォルトID（1234L）とは異なるIDを持つ`StepExecution`を返すようにします。

```java
/**
 * 回避策: ID競合を避けるため、テストクラスでgetStepExecution()を定義
 * デフォルト以外のIDまたは名前を提供することで、リスナーによって登録された
 * コンテキストがStepScopeTestUtilsで作成されたものと競合しないことを保証
 */
public StepExecution getStepExecution() {
    return MetaDataInstanceFactory.createStepExecution("uniqueStep", -1L);
    // デフォルト（1234L）と異なるIDを使用
}
```

**テスト結果**:
```bash
> Task :test
BUILD SUCCESSFUL in 3s
```

**根本的な修正方針**:

報告者は、最適な修正方法の決定は簡単ではないと述べています。以下のいずれかのアプローチが必要と考えられます：

1. **`MetaDataInstanceFactory`のID生成戦略を変更**:
   - 固定のデフォルト値（1234L）ではなく、一意のIDを生成するようにする
   - 例: `AtomicLong`を使用してインクリメンタルなIDを生成
   ```java
   private static final AtomicLong COUNTER = new AtomicLong(1);
   
   public static StepExecution createStepExecution() {
       long id = COUNTER.getAndIncrement();
       return new StepExecution("step", new JobExecution(id), id);
   }
   ```

2. **`StepSynchronizationManager`の動作を調整**:
   - テスト環境において、重複する`StepExecution`の登録を検出した場合の処理を改善
   - 例: 既存のコンテキストを上書きするオプションを提供
   ```java
   // 新しいメソッドの追加（仮）
   public static void registerAndOverwrite(StepExecution stepExecution) {
       contexts.put(stepExecution, new StepContext(stepExecution));
   }
   ```

**考慮事項**:
- `MetaDataInstanceFactory`の変更は、既存のテストコードに影響を与える可能性がある
- `StepSynchronizationManager`の変更は、スレッドセーフティを維持する必要がある
- どちらのアプローチも、既存のAPIとの後方互換性を考慮する必要がある

**まとめ**:
現時点では、テストクラスで`getStepExecution()`メソッドをオーバーライドする回避策が推奨されます。根本的な修正については、Spring Batchチームによる設計判断が必要です。
