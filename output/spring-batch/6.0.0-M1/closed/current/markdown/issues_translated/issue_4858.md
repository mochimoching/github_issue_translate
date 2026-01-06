*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# ジョブとステップにBean名を使用できる機能を追加

**Issue番号**: #4858

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-03

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4858

**関連リンク**:
- Commits:
  - [bb2440f](https://github.com/spring-projects/spring-batch/commit/bb2440fea3a1a4685acba66261bebd49fa8c382d)

## 内容

v5.2時点で、`AbstractJob`と`AbstractStep`の両方が`BeanNameAware`を実装しています。したがって、重複を避けるために、Bean名をデフォルトのジョブ/ステップ名として使用することが可能です：

```diff
@Bean
public Job job(JobRepository jobRepository, Step step) {
--	return new JobBuilder("job", jobRepository)
++	return new JobBuilder(jobRepository)
                           .start(step)
                           .build();
}
```

もちろん、必要に応じて異なる名前を指定できるように、ジョブ/ステップ名を受け取る現在のコンストラクタは維持されるべきです。

cc @joshlong
