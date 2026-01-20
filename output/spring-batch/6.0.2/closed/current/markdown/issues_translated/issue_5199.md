*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# ChunkOrientedStep#doExecuteがチャンクトランザクション境界の外でStepExecutionを更新する

**Issue番号**: #5199

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2026-01-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5199

**関連リンク**:
- コミット:
  - [563abdb](https://github.com/spring-projects/spring-batch/commit/563abdb29d26884c32f18e5d548fd079e6aad057)

## 内容

Spring Batchチームの皆さん、こんにちは 👋
まず、Spring Batchの継続的な開発に感謝します。

## 説明
この問題は、過去のPR [#5165](https://github.com/spring-projects/spring-batch/pull/5165)での変更に関連しています。

これは私のミスで、Spring Batch 6.0.1で意図しない副作用に気づいた後、適切に報告したいと思いました。

Spring Batch 6では、`ChunkOrientedStep#doExecute`がチャンクトランザクション境界の外で`StepExecution`を更新しています。
このため、`JobRepository.update(stepExecution)`が失敗した場合、チャンクトランザクションはすでに完了しており、バッチメタデータが不整合な状態になる可能性があります。

言い換えると、`ChunkOrientedStep`ではチャンク処理とステップ実行の永続化がアトミックではなくなっています。

## 環境
Spring Batch 6.0.1
`ChunkOrientedStep#doExecute()`

## 期待される動作
`JobRepository.update(stepExecution)`による`StepExecution`の更新は、チャンク処理と同じトランザクション境界内で行われるべきです。

メタデータの更新が失敗した場合、チャンクトランザクションもそれに応じてロールバックされ、処理されたデータとバッチメタデータ間の整合性が保たれるべきです。

これは、`TaskletStep`が歴史的に提供してきた動作であり、`JobRepository.update()`がトランザクションコミット後ではなくコミット前に呼び出されていました。

## 追加のコンテキスト
`ChunkOrientedStep#doExecute`の現在の実装は以下のようになっています（簡略化）:
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
});

// ここではすでにトランザクションが完了している
getJobRepository().update(stepExecution);

```

## 修正案
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
    getJobRepository().update(stepExecution);
});
```

これにより、チャンク処理とメタデータ更新が同じトランザクション境界を共有します。

この問題の再現コードや失敗するテストを提供する必要があれば、お知らせください 🙏
