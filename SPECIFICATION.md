# GitHub Issue 翻訳自動化システム - 仕様書

## 概要

GitHub issueを自動的に取得し、AI APIを使用して日本語に翻訳するPythonアプリケーション。

**バージョン**: 2.1  
**作成日**: 2025年12月26日  
**最終更新**: 2026年1月6日

### 主要な変更点（v2.0）

- **コマンド分離**: Issue取得（`fetch.py`）と翻訳（`translate.py`）を完全に分離
- **再利用性向上**: 一度取得したissueを複数の翻訳スタイルで処理可能
- **コスト削減**: GitHub APIとAI APIの呼び出しを最小化
- **柔軟性向上**: 取得と翻訳で異なるオプション設定が可能
- **シンプル化**: 統合版（main.py）を削除し、責務を明確化

---

## 1. システム構成

### 1.1 アーキテクチャ

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────┐
│  fetch.py   │────→│ {repo}/{milestone}/  │────→│translate.py │
│(Issue取得)  │     │ {state}/current/     │     │  (翻訳)     │
└──────┬──────┘     │ json/issues.json     │     └──────┬──────┘
       │            └──────────────────────┘            │
       ├─→ ┌──────────────────┐                        │
       │   │ github_client.py │                        │
       │   └──────────────────┘                        │
       │                                                │
       └─→ ┌──────────┐      ┌──────────────┐←────────┘
           │config.py │      │translator.py │
           └──────────┘      └──────────────┘
```

### 1.2 ファイル構成

```
github_issue_translate/
├── fetch.py                       # Issue取得スクリプト
├── translate.py                   # Issue翻訳スクリプト
├── config.py                      # 設定管理
├── github_client.py               # GitHub API クライアント
├── translator.py                  # AI翻訳エンジン
├── requirements.txt               # Python依存パッケージ
├── .env                           # 環境変数（非公開）
├── .env.example                   # 環境変数サンプル
├── README.md                      # プロジェクト説明
├── SPECIFICATION.md               # 本仕様書
├── TRANSLATION_GUIDELINE.md       # 翻訳ガイドライン（Copilot用）
├── SUMMARY_GUIDELINE.md           # 要約ガイドライン（Copilot用）
├── prompts/                       # 翻訳プロンプトテンプレート（未使用）
└── output/                        # 出力ディレクトリ
    ├── {repo}/                    # リポジトリ名（例: spring-batch）
    │   └── {milestone}/           # 取得したissue
    │       └── {state}/
    │           └── current/       # 固定ディレクトリ名
    │               ├── json/
    │               │   └── issues.json
    │               └── markdown/
    │                   ├── issues.md
    │                   └── issues/
    │                       ├── issue_XXXX.md
    │                       └── ...
    └── {milestone}/               # 翻訳結果（リポジトリ名なし）
        └── {state}/
            └── {style}/           # literal/free/balanced
                └── current/       # 固定ディレクトリ名
                    ├── translations.md
                    ├── translations.json
                    ├── translations.csv
                    └── translations/  # --separate-files時
                        ├── issue_XXXX.md
                        └── ...
```

---

## 2. 機能仕様

### 2.1 Issue取得機能

**モジュール**: `github_client.py`

#### 2.1.1 対象リポジトリ
- **リポジトリ**: `spring-projects/spring-batch`
- **API**: GitHub REST API v3

#### 2.1.2 取得可能な情報

| データ項目 | 説明 | 型 |
|-----------|------|-----|
| `number` | Issue番号 | 整数 |
| `title` | タイトル | 文字列 |
| `state` | 状態 (open/closed) | 文字列 |
| `author` | 作成者 | 文字列 |
| `created_at` | 作成日時 | ISO 8601文字列 |
| `updated_at` | 更新日時 | ISO 8601文字列 |
| `url` | Issue URL | 文字列 |
| `labels` | ラベルリスト | 文字列配列 |
| `body` | 本文 | 文字列 |
| `milestone` | マイルストーン | 文字列 or null |
| `comments` | コメント一覧 | オブジェクト配列 |

#### 2.1.3 フィルタリングオプション

| フィルタ | パラメータ | 値 | 説明 |
|---------|-----------|-----|------|
| 状態 | `--state` | `open`/`closed`/`all` | Issue状態で絞り込み |
| マイルストーン | `--milestone` | 文字列/`*`/`none` | マイルストーンで絞り込み |
| ラベル | `--labels` | 文字列リスト | 指定ラベルを持つIssueのみ |
| Issue番号 | `--issue-number` | 整数 | 特定のIssueを指定 |
| 最大件数 | `--max-issues` | 整数 (デフォルト: 100) | 取得する最大件数 |

#### 2.1.4 レート制限対応
- **認証なし**: 60リクエスト/時
- **認証あり**: 5,000リクエスト/時
- GitHub Personal Access Token使用を推奨

### 2.2 翻訳機能

**モジュール**: `translator.py`

#### 2.2.1 サポートAIプロバイダー

| プロバイダー | モデル例 | 必須環境変数 |
|-------------|---------|-------------|
| **OpenAI** | `gpt-4o-mini`, `gpt-4o` | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| **Azure OpenAI** | ユーザー定義 | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT` |
| **Anthropic Claude** | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |

