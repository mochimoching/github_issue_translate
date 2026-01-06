*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# 機能強化：FlatFileItemReaderBuilder：ビルド時にチェック例外を発生させる

**Issue番号**: #4757

**状態**: closed | **作成者**: frigaux | **作成日**: 2025-02-03

**ラベル**: in: infrastructure, type: bug, type: feature, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4757

## 内容

### 具体的な使用例（Xをレコードクラスとして）
`FlatFileItemReaderBuilder<X>()`
`...`
`.targetType(X::class.java)`
`.fieldSetMapper(myFieldSetMapper)`
`.build()`

**期待される動作**
`fieldSetMapper`と`targetType`の両方が定義されている場合、buildメソッドで「fieldSetMapperとtargetTypeの両方を定義することはできません」というメッセージとともに「BuildCheckException」が発生するべきです。

**現在の動作**
`FieldSetMapper`が無視され、実行時に誤解を招く結果となります。

よろしくお願いします。
