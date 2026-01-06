*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# EnableBatchProcessing(modular = true)の使用方法をv6に移行する方法を文書化

**Issue番号**: #5072

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-11-02

**ラベル**: in: documentation, type: task

**URL**: https://github.com/spring-projects/spring-batch/issues/5072

## 内容

これは#4866に関連しています。目標は、`EnableBatchProcessing(modular = true)`の使用をSpringのコンテキスト階層と`GroupAwareJob`に移行する方法を文書化することです(`EnableBatchProcessing`のJavadocで言及されているように)。

cc @kzander91 (https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3478015935で出発点を提供してくれました。ありがとうございます!)


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-19

こちらに例を追加しました: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide#changes-related-to-the-modular-batch-configurations-through-enablebatchprocessingmodular--true

### コメント 2 by kzander91

**作成日**: 2025-11-25

@fmbenhassine 例を見る機会を得ましたが、少し不足していると感じます:
* 古いモジュラー実装は、子コンテキストのライフサイクルも管理しており、親コンテキストがクローズされたときにすべてを適切にシャットダウンしていました。これを自分で再実装する必要があります。
* 以前は、親コンテキストの`JobLocator`を通じて、子コンテキストの`Job`を名前で取得できました。これはもはや不可能であり、ジョブを起動するロジックは何らかの方法で子コンテキストを取得する必要があります... 特にこの問題は、[アプリでの@marbon87のケース](https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3575452892)にも関連していると思います。

最もシンプルなアプリ以外のすべての適切な移行パスは、別々のコンテキストを使用_せず_、共有コンテキストですべてのJobを定義するか(おそらく私が行く方法)、以前のバージョンからSpring Batchの実装をコピーペーストすることだと感じます。

### コメント 3 by fmbenhassine

**作成日**: 2025-12-08

@kzander91 それを調べてフィードバックをありがとうございます!

> * 古いモジュラー実装は、子コンテキストのライフサイクルも管理しており、親コンテキストがクローズされたときにすべてを適切にシャットダウンしていました。これを自分で再実装する必要があります。

その機能はすでにSpring Bootに実装されており、理由もなくSpring Batchで重複していました。Bootから`new SpringApplicationBuilder(ParentConfig.class).child(ChildConfig.class).run(args);`を試しましたか? これによりコンテキストのライフサイクルを処理してくれます。

>  以前は、親コンテキストの`JobLocator`を通じて、子コンテキストの`Job`を名前で取得できました。これはもはや不可能です

これは#5122によるものだと思いますが、すでに修正し、今度の6.0.1にplannedしています。その修正により、`MapJobRegistry`はすべてのコンテキストからジョブを投入でき、登録はBean名(子コンテキストで同じ可能性がある)ではなくジョブ名(いずれにせよグローバルに一意であるべき)に基づくようになります。

---

もう一つ忘れていたオプションは、Springプロファイルを使用することです。この種のセットアップに適していると思います。そのアプローチを試しましたか? ここでも例を提供できます。サポートが必要な場合はお知らせください。


### コメント 4 by kzander91

**作成日**: 2025-12-08

> `new SpringApplicationBuilder(ParentConfig.class).child(ChildConfig.class).run(args);`をBootから試しましたか?

試しましたが、親コンテキストで組み込みTomcatを実行しているため、私のシナリオではうまく機能しません。Spring Bootはこれをサポートしていません: https://github.com/spring-projects/spring-boot/blob/1c0e08b4c434b0e77a83098267b2a0f5a3fc56d7/core/spring-boot/src/main/java/org/springframework/boot/builder/SpringApplicationBuilder.java#L207-L210
プロジェクトの残りを別の子コンテキストに入れ_ることもできます_が、これらのケースのどちらでも子コンテキストや兄弟コンテキストからJobビーンを見ることができません(中央のサービスビーンから名前でジョブを起動しているため、そのビーンはすべてのJobを知っている必要があります)。

> その修正により、`MapJobRegistry`はすべてのコンテキストからジョブを投入できます

それは正しくないと思います。親コンテキストは子コンテキストを認識していません。単方向の関係です(何か見逃していない限り)。`MapJobRegistry`は自身のコンテキスト_と親コンテキスト_からJobビーンを取得_できる_かもしれませんが、親コンテキストからビーンを考慮しない`getBeansOfType()`を使用しているため、そうしていません: https://github.com/spring-projects/spring-batch/blob/088487bb803c6a7a9139228ea973035a1698d864/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/support/MapJobRegistry.java#L63-L66
`getBeansOfType()`のドキュメント: https://github.com/spring-projects/spring-framework/blob/b038beb85490c8a80711b1a6c8cfffbb21276b3e/spring-beans/src/main/java/org/springframework/beans/factory/ListableBeanFactory.java#L267-L269
しかしいずれにせよ: これは`MapJobRegistry`が実行されているコンテキストとその親からビーンを見つけるだけで、子や兄弟からは見つけません。

> もう一つ忘れていたオプションは、Springプロファイルを使用することです。

すべてのビーンを単一のコンテキストに配置し、各ジョブの設定をプロファイルでガードすることについて話していますか? 🤔 これがどのように役立つかがよくわかりません。実行時に、私のアプリはいずれにせよすべてのJobを知っている必要があり、したがってこれらすべてのプロファイルを有効にする必要があります...

