*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ChunkOrientedStepBuilder: retry()なしでretryLimit()のみが設定されている場合、すべてのThrowable(Errorを含む)がリトライされる

**Issue番号**: #5078

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5078

**関連リンク**:
- Commits:
  - [4d6a5fa](https://github.com/spring-projects/spring-batch/commit/4d6a5fa39b223226a73330498024857cb34d6046)
  - [638c183](https://github.com/spring-projects/spring-batch/commit/638c1834fa1e88ed5017c3081f94e61205289e92)
  - [f606e6f](https://github.com/spring-projects/spring-batch/commit/f606e6f31c9ce6334183384485f14422e124a685)
  - [8ed93d1](https://github.com/spring-projects/spring-batch/commit/8ed93d1900b5a6d0a17e8a1ad1355c1d30e5c918)

## 内容

こんにちは、Spring Batchチームの皆さん、
前回のissue #5068に続いて、関連するが逆のシナリオを発見しました。これは潜在的なリスクをもたらします。

#5068の修正をレビューしている際、`retry()`なしで`retryLimit()`が設定されている場合、`OutOfMemoryError`や`StackOverflowError`などの重大なErrorを含むすべてのThrowableがリトライ可能になることに気づきました。前回のissueと一緒にこれを捕まえられたら良かったのですが。


**バグの説明**
Spring Batch 6で`retry()`を指定せずに`retryLimit()`を設定すると、リトライメカニズムが重大なJVM Errorを含む**すべてのThrowable**をリトライしようとします。これは、`ExceptionTypeFilter`(`DefaultRetryPolicy`で使用される)が`includes`(`retry()`で設定)と`excludes`の両方が空の場合に`matchIfEmpty = true`を使用するために発生します。


**環境**
- Spring Batchバージョン: 6.0.0-RC2


**再現手順**
1. `retry()`なしで`retryLimit()`を使用してチャンク指向ステップを設定します:
@Bean
public Step step() {
    return new StepBuilder("step", jobRepository)
        .chunk(10, transactionManager)
        .reader(reader())
        .processor(processor())
        .writer(writer())
        .faultTolerant()
        .retryLimit(3)
        // retry()設定なし
        .build();
}

2. 任意のコンポーネント(ItemReaderまたはItemProcessorなど)から重大なError(例: `OutOfMemoryError`)をスローします
3. 重大なErrorでもリトライされていることを観察します



**期待される動作**
`retry()`なしで`retryLimit()`のみが設定されている場合:
- 例外はリトライされないべき
- または`Exception`とそのサブクラスのみがリトライされるべき(`Error`を除く)

**実際の動作**
`matchIfEmpty = true`により、すべてのThrowable(Errorを含む)がリトライされます。

**最小限の完全な再現可能な例**
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(JobRepository jobRepository) {
        return new StepBuilder(jobRepository)
                .chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retryLimit(2)
                // retry()なし - リトライなしまたはExceptionのみのリトライを期待
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("OutOfMemoryError thrown for: {}", item);
                throw new OutOfMemoryError("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }
}
```


**実際の出力:**
```
Successfully processed: Item_1
Successfully processed: Item_2
OutOfMemoryError thrown for: Item_3
OutOfMemoryError thrown for: Item_3  ← リトライ1
OutOfMemoryError thrown for: Item_3  ← リトライ2
Writing items: [Item_1, Item_2] ← Item_3はスキップされ、writerは続行(#5077で別途報告)
Written: Item_1
Written: Item_2


`OutOfMemoryError`が2回リトライされ、システムの状態を悪化させる可能性があります。

**根本原因の分析**
`ChunkOrientedStepBuilder`内で:
```java
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(this.retryableExceptions)  // ← 空のセット!
          .build();
    }
    else {
       this.retryPolicy = throwable -> false;
    }
}

`retryableExceptions`が空の場合、`DefaultRetryPolicy`は`includes`と`excludes`の両方が空の`ExceptionTypeFilter`を使用します。
`ExceptionTypeFilter.matchTraversingCauses()`内で:
```java
private boolean matchTraversingCauses(Throwable exception) {
    boolean emptyIncludes = super.includes.isEmpty();
    boolean emptyExcludes = super.excludes.isEmpty();

    if (emptyIncludes && emptyExcludes) {
        return super.matchIfEmpty;  // ← trueを返す!
    }
    // ...
}
```

`matchIfEmpty = true`であるため、重大なErrorを含む**すべてのThrowableが一致**します。

**提案する修正**

`retry()`なしで`retryLimit()`が設定されている場合、Errorを除外するために`Exception.class`をデフォルトにします:
```java
if (this.retryPolicy == null) {
    if (!this.retryableExceptions.isEmpty() || this.retryLimit > 0) {
       Set<Class> exceptions = this.retryableExceptions.isEmpty()
             ? Set.of(Exception.class)
             : this.retryableExceptions;

       this.retryPolicy = RetryPolicy.builder()
          .maxAttempts(this.retryLimit)
          .includes(exceptions)
          .build();
    }
    else {
       this.retryPolicy = throwable -> false;
    }
}
```

これにより以下が保証されます:
- デフォルトで`Exception`とそのサブクラスのみがリトライされます
- 重大なJVM Errorはリトライされません
- ユーザーは`retry()`を介して特定の例外を明示的に含めることができます



この動作をレビューしていただけますか? これは、ユーザーがどの例外をリトライするかを指定せずにリトライ制限を設定した場合の潜在的なリスクのように思われます。

お時間とご検討をありがとうございます!


