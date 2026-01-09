# Minor logging issue when a step or job completes instantly

**Issue番号**: #5037

**状態**: closed | **作成者**: janossch | **作成日**: 2025-10-20

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5037

**関連リンク**:
- Commits:
  - [249330b](https://github.com/spring-projects/spring-batch/commit/249330b2718492424c2df9b452279c9601c2802e)
  - [1d50d82](https://github.com/spring-projects/spring-batch/commit/1d50d829907a580fe3aea5b6a17859a418e478b9)
  - [f3ccc74](https://github.com/spring-projects/spring-batch/commit/f3ccc7405c9d8f1c1f8a33fdfbbcbe143799e8f7)

## 内容

**Bug description**
We found such below log lines in our production environment, which misses the duration information at the end of the line.

... `Job: [FlowJob: [name=...]] completed with the following parameters: [...] and the following status: [FAILED] in `

Digging into a little bit of the code, I found that when a job is finished
https://github.com/spring-projects/spring-batch/blob/11ec7f12e8e4477ae802a02ee72f69f78afbf25b/spring-batch-core/src/main/java/org/springframework/batch/core/launch/support/TaskExecutorJobLauncher.java#L221-L228

an info level log entry gets emitted by the framework. However if the start and the end date is essentially the same, the `BatchMetrics.formatDuration` method returns an empty `String` because of the `duration.isZero()` condition.

https://github.com/spring-projects/spring-batch/blob/11ec7f12e8e4477ae802a02ee72f69f78afbf25b/spring-batch-core/src/main/java/org/springframework/batch/core/observability/BatchMetrics.java#L69-L72

**Environment**
Java21 (temurin)
Spring Batch 5.2.2
File based H2 DB is used

**Steps to reproduce**
Start a lot of batch jobs which completes fast.

**Expected behavior**
Honestly I don't know, but at least a `0ms` would be better than nothing. Something like this:
`Job: [FlowJob: [name=...]] completed with the following parameters: [...] and the following status: [FAILED] in 0ms`

**Minimal Complete Reproducible example**

The below test fails for 5.2.2:
```
    @Test
    void testFormatDurationWhenCalculationReturnsZeroDuration() {
        var startDate = LocalDateTime.now();
        // create end date from the string representation of start date to ensure both dates are equal, but different references.
        // In reality there is another LocalDateTime.now() call, but that could return a different time, which could cause flaky tests.
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

Thank you for reporting this!

> **Expected behavior**
> Honestly I don't know, but at least a `0ms` would be better than nothing.

Sure, makes sense. I planned the fix for the next patch release. Thank you for the PR as well 🙏

