# Update GraalVM runtime hints

**Issue番号**: #4844

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-22

**ラベル**: type: task, in: core, related-to: native

**URL**: https://github.com/spring-projects/spring-batch/issues/4844

**関連リンク**:
- Commits:
  - [580bd30](https://github.com/spring-projects/spring-batch/commit/580bd307a31726fa5e119a86161f05a290b44cef)
  - [f6f31ca](https://github.com/spring-projects/spring-batch/commit/f6f31cacc779f06cafb9cac275720f2a46831086)
  - [369652c](https://github.com/spring-projects/spring-batch/commit/369652cc73d227690de065d0fe3c16a14631774f)

## 内容

Related to https://github.com/spring-projects/spring-framework/issues/33847, runtime hints for Spring Batch should be updated accordingly.

See https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes#graalvm-native-applications

## コメント

### コメント 1 by goafabric

**作成日**: 2025-08-04

@fmbenhassine 
As an fyi, while trying out boot 4.0.0-M1 in combination with GraalVM 24 (both local and paketo),
the native compile now breaks with the exception below.
With GraalVM 21 the compile works, but already with simple Spring Boot Apps, the Application wont start, due to another issue.

While the build will work, when overriding the CoreRuntimeHints and escaping the curly braces "\\{", the compile works.
Though i am not sure if this is the correct way to do it.


--- cut ---
Error: Error: invalid glob patterns found:
Pattern ALL_UNNAMED/org/springframework/batch/core/schema-{h2,derby,hsqldb,sqlite,db2,hana,mysql,mariadb,oracle,postgresql,sqlserver,sybase}.sql : Pattern contains unescaped character {. Pattern contains unescaped character }. 



### コメント 2 by fmbenhassine

**作成日**: 2025-08-04

@goafabric Thank you for reporting this! I created #4937 to track this failure and planned to fix it in the upcoming 6.0.0-M2. FYI, I have planned to add a CI build against GraalVM to avoid this kind of issues (#3871).

### コメント 3 by goafabric

**作成日**: 2025-08-04

> [@goafabric](https://github.com/goafabric) Thank you for reporting this! I created [#4937](https://github.com/spring-projects/spring-batch/issues/4937) to track this failure and planned to fix it in the upcoming 6.0.0-M2. FYI, I have planned to add a CI build against GraalVM to avoid this kind of issues ([#3871](https://github.com/spring-projects/spring-batch/issues/3871)).

thank you for the very fast reply and creating the issue !
i was unsure at first if to report this, due to the milestone and how .. but its awesome that it was so easy

