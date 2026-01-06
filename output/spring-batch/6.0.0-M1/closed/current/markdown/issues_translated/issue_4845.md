*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# プリミティブ型の代わりにドメイン型を使用してJobOperator APIを改善

**Issue番号**: #4845

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-22

**ラベル**: in: core, type: enhancement, api: breaking-change, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4845

**関連リンク**:
- Commits:
  - [8dde852](https://github.com/spring-projects/spring-batch/commit/8dde8529d36b646b33a1711219a1b1e8a046345a)

## 内容

`JobOperator`はバッチジョブを操作するための主要な高レベルAPIです。しかし、現在はほとんどのメソッドシグネチャでプリミティブ型を使用することで、低レベルAPIとして設計されています。これにより、実装は本来そこで対処すべきではない関心事に対処する必要があります。

例えば、`start(String jobName, Properties parameters)`でジョブを開始するには、`JobRegistry`からジョブを見つけ、`JobParametersConverter`を使用してプロパティを`JobParameters`に変換する必要があります。この設計により、実装は2つの協力者（`JobRegistry`と`JobParametersConverter`）を必要としますが、`#start(Job job, JobParameters parameters)`のようにメソッドシグネチャでドメイン型を使用することで回避できたはずです。

別の例は`stop(long jobExecutionId)`で、IDでジョブ実行を見つけ、そこからジョブ名を取得し、次にレジストリからジョブ自体を取得して、最終的にジョブを停止できるようにする必要があります。これは代わりに`stop(JobExecution jobExecution)`を使用することで回避できます。

パラメータ変換、ジョブ取得、その他の関心事は、`CommandLineJobLauncher`や`JmxConsoleAdapter`のような低レベルAPIの一部であるべきですが、`JobOperator`では不適切です。コアドメインAPIは、メソッドシグネチャでドメイン型を使用して設計されるべきです。
