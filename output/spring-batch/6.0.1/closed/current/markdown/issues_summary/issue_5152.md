*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月9日に生成されました）*

## 課題概要

Spring Batch 6.0 マイグレーションガイドに記載されている `JobParametersInvalidException` クラスが、実際の6.0.0リリースでは `InvalidJobParametersException` にリネームされていたため、ドキュメントと実装に不整合があった問題です。

**マイグレーションガイドとは**: メジャーバージョンアップ時に、既存のコードを新しいバージョンに移行するための手順やAPIの変更点をまとめたドキュメントです。

### 問題の状況

| ドキュメントの記載 | 実際のクラス名（6.0.0） |
|-------------------|----------------------|
| `JobParametersInvalidException` | `InvalidJobParametersException` |

マイグレーションガイドには「`JobParametersInvalidException` が新しいパッケージに移動した」と記載されていましたが、実際には6.0.0-M3から6.0.0の間でクラス名自体が `InvalidJobParametersException` にリネームされていました。

## 原因

Issue [#5013](https://github.com/spring-projects/spring-batch/issues/5013) でクラス名が変更されたが、マイグレーションガイドの更新が漏れていました。

## 対応方針

### 変更内容

マイグレーションガイドが修正され、正しいクラス名 `InvalidJobParametersException` が記載されるようになりました。

---

**関連リンク**:
- [Issue #5152](https://github.com/spring-projects/spring-batch/issues/5152)
- [Spring Batch 6.0 Migration Guide](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide)
