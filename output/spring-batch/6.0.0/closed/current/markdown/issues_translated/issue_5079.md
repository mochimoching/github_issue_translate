*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ChunkOrientedStepはskipPolicy.shouldSkip()がfalseを返した際に例外をスローしない

**Issue番号**: #5079

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-07

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5079

**関連リンク**:
- Commits:
  - [946f788](https://github.com/spring-projects/spring-batch/commit/946f78825414b872f3d27110ff53347a86d362e5)
  - [97065fc](https://github.com/spring-projects/spring-batch/commit/97065fc40256ac18388f8ebdd157e7c744bc1a6a)

## 内容

こんにちは、Spring Batchチームの皆さん、

スキップポリシーがスキップを拒否した際に失敗したアイテムが静かに破棄される`ChunkOrientedStep`のバグを発見したと思います。

## バグの説明

フォールトトレラントモードでリトライが使い果たされた場合、`ChunkOrientedStep`は失敗したアイテムをスキップすべきかどうかを判断するために`skipPolicy.shouldSkip()`を呼び出します。しかし、`skipPolicy.shouldSkip()`が`false`を返した場合(アイテムをスキップすべきではないことを意味する)、コードは例外をスローしません。これにより、失敗したアイテムが静かに失われ、ジョブは何も起こらなかったかのように続行されます。

これは`ChunkOrientedStep`の3つのメソッドに影響します:
- `doSkipInRead()` (528行目)
- `doSkipInProcess()` (656行目)
- `scan()` (736行目)

## 環境

- Spring Batchバージョン: 6.0.0-RC2

## 再現手順
1. 常に`false`を返すスキップポリシー(スキップしない)でフォールトトレラントステップを設定します
2. 限られた試行回数(例: retryLimit = 2)でリトライを設定します
3. 1つのアイテムが一貫して失敗するアイテムを処理します
4. リトライ使い果たし後、失敗したアイテムがジョブを失敗させるのではなく静かに破棄されることを観察します

## 期待される動作

`skipPolicy.shouldSkip()`が`false`を返した場合、例外を再スローして以下を行うべきです:
- トランザクションをロールバックする
- ステップをFAILEDとマークする
- 静かなデータ損失を防ぐ

ジョブは、スキップ制限を超えたか、スキップポリシーがスキップを拒否したことを示す明確なエラーで失敗すべきです。

## 最小限の完全な再現可能な例
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
                .<String, String>chunk(3)
                .reader(issueReproductionReader())
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .retryLimit(2)
                .skipPolicy(new NeverSkipItemSkipPolicy())  
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
```

**実際の出力:**
ステップがCOMPLETED

```
Job: [SimpleJob: [name=issueReproductionJob]] launched with the following parameters: [{}]
Executing step: [issueReproductionStep]
Successfully processed: Item_1
Successfully processed: Item_2
Exception thrown for: Item_3
Exception thrown for: Item_3
Exception thrown for: Item_3
Writing items: [Item_1, Item_2]
Written: Item_1
Written: Item_2
Step: [issueReproductionStep] executed in 2s18ms
Job: [SimpleJob: [name=issueReproductionJob]] completed with the following parameters: [{}] and the following status: [COMPLETED] in 2s20ms
```

ご覧のように、`Item_3`は3回失敗しました(初回試行 + 2回のリトライ)が、静かに破棄されました。ジョブは`COMPLETED`ステータスで正常に完了しましたが、`NeverSkipItemSkipPolicy`はスキップを拒否すべきでした。

**期待される出力:**
スキップポリシーが失敗したアイテムのスキップを許可しないため、ジョブは`FAILED`ステータスで失敗すべきです。

---

**提案する修正:**

3つの影響を受けるメソッドは、`skipPolicy.shouldSkip()`が`false`を返した際に例外をスローすべきです:
```java
private void doSkipInRead(RetryException retryException, StepContribution contribution) {
    Throwable cause = retryException.getCause();
    if (this.skipPolicy.shouldSkip(cause, contribution.getStepSkipCount())) {
        this.compositeSkipListener.onSkipInRead(cause);
        contribution.incrementReadSkipCount();
    } else {
        throw new NonSkippableReadException("Skip policy rejected skipping", cause);
    }
}
```

同様の変更を`doSkipInProcess()`と`scan()`内のcatchブロックに適用すべきです。

このissueに注意を払っていただきありがとうございます!

## コメント

### コメント 1 by JunggiKim

**作成日**: 2025-11-08

このissueを修正するためにプルリクエスト #5081 を作成しました

### コメント 2 by fmbenhassine

**作成日**: 2025-11-13

このバグレポートに👍で反応した際、誤解していたと思います。

> `skipPolicy.shouldSkip()`が`false`を返した場合(アイテムをスキップすべきではないことを意味する)、コードは例外をスローしません

なぜその場合に例外をスローすべきなのでしょうか? それは例外的な動作ではありません。アイテムをスキップするということは、そのアイテムに対して`SkipListener`を呼び出すことを意味します。アイテムをスキップしないということは、それを破棄すること(つまり、`SkipListener`を呼び出さずに無視すること)を意味します。

あなたが共有した例では`NeverSkipItemSkipPolicy`を使用していますが、これはリトライポリシーを使い果たしたアイテムに対して`SkipListener`を呼び出さないことを意味し、これは実質的にこれらすべてのアイテムを無視することを意味します(データ損失ではなく、アイテムをスキップせず無視するという明示的な要求です)。

したがって、私が何か見落としていない限り、現在の動作は正しいと思います。同意していただけますか?



### コメント 3 by KILL9-NO-MERCY

**作成日**: 2025-11-14

@fmbenhassine 

Spring Batch 5の`FaultTolerantChunkProvider`と`FaultTolerantChunkProcessor`の理解に基づくと、

動作は以下の通りでした:
- スキップがオフの場合、`ItemReader`/`ItemProcessor`/`ItemWriter`の例外はステップに伝播され、失敗します。
- スキップがオンの場合、`SkipPolicy`がスキップを許可すると、そのアイテムのみ例外が飲み込まれ、処理が続行されます。
- スキップがオンの場合、`SkipPolicy`がスキップを許可しないと、例外が伝播され(実際には`RetryException`でラップされ)、ステップが失敗します。

これは、このissueを提起した際の私の期待と一致します(Batch 5でも、スキップ不可能な例外は`FaultTolerantStepBuilder`で`noRollback()`メソッドを明示的に使用することによってのみ無視できました)。

Batch 6では、動作の変更は設計上の決定として理解できますが、`SkipPolicy`がスキップを許可しない場合に失敗したアイテムが静かに破棄され、潜在的にデータ損失を引き起こす可能性があることを懸念しています。そのような場合、Batch 5の動作と一貫して、ステップが失敗することを期待します。

### コメント 4 by fmbenhassine

**作成日**: 2025-11-14

明確化をありがとうございます! 以前「私が何か見落としていない限り、現在の動作は正しいと思います」と言いましたが、実際に重要な詳細を見落としていました。スキップポリシーの契約では、`shouldSkip`メソッドが`false`を返した場合、処理を続行すべきではない(つまりステップは失敗すべき)ことが明確に述べられています:

```
@FunctionalInterface
public interface SkipPolicy {

	/**
	 * 与えられたthrowableで処理を続行すべきかどうかを示すtrueまたはfalseを返します。
	 * [...]
	 * @return 処理を続行すべき場合はtrue、そうでない場合はfalse。
         [...]
	 */
	boolean shouldSkip(Throwable t, long skipCount) throws SkipLimitExceededException;

}
```

したがって、これは有効なissueであり、修正すべきです。PR #5081は問題なく見えるので、GAのためにマージします。

フィードバックをありがとうございます!



### コメント 5 by KILL9-NO-MERCY

**作成日**: 2025-11-14

迅速なフィードバックをありがとうございます! GA前のわずか数日の間に私のレポートが少しでもお役に立てて嬉しいです。お時間と注意を本当に感謝します。


