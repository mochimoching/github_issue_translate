*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# 現代的なコマンドラインバッチオペレーターの導入

**Issue番号**: #4899

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-04

**ラベル**: type: feature, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4899

**関連リンク**:
- Commits:
  - [e6a8088](https://github.com/spring-projects/spring-batch/commit/e6a80889cb74409105e5df4fd092ff52f994b527)

## 内容

Spring Batchはバージョン1から`CommandLineJobRunner`を提供してきました。このランナーは長年にわたりその目的をよく果たしてきましたが、拡張性とカスタマイズに関してはいくつかの制限を示し始めました。静的初期化、オプションとパラメータの処理方法が非標準、拡張性の欠如など、課題 [#1309](https://github.com/spring-projects/spring-batch/issues/1309) や課題 [#1666](https://github.com/spring-projects/spring-batch/issues/1666) のような多くの問題が報告されています。

さらに、これらすべての問題により、そのランナーをSpring Bootで再利用することが不可能になり、両プロジェクトでコードが重複し、多くのユーザーを混乱させるジョブパラメータインクリメンタの動作の違いのような動作の乖離が生じました。

この課題の目標は、カスタマイズ可能で拡張可能で、Spring Batch 6で導入された新しい変更に対応した現代版の`CommandLineJobRunner`を作成することです。
