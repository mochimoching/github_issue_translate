# Spring Batch GitHub Issues

取得日時: 2025年12月31日 13:14:27

取得件数: 97件

---

## Issue #46248: Fix description of spring.batch.job.enabled

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-02

**ラベル**: type: documentation, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46248

**関連リンク**:
- Commits:
  - [ac2656d](https://github.com/spring-projects/spring-boot/commit/ac2656d312b7fffcfac6003f77c49a9561035adb)

### 内容

Forward port of issue #46247 to 4.0.x.

---

## Issue #46255: Remove unnecessary semicolons from Gradle build scripts

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-02

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46255

**関連リンク**:
- Commits:
  - [381706f](https://github.com/spring-projects/spring-boot/commit/381706fe33153ca6e440695ce7e7a82ffd803da6)

### 内容

Forward port of issue #46254 to 4.0.x.

---

## Issue #46258: Use ThreadLocal.remove() instead of set(null)

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-03

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46258

**関連リンク**:
- Commits:
  - [74e6851](https://github.com/spring-projects/spring-boot/commit/74e68510447c5816e8026aff10a66ed33c3db823)

### 内容

Forward port of issue #46257 to 4.0.x.

---

## Issue #46264: Remove unnecessary toString() call

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-03

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46264

**関連リンク**:
- Commits:
  - [36b713e](https://github.com/spring-projects/spring-boot/commit/36b713eb5d78672b4b3ea312d9b23b2cde60d143)

### 内容

Forward port of issue #46263 to 4.0.x.

---

## Issue #46270: NoSuchMethodFailureAnalyzerTests is relying on a incompatiblity in Spring Data R2DBC without specifying its version

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-04

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46270

**関連リンク**:
- Commits:
  - [5e969f9](https://github.com/spring-projects/spring-boot/commit/5e969f92961476e466b5fb782c507726f24b8d37)

### 内容

Forward port of issue #46269 to 4.0.x.

---

## Issue #46271: Upgrade to Spring Pulsar 2.0.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-04

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46271

**関連リンク**:
- Commits:
  - [71d88c1](https://github.com/spring-projects/spring-boot/commit/71d88c1e448e0ae21ff67ea7d6e8ce506a176cec)
  - [fbfd09e](https://github.com/spring-projects/spring-boot/commit/fbfd09ec5c58561539fcbe4cd3e4367d6bcc04b7)

### 内容

Upgrade to [Spring Pulsar 2.0.0-M1](https://github.com/spring-projects/spring-pulsar/releases/tag/v2.0.0-M1).

### コメント

#### コメント 1 by snicoll

**作成日**: 2025-07-04

We can't move to 2.0.0 snapshots just yet as there aren't any.

---

## Issue #46272: Upgrade to Neo4j Java Driver 5.28.7

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-04

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46272

**関連リンク**:
- Commits:
  - [e3ef438](https://github.com/spring-projects/spring-boot/commit/e3ef438d6d9fdb1720d243010ec369a55d79ba44)

### 内容

Upgrade to [Neo4j Java Driver 5.28.7](https://github.com/neo4j/neo4j-java-driver/releases/tag/5.28.7).

---

## Issue #46292: Update spring-boot-webclient to have an API dependency on spring-webflux

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-04

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46292

**関連リンク**:
- Commits:
  - [efde264](https://github.com/spring-projects/spring-boot/commit/efde264aee3154e35639bddef9b641ea09030b8f)
  - [108ca64](https://github.com/spring-projects/spring-boot/commit/108ca64989d87a46e62b2de88acc1a9f3b9727f8)

### 内容

It currently has an optional dependency, but the module name would suggest that `org.springframework.web.reactive.function.client.WebClient` should be available and it's in `spring-webflux`

### コメント

#### コメント 1 by wilkinsona

**作成日**: 2025-07-07

I think that was a mistake when I created the new module. IMO, it should be an `api` dependency.

---

## Issue #46293: Add support for JmsClient

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-05

**ラベル**: type: enhancement

**URL**: https://github.com/spring-projects/spring-boot/issues/46293

**関連リンク**:
- Commits:
  - [626065a](https://github.com/spring-projects/spring-boot/commit/626065a827854910231cc0428ec1b9eafdca3949)

### 内容

The next Spring Framework milestone will introduce support for `JmsClient` https://github.com/spring-projects/spring-framework/issues/32501#event-18474918776.

This issue is about adding support for that in the same spirit as `RestClient` and `JdbcClient`.

---

## Issue #46295: Guard ZipkinTracingAutoConfiguration against missing Encoding bean

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-05

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46295

**関連リンク**:
- Commits:
  - [7807cff](https://github.com/spring-projects/spring-boot/commit/7807cffc1bef045c8674a70c80d04d12fcb8fa0e)

### 内容

As noted by @onobc we have condition [here](https://github.com/spring-projects/spring-boot/blob/5e52468e83da9fdb9c519605e9626462e4aeb50a/spring-boot-project/spring-boot-tracing/src/main/java/org/springframework/boot/tracing/autoconfigure/zipkin/ZipkinTracingAutoConfiguration.java#L86) but not [here](https://github.com/spring-projects/spring-boot/blob/5e52468e83da9fdb9c519605e9626462e4aeb50a/spring-boot-project/spring-boot-tracing/src/main/java/org/springframework/boot/tracing/autoconfigure/zipkin/ZipkinTracingAutoConfiguration.java#L64)

### コメント

#### コメント 1 by snicoll

**作成日**: 2025-07-10

Shoulnd't `ZipkinTracingAutoConfiguration` have `@AutoConfiguration(afterName =  "org.springframework.boot.zipkin.autoconfigure.ZipkinAutoConfiguration")` as well? Besides the condition, I mean.

#### コメント 2 by snicoll

**作成日**: 2025-07-14

Looking at the smoke test that's failing, and the inconsistent condition, let's go ahead with the above.

#### コメント 3 by wilkinsona

**作成日**: 2025-07-14

Leaving the meeting label on for now as Phil wanted to "double check in our next team meeting that the class is in the correct place. I think it is since the tracing module configures tracing for a bunch of tech and you can use Zipkin without Micrometer tracing".

---

## Issue #46299: Upgrade to Gradle 8.14.3

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-07

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46299

**関連リンク**:
- Commits:
  - [bc98577](https://github.com/spring-projects/spring-boot/commit/bc985776e6cc9164a9e101b1734a2a8bf72195a3)

### 内容

Forward port of issue #46298 to 4.0.x.

---

## Issue #46302: Test Gradle plugin against Gradle 7.6.6

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-07

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46302

**関連リンク**:
- Commits:
  - [7e76eab](https://github.com/spring-projects/spring-boot/commit/7e76eab0b86bd76b33878ffb32d590b874af0212)

### 内容

Forward port of issue #46301 to 4.0.x.

---

## Issue #46304: Upgrade to Spring Batch 6.0.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-07

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46304

**関連リンク**:
- Commits:
  - [987b13c](https://github.com/spring-projects/spring-boot/commit/987b13c74a9d4e653d6f972d89b6b63eb431737a)

### 内容

Upgrade to [Spring Batch 6.0.0-M1](https://github.com/spring-projects/spring-batch/releases/tag/v6.0.0-M1).

---

## Issue #46306: Polish

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-07

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46306

**関連リンク**:
- Commits:
  - [53b66d0](https://github.com/spring-projects/spring-boot/commit/53b66d0da73e5c7a99ca2e21a8df53aa8203e120)

### 内容

Forward port of issue #46305 to 4.0.x.

---

## Issue #46308: Upgrade to Spring LDAP 4.0.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-07

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46308

**関連リンク**:
- Commits:
  - [06c4eaa](https://github.com/spring-projects/spring-boot/commit/06c4eaabc8c91b8c57b5f80b98f638e864439352)
  - [a111b14](https://github.com/spring-projects/spring-boot/commit/a111b148d7fadef39080448d83911b62f137ded5)

### 内容

Upgrade to [Spring LDAP 4.0.0-M1](https://github.com/spring-projects/spring-ldap/releases/tag/4.0.0-M1).

---

## Issue #46311: Change in DefaultErrorAttributes alters the shape of API validation error responses

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-07

**ラベル**: type: regression, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46311

**関連リンク**:
- Commits:
  - [0db3232](https://github.com/spring-projects/spring-boot/commit/0db3232d4545667ffc5c9eb1e60a647775f072e0)

### 内容

Forward port of issue #46260 to 4.0.x.

---

## Issue #46312: Upgrade to Spring Session 4.0.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-07

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46312

**関連リンク**:
- Commits:
  - [e39eedb](https://github.com/spring-projects/spring-boot/commit/e39eedb08e471846ec62b23f99fd37736405743b)
  - [d4e95cd](https://github.com/spring-projects/spring-boot/commit/d4e95cdf424db1d3d909704472fb7b91cf27465c)

### 内容

Upgrade to [Spring Session 4.0.0-M1](https://github.com/spring-projects/spring-session/releases/tag/4.0.0-M1).

---

## Issue #46316: Polish usage of '@ConditionalOnWebApplication' for consistency

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-07

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46316

**関連リンク**:
- Commits:
  - [912b50e](https://github.com/spring-projects/spring-boot/commit/912b50ebbd39b74ebde8b8d161fc7675126da49c)

### 内容

Forward port of issue #46315 to 4.0.x.

---

## Issue #46320: Upgrade to Spring Authorization Server 2.0.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46320

**関連リンク**:
- Commits:
  - [e185bf1](https://github.com/spring-projects/spring-boot/commit/e185bf1e563f5c0cceb715e273d3604270278c4a)
  - [bcb801b](https://github.com/spring-projects/spring-boot/commit/bcb801b7f8d6d5214673da7f5b36b2ff00fc3f40)

### 内容

Upgrade to [Spring Authorization Server 2.0.0](https://github.com/spring-projects/spring-authorization-server/releases/tag/2.0.0).

---

## Issue #46321: Upgrade to Micrometer 1.16.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46321

**関連リンク**:
- Commits:
  - [c98b1fe](https://github.com/spring-projects/spring-boot/commit/c98b1fe70523affde3b436414979897f0717a0b5)
  - [8b91176](https://github.com/spring-projects/spring-boot/commit/8b911761589b023d67bd3c02b994d6c01036ade2)

### 内容

Upgrade to [Micrometer 1.16.0-M1](https://github.com/micrometer-metrics/micrometer/releases/tag/v1.16.0-M1).

---

## Issue #46322: Upgrade to Micrometer Tracing 1.6.0-M1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46322

**関連リンク**:
- Commits:
  - [15147dd](https://github.com/spring-projects/spring-boot/commit/15147dd8ef0f3c046a2125014b79f9daac7fcb34)
  - [92c3fdd](https://github.com/spring-projects/spring-boot/commit/92c3fdddafa5f05cc6095c4100463ecfe5efd941)

### 内容

Upgrade to [Micrometer Tracing 1.6.0-M1](https://github.com/micrometer-metrics/tracing/releases/tag/v1.6.0-M1).

---

## Issue #46323: Upgrade to ActiveMQ 6.1.7

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46323

**関連リンク**:
- Commits:
  - [dc68401](https://github.com/spring-projects/spring-boot/commit/dc6840155dc9af4a587f418f28883e29576f53c2)

### 内容

Upgrade to [ActiveMQ 6.1.7](https://activemq.apache.org/components/classic/download/classic-06-01-07).

---

## Issue #46324: Upgrade to Artemis 2.41.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46324

**関連リンク**:
- Commits:
  - [147e49a](https://github.com/spring-projects/spring-boot/commit/147e49af1c1e5ea267287546b7b9952f360203e9)

### 内容

Upgrade to [Artemis 2.41.0](https://activemq.apache.org/components/artemis/download/release-notes-2.41.0).

---

## Issue #46325: Upgrade to Brave 6.3.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46325

**関連リンク**:
- Commits:
  - [aa9c297](https://github.com/spring-projects/spring-boot/commit/aa9c2978bedbed921d0e41acfd3b22ebb1bde11e)

### 内容

Upgrade to [Brave 6.3.0](https://github.com/openzipkin/brave/releases/tag/6.3.0).

---

## Issue #46326: Upgrade to Flyway 11.10.1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46326

**関連リンク**:
- Commits:
  - [d359d00](https://github.com/spring-projects/spring-boot/commit/d359d00ff85a8952701487c488a15c5064a92c7f)

### 内容

Upgrade to [Flyway 11.10.1](https://documentation.red-gate.com/flyway/release-notes-and-older-versions/release-notes-for-flyway-engine).

Supersedes #46055

---

## Issue #46327: Upgrade to Hibernate 7.0.5.Final

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46327

**関連リンク**:
- Commits:
  - [bd09c78](https://github.com/spring-projects/spring-boot/commit/bd09c786ab96669a3e262fe5dc7b2ff0cfe2305e)

### 内容

Upgrade to [Hibernate 7.0.5.Final](https://github.com/hibernate/hibernate-orm/releases/tag/7.0.5).

Supersedes #46056

---

## Issue #46328: Upgrade to HtmlUnit 4.13.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46328

**関連リンク**:
- Commits:
  - [a144105](https://github.com/spring-projects/spring-boot/commit/a1441055898a3bbaa3717896879df55e1761688e)

### 内容

Upgrade to [HtmlUnit 4.13.0](https://github.com/HtmlUnit/htmlunit/releases/tag/4.13.0).

---

## Issue #46329: Upgrade to Jetty 12.0.23

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46329

**関連リンク**:
- Commits:
  - [6f3a5e2](https://github.com/spring-projects/spring-boot/commit/6f3a5e2a040eee97ff4385754173924796ec516f)

### 内容

Upgrade to [Jetty 12.0.23](https://github.com/jetty/jetty.project/releases/tag/jetty-12.0.23).

---

## Issue #46330: Upgrade to JUnit Jupiter 5.13.3

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46330

**関連リンク**:
- Commits:
  - [ee3ffc8](https://github.com/spring-projects/spring-boot/commit/ee3ffc8dc047fb3fcab3795c341f3f9f82491836)

### 内容

Upgrade to [JUnit Jupiter 5.13.3](https://junit.org/junit5/docs/5.13.3/release-notes).

Supersedes #46058

---

## Issue #46331: Upgrade to Kotlin Coroutines 1.10.2

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46331

**関連リンク**:
- Commits:
  - [f018a1d](https://github.com/spring-projects/spring-boot/commit/f018a1d0324eb252add354d594014e222350f15a)

### 内容

Upgrade to [Kotlin Coroutines 1.10.2](https://github.com/Kotlin/kotlinx.coroutines/releases/tag/1.10.2).

---

## Issue #46332: Upgrade to Kotlin Serialization 1.9.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46332

**関連リンク**:
- Commits:
  - [9ed7ea0](https://github.com/spring-projects/spring-boot/commit/9ed7ea05456891c42a268036254308ca1b54d13a)

### 内容

Upgrade to [Kotlin Serialization 1.9.0](https://github.com/Kotlin/kotlinx.serialization/releases/tag/v1.9.0).

---

## Issue #46333: Upgrade to Liquibase 4.32.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46333

**関連リンク**:
- Commits:
  - [37f11e4](https://github.com/spring-projects/spring-boot/commit/37f11e4ce7a7fa2574f6bc540680ef58efd68afd)

### 内容

Upgrade to [Liquibase 4.32.0](https://github.com/liquibase/liquibase/releases/tag/v4.32.0).

---

## Issue #46335: Upgrade to MariaDB 3.5.4

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46335

**関連リンク**:
- Commits:
  - [f722a97](https://github.com/spring-projects/spring-boot/commit/f722a9701fff01b08eeadb3109121e975847d03c)

### 内容

Upgrade to [MariaDB 3.5.4](https://mariadb.com/kb/en/mariadb-connector-j-3-5-4-release-notes).

---

## Issue #46336: Upgrade to Maven Enforcer Plugin 3.6.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46336

**関連リンク**:
- Commits:
  - [9f53cbe](https://github.com/spring-projects/spring-boot/commit/9f53cbedcce27de2fd642a7e1b3df137a20ad9c9)

### 内容

Upgrade to [Maven Enforcer Plugin 3.6.0](https://github.com/apache/maven-enforcer/releases/tag/enforcer-3.6.0).

---

## Issue #46337: Upgrade to Maven Invoker Plugin 3.9.1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46337

**関連リンク**:
- Commits:
  - [ed1e1d7](https://github.com/spring-projects/spring-boot/commit/ed1e1d79f00ea223e8b3be4343d05e0436318a37)

### 内容

Upgrade to [Maven Invoker Plugin 3.9.1](https://github.com/apache/maven-invoker-plugin/releases/tag/maven-invoker-plugin-3.9.1).

---

## Issue #46338: Upgrade to Mockito 5.18.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46338

**関連リンク**:
- Commits:
  - [d3f8eae](https://github.com/spring-projects/spring-boot/commit/d3f8eaeb6d6305439a5c6a243d80b38e15544f21)

### 内容

Upgrade to [Mockito 5.18.0](https://github.com/mockito/mockito/releases/tag/v5.18.0).

---

## Issue #46339: Upgrade to MSSQL JDBC 12.10.1.jre11

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46339

**関連リンク**:
- Commits:
  - [aaf4cca](https://github.com/spring-projects/spring-boot/commit/aaf4cca2d5b2475fbe4079bc9c6754a84eaf9b2a)

### 内容

Upgrade to [MSSQL JDBC 12.10.1.jre11](https://github.com/microsoft/mssql-jdbc/releases/tag/v12.10.1).

---

## Issue #46340: Upgrade to MySQL 9.3.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46340

**関連リンク**:
- Commits:
  - [316db41](https://github.com/spring-projects/spring-boot/commit/316db41b10010d1d87e57a4242c398c0d1333c68)

### 内容

Upgrade to [MySQL 9.3.0](https://dev.mysql.com/doc/relnotes/connector-j/en/news-9-3-0.html).

### コメント

#### コメント 1 by devnicdna

**作成日**: 2025-07-09

@snicoll have you thought about porting this update to spring-boot 3.x as there is [vulnerability in mysql-connector-j 9.2.0](https://nvd.nist.gov/vuln/detail/CVE-2025-30706) ?

#### コメント 2 by snicoll

**作成日**: 2025-07-09

I have not, thanks for pointing that out. Our [third-party dependencies policy](https://github.com/spring-projects/spring-boot/wiki/Supported-Versions#third-party-dependencies) is such that we don't upgrade to a new feature release of a dependency in a maintenance release of Spring Boot. That being said, @wilkinsona is mentioning that 9.2.0 is superseded by 9.3.0 so there's no point to stick to that version. 

I'll do the necessary shortly.

#### コメント 3 by lzysuqianqiu

**作成日**: 2025-07-22

9.4.0 is out
 https://dev.mysql.com/doc/relnotes/connector-j/en/news-9-4-0.html

---

## Issue #46341: Upgrade to OpenTelemetry 1.51.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46341

**関連リンク**:
- Commits:
  - [07f524d](https://github.com/spring-projects/spring-boot/commit/07f524deee152c784a35fe1b8df429ba1dd56611)

### 内容

Upgrade to [OpenTelemetry 1.51.0](https://github.com/open-telemetry/opentelemetry-java/releases/tag/v1.51.0).

---

## Issue #46342: Upgrade to Oracle Database 23.8.0.25.04

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46342

**関連リンク**:
- Commits:
  - [20b0a4f](https://github.com/spring-projects/spring-boot/commit/20b0a4f244962d69125c2a167a72a96f373480ff)

### 内容

Upgrade to Oracle Database 23.8.0.25.04.

---

## Issue #46343: Upgrade to Prometheus Client 1.3.10

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46343

**関連リンク**:
- Commits:
  - [9c376f1](https://github.com/spring-projects/spring-boot/commit/9c376f1698a44c20bba0075e8d0e5f3b10592ce1)

### 内容

Upgrade to [Prometheus Client 1.3.10](https://github.com/prometheus/client_java/releases/tag/v1.3.10).

### コメント

#### コメント 1 by breun

**作成日**: 2025-07-08

Will this upgrade also be backported to the `3.4.x` and `3.5.x` branches? Those branches currently use version 1.3.8, which doesn't correctly shade `protobuf-java` (https://github.com/prometheus/client_java/issues/1431), which was fixed in [1.3.9](https://github.com/prometheus/client_java/releases/tag/v1.3.9).

#### コメント 2 by snicoll

**作成日**: 2025-07-08

Yes

---

## Issue #46344: Upgrade to Pulsar Reactive 0.7.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46344

**関連リンク**:
- Commits:
  - [3f2fee8](https://github.com/spring-projects/spring-boot/commit/3f2fee8817b70775b7c71fb551dc5228317a1c4c)

### 内容

Upgrade to [Pulsar Reactive 0.7.0](https://github.com/apache/pulsar-client-reactive/releases/tag/v0.7.0).

---

## Issue #46345: Upgrade to RxJava3 3.1.11

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46345

**関連リンク**:
- Commits:
  - [62fa433](https://github.com/spring-projects/spring-boot/commit/62fa4333fd172479eddea0c8a165676d0dd192d3)

### 内容

Upgrade to [RxJava3 3.1.11](https://github.com/ReactiveX/RxJava/releases/tag/v3.1.11).

---

## Issue #46346: Upgrade to Selenium 4.34.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46346

**関連リンク**:
- Commits:
  - [d0fe716](https://github.com/spring-projects/spring-boot/commit/d0fe716125d430ea35333f9e88ad689883c9aea6)

### 内容

Upgrade to [Selenium 4.34.0](https://github.com/SeleniumHQ/selenium/releases/tag/selenium-4.34.0).

---

## Issue #46347: Upgrade to Selenium HtmlUnit 4.33.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46347

**関連リンク**:
- Commits:
  - [ae5dadc](https://github.com/spring-projects/spring-boot/commit/ae5dadca39dab9660d93e244b4fd1ec525f04884)

### 内容

Upgrade to [Selenium HtmlUnit 4.33.0](https://github.com/SeleniumHQ/htmlunit-driver/releases/tag/htmlunit-driver-4.33.0).

---

## Issue #46348: Upgrade to Testcontainers 1.21.3

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46348

**関連リンク**:
- Commits:
  - [9f9dcff](https://github.com/spring-projects/spring-boot/commit/9f9dcffbe66940f7bc4f89df88a31a0ecc56e774)

### 内容

Upgrade to [Testcontainers 1.21.3](https://github.com/testcontainers/testcontainers-java/releases/tag/1.21.3).

---

## Issue #46349: Upgrade to Tomcat 11.0.9

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46349

**関連リンク**:
- Commits:
  - [1825453](https://github.com/spring-projects/spring-boot/commit/1825453344ff583d41762950266114cc2881e97d)

### 内容

Upgrade to [Tomcat 11.0.9](https://tomcat.apache.org/tomcat-11.0-doc/changelog.html).

Supersedes #45475

---

## Issue #46350: Upgrade to XmlUnit2 2.10.3

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46350

**関連リンク**:
- Commits:
  - [870e652](https://github.com/spring-projects/spring-boot/commit/870e652e854d882246232622e7ccf3e6e80fddc4)

### 内容

Upgrade to [XmlUnit2 2.10.3](https://github.com/xmlunit/xmlunit/releases/tag/v2.10.3).

---

## Issue #46354: Fix eclipse conventions to ensure classpath excludes binary output folders

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-08

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46354

**関連リンク**:
- Commits:
  - [29f0a41](https://github.com/spring-projects/spring-boot/commit/29f0a412c51665486567e8e1d56fc17ffb053487)

### 内容

Forward port of issue #46353 to 4.0.x.

---

## Issue #46358: Restructure project directories to better fit Gradle

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-09

**ラベル**: type: task, theme: modularization

**URL**: https://github.com/spring-projects/spring-boot/issues/46358

**関連リンク**:
- Commits:
  - [e90efd7](https://github.com/spring-projects/spring-boot/commit/e90efd7c08e7aebcf3a91274b7ac4f7121a86190)
  - [decc32d](https://github.com/spring-projects/spring-boot/commit/decc32dde3c04c980466f6f5bc7b25f17ca99c69)

### 内容

Our current directory structure contains a lot of echos from when the project was built with Maven. We could restructure things in 4.0.x

---

## Issue #46364: ApplicationNameConverter is still referenced in Logback's defaults

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-09

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46364

**関連リンク**:
- Commits:
  - [04d0710](https://github.com/spring-projects/spring-boot/commit/04d071046d5bdd52c40d5f91c83fa6395762f8af)

### 内容

`ApplicationNameConverter` is deprecated since 3.4 and removed in 4.0 but we've overlooked the reference in `org/springframework/boot/logging/logback/defaults.xml`

This produces a failure when our AOT contribution tries to build a model for the XML configuration as the class no longer exists.

(Flagging it as a task as the offending code isn't released in any milestone yet).

---

## Issue #46399: Runtime dependencies are missing from aotCompileClasspath and aotTestCompileClasspath when using Kotlin

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-10

**ラベル**: type: bug, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46399

**関連リンク**:
- Commits:
  - [a2d015a](https://github.com/spring-projects/spring-boot/commit/a2d015ad02caf00643ba0e5eeaa7b1b885b99a17)

### 内容

Forward port of issue #46398 to 4.0.x.

---

## Issue #46403: Executable JAR application class encounters performance issues when used with Palo Alto Network Cortex XDR agent

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-11

**ラベル**: type: bug, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46403

**関連リンク**:
- Commits:
  - [194fe4b](https://github.com/spring-projects/spring-boot/commit/194fe4b6448a674fb44eccfc70ba36bc278c9224)

### 内容

Forward port of issue #46402 to 4.0.x.

---

## Issue #46405: Web server starters should bring spring-boot-starter

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-11

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46405

**関連リンク**:
- Commits:
  - [14f8609](https://github.com/spring-projects/spring-boot/commit/14f86092d6212806ef2f2f7d32565e68e981f6ef)

### 内容

With the modularization, adding only a starter to bring a web server is more likely so we should make it so that we don't need to also add spring-boot-starter

---

## Issue #46406: Move org.springframework.boot.autoconfigure.thread package to org.springframework.boot.thread

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-11

**ラベル**: type: enhancement

**URL**: https://github.com/spring-projects/spring-boot/issues/46406

**関連リンク**:
- Commits:
  - [94215d3](https://github.com/spring-projects/spring-boot/commit/94215d3fdc7bcd1dde12050e0f019999d1b211dd)

### 内容

_本文なし_

---

## Issue #46407: Upgrade to Neo4j Java Driver 5.28.8

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-11

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46407

**関連リンク**:
- Commits:
  - [ec20182](https://github.com/spring-projects/spring-boot/commit/ec20182e129afc8dfb4877bd7ba913ea4daf341b)

### 内容

Upgrade to [Neo4j Java Driver 5.28.8](https://github.com/neo4j/neo4j-java-driver/releases/tag/5.28.8).

Supersedes #46272

---

## Issue #46413: Add support for overriding the upgrade policy on a per-library basis

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-14

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46413

**関連リンク**:
- Commits:
  - [f98492a](https://github.com/spring-projects/spring-boot/commit/f98492a663c8472714133a43ca9052801fa01089)

### 内容

Forward port of issue #46412 to 4.0.x.

---

## Issue #46417: Fix BootZipCopyAction.Processor.getDirMode(FileCopyDetails)

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-14

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46417

**関連リンク**:
- Commits:
  - [60c9c96](https://github.com/spring-projects/spring-boot/commit/60c9c9675bbd3a3ecc473b0f18803e859ab47a0e)

### 内容

Forward port of issue #46416 to 4.0.x.

---

## Issue #46419: Test Gradle plugin against Gradle 9.0.0-rc-2

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-14

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46419

**関連リンク**:
- Commits:
  - [fd96784](https://github.com/spring-projects/spring-boot/commit/fd967841b3a7333619208d7a17256487bd33f113)

### 内容

Forward port of issue #46418 to 4.0.x.

---

## Issue #46420: Spring Milestone repository should no longer be configured as milestones are released to Maven Central

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-14

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46420

**関連リンク**:
- Commits:
  - [17ee49b](https://github.com/spring-projects/spring-boot/commit/17ee49be2e781a6307b7368102f454196d3fa283)

### 内容

As of Spring Boot 4, all spring projects should release their corresponding milestones to Maven Central. To prevent from an accidental release that hasn't moved yet, we should stop configuring our build to use that repository.

---

## Issue #46423: Published javadoc includes unwanted packages

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-14

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46423

**関連リンク**:
- Commits:
  - [5620be0](https://github.com/spring-projects/spring-boot/commit/5620be0d9c111f062954c1dce9fb879eba6ba468)

### 内容

The [restructuring of the project's source directories](https://github.com/spring-projects/spring-boot/issues/46358) has changed the paths of various modules. We need to update the aggregated javadoc configuration to take these changes into account.

---

## Issue #46424: Upgrade to Lettuce 6.7.1.RELEASE

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-15

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46424

**関連リンク**:
- Commits:
  - [39087c0](https://github.com/spring-projects/spring-boot/commit/39087c0a3948a9072e047a29554fa6f24e62d1f2)

### 内容

Upgrade to [Lettuce 6.7.1.RELEASE](https://github.com/lettuce-io/lettuce-core/releases/tag/6.7.1.RELEASE).

---

## Issue #46436: Upgrade to Caffeine 3.2.2

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46436

**関連リンク**:
- Commits:
  - [adff948](https://github.com/spring-projects/spring-boot/commit/adff9480508a3034413dddc2e71a796b72bc4274)

### 内容

Upgrade to [Caffeine 3.2.2](https://github.com/ben-manes/caffeine/releases/tag/v3.2.2).

---

## Issue #46437: Upgrade to Commons Lang3 3.18.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46437

**関連リンク**:
- Commits:
  - [9ab2f4d](https://github.com/spring-projects/spring-boot/commit/9ab2f4d08ef7ae0dc0cabb2c51edc8c1c497d768)
  - [b424803](https://github.com/spring-projects/spring-boot/commit/b424803abdb2bec818e4fbcb251ce031c22aca53)

### 内容

Upgrade to [Commons Lang3 3.18.0](https://commons.apache.org/proper/commons-lang/changes.html#a3.18.0).

### コメント

#### コメント 1 by waileong

**作成日**: 2025-07-17

@snicoll 
Are there any plans to backport this dependency bump to the 3.4.x/3.5.x branches, considering it contains security fixes? Thanks!

#### コメント 2 by snicoll

**作成日**: 2025-07-17

@waileong thanks for the nudge. We have no plan to upgrade to a new feature release of Commons Lang3 in a maintenance release of Spring Boot. See [our upgrade policy](https://github.com/spring-projects/spring-boot/wiki/Supported-Versions#third-party-dependencies) for more details.

If you believe you're affected by the CVE, you can override the version in your project. Alternatively, you can ask the Commons Lang3 team to backport the security fix and we'll include it next time we release.

#### コメント 3 by ppkarwasz

**作成日**: 2025-07-25

Thanks for raising this.

From the Apache Commons perspective, we currently don't maintain LTS releases. While the idea has been discussed in the past, it hasn’t gained traction, largely because:

* We haven’t seen any demand from users for LTS releases.
* Apache Commons follows strict semantic versioning, so upgrading to a newer minor release (e.g., from `3.17.0` to `3.18.0`) is generally considered safe and non-breaking. Of course, an LTS release could offer additional reassurance in more conservative environments.

As for releasing a patched `3.17.1`, that would ultimately depend on our release manager’s availability (cc @garydgregory). However, it's unlikely for a couple of reasons:

* Version `3.18.0` already contains the fix for the CVE in question.
* The vulnerability (CVE-2025-48924) is not exploitable in most applications. Specifically, `ClassUtils.getName` is rarely reachable.

If there's interest, we could publish VEX (Vulnerability Exploitability eXchange) statements clarifying the reachability and risk of this CVE in other Apache Commons components. For reference, see [this thread on `dev@commons`](https://lists.apache.org/thread/b1ckyw1fg36v6mh8n6wx5vdsj6gxkdfx). We're also open to coordinating with other OSS projects on this, subject to our time availability.


#### コメント 4 by jesperronn

**作成日**: 2025-08-11

Two very good arguments pulling in differnent directions

1. We have no plan to upgrade to a new feature release of [a package] in a maintenance release.
2. [package] follows strict semantic versioning, so upgrading to a newer minor release 

It is very sad if both parties stand on their perspective and it will only lower the trust and quality of Spring Boot since all vulnerability scanners will flag issues 😢

From the perspective of Spring Boot team, you should definitely consider if [the upgrade policy](https://github.com/spring-projects/spring-boot/wiki/Supported-Versions#third-party-dependencies) needs adjustments. 

Meanwhile we have red flags in our security scannings of our projects using spring boot 3.5.x 😢



#### コメント 5 by snicoll

**作成日**: 2025-08-11

Please review the [comment before yours](https://github.com/spring-projects/spring-boot/issues/46437#issuecomment-3117065958).

> The vulnerability (https://github.com/advisories/GHSA-j288-q9x7-2f5v) is not exploitable in most applications. Specifically, ClassUtils.getName is rarely reachable.

> it will only lower the trust and quality of Spring Boot since all vulnerability scanners will flag issues 😢

I think this is quite a partisans take. The CVE is not in Spring Boot. A maintainer of the project stated here that it's likely your application is not affected. So all that remain is your vulnerability scanner issuing a red flag you have to fix. The way to do that is not necessarily here. 

#### コメント 6 by jesperronn

**作成日**: 2025-08-12

@snicoll I fully understand and respect your point of view. However, scanners are seldom sofisticated per default, so I bet many users and companies will have to modify their vulnerability scanning policies based on this decision. 

In my world, unfortunately, we will most likely not be able to upgrade spring boot until 4.0 is released several months from now. 

The reason why I think it is an important subject is that historically in other open source projects, stuff will decay over time. As an example, consider the [official postgresql docker image](https://hub.docker.com/layers/library/postgres/latest/images/sha256-2839b0a05edad90502d2b070b4b84ff9111d5ffa1cd6dc265ca434c8219f27f6): For years, the image has been flagged as vulnerable, for instance on Dockerhub (as linked), with SNYK or similar.  

(btw an interesting case because the original author of gosu package used refuses to rebuild the package because in his perspective it contains no security issues)

However, in my experience, customers and project teams will use time to discuss each vulnerability individually. This is my interest in having no security issues flagged in projects like Spring Boot. 

Of course I respect your position, and acknowledge that it will be extra work to maintain branches if minor versions of dependencies also should be considered as fixes. And if possible, I agree that the optimal place to fix is to push back to the beginning of the the chain. 

#### コメント 7 by ppkarwasz

**作成日**: 2025-08-12

@jesperronn,

I think the real improvement needed here is in **security scanners**, not necessarily in how Spring Boot manages dependency versions or Apache Commons makes security releases.

## 1. Security-conscious companies

You clearly work for a company that takes security seriously, running scans on every release (which, believe me, is not the norm). When a scan flags a vulnerable dependency, two scenarios arise:

### **A. Exploitable vulnerability**

If the vulnerability is *actually exploitable*, you can bump the dependency in your **own** application and verify everything still works. You don’t need to wait for Spring Boot to release an updated `spring-boot-dependencies`: it’s a **suggestion list**, not a guarantee of security.

Unless you have a support contract that explicitly promises zero vulnerabilities in `spring-boot-dependencies`, it’s still your team’s responsibility to ensure your app is “without known exploitable vulnerabilities” (to borrow the EU CRA terminology).

Yes, pinning dependencies is extra work, but you likely already do it for libraries not managed by Spring Boot.

### **B. Not exploitable vulnerability**

Many scan results are **false positives** because:

* Most scanners cannot assess *exploitability*.
* Vendors benefit from reporting a high number of “issues” for marketing purposes.

The first problem is solvable.

### Apache Commons example

Within Apache Commons, we’ve been experimenting with **VEX files** for CVE-2025-48924:

* Commons BCEL – *not exploitable*: [https://github.com/apache/commons-bcel/tree/master/src/conf/security](https://github.com/apache/commons-bcel/tree/master/src/conf/security)
* Commons Compress – *not exploitable*: [https://github.com/apache/commons-compress/tree/master/src/conf/security](https://github.com/apache/commons-compress/tree/master/src/conf/security)
* Commons Configuration – *only exploitable if security guidelines are ignored*: [https://github.com/apache/commons-configuration/tree/master/src/conf/security](https://github.com/apache/commons-configuration/tree/master/src/conf/security)
* Commons Text – *only exploitable if security guidelines are ignored*: [https://github.com/apache/commons-text/tree/master/src/conf/security](https://github.com/apache/commons-text/tree/master/src/conf/security)

I used these to show that Apache Solr (with \~400 dependencies) was *not* affected: apache/solr-site#152.

We don’t advertise these on our website yet, but we’ll make every effort to keep them current for any OSS or commercial security scanner provider interested in testing them.

### Tools that can help

The open-source **SecObserve** scanner is working on supporting VEX files from dependencies (MaibornWolff/SecObserve#3177). Supporting this kind of tooling is, in my opinion, time well spent.

## 2. Non security-conscious companies

Your concerns are more relevant for companies that **don’t** run regular scans. For them, having `spring-boot-dependencies` always point to “no known vulnerabilities” is indeed useful.

However, these companies rarely contribute back, either in code or financially. Since every release costs time (whether volunteer time in Apache Commons or paid time in Spring Boot), both projects have to prioritise work that benefits the broader community or their employer.

This means Apache Commons is unlikely to publish patch-only security releases solely for organisations that don’t actively manage their own security posture, just so Spring Boot can update the version in `spring-boot-dependencies`.


#### コメント 8 by marcindabrowski

**作成日**: 2025-08-21

> [@waileong](https://github.com/waileong) thanks for the nudge. We have no plan to upgrade to a new feature release of Commons Lang3 in a maintenance release of Spring Boot. See [our upgrade policy](https://github.com/spring-projects/spring-boot/wiki/Supported-Versions#third-party-dependencies) for more details.

Hey @snicoll , if you can't backport this change to 3.5.x because of your policy, why MySQL was bumped from 9.3.0 to 9.4.0 in 3.4.9 (https://github.com/spring-projects/spring-boot/issues/46715)? This is the same situation.



#### コメント 9 by wilkinsona

**作成日**: 2025-08-21

> This is the same situation

It may look that way on the surface, but it isn't. Situations with two different dependencies are very rarely the same, particularly when security vulnerabilities are involved. We have to weigh up several factors, including:

- the potential distruption of the upgrade
- the severity of the vulneratbility
- the ease with which the vulnerability can be exploited
- how widely used the dependency may be

Considering these factors among others and the fact that Spring Boot's dependency management is only an opinion and can be overridden means that different dependencies will be treated differently and different vulnerabilities in the same dependency will also be treated differently.

#### コメント 10 by gmuth

**作成日**: 2025-10-07

The simple fix is available in [PR 47427](https://github.com/spring-projects/spring-boot/pull/47427).
However - I guess according to Spring policies this PR should only be applicable to Spring Boot 3.6.x.
"Minor and major version upgrades of third-party libraries are only applied in Spring Boot minor or major releases."
Are there any plans for a maintenance release after 3.5?
Spring Boot 4 [includes an update](https://github.com/spring-projects/spring-boot/commit/9ab2f4d08ef7ae0dc0cabb2c51edc8c1c497d768) which does not seem to have any implications on the Spring Boot code base (no back port required on the Spring Boot side).


#### コメント 11 by bclozel

**作成日**: 2025-10-07

@gmuth as stated in #47427 and the discussion here, this upgrade will not be backported to 3.5.x. There [is no plan for a 3.6.x generation](https://spring.io/projects/spring-boot#support).

---

## Issue #46438: Upgrade to Hibernate 7.0.6.Final

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: task, status: superseded

**URL**: https://github.com/spring-projects/spring-boot/issues/46438

**関連リンク**:
- Commits:
  - [92b21db](https://github.com/spring-projects/spring-boot/commit/92b21db722e6285cd899d68befbfb18631ae1f49)

### 内容

Upgrade to [Hibernate 7.0.6.Final](https://github.com/hibernate/hibernate-orm/releases/tag/7.0.6).

Supersedes #46327

---

## Issue #46439: Upgrade to Maven Enforcer Plugin 3.6.1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46439

**関連リンク**:
- Commits:
  - [ba1aef2](https://github.com/spring-projects/spring-boot/commit/ba1aef285f707938cf856fad3ddcedf1e634cde6)

### 内容

Upgrade to [Maven Enforcer Plugin 3.6.1](https://github.com/apache/maven-enforcer/releases/tag/enforcer-3.6.1).

Supersedes #46336

---

## Issue #46440: Upgrade to Neo4j Java Driver 5.28.9

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46440

**関連リンク**:
- Commits:
  - [a3d7ac9](https://github.com/spring-projects/spring-boot/commit/a3d7ac973991a670a7acd6a2631054bcb024d159)

### 内容

Upgrade to [Neo4j Java Driver 5.28.9](https://github.com/neo4j/neo4j-java-driver/releases/tag/5.28.9).

Supersedes #46407

---

## Issue #46441: Upgrade to Netty 4.2.3.Final

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46441

**関連リンク**:
- Commits:
  - [fc66566](https://github.com/spring-projects/spring-boot/commit/fc6656678151ad9bc0e192665e662b4ecd03b470)

### 内容

Upgrade to Netty 4.2.3.Final.

Supersedes #46050

---

## Issue #46442: Upgrade to OpenTelemetry 1.52.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46442

**関連リンク**:
- Commits:
  - [a124466](https://github.com/spring-projects/spring-boot/commit/a124466be27eb6d673174091e22354acdb549b24)

### 内容

Upgrade to [OpenTelemetry 1.52.0](https://github.com/open-telemetry/opentelemetry-java/releases/tag/v1.52.0).

Supersedes #46341

---

## Issue #46443: Upgrade to Reactor Bom 2025.0.0-M5

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46443

**関連リンク**:
- Commits:
  - [2cc3580](https://github.com/spring-projects/spring-boot/commit/2cc3580bf618b0cd1dd24fceab13c5df5cd31f8f)

### 内容

Upgrade to [Reactor Bom 2025.0.0-M5](https://github.com/reactor/reactor/releases/tag/2025.0.0-M5).

---

## Issue #46444: Add internal dependency management for gRPC

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46444

**関連リンク**:
- Commits:
  - [3331046](https://github.com/spring-projects/spring-boot/commit/3331046306782d23ce7e81f57d22829767f6de09)

### 内容

Two modules are using `testRuntimeOnly("io.grpc:grpc-api:1.72.0")`. For consistency, this version should be managed in a single place.

---

## Issue #46445: Upgrade to Okhttp 5.1.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46445

**関連リンク**:
- Commits:
  - [c8d700c](https://github.com/spring-projects/spring-boot/commit/c8d700c5a726aa3ce92b3571be8d4115a6241692)

### 内容

This is required as the upgrade to OpenTelemetry upgraded to this version and we're still on v4.

---

## Issue #46449: SNI integration tests are not using configured repositories

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-17

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46449

**関連リンク**:
- Commits:
  - [fd3ee71](https://github.com/spring-projects/spring-boot/commit/fd3ee711947bc540edcbd5e21b1a6bf670518c3f)

### 内容

Forward port of issue #46448 to 4.0.x.

---

## Issue #46454: Changelog reference for Commons Lang3 does not create valid links

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-17

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46454

**関連リンク**:
- Commits:
  - [55de634](https://github.com/spring-projects/spring-boot/commit/55de6341729c9d20118dbbcbe177ccbc26bef041)

### 内容

Forward port of issue #46453 to 4.0.x.

---

## Issue #46459: Restore disabled test that validates incremental execution of a Spring Batch job

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-18

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-boot/issues/46459

**関連リンク**:
- Commits:
  - [548b44f](https://github.com/spring-projects/spring-boot/commit/548b44f75e51557b1df79e6bc8c1659988dc5e2b)

### 内容

A test was [recently disabled](https://github.com/spring-projects/spring-boot/commit/8fdf94c2c906e9553dd64808705a83d54e01dec4) due to a regression in Spring Batch. The regression has been fixed in the meantime, but the scenario we're testing is invalid and lead to a warning. Unfortunately, we can't fix the test to not produce the warning.

We should re-enable the test once https://github.com/spring-projects/spring-batch/issues/4914 is fixed (and not used parameters).

---

## Issue #46463: Upgrade to Couchbase Client 3.8.2

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-18

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46463

**関連リンク**:
- Commits:
  - [4c80446](https://github.com/spring-projects/spring-boot/commit/4c80446431b3024c9bdab45d5b2808a03a14518e)

### 内容

Upgrade to [Couchbase Client 3.8.2](https://docs.couchbase.com/java-sdk/current/project-docs/sdk-release-notes.html).

---

## Issue #46464: Upgrade to Infinispan 15.2.5.Final

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-18

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46464

**関連リンク**:
- Commits:
  - [b3af15d](https://github.com/spring-projects/spring-boot/commit/b3af15d882eb84c968b23c7c65820335578bd475)

### 内容

Upgrade to [Infinispan 15.2.5.Final](https://github.com/infinispan/infinispan/releases/tag/15.2.5.Final).

---

## Issue #46465: Upgrade to Spring Data Bom 2025.1.0-M4

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-18

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46465

**関連リンク**:
- Commits:
  - [a2f7d98](https://github.com/spring-projects/spring-boot/commit/a2f7d98b64d44d8ad1840b5f2829b3a70c15a764)

### 内容

Upgrade to [Spring Data Bom 2025.1.0-M4](https://github.com/spring-projects/spring-data-bom/releases/tag/2025.1.0-M4).

---

## Issue #46475: LambdaSafe.withFilter is not public

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-21

**ラベル**: type: bug, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46475

**関連リンク**:
- Commits:
  - [a53524d](https://github.com/spring-projects/spring-boot/commit/a53524d8b6a2bc48582871b290282ae45d85ae93)

### 内容

Forward port of issue #46474 to 4.0.x.

---

## Issue #46481: Additional fields for structured JSON logging incompatible with nested ecs logging in 3.5.x

**状態**: closed | **作成者**: philwebb | **作成日**: 2025-07-22

**ラベル**: type: bug, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46481

**関連リンク**:
- Commits:
  - [4c72ce6](https://github.com/spring-projects/spring-boot/commit/4c72ce69dae52876e32b06a470c60fe12eb91328)

### 内容

Forward port of issue #46351 to 4.0.x.

---

## Issue #46482: Move test kit dirs out of temp directory

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-22

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46482

**関連リンク**:
- Commits:
  - [c91b1a6](https://github.com/spring-projects/spring-boot/commit/c91b1a6652aab5f6a8d6db4d839a30bf89ae3305)

### 内容

Forward port of issue #46480 to 4.0.x.

---

## Issue #46485: Migrate to central.sonatype.com

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46485

**関連リンク**:
- Commits:
  - [52becac](https://github.com/spring-projects/spring-boot/commit/52becac192c047132db324c65ab93ee35f0f9a5c)

### 内容

Forward port of issue #46484 to 4.0.x.

---

## Issue #46488: Upgrade to Spring HATEOAS 3.0.0-M3

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46488

**関連リンク**:
- Commits:
  - [f80b897](https://github.com/spring-projects/spring-boot/commit/f80b8971a7c63203b85dd7f9ecac21c8f076d107)

### 内容

Upgrade to [Spring HATEOAS 3.0.0-M3](https://github.com/spring-projects/spring-hateoas/releases/tag/3.0.0-M3).

Supersedes #45489

---

## Issue #46490: Configure MySQL with a same-major upgrade policy

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2025-07-22

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46490

**関連リンク**:
- Commits:
  - [b81bb9e](https://github.com/spring-projects/spring-boot/commit/b81bb9e11335f95c04f02c993f47a91dafb36e28)

### 内容

Forward port of issue #46489 to 4.0.x.

---

## Issue #46495: Upgrade to Artemis 2.42.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46495

**関連リンク**:
- Commits:
  - [feede5d](https://github.com/spring-projects/spring-boot/commit/feede5d689725900374f22e34ed98f0750549519)

### 内容

Upgrade to [Artemis 2.42.0](https://activemq.apache.org/components/artemis/download/release-notes-2.42.0).

Supersedes #46324

---

## Issue #46496: Upgrade to Flyway 11.10.3

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46496

**関連リンク**:
- Commits:
  - [2a37168](https://github.com/spring-projects/spring-boot/commit/2a371685213973189d3175ea576de93bb696f3dd)

### 内容

Upgrade to [Flyway 11.10.3](https://documentation.red-gate.com/flyway/release-notes-and-older-versions/release-notes-for-flyway-engine).

Supersedes #46326

---

## Issue #46497: Upgrade to HikariCP 6.3.1

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46497

**関連リンク**:
- Commits:
  - [a0df48f](https://github.com/spring-projects/spring-boot/commit/a0df48f4ed82d070913d58a9eba943d2367472db)

### 内容

Upgrade to HikariCP 6.3.1.

---

## Issue #46498: Upgrade to Jackson Bom 2.19.2

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46498

**関連リンク**:
- Commits:
  - [80496ce](https://github.com/spring-projects/spring-boot/commit/80496cee02ebfa4cc0934a8ce14cb954b0f6be50)

### 内容

Upgrade to [Jackson Bom 2.19.2](https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.19.2).

---

## Issue #46499: Upgrade to JUnit Jupiter 5.13.4

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46499

**関連リンク**:
- Commits:
  - [ab08dc6](https://github.com/spring-projects/spring-boot/commit/ab08dc6123e137b2b2817780e47b877793ea267f)

### 内容

Upgrade to [JUnit Jupiter 5.13.4](https://junit.org/junit5/docs/5.13.4/release-notes).

Supersedes #46330

---

## Issue #46500: Upgrade to Liquibase 4.33.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46500

**関連リンク**:
- Commits:
  - [e1eead2](https://github.com/spring-projects/spring-boot/commit/e1eead2badba419ec893c8cdbe456b85a94fa01f)

### 内容

Upgrade to [Liquibase 4.33.0](https://github.com/liquibase/liquibase/releases/tag/v4.33.0).

Supersedes #46333

---

## Issue #46502: Upgrade to Rabbit AMQP Client 5.26.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46502

**関連リンク**:
- Commits:
  - [f2ccfa8](https://github.com/spring-projects/spring-boot/commit/f2ccfa800ca19f7be6ca73dd476bf166c66a36c2)

### 内容

Upgrade to [Rabbit AMQP Client 5.26.0](https://github.com/rabbitmq/rabbitmq-java-client/releases/tag/v5.26.0).

---

## Issue #46503: Upgrade to SQLite JDBC 3.50.3.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46503

**関連リンク**:
- Commits:
  - [b546b03](https://github.com/spring-projects/spring-boot/commit/b546b0347fd4e75a4e12486d565a7a0810a4a16b)

### 内容

Upgrade to [SQLite JDBC 3.50.3.0](https://github.com/xerial/sqlite-jdbc/releases/tag/3.50.3.0).

---

## Issue #46507: The release-milestone workflow does not set the mandatory commercial attribute of the create-github-release action

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-22

**ラベル**: type: task, status: forward-port

**URL**: https://github.com/spring-projects/spring-boot/issues/46507

**関連リンク**:
- Commits:
  - [e798924](https://github.com/spring-projects/spring-boot/commit/e798924d2cb5bc81ece170f67328c056aaf6aea0)

### 内容

Forward port of issue #46506 to 4.0.x.

---

## Issue #46513: Upgrade to Commons Codec 1.19.0

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-23

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46513

**関連リンク**:
- Commits:
  - [b3e2da2](https://github.com/spring-projects/spring-boot/commit/b3e2da293d7a5109d42d1f867188f50f7578b1ac)

### 内容

Upgrade to [Commons Codec 1.19.0](https://commons.apache.org/proper/commons-codec/changes-report.html#a1.19.0).

---

## Issue #46514: Upgrade to Groovy 4.0.28

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-23

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46514

**関連リンク**:
- Commits:
  - [f4749e0](https://github.com/spring-projects/spring-boot/commit/f4749e07bdf9909864fbf8d484b579d1adc9d320)

### 内容

Upgrade to Groovy 4.0.28.

---

## Issue #46515: Upgrade to Hibernate 7.0.7.Final

**状態**: closed | **作成者**: snicoll | **作成日**: 2025-07-23

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-boot/issues/46515

**関連リンク**:
- Commits:
  - [41a4ab0](https://github.com/spring-projects/spring-boot/commit/41a4ab03c7a8b138450c9ff283d3b74e9206fddc)

### 内容

Upgrade to [Hibernate 7.0.7.Final](https://github.com/hibernate/hibernate-orm/releases/tag/7.0.7).

Supersedes #46438

---

## Issue #46518: spring-boot-starter-restclient + spring-boot-starter-test gives compliation error

**状態**: closed | **作成者**: anbusampath | **作成日**: 2025-07-23

**ラベル**: type: task, type: blocker

**URL**: https://github.com/spring-projects/spring-boot/issues/46518

**関連リンク**:
- Commits:
  - [4ca7854](https://github.com/spring-projects/spring-boot/commit/4ca785470ea0695d1a40a4d05e59623c515dd1e3)

### 内容

When new spring-boot-starter-restclient used along with spring-boot-starter-test gives compilation error. If spring-boot-starter-test removed from the dependencies application works fine. 

Sample with compilation error - https://github.com/anbusampath/2025-07-22-declarative-interface-clients-in-spring-boot-4

Sample without spring-boot-starter-test - https://github.com/anbusampath/2025-07-22-declarative-interface-clients-in-spring-boot-4/tree/without-spring-boot-starter-test

I guess exclusion from spring-boot-starter-test impacting the transtive dependency of spring-boot-starter-restclient.

<img width="426" height="172" alt="Image" src="https://github.com/user-attachments/assets/c33d494c-b987-43bb-9400-7f31236b9fb6" />

### コメント

#### コメント 1 by wilkinsona

**作成日**: 2025-07-23

Thanks for reporting this. https://github.com/spring-projects/spring-boot/commit/108ca64989d87a46e62b2de88acc1a9f3b9727f8 introduced the problem. That change was later refined in https://github.com/spring-projects/spring-boot/commit/1758f509bce9d4f5b32a9bd1c8428738cc1ae751. I'm not sure what we can do instead, but we'll have to do something.

#### コメント 2 by wilkinsona

**作成日**: 2025-07-24

Fixed by 96ff9e59adc68dbd9949fbfc3594a67045559000.

---

