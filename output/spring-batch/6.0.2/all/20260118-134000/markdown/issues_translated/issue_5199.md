*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# ChunkOrientedStep#doExecuteがチャンクトランザクション境界の外でStepExecutionを更新する

**課題番号**: [#5199](https://github.com/spring-projects/spring-batch/issues/5199)

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2026-01-06

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5199

## 内容

Spring Batchチームの皆さん、こんにちは 👋
いつもSpring Batchの開発を続けていただきありがとうございます。

## 説明
この課題は、PR [#5165](https://github.com/spring-projects/spring-batch/pull/5165) での過去の変更に関連しています: https://github.com/spring-projects/spring-batch/pull/5165

これは私のミスで、Spring Batch 6.0.1で意図しない副作用に気づいた後、適切に報告したいと思いました。

Spring Batch 6では、`ChunkOrientedStep#doExecute`がチャンクトランザクション境界の外で`StepExecution`を更新しています。
このため、`JobRepository.update(stepExecution)`が失敗した場合、チャンクトランザクションはすでに完了しているため、バッチメタデータが不整合な状態になる可能性があります。

言い換えると、`ChunkOrientedStep`ではチャンク処理とステップ実行の永続化がもはやアトミックではありません。

## 環境
Spring Batch 6.0.1
`ChunkOrientedStep#doExecute()`

## 期待される動作
`JobRepository.update(stepExecution)`による`StepExecution`の更新は、チャンク処理と同じトランザクション境界内で行われるべきです。

メタデータの更新が失敗した場合、チャンクトランザクションもそれに応じてロールバックされ、処理済みデータとバッチメタデータの間の一貫性が維持されるべきです。

これは歴史的に`TaskletStep`で提供されていた動作で、`JobRepository.update()`はトランザクションコミット前に呼び出され、後ではありませんでした。

## 追加コンテキスト
現在の`ChunkOrientedStep#doExecute`の実装は以下のようになっています（簡略化）:
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
});

// ここではトランザクションがすでに完了している
getJobRepository().update(stepExecution);

```

## 提案する修正
```java
this.transactionTemplate.executeWithoutResult(transactionStatus -> {
    processNextChunk(transactionStatus, contribution, stepExecution);
    getJobRepository().update(stepExecution);
});
```

これにより、チャンク処理とメタデータの更新が同じトランザクション境界を共有します。

この課題の再現コードや失敗するテストが必要な場合はお知らせください 🙏