#### 2.2.2 翻訳スタイル

| スタイル | 説明 | 特徴 | 用途 |
|---------|------|------|------|
| `literal` | 直訳 | 原文の構造を忠実に保つ | 厳密な正確性が必要な場合 |
| `free` | 意訳 | 自然な日本語表現を優先 | 読みやすさ重視 |
| `balanced` | バランス型（推奨） | 正確性と読みやすさの両立 | 一般的な用途 |

#### 2.2.3 翻訳処理フロー

```
1. Issue取得
   ↓
2. タイトル翻訳
   - Issue番号プレフィックス削除
   - コードフォーマットなし
   ↓
3. 本文翻訳
   - マークダウン記法保持
   - コードブロック保持
   - クラス名/メソッド名をバッククォートで囲む
   - Issue参照(#XXXX)をリンクに変換
   ↓
4. コメント翻訳（オプション）
   - 最大件数制限あり
   - 各コメントを個別に翻訳
   ↓
5. 結果保存
```

#### 2.2.4 翻訳プロンプトルール

**共通要件**:
- Spring Batch等の固有名詞は保持
- マークダウン記法は保持
- コードブロックは保持
- 技術用語は適切な日本語訳を使用
  - `issue` → `課題`
  - `feature` → `機能`
  - `bug` → `バグ`

**コードフォーマットルール**:
- タイトル: コードフォーマットなし
- 本文: クラス名、メソッド名、変数名、ファイル名をバッククォート(``)で囲む
  - 例: `JobRepository class` → `` `JobRepository`クラス ``
  - 例: `execute method` → `` `execute`メソッド ``

#### 2.2.5 API設定

| 項目 | 値 |
|------|-----|
| `temperature` | 0.3 (翻訳の一貫性重視) |
| `max_tokens` | 4000 |
| `system_message` | "あなたは技術文書の翻訳に特化した翻訳アシスタントです。" |

### 2.3 出力機能

#### 2.3.1 出力形式

| 形式 | ファイル名 | エンコーディング | 用途 |
|------|-----------|----------------|------|
| **JSON** | `translations.json` | UTF-8 | データ交換、API連携 |
| **CSV** | `translations.csv` | UTF-8 with BOM | Excel、スプレッドシート |
| **Markdown** | `translations.md` | UTF-8 | ドキュメント、可読性 |

#### 2.3.2 出力ディレクトリ構造

```
output/
└── {milestone}/           # 例: "6.0.0"
    └── {state}/           # 例: "closed"
        └── {style}/       # 例: "free"
            └── {timestamp}/  # 例: "20251226-190809"
                ├── translations.md
                ├── translations.json
                ├── translations.csv
                └── translations/  # --separate-files指定時
                    ├── issue_4289.md
                    ├── issue_4732.md
                    └── ...
```

#### 2.3.3 Markdown出力仕様

**統合ファイル** (`translations.md`):
```markdown
# GitHub Issues 翻訳結果

生成日時: YYYY年MM月DD日 HH:MM:SS
取得件数: XX件

---

## Issue #XXXX: タイトル（日本語）

**元のタイトル**: Title (English)  # --include-original時のみ
**状態**: open/closed | **作成者**: username | **作成日**: YYYY-MM-DD
**ラベル**: label1, label2, ...
**URL**: https://github.com/...

### 内容

本文（日本語）

<details>
<summary>元の内容（英語）</summary>  # --include-original時のみ

本文（英語）

</details>

### コメント  # --translate-comments時のみ

#### コメント 1 by username

コメント本文（日本語）

<details>
<summary>元のコメント（英語）</summary>  # --include-original時のみ

コメント本文（英語）

</details>

---
```

