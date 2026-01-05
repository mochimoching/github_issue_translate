# Spring Framework GitHub Issues

取得日時: 2025年12月31日 16:03:17

取得件数: 34件

---

## Issue #22609: Prevent @Bean method overloading by default (avoiding accidental overloading and condition mismatches)

**状態**: closed | **作成者**: rfelgent | **作成日**: 2019-03-17

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/22609

### 内容

Hello poeple,

I lost some hours configuring a bean with same id but different properties in java config, as the raised error message was not very helpful.

The bean in question must be created, as it is required via declarative `@DependsOn` configuration.

The error

```
A component required a bean named 'postgresqlContainer' that could not be found.
	- Bean method 'postgresqlContainer' in 'PersistenceConfig.DbServersConfig' not loaded because @ConditionalOnProperty (app.persistence.servers.postgresql.enabled=true) found different value in property 'enabled'
	- Bean method 'postgresqlContainer' in 'PersistenceConfig.DbServersConfig' not loaded because @ConditionalOnProperty (app.persistence.servers.postgresql.enabled=true) found different value in property 'enabled'
```

This config fails:

```java
@Configuration
public class PersistenceConfig {

  @Configuration
  public class DbServersConfig {

    @Bean(value = "postgresqlContainer", initMethod = "start", destroyMethod = "stop")
    @ConditionalOnProperty(prefix = "app.persistence.servers.postgresql", name = "enabled", havingValue = "true")
    public PostgreSQLContainer postgresqlContainer(TCPostgresqlProperties postgresqlProperties) {
        Instance retVal = <do_your_logic>
        return retVal;
    }

    @Bean("postgresqlContainer")
    @ConditionalOnProperty(prefix = "app.persistence.servers.postgresql", name = "enabled", havingValue = "false", matchIfMissing = true)
    public PostgreSQLContainer postgresqlContainer() {
      return null;
    }
  }
}
```

This config works:

```java
@Configuration
public class PersistenceConfig {

  @Configuration
  public class DbServersConfig {

    @Bean(value = "postgresqlContainer", initMethod = "start", destroyMethod = "stop")
    @ConditionalOnProperty(prefix = "app.persistence.servers.postgresql", name = "enabled", havingValue = "true")
    public PostgreSQLContainer  postgresqlContainer(TCPostgresqlProperties postgresqlProperties) {
        Instance retVal = <do_your_logic>
        return retVal;
    }

    @Bean("postgresqlContainer")
    @ConditionalOnProperty(prefix = "app.persistence.servers.postgresql", name = "enabled", havingValue = "false", matchIfMissing = true)
    public PostgreSQLContainer postgresqlContainer2() {
      return null;
    }
  }
}
```

If you name both methods differently (`postgresqlContainer` and `postgresqlContainer2`) then everything works as expected otherwise you get an error.

Is this desired behavior ?

I am unsure if my scenario could indicate a bug, too. I do not know if this problem happens only to `@ConditionalOnProperty` or any other condition like `@ConditionalOnExpression`.

Best regards

### コメント

#### コメント 1 by mbhave

**作成日**: 2019-03-18

@rfelgent I was able to replicate this behavior. It appears to be happening because of [this](https://github.com/spring-projects/spring-framework/blob/master/spring-context/src/main/java/org/springframework/context/annotation/ConfigurationClassBeanDefinitionReader.java#L188) in Spring Framework. That check can cause unpredictable behavior because it depends on the order in which the bean definitions were processed. In the example above, if the bean definition corresponding to the second bean is processed first, it will be loaded as `configClass.skippedBeanMethods.contains(methodName)` will return false. 

I don't think there is anything we can do in Spring Boot about this. We can move it to the Spring Framework issue tracker if the rest of the team think that it's something that can be fixed there.

#### コメント 2 by wilkinsona

**作成日**: 2019-03-19

Framework's behaviour should be predictable thanks to [this logic](https://github.com/spring-projects/spring-framework/blob/0fc0849c0a13eb504cd2f308d3824148f8f36806/spring-context/src/main/java/org/springframework/context/annotation/ConfigurationClassParser.java#L394-L422).

I think it's worth moving this to Framework to consider an enhancement to use something more distinct than the method name when determining if a method has already been skipped. The simple workaround, as you have already noted, @rfelgent, is to avoid overloading `@Bean` methods and use distinct method names instead.

#### コメント 3 by sbrannen

**作成日**: 2019-03-19

@mbhave and @wilkinsona, thanks for the detective work!

I agree that the algorithm in question should take overloaded methods into account and thus track skipped methods based on each method's name plus its formal parameter list.

Let's see if the rest of the team agrees.

#### コメント 4 by jhoeller

**作成日**: 2019-03-19

The current behavior is more or less by design: There is only one bean definition per bean name, so we're conceptutally merging all relevant metadata into one definition per name. Overloaded `@Bean` methods are effectively just like overloaded constructors on a particular bean class, still constituting one bean definition only. And for condition handling, all conditions on all overloaded methods effectively apply to that same single bean. Conditions are not straightforward to isolate per bean method since we'd have to apply them to the overloaded factory method selection instead of to the bean definition.

The general recommendation is indeed not to use overloading but distinct bean/method names. And in the case of overloading, to declare the same annotations on all overloaded methods because that's closest to the actual semantics at runtime. This is not really obvious, so at the very least we need to document this properly... and we could possibly raise exceptions in case of condition mismatches among overloaded methods for the same bean definition, suggesting unified conditions or distinct bean names.

#### コメント 5 by mbhave

**作成日**: 2019-03-19

> Framework's behaviour should be predictable thanks to this logic.

@wilkinsona Sorry, I didn't explain myself very well in the previous comment. The behavior would be predictable for a given class. The unpredictability I was referring was across classes, where the `Condition` would match in some cases and not in others, depending on the order of the methods returned.

#### コメント 6 by fprochazka

**作成日**: 2019-09-04

I'd like to add my two cents - I've just lost several hours trying to debug why one of my beans was not registered (it was declared in a `@Configuration` class by `@Bean` method)... the problem was, I've made a typo and given the two methods the same name... because they had different arguments I didn't notice anything (no error anywhere) and the app just wasn't starting

```java
@ConditionalOnWebApplication
@Configuration
public class HttpRequestHelpersConfiguration
{

    @Bean
    public RequestContextHolderFacade requestContextHolderFacade()
    {
        return new RequestContextHolderFacade();
    }

    @Bean
    public RequestHandlerProvider requestContextHolderFacade(
        final ApplicationContext applicationContext,
        final RequestContextHolderFacade requestContextHolderFacade
    )
    {
        return new RequestHandlerProvider(
            applicationContext,
            requestContextHolderFacade
        );
    }

}
```

->

```
15:07:27.203 [restartedMain  ] ERROR        o.s.b.d.LoggingFailureAnalysisReporter:	

***************************
APPLICATION FAILED TO START
***************************

Description:

Parameter 2 of constructor in ThymeleafMvcTemplatesConfiguration required a bean of type 'RequestHandlerProvider' that could not be found.


Action:

Consider defining a bean of type 'RequestHandlerProvider' in your configuration.
```

I don't have any strong opinion about the behaviour, as I have no problem renaming the method... but there should be a better error message provided by Spring.

Thanks :) 

#### コメント 7 by alfonz19

**作成日**: 2020-01-10

Just to add my experience. Just like other I made typo in method name. Same return type, same method name, different parameters. 2 beans with 2 different qualifiers. First bean declaration wasn't called at all (System.out.println in it wasn't printed, breakpoint wasn't hit), the other method was called twice. Both bean were injectable using 2 different qualifiers, however bean declaration of first qualifier were ever called.

#### コメント 8 by Hakky54

**作成日**: 2022-02-07

I also have the same issue. I wanted to refactor the code below:

