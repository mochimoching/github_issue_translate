# `ChunkOrientedStep.ChunkTracker` is not reset after step, allowing only a single execution of a particular step

**Issue番号**: #5126

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-03

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5126

**関連リンク**:
- Commits:
  - [69665d8](https://github.com/spring-projects/spring-batch/commit/69665d83d8556d9c23a965ee553972a277221d83)

## 内容

**Bug description**
`ChunkOrientedStep.doExecute()` loops until `chunkTracker.moreItems()` no longer returns `true`:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L359-L375

After the reader is exhausted, the `chunkTracker` switches to `false`, but that flag is never reset back to `true`. The consequence is that starting with the second invocation of the step, it will exit immediately and never do anything because `chunkTracker.moreItems()` still returns `false`.

**Environment**
Spring Batch 6.0.0

**Steps to reproduce**
1. Configure a job with a chunk-oriented step.
2. Run the job.
3. Run the job again.

**Expected behavior**
The step is executed both times.

**Minimal Complete Reproducible example**
[demo14.zip](https://github.com/user-attachments/files/23903365/demo14.zip)
Run with `./mvnw test`

The reproducer has a test that invokes the job three times. The first invocation starts chunk processing, both subsequent invocations skip it. This is also shown in the logs, where the first execution prints logs like this:
```
Job: [SimpleJob: [name=job]] launched with the following parameters: [{JobParameter{name='batch.random', value=7960112850225085599, type=class java.lang.Long, identifying=true}}]
Executing step: [step]
Reader was called, returning item
Reader was called, returning null
Writing chunk: [items=[item], skips=[]]
Step: [step] executed in 5ms
Job: [SimpleJob: [name=job]] completed with the following parameters: [{JobParameter{name='batch.random', value=7960112850225085599, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 22ms
```

While the subsequent invocations print logs like this:
```
Job: [SimpleJob: [name=job]] launched with the following parameters: [{JobParameter{name='batch.random', value=-1299334786035736075, type=class java.lang.Long, identifying=true}}]
Executing step: [step]
Step: [step] executed in
Job: [SimpleJob: [name=job]] completed with the following parameters: [{JobParameter{name='batch.random', value=-1299334786035736075, type=class java.lang.Long, identifying=true}}] and the following status: [COMPLETED] in 6ms
```

(Nitpick: When the step duration is zero, we get a message with a missing duration: `Step: [step] executed in`) -> #5037

---

My current workaround is to declare all `Job` and `Step` beans with `@Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)`. I then implemented my own `JobRegistry` that retrieves each job on demand from the `BeanFactory` to ensure that fresh instances are used for each run.

## コメント

### コメント 1 by abstiger

**作成日**: 2025-12-03

https://github.com/spring-projects/spring-batch/issues/5099#issuecomment-3588361319

### コメント 2 by Jaraxxuss

**作成日**: 2025-12-04

facing same issue when launching same job multiple times in test method

### コメント 3 by fmbenhassine

**作成日**: 2025-12-04

Thank you for reporting this issue and for providing a minimal example. Indeed, the lifecycle of the thread bound chunk tracker is incorrect when I introduced it in #5099. I will fix that in the upcoming patch release.

Just a side note: you have reported a couple issues and shared feedback on v6 and I appreciate that🙏 I was expecting some bumps and edge cases in 6.0.0 (as with every overhaul), but I am priortizing to stabilise things in 6.0.1. I will also come back to you asap to help on your [modularisation request](https://github.com/spring-projects/spring-batch/issues/5072#issuecomment-3575523924) . Thank you for your comprehension.

### コメント 4 by kzander91

**作成日**: 2025-12-04

@fmbenhassine sure thing! Usually I'm trying to give feedback earlier during the milestone phases, but this time it wasn't feasible for me due to the modularisation, where I was basically stuck.
I personally have already migrated to using a single context (but other's may still need guidance of course), which is why I have been able to test the v6 more thoroughly now.

### コメント 5 by fmbenhassine

**作成日**: 2025-12-04

@kzander91 The reproducer you provided inspired me to create this: b58c8429bcad782702fd4f1015b9dcc984b3de2b. Thank you for the inspiration 😉

