*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# @SpringBatchTestがアクティブな場合、MetaDataInstanceFactoryのデフォルト値がStepScopeTestUtilsでStepContextの衝突を引き起こす

**課題番号**: [#5181](https://github.com/spring-projects/spring-batch/issues/5181)

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: in: test, status: waiting-for-reporter, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5181

## 内容

## バグの説明: 
`@SpringBatchTest`で管理されるテスト環境で`StepScopeTestUtils`を使用する際、`StepSynchronizationManager`で論理的な衝突が発生しています。

`StepExecution`は`stepName`、`jobExecutionId`、`id`に基づいて等価性を判定します。`MetaDataInstanceFactory`はこれらすべてのフィールドに静的なデフォルト値を提供するため、ファクトリで作成された複数のインスタンスは`SynchronizationManagerSupport.contexts`マップで同一のキーとして扱われます。

これにより、`StepScopeTestUtils`はカスタム`JobParameters`を持つ新しいコンテキストを登録できません。`computeIfAbsent`ロジックが`StepScopeTestExecutionListener`（`@SpringBatchTest`の一部）によって登録された既存のコンテキストを見つけてしまうためです。

## 再現手順:
テストクラスに`@SpringBatchTest`アノテーションを付与します。

テストメソッド内で、`MetaDataInstanceFactory.createStepExecution(jobParameters)`で作成した`StepExecution`を使用して`StepScopeTestUtils.doInStepScope()`を使用します。

スコープ内の`Tasklet`や`ItemStream`は、リスナーの初期コンテキスト（`JobParameters`を持たない）にバインドされているため、`jobParameters`を参照できません。

## 失敗する例: 
ジョブの例
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
    @DisplayName("MetadataInstanceFactoryのID衝突によりJobParameterのインジェクションが失敗する")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // 6.x（おそらく5.2.3以降も？）のMetadataInstanceFactoryは固定ID 1234LでStepExecutionを作成する
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // これは失敗します。'actualValue'はnullになります。
        // ID衝突（1234L）により、StepScopeTestUtilsで渡されたコンテキストではなく、
        // リスナーのコンテキスト（JobParametersを持たない）をTaskletが取得したためです。
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
`StepScopeTestUtils.doInStepScope()`内で作成された`StepExecution`とそれに対応する`StepContext`は、`@SpringBatchTest`がアクティブな場合でも、`StepSynchronizationManager`を通じて正しく登録されアクセス可能であるべきです。

（注: 最適な修正方法を決定するのは簡単ではないように思えます。`MetaDataInstanceFactory`のID生成戦略を変更するか、テスト環境で重複する登録を`StepSynchronizationManager`が処理する方法を調整する必要があるかもしれません。）
回避策: ユーザーはequals/hashCode衝突を回避するために、手動で一意の名前またはIDを提供する必要があります:

## 回避策: 
現在の衝突を回避するには、テストクラス内で`getStepExecution()`メソッドを明示的に定義できます。一意の名前または異なるID（例: -1L）を持つ`StepExecution`を返すことで、`StepScopeTestExecutionListener`がデフォルトのID（1234L）を占有するのを防ぎ、`StepScopeTestUtils`が意図したとおりに動作するようにできます:

```java
/**
 * 回避策: テストクラスでgetStepExecution()を定義してID衝突を回避する。
 * デフォルトではないIDまたは名前を提供することで、リスナーが登録した
 * コンテキストがStepScopeTestUtilsで作成されたものと競合しないようにする。
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

お時間をいただき、この素晴らしいプロジェクトをメンテナンスしていただきありがとうございます！

## コメント

### コメント 1 by injae-kim

**作成日**: 2026-01-11

参考情報）修正PR: https://github.com/spring-projects/spring-batch/pull/5208 👍

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

この課題を再現しようとしていますが、再現できていません。共有いただいたテストはSpring Bootを使用していますが、まずSpring Batchのみを使用してこれが有効な課題であることを確認したいと思います。

9ae777572a0978572e25f04d4cb93c0ad02b9a0fの時点で、以下のクラス（共有いただいたものと同じですが、Spring Bootなし）を`org.springframework.batch.test`パッケージに追加すると、言及されたテストは成功します:

```java
package org.springframework.batch.test;

import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.core.job.Job;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.job.parameters.RunIdIncrementer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.Step;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.infrastructure.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableBatchProcessing
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

```java
package org.springframework.batch.test;

import java.io.IOException;
import java.util.Objects;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.springframework.batch.core.job.parameters.JobParameters;
import org.springframework.batch.core.job.parameters.JobParametersBuilder;
import org.springframework.batch.core.step.StepExecution;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;

@ContextConfiguration(classes = IssueReproductionJobConfiguration.class)
@ExtendWith(SpringExtension.class)
public class IssueReproductionTest {

    @Autowired
    private Tasklet issueReproductionTasklet;

    public StepExecution getStepExecution() throws IOException {
        return MetaDataInstanceFactory.createStepExecution("dummy", -1L);
    }

    @Test
    @DisplayName("MetadataInstanceFactory ID collision causes JobParameter injection failure")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // MetadataInstanceFactory in 6.x / maybe after 5.2.3?? creates StepExecution with fixed ID 1234L
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // This will FAIL because 'actualValue' will be null.
        // The Tasklet retrieved the listener's context (which has no JobParameters)
        // instead of the one passed via StepScopeTestUtils due to ID collision (1234L).
        assertEquals(expectedValue, actualValue);
    }
}
```

確認していただけますか？
