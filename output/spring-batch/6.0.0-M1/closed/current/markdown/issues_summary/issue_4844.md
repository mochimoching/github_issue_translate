*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

Spring FrameworkのGraalVMランタイムヒントAPIの変更（https://github.com/spring-projects/spring-framework/issues/33847）に対応するため、Spring Batchのランタイムヒントを更新する作業です。

**GraalVMとは**: Javaアプリケーションをネイティブイメージ（実行ファイル）にコンパイルできる高性能VM環境です。起動速度とメモリ使用量が劇的に改善されます。

**ランタイムヒントとは**: リフレクション、リソース、プロキシなど、コンパイル時に静的解析できない要素をGraalVMに通知するメタデータです。

### 問題の例

GraalVM 24でのコンパイルエラー：
```
Error: invalid glob patterns found:
Pattern ALL_UNNAMED/org/springframework/batch/core/schema-{h2,derby,...}.sql : 
Pattern contains unescaped character {.
Pattern contains unescaped character }.
```

## 原因

Spring Framework 7.0でGraalVMランタイムヒントのAPI仕様が変更され、globパターンの書き方等が厳密化されました。Spring BatchのヒントもこれIconに準拠する必要がありました。

## 対応方針

**コミット**: [580bd30](https://github.com/spring-projects/spring-batch/commit/580bd307a31726fa5e119a86161f05a290b44cef), [f6f31ca](https://github.com/spring-projects/spring-batch/commit/f6f31cacc779f06cafb9cac275720f2a46831086), [369652c](https://github.com/spring-projects/spring-batch/commit/369652cc73d227690de065d0fe3c16a14631774f)

1. Globパターンの中括弧をエスケープ（`\\{`, `\\}`）
2. Spring Framework 7.0の新しいヒントAPIに準拠
3. GraalVM 24との互換性を確保

### 修正例

```java
// 修正前
hints.resources().registerPattern("schema-{h2,derby,hsqldb}.sql");

// 修正後
hints.resources().registerPattern("schema-\\{h2,derby,hsqldb\\}.sql");
```

### メリット

- GraalVM 24でのネイティブコンパイルが正常に動作
- Spring Batch アプリケーションのネイティブイメージ化が可能に
- 起動速度とメモリ使用量の大幅改善

今後、課題 [#3871](https://github.com/spring-projects/spring-batch/issues/3871) でGraalVMに対するCIビルドを追加予定です。
