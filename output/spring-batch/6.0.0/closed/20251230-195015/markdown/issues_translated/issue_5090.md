*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# Batch 6 RC2でJobLauncherTestUtils.getJobLauncher()がNPEをスロー

**Issue番号**: #5090

**状態**: closed | **作成者**: lucas-gautier | **作成日**: 2025-11-17

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5090

**関連リンク**:
- Commits:
  - [5b80510](https://github.com/spring-projects/spring-batch/commit/5b8051001475d4529239390820a419ff4aceb792)

## 内容

**バグの説明**

非推奨になったばかりの`JobLauncherTestUtils`が、Batch 6 RC2のユニットテストで`getJobLauncher()`においてNPEをスローします。
`JobLauncherTestUtils`を使用するテストは失敗する一方で、新しい`JobOperatorTestUtils`を使用するテストはRC2で期待通りに動作します。

**環境**

- Spring Boot 4.0.0 RC2
- Spring Batch 6.0.0 RC2
- Mandrel/Temurin JDK 25.0.1+8

**再現手順**

1. "batch-rc2"の再現例を開き、`./gradlew test`でテストを実行し、失敗するテストを確認
   - スタックトレースは`build/reports/tests/test/index.html`で確認できます
2. テストをスキップしてプロジェクトをビルド`./gradlew build -x test`し、exampleセクションで指定されたジョブを実行
3. オプションで、"batch5"プロジェクトを参照し、Boot 3.5.7とBatch 5.2.4で`JobLauncherTestUtils`を使用した成功するテストを確認

**期待される動作**

非推奨の`JobLauncherTestUtils`を使用して書かれたテストは、Batch 7で削除されるまで引き続き正しく動作すべきです。

**最小限の再現可能な例**

"batch6-rc2"プロジェクトには、`JobLauncherTestUtils`を使用した失敗するテストと、新しい`JobOperatorTestUtils`を使用した成功するテストが含まれています。
"batch5"プロジェクトには、`JobLauncherTestUtils`を使用した成功するテストが含まれています。

両方のプロジェクトには、jar経由で実行できる同じ2つのジョブがあります(batch6-rc2プロジェクトではテストをスキップ):

```bash
java -jar build/libs/*jar --spring.batch.job.name=HelloJob
java -jar build/libs/*jar --spring.batch.job.name=GoodbyeJob
```

[batch5.tgz](https://github.com/user-attachments/files/23571876/batch5.tgz)
[batch6-rc2.tgz](https://github.com/user-attachments/files/23571878/batch6-rc2.tgz)

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-17

これは有効な問題です。報告していただきありがとうございます! 次回のGAで修正を計画します。

### コメント 2 by lucas-gautier

**作成日**: 2025-11-17

ありがとうございます、Ben!


