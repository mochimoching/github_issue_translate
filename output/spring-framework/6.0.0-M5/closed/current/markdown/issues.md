# Spring Framework GitHub Issues

取得日時: 2026年01月06日 12:59:06

取得件数: 88件

---

## Issue #28298: findAnnotationOnBean finds annotations from a static @Bean method's enclosing class

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2022-04-07

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28298

**関連リンク**:
- Commits:
  - [3da2b5c](https://github.com/spring-projects/spring-framework/commit/3da2b5c1b914a20f6728e614f51d8eb25d956c3d)
  - [a364410](https://github.com/spring-projects/spring-framework/commit/a36441064639eed2ed79986fce20f82ea8feef3a)
  - [a14650e](https://github.com/spring-projects/spring-framework/commit/a14650e0dc37ad36e0d1c1d8ebbb0440bcfd312b)
  - [a1fe05f](https://github.com/spring-projects/spring-framework/commit/a1fe05f40b02cc79dc3777ff6f90a04ac4de6eac)

### 内容

**Affects:** 5.3.x

When a bean is defined using a static method, `findAnnotationOnBean` finds an annotation from the `@Configuration` class to which the static `@Bean` method belongs. The annotation is not found if the `@Bean` method is not static.

The following tests illustrate this behavior:

```java
package com.example;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

import org.junit.jupiter.api.Test;

import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static org.assertj.core.api.Assertions.assertThat;

class FindAnnotationOnBeanTests {

    @Test
    void beanDefinedInInstanceMethodDoesNotHaveAnnotationsFromItsConfigurationClass() {
        beanDoesNotHaveAnnotationsFromItsConfigurationClass(InstanceBeanMethodConfiguration.class);
    }

    @Test
    void beanDefinedInStaticMethodDoesNotHaveAnnotationsFromItsConfigurationClass() {
        beanDoesNotHaveAnnotationsFromItsConfigurationClass(StaticBeanMethodConfiguration.class);
    }

    void beanDoesNotHaveAnnotationsFromItsConfigurationClass(Class<?> config) {
        try (AnnotationConfigApplicationContext context = new AnnotationConfigApplicationContext(config)) {
            ExampleAnnotation annotation = context.getBeanFactory().findAnnotationOnBean("exampleBean",
                    ExampleAnnotation.class);
            assertThat(annotation).isNull();
        }
    }

    @Configuration
    @ExampleAnnotation
    static class StaticBeanMethodConfiguration {

        @Bean
        static String exampleBean() {
            return "example";
        }

    }

    @Configuration
    @ExampleAnnotation
    static class InstanceBeanMethodConfiguration {

        @Bean
        String exampleBean() {
            return "example";
        }

    }

    @Target(ElementType.TYPE)
    @Retention(RetentionPolicy.RUNTIME)
    static @interface ExampleAnnotation {

    }

}
```

`beanDefinedInInstanceMethodDoesNotHaveAnnotationsFromItsConfigurationClass` passes but `beanDefinedInStaticMethodDoesNotHaveAnnotationsFromItsConfigurationClass` fails.

### コメント

#### コメント 1 by 284831721

**作成日**: 2022-04-08

I can't understand, so, which test result is expected? first or second.

From the `findAnnotationOnBean` method's comment describe as follow, I think test 1 is the expected behavior, am I right?

```
/**
	 * Find an {@link Annotation} of {@code annotationType} on the specified bean,
	 * traversing its interfaces and super classes if no annotation can be found on
	 * the given class itself, as well as checking the bean's factory method (if any).
	 * @param beanName the name of the bean to look for annotations on
	 * @param annotationType the type of annotation to look for
	 * (at class, interface or factory method level of the specified bean)
	 * @return the annotation of the given type if found, or {@code null} otherwise
	 * @throws NoSuchBeanDefinitionException if there is no bean with the given name
	 * @since 3.0
	 * @see #getBeanNamesForAnnotation
	 * @see #getBeansWithAnnotation
	 */

```

#### コメント 2 by wilkinsona

**作成日**: 2022-04-08

Both should pass. The tests are illustrating the described difference between static and instance bean methods.

---

## Issue #28398: Avoid collectList when sending a Flux of objects as JSON using WebClient

**状態**: closed | **作成者**: micopiira | **作成日**: 2022-04-29

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28398

**関連リンク**:
- Commits:
  - [ce56846](https://github.com/spring-projects/spring-framework/commit/ce568468aed09147e335b5d5a717e1b2dac581a8)

### 内容

Would it be possible to send a flux of objects in the request body using WebClient with "Content-Type: application/json" but avoid having to collect the whole flux as a list in memory?

Let's say I have a Flux containing millions of elements and my target server only accepts non-streaming content-types, the Jackson2JsonEncoder would then call "collectList()" on the flux, possibly running out of memory.

Couldn't the Jackson2JsonEncoder somehow write the objects as they come available?

### コメント

#### コメント 1 by poutsma

**作成日**: 2022-05-09

It is possible, but not with `application/json` as the Content-Type; it needs to be `application/x-ndjson` instead.

There is significant overhead for writing JSON content individually instead of collectively. That is why the `Jackson2JsonEncoder` collects to a list by default, and serializes that. If you specify a streaming mime-type, set to `application/x-ndjson` by default–but changeable via the `streamingMediaTypes` property, then the `Jackson2JsonEncoder` will not collect the list but stream them as they arrive, with a newline in between the elements.

Does that answer your question?

#### コメント 2 by micopiira

**作成日**: 2022-05-09

Hey, I'm trying to POST to a server that only accepts `application/json` . With something more low level than WebClient, like reactor-netty I could do something like this:

        Flux<String> flux = Flux.range(0, 1000000).map(Object::toString);
        final Mono<HttpClientResponse> response = httpClient.headers(headers -> {
                    headers.set(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON.toString());
                    headers.set(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON.toString());
                }).post()
                .uri("/url")
                .send(ByteBufFlux.fromString(flux
                        .map(o -> {
                            try {
                                return objectMapper.writeValueAsString(o);
                            } catch (JsonProcessingException e) {
                                throw new RuntimeException(e);
                            }
                        }).zipWith(Flux.just(",").repeat(), (a, b) -> a + b).startWith("[").concatWithValues("]")))
                .response();

Which would then, atleast for what I know stream the objects to the target as they come available without having to wait for all of them.

Would this kind of behaviour be possible to implement in WebClient or should I stick with more low level clients like reactor-netty?

#### コメント 3 by poutsma

**作成日**: 2022-05-10

>I'm trying to POST to a server that only accepts application/json 

You can change the `streamingMediaTypes ` property of `Jackson2JsonEncoder` from the default to `application/json`, and trigger the streaming behavior that way. The reference docs explains [how to change codec defaults](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#webflux-config-message-codecs).

#### コメント 4 by micopiira

**作成日**: 2022-05-11

I see,   however it does not produce valid JSON "out of the box". Heres what I tried:

```java
private final WebClient webClient = WebClient.builder()
   .baseUrl("http://localhost:8080/")
   .codecs(clientCodecConfigurer -> {
     final Jackson2JsonEncoder jackson2JsonEncoder = new Jackson2JsonEncoder();
     jackson2JsonEncoder.setStreamingMediaTypes(List.of(MediaType.APPLICATION_JSON));
     clientCodecConfigurer.defaultCodecs().jackson2JsonEncoder(jackson2JsonEncoder);
    })
   .build();

    Flux<MyEntity> flux = ...;
    webClient.post()
               .uri("/")
               .contentType(MediaType.APPLICATION_JSON)
               .accept(MediaType.APPLICATION_JSON)
               .body(flux, MyEntity.class)
               .retrieve()
               .bodyToMono(MyResponse.class)
```

This will not wrap the JSON in an array nor add commas between the items. Should I manually map my `Flux<MyEntity>` into a `Flux<String>` with the wrapping `[` & `]` and commas in between the items?

#### コメント 5 by rstoyanchev

**作成日**: 2022-05-17

Looking at the Javadoc of `setStreamingMediaTypes` it's mainly about flushing per item (for event streams that emit periodically) vs a single flush at the end (for continuous streams).

Maybe, if we are in the [streaming section](https://github.com/spring-projects/spring-framework/blob/874077d16ec126ca19d4b9fbb4157cfdc4eac382/spring-web/src/main/java/org/springframework/http/codec/json/AbstractJackson2Encoder.java#L155-L183) and the media type is "application/json" (i.e. explicitly set as a streaming media type), we could simply add the opening and closing square brackets to ensure valid JSON is produced. 

We could also switch to flushing at some regularity > 1 (or just leave it to the underlying server buffer) since we know it's a media type that implies continues writing and shouldn't require explicit flushes. In which case I'm even wondering about removing the non-streaming section entirely, and doing this by default, so that we always write `Flux` items as they come with flushing as the only difference between streaming and non-streaming media types.


#### コメント 6 by hu553in

**作成日**: 2023-07-11

@rstoyanchev is there a way to override this behavior to old-way now?
I need to temporarily configure Spring WebFlux Kotlin `Flow` endpoints to have `Content-Type: application/json` and to be collected to list before writing...
Because my frontend app is not able to process stream at the moment

#### コメント 7 by bclozel

**作成日**: 2023-07-11

@hu553in this issue is about the other way around: avoiding to buffer all elements before sending them as a single JSON document from the client. If you're using the server side of WebFlux and an `application/json` content type, data should not be streamed to the client. Maybe create a new StackOverflow question explaining the problem and showing how you're using this?

#### コメント 8 by hu553in

**作成日**: 2023-07-11

@bclozel [done](https://stackoverflow.com/questions/76663504/how-to-return-kotlin-flow-as-non-streaming-json-data-using-content-type-applica), thank you... :)
will be glad if you check it, maybe you have simple answer.. I don't think that this is very complex issue

---

## Issue #28438: Update documentation for RFC 7807 support

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-05-10

**ラベル**: type: documentation, in: web

**URL**: https://github.com/spring-projects/spring-framework/issues/28438

**関連リンク**:
- Commits:
  - [eea793b](https://github.com/spring-projects/spring-framework/commit/eea793be98ae70f2f6be970738678fe927c2cf4a)
  - [ff9a4ab](https://github.com/spring-projects/spring-framework/commit/ff9a4ab35c1dad7e1f1ba640280461fc84cf2300)

### 内容

Following the changes for #27052 and sub-tasks, we need an update in the reference documentation. In the mean time, the best alternative is the commit history for #27052 and sub-tasks, the Javadoc  on the added types, and the [sample project](https://github.com/rstoyanchev/sandbox-rfc7807).

---

## Issue #28439: Add WebFlux equivalent of ResponseEntityExceptionHandler

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-05-10

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28439

**関連リンク**:
- Commits:
  - [b64835d](https://github.com/spring-projects/spring-framework/commit/b64835d2c8d6e195aa6d553fda6230b392b6f4f0)

### 内容

This would be helpful to facilitate customization of error messages for all framework exceptions especially for RFC 7807 problem details, under #27052.

### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-07-13

Fixed in 263811ecfa912a55bce8d0371ed20202abcf5dd5 but referenced wrong issue.

---

## Issue #28455: Resolve package cycle around MissingServletRequestPartException

**状態**: closed | **作成者**: jhoeller | **作成日**: 2022-05-12

**ラベル**: in: web, type: regression

**URL**: https://github.com/spring-projects/spring-framework/issues/28455

**関連リンク**:
- Commits:
  - [2269c00](https://github.com/spring-projects/spring-framework/commit/2269c0063a4f56985a8903b16d922ef05a7e6b30)

### 内容

Since #27910 / #27948 `web.multipart.MissingServletRequestPartException` extends `web.bind.ServletRequestBindingException` which unfortunately creates a package cycle since the `web.bind` package depends on `web.multipart` within its binder implementations.

The root of the problem there is that `MissingServletRequestPartException` serves two rather different purposes: It is being thrown by `RequestPartServletServerHttpRequest` as a low-level API exception (which is why it lives in the `web.multipart` package), but then also used by `RequestParamMethodArgumentResolver` for handler method argument binding (for which it should actually live in `web.bind`). The proper solution would be to use a different exception type for the bind purpose, and to only let that one extend `ServletRequestBindingException` as of 6.0. Let's revisit this for M5.

### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-05-12

It looks like originally `MissingServletRequestPartException` came as a result of differentiating 4xx vs 5xx exception related to multipart handling, see #13284 and related fix 56c8c69c4ce04e9d35d19e26d279ccd3b2e5a385, and prior to that `RequestParamMethodArgumentResolver` used to raise the base class `ServletRequestBindingException`. 

I think it would be still useful to have a single exception for a missing part, no matter where it was detected. `RequestPartServletServerHttpRequest` is under `web.multipart` because it relates to multipart processing and that's the lowest place where it is needed. 

One alternative would be to revert the changes under #27948, i.e. make it extend `ServletException` again, and document more explicitly the reason it does not extend `ServletRequestBindingException` is that it can be raised at a lower level and lives in a different package. In retrospect, I suspect #27910 was more a question than an actual problem. This essentially answers the "if there is no good reason" question under #27910.




---

## Issue #28458: Add resolver for request attributes for `@HttpExchange` methods

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-05-13

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28458

**関連リンク**:
- Commits:
  - [496c1dc](https://github.com/spring-projects/spring-framework/commit/496c1dcae195194be4c6c829b5e6a510d0817032)
  - [495507e](https://github.com/spring-projects/spring-framework/commit/495507e5d40bec0b7cd1d2759e9aed81bdb3ad07)

### 内容

This can be used to provide hints to the `WebExchangeFilter` chain which is useful for security and other reasons.

---

## Issue #28469: Introduce a meta-annotation that indicates the annotated element requires reflection hints

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-05-17

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28469

**関連リンク**:
- Commits:
  - [255a52b](https://github.com/spring-projects/spring-framework/commit/255a52bc7a5f10a1f142f45e4ef7118f241314aa)
  - [4cca190](https://github.com/spring-projects/spring-framework/commit/4cca190aad3cf643c765f39655432e0ebd00549e)

### 内容

We're now at a stage where we need to port a number of hints in a sustainable way and avoid having to write dedicated code for common patterns we have in the portfolio. 

On such simple pattern is the following:

```java
@EventListener
public void onContextRefresh(ContextRefreshedEvent event) { ... }
```

The internal implementation processing `@EventListener` is creating a wrapper that invokes the method via reflection so that needs an invocation hint to work in restricted environment (native image).

A more complex pattern could be

```java
@GetMapping("/dtos/{id}")
public MyDto findById(String id) { ... }
```

In this case, not only the `findById` method is invoked by reflection but the chances are high that `MyDto` is going to be serialized using some sort of converter and therefore require additional hints.

Rather than having dedicated `BeanRegistrationAotProcessor` or `BeanFactoryInitializationAotProcessor` we could build a generic one that checks for the presence of a certain annotation. We could then annotate the annotations that we know require reflection so that they are processed semi-automatically.

```java
@Target({ElementType.METHOD, ElementType.ANNOTATION_TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Reflective
public @interface EventListener { ... }
``` 
 
`@Reflective` could take the strategy to use (a bit like `@Conditional` does). This would help us implement a more fine-grained algorithm like the MVC use case.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-05-17

One thing to mention is that adding this meta-annotation can be temporary. Once the underlying infrastructure is fully resolved ahead-of-time, and therefore the need for reflection for AOT-based context is no longer necessary, the meta-annotation can be simply removed.

---

## Issue #28474: Introduce AotDetector mode

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-05-18

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28474

**関連リンク**:
- Commits:
  - [da8c4de](https://github.com/spring-projects/spring-framework/commit/da8c4de263835afb3adf2c26ab62afb214157b85)
  - [c606f75](https://github.com/spring-projects/spring-framework/commit/c606f757739aa30e801ca20837e51905dbb09560)
  - [a9295e8](https://github.com/spring-projects/spring-framework/commit/a9295e877e4388e83bf09b633de31486e30f1963)

### 内容

We need a way to opt-in for the use of AOT on the JVM. Right now, we rely on the system property that is set when building a native image (or running with the native image agent with Native Build Tools), but this should be restricted to things that should really behave differently there.

Spring Native has [an `AotModeDetector`](https://github.com/spring-projects-experimental/spring-native/blob/d176e2d360350c5f91d0a44f9b7fefddd3f6d2db/spring-native/src/main/java/org/springframework/nativex/AotModeDetector.java#L29) we could use as an inspiration. This will also be relevant for #28205.

---

## Issue #28491: Support default methods in `@HttpExchange` interface

**状態**: closed | **作成者**: wonwoo | **作成日**: 2022-05-20

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28491

**関連リンク**:
- Commits:
  - [cc56da7](https://github.com/spring-projects/spring-framework/commit/cc56da7735291d1576d08f0f853e6dad07de0aa6)

### 内容

```java
@HttpExchange("http://localhost:8080")
public interface GreetingClient {

    @GetExchange("/greeting")
    Flux<Greeting> greetings();

    @PostExchange("/greeting")
    Mono<Greeting> greetings(@RequestBody Greeting greeting);

    default Flux<Greeting> defaultMethod() {
        return greetings(new Greeting("default method test"))
                .flatMapMany(it -> greetings());
    }
}
```

defaultMethod method I hope it works! 


---

## Issue #28492: Support property placeholders in url attribute of @HttpExchange

**状態**: closed | **作成者**: xuan | **作成日**: 2022-05-20

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28492

**関連リンク**:
- Commits:
  - [2a2fba6](https://github.com/spring-projects/spring-framework/commit/2a2fba6a37666b41205565b7d1a804373a6635d2)

### 内容

**Affects:** 6.0.0-SNAPSHOT

---
Hi Spring Team,

Can you please add the ability to reference properties for `@HttpExchange`, `@GetExchange`, and `@PostExchange` defined in `application.yaml`?

Right now, I have to hard code my URL in the annotation:

```java
@HttpExchange(url = "/multitenant/public/api")
public interface CumulusRepository {

    @GetExchange("/get_stuff")
    Cumulus getCumulusAlerts(@RequestHeader Map<String, String> headers);

    @PostExchange("/getAccessToken")
    Token getAccessToken(@RequestBody String credential);
}
```

But I wish to define my URL in `application.yaml` and reference it in the annotations like this:

```java
@HttpExchange(url = "${cumulus.baseUrl}")
public interface CumulusRepository {

    @GetExchange("${cumulus.alertUrl}")
    Cumulus getCumulusAlerts(@RequestHeader Map<String, String> headers);

    @PostExchange("${cumulus.tokenUrl}")
    Token getAccessToken(@RequestBody String credential);
}
```



### コメント

#### コメント 1 by jcthalys

**作成日**: 2022-12-02

This is still not working for me:
```java 
// using spring boot 3.0.0 and framework 6.0.2
@SpringBootApplication
public class HttpInterfaceApplication {

	public static void main(String[] args) {
		SpringApplication.run(HttpInterfaceApplication.class, args);
	}

	@Bean
	ApplicationListener<ApplicationReadyEvent> ready(GoogleClient googleClient) {
		return event -> {
			String googlePage = googleClient.getGooglePage();
			System.out.println(googlePage);
		};
	}

	@Bean
	GoogleClient googleClient(HttpServiceProxyFactory factory) {
		return factory.createClient(GoogleClient.class);
	}

	@Bean
	HttpServiceProxyFactory getHttpServiceProxyFactory(WebClient.Builder builder) {
		return HttpServiceProxyFactory.builder()
				.clientAdapter(WebClientAdapter.forClient(builder.build())).build();
	}
}

@HttpExchange(url = "${google.url}")
interface GoogleClient {
	@GetExchange
	String getGooglePage();
}
```
Error:
```log
java.lang.IllegalArgumentException: Map has no value for 'google.url'
	at org.springframework.web.util.UriComponents$MapTemplateVariables.getValue(UriComponents.java:348) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.UriComponents.expandUriComponent(UriComponents.java:263) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.HierarchicalUriComponents$FullPathComponent.expand(HierarchicalUriComponents.java:921) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.HierarchicalUriComponents.expandInternal(HierarchicalUriComponents.java:439) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.HierarchicalUriComponents.expandInternal(HierarchicalUriComponents.java:52) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.UriComponents.expand(UriComponents.java:161) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.DefaultUriBuilderFactory$DefaultUriBuilder.build(DefaultUriBuilderFactory.java:391) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.util.DefaultUriBuilderFactory.expand(DefaultUriBuilderFactory.java:149) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.reactive.function.client.DefaultWebClient$DefaultRequestBodyUriSpec.uri(DefaultWebClient.java:228) ~[spring-webflux-6.0.2.jar:6.0.2]
	at org.springframework.web.reactive.function.client.DefaultWebClient$DefaultRequestBodyUriSpec.uri(DefaultWebClient.java:189) ~[spring-webflux-6.0.2.jar:6.0.2]
	at org.springframework.web.reactive.function.client.support.WebClientAdapter.newRequest(WebClientAdapter.java:105) ~[spring-webflux-6.0.2.jar:6.0.2]
	at org.springframework.web.reactive.function.client.support.WebClientAdapter.requestToBody(WebClientAdapter.java:69) ~[spring-webflux-6.0.2.jar:6.0.2]
	at org.springframework.web.service.invoker.HttpServiceMethod$ResponseFunction.lambda$initBodyFunction$5(HttpServiceMethod.java:378) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.service.invoker.HttpServiceMethod$ResponseFunction.execute(HttpServiceMethod.java:288) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.service.invoker.HttpServiceMethod.invoke(HttpServiceMethod.java:105) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.web.service.invoker.HttpServiceProxyFactory$HttpServiceMethodInterceptor.invoke(HttpServiceProxyFactory.java:271) ~[spring-web-6.0.2.jar:6.0.2]
	at org.springframework.aop.framework.ReflectiveMethodInvocation.proceed(ReflectiveMethodInvocation.java:184) ~[spring-aop-6.0.2.jar:6.0.2]
	at org.springframework.aop.framework.JdkDynamicAopProxy.invoke(JdkDynamicAopProxy.java:218) ~[spring-aop-6.0.2.jar:6.0.2]

```
When I use the url directly it works fine

#### コメント 2 by renatomrcosta

**作成日**: 2022-12-02

> This is still not working for me:

I stumbled in the same issue, and found out perhaps a clue to clarify if the URL field considers `application properties` at all, or just URI placeholders.

This error indicates that the application properties with placeholders are not considered at all: If you try, it just considers it a path: (like when you call `"/v1/api/customer/{customerId}"`. The `$` sign in java or `\$` in Kotlin were not parsed.

```kotlin
@HttpExchange(url = "{httpbin}") // I chose a single name here, because if we try to simply remove the braces and add the $ back, it still doesn't work, but it's easy enough to use to test.
interface HttpBinClient {
    @GetExchange("/anything")
    fun anything(@PathVariable("httpbin") httpbin: String): Mono<String>
}
```

(Repo with working example here: [LINK](https://github.com/renatomrcosta/springboot3releaseplayground/blob/spring-issue-28492/src/main/kotlin/com/xunfos/springboot3releaseplayground/Springboot3releaseplaygroundApplication.kt))

so, in this case: is it truly intended that the URL and other fields can be parameterized with application properties at all? If so, then this ticket shouldn't be closed as completed. 

Otherwise @jcthalys , I recommend taking the more verbose approach of providing a webClient with its baseUrl set per httpProxyFactory you need to build for the time being, and not setting the URL property at the annotation level. It's the approach I'll be taking for the time being.

---

## Issue #28496: Break package tangle between o.s.aot and o.s.core

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-05-20

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28496

**関連リンク**:
- Commits:
  - [16eff68](https://github.com/spring-projects/spring-framework/commit/16eff6835748be5316520b313e08a8a481b900d1)

### 内容

Two hints registrar have been recently added that creates a cycle between those two packages. We should consider moving those, perhaps all the way up to `spring-context` as they aren't really useful without it.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-05-20

The tangle for spring factories hint is a little bit problematic as it relies on a package protected method in `SpringFactories`, cc @philwebb 

#### コメント 2 by philwebb

**作成日**: 2022-05-20

Tricky. There's just enough code in `SpringFactoriesLoader.loadFactoriesResource` to make copy/paste unappealing. We could perhaps make it a `protected static` method then have a private subclass in `SpringFactoriesLoaderRuntimeHintsRegistrar` to access it again. Either that, or just make that method public.

#### コメント 3 by philwebb

**作成日**: 2022-05-20

It feels a bit odd to have `spring-context` add the factory hints, I think I'd prefer a `org.springframework.aot.support` package that takes care of registering hints for items in `org.springframework.code`.

It would also be really nice to have a checkstyle rule to enforce the layering.

---

## Issue #28497: Introduce utility to register hints for an annotation that uses AliasFor

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-05-20

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28497

**関連リンク**:
- Commits:
  - [2f94713](https://github.com/spring-projects/spring-framework/commit/2f94713078ddf9ed17426b062bd70bf0ab83fe83)
  - [059b66b](https://github.com/spring-projects/spring-framework/commit/059b66bf26c2aa8b96847938a2eb00e7645c69e1)
  - [2517c72](https://github.com/spring-projects/spring-framework/commit/2517c72f7d2a7406137c25c9f63ccdd35c082979)

### 内容

The core framework allows the use of `@AliasFor` which creates a JDK proxy behind the scenes. Registering a reflection hint for the attributes of the annotation is not enough for this to be used at runtime in a native image. 

To ease the registration, we'll add a utility that takes care of this logic.

---

## Issue #28501: Create UrlResource factory methods that throw unchecked exceptions

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-05-22

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28501

**関連リンク**:
- Commits:
  - [f07e7ab](https://github.com/spring-projects/spring-framework/commit/f07e7ab39d04c0f8b27f3e5678227952cc3ac380)

### 内容

## Overview

`UrlResource` constructors throw checked exceptions which makes it difficult to use them in `java.util.Stream` and `java.util.Optional` APIs or other scenarios when a checked `IOException` is undesirable.

## Proposal

To support such use cases, we should introduce factory methods in `UrlResource` that throw `UncheckedIOException`, initially for the constructor variants that accept a `URI` or `String`.

## Related Issues

- #21515 

---

## Issue #28504: Allow custom HTTP method with @HttpExchange methods

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-05-23

**ラベル**: type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28504

**関連リンク**:
- Commits:
  - [ff890bc](https://github.com/spring-projects/spring-framework/commit/ff890bc1cc11381a3cfffa66f9be9f013adc0b51)

### 内容

`@HttpExchange` is currently only allowed at the class level for inheriting common attributes, but at the method level one has to choose one of the HTTP method specific shortcut annotations. We can allow it at the method level for custom HTTP methods, or less common ones like OPTIONS which won't need a dedicated shortcut.

---

## Issue #28505: Refactor HttpServiceProxyFactory to be suitable as an infrastructure bean

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-05-23

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28505

**関連リンク**:
- Commits:
  - [48c1746](https://github.com/spring-projects/spring-framework/commit/48c1746693e91a0b2b96af837841dab98e535b5a)

### 内容

Currently `HttpServiceProxyFactory` is friendly for programmatic use but is more likely to be declared as a bean since it needs a number of dependencies injected such as as a `ConversionService`, and an `EmbeddedValueResolver` as of #28492. In a Boot application one would also inject `WebClient.Builder`. 

---

## Issue #28506: Support module path scanning for "classpath*:" resource prefix

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-05-23

**ラベル**: in: test, in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28506

**関連リンク**:
- Commits:
  - [fa8b3ef](https://github.com/spring-projects/spring-framework/commit/fa8b3ef8b61319a08d5238888b3a6f77d18f04f9)
  - [19b436c](https://github.com/spring-projects/spring-framework/commit/19b436c6aa14e79e6f3a98c15a8edff2a8c351fc)
  - [190a459](https://github.com/spring-projects/spring-framework/commit/190a459cfa538d16f7a73d23759859e4167a7409)
  - [957faac](https://github.com/spring-projects/spring-framework/commit/957faac91832a7f6e79ceb79bd573c66dde1afa6)
  - [23a58e6](https://github.com/spring-projects/spring-framework/commit/23a58e6bab2b5aecd77e30c2b2d0ee41b643876f)

### 内容

In light of the findings from investigating #21515, we should introduce implicit support for scanning the module path whenever the `classpath*:` resource prefix is used.

This should allow existing applications relying on `classpath*:` semantics to work when migrating to the Java module system (for use cases not already supported by `ClassLoader`-based class path scanning).

For example, `@ComponentScan` should effectively work the same when an application is deployed on the class path or module path.

### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-05-24

This issue has been resolved for inclusion in 6.0 M5.

In the interim, feel free to try out 6.0 snapshots for applications deployed with patched modules.

I've created a new repository for demonstrating the use of the Spring Framework with the Java Module System: https://github.com/sbrannen/spring-module-system

That repository currently contains a single `maven-surefire-patched-module` project which demonstrates support for `@ComponentScan` in a patched module using Maven Surefire.

---

## Issue #28517: Ambiguous behavior for ClassNameGenerator::generateClassName

**状態**: closed | **作成者**: bclozel | **作成日**: 2022-05-24

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28517

**関連リンク**:
- Commits:
  - [63fae8c](https://github.com/spring-projects/spring-framework/commit/63fae8c5a7ea21e4ff59ee094cc4541c048e8e54)

### 内容

`ClassNameGenerator` has two variants for the `generateClassName` feature. One that takes a target `Class<?>` and another that takes a target `String`. I'm a bit confused by the concept of a target here and I think we should explain that a bit more in the javadocs.

These methods also have different behavior:

```java
ClassName first = this.generator.generateClassName(java.io.InputStream.class, "bytes");
// will result in java.io.InputStream__Bytes

ClassName first = this.generator.generateClassName("java.io.InputStream", "bytes");
// will result in __.JavaIoInputStream__Bytes
```

Even if the difference of behavior is intended, the name and docs are very similar. Also, a common use case for the `ClassNameGenerator` is about generating sources in a specific package to work around visibility issues. The second variant can make this case more difficult to achieve.

As a side note, this class is also referring to the now defunct `@see GeneratedClassName`.

cc @philwebb @snicoll 

### コメント

#### コメント 1 by philwebb

**作成日**: 2022-05-24

The `String` variant was added to support generation where there isn't a single class that can be linked. I think it's currently only used in `BeanRegistrationsAotContribution`. We should probably rename that method to make it clearer that there is no target class.

I know @snicoll was wondering about the use of the `__` package in general, perhaps we can make the generated `BeanRegistrations` class be in the same package as the `@SpringBootApplication` class then we can drop the string version entirely.

The `ClassNameGenerator` should be removed, we dropped that class during the prototype work.

#### コメント 2 by snicoll

**作成日**: 2022-06-20

The second method that takes a `String` rather than a `Class<?>` has been removed in 4bd33cb6e0659df2cd0b9fa04feea8fd77e5a16d. I am going to look at the Javadoc and see if we can clarify 

---

## Issue #28518: Add reflection hints for Web controllers

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-05-24

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28518

**関連リンク**:
- Commits:
  - [c956c06](https://github.com/spring-projects/spring-framework/commit/c956c06077a2c2c210bb79c5ef72d7a4527c041d)
  - [966e46c](https://github.com/spring-projects/spring-framework/commit/966e46c833bba197382aa2c1224c67d8576e918c)
  - [6bc1f33](https://github.com/spring-projects/spring-framework/commit/6bc1f3365a604545c8ba2f31efc19398b4e784b8)
  - [3574f3d](https://github.com/spring-projects/spring-framework/commit/3574f3d2c0ba128d967c7e9772e7ed2f32c9619a)
  - [9aefe70](https://github.com/spring-projects/spring-framework/commit/9aefe70bab08b4968e63178fa7e1ee00b8e69ac1)
  - [10244cf](https://github.com/spring-projects/spring-framework/commit/10244cfdd44e6af28bf9eacc5e3388487b35ecc7)
  - [5b21e65](https://github.com/spring-projects/spring-framework/commit/5b21e65f2ad6debc6d32291b2711adfd038669d9)
  - [bc065e8](https://github.com/spring-projects/spring-framework/commit/bc065e8f8344b1c5d1f74f4b39c77e2ef753d06d)
  - [239e979](https://github.com/spring-projects/spring-framework/commit/239e979e5ab5eac58e7fc3134137ae256cc01375)
  - [48d022d](https://github.com/spring-projects/spring-framework/commit/48d022d35ea9df900c84d1ccb7dead868821872c)
  - [ef3f465](https://github.com/spring-projects/spring-framework/commit/ef3f4655326b03860ff20a2b3cde370c3666ef84)
  - [a57dead](https://github.com/spring-projects/spring-framework/commit/a57dead4be7e19c423df867852380b38c1f5ddbc)
  - [0992f85](https://github.com/spring-projects/spring-framework/commit/0992f855e64216970cb2c3f92cf6e6eab0ad62e4)
  - [12d756a](https://github.com/spring-projects/spring-framework/commit/12d756a2520dbd65f55d342ef83a9ce9ea8b4931)
  - [5e56d9c](https://github.com/spring-projects/spring-framework/commit/5e56d9cb2171ff8bb051a8a5c30fbfeae1301d36)
  - [90dcbe8](https://github.com/spring-projects/spring-framework/commit/90dcbe85bde899b9f9d2a1d16d952946806b9fb3)
  - [dee47c3](https://github.com/spring-projects/spring-framework/commit/dee47c366e909dc50978fa19b3dc06a9d73a182d)
  - [2b76a12](https://github.com/spring-projects/spring-framework/commit/2b76a12b86a62cc46886e1b7f0e52ea9d256f899)
  - [ecf39cf](https://github.com/spring-projects/spring-framework/commit/ecf39cfaa6055513ee9918951099aba870ae8c74)
  - [3491563](https://github.com/spring-projects/spring-framework/commit/349156368ffa0a35a7565c1a1f8aeae636a9b666)

### 内容

The core framework invokes `@RequestMapping`-annotated methods (`@GetMapping`, etc) using reflection. To run in a native image, we need hints for those. We may also want to infer that return types are going to be serialized, or that input times are going to be mapped from the request.

All this can go away if we generate an optimized code for the router but let's go the hints route for now.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-05-24

For the annotations themselves and loading `org/springframework/http/mime.types` it would be nice if those were contributed only if the application is going to use it. Adding a `RuntimeHintsRegistrar` in `aot.factories` would not achieve that goal but it's not clear cut where to put `@ImportRuntimeHints`. As it should be consistent, we can't really rely on Spring Boot for that. 

For the annotations, I was tempted to add an import on `org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping` but it's not obvious that's going to be a bean so the annotation there feels a little bit odd.

#### コメント 2 by snicoll

**作成日**: 2022-05-24

Considering that `MergedAnnotations` is required to automatically handle the creation of the proxy. I wonder if dealing with everything that is method specific can be a good thing. This would be more code but more tailored to what is actually happening in the application.

#### コメント 3 by sdeleuze

**作成日**: 2022-06-08

I managed to make `webmvc-tomcat` sample working with https://github.com/sdeleuze/spring-framework/tree/gh-28518. I will refine it based on @snicoll feedback.

#### コメント 4 by sdeleuze

**作成日**: 2022-06-13

This issue will be focused on reflection hints for controllers and reflection-based serialization of parameters annotated
with `@RequestBody` and return values annotated with `@ResponseBody`. I will create subsequent issues for other use-cases (`HttpEntity`, `@ControllerAdvice`, etc.)

---

## Issue #28526: Filtering of BeanRegistrationAotProcessor beans should be optional

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-25

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28526

**関連リンク**:
- Commits:
  - [6f71328](https://github.com/spring-projects/spring-framework/commit/6f71328ba6f8d2d6d001cf26f24459852ee5dd8f)

### 内容

Currently `BeanDefinitionMethodGeneratorFactory.isImplicitlyExcluded` always filters beans that implement `BeanRegistrationAotProcessor`. For Spring Boot, we think we'll need to have bean that implements `BeanRegistrationAotProcessor` but isn't filtered.

### コメント

#### コメント 1 by philwebb

**作成日**: 2022-05-27

I think we can use `BeanRegistrationExcludeFilter` as a signal for this. Any AOT processor bean that doesn't implement `BeanRegistrationExcludeFilter` can be implicitly filtered. If it does implement `BeanRegistrationExcludeFilter` then we consider that a signal that it is handling its own filtering.

#### コメント 2 by philwebb

**作成日**: 2022-06-09

Reopening because it's not particularly obvious that `BeanRegistrationExcludeFilter` is being implemented just to exclude the processor. Perhaps a default method on `AotProcessor` might be better.

#### コメント 3 by snicoll

**作成日**: 2022-07-13

@philwebb I am assuming this one won't make it the release tomorrow.

#### コメント 4 by philwebb

**作成日**: 2022-07-18

Sorry @snicoll, I didn't get to refine it. The original fix is in M5 so I'll move it back and open a new issue 

---

## Issue #28528: Proxy hint missing when `AliasFor` is used on the annotation itself

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-05-26

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28528

**関連リンク**:
- Commits:
  - [718ef42](https://github.com/spring-projects/spring-framework/commit/718ef42d68acbdc9f62799d2e3762bd4d4361a04)
  - [86a85f5](https://github.com/spring-projects/spring-framework/commit/86a85f558c7c319c6dbb651807dce7ebbe2e1f3e)

### 内容

`RuntimeHintsUtils#registerAnnotation` will not register a proxy hint for an annotation using `@AliasFor` against a local attribute. This leads to issues in a native environment:

```
Caused by: com.oracle.svm.core.jdk.UnsupportedFeatureError: Proxy class defined by interfaces [interface org.springframework.web.bind.annotation.RequestMapping, interface org.springframework.core.annotation.SynthesizedAnnotation] not found. Generating proxy classes at runtime is not supported. Proxy classes need to be defined at image build time by specifying the list of interfaces that they implement. To define proxy classes use -H:DynamicProxyConfigurationFiles=<comma-separated-config-files> and -H:DynamicProxyConfigurationResources=<comma-separated-config-resources> options.
```

---

## Issue #28533: Improve options for exception handling in HTTP interface client 

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-05-27

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28533

**関連リンク**:
- Commits:
  - [a04e805](https://github.com/spring-projects/spring-framework/commit/a04e805d2709122e2bb43a35f71d6c4d1f04ab41)
  - [24c4614](https://github.com/spring-projects/spring-framework/commit/24c46142c63ff0375e83374766903ac87c86d85d)

### 内容

There is no good way to handle exceptions from a single place. 

An application may want to turn `WebClientException` into another exception, or handle a specific exception. `WebClient` provides status handlers, but those are configured per request, and not exposed through the builder.

---

## Issue #28552: Deprecate trailing slash match and change default value from true to false

**状態**: closed | **作成者**: vpavic | **作成日**: 2022-06-01

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28552

**関連リンク**:
- Commits:
  - [d96b4a0](https://github.com/spring-projects/spring-framework/commit/d96b4a046342a5d886eeb967c05f8b7f95b6dfb1)
  - [4bff95a](https://github.com/spring-projects/spring-framework/commit/4bff95a18017b7a9f603315c606e8f31e74bd658)
  - [0098f29](https://github.com/spring-projects/spring-framework/commit/0098f2931adaa919ddfe66eda2ef620036e7044a)
  - [b312eca](https://github.com/spring-projects/spring-framework/commit/b312eca39177cf9bd588c52c3b56ca42b4f75271)
  - [a81ba68](https://github.com/spring-projects/spring-framework/commit/a81ba68da19efc6f09fe70497f4cf5d4d6c3b190)
  - [93b343f](https://github.com/spring-projects/spring-framework/commit/93b343fbd605d05e3b209bd69f011022eccf72ec)

### 内容

> Whether to match to URLs irrespective of the presence of a trailing slash. If enabled a method mapped to `"/users"` also matches to `"/users/"`.
> The default value is `true`.

Even though this behavior has been long present in Spring, it introduces ambiguity that can (combined with some other choices) easily have consequences in shape of security vulnerabilities. Consider this example:

```java
@SpringBootApplication
@RestController
public class SampleApplication {

    public static void main(String[] args) {
        SpringApplication.run(SampleApplication.class, args);
    }

    @GetMapping("/resources")
    String resources() {
        return "Hello from /resources";
    }

    @GetMapping("/resources/{id}")
    String resourceById(@PathVariable Long id) {
        return "Hello from /resources/" + id;
    }

    @Bean
    SecurityFilterChain filterChain(HttpSecurity httpSecurity) throws Exception {
        return httpSecurity
                .authorizeHttpRequests(requests -> {
                    requests.antMatchers("/resources").hasRole("admin");
                    requests.antMatchers("/resources/**").hasRole("user");
                    requests.anyRequest().denyAll();
                })
                .httpBasic(Customizer.withDefaults())
                .build();
    }

}
```

```properties
spring.security.user.password=password
spring.security.user.roles=user
```

Default user (with role `user`) will get `403` attempting to `GET /resources` but can avoid protection by issuing `GET /resources/`, which wouldn't be possible with trailing slash matching disabled.

Let me note that I'm aware that using `mvcMatchers` instead of `antMatchers` would have prevented this issue but that doesn't change the fact that there are many configurations out there relying on `antMatchers` and that sometimes `antMatchers` are simply more suitable for other reasons.

Also, I personally see little real benefit of having trailing slash matching enabled because:
- if application renders server-side generated views navigation is either way established using hyperlinks
- if application exposes APIs then even more so it is expected that requests are aligned with the API docs

For places where it's really needed for application to respond to both requests, I'd argue that it's either way better solution to configure redirects instead of application wide ambiguous request mappings.

Please consider making this change for `6.0`.

### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-06-08

I think most users would would expect that a trailing slash doesn't make a difference. From that perspective, the default is not unreasonable, and more than just HATEOAS style navigation or API guidance, even just manually typing a URL somewhere.

If we change the default, many would look to change it back, so overall it's hard to avoid the need to align Spring Security with with Spring MVC through `mvcMatchers`. One could argue that it's a safer default but this applies only when used with Spring Security. It's not unsafe by itself. 

For configuring redirects, do you mean externally, like in a proxy? That would solve the problem at a different level, before Spring Security and Spring MVC, so I would be more interested in that direction but we can only make it a recommendation, and we can still make such a recommendation independent of this.





#### コメント 2 by vpavic

**作成日**: 2022-06-09

> From that perspective, the default is not unreasonable, and more than just HATEOAS style navigation or API guidance, even just manually typing a URL somewhere.

I can see _manually typing a URL_ as a real argument only in case of web apps (not APIs) and even there it's only potentially useful for a few select URLs that are considered to be entry points into the application and are likely to be directly entered by the users.

> One could argue that it's a safer default but this applies only when used with Spring Security. It's not unsafe by itself.

This is the part I strongly disagree with - what Spring Security does is nothing special nor unique. You can end up with the same kind of risks with other Java filter based security frameworks (for example, Apache Shiro) or by applying security (authorization) in an external component that sits in front of your Spring application. After all, on a high level, conceptually these all take the same approach.

> For configuring redirects, do you mean externally, like in a proxy?

Either externally in a proxy or using something like [Tuckey UrlRewriteFilter](https://www.tuckey.org/urlrewrite/) or even simply using `ViewControllerRegistry::addRedirectViewController` to add redirects where needed.

What I would like to see in Spring are the defaults that are not ambiguous and are therefore less prone to abuse. When I see a handler annotated with `@GetMapping("/api/resources")` that it really maps to only what I see, unless I opt into any additional (ambiguous) behavior explicitly. This change together with #23915 would achieve that.

#### コメント 3 by rstoyanchev

**作成日**: 2022-06-10

I'm not necessarily disagreeing. I'm merely making the point that by itself, trailing slash is not unsafe. It's only when combined with a proxy or filter that also interprets URLs, where it becomes a problem, and the problem more generally is that there may be differences, which could go both ways. 

That said, this is also the reason, I've come to see over time that URL paths should be left alone as is as much as possible, avoiding normalization as much as possible. It's the only way for frameworks to minimize differences and align naturally. This is also why `PathPatternParser` was designed to not decode the full path in order to match to mappings, unlike `AntPathMatcher`, doesn't even support suffix patterns, etc.

In any case, the only way to really make a significant difference here I think is to deprecate the trailingSlash option entirely and encourage an alternative solution, like a proxy or filter to redirect. That enforces being more precise about where you want to do that exactly, and it can be done ahead of security decisions. Otherwise the possibility for a mismatch between web and security frameworks remains. It's just too easy to flip the default back and not think about it again.

This is something that we'll discuss as a possibility for 6.0.


#### コメント 4 by vpavic

**作成日**: 2022-06-10

> In any case, the only way to really make a significant difference here I think is to deprecate the trailingSlash option entirely and encourage an alternative solution, like a proxy or filter to redirect.

I like that even better. Thanks for the feedback.

#### コメント 5 by rstoyanchev

**作成日**: 2022-06-21

**Team decision:** we'll go ahead with this. It aligns with various other path matching changes we've made in 5.2 and 5.3 such suffix pattern matching, path segment trimming, and path decoding, to make path matching more transparent and explicit. 

#### コメント 6 by wilkinsona

**作成日**: 2022-06-21

Will the default be changed to false as part of this deprecation?

#### コメント 7 by rstoyanchev

**作成日**: 2022-06-21

Yes, I'm thinking that we might as well and that we'll have to, since otherwise you'd need to set it in order to stop using it. We had the same issue with suffix pattern matching. 

#### コメント 8 by rstoyanchev

**作成日**: 2022-06-29

The trailing slash option is now deprecated and set to `false` in all applicable places. The change applies mainly to annotated controllers, since `SimpleUrlHandlerMapping`, it turns out, was already set to `false` by default. Nevertheless, it's now deprecated throughout and to be removed eventually.

#### コメント 9 by bclozel

**作成日**: 2022-07-01

I've just found this while browing the code @rstoyanchev :

https://github.com/spring-projects/spring-framework/blob/50240bb609b6441390d436005a7f2e7a4cdf5454/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerMapping.java#L85

Should this value be changed as well?

#### コメント 10 by rstoyanchev

**作成日**: 2022-07-01

Looks like it, yes.

#### コメント 11 by MartinHaeusler

**作成日**: 2022-12-02

This little stunt just cost us over 10 man-hours of pure frustration staring at 404 issues. We debugged through the entire security filter chain, the servlet, everything (great fun!) - until we arrived at the path matchers where it became apparent that the difference between the pattern (and its path placeholders) and the provided path was only the trailing slash. This may be apparent in small applications, but we have over 300 endpoint mappings. If the little phrase `404` would have appeared somewhere in the lengthy migration notes, we would have found it.

#### コメント 12 by bclozel

**作成日**: 2022-12-02

@MartinHaeusler I'm sorry you went through this. Maybe we can improve the documentation to avoid the same issue for other developers. Can you share at which documentation you were looking at while working on this?

#### コメント 13 by MartinHaeusler

**作成日**: 2022-12-02

@bclozel we were looking at this:

https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide

But given how big Spring Boot is (with all its modules) it's hard to tell which parts of this document are even relevant for any given application. We spent some time on google looking for "Spring Boot 3 404", but the search results produced nothing specific for the latest version. Up to this point, we were not even **aware** that some clients were sending trailing slashes to our endpoints, it just "happened to work". That's why the section on trailing slashes didn't really catch any attention. Making the migration guide easier to search through (i.e. "if you do not update X, you will receive error Y") would have been great. If there was any mention of "if your application relied on this behavior, you will receive HTTP 404 errors" in the migration guide, we would have found it instantly... No hard feelings. We are now aware of it and can move on.

#### コメント 14 by bclozel

**作成日**: 2022-12-02

@MartinHaeusler I've added a quick mention of "HTTP 404 errors" in [the dedicated section of the Spring Boot migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide#spring-mvc-and-webflux-url-matching-changes), hopefully this will help others. Thanks for bringing this up.

#### コメント 15 by armlesshobo

**作成日**: 2022-12-20

Are there any considerations for trimming trailing slashes by default?

#### コメント 16 by kdebski85

**作成日**: 2022-12-29

@bclozel  Migration guide should also provide a workaround for SpingFlux, not only SpringMVC.
Something like:

```java
@Configuration
class WebConfiguration implements WebFluxConfigurer {

    @Override
    public void configurePathMatching(PathMatchConfigurer configurer) {
        configurer.setUseTrailingSlashMatch(true);
    }
}

#### コメント 17 by philwebb

**作成日**: 2022-12-29

@kdebski85 Thanks for the suggestions, I've updated the wiki.

#### コメント 18 by kdebski85

**作成日**: 2022-12-30

@philwebb I found that the workaround with WebFluxConfigurer does not work when `authorizeExchange` with `pathMatchers` is used.
I created https://github.com/spring-projects/spring-framework/issues/29755 for this issue.

#### コメント 19 by lpandzic

**作成日**: 2023-01-31

This seems pretty problematic to me on a grander scale of things.
Consider that many Spring Boot applications are in fact APIs served to many different customers over which the API developer has very little, if any, control over.
Since this worked before Spring Boot 3 if any of those customers used legacy behavior suddenly application developer is in a impossible situation where he's essentially forced to support this legacy behavior indefinitely. I'm saying indefinitely because I find it highly unlikely anyone will be able to convince all of their customers  to fix it in their code for what seems to be for superficial or puristic reasons.

Now I'm not necessarily against this  change, I just expect Spring Framework teams will get a lot of flak for this because of the situation explained above. It puts developers into an impossible situation which can be hard to detect at first and cause a lot of frustration.

At Infobip I know where to fix this for all our public API's without duplicating this change all over our codebase, but I'm not sure everyone will be that lucky.

#### コメント 20 by dkoding

**作成日**: 2023-02-22

This brilliant move just cost our teams hundreds of man-hours. So thanks for that.

---

## Issue #28555: Introduce RuntimeHints predicates utilities

**状態**: closed | **作成者**: bclozel | **作成日**: 2022-06-02

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28555

**関連リンク**:
- Commits:
  - [7f7f458](https://github.com/spring-projects/spring-framework/commit/7f7f458a5977ad51f6ba7cfbb3440e33b754d60b)
  - [15b69a3](https://github.com/spring-projects/spring-framework/commit/15b69a3edec7a7f1dc166e3f07fa4b1cb54b0df9)
  - [9c9b235](https://github.com/spring-projects/spring-framework/commit/9c9b2356cec4a74c685320c5b8b1b6eb283f9dc0)

### 内容

The new `RuntimeHints` API allows to describe hints for the reflection/proxies/resources needs at runtime.
The problem is, a single invocation at runtime can be covered by multiple, different hints.

For example, reflection introspection on the `myMethod` method for the class `MyClass` can be covered by any of:

* `MemberCategory.INTROSPECT_PUBLIC_METHODS` if `myMethod` is public
* `MemberCategory.INVOKE_PUBLIC_METHODS` if `myMethod` is public
* `MemberCategory.INTROSPECT_DECLARED_METHODS` in all cases
* `MemberCategory.INVOKE_DECLARED_METHODS` in all cases
* a specific introspection or invokation reflection entry for `MyClass::myMethod`

Because of the knowledge required for checking if registered hints are enough for a particular use case, we should introduce `Predicate<RuntimeHints>` static utilities to be used in tests and in #27981 

---

## Issue #28556: Simplify SourceFileAssert assertion methods

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-03

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28556

**関連リンク**:
- Commits:
  - [74caa92](https://github.com/spring-projects/spring-framework/commit/74caa9213a44e2b613025b2387d41389c9344953)

### 内容

The `SourceFileAssert` class offers a lot of assertions that we ended up not using. We should remove them before the module is made public. This will also help keep qdox as an implementation detail that we could possibly remove later.

---

## Issue #28557: Allow BeanRegistrationAotContributions to provide BeanRegistrationCodeFragments customization

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-03

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28557

**関連リンク**:
- Commits:
  - [8d79ec0](https://github.com/spring-projects/spring-framework/commit/8d79ec0b67972f3bcd253b046c18fe22bc13d33a)
  - [305055d](https://github.com/spring-projects/spring-framework/commit/305055d6b1a42c7795891b7b389936ed80270505)

### 内容

Currently only `BeanRegistrationCodeFragmentsCustomizer` can be used to customize `BeanRegistrationCodeFragments` but for parent/child context support we'd like to be able to apply customization directly from a `BeanRegistrationAotContribution`.

Making such a change should also allow us to from the `BeanRegistrationCodeFragmentsCustomizer` entirely since the same functionality could be achieved using the existing `BeanRegistrationAotProcessor` interface.

---

## Issue #28558: Publish spring-core-test module

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-03

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28558

**関連リンク**:
- Commits:
  - [3ebdaea](https://github.com/spring-projects/spring-framework/commit/3ebdaeabd3b40bdfe197b4b2ee3f514906ac936e)

### 内容

Spring Boot now need to use the TestCompiler class so we should publish the module.

---

## Issue #28561: ScopedProxyBeanRegistrationAotProcessor is never called

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-03

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28561

**関連リンク**:
- Commits:
  - [3aefa88](https://github.com/spring-projects/spring-framework/commit/3aefa88d3cb2f957f73a8fedd287f0f90c97df8e)
  - [176ea5e](https://github.com/spring-projects/spring-framework/commit/176ea5e9a7a04a81d76130c795d7597f0fc1de75)

### 内容

The entry in `aot.factories` is pointing to a non existing factory class. This means that the processor is never called and scoped proxy handling does not work.

---

## Issue #28562: Stop initializing DataSize at build time for GraalVM

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-06-03

**ラベル**: type: task, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28562

**関連リンク**:
- Commits:
  - [92f8ab7](https://github.com/spring-projects/spring-framework/commit/92f8ab774f6616a2c47b91ec74a95f96c596b954)

### 内容

## Overview

In light of #28560, we can now revert the change made in #28328.

## Related Issues

- #28560
- #28328
- https://github.com/oracle/graal/issues/4489


---

## Issue #28563: Use a single `--initialize-at-build-time` parameter per file

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-03

**ラベル**: type: task, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28563

**関連リンク**:
- Commits:
  - [74c49c5](https://github.com/spring-projects/spring-framework/commit/74c49c510a3e9bd8a7ec193e5ad33c3b75afbef3)

### 内容

`native-image.properties` supports specifying a single `--initialize-at-build-time` parameter with multiple packages separated with `,`. This issue intend to use this capability since:
 - This is usually the recommended way to specify multiple packages.
 - This is consistent with the generated configuration.
 - It allows to group per module `--initialize-at-build-time` when passed to the `native-image` command.

---

## Issue #28565: Allow ApplicationContextAotGenerator to generated better class names

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-04

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28565

**関連リンク**:
- Commits:
  - [172102d](https://github.com/spring-projects/spring-framework/commit/172102d225c916e2ca24b87aa0f0a74d824815b2)
  - [4bd33cb](https://github.com/spring-projects/spring-framework/commit/4bd33cb6e0659df2cd0b9fa04feea8fd77e5a16d)

### 内容

Currently `ApplicationContextAotGenerator` always generates a `__.BeanFactoryRegistrations` class. For context hierarchy support we're going to need multiple registration classes so we should use different names. We'd also like to be able to provide a target class so that we can use a package other than `__`.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-06-07

The default classname is still generated in that `__` package. Is that expected? I was under the impression that this issue would move it at the same level as the application class itself.

#### コメント 2 by philwebb

**作成日**: 2022-06-07

We'll need to make some updates on the Boot side to pass the target in.

---

## Issue #28567: Introduce attribute support in Kotlin RouterFunction DSL

**状態**: closed | **作成者**: christophejan | **作成日**: 2022-06-05

**ラベル**: in: web, type: enhancement, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28567

**関連リンク**:
- Commits:
  - [cc17178](https://github.com/spring-projects/spring-framework/commit/cc1717871f4475459cebc1f39d5167a7af43abb5)
  - [bbabf8d](https://github.com/spring-projects/spring-framework/commit/bbabf8d855cc8d48757bdc86f2f2c426a7438f0a)
  - [283bc9e](https://github.com/spring-projects/spring-framework/commit/283bc9ede936bd41b68ad2ee7fe00047d5550b93)

### 内容

On current spring framework version (5.3.19), RouterFunction **attributes** are **not supported** by RouterFunction Kotlin **DSL**.
<br />

RouterFunction attributes is currently supported by Java Builder :
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webflux/src/main/java/org/springframework/web/reactive/function/server/RouterFunctionBuilder.java#L335
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webflux/src/main/java/org/springframework/web/reactive/function/server/RouterFunctionBuilder.java#L350
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webmvc/src/main/java/org/springframework/web/servlet/function/RouterFunctionBuilder.java#L328
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webmvc/src/main/java/org/springframework/web/servlet/function/RouterFunctionBuilder.java#L343
<br />

But RouterFunction attributes support is missing from all Kotlin DSL :
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webflux/src/main/kotlin/org/springframework/web/reactive/function/server/RouterFunctionDsl.kt#L65
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webflux/src/main/kotlin/org/springframework/web/reactive/function/server/CoRouterFunctionDsl.kt#L66
- https://github.com/spring-projects/spring-framework/blob/172102d225c916e2ca24b87aa0f0a74d824815b2/spring-webmvc/src/main/kotlin/org/springframework/web/servlet/function/RouterFunctionDsl.kt#L62


---

## Issue #28570: BeanDefinitionPropertiesCodeGenerator should filter single inferred init/destroy method

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-05

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28570

**関連リンク**:
- Commits:
  - [9a9c3ea](https://github.com/spring-projects/spring-framework/commit/9a9c3ea00e2a955c06452d1e28d092594cca53a8)

### 内容

`BeanDefinitionPropertiesCodeGenerator` currently generates `setInitMethodNames()/setDestroyMethodNames()` methods with not parameters if only a single `AbstractBeanDefinition.INFER_METHOD` method is specified. Although this is harmless, it doesn't look great so we should just not add the statement.

---

## Issue #28574: CompileWithTargetClassAccessClassLoader does not implement findResource

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-06

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28574

**関連リンク**:
- Commits:
  - [26944f3](https://github.com/spring-projects/spring-framework/commit/26944f3c8ef2f1d5e2a45ab0081556382e90e960)

### 内容

The `CompileWithTargetClassAccessClassLoader` implements `findResources` but missed `findResource`.

---

## Issue #28578: BeanRegistrationCodeFragments sets a non-nullable field to null

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-07

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28578

**関連リンク**:
- Commits:
  - [c01a2e8](https://github.com/spring-projects/spring-framework/commit/c01a2e897d410efbcbaef36ffd0f56208e276970)

### 内容

There is a strange arrangement in `BeanRegistrationCodeFragments` where a package private constructor sets a non-null field to `null`. Making the field nullable doesn't help as it's used in all methods implemented by that class. 

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-06-07

cc @philwebb 

---

## Issue #28580: Allow @CompileWithTargetClassAccess to work with all classes

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-07

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28580

**関連リンク**:
- Commits:
  - [46a2f2d](https://github.com/spring-projects/spring-framework/commit/46a2f2d71ce0c1687f289c01746e808f61b140d5)
  - [7119d42](https://github.com/spring-projects/spring-framework/commit/7119d420cece91ca810ce917ac9ade6853169fde)

### 内容

Currently `@CompileWithTargetClassAccess` works by using `MethodHandles.privateLookupIn` and having target classes listed on the annotation. This is quite error prone and makes it impossible to have target access if the there isn't a class in the same package available.

We can probably get away with a reflection approach instead which will simplify a lot of tests.

---

## Issue #28582: Add support for annotation processors with TestCompiler

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-06-07

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28582

**関連リンク**:
- Commits:
  - [45ef21f](https://github.com/spring-projects/spring-framework/commit/45ef21f900baa4dcad269100553818d4839b8cfb)

### 内容

See https://github.com/spring-projects/spring-boot/issues/31266 for background.


---

## Issue #28585: Rationalize naming strategy in ApplicationContextAotGenerator

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-08

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28585

**関連リンク**:
- Commits:
  - [fe39598](https://github.com/spring-projects/spring-framework/commit/fe39598e81e01710f709b001342b62606422fb5b)
  - [6199835](https://github.com/spring-projects/spring-framework/commit/6199835d6ea791a7f74a8e98f1a2a08c17014aef)
  - [88428ed](https://github.com/spring-projects/spring-framework/commit/88428edb3dd47891adc962d1efbfd44b223f6b98)

### 内容

`ApplicationContextAotGenerator` uses a `GenerationContext` to analyze an `ApplicationContext`. The generation context provides the necessary infrastructure to generate "files" (i.e. source code and resources). It's part of `spring-core`.

As part of this analysis, an `ApplicationContextInitializer` is generated and serves as the entry point for running an optimized version of the specified `ApplicationContext` at runtime. Additional files may be generated and needs extra help in terms of naming conventions.

The current API has a `ClassName` for the `ApplicationContextInitializer` as well as a target `Class` and a `name` for naming conventions purposes. I think that, at the very least, we should gather these in some sort of naming conventions strategy. Because we need to get a reference to the initializer classname, we could return something rather than `void`.

There is the use case that `ApplicationContextGenerator` is called for dedicated contexts (such as the management context in Spring Boot). In this case we want to pass along the `GenerationContext` so that it records all resources/files in a single place and an updated naming strategy.



### コメント

#### コメント 1 by snicoll

**作成日**: 2022-06-09

Another example is the `getAotProcessor` on `AotProcessor` that's used by the [management context stuff](https://github.com/spring-projects/spring-boot/blob/c56783064de907283e8f4c6fd04e4489682f9a9b/spring-boot-project/spring-boot-actuator-autoconfigure/src/main/java/org/springframework/boot/actuate/autoconfigure/web/server/ChildManagementContextInitializer.java#L99) in Spring Boot to only get the target application.

#### コメント 2 by snicoll

**作成日**: 2022-06-17

We've discussed passing the `target/name` pair as constructor arguments of `ApplicationContextGenerator`. I don't think that works as we'd still need to get those values somehow and that would leave what we have in `AotProcessor`.

https://github.com/snicoll/spring-framework/commit/88428edb3dd47891adc962d1efbfd44b223f6b98 is an attempt at making the naming strategy a separate, third argument. In short `BeanFactoryNamingConvention` hides the `target/name` pair and offer a way to generate class names for the bean factory at hand. The default implementation delegates to `ClassNameGenerator` (although the contract does not specify it strictly, which is a problem as it is a stateful thing).

Experimenting with this reveals several interesting things:

* Tests don't really care what the name of the entry point is as they rely on the fact that the first thing (initializer) that registers a class is the entry point.
* Returning the initializer class name rather than passing it works really well (and the implementation is in control over the name like all the other ones)
* That `Class<?> target` and `String name` can be abstracted behind a strategy interface except for [one use case](https://github.com/snicoll/spring-framework/blob/88428edb3dd47891adc962d1efbfd44b223f6b98/spring-beans/src/main/java/org/springframework/beans/factory/aot/BeanRegistrationsAotContribution.java#L68-L69). The naming strategy returning the bean factory name is a little odd as a result.

This works relatively nicely up to a point where we need to process another context as part of processing the context of the application. When this happens, the only reliable callback we have is `GenerationContext`. We don't have the third argument anymore (the naming convention) so we're stuffed.

`GenerationContext` already has `ClassNameGenerator`. We could update `GeneratingContext` to provide a higher level class that encapsulates this + the naming convention for the bean factory. If we do that, we need to be able to change the naming convention when processing a child context, and yet keeping the current created objects so that clashes are identified properly.

Spring Native had a `fork` option on the context where the naming convention can be changed. I never really liked the name but everything seems to point in the direction of some sort of feature like that.

#### コメント 3 by snicoll

**作成日**: 2022-06-20

I also believe that tightening this will help us remove the AOT package name (`__`) altogether. #28585 is related.

#### コメント 4 by snicoll

**作成日**: 2022-06-21

Another thing to note is that the "name" uniqueness is not enforced upfront. If you try to generate multiple contexts with the name `Test`, you'd end up with `__TestBeanDefinitions` and `TestBeanDefinitions1` rather than `__TestBeanDefinitions` and `Test1BeanDefinitions` .

This goes in the direction again of the  context being in charge of the registered names and their uniqueness. Unfortunately `GenerationContext` is in `spring-core` and does not know anything about the bean factory.

#### コメント 5 by snicoll

**作成日**: 2022-06-21

Yet another thing. If we process multiple contexts against the same bean, and that bean requires autowiring, then we invoke multiple times `AutowiredAnnotationBeanPostProcessor` which leads to the same file being created multiple times with the same name.

The original design had the idea of registering that a processor already ran. Right now, it's not obvious to me what is "static" and what is bean factory specific (and therefore should be qualified).

---

## Issue #28588: JdkHttpClientResourceFactory has dependency  on org.eclipse.jetty

**状態**: closed | **作成者**: j3graham | **作成日**: 2022-06-08

**ラベル**: in: web, type: bug

**URL**: https://github.com/spring-projects/spring-framework/issues/28588

**関連リンク**:
- Commits:
  - [1881e48](https://github.com/spring-projects/spring-framework/commit/1881e48bb4f5643a0dbdfa6f24a5e0fb055274f6)

### 内容

in spring-web, `org.springframework.http.client.reactive.JdkHttpClientResourceFactory` makes use of the jetty LifeCycle class.

It would be good to be able to use JdkHttpClientResourceFactory with no extra dependencies.

This is in v 6.0

### コメント

#### コメント 1 by poutsma

**作成日**: 2022-06-13

@rstoyanchev was the usage of Jetty's `LifeCycle` type in `JdkHttpClientResourceFactory` intentional? I think it can be replaced with a check for `ExecutorService` in `destroy()`, and call `ExecutorService::shutdown` if so.

#### コメント 2 by rstoyanchev

**作成日**: 2022-06-13

No, it's most certainly an oversight.

---

## Issue #28594: Support that the same RuntimeHintsRegistrar can be specified multiple times and invoked only once

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-09

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28594

**関連リンク**:
- Commits:
  - [3637228](https://github.com/spring-projects/spring-framework/commit/363722893b2dcb65a29eac01007bd45ac0b3563c)

### 内容

Given the conditional nature of `@ImportRutimeHints`, we should make sure that several classes can defined it with the same processor and that doesn't mean it is invoked multiple times.

The javadoc should be updated accordingly?

---

## Issue #28597: Fix `ResourceHintsWriter` for leading/trailing wildcards

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-09

**ラベル**: type: bug

**URL**: https://github.com/spring-projects/spring-framework/issues/28597

**関連リンク**:
- Commits:
  - [1734deb](https://github.com/spring-projects/spring-framework/commit/1734debca1fae01f9a9851b9ac93d5a166c8f63a)
  - [99ffd97](https://github.com/spring-projects/spring-framework/commit/99ffd97a72ec6a85d8606bdc069e8073a4792642)
  - [26ea978](https://github.com/spring-projects/spring-framework/commit/26ea97843bf95f41366851572ffff3e8b893410c)

### 内容

While working on spring-projects/spring-boot#31278 with @snicoll we found that specifying `static/*` resource pattern was not working as expected for example.

---

## Issue #28598: Improve `ResourcePatternHint` documentation

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-09

**ラベル**: type: documentation

**URL**: https://github.com/spring-projects/spring-framework/issues/28598

**関連リンク**:
- Commits:
  - [5dfc79f](https://github.com/spring-projects/spring-framework/commit/5dfc79fc6e5a00184e9430d57174fb7cc1c7e3fb)
  - [b9f8562](https://github.com/spring-projects/spring-framework/commit/b9f85627a17a55270d5ba3d3b6e7b7d267ba8817)
  - [7302e6d](https://github.com/spring-projects/spring-framework/commit/7302e6d54b55de2e0be77040e3e03ca53a7c9a01)

### 内容

Also add a link to this documentation to the various usages Javadoc.

---

## Issue #28600: Remove obsolete references to @Required

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-06-09

**ラベル**: type: documentation

**URL**: https://github.com/spring-projects/spring-framework/issues/28600

**関連リンク**:
- Commits:
  - [74d1be9](https://github.com/spring-projects/spring-framework/commit/74d1be9bd83eb5a3a1b1362e75b0fae511356375)

### 内容

`@Required` was removed in a previous 6.0 milestone.

---

## Issue #28606: Reflection configuration for parameter types with an inner class have wrong name

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-10

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28606

**関連リンク**:
- Commits:
  - [100ce96](https://github.com/spring-projects/spring-framework/commit/100ce9642afb14b806e42ae9277f77171a7bc04c)

### 内容

_本文なし_

---

## Issue #28607: Use PathPatternParser by default in Spring MVC

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-06-10

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28607

**関連リンク**:
- Commits:
  - [8a9b082](https://github.com/spring-projects/spring-framework/commit/8a9b082d8a0f84e7b72416e57e9b6a7a9321567e)
  - [92cf1e1](https://github.com/spring-projects/spring-framework/commit/92cf1e13e8770aae306886555ed8210d95464d46)
  - [14fd260](https://github.com/spring-projects/spring-framework/commit/14fd2605a39462f7ae3d0377aac249a171908a91)

### 内容

`PathPatternParser` was introduced for WebFlux in 5.0 as a replacement for `AntPathMatcher` that uses pre-compiled patterns, supports mapping without decoding the full URL path, and optimizes the pattern syntax for web (vs file system) paths. 

It has been available for use in Spring MVC since version 5.3 and has been enabled as the default in Spring Boot since version 2.6 with https://github.com/spring-projects/spring-boot/issues/24805.

This issue is to consider switching the default in Spring Framework to `PathPatternParser` for 6.0, and potentially deprecate `PathMatcher` and related options.




### コメント

#### コメント 1 by bclozel

**作成日**: 2022-06-21

I think we should do this (including the deprecation) for 6.0.

#### コメント 2 by rstoyanchev

**作成日**: 2022-06-21

**Team decision:** we'll go ahead with it and align with the default in Boot. 

#### コメント 3 by rstoyanchev

**作成日**: 2022-06-29

Parsed patterns are now enabled by default in Spring MVC. This means, each `HandlerMapping`, or rather every subclass of `AbstractHandlerMapping` has a `PathPatternParser` instance, and that effectively means parsed patterns are used instead of String path matching with `AntPathMatcher`. 

To minimize unnecessary breakage where intentions are clear, String path matching is still enabled through the MVC config, when either of the following is true:
- `PathPatternParser` is not explicitly set, while `AntPathMatcher` or `UrlPathHelper` related options are customized.
- `PathPatternParser` is explicitly set to `null`.

Further steps have also been taken to minimize failures in existing tests. For example the URL path is parsed per handler lookup if not called by the `DispacherServlet`, which pre-parses and caches the path. Likewise, `MockHttpServletRequest` detects a Servlet path mapping, to ensure a Servlet path prefix is taken into account.




---

## Issue #28614: Register native hints for jakarta.inject annotations

**状態**: closed | **作成者**: bclozel | **作成日**: 2022-06-13

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28614

**関連リンク**:
- Commits:
  - [bb952cb](https://github.com/spring-projects/spring-framework/commit/bb952cb95e37404b3f5b0eb8d7a659a3eeeddab0)
  - [7e8b1ed](https://github.com/spring-projects/spring-framework/commit/7e8b1ed40181ca224a62b8bed8c3e1911c66f9ad)

### 内容

As of #28442, core Spring annotations are registered for native hints, including `@Order` and `@AliasFor`.

Spring optionally supports `jakarta.inject.Inject` and `jakarta.inject.Qualifier`, detecting their presence on the classpath. We should ensure that similar hints are registered if they are present on the classpath during the AOT phase.

---

## Issue #28617: Add ifPresent utility methods on RuntimeHints

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28617

**関連リンク**:
- Commits:
  - [d6d4b98](https://github.com/spring-projects/spring-framework/commit/d6d4b98780132fff58ba610d2cde53419d32ce4a)

### 内容

Based on concrete usage of the API, it looks like a `registerIfPresent` would be a nice addition to the API. This makes sure hints aren't contributed for things that aren't available.

---

## Issue #28618: Remove support for cyclic annotation parameter types in Kotlin

**状態**: closed | **作成者**: poutsma | **作成日**: 2022-06-14

**ラベル**: type: task, in: core, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28618

**関連リンク**:
- Commits:
  - [6a7a0bd](https://github.com/spring-projects/spring-framework/commit/6a7a0bddb749cbc8d716d4aee3d10ff88e4793eb)

### 内容

#28012 introduced support for cyclic annotation parameter types in Kotlin. However, in Kotlin 1.7 the compiler gives a warning for these cyclic parameters, which will turn into an error in Kotlin 1.9. See [KT-47932](https://youtrack.jetbrains.com/issue/KT-47932).

We could theoretically keep supporting cyclic annotation parameters, but by this point it is clear that this feature was never intended to be there. So removal seems better.

Effectively, this would mean reverting https://github.com/spring-projects/spring-framework/commit/3ec612aaf8611d2ad6e6f7f3d5868feee5024477 and https://github.com/spring-projects/spring-framework/commit/3188c0f7db54cffdb95e7127e2adde959dd078f9.

### コメント

#### コメント 1 by poutsma

**作成日**: 2022-06-14

Resolved in https://github.com/spring-projects/spring-framework/commit/bf9f261b9512a3d0f84844dfa75943a231ed5a87

---

## Issue #28619: Upgrade to Kotlin 1.7.0

**状態**: closed | **作成者**: poutsma | **作成日**: 2022-06-14

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/28619

**関連リンク**:
- Commits:
  - [4658b3f](https://github.com/spring-projects/spring-framework/commit/4658b3fdb909b33ea39ca7f3beb830ecad2387f9)

### 内容

This will means dropping (support for) cyclic annotation type parameters, see #28618.

---

## Issue #28620: Introduce ResourcePatternHint#toRegex

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28620

**関連リンク**:
- Commits:
  - [c235ad0](https://github.com/spring-projects/spring-framework/commit/c235ad0b35c1df24eb2da8df31566e839cfd19c3)
  - [0c01238](https://github.com/spring-projects/spring-framework/commit/0c0123823dcffc7d74eae931c38be84bad375a5d)
  - [532bca2](https://github.com/spring-projects/spring-framework/commit/532bca2968c46a0f495f2f0fb6dcecd8f40c10b8)
  - [7f7f458](https://github.com/spring-projects/spring-framework/commit/7f7f458a5977ad51f6ba7cfbb3440e33b754d60b)

### 内容

This change is done for several reasons:
 - Move the logic where it is documented.
 - Test it with `ResourcePatternHintTests`.
 - Allow `RuntimeHintsPredicates` to leverage this logic.

---

## Issue #28622: Add reflection hints for `HttpEntity` used in Web controllers

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28622

**関連リンク**:
- Commits:
  - [be28563](https://github.com/spring-projects/spring-framework/commit/be28563621c7a1783f53633b4848fcfc4da0aea9)
  - [93b340e](https://github.com/spring-projects/spring-framework/commit/93b340e5633d623e0899dd296bda7ce86ce02b20)

### 内容

Follow-up of #28518.

---

## Issue #28623: Add reflection hints for data binding in Web controllers

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28623

**関連リンク**:
- Commits:
  - [9d42779](https://github.com/spring-projects/spring-framework/commit/9d42779826b84fc5e4060c3b14287c33eef72835)
  - [13888f3](https://github.com/spring-projects/spring-framework/commit/13888f38d0f3b44354e8dad4283c78bf0a43c281)

### 内容

Follow-up of #28518.

---

## Issue #28624: Replace build-time initialization by constant field evaluation at build-time

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28624

**関連リンク**:
- Commits:
  - [b9acbf3](https://github.com/spring-projects/spring-framework/commit/b9acbf3bebb977cd7e213e9621820edf8c6c62a1)
  - [b589294](https://github.com/spring-projects/spring-framework/commit/b5892940df9fe0d1ce269f7dc093e49938736bf8)
  - [3f65686](https://github.com/spring-projects/spring-framework/commit/3f65686aaa2d1087900cb5f38c1aee0fe5b01879)
  - [48d634a](https://github.com/spring-projects/spring-framework/commit/48d634ae4e78e1a7788acb5118991eba06587fb5)

### 内容

In order to compile to native images and to provide a reasonable footprint, we are currently forced to initialize classes containing `ClassUtils#isPresent` checks at build time. A meaningful concrete example of that requirement is provided by Spring MVC support that does not compile unless a few classes are initialized at build time, see 2b76a12b86a62cc46886e1b7f0e52ea9d256f899.

The drawback is that this build time init of `WebMvcConfigurationSupport` and `RestTemplate` forces to initialize transitively all classes used in static fields/blocks at build time as well : `ClassUtils`, `SpringProperties`, `ConcurrentReferenceHashMap`. Worse : for other classes with similar pattern, if they contain a static loggers, this will force to initialize Logback at build time which is a dead end in term of compatibility as shown multiple times in Spring Native.

We are working on a middle-long term solution with GraalVM to replace build time init by another mechanism, less viral, with less compatibility issues. But for time being, we need to find a solution to this issue.

A pragmatic solution would be isolate classpath checks in a per module (`spring-core`, `spring-web`) class that would be itself init at build time but with no other purpose, removing the risk of viral expension of the classes init at build time. If we take the `WebMvcConfigurationSupport` use case, we would have something like:

```java
public abstract class ClasspathUtils {

    private static final boolean romePresent;
    private static final boolean jaxb2Present;
    private static final boolean jackson2Present;

    static {
        // ...
    }

    public static boolean isRomePresent() { ... }
    public static boolean isJaxb2Present() { ... }
    public static boolean isJackson2Present() { ... }
    // ...
}
```
Bonus point, I think I like the fact that we provide reusable methods for classpath checks without arbitrary `String` parameter.
Implementation would potentially even not use `ClassUtils` to limit the classes init at build time (not sure what is would use instead, to be discussed, not a blocking point).

Any thoughts @jhoeller @snicoll @bclozel?

### コメント

#### コメント 1 by philwebb

**作成日**: 2022-06-14

Perhaps the `@Constant` annotation from this branch that we discussed in the past might help? https://github.com/philwebb/scratch-graal-conditions/tree/annotations

#### コメント 2 by sdeleuze

**作成日**: 2022-06-21

@philwebb Could you please confirm that [this build time initialization of classes](https://github.com/philwebb/scratch-graal-conditions/blob/annotations/src/main/java/gce/graalvm/ConstantFeature.java#L48) is just required for class level `@Constant` not for field level ones?

#### コメント 3 by philwebb

**作成日**: 2022-06-21

@sdeleuze correct, that's just for class-level use.

#### コメント 4 by sdeleuze

**作成日**: 2022-06-22

Good news, I have been able to leverage the updated `@Constant` experiment to remove totally build time initialization from Spring Framework 6 (can be used for portfolio projects and Boot as well) while keeping the same benefits in term of build time code removal, see [this related WIP branch](https://github.com/sdeleuze/spring-framework/tree/gh-28624). Thanks a lot @philwebb!

As soon as GraalVM team provides a builtin solution via the working group @bclozel and I have joined, it would replace this GraalVM feature. That's why I have preferred not introducing a new annotation like `@Constant` but just target a set of patterns. Since we don't have a real idea of the timeframe, I think the GraalVM feature provide a reasonable path for this transition period.

#### コメント 5 by sdeleuze

**作成日**: 2022-06-24

https://github.com/sdeleuze/build-time-constant-fields allows to test it works as expected. Not sure yet if/how we should integrate that in the CI, but probably good enough for this milestone to have such side repository to test the behavior.

Logs printed during the native build allow to identify which fields are set to a constant value at build time.

---

## Issue #28625: Set Kotlin language version to 1.7

**状態**: closed | **作成者**: poutsma | **作成日**: 2022-06-14

**ラベル**: type: task, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28625

**関連リンク**:
- Commits:
  - [070af5c](https://github.com/spring-projects/spring-framework/commit/070af5ceb4d410f69b0755abfb639092c4434c93)

### 内容

We should change the Kotlin language version to 1.7, see [here](https://github.com/spring-projects/spring-framework/blob/933965b7b4b608b7fb6214d25e5c71bbe674cecb/build.gradle#L280-L281). Doing this allows us to upgrade to Kotlin 1.9 within the 6.0.x timeline.

---

## Issue #28626: Add ResourceHints registrar for classpath patterns

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28626

**関連リンク**:
- Commits:
  - [ff9535e](https://github.com/spring-projects/spring-framework/commit/ff9535ef15de35217472acd3acd3a62b9ae27a7e)

### 内容

Having to scan locations is quite common. Rather than implementing that logic multiple times, this issue is about offering a basic implementation that can be customized with file names, locations, and file extensions.

---

## Issue #28635: Add Kotlinx Serialization support to BindingReflectionHintsRegistrar

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-15

**ラベル**: type: enhancement, theme: aot, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28635

**関連リンク**:
- Commits:
  - [4e3393d](https://github.com/spring-projects/spring-framework/commit/4e3393d7ff1d24f20c563386814a4f0d7160b601)
  - [c5cf7c0](https://github.com/spring-projects/spring-framework/commit/c5cf7c0ab034e5921b2717f3a06c9028a6b1420e)
  - [2b1f61a](https://github.com/spring-projects/spring-framework/commit/2b1f61a587ed6640f62206e42bc04583f45c3ec7)
  - [16d6dc3](https://github.com/spring-projects/spring-framework/commit/16d6dc36112ae1b0500a31c0848a06fb208d1237)

### 内容

_本文なし_

---

## Issue #28641: Upgrade Dokka to 1.7

**状態**: closed | **作成者**: poutsma | **作成日**: 2022-06-16

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/28641

**関連リンク**:
- Commits:
  - [dc4ae55](https://github.com/spring-projects/spring-framework/commit/dc4ae559c5d8df01f2b7388db827e330b361ffc7)

### 内容

_本文なし_

---

## Issue #28655: Add automatic hint for autowired field support

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-19

**ラベル**: type: regression, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28655

**関連リンク**:
- Commits:
  - [3654813](https://github.com/spring-projects/spring-framework/commit/365481379d8e331214118a9dc930fb5f201ef8cc)

### 内容

If a field is flagged with `@Autowired` the container uses reflection to set the value. A hint should have been generated automatically for this but it looks like that's not the case at the moment.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-06-19

This is a regression of a refactoring. We used to [flag a field regardless of its visibility](https://github.com/spring-projects/spring-framework/blob/4fe1eaddecaabb41b9fad3c7c5af786b9a68ab83/spring-beans/src/main/java/org/springframework/beans/factory/annotation/AutowiredAnnotationBeanPostProcessor.java#L863) and that is no longer the case.

#### コメント 2 by snicoll

**作成日**: 2022-06-19

A bit frustrating as the tests that were validating hints have been contributed have been dropped apparently.

#### コメント 3 by snicoll

**作成日**: 2022-06-20

Even more frustrating when I realize I was the one saying the hints was wrong in a review document 🙄

---

## Issue #28659: Move Mock duplicates to test fixtures

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-06-20

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28659

**関連リンク**:
- Commits:
  - [90759fb](https://github.com/spring-projects/spring-framework/commit/90759fb38f71b76f36992d3b0a0405fe5aea6f2b)

### 内容

The AOT tests are relying on mock implementations that are duplicated in the codebase. We should rationalize those in test fixtures instread as it makes it hard to change an interface that those duplicated mocks implement.

---

## Issue #28665: Allow dynamic properties in ProblemDetail

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-06-20

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28665

**関連リンク**:
- Commits:
  - [45ee791](https://github.com/spring-projects/spring-framework/commit/45ee7913bff4543dd3b4d701d969743aee258b20)
  - [380aedb](https://github.com/spring-projects/spring-framework/commit/380aedb12a5cc39fa0505d0169a0c0b37f0a1b7b)
  - [263811e](https://github.com/spring-projects/spring-framework/commit/263811ecfa912a55bce8d0371ed20202abcf5dd5)
  - [c139f3d](https://github.com/spring-projects/spring-framework/commit/c139f3d526d29a2e152ce336d29e068774f83dd5)

### 内容

There is a need for a generic map of properties in `ProblemDetail` for properties that are not known ahead of time, and cannot be exposed as setters from a subclass. Based on feedback on https://github.com/spring-projects/spring-framework/issues/27052#issuecomment-1140294702 and https://github.com/spring-projects/spring-framework/issues/27052#issuecomment-1141907448,  

### コメント

#### コメント 1 by vy

**作成日**: 2022-07-05

@rstoyanchev, getting unknown properties mapped to a single field can be tricky for Jackson. Even though this ticket is closed, I would strongly encourage adding tests for checking whether both de- and serialization works as expected.

#### コメント 2 by rstoyanchev

**作成日**: 2022-07-08

@vy, happy to re-open and make further updates. That said, from Jackson's perspective, isn't it just a straight-forward `Map` field to serialize and deserialize? In other words, could you clarify the tricky part is you have in mind?

#### コメント 3 by vy

**作成日**: 2022-07-09

I think we have a misunderstanding about the use case here. Let me try to clarify it with an example. Let the server have a `CustomProblemDetail` extending from `ProblemDetail`:

```java
import org.springframework.http.ProblemDetail;

public class CustomProblemDetail extends ProblemDetail {

    private final String host;

    public CustomProblemDetail(ProblemDetail parent, String host) {
        super(parent);
        this.host = host;
    }

    public void setHost(String host) {
        this.host = host;
    }

    public String getHost() {
        return this.host;
    }

}
```

Due to a service failure, the server responds with a `CustomProblemDetail` and the client receives the following JSON:

```json
{
  "type": "/problem/bad-request",
  "title": "Bad Request",
  "status": 400,
  "detail": "miserable failure",
  "instance": "/greeting",
  "host": "awesome-x3csd3.bol.com"
}
```

Note the extra `host` entry at the bottom.

Since the client doesn't know about the `CustomProblemDetail` class, it will try to deserialize this JSON to a `ProblemDetail`. It would expect `ProblemDetail#properties` to contain a single entry: `host=awesome-x3csd3.bol.com`, though it won't since we didn't use any `@JsonAnyGetter`, `@JsonAnySetter`, etc. magic there. Hence the `host` information get totally lost during deserialization and this should exactly be the goal this feature aims to prevent.

#### コメント 4 by rstoyanchev

**作成日**: 2022-07-11

Thanks for clarifying.

The goal is to avoid dependency on any serialization technology at the lowest level. `ProblemDetail` is the basic abstraction that Spring MVC and WebFlux can use to raise exceptions with the standard fields, and that also helps to enable a range of features for handling and rendering such responses.

Extra properties and serialization magic remain as a separate layer, through sub-classes and a global exception handler cloning the original exception to create the sub-class, as with your `CustomProblemDetail` above.

Originally I left `Map<String, Object> properties` out of `ProblemDetail`, thinking that sub-classes would declare it and add `@JsonAnyGetter/Setter`. I introduced it here, thinking it would be useful still for the base class to provide a way to add dynamic properties from the server side, but your example above is with a property that's known on the server side, but not on the client side. So I'm not sure if dynamic properties from the server side are something all that useful? In any case, the expectation is still for a sub-class to override `getProperties` and `setProperty` and to add `@JsonAnyGetter/Setter`, which does mean that out of the box, a `properties: {}` map is what gets serialized. If that seems not unacceptable, then it doesn't make sense to have `properties` in `ProblemDetail` after all.

I'm thinking that we should add a `JacksonProblemDetail` sub-class with the `@JsonAnyGetter/Setter` annotations and apply it from `ResponseEntityExceptionHandler`, if Jackson is present, or perhaps even create it by default for Spring MVC/WebFlux exceptions when Jackson is present. Then a `CustomProblemDetail` could also extend from `JacksonProblemDetail`.

What do you think?




#### コメント 5 by vy

**作成日**: 2022-07-11

I am happy to hear that we are on the same page. (And thanks so much for hearing me out! :pray:)

> So I'm not sure if dynamic properties from the server side are all something useful?

I think they certainly are! Ideally people shouldn't subclass `ProblemDetail` and should simply use its `properties` to tailor the content. So please keep it.

> I'm thinking that we should add a `JacksonProblemDetail` sub-class with the `@JsonAnyGetter/Setter` annotations and apply it from `ResponseEntityExceptionHandler`, if Jackson is present, or perhaps even create it by default for Spring MVC/WebFlux exceptions when Jackson is present. Then a `CustomProblemDetail` could also extend from `JacksonProblemDetail`.

What about introducing a `ProblemDetailJacksonMixIn` and registering it to the available `ObjectMapper` bean and/or as an `ObjectMapper` customizer? This way, if I am not mistaken, `ProblemDetail` subclasses employing Jackson for serialization will implicitly use the mix-in for the `properties` field, unless they override it or use a custom `ObjectMapper`.

The reason I prefer a mix-in compared to a `JacksonProblemDetail`, the former will implicitly work for any `ProblemDetail` subclass thrown against Jackson, whereas the latter approach expects the user to _always_ subclass from `JacksonProblemDetail` instead.

#### コメント 6 by rstoyanchev

**作成日**: 2022-07-12

No worries, and thanks for tracking this and providing feedback. This is very much appreciated!

Good suggestion for the Jackson mix-in. We'll go with that and register it automatically from `Jackson2ObjectMapperBuilder` so it will require no further configuration. The only drawback is that `properties` will render as a nested map with other libraries but Jackson is popular and comparable solutions could probably be found for others too. The benefit of built-in support for additional properties, and reducing the need for sub-classing, that just works with Jackson is overall a good place to be.


---

## Issue #28666: Stop using SpringFactoriesLoader.loadFactoryNames in the TestContext framework

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-06-20

**ラベル**: in: test, type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28666

**関連リンク**:
- Commits:
  - [d1b65f6](https://github.com/spring-projects/spring-framework/commit/d1b65f6d3e90af3f55d1b4d347afb3ebe9a3de44)
  - [f550329](https://github.com/spring-projects/spring-framework/commit/f5503298fb00d0dde053ec3bb4cd9f91c41313a2)

### 内容

`AbstractTestContextBootstrapper.getDefaultTestExecutionListenerClassNames()` is currently the only remaining use of `SpringFactoriesLoader.loadFactoryNames()` in the core Spring Framework.

Since `SpringFactoriesLoader.loadFactoryNames()` will be deprecated in #27954, we should stop using it and remove the `getDefaultTestExecutionListenerClassNames()` method from `AbstractTestContextBootstrapper`. 

We should likely remove `getDefaultTestExecutionListenerClasses()` as well and refactor `getTestExecutionListeners()` to make use of the new `FailureHandler` support in `SpringFactoriesLoader`.

### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-06-20

Since `getDefaultTestExecutionListenerClassNames()` and `getDefaultTestExecutionListenerClasses()` are both `protected` methods and therefore part of the "public" API for anyone extending `AbstractTestContextBootstrapper` (see https://github.com/spring-projects/spring-framework/issues/27954#issuecomment-1160646333), we could potentially deprecate those two methods in `5.3.x`.

@jhoeller & @snicoll, thoughts? 

---

## Issue #28683: StackOverflowError when using BindingReflectionHintsRegistrar

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-23

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28683

**関連リンク**:
- Commits:
  - [900349f](https://github.com/spring-projects/spring-framework/commit/900349fcca1cd15d50a26cc4d6a360e30e9f9972)
  - [fb1aa4f](https://github.com/spring-projects/spring-framework/commit/fb1aa4f5d5601ddd1fe7928b39c6408a3003a59a)
  - [b121eed](https://github.com/spring-projects/spring-framework/commit/b121eed7533490448e7e98ca84cf34cd4983b0c8)
  - [fe6fd49](https://github.com/spring-projects/spring-framework/commit/fe6fd498899d6c6d3023d8ef8e8cea6955a3aef6)
  - [58aeab3](https://github.com/spring-projects/spring-framework/commit/58aeab3ab68766676942bd097dc42b5f1d2c553c)
  - [1aaa44b](https://github.com/spring-projects/spring-framework/commit/1aaa44bbfe4a6efbab09f3ac48fe6babd60b2ad9)
  - [0546003](https://github.com/spring-projects/spring-framework/commit/0546003dce08724a90bc715b65893386eaca675e)
  - [61e9aa9](https://github.com/spring-projects/spring-framework/commit/61e9aa9f42b34666d94067c23f9c54eea1226a63)
  - [7df1737](https://github.com/spring-projects/spring-framework/commit/7df17370db12cc91e8b62d70a28a1fdb01101588)
  - [5118751](https://github.com/spring-projects/spring-framework/commit/51187517a3b6fa14e8d0647879d898af90ebe4fa)

### 内容

Minimal reproducer:

```
import org.springframework.hateoas.CollectionModel;

public static void main(String[] args) {
  BindingReflectionHintsRegistrar reflectionHintsRegistrar = new BindingReflectionHintsRegistrar();
  ReflectionHints reflectionHints = new ReflectionHints();
  reflectionHintsRegistrar.registerReflectionHints(reflectionHints, CollectionModel.class);
}
```

It looks like the `ResolvableType` in the `CollectionModel1` is the problem, as this crashes too:

```
reflectionHintsRegistrar.registerReflectionHints(reflectionHints, ResolvableType.class);
```

### コメント

#### コメント 1 by mhalbritter

**作成日**: 2022-06-23

The same happens with the `org.springframework.integration.IntegrationPatternType` type.

There's no `ResolvableType` involved, but the type references itself (with a type in between the cycle).

#### コメント 2 by mhalbritter

**作成日**: 2022-06-23

It seems the cycle detection is broken:

```
public class Bar {
  public Bar getBar() {
    return null;
  }
}
```

throws an Exception too.

---

## Issue #28688: Field `PROPAGATION_REQUIRED` not found in class `TransactionDefinition` in native image

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-23

**ラベル**: in: data, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28688

**関連リンク**:
- Commits:
  - [50240bb](https://github.com/spring-projects/spring-framework/commit/50240bb609b6441390d436005a7f2e7a4cdf5454)

### 内容

In the `batch` sample from `spring-native` in `sb-3.0.x` branch, running the native image fails with the following exception:

```
org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'batchApplication': Unsatisfied dependency expressed through field 'jobBuilderFactory': Error creating bean with name 'org.springframework.batch.core.configuration.annotation.SimpleBatchConfiguration': Unsatisfied dependency expressed through field 'configurers': Error creating bean with name 'batchConfigurer': Unable to initialize Spring Batch
	at org.springframework.beans.factory.aot.AutowiredFieldValueResolver.resolveValue(AutowiredFieldValueResolver.java:195) ~[na:na]
	at org.springframework.beans.factory.aot.AutowiredFieldValueResolver.resolveAndSet(AutowiredFieldValueResolver.java:167) ~[na:na]
	at com.example.batch.BatchApplication__Autowiring.apply(BatchApplication__Autowiring.java:14) ~[na:na]
	at org.springframework.beans.factory.support.InstanceSupplier.lambda$andThen$0(InstanceSupplier.java:64) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:930) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:926) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:592) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:735) ~[batch:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:431) ~[batch:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[batch:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1307) ~[batch:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1296) ~[batch:3.0.0-SNAPSHOT]
	at com.example.batch.BatchApplication.main(BatchApplication.java:49) ~[batch:0.0.1-SNAPSHOT]
Caused by: org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'org.springframework.batch.core.configuration.annotation.SimpleBatchConfiguration': Unsatisfied dependency expressed through field 'configurers': Error creating bean with name 'batchConfigurer': Unable to initialize Spring Batch
	at org.springframework.beans.factory.aot.AutowiredFieldValueResolver.resolveValue(AutowiredFieldValueResolver.java:195) ~[na:na]
	at org.springframework.beans.factory.aot.AutowiredFieldValueResolver.resolveAndSet(AutowiredFieldValueResolver.java:167) ~[na:na]
	at org.springframework.batch.core.configuration.annotation.SimpleBatchConfiguration__Autowiring.apply(SimpleBatchConfiguration__Autowiring.java:17) ~[na:na]
	at org.springframework.beans.factory.support.InstanceSupplier.lambda$andThen$0(InstanceSupplier.java:64) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:225) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveNamedBean(DefaultListableBeanFactory.java:1267) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveNamedBean(DefaultListableBeanFactory.java:1228) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveBean(DefaultListableBeanFactory.java:483) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.getBean(DefaultListableBeanFactory.java:338) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.getBean(DefaultListableBeanFactory.java:331) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.batch.core.configuration.annotation.AbstractBatchConfiguration__BeanDefinitions.getJobBuildersInstance(AbstractBatchConfiguration__BeanDefinitions.java:30) ~[na:na]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.config.DependencyDescriptor.resolveCandidate(DependencyDescriptor.java:254) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.doResolveDependency(DefaultListableBeanFactory.java:1374) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:1294) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredFieldValueResolver.resolveValue(AutowiredFieldValueResolver.java:189) ~[na:na]
	... 21 common frames omitted
Caused by: org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'batchConfigurer': Unable to initialize Spring Batch
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.initializeBean(AbstractAutowireCapableBeanFactory.java:1752) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:604) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.config.DependencyDescriptor.resolveCandidate(DependencyDescriptor.java:254) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.addCandidateEntry(DefaultListableBeanFactory.java:1590) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.findAutowireCandidates(DefaultListableBeanFactory.java:1554) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveMultipleBeans(DefaultListableBeanFactory.java:1445) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.doResolveDependency(DefaultListableBeanFactory.java:1332) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:1294) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredFieldValueResolver.resolveValue(AutowiredFieldValueResolver.java:189) ~[na:na]
	... 52 common frames omitted
Caused by: java.lang.IllegalStateException: Unable to initialize Spring Batch
	at org.springframework.boot.autoconfigure.batch.BasicBatchConfigurer.initialize(BasicBatchConfigurer.java:107) ~[batch:0.0.1-SNAPSHOT]
	at org.springframework.boot.autoconfigure.batch.BasicBatchConfigurer.afterPropertiesSet(BasicBatchConfigurer.java:96) ~[batch:0.0.1-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.invokeInitMethods(AbstractAutowireCapableBeanFactory.java:1798) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.initializeBean(AbstractAutowireCapableBeanFactory.java:1748) ~[batch:6.0.0-SNAPSHOT]
	... 65 common frames omitted
Caused by: org.springframework.core.Constants$ConstantException: Field 'PROPAGATION_REQUIRED' not found in class [org.springframework.transaction.TransactionDefinition]
	at org.springframework.core.Constants.asObject(Constants.java:145) ~[na:na]
	at org.springframework.core.Constants.asNumber(Constants.java:113) ~[na:na]
	at org.springframework.transaction.support.DefaultTransactionDefinition.setPropagationBehaviorName(DefaultTransactionDefinition.java:122) ~[batch:6.0.0-SNAPSHOT]
	at org.springframework.transaction.interceptor.TransactionAttributeEditor.setAsText(TransactionAttributeEditor.java:65) ~[na:na]
	at org.springframework.transaction.interceptor.NameMatchTransactionAttributeSource.setProperties(NameMatchTransactionAttributeSource.java:87) ~[na:na]
	at org.springframework.batch.core.repository.support.AbstractJobRepositoryFactoryBean.initializeProxy(AbstractJobRepositoryFactoryBean.java:182) ~[batch:5.0.0-M3]
	at org.springframework.batch.core.repository.support.AbstractJobRepositoryFactoryBean.afterPropertiesSet(AbstractJobRepositoryFactoryBean.java:212) ~[batch:5.0.0-M3]
	at org.springframework.batch.core.repository.support.JobRepositoryFactoryBean.afterPropertiesSet(JobRepositoryFactoryBean.java:225) ~[na:na]
	at org.springframework.boot.autoconfigure.batch.BasicBatchConfigurer.createJobRepository(BasicBatchConfigurer.java:134) ~[batch:0.0.1-SNAPSHOT]
	at org.springframework.boot.autoconfigure.batch.BasicBatchConfigurer.initialize(BasicBatchConfigurer.java:102) ~[batch:0.0.1-SNAPSHOT]
	... 68 common frames omitted
```

I guess there are some hints missing.

### コメント

#### コメント 1 by christophstrobl

**作成日**: 2022-06-27

```java
RuntimeHintsUtils.registerAnnotation(hints, org.springframework.transaction.annotation.Transactional.class);

hints.reflection()
	.registerTypes(asList(
		TypeReference.of(org.springframework.transaction.annotation.Isolation.class),
		TypeReference.of(org.springframework.transaction.annotation.Propagation.class),
		TypeReference.of(org.springframework.transaction.TransactionDefinition.class)),
		hint -> ...)

hints.reflection()
	.registerTypes(asList(
		TypeReference.of(AutoProxyRegistrar.class),
		TypeReference.of(ProxyTransactionManagementConfiguration.class),
		TypeReference.of("org.springframework.transaction.interceptor.BeanFactoryTransactionAttributeSourceAdvisor$1")), ...
```

_(updated to make use of RuntimeHintsUtils.registerAnnotation)_

#### コメント 2 by sdeleuze

**作成日**: 2022-06-28

@christophstrobl Thanks for the hints ;-) What about annotating `ProxyTransactionManagementConfiguration` with `@ImportRuntimeHints(TransactionRuntimeHintsRegistrar.class)` where `TransactionRuntimeHintsRegistrar` would register those entries?

#### コメント 3 by snicoll

**作成日**: 2022-06-28

Please don't register proxies like that, and use registerAnnotation. 

#### コメント 4 by sbrannen

**作成日**: 2023-08-01

@christophstrobl, do you recall why you needed to register reflection hints for the enum constant fields in `Isolation` and `Propagation`?

I'm asking, because while working on #30854 I wondered if we still need those hints.

#### コメント 5 by sbrannen

**作成日**: 2023-08-01

> @christophstrobl, do you recall why you needed to register reflection hints for the enum constant fields in `Isolation` and `Propagation`?

@sdeleuze, Christoph informed me that he does not recall. Do you recall?

#### コメント 6 by sdeleuze

**作成日**: 2023-08-02

I don't, but if we change something here, worth to check if we have a related smoke test and check after that it does not break. In any case, I would advise to test on a sample with both 22.3 and 23.0 GraalVM releases.

---

## Issue #28689: native-image: Support for MethodValidationPostProcessor

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-23

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28689

**関連リンク**:
- Commits:
  - [8c063a0](https://github.com/spring-projects/spring-framework/commit/8c063a0e2ad5f6041c781474ab1fd5f9afacf1f0)

### 内容

When running the native-image from the spring-native sample `cloud-config/configserver` on the `sb-3.0.x` branch, i get the following exception:

```
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'methodValidationPostProcessor': Instantiation of supplied bean failed
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1234) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:205) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.context.support.PostProcessorRegistrationDelegate.registerBeanPostProcessors(PostProcessorRegistrationDelegate.java:261) ~[na:na]
	at org.springframework.context.support.AbstractApplicationContext.registerBeanPostProcessors(AbstractApplicationContext.java:771) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:576) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.boot.web.servlet.context.ServletWebServerApplicationContext.refresh(ServletWebServerApplicationContext.java:146) ~[configserver:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:735) ~[configserver:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:431) ~[configserver:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[configserver:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1307) ~[configserver:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1296) ~[configserver:3.0.0-SNAPSHOT]
	at org.demo.configserver.ConfigServerApplication.main(ConfigServerApplication.java:19) ~[configserver:0.0.1-SNAPSHOT]
Caused by: com.oracle.svm.core.jdk.UnsupportedFeatureError: Proxy class defined by interfaces [interface jakarta.validation.Validator, interface org.springframework.aop.SpringProxy, interface org.springframework.aop.framework.Advised, interface org.springframework.core.DecoratingProxy] not found. Generating proxy classes at runtime is not supported. Proxy classes need to be defined at image build time by specifying the list of interfaces that they implement. To define proxy classes use -H:DynamicProxyConfigurationFiles=<comma-separated-config-files> and -H:DynamicProxyConfigurationResources=<comma-separated-config-resources> options.
	at com.oracle.svm.core.util.VMError.unsupportedFeature(VMError.java:89) ~[na:na]
	at com.oracle.svm.reflect.proxy.DynamicProxySupport.getProxyClass(DynamicProxySupport.java:158) ~[na:na]
	at java.lang.reflect.Proxy.getProxyConstructor(Proxy.java:48) ~[configserver:na]
	at java.lang.reflect.Proxy.newProxyInstance(Proxy.java:1037) ~[configserver:na]
	at org.springframework.aop.framework.JdkDynamicAopProxy.getProxy(JdkDynamicAopProxy.java:126) ~[na:na]
	at org.springframework.aop.framework.ProxyFactory.getProxy(ProxyFactory.java:110) ~[na:na]
	at org.springframework.context.annotation.ContextAnnotationAutowireCandidateResolver.buildLazyResolutionProxy(ContextAnnotationAutowireCandidateResolver.java:130) ~[na:na]
	at org.springframework.context.annotation.ContextAnnotationAutowireCandidateResolver.getLazyResolutionProxyIfNecessary(ContextAnnotationAutowireCandidateResolver.java:54) ~[na:na]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:1291) ~[configserver:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolveArgument(AutowiredInstantiationArgumentsResolver.java:302) ~[na:na]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolveArguments(AutowiredInstantiationArgumentsResolver.java:232) ~[na:na]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolve(AutowiredInstantiationArgumentsResolver.java:154) ~[na:na]
	at org.springframework.boot.autoconfigure.validation.ValidationAutoConfiguration__BeanDefinitions.getMethodValidationPostProcessorInstance(ValidationAutoConfiguration__BeanDefinitions.java:68) ~[na:na]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[configserver:6.0.0-SNAPSHOT]
	... 18 common frames omitted
```

Looks like there are some proxy hints missing.

---

## Issue #28690: native-image: Missing resource hint for ConfigurableMimeFileTypeMap

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-23

**ラベル**: in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28690

**関連リンク**:
- Commits:
  - [16c43c2](https://github.com/spring-projects/spring-framework/commit/16c43c2041a50a8e1fd0befbb71cc2aa9644620a)

### 内容

Running the native-image from spring-native samples in branch `sb-3.0.x` leads to

```
org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'javamailService': Unsatisfied dependency expressed through constructor parameter 0: Error creating bean with name 'mailSender': Instantiation of supplied bean failed
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolveArgument(AutowiredInstantiationArgumentsResolver.java:319) ~[na:na]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolveArguments(AutowiredInstantiationArgumentsResolver.java:232) ~[na:na]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolve(AutowiredInstantiationArgumentsResolver.java:154) ~[na:na]
	at com.example.javamail.service.JavamailService__BeanDefinitions.getJavamailServiceInstance(JavamailService__BeanDefinitions.java:31) ~[na:na]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:930) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:926) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:592) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.boot.web.servlet.context.ServletWebServerApplicationContext.refresh(ServletWebServerApplicationContext.java:146) ~[javamail:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:735) ~[javamail:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:431) ~[javamail:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[javamail:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1307) ~[javamail:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1296) ~[javamail:3.0.0-SNAPSHOT]
	at com.example.javamail.JavamailApplication.main(JavamailApplication.java:10) ~[javamail:0.0.1-SNAPSHOT]
Caused by: org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'mailSender': Instantiation of supplied bean failed
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1234) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.config.DependencyDescriptor.resolveCandidate(DependencyDescriptor.java:254) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.doResolveDependency(DefaultListableBeanFactory.java:1374) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:1294) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolveArgument(AutowiredInstantiationArgumentsResolver.java:302) ~[na:na]
	... 22 common frames omitted
Caused by: java.lang.IllegalStateException: Could not load specified MIME type mapping file: class path resource [org/springframework/mail/javamail/mime.types]
	at org.springframework.mail.javamail.ConfigurableMimeFileTypeMap.getFileTypeMap(ConfigurableMimeFileTypeMap.java:126) ~[na:na]
	at org.springframework.mail.javamail.ConfigurableMimeFileTypeMap.afterPropertiesSet(ConfigurableMimeFileTypeMap.java:110) ~[na:na]
	at org.springframework.mail.javamail.JavaMailSenderImpl.<init>(JavaMailSenderImpl.java:115) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.boot.autoconfigure.mail.MailSenderPropertiesConfiguration.mailSender(MailSenderPropertiesConfiguration.java:44) ~[javamail:0.0.1-SNAPSHOT]
	at org.springframework.boot.autoconfigure.mail.MailSenderPropertiesConfiguration__BeanDefinitions.lambda$getMailSenderInstance$0(MailSenderPropertiesConfiguration__BeanDefinitions.java:41) ~[na:na]
	at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:63) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:51) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolve(AutowiredInstantiationArgumentsResolver.java:156) ~[na:na]
	at org.springframework.boot.autoconfigure.mail.MailSenderPropertiesConfiguration__BeanDefinitions.getMailSenderInstance(MailSenderPropertiesConfiguration__BeanDefinitions.java:41) ~[na:na]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[javamail:6.0.0-SNAPSHOT]
	... 34 common frames omitted
Caused by: java.io.FileNotFoundException: class path resource [org/springframework/mail/javamail/mime.types] cannot be opened because it does not exist
	at org.springframework.core.io.ClassPathResource.getInputStream(ClassPathResource.java:183) ~[javamail:6.0.0-SNAPSHOT]
	at org.springframework.mail.javamail.ConfigurableMimeFileTypeMap.createFileTypeMap(ConfigurableMimeFileTypeMap.java:149) ~[na:na]
	at org.springframework.mail.javamail.ConfigurableMimeFileTypeMap.getFileTypeMap(ConfigurableMimeFileTypeMap.java:123) ~[na:na]
	... 43 common frames omitted
```

There's a resource hint missing.

---

## Issue #28696: native-image: Problem with Scheduled annotation

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-24

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28696

**関連リンク**:
- Commits:
  - [fd265a1](https://github.com/spring-projects/spring-framework/commit/fd265a18c619b21f97f753871c6e1c32df65ba32)

### 内容

When running the native-image from the spring-native sample `scheduling-tasks` on the `sb-3.0.x` branch, i get the following exception:

```
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'schedulingTasksApplication': Invalid declaration of container type [org.springframework.scheduling.annotation.Schedules] for repeatable annotation [org.springframework.scheduling.annotation.Scheduled]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:611) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:930) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:926) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:592) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:735) ~[scheduling-tasks:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:431) ~[scheduling-tasks:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[scheduling-tasks:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1307) ~[scheduling-tasks:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1296) ~[scheduling-tasks:3.0.0-SNAPSHOT]
	at com.example.schedulingtasks.SchedulingTasksApplication.main(SchedulingTasksApplication.java:13) ~[scheduling-tasks:0.0.1-SNAPSHOT]
Caused by: org.springframework.core.annotation.AnnotationConfigurationException: Invalid declaration of container type [org.springframework.scheduling.annotation.Schedules] for repeatable annotation [org.springframework.scheduling.annotation.Scheduled]
	at org.springframework.core.annotation.RepeatableContainers$ExplicitRepeatableContainer.<init>(RepeatableContainers.java:219) ~[na:na]
	at org.springframework.core.annotation.RepeatableContainers.of(RepeatableContainers.java:117) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.core.annotation.AnnotatedElementUtils.getRepeatableAnnotations(AnnotatedElementUtils.java:759) ~[na:na]
	at org.springframework.core.annotation.AnnotatedElementUtils.getMergedRepeatableAnnotations(AnnotatedElementUtils.java:455) ~[na:na]
	at org.springframework.scheduling.annotation.ScheduledAnnotationBeanPostProcessor.lambda$postProcessAfterInitialization$0(ScheduledAnnotationBeanPostProcessor.java:366) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.core.MethodIntrospector.lambda$selectMethods$0(MethodIntrospector.java:74) ~[na:na]
	at org.springframework.util.ReflectionUtils.doWithMethods(ReflectionUtils.java:366) ~[na:na]
	at org.springframework.core.MethodIntrospector.selectMethods(MethodIntrospector.java:72) ~[na:na]
	at org.springframework.scheduling.annotation.ScheduledAnnotationBeanPostProcessor.postProcessAfterInitialization(ScheduledAnnotationBeanPostProcessor.java:364) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.applyBeanPostProcessorsAfterInitialization(AbstractAutowireCapableBeanFactory.java:440) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.initializeBean(AbstractAutowireCapableBeanFactory.java:1755) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:604) ~[scheduling-tasks:6.0.0-SNAPSHOT]
	... 14 common frames omitted
Caused by: java.lang.NoSuchMethodException: No value method found
	at org.springframework.core.annotation.RepeatableContainers$ExplicitRepeatableContainer.<init>(RepeatableContainers.java:203) ~[na:na]
	... 25 common frames omitted
```

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-07-04

@sdeleuze is the registrar really necessary? Unless the implementation has changed, adding `@Reflective` should register the annotation as well. 

Now the agent is available it would be nice to have a test for this. 

#### コメント 2 by sdeleuze

**作成日**: 2022-07-04

I will double check.

#### コメント 3 by sdeleuze

**作成日**: 2022-07-04

It does not work without the registrar (maybe something to refine on `@Reflective` to refine later), I will add related tests.

---

## Issue #28697: Add runtime hints for `AbstractHandshakeHandler`

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-24

**ラベル**: in: web, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28697

**関連リンク**:
- Commits:
  - [ecdd934](https://github.com/spring-projects/spring-framework/commit/ecdd934658fa99c3420fc583331edb1be6e1634d)

### 内容

When running the native-image from the spring-native sample `websocket` on the `sb-3.0.x` branch, i get the following exception:

```
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'stompWebSocketHandlerMapping': Instantiation of supplied bean failed
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1234) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:930) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:926) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:592) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.boot.web.servlet.context.ServletWebServerApplicationContext.refresh(ServletWebServerApplicationContext.java:146) ~[websocket:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:735) ~[websocket:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:431) ~[websocket:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[websocket:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1307) ~[websocket:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1296) ~[websocket:3.0.0-SNAPSHOT]
	at com.example.websocket.WebsocketApplication.main(WebsocketApplication.java:20) ~[websocket:0.0.1-SNAPSHOT]
Caused by: java.lang.IllegalStateException: Failed to instantiate RequestUpgradeStrategy: org.springframework.web.socket.server.standard.TomcatRequestUpgradeStrategy
	at org.springframework.web.socket.server.support.AbstractHandshakeHandler.initRequestUpgradeStrategy(AbstractHandshakeHandler.java:160) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.web.socket.server.support.AbstractHandshakeHandler.<init>(AbstractHandshakeHandler.java:118) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.web.socket.server.support.DefaultHandshakeHandler.<init>(DefaultHandshakeHandler.java:35) ~[na:na]
	at org.springframework.web.socket.server.support.WebSocketHttpRequestHandler.<init>(WebSocketHttpRequestHandler.java:73) ~[na:na]
	at org.springframework.web.socket.config.annotation.WebMvcStompWebSocketEndpointRegistration.getMappings(WebMvcStompWebSocketEndpointRegistration.java:160) ~[na:na]
	at org.springframework.web.socket.config.annotation.WebMvcStompEndpointRegistry.getHandlerMapping(WebMvcStompEndpointRegistry.java:155) ~[na:na]
	at org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurationSupport.stompWebSocketHandlerMapping(WebSocketMessageBrokerConfigurationSupport.java:92) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurationSupport__BeanDefinitions.lambda$getStompWebSocketHandlerMappingInstance$0(WebSocketMessageBrokerConfigurationSupport__BeanDefinitions.java:38) ~[na:na]
	at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:63) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:51) ~[websocket:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolve(AutowiredInstantiationArgumentsResolver.java:156) ~[na:na]
	at org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurationSupport__BeanDefinitions.getStompWebSocketHandlerMappingInstance(WebSocketMessageBrokerConfigurationSupport__BeanDefinitions.java:38) ~[na:na]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[websocket:6.0.0-SNAPSHOT]
	... 18 common frames omitted
Caused by: java.lang.ClassNotFoundException: org.springframework.web.socket.server.standard.TomcatRequestUpgradeStrategy
	at java.lang.Class.forName(DynamicHub.java:1121) ~[websocket:na]
	at org.springframework.util.ClassUtils.forName(ClassUtils.java:284) ~[na:na]
	at org.springframework.web.socket.server.support.AbstractHandshakeHandler.initRequestUpgradeStrategy(AbstractHandshakeHandler.java:156) ~[websocket:6.0.0-SNAPSHOT]
	... 30 common frames omitted
```

---

## Issue #28701: RuntimeHints missing for WebFlux

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-24

**ラベル**: in: web, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28701

**関連リンク**:
- Commits:
  - [8a7f82b](https://github.com/spring-projects/spring-framework/commit/8a7f82b8008f70295396419da0f7fc687e60206c)
  - [4ec3e10](https://github.com/spring-projects/spring-framework/commit/4ec3e1042a2018562e1aa1d1bc79c6d9b624d004)

### 内容

I had to add these hints to get WebFlux with Netty running, using the spring-native sample `webflux-netty` on [this branch](https://github.com/mhalbritter/spring-native/tree/mh/netty):

```
        hints.resources().registerPattern("org/springframework/http/codec/CodecConfigurer.properties");
        hints.reflection().registerType(DefaultClientCodecConfigurer.class, hint -> hint.withMembers(MemberCategory.INVOKE_PUBLIC_CONSTRUCTORS));
        hints.reflection().registerType(DefaultServerCodecConfigurer.class, hint -> hint.withMembers(MemberCategory.INVOKE_PUBLIC_CONSTRUCTORS));
        RuntimeHintsUtils.registerAnnotation(hints, RequestMapping.class);
```

I only did the minimal possible work that the sample passes, so I guess this is far from being complete.

---

## Issue #28709: Jackson well-known module support in native image

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-27

**ラベル**: type: enhancement, theme: aot, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28709

**関連リンク**:
- Commits:
  - [f782517](https://github.com/spring-projects/spring-framework/commit/f78251769c84ad94b9289b7b862e01a0c5eb8a79)
  - [e94f2a8](https://github.com/spring-projects/spring-framework/commit/e94f2a8e3ffaf203053ec82ea7719e4ca11c6a77)

### 内容

When running the binary from the `webflux-kotlin` sample from spring-native, I get the following exception:

```
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'jacksonObjectMapper': Instantiation of supplied bean failed
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1234) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:930) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:926) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:592) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.boot.web.reactive.context.ReactiveWebServerApplicationContext.refresh(ReactiveWebServerApplicationContext.java:66) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:729) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:428) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:1301) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:1290) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at com.example.webflux.WebfluxApplicationKt.main(WebfluxApplication.kt:16) ~[webflux-kotlin:0.0.1-SNAPSHOT]
Caused by: kotlin.jvm.KotlinReflectionNotSupportedError: Kotlin reflection implementation is not found at runtime. Make sure you have kotlin-reflect.jar in the classpath
        at kotlin.jvm.internal.ClassReference.error(ClassReference.kt:88) ~[na:na]
        at kotlin.jvm.internal.ClassReference.getConstructors(ClassReference.kt:21) ~[na:na]
        at kotlin.reflect.jvm.ReflectJvmMapping.getKotlinFunction(ReflectJvmMapping.kt:146) ~[na:na]
        at org.springframework.beans.BeanUtils$KotlinDelegate.instantiateClass(BeanUtils.java:869) ~[na:na]
        at org.springframework.beans.BeanUtils.instantiateClass(BeanUtils.java:191) ~[na:na]
        at org.springframework.beans.BeanUtils.instantiateClass(BeanUtils.java:152) ~[na:na]
        at org.springframework.http.converter.json.Jackson2ObjectMapperBuilder.registerWellKnownModulesIfAvailable(Jackson2ObjectMapperBuilder.java:842) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.http.converter.json.Jackson2ObjectMapperBuilder.configure(Jackson2ObjectMapperBuilder.java:689) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.http.converter.json.Jackson2ObjectMapperBuilder.build(Jackson2ObjectMapperBuilder.java:672) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.boot.autoconfigure.jackson.JacksonAutoConfiguration$JacksonObjectMapperConfiguration.jacksonObjectMapper(JacksonAutoConfiguration.java:113) ~[webflux-kotlin:3.0.0-SNAPSHOT]
        at org.springframework.boot.autoconfigure.jackson.JacksonAutoConfiguration_JacksonObjectMapperConfiguration__BeanDefinitions.lambda$getJacksonObjectMapperInstance$0(JacksonAutoConfiguration_JacksonObjectMapperConfiguration__BeanDefinitions.java:43) ~[na:na]
        at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:63) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:51) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolve(AutowiredInstantiationArgumentsResolver.java:156) ~[na:na]
        at org.springframework.boot.autoconfigure.jackson.JacksonAutoConfiguration_JacksonObjectMapperConfiguration__BeanDefinitions.getJacksonObjectMapperInstance(JacksonAutoConfiguration_JacksonObjectMapperConfiguration__BeanDefinitions.java:43) ~[na:na]
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[webflux-kotlin:6.0.0-SNAPSHOT]
        ... 18 common frames omitted
```

There is

```
		<dependency>
			<groupId>org.jetbrains.kotlin</groupId>
			<artifactId>kotlin-reflect</artifactId>
		</dependency>
```

in the `pom.xml`, the sample runs with `mvn spring-boot:run`

### コメント

#### コメント 1 by sdeleuze

**作成日**: 2022-06-28

Seems related to the well-known Jackson modules (here `KotlinModule`) registered in [Jackson2ObjectMapperBuilder#registerWellKnownModulesIfAvailable](https://github.com/spring-projects/spring-framework/blob/efb83fa064b3d3335393defcf6d6fa785c0e3ef6/spring-web/src/main/java/org/springframework/http/converter/json/Jackson2ObjectMapperBuilder.java#L816).

There could be Kotlin reflection hints missing as well (but those ones should go in the reachability metadata reprository I think, not sure yet what we do in the interim).

Spring Native [`KotlinHints`](https://github.com/spring-projects-experimental/spring-native/blob/main/spring-native-configuration/src/main/java/kotlin/KotlinHints.java) could be used as a source of inspiration.

#### コメント 2 by sdeleuze

**作成日**: 2022-06-30

Notice I had to add Kotlin hints via https://github.com/spring-projects-experimental/spring-native/commit/3392357741671f29b5934a000f5d7c34070eadc0 to make it work, this will go to the reachability repo or better we could ask Kotlin team to ship that out of the box.

---

## Issue #28714: Replace java.util.Date and TimeUnit usage in scheduling with appropiate java.time classes

**状態**: closed | **作成者**: desiderantes | **作成日**: 2022-06-27

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28714

**関連リンク**:
- Commits:
  - [9b739a2](https://github.com/spring-projects/spring-framework/commit/9b739a2310bac781c89a22bf92650615f9dd7406)

### 内容

Given that a lot of times we get the values for Triggers and such from configs or other places that use java.time types, and the fact that they're the proper types to model this sort of thing, it would be nice to reduce usage of java.util.Date (since it's so prone to improper handling).


### コメント

#### コメント 1 by poutsma

**作成日**: 2022-07-08

@desiderantes This is now complete, see https://github.com/spring-projects/spring-framework/commit/9b739a2310bac781c89a22bf92650615f9dd7406. Let me know if there are `java.util.Date` usages that I missed.

#### コメント 2 by desiderantes

**作成日**: 2022-07-08

@poutsma Whoah, thanks a lot! I don't see other usages of java.util.Date in scheduling (and I can't judge the usages in the other parts)

---

## Issue #28717: Add support for `@Transactional` in native images

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-28

**ラベル**: in: data, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28717

**関連リンク**:
- Commits:
  - [c77a3bc](https://github.com/spring-projects/spring-framework/commit/c77a3bcc4f13624c40874a2e9148353126fc49f7)
  - [69739e5](https://github.com/spring-projects/spring-framework/commit/69739e5e87ae0fdec8c6bef797012860151f51a3)
  - [0387d54](https://github.com/spring-projects/spring-framework/commit/0387d54607f371b7ff9e28dd8a89ec6203d3a09b)
  - [8d12d4d](https://github.com/spring-projects/spring-framework/commit/8d12d4d0c6e8499de8e48a4b66ae547d7a2cfb98)
  - [975a7f0](https://github.com/spring-projects/spring-framework/commit/975a7f0e4c15d21ca7a3acade5d7657ad9183be1)
  - [032a9c8](https://github.com/spring-projects/spring-framework/commit/032a9c8f38a68c8c1b305b496082f4a5c4f87121)
  - [49fd7c9](https://github.com/spring-projects/spring-framework/commit/49fd7c99ae6483b4878145bf79ae1fe93de74f7d)
  - [8ccf05a](https://github.com/spring-projects/spring-framework/commit/8ccf05adeefa3fd2a377eba067a156ea163dd616)
  - [dfbcaf3](https://github.com/spring-projects/spring-framework/commit/dfbcaf31dcbcd37d065db581fb62e8def726f389)
  - [1458d5f](https://github.com/spring-projects/spring-framework/commit/1458d5f39fef06d01348352fc67d5bc2cbe812e9)

### 内容

When running the `jdbc-tx` sample in `sb-3.0.x` branch from spring-native, it fails with:

```
java.lang.IllegalStateException: Failed to execute CommandLineRunner
        at org.springframework.boot.SpringApplication.callRunner(SpringApplication.java:769) ~[jdbc-tx:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.callRunners(SpringApplication.java:750) ~[jdbc-tx:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:318) ~[jdbc-tx:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:1301) ~[jdbc-tx:3.0.0-SNAPSHOT]
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:1290) ~[jdbc-tx:3.0.0-SNAPSHOT]
        at app.main.SampleApplication.main(SampleApplication.java:23) ~[jdbc-tx:0.0.1.BUILD-SNAPSHOT]
Caused by: java.lang.IllegalArgumentException: Expected transaction
        at org.springframework.util.Assert.isTrue(Assert.java:121) ~[na:na]
        at app.main.Runner.run(Runner.java:53) ~[jdbc-tx:0.0.1.BUILD-SNAPSHOT]
        at org.springframework.boot.SpringApplication.callRunner(SpringApplication.java:766) ~[jdbc-tx:3.0.0-SNAPSHOT]
        ... 5 common frames omitted
```

This is the run method:

```java
	@Override
	@Transactional
	public void run(String... args) throws Exception {
		Assert.isTrue(TransactionSynchronizationManager.isActualTransactionActive(), "Expected transaction");
		try {
			find(1L);
		}
		catch (EmptyResultDataAccessException e) {
			entities.update(ADD_FOO, 1L, "Hello");
		}
	}
```

I guess that `@Transactional` doesn't work in native-image.

### コメント

#### コメント 1 by sdeleuze

**作成日**: 2022-06-28

Related to #28688.

#### コメント 2 by sdeleuze

**作成日**: 2022-07-07

I have improved the support for `@Transactional` with [this commit](https://github.com/spring-projects/spring-framework/commit/0387d54607f371b7ff9e28dd8a89ec6203d3a09b) that makes `@Transactional` annotated with `@Reflective` and registers proxy hints for `SpringProxy` but the `jdbc-tx` sample [here](https://github.com/spring-projects-experimental/spring-native/tree/sb-3.0.x/samples/jdbc-tx) still fails when compiled as a native executable with `error creating bean with name 'userEndpoints': Unsatisfied dependency expressed through method 'userEndpoints' parameter 0: No qualifying bean of type 'app.main.Finder<app.main.model.Foo>' available: expected at least 1 bean which qualifies as autowire candidate. Dependency annotations: {} error`, like if proxied beans can't be injected in native. Notice here we have `@Component public class Runner implements CommandLineRunner, Finder<Foo> { ... }` that needs to be injected in `@Bean public RouterFunction<?> userEndpoints(Finder<Foo> entities) { ... }`.This samples works correctly on JVM + AOT so this issue is native specific.

#### コメント 3 by sdeleuze

**作成日**: 2022-07-07

As discussed with @sbrannen, we need to replace the `SpringProxyRuntimeHintsRegistrar` by an AOT processor that will register dynamically the required proxies like here `CommandLineRunner.class, Finder.class, SpringProxy.class, Advised.class, DecoratingProxy.class` + reflection entries for proxied interfaces with [declared methods](https://github.com/spring-projects/spring-framework/blob/main/spring-aop/src/main/java/org/springframework/aop/framework/JdkDynamicAopProxy.java#L136).

---

## Issue #28721: Add support for records in BindingReflectionHintsRegistrar

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-28

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28721

**関連リンク**:
- Commits:
  - [da68781](https://github.com/spring-projects/spring-framework/commit/da68781b9ef3d00151ad938209c69c7b7c35288a)

### 内容

Using `BindingReflectionHintsRegistrar` with records lead to this Jackson exception on native image runtime:

```
Exception in thread "main" com.fasterxml.jackson.databind.exc.InvalidDefinitionException: Failed to access RecordComponents of type `nativeplayground.R`
        at com.fasterxml.jackson.databind.SerializerProvider.reportBadDefinition(SerializerProvider.java:1300)
        at com.fasterxml.jackson.databind.SerializerProvider._createAndCacheUntypedSerializer(SerializerProvider.java:1447)
        at com.fasterxml.jackson.databind.SerializerProvider.findValueSerializer(SerializerProvider.java:544)
        at com.fasterxml.jackson.databind.SerializerProvider.findTypedValueSerializer(SerializerProvider.java:822)
        at com.fasterxml.jackson.databind.ser.DefaultSerializerProvider.serializeValue(DefaultSerializerProvider.java:308)
        at com.fasterxml.jackson.databind.ObjectMapper._writeValueAndClose(ObjectMapper.java:4568)
        at com.fasterxml.jackson.databind.ObjectMapper.writeValueAsString(ObjectMapper.java:3821)
        at nativeplayground.SerializeMain.main(SerializeMain.java:14)
```

For records, there has to be this in the reflect-config.json:

```
  {
    "name": "nativeplayground.R",
    "allDeclaredMethods": true
  }
```

It would be nice if `BindingReflectionHintsRegistrar` would support records.

---

## Issue #28722: HtmlUnit / MockMvc integration handles forwarded URLs partially

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-06-28

**ラベル**: in: test, in: web, type: bug

**URL**: https://github.com/spring-projects/spring-framework/issues/28722

**関連リンク**:
- Commits:
  - [9c2ad4a](https://github.com/spring-projects/spring-framework/commit/9c2ad4a1b15f64375aa537097f649d3f2b26b402)

### 内容

Currently `ForwardRequestPostProcessor` uses the forwarded URL only to set the servletPath of the mock request, which means `requestUri` and `servletPath` are out of sync.

This hasn't been reported as an issue since `UrlPathHelper` falls back on the `servletPath` if it doesn't match the `requestURI` but that's not really correct behavior, and causes issues in more modern setups like parsed patterns where we rely mainly on the `requestURI` and only check the `servletPath` if a Servlet prefix mapping can be confirmed with Servlet 4.0. 

In the absence of a Servlet container, i.e. with mock request and response, there is actually no good way to take a `forwardedUrl` and break it down into `contextPath`, `servletPath`, and `pathInfo`. At best, we can assert that the forwarded URL does start with the same `contextPath`, but otherwise break it down into `contextPath` + `servletPath`.

This was uncovered while working on #28607.

---

## Issue #28727: AOT generated code leads to exception on startup: Object of class [java.lang.Boolean] must be an instance of boolean

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-06-29

**ラベル**: type: bug, in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28727

**関連リンク**:
- Commits:
  - [a21b27e](https://github.com/spring-projects/spring-framework/commit/a21b27e6d924e5be356d337ad374e007469ccbda)

### 内容

Hi,

when running a Spring Boot project with the `starter-integration` in it in AOT mode, it crashes on startup with this exception:

```
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'errorChannel': Instantiation of supplied bean failed
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1234) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainFromSupplier(AbstractAutowireCapableBeanFactory.java:1209) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1156) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:566) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:526) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:326) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:234) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:324) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:200) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:930) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:926) ~[spring-context-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:592) ~[spring-context-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:729) ~[spring-boot-3.0.0-SNAPSHOT.jar!/:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:428) ~[spring-boot-3.0.0-SNAPSHOT.jar!/:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:310) ~[spring-boot-3.0.0-SNAPSHOT.jar!/:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1301) ~[spring-boot-3.0.0-SNAPSHOT.jar!/:3.0.0-SNAPSHOT]
	at org.springframework.boot.SpringApplication.run(SpringApplication.java:1290) ~[spring-boot-3.0.0-SNAPSHOT.jar!/:3.0.0-SNAPSHOT]
	at com.example.integrationaot.IntegrationAotApplication.main(IntegrationAotApplication.java:10) ~[classes!/:0.0.1-SNAPSHOT]
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method) ~[na:na]
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77) ~[na:na]
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43) ~[na:na]
	at java.base/java.lang.reflect.Method.invoke(Method.java:568) ~[na:na]
	at org.springframework.boot.loader.MainMethodRunner.run(MainMethodRunner.java:49) ~[integration-aot-0.0.1-SNAPSHOT.jar:0.0.1-SNAPSHOT]
	at org.springframework.boot.loader.Launcher.launch(Launcher.java:95) ~[integration-aot-0.0.1-SNAPSHOT.jar:0.0.1-SNAPSHOT]
	at org.springframework.boot.loader.Launcher.launch(Launcher.java:58) ~[integration-aot-0.0.1-SNAPSHOT.jar:0.0.1-SNAPSHOT]
	at org.springframework.boot.loader.JarLauncher.main(JarLauncher.java:65) ~[integration-aot-0.0.1-SNAPSHOT.jar:0.0.1-SNAPSHOT]
Caused by: java.lang.IllegalArgumentException: Object of class [java.lang.Boolean] must be an instance of boolean
	at org.springframework.util.Assert.instanceCheckFailed(Assert.java:702) ~[spring-core-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.util.Assert.isInstanceOf(Assert.java:602) ~[spring-core-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.util.Assert.isInstanceOf(Assert.java:633) ~[spring-core-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredArguments.get(AutowiredArguments.java:45) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.integration.channel.PublishSubscribeChannel__BeanDefinitions.lambda$getErrorChannelInstance$0(PublishSubscribeChannel__BeanDefinitions.java:31) ~[classes!/:0.0.1-SNAPSHOT]
	at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:63) ~[spring-core-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.util.function.ThrowingFunction.apply(ThrowingFunction.java:51) ~[spring-core-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.beans.factory.aot.AutowiredInstantiationArgumentsResolver.resolve(AutowiredInstantiationArgumentsResolver.java:156) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	at org.springframework.integration.channel.PublishSubscribeChannel__BeanDefinitions.getErrorChannelInstance(PublishSubscribeChannel__BeanDefinitions.java:31) ~[classes!/:0.0.1-SNAPSHOT]
	at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.obtainInstanceFromSupplier(AbstractAutowireCapableBeanFactory.java:1223) ~[spring-beans-6.0.0-SNAPSHOT.jar!/:6.0.0-SNAPSHOT]
	... 25 common frames omitted
```

This looks like a bug in the AOT generated code (?).

Reproducer repo: https://github.com/mhalbritter/integration-aot

### コメント

#### コメント 1 by jhoeller

**作成日**: 2022-06-29

Looks like a strict instance-of check where we should be using `isAssignableValue` as we do in other places.

---

## Issue #28728: Support by-type constructor references in `ConstructorOrFactoryMethodResolver`

**状態**: closed | **作成者**: mp911de | **作成日**: 2022-06-29

**ラベル**: type: bug, in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28728

**関連リンク**:
- Commits:
  - [d2e27ad](https://github.com/spring-projects/spring-framework/commit/d2e27ad75407e00175f717e2ed5bcf9249e6825c)

### 内容

`ConstructorOrFactoryMethodResolver` supports type various constructor argument types such as by-name references through inspecting `BeanReference`. It would be neat to also support `RuntimeBeanReference` with a `Class` argument to lookup beans by their type rather than just the type name. Having by-type references that work similar to the non-AOT runtime arrangement would simplify bean definitions.

FWIW, a `RuntimeBeanReference` leads to the following exception:

```
Exception in thread "main" org.springframework.beans.factory.NoSuchBeanDefinitionException: No bean named 'org.springframework.data.mongodb.core.mapping.MongoMappingContext' available
	at org.springframework.beans.factory.support.DefaultListableBeanFactory.getBeanDefinition(DefaultListableBeanFactory.java:862)
	at org.springframework.beans.factory.support.AbstractBeanFactory.getMergedLocalBeanDefinition(AbstractBeanFactory.java:1302)
	at org.springframework.beans.factory.support.AbstractBeanFactory.getType(AbstractBeanFactory.java:691)
	at org.springframework.beans.factory.aot.ConstructorOrFactoryMethodResolver.determineParameterValueType(ConstructorOrFactoryMethodResolver.java:137)
	at org.springframework.beans.factory.aot.ConstructorOrFactoryMethodResolver.determineParameterValueTypes(ConstructorOrFactoryMethodResolver.java:125)
	at org.springframework.beans.factory.aot.ConstructorOrFactoryMethodResolver.resolve(ConstructorOrFactoryMethodResolver.java:84)
	at org.springframework.beans.factory.aot.ConstructorOrFactoryMethodResolver.resolve(ConstructorOrFactoryMethodResolver.java:436)
	at org.springframework.beans.factory.aot.BeanDefinitionMethodGenerator.<init>(BeanDefinitionMethodGenerator.java:73)
	at org.springframework.beans.factory.aot.BeanDefinitionMethodGeneratorFactory.getBeanDefinitionMethodGenerator(BeanDefinitionMethodGeneratorFactory.java:91)
	at org.springframework.beans.factory.aot.BeanRegistrationsAotProcessor.processAheadOfTime(BeanRegistrationsAotProcessor.java:44)
	at org.springframework.beans.factory.aot.BeanRegistrationsAotProcessor.processAheadOfTime(BeanRegistrationsAotProcessor.java:32)
	at org.springframework.context.aot.BeanFactoryInitializationAotContributions.getContributions(BeanFactoryInitializationAotContributions.java:67)
	at org.springframework.context.aot.BeanFactoryInitializationAotContributions.<init>(BeanFactoryInitializationAotContributions.java:49)
	at org.springframework.context.aot.BeanFactoryInitializationAotContributions.<init>(BeanFactoryInitializationAotContributions.java:44)
	at org.springframework.context.aot.ApplicationContextAotGenerator.generateApplicationContext(ApplicationContextAotGenerator.java:53)
	at org.springframework.boot.AotProcessor.performAotProcessing(AotProcessor.java:150)
	at org.springframework.boot.AotProcessor.process(AotProcessor.java:111)
	at org.springframework.boot.AotProcessor.main(AotProcessor.java:221)
```

---

## Issue #28735: Move `BindingReflectionHintsRegistrar` to spring-context

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-06-30

**ラベル**: type: task, in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28735

**関連リンク**:
- Commits:
  - [9135921](https://github.com/spring-projects/spring-framework/commit/9135921d1d5522ababce683fd027adfcdda55822)

### 内容

Move `BindingReflectionHintsRegistrar` to `spring-context` module in `org.springframework.context.aot` package because:
 - Otherwise we can't test it with the agent that lives in spring-core-test
 - Conceptually this is for reflection based serialization like Jackson (that lives in `spring-web`) and databinder (that lives in `spring-context`)

---

## Issue #28745: Simplify hint registration for Spring AOP proxies

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-07-02

**ラベル**: in: core, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28745

**関連リンク**:
- Commits:
  - [49dfcad](https://github.com/spring-projects/spring-framework/commit/49dfcad44743d9c87cfe64af263648861e4dea6b)
  - [7bfcb4c](https://github.com/spring-projects/spring-framework/commit/7bfcb4c753c86768a28c9612966b8f30184b48f2)
  - [5178e9c](https://github.com/spring-projects/spring-framework/commit/5178e9c28eda20859829937c1bc3d38b8b314726)

### 内容

For JDK dynamic proxies created by Spring's AOP support, `SpringProxy`, `Advised`, and `DecoratingProxy` will often be included in the interfaces that the proxy implements.

Here's an example taken from Spring Integration.

```java
proxyHints
    .registerJdkProxy(RequestReplyExchanger.class, SpringProxy.class, Advised.class, DecoratingProxy.class)
    .registerJdkProxy(AbstractReplyProducingMessageHandler.RequestHandler.class, SpringProxy.class, Advised.class, DecoratingProxy.class)
    .registerJdkProxy(IntegrationFlow.class, SmartLifecycle.class, SpringProxy.class, Advised.class, DecoratingProxy.class);
```

We should investigate options for simplifying the proxy hint registration for Spring AOP proxies so that users are not required to specify `SpringProxy`, `Advised`, and `DecoratingProxy`.

One option would be to introduce a new `registerSpringJdkProxy(...)` method (or similar) in `ProxyHints` that automatically registers the required Spring AOP interfaces. Though, it is not always the case that all 3 of those interfaces are implemented by the proxy. So we could document that this particular `registerSpringJdkProxy(...)` variant always registers those 3 particular interfaces to cover common use cases and allow users to continue to use `registerJdkProxy(...)` when the additional Spring AOP interfaces differ from that common set of 3.

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-07-02

We can't really do that, can we? Spring AOP is higher in the dependency tree. Perhaps something along the lines of RuntimeHintsUtils, but for SpringAopProxy?

I am afk but perhaps AopUtils could be used?

#### コメント 2 by sbrannen

**作成日**: 2022-07-02

> Spring AOP is higher in the dependency tree.

That's a good point. We definitely cannot refer to the `Class` references, and it does unfortunately seem a bit out of place to be talking about Spring AOP in Spring Core.

> We can't really do that, can we?

Well, by using the class names we can implement it like this:

```java
public ProxyHints registerSpringAopJdkProxy(Class<?>... proxiedInterfaces) {
    return registerJdkProxy(jdkProxyHint -> {
        jdkProxyHint.proxiedInterfaces(proxiedInterfaces);
        jdkProxyHint.proxiedInterfaces(
            TypeReference.of("org.springframework.aop.SpringProxy"),
            TypeReference.of("org.springframework.aop.framework.Advised"),
            TypeReference.of("org.springframework.core.DecoratingProxy"));
    });
}
```

> Perhaps something along the lines of RuntimeHintsUtils, but for SpringAopProxy?

Sure. If we don't want to use the class name based approach I pasted above, we could introduce something along the lines of `RuntimeHintsUtils` for Spring AOP proxies in `spring-aop`.


> I am afk but perhaps AopUtils could be used?

Not that I'm aware of.

#### コメント 3 by snicoll

**作成日**: 2022-07-03

> Well, by using the class names we can implement it like this:

That sounds like hiding a conceptual cycle to me.

> Sure. If we don't want to use the class name based approach I pasted above, 

Are we doing this elsewhere, except in Javadoc links?

> Not that I'm aware of.

How do you mean? I believe `AopUtils#registerAopProxyHints(Class<?>... proxiedInterfaces)` could be  a possibility.

#### コメント 4 by sbrannen

**作成日**: 2022-07-04

**Team Decision**:

- Introduce static utility methods in `AopProxyUtils` that combine user provided interfaces with `SpringProxy`, `Advised`, and `DecoratingProxy`.
- This method could be named something along the lines of `completeProxiedInterfaces()` to align with the existing methods in that class.
- We will need to two variants, one accepting `Class<?>...` and one accepting `TypeReference...`.
- The returned arrays should be able to be supplied as input to both variants of `proxyHints.registerJdkProxy()`.
- Cross reference these new methods from the Javadoc in the existing `registerJdkProxy()` methods in `spring-core` to make the AOP specific support _discoverable_ via the core user API.

#### コメント 5 by snicoll

**作成日**: 2022-07-04

> Cross reference these new methods from the Javadoc in the existing registerJdkProxy() methods in spring-core to make the AOP specific support discoverable via the core user API.

If that is so important this was discussed, I'd like us to review `RuntimeHintsUtils#registerAnnotation`.

#### コメント 6 by sbrannen

**作成日**: 2022-07-05

> If that is so important this was discussed, I'd like us to review `RuntimeHintsUtils#registerAnnotation`.

Do you mean you'd like to cross reference `RuntimeHintsUtils` from `ProxyHints`?

If so, I agree that that's a good idea.

In any case, feel free to bring it up in the team or open an issue to discuss what you'd like to review.

#### コメント 7 by sbrannen

**作成日**: 2022-07-11

Reopening to reduce the scope of this feature to `Class` references.

---

## Issue #28754: Add native image support for WebSocket STOMP messaging

**状態**: closed | **作成者**: mhalbritter | **作成日**: 2022-07-04

**ラベル**: in: web, type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28754

**関連リンク**:
- Commits:
  - [938b05b](https://github.com/spring-projects/spring-framework/commit/938b05bd322f51d70204f74939a4d01cc687b2c0)
  - [bcb6f13](https://github.com/spring-projects/spring-framework/commit/bcb6f13fc4e0b38e9e9739f9709f621963cca5bd)

### 内容

The native sample `websocket-stomp` works with AOT mode, but not in native image.

I identified at least two problems:

* The return and parameter values from `GreetingController` are not registered in `reflect-config.json`
* Even if I manually add runtime hints, the handler methods are not called when a STOMP message arrives at the server

---

## Issue #28760: Deprecate convention-based annotation attribute overrides in favor of `@AliasFor`

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-07-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28760

**関連リンク**:
- Commits:
  - [e09cdcd](https://github.com/spring-projects/spring-framework/commit/e09cdcd92077e1c44772fe3d9fa1e1e638f59fe0)
  - [73d92d6](https://github.com/spring-projects/spring-framework/commit/73d92d66b938a5ff9080442396bed13c421d1f8f)
  - [0beee7d](https://github.com/spring-projects/spring-framework/commit/0beee7dc69f157a5cfd478c63abdc4b68ed6cc7e)
  - [d7b45b7](https://github.com/spring-projects/spring-framework/commit/d7b45b7c8ee7bf9fc780d5512005a273846d9ee1)
  - [0e861af](https://github.com/spring-projects/spring-framework/commit/0e861af0502e7dc7622f574e496652013c3f08a6)
  - [a68f5b1](https://github.com/spring-projects/spring-framework/commit/a68f5b1674635bf3de79435f83c3d8f4b7ae9098)

### 内容

## Overview

**Implicit** convention-based annotation attribute overrides have been supported for a long time; however, Spring Framework 4.2 introduced support for **explicit** annotation attribute overrides via `@AliasFor`.

Since explicit overrides are favorable to implicit overrides, and since the support for convention-based overrides increases the complexity of Spring's annotation search algorithms, we will deprecate convention-based overrides in 6.0 and remove the support in 7.0 (see #28761).

## Deliverables

- [x] in 6.0, whenever a convention-based override is detected, log a warning stating the reasons mentioned above


---

## Issue #28766: Upgrade to Reactor 2022.0.0-M4

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-07-06

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/28766

**関連リンク**:
- Commits:
  - [0938909](https://github.com/spring-projects/spring-framework/commit/0938909cd91772dd6de0387107ebfeef853642e0)
  - [7f0abb7](https://github.com/spring-projects/spring-framework/commit/7f0abb718b0d596f58e127df3e83b59c11e43289)

### 内容

_本文なし_

### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-07-13

This was done in 7055ddb489d18c4940c5685eca8ea72f29c58679.

---

## Issue #28772: Provide SerializationHintsPredicates in RuntimeHintsPredicates

**状態**: closed | **作成者**: marcusdacoregio | **作成日**: 2022-07-07

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28772

**関連リンク**:
- Commits:
  - [ee6a4e7](https://github.com/spring-projects/spring-framework/commit/ee6a4e7c1e3245bd758c1a553f21ae8b3a8a6dbc)

### 内容

It would be nice to have the `SerializationHintsPredicates` in `RuntimeHintsPredicates` as we have for `reflections`, `resource` and `proxies`.

I've created one myself for now: 
```java
public class SerializationHintsPredicates {

	public TypeHintPredicate onType(TypeReference typeReference) {
		Assert.notNull(typeReference, "'typeReference' should not be null");
		return new TypeHintPredicate(typeReference);
	}

	public TypeHintPredicate onType(Class<?> type) {
		Assert.notNull(type, "'type' should not be null");
		return new TypeHintPredicate(TypeReference.of(type));
	}

	public static class TypeHintPredicate implements Predicate<RuntimeHints> {

		private final TypeReference type;

		TypeHintPredicate(TypeReference type) {
			this.type = type;
		}

		@Override
		public boolean test(RuntimeHints hints) {
			return hints.serialization().javaSerialization().anyMatch((hint) -> hint.getType().equals(this.type));
		}

	}

}
```

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-07-11

Good catch @marcusdacoregio, thanks!

---

## Issue #28773: AnnotationTypeMapping tracks @AliasFor mappings as convention-based

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-07-07

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28773

**関連リンク**:
- Commits:
  - [81acbe7](https://github.com/spring-projects/spring-framework/commit/81acbe7e2f2e2fc7afd83f9759e6ad8470766de1)

### 内容

While working on #28760, I noticed that `AnnotationTypeMapping.addConventionMappings()` actually adds convention-based mappings that it should not.

For example, in certain circumstances an explicit annotation attribute override configured via `@AliasFor` can be mapped as convention-based.

Although this does not _appear_ to cause negative side effects (other than unnecessary processing), this is technically a bug that should be addressed.

However, since there may be unknown use cases that somehow rely on the behavior of this bug, I currently only intend to apply the fix to 6.0.

---

## Issue #28784: Upgrade to Kotlin 1.7.10

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-07-11

**ラベル**: type: dependency-upgrade, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28784

**関連リンク**:
- Commits:
  - [4104ea7](https://github.com/spring-projects/spring-framework/commit/4104ea7c1cbb5509664729a96b59f06d79bd5291)

### 内容

_本文なし_

---

## Issue #28786: Reject JDK proxy hint registration for sealed interfaces

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-07-11

**ラベル**: type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28786

**関連リンク**:
- Commits:
  - [656dc54](https://github.com/spring-projects/spring-framework/commit/656dc549b16900f93dbbdce77c6b07cb4fccaa7e)

### 内容

_本文なし_

---

## Issue #28787: Upgrade client support to R2DBC 1.0

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-07-11

**ラベル**: in: data, type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/28787

**関連リンク**:
- Commits:
  - [7055ddb](https://github.com/spring-projects/spring-framework/commit/7055ddb489d18c4940c5685eca8ea72f29c58679)
  - [9d1dfc7](https://github.com/spring-projects/spring-framework/commit/9d1dfc733d911e1a6aea7d8bb83fb6bd40f0168d)

### 内容

This is a follow up to #28059.

Since R2DBC 1.0 has been released, we should upgrade and ensure compatibility with 1.0 for Spring Framework 6.0.

For example, `io.r2dbc.spi.Result.getRowsUpdated()` returned `Publisher<Integer>` in 0.9 and apparently returns `Publisher<Long>` in 1.0.

---

## Issue #28799: Move RuntimeHints predicates to a dedicated package

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-07-12

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/28799

**関連リンク**:
- Commits:
  - [54a3f66](https://github.com/spring-projects/spring-framework/commit/54a3f66d1d8ed97cf7d8449f70f579712b27afb9)
  - [40c8b7c](https://github.com/spring-projects/spring-framework/commit/40c8b7c59f54e67a9279d49bbf0f35db77c45843)

### 内容

The predicates support deserves to be in its own package. This will also avoid `.hint` to be too flat.

---

## Issue #28801: Name RuntimeHintsRegistrar implementations consistently

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-07-12

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28801

**関連リンク**:
- Commits:
  - [2c92d7d](https://github.com/spring-projects/spring-framework/commit/2c92d7da8f8feace44fcbef1578e80b341109b41)

### 内容

We'd like to use `RuntimeHints` as suffix for `RuntimeHintsRegistrar` implementations (to follow the naming of `@ImportRuntimeHints`), and because it reads better than a `RuntimeHintsRegistrar` suffix. 

This issue is about harmonizing the names we have at the moment.

---

## Issue #28813: `HibernateTransactionManager` compatibility with Hibernate 6.0/6.1

**状態**: closed | **作成者**: odrotbohm | **作成日**: 2022-07-13

**ラベル**: in: data, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28813

**関連リンク**:
- Commits:
  - [7a04206](https://github.com/spring-projects/spring-framework/commit/7a042062f59deb596e9208ecafebd4a08139dbf0)

### 内容

We [already fixed](https://github.com/spring-projects/spring-framework/issues/28007) references to API removed in Hibernate 6 for `HibernateJpaVendorAdapter` but apparently `HibernateTransactionManager` also refers to the [very same API](https://github.com/spring-projects/spring-framework/blob/0b5c5dbc313fcd61abdf8e0f3b68a6a8fbbc0f98/spring-orm/src/main/java/org/springframework/orm/hibernate5/HibernateTransactionManager.java#L565).

### コメント

#### コメント 1 by jhoeller

**作成日**: 2022-07-13

To be clear, `HibernateTransactionManager` is part of our legacy `orm.hibernate5` package and should be replaced with `JpaTransactionManager` plus `HibernateJpaDialect` / `HibernateJpaVendorAdapter` with `LocalContainerEntityManagerFactoryBean` since we officially only support Hibernate 6.x via JPA.

That said, it turns out that we can make `HibernateTransactionManager` compatible with Hibernate 6.0/6.1 with a few minor tweaks where we're calling Hibernate 5.6's internal connection handling mechanisms instead of the public API (the latter is gone in Hibernate 6.0 but the internal coordinator SPI is still the same). We won't be able to guarantee compatibility with Hibernate 6.x going forward, but for a start this allows usage of `LocalSessionFactoryBean` and `HibernateTransactionManager` for transitional purposes when upgrading from Hibernate 5.5/5.6 to 6.0/6.1.

---

## Issue #28816: Guard against NPE in PathMatchConfigurer

**状態**: closed | **作成者**: mbhave | **作成日**: 2022-07-13

**ラベル**: type: bug

**URL**: https://github.com/spring-projects/spring-framework/issues/28816

**関連リンク**:
- Commits:
  - [4c08c27](https://github.com/spring-projects/spring-framework/commit/4c08c276f79e00f66d56344b9aca901f1b326e0c)

### 内容

[This](https://github.com/spring-projects/spring-framework/blob/7a042062f59deb596e9208ecafebd4a08139dbf0/spring-webmvc/src/main/java/org/springframework/web/servlet/config/annotation/PathMatchConfigurer.java#L156) would cause an NPE if `suffixPatternMatch` is `null`.

```java
Caused by: java.lang.NullPointerException: Cannot invoke "java.lang.Boolean.booleanValue()" because "suffixPatternMatch" is null
	at org.springframework.web.servlet.config.annotation.PathMatchConfigurer.setUseSuffixPatternMatch(PathMatchConfigurer.java:156) ~[spring-webmvc-6.0.0-SNAPSHOT.jar:6.0.0-SNAPSHOT]
	at com.example.demo.PathMatchingThingyApplication.configurePathMatch(PathMatchingThingyApplication.java:14) ~[main/:na]
	at org.springframework.web.servlet.config.annotation.WebMvcConfigurerComposite.configurePathMatch(WebMvcConfigurerComposite.java:53) ~[spring-webmvc-6.0.0-SNAPSHOT.jar:6.0.0-SNAPSHOT]
	at org.springframework.web.servlet.config.annotation.DelegatingWebMvcConfiguration.configurePathMatch(DelegatingWebMvcConfiguration.java:58) ~[spring-webmvc-6.0.0-SNAPSHOT.jar:6.0.0-SNAPSHOT]
	at org.springframework.web.servlet.config.annotation.WebMvcConfigurationSupport.getPathMatchConfigurer(WebMvcConfigurationSupport.java:388) ~[spring-webmvc-6.0.0-SNAPSHOT.jar:6.0.0-SNAPSHOT]
	at org.springframework.web.servlet.config.annotation.WebMvcConfigurationSupport.mvcResourceUrlProvider(WebMvcConfigurationSupport.java:614) ~[spring-webmvc-6.0.0-SNAPSHOT.jar:6.0.0-SNAPSHOT]
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method) ~[na:na]
	at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77) ~[na:na]
	at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43) ~[na:na]
	at java.base/java.lang.reflect.Method.invoke(Method.java:568) ~[na:na]
	at org.springframework.beans.factory.support.SimpleInstantiationStrategy.instantiate(SimpleInstantiationStrategy.java:130) ~[spring-beans-6.0.0-SNAPSHOT.jar:6.0.0-SNAPSHOT]
	... 34 common frames omitted
```

While the API doesn't expect nulls, it's worth investigating whether switching to `boolean` or adding an `Assert` would be possible. Similar case for `registeredSuffixPatternMatch `.

---

