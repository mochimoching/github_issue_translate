*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ChunkOrientedStep: #5048からのリグレッション - フォールトトレラントモードでのスキップ時に中断

**Issue番号**: #5084

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-11

**ラベル**: type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5084

**関連リンク**:
- Commits:
  - [4c9fe94](https://github.com/spring-projects/spring-batch/commit/4c9fe94bb12d6a9679848221abbadbbaa1b494f8)

## 内容

こんにちは、Spring Batchチームの皆さん、Spring Batch 6の素晴らしい作業に感謝します。


**バグの説明**
Issue [#5048](https://github.com/spring-projects/spring-batch/issues/5048)が報告された際、私が提案した修正で読み取りループに`else { break; }`を追加するというミスをしました。

その修正は、`readItem()`がnullを返す2つの異なるシナリオの区別を考慮していませんでした:
1) データの終わり(EOF): 利用可能なアイテムがもうない → 中断すべき ✅
2) フォールトトレラントモードでのスキップ: 例外がスキップされた → 読み取りを続行すべき ❌

`readChunk()`の現在のループ終了条件は、両方のケースを同一に扱い、スキップが発生した際に読み取りループが早期に終了します。

**シナリオ例:**
チャンクサイズ: 3
Item-2が例外をスロー → スキップが発生
期待: Item-2をスキップしてItem-3の読み取りを続行(チャンク内に2アイテム: Item-1、Item-3)
実際: Item-1の後に読み取りループが中断(チャンク内に1アイテム)

