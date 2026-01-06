# @SpringBatchTestの使用時にMetaDataInstanceFactoryのデフォルト値がStepScopeTestUtilsでStepContextの競合を引き起こす

**課題番号**: #5181

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5181

## 内容

## バグの説明: 
`@SpringBatchTest`で管理されるテスト環境において、`StepScopeTestUtils`を使用する際に`StepSynchronizationManager`で論理的な競合が発生します。

`StepExecution`は`stepName`、`jobExecutionId`、`id`に基づいて等価性を判断します。`MetaDataInstanceFactory`がこれらすべてのフィールドに静的なデフォルト値を提供するため、ファクトリーによって作成された複数のインスタンスが`SynchronizationManagerSupport.contexts`マップ内で同一のキーとして扱われてしまいます。

この結果、`computeIfAbsent`ロジックが`StepScopeTestExecutionListener`（`@SpringBatchTest`の一部）によって登録された既存のコンテキストを見つけるため、`StepScopeTestUtils`がカスタム`JobParameters`を持つ新しいコンテキストを登録できなくなります。

## 再現手順:
テストクラスに`@SpringBatchTest`アノテーションを付与します。

テストメソッド内で、`MetaDataInstanceFactory.createStepExecution(jobParameters)`を使用して作成した`StepExecution`を用いて`StepScopeTestUtils.doInStepScope()`を呼び出します。

スコープ内の`Tasklet`または`ItemStream`は、リスナーの初期コンテキストに紐付けられているため、`jobParameters`を参照できずに失敗します。

## 失敗する例: 
ジョブの設定例
```java
@Slf4j
@Configuration
public class IssueReproductionJobConfiguration {
    @Bean
    public Job issueReproductionJob(JobRepository jobRepository, Step issueReproductionStep) {
        return new JobBuilder(jobRepository)
                .incrementer(new RunIdIncrementer())
                .start(issueReproductionStep)
                .build();
    }

    @Bean
    public Step issueReproductionStep(
            JobRepository jobRepository,
            Tasklet issueReproductionTasklet
    ) {
        return new StepBuilder(jobRepository)
                .tasklet(issueReproductionTasklet)
                .build();
    }

    @Bean
    @StepScope
    public Tasklet issueReproductionTasklet(@Value("#{jobParameters['testParam']}") String testParam) {
        return (contribution, chunkContext) -> {
            contribution.getStepExecution().getExecutionContext().putString("result", testParam);
            return RepeatStatus.FINISHED;
        };
    }
}
```

テストクラス
```java
@SpringBatchTest
@SpringBootTest
@ActiveProfiles("test")
@Import(TestBatchConfiguration.class)
public class IssueReproductionTest {
    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactoryのID競合がJobParameterの注入失敗を引き起こす")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // 6.x / 5.2.3以降のMetadataInstanceFactoryは固定ID 1234Lで StepExecutionを作成
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // これは失敗します。'actualValue'がnullになるためです。
        // Taskletは、ID競合（1234L）により、StepScopeTestUtilsで渡されたものではなく、
        // リスナーのコンテキスト（JobParametersを持たない）を取得してしまいます。
        assertEquals(expectedValue, actualValue);
    }
}

@TestConfiguration
public class TestBatchConfiguration extends DefaultBatchConfiguration {
}
```

application-test.yml
```yaml
spring:
  batch:
    job:
      enabled: false
```
テスト結果:
```bash
Value for key=[result] is not of type: [class java.lang.String], it is [null]
java.lang.ClassCastException: Value for key=[result] is not of type: [class java.lang.String], it is [null]
```

## 期待される動作:
`@SpringBatchTest`が有効な場合でも、`StepScopeTestUtils.doInStepScope()`内で作成された`StepExecution`とそれに対応する`StepContext`が正しく登録され、`StepSynchronizationManager`を通じてアクセス可能であるべきです。

（注：最適な修正方法の決定は簡単ではないようです。`MetaDataInstanceFactory`のID生成戦略を変更するか、テスト環境での重複登録を処理する`StepSynchronizationManager`の動作を調整する必要がある可能性があります。）

## 回避策: 
現在の競合を回避するには、テストクラス内で`getStepExecution()`メソッドを明示的に定義できます。一意の名前または異なるID（例：-1L）を持つ`StepExecution`を返すことで、`StepScopeTestExecutionListener`がデフォルトID（1234L）を占有することを防ぎ、`StepScopeTestUtils`が意図通りに動作するようにできます：

```java
/**
 * 回避策：ID競合を避けるため、テストクラスでgetStepExecution()を定義します。
 * デフォルト以外のIDまたは名前を提供することで、リスナーによって登録された
 * コンテキストがStepScopeTestUtilsで作成されたものと競合しないことを保証します。
 */
public StepExecution getStepExecution() {
    return MetaDataInstanceFactory.createStepExecution("uniqueStep", -1L);
}
```

テスト結果:
```bash
> Task :test
BUILD SUCCESSFUL in 3s
```

お時間を割いていただき、またこの素晴らしいプロジェクトをメンテナンスしていただきありがとうございます！
