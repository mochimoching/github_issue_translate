*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました。*

# Issue #5077: デフォルトSkipPolicyの不具合修正

## 課題概要

retryのみが設定され、skip設定がない場合、デフォルトの`SkipPolicy`が`AlwaysSkipItemSkipPolicy`に設定され、retry試行を使い果たした後に失敗したアイテムがステップを失敗させるのではなく、静かにスキップされる問題が報告されました。

**SkipPolicyとは**: アイテム処理中にエラーが発生した際、そのアイテムをスキップして処理を続行するか、ステップを失敗させるかを決定するポリシーです。

## 問題の詳細

### 期待される動作
skip設定なしでretryのみが設定されている場合、retry試行を使い果たした後に失敗したアイテムは**ステップを失敗させる**べきです。

### 実際の動作  
失敗したアイテムが静かにスキップされ、ステップは成功として完了します。

## 原因

```java
// 修正前のコード
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(
            this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new AlwaysSkipItemSkipPolicy(); // ← 問題!
    }
}
```

## 対応方針

```java
// 修正後のコード
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(
            this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new NeverSkipItemSkipPolicy(); // ✅ 修正
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
        .retry(ProcessingException.class)
        .retryLimit(3)
        // skip設定なし → retry使い果たし後はステップ失敗
        .build();
}
```

修正により、retry試行を3回使い果たした後、アイテムはスキップされずにステップが失敗します。

## 学習ポイント

### SkipPolicyの種類

| SkipPolicy | 動作 |
|-----------|------|
| AlwaysSkipItemSkipPolicy | 常にスキップ |
| NeverSkipItemSkipPolicy | 決してスキップしない |
| LimitCheckingExceptionHierarchySkipPolicy | 指定例外と回数制限でスキップ |
