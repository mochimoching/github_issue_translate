# GitHub Issue 要約ガイドライン

このドキュメントは、翻訳されたGitHub Issueを要約する際のガイドラインです。
Copilotや他のAIツールを使って要約する際に、このファイルを参照してください。

---

## 要約に使用したAIの明示

テキスト先頭に、以下を明示する。

*（このドキュメントは生成AI(model_name)によってyyyy年mm月dd日に生成されました）*

- model_name：使用した生成AIのモデル名
- yyyy：作成日（西暦）
- mm：作成日（月）
- dd：作成日（日）

例：*（このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました）*

---

## 要約内容

### 課題概要
- JavaやSpring Batch、Spring Framework、Spring Bootの知識は入門レベルである前提で、適宜内容を補足してください
- 表や図（PlantUML）を積極的に使用し、補足説明をしてください。処理の実行状態を、状態遷移図やシーケンス図を使い、表現すると有効です。
- PlantUMLで描画する場合は、mdファイルに埋め込んでください

### 原因
- 課題が発生した原因を記載

### 対応方針
- PR/commitリンク先の変更内容も踏まえて記載してください

---

## 注意点

- クラス名・メソッド名をバッククォート(``)で囲む
- Issue番号参照 (#XXXX) をリンク形式に変換
- 入力mdファイルに記載されているリンクを要約内容に記載する場合、リンク情報を維持する

---

## 出力ディレクトリ

要約結果は以下のディレクトリ構造で保存してください：

```
output/{repo}/{milestone}/{state}/current/markdown/issues_summary/
```

例：
- 入力ファイル: `output/spring-framework/6.0.0-M5/closed/current/markdown/issues_translated/issue_28298.md`
- 出力ファイル: `output/spring-framework/6.0.0-M5/closed/current/markdown/issues_summary/issue_28298.md`

### 出力ルール

1. **ディレクトリ**: `issues`、`issues_translated` ディレクトリと同階層に `issues_summary` ディレクトリを作成
2. **ファイル名**: 元のファイル名を維持（例: `issue_28298.md` → `issue_28298.md`）
3. **形式**: Markdown形式で保存
4. **エンコーディング**: UTF-8

---

## Copilotでの使用方法

### 方法1: 単一ファイルの要約

```
@workspace SUMMARY_GUIDELINE.mdのガイドラインに従って、
以下のファイルを要約してください：

[翻訳済みissueファイルのパス]
```

### 方法2: 複数ファイルの一括要約

```
@workspace SUMMARY_GUIDELINE.mdのガイドラインに従って、
issues_translatedディレクトリ内のすべてのファイルを要約し、
issues_summaryディレクトリに出力してください。
```

---

## 要約例

### 入力（翻訳済みissue）

```markdown
# SpEL式でnull安全な配列アクセスを追加

**Issue番号**: #28298
**状態**: closed | **作成者**: user123 | **作成日**: 2022-04-15

## 内容

現在、`array[0]`のようなSpEL式では、配列が`null`の場合に例外が発生します。
`array?[0]`のようなnull安全な構文をサポートしてほしいです。
```

### 出力（要約）

```markdown
*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました。*

## 課題概要

Spring Expression Language (SpEL) において、配列要素へのアクセス時にnull安全な演算子が利用できないという課題です。

**SpELとは**: Spring Frameworkが提供する式言語で、実行時にオブジェクトグラフの照会や操作を行うための機能です。`#{expression}`の形式で記述します。

現状の問題点:
- `array[0]`のような配列アクセスでは、`array`が`null`の場合に`NullPointerException`が発生
- 安全な処理のためには事前に`null`チェックが必要

## 原因

SpELの配列アクセス構文が、null安全な演算子（`?.`）に対応していないため。

## 対応方針

配列アクセスにnull安全な演算子を導入:
- 構文: `array?[0]`
- `array`が`null`の場合、例外をスローせず`null`を返す
- プロパティアクセスの`object?.property`と同様の動作
```

---

## 更新履歴

- 2026-01-06: 初版作成
