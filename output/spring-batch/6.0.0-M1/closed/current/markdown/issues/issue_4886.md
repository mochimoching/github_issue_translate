# Remove unnecessary generic from JobKeyGenerator interface

**Issue番号**: #4886

**状態**: closed | **作成者**: patrickwinti | **作成日**: 2025-06-13

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4886

## 内容

The `JobKeyGenerator<T>` interface currently uses a generic type parameter `<T>` to represent the source used to generate a job key. However, in practice, the implementations and usages of this interface rely on JobParameters as the source type.

Since the generic parameter is not providing meaningful flexibility and introduces unnecessary complexity (e.g., requiring casts or wildcard types in consumers), it would be cleaner to refactor the interface to:

```
public interface JobKeyGenerator {
    String generateKey(JobParameters source);
}
```


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-07-14

I agree, thank you for raising this!

This is a good candidate for a major release so I will plan it for v6.

### コメント 2 by fmbenhassine

**作成日**: 2025-07-14

Resolved with #4887.