[github/mutual-tls-ssl/SSLConfig.java](https://github.com/Hakky54/mutual-tls-ssl/blob/ca34a84fc4d6cd62fc675ec148e52d1fedd800ff/client/src/main/java/nl/altindag/client/SSLConfig.java#L24)

```java
@Component
public class SSLConfig {

    @Bean
    @Scope("prototype")
    public SSLFactory sslFactory(
            @Value("${client.ssl.one-way-authentication-enabled:false}") boolean oneWayAuthenticationEnabled,
            @Value("${client.ssl.two-way-authentication-enabled:false}") boolean twoWayAuthenticationEnabled,
            @Value("${client.ssl.key-store:}") String keyStorePath,
            @Value("${client.ssl.key-store-password:}") char[] keyStorePassword,
            @Value("${client.ssl.trust-store:}") String trustStorePath,
            @Value("${client.ssl.trust-store-password:}") char[] trustStorePassword) {
        SSLFactory sslFactory = null;

        if (oneWayAuthenticationEnabled) {
            sslFactory = SSLFactory.builder()
                    .withTrustMaterial(trustStorePath, trustStorePassword)
                    .withProtocols("TLSv1.3")
                    .build();
        }

        if (twoWayAuthenticationEnabled) {
            sslFactory = SSLFactory.builder()
                    .withIdentityMaterial(keyStorePath, keyStorePassword)
                    .withTrustMaterial(trustStorePath, trustStorePassword)
                    .withProtocols("TLSv1.3")
                    .build();
        }

        return sslFactory;
    }

}
```

Into the following snippet:
```java
@Component
public class SSLConfig {

    @Bean
    @Scope("prototype")
    @ConditionalOnExpression("${client.ssl.one-way-authentication-enabled} == true and ${client.ssl.two-way-authentication-enabled} == false")
    public SSLFactory sslFactory(@Value("${client.ssl.trust-store:}") String trustStorePath,
                                 @Value("${client.ssl.trust-store-password:}") char[] trustStorePassword) {

        return SSLFactory.builder()
                .withTrustMaterial(trustStorePath, trustStorePassword)
                .withProtocols("TLSv1.3")
                .build();
    }


    @Bean
    @Scope("prototype")
    @ConditionalOnExpression("${client.ssl.two-way-authentication-enabled} == true and ${client.ssl.one-way-authentication-enabled} == false")
    public SSLFactory sslFactory(@Value("${client.ssl.key-store:}") String keyStorePath,
                                 @Value("${client.ssl.key-store-password:}") char[] keyStorePassword,
                                 @Value("${client.ssl.trust-store:}") String trustStorePath,
                                 @Value("${client.ssl.trust-store-password:}") char[] trustStorePassword) {

        return SSLFactory.builder()
                .withIdentityMaterial(keyStorePath, keyStorePassword)
                .withTrustMaterial(trustStorePath, trustStorePassword)
                .withProtocols("TLSv1.3")
                .build();
    }

}
```

However it fails. When I set debug on I see that the first is not matched because the expression is evaluated into negative. But the second method should pass, however that one is never evaluated. 

I don't think this is a must option as there is a workaround such as not using method overloading/ and use different method name or combine it in a single method. However it will give a better DX if this would just work out of the box. Looking forward to have this feature 😄 

Any news regarding this issue?

#### コメント 9 by rfelgent

**作成日**: 2022-02-07

I am sorry for you @Hakky54 - you walked into the same trap like me and others :-(

@jholler, I do understand your hint regarding "more or less" by design and I do love your suggestions regarding
"... so at the very least we need to document this properly... and we could possibly raise exceptions in case of condition mismatches among overloaded methods for the same bean definition..."

#### コメント 10 by fprochazka

**作成日**: 2022-02-07

Simply disallowing to declare more methods with the same name on the same configuration class (and guarding that with an exception) would suffice to prevent others from walking into the same trap :+1: 

I guess this could be even easily made into an ErrorProne check for example :thinking:  

#### コメント 11 by Hakky54

**作成日**: 2022-02-07

I have forked the repo and made it working for this specific use case. It was a bit tricky because of some unit tests which still needed to pass. Anyone of the spring-framework team here? Just curious if it is worth to submit a PR as I am wondering if the team is considering to have this kind of capability for allowing of creating a bean conditionally while using method overload.

#### コメント 12 by Hakky54

**作成日**: 2022-02-08

I have created a PR to make this feature working, see here for the details: https://github.com/spring-projects/spring-framework/pull/28019 Would love to get everyones input ❤️ 

#### コメント 13 by jhoeller

**作成日**: 2022-02-15

After a team discussion this morning, we are leaning towards a more radical step: **disallowing overloaded `@Bean` methods completely**, therefore raising an error in case of the same method name reappearing in any form. The original method overloading arrangement for factory methods was inspired by overloaded constructors, treated the same way by our constructor resolution algorithm. Unfortunately this causes more harm than good with `@Bean` methods where it is not obvious that all such same-named methods are part of the same bean definition, with all metadata expected to be equivalent. This was simply never meant to be used with mutually exclusive conditions, or any differing conditions to begin with.

The use cases for factory method overloading (just like with constructor overloading) are mostly related to optional arguments, with the "greediest satisfiable" factory method being calling, e.g. a variant with an optional argument, falling back to the overloaded method without the optional argument otherwise. In a modern-day Spring application, optional factory method arguments can be modeled in various forms, including `@Nullable` arguments and `Optional<...>` declarations, so there should not be any exclusive needs for factory method overloading anymore. That's why we are considering to disallow it completely for Spring Framework 6.0, ideally as of the 6.0 M3 release already.

Enforcing a strict non-overloading rule for `@Bean` methods would prevent accidental overloading that cannot ever work properly, as well as half-accidental overloading that might work by chance but not really by design. For exclusive conditions ("alternative beans"), it is always preferable to use distinct bean names, no matter whether there are optional arguments involved or not. After all, alternative beans with the same (or no) arguments can only be modeled with distinct method names according to Java language rules; this is a strong indication that method overloading for exclusive conditions is misguided, only accidentally working if the method arguments happen to differ between the alternative definitions.

#### コメント 14 by jhoeller

**作成日**: 2022-02-17

I ended up introducing an `enforceUniqueMethods` flag on the `@Configuration` annotation, by default set to `true`. This prevents accidental overloading by enforcing distinct `@Bean` method names for separate bean definitions (which includes "alternative" bean definitions with mutually exclusive conditions). This can be switched to `false` for the previous lenient acceptance of overloaded methods as factory method candidates for the same bean definition.

All in all, the default behavior should provide better guidance now. The error message shown when rejecting same-named `@Bean` methods in 6.0 hints at the `enforceUniqueMethods` flag for whoever intends to opt into the overloading behavior, or whoever has existing configuration classes which happen to rely on the overloading.

#### コメント 15 by rfelgent

**作成日**: 2022-02-20

@jhoeller thx 

- for improved exception logging
- and for the opt in configuration



---

## Issue #27416: Upgrade to AspectJ 1.9.8 GA

**状態**: closed | **作成者**: bclozel | **作成日**: 2021-09-15

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27416

**関連リンク**:
- Commits:
  - [4e3d1fa](https://github.com/spring-projects/spring-framework/commit/4e3d1fa4e9da90b21c2e19c29037f0d687ee4f3e)
  - [2019e17](https://github.com/spring-projects/spring-framework/commit/2019e176ee9c75c2f20ce68a82df2cf1a2af872a)

### 内容

This is the first version that officially supports JDK17 source and target compatibility level (see eclipse/org.aspectj#79).

Right now, we've downgraded the language level to 1.8 in aspectj Gradle tasks. Closing this issue would involve reverting the changes to the `compileAspectj` and `compileTestAspectj` tasks in `spring-aspects.gradle`.

### コメント

#### コメント 1 by jhoeller

**作成日**: 2021-12-14

We're tracking the AspectJ 1.9.8 RCs in spring-projects/spring-framework#27537 (for 6.0 M1), so I'm repurposing this ticket for AspectJ 1.9.8 GA (in 6.0 M2).

#### コメント 2 by sbrannen

**作成日**: 2022-01-14

Related Issue:

- spring-projects/spring-boot#29754

#### コメント 3 by philjoseph

**作成日**: 2022-02-08

Hello AspectJ team, so is the GA for version 1.9.8, that will be the first GA for Java 17, currently depending on the optimization @sbrannen mentioned 25 days ago ? 

#### コメント 4 by kriegaex

**作成日**: 2022-02-08

No @philjoseph, that optimisation is already merged. Actually, we had stable versions for 1.9.8 - currently RC3 - for a long time and could have declared any of them final. Actually, I wanted to celebrate my committer status for AspectJ by cutting the release, even though technically it is not necessary, because I can already deploy to Maven Central ob behalf of the organisation. I just cannot directly commit and always have to trigger Andy Clement to merge my PRs for every little commit. Because internal Eclipse processes are rather Byzyntine, I still do not have committer status for AspectJ proper (only for AJDT), so I simply did not "push the release button". Sorry to have no more exciting (feature-wise) or better justified excuse for you. Maybe I should just deploy a release. For further oprimisations (Andy fixed a few minor bugs since 1.9.8.RC3), there is always the next release. But if you simply want to use Java 17, just use RC3. It does not contain the optimisation you talked about yet, though. That will be in the next Maven Central version.

#### コメント 5 by kriegaex

**作成日**: 2022-02-11

Release 1.9.8 is out, see also https://github.com/eclipse/org.aspectj/pull/121 and the [release announcement](https://www.eclipse.org/lists/aspectj-users/msg15534.html) I sent to the AspectJ users mailing list. Quote:

> Dear AspectJ users,
> 
> we have just released 1.9.8 (yes, finally). It is [available on Maven Central](https://repo1.maven.org/maven2/org/aspectj/aspectjtools/1.9.8/) already. The AspectJ installer can be found on [Aspectj.dev](https://aspectj.dev/maven/org/aspectj/installer/1.9.8/).
> 
> For more information, please read the [release notes](https://htmlpreview.github.io/?https://github.com/kriegaex/org.aspectj/blob/4b9d86acd096e5ee9e108ff0a450c420c880b6ea/docs/dist/doc/README-198.html).
> 
> See [AspectJ GitHub issue spring-projects/spring-framework#95](https://github.com/eclipse/org.aspectj/issues/95) for more information and for an example project showing how to upgrade to the latest AspectJ version when using [dev.aspectj:aspectj-maven-plugin:1.13.1](https://github.com/dev-aspectj/aspectj-maven-plugin).
> 
> Enjoy AspectJ!
> 
> The AspectJ team

#### コメント 6 by snicoll

**作成日**: 2022-02-16

FTR we've decided to backport this to `5.3.x` as well, see #28060 

---

## Issue #27814: Raise bytecode level to Java 17 for Kotlin classes

**状態**: closed | **作成者**: bclozel | **作成日**: 2021-12-14

**ラベル**: type: task, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/27814

**関連リンク**:
- Commits:
  - [6c42bcf](https://github.com/spring-projects/spring-framework/commit/6c42bcfaec45128f7b0807676288552912a1b234)

### 内容

This requires Kotlin 1.6.20, as the fix for https://youtrack.jetbrains.com/issue/KT-49329 is needed.

---

## Issue #27828: Provide repackaged version of JavaPoet

**状態**: closed | **作成者**: snicoll | **作成日**: 2021-12-16

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/27828

**関連リンク**:
- Commits:
  - [42243d9](https://github.com/spring-projects/spring-framework/commit/42243d974f99255eb3a4efd69022b77e4e8610c7)
  - [dd7ec1a](https://github.com/spring-projects/spring-framework/commit/dd7ec1ae057b7937cf031656b40d89cdf57d9e69)
  - [61e15d9](https://github.com/spring-projects/spring-framework/commit/61e15d94fc8aa9dc29e027d5a435aa2bd9571a03)
  - [d0b6612](https://github.com/spring-projects/spring-framework/commit/d0b66129f9238cbb8aa755faab177396aa5c0456)
  - [f9ccac0](https://github.com/spring-projects/spring-framework/commit/f9ccac0682d444cffdb4aa5ae9a4fcd04d2350c1)
  - [467dd75](https://github.com/spring-projects/spring-framework/commit/467dd75b00ebf3de8fc6863c48ad8c77c131f6da)
  - [f61ad47](https://github.com/spring-projects/spring-framework/commit/f61ad4764276bd0fa2d0061ab6f2cceb9c158d07)
  - [b74b86b](https://github.com/spring-projects/spring-framework/commit/b74b86ba9f34ec287487f76bd4c085d9d0f96d2e)
  - [dfae8ef](https://github.com/spring-projects/spring-framework/commit/dfae8effa8c26ab69cf7b237b3c2fdd382f64b75)
  - [bb06af0](https://github.com/spring-projects/spring-framework/commit/bb06af0273fb32410c6496f275bdb8c28445240f)
  - [cff4346](https://github.com/spring-projects/spring-framework/commit/cff4346293581caabd2c5ffdd1ded57ed231c2eb)
  - [ce7513e](https://github.com/spring-projects/spring-framework/commit/ce7513e7575b9dc7e9e5d6c138f40ad026e3124a)
  - [704e1a0](https://github.com/spring-projects/spring-framework/commit/704e1a02d9b234480fe2f328427009ee5c2c0322)

### 内容

Our AOT processing needs a code generation library and we're quite happy using JavaPoet in Spring Native. It would be quite unusual for the core container to have a direct dependency on a third-party so the plan is to jarjar it in `org.springframework.javapoet` in the `spring-core` module.



### コメント

#### コメント 1 by snicoll

**作成日**: 2022-01-11

We've decided to depend on JavaPoet directly for now with an optional dependency in modules that require it.

#### コメント 2 by snicoll

**作成日**: 2022-02-03

With our design evolving where certain components can provide both the regular runtime behavior and something that can generate a pre-processed version of it, it became apparent that it's odd to rely on an optional dependency of javapoet. 

We've decided to give the repackaging another try.

---

## Issue #27829: Add a way to register the need for runtime reflection, resources, proxying, and serialization on components

**状態**: closed | **作成者**: snicoll | **作成日**: 2021-12-16

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/27829

**関連リンク**:
- Commits:
  - [5f8198d](https://github.com/spring-projects/spring-framework/commit/5f8198d74f380ef534ac91c85c717c74bced0531)
  - [7c2f94c](https://github.com/spring-projects/spring-framework/commit/7c2f94c5c3369cdbb55f8060603c0e66f79eb22d)
  - [cb44ef0](https://github.com/spring-projects/spring-framework/commit/cb44ef0561e1531d595025f31dcdec0e0408e47f)
  - [578d04f](https://github.com/spring-projects/spring-framework/commit/578d04ff860cc2246b9122e3065d881753833193)
  - [a0c97e4](https://github.com/spring-projects/spring-framework/commit/a0c97e4c36e5e07bc13bab4409ec740332a57871)
  - [5da0e85](https://github.com/spring-projects/spring-framework/commit/5da0e8537ca7fb93f2c6c056b4e547d568b080d8)
  - [e4277e6](https://github.com/spring-projects/spring-framework/commit/e4277e6b1f14ef5c4a36fb13fcd9352de1ad0609)
  - [374bfd1](https://github.com/spring-projects/spring-framework/commit/374bfd13be732271009f6551e1fe15e4a09badb3)
  - [4e127de](https://github.com/spring-projects/spring-framework/commit/4e127de10a671be15a2bdf8ef54276612a2419bb)
  - [f906fa7](https://github.com/spring-projects/spring-framework/commit/f906fa78a1f282cfc60f49a078c429f91e6c53a6)
  - [4d3f27d](https://github.com/spring-projects/spring-framework/commit/4d3f27d6dfe1949ccd1b0d921112c91a0cfb951b)
  - [6f7d9ab](https://github.com/spring-projects/spring-framework/commit/6f7d9ab589ecfec6fc454650448de09e8e9681e5)
  - [73f0167](https://github.com/spring-projects/spring-framework/commit/73f01676d8cd61e5608c8a10d0d2f6742fc6c32a)
  - [aef0850](https://github.com/spring-projects/spring-framework/commit/aef0850d3937de88cf22480cce8a6b0f7f89e540)
  - [6936f7e](https://github.com/spring-projects/spring-framework/commit/6936f7e0cb1eae8357f3c700d2c2d33834475ec2)
  - [258ea06](https://github.com/spring-projects/spring-framework/commit/258ea0686e145fe05bdd02faed665956d6dc71a1)
  - [40336fa](https://github.com/spring-projects/spring-framework/commit/40336fa1bc866039776e0a53cb7257b97814fe7a)
  - [7dae7b0](https://github.com/spring-projects/spring-framework/commit/7dae7b01d8719029a9d52c7525e27026e066a806)
  - [1a43f1d](https://github.com/spring-projects/spring-framework/commit/1a43f1ddf771ae5eaa1fd12c3b101ee5401e8e5b)
  - [a4ac999](https://github.com/spring-projects/spring-framework/commit/a4ac99900cd56c6f3f5a0126c055792714c600c1)
  - [48ce714](https://github.com/spring-projects/spring-framework/commit/48ce714d159f0c648f836a5abdf18c12cb4c6f40)

### 内容

Spring Native has a component called `NativeConfigurationRegistry` that offers a programmatic API to register the need for reflection, resources that are to be shipped in the native image, proxies as well as classes that should be `Serializable`.

We'd like to revisit this contract and make less native specific as we believe that such information could be useful elsewhere.

Such an infrastructure could land in `spring-core` as it is rather high-level and focused on classes and resources. The actual processing of the registry, for instance, to write GraalVM-specific configuration files is not in the scope of this issue.

---

## Issue #27866: Inconsistent overriding (and enforcement of non-overriding) between bean definition names and aliases

**状態**: closed | **作成者**: levitin | **作成日**: 2021-12-29

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/27866

**関連リンク**:
- Commits:
  - [6b1c2dc](https://github.com/spring-projects/spring-framework/commit/6b1c2dc944e9541720d8fd7de3ce3c54ca03d5c2)

### 内容

When I try to register two beans (one of aliases of the first bean corresponds to method name (= future id) of the second bean, the creation of second bean is ignored. The context starts without any exception. 

```java
@Configuration
public class MyConfiguration {

    @Bean({"name1", "name2"})
    public MyInterface myBean() {
        return new MyFirstBean();
    }

    @Bean
    public MyInterface name2() {
        return new MySecondBean();
    }
}
```

`MyMap` in the following example contains only one bean, actually: `name1 -> MyFirstBean`

```java
    @Autowired
    Map<String, MyInterface> myMap;
```

I'm not sure if it is a bug or a feature. In my opinion [NoUniqueBeanDefinitionException](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/NoUniqueBeanDefinitionException.html) should be thrown in this case.

What do you think?

### コメント

#### コメント 1 by snicoll

**作成日**: 2021-12-29

It depends. Given that `myBean` claims `name1` and `name2`, it sounds logical that `MySecondBean` isn't created. We need to put a priority somewhere. If we did the reverse, you could equally claim that `MyFirstBean` isn't used despite it declaring an alias for `name2`.

Having said that, I was expecting this to fail with Spring Boot as we prevent bean overriding by default. It did not and that felt a little bit more surprising. Flagging to get more feedback from the team.


#### コメント 2 by levitin

**作成日**: 2021-12-29

> If we did the reverse, you could equally claim that MyFirstBean isn't used despite it declaring an alias for name2

Yes, another direction would also cause an unpleasant surprise. But it is even worse, if giving any bean a "harmless" alias would suddenly exclude another existing bean in case of name matching. I think, such side effect could be really dangerous, perhaps it can be even a security issue. 

In my opinion, in such case as described above, it would be much more safer, if the context would not even start at all. 

Is there any reason not to treat every bean name and every alias as unique?


#### コメント 3 by jhoeller

**作成日**: 2022-01-18

There are indeed two inconsistencies in our overriding checks between bean definition names and aliases: Not only is a new bean definition overriding an existing alias not prevented when allowBeanDefinitionOverriding=false (like in Boot by default), the factory also silently registers a new bean definition but does not remove a same-named alias when allowBeanDefinitionOverriding=true.

In other words, bean definition overriding between bean definition names and aliases is a feature, but a later definition should consistently override an existing definition - so in our scenario here, the `name2` method should override the existing `name2` alias. And with overriding deactivated, it should consistently throw an exception when encountering such an attempted override for an existing alias.

I'll revise this for 6.0 M3.

---

## Issue #27921: Implement an AOT equivalent of AutowiredAnnotationBeanPostProcessor

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-01-11

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/27921

**関連リンク**:
- Commits:
  - [8cd55e6](https://github.com/spring-projects/spring-framework/commit/8cd55e651b605cd174d34b6a98672828b6fc1168)
  - [6fd95f6](https://github.com/spring-projects/spring-framework/commit/6fd95f60ea60b590689e18c8a0ad34c36773608b)
  - [8ada537](https://github.com/spring-projects/spring-framework/commit/8ada53707f11daa17002b31a94033d673dd4c6b1)
  - [31de85b](https://github.com/spring-projects/spring-framework/commit/31de85b77bc3cf732badbb9caec4bd2bd25550b2)
  - [c05167b](https://github.com/spring-projects/spring-framework/commit/c05167bc531f4b2dc695a3c7c376e362edb92d71)
  - [f9a00c9](https://github.com/spring-projects/spring-framework/commit/f9a00c9974ddb03786e66bedea1d54eb592d3e3b)
  - [e74e794](https://github.com/spring-projects/spring-framework/commit/e74e794dbbf439912b483a31dacdffa205b5234a)
  - [b8f675c](https://github.com/spring-projects/spring-framework/commit/b8f675cdb70d196c6408b7d6767bb7174059d3c9)
  - [2c57c9e](https://github.com/spring-projects/spring-framework/commit/2c57c9ec9cf9f2cad3314c8783674cbe5d4ab347)
  - [0cbae1c](https://github.com/spring-projects/spring-framework/commit/0cbae1ca08280dc7804492aded7b95f6f038e989)
  - [3a4f63c](https://github.com/spring-projects/spring-framework/commit/3a4f63cfcb04e753268763a7a5c7f1420018ab9e)
  - [dc6e8a4](https://github.com/spring-projects/spring-framework/commit/dc6e8a422d05d2660a3b3f36140c525e5c9d9018)
  - [2150272](https://github.com/spring-projects/spring-framework/commit/2150272f1789b76eb96d24c70f92cc0da7e4a47e)
  - [6b50c75](https://github.com/spring-projects/spring-framework/commit/6b50c75e03be62f1882c7a02bb1cdfa54c3af139)
  - [39fd3a2](https://github.com/spring-projects/spring-framework/commit/39fd3a2787ac93a39b73e4dd688f18bedeccd9e2)
  - [2141373](https://github.com/spring-projects/spring-framework/commit/2141373c432dfc18bb665ec4f54b1e3c3b121c99)
  - [d540460](https://github.com/spring-projects/spring-framework/commit/d540460a56cf282fdf51fb8bbe8b548beccc8a08)
  - [333b3c7](https://github.com/spring-projects/spring-framework/commit/333b3c76a33e9cbf9553d7a2d660834ecda95f7f)
  - [c9e90d5](https://github.com/spring-projects/spring-framework/commit/c9e90d5f75b05d4b55965679551ae40f2a7901e6)

### 内容

`InjectionMetadata`  provides some information we could use at build-time. For instance, if `AutowiredAnnotationBeanPostProcessor` is enabled for the `ApplicationContext` that app uses without AOT, we should be able to find out about `autowired` elements, potentially even reusing any custom configuration that was set on the post processor.

There is also some logic in the way injection works that we may need to streamline to be consistent.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-01-31

We're trying to design an interface that allows a `BeanPostProcessor` to opt-in for providing a code contributor that replaces what it does at runtime. The current model is implementing an interface that returns a contributor based on a `RootBeanDefinition`, similar to `MergedBeanDefinitionPostProcessor#postProcessMergedBeanDefinition`.

While the processor would be excluded by default at runtime, it would be nice if it could indicate that it needs to run again.  If we want such a feature, the phase at which the `BeanFactory` is processed should become a high-level concept, something like "build-time" vs. "runtime" vs. "optimized-runtime".


#### コメント 2 by snicoll

**作成日**: 2022-02-14

We need #28047 to move forward on this one.

---

## Issue #27928: Gradle apiDiff task does not work against a milestone

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-01-13

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/27928

**関連リンク**:
- Commits:
  - [2d9c9fe](https://github.com/spring-projects/spring-framework/commit/2d9c9fe9cca01f0851158424134467e96f6debcf)

### 内容

Running `./gradlew apiDiff -PbaselineVersion=6.0.0-M1` leads to:

```
Starting a Gradle Daemon (subsequent builds will be faster)
> Task :spring-instrument:apiDiff FAILED
> Task :spring-jcl:apiDiff FAILED

FAILURE: Build completed with 2 failures.

1: Task failed with an exception.
-----------
* What went wrong:
Execution failed for task ':spring-instrument:apiDiff'.
> Could not resolve all files for configuration ':detachedConfiguration9'.
   > Could not find org.springframework:spring-instrument:6.0.0-M1.
     Searched in the following locations:
       - https://repo.maven.apache.org/maven2/org/springframework/spring-instrument/6.0.0-M1/spring-instrument-6.0.0-M1.pom
       - https://repo.spring.io/libs-spring-framework-build/org/springframework/spring-instrument/6.0.0-M1/spring-instrument-6.0.0-M1.pom
     Required by:
         project :

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.
==============================================================================

2: Task failed with an exception.
-----------
* What went wrong:
Execution failed for task ':spring-jcl:apiDiff'.
> Could not resolve all files for configuration ':detachedConfiguration10'.
   > Could not find org.springframework:spring-jcl:6.0.0-M1.
     Searched in the following locations:
       - https://repo.maven.apache.org/maven2/org/springframework/spring-jcl/6.0.0-M1/spring-jcl-6.0.0-M1.pom
       - https://repo.spring.io/libs-spring-framework-build/org/springframework/spring-jcl/6.0.0-M1/spring-jcl-6.0.0-M1.pom
     Required by:
         project :

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.
==============================================================================

* Get more help at https://help.gradle.org

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD FAILED in 15s
31 actionable tasks: 8 executed, 4 from cache, 19 up-to-date
```

Adding the milestone repo manually fixes the problem.

---

## Issue #27985: Upgrade to Groovy 4.0

**状態**: closed | **作成者**: jhoeller | **作成日**: 2022-01-28

**ラベル**: in: web, in: core, type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27985

**関連リンク**:
- Commits:
  - [9688e61](https://github.com/spring-projects/spring-framework/commit/9688e61e2066b2fb45f865e64a75c29c99405192)

### 内容

_本文なし_

---

## Issue #28007: HibernateJpaDialect compatibility with Hibernate 6 (read-only transactions etc)

**状態**: closed | **作成者**: odrotbohm | **作成日**: 2022-02-04

**ラベル**: in: data, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28007

**関連リンク**:
- Commits:
  - [d07e1be](https://github.com/spring-projects/spring-framework/commit/d07e1be623b607c77afe6faf8c02eda8a1b0b110)

### 内容

During our work to investigate the compatibility with Hibernate 6 in Spring Data JPA we ran into an issue surfacing in Spring Frameworks transaction management:

In `….beginTransaction(…)`, `HibernateJpaDialect` calls `SessionImplementor.connection()` a method that has been removed in CR1 (could've been in one of the betas already, I didn't check) to issue read-only transactions. It looks like the new way to access the `Connection` is calling `….getJdbcConnectionAccess().obtainConnection()`.

Related tickets:
* spring-projects/spring-data-jpa#2423

### コメント

#### コメント 1 by jhoeller

**作成日**: 2022-02-04

We aim for a complete Hibernate 6.0 support story in our own 6.0 M3, not sure yet how far we'll go (native API via `orm.hibernate6`? or just with JPA? keeping up Hibernate 5.x support in parallel? etc): #22128

That said, it's definitely worth considering what we could do in 5.3.x to allow for using Hibernate 6.0 with our JPA support at least. We might want to leniently tolerate it at runtime for a start, even without full alignment yet. Let's use this ticket for it.

#### コメント 2 by odrotbohm

**作成日**: 2022-02-04

Once I avoided read-only transactions by rather using a simple `@Transactional` the integration tests using Hibernate 6 CR1 on a Boot 3 M1 ran just fine. I.e. it might be just that particular issue for starters. That's why I thought I'd open the ticket around something actionable. But of course, as you see fit.

Oh, H6 is JakartaEE based. I guess that is a showstopper for any support of it in our 5.x generation.

#### コメント 3 by jhoeller

**作成日**: 2022-02-04

Good point, there's no classic JPA binding for it anymore, it's exclusively built on `jakarta.persistence` indeed. And it won't be usable with `orm.hibernate5` either due to plenty of incompatibilities in the native Hibernate API. Alright, so Hibernate ORM 6.0 becomes a Spring Framework 6.0 only topic then :-)

#### コメント 4 by jhoeller

**作成日**: 2022-02-04

Alright, so we'll definitely sort out `HibernateJpaDialect` compatibility for 6.0 M3 for a start, using this ticket. Full Hibernate 6.0 alignment - or even Hibernate 6.0 baselining - might take longer anyway, let's use #22128 for that part then.

#### コメント 5 by odrotbohm

**作成日**: 2022-02-04

I just realized that the API I found and suggested as workaround (never tested using it myself, though) also already exists in 5.6.5. I.e. we could try to just move that in 6.0 but stick to the Hibernate 5.x baseline.

#### コメント 6 by jhoeller

**作成日**: 2022-02-04

It turns out that it is indeed straightforward to support both Hibernate 5.6 and 6.0 through a revision of `HibernateJpaDialect` where it retrieves the current JDBC connection differently. The correct replacement is `getJdbcCoordinator().getLogicalConnection().getPhysicalConnection()` for obtaining the current connection held by the session, as far as the connection release mode is appropriate for it. This seems to work fine on 5.6 as well as 6.0.

The other area affected is `HibernateJpaVendorAdapter` and its selection of default dialects for the database enum. Those dialects seem to be deprecated now, the Informix dialect is even gone completely. However, this shouldn't be a big deal since we recommend explicit Hibernate dialect configuration in any case (rather than relying on our database enum).

From that perspective, we seem to be covered in terms of JPA compatibility, so I'll close this ticket right away. The main remaining part for #22128 is whether we want/need an `orm.hibernate6` package next to `orm.hibernate5`, or possibly as a replacement for `orm.hibernate5`. This mostly depends on what we are going to recommend for existing `orm.hibernate5` users: staying on Hibernate 5.6, upgrading to Hibernate 6.0 via `orm.hibernate6`, or upgrading to Hibernate 6.0 via JPA.

#### コメント 7 by odrotbohm

**作成日**: 2022-02-08

Thanks for that, Jürgen. Verified working as expected now! 🙇

---

## Issue #28013: Add support for registering multiple init & destroy method names

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-07

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28013

**関連リンク**:
- Commits:
  - [41ee233](https://github.com/spring-projects/spring-framework/commit/41ee23345d72623d18accb9484ce5119403c39d5)

### 内容

A `BeanDefinition` can have an `init` and `destroy` method name. While uncommon, it is possible for a bean to have more than one of those, see `InitDestroyAnnotationBeanPostProcessor`. 

To replace the runtime behavior of searching for those annotations, we need a way to specify multiple init and destroy method names. There might be an impact on `isExternallyManagedConfigMember` in `RootBeanDefinition` as well.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-02-07

Reviewing what we did in Spring Native to support this feature, it looks like that adding multiple init/destroy method names could be enough to support this use case, if we'd honor `MergedBeanDefinitionPostProcessor`. 

The current code registers detected method as externally managed. We could rather "just" register it and let the new code invokes the method. 

#### コメント 2 by chenggwang

**作成日**: 2025-06-16

> A `BeanDefinition` can have an `init` and `destroy` method name. While uncommon, it is possible for a bean to have more than one of those, see `InitDestroyAnnotationBeanPostProcessor`.
> 
> To replace the runtime behavior of searching for those annotations, we need a way to specify multiple init and destroy method names. There might be an impact on `isExternallyManagedConfigMember` in `RootBeanDefinition` as well.

Hi snico！So far, it seems that this support is only used in AOT. It doesn't seem to be used in other spring modules. For example, at least @bean(initMethod={"init1",init2,..." }), extending to xml configuration is obviously not supported. It seems that it is not needed elsewhere. So should this method be set as protected? Because we can directly accessible beanDefinition. SetDestroyMethodNames (init1 init2), if you really need to generality, the initialization method execution order how to guarantee? And how to coordinate?

#### コメント 3 by snicoll

**作成日**: 2025-06-16

Do you have an actual problem? If so, please create a new issue with a sample that demonstrates it and we can have a look.

#### コメント 4 by chenggwang

**作成日**: 2025-06-17

> Do you have an actual problem? If so, please create a new issue with a sample that demonstrates it and we can have a look.

I didn't find any actual problems. I discovered during the use of Spring that a bean can have multiple initialization or destruction methods using either 'beanDefinition. SetInitMethodNames (init1, init2)' or 'beanDefinition. SetDestroyMethodNames (destruct1, destruct12)'. These methods were submitted by you three years ago. If only AOT is supported, should these methods be visible within the package so that they cannot be called externally? If bean multi initialization methods are supported, implement @ bean (initMethod={"init1", init2,... "}). Support multi initialization methods, I have modified the implementation locally and can submit the code.

---

## Issue #28020: Upgrade to Gradle 7.4

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-02-08

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/28020

**関連リンク**:
- Commits:
  - [5c60a72](https://github.com/spring-projects/spring-framework/commit/5c60a721a7ab81f50e9b88a031bc8a1d3e17ccb4)

### 内容

https://docs.gradle.org/7.4/release-notes.html

---

## Issue #28028: Add core JavaPoet utilities

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-10

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28028

**関連リンク**:
- Commits:
  - [b3ceb0f](https://github.com/spring-projects/spring-framework/commit/b3ceb0f625a5b40d1007bb4dfe673be497fc2c9e)

### 内容

Our prototype with Spring Native has shown that working with multiple statements and/or code blocks can lead to repetitive code. Also, JavaPoet does not resolve imports on code snippet so that makes code assertion a bit awkward. 

this issue is about porting those utilities in `spring-core` so that we can benefit from it.

---

## Issue #28029: Make BeanDefinitionValueResolver public

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-10

**ラベル**: type: task, in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28029

**関連リンク**:
- Commits:
  - [d64f8c1](https://github.com/spring-projects/spring-framework/commit/d64f8c1a05f9b5a3cd6451a20261c5e6f7b4108d)
  - [a4ab4b7](https://github.com/spring-projects/spring-framework/commit/a4ab4b773abb818b4d3fea5ef70297bb5b112058)

### 内容

`BeanDefinitionValueResolver` is package private at the moment and the AOT engine could use calling it directly to resolve constructur arguments typically. 

We could also improve the current usage where a default `TypeConverter` can be provided by default as the current pattern uses a protected method of the bean factory to initialize it.

---

## Issue #28030: Add code contribution infrastructure

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-10

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28030

**関連リンク**:
- Commits:
  - [1a45736](https://github.com/spring-projects/spring-framework/commit/1a4573641d3ae35d044e366b472e68cc6daaad8a)
  - [5bbc7db](https://github.com/spring-projects/spring-framework/commit/5bbc7dbce237f049a53291d47d6b1e5f6f897907)
  - [e873715](https://github.com/spring-projects/spring-framework/commit/e873715737fda8fc284bc5c18f0e8c260416c3ba)

### 内容

We need a contract where individual components can provide some code, the related `RuntimeHints` that could be necessary in a constrained environment as well as whether the code is using protected access (i.e. non public types or methods). 

This is required by #27921

---

## Issue #28047: Add Bean instantiation generator infrastructure

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-14

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28047

**関連リンク**:
- Commits:
  - [9809752](https://github.com/spring-projects/spring-framework/commit/9809752c3c9b77e4fa6d1e06c9e1b080b6affb17)
  - [c541bde](https://github.com/spring-projects/spring-framework/commit/c541bde513443862e24e372c83f33e8c511d8903)
  - [572d017](https://github.com/spring-projects/spring-framework/commit/572d0173703e15a80e76eac2ad0bea9c56f35326)
  - [ea19b92](https://github.com/spring-projects/spring-framework/commit/ea19b92deb44fc74c04da6771afd714efeb79521)
  - [97986b3](https://github.com/spring-projects/spring-framework/commit/97986b368a42f858a8f6ee84e2ca4a79f17e7410)
  - [c5e1a77](https://github.com/spring-projects/spring-framework/commit/c5e1a774a5a1e27eb1ca693b663ec37e6583ac41)
  - [20b17f0](https://github.com/spring-projects/spring-framework/commit/20b17f02a29de8f10773d400b92f310fc6aba5a2)

### 内容

As part of our AOT effort, we need an infrastructure that lets us generate the code to instantiate a bean.

This includes some low-level code generation infrastructure to write method calls, parameters, etc, as well as an API that can be used to contribute to the bean instance. 

Such contributors should namely be based on the existing `BeanPostProcessor` infrastructure as they augment a bean instance with some logic that can be translated into code during the AOT phase. As BPP are ordered, so can their contributions so that the order in which they are applied by executing generated code matches.

To ease code generation, we need an infrastructure that focuses on something quite basic for a first version, something like:

```java
BeanDefinitionRegistrar.of("restTemplateClientService", RestTemplateClientService.class)
	  .withConstructor(RestTemplateBuilder.class)
	  .instanceSupplier((instanceContext) -> instanceContext.create(beanFactory, (attributes) ->
			  new RestTemplateClientService(attributes.get(0))))
	  .register(beanFactory);
```

This registeres a `restTemplateClientService` bean that requires a `RestTemplateBuilder`. Rather than doing all the dependency resolution at build-time, we leverage framework's dependency resolution algorithm, via the `instanceContext` who can provide us resolved attributes according to `Executable` to use to instantiate the bean (here a constructor that takes a `RestTemplateBuilder`).

---

## Issue #28054: Remove deprecated SocketUtils

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-02-15

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28054

**関連リンク**:
- Commits:
  - [ee51dab](https://github.com/spring-projects/spring-framework/commit/ee51dab1f348361f26c477ad64ab730ad7359d6e)
  - [c661d79](https://github.com/spring-projects/spring-framework/commit/c661d7925e574793475f0fd38998300babc619e7)
  - [9b27fbe](https://github.com/spring-projects/spring-framework/commit/9b27fbee897797bba181587fd736e4dc99f36e69)
  - [2cee634](https://github.com/spring-projects/spring-framework/commit/2cee63491d1fbb6e21a9044715d98838fec9a51b)
  - [fb72f1f](https://github.com/spring-projects/spring-framework/commit/fb72f1fdade2591220d58e8a0d91d954c8824080)

### 内容

See:

-  #28052

### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-02-15

Closed via 2cee63491d1fbb6e21a9044715d98838fec9a51b

#### コメント 2 by sbrannen

**作成日**: 2022-03-21

Please note that the team plans to introduce `TestSocketUtils` in Spring Framework 5.3.18. See #28210 for details.

---

## Issue #28065: Add support for refreshing an ApplicationContext for AOT processing

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-17

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28065

**関連リンク**:
- Commits:
  - [67d5786](https://github.com/spring-projects/spring-framework/commit/67d5786ef572c29b301688181beaccda1a974229)
  - [ab8b45d](https://github.com/spring-projects/spring-framework/commit/ab8b45d02dd9c25fdcde1b27e1f55154ce969de2)
  - [d5d2da8](https://github.com/spring-projects/spring-framework/commit/d5d2da8683804383293fa78a194e1a784ee483a4)
  - [b5695b9](https://github.com/spring-projects/spring-framework/commit/b5695b92483118aa738ada26e438c32017dbeef7)

### 内容

For us to be able to pre-process an `ApplicationContext` at build-time, we need a way to "refresh" it up to a point where it is ready to create bean instances, this includes:

* Prepare the `BeanFactory`
* Invoke `BeanDefinitionRegistryPostProcessor` implementations
* Invoke `MergedBeanDefinitionPostProcessor` implementations (note that these are special extensions of `BeanPostProcessor` that operates at the (merged) `BeanDefinition` level



---

## Issue #28079: Deprecate "enclosing classes" search strategy for MergedAnnotations

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-02-19

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28079

**関連リンク**:
- Commits:
  - [29d9828](https://github.com/spring-projects/spring-framework/commit/29d98285bea8be459d0bdcaad655c84338c3d0e5)
  - [5689395](https://github.com/spring-projects/spring-framework/commit/5689395678f57fe967a3b21ed7d9087cfec7b622)
  - [b97a3ae](https://github.com/spring-projects/spring-framework/commit/b97a3ae07aa29d9c55c95f54c50b5558564a87c5)
  - [fc8f31c](https://github.com/spring-projects/spring-framework/commit/fc8f31ccfbecd2179d7ce216a5a3521f13397c05)
  - [c9cd53f](https://github.com/spring-projects/spring-framework/commit/c9cd53f469a7b3a79284542fe0222b0f9fd05785)

### 内容

### Overview

The `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` search strategy for `MergedAnnotations` was originally introduced to support `@Nested` test classes in JUnit Jupiter.

However, while implementing #19930, we determined that the `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` search strategy unfortunately could not be used since it does not allow the user to control when to recurse up the enclosing class hierarchy. For example, this search strategy will automatically search on enclosing classes for static nested classes as well as for inner classes, when the user probably only wants one such category of "enclosing class" to be searched. Consequently, [`TestContextAnnotationUtils`](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/TestContextAnnotationUtils.java) was introduced in the _Spring TestContext Framework_ to address the shortcomings of the `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` search strategy.

Since this search strategy is unlikely to be useful to general users, the team should consider deprecating this search strategy in Spring Framework 6.0.

### Related Issues

- #19930
- #23378
- #28080

### コメント

#### コメント 1 by philwebb

**作成日**: 2022-03-11

@sbrannen We use this strategy in Spring Boot to find `@ConstructorBinding` annotations from nested classes. Can we reconsider deprecating it?

#### コメント 2 by sbrannen

**作成日**: 2022-03-12

Hi @philwebb,

I saw that you once used it in Boot's `ConfigurationPropertiesBean`, but that no longer seems to be the case.

Where is `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` still used in Spring Boot?

#### コメント 3 by snicoll

**作成日**: 2022-03-12

Here is one: https://github.com/spring-projects/spring-boot/blob/de321b00b7d0f2c5c1c79a77e7241b43fbcd8313/spring-boot-project/spring-boot-actuator/src/main/java/org/springframework/boot/actuate/context/properties/ConfigurationPropertiesReportEndpoint.java#L559

We don't on `main` as the semantic of `@ConstructorBinding` has evolved in such a way that it is no longer necessary to search it this way.

#### コメント 4 by sbrannen

**作成日**: 2022-03-13

Thanks for the link and explanation, @snicoll.

If the search strategy is only used for `@ConstructorBinding` against Framework 5.3.x and is no longer used in Boot 3.0+ (relying on Framework 6.0+), is there still an issue with having the search strategy deprecated in Framework 5.3.x and removed in 6.0?

#### コメント 5 by snicoll

**作成日**: 2022-03-13

I think so, yes. Our policy is to not rely on deprecated code unless absolutely necessary. Getting in this situation for the whole duration of the `2.x` line is far from ideal and we'd probably copy the code to avoid using deprecated code in framework.

While I have the opportunity, I disagree with the opening statements. It may have been introduced for a very specific use case but once it becomes public API, we can't really argue that this is the only use. It sounds like an addition in [TestContextAnnotationUtils](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/TestContextAnnotationUtils.java) is fixing the problem. It doesn't, at least for us.


#### コメント 6 by sbrannen

**作成日**: 2022-03-16

For the `5.3.x` line, the team has decided not to deprecate the `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` search strategy.

Instead, we will add notes to the documentation to increase awareness of how the search strategy behaves.

In addition, we will reconsider deprecation/removal of the search strategy in `6.0.x`.

#### コメント 7 by sbrannen

**作成日**: 2022-03-16

**Team Decision**: we have decided to deprecate the `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` search strategy in 6.0 M3, allowing consumers of 6.0 milestones and release candidates to provide feedback before potentially completely removing it and/or providing an alternate mechanism for achieving the same goal prior to 6.0 GA.

- see #28080 for details

---

## Issue #28088: Add API to contribute to the setup of an ApplicationContext

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-21

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28088

**関連リンク**:
- Commits:
  - [5bc701d](https://github.com/spring-projects/spring-framework/commit/5bc701d4fe32b45481bcf63f093759df75df7f57)
  - [ec6a19f](https://github.com/spring-projects/spring-framework/commit/ec6a19fc6b37ef03d2667100a2ee9de1488c902d)

### 内容

When a context is pre-processed at build-time and we generate optimized code for it, bean definition registration is one obvious part but not the only one. The core container should have an abstraction and an API that other components can implement to contribute to the setup of the context.

One example is the thing that scans for `@EventListener`-annotated methods and register an event-listener if necessary. As these components are actually replacing something else, they could opt-in for excluding bean definitions that they are replacing.

---

## Issue #28093: Rationalise merged BeanDefinition resolution for inner beans

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-22

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28093

**関連リンク**:
- Commits:
  - [fc4312b](https://github.com/spring-projects/spring-framework/commit/fc4312b633f7ec2ae98d89450b59a78e9cd6ee35)
  - [929b5a0](https://github.com/spring-projects/spring-framework/commit/929b5a040eb69dd421670a67cae0a23647f1f291)
  - [cc57b55](https://github.com/spring-projects/spring-framework/commit/cc57b55c61fa35d97d7a16db1b389f6b85ec8633)

### 内容

There are more places where we need to create a `beanName` for an inner bean definition so rather than copy/pasting those, it would be better to have that logic in a single place.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-02-22

I was under the impression I could add that in `BeanFactoryUtils` but this introduces a package tangle. @jhoeller any idea?

#### コメント 2 by snicoll

**作成日**: 2022-03-06

It turns out that the way a `RootBeanDefinition` for an inner bean is required and it goes beyons getting a bean name for it. I've updated the issue accordingly.

---

## Issue #28098: Support type-safe transaction rollback rules

**状態**: closed | **作成者**: hduyyg | **作成日**: 2022-02-23

**ラベル**: in: data, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28098

**関連リンク**:
- Commits:
  - [c1033db](https://github.com/spring-projects/spring-framework/commit/c1033dbfb3609f3b3fe002d7b582b3302620c05a)
  - [67b91b2](https://github.com/spring-projects/spring-framework/commit/67b91b239091afe169045cf0dafa800aaa5884aa)

### 内容

Source code in question：

```java
private int getDepth(Class<?> exceptionClass, int depth) {
	if (exceptionClass.getName().contains(this.exceptionName)) {
		// Found it!
		return depth;
	}
	// If we've gone as far as we can go and haven't found it...
	if (exceptionClass == Throwable.class) {
		return -1;
	}
	return getDepth(exceptionClass.getSuperclass(), depth + 1);
}
```

test code:

```java
public class CustomException extends Exception {
}

public class CustomExceptionX extends Exception {
}

@Override
@Transactional(rollbackFor = CustomException.class)
public void testTransaction() throws Exception {
    taskMapper.softDeleteById(1, "test");
    if (1 == 1) {
        throw new CustomExceptionX();
    }
}
```


### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-02-28

This is by design and was originally implemented using `contains()` for use in XML configuration files where users often specified the _simple name_ of a custom exception type instead of the _fully qualified class name_.

You can see examples of this in the [reference docs](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction-declarative-rolling-back).

```xml


<tx:advice id="txAdvice" transaction-manager="txManager">
  <tx:attributes>
    <tx:method name="get*" read-only="true" rollback-for="NoProductInStockException"/>
    <tx:method name="*"/>
  </tx:attributes>
</tx:advice>
```

With your proposal to use `equals()` instead of `contains()`, configuration like that would no longer work since `NoProductInStockException` would only ever be equal to the fully qualified class name if the `NoProductInStockException` was declared as a top-level class in the _default_ package -- which is rather unlikely.

Please take note of the [Javadoc for `RollbackRuleAttribute`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/interceptor/RollbackRuleAttribute.html#RollbackRuleAttribute-java.lang.String-) as well:

> **NB**: Consider carefully how specific the pattern is, and whether to include package information (which is not mandatory). For example, "Exception" will match nearly anything, and will probably hide other rules. "java.lang.Exception" would be correct if "Exception" was meant to define a rule for all checked exceptions. With more unusual exception names such as "BaseBusinessException" there's no need to use a fully package-qualified name.

Similar documentation exists for the `rollbackForClassName` attribute in `@Transactional`.

----

The Javadoc for the `RollbackRuleAttribute(Class)` constructor states the following,

> Create a new instance of the RollbackRuleAttribute class.
> 
> This is the preferred way to construct a rollback rule that matches the supplied Exception class, its subclasses, and its nested classes.

However, that last sentence is not honored in the current implementation, since the type information (supplied via the `Class` reference) is not taken into account in the implementation of `getDepth(...)`.


#### コメント 2 by sbrannen

**作成日**: 2022-03-01

Correction to my previous statement. The Javadoc for the `RollbackRuleAttribute(Class)` constructor is _mostly_ correct.

However, the documentation for rollback rules can be improved to warn that unintentional matches may arise if the name of a thrown exception _contains_ the name of a registered exception type.

I am therefore repurposing this issue to improve the documentation.

#### コメント 3 by hduyyg

**作成日**: 2022-03-02

I think this rollback rule is fallible and needs more precise matching rules。
A lot of people don't really read documents。

#### コメント 4 by sbrannen

**作成日**: 2022-03-02

> I think this rollback rule is fallible and needs more precise matching rules。

I agree with you. I've raised #28125 to improve the documentation for `5.3.x`.

And we'll use _this_ issue to improve the behavior in `6.0`.

Specifically:

- If an _exception pattern_ is supplied as a `String` -- for example, in XML configuration or via `@Transactional(rollbackForClassName = "example.CustomException")` -- the existing `contains()` logic will continue to be used.
- If a concrete _exception type_ is supplied as a `Class` reference -- for example, via `@Transactional(rollbackFor = example.CustomException.class)` -- new logic will be implemented which honors the supplied type information, thereby avoiding an unintentional match against `example.CustomException2` when `example.CustomException` (without the `2)` was supplied as the exception type.


---

## Issue #28111: Support for ImportAware in AOT-processed contexts

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-02-28

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28111

**関連リンク**:
- Commits:
  - [ed4e858](https://github.com/spring-projects/spring-framework/commit/ed4e8586a55db64eb50876e204292571a0b23242)
  - [b388dac](https://github.com/spring-projects/spring-framework/commit/b388dac236389f9501da898db55c9addc404d848)
  - [2ccb1a1](https://github.com/spring-projects/spring-framework/commit/2ccb1a1291eeac6a84c7237c7f87fa48173257fa)
  - [5944f09](https://github.com/spring-projects/spring-framework/commit/5944f0912952f6e56ded849220679149317206a9)
  - [369ef07](https://github.com/spring-projects/spring-framework/commit/369ef07660e550f478ba04975af58c06ad98a7c7)
  - [eba6cb9](https://github.com/spring-projects/spring-framework/commit/eba6cb964e532bb2a6872cc787bf55d4a1ae02c9)
  - [e103d0b](https://github.com/spring-projects/spring-framework/commit/e103d0b7c333c87c6dbffdf1f1559f6c70b53fd1)
  - [12f4201](https://github.com/spring-projects/spring-framework/commit/12f4201c82da0ead72d3055d9b8f5fb816d0a4fc)
  - [145401f](https://github.com/spring-projects/spring-framework/commit/145401fc5348d3cbe354cd8928d8095effd1183f)

### 内容

When a context is pre-processed by the AOT engine, there's no configuration class parsing at runtime anymore and the link between an `ImportAware` configuration class and the class that imported it should be preserved.

This can be done by computing the mapping and then providing a post procesor that honors the callback.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-03-09

Closed by https://github.com/spring-projects/spring-framework/commit/9ba927215edc7b8f936d6205d8f1c0c10b2202a2

---

## Issue #28120: Support for compiling and running generated code in tests

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-01

**ラベル**: type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28120

**関連リンク**:
- Commits:
  - [30cd14d](https://github.com/spring-projects/spring-framework/commit/30cd14d61ddeb6851b4e4b30f8824465975dfe79)
  - [4d24d9e](https://github.com/spring-projects/spring-framework/commit/4d24d9e5c0e93d50329274d63222ce1705e22625)
  - [7255a8b](https://github.com/spring-projects/spring-framework/commit/7255a8b48e6bedb3e964c44d1a8e00bb6e240d07)
  - [653dc59](https://github.com/spring-projects/spring-framework/commit/653dc5951d24fc2c5560cb38314f536a67c3bbbf)
  - [d311dce](https://github.com/spring-projects/spring-framework/commit/d311dceaea25dd8bf9fec89c1d98c4d356bb1980)
  - [4b82546](https://github.com/spring-projects/spring-framework/commit/4b82546b975a95bb69b70d892e1661accf869d7d)
  - [54c591d](https://github.com/spring-projects/spring-framework/commit/54c591dfdcb76e077b2cb39e528717e6a47cc8ac)
  - [55cb758](https://github.com/spring-projects/spring-framework/commit/55cb758619915b3f63b85e1b6d5a7f5a1192e5a9)
  - [3ba3b58](https://github.com/spring-projects/spring-framework/commit/3ba3b5846ae764bbb445107f1f6d0aaf1357affd)
  - [d4d1759](https://github.com/spring-projects/spring-framework/commit/d4d1759315b5557c75b4786e15dd4483407afcf2)
  - [d47b115](https://github.com/spring-projects/spring-framework/commit/d47b115a450888fc1099bfc985b3c6de07665c59)
  - [f031a76](https://github.com/spring-projects/spring-framework/commit/f031a765e709bf9495f22ed7c89af409a7fe4f7c)
  - [4f93dad](https://github.com/spring-projects/spring-framework/commit/4f93dad28bf4e045672104add7158376b9710c66)
  - [e4a812e](https://github.com/spring-projects/spring-framework/commit/e4a812e3195af6511a9a51cbafabdcce8be0cc23)
  - [8e0d29d](https://github.com/spring-projects/spring-framework/commit/8e0d29daf95bcd823f2b4233fb3b1e04048320c7)
  - [446674f](https://github.com/spring-projects/spring-framework/commit/446674f0dbb23481f51ce0f8a5f39a13d7c0b4c3)

### 内容

With the AOT engine now generating an optimized view of the bean factory, there is a need to be able to compile and run the generated code in a test to assert that it has the intended effect. 

Such general purpose utility could land in a new `spring-core-test` module for a start (with, potentially, a dependency on `spring-core`). 

### コメント

#### コメント 1 by philwebb

**作成日**: 2022-03-02

I've pushed a branch [here](https://github.com/philwebb/spring-framework/tree/gh-28120) for review. Currently the package is under `org.springframework.aot.test.generator`.

---

## Issue #28144: Replace KotlinBodySpec with proper ResponseSpec extensions

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-03-08

**ラベル**: in: test, type: enhancement, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28144

**関連リンク**:
- Commits:
  - [617ba84](https://github.com/spring-projects/spring-framework/commit/617ba845771f8cf6d8f7e30ba8ff66214e97bc54)
  - [afa307e](https://github.com/spring-projects/spring-framework/commit/afa307e7dca4458c08a7a53ecb9ae8fd37a6dddd)
  - [1be3eec](https://github.com/spring-projects/spring-framework/commit/1be3eecb2a088af4c5b9bc44c8a68cc724074be3)

### 内容

Due to #20606, we had to introduce `KotlinBodySpec` in Spring Framework 5.0.x in order to unlock Kotlin developers for most common use cases of `WebTestClient` in Kotlin.

[As of Kotlin 1.6, the related Kotlin issue on recursive generic types has been fixed](https://blog.jetbrains.com/kotlin/2021/11/kotlin-1-6-0-is-released/#improved-type-inference-for-recursive-generic-types), making it possible for Spring Framework to provide regular reified extensions for `ResponseSpec` methods that takes a `ParameterizedTypeReference` (to be verified of course, but that's my current understanding).

As a consequence, my proposal is in Spring Framework 6 to remove `KotlinBodySpec`, as well as the current `inline fun <reified B : Any> ResponseSpec.expectBody(): KotlinBodySpec<B>` extension, and introduce regular reified extensions for `ResponseSpec.expectBody` since `ResponseSpec.expectBodyList`, `ResponseSpec.returnResult` extensions already exists.

This is a breaking change, I am afraid impossible to avoid, so it should be mentioned in the release notes. I am not sure we should deprecate the related extension in Spring Framework 5.3 since we need to support Kotlin 1.5 there and the current extension prevent to introduce the new proper one describe in this issue.

### コメント

#### コメント 1 by sdeleuze

**作成日**: 2022-03-16

See [related comment in KT-5464](https://youtrack.jetbrains.com/issue/KT-5464#focus=Comments-27-5878033.0-0) where we discussed the fact that while this is now usable with Kotlin 1.6+, Kotlin is still more verbose than Java so there is room for improvement.

---

## Issue #28146: WebSocketConfigurationSupport.DefaultSockJsSchedulerContainer is private and exposed as a Bean

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-08

**ラベル**: type: bug

**URL**: https://github.com/spring-projects/spring-framework/issues/28146

**関連リンク**:
- Commits:
  - [67b7c16](https://github.com/spring-projects/spring-framework/commit/67b7c16bc0b5e9f21d38173676d52db4541a997f)

### 内容

`defaultSockJsSchedulerContainer()` is a package protected method that exposes a type that is private. This makes it impossible to create a programmatic equivalent of this configuration arrangement.

---

## Issue #28147: Upgrade Kotlin to 1.6.20-RC

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-03-09

**ラベル**: type: dependency-upgrade, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28147

### 内容

Since Kotlin 1.6.20 won't be available for M3, the upgrade to 1.6.20 will be part of M4, see #28036.

---

## Issue #28148: Add support for contributing runtime hints for generated code

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-09

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28148

**関連リンク**:
- Commits:
  - [14b147c](https://github.com/spring-projects/spring-framework/commit/14b147ce704151e5d554ff10181b24ff01d1059d)

### 内容

If a component wishes to contribute hints for generated code, it can use `TypeReference.of` taking a `String` but we could just as well offer a way to create a type reference using a `ClassName`.

---

## Issue #28149: Add GeneratedType infrastructure

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-09

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28149

**関連リンク**:
- Commits:
  - [fd191d1](https://github.com/spring-projects/spring-framework/commit/fd191d165bb6c886d8c3720c96240441f89d75cd)

### 内容

Contributions need a way to contribute code without having to care about naming and access to privileged packages. A generation context of some kind offering a way to access such type and contribute methods is a first step towards that goal.

---

## Issue #28150: Introduce ApplicationContextAotGenerator

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-09

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28150

**関連リンク**:
- Commits:
  - [9b07457](https://github.com/spring-projects/spring-framework/commit/9b07457d06d0bfc5f87d157a79a227b66b9aee2b)

### 内容

Based on https://github.com/spring-projects/spring-framework/issues/28065 and https://github.com/spring-projects/spring-framework/issues/28088, we are now capable of creating an entry point for processing a `GenericApplicationContext` ahead of time. 

The generator refreshes the context for AOT processing  first, and then identifies the relevant contributions that are applicable for contributed bean definitions. It then invokes them so that code and runtime hints are contributed.

---

## Issue #28151: Update AOT processing to account for multiple init or destroy methods

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-09

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28151

**関連リンク**:
- Commits:
  - [76457a5](https://github.com/spring-projects/spring-framework/commit/76457a542d4e9b5cd7f9a7620b3b7ecdede98425)
  - [672555a](https://github.com/spring-projects/spring-framework/commit/672555a568445d27ab3d1efc0d87dd9bde779acc)
  - [4a35b6c](https://github.com/spring-projects/spring-framework/commit/4a35b6c48d19c23a8146afdf2d07251c893c0acb)
  - [4ecda24](https://github.com/spring-projects/spring-framework/commit/4ecda241fbb18644b36bf968be5d1624e623016e)

### 内容

Now that #28013 is implemented we need to make sure that the bean definition is registered with the appropriate init and destroy method names.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-03-10

I am blocked. I've added `AotContributingBeanPostProcessor` to the BPP that detects custom init and destroy methods. I am now left with the choice of mutating the `RootBeanDefinition`. From an AOT perspective, that's alright as the bean instance supplier is generated first (and therefore the contributors are invoked upfront).

From a context perspective, it is a little bit odd as `MergedDefinitionBeanPostProcessor` explicitly states that the methods of the base `BeanDefinition` class couldn't be invoked. 

Looking at things from a generic fashion, if `MergedDefinitionBeanPostProcessor` did register those using the API that was created as part of #28103, then this PP shouldn't even have to be an aot-contributing. It kind of shows in the current implementation where it mutates the `RootBeanDefinition` if necessary and always return a `null` contribution.

---

## Issue #28153: BeanRegistrationBeanFactoryContribution should expect a RootBeanDefinition

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-10

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/28153

**関連リンク**:
- Commits:
  - [a0061b7](https://github.com/spring-projects/spring-framework/commit/a0061b7fb944b70d6d1e581ff46c4e16ed1071e8)

### 内容

Given the contract of `MergedBeanDefinitionPostProcessor` and the AOT equivalent, we can expect that bean definitions suitable for code generation are `RootBeanDefinition` instances.

---

## Issue #28154: Ambiguous check only applied to constructors

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-03-10

**ラベル**: type: task, in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28154

**関連リンク**:
- Commits:
  - [93a2651](https://github.com/spring-projects/spring-framework/commit/93a26514175c7b88537b6710e4559552ae484a41)

### 内容

When a constructor should be invoked to create a bean instance, there is the danger that several flavors exist with different parameter types so that the call to `new MyBean(attributes.get(0)` is ambiguous as the type is not declared.

There is an explicit check for this case where an explicit type-based method on `InjectedElementAttributes` is used. Unfortunately, it hasn't been applied to factory methods that suffer from the same problem if several methods have a similar signature.



---

## Issue #28187: Add types to represent RFC 7807 problem details and exceptions

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-03-16

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28187

### 内容

The goal for this issue is to add a representation for an RFC 7807 problem detail, and integrate it into Spring MVC and Spring WebFlux error response handling.

On the WebFlux side we have the `ResponseStatusException` hierarchy which contains HTTP status, a reason, and headers. We can now add a `ProblemDetail` as the body. This provides full encapsulation of all error response details within the exception.

On the Spring MVC side, we have the `DefaultHandlerExceptionResolver` which maps exceptions to HTTP status and headers, so exceptions do not themselves contain that information. Furthermore the exception hierarchy does not have a single base class where this can be added. We can add an interface to represent an error response, e.g. `ErrorResponse`, similar to the information exposed from `ResponseStatusException` on the WebFlux side, and then have all Spring MVC exceptions implement it in order to expose it in which case `DefaultHandlerExceptionResolver` no longer needs mapping logic.

`ResponseEntityExceptionHandler` is a base class for a controller advice that uses an `@ExceptionHandler` method to render error details. It has been around for some time, but so far application have had to extend it to decide on the error body format. We can now fill in the blank and use `ProblemDetail` for `ResponseError` exceptions that expose such information. A similar class does not exist for WebFlux but can be added.

`ResponseEntity` handling for both Spring MVC and WebFlux should support `ProblemDetail` and `ErrorResponse` as return types, automatically setting the response status, headers, and body accordingly. This is also an opportunity to set the `instance` field of `ProblemDetail` to the request path as a fallback if `instance` hasn't been set.



### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-03-16

See commits linked the umbrella issue #27052.

---

