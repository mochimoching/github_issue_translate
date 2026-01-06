*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

課題 [#4847](https://github.com/spring-projects/spring-batch/issues/4847) のAPI簡素化の一環として、テストユーティリティ`StepRunner`を非推奨化しました。

**StepRunnerとは**: ステップを「偽の」単一ステップジョブ内で実行するテストユーティリティです。

### v5.2の問題

```java
public class StepRunner {
    // 単一メソッドのみで付加価値が低い
    public JobExecution launch(Step step, JobParameters params) {
        // ステップを囲む単一ステップジョブを作成して実行
    }
}
```

## 原因

`StepRunner`には以下の問題がありました：
1. **付加価値が低い**: 単一のメソッドしかなく、ユーザーが直接書いても同程度の労力
2. **重複コード**: `JobLauncherTestUtils`と類似した`makeUniqueJobParameters()`メソッドを持つ
3. **使用頻度が低い**: 通常のユーザーはほとんど使用しない

## 対応方針

**コミット**: [0aae4e9](https://github.com/spring-projects/spring-batch/commit/0aae4e91089df70f6f9e9750c95a3c9c30a7ff73)

`StepRunner`を非推奨化し、v6.2での削除を予定しました。

### 代替方法

```java
// v5.2（StepRunnerを使用）
StepRunner stepRunner = new StepRunner();
JobExecution execution = stepRunner.launch(myStep, params);

// v6.0推奨（JobOperatorTestUtilsを使用）
JobOperatorTestUtils testUtils = new JobOperatorTestUtils();
testUtils.setJob(job);  // ステップを含むジョブを設定
JobExecution execution = testUtils.startStep("myStep", params);
```

### メリット

- テストAPIの簡素化
- 重複コードの削減
- より統一されたテストユーティリティ（`JobOperatorTestUtils`に集約）
