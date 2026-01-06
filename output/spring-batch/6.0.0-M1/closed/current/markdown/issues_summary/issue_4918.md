*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

リモートパーティショニング機能の`StepExecutionRequestHandler`で、非推奨となった`JobExplorer`の使用を`JobRepository`に置き換えました。

**StepExecutionRequestHandlerとは**: リモートパーティショニングにおいて、ワーカーノードでステップ実行リクエストを処理するハンドラーです。

## 原因

課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824) で`JobExplorer`が非推奨化されたため、すべてのコンポーネントを`JobRepository`に移行する必要がありました。

## 対応方針

**コミット**: [ce89612](https://github.com/spring-projects/spring-batch/commit/ce896128424e7673d1a9f2b884bb5866d296f8c4)

`StepExecutionRequestHandler`の`JobExplorer`依存を`JobRepository`に置き換えました。

### API変更

```java
// v5.2
public class StepExecutionRequestHandler {
    private JobExplorer jobExplorer;  // 非推奨
}

// v6.0
public class StepExecutionRequestHandler {
    private JobRepository jobRepository;  // 統合API
}
```

### メリット

- 統合されたリポジトリAPI
- Bean定義の簡素化
- 一貫性のあるAPI使用
