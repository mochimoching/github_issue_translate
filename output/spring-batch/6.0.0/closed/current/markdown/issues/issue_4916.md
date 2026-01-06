# RecordFieldExtractor in FlatFileItemWriterBuilder doesn't reflect names() setting

**Issue番号**: #4916

**状態**: closed | **作成者**: kyb4312 | **作成日**: 2025-07-18

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4916

**関連リンク**:
- Commits:
  - [8f56f93](https://github.com/spring-projects/spring-batch/commit/8f56f9379149ee3d8ac08910be2cdf3125cc1d0f)
  - [0eeacd5](https://github.com/spring-projects/spring-batch/commit/0eeacd583ffbb2d47dd6ed9bc76f914fd320b496)

## 内容

This is related to [spring-projects/spring-batch#4908](https://github.com/spring-projects/spring-batch/issues/4908), which points out that using names() with a record type and sourceType() might seem redundant. While that discussion raises a valid concern, this issue is coming from a slightly different angle: it would be helpful if the names() setting actually worked when a record is used with sourceType(). That way, developers wouldn't be surprised when their field selections are silently ignored.

---
### **Bug description**
When using FlatFileItemWriterBuilder’s build() method with sourceType() set to a record class and specifying field names via names(), the RecordFieldExtractor used internally ignores the names() configuration.
In contrast, when sourceType() is not specified, the BeanWrapperFieldExtractor honors the names() configuration as expected.

This inconsistency can cause confusion, as the same record type behaves differently depending on whether sourceType() is provided.

---
### **Steps to reproduce**
```
public record MyRecord(String name, int age, String address) {}

FlatFileItemWriter<MyRecord> writer = new FlatFileItemWriterBuilder<MyRecord>()
    .name("myRecordWriter")
    .resource(new FileSystemResource("output.csv"))
    .sourceType(MyRecord.class)  // triggers RecordFieldExtractor
    .names("name", "age")        // currently ignored
    .delimited()
    .build();
```
Expected output: name, age
Actual output: name, age, address

---
### **Suggested Fix**

Update the builder to pass names into RecordFieldExtractor:

FlatFileItemWriterBuilder.build()

Before:
```
if (this.sourceType != null && this.sourceType.isRecord()) {
    this.fieldExtractor = new RecordFieldExtractor<>(this.sourceType);
}
```

After:
```
if (this.sourceType != null && this.sourceType.isRecord()) {
    RecordFieldExtractor<T> extractor = new RecordFieldExtractor<>(this.sourceType);
    extractor.setNames(this.names.toArray(new String[this.names.size()]));
    this.fieldExtractor = extractor;
}
```
This would make the behavior consistent and avoid surprises.

---
Let me know if you'd like a pull request with this change - I'd be happy to help!

powerd by KILL-9 💀

## コメント

### コメント 1 by LeeHyungGeol

**作成日**: 2025-10-04

Hello @fmbenhassine.

Would it be okay if i give it a try on this issue?

### コメント 2 by fmbenhassine

**作成日**: 2025-10-04

@LeeHyungGeol Sure! thank you for your offer to help 🙏

### コメント 3 by LeeHyungGeol

**作成日**: 2025-10-04

@fmbenhassine 

I've created a PR https://github.com/spring-projects/spring-batch/pull/5009 to address this issue. Could you please assign this issue to me?

Also, I noticed this issue is closely related to https://github.com/spring-projects/spring-batch/issues/4908. I'd greatly appreciate it if you could review them together.

Thank you!

