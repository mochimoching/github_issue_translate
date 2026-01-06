*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# JobRepositoryをJobExplorerの拡張とする

**Issue番号**: #4824

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-05

**ラベル**: in: core, type: enhancement, api: deprecation

**URL**: https://github.com/spring-projects/spring-batch/issues/4824

**関連リンク**:
- Commits:
  - [b8c93d6](https://github.com/spring-projects/spring-batch/commit/b8c93d677ed86130262042fb8565ce30816c2270)

## 内容

v5.2時点で、`JobRepository`と`JobExplorer`には、異なるシグネチャ/名前で同じことを行う類似/同一のメソッドがあります（つまり、重複した実装）。以下にいくつかの例を示します：

| JobRepository | JobExplorer |
|--------|--------|
| findJobExecutions | getJobExecutions |
| getLastJobExecution | getLastJobExecution |
| getJobNames | getJobNames |
| getJobInstance | getJobInstance |
| findJobInstancesByName | findJobInstancesByJobName |

重複した実装を維持することは明らかに理想的ではありません。さらに、`JobExplorer`は`JobRepository`の読み取り専用版として設計されているため、技術的には`JobRepository`を`JobExplorer`の拡張とすることができます。

最終的に、これによりバッチ設定もユーザーにとって簡単になります。`JobRepository`を設定すれば、ほぼ常に必要となる追加のBean（`JobExplorer`）を設定する必要がなくなります。