**環境**
Spring Batchバージョン: 6.0.0-RC2(コミット706add7での#5048修正後)


**再現手順**
以下の設定でチャンク指向ステップを設定します:
チャンクサイズ: 3
フォールトトレラント: true
スキップポリシー設定済み(例: AlwaysSkipItemSkipPolicy)

2番目のアイテムで例外をスローする`ItemReader`を使用
ジョブを実行し、ログでチャンクサイズを観察

**期待される動作**
フォールトトレラントモードでアイテム読み取り中にスキップが発生した場合:

問題のあるアイテムはスキップされるべき
読み取りループは設定されたチャンクサイズまでチャンクを埋めるために続行すべき
期待されるチャンク: [Item-1、Item-3](2アイテム、Item-2がスキップされた)


**期待されるコンソール出力:**
```bash
>>>> Read: Item-1
>>>> EXCEPTION on Item-2!
>>>> Skip occurred on reader
>>>> Read: Item-3
>>>> EOF: No more items
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-3
```
→ Item-1とItem-3の両方が同じチャンクで処理される

**実際の動作**
スキップが発生すると、読み取りループがすぐに終了します:
実際のチャンク1: [Item-1](1アイテムのみ)
実際のチャンク2: [Item-3](次のチャンクの残りのアイテム)

**実際のコンソール出力:**
```bash
>>>> Read: Item-1
>>>> EXCEPTION on Item-2!
>>>> Skip occurred on reader
>>>> Successfully processed: Item-1
>>>> Writing items: Item-1
>>>> Read: Item-3
>>>> EOF: No more items
>>>> Successfully processed: Item-3
>>>> Writing items: Item-3
```
→ Item-1とItem-3が異なるチャンクで処理される ❌

最小限の完全な再現可能な例
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
    public Step issueReproductionStep(JobRepository jobRepository, DataSource dataSource) {
        return new StepBuilder(jobRepository)
                .<TestItem, TestItem>chunk(3)
                .reader(issueReproductionReader(dataSource))
                .processor(issueReproductionProcessor())
                .writer(issueReproductionWriter())
                .faultTolerant()
                .skipPolicy(new AlwaysSkipItemSkipPolicy())
                .skipListener(skipListener())
                .build();
    }

    @Bean
    public ItemReader<TestItem> issueReproductionReader(DataSource dataSource) {
        return new SkippableItemReader();
    }

    @Bean
    public ItemProcessor<TestItem, TestItem> issueReproductionProcessor() {
        return item -> {
            log.info(">>>> Successfully processed: {}", item.getName());
            return item;
        };
    }

    @Bean
    public ItemWriter<TestItem> issueReproductionWriter() {
        return items -> {
            for (TestItem item : items) {
                log.info(">>>> Writing items: {}", item.getName());
            }
        };
    }

    private SkipListener<TestItem, TestItem> skipListener() {
        return new SkipListener<>() {
            @Override
            public void onSkipInRead(Throwable t) {
                log.info(">>>> Skip occurred on reader");
            }
        };
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestItem {
        private Long id;
        private String name;
        private String description;
    }

    @Slf4j
    static class SkippableItemReader implements ItemReader<TestItem> {
        private int count = 0;
        private final List<TestItem> items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item - will throw exception"),
                new TestItem(3L, "Item-3", "Third item")
        );

        @Override
        public TestItem read() {
            if (count >= items.size()) {
                log.info(">>>> EOF: No more items");
                return null;
            }

            TestItem item = items.get(count);
            count++;

            // 2番目のアイテム(Item-2)で例外をスロー
            if (count == 2) {
                log.error(">>>> EXCEPTION on Item-2!");
                throw new RuntimeException("Simulated read error on Item-2");
            }

            log.info(">>>> Read: {}", item.getName());
            return item;
        }
    }
}
```


**根本原因の分析**
`readItem()`メソッド内(約508-545行目)

スキップが発生した場合:
```java
catch (Exception exception) {
    this.compositeItemReadListener.onReadError(exception);
    if (this.faultTolerant && exception instanceof RetryException retryException) {
        doSkipInRead(retryException, contribution);
        // ⚠️ nullを返すが、chunkTracker.moreItems()は依然としてtrue!
    }
    // ...
}
return item;  // スキップの場合nullを返す
```
`chunkTracker.noMoreItems()`は実際のデータ終了時のみ呼び出されます:
```java
item = doRead();
if (item == null) {
    this.chunkTracker.noMoreItems();  // EOFでのみ設定
}
```
したがって、2つの異なるnull返却ケースがあります:
EOF: nullが返され + `moreItems()` == false
スキップ: nullが返され + `moreItems()` == true

**`readChunk()`メソッド内(約478-487行目)**
現在の問題のあるコード(私のミス):
```java
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else {
            break;  // ❌ EOFとスキップの両方で中断!
        }
    }
    return chunk;
}
```
#5048で追加された`else { break; }`は、EOFとスキップを区別できません。

**提案する修正**
nullで盲目的に中断するのではなく、`ChunkTracker`の状態をチェックするように中断条件を変更します:
**`readChunk()`の修正:**
```java
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
    for (int i = 0; i < chunkSize; i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
        } else if (!chunkTracker.moreItems()) {  // ✅ 実際のEOFでのみ中断
            break;
        }
        // else: スキップが発生、次のアイテムへ続行
    }
    return chunk;
}
```

**優先度に関する注記**
この問題はチャンクサイズに影響しますが、ステップは正しく機能し続けます - すべてのアイテムは正常に処理され、意図されたよりも多くのトランザクションが発生するだけです。これは優先度に基づいて、ご都合の良いときに対処できます。

**さらに**
追加の問題は`processChunkConcurrently()`メソッドにも存在します

並行処理モードでは、同じ問題が発生しますが、元の#5048の修正では対処されていませんでした。
**`processChunkConcurrently()`メソッド内(約431-438行目)**
現在のコード:
```java
// アイテムを読み取り、並行アイテム処理タスクを送信
for (int i = 0; i < this.chunkSize; i++) {
    I item = readItem(contribution);
    if (item != null) {
        Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> processItem(item, contribution));
        itemProcessingTasks.add(itemProcessingFuture);
    }
    // ❌ else句なし - EOF後もループが続き、不要なread()呼び出しが発生
}
```
このメソッドには2つの問題があります:
1) 元の#5048の問題: EOFで中断しない → 不要な`readItem()`呼び出しが続く
2) この問題: `else { break; }`で修正しても、スキップ時に中断する(`readChunk()`と同じ)


**`processChunkConcurrently()`の修正:**
```java
// アイテムを読み取り、並行アイテム処理タスクを送信
for (int i = 0; i < this.chunkSize; i++) {
    I item = readItem(contribution);
    if (item != null) {
        Future<O> itemProcessingFuture = this.taskExecutor.submit(() -> processItem(item, contribution));
        itemProcessingTasks.add(itemProcessingFuture);
    } else if (!chunkTracker.moreItems()) {  // ✅ 実際のEOFでのみ中断
        break;
    }
    // else: スキップが発生、次のアイテムへ続行
}
```
この修正は両方の問題に対処します:
- EOF後の不要な読み取りを防ぐ(#5048の問題と同じ)
- スキップ後にチャンクが埋め続けることを許可(この問題)

このissueや追加情報が必要な場合は、お知らせください。

お忙しい中でもissueへの継続的な対応に感謝します。優先度に基づいて、ご都合の良いときに対処していただければ幸いです。


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-13

これは有効なissueです。チャンク指向処理モデルのこの新しい実装には、いくつかの問題やエッジケースが予想されていたため、RCフェーズの早期にこのissue(および他のissue!)を報告していただき、本当にありがとうございます 🙏 これらのエッジケースに関して、テストスイートに明らかなギャップがあり、GAのために修正します。

### コメント 2 by fmbenhassine

**作成日**: 2025-11-13

> nullで盲目的に中断するのではなく、`ChunkTracker`の状態をチェックするように中断条件を変更します:
> **`readChunk()`の修正:**

提案された修正をありがとうございます! これは実際に以下と同等です:

```diff
private Chunk<I> readChunk(StepContribution contribution) throws Exception {
    Chunk<I> chunk = new Chunk<>();
--    for (int i = 0; i < chunkSize; i++) {
++    for (int i = 0; i < chunkSize && this.chunkTracker.moreItems(); i++) {
        I item = readItem(contribution);
        if (item != null) {
            chunk.add(item);
--        } else if (!chunkTracker.moreItems()) {  // ✅ 実際のEOFでのみ中断
--           break;
          }
    }
    return chunk;
}
```

これの方が考えやすいと思いますし、実際には両方の問題(#5048のものとこの#5084)を修正します。#5084が#5048のリグレッションであることは驚くべきことです 😉 これらのケースをカバーするために、`ChunkOrientedStepFaultToleranceIntegrationTests`に`testSkipInReadInSequentialMode`と`testSkipInReadInConcurrentMode`を追加しました。

> 追加の問題は`processChunkConcurrently()`メソッドにも存在します

これも修正し、そのケースをカバーするために`ChunkOrientedStepTests#testReadNoMoreThanAvailableItemsInConcurrentMode`を追加しました(#5048で追加された`ChunkOrientedStepTests#testReadNoMoreThanAvailableItemsInSequentialMode`と同様)

---

このissueを報告していただきありがとうございます!


