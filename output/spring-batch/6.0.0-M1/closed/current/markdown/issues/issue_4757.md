# Enhancement : FlatFileItemReaderBuilder : raise check exception on build

**Issue番号**: #4757

**状態**: closed | **作成者**: frigaux | **作成日**: 2025-02-03

**ラベル**: in: infrastructure, type: bug, type: feature, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4757

## 内容

### Given concrete use case (X as record class)
`FlatFileItemReaderBuilder<X>()`
`...`
`.targetType(X::class.java)`
`.fieldSetMapper(myFieldSetMapper)`
`.build()`

**Expected Behavior**
When both **fieldSetMapper** and **targetType** are defined, a "BuildCheckException" should be raised in build method with "you cannot define both FieldSetMapper and targetType"

**Current Behavior**
FieldSetMapper is ignored and result in misunderstanding at runtime

Best regard


