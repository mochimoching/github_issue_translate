*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

課題 [#4910](https://github.com/spring-projects/spring-batch/issues/4910) に関連して、`JobParametersBuilder`の`getNextJobParameters(Job job)`メソッドを`JobOperator`に移動し、`JobExplorer`への依存を削除しました。

### v5.2の問題

```java
public class JobParametersBuilder {
    private JobExplorer jobExplorer;  // 依存関係
    
    // このメソッドのためだけにJobExplorerが必要だった
    public JobParameters getNextJobParameters(Job job) {
        JobInstance lastInstance = jobExplorer.getLastJobInstance(job.getName());
        // ...
    }
}
```

## 原因

`JobParametersBuilder`の`getNextJobParameters(Job)`メソッドは、次のジョブインスタンスのパラメータを計算するために`JobExplorer`を使用していました。しかし、課題 [#4910](https://github.com/spring-projects/spring-batch/issues/4910) で説明されているように、連続内の次のインスタンスのパラメータ計算は**前のインスタンスのパラメータのみ**に基づくべきです。

この責任は`JobParametersBuilder`ではなく、`JobOperator#startNextInstance(Job)`メソッドに属します。

## 対応方針

**コミット**: [9209fb4](https://github.com/spring-projects/spring-batch/commit/9209fb476d7c18d65716c92e5fa1431263b8f143)

`getNextJobParameters(Job)`のロジックを`JobOperator`に移動しました。

### v6.0の改善

```java
// JobParametersBuilderはシンプルに
public class JobParametersBuilder {
    // JobExplorer依存なし
    
    public JobParameters toJobParameters() {
        // パラメータを構築するだけ
    }
}

// JobOperatorが責任を持つ
public interface JobOperator {
    Long startNextInstance(String jobName);
    // 内部で前回のパラメータから次のパラメータを計算
}
```

### メリット

- `JobParametersBuilder`の責任が明確（パラメータ構築のみ）
- `JobExplorer`への不必要な依存を削除
- 次インスタンス起動のロジックが`JobOperator`に集約
- より適切な責任分離
