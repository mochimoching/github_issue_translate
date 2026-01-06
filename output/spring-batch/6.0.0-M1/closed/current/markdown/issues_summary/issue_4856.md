*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

課題 [#4855](https://github.com/spring-projects/spring-batch/issues/4855) で`MapJobRegistry`が自動登録機能を持ったため、`JobRegistrySmartInitializingSingleton`クラスが冗長となり、非推奨化されました。

### 経緯

`JobRegistrySmartInitializingSingleton`は、課題 [#4519](https://github.com/spring-projects/spring-batch/issues/4519) と [#4489](https://github.com/spring-projects/spring-batch/issues/4489) への「アドホック」ソリューションとしてv5.1.1で導入されました。

## 原因

v5.1.1では、ジョブレジストリの自動登録機能を別のコンポーネントとして実装していましたが、v6.0で`MapJobRegistry`自体にその機能が組み込まれたため、このクラスは不要になりました。

## 対応方針

**コミット**: [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

`JobRegistrySmartInitializingSingleton`を非推奨化し、v6.2で削除予定としました。

### 移行

```java
// v5.1.1
@Bean
JobRegistrySmartInitializingSingleton registrar(JobRegistry registry) {
    return new JobRegistrySmartInitializingSingleton(registry);
}

// v6.0以降：不要！
@Bean
public JobRegistry jobRegistry() {
    return new MapJobRegistry();  // 自動登録機能が内蔵
}
```

### メリット

- 設定コードの削減
- 概念的なシンプル化（Registry1つで完結）
- 保守すべきクラスの削減
