# GitHub Issue 翻訳ガイドライン

このドキュメントは、GitHub Issueを日本語に翻訳する際のガイドラインです。
Copilotや他のAIツールを使って翻訳する際に、このファイルを参照してください。

---

## 翻訳に使用したAIの明示

テキスト先頭に、以下を明示する。

*（このドキュメントは生成AI(model_name)によってyyyy年mm月dd日に生成されました）*

- model_name：使用した生成AIのモデル名
- yyyy：作成日（西暦）
- mm：作成日（月）
- dd：作成日（日）

例：*（このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました）*

---

## 翻訳スタイル

以下の3つの翻訳スタイルから選択してください。

### 1. 直訳 (literal)

- 原文の構造と表現をできるだけ忠実に保つ
- 原語の順序を尊重し、直接的な翻訳を行う
- 意訳や意訳的な表現を避ける
- 文字通りの翻訳を優先する

**用途**: 厳密な正確性が必要な場合、技術仕様書など

### 2. 意訳 (free)

- 原文の意図とニュアンスを正確に伝える
- 日本語として最も自然で読みやすい表現を使用
- 必要に応じて文構造を変更しても良い
- 日本語読者にとって理解しやすい表現を優先する

**用途**: エンドユーザー向けドキュメント、読みやすさ重視の場合

### 3. バランス型 (balanced) ※推奨

- 原文の意図を正確に伝えながら、自然な日本語を使用
- 直訳と意訳のバランスを取る
- 技術的な正確さと読みやすさを両立させる

**用途**: 一般的な技術文書の翻訳

---

## 共通翻訳要件

すべての翻訳スタイルで以下のルールを守ってください。

### 固有名詞の扱い

- **Spring Batch** などの固有名詞はそのまま保持すること
- 製品名、プロジェクト名は原語のまま使用する

### マークダウン記法の保持

