# テスト用の`ResourcelessJobRepository`実装の強化

**Issue番号**: #5139

**状態**: closed | **作成者**: benelog | **作成日**: 2025-12-07

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5139

## 内容

## 背景

以下の課題に基づいて、`ResourcelessJobRepository`の設計意図を理解しています:

* [https://github.com/spring-projects/spring-batch/issues/4679](https://github.com/spring-projects/spring-batch/issues/4679)

しかし、元の設計目標を侵害することなく、このクラスをテストではるかに有用にするいくつかの的を絞った機能強化があると考えています。

単一のアプリケーションコンテキストでは、`ResourcelessJobRepository`は同じジョブを複数回実行できません。この制限は、ユーザーがそれを理解している限り許容されますが、テストでは制約になる可能性があります。

たとえば、以下のテストは`JobOperatorTestUtils`を使用して異なる`JobParameters`で同じジョブを実行しますが、`ResourcelessJobRepository`に依存できません:

```java
@SpringBootTest("spring.batch.job.enabled=false")
@SpringBatchTest
class HelloParamJobTest {

  @Autowired
  JobOperatorTestUtils testUtils;

  @BeforeEach
  void prepareTestUtils(@Autowired @Qualifier("helloParamJob") Job helloParamJob) {
    testUtils.setJob(helloParamJob);
  }

  @Test
  void startJob() throws Exception {
    JobParameters params = testUtils.getUniqueJobParametersBuilder()
        .addLocalDate("helloDate", LocalDate.of(2025, 7, 28))
        .toJobParameters();
    JobExecution execution = testUtils.startJob(params);
    assertThat(execution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);
  }

  @Test
  void startJobWithInvalidJobParameters() {
    JobParameters params = testUtils.getUniqueJobParametersBuilder()
        .addLocalDate("goodDate", LocalDate.of(2025, 7, 28))
        .toJobParameters();
    assertThatExceptionOfType(InvalidJobParametersException.class)
        .isThrownBy(() -> testUtils.startJob(params))
        .withMessageContaining("do not contain required keys: [helloDate]");
  }
}
```

## 既知の解決策

この制限に対するいくつかの既存の回避策を知っています:

* `ResourcelessJobRepository`をプロトタイプスコープのBeanとして登録する。
* インメモリデータベースとJDBCベースの`JobRepository`を一緒に使用する。
* 各テスト前に`ApplicationContext`を更新するために`@DirtiesContext`(または類似)を使用する。

しかし、これらすべてにはトレードオフがあります:

* オブジェクトの配線と依存関係における追加の複雑さ。
* 追加の設定オーバーヘッド。
* 頻繁なコンテキストの更新によるテスト実行の遅延。

特に、このコメントで述べられているように:

* [https://github.com/spring-projects/spring-batch/issues/5118#issuecomment-3604092261](https://github.com/spring-projects/spring-batch/issues/5118#issuecomment-3604092261)

`ResourcelessJobRepository#getJobInstance(String, JobParameters)`への呼び出しにより、Spring Batch v5.2でうまく機能していたテストシナリオがv6.0へのアップグレード時に不可能になりました。

このような場合、ユーザーは次のようなエラーを目にする可能性があります:

```text
Message: A job instance already exists and is complete for identifying parameters={JobParameter{name='batch.random', value=4546055881725385948}
```

これは混乱を招く可能性があります。なぜなら、ジョブ名や`JobParameters`が実際には異なっているにもかかわらず、リポジトリはそれらを同じ`JobInstance`に解決するからです。これはSpring Batchの概念モデルとも一致しないように感じられます。概念モデルでは、`JobInstance`はジョブ名とその`JobParameters`によって一意に識別されます。

## 提案される機能強化

元の設計を維持しながらこれらの課題に対処するために、`ResourcelessJobRepository`への以下の機能強化を提案したいと思います:

### 1. ジョブ名、ID、およびパラメータに基づいて戻り値をフィルタリング

以下のメソッドについて、内部の`JobInstance`および`JobExecution`フィールドに保持されている値と入力引数(`jobName`、`instanceId`、`executionId`、`JobParameters`など)を比較し、それに応じて戻り値をフィルタリングします:

* `getJobInstances(String jobName, int start, int count)`
* `findJobInstances(String jobName)`
* `getJobInstance(long instanceId)`
* `getLastJobInstance(String jobName)`
* `getJobInstance(String jobName, JobParameters jobParameters)`
* `getJobInstanceCount(String jobName)`
* `getJobExecution(long executionId)`
* `getLastJobExecution(String jobName, JobParameters jobParameters)`
* `getLastJobExecution(JobInstance jobInstance)`
* `getJobExecutions(JobInstance jobInstance)`

いくつかのメソッドには既に`// FIXME should return null if the id is not matching`のようなコメントがあり、この種のフィルタリングがすでに検討されていたことを示唆しています。これらのメソッドの一部だけが更新されても、観察可能な動作は実際には許容できるかもしれません。しかし、概念的な一貫性と将来の実装の保護のために、クラス全体で`jobName`、`jobInstanceId`などの体系的な比較を行う方が良いと思います。

### 2. 現在のJobInstanceとJobExecutionを削除するメソッドを追加

`ResourcelessJobRepository`から現在保持されている`JobInstance`と`JobExecution`を削除する機能を追加します:

* `deleteJobInstance(JobInstance jobInstance)`
* `deleteJobExecution(JobExecution jobExecution)`

これらのメソッドが導入されると、テストは実行したばかりの`JobInstance`または`JobExecution`を意図的に削除して、同じ`ResourcelessJobRepository`インスタンスをより柔軟に再利用できます。たとえば:

```java
@Autowired
JobOperatorTestUtils testUtils;

@Autowired
JobRepository repository;

@BeforeEach
void prepareTestUtils(@Autowired @Qualifier("helloParamJob") Job helloParamJob) {
  testUtils.setJob(helloParamJob);
}

@Test
void startJob() throws Exception {
  JobParameters params = testUtils.getUniqueJobParametersBuilder()
      .addLocalDate("helloDate", LocalDate.of(2025, 7, 28))
      .toJobParameters();
  JobExecution execution = testUtils.startJob(params);
  assertThat(execution.getExitStatus()).isEqualTo(ExitStatus.COMPLETED);

  // 次のテストのために現在のJobInstanceを明示的にクリア
  repository.deleteJobInstance(execution.getJobInstance());
}
```

これら2つの機能強化により、以下が実現されます:

* JobRepositoryインターフェースの契約により忠実な実装になる。
  * 異なるジョブ/パラメータが同じ`JobInstance`にマッピングされるという驚くべき動作を減らす。
* 特にSpring Batch 5.xから6.xへのアップグレード時に、テストシナリオで`ResourcelessJobRepository`をより有用にする。
* `ResourcelessJobRepository`の元のインメモリ、単一インスタンスの性質を維持する。

メンテナからのフィードバックに基づいて、喜んでPRを開くか、この提案をさらに洗練させます。


## コメント

### コメント 1 by arey

**作成日**: 2025-12-09

Spring Batch 5.xから6.0.0への移行時に、@benelogと同じ課題に遭遇しました:

> Message: A job instance already exists and is complete for identifying parameters={JobParameter{name='batch.random', value=4546055881725385948}

`SpringBatchTest`を使用した単体テストは、複数のジョブを実行しようとすると失敗しました。

2つのテストメソッド間でコンテキストが汚れるのを避けるために、`ResourcelessJobRepository`の制限を回避するいくつかのトリックを使用し、`deleteJobExecution`メソッドをオーバーライドしました。

`ResourcelessJobRepository`実装を改善し、`FIXME`を削除して`JobRepository`インターフェースの`UnsupportedOperationException`を実装できることを期待しています。

(コード例は省略)

### コメント 2 by benelog

**作成日**: 2025-12-10

@arey
同じ考えを持っていて、以下のプルリクエストに組み込みました:
https://github.com/spring-projects/spring-batch/pull/5140

### コメント 3 by fmbenhassine

**作成日**: 2025-12-10

この課題を報告していただきありがとうございます! 疑いの余地はありません。`ResourcelessJobRepository`はFIXMEを修正し(😅)、`JobRepository`インターフェースからのデフォルトメソッド(メタデータ削除メソッドを含む)を実装するために更新されるべきです。課題 [#5140](https://github.com/spring-projects/spring-batch/pull/5140) をマージします。LGTM 👍

それが整ったら、Spring Batchが提供するテストユーティリティを使用しているので、`JobRepository`を直接使用するのではなく`JobRepositoryTestUtils`を使用する必要があります(`JobOperator`の代わりに`JobOperatorTestUtils`を使用するのと同様):

(コード例の改善案は省略)

とはいえ、`ResourcelessJobRepository`は非常に特定のユースケース向けに設計されています: Spring Batchジョブの単一実行です。まさにそれを行います(そして、他のリポジトリ実装よりも2桁優れたパフォーマンスを発揮するため、非常にうまく機能していると思います)。これはそのJavadocおよび[リファレンスドキュメント](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html#_configuring_a_resourceless_jobrepository)に記載されています。したがって、適切なライフサイクル管理なしでテストで使用することを含め、設計された目的以外に使用することは正しくありません。実際、`ResourcelessJobRepository`は非常に軽量であり、テストコンテキストでプロトタイプBeanとして定義できます。すべてのジョブはそれぞれ異なるインスタンスを使用でき、これは完全に問題ありません。私はそれを仮想スレッドのようなものだと考えています: 必要なだけ使い捨てのリソースレスジョブリポジトリを持つことができ、それらを再利用したりプールしたりする必要はありません。いずれにせよGCされます。

### コメント 4 by benelog

**作成日**: 2025-12-10

@fmbenhassine
フィードバックと私のPRを好意的に検討していただきありがとうございます。

まず第一に、これは非常に直接的ですが、Spring Batch 6.0.0で`JobRepositoryTestUtils.removeJobExecutions()`を使用する際にこの課題を参照する人々のために、ここにメモを残しておきたいと思いました。

(技術的な説明は省略)

また、テストで使用される`JobRepository`を`ResourcelessJobRepository`から別の実装に切り替える可能性がある将来を考えると、すべての実行をクリアするのではなく、現在のテストによって作成された単一の`JobExecution`のみを削除する方が有益な場合があると思います。
テストに使用されるデータベースが複数の開発者間で共有されている環境では、すべての`JobExecution`レコードを消去すると意図しない副作用が生じる可能性があります。

`ResourcelessJobRepository.removeJobExecution(JobExecution)`などのメソッドの実装を追加することで、上記のように`JobRepositoryTestUtils`の使いやすさが向上し、同時に`JobRepository`契約がより完全に実装されます。

テスト用に`ResourcelessJobRepository`をプロトタイプBeanとして登録できるという設計意図を改めて説明していただきありがとうございます。
同じジョブを繰り返し実行する必要があるテスト用に別の`ApplicationContext`を定義することは確かに可能ですが、利便性の面でトレードオフがあると感じています。
このPRで提案されている`ResourcelessJobRepository.removeJobExecution(JobExecution)`の実装が採用されれば、これらの懸念に対処するのに役立つと期待しています。


### コメント 5 by fmbenhassine

**作成日**: 2025-12-11

課題 [#5140](https://github.com/spring-projects/spring-batch/pull/5140) で解決されました。課題を提起し、PRを貢献していただきありがとうございます 🙏

### コメント 6 by phactum-mnestler

**作成日**: 2025-12-15

私と同じ方法でこの課題を見つけた人のために:
私たちはSpring Bootの自動設定を使用しており、Spring Boot 4へのアップグレード後、フレームワークが`SimpleJobRepository`の代わりに`ResourcelessJobRepository`を提供したため、突然この課題と課題 [#5108](https://github.com/spring-projects/spring-batch/issues/5108) の両方が発生しました。`spring-boot-starter-batch-jdbc`の追加依存関係を追加することで、私たちの課題は解決しました。

