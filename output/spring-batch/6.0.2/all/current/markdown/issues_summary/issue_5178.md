*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

## 課題概要

`JobParametersConverter`に`ZonedDateTime`と`OffsetDateTime`のサポートを追加する機能リクエストです。グローバルサービスやマルチタイムゾーンアプリケーションでタイムゾーン情報を持つ日時をJobParametersとして渡す必要がある場合に対応します。

### Spring Batchの背景知識

| 用語 | 説明 |
|------|------|
| `JobParameters` | バッチジョブに渡すパラメータのコレクション |
| `JobParametersConverter` | `JobParameters`と`Properties`間の変換を行うインターフェース |
| `LocalDateTime` | タイムゾーン情報を持たない日時型 |
| `ZonedDateTime` | タイムゾーン情報（ZoneIdを含む）を持つ日時型 |
| `OffsetDateTime` | UTCからのオフセット情報を持つ日時型 |

### 現状の問題

Spring Batchでは以下の日時型のみサポート：
- `LocalDateTime`
- `LocalDate`
- `LocalTime`

タイムゾーン対応の型（`ZonedDateTime`、`OffsetDateTime`）用のコンバーターがないため、以下の回避策を取る必要がありました：

| 回避策 | 問題点 |
|--------|--------|
| `LocalDateTime`に変換 | タイムゾーン情報が失われる |
| `String`型で手動パース | 型安全でなくエラーが発生しやすい |
| `Date`＋タイムゾーンオフセット | レガシーAPI、非推奨 |

### 使用例

```java
// 期待される使用方法
ZonedDateTime scheduleTime = ZonedDateTime.of(
    2023, 12, 25, 10, 30, 0, 0, 
    ZoneId.of("Asia/Seoul")
);
JobParameters parameters = new JobParametersBuilder()
    .addJobParameter("schedule.time", scheduleTime, ZonedDateTime.class, true)
    .toJobParameters();
```

## 原因

Spring Batchのコンバーターがタイムゾーン対応の日時型に対応していなかったため。

## 対応方針

### PR [#5186](https://github.com/spring-projects/spring-batch/pull/5186)での修正内容

Spring Frameworkの`DefaultFormattingConversionService`を活用するアーキテクチャ変更を実施。

#### 新規クラス: ConversionServiceFactory.java

`ConfigurableConversionService`のファクトリクラスを新設：

```java
public final class ConversionServiceFactory {
    
    public static ConfigurableConversionService createConversionService() {
        FormattingConversionService conversionService = 
            new DefaultFormattingConversionService();
        conversionService.addFormatterForFieldType(Date.class, new DateFormatter());

        DateTimeFormatterRegistrar dateTimeFormatterRegistrar = 
            new DateTimeFormatterRegistrar();
        dateTimeFormatterRegistrar.setUseIsoFormat(true);
        dateTimeFormatterRegistrar.registerFormatters(conversionService);

        return conversionService;
    }
}
```

#### 新規クラス: DateFormatter.java

`Date`型のISO_INSTANTフォーマット対応フォーマッター：

```java
class DateFormatter implements Formatter<Date> {
    private final DateTimeFormatter formatter = DateTimeFormatter.ISO_INSTANT;

    @Override
    public Date parse(String text, Locale locale) {
        return Date.from(formatter.parse(text, Instant::from));
    }

    @Override
    public String print(Date object, Locale locale) {
        return formatter.format(object.toInstant());
    }
}
```

#### 既存コンバーターの非推奨化

以下のコンバーターは6.1で`@Deprecated`とし、6.3以降で削除予定：

- `DateToStringConverter` / `StringToDateConverter`
- `LocalDateToStringConverter` / `StringToLocalDateConverter`
- `LocalTimeToStringConverter` / `StringToLocalTimeConverter`
- `LocalDateTimeToStringConverter` / `StringToLocalDateTimeConverter`
- `AbstractDateTimeConverter`

#### DefaultJobParametersConverter の変更

```diff
 public class DefaultJobParametersConverter implements JobParametersConverter {

-    protected ConfigurableConversionService conversionService;
-
-    public DefaultJobParametersConverter() {
-        DefaultConversionService conversionService = new DefaultConversionService();
-        conversionService.addConverter(new DateToStringConverter());
-        conversionService.addConverter(new StringToDateConverter());
-        // ... 他のコンバーター登録
-        this.conversionService = conversionService;
-    }
+    protected ConfigurableConversionService conversionService = 
+        ConversionServiceFactory.createConversionService();
```

### サポートされるフォーマット

修正後、以下の日時型とフォーマットがサポートされます：

| 型 | フォーマット |
|---|-------------|
| `Date` | `ISO_INSTANT` |
| `LocalDate` | `ISO_LOCAL_DATE` |
| `LocalTime` | `ISO_LOCAL_TIME` |
| `LocalDateTime` | `ISO_LOCAL_DATE_TIME` |
| `ZonedDateTime` | `ISO_ZONED_DATE_TIME` |
| `OffsetDateTime` | `ISO_OFFSET_DATE_TIME` |

### リリース計画

- **6.0.2**: PR [#5179](https://github.com/spring-projects/spring-batch/pull/5179)（個別コンバーター追加版）
- **6.1.0**: PR [#5186](https://github.com/spring-projects/spring-batch/pull/5186)（Spring Framework連携版）

### 関連リンク

- Issue: https://github.com/spring-projects/spring-batch/issues/5178
- PR #5179: 個別コンバーター追加
- PR #5186: Spring Framework `DefaultFormattingConversionService`活用
- 関連コミット: [077a332](https://github.com/spring-projects/spring-batch/commit/077a33238b8990e6993fb29a35dc9204b315a339)
