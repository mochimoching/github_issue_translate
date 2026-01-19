*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

## 課題概要

Spring Batchのドキュメント（`whatsnew.adoc`）およびテストメソッドにタイポ（誤字）があるという軽微な問題です。

### 誤字の内容

| 誤 | 正 | 箇所 |
|---|---|------|
| `faultToleranChunkOrientedStep` | `faultToleran**t**ChunkOrientedStep` | テストメソッド名、ドキュメント |
| `nonRetrybaleExceptions` | `nonRetry**ab**leExceptions` | テストメソッド名、ドキュメント |

### 修正対象

1. **whatsnew.adoc**: Spring Batch 6.0の新機能を説明するドキュメント
2. **統合テスト**: `ChunkOrientedStep`関連のテストクラス

## 原因

単純なタイポ（スペルミス）です。

## 対応方針

**注意**: このIssueにはdiffファイルが存在しませんが、Issue内でPR #5206によって修正されたことが記載されています。

### 修正内容

[PR #5206](https://github.com/spring-projects/spring-batch/pull/5206)において、以下の修正が行われました：

1. `faultToleranChunkOrientedStep` → `faultTolerantChunkOrientedStep`
   - 「t」が欠落していた

2. `nonRetrybaleExceptions` → `nonRetryableExceptions`
   - 「a」と「b」の順序が逆になっていた

### 対象ファイル

- `spring-batch-docs/src/main/asciidoc/whatsnew.adoc`
- テストクラス内のメソッド名

この修正は、コードの動作には影響しませんが、ドキュメントの可読性とコードの一貫性を向上させます。
