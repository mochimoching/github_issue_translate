# MetaDataInstanceFactory.createStepExecution(JobParameters)がJobParametersをStepExecutionに伝播しない

**Issue番号**: #5115

**状態**: closed | **作成者**: benelog | **作成日**: 2025-11-27

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5115

**関連リンク**:
- Commits:
  - [1a5b8d0](https://github.com/spring-projects/spring-batch/commit/1a5b8d0321fd6efd02c589b0711260f93fe9315f)
  - [da16f6b](https://github.com/spring-projects/spring-batch/commit/da16f6b92ecc1b4d5ed0acb947df1dad923e590a)
  - [8264ab1](https://github.com/spring-projects/spring-batch/commit/8264ab11b9fa1905da648f454a050dd058b3fda0)

## 内容

## バグの説明
`MetaDataInstanceFactory.createStepExecution(JobParameters)`を介して作成された`StepExecution`インスタンスが、提供された`JobParameters`を参照しません。

これは以下のコミットによって導入された副作用のようです:

https://github.com/spring-projects/spring-batch/commit/90d895955d951156849ba6fa018676273fdbe2c4

## 環境
Spring Batch v6.0.0

## 再現手順
以下のテストケースでバグが再現されます:

```java
@Test
void testCreateStepExecutionJobParameters() {
    JobParameters parameters = new JobParametersBuilder()
        .addString("foo", "bar")
        .toJobParameters();

    StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(parameters);
    String paramValue = stepExecution.getJobExecution().getJobParameters().getString("foo");

    assertEquals("bar", paramValue);
}
```


## コメント

### コメント 1 by benelog

**作成日**: 2025-12-13

@fmbenhassine

この課題はSpring Batch v5.2.xでは発生しませんでしたが、v6.0.0へのアップグレード後に新たに現れました。

現在、以下の回避策で対処しています:

(Spring Batch v5.2.xを使用する場合)
```java
StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);
```

→

(Spring Batch v6.0.0へのアップグレード後)

```java
JobExecution jobExecution = MetaDataInstanceFactory.createJobExecution("testJob", 0L, 0L, jobParameters);
StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobExecution, "testStep", 0L);
```

以下のPRがSpring Batch v6.0.1に含まれれば、バージョンをアップグレードするユーザーが経験する試行錯誤を減らし、v6.0.xが安定していると感じてもらうことに貢献するでしょう。

https://github.com/spring-projects/spring-batch/pull/5116