**個別ファイル** (`issue_XXXX.md`): `--separate-files`指定時
- 上記と同様の構造
- Issue単位で1ファイル

#### 2.3.4 JSON出力仕様

```json
[
  {
    "number": 4289,
    "title": "Add integration tests for DDL migration scripts",
    "title_ja": "DDLマイグレーションスクリプトの統合テストを追加",
    "state": "closed",
    "author": "fmbenhassine",
    "created_at": "2023-02-08T10:30:00Z",
    "updated_at": "2023-02-15T14:20:00Z",
    "url": "https://github.com/spring-projects/spring-batch/issues/4289",
    "labels": ["type: task", "in: core"],
    "milestone": "6.0.0",
    "body": "Original body text...",
    "body_ja": "翻訳された本文...",
    "comments": [
      {
        "author": "baezzys",
        "created_at": "2023-02-08T11:00:00Z",
        "body": "Original comment...",
        "body_ja": "翻訳されたコメント..."
      }
    ],
    "comments_ja": [...]  # --translate-comments時のみ
  }
]
```

---

## 3. コマンドライン仕様

### 3.1 コマンド種別

本システムは2つのコマンドを提供します：

| コマンド | 用途 | AI APIキー |
|---------|------|----------|
| `fetch.py` | GitHub issueの取得 | 不要 |
| `translate.py` | 取得済みissueの翻訳 | 必要 |

### 3.2 fetch.py (Issue取得)

#### 3.2.1 基本構文

```bash
python fetch.py [OPTIONS]
```

#### 3.2.2 オプション一覧

| オプション | 型 | デフォルト | 必須 | 説明 |
|-----------|-----|-----------|------|------|
| `--max-issues` | 整数 | 100 | ❌ | 取得する最大Issue数 |
| `--state` | 文字列 | `open` | ❌ | Issue状態 (`open`/`closed`/`all`) |
| `--issue-number` | 整数 | - | ❌ | 特定Issue番号を指定 |
| `--milestone` | 文字列 | - | ❌ | マイルストーンで絞り込み |
| `--labels` | リスト | - | ❌ | ラベルで絞り込み（複数可） |
| `--max-comments` | 整数 | 20 | ❌ | 取得する最大コメント数（コメントは常に取得） |
| `--output` | 文字列 | 自動生成 | ❌ | 出力ファイルパス |

#### 3.2.3 使用例

```bash
# 基本実行（最新100件のopenなIssue）
python fetch.py
# 出力: output/spring-batch/all/open/current/json/issues.json

# マイルストーン6.0.0のclosedなIssueを100件取得
python fetch.py --milestone "6.0.0" --state closed --max-issues 100
# 出力: output/spring-batch/6.0.0/closed/current/json/issues.json

# 特定のIssue番号を指定
python fetch.py --issue-number 5183
# 出力: output/spring-batch/all/open/current/json/issues.json

# ラベルで絞り込み（複数指定）
python fetch.py --labels enhancement bug --max-issues 20
# 出力: output/spring-batch/all/open/current/json/issues.json

# 出力パスを指定（JSONのみ、Markdownは自動配置）
python fetch.py --milestone "6.0.0" --state closed --output "my_issues.json"
# JSON: my_issues.json
# Markdown: output/spring-batch/6.0.0/closed/current/markdown/
```

### 3.3 translate.py (Issue翻訳)

#### 3.3.1 基本構文

```bash
python translate.py INPUT_FILE [OPTIONS]
```

#### 3.3.2 オプション一覧

| オプション | 型 | デフォルト | 必須 | 説明 |
|-----------|-----|-----------|------|------|
| `input` | 文字列 | - | ✅ | 入力JSONファイルパス |
| `--translation-style` | 文字列 | `balanced` | ❌ | 翻訳スタイル (`literal`/`free`/`balanced`) |
| `--translate-comments` | フラグ | `false` | ❌ | コメントも翻訳 |
| `--max-comments` | 整数 | 20 | ❌ | 翻訳する最大コメント数 |
| `--output-formats` | リスト | `json csv markdown` | ❌ | 出力形式（複数可） |
| `--separate-files` | フラグ | `false` | ❌ | Issue毎に個別ファイル作成 |
| `--include-original` | フラグ | `false` | ❌ | 原文を含める |
| `--output-dir` | 文字列 | 自動生成 | ❌ | 出力ディレクトリパス |

