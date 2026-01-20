# Add ZonedDateTime and OffsetDateTime support to JobParametersConverter

**Issue番号**: #5178

**状態**: closed | **作成者**: thswlsqls | **作成日**: 2025-12-21

**ラベル**: type: feature, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5178

**関連リンク**:
- Commits:
  - [077a332](https://github.com/spring-projects/spring-batch/commit/077a33238b8990e6993fb29a35dc9204b315a339)
  - [868849e](https://github.com/spring-projects/spring-batch/commit/868849e9911782899affd01d4a70b7b31d18c242)

## 内容

**Expected Behavior**

`ZonedDateTime` and `OffsetDateTime` should be supported as JobParameters types, similar to `LocalDateTime`, `LocalDate`, and `LocalTime`.

Example usage:
```java
ZonedDateTime scheduleTime = ZonedDateTime.of(2023, 12, 25, 10, 30, 0, 0, ZoneId.of("Asia/Seoul"));
JobParameters parameters = new JobParametersBuilder()
    .addJobParameter("schedule.time", scheduleTime, ZonedDateTime.class, true)
    .toJobParameters();
```

**Current Behavior**

Spring Batch currently only provides converters for `LocalDateTime`, `LocalDate`, and `LocalTime`. 
`ZonedDateTime` and `OffsetDateTime` cannot be used as JobParameters because there are no converters available.

**Context**

**How has this issue affected you?**
When working with global services or multi-timezone applications, we need to pass timezone-aware date/time values as JobParameters, but currently only timezone-naive types (`LocalDateTime`, `LocalDate`, `LocalTime`) are supported.

**What are you trying to accomplish?**
- Execute batch jobs based on specific timezones in global services
- Require both UTC and local timezone in log analysis
- Include timezone information for each country in multi-country services

**What other alternatives have you considered?**
- Converting to `LocalDateTime` and storing timezone separately (loses timezone information)
- Using `String` type and parsing manually (error-prone, not type-safe)
- Using `Date` with timezone offset (legacy API, not recommended)

**Are you aware of any workarounds?**
Currently, there is no clean workaround. Users must convert to `LocalDateTime` and lose timezone information, or use `String` type which is not type-safe.

**Proposed Implementation:**
- Add `ZonedDateTimeToStringConverter` and `StringToZonedDateTimeConverter`
- Add `OffsetDateTimeToStringConverter` and `StringToOffsetDateTimeConverter`
- Register new converters in `DefaultJobParametersConverter`
- Add related test code

## コメント

### コメント 1 by scordio

**作成日**: 2025-12-21

> Currently, there is no clean workaround. Users must convert to `LocalDateTime` and lose timezone information, or use `String` type which is not type-safe.  

That's not entirely true. In an average Spring Boot application, this conversion capability could be obtained out of the box when defining a [`DefaultFormattingConversionService`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/format/support/DefaultFormattingConversionService.html) bean in the Spring context:

```java
import org.springframework.format.support.DefaultFormattingConversionService;

@Bean
DefaultFormattingConversionService conversionService() {
  return new DefaultFormattingConversionService();
}
```

This allows the use of job parameters like the following:

```java
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.format.annotation.DateTimeFormat.ISO;

@Bean
@StepScope
ItemReader<Item> itemReader(@Value("#{jobParameters['targetDate']}") @DateTimeFormat(iso = ISO.DATE) LocalDate targetDate) {
  ...
}
```

The same should also work with [`ZonedDateTime`](https://github.com/spring-projects/spring-framework/blob/0b2bb7e751d5effd798adaf545c64a7342657ecc/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L180-L182) and [`OffsetDateTime`](https://github.com/spring-projects/spring-framework/blob/0b2bb7e751d5effd798adaf545c64a7342657ecc/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L184-L186).

Nevertheless, it would be nice if Spring Batch would offer this out of the box.
 
> * Register new converters in `DefaultJobParametersConverter`

As Spring Batch already depends on `spring-context`, what about instantiating a `DefaultFormattingConversionService` instead of `DefaultConversionService` in the `DefaultJobParametersConverter` constructor?

https://github.com/spring-projects/spring-batch/blob/2cc7890be100034f66bab9b4297de93dfbfad3a3/spring-batch-core/src/main/java/org/springframework/batch/core/converter/DefaultJobParametersConverter.java#L79

Some existing custom converters in Spring Batch might also become obsolete.

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

@thswlsqls Thank you for opening this issue and contributing a PR!

@scordio Thank you for the follow up and for the PR as well!

Both PRs LGTM 👍  I think we can merge #5179 for 6.0.2 and then #5186 in 6.1.0 so that users don't have to wait a year or more to get these two converters (and indeed, it's better to leverage converters from Spring Framework as in #5186). 

### コメント 3 by scordio

**作成日**: 2026-01-13

I'll rebase #5186 once #5179 is merged.

### コメント 4 by fmbenhassine

**作成日**: 2026-01-15

@scordio FYI, #5179 was merged.

