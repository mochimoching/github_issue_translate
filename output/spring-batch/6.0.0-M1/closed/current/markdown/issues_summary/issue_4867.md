*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

すべてのリスナーAPIを`org.springframework.batch.core.listener`パッケージに移動し、パッケージ構造を整理しました。

**リスナーとは**: ジョブやステップの実行ライフサイクルの特定のポイント（開始前、完了後、エラー発生時など）でコールバックを受け取るためのインターフェースです。

### v5.2の問題

```
org.springframework.batch.core
├── JobExecutionListener        ← coreパッケージ直下
├── StepExecutionListener       ← coreパッケージ直下
├── ChunkListener               ← coreパッケージ直下
└── listener/                   ← 専用パッケージは存在
    └── (一部のリスナーのみ)
```

## 原因

`core.listener`パッケージは既に存在していましたが、すべてのリスナーAPIが整理されておらず、コアパッケージ直下に散在していました。これは一貫性に欠け、適切な凝集性がありませんでした。

## 対応方針

**コミット**: [90f7398](https://github.com/spring-projects/spring-batch/commit/90f7398222e22aef57b3207be3daa11f0b2fd668)

すべてのリスナーAPIを`core.listener`パッケージに移動しました。

### v6.0の改善されたパッケージ構造

```
org.springframework.batch.core.listener
├── JobExecutionListener       ← 移動
├── StepExecutionListener      ← 移動
├── ChunkListener              ← 移動
├── ItemReadListener
├── ItemProcessListener
├── ItemWriteListener
└── SkipListener
```

### メリット

- リスナーAPIが1箇所に集約
- パッケージの責任が明確
- クラスの発見と理解が容易
