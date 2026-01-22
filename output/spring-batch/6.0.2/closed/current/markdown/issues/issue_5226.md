# Clarify ChunkListener changes in v6

**Issue番号**: #5226

**状態**: closed | **作成者**: cho-heidi | **作成日**: 2026-01-20

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5226

**関連リンク**:
- Commits:
  - [20eaa7b](https://github.com/spring-projects/spring-batch/commit/20eaa7b696c94a1432feb94e6d452cd959ad571f)

## 内容

**Bug description**
After upgrading from Spring Batch 5.x to 6.x, ChunkListener callbacks are no longer invoked when defined on an ItemReader.
This affects both of the following approaches:
	•	Implementing ChunkListener directly on the ItemReader
	•	Using the @BeforeChunk annotation
Both approaches worked as expected in Spring Batch 5.x, but in Spring Batch 6.x neither beforeChunk nor methods annotated with @BeforeChunk are called.
The step itself executes normally and read() is invoked, but chunk lifecycle callbacks are silently skipped.
I could not find any mention of this behavioral change in the migration guide or reference documentation.

**Environment**
	•	Spring Batch version: 6.x 
	•	Spring Boot version: 4.0.1
	•	Java version: 21 
	•	Language: Kotlin 

**Steps to reproduce**
1. Create an ItemReader bean annotated with @StepScope
2. Define chunk lifecycle logic using either:
	•	ChunkListener#beforeChunk
	•	a method annotated with @BeforeChunk
3. Register the reader normally in a chunk-oriented step
4. Run the job

Example Using ChunkListener
```kotlin
@Component
@StepScope
class TestReader() : ItemReader<Long>, ChunkListener<Long, Long> {
    private val logger = LoggerFactory.getLogger(this::class.simpleName)

    override fun beforeChunk(chunk: Chunk<Long>) {
           logger.info("before chunk") // never invoked in Spring Batch 6.x
    }

    override fun read(): Long? {
        return 10000L
    }
}
```

**Expected behavior**
Chunk lifecycle callbacks (beforeChunk, @BeforeChunk) should be invoked before each chunk, as they were in Spring Batch 5.x.


## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2026-01-21

Hi there!
It looks like you're probably using the deprecated chunk method when configuring your Step (please let me know if this isn't the case):
```java
chunk(int chunkSize, PlatformTransactionManager transactionManager)
```

When you use this deprecated method, Spring Batch uses the legacy (pre-6.0) Step implementation. In the legacy Step, the beforeChunk method signature you're implementing is not invoked:
```java
beforeChunk(Chunk<I> chunk)  // This is NOT called in legacy Step
```

The legacy Step implementation only calls the older beforeChunk method signature:
```java
beforeChunk(ChunkContext context)  // This is what legacy Step expects
```

To fix this, you should either:
- Migrate to the new Step builder API for Spring Batch 6.x, or
- Update your ChunkListener implementation to use the legacy method signature that matches your Step version

### コメント 2 by fmbenhassine

**作成日**: 2026-01-21

This was part of a bigger change (see #3950) and was documented in the Javadocs but not in the reference docs / migration guide. Apologies for the confusion, I will update those accordingly, but here is the rationale behind this change:

The `ChunkContext` concept is only used in the legacy implementation of the chunk-oriented processing model (v5) as part of the [repeat framework](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-infrastructure/src/main/java/org/springframework/batch/infrastructure/repeat). However, the new implementation does not use that concept, that's why the chunk listener methods that accept `ChunkContext` were deprecated for removal (they are only kept for use with the legacy implementation and will be removed at the same time as the legacy implementation, ie in v7).

The `ChunkListener` methods were adapted to the new implementation to accept a `Chunk` of items (nor more `ChunkContext`), and if you think about it, before reading a chunk, the chunk is not there yet, so we can't really pass it as a parameter to `beforeChunk(Chunk chunk)` at that time. That's why `beforeChunk` is actually only called when the chunk is ready to be processed (ie after reading it from the datasource). This is mentioned in the [Javadoc of ChunkListener.html#beforeChunk](https://docs.spring.io/spring-batch/reference/api/org/springframework/batch/core/listener/ChunkListener.html#beforeChunk(org.springframework.batch.infrastructure.item.Chunk)): `Callback before the chunk is processed`.

Moreover, when I designed the new interface, I thought about keeping a `ChunkListener#beforeChunk()` with no parameters but this did not make sense to me (as a user, what can I do in that method with no context nor a chunk of items?).

I hope that clarifies things better.

@KILL9-NO-MERCY Thank you for the follow up on this! And indeed, one can choose between the legacy or the new implementation, but need to use the right listener callbacks.

### コメント 3 by cho-heidi

**作成日**: 2026-01-22

@KILL9-NO-MERCY @fmbenhassine I understand now. Thank you very much for the clear explanation.

