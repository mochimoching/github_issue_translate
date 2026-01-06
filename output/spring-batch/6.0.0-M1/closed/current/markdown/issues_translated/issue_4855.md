*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# MapJobRegistryをアプリケーションコンテキストで定義されたジョブを自動登録できるように改善

**Issue番号**: #4855

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4855

**関連リンク**:
- Commits:
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

## 内容

v5.2時点では、`JobOperator`で使用できるようにする前に、別のコンポーネント（Beanポストプロセッサ、スマート初期化Beanなど）でジョブレジストリを設定する必要があります。

この機能要求は、`MapJobRegistry`をアプリケーションコンテキストで定義されたジョブを自動登録できるように改善することです。これにより、レジストリを設定するための別個のコンポーネントが不要になり、設定が簡素化されます。これは`MapJobRegistry`を拡張する`SmartMapJobRegistry`を作成することで実現できますが、課題 [#4847](https://github.com/spring-projects/spring-batch/issues/4847) に沿って物事をシンプルに保ち、`MapJobRegistry`自体を`SmartInitializingSingleton`にします。

アプリケーションコンテキストの外部で定義された他のジョブは、ユーザーが手動で登録できます（以前と同様）。
