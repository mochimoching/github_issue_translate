# Proposal: Automatically register ItemHandler as StepListener instead of only StepExecutionListener in ChunkOrientedStepBuilder

**Issue番号**: #5087

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-14

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5087

**関連リンク**:
- Commits:
  - [bf282b4](https://github.com/spring-projects/spring-batch/commit/bf282b4eef318796b3295c1846d400208b395364)

## 内容

Hello, Spring Batch team! I would like to submit a proposal regarding how item handlers are automatically registered as listeners on ChunkOrientedStepBuilder


**Context**
Starting from commit 52875e7, an ItemReader, ItemProcessor, or ItemWriter is automatically registered  to stepListeners(as a StepExecutionListener) only when it directly implements *StepExecutionListener*:

```java
if (this.reader instanceof StepExecutionListener listener) {
    this.stepListeners.add(listener);
}
if (this.writer instanceof StepExecutionListener listener) {
    this.stepListeners.add(listener);
}
if (this.processor instanceof StepExecutionListener listener) {
    this.stepListeners.add(listener);
}
```

In Batch 5, however, these components were automatically registered as listeners if:

1) they implemented *StepListener*, or
2) they had methods annotated with any listener annotation defined in StepListenerMetaData
(handled internally by `StepListenerFactoryBean.isListener(itemHandler)` in `SimpleStepBuilder#registerAsStreamsAndListeners()`)

This allowed ItemReader/ItemProcessor/ItemWriter to be detected as a listener even when implementing more specific listener interfaces (e.g., ItemReadListener, ItemProcessListener, etc.) or when using listener annotations such as @BeforeRead, @AfterRead, @OnReadError, etc.


**Proposal**
Although I haven’t personally used this pattern extensively, allowing item handlers that implement ItemReadListener/ItemProcessListener/ItemWriteListener to be automatically registered via the StepListener interface could increase their practical utility, as the listener could access internal state of the item handler directly.

```java
if (this.reader instanceof StepListener listener) {
    this.stepListeners.add(listener);
}
if (this.writer instanceof StepListener listener) {
    this.stepListeners.add(listener);
}
if (this.processor instanceof StepListener listener) {
    this.stepListeners.add(listener);
}
```

Thank you for your time and consideration!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-14

Thank you for the proposal! I think that was targeted at polymorphic objects, which act for example as an item reader and an item read listener at the same time. I have no objection to add this in v6 to reduce the gap with v5 and make migrations as smooth as possible.

### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-11-15

Thank you for the quick review and decision to include this in v6! I am happy that this change will help smooth out migrations for v5 users.

