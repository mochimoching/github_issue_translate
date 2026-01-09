*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# リソース不要なJobRepositoryの実装を検討

**課題番号**: #5139

**状態**: closed | **作成者**: izeye | **作成日**: 2025-12-02

**ラベル**: type: enhancement, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5139

**関連リンク**:
- Commits:
  - [e25c98d](https://github.com/spring-projects/spring-batch/commit/e25c98d5b30fff8c2dc81f29bee7d25dfad76c7e)

## 内容

**機能強化の説明**
アプリケーション開発者が、メモリ内ジョブリポジトリやテストに使用する`JobRepositoryTestUtils`の代わりに、本番環境や組み込みテストのような現実的なシナリオで使用できる、リソース不要な`JobRepository`の実装が提供されることを希望します。

**現在の状況**
Spring Frameworkでは、組み込みテストでリソースを使わずに実行するための`ResourcelessTransactionManager`があります。

**環境**
- Spring Batch 6.0.0
- Java 21

**関連課題**
- [関連討議 #4918](https://github.com/spring-projects/spring-batch/discussions/4918)
- [関連討議 #1521](https://github.com/spring-projects/spring-batch/discussions/1521)

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-02

@izeye さん、課題を作成していただきありがとうございます！メモリ内ジョブリポジトリやJobRepositoryTestUtilsの正確な課題は何でしょうか？もう少し詳しく教えていただけますか？

ユーティリティクラス`JobRepositoryTestUtils`はそれ自体がリソースレスです。これは、特定のジョブリポジトリ実装に対してテストデータを作成するためのヘルパーです。

また、すべての実装がトランザクション化されているわけではないため、`ResourcelessJobRepository`が必ずしも必要というわけではないでしょう。

とはいえ、`JobRepository`をトランザクションリソースとして指定できる仕組みを検討する価値はあるかもしれません（`ResourcelessTransactionManager`の場合と同様）。いくつかの調査と設計作業が必要です。

> 本番環境や組み込みテストのような現実的なシナリオで使用できる、リソース不要なJobRepositoryの実装が提供されることを希望します

メモリ内実装やMapベースの実装も現実的なシナリオで使用可能です。`MongoJobRepositoryFactoryBean`を検討していただいて良いでしょうか？それについてのご意見を伺いたいです。

最後に、長期的にはテストのためにリソースレスのジョブリポジトリをデフォルト化することを検討していますが、これは慎重に進める必要があります。

### コメント 2 by izeye

**作成日**: 2025-12-02

@fmbenhassine さん、迅速なご返信ありがとうございます！

> @izeye さん、課題を作成していただきありがとうございます！メモリ内ジョブリポジトリやJobRepositoryTestUtilsの正確な課題は何でしょうか？もう少し詳しく教えていただけますか？

私のユースケースは単純です。Mavenプロジェクトを作成する際、リソースとして使用するものを何も追加したくありません。データベースの依存関係も、組み込みテストのためのものも追加したくありません。

現在のところ、そのためには`@SpringBatchTest`などのユーティリティを使うことができません。`@SpringBatchTest`と`JobRepositoryTestUtils`についてのコメントはこれを意図したものです。

> また、すべての実装がトランザクション化されているわけではないため、`ResourcelessJobRepository`が必ずしも必要というわけではないでしょう。

ここでの「リソースレス」は、必ずしもトランザクションに関するものとは限りません。外部リソースを全く必要としないことを意味します。

> とはいえ、`JobRepository`をトランザクションリソースとして指定できる仕組みを検討する価値はあるかもしれません（`ResourcelessTransactionManager`の場合と同様）。いくつかの調査と設計作業が必要です。

それがあれば理想的ですね。

> メモリ内実装やMapベースの実装も現実的なシナリオで使用可能です。`MongoJobRepositoryFactoryBean`を検討していただいて良いでしょうか？それについてのご意見を伺いたいです。

`MongoJobRepositoryFactoryBean`はMongoDBを必要とするので、私の要件には合いません。

メモリ内またはMapベースの実装があれば、私のユースケースを満たすものとして完璧です。ただし、それが本番環境で使用するには意図されていないものであれば、ここで説明されているような名前（例：`ResourcelessJobRepository`）があった方が適切だと思います。

> 最後に、長期的にはテストのためにリソースレスのジョブリポジトリをデフォルト化することを検討していますが、これは慎重に進める必要があります。

それは素晴らしいですね！

### コメント 3 by fmbenhassine

**作成日**: 2025-12-03

@izeye さん、ご返信ありがとうございます。ご要望を理解できました。`@SpringBatchTest`と`JobRepositoryTestUtils`は、既に設定されている`JobRepository`の実装と連携して動作します。これらはそれ自体が`JobRepository`の実装ではありません。ですので、テストのためだけに`MapJobRepository`を使用していただければと思います。それが「リソースレス」なものです（永続性メカニズムがなく、ジョブリポジトリインターフェースのシンプルなマップベースの実装です）。

### コメント 4 by izeye

**作成日**: 2025-12-03

@fmbenhassine さん、返信ありがとうございます。

`MapJobRepositoryFactoryBean`を使えば、`@SpringBatchTest`と`JobRepositoryTestUtils`は問題なく使えることを確認しました。

ただ、永続化メカニズムがないため`MapJobRepositoryFactoryBean`を設定しようとすると、Spring Bootが自動設定する`JdbcJobRepository`が上書きされてしまうという問題があります。`spring-batch-test`を使用する場合でも、Spring Bootを使用する際にテストのためだけにデータベース依存関係を追加したくないのです。データベースの依存関係を追加せずにSpring Batchのテストユーティリティを使うことはできないでしょうか？

また、MongoDB、RabbitMQ、ActiveMQなどを使用する必要がないSpring Batchジョブを実装したい場合、リソースレスな`JobRepository`を使用できると良いのですが。

### コメント 5 by fmbenhassine

**作成日**: 2025-12-03

> ただ、永続化メカニズムがないため`MapJobRepositoryFactoryBean`を設定しようとすると、Spring Bootが自動設定する`JdbcJobRepository`が上書きされてしまうという問題があります。

その通りです。私もこれを確認しました。

> `spring-batch-test`を使用する場合でも、Spring Bootを使用する際にテストのためだけにデータベース依存関係を追加したくないのです。データベースの依存関係を追加せずにSpring Batchのテストユーティリティを使うことはできないでしょうか？

現在のところはできません。これはかなり前からの要望です。Spring Boot 4では、ストレージレイヤーをオプトインのアプローチとすることを検討しています。以下のチケットを参照してください：
- https://github.com/spring-projects/spring-boot/issues/28520
- https://github.com/spring-projects/spring-boot/issues/42993

これが実装されれば、自動設定されたデータソースとデフォルトのJDBCジョブリポジトリを回避するために、データベースの依存関係を追加する必要がなくなります。また、Spring Batchのバージョン6では、デフォルトの`JobLauncher`を取得するためにジョブリポジトリが必要なので、ジョブリポジトリの自動設定を使わずにアプリケーションを起動する際には、カスタムの`JobRepository`を提供する必要があります。`MapJobRepositoryFactoryBean`がここで役立ちます。

> また、MongoDB、RabbitMQ、ActiveMQなどを使用する必要がないSpring Batchジョブを実装したい場合、リソースレスな`JobRepository`を使用できると良いのですが。

MapベースのJobRepositoryを使うことができます。

私が見ている限りでは、MapベースのJobRepositoryをSpring Bootで利用可能にし、アプリケーション設定で簡単に設定できるようにする必要があります。例：

```
spring.batch.job.repository=map
spring.batch.job.repository=jdbc
spring.batch.job.repository=mongo
```

同時に、組み込みデータソースに頼らず、Spring Batchアプリを起動するための最小限の依存関係を提供できるようにする必要があります（これにはSpring Bootの変更も必要です）。

### コメント 6 by izeye

**作成日**: 2025-12-04

@fmbenhassine さん、たくさんのコンテキストを提供していただきありがとうございます！

> これが実装されれば、自動設定されたデータソースとデフォルトのJDBCジョブリポジトリを回避するために、データベースの依存関係を追加する必要がなくなります。また、Spring Batchのバージョン6では、デフォルトの`JobLauncher`を取得するためにジョブリポジトリが必要なので、ジョブリポジトリの自動設定を使わずにアプリケーションを起動する際には、カスタムの`JobRepository`を提供する必要があります。`MapJobRepositoryFactoryBean`がここで役立ちます。

今のところ、テストで`MapJobRepositoryFactoryBean`を使用する際には、データベースの依存関係を除外することは可能ですか？

### コメント 7 by fmbenhassine

**作成日**: 2025-12-04

> 今のところ、テストで`MapJobRepositoryFactoryBean`を使用する際には、データベースの依存関係を除外することは可能ですか？

申し訳ございませんが、私の前回のコメントは少し紛らわしかったかもしれません。更新させてください：

データベースの依存関係がない場合、デフォルトではSpring Bootが組み込みデータソースを提供します。これは、Spring BootがSpring Batchの自動設定を提供したときからの動作です。

Spring Boot 4では、Spring Batchの自動設定はデフォルトでJDBCジョブリポジトリとそれに必要なデータソースを提供しなくなります。ただし、Mapベースのジョブリポジトリを提供します。Spring Bootでの詳細：https://github.com/spring-projects/spring-boot/issues/28520

この変更に加えて、Spring Batchでは、https://github.com/spring-projects/spring-batch/issues/1521 の中で、以下のようなジョブリポジトリを設定ファイルで選択できるようにする予定です：

```
spring.batch.job.repository.type=map
spring.batch.job.repository.type=jdbc
spring.batch.job.repository.type=mongo
```

これらの変更はすべて、私が「ストレージレイヤーをオプトインにする」と言っているものです。

その時点で、データベースの依存関係を追加しなくても、Mapベースのジョブリポジトリを使ってSpring Batchアプリケーションをテストできるようになります。それまでの間は、データベースの依存関係が必要になります。それが現在の仕組みです。

### コメント 8 by fmbenhassine

**作成日**: 2025-12-04

`MapJobRepositoryFactoryBean`をSpring Batchのテストに使用するために、データベースの依存関係を持たずにSpring Batchをテストする例を作成しました：https://github.com/fmbenhassine/spring-batch-lab/tree/main/issues/so79301374

これは今でも実現可能です。ただし、Spring Batchの自動設定をSpring Bootのすべての機能を保持したまま無効にすることはできません（これはSpring Boot 4で変更される予定です）。詳細は先ほどの私のコメントを参照してください。

### コメント 9 by izeye

**作成日**: 2025-12-04

@fmbenhassine さん、例を提供していただきありがとうございます！

Spring Boot 4で自動設定が変わり、設定プロパティだけでジョブリポジトリのタイプを変更できるようになることは素晴らしいですね。

また、「H2のような組み込みDBを使わずに」メモリ内データベースのみを使用して「MapJobRepository」を使えるようになることを願っています。

### コメント 10 by fmbenhassine

**作成日**: 2025-12-04

ありがとうございます。私のプロトタイプはその時点での動作を示しています。Mapベースのジョブリポジトリは必要に応じて設定できます。おそらくデフォルトになると思います（まだ確定ではありません）。

上述したように、Spring Boot 4では、組み込みデータソース（例：H2）は自動設定されなくなります。メモリ内データソースはMapベースのジョブリポジトリで、データベースは不要です。

> また、「H2のような組み込みDBを使わずに」メモリ内データベースのみを使用して「MapJobRepository」を使えるようになることを願っています。

これは私のプロトタイプで示されていることです。データベースはまったく使用されていません。

