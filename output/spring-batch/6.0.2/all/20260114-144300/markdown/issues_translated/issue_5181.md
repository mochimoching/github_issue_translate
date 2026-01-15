*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

# @SpringBatchTestがアクティブな状態でStepScopeTestUtilsを使用するとMetaDataInstanceFactoryのデフォルト値がStepContextの衝突を引き起こす

**Issue番号**: [#5181](https://github.com/spring-projects/spring-batch/issues/5181)

**状態**: open | **作成者**: KILL9-NO-MERCY | **作成日**: 2025-12-23

**ラベル**: in: test, status: waiting-for-reporter, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5181

## 内容

## バグの説明:
`@SpringBatchTest`で管理されるテスト環境で`StepScopeTestUtils`を使用する際、`StepSynchronizationManager`で論理的な衝突が発生します。

`StepExecution`はstepName、jobExecutionId、idに基づいて等価性を判定します。`MetaDataInstanceFactory`がこれらすべてのフィールドに対して静的なデフォルト値を提供するため、ファクトリーで作成された複数のインスタンスは`SynchronizationManagerSupport.contexts`マップで同一のキーとして扱われます。

これにより、`StepScopeTestUtils`がカスタム`JobParameters`を持つ新しいコンテキストを登録できなくなります。`computeIfAbsent`ロジックが`StepScopeTestExecutionListener`（`@SpringBatchTest`の一部）によって登録された既存のコンテキストを見つけてしまうためです。

## 再現手順:
テストクラスに`@SpringBatchTest`アノテーションを付与します。

テストメソッド内で、`MetaDataInstanceFactory.createStepExecution(jobParameters)`で作成した`StepExecution`を使用して`StepScopeTestUtils.doInStepScope()`を使用します。

スコープ内の`Tasklet`や`ItemStream`は、リスナーの初期コンテキスト（`JobParameters`がない）にバインドされているため、jobParametersを参照できません。

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
    @DisplayName("MetadataInstanceFactory ID collision causes JobParameter injection failure")
    void reproduceIdCollisionBug() throws Exception {
        // Given
        String expectedValue = "HelloBatch";
        JobParameters jobParameters = new JobParametersBuilder()
                .addString("testParam", expectedValue)
                .toJobParameters();

        // 6.x以降の（おそらく5.2.3以降も？）MetadataInstanceFactoryは固定ID 1234LでStepExecutionを作成する
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // これは失敗します。'actualValue'はnullになります。
        // TaskletはID衝突（1234L）により、StepScopeTestUtilsで渡されたコンテキストではなく、
        // リスナーのコンテキスト（JobParametersがない）を取得しました。
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
`StepScopeTestUtils.doInStepScope()`内で作成された`StepExecution`とそれに対応する`StepContext`は、`@SpringBatchTest`がアクティブな状態でも、`StepSynchronizationManager`を通じて正しく登録されアクセス可能であるべきです。

（注意: 最適な修正方法を決定するのは私には簡単ではないようです。`MetaDataInstanceFactory`のID生成戦略を変更するか、テスト環境で重複する登録を`StepSynchronizationManager`がどのように処理するかを調整する必要があるかもしれません。）

## 回避策:
現在の衝突を回避するため、テストクラス内で`getStepExecution()`メソッドを明示的に定義できます。一意の名前または別のID（例: -1L）を持つ`StepExecution`を返すことで、`StepScopeTestExecutionListener`がデフォルトのID（1234L）を占有することを防ぎ、`StepScopeTestUtils`が意図通りに動作するようになります:

```java
/**
 * 回避策: テストクラスでgetStepExecution()を定義してID衝突を回避。
 * デフォルト以外のIDまたは名前を提供することで、リスナーが登録したコンテキストが
 * StepScopeTestUtilsで作成されたものと衝突しないようにします。
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

この素晴らしいプロジェクトをメンテナンスしていただきありがとうございます！

## コメント

### コメント 1 by injae-kim

**作成日**: 2026-01-11

参考）修正PR: https://github.com/spring-projects/spring-batch/pull/5208 👍

### コメント 2 by fmbenhassine

**作成日**: 2026-01-13

この問題を再現しようとしていますが、できませんでした。共有していただいたテストはSpring Bootを使用していますが、まずSpring Batchのみを使用してこれが有効な問題であることを確認したいと思います。

9ae777572a0978572e25f04d4cb93c0ad02b9a0fの時点で、以下のクラス（共有されたものと同じですがSpring Bootなし）を`org.springframework.batch.test`パッケージに追加すると、言及されたテストはパスします:

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

        // 6.x以降の（おそらく5.2.3以降も？）MetadataInstanceFactoryは固定ID 1234LでStepExecutionを作成する
        StepExecution stepExecution = MetaDataInstanceFactory.createStepExecution(jobParameters);

        // When
        StepScopeTestUtils.doInStepScope(stepExecution, () ->
                Objects.requireNonNull(issueReproductionTasklet.execute(stepExecution.createStepContribution(), null))
        );

        // Then
        String actualValue = stepExecution.getExecutionContext().getString("result");

        // これは失敗します。'actualValue'はnullになります。
        // TaskletはID衝突（1234L）により、StepScopeTestUtilsで渡されたコンテキストではなく、
        // リスナーのコンテキスト（JobParametersがない）を取得しました。
        assertEquals(expectedValue, actualValue);
    }
}
```

確認していただけますか？
