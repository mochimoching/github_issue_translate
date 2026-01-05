# ChunkOrientedStepBuilder does not apply StepBuilderHelper properties (allowStartIfComplete, startLimit, stepExecutionListeners)

**Issue番号**: #5093

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5093

**関連リンク**:
- Commits:
  - [2d5c703](https://github.com/spring-projects/spring-batch/commit/2d5c7039e8d1f393c3616b0aeb0101956af31c97)

## 内容

Hello Spring Batch team,
I've found an issue where `ChunkOrientedStepBuilder` does not properly apply properties from its parent class `StepBuilderHelper` to the built step. I've searched existing issues but couldn't find a duplicate, so I'm reporting it here.

**Bug description**

When using `StepBuilder.chunk()`, properties set through `StepBuilderHelper` methods are not applied to the resulting `ChunkOrientedStep`. Specifically:
- `allowStartIfComplete(boolean)`
- `startLimit(int)`
- `listener(StepExecutionListener)`


These properties are correctly stored in the parent class's `properties` object, but they are never transferred to the actual step instance.


**Root cause**

The parent class `StepBuilderHelper` provides an `enhance(AbstractStep step)` method that applies all properties to a step:
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

However, `ChunkOrientedStepBuilder.build()` does not call this `enhance()` method, nor does it manually set these properties on the step.

The builder should either:
1. Call `enhance(step)` to apply all properties from `StepBuilderHelper`, OR
2. Explicitly set `allowStartIfComplete`, `startLimit`, and `stepExecutionListeners` on the step (if avoiding `enhance()` for code organization reasons)

Currently, neither approach is implemented, resulting in these properties being silently ignored.


**Environment**
- Spring Batch version: 6.0.0-RC2

**Steps to reproduce**
1. Create a chunk-oriented step using `StepBuilder.chunk()`
2. Set `allowStartIfComplete(true)` or `startLimit(5)` or add a `StepExecutionListener`
3. Build and run the step
4. Observe that these properties have no effect on the step's behavior


**Expected behavior**
Properties configured through `StepBuilderHelper` methods should be applied to the built step, regardless of the step type.


**Minimal Complete Reproducible example**
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

**Actual output:**

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

Notice that the beforeStep() and afterStep() messages never appear.


Workaround

For StepExecutionListener, explicitly casting to StepListener works because it routes to the child class's listener(StepListener) method, which adds to stepListeners collection:

```java
.listener((StepListener) new StepExecutionListener() {
    @Override
    public void beforeStep(StepExecution stepExecution) {
        System.out.println(">>>> Now this IS printed!");
    }
})
```

For allowStartIfComplete and startLimit, there is currently no workaround via the builder API.


Proposed fix

if there's a reason to avoid calling enhance(), explicitly set these properties:

```java
public ChunkOrientedStep build() {

    ChunkOrientedStep step = // ... create step ...
    
    // Manually apply StepBuilderHelper properties
  this.stepListeners.addAll(properties.getStepExecutionListeners());

    if (properties.allowStartIfComplete != null) {
        step.setAllowStartIfComplete(properties.allowStartIfComplete);
    }
    step.setStartLimit(properties.startLimit);

    …

    return step;
}
```

It would resolve this issue and ensure that all StepBuilderHelper properties are properly applied to chunk-oriented steps.

Thank you for looking into this issue! Please let me know if you need any additional information.

