# Partitioned step stops processing when first partition is finished in new chunk processing implementation

**Issue番号**: #5099

**状態**: closed | **作成者**: marbon87 | **作成日**: 2025-11-21

**ラベル**: type: bug, in: core, has: minimal-example, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5099

**関連リンク**:
- Commits:
  - [a2d61f8](https://github.com/spring-projects/spring-batch/commit/a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69)

## 内容

When using a step with local partitions, that have different amount of items, the step is finished when the first partition has done it's work. That lead's to unprocessed items in the other partitions.

Here is an example with a step and a test, that is failing with the new chunk processing implementation:

[partition-example.tar.gz](https://github.com/user-attachments/files/23675568/partition-example.tar.gz)

If you switch to the old chunk implemenation the test runs successfully.

## コメント

### コメント 1 by KILL9-NO-MERCY

**作成日**: 2025-11-21

I happened to come across this issue and did some digging.

I'm not entirely sure if I've found the root cause, but here's what I observed:
Since ChunkOrientedStep.doExecute(StepExecution) is executed for each partition, it gets called 3 times in total. However, ChunkTracker.noMoreItems() — which is called when there are no more items to read — is only invoked once across all executions.

It seems like each partition execution might need its own ChunkTracker instance.

I could be wrong, so please verify this.

### コメント 2 by fmbenhassine

**作成日**: 2025-11-24

Thank you for reporting this issue and for providing an example! The sample uses a `ResourcelessJobRepository` (the default in Spring Batch 6 / Spring Boot 4). This job repository implementation is not suitable for use cases involving the execution context in any way (including local partitioning, see its javadoc as well as the [reference docs](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html#_configuring_a_resourceless_jobrepository)).

That said, even with a JDBC job repository implementation there is an issue in `ChunkOrientedStep` as the chunk tracker is currently defined per instance while it should per thread (seems like we have a gap in our test suite as we currently test local partitioning with a simple tasklet and not with a chunk-oriented tasklet). I planned the fix for the next patch release.

### コメント 3 by zhaozhiguang

**作成日**: 2025-11-28

I also encountered the same problem,When using Partitioner and JdbcPageItemReaderBuilder

### コメント 4 by abstiger

**作成日**: 2025-11-28

I don’t think switching to thread-local solves the problem. What if a job-step is executed twice in the same thread?

I have encountered a similar issue. In a job, there is only one step, and the reader is JdbcCursorItemReader (which reads all users, assuming there are ten users), with a chunk size of 1.

run this job twice:

The first execution was successfully reading ten users and performing subsequent processing (at this point, the chunkTracker set `noMoreItems()`;).

The second execution skipped directly because `noMoreItems()`; had already been set.

maybe set it to true while step open in `ChunkOrientedStep` ?

```java
	@Override
	protected void open(ExecutionContext executionContext) throws Exception {
		this.compositeItemStream.open(executionContext);
		// set to true on every step open
		this.chunkTracker.get().moreItems = true;
	}

```



### コメント 5 by kzander91

**作成日**: 2025-12-03

This bug is also the cause of #5126, and the fix committed here won't solve it, as explained by @abstiger.
There's another issue with the fix in that the `ThreadLocal` is never cleared again, so instead of flipping flags in `open()`, I would suggest to clear it in `close()`:
```java
	@Override
	protected void close(ExecutionContext executionContext) throws Exception {
		this.chunkTracker.remove(); // ensure that the next invocation instantiates a new instance, and avoid leaks
		this.compositeItemStream.close();
	}
```

### コメント 6 by fmbenhassine

**作成日**: 2025-12-04

Thank you all for the feedback! 

@abstiger 

> I don’t think switching to thread-local solves the problem. What if a job-step is executed twice in the same thread?
 
It does, it is just the lifecycle of the thread bound chunk tracker that was not correctly managed when I introduced it in a2d61f8ffa33da7680b9ca0d3f8b8195d90fab69. I have addressed that in 69665d83d8556d9c23a965ee553972a277221d83.