- コードブロック（```で囲まれた部分）はそのまま保持すること
- マークダウンのフォーマット（見出し、リスト、強調など）は維持すること
- リンクやURL構造は変更しないこと

### コードフォーマットルール

#### タイトル翻訳の場合
- クラス名やメソッド名もそのまま翻訳し、バッククォート(``)で囲まない
- 例: "Add JobRepository class support" → "JobRepositoryクラスのサポートを追加"

#### 本文翻訳の場合
- クラス名、メソッド名、変数名、ファイル名などのプログラムコードは必ずバッククォート(``)で囲むこと
- 例: "JobRepository class" → "`JobRepository`クラス"
- 例: "the execute method" → "`execute`メソッド"
- 例: "StepExecution object" → "`StepExecution`オブジェクト"

### 技術用語の翻訳

以下の技術用語は適切な日本語訳を使用してください:

| 英語 | 日本語 |
|------|--------|
| issue | 課題 |
| feature | 機能 |
| bug | バグ |
| enhancement | 機能強化 |
| documentation | ドキュメント |
| test | テスト |
| implementation | 実装 |
| behavior | 動作 |
| parameter | パラメータ |
| configuration | 設定 |
| repository | リポジトリ |
| dependency | 依存関係 |

### 文体

- 丁寧で読みやすい文章にすること
- 技術文書として適切な表現を使用すること
- 「です・ます」調を使用すること

---

## 翻訳例

### タイトル翻訳の例

**原文:**
```
Add integration tests for DDL migration scripts
```

**翻訳 (バランス型):**
```
DDLマイグレーションスクリプトの統合テストを追加
```

注意: タイトルでは「Issue #1234:」のようなプレフィックスは除外してください。

### 本文翻訳の例

**原文:**
```
The JobRepository class needs to support batch processing.
We should update the execute method to handle this case.
See issue #5093 for details.
```

**翻訳 (バランス型):**
```
`JobRepository`クラスはバッチ処理をサポートする必要があります。
このケースを処理するために`execute`メソッドを更新する必要があります。
詳細については課題 [#5093](https://github.com/spring-projects/spring-batch/issues/5093) を参照してください。
```

注意点:
- クラス名・メソッド名をバッククォートで囲む
- Issue番号参照 (#XXXX) をリンク形式に変換

---

## 出力ディレクトリ

翻訳結果は以下のディレクトリ構造で保存してください：

```
output/{repo}/{milestone}/{state}/current/markdown/issues_translated/
```

例：
- 入力ファイル: `output/spring-framework/6.0.0-M5/closed/current/markdown/issues/issue_28298.md`
- 出力ファイル: `output/spring-framework/6.0.0-M5/closed/current/markdown/issues_translated/issue_28298.md`

### 出力ルール

1. **ディレクトリ**: `issues` ディレクトリと同階層に `issues_translated` ディレクトリを作成
2. **ファイル名**: 元のファイル名を維持（例: `issue_28298.md` → `issue_28298.md`）
3. **形式**: Markdown形式で保存
4. **エンコーディング**: UTF-8

---

## AIシステム設定

### システムメッセージ

```
あなたは技術文書の翻訳に特化した翻訳アシスタントです。
```

### パラメータ設定

- **temperature**: 0.3 (翻訳の一貫性を重視)
- **max_tokens**: 4000
- 技術文書としての文脈を理解すること

---

## Copilotでの使用方法

### 方法1: Askモードで使用

1. このファイル (`TRANSLATION_PROMPT.md`) を開く
2. 翻訳したいIssueのテキストを選択
3. Copilot Chatで以下のように指示:

```
@workspace /explain このファイルのガイドラインに従って、以下のテキストを日本語に翻訳してください。
翻訳スタイル: バランス型

[翻訳したいテキストをペースト]
```

### 方法2: Agentモードで使用

1. Copilot Chatを開く
2. ファイルを指定して指示:

```
@workspace TRANSLATION_PROMPT.mdのガイドラインに従って、
以下のIssueを日本語に翻訳してください。

タイトル: Add integration tests for DDL migration scripts
本文: The JobRepository class needs to support...
```

### 方法3: ファイル指定で一括翻訳

1. 翻訳対象のMarkdownファイルを開く
2. Copilot Chatで指示:

```
@workspace TRANSLATION_PROMPT.mdのガイドラインを参照して、
現在開いているファイル内のすべてのIssueを翻訳してください。
```

---

## トラブルシューティング

### よくある問題と対処法

#### 問題: コードがバッククォートで囲まれていない

**対処法**: プロンプトに以下を追加
```
重要: クラス名、メソッド名は必ずバッククォート(``)で囲んでください。
```

#### 問題: Issue番号参照がリンクになっていない

**対処法**: 翻訳後に以下の正規表現で置換
```
検索: #(\d+)
置換: [#$1](https://github.com/spring-projects/spring-batch/issues/$1)
```

#### 問題: 翻訳が直訳すぎる/意訳すぎる

**対処法**: 翻訳スタイルを明示的に指定
```
翻訳スタイル: バランス型
原文の意図を正確に伝えながら、自然な日本語を使用してください。
```

---

## 参考情報

### Spring Batch 用語集

- **Job**: ジョブ（バッチ処理の単位）
- **Step**: ステップ（ジョブを構成する処理単位）
- **JobRepository**: ジョブリポジトリ（ジョブの実行情報を管理）
- **JobExecution**: ジョブ実行（ジョブの実行インスタンス）
- **StepExecution**: ステップ実行（ステップの実行インスタンス）
- **ItemReader**: アイテムリーダー（データ読み込み）
- **ItemProcessor**: アイテムプロセッサー（データ処理）
- **ItemWriter**: アイテムライター（データ書き込み）
- **Chunk**: チャンク（一括処理の単位）

### GitHub Issue の構造

- **Title**: タイトル（Issue の概要）
- **Body**: 本文（Issue の詳細説明）
- **Comments**: コメント（Issue に対する議論）
- **Labels**: ラベル（Issue の分類）
- **Milestone**: マイルストーン（対象バージョン）
- **State**: 状態（open/closed）

---

## 更新履歴

- 2025-12-30: 初版作成
  - translator.pyから翻訳プロンプトを抽出
  - Copilot利用方法を追加
  - トラブルシューティングセクションを追加
