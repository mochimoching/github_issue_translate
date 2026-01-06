# JsonObjectReader fails to read JSON array format due to Jackson 3.0 FAIL_ON_TRAILING_TOKENS default change

**Issue番号**: #5047

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-24

**ラベル**: in: infrastructure, type: bug, related-to: item-readers-writers

**URL**: https://github.com/spring-projects/spring-batch/issues/5047

**関連リンク**:
- Commits:
  - [c534e6c](https://github.com/spring-projects/spring-batch/commit/c534e6c367ad705163a825d3d9ebee73f4f87e4c)

## 内容

Hi Spring Batch team!
First of all, thank you for your amazing work on Spring Batch 6.0

I've encountered an issue when reading JSON array files with JsonItemReader in Spring Batch 6.0 with Spring Boot 4(use jackson 3.0), and I wanted to report it in case it affects other users migrating to this version.




**Bug description**
`JacksonJsonObjectReader`(used by JsonItemReader) cannot read JSON array format `[{...}, {...}]` when using the default constructor in Spring Batch 6.0 with Jackson 3.0. 

This appears to be caused by Jackson 3.0's change where `DeserializationFeature.FAIL_ON_TRAILING_TOKENS` default was changed from `false` to `true` ([Jackson JSTEP-2](https://github.com/FasterXML/jackson-future-ideas/wiki/JSTEP-2#deserializationfeature)).

When reading a JSON array, after parsing the first object, the second object's start token `{` is detected as a "trailing token", causing a `MismatchedInputException`.

**Environment**
- Spring Boot: 4.0.0-SNAPSHOT / spring-boot-starter-json 4.0.0-SNAPSHOT
- Spring Batch: 6.0.0-RC1
- Jackson: 3.0.1
- Java: 21

**Steps to reproduce**
1. Create a JSON array file:
```bash
echo '[
{"command": "destroy", "cpu": 99, "status": "memory overflow"},
{"command": "explode", "cpu": 100, "status": "cpu meltdown"},
{"command": "collapse", "cpu": 95, "status": "disk burnout"}
]' > system_death.json
```

2. Configure `JsonItemReader` with default `JacksonJsonObjectReader`:
```java
@Bean
@StepScope
public JsonItemReader systemFailureItemReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new JsonItemReaderBuilder()
            .name("systemFailureItemReader")
            .jsonObjectReader(new JacksonJsonObjectReader<>(SystemFailure.class))
            .resource(new FileSystemResource(inputFile))
            .build();
}

public record SystemFailure(String command, int cpu, String status) {}
```

3. Run the job with the JSON array file



**Expected behavior**

`JsonItemReader` should successfully read all objects from the JSON array `[{...}, {...}, {...}]` without requiring manual Jackson configuration, as JSON arrays are a common input format for batch processing.

**Actual behavior**

Job fails with:
```
tools.jackson.databind.exc.MismatchedInputException: Trailing token (JsonToken.START_OBJECT) found after value (bound as SystemFailure): not allowed as per DeserializationFeature.FAIL_ON_TRAILING_TOKENS
```

**Minimal Complete Reproducible example**

Here's the complete configuration that reproduces the issue:
```java
@Bean
public Job systemFailureJob(Step systemFailureStep) {
    return new JobBuilder("systemFailureJob", jobRepository)
            .start(systemFailureStep)
            .build();
}

@Bean
public Step systemFailureStep(JsonItemReader systemFailureItemReader) {
    return new StepBuilder("systemFailureStep", jobRepository)
            .chunk(10)
            .reader(systemFailureItemReader)
            .writer(items -> items.forEach(item -> log.info("{}", item)))
            .build();
}

@Bean
@StepScope
public JsonItemReader systemFailureItemReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    return new JsonItemReaderBuilder()
            .name("systemFailureItemReader")
            .jsonObjectReader(new JacksonJsonObjectReader<>(SystemFailure.class))
            .resource(new FileSystemResource(inputFile))
            .build();
}

public record SystemFailure(String command, int cpu, String status) {}
```

**Current Workaround**

manually creating a `JsonMapper` with `FAIL_ON_TRAILING_TOKENS` disabled resolves the issue:
```java
@Bean
@StepScope
public JsonItemReader systemFailureItemReader(
        @Value("#{jobParameters['inputFile']}") String inputFile) {
    
    JsonMapper jsonMapper = JsonMapper.builder()
            .disable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS)
            .build();
    
    JacksonJsonObjectReader jsonReader =
            new JacksonJsonObjectReader<>(jsonMapper, SystemFailure.class);
    
    return new JsonItemReaderBuilder()
            .name("systemFailureItemReader")
            .jsonObjectReader(jsonReader)
            .resource(new FileSystemResource(inputFile))
            .build();
}
```

**Suggested Solutions**

I'd like to humbly suggest two possible approaches:

1. **Update `JacksonJsonObjectReader` default constructor** to create a `JsonMapper` with `FAIL_ON_TRAILING_TOKENS` disabled by default, since JSON array reading is a fundamental use case for `JsonItemReader`

2. **Update the documentation** to clearly guide users that manual `JsonMapper` configuration with `FAIL_ON_TRAILING_TOKENS` disabled is required when reading JSON arrays in Spring Batch 6.0+


Thank you again for maintaining Spring Batch! Please let me know if you need any additional information or clarification.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-10-28

Thank you for raising this issue! Indeed, it was expected that the user disables `FAIL_ON_TRAILING_TOKENS` before passing the Jackson mapper to `JacksonJsonItemReader` (see [here](https://github.com/spring-projects/spring-batch/blob/main/spring-batch-infrastructure/src/test/java/org/springframework/batch/infrastructure/item/json/JacksonJsonItemReaderFunctionalTests.java#L34)), but you are right, it's better to make that the default since the `JsonItemReader` is expected to correctly read json files having the `[{...}, {...}, {...}]` format.

I will plan that change for the upcoming 6.0.0-RC2.

