# JobLauncherTestUtils throws an NPE at getJobLauncher() in Batch 6 RC2

**Issue番号**: #5090

**状態**: closed | **作成者**: lucas-gautier | **作成日**: 2025-11-17

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5090

**関連リンク**:
- Commits:
  - [5b80510](https://github.com/spring-projects/spring-batch/commit/5b8051001475d4529239390820a419ff4aceb792)

## 内容

**Bug description**
The just-deprecated JobLauncherTestUtils throws an NPE at getJobLauncher() in Batch 6 RC2 in unit tests.
Tests using JobLauncherTestUtils fail while tests using the new JobOperatorTestUtils work as expected in RC2.

**Environment**
Spring Boot 4.0.0 RC2
Spring Batch 6.0.0 RC2
Mandrel/Temurin JDK 25.0.1+8

**Steps to reproduce**
1. Open "batch-rc2" reproducible example and run the tests `./gradlew test` to see the failing tests
    - Stacktrace here: `build/reports/tests/test/index.html`
2. Build the project skipping tests `./gradlew build -x test` and run the jobs specified in the example section
3. Optionally, see the "batch5" project to see passing tests using JobLauncherTestUtils on boot 3.5.7 and batch 5.2.4.

**Expected behavior**
Tests written using the deprecated JobLauncherTestUtils should still work correctly until removal in Batch 7.

**Minimal Complete Reproducible example**
The "batch6-rc2" project contains the failing tests using JobLauncherTestUtils and passing tests using the new JobOperatorTestUtils.
The "batch5" project has passing tests using JobLauncherTestUtils.

Both projects have the same 2 jobs that be ran via the jar (skip tests in the batch6-rc2 project):
```
java -jar build/libs/*jar --spring.batch.job.name=HelloJob
java -jar build/libs/*jar --spring.batch.job.name=GoodbyeJob
```

[batch5.tgz](https://github.com/user-attachments/files/23571876/batch5.tgz)
[batch6-rc2.tgz](https://github.com/user-attachments/files/23571878/batch6-rc2.tgz)

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

That's a valid issue, thank you for reporting it! I will plan the fix for the upcoming GA.

### コメント 2 by lucas-gautier

**作成日**: 2025-11-17

Thanks so much, Ben!