#### 3.3.3 使用例

```bash
# 基本実行（バランス型翻訳）
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json
# 出力: output/6.0.0/closed/balanced/current/

# コメント含めて意訳スタイルで翻訳、原文も含める
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json --translate-comments --translation-style free --include-original
# 出力: output/6.0.0/closed/free/current/

# Issue毎に個別ファイルで保存
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json --separate-files
# 出力: output/6.0.0/closed/balanced/current/translations/ (個別ファイル)

# Markdown形式のみ出力
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json --output-formats markdown

# 出力ディレクトリを指定
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json --output-dir "output/custom_dir"
```

### 3.4 ワークフロー例

```bash
# ステップ1: Issue取得
python fetch.py --milestone "6.0.0" --state closed --max-issues 100
# 出力: output/spring-batch/6.0.0/closed/current/json/issues.json

# ステップ2: 意訳スタイルで翻訳
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json --translation-style free
# 出力: output/6.0.0/closed/free/current/

# ステップ3: 同じIssueを直訳スタイルで翻訳（再利用）
python translate.py output/spring-batch/6.0.0/closed/current/json/issues.json --translation-style literal
# 出力: output/6.0.0/closed/literal/current/
```

---

## 4. 環境変数仕様

### 4.1 必須環境変数

最低1つのAIプロバイダー設定が必要。

### 4.2 環境変数一覧

#### 4.2.1 GitHub設定

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `GITHUB_TOKEN` | ❌ | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |

#### 4.2.2 OpenAI設定

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `OPENAI_API_KEY` | ✅* | OpenAI APIキー | `sk-xxxxxxxxxxxx` |
| `OPENAI_MODEL` | ❌ | 使用モデル | `gpt-4o-mini` |

*OpenAI使用時のみ必須

#### 4.2.3 Azure OpenAI設定

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `AZURE_OPENAI_API_KEY` | ✅* | Azure OpenAI APIキー | `xxxxxxxxxxxx` |
| `AZURE_OPENAI_ENDPOINT` | ✅* | エンドポイントURL | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | ✅* | デプロイメント名 | `gpt-4o-deployment` |
| `AZURE_OPENAI_API_VERSION` | ❌ | APIバージョン | `2024-02-15-preview` |

*Azure OpenAI使用時のみ必須

#### 4.2.4 Anthropic Claude設定

| 変数名 | 必須 | 説明 | 例 |
|--------|------|------|-----|
| `ANTHROPIC_API_KEY` | ✅* | Anthropic APIキー | `sk-ant-xxxxxxxxxxxx` |
| `ANTHROPIC_MODEL` | ❌ | 使用モデル | `claude-sonnet-4-20250514` |

*Claude使用時のみ必須

#### 4.2.5 アプリケーション設定

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|-----------|------|
| `MAX_ISSUES` | ❌ | `100` | 取得する最大Issue数 |
| `ISSUE_STATE` | ❌ | `open` | Issue状態 |
| `MAX_COMMENTS` | ❌ | `20` | 取得する最大コメント数 |

### 4.3 .envファイル例

```env
# GitHub設定
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# AI API設定（いずれか1つを選択）

# OpenAI
# OPENAI_API_KEY=sk-xxxxxxxxxxxx
# OPENAI_MODEL=gpt-4o-mini

# Azure OpenAI
# AZURE_OPENAI_API_KEY=xxxxxxxxxxxx
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=gpt-4o-deployment

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# 取得設定
MAX_ISSUES=100
ISSUE_STATE=open
MAX_COMMENTS=20
```

---

## 5. エラーハンドリング

### 5.1 エラー種別

| エラー種別 | 原因 | 対処 |
|-----------|------|------|
| **設定エラー** | AI APIキー未設定 | `.env`ファイルを確認 |
| **GitHub APIエラー** | レート制限超過 | GitHub Token設定、または時間をおいて再実行 |
| **翻訳エラー** | AI API呼び出し失敗 | APIキーとネットワーク接続を確認 |
| **ファイルI/Oエラー** | 出力ディレクトリ作成失敗 | 書き込み権限を確認 |

