*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月21日に生成されました）*

# 並列チャンク処理時にStepContributionのカウンターがスレッドセーフではない

**Issue番号**: #5188

**状態**: closed | **作成者**: KMGeon | **作成日**: 2025-12-29

**ラベル**: type: bug, in: core, related-to: multi-threading

**URL**: https://github.com/spring-projects/spring-batch/issues/5188

**関連リンク**:
- コミット:
  - [6bd771a](https://github.com/spring-projects/spring-batch/commit/6bd771ab6c87fdec1ce98f773865a07394624cfc)
  - [0868c02](https://github.com/spring-projects/spring-batch/commit/0868c02574ee7920c60b3dc20da5aa75615bfeb3)
  - [b9587c7](https://github.com/spring-projects/spring-batch/commit/b9587c72f126bdaedb013c738b30accd9f0262bc)
  - [cc06132](https://github.com/spring-projects/spring-batch/commit/cc06132c31f760156de69e16bf93828f74a48c21)

## 内容

# バグの説明

`ChunkOrientedStep`が並列モード（`TaskExecutor`を設定した状態）で実行される場合、`StepContribution.incrementFilterCount()`と`StepContribution.incrementProcessSkipCount()`でレースコンディションが発生し、カウント値が実際より少なくなります。これは、複数のワーカースレッドが同じ`StepContribution`インスタンスに対してこれらのメソッドを同時に呼び出すためです。`filterCount`と`processSkipCount`フィールドはスレッドセーフではない`long`型を使用しており、`+=`や`++`演算でアクセスされています。

## 環境

- Spring Batchバージョン: 6.0.1
- Javaバージョン: 22
- OS: macOS（Linux/Windowsでも再現可能）

## 再現手順

1. `TaskExecutor`を設定して並列モードを有効にした`ChunkOrientedStep`を構成する
2. すべてのアイテムをフィルタリングする（nullを返す）`ItemProcessor`を使用する
3. 大量のアイテムを処理する
4. 実行後に`StepExecution.getFilterCount()`と`StepExecution.getProcessSkipCount()`を確認する

## 期待される動作

`filterCount`と`processSkipCount`は、フィルタリング/スキップされたアイテムの数を正確に反映すべきです。

## 根本原因の分析

問題は`StepContribution.java`にあります：

```java
// 現在の実装 - スレッドセーフではない
private long filterCount = 0;
private long processSkipCount = 0;

public void incrementFilterCount(long count) {
    filterCount += count; // レースコンディション発生！
}

public void incrementProcessSkipCount() {
    processSkipCount++; // レースコンディション発生！
}
```

`ChunkOrientedStep.processChunkConcurrently()`では、複数のタスクが`TaskExecutor`に送信され、すべてが同じcontributionオブジェクトを共有しています：

```java
Future itemProcessingFuture = this.taskExecutor.submit(
    () -> processItem(item, contribution) // 同じcontributionを共有
);
```

各ワーカースレッドがアイテム処理時に`contribution.incrementFilterCount()`または`contribution.incrementProcessSkipCount()`を呼び出すため、レースコンディションが発生します。

### `long +=`と`++`演算の問題点

これらの演算は**アトミックではなく**、複数のステップで構成されています：

1. 現在の値を読み取る
2. カウント分を加算する
3. メモリに書き戻す

複数のスレッドがこれらのステップを同時に実行すると、更新が失われる可能性があります：

```
スレッド1: 読み取り(100) → 加算 → 書き込み(101)
スレッド2: 読み取り(100) → 加算 → 書き込み(101)  ← 更新が失われた！
期待値: 102, 実際の値: 101
```

## 提案する解決策

`filterCount`と`processSkipCount`を`AtomicLong`に変更します：

```java
private final AtomicLong filterCount = new AtomicLong(0);
private final AtomicLong processSkipCount = new AtomicLong(0);

public void incrementFilterCount(long count) {
    filterCount.addAndGet(count);
}

public void incrementProcessSkipCount() {
    processSkipCount.incrementAndGet();
}

public long getFilterCount() {
    return filterCount.get();
}

public long getProcessSkipCount() {
    return processSkipCount.get();
}
```

## 検討した代替アプローチ

### アプローチ1: AtomicLongの部分適用（現在の実装）

このアプローチでは、`StepContribution`クラス内の`filterCount`と`processSkipCount`のみを`AtomicLong`に変更します。ロックフリーのパフォーマンスとAPIの互換性を維持しつつ、最小限のコード変更で済みます。ただし、一部のフィールドのみを`AtomicLong`にして他を`long`のままにすると、コードの一貫性が低下し、他の開発者に混乱を招く可能性があります。


### アプローチ2: メインスレッドで結果を集約

`processChunkConcurrently()`を修正して、処理結果を収集し、メインスレッドでのみカウントを更新します。

```java
record ProcessingResult<O>(@Nullable O item, boolean filtered, boolean skipped) {}

private void processChunkConcurrently(...) {
    List<Future<ProcessingResult<O>>> tasks = new LinkedList<>();

    for (...) {
        Future<ProcessingResult<O>> future = this.taskExecutor.submit(
            () -> processItemWithResult(item)  // contributionを渡さない
        );
        tasks.add(future);
    }

    // メインスレッドで結果を集約 - レースコンディションなし
    for (Future<ProcessingResult<O>> future : tasks) {
        ProcessingResult<O> result = future.get();
        if (result.filtered()) ...
        if (result.skipped())...
        if (result.item() != null) ...
    }
}
```

**アプローチ1（AtomicLong）**が最もシンプルで実用的な解決策だと考えていますが、フィードバックは歓迎します。**アプローチ2**を希望される場合や、他の提案があれば、お知らせください。修正いたします。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-13

この課題を報告いただきありがとうございます。ステップ実行はワーカースレッド間で共有できますが、ステップコントリビューションは共有すべきではありません。実際、これらのAPIの背後にある考え方として、各スレッドはステップ実行全体に対する独自のコントリビューションを持つべきです（つまり、各スレッドが独自の読み取りカウント、書き込みカウントなどを持ち、マネージャーステップがそれらのカウンターを集約します）。

サンプルを共有していただけますか？記載された手順に従うことはできますが、すべてのコードが共有されていないため、同じ構成になっているか確信が持てません。

よろしくお願いします！

### コメント 2 by KMGeon

**作成日**: 2026-01-14

この課題に関心を持っていただきありがとうございます！

サンプルプロジェクトはこちらです: [sample_code](https://github.com/KMGeon/spring-batch-issue-5188)


### コメント 3 by KMGeon

**作成日**: 2026-01-16

## 訂正

前回のコメントで間違いがありました。申し訳ありません。当初GitHubリポジトリのリンクを共有しましたが、Spring Batchの課題でMCVE（最小完全検証可能な例）を提出する場合は、代わりにzipファイルを提供すべきでした。

サンプルプロジェクトをzipファイルとして添付しました: [spring-batch-mcve.zip](https://github.com/user-attachments/files/24661198/spring-batch-mcve.zip)


### コメント 4 by KMGeon

**作成日**: 2026-01-20

> この課題を報告いただきありがとうございます。ステップ実行はワーカースレッド間で共有できますが、ステップコントリビューションは共有すべきではありません。実際、これらのAPIの背後にある考え方として、各スレッドはステップ実行全体に対する独自のコントリビューションを持つべきです（つまり、各スレッドが独自の読み取りカウント、書き込みカウントなどを持ち、マネージャーステップがそれらのカウンターを集約します）。
> 
> サンプルを共有していただけますか？記載された手順に従うことはできますが、すべてのコードが共有されていないため、同じ構成になっているか確信が持てません。
> 
> よろしくお願いします！

@fmbenhassine 

フィードバックありがとうございます。

この課題を最初に作成した際、2つの解決策を提案しました：
- アプローチ1: `filterCount`と`processSkipCount`を`AtomicLong`に変更
- アプローチ2: 各ワーカースレッドからの処理結果をメインスレッドで集約

当時は、アプローチ1の方がコード変更が少なくシンプルだと考えたため、`AtomicLong`アプローチを使用したPR [#5189](https://github.com/spring-projects/spring-batch/pull/5189)を提出しました。

しかし、フィードバックによりSpring Batchの設計哲学を理解できました：

「ステップコントリビューションはワーカースレッド間で共有すべきではない。各スレッドはステップ実行全体に対する独自のコントリビューションを持ち、マネージャーステップがそれらのカウンターを集約すべきである。」

この設計意図に基づき、アプローチ1の代わりにアプローチ2を使用したPR [#5224](https://github.com/spring-projects/spring-batch/pull/5224)を提出しました。

変更点：
- 各ワーカースレッドに対して個別の`StepContribution`インスタンスを作成
- すべてのfutureが完了した後、メインスレッドで`filterCount`と`processSkipCount`を集約
- `StepContribution`クラス自体の変更なし

お時間があるときにレビューをお願いします。ありがとうございます！

### コメント 5 by fmbenhassine

**作成日**: 2026-01-20

フィードバックとPRをありがとうございます！

前回の[コメント](https://github.com/spring-projects/spring-batch/issues/5188#issuecomment-3742868170)は**正確ではありませんでした**。実際、そのアプローチはローカルチャンキングにのみ当てはまります（[こちら](https://github.com/spring-projects/spring-batch/blob/82121a59872e018b1c98cbe68345fde716cd2e60/spring-batch-integration/src/main/java/org/springframework/batch/integration/chunk/ChunkTaskExecutorItemWriter.java#L90-L96)がステップコントリビューションの集約が行われる場所で、[こちら](https://github.com/spring-projects/spring-batch/tree/main/spring-batch-samples/src/main/java/org/springframework/batch/samples/chunking/local)にサンプルがあります）。混乱を招きアプローチ2のコントリビューションにつながったことをお詫びします。しかし、実際にはアプローチ1が正しい方法です。

アプローチ1を使用したPRをマージし、もう一方はクローズします。
