# Unclear reference to example about job parameters in reference documentation

**Issue番号**: #4791

**状態**: closed | **作成者**: quaff | **作成日**: 2025-03-26

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/4791

**関連リンク**:
- Commits:
  - [8020331](https://github.com/spring-projects/spring-batch/commit/8020331dc0a0950f3f759bb520490c9a0ab611fc)

## 内容

https://docs.spring.io/spring-batch/reference/domain.html#jobParameters

>> In the preceding example, where there are two instances, one for January 1st and another for January 2nd, there is really only one Job, but it has two JobParameter objects: one that was started with a job parameter of 01-01-2017 and another that was started with a parameter of 01-02-2017. 

The figure doesn't show two instances of 01-01-2017 and 01-02-2017.

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-19

I think the text references the preceding example from the previous section [JobInstance](https://docs.spring.io/spring-batch/reference/domain.html#jobinstance) to continue the explanation in the current section. Here is the text from the previous section:

```
For example, there is a January 1st run, a January 2nd run, and so on. If the January 1st run fails the first time and is run again the next day, it is still the January 1st run. (Usually, this corresponds with the data it is processing as well, meaning the January 1st run processes data for January 1st). Therefore, each JobInstance can have multiple executions (JobExecution is discussed in more detail later in this chapter), and only one JobInstance (which corresponds to a particular Job and identifying JobParameters) can run at a given time.
```

The text doesn't say "In the preceding figure" or "In this figure, there are two instances". I will update the text with a link to the previous section where the example is first introduced.

