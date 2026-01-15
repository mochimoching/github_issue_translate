*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

# JobParametersConverterにZonedDateTimeとOffsetDateTimeのサポートを追加

**Issue番号**: [#5178](https://github.com/spring-projects/spring-batch/issues/5178)

**状態**: open | **作成者**: thswlsqls | **作成日**: 2025-12-21

**ラベル**: type: feature, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5178

**関連リンク**:
- コミット:
  - [077a332](https://github.com/spring-projects/spring-batch/commit/077a33238b8990e6993fb29a35dc9204b315a339)

## 内容

**期待される動作**

`ZonedDateTime`と`OffsetDateTime`は、`LocalDateTime`、`LocalDate`、`LocalTime`と同様に、JobParametersの型としてサポートされるべきです。

使用例:
```java
ZonedDateTime scheduleTime = ZonedDateTime.of(2023, 12, 25, 10, 30, 0, 0, ZoneId.of("Asia/Seoul"));
JobParameters parameters = new JobParametersBuilder()
    .addJobParameter("schedule.time", scheduleTime, ZonedDateTime.class, true)
    .toJobParameters();
```

**現在の動作**

Spring Batchは現在、`LocalDateTime`、`LocalDate`、`LocalTime`用のコンバーターのみを提供しています。
`ZonedDateTime`と`OffsetDateTime`は利用可能なコンバーターがないため、JobParametersとして使用できません。

**背景**

**この問題はどのように影響していますか？**
グローバルサービスやマルチタイムゾーンアプリケーションで作業する場合、タイムゾーン対応の日時値をJobParametersとして渡す必要がありますが、現在はタイムゾーン非対応の型（`LocalDateTime`、`LocalDate`、`LocalTime`）のみがサポートされています。

**何を達成しようとしていますか？**
- グローバルサービスで特定のタイムゾーンに基づいてバッチジョブを実行する
- ログ分析でUTCとローカルタイムゾーンの両方が必要
- 複数国対応サービスで各国のタイムゾーン情報を含める

**他にどのような代替案を検討しましたか？**
- `LocalDateTime`に変換してタイムゾーンを別途保存する（タイムゾーン情報が失われる）
- `String`型を使用して手動でパースする（エラーが発生しやすく、型安全ではない）
- タイムゾーンオフセット付きの`Date`を使用する（レガシーAPI、推奨されない）

**回避策はご存知ですか？**
現在、クリーンな回避策はありません。ユーザーは`LocalDateTime`に変換してタイムゾーン情報を失うか、型安全ではない`String`型を使用する必要があります。

**提案する実装:**
- `ZonedDateTimeToStringConverter`と`StringToZonedDateTimeConverter`を追加
- `OffsetDateTimeToStringConverter`と`StringToOffsetDateTimeConverter`を追加
- `DefaultJobParametersConverter`に新しいコンバーターを登録
- 関連するテストコードを追加

## コメント

### コメント 1 by scordio

**作成日**: 2025-12-21

> 現在、クリーンな回避策はありません。ユーザーはLocalDateTimeに変換してタイムゾーン情報を失うか、型安全ではないString型を使用する必要があります。

それは完全には正確ではありません。標準的なSpring Bootアプリケーションでは、Springコンテキストに[`DefaultFormattingConversionService`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/format/support/DefaultFormattingConversionService.html)ビーンを定義することで、この変換機能をすぐに利用できます:

```java
import org.springframework.format.support.DefaultFormattingConversionService;

@Bean
DefaultFormattingConversionService conversionService() {
  return new DefaultFormattingConversionService();
}
```

これにより、以下のようなジョブパラメータを使用できます:

```java
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.format.annotation.DateTimeFormat.ISO;

@Bean
@StepScope
ItemReader<Item> itemReader(@Value("#{jobParameters['targetDate']}") @DateTimeFormat(iso = ISO.DATE) LocalDate targetDate) {
  ...
}
```

同じことが[`ZonedDateTime`](https://github.com/spring-projects/spring-framework/blob/0b2bb7e751d5effd798adaf545c64a7342657ecc/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L180-L182)と[`OffsetDateTime`](https://github.com/spring-projects/spring-framework/blob/0b2bb7e751d5effd798adaf545c64a7342657ecc/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L184-L186)でも機能するはずです。

とはいえ、Spring Batchがこれをすぐに使える形で提供してくれると良いでしょう。

> * DefaultJobParametersConverterに新しいコンバーターを登録

Spring Batchはすでに`spring-context`に依存しているので、`DefaultJobParametersConverter`コンストラクタで`DefaultConversionService`の代わりに`DefaultFormattingConversionService`をインスタンス化するのはどうでしょうか？

https://github.com/spring-projects/spring-batch/blob/2cc7890be100034f66bab9b4297de93dfbfad3a3/spring-batch-core/src/main/java/org/springframework/batch/core/converter/DefaultJobParametersConverter.java#L79

Spring Batchの既存のカスタムコンバーターの一部も不要になるかもしれません。

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@thswlsqls この課題のオープンとPRへの貢献ありがとうございます！

@scordio フォローアップとPRもありがとうございます！

両方のPRは良さそうです 👍 ユーザーがこれら2つのコンバーターを1年以上待たなくて済むように、6.0.2で[#5179](https://github.com/spring-projects/spring-batch/issues/5179)をマージし、その後6.1.0で[#5186](https://github.com/spring-projects/spring-batch/issues/5186)をマージできると思います（確かに、#5186のようにSpring Frameworkのコンバーターを活用する方が良いです）。

### コメント 3 by scordio

**作成日**: 2026-01-13

[#5179](https://github.com/spring-projects/spring-batch/issues/5179)がマージされたら[#5186](https://github.com/spring-projects/spring-batch/issues/5186)をリベースします。
