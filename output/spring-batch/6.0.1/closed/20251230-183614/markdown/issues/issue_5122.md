# `MapJobRegistry` registers discovered Jobs by their bean name instead of their job name

**Issue番号**: #5122

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-02

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5122

**関連リンク**:
- Commits:
  - [184ac31](https://github.com/spring-projects/spring-batch/commit/184ac31f704935c6d49865839713cd3126ce7cd3)

## 内容

The changes made with #4855 ignore the _names_ of the discovered Jobs:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/support/MapJobRegistry.java#L63-L67
We see that the bean names are used instead of `Job#getName()`.
This should probably be changed to something like this:
```java
	@Override
	public void afterSingletonsInstantiated() {
		this.applicationContext.getBeansOfType(Job.class).values().forEach(this::register);
	}
```
Since `register()` throws a checked exception, the exact logic may need to be changed a bit.

---

My workaround:
```java
@Bean
MapJobRegistry jobRegistry(ObjectProvider<Job> jobs) {
    return new MapJobRegistry() {

        // Workaround for https://github.com/spring-projects/spring-batch/issues/5122
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

Thank you for reporting this issue. In fact, jobs should be registered by their name and not their bean name. This is an oversight from my side, I will fix that in 6.0.1.

