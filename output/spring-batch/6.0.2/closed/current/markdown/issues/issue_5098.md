# ClosedChannelException when using StaxEventItemWriter in combination with MultiResourceItemWriter

**Issue番号**: #5098

**状態**: closed | **作成者**: g00glen00b | **作成日**: 2025-11-21

**ラベル**: in: infrastructure, type: bug, has: minimal-example, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5098

**関連リンク**:
- Commits:
  - [5dc40a6](https://github.com/spring-projects/spring-batch/commit/5dc40a6b97dfb2dd3f556913d5ec60f0ba94acfb)

## 内容

**Bug description**
When using a `StaxEventItemWriter` in combination with a `MultiResourceItemWriter`, a `ClosedChannelException` is thrown with following stacktrace:

```
Caused by: java.nio.channels.ClosedChannelException: null
    at java.base/sun.nio.ch.FileChannelImpl.ensureOpen(FileChannelImpl.java:160) ~[na:na]
    at java.base/sun.nio.ch.FileChannelImpl.write(FileChannelImpl.java:284) ~[na:na]
    at org.springframework.batch.support.transaction.TransactionAwareBufferedWriter$1.complete(TransactionAwareBufferedWriter.java:121) ~[spring-batch-infrastructure-5.2.4.jar:5.2.4]
    at org.springframework.batch.support.transaction.TransactionAwareBufferedWriter$1.beforeCommit(TransactionAwareBufferedWriter.java:106) ~[spring-batch-infrastructure-5.2.4.jar:5.2.4]
    ... 44 common frames omitted
```

This only occurs as long as `StaxEventItemWriter` is configured to be transactional. After debugging some more it seemd to be related to the `endDocument()` method  running after the writer has been closed, but I'm not sure if this is really the case.

**Environment**
Reproducible in multiple versions of Spring Batch (including 5.2.3, 6.0.0) on Java 21

**Steps to reproduce**
1. Define a `StaxEventItemWriter`:

    ```java
    @Bean
    public StaxEventItemWriter<Foo> fooWriter() {
        return new StaxEventItemWriterBuilder<Foo>()
            .name("fooWriter")
            .marshaller(marshaller())
            .rootTagName("foos")
            // Note, in Spring Batch 6.0, it seems to be required to pass a `resource` within the builder
            // even though it isn't used  due to being overriden by the `MultiResourceItemWriter`
            .resource(new FileSystemResource("foo/foo.xml"))
            .build();
    }
    ```

2. Define a `MultiResourceItemWriter`:

    ```java
    @Bean
    public MultiResourceItemWriter<Foo> multiFooWriter() {
        return new MultiResourceItemWriterBuilder<Foo>()
            .name("multiFooWriter")
            .delegate(fooWriter())
            .itemCountLimitPerResource(100)
            .resourceSuffixCreator(index -> "-" + index + ".xml")
            .resource(new FileSystemResource("foo"))
            .build();
    }
    ```

3. Define a `Job` using this `MultiResourceItemWriter` and run it. It will result in the aforementioned stack trace. When I set `.transactional(false)` within the `StaxEventItemWriter`, the batch succeeds.

**Expected behavior**
I expect 100 XML files to be created (reader produces 10.000 items and writer creates a separate file per 100 items). 

**Minimal Complete Reproducible example**
[GitHub Repository](https://github.com/g00glen00b/spring-batch-multiresource-stax-reader-transactional-issue/)

**Additional notes**
Relevant Stack Overflow thread I created: [link](https://stackoverflow.com/q/79825366)
In this Stack Overflow thread it was discussed that this might be intentional behavior. If that's the case, I could send a PR to mention this in the documentation somewhere.


## コメント

### コメント 1 by banseok1216

**作成日**: 2025-12-20

Hello,

Since the explanation was too long to fit into a comment, I opened a separate issue with a more complete repro and detailed notes, and submitted a PR with the fix.
- https://github.com/spring-projects/spring-batch/issues/5176

### コメント 2 by fmbenhassine

**作成日**: 2026-01-21

@g00glen00b Thank you for opening this issue and for providing an example! This is a bug and not a documentation issue.

I am reviewing #5177 which goes in the right direction to fix this issue, and I will add a comment here for an update about the version which will include it.

@banseok1216 Thank you for the great analysis in #5176 and for the PR. Really appreciated 🙏

> Since the explanation was too long to fit into a comment

Since that was just an explanation for the same issue, I will close it as a duplicate of this one.

