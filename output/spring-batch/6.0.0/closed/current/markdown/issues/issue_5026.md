# Document requirements of CommandLineJobOperator in the reference docs

**Issue番号**: #5026

**状態**: closed | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-10-15

**ラベル**: in: documentation, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5026

**関連リンク**:
- Commits:
  - [acc48a3](https://github.com/spring-projects/spring-batch/commit/acc48a3a3bc76ae85e0d936f260e5e6594c7ba9a)

## 内容

Hello Spring Batch team,

Thank you for all your great work on Spring Batch 6! I've been testing the milestone releases and came across what might be an issue or a documentation gap regarding `CommandLineJobOperator` and `JobRegistry` configuration.


**Bug description**
After [#4971](https://github.com/spring-projects/spring-batch/issues/4971), `JobRegistry` was made optional and is no longer automatically registered as a bean in Spring Batch configuration. 

However, `CommandLineJobOperator` (introduced in [#4899](https://github.com/spring-projects/spring-batch/issues/4899)) explicitly requires a `JobRegistry` bean from the `ApplicationContext`, causing it to fail with both `@EnableBatchProcessing` and `DefaultBatchConfiguration`.

**Environment**
- Spring Batch version: 6.0.0-M4


**Steps to reproduce** / **Minimal Complete Reproducible example**
**With `DefaultBatchConfiguration`:**
```java
@Configuration
public class BatchConfig extends DefaultBatchConfiguration {
    // No JobRegistry bean
}
```

**Or with `@EnableBatchProcessing`:**
```java
@Configuration
@EnableBatchProcessing
public class BatchConfig {
    // No JobRegistry bean
}
```

**Then run:**
```bash
java CommandLineJobOperator my.package.BatchConfig start myJob
```

**Result:** Application fails with error.

**Expected behavior**
`CommandLineJobOperator` should work with the default Spring Batch configuration, or the documentation should clearly state that manual `JobRegistry` bean registration is required.

**Actual behavior**
Application fails with:
```
A required bean was not found in the application context: 
No qualifying bean of type 'org.springframework.batch.core.configuration.JobRegistry' available
```

**Error location:**
The error occurs in `CommandLineJobOperator.main()` at line 314:
```java
public static void main(String[] args) {
    ...
    jobRegistry = context.getBean(JobRegistry.class);  // ← Fails here (line 314)
    ...
}

**Current Workaround**
Users must manually register `JobRegistry` as a bean:

**With `DefaultBatchConfiguration`:**
```java
@Configuration
public class BatchConfig extends DefaultBatchConfiguration {
    
    @Bean
    public JobRegistry jobRegistry() {
        return new MapJobRegistry();
    }
    
    @Override
    protected JobRegistry getJobRegistry() {
        return applicationContext.getBean(JobRegistry.class);
    }
}
```

**Question**
Is this the intended behavior? Since #4971 made `JobRegistry` optional, we're wondering if `CommandLineJobOperator` is expected to require manual `JobRegistry` bean registration, or if this is an unintended side effect.

If manual registration is the intended approach, it would be very helpful to have this documented with examples for both configuration styles (`@EnableBatchProcessing` and `DefaultBatchConfiguration`).

would appreciate any clarification on the expected usage pattern. Thank you!


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

Thank you for reporting this issue. I think this is documented in the Javadoc of the class, here is an excerpt:

```
This utility requires a Spring application context to be set up with the necessary batch infrastructure, including a `JobOperator`, a `JobRepository`, and a `JobRegistry` populated with the jobs to operate.
```

When the job registry bean is not defined in the context, the user should get this message (see [here](https://github.com/spring-projects/spring-batch/blob/4646a4479a44ae1d836f7053c41c4af09f7a9e1a/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/CommandLineJobOperator.java#L319-L330)):

```
A required bean was not found in the application context: [...]
```



> I've been testing the milestone releases and came across what might be an issue or a documentation gap regarding `CommandLineJobOperator` and `JobRegistry` configuration.

So I guess this is not an issue but a documentation gap, we need to update the reference docs in addition to the javadoc. I will turn this into a documentation enhancement.

### コメント 2 by KILL9-NO-MERCY

**作成日**: 2025-11-17

Thank you for your clear response.

I agree with your assessment that this is a documentation gap rather than a technical issue, and I appreciate you turning it into a documentation enhancement ticket!

