# Errors are not propagated from job execution

**Issue番号**: #808

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2019-03-21

**ラベル**: type: bug, in: core, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/808

**関連リンク**:
- Commits:
  - [b251512](https://github.com/spring-projects/spring-batch/commit/b251512ee40f9104e1f64daf9d390f956dd3838e)
  - [7f375c6](https://github.com/spring-projects/spring-batch/commit/7f375c662769f0a680cd03badd2fc2ac30d5163b)

## 内容

**[Paolo](https://jira.spring.io/secure/ViewProfile.jspa?name=pdv_)** opened **[BATCH-2800](https://jira.spring.io/browse/BATCH-2800?redirect=false)** and commented

The piece of code below in the AbstractJob class is catching Throwable, thus preventing the JVM to crash on any Error like it should.
Is there a good reason for this ? If so, shouldn't this be documented somewhere ?
It can be really surprising and upsetting when you find this out in a production environment.
See details in the linked StackOverflow thread.

```java
@Override
public final void execute(JobExecution execution) {
    [...]
    try {
            [...]
    } catch (Throwable t) {
            logger.error("Encountered fatal error executing job", t);
            execution.setExitStatus(getDefaultExitStatusForFailure(t, execution));
            execution.setStatus(BatchStatus.FAILED);
            execution.addFailureException(t);
    }
```



---

**Affects:** 4.1.1

**Reference URL:** https://stackoverflow.com/questions/54811702/spring-batch-doesnt-propagate-errors


## コメント

### コメント 1 by Agniswar123

**作成日**: 2025-10-28

Quick qes. If a heapdump is needed can't visualVM be used? A project can have multiple job, so maybe some alert by execution listener will help, but stopping entire application, is it ideal?

