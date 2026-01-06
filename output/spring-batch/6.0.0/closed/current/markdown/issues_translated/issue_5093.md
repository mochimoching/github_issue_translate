*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# ChunkOrientedStepBuilderがStepBuilderHelperのプロパティ(allowStartIfComplete、startLimit、stepExecutionListeners)を適用しない

**Issue番号**: #5093

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5093

**関連リンク**:
- Commits:
  - [2d5c703](https://github.com/spring-projects/spring-batch/commit/2d5c7039e8d1f393c3616b0aeb0101956af31c97)

## 内容

こんにちは、Spring Batchチームの皆さん、
`ChunkOrientedStepBuilder`が親クラス`StepBuilderHelper`のプロパティをビルドされたステップに適切に適用しない問題を発見しました。既存のissueを検索しましたが重複が見つからなかったため、ここで報告します。

**バグの説明**

`StepBuilder.chunk()`を使用する際、`StepBuilderHelper`のメソッドで設定されたプロパティが、結果として得られる`ChunkOrientedStep`に適用されません。具体的には:

- `allowStartIfComplete(boolean)`
- `startLimit(int)`
- `listener(StepExecutionListener)`

これらのプロパティは親クラスの`properties`オブジェクトに正しく格納されますが、実際のステップインスタンスに転送されることはありません。

**根本原因**

親クラス`StepBuilderHelper`は、すべてのプロパティをステップに適用する`enhance(AbstractStep step)`メソッドを提供しています:

```java
protected void enhance(AbstractStep step) {
    step.setJobRepository(properties.getJobRepository());

    ObservationRegistry observationRegistry = properties.getObservationRegistry();
    if (observationRegistry != null) {
       step.setObservationRegistry(observationRegistry);
    }

    Boolean allowStartIfComplete = properties.allowStartIfComplete;
    if (allowStartIfComplete != null) {
       step.setAllowStartIfComplete(allowStartIfComplete);
    }

    step.setStartLimit(properties.startLimit);

    List<StepExecutionListener> listeners = properties.stepExecutionListeners;
    if (!listeners.isEmpty()) {
       step.setStepExecutionListeners(listeners.toArray(new StepExecutionListener[0]));
    }
}
```

しかし、`ChunkOrientedStepBuilder.build()`はこの`enhance()`メソッドを呼び出さず、これらのプロパティをステップに手動で設定することもしません。

ビルダーは以下のいずれかを行うべきです:

1. `enhance(step)`を呼び出して、`StepBuilderHelper`からすべてのプロパティを適用する、または
2. `allowStartIfComplete`、`startLimit`、`stepExecutionListeners`をステップに明示的に設定する(コード構成上の理由で`enhance()`を避ける場合)

現在、どちらのアプローチも実装されておらず、これらのプロパティは暗黙的に無視されます。

**環境**

- Spring Batchバージョン: 6.0.0-RC2

**再現手順**

1. `StepBuilder.chunk()`を使用してチャンク指向ステップを作成
2. `allowStartIfComplete(true)`または`startLimit(5)`を設定、または`StepExecutionListener`を追加
3. ステップをビルドして実行
4. これらのプロパティがステップの動作に影響を与えないことを確認

**期待される動作**

`StepBuilderHelper`メソッドで設定されたプロパティは、ステップのタイプに関係なく、ビルドされたステップに適用されるべきです。

**最小限の再現可能な例**

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
                .listener(new StepExecutionListener() {
                    @Override
                    public void beforeStep(StepExecution stepExecution) {
                        System.out.println(">>>> This message is NEVER printed");
                    }
                    
                    @Override
                    public ExitStatus afterStep(StepExecution stepExecution) {
                        System.out.println(">>>> This message is NEVER printed either");
                        return stepExecution.getExitStatus();
                    }
                })
                .build();
    }

    @Bean
    public ItemReader issueReproductionReader() {
        return new SkippableItemReader();
    }

    @Bean
    public ItemProcessor issueReproductionProcessor() {
        return item -> {
            log.info(">>>> Successfully processed: {}", item.getName());
            return item;
        };
    }

    @Bean
    public ItemWriter issueReproductionWriter() {
        return items -> {
            for(TestItem item: items) {
                log.info(">>>> Writing items: {}", item.getName());
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
    static class SkippableItemReader implements ItemReader {
        private int count = 0;
        private final List items = List.of(
                new TestItem(1L, "Item-1", "First item"),
                new TestItem(2L, "Item-2", "Second item"),
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

            log.info(">>>> Read: {}", item.getName());
            return item;
        }
    }
}
```

**実際の出力:**

```
Job: [SimpleJob: [name=issueReproductionJob]] launched with the following parameters: [{}]
Executing step: [issueReproductionStep]
>>>> Read: Item-1
>>>> Read: Item-2
>>>> Read: Item-3
>>>> Successfully processed: Item-1
>>>> Successfully processed: Item-2
>>>> Successfully processed: Item-3
>>>> Writing items: Item-1
>>>> Writing items: Item-2
>>>> Writing items: Item-3
>>>> EOF: No more items
Step: [issueReproductionStep] executed in 2ms
```

`beforeStep()`と`afterStep()`のメッセージが表示されないことに注意してください。

**回避策**

`StepExecutionListener`については、`StepListener`に明示的にキャストすると機能します。これは、子クラスの`listener(StepListener)`メソッドにルーティングされ、`stepListeners`コレクションに追加されるためです:

```java
.listener((StepListener) new StepExecutionListener() {
    @Override
    public void beforeStep(StepExecution stepExecution) {
        System.out.println(">>>> Now this IS printed!");
    }
})
```

`allowStartIfComplete`と`startLimit`については、現在ビルダーAPIを介した回避策はありません。

**提案される修正**

`enhance()`を呼び出すことを避ける理由がある場合、これらのプロパティを明示的に設定します:

```java
public ChunkOrientedStep build() {

    ChunkOrientedStep step = // ... create step ...
    
    // StepBuilderHelperのプロパティを手動で適用
    this.stepListeners.addAll(properties.getStepExecutionListeners());

    if (properties.allowStartIfComplete != null) {
        step.setAllowStartIfComplete(properties.allowStartIfComplete);
    }
    step.setStartLimit(properties.startLimit);

    …

    return step;
}
```

これにより問題が解決され、すべての`StepBuilderHelper`プロパティがチャンク指向ステップに適切に適用されることが保証されます。

この問題を調査していただきありがとうございます! 追加情報が必要な場合はお知らせください。


