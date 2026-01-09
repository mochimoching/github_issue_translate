*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobOperatorTestUtilsがJobBuilderのdeprecated警告を引き起こす

**課題番号**: #5123

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2025-11-27

**ラベル**: type: bug, in: test

**URL**: https://github.com/spring-projects/spring-batch/issues/5123

**関連リンク**:
- Commits:
  - [63a4c13](https://github.com/spring-projects/spring-batch/commit/63a4c136ad0c83e52f5f91a1b5e36c25bc5c6c80)

## 内容

**バグの説明**
`JobOperatorTestUtils`内の`createJob(String jobName)`メソッドで非推奨の`JobBuilder`コンストラクタが使用されているため、警告が発生します。

**再現手順**
https://github.com/spring-projects/spring-framework/actions/runs/12089690095/job/33707730682#step:6:22

