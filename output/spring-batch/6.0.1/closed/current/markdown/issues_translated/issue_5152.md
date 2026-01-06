*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Spring Batch 6マイグレーションガイドのドキュメント誤り

**課題番号**: #5152

**状態**: closed | **作成者**: klyashko | **作成日**: 2025-12-09

**ラベル**: type: documentation

**URL**: https://github.com/spring-projects/spring-batch/issues/5152

**関連リンク**:
- Commits:
  - [c2a5b6f](https://github.com/spring-projects/spring-batch/commit/c2a5b6f50fedb3e4b84c81fa2449b3d5df09c4e0)

## 内容

**バグの説明**
Spring Batch 6マイグレーションガイドのドキュメントには誤りがあります。

**詳細**
ドキュメント：https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide#change-in-the-database-schema

変更前：
```
// v5
JobBuilder jobBuilder = new JobBuilder("myJob", jobRepository);

// v6
JobBuilder jobBuilder = new JobBuilder(jobRepository);
```

期待される変更後：
```
// v5
JobBuilder jobBuilder = new JobBuilder("myJob", jobRepository);

// v6
JobBuilder jobBuilder = new JobBuilder("myJob", jobRepository); // ジョブ名パラメータは不要
```

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-09

ご報告ありがとうございます。これを修正します。

