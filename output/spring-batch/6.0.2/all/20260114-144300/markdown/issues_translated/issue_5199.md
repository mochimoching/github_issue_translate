*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

# ChunkOrientedStep#doExecuteがチャンクトランザクション境界の外でStepExecutionを更新している

**Issue番号**: [#5199](https://github.com/spring-projects/spring-batch/issues/5199)

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2026-01-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5199

## 内容

Spring Batchチームの皆さん、こんにちは 👋
まず、Spring Batchの継続的な開発に感謝いたします。

## 説明
この課題は、過去のPR [#5165](https://github.com/spring-projects/spring-batch/pull/5165)での変更に関連しています。

これは私のミスであり、Spring Batch 6.0.1で意図しない副作用に気づいた後、適切に報告したいと思いました。

Spring Batch 6では、`ChunkOrientedStep#doExecute`がチャンクトランザクション境界の外で`StepExecution`を更新します。
このため、`JobRepository.update(stepExecution)`が失敗すると、チャンクトランザクションはすでに完了しており、バッチメタデータが不整合な状態になる可能性があります。

言い換えると、チャンク処理とステップ実行の永続化は`ChunkOrientedStep`ではもはやアトミックではありません。

## 環境
Spring Batch 6.0.1
ChunkOrientedStep#doExecute()

## 期待される動作
`JobRepository.update(stepExecution)`による`StepExecution`の更新は、チャンク処理と同じトランザクション境界内で行われるべきです。

メタデータの更新が失敗した場合、チャンクトランザクションもそれに応じてロールバックされ、処理済みデータとバッチメタデータの間の一貫性が保たれるべきです。

これは歴史的に`TaskletStep`が提供していた動作であり、`JobRepository.update()`はトランザクションコミット後ではなく、コミット前に呼び出されていました。

## 追加コンテキスト
`ChunkOrientedStep#doExecute`の現在の実装は以下のようになっています（簡略化）:
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
});

// トランザクションはここで既に完了している
getJobRepository().update(stepExecution);
```

## 提案する修正
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
    getJobRepository().update(stepExecution);
});
```

これにより、チャンク処理とメタデータ更新が同じトランザクション境界を共有します。

この課題について再現コードや失敗するテストの提供が必要であればお知らせください。🙏
