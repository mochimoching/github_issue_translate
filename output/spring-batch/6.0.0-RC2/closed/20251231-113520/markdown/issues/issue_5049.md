# JobParameter constructor validates wrong parameter (value instead of name)

**Issue番号**: #5049

**状態**: closed | **作成者**: KMGeon | **作成日**: 2025-10-24

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5049

**関連リンク**:
- Commits:
  - [b5c10c2](https://github.com/spring-projects/spring-batch/commit/b5c10c2301a5f58805c3a670261b07321fd0ac7d)

## 内容

## Issue Description

### Summary
The `JobParameter` record's compact constructor has a bug in parameter validation. It validates the `value` parameter twice instead of validating both `name` and `value` parameters.

---

## Current Behavior

```java
public record JobParameter<T>(String name, T value, Class<T> type, boolean identifying) implements Serializable {
    public JobParameter {
        Assert.notNull(value, "name must not be null");  // ❌ Bug: validates 'value' but message says 'name'
        Assert.notNull(value, "value must not be null"); // ❌ Bug: validates 'value' twice
        Assert.notNull(type, "type must not be null");
    }
}
```

---

## Expected Behavior

```java
public record JobParameter<T>(String name, T value, Class<T> type, boolean identifying) implements Serializable {
    public JobParameter {
        Assert.notNull(name, "name must not be null");   // ✅ Correct: validates 'name'
        Assert.notNull(value, "value must not be null"); // ✅ Correct: validates 'value'
        Assert.notNull(type, "type must not be null");
    }
}
```

---


## Steps to Reproduce

### 1. Create Test Case

```java
@Test
void testNameParameterIsNull() {
    JobParameter<String> jobParameter = new JobParameter<>(null, "test", String.class, true);
    assertEquals("param", jobParameter.name());
    assertEquals("test", jobParameter.value());
    assertEquals(String.class, jobParameter.type());
    assertTrue(jobParameter.identifying());
}
```

### 2. Test Result

The test demonstrates that a `JobParameter` can be created with a `null` name, which should not be allowed:

```
[ERROR] Failures: 
[ERROR]   JobParameterTests.testNameParameterIsNull:37 expected: <param> but was: <null>
[INFO] 
[ERROR] Tests run: 7, Failures: 1, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.049 s
[INFO] Finished at: 2025-10-25T01:43:01+09:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.5.3:test (default-test) on project spring-batch-core: There are test failures.
```

### 3. Analysis

The test fails because:
1. **No exception is thrown** when `name` is `null` during object construction (due to the validation bug)
2. The object is created successfully with `name = null`
3. The assertion `assertEquals("param", jobParameter.name())` fails because the actual value is `null`

This proves that the validation is not working correctly.

---

## Environment

- **Spring Batch Version:** 6.0.0-SNAPSHOT
- **Java Version:** 21
- **File:** `org.springframework.batch.core.job.parameters.JobParameter`

---

## Proposed Fix

### Change Required

**Line 41** - Change from:
```java
Assert.notNull(value, "name must not be null");
```

**To:**
```java
Assert.notNull(name, "name must not be null");
```

### Complete Fixed Constructor

```java
public JobParameter {
    Assert.notNull(name, "name must not be null");   // ✅ Fixed: validates 'name' correctly
    Assert.notNull(value, "value must not be null");
    Assert.notNull(type, "type must not be null");
}
```

