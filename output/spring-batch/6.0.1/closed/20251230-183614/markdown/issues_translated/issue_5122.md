# `MapJobRegistry`が発見されたJobをジョブ名ではなくBean名で登録する

**Issue番号**: #5122

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-02

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5122

**関連リンク**:
- Commits:
  - [184ac31](https://github.com/spring-projects/spring-batch/commit/184ac31f704935c6d49865839713cd3126ce7cd3)

## 内容

課題 [#4855](https://github.com/spring-projects/spring-batch/issues/4855) で行われた変更は、発見された`Job`の_名前_を無視しています:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/support/MapJobRegistry.java#L63-L67
Bean名が`Job#getName()`の代わりに使用されていることがわかります。
これはおそらく次のように変更すべきです:
```java
	@Override
	public void afterSingletonsInstantiated() {
		this.applicationContext.getBeansOfType(Job.class).values().forEach(this::register);
	}
```
`register()`はチェック例外をスローするため、正確なロジックは少し変更する必要があるかもしれません。

---

私の回避策:
```java
@Bean
MapJobRegistry jobRegistry(ObjectProvider<Job> jobs) {
    return new MapJobRegistry() {

        // https://github.com/spring-projects/spring-batch/issues/5122 の回避策
        @Override
        public void afterSingletonsInstantiated() {
            for (Job job : jobs) {
                try {
                    register(job);
                } catch (DuplicateJobException e) {
                    throw new IllegalStateException(e);
                }
            }
        }
    };
}
```

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-05

この課題を報告していただきありがとうございます。実際、ジョブはBean名ではなく名前で登録されるべきです。これは私の見落としです。6.0.1で修正します。

