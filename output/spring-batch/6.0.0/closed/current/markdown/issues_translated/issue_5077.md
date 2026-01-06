*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ChunkOrientedStepBuilder: retryのみが設定されている場合、デフォルトのSkipPolicyはNeverSkipItemSkipPolicyであるべき(AlwaysSkipItemSkipPolicyではない)

**Issue番号**: #5077

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5077

**関連リンク**:
- Commits:
  - [ce7e03a](https://github.com/spring-projects/spring-batch/commit/ce7e03acf9766983019be34e3b2a633756b5669f)
  - [e77e21c](https://github.com/spring-projects/spring-batch/commit/e77e21cb7926f4689b9903bb65ae81bc80a56e7a)

## 内容

こんにちは、Spring Batchチームの皆さん、

retryのみが設定されている場合のデフォルトのスキップポリシーに関して、Spring Batch 6で予期しない動作変更を発見したと思います。


**バグの説明**

skip設定なしでretry設定のみを構成した場合、デフォルトの`SkipPolicy`が`AlwaysSkipItemSkipPolicy`に設定されます。これにより、retry試行を使い果たした後に失敗したすべてのアイテムがステップを失敗させるのではなく、静かにスキップされ、意図されていないように思われます。


**環境**

- Spring Batchバージョン: 6.0.0-RC2


**再現手順**
1. skip設定なしでretryを使用してチャンク指向ステップを設定します:


2. retry制限を超える例外をプロセッサーからスローします

4. アイテムがステップを失敗させるのではなく、スキップされることを観察します


**期待される動作**
skip設定なしでretryのみが設定されている場合、すべてのretry試行を使い果たした後に失敗したアイテムは**ステップを失敗させる**べきであり、スキップされるべきではありません。

skipが明示的に設定されていない場合、デフォルトの`SkipPolicy`は`NeverSkipItemSkipPolicy`(または同等のもの)であるべきです。

**根本原因**

`ChunkOrientedStepBuilder`内で:
```java
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new AlwaysSkipItemSkipPolicy(); // ← これは間違っているように思われる
    }
}
```

`skippableExceptions`も`skipLimit`も設定されていない場合、`AlwaysSkipItemSkipPolicy`にデフォルト設定され、予期しないスキップ動作を引き起こします。


**Spring Batch 5との比較**

Spring Batch 5の`FaultTolerantStepBuilder`では:
```java
if (skipPolicy == null) { // default == null
    if (skippableExceptionClasses.isEmpty() && skipLimit > 0) {
        logger.debug(String.format(
            "A skip limit of %s is set but no skippable exceptions are defined.",
            skipLimit));
    }
    skipPolicy = limitCheckingItemSkipPolicy; 
}
```

これにより、skip設定なしでretryが使い果たされた場合、ステップ失敗となります。


**提案する修正**
skipが設定されていない場合、デフォルトの`SkipPolicy`を`NeverSkipItemSkipPolicy`に変更します:
```java
if (this.skipPolicy == null) {
    if (!this.skippableExceptions.isEmpty() || this.skipLimit > 0) {
        this.skipPolicy = new LimitCheckingExceptionHierarchySkipPolicy(this.skippableExceptions, this.skipLimit);
    }
    else {
        this.skipPolicy = new NeverSkipItemSkipPolicy(); // ← これであるべき
    }
}
```

**最小限の完全な再現可能な例**
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
    public Step issueReproductionStep(
            JobRepository jobRepository
    ) {
        return new StepBuilder(jobRepository)
                .<String, String>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retry(ProcessingException.class)
                .retryLimit(2)
                // skip設定なし - retry使い果たし後にステップが失敗することを期待
                .build();
    }

    @Bean
    public ItemReader<String> issueReproductionReader() {
        return new ListItemReader<>(List.of("Item_1", "Item_2", "Item_3"));
    }

    @Bean
    public ItemProcessor<String, String> issueReproductionProcessor() {
        return item -> {
            if ("Item_3".equals(item)) {
                log.error("Exception thrown for: {}", item);
                throw new ProcessingException("Processing failed for " + item);
            }

            log.info("Successfully processed: {}", item);
            return item;
        };
    }

    @Bean
    public ItemWriter<String> issueReproductionWriter() {
        return items -> {
            log.info("Writing items: {}", items.getItems());
            items.getItems().forEach(item -> log.info("Written: {}", item));
        };
    }

    public static class ProcessingException extends RuntimeException {
        public ProcessingException(String message) {
            super(message);
        }
    }

}

**実際の動作**

```bash
Executing step: [issueReproductionStep]
Successfully processed: Item_1
Successfully processed: Item_2
Exception thrown for: Item_3
Exception thrown for: Item_3
Exception thrown for: Item_3
Writing items: [Item_1, Item_2]
Written: Item_1
Written: Item_2
Step: [issueReproductionStep] executed in 2s13ms
```

この動作をレビューしていただけますか? 質問や追加情報が必要な場合は、お気軽にお知らせください。

お時間とご検討をありがとうございます!





## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-13

その通りです。ユーザーが明示的に要求するまで、デフォルトではアイテムをスキップすべきではありません。これで修正されているはずです。これを提起していただきありがとうございます!


