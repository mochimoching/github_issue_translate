*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5037: ステップまたはジョブが瞬時に完了した際のロギングに関する軽微な問題

## 課題概要

Spring Batchのジョブやステップが瞬時に完了した場合、ログメッセージの末尾に表示されるべき処理時間情報が欠落してしまう問題です。

**Spring Batchとは**: Javaで大量データを効率的に処理するためのフレームワークです。バッチ処理（定期的または一括で実行される処理）を実装する際に使用されます。

### 問題の詳細

通常、ジョブが完了すると以下のようなログが出力されます：

```
Job: [FlowJob: [name=MyJob]] completed with the following parameters: [...] and the following status: [FAILED] in 1234ms
```

しかし、ジョブが非常に短時間（1ミリ秒未満）で完了した場合、処理時間の部分が空になってしまいます：

```
Job: [FlowJob: [name=MyJob]] completed with the following parameters: [...] and the following status: [FAILED] in 
```

### 影響範囲

- 高速に完了するバッチジョブを大量に起動する環境
- 処理時間のログを監視・分析している場合に影響

## 原因

`BatchMetrics.formatDuration()`メソッドの実装に問題がありました。

### 詳細な流れ

1. `TaskExecutorJobLauncher`がジョブ完了時にログを出力する際、`BatchMetrics.formatDuration()`を呼び出す
2. このメソッド内で`duration.isZero()`をチェックしている
3. 開始時刻と終了時刻が実質的に同じ場合（1ミリ秒未満）、durationがゼロと判定される
4. ゼロの場合、空の文字列`""`を返してしまう

### 問題のコード

```java
// BatchMetrics.java
public static String formatDuration(Duration duration) {
    if (duration.isZero()) {
        return "";  // 空文字列を返してしまう
    }
    // ... 通常の処理
}
```

この実装では、処理時間が0ミリ秒の場合に何も表示されず、ログが不完全になります。

## 対応方針

処理時間がゼロの場合でも、明示的に`0ms`と表示するように修正されました。

### 修正内容

[コミット 249330b](https://github.com/spring-projects/spring-batch/commit/249330b2718492424c2df9b452279c9601c2802e)、[コミット f3ccc74](https://github.com/spring-projects/spring-batch/commit/f3ccc7405c9d8f1c1f8a33fdfbbcbe143799e8f7)、[コミット 1d50d82](https://github.com/spring-projects/spring-batch/commit/1d50d829907a580fe3aea5b6a17859a418e478b9)

```java
// 修正後のコード
public static String formatDuration(Duration duration) {
    if (duration.isZero()) {
        return "0ms";  // 明示的に0msを返す
    }
    // ... 通常の処理
}
```

### 修正後の動作

処理時間が1ミリ秒未満のジョブでも、以下のように完全なログが出力されます：

```
Job: [FlowJob: [name=MyJob]] completed with the following parameters: [...] and the following status: [FAILED] in 0ms
```

これにより、ログの一貫性が保たれ、監視ツールでのパースエラーなども回避できます。

## 参考情報

- **対象バージョン**: Spring Batch 5.2.2以降で発生、6.0.1で修正
- **関連クラス**: 
  - `TaskExecutorJobLauncher` - ジョブ実行とログ出力を担当
  - `BatchMetrics` - 処理時間のフォーマットを担当
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5037
