# Spring Batch GitHub Issues

取得日時: 2025年12月31日 13:18:27

取得件数: 39件

---

## Issue #17778: Upgrade core framework build to JDK 17

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2015-07-02

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/17778

**関連リンク**:
- Commits:
  - [33cddef](https://github.com/spring-projects/spring-framework/commit/33cddef026ad7a8c86eac0195377d67f00b37674)
  - [b74e938](https://github.com/spring-projects/spring-framework/commit/b74e93807e0443d30cd1a7c5a8671ceae27e3178)

### 内容

**[Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller)** opened **[SPR-13186](https://jira.spring.io/browse/SPR-13186?redirect=false)** and commented

#### Resources

- [JDK 9 early access builds](https://jdk9.java.net/download/)
- [Gradle 3.0 nightly builds](http://gradle.org/gradle-nightly-build/)
  - [nightly release notes](https://docs.gradle.org/nightly/release-notes)
- [Gradle JDK 9 Support](https://github.com/gradle/gradle/blob/master/design-docs/jdk9-support.md) wiki page

---

**Issue Links:**
- #17928 Compatibility with merged JDK 9 mainline (_**"depends on"**_)
- #19138 Upgrade build to Gradle 3.0 (_**"depends on"**_)
- #18092 Remove AbstractJpaTests and revise spring-orm test suite accordingly (_**"depends on"**_)
- #18079 Declare Spring modules with JDK 9 module metadata (_**"is depended on by"**_)
- #17779 Support for new JDK 9 HTTP Client API (_**"is depended on by"**_)

2 votes, 12 watchers


### コメント

#### コメント 1 by spring-projects-issues

**作成日**: 2016-06-15

**[Sam Brannen](https://jira.spring.io/secure/ViewProfile.jspa?name=sbrannen)** commented

Hi [Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller),

I've got some good news...

If you remove the `-Werror` flag from `compileJava.options*.compilerArgs` in `build.gradle`, it is once again possible to start _smoke testing_ against OpenJDK 9 Early Access builds using [Gradle 3.0 nightly builds](http://gradle.org/gradle-nightly-build/).

```
$> gradlew wrapper --gradle-distribution-url=https://services.gradle.org/distributions-snapshots/gradle-3.0-20160615000025+0000-bin.zip
$> gradlew -version
$> gradlew clean test
```

Of course, lots of things don't work, such as: JAXB, XmlBeans, AspectJ, JRuby, our shadow ClassLoader for JPA tests, etc.

As an experiment, however, I was able to get the JAXB support in Spring OXM to compile by declaring the following dependencies in `spring-oxm/oxm.gradle`.

```java
xjc 'javax.xml.bind:jaxb-api:2.2.11'
xjc 'com.sun.xml.bind:jaxb-core:2.2.11'
xjc 'com.sun.xml.bind:jaxb-impl:2.2.11'
xjc 'com.sun.xml.bind:jaxb-xjc:2.2.11'
xjc 'javax.activation:activation:1.1.1'
```

So.... happy testing! ;)

p.s., I read elsewhere that the preferred way to reference the _current_ JAXB dependencies (without referencing com.sun.*) is as follows:

- `org.glassfish.jaxb:jaxb-xjc:2.2.11`
- `org.glassfish.jaxb:jaxb-runtime:2.2.11`



#### コメント 2 by spring-projects-issues

**作成日**: 2017-06-19

**[Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller)** commented

For the time being, we're going to stay on a JDK 8 build. Technically we only have a need to build on JDK 9 once we decide to ship `module-info` descriptors, and it looks like we'll be able to live with `Automatic-Module-Name` entries (#18289) up until Spring Framework 6.


#### コメント 3 by spring-projects-issues

**作成日**: 2018-11-02

**[Rostislav Krasny](https://jira.spring.io/secure/ViewProfile.jspa?name=rosti)** commented

[Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller), I think the minimum JDK version for Spring Framework 6 building should be JDK 11 because this is the first Long Term Support (LTS) version of JDK after JDK 8. JDK 9 and JDK 10 had very short term support and are already dead, i.e. they are unsupported by Oracle. I think the title of this Jira ticket should be updated accordingly.


#### コメント 4 by spring-projects-issues

**作成日**: 2018-11-04

**[Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller)** commented

Good point, once we upgrade the Java baseline for Spring Framework 6, we'll certainly aim for JDK 11+ right away. However, from where we stand right now, this is unlikely to happen before 2021 (when JDK 17 is on the horizon as the next LTS release, providing us with a target support range of two LTS generations of Java again).


#### コメント 5 by jhoeller

**作成日**: 2021-09-15

Repurposing this issue for our JDK 17 baseline in Spring Framewor 6.0, the basics have been covered by a few recent commits already, e.g. through #26901.

#### コメント 6 by jhoeller

**作成日**: 2021-12-14

Closing this issue for 6.0 M1 since all the basic upgrade is complete.
Further steps towards the Java module system are planned for a later milestone, e.g. #18079.

---

## Issue #19846: Add support for instant in @DateTimeFormat

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2017-02-22

**ラベル**: in: web, in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/19846

**関連リンク**:
- Commits:
  - [110e0f7](https://github.com/spring-projects/spring-framework/commit/110e0f7f2b0a07699a96bf6410299d95635b2f63)

### 内容

**[Krzysztof Krason](https://jira.spring.io/secure/ViewProfile.jspa?name=krzyk)** opened **[SPR-15280](https://jira.spring.io/browse/SPR-15280?redirect=false)** and commented

`@DateTimeFormat` annotation is supported by all Java 8 time classes except Instant, which always assumes the date is in the format "2017-02-21T13:00:00Z".

Right now when making a request with **start** set to **2017-02-21T13:00**, following code works (uses LocalDateTime):

```
@RestController
public final class ReportController {

    @RequestMapping(path = "/test", method = RequestMethod.GET)
    public String report(
        @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd'T'HH:mm") LocalDateTime start) {
    return start.toString();
}
```

But following doesn't (fails with parsing exception):

```
@RestController
public final class ReportController {

    @RequestMapping(path = "/test", method = RequestMethod.GET)
    public String report(
        @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd'T'HH:mm") Instant start) {
    return start.toString();
}
```



---

**Affects:** 4.3.6

1 votes, 2 watchers


### コメント

#### コメント 1 by spring-projects-issues

**作成日**: 2017-03-15

**[Krzysztof Krason](https://jira.spring.io/secure/ViewProfile.jspa?name=krzyk)** commented

Any updates here? Is this behavior intentional?


#### コメント 2 by spring-projects-issues

**作成日**: 2018-09-28

**[Krzysztof Krason](https://jira.spring.io/secure/ViewProfile.jspa?name=krzyk)** commented

[Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller) Any updates?


#### コメント 3 by YuryYaroshevich

**作成日**: 2019-05-09

I assume the main difficulty in implementing this feature is passing zone id(since you can't format an Instant without zone id: https://stackoverflow.com/questions/25229124/format-instant-to-string) to this formatter:
https://github.com/spring-projects/spring-framework/blob/master/spring-context/src/main/java/org/springframework/format/datetime/standard/InstantFormatter.java#L42
which is registered here: https://github.com/spring-projects/spring-framework/blob/master/spring-context/src/main/java/org/springframework/format/datetime/standard/DateTimeFormatterRegistrar.java#L192

#### コメント 4 by eldarj

**作成日**: 2023-01-26

How come this actually doesn't work for me?

The exact same above sample throws an parser exception
```@RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd'T'HH:mm") Instant start```

What I noted is that `Instant.parser` is the one that tries to parse the request param, and not the `TemporalAccessorParser` - is this expected?

Secondly, the `Instant.parser` doesn't make any use of the pattern supplied in `@DateTimeFormat` annotation, it actually always expect the following `yyyy-MM-dd'T'HH:mm:ssz' for example `2022-10-10T10:00:00Z`

@snicoll any ideas? 

#### コメント 5 by sbrannen

**作成日**: 2023-01-26

@eldarj, this issue was closed over a year ago.

If you feel that you have encountered a bug, please create a new issue and provide a minimal example that reproduces the behavior.

As for why `Instant.parse(...)` would be invoked without taking into account a custom format, that can happen in a fallback scenario in which `org.springframework.format.datetime.standard.TemporalAccessorParser.defaultParse(String)` is invoked.

#### コメント 6 by eldarj

**作成日**: 2023-01-27

@sbrannen Thanks a lot for the quick tip, and sure, I'll double check further and open a new issue if needed. Ty!

---

## Issue #20269: Enable support for custom vnd types in messaging MappingJackson2MessageConverter [SPR-15712]

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2017-06-27

**ラベル**: in: messaging, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/20269

**関連リンク**:
- Commits:
  - [b7cd049](https://github.com/spring-projects/spring-framework/commit/b7cd049d7d0c03496ee9d958590c1f7e1af8b5aa)

### 内容

**[Vinicius Carvalho](https://jira.spring.io/secure/ViewProfile.jspa?name=vcarvalho)** opened **[SPR-15712](https://jira.spring.io/browse/SPR-15712?redirect=false)** and commented

The current implementation of converters will not allow conversion of vnd types such as application/vnd.springframework.type+json, although one could set the custom types beforehand, it is useful at least on Spring Cloud Stream use cases that we could support any type that has +json on the payload.

using subtypes from MimeType would not work as json and vnd... will be consider different types.

Spring AMQP takes a different approach using just a simple contains for the word json on the content type.

It would be nice to have some sort of support on this core component and avoid another snowflake implementation on Spring Cloud Stream to override the default behavior.


---

**Affects:** 4.3.9


### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2021-09-07

We can add `"application/*+json"` as a supported MIME type, just like in the same converter for HTTP. 

---

## Issue #20606: Unable to use WebTestClient with mock server in Kotlin

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2017-10-10

**ラベル**: in: test, type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/20606

**関連リンク**:
- Commits:
  - [dc5a21f](https://github.com/spring-projects/spring-framework/commit/dc5a21fbd1d59a573b7385cdeb92d3bc103672a1)

### 内容

**[Daniel Jones](https://jira.spring.io/secure/ViewProfile.jspa?name=jonesd9)** opened **[SPR-16057](https://jira.spring.io/browse/SPR-16057?redirect=false)** and commented

I'm trying to set up a Kotlin/Spring project using Spring Boot 2.0.0.M4 and Spring Framework 5.0.0.M4 and have ran into trouble with `WebTestClient` in a mocked-server test.

Essentially the following in Java works fine:

```java
class JavaHelper {
    static WebTestClient getMockWebTestClient(ApplicationContext ctx) {
        return WebTestClient.bindToApplicationContext(ctx)
                            .apply(springSecurity())
                            .configureClient()
                            .filter(basicAuthentication())
                            .build();
    }
}
```

But Kotlin is unable to infer the type T of apply method:

```java
<T extends B> T apply(MockServerConfigurer configurer)
```

With the following code:

```java
WebTestClient.bindToApplicationContext(context)
                .apply(springSecurity())
                .configureClient()
                .filter(basicAuthentication())
                .build()
```

The problem is to do with the generic typings, I'm still fairly new to Kotlin but if I write my test using the same package as `ApplicationContextSpec` (since they're package-private) and do the following, it works as expected:

```java
(WebTestClient.bindToApplicationContext(context) as ApplicationContextSpec)
                .apply<ApplicationContextSpec>(springSecurity())
                .configureClient()
                .filter(basicAuthentication())
                .build()
```

I think the following:

```java
static MockServerSpec<?> bindToApplicationContext(ApplicationContext applicationContext) {
    return new ApplicationContextSpec(applicationContext);
}
```

should be changed to return `ApplicationContextSpec` (or at least `AbstractMockServerSpec<ApplicationContextSpec>`):

and make the class `ApplicationContextSpec` public. The constructor can still be default visibility so users won't be able to misuse the class outside of the defined API, and users in Kotlin will be able to import it for type inference.

---

**Affects:** 5.0 GA

**Issue Links:**
- #20945 Upgrade to Kotlin 1.3 (_**"depends on"**_)
- #20251 Kotlin unable to inherit type for WebTestClient#BodySpec

**Referenced from:** commits https://github.com/spring-projects/spring-framework/commit/b9a0e6bbf2b6fe5f0ed222f506efc644d0d9a4f0

2 votes, 11 watchers


### コメント

#### コメント 1 by spring-projects-issues

**作成日**: 2017-10-10

**[Daniel Jones](https://jira.spring.io/secure/ViewProfile.jspa?name=jonesd9)** commented

I've added a test repo here:

https://github.com/dan-j/kotlin-reactive-test-SPR-16057


#### コメント 2 by spring-projects-issues

**作成日**: 2017-10-27

**[Sébastien Deleuze](https://jira.spring.io/secure/ViewProfile.jspa?name=sdeleuze)** commented

I think this is similar to #20251 which was expected to be fixed in Kotlin 1.2 via [KT-5464](https://youtrack.jetbrains.com/issue/KT-5464) and similar to what [Rob Winch](https://jira.spring.io/secure/ViewProfile.jspa?name=rwinch) raised as well, but was sadly postponed to Kotlin 1.3. As reported to JetBrains, this pending issue on Kotlin side makes `WebTestClient` not usable at all with Kotlin, and I have no other workaround to propose than using `WebClient` with non-mocked server for now, Reactor and Spring Kotlin extensions making that quite usable as demonstrated on this [example](https://github.com/sdeleuze/spring-kotlin-deepdive/blob/248c1c89cf5a7a4293adbace296d945637ed0d20/src/test/kotlin/io/spring/deepdive/PostJsonApiTests.kt).

For now I am going to update `WebTestClient` Javadoc to add a warning and a link to JetBrains issue + update our reference documentation with these infos. We will mark this issue as resolved asap we have the confirmation Kotlin 1.3 fixes this issue and our documentation has been updated to specify Kotlin 1.3+ should be used for `WebTestCient`.


#### コメント 3 by spring-projects-issues

**作成日**: 2018-04-17

**[Sébastien Deleuze](https://jira.spring.io/secure/ViewProfile.jspa?name=sdeleuze)** commented

Notice that #20251 is now fixed.


#### コメント 4 by andriipivovarov

**作成日**: 2020-03-13

Any work around?

#### コメント 5 by noah-iam

**作成日**: 2020-06-25

Hey,
For the similar issue , I want to share you my piece of code that is giving me same error :

.webFilter<>(myfilter) . This is saying to give the generic type here.

Error : Type expected

val client: WebTestClient = WebTestClient.bindToWebHandler { Mono.empty() } .webFilter<>(myfilter) .build()

Error : Type argument is not within its bounds. Expected: Nothing! Found: WebFilter!

@sdeleuze can you help me in this 

#### コメント 6 by maresja1

**作成日**: 2020-10-19

@andriipivovarov Work around:

You have to re-define class MutatorFilter (it is a private static class in `SecurityMockServerConfigurers`):

```kotlin
// copy of org.springframework.security.test.web.reactive.server.SecurityMockServerConfigurers.MutatorFilter
internal class MutatorFilter : WebFilter {

    override fun filter(exchange: ServerWebExchange, webFilterChain: WebFilterChain): Mono<Void> {
        val context = exchange.getAttribute<Supplier<Mono<SecurityContext>>>(ATTRIBUTE_NAME)
        if (context != null) {
            exchange.attributes.remove(ATTRIBUTE_NAME)
            return webFilterChain.filter(exchange)
                .subscriberContext(ReactiveSecurityContextHolder.withSecurityContext(context.get()))
        }
        return webFilterChain.filter(exchange)
    }

    companion object {
        const val ATTRIBUTE_NAME = "context"
    }
}
```

And apply:

```kotlin
        WebTestClient.bindToApplicationContext(context)
            .configureClient()
            .baseUrl("https://api.example.com")
            .defaultHeader("Content-Type", MediaType.APPLICATION_JSON_VALUE)
// ...
            .apply { _, httpHandlerBuilder, _ ->
                httpHandlerBuilder?.filters { filters -> filters.add(0, MutatorFilter()) }
            }
```

If anyone knows about a better way, please let me know.

#### コメント 7 by sdeleuze

**作成日**: 2020-10-27

This issue still happens with Kotlin 1.4.10 likely due to [KT-40804](https://youtrack.jetbrains.com/issue/KT-40804) and I agree we should try to find a solution. I am discussing that with Kotlin team.

#### コメント 8 by xetra11

**作成日**: 2021-02-04

Any updates on this?

#### コメント 9 by sdeleuze

**作成日**: 2021-03-25

Both Kotlin and Spring team agreed this issue should be fixed on Kotlin side. My current hope is that it will be fixed in Kotlin 1.6 (Kotlin 1.5 is just around the corner and Kotlin has now a 6 month release cycle so that won't be too far away).

#### コメント 10 by petukhovv

**作成日**: 2021-08-03

Note that we (Kotlin team) supported given cases in the experimental mode in 1.5.30. In 1.5.30 the `-Xself-upper-bound-inference` compiler flag could be used to enabled the corresponding feature.
More information: https://youtrack.jetbrains.com/issue/KT-40804

#### コメント 11 by sdeleuze

**作成日**: 2021-09-07

Indeed seems to work based on my tests, thanks! I will close this issue when we will be based on Kotlin 1.6 in order to add proper test.

@petrukhnov Could you please confirm this will be the default as of Kotlin 1.6?

#### コメント 12 by petukhovv

**作成日**: 2021-09-07

Yes, it's going to be enabled by default since 1.6.

#### コメント 13 by sdeleuze

**作成日**: 2021-10-29

Depends on #27413.

---

## Issue #22093: Upgrade Spring Context Support to Jakarta EE's com.sun.mail:jakarta.mail and com.sun.activation:jakarta.activation [SPR-17561]

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2018-12-04

**ラベル**: in: messaging, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/22093

**関連リンク**:
- Commits:
  - [d84ca2b](https://github.com/spring-projects/spring-framework/commit/d84ca2ba90d27a7c63d7b35a6259b5b9cf341118)
  - [9241039](https://github.com/spring-projects/spring-framework/commit/92410395e3e2eeb8b0b4495465f883a8796d34fa)

### 内容

**[Juergen Zimmermann](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.zimmermann)** opened **[SPR-17561](https://jira.spring.io/browse/SPR-17561?redirect=false)** and commented

Spring Context Support is using _javax.mail:javax.mail-api_ and _javax.activation:javax.activation-api_. Meanwhile there is _com.sun.mail:jakarta.mail_ and _com.sun.activation:jakarta.activation_.


---

**Affects:** 5.1.3


### コメント

#### コメント 1 by spring-projects-issues

**作成日**: 2018-12-04

**[Juergen Hoeller](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.hoeller)** commented

We generally compile against baseline APIs, not necessarily against the latest... except for cases where we need (optional) dependencies on newer interfaces, like with Servlet 4.0 where we compile against 4.0 while retaining 3.1 compatibility at runtime. From that perspective, I see us hanging on to the common EE 7/8 API artifacts as a baseline for the time being.

Is there a specific reason why you'd like us to switch to the Jakarta-provided artifacts? A concrete application project can bring in the Jakarta variant at runtime in any case since we are not enforcing the Oracle-provided artifacts, in particular not for optional dependencies, just using them for compilation purposes as the common reference APIs out there.


#### コメント 2 by spring-projects-issues

**作成日**: 2018-12-04

**[Juergen Zimmermann](https://jira.spring.io/secure/ViewProfile.jspa?name=juergen.zimmermann)** commented

OK, got it. I thought that you are compiling against the latest API versions.


#### コメント 3 by pontello

**作成日**: 2020-05-04

@spring-issuemaster , what is the correct way to tell spring CDI that `jakarta.inject.Inject` plays the same role as `javax.inject.Inject`?

I've researched a lot aboud this topic and haven't figured out an elegant solution for it. Please note that `@AliasFor` isn't an option because I can't annotate jakarta packages. 

---

## Issue #22154: @RequestMapping without @Controller registered as handler [SPR-17622]

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2018-12-23

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/22154

**関連リンク**:
- Commits:
  - [da2bcd8](https://github.com/spring-projects/spring-framework/commit/da2bcd837d58b03e3f696572d656153ee312521c)
  - [93bc27c](https://github.com/spring-projects/spring-framework/commit/93bc27cf2330e07f91a97b2934a0a0ef218cb928)
  - [b0fc461](https://github.com/spring-projects/spring-framework/commit/b0fc46113b4a93d532f56574571005ee3b47afaf)
  - [3bed306](https://github.com/spring-projects/spring-framework/commit/3bed306d1834465c0ea380c188bf9a320c06bc11)
  - [1d82544](https://github.com/spring-projects/spring-framework/commit/1d825440c328ef90b940ba6be8483aec184daeb4)
  - [a6b628a](https://github.com/spring-projects/spring-framework/commit/a6b628ab9a8d712e9aa06e7cb5cd6823d10daa1b)
  - [a791f13](https://github.com/spring-projects/spring-framework/commit/a791f13700da04f1f3fea4e9b2b64570f68d033b)
  - [eee4dd9](https://github.com/spring-projects/spring-framework/commit/eee4dd9f14954bb6fdc6b3198b3fe71c0c34ab3b)
  - [26c5968](https://github.com/spring-projects/spring-framework/commit/26c59681ad8e05cb65d573ca389269cccd13150d)
  - [3600644](https://github.com/spring-projects/spring-framework/commit/3600644ed1776dce35c4a42d74799a90b90e359e)
  - [32b8710](https://github.com/spring-projects/spring-framework/commit/32b87104892bc5d551947af125104b350d00a80b)
  - [436d71d](https://github.com/spring-projects/spring-framework/commit/436d71d01e89fe07508a9fb6b02960bb4acff200)
  - [d87fcfa](https://github.com/spring-projects/spring-framework/commit/d87fcfaf3eb403bb58ec4d71ce329fbbc32c2e00)
  - [18c8d14](https://github.com/spring-projects/spring-framework/commit/18c8d146d88cd00959b69b1071a96ff5496e01dd)

### 内容

**[Eugene Tenkaev](https://jira.spring.io/secure/ViewProfile.jspa?name=hronom)** opened **[SPR-17622](https://jira.spring.io/browse/SPR-17622?redirect=false)** and commented

Following this approach here http://projects.spring.io/spring-cloud/spring-cloud.html#spring-cloud-feign-inheritance

If you add root `@RequestMapping` to the `UserService` it will be registered as handler in Spring MVC application.

Example project to reproduce here https://github.com/Hronom/test-shared-mapping-interface

Related discussions:
* https://github.com/spring-cloud/spring-cloud-netflix/issues/466
* https://stackoverflow.com/questions/29284911/can-a-spring-cloud-feign-client-share-interface-with-an-spring-web-controller

To handle this properly need to avoid registration of controller that has only `@RequestMapping` annotation.

Proposed solution:
Register handler only if it has annotation `@Controller` or `@RestController`.

---

**Affects:** 5.1.3

**Issue Links:**
- #16747 Introduce proxy-based REST client similar to HttpInvokerProxyFactoryBean

1 votes, 3 watchers


### コメント

#### コメント 1 by spring-projects-issues

**作成日**: 2018-12-24

**[Sébastien Deleuze](https://jira.spring.io/secure/ViewProfile.jspa?name=sdeleuze)** commented

I understand the rationale behind what you ask, but class level `@Component` + `@RequestMapping` is supported for a long time, so removing that support would break a lot of applications.

[Rossen Stoyanchev](https://jira.spring.io/secure/ViewProfile.jspa?name=rstoya05-aop) [Arjen Poutsma](https://jira.spring.io/secure/ViewProfile.jspa?name=arjen.poutsma) Could you share your point of view on this change request?


#### コメント 2 by spring-projects-issues

**作成日**: 2018-12-24

**[Eugene Tenkaev](https://jira.spring.io/secure/ViewProfile.jspa?name=hronom)** commented

[Sébastien Deleuze](https://jira.spring.io/secure/ViewProfile.jspa?name=sdeleuze) I have edit description the idea is next:
Make Spring MVC register endpoint **only if** it has `@Controller` or `@RestController` on the class level.

My example shows that:
Right now, if class has only `@RequestMapping` - this class will be registered as the endpoint in Spring MVC.


#### コメント 3 by spring-projects-issues

**作成日**: 2018-12-25

**[Sébastien Deleuze](https://jira.spring.io/secure/ViewProfile.jspa?name=sdeleuze)** commented

I understand, but what I wanted to clarify is that `@RequestMapping` alone does not expose endpoints automatically, but beans with class level `@RequestMapping` annotations does and this is used by developers in various ways, one of these ways being my `@Component` + `@RequestMapping` example.

`@FeignClient` itself is not meta annotated with `@Component`, but I guess it is registered as a bean by `FeignClientFactoryBean` (I have not verified) which is from Spring Framework POV similar to `@Component` + `@RequestMapping` or programmatic bean registration of classes annotated by `@RequestMapping`.

I understand your request for being more restrictive in how we identify REST endpoints, and the issue raised for `@FeignClient` could apply for #16747. But I am also concern by such breaking change, that's why I am asking Rossen and Arjen feedback who have more knowledge and context than me on that topic.


#### コメント 4 by rstoyanchev

**作成日**: 2019-01-18

Class level `@RequestMapping` is used as a hint, independent of `@Controller`, because `@RequestMapping` can be used on an interface, in which case the controller can be an AOP proxy and the `@Controller` annotation is not accessible to Spring MVC through the proxy.

@jhoeller do you see any options to refine the checks, e.g. if type-level `@RequestMapping` is found without `@Controller` and the bean is a proxy, then introspect further to see if we can find the `@Controller` annotation? 

Note also that Spring Data REST has a similar situation for REST endpoints, and it [solves that through](https://docs.spring.io/spring-data/rest/docs/3.1.4.RELEASE/reference/html/#_repositoryresthandlermapping) an additional `RequestMappingHandlerMapping` instance ordered earlier + a special stereotype to identify such endpoints, which works but is probably more involved than it needs to be. We could also try and suppress Spring MVC from treating certain types (based on some criteria) as controllers but again that doesn't seem ideal and requires extra config.



#### コメント 5 by remal

**作成日**: 2019-07-05

This issue leads to a lot of different problems that are very hard to debug. Please fix it. I can suggest these solutions:
1. Do not treat classes annotated by `@RequestMapping` as handlers. Only `@Controller` annotation should be taken into consideration.
1. Spring Data has `@NoRepositoryBean`. A similar annotation can be created for request handlers. For example: `@NoRequestHandler`.
    * In this case `@FeignClient` annotation can be annotated by this `@NoRequestHandler` annotation.

I'd suggest implementing the first solution.

#### コメント 6 by TannnnnnnnnnnnnnnnK

**作成日**: 2020-04-16

regist handler and regist requestmapping
two different things, should be separate from each other, even they are related

#### コメント 7 by glockbender

**作成日**: 2020-06-16

This issue is still relevant. Any progress with that?

#### コメント 8 by odrotbohm

**作成日**: 2020-07-14

Copying the description of #25386 here for reference:

**tl;dr** – The current behavior is problematic for folks trying to customize Spring Data REST using custom controllers, too, as it subtley makes controllers using `@RequestMapping` on the type level end up in the wrong handler mapping

Rossen mentioned that [here](https://github.com/spring-projects/spring-framework/issues/22154#issuecomment-455561279) already, but it just recently came up in StackOverflow questions again.

> `RequestMappingHandlerMapping.isHandler(…)` not only picks up types annotated with `@Controller` but also ones that are annotated with `@RequestMapping` on the type level. This is problematic in cases in which other `HandlerMapping` instances are registered that might be supposed to handle those controllers.
>
> A prominent example of this is Spring Data REST, which registers a dedicated mapping to expose HTTP resources for Spring Data repositories. Users can selectively override those resources by declaring a controller themselves and just declare a handler method for e.g. the URI of an item resource and an HTTP verb of choice. If that controller now declares an `@RequestMapping` on the type level, the Spring MVC registered one will pick up that class, and not see any other mappings defined for the same URI pattern but exposing support for other HTTP methods potentially available in subsequent `HanderMapping` implementations.
> 
> This is a pretty common error scenario reported by users (see [this StackOverflow](https://stackoverflow.com/questions/62865947/restrepositorycontroller-hide-rest-repository-endpoints/62877864) question for example). It's also pretty hard to explain to users as it involves talking about quite a few implementation details.
>
> Removing the explicit handling of `@RequestMapping` on the type level bears the risk that controller implementations not also being annotated with `@Controller` would not be picked up automatically anymore. I haven't found any Spring MVC related documentation that actually shows an example of code not using the annotations in combination when used at the type level. A fix for that issue would be to also annotate the affected controller type with `@Controller`. I can see this being suboptimal for a release in a minor version but for 6.0 we should at least reevaluate.

#### コメント 9 by mothinx

**作成日**: 2020-11-12

Just get this issue with a feign client and spent a lot of hours to locate it. Is someone on that issue ?

#### コメント 10 by odrotbohm

**作成日**: 2020-12-18

This just came up in yet another Spring Data REST issue: https://jira.spring.io/browse/DATAREST-1591.

#### コメント 11 by rstoyanchev

**作成日**: 2021-10-06

**Team Decision:** after some cross-team discussions, for the short term the issue will be addressed on the side of Spring Data REST and Spring Cloud.

For Spring Framework 6.0, we will also address this in the Spring Framework by no longer considering a class with a type-level `@RequestMapping` as a candidate for detection, unless there is also `@Controller`. 


#### コメント 12 by remal

**作成日**: 2021-10-06

@rstoyanchev do you know if there is a corresponding ticket in Spring Cloud that can be subscribed to?

#### コメント 13 by rstoyanchev

**作成日**: 2021-10-14

@remal, yes you can follow here https://github.com/spring-cloud/spring-cloud-openfeign/issues/547.

#### コメント 14 by OrangeDog

**作成日**: 2024-01-23

Just to note that the previous behaviour allowed declaring and constructing the controller with a `@Bean` method. Now that you have to add `@Controller` to the class, they are automatically declared by `@ComponentScan`, which will now need additional exclusion filters.

---

## Issue #25354: Support for Jakarta EE 9 (annotations and interfaces in jakarta.* namespace)

**状態**: closed | **作成者**: zenbones | **作成日**: 2020-07-02

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/25354

**関連リンク**:
- Commits:
  - [b88ed7f](https://github.com/spring-projects/spring-framework/commit/b88ed7f4bb719a71a4a6fb9442e8dc731159c331)
  - [4a89ac7](https://github.com/spring-projects/spring-framework/commit/4a89ac7a213f7bd97b4b53291fd2f56ac91622e5)
  - [d84ca2b](https://github.com/spring-projects/spring-framework/commit/d84ca2ba90d27a7c63d7b35a6259b5b9cf341118)
  - [555807e](https://github.com/spring-projects/spring-framework/commit/555807ea9c632522240b871b025dd9448e837c58)
  - [f4ede92](https://github.com/spring-projects/spring-framework/commit/f4ede9200955646e32ffb30118c833c0a762d918)
  - [19ce194](https://github.com/spring-projects/spring-framework/commit/19ce194fc46709372e022de614d22e6081718217)

### 内容

What is the timing for the switch to the jakarta.* namespaced dependencies in JEE9? Is there a version I can use or build that's made that change?

### コメント

#### コメント 1 by jhoeller

**作成日**: 2020-07-02

We have no immediate plans to make such a switch, and also no plans for an early access branch. Our upcoming Spring Framework 5.3 generation will be compatible with Java 8+ and based on the javax-namespaced EE 8 APIs still, for immediate use in current production environments. Beyond that, Spring Framework 6 is likely to adopt the jakarta namespace at a later point.

The jakarta-namespaced APIs are not final yet and we expect a long time to go by before all major providers support them in production releases. We not only need Tomcat, Jetty and Undertow but also EclipseLink, Hibernate ORM and Hibernate Validator to provide major releases here, plus several special-purpose providers and libraries, before we can consider a version of Spring based on jakarta-namespaced APIs. Since there is no relevant value add in EE 9's namespace change per se, backwards compatibility with existing application servers and persistence providers through the javax namespace is more important to us.

That said, if you have a production-targeting stack scenario where our continued use of the javax namespace is an issue, please elaborate. We are aware that the upcoming Tomcat 10 cannot be supported quite yet and recommend sticking with Tomcat 9.0.x (which is feature-equivalent with Tomcat 10, just still based on the javax namespace) for the time being.

#### コメント 2 by krzyk

**作成日**: 2021-04-02

HIbernate validator 7.x made a switch to jakarta.* namespace and now I have issue I have to choose if I want hibernate validation to work or Spring validation.

Isn't it really possible to support both javax.* and jakarta.* namespace? Or is there a workaround for this I could implement in my code?

#### コメント 3 by andrei-ivanov

**作成日**: 2021-04-02

You can use HV 6.2: https://in.relation.to/2021/01/06/hibernate-validator-700-62-final-released/

#### コメント 4 by krzyk

**作成日**: 2021-04-02

yes, but I would need to rename all packages jakarta.validation back to javax.

Considering that the release was in December I think it would be good to add both jakarta and javax packages in the validation.

I was hoping: Copy that bean from Spring source, and rename javax there to jakarta and it will magically work :)

#### コメント 5 by jhoeller

**作成日**: 2021-04-02

I'm afraid this won't work in a per-spec fashion, at least not for us as framework provider. We need to make the move to Jakarta EE 9 and the `jakarta` namespace for all EE APIs at the same time, otherwise it'll just be a mess in terms of API interoperability and also in terms of commercial support. You may copy and paste individual classes on your own, of course, but this is not recommended and we won't officially support this for the time being.

It is generally understood that the Eclipse-Foundation-enforced namespace switch in Jakarta EE 9 is a huge breaking change that will take years for the ecosystem to broadly adopt. That's exactly why many product providers chose to release two versions in parallel, e.g. Tomcat 9 vs 10, Jetty 10 vs 11, and also Hibernate Validator 6.2 vs 7. Each respective pair of releases is largely feature-equivalent, just differing in the package namespace that those releases work with. Making use of those latest javax-based releases is what we strongly recommend in the meantime, before Spring Framework 6 and Spring Boot 3 will make the general upgrade to Jakarta EE 9+ next year.

#### コメント 6 by Sudha-84

**作成日**: 2021-07-07

Is there any ETA on this? I greatly appreciate your response.

#### コメント 7 by jhoeller

**作成日**: 2021-07-07

No ETA yet, I'm afraid, just rough guidance that Spring Framework 6 and Spring Boot 3 will become generally available in 2022. We'll certainly release a first 6.0 milestone in Q4 2021 still but the final production releases are at least a year away. For the time being, we aim to support the **latest javax-based versions of all common open source projects in our actively developed Spring Framework 5.3.x line**, with Boot 2.4 and 2.5 (and also the upcoming Boot 2.6 and 2.7 releases) building on it.

Please note that this is in alignment with the rest of the open source ecosystem and also the Java industry overall. As outlined above, while some open source projects have early Jakarta EE 9 based releases already, they keep mainline Java/Jakarta EE 8 based releases in parallel which are feature equivalent and will be maintained for a long time still. This is also the case for the recently released Hibernate ORM 5.5, for example. **We strongly recommend staying on EE 8 for the time being.**

#### コメント 8 by Sudha-84

**作成日**: 2021-07-13

Thanks for your response

#### コメント 9 by mckramer

**作成日**: 2021-07-20

@jhoeller from a hibernate-validator perspective, that artifact has actually already upgraded to jakarta dependencies in 6.1.x, which Spring has moved to already.  Maybe that was not known, but Spring does have transient dependencies on jakarta.* now.

[spring-framework javax validation-api@2.0.1.Final](https://github.com/spring-projects/spring-framework/blob/main/build.gradle#L270)
[spring-framework hibernate-validator@6.2.0.Final](https://github.com/spring-projects/spring-framework/blob/main/build.gradle#L126)

[hibernate-validator jakarta.validation-api@2.0.2](https://github.com/hibernate/hibernate-validator/blob/6.2.0.Final/pom.xml#L347)

This introduces a conflict as spring sits today.  Is that intentional?

#### コメント 10 by spencergibb

**作成日**: 2021-07-20

> Hibernate Validator 6.x will keep the javax. packages while Hibernate Validator 7.x moved to the jakarta. packages.

From the article linked in a comment above https://github.com/spring-projects/spring-framework/issues/25354#issuecomment-812572313

#### コメント 11 by MCMicS

**作成日**: 2021-07-21

@mckramer Hibernate 6.x still use javax. The 2.0.2 version of `jakarta.validation-api` contains the javax packages. it will be renamed with 3.x version

#### コメント 12 by jhoeller

**作成日**: 2021-07-21

@mckramer It's confusing, unfortunately. Jakarta-provided artifacts may contain `javax.` or `jakarta.` APIs, depending on the version.

Jakarta EE 8 is effectively a repackaging of Java EE 8, preserving not only the `javax` namespace but also the existing major version numbers of the individual APIs (e.g. bumping the Validation API from 2.0.1 to 2.0.2), remaining compatible with existing API usage at the source and binary level, just suggesting different Maven coordinates for the build artifacts.

Jakarta EE 9 and higher actually repackage the APIs into the `jakarta` namespace at the Java interface level, forcing all downstream projects to adapt their code. That's the new baseline that we will pick up in Spring Framework 6 and Spring Boot 3, supporting common open source projects which provide established versions on that baseline by then (e.g. Tomcat, Jetty, Hibernate but possibly dropping support for a few other servers and libraries which might remain stuck on EE 8).

#### コメント 13 by mckramer

**作成日**: 2021-07-21

Right, the concern isn't with the change in "api", but rather that Hibernate >= 6.1.x uses the jakarta artifact.  Despite it still being the same package/classes under the covers, it is a separate artifact.  As a result, the javax validation-api AND jakarta validation-api jars can both end up on the classpath of the final application.  Resulting in duplicate classes.

Applications then are required to try to manage exclusions across many transient dependencies to avoid both jars from being resolved.

The answer may simply be that Spring has a preference to the Jakarta EE 8 packages (as opposed to Java EE 8), and apps should manage as such?  Spring generally simply defines the javax validation-api deps as optional, but contains managed versions for both artifacts.

#### コメント 14 by SushmitaGoswami

**作成日**: 2022-03-04

Is there any updates on this? May we know when will spring move to jakarta? Any approximate quarter?

#### コメント 15 by martin-g

**作成日**: 2022-03-04

Spring 6.x moved to Jakarta APIs.
M1 has been released several months ago.

#### コメント 16 by sbrannen

**作成日**: 2022-03-04

@SushmitaGoswami, see related blog post:

https://spring.io/blog/2021/09/02/a-java-17-and-jakarta-ee-9-baseline-for-spring-framework-6

---

## Issue #25582: @Transactional does not work on package protected methods of CGLib proxies

**状態**: closed | **作成者**: odrotbohm | **作成日**: 2020-08-12

**ラベル**: in: data, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/25582

**関連リンク**:
- Commits:
  - [9efa99e](https://github.com/spring-projects/spring-framework/commit/9efa99e0d84759d321c1676f0f4ac7d43f125eda)
  - [37bebea](https://github.com/spring-projects/spring-framework/commit/37bebeaaaf294ef350ec646604124b5b78c6e690)
  - [c8a4026](https://github.com/spring-projects/spring-framework/commit/c8a40265128ceb56af2176911d46dcc1e92f9a39)

### 内容

`AnnotationTransactionAttributeSource` contains a flag whether to only consider public methods, set to `true` by default. I assume that stems from the times when JDK proxies where the primary way of applying proxies and with those only public methods can be intercepted anyway.

With CGLib proxies this is different. Package private methods *can* be invoked on the proxy and properly make their way through the AOP infrastructure. However, the lookup of transaction attributes is eagerly aborted due to the flag mentioned above. This creates confusing situations (assume `@EnableGlobalMethodSecurity` and `@EnableTransactionManagement` applied):

```java
@Component
class MyClass {

  @Secured(…)
  @Transactional
  void someMethod() { … }
}
```

In this example, the security annotations *are* applied as the security infrastructure does not work with a flag like this and the advice is registered for the method invocation. The transactional annotations are *not* applied, as the method is not inspected for transactional annotations in the first place.

I wonder if it makes sense to flip the flag based on the `proxyTargetClass` attribute in `@EnableTransactionManagement`. If that is set to true, CGLib proxies are created and thus, transaction annotations should be regarded on package protected methods. This seems to be especially important in the context of Spring Boot setting this flag to `true` by default.

A current workaround is demonstrated in [this commit](https://github.com/quarano/quarano-application/commit/4d4e8239de7ee0a4a6b7ef4af1b8431932dee8b5), which uses a `PriorityOrdered` `BeanPostProcessor` to reflectively flip the flag, not considering any configuration as in that particular case we know we're always gonna run with CGLib proxies.

### コメント

#### コメント 1 by sbrannen

**作成日**: 2020-08-14

FWIW, the TestContext framework actually sets the flag to `false` in order to support package-private `@Test` methods in TestNG and JUnit Jupiter.

https://github.com/spring-projects/spring-framework/blob/13183c89ce1eb178793e542753cd78f3d9908164/spring-test/src/main/java/org/springframework/test/context/transaction/TransactionalTestExecutionListener.java#L151

I'd be in favor of making production changes here (as an opt-in feature). In light of that, I've added the `for: team-attention` label.

#### コメント 2 by odrotbohm

**作成日**: 2020-08-14

> I'd be in favor of making production changes here (as an opt-in feature).

I really don't think it should be an opt-in fix as it currently creates an inconsistency in the applicability of annotations to methods as shown above. Also, you don't have to explicitly enable this for other annotations, why would you have to in this particular case?

I guess the reason that this has been overseen for so long is that folks are used to make everything and the world `public` in the first place even on code that doesn't need to be public (mostly due to misguidance by their IDEs).

#### コメント 3 by sbrannen

**作成日**: 2020-08-14

> > I'd be in favor of making production changes here (as an opt-in feature).
> 
> I really don't think it should be an opt-in fix as it currently creates an inconsistency in the applicability of annotations to methods as shown above. Also, you don't have to explicitly enable this for other annotations, why would you have to in this particular case?

Then perhaps an opt-in feature for switching it back to the old way, in case the change causes issues for some projects.

> I guess the reason that this has been overseen for so long is that folks are used to make everything and the world `public` in the first place even on code that doesn't need to be public (mostly due to misguided guidance by their IDEs).

Yes, I agree.

#### コメント 4 by odrotbohm

**作成日**: 2020-09-01

Another user stumbling over this: https://stackoverflow.com/questions/63675153/transactional-annotation-doesnt-solve-org-hibernate-lazyinitializationexception

#### コメント 5 by odrotbohm

**作成日**: 2020-10-25

[Here](https://github.com/quarano/quarano-application/blob/c35b48635af42f5a1b1cb3cff573ffcf477b47ed/backend/src/main/java/quarano/Quarano.java#L90-L139)'s how I currently work around the issue in a project. I get hold of the `AnnotationTransactionAttributeSource` very early in the bean lifecycle and flip the `publicMethodsOnly` flag.

#### コメント 6 by andrei-ivanov

**作成日**: 2020-10-25

Maybe you can try this one 😀

> hibernate.enable_lazy_load_no_trans (e.g. true or false (default value))
>
>    Initialize Lazy Proxies or Collections outside a given Transactional Persistence Context.
>    Although enabling this configuration can make LazyInitializationException go away, it’s better to use a > fetch plan that guarantees that all properties are properly initialized before the Session is closed.
>
>    In reality, you shouldn’t probably enable this setting anyway.


---

## Issue #26185: CommonAnnotationBeanPostProcessor jakarta.annotation-api:2.0.0 support (@PostConstruct/Predestroy)

**状態**: closed | **作成者**: qeepcologne | **作成日**: 2020-12-01

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/26185

**関連リンク**:
- Commits:
  - [d84ca2b](https://github.com/spring-projects/spring-framework/commit/d84ca2ba90d27a7c63d7b35a6259b5b9cf341118)

### 内容

I tried to upgrade jakarta.annotation:jakarta.annotation-api from 1.3.5 to 2.0.0
The annotations moved from package javax.annotation to jakarta.annotation.
After the Upgrade @PostConstruct and @PreDestroy are not working.
Please let annotations from both packages work in CommonAnnotationBeanPostProcessor.

### コメント

#### コメント 1 by jhoeller

**作成日**: 2020-12-01

I'm afraid there are no plans for such parallel support for both EE namespaces in the Spring Framework 5.x generation. While we could rather easily implement this for `@PostConstruct` and `@PreDestroy`, it's harder for `@Inject` and its `Provider` interface already, requires duplicated modules for JPA and JMS, and is effectively impossible for Spring MVC on the Servlet API. We intend to do a full switch in the Spring Framework 6 generation (see #25354), possibly along with support for Jakarta EE 10 next year.

Please note that Jakarta EE 9 is a plain repackaging and does not provide new features yet. What's your motivation for using the Commons Annotations API 2.0 over 1.3 there? In what way is that one worth upgrading in a singular fashion while consuming the other EE APIs from the `javax` namespace still?

#### コメント 2 by qeepcologne

**作成日**: 2020-12-01

Thanks for the quick response and the detailed explanations.
There is no requirement for the upgrade, i just prefer gradual upgrade over big bang. Otherwise upgrade (tomcat10,spring,spring-security, jakarta apis and probably a lot more) is such a big brick and not integrated timely.
I already switched some apis like jakarta.mail-api and jakarta.xml.bind-api and nearly none of these run smoothly without changes.

#### コメント 3 by hantsy

**作成日**: 2020-12-06

Before Spring framework moving to the Jakarta EE 9/10 stack. I hope Spring can consider releasing a Jakarta EE 9.0 version alongside the Jakarta EE 8.0 release(eg. a Maven artifact classifier **jakartaee9** or a specific version) at the same time.
There are several projects that used [Eclipse Transformer tooling](https://projects.eclipse.org/projects/technology.transformer) to transfer the existing work to Jakarta EE 9, such as Apache TomEE, WildFly 22.0.0 Jakarta EE preview.

#### コメント 4 by hantsy

**作成日**: 2020-12-06

I created an issue for this, https://github.com/spring-projects/spring-framework/issues/26224

---

## Issue #26901: Remove support for deprecated Java SecurityManager

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-05-06

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/26901

**関連リンク**:
- Commits:
  - [cf2429b](https://github.com/spring-projects/spring-framework/commit/cf2429b0f0ce2a5278bdc2556663caf6cf0b0cae)

### 内容

Anticipating https://openjdk.java.net/jeps/411, we should simply remove all of our optional SecurityManager code paths in the core container.

---

## Issue #27072: Allow BeanUtils#instantiateClass inlining with native

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2021-06-17

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27072

**関連リンク**:
- Commits:
  - [2fba0bc](https://github.com/spring-projects/spring-framework/commit/2fba0bc27268d863f04734b96bdce331dad57438)

### 内容

See related comment [here](https://github.com/oracle/graal/issues/2500#issuecomment-860330959). Per @jhoeller guidance, `LinkageError` should be rare enough to allow `BeanUtils#instantiateClass` not catching it. See also #27070 related issue.

---

## Issue #27409: Switch CI pipeline to a JDK17 baseline

**状態**: closed | **作成者**: bclozel | **作成日**: 2021-09-15

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27409

**関連リンク**:
- Commits:
  - [c0e4794](https://github.com/spring-projects/spring-framework/commit/c0e479460e09b7065a21ebfbd95cec7d213ca62e)
  - [a216415](https://github.com/spring-projects/spring-framework/commit/a2164151839221c0e9b090bd3f6422b77798cb6b)

### 内容

As announced on the spring.io blog, [Spring Framework 6.0 will require JDK17 as a baseline](https://spring.io/blog/2021/09/02/a-java-17-and-jakarta-ee-9-baseline-for-spring-framework-6).

As a result, the default build pipeline should use JDK17 (with future variants for JDK18+) and the published artifacts should use the Java 17 language level.

This task should refactor the current CI pipeline to:
* only ship 17+ JDKs in the CI container image
* consistently use Java 17 language level for compiling main and test sources
* for now, Kotlin doesn't officially support Java 17, so we'll move to JDK 11 for now

---

## Issue #27413: Upgrade to Kotlin 1.6.10

**状態**: closed | **作成者**: bclozel | **作成日**: 2021-09-15

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27413

**関連リンク**:
- Commits:
  - [c0e4794](https://github.com/spring-projects/spring-framework/commit/c0e479460e09b7065a21ebfbd95cec7d213ca62e)
  - [bb53a99](https://github.com/spring-projects/spring-framework/commit/bb53a99defc5ec70393ff21a8a40f74d650e2e1a)
  - [a216415](https://github.com/spring-projects/spring-framework/commit/a2164151839221c0e9b090bd3f6422b77798cb6b)

### 内容

As seen in #27409, this change also implies switching to a JDK17 baseline for compiling Kotlin code.

### コメント

#### コメント 1 by bclozel

**作成日**: 2021-10-27

Waiting for https://youtrack.jetbrains.com/issue/KT-49329

#### コメント 2 by bclozel

**作成日**: 2021-12-14

I've created #27814 as a follow up.

---

## Issue #27422: Drop RPC-style remoting: Hessian, HTTP Invoker, JMS Invoker, JAX-WS

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-09-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27422

**関連リンク**:
- Commits:
  - [b9ca350](https://github.com/spring-projects/spring-framework/commit/b9ca350f6d9197bf2456f5fd8ef2d44b62987a11)
  - [5822f1b](https://github.com/spring-projects/spring-framework/commit/5822f1bf85b94fd15f9829914b065b1c61910c7d)
  - [774583d](https://github.com/spring-projects/spring-framework/commit/774583dfa7dba5c3440c4a1341809ab2f3a88780)
  - [960a4c8](https://github.com/spring-projects/spring-framework/commit/960a4c8fc9045b1fcf152c45783a17142199ffed)

### 内容

Since most of our RPC-style remoting support has been officially and/or effectively deprecated for several years, let's remove it for 6.0 M1 right away (which also reduces subpackage overload in several modules a bit).

### コメント

#### コメント 1 by knoobie

**作成日**: 2023-04-05

@jhoeller Are there any recommended strategies documented by Spring how to get JAX-WS working with the latest Spring Framework / Boot again? Especially removal of `ignoreResourceType("javax.xml.ws.WebServiceContext");` (now jakarta.*) breaks integration with CXF 4.0 by default if `WebServiceContext`is injected as `@Resource` with no clear migration path how to overcome this.

#### コメント 2 by snicoll

**作成日**: 2023-04-05

As stated above, it's been deprecated for several years and now removed so we can't recommend anything about those.

#### コメント 3 by knoobie

**作成日**: 2023-04-05

@snicoll Thanks for your comment! I'm aware of the deprecating and removal of RPC-style remoting (I'm totally find with that). I just came across this commit because it also removed JAX-WS "Integration" which I think is not deprecated and still heavily used. For example from the CXF 4 / Jakarta 9+ Migration, there is this open issue that lead me to this change: https://issues.apache.org/jira/browse/CXF-8666

My current workaround is to customize the `CommonAnnotationBeanPostProcessor`and re-introduce the deleted line. 

```java
@Configuration
public class WorkaroundForCxfConfig {

  @Autowired
  private CommonAnnotationBeanPostProcessor processor;

  @PostConstruct
  public void initialize() {
    processor.ignoreResourceType("jakarta.xml.ws.WebServiceContext");
  }
}
```



#### コメント 4 by snicoll

**作成日**: 2023-04-05

>  JAX-WS "Integration" which I think is not deprecated and still heavily used.

Our JAX-WS integration is deprecated and has been removed as a result, so whatever you were relying on from there is not available anymore. This isn't the right place to discuss CXF issues either, please raise that on the proper support channel.

#### コメント 5 by Osmanbell

**作成日**: 2024-10-13

yes

---

## Issue #27423: Drop outdated Servlet-based integrations: Commons FileUpload, FreeMarker JSP support, Tiles

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-09-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27423

**関連リンク**:
- Commits:
  - [d3738e1](https://github.com/spring-projects/spring-framework/commit/d3738e131bd67aaaa0785e5da97626d7708c4f18)
  - [047f660](https://github.com/spring-projects/spring-framework/commit/047f66057217be3971f02974c4744f7940ff3d74)
  - [d84ca2b](https://github.com/spring-projects/spring-framework/commit/d84ca2ba90d27a7c63d7b35a6259b5b9cf341118)

### 内容

Several integration options in our web support date back to the 2005 era, not having seen maintenance in recent years and apparently not getting an upgrade for Jakarta Servlet (in the `jakarta.servlet` package namespace). As part of our Jakarta EE 9+ revision, we'll therefore drop support for CommonsMultipartResolver, FreeMarkerServlet-style JSP taglib support and Tiles views.

---

## Issue #27424: Support for Jetty 11

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-09-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27424

**関連リンク**:
- Commits:
  - [958eb0f](https://github.com/spring-projects/spring-framework/commit/958eb0f964ddef1ff1440fd10c5cb850f6ee96db)
  - [513cc15](https://github.com/spring-projects/spring-framework/commit/513cc1576e5860b5bd953351850cabd1a0d6e385)
  - [d84ca2b](https://github.com/spring-projects/spring-framework/commit/d84ca2ba90d27a7c63d7b35a6259b5b9cf341118)
  - [b732ff3](https://github.com/spring-projects/spring-framework/commit/b732ff349509d2b174978c71fe522ee6aa6b57a8)
  - [853ab5d](https://github.com/spring-projects/spring-framework/commit/853ab5d67b3336ae73ad962da7a60b19cc455667)
  - [8b5f5d9](https://github.com/spring-projects/spring-framework/commit/8b5f5d9f653d0656787e285065f5bdd66fc9427e)
  - [5eac855](https://github.com/spring-projects/spring-framework/commit/5eac8555d9b115b40d6de6b2c8f935ffc35864de)
  - [48875dc](https://github.com/spring-projects/spring-framework/commit/48875dc44fc019350a3b02bd9d04ade583021523)

### 内容

As part of our Jakarta EE 9 revision, we need to support Jetty 11 which turns out to be a significant area of work after our previous adaptive support for Jetty 9/10.

---

## Issue #27425: Remove JiBX support

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-09-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27425

**関連リンク**:
- Commits:
  - [3c8724b](https://github.com/spring-projects/spring-framework/commit/3c8724ba3d0375e4a50354c15383972fee788e9c)

### 内容

Following up on #22249, JiBX support will be removed for Spring Framework 6 now.

---

## Issue #27426: Remove Joda-Time support

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-09-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27426

**関連リンク**:
- Commits:
  - [b7b078d](https://github.com/spring-projects/spring-framework/commit/b7b078d26e4eea472f753b3027d86ddba183b3b9)
  - [4d792d0](https://github.com/spring-projects/spring-framework/commit/4d792d0e459ba2667dbbbcff051b7abcddc37b46)

### 内容

Following up on #25736, Joda-Time support will be removed for Spring Framework 6 now.

### コメント

#### コメント 1 by nealeu

**作成日**: 2025-10-29

Bit behind the times on helping someone do 5.x to 6 and hit their Spring Hateoas missing formatters. 
Can you add this at https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-6.0-Release-Notes pls?

---

## Issue #27443: Remove support for RxJava 1 and 2

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-09-21

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27443

**関連リンク**:
- Commits:
  - [e611234](https://github.com/spring-projects/spring-framework/commit/e6112344d20b9a744ca44073cc1331a0a9e691b4)
  - [3beb074](https://github.com/spring-projects/spring-framework/commit/3beb07427817069d405f22729c4f0c35b67f7948)

### 内容

Following up on #19628, we're finally removing RxJava 1.x support from Spring's `ReactiveAdapterRegistry` since it has been superseded not only by RxJava 2.x but even RxJava 3.x in the meantime.

As per a later note, we're also removing RxJava 2.x support right away since RxJava 2 reached EOL itself in February 2021 already.

### コメント

#### コメント 1 by jhoeller

**作成日**: 2021-09-27

Reopening for removing RxJava 2.x support - which reached EOL in February 2021 - as well, since it'll be 1.5 years by the time we go GA.

---

## Issue #27444: Retain support for legacy JSR-250 `javax.annotation.PostConstruct`/`PreDestroy` and JSR-330 `javax.inject.Inject` in addition to Jakarta EE 9 annotations

**状態**: closed | **作成者**: mp911de | **作成日**: 2021-09-21

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27444

**関連リンク**:
- Commits:
  - [774583d](https://github.com/spring-projects/spring-framework/commit/774583dfa7dba5c3440c4a1341809ab2f3a88780)

### 内容

After migration to Jakarta EE 9, it's easy to miss that `javax.annotation.PostConstruct` or `javax.inject.Inject` are no longer working when not covered by a test. This can be an easy-to-make bug when these annotations reside on the classpath after migrating to Jakarta EE 9. 

It would be neat to support both annotation variants for at least a grace period or to fail fast when these annotations are in use.

### コメント

#### コメント 1 by mdeinum

**作成日**: 2021-09-22

Would it make sense to, next to retain support, log a warning if the legacy JSR-250 annotations are detected? As to warning/incentive to the user to migrate to the Jakarta annotations? 

---

## Issue #27464: Change default driver in XStreamMarshaller from XppDriver to DomDriver

**状態**: closed | **作成者**: sbrannen | **作成日**: 2021-09-24

**ラベル**: in: data, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27464

**関連リンク**:
- Commits:
  - [30efa4d](https://github.com/spring-projects/spring-framework/commit/30efa4d478d6673ecfc735bef1ce65decadf4e77)

### 内容

## Overview

As explained in commit a247b83cd9c9aefd3c329d493c5ce7cd11d0cdfa, the `XppDriver` from XStream relies on the XPP3 library which publishes `javax.xml.namespace.QName` as part of its JAR. The `QName` type is also published by the `java.xml` system module in modular JREs (i.e., Java 9 or higher).

This results in a _split package_ between the `unnamed` module and the `java.xml` system module, which the Java Language Specification defines as illegal (see [§6.5.5.2](https://docs.oracle.com/javase/specs/jls/se11/html/jls-6.html#jls-6.5.5.2) and [§7.4.3](https://docs.oracle.com/javase/specs/jls/se11/html/jls-7.html#jls-7.4.3)).

Most Java compilers do not currently enforce this rule; however, the Eclipse compiler does. This makes it impossible to use `spring-oxm` out-of-the-box in the Eclipse IDE. In addition, if bug [JDK-8215739](https://bugs.openjdk.java.net/browse/JDK-8215739) is fixed in a future version of OpenJDK, this rule will affect all users of `spring-oxm`.

In light of that, the team has decided to switch the default driver in `XStreamMarshaller` from `XppDriver` to `DomDriver`. Users can naturally switch back to the `XppDriver` if they wish, since the `defaultDriver` is configurable.

## Deliverables

- [x] Change default driver in `XStreamMarshaller` from `XppDriver` to `DomDriver`.
- [x] Revert related changes in a247b83cd9c9aefd3c329d493c5ce7cd11d0cdfa.

---

## Issue #27487: AbstractJpaVendorAdapter refers to JPA 2.1 but requires JPA 3.0

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2021-09-28

**ラベル**: in: data, type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27487

**関連リンク**:
- Commits:
  - [ac5dc69](https://github.com/spring-projects/spring-framework/commit/ac5dc698e2f0f6f758983f1af3039eea627ef54d)

### 内容


**Affects:** 6.0 snapshots

`AbstractJpaVendorAdapter` refers to JPA 2.1 but it now requires JPA 3.0. Similarly, `HibernateJpaVendorAdapter` describes support for Hibernate 5.2, 5.3, and 5.4. I believe it now requires a minimum of 5.5 as that's the earliest version that has `-jakarta` variants of its modules and supports JPA 3.0.

---

## Issue #27496: Use default stylesheet for generated Javadoc HTML

**状態**: closed | **作成者**: sbrannen | **作成日**: 2021-09-29

**ラベル**: type: documentation

**URL**: https://github.com/spring-projects/spring-framework/issues/27496

**関連リンク**:
- Commits:
  - [aa5a2a8](https://github.com/spring-projects/spring-framework/commit/aa5a2a860045b84457f8b6e596ebb54cf8863d36)
  - [8e245e4](https://github.com/spring-projects/spring-framework/commit/8e245e4410f0d017794828660c05b448efb3cd4e)

### 内容

The Javadoc for Spring Framework 6.0 currently does not have proper styling, since we switched from JDK 8 to JDK 17.

https://docs.spring.io/spring-framework/docs/6.0.0-SNAPSHOT/javadoc-api/index.html

### コメント

#### コメント 1 by xixingya

**作成日**: 2021-10-14

I want to fix the style but I can not find the index.html

#### コメント 2 by sbrannen

**作成日**: 2021-10-14

> I want to fix the style but I can not find the index.html

`index.html` is generated by the `javadoc` tool.

#### コメント 3 by xixingya

**作成日**: 2021-10-15

> > I want to fix the style but I can not find the index.html
> 
> `index.html` is generated by the `javadoc` tool.

thanks, I will try

#### コメント 4 by sbrannen

**作成日**: 2021-10-20

As stated in commit 8e245e4410f0d017794828660c05b448efb3cd4e, the team has decided to use the default Javadoc stylesheet with JDK 17.

---

## Issue #27537: Upgrade to AspectJ 1.9.8-RC3

**状態**: closed | **作成者**: sbrannen | **作成日**: 2021-10-08

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27537

**関連リンク**:
- Commits:
  - [2fb3f99](https://github.com/spring-projects/spring-framework/commit/2fb3f9993f34c561223c5dc3b35537d78020e21d)
  - [fa3a2dc](https://github.com/spring-projects/spring-framework/commit/fa3a2dc98142d397c8394e93d79749f345c149a7)

### 内容

## Overview

AspectJ 1.9.8 RC1 was [released](https://github.com/eclipse/org.aspectj/issues/79#issuecomment-938499393) today, so we'll start testing against that and upgrade to 1.9.8 GA once it's been released.

## Resources

- preliminary [release notes](https://htmlpreview.github.io/?https://github.com/eclipse/org.aspectj/blob/29b024efe4cb4db803103aa099d60b9bc85bac6c/docs/dist/doc/README-198.html)

## Deliverables

- Upgrade to AspectJ 1.9.8 GA
- Add note to reference manual regarding changes to LTW support (see AspectJ 1.9.8 release notes for details)


### コメント

#### コメント 1 by kriegaex

**作成日**: 2021-10-09

Thanks for adopting the new AspectJ version so quickly. I am looking forward to your feedback. Not knowing what the minimum Java version is in your build system, please note the following caveat:

* The Eclipse Java Compiler (ECJ) 3.2.7 supporting Java 17 now needs JDK 11+ as a build environment, because Eclipse migrated the code base to Java 11. Because the AspectJ Compiler (AJC) contained in `aspectjtools` is an ECJ fork, using a Java-17-enabled AJC version (1.9.8.RC1 and higher) means that you need to run your build on JDK 11+. You can still compile to goals as low as Java 1.3, don't worry. It is only about the build environment. I am not sure if you even use AJC or depend on the AspectJ Tools library anywhere, please check.

* As for LTW, I just verified that for now, the class files contained in the smaller `aspectjweaver` agent library still do not contain any Java 11 class files, i.e. LTW should still work on JDK 8 systems.

#### コメント 2 by sbrannen

**作成日**: 2021-10-10

> Thanks for adopting the new AspectJ version so quickly. I am looking forward to your feedback. 

You're welcome. We're glad to help integration test with the RC before the GA release.

Our build is working fine with the changes in fa3a2dc98142d397c8394e93d79749f345c149a7.

> Not knowing what the minimum Java version is in your build system, please note the following caveat:

For Spring Framework 6.0 (`main`), Java 17 is the baseline for the build and any applications using Spring 6.0.


#### コメント 3 by jhoeller

**作成日**: 2021-12-14

I'm about to close this issue with an upgrade to AspectJ 1.9.8 RC3 (for 6.0 M1). We can track the AspectJ 1.9.8 GA upgrade in #27416 then.

---

## Issue #27580: Revisit MediaType ordering

**状態**: closed | **作成者**: poutsma | **作成日**: 2021-10-19

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27580

**関連リンク**:
- Commits:
  - [259bcd6](https://github.com/spring-projects/spring-framework/commit/259bcd60fbbc5cdb8b230595a5004707f4c6ff23)
  - [fa59834](https://github.com/spring-projects/spring-framework/commit/fa59834fa7a173033748d608a75b9cca248d9605)
  - [f55bebc](https://github.com/spring-projects/spring-framework/commit/f55bebce35af304025accaa1e04f4d8d96af8787)
  - [a3aeefa](https://github.com/spring-projects/spring-framework/commit/a3aeefa7433dbc28ec8f0e668ffb816dfa9c0433)
  - [6dc8cde](https://github.com/spring-projects/spring-framework/commit/6dc8cdeb5b5dfc3b6e775c2979fa09e29d104d4f)
  - [9b3e46d](https://github.com/spring-projects/spring-framework/commit/9b3e46d193ad384a122cdef894c4aa8a625484e7)
  - [9a71fd1](https://github.com/spring-projects/spring-framework/commit/9a71fd10085c1820b75c6e6fe96635aa27ba7aed)
  - [6d91360](https://github.com/spring-projects/spring-framework/commit/6d9136013e5bf6f5655f9d8a3c68a7501e9a816c)
  - [2c90851](https://github.com/spring-projects/spring-framework/commit/2c908519d77662b9991c633d0bf9f92f9530cab7)
  - [177b292](https://github.com/spring-projects/spring-framework/commit/177b29226d6c1c8df127c8aedbf5e7a0d57d6f6c)

### 内容

We should reconsider the way we order `MediaType` objects. Currently we use `Comparator`s to sort media types in order of preference, but those need to be transitive (see #27488). We should investigate other ordering mechanisms for 6.0, possibly dropping the comparators altogether in favor of a less restrictive, though possibly slower, ordering algorithm.

---

## Issue #27607: Add JDK18 build variant to CI pipeline

**状態**: closed | **作成者**: bclozel | **作成日**: 2021-10-25

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27607

**関連リンク**:
- Commits:
  - [6fd0615](https://github.com/spring-projects/spring-framework/commit/6fd0615be9003a86c4ac5a0cb89e78aac4cc83f6)
  - [683bdf2](https://github.com/spring-projects/spring-framework/commit/683bdf2675c2a2a9664e913579cfdb883bfc186f)
  - [65bf5f7](https://github.com/spring-projects/spring-framework/commit/65bf5f7c81fb35f3291a548e9d326a65e331e5eb)

### 内容

_本文なし_

---

## Issue #27608: Create immutable MultiValueMap wrapper

**状態**: closed | **作成者**: poutsma | **作成日**: 2021-10-25

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27608

**関連リンク**:
- Commits:
  - [0a58419](https://github.com/spring-projects/spring-framework/commit/0a58419df4fee5e50b6831c065c1a14bedc5f5f8)
  - [af4e677](https://github.com/spring-projects/spring-framework/commit/af4e677bfc61921123385af55887f3ad1ab0ab4b)

### 内容

Currently, `CollectionUtils::unmodifiableMultiValueMap` returns an (unmodifiable) copy of the target map, and therefore allocates extra memory. We cannot use the `Collections.unmodifiableMap` wrapper in said method, because each value of the map should be immutable as well, and thus needs a `Collections.unmodifiableList` wrapper.

We should create a `UnmodifiableMultiValueMap` wrapper, similar to the JDK `Collections`, that wraps entries and values with immutable counterparts where needed.

---

## Issue #27637: Add method to ClientResponse that returns Mono terminating with createException

**状態**: closed | **作成者**: jwChung | **作成日**: 2021-11-04

**ラベル**: in: web, type: enhancement, status: feedback-provided

**URL**: https://github.com/spring-projects/spring-framework/issues/27637

**関連リンク**:
- Commits:
  - [7794606](https://github.com/spring-projects/spring-framework/commit/7794606305da37e5efbfeded67eb421208492339)

### 内容

[The method `ClientResponse.createException()` returns the `Mono<WebClientResponseException>` type.](https://github.com/spring-projects/spring-framework/blob/main/spring-webflux/src/main/java/org/springframework/web/reactive/function/client/ClientResponse.java#L182) `Mono<Exception>` feels like `Either<Exception, Exception>`. I think that the `Mono<RESULT>` type is actually needed. So, what if there is the `createError` method that returns the `Mono<RESULT>` type in the `ClientResponse` interface?



### コメント

#### コメント 1 by poutsma

**作成日**: 2021-11-19

I can see the point for having a different exception, but can't you just `map` the `WebClientResponseException` to the type you'd like?

#### コメント 2 by jwChung

**作成日**: 2021-11-26

@poutsma Isn't `Mono<T>.onErrorMap/onErrorResume` for that? 

In many cases, a returning value of `createException()` is changed to `Mono<RESULT>` in the following way.

```java
Mono<RESULT> mono = clientResponse.createException().flatMap(e -> Mono.error(new MyException("message", e)));
```

I wish I could just write it down as the following.

```java
Mono<RESULT> mono = clientResponse.createError().onErrorMap(e -> new MyException("message", e));
```

#### コメント 3 by rstoyanchev

**作成日**: 2021-11-30

There is a related example in #27645 that doesn't even involve changing the exception. If you use `createException` from `exchangeToMono` and `exchangeToFlux` we have it documented as returning `Mono.error(response.createException())` but actually you need `response.createException().flatMap(Mono::error)` and that's only to be able to match the generic type of the result. It could also be `response.createException().cast(...)` but either way it's inconvenient.

It would make sense to align `createException` with `Mono#error` in terms of being able to cast to anything. After all an error signal switches from some type `T` to an `Exception` so this is to be expected. WDYT @poutsma?

#### コメント 4 by poutsma

**作成日**: 2021-12-01

Personally I prefer the explicitness that the `Mono<WebClientResponseException>` return type offers, as opposed to a generic type. In the latter case, reading the javadoc of the method is pretty much required to see what it does, and that is not true for the former, which pretty much does what you expect from `createException`.

That said, by looking at #27645, I realise that the current signature is not ideal either and requires the use of a `flatMap`, which is not obvious. There is no reason against having both `createException` and `createError`, so I will add it.

---

## Issue #27664: Consistently replace String encoding names with StandardCharset arguments

**状態**: closed | **作成者**: jhoeller | **作成日**: 2021-11-10

**ラベル**: in: web, in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27664

**関連リンク**:
- Commits:
  - [54bd667](https://github.com/spring-projects/spring-framework/commit/54bd66755c12b7dc7f353796ebe128da98e2831e)

### 内容

On a related note to gh-27646, our `EncodedResource` should consistently be used with `StandardCharsets` arguments instead of String encoding names. Also, there are `URLEncoder`/`URLDecoder` variants with a `Charset` argument in JDK 10+ now.

### コメント

#### コメント 1 by dreis2211

**作成日**: 2021-11-10

Please check https://github.com/spring-projects/spring-framework/pull/27554

#### コメント 2 by jhoeller

**作成日**: 2021-11-10

Oops, sorry for not noticing your PR before, @dreis2211 ... This consistency commit of mine only really covered a single URLEncoder case but the PR #27646 included some URLDecoder changes as well, next to the toString stuff.

If you could rebase #27554 against current main, we'll see how much we're still missing. From a quick glance, there are quite a few hard-coded `"UTF-8"` constants in use against `URLDecoder` still. It'd be great to apply your PR for that purpose!

#### コメント 3 by dreis2211

**作成日**: 2021-11-10

@jhoeller Done

#### コメント 4 by jhoeller

**作成日**: 2021-11-10

@dreis2211 Wow that was quick, thanks for the immediate turnaround!

---

## Issue #27686: Early removal of 5.x-deprecated code

**状態**: closed | **作成者**: snicoll | **作成日**: 2021-11-16

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27686

**関連リンク**:
- Commits:
  - [25feedb](https://github.com/spring-projects/spring-framework/commit/25feedb8701ddac92a239376ccbcf634f54707e2)
  - [4750a94](https://github.com/spring-projects/spring-framework/commit/4750a9430cdae9156d1e7fc32cec2c11ba2b8514)
  - [313c643](https://github.com/spring-projects/spring-framework/commit/313c6431185fcd920113543ab51d69e56e46cd15)
  - [f9f9470](https://github.com/spring-projects/spring-framework/commit/f9f9470e5c18fdbc8510be029dee0d22660d3b96)

### 内容

Removing deprecated code in the `5.x` generation early in the 6.x milestone will give a chance to early adopters to adapt or raise concerns during their migration.

### コメント

#### コメント 1 by jhoeller

**作成日**: 2021-11-17

I'm using this issue for early removal of 5.x-deprecated code in 6.0 M1, meaning a first removal pass with possibly a later one following. There are plenty of obvious candidates to remove right away, mostly dating back to deprecations in the 5.1 line. I intend to leave some 5.2.x and 5.3.x deprecations in place for the time being where external code might commonly refer to it still.

---

## Issue #27689: Update javadoc and reference docs for consistent version and package references to the Jakarta EE 9 APIs

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2021-11-16

**ラベル**: in: messaging, in: data, type: documentation, in: web, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/27689

**関連リンク**:
- Commits:
  - [b88ed7f](https://github.com/spring-projects/spring-framework/commit/b88ed7f4bb719a71a4a6fb9442e8dc731159c331)

### 内容

The javadoc for `WebApplicationInitializer` and `SpringServletContainerInitializer ` references Servlet 3.0 in a few places. It should be Servlet 5 now.

### コメント

#### コメント 1 by jhoeller

**作成日**: 2021-11-17

Along with #27690 and  #27692, I'm also updating other EE doc references for Jakarta EE 9 package names (extending the scope of this issue).

---

## Issue #27690: Update ServletContainerInitializer filename with old `javax` prefix to `jakarta`.

**状態**: closed | **作成者**: marcusdacoregio | **作成日**: 2021-11-16

**ラベル**: in: web, type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27690

**関連リンク**:
- Commits:
  - [555807e](https://github.com/spring-projects/spring-framework/commit/555807ea9c632522240b871b025dd9448e837c58)

### 内容

<!--
!!! For Security Vulnerabilities, please go to https://spring.io/security-policy !!!
-->
**Affects:** 6.0.0-SNAPSHOT

When implementing the `WebApplicationInitializer` interface, the implementation is never called.
This was caused because [this file](https://github.com/spring-projects/spring-framework/blob/main/spring-web/src/main/resources/META-INF/services/javax.servlet.ServletContainerInitializer) is still named with the old `javax` namespace. 

As a workaround, I just added the file with the `jakarta.servlet.ServletContainerInitializer` to my app.

Found that problem while working with Spring Security samples that use the [custom `WebApplicationInitializer` implementation](https://github.com/spring-projects/spring-security/blob/e398fbf2a7585c745a6a8d9d4ae6e980dff33462/web/src/main/java/org/springframework/security/web/context/AbstractSecurityWebApplicationInitializer.java#L74).


---

## Issue #27697: Refactor HttpMethod from enum to class

**状態**: closed | **作成者**: poutsma | **作成日**: 2021-11-18

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27697

**関連リンク**:
- Commits:
  - [d075b43](https://github.com/spring-projects/spring-framework/commit/d075b43412ed86053249a6b82c879bf9f9820084)
  - [df0118d](https://github.com/spring-projects/spring-framework/commit/df0118d097c1692b08b6670542af441aebeb4250)
  - [47041ef](https://github.com/spring-projects/spring-framework/commit/47041ef407fff323c6fabd2511e2e0a3aa719273)
  - [b15b13a](https://github.com/spring-projects/spring-framework/commit/b15b13a68033e00aef52df28d70503e78a7723fb)
  - [5955253](https://github.com/spring-projects/spring-framework/commit/59552533402941d3ec81237e67be387c970cad4f)
  - [c710ada](https://github.com/spring-projects/spring-framework/commit/c710ada6ecfb49071ce5e27b432e885d748443b7)
  - [bc76dea](https://github.com/spring-projects/spring-framework/commit/bc76dea25a05b9ed821416dca401a943cc71035b)
  - [6623b31](https://github.com/spring-projects/spring-framework/commit/6623b31c2197b3a9c1c6fa43e52d09c427de99df)
  - [64eebf8](https://github.com/spring-projects/spring-framework/commit/64eebf86dd6d51ea4672f7f7c82d645538bd2696)
  - [6e335e3](https://github.com/spring-projects/spring-framework/commit/6e335e3a9ff7727dc42e790904ae98a6d0edb7b5)
  - [d370fca](https://github.com/spring-projects/spring-framework/commit/d370fcaa1778bd89f0c5c455a8ba33ceb4e5cedd)
  - [445f25c](https://github.com/spring-projects/spring-framework/commit/445f25c466c64f206f5f141c56a1b7cf63f3a30b)
  - [7a4207c](https://github.com/spring-projects/spring-framework/commit/7a4207cd7bfbe57217b1718111f8c56cb076a34d)
  - [f10998b](https://github.com/spring-projects/spring-framework/commit/f10998b7d24b7f086eab248382faa93c6943a84a)
  - [11d6822](https://github.com/spring-projects/spring-framework/commit/11d682292eeba75c100d1562aab875833929e1d7)
  - [a55c5eb](https://github.com/spring-projects/spring-framework/commit/a55c5eb324f8408ba29a2fecc4bd4c27890357c7)
  - [6f5cdf6](https://github.com/spring-projects/spring-framework/commit/6f5cdf6cab11bf9106e6aa0fbd30d2bf28fa6c33)
  - [88e6544](https://github.com/spring-projects/spring-framework/commit/88e6544d9d3498359b49a2548a1b6ef52b32a5ad)
  - [97625e3](https://github.com/spring-projects/spring-framework/commit/97625e365803526658d47a26cc6f010259154be1)

### 内容

According to [the HTTP specification](https://datatracker.ietf.org/doc/html/rfc2616#section-5.1.1), the HTTP method is not limited to the well known set (GET, HEAD, PUT, POST, etc.), but can also be an "extension-method". Well known extensions include [WebDAV](http://www.webdav.org/specs/rfc4918.html#http.methods.for.distributed.authoring), which added methods like LOCK, COPY, and MOVE.

In Spring Framework, HTTP methods are enumerated in `HttpMethod`. Because this type is an Java `enum`, Spring framework needs several workarounds, to allow for HTTP methods not in the enum, such as having both `HttpRequest::getMethod` as well as `HttpRequest::getMethodValue`.

If we change `HttpMethod` from `enum` to `class`, we no longer need these workarounds. If we make sure that the new `class` has the same methods that `java.lang.Enum` exposes, and given that upgrading to 6.0 requires a recompilation anyway, I believe that now is the time to make this long overdue change.

Note that this issue does *not* include support for non-standard HTTP (i.e. WebDAV) methods in Spring MVC and/or WebFlux. 

### コメント

#### コメント 1 by quaff

**作成日**: 2021-11-25

> such as having both HttpMethod::getMethod as well as HttpRequest::getMethodValue.

`HttpMethod::getMethod` should be `HttpRequest::getMethod`

#### コメント 2 by poutsma

**作成日**: 2021-11-25

@quaff Fixed, thanks!

#### コメント 3 by quaff

**作成日**: 2021-12-01

Can we use `extension-method` for `RequestMapping`?

#### コメント 4 by poutsma

**作成日**: 2021-12-01

> Can we use `extension-method` for `RequestMapping`?

I am not sure what you mean by that, can you elaborate? Because annotations can refer to enum elements but not classes, `RequestMapping` uses the `RequestMethod` enumeration.

#### コメント 5 by quaff

**作成日**: 2021-12-02

> > Can we use `extension-method` for `RequestMapping`?
> 
> I am not sure what you mean by that, can you elaborate? Because annotations can refer to enum elements but not classes, `RequestMapping` uses the `RequestMethod` enumeration.

I mean should `RequestMapping` introduce `String[] methodValue()` to supports `extension-method`?

#### コメント 6 by poutsma

**作成日**: 2021-12-02

> I mean should `RequestMapping` introduce `String[] methodValue()` to supports `extension-method`?

`RequestMapping` uses `RequestMethod`, and that's fine the way it is. As I wrote in the description, we have no intention of supporting non-standard HTTP methods. `HttpMethod` is a lower-level component that is used for our HTTP abstraction, and that did need support for non-standard methods.

#### コメント 7 by tamizh-m

**作成日**: 2024-05-28

Hi @poutsma , After upgrading to Spring 6, I am unable to serialize and deserialize 'HttpMethod' using 'ObjectMapper' because the class does not have a public constructor or a getter for 'name' attribute. This issue did not arise previously when HttpMethod was an enum. Would be helpful if you can provide a workaround for this?

#### コメント 8 by poutsma

**作成日**: 2024-05-28

@tamizh-m Please file a new issue. This issue is closed.

---

## Issue #27701: Retrieve MethodMetadata for all user-declared methods in the order of declaration

**状態**: closed | **作成者**: mp911de | **作成日**: 2021-11-19

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27701

**関連リンク**:
- Commits:
  - [50c7c84](https://github.com/spring-projects/spring-framework/commit/50c7c848860fea9ae1ba8d9ce12a9ee7e2eee45f)

### 内容

Spring Data has a use-case in which it requires a stable method order (ordering of methods within a class file). To detect method ordering, it extended Spring Framework's `ClassMetadata` and ASM visitors to expose `Set<MethodMetadata> getMethods()`.

After removal of `AnnotationMetadataReadingVisitor`, there's no extension point available and Spring Data would have to hold a copy of all involved components to determine the method order.

It would be good to have access to `MethodMetadata` from `ClassMetadata`, ideally as `MethodMetadata[] getMethods()` or `Collection<MethodMetadata>`.

See for further reference:

https://github.com/spring-projects/spring-data-commons/blob/788457c90132ae7ca893791d091279faa8e76abe/src/main/java/org/springframework/data/type/MethodsMetadata.java

https://github.com/spring-projects/spring-data-commons/blob/788457c90132ae7ca893791d091279faa8e76abe/src/main/java/org/springframework/data/type/classreading/DefaultMethodsMetadataReader.java#L121-L162

### コメント

#### コメント 1 by jhoeller

**作成日**: 2021-12-15

I ended up introducing `getDeclaredMethods()` on `AnnotationMetadata` since that is where `getAnnotatedMethods` lives already, and also since `MethodMetadata` includes annotation functionality as well. (The distinction between `ClassMetadata` and `AnnotationMetadata` is outdated in any case, with the present implementation we'll always retrieve full annotation metadata in any case.)

---

## Issue #27734: Enforce Future or void return declaration for each asynchronously executed method (e.g. with class-level @Async)

**状態**: closed | **作成者**: djechelon | **作成日**: 2021-11-25

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27734

**関連リンク**:
- Commits:
  - [9a513cf](https://github.com/spring-projects/spring-framework/commit/9a513cfdea9020c6ed2cf3f37711ed4e31d7c310)

### 内容

https://github.com/spring-projects/spring-framework/blob/79d3f5c64c94a356831916ec78be4296fba92b18/spring-aop/src/main/java/org/springframework/aop/interceptor/AsyncExecutionInterceptor.java#L113-L127

I have found an odd behaviour working with `@Async`-annotated classes in Spring. Please note that **there is** a fundamental error in my code. Unfortunately, this post has to be long and detailed.

Let's say I have already made a synchronous REST API generated by Swagger generator. Following code omits all documentation-level annotations

```java

public interface TaxonomiesApi {
   
    ResponseEntity<GenericTaxonomyItem> disableItem(Integer idTaxonomyType, String idTaxonomy, String appSource);

}
```

This API is easily implemented via `RestTemplate`, but I won't discuss the inner details.

Now, suppose I want to provide an async version to developers consuming the API. What I have done is to create another interface with some search&replace-fu 🥋🥋

```java
@Async
public interface TaxonomiesApiAsync extends TaxonomyApi {
   
    default CompletableFuture<ResponseEntity<GenericTaxonomyItem>> disableItemAsync(Integer idTaxonomyType, String idTaxonomy, String appSource) {
        try {
            return completedFuture(this.disableItem(idTaxonomyType, idTaxonomy, appSource));
        } catch (Exception ex) {
            return failedFuture(ex);
        }
    }
}
```

With the search&replace, I basically created an async-ish version of every method that should be backed by Spring's `@Async` annotation. My original idea was that synchronous methods can be invoked as they are, but if you instantiate `TaxonomiesApiAsync` you also have access to the async version.

I have discovered I made **a fundamental mistake** by applying the `@Async` annotation at interface level when the class contains both sync and async methods. I found that synchronous `disableItem` was performed in the same `@Async` context. Accoding to design (correctly), Spring found the `@Async` annotation at interface level so **every method**, including inherited ones, was invoked asynchronously.

But the method always returned null. By debugging and looking at the code, I found that Spring tries to resolve the return value of the invoked method **only** if it's a `Future`. What if the returned value is a _Present_ object?

That means that if the returned value is not a `Future<ResponseEntity<GenericTaxonomyItem>>` but rather just a `ResponseEntity<GenericTaxonomyItem>` Spring neither throws an exception nor returns that value directly.

Example of working calling code (invoking a different method)

```java
    protected CompletableFuture<Set<TaxonomyLegalEntityDTO>> importTaxonomyLegalEntities(int userId) {
        TaxonomySearchParameters searchParameters = new TaxonomySearchParameters();
        searchParameters.setIdTaxonomyType(amlcProperties.getTaxonomies().getTaxonomyLegalEntitiesId());
        searchParameters.setLogicalState(1);
        return taxonomiesApiAsync.getAllTaxonomyItemsAsync(searchParameters)
                .thenApply(ResponseEntity::getBody)
                .thenApply(taxonomyLegalEntityMasterDbMapping::toLegalEntity) // Costruisco i DTO che voglio utilizzare
                .whenComplete(traceLoggerConsumer("Legal entity"))
                .thenApply(dtos -> taxonomyLegalEntityManager.mergeFromMasterDb(dtos, userId))
                .whenComplete((ignored, ex) -> {
                    if (ex != null)
                        log.error("Error importing legal entities: " + ex.getMessage(), ex);
                })
                .thenApply(TaxonomyMasterDbMergeDTO::getSnapshot);
    }
```

Example of non-working code; the result of the CompletableFuture is always null.
In this code, I decided not to use the executor _embedded_ in the API service, but rather the executor injected in the consuming service. So I ran a sync method in an executor, expecting the same result.

```java
    protected CompletableFuture<Set<TaxonomyLegalEntityDTO>> importTaxonomyLegalEntities(int userId) {
        TaxonomySearchParameters searchParameters = new TaxonomySearchParameters();
        searchParameters.setIdTaxonomyType(amlcProperties.getTaxonomies().getTaxonomyLegalEntitiesId());
        searchParameters.setLogicalState(1);
        return CompletableFuture.supplyAsync(() -> taxonomiesApi.getAllTaxonomyItems(searchParameters), taxonomyBatchImportServiceExecutor)
                .thenApply(ResponseEntity::getBody)
                .thenApply(taxonomyLegalEntityMasterDbMapping::toLegalEntity)
                .whenComplete(traceLoggerConsumer("Legal entity"))
                .thenApplyAsync(dtos -> taxonomyLegalEntityManager.mergeFromMasterDb(dtos, userId))
                .whenComplete((ignored, ex) -> {
                    if (ex != null)
                        log.error("Error importing legal entities: " + ex.getMessage(), ex);
                })
                .thenApply(TaxonomyMasterDbMergeDTO::getSnapshot);
    }
```


Since I spent one hour debugging that problem, I decided to spend more of my after-work time to document the issue here.

**Proposed fix**

In the code I linked, if the `instanceof` check fails the returned value is simply null. I don't yet understand the implications, but what about not unwrapping the value from Future if that's not a future? I mean `return result`

### コメント

#### コメント 1 by mdeinum

**作成日**: 2021-11-26

> In terms of target method signatures, any parameter types are supported. However, the return type is constrained to either `void` or `Future`. In the latter case, you may declare the more specific `ListenableFuture` or `CompletableFuture` types which allow for richer interaction with the asynchronous task and for immediate composition with further processing steps.

The documentation states the limitations in the return types only `void` or `Future`. It doesn't really make sense to allow for a return of a specific type as that would make the method call synchronous again as one would need to do a `Future.get` which is blocking and thus renders the `@Async` useless. 

So I the return type isn't a `Future` it can return `null` because the other allowed return value is `void`. 

As a solution an exception would be better imho with a clear message stating that only `void` or `Future` is supported as a return type. 

#### コメント 2 by rstoyanchev

**作成日**: 2021-11-26

As the documentation states and as @mdeinum pointed out, the return type must `Future` or `void`, or otherwise the calling code has to block anyway, making it pointless to involve an Executor thread, and making asynchronous methods that are meant to be synchronous.

I think this can be closed, unless @jhoeller you see some opportunity to bypass methods that don't return void or Future.


#### コメント 3 by jhoeller

**作成日**: 2021-11-29

I'm inclined to explicitly throw an exception for non-Future/void return type declarations whenever we attempt to execute a method asynchronously. While this may not be much of an issue with an explicit annotated method, a class-level `@Async` declaration is certainly harder to track when some specific method mismatches then.

#### コメント 4 by LifeIsStrange

**作成日**: 2022-01-04

Noob question @jhoeller since I assume you systematically do an instanceof/reflection check, and that *could* incur a slowdown, wouldn't it be better to have this check only enabled on dev/debug mode et disabled on release mode? 

#### コメント 5 by djechelon

**作成日**: 2022-01-04

@LifeIsStrange as you can see in the code, what is done is a `==` check on the `returnType`, which is already available (already reflected). So, it's not going to add any overhead.

As for your question about the `instanceof` performance, I found an [interesting reading](https://stackoverflow.com/questions/103564/the-performance-impact-of-using-instanceof-in-java) and the **tl;dr** says

> In Java 1.8 instanceof is the fastest approach, although getClass() is very close.

Nevertheless, it doesn't apply to this fix.

---

## Issue #27769: Deprecate StringUtils::trimWhitespace

**状態**: closed | **作成者**: poutsma | **作成日**: 2021-12-06

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27769

**関連リンク**:
- Commits:
  - [81af733](https://github.com/spring-projects/spring-framework/commit/81af7330f65bdf009c34f23489d7fd9a45376e3f)

### 内容

PR #27703 has made `StringUtils::trimWhitespace` trivial, as the method now delegates to `String::strip`. The only significance that `trimWhitespace` accepts `null`. We should deprecate `trimWhitespace` in favor of `String::strip`. 

Similarly, we should deprecate `StringUtils::trimLeadingWhitespace` in favor of `String::stripLeading`, and `StringUtils::trimTrailingWhitespace` in favor of `String::stripTrailing`.

---

## Issue #27786: Remove JamonPerformanceMonitorInterceptor support

**状態**: closed | **作成者**: mdeinum | **作成日**: 2021-12-08

**ラベル**: type: task, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/27786

**関連リンク**:
- Commits:
  - [ba468a7](https://github.com/spring-projects/spring-framework/commit/ba468a731fc49a383021d3243e6934d29aa1a802)

### 内容

The [JAMon](https://github.com/stevensouza/jamonapi) project doesn't seem really active anymore. Last update was (almost) 2 years ago, by the time Spring 6 will be released this will be 3 years. I'm not even sure if it fully supports new java versions or API versions released after that. 

In the current day and age there are more sophisticated solutions like JavaMelody, Micrometer, Sentry.io to name a few. It might be of consideration to drop this native support (maybe donate the interceptor to the JAMon project). 

---

## Issue #27813: Deprecate CachingConfigurerSupport and AsyncConfigurerSupport

**状態**: closed | **作成者**: snicoll | **作成日**: 2021-12-14

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27813

**関連リンク**:
- Commits:
  - [2f3a9db](https://github.com/spring-projects/spring-framework/commit/2f3a9dbc685f03ad0fc9f58ba4bb60158c9da24e)

### 内容

With default methods available for the base interface in `5.3.x`, let's deprecated the support classes as these are no longer necessary.

---

## Issue #27815: Upgrade Dokka to 1.6.0

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2021-12-14

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27815

**関連リンク**:
- Commits:
  - [ea9b8c1](https://github.com/spring-projects/spring-framework/commit/ea9b8c1d0f273cc4cadd39fc2a4e24780c7857fb)

### 内容

See https://github.com/Kotlin/dokka/releases/tag/v1.6.0.

---

