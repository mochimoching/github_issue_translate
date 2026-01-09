*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# フォールトトレラントステップにおける再試行可能/スキップ可能な例外の扱いに一貫性がない

**課題番号**: #5127

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-11-28

**ラベル**: type: bug, in: core, has: minimal-example

**URL**: https://github.com/spring-projects/spring-batch/issues/5127

**関連リンク**:
- Commits:
  - [b95be1a](https://github.com/spring-projects/spring-batch/commit/b95be1ad1f5b67b6ae2b8b10c0d9e766f9d56f8b)

## 内容

**バグの説明**
これは[@daninelAliが報告した課題](https://github.com/spring-projects/spring-batch/discussions/4920#discussioncomment-11406031)のフォローアップです。

バージョン6.0.0では、再試行ポリシーとスキップポリシーがデフォルトで特定の例外のサブクラスをカバーするようになりましたが、対象外の例外の処理方法には一貫性がありません：

* 読み込み中にスキップ不可能な例外が発生すると、アイテムはスキップされません
* 処理中にスキップ不可能な例外が発生すると、アイテムはスキップされます

同様に：

* 読み込み中に再試行不可能な例外が発生すると、操作は再試行されます
* 処理中に再試行不可能な例外が発生すると、操作は再試行されません

この動作には一貫性がありません。以下のテストケースでこの問題を再現できます：

```java
@Test
public void testSkipPolicyConsistency() {
    var items = List.of("1", "2", "3", "4", "5", "6");
    var itemReader = new ListItemReader<>(items);
    var itemWriter = new ListItemWriter<>();
    var tasklet = new ChunkOrientedTasklet<String, String>(itemReader, new ItemProcessor<>() {
        int count = 0;

        @Override
        public String process(String item) throws Exception {
            count++;
            if (count == 3) {
                // この例外はスキップ不可能な例外としてマークされていないため、
                // アイテムはスキップされてしまいます
                throw new UncheckedIOException(new IOException("Expected"));
            }
            return item;
        }
    }, itemWriter, new RepeatTemplate());

    var faultTolerantStepBuilder = new FaultTolerantStepBuilder<String, String>(new StepBuilder("step"));
    var stepExecution = MetaDataInstanceFactory.createStepExecution();
    var chunkContext = new ChunkContext(new StepContext(stepExecution));
    faultTolerantStepBuilder.skipLimit(Integer.MAX_VALUE);
    faultTolerantStepBuilder.skip(IllegalStateException.class); // IOExceptionではない
    faultTolerantStepBuilder.listener((SkipListener<String, String>) (item, t) -> {
        System.out.println("item = " + item);
        System.out.println("t = " + t.getMessage());
    });
    var chunkProcessor = faultTolerantStepBuilder.build();
    tasklet.setChunkProcessor(chunkProcessor);

    // Arrange
    tasklet.open(chunkContext.getStepContext().getStepExecution().getExecutionContext());
    Contribution contribution = new Contribution(stepExecution);
    tasklet.execute(contribution, chunkContext); // ここで失敗するべき、しかしアイテム3がスキップされてしまう
    tasklet.close();

    // Assert
    Assertions.assertThat(itemWriter.getWrittenItems()).hasSize(5);
}

@Test
public void testRetryPolicyConsistency() throws Exception {
    var items = List.of("1", "2", "3", "4", "5", "6");
    var itemReader = new ListItemReader<>(items) {
        int count = 0;

        @Override
        public String read() {
            count++;
            if (count == 3) {
                // この例外は再試行可能な例外としてマークされていないため、
                // 操作は再試行されないべき、しかし再試行されてしまいます
                throw new UncheckedIOException(new IOException("Expected"));
            }
            return super.read();
        }
    };
    var itemWriter = new ListItemWriter<>();
    var tasklet = new ChunkOrientedTasklet<>(itemReader, null, itemWriter, new RepeatTemplate());

    var faultTolerantStepBuilder = new FaultTolerantStepBuilder<String, String>(new StepBuilder("step"));
    var stepExecution = MetaDataInstanceFactory.createStepExecution();
    var chunkContext = new ChunkContext(new StepContext(stepExecution));
    faultTolerantStepBuilder.retryLimit(10);
    faultTolerantStepBuilder.retry(IllegalStateException.class); // IOExceptionではない
    faultTolerantStepBuilder.listener(new RetryListener() {
        @Override
        public void onRetry(RetryContext context) {
            System.out.println("Retry: " + context.getLastThrowable().getMessage());
            System.out.println("Retry count = " + context.getRetryCount());
        }
    });
    var chunkProcessor = faultTolerantStepBuilder.build();
    tasklet.setChunkProcessor(chunkProcessor);

    // Arrange
    tasklet.open(chunkContext.getStepContext().getStepExecution().getExecutionContext());
    Contribution contribution = new Contribution(stepExecution);
    try {
        tasklet.execute(contribution, chunkContext); // ここで失敗するべき、しかし再試行されてしまう
    }
    catch (Exception e) {
        // 期待される例外
    }
    finally {
        tasklet.close();
    }

    // Assert
    Assertions.assertThat(itemWriter.getWrittenItems()).isEmpty();
}
```

**期待される動作**
対象外の例外が発生した場合の処理は、読み込み/書き込み/処理の各フェーズで一貫している必要があります。

**環境**
- Spring Batch 6.0.0

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-04

修正は以下のコミットにあります：https://github.com/spring-projects/spring-batch/commit/b95be1ad1f5b67b6ae2b8b10c0d9e766f9d56f8b

@cppwfs さん、お時間のある時に確認していただけますか？

### コメント 2 by cppwfs

**作成日**: 2025-12-04

ありがとうございます@fmbenhassine

