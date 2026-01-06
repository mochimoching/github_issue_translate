# MessageChannelPartitionHandler not usable with non-jdbc job repository implementations

**Issue番号**: #4917

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-21

**ラベル**: type: feature, in: integration, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4917

**関連リンク**:
- Commits:
  - [61fc226](https://github.com/spring-projects/spring-batch/commit/61fc22652c9c1f3da38aea9b22cf80da4c5c7ea2)

## 内容

As of v5.2, in a remote partitioning setup with repository polling, the `MessageChannelPartitionHandler` is not usable with MongoDB as it requires a data source.

This handler should work against the job repository interface.

