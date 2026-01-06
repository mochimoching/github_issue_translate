*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# GraalVMランタイムヒントの更新

**Issue番号**: #4844

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-22

**ラベル**: type: task, in: core, related-to: native

**URL**: https://github.com/spring-projects/spring-batch/issues/4844

**関連リンク**:
- Commits:
  - [580bd30](https://github.com/spring-projects/spring-batch/commit/580bd307a31726fa5e119a86161f05a290b44cef)
  - [f6f31ca](https://github.com/spring-projects/spring-batch/commit/f6f31cacc779f06cafb9cac275720f2a46831086)
  - [369652c](https://github.com/spring-projects/spring-batch/commit/369652cc73d227690de065d0fe3c16a14631774f)

## 内容

https://github.com/spring-projects/spring-framework/issues/33847 に関連して、Spring Batchのランタイムヒントを適切に更新する必要があります。

https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes#graalvm-native-applications を参照してください。

## コメント

### コメント 1 by goafabric

**作成日**: 2025-08-04

@fmbenhassine 
参考までに、GraalVM 24（ローカルとpaketoの両方）と組み合わせてboot 4.0.0-M1を試している間、ネイティブコンパイルが以下の例外で失敗するようになりました。
GraalVM 21ではコンパイルが機能しますが、既に単純なSpring Bootアプリでも、別の問題によりアプリケーションが起動しません。

`CoreRuntimeHints`をオーバーライドして中括弧を"\\{"とエスケープすると、コンパイルが機能します。
ただし、これが正しい方法かどうかはわかりません。

--- カット ---
Error: Error: invalid glob patterns found:
Pattern ALL_UNNAMED/org/springframework/batch/core/schema-{h2,derby,hsqldb,sqlite,db2,hana,mysql,mariadb,oracle,postgresql,sqlserver,sybase}.sql : Pattern contains unescaped character {. Pattern contains unescaped character }.

### コメント 2 by fmbenhassine

**作成日**: 2025-08-04

@goafabric 報告ありがとうございます！この失敗を追跡するために課題 [#4937](https://github.com/spring-projects/spring-batch/issues/4937) を作成し、次回の6.0.0-M2で修正する予定です。参考までに、この種の問題を回避するために、GraalVMに対するCIビルドを追加する予定です（課題 [#3871](https://github.com/spring-projects/spring-batch/issues/3871)）。

### コメント 3 by goafabric

**作成日**: 2025-08-04

> [@goafabric](https://github.com/goafabric) 報告ありがとうございます！この失敗を追跡するために [#4937](https://github.com/spring-projects/spring-batch/issues/4937) を作成し、次回の6.0.0-M2で修正する予定です。参考までに、この種の問題を回避するために、GraalVMに対するCIビルドを追加する予定です（[#3871](https://github.com/spring-projects/spring-batch/issues/3871)）。

とても迅速な返信と課題の作成をありがとうございます！
マイルストーンとその方法について、最初は報告すべきか迷いましたが、こんなに簡単だったのは素晴らしいです。
