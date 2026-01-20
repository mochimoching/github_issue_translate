*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月18日に生成されました）*

## 課題概要

Issue報告ガイドで提供されているプロジェクトテンプレートをSpring Batch 6に更新する内部タスクです。

**Issue報告ガイドとは**: [ISSUE_REPORTING.md](https://github.com/spring-projects/spring-batch/blob/main/ISSUE_REPORTING.md) ファイルで、Issue報告者が再現可能なサンプルプロジェクトを作成するためのテンプレートとガイドラインを提供しています。

### タスクの内容

1. プロジェクトテンプレートの依存関係をSpring Batch 5からSpring Batch 6に更新
2. 更新したZIPファイルをアップロード

### 将来的な改善案

毎回ZIPファイルを更新・アップロードするのではなく、より良い方法を検討：
- ソース管理下のプロジェクトテンプレートをIssue報告者がクローンできるようにする
- GitHubのテンプレートリポジトリ機能の活用（ただしSpring Projectsでは多数のテンプレートリポジトリが管理困難になるため採用見送り）

## 原因

（タスクのため、バグではありません）

Spring Batch 6.0のリリースに伴い、Issue報告用のプロジェクトテンプレートの更新が必要になりました。

## 対応方針

diffファイルは存在しません。

内部チーム（for-internal-team）向けのタスクとしてラベル付けされています。

| 項目 | 内容 |
|------|------|
| ラベル | type: task, status: for-internal-team |
| 担当 | Spring Batchメンテナー |
