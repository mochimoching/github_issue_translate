# フォールトトレラントステップ: `retry(Class)`は例外の原因をたどるが、`skip(Class)`はたどらない

**Issue番号**: #5127

**状態**: closed | **作成者**: kzander91 | **作成日**: 2025-12-03

**ラベル**: type: bug, in: core, has: minimal-example, related-to: fault-tolerance

**URL**: https://github.com/spring-projects/spring-batch/issues/5127

**関連リンク**:
- Commits:
  - [5edb62f](https://github.com/spring-projects/spring-batch/commit/5edb62f0c818f4505804b46b45f5843556e6e826)
  - [2c57f8d](https://github.com/spring-projects/spring-batch/commit/2c57f8d13e6f8fda7b89cfaa9b9668209bc6ee54)
  - [8cade4d](https://github.com/spring-projects/spring-batch/commit/8cade4d656f79646ed99ba68cd6e8b77ee0fe862)

## 内容

**バグの説明**
`skip(Class)`と`retry(Class)`の動作に一貫性がありません。`skip(SkippableException.class)`は`throw new RuntimeException(new SkippableException())`をスキップ_しません_が、`retry(SkippableException.class)`は原因を_検査し_、同じ式を再試行します。

期待される動作は、`RetryPolicy`と`SkipPolicy`の両方で例外マッチングが一貫して動作することです(理想的には`RetryPolicy`に合わせて、原因がたどられるようにします)。

根本的な理由は、常に原因をたどるFrameworkの新しいリトライサポートへの切り替えです(実は、私自身がリクエストした機能です 🙃): spring-projects/spring-framework#35583

**環境**
Spring Batch 6.0.0

**再現手順**
1. 同じ例外タイプをスキップおよび再試行するフォールトトレラントステップを設定します。
2. スキップ可能な例外を原因とする別の例外をスローします。

**期待される動作**
例外が再試行され、その後(再試行が枯渇した後)スキップされます。

**最小限の再現可能な例**
再現プログラム: [demo14.zip](https://github.com/user-attachments/files/23907601/demo14.zip)
`./mvnw test`で実行

プロジェクトには次のようなステップがあります:
```java
@Bean
Step step() {
    return new StepBuilder("step", jobRepository)
            .chunk(5)
            .transactionManager(transactionManager)
            .faultTolerant()
            .retry(SkippableException.class)
            .retryLimit(1)
            .skip(SkippableException.class)
            .skipLimit(1)
            .reader(new ListItemReader<>(List.of("item")))
            .writer(_ -> {
                throw new RuntimeException(new SkippableException());
            })
            .build();
}

static class SkippableException extends RuntimeException {

}
```

テストはジョブを起動し、正常完了とスキップ数が1であることを期待します。

---
Spring Batch 5では、原因をたどるように設定された`BinaryExceptionClassifier`(spring-retryから)を持つ`LimitCheckingItemSkipPolicy`を使用していました。しかし、これは現在非推奨であり、同等の代替品は存在しません(独自の`SkipPolicy`を完全に再実装する以外)。

---

これをデバッグ中に、おそらく関連する別の課題を見つけました:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/skip/LimitCheckingExceptionHierarchySkipPolicy.java#L50-L54
`skipCount < 0`の場合(再試行可能な例外が発生した直後に`SkipPolicy`が照会される場合)、ロジックが反転していることに注意してください。その場合、`!isSkippable(t)`のため、スキップ不可能な例外がスキップ可能として分類されます。

## コメント

### コメント 1 by kzander91

**作成日**: 2025-12-03

さらにデバッグした結果、より混乱してきました。おそらくここのロジックも反転していますか?
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L688-L702
なぜ`this.skipPolicy.shouldSkip()`が否定されているのですか? `SkipPolicy`がスキップを_示した_ときにログに記録されるこのエラーも、逆が意図されていたことを示しています:
https://github.com/spring-projects/spring-batch/blob/fa73e01f40d6cd7e8274b473a17e8c0c387fae84/spring-batch-core/src/main/java/org/springframework/batch/core/step/item/ChunkOrientedStep.java#L700


### コメント 2 by fmbenhassine

**作成日**: 2025-12-16

この課題を報告し、例を提供していただきありがとうございます! 確かに、`LimitCheckingExceptionHierarchySkipPolicy`のその否定と`ChunkOrientedStep`での反転は混乱を招くものであり、修正すべきです。

明日予定されている6.0.1リリースでこれを修正しようと思います(今日は非常に忙しいので難しいかもしれません)。そうでなければ、誰かがタイムリーに修正を貢献してくれない限り、6.0.2で予定します。以下は、`ChunkOrientedStepTests`に追加する最新のmainでの失敗するテストです:


```java
@Test
void testSkippableExceptionsTraversal() throws Exception {
	// given
	class SkippableException extends RuntimeException {

	}
	ItemReader<String> reader = new ListItemReader<>(List.of("item1"));
	ItemWriter<String> writer = chunk -> {
		throw new RuntimeException(new SkippableException());
	};

	JobRepository jobRepository = new ResourcelessJobRepository();
	ChunkOrientedStep<String, String> step = new StepBuilder("step", jobRepository).<String, String>chunk(1)
		.reader(reader)
		.writer(writer)
		.faultTolerant()
		.retry(SkippableException.class)
		.retryLimit(1)
		.skip(SkippableException.class)
		.skipLimit(1)
		.build();

	JobInstance jobInstance = new JobInstance(1L, "job");
	JobExecution jobExecution = new JobExecution(1L, jobInstance, new JobParameters());
	StepExecution stepExecution = new StepExecution(1L, "step", jobExecution);

	// when - execute step
	step.execute(stepExecution);

	// then - should skip the exception thrown by the writer
	ExitStatus stepExecutionExitStatus = stepExecution.getExitStatus();
	assertEquals(ExitStatus.COMPLETED.getExitCode(), stepExecutionExitStatus.getExitCode());
	assertEquals(1, stepExecution.getSkipCount());
}
```

---

> 根本的な理由は、常に原因をたどるFrameworkの新しいリトライサポートへの切り替えです(実は、私自身がリクエストした機能です 🙃) : https://github.com/spring-projects/spring-framework/issues/35583

はい、見ました、おめでとうございます! ポートフォリオ全体へのすべての貢献で素晴らしい仕事をされていて、本当に感謝しています 🙏

> 根本的な理由は、Frameworkの新しいリトライサポートへの切り替えです

実は、私自身が貢献した機能です 🙃: https://github.com/spring-projects/spring-framework/pull/34716

### コメント 3 by therepanic

**作成日**: 2025-12-16

こんにちは、@fmbenhassine! このプロジェクトでのすべての作業に感謝します!

あなたはこれに取り組む時間がないと書いたので、今日PRを作ることにしました。もしかしたら、それをレビューして、必要に応じて磨きをかけて、新しい6.0.1リリースで直接リリースできるかもしれません。いずれにせよ、6.0.2で修正する必要があると思います。いくつかのコメントも残しました。PTAL https://github.com/spring-projects/spring-batch/pull/5171。


### コメント 4 by fmbenhassine

**作成日**: 2025-12-16

> あなたはこれに取り組む時間がないと書いたので、今日PRを作ることにしました。

とても親切です! ご協力いただき、本当にありがとうございます 🙏

あなたのPRを確認します。

