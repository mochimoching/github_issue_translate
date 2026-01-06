# Step execution no longer persisted after partitioner creates the context

**Issue番号**: #5138

**状態**: closed | **作成者**: brian-mcnamara | **作成日**: 2025-12-05

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5138

**関連リンク**:
- Commits:
  - [d983f71](https://github.com/spring-projects/spring-batch/commit/d983f71da9cf8fa014d5cb2657174a84e966c17c)
  - [1da2f28](https://github.com/spring-projects/spring-batch/commit/1da2f28b4c1a855feed5f10ad70b708ead061305)
  - [412158a](https://github.com/spring-projects/spring-batch/commit/412158afd9f8576b323d445212ed9e8f76c4bd84)
  - [60bf5b4](https://github.com/spring-projects/spring-batch/commit/60bf5b42bb6bee89a180ad321397c09b1c3999dc)
  - [cc2d57f](https://github.com/spring-projects/spring-batch/commit/cc2d57fde1cc603fc6d18defcc3eee1807e2adcd)
  - [a8961a6](https://github.com/spring-projects/spring-batch/commit/a8961a6770a78cf94eee2f5d270f280751d2092d)
  - [e64383d](https://github.com/spring-projects/spring-batch/commit/e64383d8eeab77a5894657cfa2b343bffca54979)

## 内容

**Bug description**
With [this change](https://github.com/spring-projects/spring-batch/commit/90d895955d951156849ba6fa018676273fdbe2c4#diff-1ccc98868257080253b51baded74a755478f3f85f754e0dc8ef05144ecd7dc02), a steps context is no longer persisted inside SimpleStepExecutionSplitter.java, causing the execution context created by a partitioner to be lost, preventing a remote worker from loading the created context. Specifically the call to jobRepository.addAll prior to batch 6 ensured the context was persisted

Specifically, after the contexts are created, MessageChannelPartitionHandler.doHandle is responsible to create and send the message, when the remote worker receives the message, it loads the steps through the job repository.

**Environment**
Spring boot 4.0.0, batch 6.0.0, batch-integration 6.0.0, JDK21

**Steps to reproduce**

See https://github.com/brian-mcnamara/SpringBatch6/blob/main/src/main/java/com/example/batchpartitionbug/BatchPartitionBugApplication.java

(can be run with `./gradlew run`) Specifically note line 91 which should get the context from the partitioner on line 197

This bug is seen with a partitioned step using message channels for delivery and a persistence layer for the jobRepository. 


**Expected behavior**

The partitioner should initialize the step contexts on the controller and update the step in the repository. This enabling the worker to load the step from the repository and use the context created earlier


## コメント

### コメント 1 by quaff

**作成日**: 2025-12-08

My application failed to start due to `@Value("#{stepExecutionContext['xxx']}")` is null after upgrade to Spring Boot 4.0.

### コメント 2 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue and for providing an example! This is a valid issue. It seems like we have a gap in our remote partitioning [tests](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/test/java/org/springframework/batch/samples/partition/remote).. I will check that. I planned the fix for the upcoming 6.0.1 release.

### コメント 3 by brian-mcnamara

**作成日**: 2025-12-10

Thank you both for the quick turn around, and all your work!

