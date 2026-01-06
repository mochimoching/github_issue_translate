# Add ability to use bean names for jobs and steps

**Issue番号**: #4858

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-03

**ラベル**: type: feature, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/4858

**関連リンク**:
- Commits:
  - [bb2440f](https://github.com/spring-projects/spring-batch/commit/bb2440fea3a1a4685acba66261bebd49fa8c382d)

## 内容

As of v5.2, both `AbstractJob` and `AbstractStep` implement `BeanNameAware`. So it could be possible to use the bean name as a default job/step name in order to avoid duplication:

``` diff
@Bean
public Job job(JobRepository jobRepository, Step step) {
--	return new JobBuilder("job", jobRepository)
++	return new JobBuilder(jobRepository)
                           .start(step)
                           .build();
}
```

Obviously, the current constructor that takes the job/step name should remain to be able to specify a different name if needed.

cc @joshlong

