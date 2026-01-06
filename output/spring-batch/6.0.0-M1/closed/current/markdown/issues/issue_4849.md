# Move core partitioning APIs under org.springframework.batch.core.partition

**Issue番号**: #4849

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: type: task, in: core, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4849

**関連リンク**:
- Commits:
  - [08c4cb1](https://github.com/spring-projects/spring-batch/commit/08c4cb16b854b773f974eeb2073a04c56a0eb6ab)

## 内容

Several core partitioning APIs like `Partitioner`, `StepExecutionAggregator` and `PartitionStep` are currently under the `org.springframework.batch.core.partition.support` package. Those are not "support" interfaces and classes and should be moved to the `org.springframework.batch.core.partition` package.


