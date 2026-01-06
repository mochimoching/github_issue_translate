*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# 空のパラメータセットでジョブを開始する際の不正な警告

**Issue番号**: #4914

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-18

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4914

**関連リンク**:
- Commits:
  - [980ff7b](https://github.com/spring-projects/spring-batch/commit/980ff7b8d72bba7f8cfa0aa62fc057bc27a4aba0)
  - [e2dcee1](https://github.com/spring-projects/spring-batch/commit/e2dcee113dfe78627e1adbf12dfe2a91e89f306c)

## 内容

課題 [#4910](https://github.com/spring-projects/spring-batch/issues/4910) の導入後、インクリメンタを持つジョブを空のパラメータセットで開始すると、不必要な警告が表示されます：

```
[main] WARN org.springframework.batch.core.launch.support.TaskExecutorJobOperator -  COMMONS-LOGGING Attempting to launch job 'job' which defines an incrementer with additional parameters={{}}. Those additional parameters will be ignored.
```

パラメータセットが空の場合、この警告は削除されるべきです。
