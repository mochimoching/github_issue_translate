*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました。*

# Issue #5078: retryLimit()のみ設定時にErrorもリトライされる問題の修正

## 課題概要

`retry()`なしで`retryLimit()`のみが設定されている場合、`OutOfMemoryError`や`StackOverflowError`などの重大なJVM Errorを含む**全てのThrowable**がリトライ対象になる問題が報告されました。

**Errorとは**: Javaの例外階層において、通常は回復不可能な深刻なシステムエラーを表します。`OutOfMemoryError`, `StackOverflowError`などがあり、これらはリトライしても回復しないため、リトライすべきではありません。

## 問題の詳細

### 期待される動作
`retry()`なしで`retryLimit()`のみが設定されている場合:
- 例外(Exception)はリトライされない、または
- `Exception`とそのサブクラスのみがリトライされる(`Error`は除く)

### 実際の動作
`matchIfEmpty = true`により、**全てのThrowable(Errorを含む)**がリトライされます。

## 原因

```java
// 問題のあるコード
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(this.retryableExceptions)  // ← 空のセット!
          .build();
    }
}
```

`retryableExceptions`が空の場合、`ExceptionTypeFilter`の`matchIfEmpty = true`により、全てのThrowableが一致してしまいます。

## 対応方針

```java
// 修正後のコード
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       Set<Class<? extends Throwable>> exceptions = this.retryableExceptions.isEmpty()
             ? Set.of(Exception.class)  // ✅ Errorを除外
             : this.retryableExceptions;

       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(exceptions)
          .build();
    }
}
```

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
        .retryLimit(3)
        // retry()なし → Exceptionのみリトライ、Errorはリトライしない
        .build();
}
```

修正により、`OutOfMemoryError`などの重大なErrorはリトライされず、即座にステップが失敗します。

## 学習ポイント

### Java例外階層

```
Throwable
├── Error (回復不可能)
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── VirtualMachineError
└── Exception (回復可能)
    ├── RuntimeException
    │   ├── NullPointerException
    │   └── IllegalArgumentException
    └── CheckedException
        ├── IOException
        └── SQLException
```

### リトライすべき例外とすべきでない例外

| 例外タイプ | リトライ | 理由 |
|----------|---------|------|
| IOException | ✅ | ネットワーク一時的障害 |
| SQLException (一時的) | ✅ | DB接続タイムアウト |
| OutOfMemoryError | ❌ | メモリ不足、リトライ無意味 |
| StackOverflowError | ❌ | 無限再帰、リトライ無意味 |
| NullPointerException | ❌ | プログラムバグ |
