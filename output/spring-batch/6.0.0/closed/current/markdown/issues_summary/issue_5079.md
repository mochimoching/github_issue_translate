*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました。*

# Issue #5079: SkipPolicyがfalseを返した際に例外がスローされない問題の修正

## 課題概要

フォールトトレラントモードでリトライが使い果たされた後、`skipPolicy.shouldSkip()`が`false`を返した場合(アイテムをスキップすべきではない)、コードが例外をスローせず、失敗したアイテムが静かに破棄される問題が報告されました。

**SkipPolicyとは**: エラー発生時にアイテムをスキップするか、ステップを失敗させるかを決定するポリシーです。`shouldSkip()`メソッドが`true`を返すとスキップ、`false`を返すとステップ失敗を意味します。

## 問題の詳細

### 期待される動作
`skipPolicy.shouldSkip()`が`false`を返した場合:
1. 例外を再スローしてトランザクションをロールバック
2. ステップを`FAILED`とマークする
3. 静かなデータ損失を防ぐ

### 実際の動作
`skipPolicy.shouldSkip()`が`false`を返しても例外がスローされず、失敗したアイテムが静かに破棄され、ジョブは何事もなかったかのように続行します。

## 原因

### 影響を受けるメソッド
この問題は`ChunkOrientedStep`の3つのメソッドに影響します:
1. `doSkipInRead()` (528行目)
2. `doSkipInProcess()` (656行目)
3. `scan()` (736行目)

```java
// 問題のあるコード
private void doSkipInRead(RetryException retryException, StepContribution contribution) {
    Throwable cause = retryException.getCause();
    if (this.skipPolicy.shouldSkip(cause, contribution.getStepSkipCount())) {
        this.compositeSkipListener.onSkipInRead(cause);
        contribution.incrementReadSkipCount();
    }
    // else ブロックがない → 何もしない!
}
```

## 対応方針

```java
// 修正後のコード
private void doSkipInRead(RetryException retryException, StepContribution contribution) {
    Throwable cause = retryException.getCause();
    if (this.skipPolicy.shouldSkip(cause, contribution.getStepSkipCount())) {
        this.compositeSkipListener.onSkipInRead(cause);
        contribution.incrementReadSkipCount();
    } else {
        // ✅ スキップポリシーがスキップを拒否した場合、例外をスロー
        throw new NonSkippableReadException("Skip policy rejected skipping", cause);
    }
}
```

同様の修正が`doSkipInProcess()`と`scan()`にも適用されました。

## 使用例

```java
@Bean
public Step myStep(JobRepository jobRepository,
                   PlatformTransactionManager transactionManager) {
    return new StepBuilder("myStep", jobRepository)
        .<String, String>chunk(10, transactionManager)
        .reader(reader())
        .processor(processor())
        .writer(writer())
        .faultTolerant()
        .retryLimit(2)
        .skipPolicy(new NeverSkipItemSkipPolicy())  // 決してスキップしない
        .build();
}
```

修正により、retry試行を2回使い果たした後、`NeverSkipItemSkipPolicy`がスキップを拒否し、`NonSkippableException`がスローされてステップが失敗します。

## 学習ポイント

### SkipPolicyの契約

```java
@FunctionalInterface
public interface SkipPolicy {
    /**
     * @return 処理を続行すべき場合はtrue(スキップ)、
     *         そうでない場合はfalse(失敗)。
     */
    boolean shouldSkip(Throwable t, long skipCount) 
        throws SkipLimitExceededException;
}
```

`false`を返すことは「処理を続行すべきでない」、つまりステップを失敗させるべきことを意味します。

### カスタムSkipPolicyの例

```java
public class CustomSkipPolicy implements SkipPolicy {
    
    @Override
    public boolean shouldSkip(Throwable t, long skipCount) {
        // 特定の例外のみスキップ
        if (t instanceof TemporaryException) {
            return skipCount < 10;  // 10回までスキップ
        }
        
        // それ以外はスキップしない(ステップ失敗)
        return false;
    }
}
```
