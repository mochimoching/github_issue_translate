*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# 提案: ChunkOrientedStepBuilderでItemHandlerをStepExecutionListenerだけでなくStepListenerとして自動登録

**Issue番号**: #5087

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-11-14

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5087

**関連リンク**:
- Commits:
  - [bf282b4](https://github.com/spring-projects/spring-batch/commit/bf282b4eef318796b3295c1846d400208b395364)

## 内容

こんにちは、Spring Batchチームの皆さん! `ChunkOrientedStepBuilder`でアイテムハンドラーがリスナーとして自動登録される方法について提案を提出したいと思います。


**コンテキスト**
コミット52875e7から、`ItemReader`、`ItemProcessor`、または`ItemWriter`は、*StepExecutionListener*を直接実装している場合にのみ、`stepListeners`に(StepExecutionListenerとして)自動登録されます:

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

しかし、Batch 5では、これらのコンポーネントは以下の場合に自動的にリスナーとして登録されていました:

1) *StepListener*を実装している場合、または
2) `StepListenerMetaData`で定義されている任意のリスナーアノテーションでアノテートされたメソッドを持つ場合
(`SimpleStepBuilder#registerAsStreamsAndListeners()`の`StepListenerFactoryBean.isListener(itemHandler)`によって内部的に処理)

これにより、`ItemReader`/`ItemProcessor`/`ItemWriter`は、より具体的なリスナーインターフェース(例: `ItemReadListener`、`ItemProcessListener`など)を実装している場合や、`@BeforeRead`、`@AfterRead`、`@OnReadError`などのリスナーアノテーションを使用している場合でも、リスナーとして検出されました。


**提案**
個人的にはこのパターンを広範囲に使用したことはありませんが、`ItemReadListener`/`ItemProcessListener`/`ItemWriteListener`を実装するアイテムハンドラーが`StepListener`インターフェースを介して自動登録されることを許可すると、リスナーがアイテムハンドラーの内部状態に直接アクセスできるため、実用性が向上する可能性があります。

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

お時間とご検討をありがとうございます!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-14

提案をありがとうございます! これは、例えばアイテムリーダーとアイテムリードリスナーの両方として機能するポリモーフィックオブジェクトを対象としていたと思います。v5とのギャップを減らし、移行をできるだけスムーズにするために、v6にこれを追加することに異議はありません。

### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-11-15

迅速なレビューとv6に含めるという決定をありがとうございます! この変更がv5ユーザーの移行をスムーズにするのに役立つことを嬉しく思います。


