# Incorrect documentation about concurrent steps in v6

**Issue番号**: #5228

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2026-01-21

**ラベル**: in: documentation, type: bug, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5228

**関連リンク**:
- Commits:
  - [9ccbafa](https://github.com/spring-projects/spring-batch/commit/9ccbafa0cf387b36e22462921c53aab055f9cd64)

## 内容


### Discussed in https://github.com/spring-projects/spring-batch/discussions/5214

<div type='discussions-op-text'>

<sup>Originally posted by **ctrung** January 14, 2026</sup>
Hi, 

With the new concurrency model of Spring Batch 6, `ItemReader.read()` is accessed by the main thread whereas it was accessed by the threads of the taskExecutor before.

It seems that the reader doesn't need to be thread-safe anymore (I have verified that myself, and the behaviour is the same with or without a thread-safe reader).

Chapter https://docs.spring.io/spring-batch/reference/scalability.html#multithreadedStep of the reference documentation still mentions the need for a thread safe reader. 

Are there other usecases where a thread-safe reader is still needed ? 

My step definition :

```java
var step = new StepBuilder("my_step", jobRepository)
                         .<I, O>chunk(5)
                         .transactionManeger(transactionManager)
                         .reader(reader)
                         .writer(writer)
                         .taskExecutor(taskExecutor)
                         .build();
```
</div>

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-21

Yes, with the new concurrency model, the reader is only called by a single thread and does not have to be thread-safe. I gave some details about that here: https://github.com/spring-projects/spring-batch/issues/4955#issuecomment-3423549722. 

> Chapter https://docs.spring.io/spring-batch/reference/scalability.html#multithreadedStep of the reference documentation still mentions the need for a thread safe reader.

That's an oversight, I will update the documentation accordingly.

> Are there other usecases where a thread-safe reader is still needed ?

Not with the step implementations provided by Spring Batch. We kept the synchronised wrappers around for anyone implementing a custom step and who might need to wrap the reader/writer in a synchronized decorator.

> My step definition

That step only reads and writes data (no processing, transformation, validation, etc), so I see no need for it to be concurrent and I am not sure involving multiple threads will improve its throughput (benchmarks needed here, it probably will have the opposite effect, meaning the step will spend more time handling concurrency rather than transferring bytes).

