*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# コアAPIの簡素化

**Issue番号**: #4847

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-23

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4847

**関連リンク**:
- Commits:
  - [c872a12](https://github.com/spring-projects/spring-batch/commit/c872a12ad5fdc191a2637ed04775160f8fe7632e)
  - [bfe487c](https://github.com/spring-projects/spring-batch/commit/bfe487ccccfd2b5d7f82b07386094fdaaddd06c1)
  - [bcf4f72](https://github.com/spring-projects/spring-batch/commit/bcf4f724addc96c5beed2447ad9423008a3d6da8)

## 内容

この課題は、一般的なSpring Batchアプリケーションのために、APIの簡素化と縮小を試みるものです。長年にわたりコミュニティからフィードバックを収集してきましたが、共通の問題点は以下の通りです：

### APIが大きすぎて圧倒される

これは過去に何度も指摘されてきました（課題 [#3242](https://github.com/spring-projects/spring-batch/issues/3242)、課題 [#2901](https://github.com/spring-projects/spring-batch/issues/2901)）。長年にわたり、実質的な付加価値のない偶発的な複雑性が多数追加されてきました。典型的な例は、`JobRegistry`でのジョブ名の衝突を避けるために`@EnableBatchProcessing(modular = true)`を通じてモジュール性をサポートすることです。この機能に必要なクラスとインターフェースの量（`JobFactory`、`ApplicationContextFactory`、`ApplicationContextJobFactory`、`ReferenceJobFactory`、`AbstractApplicationContextFactory`（2つの拡張を含む）、`JobLoader`、`JobFactoryRegistrationListener`など）は、実際の利益を正当化しません。これは`GroupAwareJob`を活用するか、`namespace.jobName`のような単純な命名規則を使用することで、ユーザーに任せることができたはずです。

### 一般的なアプリケーションで多くのBeanと設定を定義する必要がある

コアインフラストラクチャコンポーネントからカスタムスコープ、バッチアーティファクトまで、シンプルなジョブを実行するために必要なBeanの数は圧倒的です。例えば、ジョブを実行するためのエントリーポイントは2つあります：`JobOperator#start`と`JobLauncher#run`で、異なるメソッドシグネチャを持っています。`JobOperator`で十分であり、ジョブを実行するだけの関数型インターフェース（おそらくジョブを停止するための別のインターフェースなど）を持つ必要はありません。`JobLauncher`は不必要な複雑性の例です（正当な理由でBatch JSRには保持されませんでした）。

`JobRepository`と`JobExplorer`も同様のケースです。課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824) はこれら2つのBeanに関する混乱を詳細に説明しています。`JobRepository`なしでSpring Batchアプリケーションを持つことはほぼ不可能です（メタデータを探索するためのツールアプリでない限り）。したがって、`JobRepository`に*加えて*`JobExplorer`を定義する必要があるのは直感に反しています。ちなみに、`JobExplorer`のコンセプトも不必要な複雑性の別の例です（参考までに、これもBatch JSRには保持されませんでした）。

### 同じことを行う複数の方法があり混乱を招く

いくつかの例：

- `JobRegistry`を設定する方法は少なくとも3つあります：`JobRegistryBeanPostProcessor`（最近`JobRegistrySmartInitializingBean`に置き換えられた）、`AutomaticJobRegistrar`、手動ジョブ登録。
- ジョブを起動する方法は2つあります：`JobLauncher`または`JobOperator`を使用し、それぞれ独自の設定セットと異なるメソッドシグネチャを持っています。

理想的には、物事を行う方法は1つだけであるべきです。

これらの問題のいくつかはv5.0で対処されました（`JobBuilderFactory`、`StepBuilderFactory`、その他のAPIの削除など）が、まだ一部の重複した機能があります。次のメジャーバージョンは、これらの問題に対処する良い機会だと考えています。
