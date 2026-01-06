*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobKeyGeneratorインターフェースから不要なジェネリックを削除

**Issue番号**: #4886

**状態**: closed | **作成者**: patrickwinti | **作成日**: 2025-06-13

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4886

## 内容

`JobKeyGenerator<T>`インターフェースは現在、ジョブキーを生成するために使用されるソースを表すジェネリック型パラメータ`<T>`を使用しています。しかし、実際には、このインターフェースの実装と使用は`JobParameters`をソース型として依存しています。

ジェネリックパラメータは意味のある柔軟性を提供せず、不必要な複雑性を導入する（例：消費者でキャストやワイルドカード型を必要とする）ため、インターフェースを以下にリファクタリングする方がクリーンです：

```java
public interface JobKeyGenerator {
    String generateKey(JobParameters source);
}
```

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-07-14

同意します、指摘していただきありがとうございます！

これはメジャーリリースの良い候補なので、v6で計画します。

### コメント 2 by fmbenhassine

**作成日**: 2025-07-14

課題 [#4887](https://github.com/spring-projects/spring-batch/issues/4887) で解決されました。