### コメント 5 by fmbenhassine

**作成日**: 2025-12-09

> 親コンテキストで組み込みTomcatを実行しているため、私のシナリオではうまく機能しません。Spring Bootはこれをサポートしていません

なるほど。親コンテキストにTomcatを埋め込んでいるという事実は重要な詳細ですが、最初のリクエストでも共有した最小限の例でも言及されていませんでした(私の以前のすべての回答は、非Web設定を前提としていました)。しかし問題ありません。あなたのケースのガイダンスを提供します。

まず最初に: Bean名の衝突を避けるためにSpringコンテキストをモジュール化することは、間違いなくSpring Batchの懸念事項ではありません。Spring Batchで`EnableBatchProcessing(modular = true)`や他の方法でこれを行おうとすると、間違いなく保守が過度に複雑なコードにつながるか、せいぜいSpring FrameworkやSpring Bootが提供するソリューションよりも悪いものになります。そして、この問題はSpring Batch自体に特有のものではなく、ユーザーがプロジェクト固有の名前付きアーティファクトをSpring Beanとして定義できる他のプロジェクト(Spring Integrationの統合フローやSpring Shellのシェルコマンドなど)でも発生する可能性があります。

さて、Spring Bootがあなたのユースケースをサポートしていないという事実は、Spring Bootの問題であり、Spring Batchの問題ではありません。そしてさらに重要なことに、単一のJVM内のサーブレットコンテナで複数のバッチジョブを実行するこのセットアップが物事を困難にしていると私は信じています(私は個人的にそのセットアップを推奨したことはなく、常に「コンテキストごとjarごとの単一ジョブ」パッケージング/デプロイメントモデルを推進してきました)。そのモノリシックモデルはSpring Batch Adminで使用されており、いくつかの問題があり、SCDFのモジュラーアプローチを支持してプロジェクトが廃止されることになりました([ここ](https://github.com/spring-attic/spring-batch-admin/blob/master/MIGRATION.md)の問題と移行の推奨事項を参照)。

とはいえ、あなたが持っているWebモデルを引き続き使用できますが、Spring Batchが提供するものよりもスマートなジョブレジストリが間違いなく必要です。

> 親コンテキストは子コンテキストを認識していません。単方向の関係です(何か見逃していない限り)。`MapJobRegistry`は自身のコンテキスト_と親コンテキスト_からJobビーンを取得_できる_かもしれませんが、親コンテキストからビーンを考慮しない`getBeansOfType()`を使用しているため、そうしていません

ほとんどの典型的なユースケースで物事を壊さない場合、双方向の関係を処理するために`MapJobRegistry`をよりスマートにすることにはオープンです。しかし、これが非常に特定のユースケースのためにフレームワーク側でコードを過度に複雑にする場合、ユーザーが独自のカスタムスマートレジストリを提供するようにします。フレームワークに入る偶発的な複雑さをどれだけ制御するかを常に試みています(これはv6の主要なテーマの一つです)。

> すべてのビーンを単一のコンテキストに配置し、各ジョブの設定をプロファイルでガードすることについて話していますか? 🤔 これがどのように役立つかがよくわかりません。実行時に、私のアプリはいずれにせよすべてのJobを知っている必要があり、したがってこれらすべてのプロファイルを有効にする必要があります...

あなたのユースケースについてはプロファイルのことは忘れてください。Web設定では機能しません。前述のように、非Web設定を想定しており、各ジョブを独自のコンテキスト/JVMで起動すると考えていたため、起動時にプロファイルを指定してその特定のジョブのビーン定義のみをロードすることになります。

---

フィードバックをお待ちしており、さらにお手伝いできることがあればご連絡ください。


### コメント 6 by kzander91

**作成日**: 2025-12-10

継続的な意見と説明をありがとうございます! 🙏

> 親コンテキストにTomcatを埋め込んでいるという事実は重要な詳細ですが、最初のリクエストでも共有した最小限の例でも言及されていませんでした

本当に申し訳ありません。この特定の詳細が問題になる(したがって関連する)とは知りませんでした。Bootの`SpringApplicationBuilder#child`であなたの提案を試したときにその制限について知っただけです。

> フィードバックをお待ちしています

あなたが提供した追加のコンテキストと理由付けを考慮すると、_なぜ_そのサポートを削除することを決定したのかをよりよく理解できます。以前は、完璧に機能していた機能(そして表面上はそれほど複雑には見えませんでした)が複雑さを減らすために「ただ」削除されたように見えました。

他の点については、もう一度言いたいのですが(https://github.com/spring-projects/spring-batch/issues/5126#issuecomment-3611770749を参照)、私はすでにアプリをリファクタリングして単一のコンテキストですべてのジョブを定義しています。
したがって、私_個人的には_モジュール化されたコンテキストの削除されたサポートに関する移行ヘルプはもはや必要なく、ここで終了してもかまいません。

同じことをしようと考えている他の人のために: 基本的に`ApplicationContextFactory` Beanを削除し、すべてのジョブ設定を含めるようにルートコンポーネントスキャンを調整しました。
それらの内部で、Bean名の衝突が存在しないようにBeanの名前を変更しました。
私の特定のアプリに固有のいくつかの場所で追加の調整が必要でしたので、状況によって異なります。


