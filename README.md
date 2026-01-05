# GitHub Issue 翻訳自動化

このプロジェクトは、GitHub issueを自動的に取得し、生成AIを使用して日本語に翻訳するシステムです。

## 機能

- GitHub APIを使用したissueの自動取得（`fetch.py`）
- OpenAI API / Azure OpenAI / Claude APIによる自動翻訳（`translate.py`）
- 翻訳結果の保存とエクスポート（JSON, CSV, Markdown）
- 取得と翻訳の分離による柔軟な運用

## 必要な環境

- Python 3.8以上
- GitHub Personal Access Token (オプション、レート制限緩和のため)
- 生成AI APIキー (OpenAI, Azure OpenAI, または Anthropic Claude)

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の情報を設定:

```env
# GitHub設定
GITHUB_TOKEN=your_github_token_here  # オプション

# AI API設定 (いずれか1つを選択)
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# または Azure OpenAI
# AZURE_OPENAI_API_KEY=your_azure_key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# または Claude
# ANTHROPIC_API_KEY=your_claude_api_key
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# 取得設定
MAX_ISSUES=10  # 取得する最大issue数
ISSUE_STATE=open  # open, closed, all
```

## 使用方法

### 基本的な実行

```powershell
# ステップ1: issueを取得
python fetch.py --milestone "6.0.0" --state closed --max-issues 100

# ステップ2: 取得したissueを翻訳
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style free
```

**注意**: `fetch.py`（issue取得のみ）を使用する場合、AI APIキーは不要です。

## コマンドラインオプション

### fetch.py（Issue取得）のオプション

#### 必須オプション

なし（全てのオプションはデフォルト値を持ちます）

#### オプション一覧

| オプション | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `--max-issues` | 整数 | 100 | 取得する最大issue数を指定 |
| `--state` | 文字列 | open | issueの状態を指定<br>`open`: オープンなissueのみ<br>`closed`: クローズされたissueのみ<br>`all`: すべてのissue |
| `--issue-number` | 整数 | なし | 特定のissue番号を指定して取得 |
| `--milestone` | 文字列 | なし | マイルストーンで絞り込み<br>例: `"6.0.0"`, `"5.0.0-M1"`<br>`"*"`: 任意のマイルストーン<br>`"none"`: マイルストーンなし |
| `--labels` | リスト | なし | ラベルで絞り込み（複数指定可能）<br>例: `enhancement`, `bug` |
| `--max-comments` | 整数 | 20 | 取得する最大コメント数（コメントは常に取得されます） |
| `--output` | 文字列 | 自動生成 | 出力ファイルパス（JSONファイル） |

### translate.py（Issue翻訳）のオプション

#### 必須オプション

| オプション | 型 | 説明 |
|-----------|-----|------|
| `input` | 文字列 | 入力JSONファイルパス（fetch.pyで取得したファイル） |

#### オプション一覧

| オプション | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| `--translation-style` | 文字列 | balanced | 翻訳スタイル<br>`literal`: 直訳（原文に忠実）<br>`free`: 意訳（自然な日本語）<br>`balanced`: バランス型（推奨） |
| `--translate-comments` | フラグ | false | コメントも翻訳する |
| `--max-comments` | 整数 | 20 | 翻訳する最大コメント数 |
| `--output-formats` | リスト | json markdown | 出力形式を指定<br>複数指定可能: `json`, `markdown` |
| `--separate-files` | フラグ | false | issueごとに個別のファイルに保存する |
| `--include-original` | フラグ | false | 元の英語テキストを翻訳結果に含める |
| `--output-dir` | 文字列 | 自動生成 | 出力ディレクトリパス |

### ヘルプの表示

```powershell
# Issue取得のヘルプ
python fetch.py --help

# Issue翻訳のヘルプ
python translate.py --help
```

## 詳細な使用例

### Issue取得の例

```powershell
# 基本的な取得（コメントは自動的に含まれます）
python fetch.py --milestone "6.0.0" --state closed --max-issues 100

# コメント数を制限して取得
python fetch.py --milestone "6.0.0" --state closed --max-comments 50

# 特定のissue番号を取得
python fetch.py --issue-number 5183

# ラベルで絞り込み
python fetch.py --labels enhancement bug --state open --max-issues 20

# 出力先を指定
python fetch.py --milestone "6.0.0" --state closed --output "my_issues.json"
```

### Issue翻訳の例

```powershell
# 基本的な翻訳（バランス型）
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json

# 意訳スタイルで翻訳
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style free

# 直訳スタイルで翻訳
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style literal

# コメントも翻訳
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translate-comments

# 原文も含めて翻訳
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --include-original

# 個別ファイルに分割して保存
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --separate-files

# Markdown形式のみ出力
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --output-formats markdown
```

### 同じissueを複数スタイルで翻訳

```powershell
# 一度取得したissueを異なるスタイルで翻訳
python fetch.py --milestone "6.0.0" --state closed --max-issues 50

# 直訳版を生成
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style literal

# 意訳版を生成
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style free

# バランス型版を生成
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style balanced
```

### マイルストーンで絞り込み

```powershell
# 特定のマイルストーンのissueを取得
python fetch.py --milestone "6.0.0"

# マイルストーン 5.0.0-M1 のissueを取得
python fetch.py --milestone "5.0.0-M1" --state closed

# マイルストーンが設定されているissueを取得
python fetch.py --milestone "*"

# マイルストーンが設定されていないissueを取得
python fetch.py --milestone "none"
```

