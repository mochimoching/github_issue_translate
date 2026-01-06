*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# 6.0.0-RC2のJavadocサイトが欠落

**Issue番号**: #5085

**状態**: closed | **作成者**: scordio | **作成日**: 2025-11-11

**ラベル**: in: documentation, in: build, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5085

## 内容

https://docs.spring.io/spring-batch/docs/6.0.0-RC2/api/ が存在しませんが、https://docs.spring.io/spring-batch/docs/6.0.0-RC1/api/ は存在します。


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-12

これを報告していただきありがとうございます。c266075e5eb695da1316087c217264c302d277f8のリグレッションのようです。Javadocで問題が発生するのはこれが初めてではありません... ご不便をおかけして申し訳ございません 😔

来週予定されているGAで修正します。

### コメント 2 by fmbenhassine

**作成日**: 2025-11-18

こんにちは @scordio、

ご参考までに、6.0.0-RC2のJavadocがオンラインで利用可能になりました: https://docs.spring.io/spring-batch/reference/6.0/api/index.html

ただし、今後のURLの違いに注意してください:

```
以前: https://docs.spring.io/spring-batch/docs/6.0.0-RC1/api/index.html
今後: https://docs.spring.io/spring-batch/reference/6.0/api/index.html
```
パッチバージョン番号はURLに含まれなくなりましたが、ホームページの左上のナビゲーションメニューから選択できます。この変更は、Antora基盤のドキュメントプロセス(一元化されたドキュメント、SEOフレンドリーなURL、マルチバージョン検索機能など)を使用するというポートフォリオ全体の目標に関連しています。このURL変更はリリースノートに文書化されます。

### コメント 3 by scordio

**作成日**: 2025-11-18

> パッチバージョン番号はURLに含まれなくなりました

https://docs.spring.io/spring-batch/reference/6.0.0-RC2/api/ から新しいURLへのリダイレクトがあることに気づきました。これにより、`spring-boot-dependencies`の[`spring-batch.version`](https://github.com/spring-projects/spring-batch-extensions/blob/e4b2130053a442c5bfd7d062a6199013f0e41040/spring-batch-notion/pom.xml#L204)プロパティを引き続き使用できます。

しかし、`javadoc`はリダイレクトを[警告](https://github.com/spring-projects/spring-batch-extensions/actions/runs/19467873075/job/55707152839?pr=191#step:4:460)として扱います:

```
[WARNING] Javadoc Warnings
[WARNING] warning: URL https://docs.spring.io/spring-batch/reference/6.0.0-RC2/api/element-list was redirected to https://docs.spring.io/spring-batch/reference/6.0/api/element-list -- Update the command-line options to suppress this warning.
[WARNING] 1 warning
```

私のビルドはjavadocの警告で失敗するように設定されているため、この警告を特別に抑制できるか確認しましたが、[DocLintグループ](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javadoc.html#groups)にそのような粒度は見当たりませんでした。これにより、3つのオプションが残されます:
* 警告の場合の失敗を削除する(あまり好みではない)
* URLに`6.0`をハードコード
* [javadoc.io](https://javadoc.io/)でホストされている[Spring Batch Javadoc](https://javadoc.io/doc/org.springframework.batch/spring-batch-core/latest/index.html)にフォールバック

今のところ、https://github.com/spring-projects/spring-batch-extensions/pull/191/commits/6bbcf83780bf1ae510ffad1685c7fec67fc199fc で最後のオプションを選択しました。

### コメント 4 by fmbenhassine

**作成日**: 2025-11-19

このサーバー側のリダイレクトはポートフォリオ全体で行われており、Spring Batch側でできることが見当たりませんが、提案があればお聞かせください。

### コメント 5 by scordio

**作成日**: 2025-11-19

Frameworkでは明示的なRCまたはパッチバージョンでまだ動作していることがわかります。例:
* https://docs.spring.io/spring-framework/docs/7.0.0-RC3/javadoc-api
* https://docs.spring.io/spring-framework/docs/7.0.0/javadoc-api

まだ新しい方法に移行する必要があるのかもしれませんか?

### コメント 6 by fmbenhassine

**作成日**: 2025-11-19

はい、そうかもしれません。チームに確認して、お返事します。

ちなみに、Bootのjavadocもリダイレクトがあります(Batchと同様):

https://docs.spring.io/spring-boot/4.0.0-RC2/api/java/index.html は
https://docs.spring.io/spring-boot/4.0/api/java/index.html にリダイレクトされます

### コメント 7 by scordio

**作成日**: 2025-11-19

ポートフォリオ全体がこの方向に進んでいるので、[javadoc-dev](https://mail.openjdk.org/mailman/listinfo/javadoc-dev)メーリングリストでこのユースケースにどう対処すべきか聞いてみます。


