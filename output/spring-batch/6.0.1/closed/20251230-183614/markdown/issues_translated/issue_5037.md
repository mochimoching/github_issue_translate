# ステップやジョブが瞬時に完了した際の軽微なログ出力の問題

**Issue番号**: #5037

**状態**: closed | **作成者**: janossch | **作成日**: 2025-10-20

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5037

**関連リンク**:
- Commits:
  - [249330b](https://github.com/spring-projects/spring-batch/commit/249330b2718492424c2df9b452279c9601c2802e)
  - [f3ccc74](https://github.com/spring-projects/spring-batch/commit/f3ccc7405c9d8f1c1f8a33fdfbbcbe143799e8f7)
  - [1d50d82](https://github.com/spring-projects/spring-batch/commit/1d50d829907a580fe3aea5b6a17859a418e478b9)

## 内容

**バグの説明**
本番環境で以下のようなログ行を発見しましたが、行末の実行時間情報が欠落していました。

... `Job: [FlowJob: [name=...]] completed with the following parameters: [...] and the following status: [FAILED] in `

コードを少し調べたところ、ジョブが終了する際に
https://github.com/spring-projects/spring-batch/blob/11ec7f12e8e4477ae802a02ee72f69f78afbf25b/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/TaskExecutorJobLauncher.java#L221-L228

フレームワークによってinfoレベルのログエントリが出力されます。しかし、開始日時と終了日時が本質的に同じである場合、`duration.isZero()`条件により、`BatchMetrics.formatDuration`メソッドが空の`String`を返してしまいます。

https://github.com/spring-projects/spring-batch/blob/11ec7f12e8e4477ae802a02ee72f69f78afbf25b/spring-batch-core/src/main/java/org/springframework/batch/core/observability/BatchMetrics.java#L69-L72

**環境**
Java21 (temurin)
Spring Batch 5.2.2
ファイルベースのH2 DBを使用

**再現手順**
高速に完了する多数のバッチジョブを起動します。

**期待される動作**
正直なところ分かりませんが、少なくとも`0ms`の方が何もないよりは良いでしょう。以下のような形式です:
`Job: [FlowJob: [name=...]] completed with the following parameters: [...] and the following status: [FAILED] in 0ms`

**最小限の再現可能な例**

以下のテストは5.2.2で失敗します:
```
    @Test
    void testFormatDurationWhenCalculationReturnsZeroDuration() {
        var startDate = LocalDateTime.now();
        // 両方の日付が等しいが異なる参照であることを保証するため、開始日時の文字列表現から終了日時を作成します。
        // 実際には別のLocalDateTime.now()呼び出しがありますが、それは異なる時刻を返す可能性があり、不安定なテストの原因となる可能性があります。
        var endDate = LocalDateTime.parse(startDate.toString());
        var calculateDuration = BatchMetrics.calculateDuration(startDate, endDate);
        Assertions.assertNotNull(calculateDuration, "Calculated duration is a null reference!");
        var formattedDurationString = BatchMetrics.formatDuration(calculateDuration);
        Assertions.assertTrue(StringUtils.hasText(formattedDurationString), formattedDurationString);
    }
```


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-21

報告ありがとうございます!

> **期待される動作**
> 正直なところ分かりませんが、少なくとも`0ms`の方が何もないよりは良いでしょう。

確かに、理にかなっています。次のパッチリリースで修正を予定しています。PRもありがとうございます 🙏

