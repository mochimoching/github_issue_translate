*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

システムコマンドを実行するタスクレット`SystemCommandTasklet`で、非推奨となった`JobExplorer`の使用を`JobRepository`に置き換えました。

**SystemCommandTaskletとは**: OSのシェルコマンド（例：スクリプト実行、外部プログラム呼び出し）をステップ内で実行するためのタスクレットです。

### v5.2の実装

```java
public class SystemCommandTasklet {
    private JobExplorer jobExplorer;  // 非推奨API
    
    // 実行状態の確認等に使用
}
```

## 原因

課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824) で`JobExplorer`が非推奨化されたため、`SystemCommandTasklet`も`JobRepository`に移行する必要がありました。

## 対応方針

**コミット**: [a8e138c](https://github.com/spring-projects/spring-batch/commit/a8e138cbf488596f48e9c8f49522fa7235a32943)

`SystemCommandTasklet`の内部実装を`JobRepository`を使用するように変更しました。

### v6.0の改善

```java
public class SystemCommandTasklet {
    private JobRepository jobRepository;  // 統一API
}
```

### 使用例

```java
@Bean
public Step systemCommandStep(JobRepository jobRepository) {
    SystemCommandTasklet tasklet = new SystemCommandTasklet();
    tasklet.setCommand("sh /path/to/script.sh");
    tasklet.setTimeout(5000);
    
    return new StepBuilder("systemCommandStep", jobRepository)
        .tasklet(tasklet)
        .build();
}
```

### メリット

- 統合されたリポジトリAPI
- Bean定義の簡素化（JobExplorerが不要）
- APIの一貫性向上
