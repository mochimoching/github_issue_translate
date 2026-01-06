*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

パーティショニング関連のコアAPI（`Partitioner`、`StepExecutionAggregator`、`PartitionStep`等）を`support`パッケージから`org.springframework.batch.core.partition`直下に移動するリファクタリングです。

**パーティショニングとは**: 大量データを複数のパーティション（分割）に分けて並列処理する機能です。各パーティションを異なるスレッドやノードで処理することで、処理時間を大幅に短縮できます。

### v5.2のパッケージ構造

```
org.springframework.batch.core.partition
├── support/                          ← 不適切な配置
│   ├── Partitioner                  ← コアインターフェース
│   ├── StepExecutionAggregator      ← コアインターフェース
│   ├── PartitionStep                ← コアクラス
│   └── SimplePartitioner            ← サポート実装
```

## 原因

これらのクラスは`support`パッケージに配置されていましたが、実際には「サポート」実装ではなくパーティショニング機能のコアAPIです。`support`は通常、補助的な実装クラスを配置する場所であり、主要なインターフェースやクラスを配置するのは不適切でした。

## 対応方針

**コミット**: [08c4cb1](https://github.com/spring-projects/spring-batch/commit/08c4cb16b854b773f974eeb2073a04c56a0eb6ab)

コアAPIを`partition`直下に移動し、サポート実装のみを`support`に残しました。

### v6.0の改善されたパッケージ構造

```
org.springframework.batch.core.partition
├── Partitioner                      ← コアインターフェース
├── StepExecutionAggregator         ← コアインターフェース
├── PartitionStep                   ← コアクラス
└── support/
    └── SimplePartitioner           ← サポート実装
```

### メリット

- パッケージ構造がAPI階層を正確に反映
- コアAPIとサポート実装の区別が明確
- 開発者がインポートすべきクラスを見つけやすい
