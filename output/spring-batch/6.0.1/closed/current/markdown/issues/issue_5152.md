# Class JobParametersInvalidException mentioned in "Spring Batch 6.0 Migration Guide" but is not available in 6.0.0

**Issue番号**: #5152

**状態**: closed | **作成者**: sebeichholz | **作成日**: 2025-12-09

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5152

## 内容

The [Spring Batch 6.0 Migration Guide](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide) says that the class **JobParametersInvalidException** was moved to a new package.

The class was in 6.0.0-M3 , but in 6.0.0 the class appears to have been renamed to "InvalidJobParametersException".

So perhaps the Migration Guide should be updated. Thanks!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-10

Thank you for reporting this issue! Indeed, that class was renamed as part of #5013.

I fixed the migration guide accordingly.