### 5.2 エラーメッセージ

```python
# 設定エラー
"AI APIキーが設定されていません。.envファイルにOPENAI_API_KEY、AZURE_OPENAI_API_KEY、またはANTHROPIC_API_KEYを設定してください。"

# 翻訳エラー（本文に表示）
"[翻訳エラー: {エラー詳細}]"
```

---

## 6. 依存パッケージ

### 6.1 requirements.txt

```txt
requests>=2.31.0
python-dotenv>=1.0.0
openai>=1.3.0
anthropic>=0.7.0
```

### 6.2 Python要件

- **Python バージョン**: 3.8以上推奨
- **OS**: Windows, Linux, macOS

---

## 7. パフォーマンス仕様

### 7.1 処理時間目安

| 処理内容 | 件数 | 目安時間 |
|---------|------|---------|
| Issue取得のみ | 10件 | 2-5秒 |
| Issue + 翻訳 | 10件 | 30-60秒 |
| Issue + 翻訳 + コメント | 10件 | 60-120秒 |

※ネットワーク速度とAI APIのレスポンス時間に依存

### 7.2 コスト目安

**OpenAI (gpt-4o-mini)**:
- 入力: $0.15 / 1M tokens
- 出力: $0.60 / 1M tokens
- 1 Issue (平均): 約500-1000 tokens
- 10 Issues: 約$0.01-0.02

**Anthropic Claude (claude-sonnet-4)**:
- 入力: $3.00 / 1M tokens
- 出力: $15.00 / 1M tokens
- 10 Issues: 約$0.10-0.20

---

## 8. セキュリティ

### 8.1 機密情報管理

- `.env`ファイルは`.gitignore`で除外
- APIキーはハードコードしない
- GitHub Tokenは最小限の権限(`public_repo`)のみ

### 8.2 推奨設定

```bash
# .gitignoreに以下を追加
.env
__pycache__/
*.pyc
output/
```

---

## 9. 制限事項

### 9.1 技術的制限

- GitHub API レート制限: 認証なし 60req/h、認証あり 5000req/h
- AI API トークン制限: 各プロバイダーのmax_tokens制限に依存
- 非常に長いIssue本文は切り捨てられる可能性がある

### 9.2 機能的制限

- 添付ファイル（画像等）の翻訳は非対応
- リアルタイム翻訳は非対応（バッチ処理のみ）
- 翻訳品質はAIモデルに依存

---

## 10. 今後の拡張予定

### 10.1 予定機能

- [ ] GitHub Models (OpenAI互換) サポート追加
- [ ] 翻訳キャッシュ機能（同じIssueの再翻訳を避ける）
- [ ] 翻訳品質評価機能
- [ ] WebUIフロントエンド
- [ ] マルチリポジトリ対応

### 10.2 改善予定

- [ ] 並列翻訳処理によるパフォーマンス向上
- [ ] 翻訳プロンプトの最適化
- [ ] エラーリトライ機構

---

## 付録A: 用語集

| 用語 | 説明 |
|------|------|
| **Issue** | GitHub上の課題・要望・バグ報告 |
| **Milestone** | Issueをグループ化するバージョン管理単位 |
| **Label** | Issueの分類タグ |
| **Personal Access Token** | GitHub APIアクセス用の認証トークン |
| **直訳 (literal)** | 原文の構造を保った翻訳 |
| **意訳 (free)** | 意味を重視した自然な翻訳 |

---

## 付録B: トラブルシューティング

### B.1 よくある問題

**Q: 翻訳結果が空白になる**  
A: AI APIキーが正しく設定されているか確認してください。

**Q: GitHub APIエラーが発生する**  
A: レート制限に達している可能性があります。GITHUB_TOKENを設定するか、時間をおいて再試行してください。

**Q: マークダウンのフォーマットが崩れる**  
A: `--include-original`オプションを使用して原文と比較してください。AI翻訳の品質に依存します。

**Q: コメントが翻訳されない**  
A: `--translate-comments`フラグを指定してください。

---

**更新履歴**:
- 2026-01-06: v2.1 - 出力ディレクトリをcurrentに統一、TRANSLATION_GUIDELINE.md/SUMMARY_GUIDELINE.md追加
- 2025-12-29: v2.0 - コマンド分離、main.py削除
- 2025-12-26: v1.0 - 初版作成
