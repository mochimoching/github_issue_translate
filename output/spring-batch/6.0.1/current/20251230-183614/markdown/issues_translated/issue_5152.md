# "Spring Batch 6.0 Migration Guide"で言及されているクラスJobParametersInvalidExceptionが6.0.0で利用できない

**Issue番号**: #5152

**状態**: closed | **作成者**: sebeichholz | **作成日**: 2025-12-09

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5152

## 内容

[Spring Batch 6.0 Migration Guide](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide)には、クラス**JobParametersInvalidException**が新しいパッケージに移動されたと記載されています。

このクラスは6.0.0-M3には存在しましたが、6.0.0では"InvalidJobParametersException"に名前が変更されたようです。

したがって、Migration Guideを更新すべきかもしれません。ありがとうございます!

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-12-10

この課題を報告していただきありがとうございます! 確かに、そのクラスは課題 [#5013](https://github.com/spring-projects/spring-batch/issues/5013) の一部として名前が変更されました。

それに応じてマイグレーションガイドを修正しました。