### ラベルで絞り込み

```powershell
# "bug"ラベルのissueのみ取得
python fetch.py --labels bug

# "enhancement"と"in: core"ラベルの両方を持つissueを取得
python fetch.py --labels enhancement "in: core"

# ラベルとマイルストーンで絞り込み
python fetch.py --milestone "6.0.0" --labels bug --state closed
```

### 複数オプションの組み合わせ

```powershell
# 最新5件のopenなissueを取得
python fetch.py --max-issues 5 --state open

# マイルストーン6.0.0のclosedなissueを意訳で翻訳
python fetch.py --milestone "6.0.0" --state closed
python translate.py output/raw/6.0.0/closed/issues_20251229-223743.json --translation-style free --separate-files

# bugラベルのissueを直訳で翻訳、元の英語も含める
python fetch.py --labels bug
python translate.py output/raw/all/open/issues_20251229-223743.json --translation-style literal --include-original

# 特定のissueをコメント付きで翻訳、全形式で出力
python fetch.py --issue-number 5161 --max-comments 20
python translate.py output/raw/all/open/issues_20251229-223743.json --translate-comments --max-comments 20
```

## 出力

### 取得結果（fetch.py）
- `output/raw/{milestone}/{state}/issues_{YYYYMMDD-HHMMSS}.json` - 取得したissue（JSON形式）

### 翻訳結果（translate.py）

#### 出力ディレクトリ構造

```
output/
├── 6.0.0/                    # マイルストーン名
│   ├── closed/               # issueの状態
│   │   ├── free/             # 翻訳スタイル
│   │   │   └── 20251226-180000/  # 日時
│   │   │       ├── translations.json
│   │   │       ├── translations.csv
│   │   │       ├── translations.md  # 統合ファイル
│   │   │       └── translations/    # 個別ファイル（--separate-files時）
│   │   │           ├── issue_5090.md
│   │   │           └── issue_5093.md
│   │   ├── literal/
│   │   └── balanced/
│   └── open/
├── 5.0.0/
└── all/                      # マイルストーン指定なし
```

#### ファイル形式

- **JSON** (`translations.json`) - プログラムから読み込める構造化データ
- **CSV** (`translations.csv`) - ExcelやGoogle Spreadsheetsで開いて分析可能
- **Markdown** (`translations.md`) - 見やすい形式でissueとその翻訳を表示
  - issue番号の若い順に並んでいます
  - コメント内の `#XXXX` 形式のissue番号は自動的にリンクに変換されます
  - 統合ファイルでは各issueタイトルに `## Issue #XXXX:` が付きます
  - 個別ファイルでは日本語タイトルのみが表示されます
  - `--include-original` を指定すると元の英語テキストが折りたたみ形式で含まれます
  - ウェブブラウザやMarkdownビューアで閲覧可能

## 翻訳スタイルの詳細

### literal（直訳）
- 原文の構造と表現をできるだけ忠実に保つ
- 文字通りの翻訳を優先
- 技術的な正確性を最優先したい場合に使用

### free（意訳）
- 日本語として最も自然で読みやすい表現を使用
- 原文の意図とニュアンスを正確に伝える
- エンドユーザー向けドキュメントに適している

### balanced（バランス型）※デフォルト
- 直訳と意訳のバランスを取る
- 技術的な正確さと読みやすさを両立
- 一般的な技術文書の翻訳に推奨

## AI APIの選択

### OpenAI

`.env`:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

コスト効率が良い: `gpt-4o-mini`  
高品質な翻訳: `gpt-4o`, `gpt-4-turbo`

### Azure OpenAI

`.env`:
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

エンタープライズ利用に推奨。

### Anthropic Claude

`.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

高精度な翻訳: `claude-3-5-sonnet-20241022`  
コスト重視: `claude-3-5-haiku-20241022`

## トラブルシューティング

### APIキーのエラー

```
ValueError: AI APIキーが設定されていません
```

→ `.env`ファイルにAPIキーを設定してください。

### GitHub APIレート制限

```
GitHub API エラー: 403 Client Error
```

→ `.env`に`GITHUB_TOKEN`を設定してレート制限を緩和してください。

### 翻訳エラー

```
翻訳エラー: 401 Unauthorized
```

→ AIサービスのAPIキーと設定を確認してください。

## GitHub Personal Access Tokenの作成方法

1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token" をクリック
4. スコープは `public_repo` のみでOK
5. 生成されたトークンを `.env` の `GITHUB_TOKEN` に設定

## ファイル構成

```
github_issue_translate/
├── fetch.py                # Issue取得スクリプト
├── translate.py            # Issue翻訳スクリプト
├── github_client.py        # GitHub API クライアント
├── translator.py           # AI翻訳モジュール
├── config.py              # 設定管理
├── requirements.txt       # 依存パッケージ
├── .env.example          # 環境変数サンプル
├── README.md             # このファイル
└── output/               # 翻訳結果の出力先
```

## トラブルシューティング

### GitHub APIレート制限
- 認証なし: 60リクエスト/時間
- 認証あり: 5000リクエスト/時間
- Personal Access Tokenの使用を推奨

### AI APIエラー
- APIキーが正しく設定されているか確認
- APIの利用制限・残高を確認
- モデル名が正しいか確認

## ライセンス

MIT License
