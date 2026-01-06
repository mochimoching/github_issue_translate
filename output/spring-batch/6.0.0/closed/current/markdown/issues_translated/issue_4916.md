*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# FlatFileItemWriterBuilderのRecordFieldExtractorがnames()設定を反映しない

**Issue番号**: #4916

**状態**: closed | **作成者**: kyb4312 | **作成日**: 2025-07-18

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4916

**関連リンク**:
- Commits:
  - [8f56f93](https://github.com/spring-projects/spring-batch/commit/8f56f9379149ee3d8ac08910be2cdf3125cc1d0f)
  - [0eeacd5](https://github.com/spring-projects/spring-batch/commit/0eeacd583ffbb2d47dd6ed9bc76f914fd320b496)

## 内容

これは[spring-projects/spring-batch#4908](https://github.com/spring-projects/spring-batch/issues/4908)に関連しており、recordタイプと`sourceType()`で`names()`を使用することが冗長に見える可能性があると指摘しています。その議論は妥当な懸念を提起していますが、このissueは少し異なる角度から来ています。recordが`sourceType()`と共に使用される場合、`names()`設定が実際に機能すると便利です。そうすれば、開発者はフィールド選択が静かに無視されても驚かないでしょう。

---
### **バグの説明**
`FlatFileItemWriterBuilder`の`build()`メソッドを使用する際、`sourceType()`をrecordクラスに設定し、`names()`でフィールド名を指定すると、内部で使用される`RecordFieldExtractor`が`names()`の設定を無視します。
対照的に、`sourceType()`が指定されていない場合、`BeanWrapperFieldExtractor`は予想通りに`names()`の設定を尊重します。

この不整合により、同じrecordタイプが`sourceType()`が提供されているかどうかによって異なる動作をするため、混乱を引き起こす可能性があります。

---
### **再現手順**
```
public record MyRecord(String name, int age, String address) {}

FlatFileItemWriter<MyRecord> writer = new FlatFileItemWriterBuilder<MyRecord>()
    .name("myRecordWriter")
    .resource(new FileSystemResource("output.csv"))
    .sourceType(MyRecord.class)  // RecordFieldExtractorをトリガー
    .names("name", "age")        // 現在無視される
    .delimited()
    .build();
```
期待される出力: name, age
実際の出力: name, age, address

---
### **提案する修正**

ビルダーを更新して、`names`を`RecordFieldExtractor`に渡すようにします:

FlatFileItemWriterBuilder.build()

修正前:
```
if (this.sourceType != null && this.sourceType.isRecord()) {
    this.fieldExtractor = new RecordFieldExtractor<>(this.sourceType);
}
```

修正後:
```
if (this.sourceType != null && this.sourceType.isRecord()) {
    RecordFieldExtractor<T> extractor = new RecordFieldExtractor<>(this.sourceType);
    extractor.setNames(this.names.toArray(new String[this.names.size()]));
    this.fieldExtractor = extractor;
}
```
これにより、動作が一貫性を持ち、驚きを避けることができます。

---
この変更を含むプルリクエストが必要であれば、ぜひお手伝いさせてください!

powered by KILL-9 💀

## コメント

### コメント 1 by LeeHyungGeol

**作成日**: 2025-10-04

こんにちは @fmbenhassine。

このissueに取り組んでもよろしいでしょうか?

### コメント 2 by fmbenhassine

**作成日**: 2025-10-04

@LeeHyungGeol もちろんです! 助けてくれる申し出をありがとうございます 🙏

### コメント 3 by LeeHyungGeol

**作成日**: 2025-10-04

@fmbenhassine 

このissueに対処するためにPR https://github.com/spring-projects/spring-batch/pull/5009 を作成しました。このissueを私にアサインしていただけますか?

また、このissueは https://github.com/spring-projects/spring-batch/issues/4908 に密接に関連していることに気づきました。一緒にレビューしていただければ大変ありがたいです。

ありがとうございます!


