# Incorrect deprecation warning in `JobOperatorTestUtils.getJob()`

**Issue番号**: #5123

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-02

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5123

**関連リンク**:
- Commits:
  - [4216a0a](https://github.com/spring-projects/spring-batch/commit/4216a0a5834d90f0063cfe6ec32bc45c1e9d260b)

## 内容

`JobOperatorTestUtils` does not override and "un-deprecate" `getJob()`.
This causes unnecessary deprecation warnings to be raised for clients.

