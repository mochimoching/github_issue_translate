*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

課題 [#4847](https://github.com/spring-projects/spring-batch/issues/4847) のAPI簡素化の一環として、`JobRegistry`から`JobFactory`の使用を削除し、ジョブを直接登録できるように改善しました。

### v5.2の問題

```java
// 複雑なファクトリーパターンを経由
JobRegistry registry = ...;
JobFactory factory = new ReferenceJobFactory(job);
registry.register(factory);  // ファクトリーを登録
```

## 原因

`JobFactory`は公開APIでしたが、「ユーザー向け」ではなく内部実装の詳細でした。ユーザーがジョブを登録するのに、わざわざファクトリーを介する必要性は低く、不必要な複雑性を生んでいました。

## 対応方針

**コミット**: [ce5ef2f](https://github.com/spring-projects/spring-batch/commit/ce5ef2f8b69ecd3bfe81ce218284b2710706a101), [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

`JobRegistry`のAPIをシンプル化し、ジョブを直接登録できるようにしました。

### API変更

```java
// v5.2（変更前）
interface JobRegistry {
    void register(JobFactory jobFactory);  // ❌ ファクトリー経由
}

// v6.0（変更後）
interface JobRegistry {
    void register(Job job);  // ✅ 直接登録
}
```

### 使用例の比較

```java
// v5.2
JobFactory factory = new ReferenceJobFactory(myJob);
jobRegistry.register(factory);

// v6.0
jobRegistry.register(myJob);  // シンプル！
```

### メリット

- APIがシンプルで直感的
- `JobFactory`の理解が不要
- コード量の削減
