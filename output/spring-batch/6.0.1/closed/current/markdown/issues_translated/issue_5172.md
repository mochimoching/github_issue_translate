*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# ローカルチャンキングにおいて、マネージャーステップのBatchStatusが完了しているのにワーカーステップが処理を続けている

**課題番号**: #5172

**状態**: closed | **作成者**: EduardoDiezBaez | **作成日**: 2025-12-17

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5172

**関連リンク**:
- Commits:
  - [0d5c7c7](https://github.com/spring-projects/spring-batch/commit/0d5c7c7b98e0bfcc39dee5a87cf42dc8bce3de04)

## 内容

**バグの説明**
ローカルチャンキングパターンを実装したジョブを実行すると、処理するアイテムがなくなる前にマネージャーステップが完了した状態になる場合があります。その結果、マネージャーステップの`BatchStatus`は`COMPLETED`になりますが、ワーカーステップがまだアイテムを処理中で、ワーカーステップの`BatchStatus`が`STARTED`のままという状態になります。

**環境**
- Spring Batch 6.0.0
- Spring Integration 6.3.8
- Spring Boot 4.0.0

**再現手順**
次の再現例を実行してください：
https://github.com/EduardoDiezBaez/spring-batch-local-chunking-reproducible-example

1. リポジトリをクローン
2. メインアプリケーションを実行
3. マネージャーステップが完了した後も、ワーカーステップがアイテムを処理し続けることを確認

## コメント

### コメント 1 by EduardoDiezBaez

**作成日**: 2025-12-17

この課題は、ステップ実行コンテキストの更新時にPessimistic Locking例外が断続的に発生していたことに起因していると考えられます。最近この例外をコンソールで確認しました。

```
org.springframework.dao.OptimisticLockingFailureException: Attempt to update step execution id=17763 with wrong version (1), where current version is 13
```

この課題は、次のPRで修正される予定であることが判明しました：
https://github.com/spring-projects/spring-batch/pull/4925/

`ResourcelessTransactionManager`を使用することで、ローカルでもこの問題を回避できることを確認しました。

この課題を報告したことをお詫びします。既にこの問題に対処されていることが分かりました。

### コメント 2 by fmbenhassine

**作成日**: 2025-12-18

@EduardoDiezBaez さん、問題ございません。ご報告とサンプルをありがとうございます！これは実際にバグです。

> この課題は、ステップ実行コンテキストの更新時にPessimistic Locking例外が断続的に発生していたことに起因していると考えられます。

これは異なる問題です。マネージャーステップがすべてのチャンクを送信した後、次のコールチェーンで`MessageChannelPartitionHandler#handle`メソッドが`ExecutorChannel`をシャットダウンします：

```
Manager step completes before processing all items -> pollable.receive() times out -> manager executor channel is shutdown
```

これにより、ワーカーが実行を試みる前にチャネルがシャットダウンされてしまいます。私のマシンでは、以下のようなログが表示されます：

```
2025-12-18T11:32:44.854+01:00  INFO 24608 --- [localChunkingApp] [cTaskExecutor-3] o.s.i.endpoint.EventDrivenConsumer       : Removing {message-handler:inboundRequests.serviceActivator} as a subscriber to the 'inboundRequests' channel
2025-12-18T11:32:44.858+01:00  INFO 24608 --- [localChunkingApp] [cTaskExecutor-3] o.s.integration.channel.ExecutorChannel  : Channel 'application.inboundRequests' has 0 subscriber(s).
2025-12-18T11:32:44.860+01:00  INFO 24608 --- [localChunkingApp] [cTaskExecutor-3] o.s.i.endpoint.EventDrivenConsumer       : stopped bean 'inboundRequests.serviceActivator'
2025-12-18T11:32:44.864+01:00  INFO 24608 --- [localChunkingApp] [cTaskExecutor-3] o.s.b.c.l.s.SimpleJobLauncher            : Job: [SimpleJob: [name=localChunkingJob]] completed with the following parameters: [{'run.id':'{value=1, type=class java.lang.Long, identifying=true}'}] and the following status: [COMPLETED]
```

以下の出力を見ると、ワーカーがシャットダウンされた後に到着したことが分かります：

```
Channel 'application.inboundRequests' has 0 subscriber(s).
```

しかしながら、`MessageChannelPartitionHandler#handle`メソッドのコードを調べると、「チャンクリクエストがすべて送信された時点でマネージャーステップが完了した」と見なすことが間違いであることが分かります。正しくは、チャンクリクエストが送信され、それらのチャンクに対するすべての**応答**が受信された時点で、マネージャーステップは完了します。

このため、次のコールチェーンが発生します：

```
Manager step completes before processing all items -> pollable.receive() times out -> manager step is put in COMPLETED status with an empty aggregate status -> manager executor channel is shutdown
```

これは理にかなっています。なぜなら、チャンクリクエストが送信され、マネージャーステップがタイムアウト前にすべての応答を受信しなかった場合、不完全な集約ステータスでマネージャーステップを完了状態にするべきではないからです。マネージャーステップは、すべてのワーカーからの応答を受信するまで`STARTED`状態にとどまるべきです。この課題をバグとして確認し、6.0.1で修正します。

また、#5175で、この問題を予防またはデバッグしやすくするために、提供されるタイムアウト値をもとに警告メッセージを表示するようにします。

### コメント 3 by EduardoDiezBaez

**作成日**: 2025-12-18

@fmbenhassine さん、フィードバックありがとうございます！この問題を解決しようとしている際に、`stepExecutionUpdates`チャネルが設定されていなかったことに気付きました。このチャネルは、[リファレンスドキュメント](https://docs.spring.io/spring-batch/reference/spring-batch-integration/remote-chunking.html)によると、オプションとされています。

`stepExecutionUpdates`をチャネルに設定し、`IntegrationMessageChannelItemWriter`が書き込むたびに、設定した`stepExecutionUpdates`チャネルにメッセージを送信するようにしました。

この修正により、マネージャーステップとワーカーステップの両方が、すべてのアイテムが処理された後に完了するようになりました。マネージャーステップは、期待通りに`COMPLETED`ステータスで終了します。

ただし、ワーカーステップの`BatchStatus`がすべてのアイテムが処理された後でも正しく更新されないという課題が残っています。前述の変更により、ワーカーステップは最終的に完了し、すべてのアイテムが処理されますが、そのステータスは依然として`STARTED`のままです。ワーカーステップの実行中に何も変更されないようです。

### コメント 4 by fmbenhassine

**作成日**: 2025-12-18

@EduardoDiezBaez さん、ご返信ありがとうございます！`stepExecutionUpdates`チャネルを追加しても、マネージャーステップがすべてのワーカーからの応答を受信する前に完了してしまうという問題は解決されません。

このバグの修正には、返信集約動作の変更が必要です。集約ストア内のすべてのチャンクが受信されるまで、ポーリングがタイムアウトしないようにします。これにより、マネージャーが完了する前にすべてのチャンクが集約されることが保証されます。修正を進めます。進捗はhttps://github.com/spring-projects/spring-batch/commit/0d5c7c7b98e0bfcc39dee5a87cf42dc8bce3de04でご確認いただけます。完了したら追ってお知らせします。

### コメント 5 by EduardoDiezBaez

**作成日**: 2025-12-18

@fmbenhassine さん、フィードバックありがとうございます。確かにコミットを確認させていただきます。時間を割いていただき、お手数をおかけしました！

### コメント 6 by fmbenhassine

**作成日**: 2025-12-19

修正を完了しました。@EduardoDiezBaez さん、私の変更をプルしてご確認いただけますでしょうか？よろしくお願いします。

### コメント 7 by EduardoDiezBaez

**作成日**: 2025-12-19

@fmbenhassine さん、修正いただきありがとうございます！変更をプルして確認させていただきます。近日中に更新させていただきます。

### コメント 8 by EduardoDiezBaez

**作成日**: 2025-12-19

@fmbenhassine さん、修正をテストしました。マネージャーステップが完了する前にワーカーステップのすべてのパーティションが完了していることを確認できました。ローカルチャンキングのサンプルでテストし、意図通りに動作しています。

ただ、気になる点があります：マネージャーステップは現在、ワーカーステップからの応答を最大で`timeout * number_of_chunks`ミリ秒待ちます。これは正しい動作で、すべてのパーティションが完了するまでマネージャーが待機することを保証します。この動作は以前から存在していましたでしょうか？もしそうであれば、以前のバージョンでは異なる動作をしていた可能性があるため、確認させてください。

それ以外は、すべて正常に動作しています。修正をありがとうございました！

### コメント 9 by fmbenhassine

**作成日**: 2025-12-19

動作確認ありがとうございます！

> ただ、気になる点があります：マネージャーステップは現在、ワーカーステップからの応答を最大で`timeout * number_of_chunks`ミリ秒待ちます。

それは正しいです。`MessagingTemplate#receive(PollableChannel destination, long timeout)`のjavadocに記載されています：

> 指定されたタイムアウト内にメッセージが利用可能になった場合、Messageを受信します。利用可能なメッセージがない場合、このメソッドは即座にnullを返します。

このタイムアウトは、アプリケーションが応答を取得するために待機する時間です。集約ストアを使用して利用可能なチャンクをすべて消費するように実装が変更されました。この変更により、ステップはすべてのパーティションステータスが収集されるまで完了しません。これが意図された動作です。

詳細については、以下のコメントを参照してください：https://github.com/spring-projects/spring-batch/issues/5172#issuecomment-2555264408

