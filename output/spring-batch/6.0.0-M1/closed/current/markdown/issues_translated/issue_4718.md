*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# 代替JobRepositoryの設定時の使いやすさを改善

**Issue番号**: #4718

**状態**: closed | **作成者**: joshlong | **作成日**: 2024-11-24

**ラベル**: type: bug, in: core, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4718

**関連リンク**:
- Commits:
  - [f7fcfaa](https://github.com/spring-projects/spring-batch/commit/f7fcfaa4fdb1f762a3bc16c30750d646dc52a6ed)

## 内容

Spring Bootが依存している`DefaultBatchConfiguration`がJDBCベースのインフラストラクチャのみを前提としているため、代替の`JobRepository`を設定する際の使いやすさを改善する必要があります。つまり、Spring Bootを使用している場合、`JobRepository`型のBean1つを単純に置き換えるだけでは動作しません。Spring Bootが登場する前に行っていたように、すべてを一から再設定する必要があります。

これは、新しい「リソースレス」およびMongoDB JobRepositoryの代替実装を利用したいSpring Batchユーザーにとって問題となります。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2024-12-03

`@EnableBatchProcessing`（およびそれに基づく`DefaultBatchConfiguration`）は、データソースが必須であるbatch名前空間のXML要素`job-repository`のJava対応として設計されました：

```xml
<batch:job-repository id="jobRepository" data-source="dataSource" transaction-manager="transactionManager"/>
```

そのため、`@EnableBatchProcessing`はJDBCインフラストラクチャを前提としていますが、MongoDBのJobRepositoryとリソースレスのJobRepositoryを導入した今、これは変更すべきです。

この問題に対処する方法についていくつかアイデアがありますし、もちろんこれに関するあらゆる意見にも対応します。次のメジャーリリースに向けてこの設計課題に取り組む際に、これらのアイデアをコミュニティと共有する予定です。このコメントは、問題を検証し認識するためのものです。報告いただきありがとうございます、@joshlong！

### コメント 2 by krewetka

**作成日**: 2025-03-10

@fmbenhassine こんにちは。適切な修正が次のメジャーバージョンで予定されているとのことですが、それより早い回避策はありますか？🤔

特にシャットダウンの問題を克服する方法についてです。正直なところ、これは本番環境での使用において非常に大きな問題であり、5.3ではなく6で修正されるということは、少なくとも数年間は修正されないように思えます🤔

何か間違ったことをしているだけかもしれませんが、多くの試みにもかかわらず、適切なシャットダウンを設定することができませんでした。

ジョブの起動を通常のコンテナからAWS Batchでの起動に移行したので、少なくとも通常のCI/CDデプロイメントが長時間実行ジョブを中断することはなくなりましたが、これは私たちが見つけた回避策に過ぎません。

### コメント 3 by fmbenhassine

**作成日**: 2025-03-11

@krewetka どのシャットダウンの問題を指していますか？それはこの課題とどのように関連していますか？別の[ディスカッション](https://github.com/spring-projects/spring-batch/discussions)を開いて問題を説明していただければ、そこで喜んでお手伝いします。

参考までに、v6は今年11月に予定されており、現時点ではv5.3の計画はありません。その間、v5.2で非JDBCのJobRepositoryを使用したい方は、完全な例を添付したこの[SOスレッド](https://stackoverflow.com/a/79492398/5019386)をご確認ください。

### コメント 4 by krewetka

**作成日**: 2025-03-12

こんにちは、すみません。私の間違いでした。私が言及しているのは https://github.com/spring-projects/spring-batch/issues/4728#issuecomment-2578356238 で、これはこの課題の重複としてマークされています。それでも別の課題を開くべきでしょうか？🤔

MongoDBのセットアップは正常に動作しています（ただしH2がまだ残っています）。

`DataSourceAutoConfiguration.class`を除外することも試みましたが、まだいくつかの問題に直面しています。もう一度試してみて、正確な結果を確認します。

### コメント 5 by fmbenhassine

**作成日**: 2025-03-12

@krewetka 

> それでも別の課題を開くべきでしょうか？

はい、お願いします。シャットダウンのライフサイクルの問題は、MongoDBセットアップでH2が必要になることとは別の問題です。

### コメント 6 by krewetka

**作成日**: 2025-03-12

わかりました、シャットダウンに関する完全な例を新しい課題で提供するようにします。コードからH2を完全に削除できれば解決するかもしれません🤞

ところで、[SOスレッド](https://stackoverflow.com/a/79492398/5019386)を確認しましたが、`EnableBatchProcessing`を使用していないことに気づきました。

私たちのコードではまだこれを使用しており、H2を削除すると次のエラーが発生します：
`Error creating bean with name 'jobExplorer': Cannot resolve reference to bean 'dataSource' while setting bean property 'dataSource'`
追加した内容：`@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`

おそらく`EnableBatchProcessing`を使用しないようにする必要がありますが、それでも`tablePrefix`、`isolationLevelForCreate`、`taskExecutorRef`など、そこからのほぼすべての他の要素をどこかで設定する必要があります。
