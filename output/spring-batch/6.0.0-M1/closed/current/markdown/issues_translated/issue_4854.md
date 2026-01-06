*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobRegistryからJobFactoryの使用を削除

**Issue番号**: #4854

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-02

**ラベル**: in: core, type: enhancement, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4854

**関連リンク**:
- Commits:
  - [ce5ef2f](https://github.com/spring-projects/spring-batch/commit/ce5ef2f8b69ecd3bfe81ce218284b2710706a101)
  - [a7f090a](https://github.com/spring-projects/spring-batch/commit/a7f090a45d1aa055e3bdfbc4fdfd06d02ed6d0ac)

## 内容

課題 [#4847](https://github.com/spring-projects/spring-batch/issues/4847) に沿って、この課題は`JobRegistry`（および`MapJobRegistry`）から`JobFactory`の使用を削除するためのものです。

API変更は以下の通りです：

```diff
-- void register(JobFactory jobFactory) throws DuplicateJobException;
++ void register(Job job) throws DuplicateJobException;
```

`JobFactory`は公開（ただし「ユーザー向け」ではない）APIではありませんが、ユーザー向けAPIで依然として使用されています。物事を簡素化するために、レジストリへのジョブ登録はファクトリを介して行うべきではありません。
