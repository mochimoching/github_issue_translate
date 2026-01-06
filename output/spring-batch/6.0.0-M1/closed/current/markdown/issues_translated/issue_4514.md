*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# チャンク処理における書き込みスキップカウントが更新されない

**Issue番号**: #4514

**状態**: closed | **作成者**: thilotanner | **作成日**: 2023-12-14

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4514

**関連リンク**:
- Commits:
  - [1fe91eb](https://github.com/spring-projects/spring-batch/commit/1fe91eb6fc80f79720c6036d1fc257d7217832ae)
  - [61d446e](https://github.com/spring-projects/spring-batch/commit/61d446e71f63c6b1d15826fb5e68aef7403b8702)

## 内容

**バグの説明**

書き込み処理中にチャンクからアイテムが削除される場合（アイテムの書き込みに失敗した場合）、書き込みスキップカウントが増加・更新されないようです。

**環境**

Spring Batch 5.0.3 / Spring Boot 3.1.5 / Java 17

**再現手順**

```java
public class MemberWriter implements ItemStreamWriter<String> {

    @Override
    public void write(Chunk<? extends String> memberChunk) {
        Chunk<? extends String>.ChunkIterator iterator = memberChunk.iterator();
        ...
        iterator.remove(new RuntimeException());
    }
}
```

**期待される動作**

`Chunk`クラスのドキュメントによると、`ChunkIterator`から削除されたアイテムごとに、対応する`StepExecution`オブジェクトの`writeSkipCount`が増加されるべきです：

`処理対象のアイテムリストと、スキップすべき失敗したアイテムのリストをカプセル化したもの。アイテムをスキップとしてマークするには、クライアントはiterator()メソッドを使用してチャンクを反復処理し、失敗が発生した場合はイテレータのChunk.ChunkIterator.remove()を呼び出す必要があります。スキップされたアイテムはチャンクを通じて利用可能になります。`

**回避策**

`SkipListener`と`StepExecutionListener`を組み合わせることで、この問題を回避することができます：

```java
public class SkipTestListener implements SkipListener<String, String>, StepExecutionListener {
    private StepExecution stepExecution;

    @Override
    public void beforeStep(StepExecution stepExecution) {
        this.stepExecution = stepExecution;
    }

    @Override
    public void onSkipInWrite(String item, Throwable t) {
        stepExecution.setWriteSkipCount(stepExecution.getWriteSkipCount() + 1);
        log.warn("Skipped item: {}", item);
    }
}
```
