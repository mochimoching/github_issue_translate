# Missing Javadoc site for 6.0.0-RC2

**Issue番号**: #5085

**状態**: closed | **作成者**: scordio | **作成日**: 2025-11-11

**ラベル**: in: documentation, in: build, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/5085

## 内容

https://docs.spring.io/spring-batch/docs/6.0.0-RC2/api/ does not exist, while https://docs.spring.io/spring-batch/docs/6.0.0-RC1/api/ exists.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-12

Thank you for reporting this, seems like a regression of c266075e5eb695da1316087c217264c302d277f8. This is not the first time I have issues with Javadocs.. apologies for the inconvenience 😔

I will fix that for the GA planned for next week.

### コメント 2 by fmbenhassine

**作成日**: 2025-11-18

Hi @scordio ,

FYI, the Javadocs for 6.0.0-RC2 are now available online: https://docs.spring.io/spring-batch/reference/6.0/api/index.html.

However, notice the difference in the URL from now onwards:

```
Before: https://docs.spring.io/spring-batch/docs/6.0.0-RC1/api/index.html
After : https://docs.spring.io/spring-batch/reference/6.0/api/index.html
```
The patch version number is not in the URL anymore, but can be picked up from the top left navigation menu of the home page. This change is related to our portfolio-wise goal to use Antora-based documentation process (centralised docs, SEO friendly URLs, multi-version search capabilities, etc). This URL change will be documented in the release notes.

### コメント 3 by scordio

**作成日**: 2025-11-18

> The patch version number is not in the URL anymore

I noticed that there is a redirection from https://docs.spring.io/spring-batch/reference/6.0.0-RC2/api/ to the new URL, which would allow me to still use the [`spring-batch.version`](https://github.com/spring-projects/spring-batch-extensions/blob/e4b2130053a442c5bfd7d062a6199013f0e41040/spring-batch-notion/pom.xml#L204) property from `spring-boot-dependencies`.

However, `javadoc` considers the redirection to be a [warning](https://github.com/spring-projects/spring-batch-extensions/actions/runs/19467873075/job/55707152839?pr=191#step:4:460):

```
[WARNING] Javadoc Warnings
[WARNING] warning: URL https://docs.spring.io/spring-batch/reference/6.0.0-RC2/api/element-list was redirected to https://docs.spring.io/spring-batch/reference/6.0/api/element-list -- Update the command-line options to suppress this warning.
[WARNING] 1 warning
```

Given that my build is configured to fail with javadoc warnings, I checked if I could suppress this one specifically, but I don't see such a granularity in the [DocLint groups](https://docs.oracle.com/en/java/javase/25/docs/specs/man/javadoc.html#groups), which leaves me with three options:
* Remove failing in case of warnings (not really my preference)
* Hardcode `6.0` in the URL
* Fall back to the [Spring Batch Javadoc](https://javadoc.io/doc/org.springframework.batch/spring-batch-core/latest/index.html) hosted at [javadoc.io](https://javadoc.io/)

For now, I went with the last option at https://github.com/spring-projects/spring-batch-extensions/pull/191/commits/6bbcf83780bf1ae510ffad1685c7fec67fc199fc.

### コメント 4 by fmbenhassine

**作成日**: 2025-11-19

This server-side redirection is portfolio-wise and I don't see what we can do on the Spring Batch side, but I am open to suggestions.

### コメント 5 by scordio

**作成日**: 2025-11-19

I see that the Framework still works with explicit RC or patch versions, for example:
* https://docs.spring.io/spring-framework/docs/7.0.0-RC3/javadoc-api
* https://docs.spring.io/spring-framework/docs/7.0.0/javadoc-api

Could it be that they still need to migrate to the new way?

### コメント 6 by fmbenhassine

**作成日**: 2025-11-19

Yes, it could be. I will ask the team and get back to you.

BTW, the Boot javadocs have the redirection in place (similar to Batch):

https://docs.spring.io/spring-boot/4.0.0-RC2/api/java/index.html redirects to
https://docs.spring.io/spring-boot/4.0/api/java/index.html

### コメント 7 by scordio

**作成日**: 2025-11-19

Since the entire portfolio is moving in this direction, I'll ask on the [javadoc-dev](https://mail.openjdk.org/mailman/listinfo/javadoc-dev) mailing list how this use case should be addressed.

