*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobParametersIncrementerを使用する際のジョブパラメータの不正な処理

**Issue番号**: #4910

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-07-16

**ラベル**: type: bug, in: core, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/4910

**関連リンク**:
- Commits:
  - [72cd7bc](https://github.com/spring-projects/spring-batch/commit/72cd7bcbeec3097d2e5828dda6c2daf0b8b41d85)
  - [eb42128](https://github.com/spring-projects/spring-batch/commit/eb42128f448a4417600a96141b4299cbefe95eb5)

## 内容

`JobParametersIncrementer`のコンセプトは、ジョブインスタンスの自然な連続（時間ごと、日ごとなど）がある場合に使用する便利な抽象化です。この抽象化の目標は、ジョブパラメータの初期セットをブートストラップし、フレームワークに連続内の次のインスタンスのパラメータを計算させることです。これは、`JobOperator#startNextInstance(String jobName)`メソッドの初期設計から明確でした（シグネチャにジョブパラメータがないことに注目してください）。このコンセプトは、ユーザーによって一度初期化され、データベースシステムによって自動的に増分される（つまり、ユーザーによってもはや変更されない）データベースシーケンスと似ています。したがって、インクリメンタを使用するときにジョブパラメータを提供することは意味をなしません。

残念ながら、この機能はSpring BatchとSpring Bootのコマンドラインランナーを通じて長年にわたって誤って使用されており、ユーザーが連続間でジョブパラメータをいじっているのを見てきました。これはインクリメンタのコンセプトの本来の意図に反し、課題 [#882](https://github.com/spring-projects/spring-batch/issues/882)、https://github.com/spring-projects/spring-boot/issues/22602、https://github.com/spring-projects/spring-boot/issues/14484 のようないくつかの混乱を招く問題を引き起こしました。もし誰かが連続のロジックを変更し、インスタンス間でジョブパラメータを変更し始めたら、そもそもインクリメンタを使用すべきではありません。

v6はそれを修正する良い機会です。ジョブパラメータインクリメンタがジョブ定義に付加されている場合、次のインスタンスのパラメータはフレームワークによって計算されるべきで、ユーザーによって供給された追加のパラメータは警告とともに無視されるべきです。
