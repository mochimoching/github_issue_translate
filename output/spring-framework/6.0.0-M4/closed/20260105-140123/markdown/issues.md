# Spring Framework GitHub Issues

取得日時: 2026年01月05日 14:01:23

取得件数: 41件

---

## Issue #14023: Introduce removeApplicationListener in ConfigurableApplicationContext

**状態**: closed | **作成者**: spring-projects-issues | **作成日**: 2012-05-08

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/14023

**関連リンク**:
- Commits:
  - [f8c4071](https://github.com/spring-projects/spring-framework/commit/f8c4071f7302a7d6f7e02e877d3c815ad6d81e4f)

### 内容

**[Archie Cobbs](https://jira.spring.io/secure/ViewProfile.jspa?name=archie172)** opened **[SPR-9387](https://jira.spring.io/browse/SPR-9387?redirect=false)** and commented

I have some object which need to receive some `ApplicationEvents` that are sent around in my application.

However, these objects have a lifecycle that does not match with the lifecycle of normal beans in the application context (their lifecycle is shorter).

Therefore, I have these beans marked `@Configurable`, and they are `ApplicationContextAware` so they can get a reference to the application context (which is assumed to be a `ConfigurableApplicationContext`.

Then, when they "start" they register as listeners for application events via `ConfigurableApplicationContext.addApplicationListener()`. However, when they "stop" there is no way for them to unregister themselves as listeners, because there is no corresponding method `ConfigurableApplicationContext.removeApplicationListener()`.

So this request is simply to add `ConfigurableApplicationContext.removeApplicationListener()`.

If there is some more elegant way to do what I'm trying to do please let me know. But just from the face of it, it seems weirdly asymmetrical to have a public `addFooListener()` method without a corresponding `removeFooListener()` method.

Thanks.

---

**Affects:** 3.1.1

**Issue Links:**
- #14027 Support DisposableBean on prototype and `@Configurable` beans using weak references

1 votes, 4 watchers


### コメント

#### コメント 1 by spring-projects-issues

**作成日**: 2012-05-09

**[Archie Cobbs](https://jira.spring.io/secure/ViewProfile.jspa?name=archie172)** commented

Additional info: even though these `@Configurable` beans implement `ApplicationListener`, they are not automatically registered with the event multicaster, instead triggering this warning in `AbstractApplicationContext.java`:

```
Boolean flag = this.singletonNames.get(beanName);
if (Boolean.TRUE.equals(flag)) {
    // singleton bean (top-level or inner): register on the fly
    addApplicationListener((ApplicationListener<?>) bean);
}
else if (flag == null) {
    if (logger.isWarnEnabled() && !containsBean(beanName)) {
        // inner bean with other scope - can't reliably process events
        logger.warn("Inner bean '" + beanName + "' implements ApplicationListener interface " +
                "but is not reachable for event multicasting by its containing ApplicationContext " +
                "because it does not have singleton scope. Only top-level listener beans are allowed " +
                "to be of non-singleton scope.");
    }
    this.singletonNames.put(beanName, Boolean.FALSE);
}
```

That is why they have to be manually registered as listeners.

So this is kind-of a Catch-22 situation.

By the way, this issue relates to #9922, which is marked Resolved, but is it really? It seems like the code above means that it's not really resolved.

Also: I accidentally set the Component to SpringAOP instead of SpringCore, but don't have permission to edit it... sorry.


#### コメント 2 by spring-projects-issues

**作成日**: 2012-05-31

**[Archie Cobbs](https://jira.spring.io/secure/ViewProfile.jspa?name=archie172)** commented

Related to this. There is an opportunity for a little API cleanup:
* Why not let `ConfigurableApplicationContext` extend `ApplicationEventMulticaster`? Right now there are two separate interfaces declaring an `addApplicationListener()` method.
* `ApplicationEventMulticaster` still needs some genericization, i.e., methods should take parameters of type `ApplicationListener<?>` instead of `ApplicationListener`
* We have both `ApplicationEventPublisher.publishEvent()` and `ApplicationEventMulticaster.multicastEvent()`, both doing the same thing. Seems like these methods should have the same name, and `ApplicationEventMulticaster` should just extend `ApplicationEventPublisher`.



#### コメント 3 by spring-projects-issues

**作成日**: 2019-01-12

Bulk closing outdated, unresolved issues. Please, reopen if still relevant.

#### コメント 4 by archiecobbs

**作成日**: 2019-01-15

> Bulk closing outdated, unresolved issues. Please, reopen if still relevant.

... except Github won't let me reopen it...

#### コメント 5 by sbrannen

**作成日**: 2021-02-10

This feature was also considered in conjunction with the initial implementation for #25616.

#### コメント 6 by rstoyanchev

**作成日**: 2022-03-29

Scheduling for 6.0 with a chance to explore a backport to 5.3.x.

#### コメント 7 by archiecobbs

**作成日**: 2022-05-06

Woo-hoo! Just in time for it's 10th birthday on Sunday :)

Seriously, this is why I love Spring - most projects would never bother to fix a 10 year old minor feature request.

---

## Issue #27506: AntPathMatcher matches path with trailing slash differently if '**' is present in the pattern

**状態**: closed | **作成者**: aomader | **作成日**: 2021-10-01

**ラベル**: in: web, type: bug, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/27506

**関連リンク**:
- Commits:
  - [705bf78](https://github.com/spring-projects/spring-framework/commit/705bf7810406358aa42e091f029e7bfa60cbf3d5)

### 内容

I'm curious why `AntPathMatcher` matches a path with a trailing slash differently if the pattern contains a `**` pattern. See the following example:

```
AntPathMatcher matcher = new AntPathMatcher();

matcher.match("/en", "/en/") == false // does not match
matcher.match("/*/en", "/en/foo/") == false // does not match
matcher.match("/**/foo", "/en/foo/") == true // does match
```

Could someone enlighten me why `AntPathMatcher` behaves this way?

### コメント

#### コメント 1 by bclozel

**作成日**: 2021-10-01

Is there a typo in your code snippet?

```
// does not match because the pattern doesn't have a trailing slash and the path has one
matcher.match("/en", "/en/")
// does not match because the pattern ends with "/en" and the path ends with "/foo/"
matcher.match("/*/en", "/en/foo/")
// this is problematic
matcher.match("/**/foo", "/en/foo/") == true // does match
```

I've tested the following combinations and it looks like there is an inconsistency between `*` and `**` when it comes to matching trailing slashes.

```
assertThat(pathMatcher.match("/*/foo", "/en/foo")).isTrue();
assertThat(pathMatcher.match("/*/foo", "/en/foo/")).isFalse();
assertThat(pathMatcher.match("/**/foo", "/en/foo")).isTrue();
assertThat(pathMatcher.match("/**/foo", "/en/foo/")).isFalse(); // fails
```

I've found a fix for this issue that doesn't break any test in our test suite, but `AntPathMatcher` has a long history of subtle behavior and lots of people relying on it.

Using `**` within patterns and trailing slashes are very likely in web applications using `AntPathMatcher`. There is a trailing slash matching option in Spring MVC but applications might still rely on this behavior, so I'm not tempted to fix this in the 5.3.x branch.

On the other hand, I think that using `AntPathMatcher` as a matcher for request patterns in Spring MVC might be retired in Spring Framework 6.0. In the 6.0.x timeline we can consider several options for `AntPathMatcher`:

1. keeping it around as it is and fixing small issues like this one
2. reworking it to only target file patterns use cases (and not URL path patterns which is now `PathPatternParser`'s job)
3. or retiring it completely

In any case, this needs to be discussed within the Spring Framework team.

Did you notice this issue in a Spring MVC application while debugging the problem, or `AntPathMatcher` for some other use case?

#### コメント 2 by aomader

**作成日**: 2021-10-05

Regarding your first question, no, I cannot see a typo. The last case is obviously the problematic one and the reason I created this issue.

Exactly, I came across this "subtle behavior" when working with Spring MVC and Spring Security. The latter I find somewhat problematic with regards to "sublte behavior"...

---

## Issue #27633: Automatically clean up multipart temp files

**状態**: closed | **作成者**: poutsma | **作成日**: 2021-11-02

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27633

**関連リンク**:
- Commits:
  - [192f2be](https://github.com/spring-projects/spring-framework/commit/192f2becf616642de23b43e03ffb3cdf5c5f4493)

### 内容

The `DefaultPartHttpMessageReader` creates temp files that are never deleted. There should be an option to delete these files after the corresponding request was handled.

Related to #27613, the resolution of which introduced a `Part::delete` method to explicitly remove the temp file. This issue  focusses on automatically removing these temp files.



### コメント

#### コメント 1 by vovaspk

**作成日**: 2021-11-03

@poutsma hi, do you know if it is possible to disable creating temp file? when for example i know i will be receiving files around 10mb, and i want to save them right to the storage from memory, without creating temp file and then copying

#### コメント 2 by poutsma

**作成日**: 2021-11-03

@vovaspk You will need to change the `maxInMemorySize` for the `DefaultPartHttpMessageReader` by using the `ServerCodecConfigurer`, see https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#webflux-config-message-codecs

#### コメント 3 by vovaspk

**作成日**: 2021-11-03

Thank you very much!

---

## Issue #27955: Support AOT registration of Spring Factories

**状態**: closed | **作成者**: bclozel | **作成日**: 2022-01-19

**ラベル**: in: core, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/27955

**関連リンク**:
- Commits:
  - [2961426](https://github.com/spring-projects/spring-framework/commit/2961426d8ad256983ffe1445acd4cbfaab4fd5db)
  - [267b914](https://github.com/spring-projects/spring-framework/commit/267b91486efd409a4f095be4a87db2c45fee1322)
  - [6a67b4a](https://github.com/spring-projects/spring-framework/commit/6a67b4a2aa22da5a252b4fe5e9d5fd5fe494e1c1)
  - [e6c0152](https://github.com/spring-projects/spring-framework/commit/e6c0152916806905dcdf106798de0b475391f830)

### 内容

As seen in #27753, `SpringFactoriesLoader` is currently supported in Spring Native through subtitutions and complex AOT processors.

We'd like to improve `SpringFactoriesLoader` and allow static registration of Spring Factories, something our AOT processing could leverage and call early during application startup. Once a Factory type is registered with entries, `SpringFactoriesLoader` should use this entry as a pre-warmed cache and never look for additional entries in `spring.factories` files, skipping all the resource loading and reflection operations.

Instead of registering String instances as entries, this new contract might take `Supplier` instances instead, maybe mirroring the new contract to be added in #27954

---

## Issue #28006: Introduce token-based consumption of  multipart requests in WebFlux

**状態**: closed | **作成者**: poutsma | **作成日**: 2022-02-04

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28006

**関連リンク**:
- Commits:
  - [be7fa3a](https://github.com/spring-projects/spring-framework/commit/be7fa3aaa879cfb44fc976be7331caf5479a943f)
  - [e29bc3d](https://github.com/spring-projects/spring-framework/commit/e29bc3db7c943cf75bd1b25c661c53f372304f7f)
  - [639c047](https://github.com/spring-projects/spring-framework/commit/639c047f2f8e9c99b7b6f7dbe53462c33c269225)

### 内容

In version 5.3, Spring Framework introduced the `DefaultPartHttpMessageReader` as a fully reactive way to handle multipart upload requests. One of the features of this message reader is [streaming mode](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/http/codec/multipart/DefaultPartHttpMessageReader.html#setStreaming-boolean-), where the contents of the uploaded parts is not stored in memory or on disk, but directly passed on to the subscriber (in the form of [DataBuffers](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/http/codec/multipart/Part.html#content--) ). This feature is particularly useful for server proxies, where the controller passes on the data buffers to another service, for instance by using `WebClient`.

However, there is a problem in the way streaming mode deals with back pressure. In streams produces by other `HttpMessageReader`s and codecs, there is a clear relationship between the requests made by the subscriber and the request made against the incoming buffer stream (for instance, the `ByteBufferDecoder` creates one `ByteBuffer` for each incoming `DataBuffer`). When `DefaultPartHttpMessageReader` is used in streaming mode, there is no such relationship, because each `Part` produced can consists of multiple databuffers. Effectively, there are two kinds of back pressure in streaming mode:

1. the back pressure of the `Part` elements, i.e. the 'outer' flux
2. the back pressure of the `DataBuffer` contents of each part, i.e. the 'inner' flux.
 
There are several scenarios to consider:

* What should happen when a request for a second part comes in, while the contents of the first has not been consumed yet?
* What should happen when the inner flux is canceled, while the outer flux is not?
* What should happen when `flatMap` is used on the `Part` stream? 
* How should [prefetch be used](https://github.com/spring-projects/spring-framework/issues/27743)?
* etc. etc.

Though I am sure we can come up with answers to these questions, the fact remains that in streaming scenarios, representing multipart data as `Flux<Part>` where each part contains a `Flux<DataBuffer>` has inherent difficulties with back pressure. Instead, we should introduce an alternative way to consume multipart data, a better fit for streaming scenarios. 

### Part tokens

Instead `Part` elements, the multipart upload is represented by a stream of part tokens. Each part in the multipart request is represented by a **header** token that contains the part headers, followed by one or more **body** tokens with data buffers containing the part body. Subsequent parts will result in another header token, followed by more body tokens, and so on.

For instance, a multipart message with a form field and a file will produce the following tokens:

1. header token containing the headers of the form field part
2. a body token containing the form field value
3. header token containing the headers of the file part
4. multiple body tokens containing buffers with the contents of the file

Using part tokens, there is a direct relationship between back pressure of the the token subscriber and that of the buffer input. In the case of body tokens, this even is a 1-on-1 relationship.

For instance, here is a typical controller method that splits the tokens into multiples fluxes that start with a header token, so that each inner flux contains the tokens of one part. The headers from said token can then be used if necessary, and the remaining body tokens can be used as well.

```java
@PostMapping("/tokens")
Flux<String> tokens(@RequestBody Flux<PartToken> tokens) {
	return tokens
			.windowUntil(token -> token instanceof PartToken.Headers, true)  // Flux<Flux<PartToken>>
			.concatMap(t -> t.switchOnFirst((signal, partTokens) -> {
				if (signal.hasValue()) {
					PartToken.Headers headersToken = (PartToken.Headers) signal.get();
					HttpHeaders headers = headersToken.headers();
					// Use info in headers if necessary
					Flux<DataBuffer> bodyBuffers = partTokens
							.filter(token -> token instanceof PartToken.Body)
							.cast(PartToken.Body.class)
							.map(PartToken.Body::buffer);
					// Send body buffers to other service
					return Mono.empty();
				}
				else {
					return releaseBody(partTokens)
							.then(Mono.empty());
				}
			}));

}
```


### コメント

#### コメント 1 by poutsma

**作成日**: 2022-02-04

As part of this effort, we would also deprecate the current streaming support in `DefaultPartHttpMessageReader`.

#### コメント 2 by poutsma

**作成日**: 2022-02-09

After considering the way (Reactor) Netty deals with multipart streaming, we have come up with an alternative to the token-based approach described above, so that headers and body contents are merged into one `PartData` object.

### Part Data objects

In this design, each part in a multipart HTTP message produces at least one `PartData` object containing both headers and a `DataBuffer` with data of the part. If the part is large enough to be split across multiple buffers (i.e. a file upload), the first `PartData` will be followed by subsequent objects. The final `PartData` for a particular part will have its
`isLast` property set to true.

For instance, a multipart message with a form field and a file will produce the following tokens:

1. a data object containing the headers and data of the form field part. `isLast` is true.
2. a data object containing header token containing headers and first buffer of data of the file part. `isLast` is false.
3. multiple data object tokens containing headers and buffers with the subsequent contents of the file
4. a data object containing header token containing headers and final buffer of data of the file part. `isLast` is true.

#### コメント 3 by djouvin

**作成日**: 2022-02-12

The second approach with a unified `PartData` (we could call it alternatively `PartFragment`) seems indeed more appealing and polyvalent. And it is simpler in design, thus probably more robust.

However, I think there is a way to still have a composite approach with an outer `Flux<Part>` (producing a `Flux<DataBuffer>` for each part's content), while still maintaining a correct relationship between the demand and the incoming data buffers, at least for the inner flux (part content).
For the outer flux, quantitative demand is not really useful anyway since parts may have completely different sizes. The `Flux<Part>` should work with `concatMap` but also with `flatMap` : the difference is that with `concatMap` the next part consumption would wait the whole previous part content pipeline to complete, whereas with `flatMap`, it is sufficient that the part content is fully produced to the next operator, but the content can be "in transit / in processing" in the content processing pipeline while the second part is produced (thus parallelizing a bit more the processing).

The conditions for this composite approach to work is to maintain the following predicates true:
- part demand and part content demand must not be mixed and must be processed differently
- a part content flux has to be subscribed *before* any other part is processed
  - the corollary is that the next part must not be delivered by the producer without the consumer having fully consumed, or explicitly cancelled the previous part's content flux : the part should thus expose an explicit `cancel` or `dispose` method (for example, by implementing the `Disposable` interface). We are bending here a little the reactive streams contract semantics (part content are in a way "pre-subscribed"), but there is no other way to ensure parts are not skipped unintentionally by a prefetching operator
  - prefetch should not be used for part consumption on the outer flux, as it will never be honored by the producer, but it can be used for part content consumption on the inner flux (which behaves as a regular `Flux<DataBuffer>`)
  - the next part should be delivered to the outer flux consumer :
    - when the previous part's content delivery is complete,
    - or when all subscriptions to this part content are cancelled,
    - or when the part itself is cancelled or disposed,
  - and of course part demand is still there and the outer flux itself is not cancelled
- part content delivery should honore content demand as any data buffer flux would, until of course the end of the part is encountered (then the content flux is completed and the potentially remaining prefetched data buffer are retained by the producer)

I agree that the composite approach implementation is more complex, and I am not sure it is always interesting to have an outer `Flux<Part>`, because most of the time an HTTP stream has only one, or just a few, parts (so viewing parts as a `Flux` is not a must). It does however fit well with `flatMap` and `concatMap` operators.
And, it can be build on the `PartData` approach too (as it is now with the `PartToken` generator) : consumers would have the choice to consume either directly a `Flux<PartData>` or a `Flux<Part>` wrapping that `Flux<PartData>`.

#### コメント 4 by jomach

**作成日**: 2022-03-15

this is related with https://github.com/spring-projects/spring-framework/issues/27743 right ?

#### コメント 5 by poutsma

**作成日**: 2022-04-20

This feature is now in `main`, will be in Spring Framework 6.0 M4 when it comes out on May 11th. I would really appreciate feedback before 6.0 RC is released.

There is no reference documentation as of yet, it will be written when the RC approaches, but for now there is a substantial amount of Javadoc on the main type: `PartEvent`, see [here](https://docs.spring.io/spring-framework/docs/6.0.0-SNAPSHOT/javadoc-api/org/springframework/http/codec/multipart/PartEvent.html).

Note that I changed the name of this type from `PartData` to `PartEvent`, as I think that more clearly describes the intent of the type.

#### コメント 6 by poutsma

**作成日**: 2022-04-20

@djouvin 

> The conditions for this composite approach to work is to maintain the following predicates true:
> 
> * part demand and part content demand must not be mixed and must be processed differently
> * a part content flux has to be subscribed _before_ any other part is processed
>   
>   * the corollary is that the next part must not be delivered by the producer without the consumer having fully consumed, or explicitly cancelled the previous part's content flux : the part should thus expose an explicit `cancel` or `dispose` method (for example, by implementing the `Disposable` interface). We are bending here a little the reactive streams contract semantics (part content are in a way "pre-subscribed"), but there is no other way to ensure parts are not skipped unintentionally by a prefetching operator
>   * prefetch should not be used for part consumption on the outer flux, as it will never be honored by the producer, but it can be used for part content consumption on the inner flux (which behaves as a regular `Flux<DataBuffer>`)
>   * the next part should be delivered to the outer flux consumer :
>     
>     * when the previous part's content delivery is complete,
>     * or when all subscriptions to this part content are cancelled,
>     * or when the part itself is cancelled or disposed,
>   * and of course part demand is still there and the outer flux itself is not cancelled
> * part content delivery should honore content demand as any data buffer flux would, until of course the end of the part is encountered (then the content flux is completed and the potentially remaining prefetched data buffer are retained by the producer)

While the user might be able to limit their usage of operators on the `Flux<Part>` we provide, it is impossible to make the same guarantee when that flux is passed on to another library or framework. As a consequence, things can unexpectedly break when they worked perfectly fine before. 

> I agree that the composite approach implementation is more complex, and I am not sure it is always interesting to have an outer `Flux<Part>`, because most of the time an HTTP stream has only one, or just a few, parts (so viewing parts as a `Flux` is not a must). It does however fit well with `flatMap` and `concatMap` operators. And, it can be build on the `PartData` approach too (as it is now with the `PartToken` generator) : consumers would have the choice to consume either directly a `Flux<PartData>` or a `Flux<Part>` wrapping that `Flux<PartData>`.

I will try to refactor the `PartGenerator` to use the functionality for this issue, and will let you know how that proceeds.



#### コメント 7 by jomach

**作成日**: 2022-04-20

Would be great if you could provide a working example of this :) thx and great work !

#### コメント 8 by poutsma

**作成日**: 2022-05-10

> Would be great if you could provide a working example of this :) thx and great work !

There is some sample code available on the [PartEvent Javadoc](https://docs.spring.io/spring-framework/docs/6.0.0-SNAPSHOT/javadoc-api/org/springframework/http/codec/multipart/PartEvent.html).

---

## Issue #28024: MediaType parameters in the "consumes" condition of `@RequestMapping` are not considered for matching

**状態**: closed | **作成者**: thake | **作成日**: 2022-02-10

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28024

### 内容

This issue was opened based on the discussion in #27999.

Given the following controller:
```kotlin
@RestController
@RequestMapping("/hal-documents")
class MyController {
    @PostMapping(
        consumes = ["""application/hal+json;profile="my-resource-v1""""],
        produces = ["""application/hal+json;profile="my-resource-v1""""]
    )
    fun postVersion1(@RequestBody request : String) = "version-1"

    @PostMapping(
        consumes = ["""application/hal+json;profile="my-resource-v2""""],
        produces = ["""application/hal+json;profile="my-resource-v2""""]
    )
    fun postVersion2(@RequestBody request : String) = "version-2";
}
```
A request that provides a request body with the content type `application/hal+json;profile="my-resource-v2"` is being routed to `postVersion1` but should be routed to `postVersion2`.

Even worse, if the `consumes` media type only differs in media type parameters and the handler methods can't be ranked by `produces` an `Ambiguous handler methods mapped for ...` error will be thrown leading to a 500er. 

<details><summary>Example</summary>
<p>
Controller:

```kotlin
@RestController
@RequestMapping("/hal-documents")
class MyController {
    @PostMapping(
        consumes = ["""application/hal+json;profile="my-resource-v1""""]
    )
    fun postVersion1(@RequestBody request : String) = "version-1"

    @PostMapping(
        consumes = ["""application/hal+json;profile="my-resource-v2""""]
    )
    fun postVersion2(@RequestBody request : String) = "version-2";
}
```
Request:
```http
POST http://localhost:8080/hal-documents
Content-Type: application/hal+json;profile="my-resource-v2"

{
  "my content" : "blub"
}
```
Response:
```http
HTTP/1.1 500 
Content-Type: application/json
Transfer-Encoding: chunked
Date: Thu, 10 Feb 2022 06:51:58 GMT
Connection: close

{
  "timestamp": "2022-02-10T06:51:58.921+00:00",
  "status": 500,
  "error": "Internal Server Error",
  "trace": "java.lang.IllegalStateException: Ambiguous handler methods mapped for '/hal-documents': {...}",
  "path": "/hal-documents"
}
```
</p>
</details>

Looking into the code, it seems like `consumes` and `produces` are treated differently in `ProducesRequestCondition` and `ConsumesRequestCondition` when it comes to media type parameters.

**Affects:** 5.3.15


### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-02-14

We can align `consumes` with the `produces` condition, along the lines of 8dc535c15c15a71ce29bc21a45e9daeb064dd35e, such that if a media type parameter is explicitly declared in the mapping **and** the same parameter is also present in the `Content-Type` header, then the two must match. 

#### コメント 2 by rstoyanchev

**作成日**: 2022-05-11

Fixed in f0e23b66f32055b6ad9515955d9dd2902d38366e but commit message references a different issue by accident.

---

## Issue #28036: Upgrade to Kotlin 1.6.20

**状態**: closed | **作成者**: bclozel | **作成日**: 2022-02-11

**ラベル**: type: dependency-upgrade, theme: kotlin

**URL**: https://github.com/spring-projects/spring-framework/issues/28036

**関連リンク**:
- Commits:
  - [e009054](https://github.com/spring-projects/spring-framework/commit/e0090545f5029dc1cba2c984ce86e428dbee5991)

### 内容

As a follow-up of #27814.

---

## Issue #28080: Remove TYPE_HIERARCHY_AND_ENCLOSING_CLASSES search strategy for MergedAnnotations

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-02-19

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28080

**関連リンク**:
- Commits:
  - [1e1256a](https://github.com/spring-projects/spring-framework/commit/1e1256aad55b2277d7346f5783fa4fae59302802)
  - [4dfead3](https://github.com/spring-projects/spring-framework/commit/4dfead3ab868351aaa351e02332721deca7646f8)
  - [42a61b9](https://github.com/spring-projects/spring-framework/commit/42a61b966b7d38f073f65b1c1cacbd92ac0b9c2c)
  - [133dd1a](https://github.com/spring-projects/spring-framework/commit/133dd1a41810f782b111273471eaf6b429f1be8c)
  - [c23edf7](https://github.com/spring-projects/spring-framework/commit/c23edf7da6c403eeedb862e02b9a7293cfba38a1)
  - [3a6828f](https://github.com/spring-projects/spring-framework/commit/3a6828f61340ae3d75b706c8e1c721109a05d808)
  - [819d425](https://github.com/spring-projects/spring-framework/commit/819d4256b7984fdec58840a56b82e411bc53c9c9)
  - [b70b6e7](https://github.com/spring-projects/spring-framework/commit/b70b6e79164748df8c73876e55b656f22ff6e3e4)
  - [fc8f31c](https://github.com/spring-projects/spring-framework/commit/fc8f31ccfbecd2179d7ce216a5a3521f13397c05)
  - [317c989](https://github.com/spring-projects/spring-framework/commit/317c98939d7079467947b02cf8a1d70ed2ba51da)
  - [ae51ca9](https://github.com/spring-projects/spring-framework/commit/ae51ca9bca396a7ab459c33cde91aff787643805)

### 内容

## Overview

Since #28207 has introduced support for providing a `Predicate<Class<?>>` that allows for complete control over the "enclosing classes" aspect of the search algorithm in `MergedAnnotations`, the deprecated `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` search strategy can now be completely removed.

## Related Issues

- #28079
- #28207 

### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-03-21

Blocked until #28207 is implemented

---

## Issue #28142: Ability to differentiate different causes for WebInputException

**状態**: closed | **作成者**: ascopes | **作成日**: 2022-03-07

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28142

**関連リンク**:
- Commits:
  - [5d0f49c](https://github.com/spring-projects/spring-framework/commit/5d0f49c2c8c5436c667d5ba4753febd531fe5c7d)

### 内容

This is a request for the ability to generate a message stating that a WebFlux controller request body (or other request component) is missing, without exposing potentially sensitive implementation details in the error message. By doing this, it would remove the need for implementing a custom handler for validation where Spring provides messages that may fail organisational governance.

If we write a controller such as the following:

```java
@RestController
@Validated
public class TestController {
  @PostMapping("/foo/{bar}")
  @ResponseStatus(ACCEPTED)
  public Mono<Void> fooBar(@PathVariable String bar, @RequestBody Body body) {
    ...
  }
}
```

...the implementation for a missing request body appears to be currently defined in [AbstractMessageReaderArgumentResolver](https://github.com/spring-projects/spring-framework/blob/main/spring-webflux/src/main/java/org/springframework/web/reactive/result/method/annotation/AbstractMessageReaderArgumentResolver.java#L229):

```java
	private ServerWebInputException handleMissingBody(MethodParameter parameter) {
		String paramInfo = parameter.getExecutable().toGenericString();
		return new ServerWebInputException("Request body is missing: " + paramInfo, parameter);
	}
```

The error message here cannot be presented to the consumer of the API on systems where governance prevents the exposure of the underlying implementation technology (this would fail penetration testing, for example). The reason for this is that the error message with the concatenated parameter info will render to something like:

```
Request body is missing: public reactor.core.publisher.Mono<java.lang.Void> com.mycompany.TestController.fooBar(java.lang.String, com.mycompany.Body)
```

This can potentially expose information allowing the inference of the underlying JDK or Spring Boot version by observing the names of the parameters and method in the underlying error, which may enable malicious actors to "comb" an API and determine if certain exploits may exist.

The issue arises that while we can override this exception with a custom exception handler, this then involves writing a significant amount of boilerplate to cater for parsing every potential binding annotation, and then extracting information such as the name of the parameter (in the case of headers), or the request body. The current API does not provide a simple way of determining that the request body is the part that is missing in this case.

If we instead use Spring Validation, and use `@RequestBody(required = false) @Valid @NotNull`, the issue will instead arise that a ConstraintViolationException is raised instead of a WebExchangeBindingException, which then requires two almost identical sets of exception handlers to achieve the same consistent validation error handling. This appears to be due to `validate()` not being called on the body in `AbstractMessageReaderArgumentResolver.java` when the body is determined to be missing.

If we omit the message altogether, it leaves a response to the consumer that is not helpful for diagnosing the issue with the request. For example:

```java
{
  "status": 400,
  "message": "null"
}
```

Is there a workaround for this, or is this something that could be potentially tweaked? Providing consistent validation using the Spring Validation API with WebFlux is somewhat painful at the moment because of this, and it leads to code that can be somewhat difficult to maintain when it caters for multiple edge cases.

An ideal scenario would be where we could obtain a string "type" of the parameter in question that failed validation (e.g. `"header"`, `"body"`, `"pathVariable"`, etc, and then a simplified message such as `"Request body is required"` that can be presented back to the consumer of the API.

Any help or suggestions would be greatly appreciated!

Thanks


### コメント

#### コメント 1 by ascopes

**作成日**: 2022-03-22

Can confirm that this also occurs in UnsupportedMediaTypeStatusException as well, where the implementation package name is leaked in the error reason.

`415 UNSUPPORTED_MEDIA_TYPE "Content type 'application/x-yaml' not supported for bodyType=org.example.MyModelName`

#### コメント 2 by askar882

**作成日**: 2022-04-30

I was also trying to find a way to tell the client that the request body missing without exposing much information. And I was able to make this work with a custom exception handler as follows.
```Java
@RestControllerAdvice
public class ExceptionHandler {
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public Map<String, Object> requestBodyMissing(HttpServletRequest request) {
        HandlerMethod method = (HandlerMethod) request.getAttribute("org.springframework.web.servlet.HandlerMapping.bestMatchingHandler");
        String requestBody = Arrays.stream(method.getMethodParameters())
                .map(m -> m.getParameterType().getSimpleName() + " " + m.getParameterName())
                .collect(Collectors.joining(","));
        return Arrays.stream(new Object[][] {
                {"status", 400},
                {"message", "Required request body is missing: " + requestBody}
        }).collect(Collectors.toMap(o -> (String) o[0], o-> o[1]));
    }
}
```

When a client sends a request without a required body, it will receive something like:
```JSON
{
    "status": 400,
    "message": "Required request body is missing: String name"
}
```

#### コメント 3 by rstoyanchev

**作成日**: 2022-05-04

@ascopes thanks for creating this issue.

`ServerWebInputException` is indeed raised for different kinds of missing input, which is reflected in the message, but no easy way for an exception handler to tell what's missing and customize the message. I will experiment with adding a sub-class for `MissingRequestValueException` that exposes the `name` and `type` of the missing value where the type is just a string, e.g. "request header", "cookie value", etc. Also add a sub-class for type mismatch issues (conversion) and request body decoding issues. This should cover most cases. 

For validation, I see your point about `ConstraintViolation` with a class-level `@Validated` which is handled with an AOP interceptor (independent of Spring WebFlux) vs putting the same on `@RequestBody` which is handled in WebFlux and the `ConstraintViolation` is translated to `Errors` in `SpringValidatorAdapter`. We might be able to make that more easily accessible so the same adaptation can be performed from an exception handler.

Note also that for 6.0 we are making wider changes with #27052 to support problem details. This will provide more support for applications to set the response body directly from an `@ExceptionHandler` through the `ProblemDetail` type.



#### コメント 4 by rstoyanchev

**作成日**: 2022-05-04

@askar882 your snippet is for Spring MVC but this issue is for WebFlux. In Spring MVC there is a wider hierarchy of exceptions that make it possible to customize on a case by case basis.

#### コメント 5 by ascopes

**作成日**: 2022-05-04

@rstoyanchev that sounds great! Look forward to seeing what comes of this, thanks for taking a look.

#### コメント 6 by rstoyanchev

**作成日**: 2022-05-09

I've added `MissingRequestValueException` which covers cases of missing "named" values (headers, cookies, request params, etc) and `UnsatisfiedRequestParameterException` as subclasses of `WebInputException` that also expose properties with details about the exception. For request body, I've adjusted it to raise `WebInputException` with a nested `DecoderException` which should help to signal a problem with the request body.

#### コメント 7 by dpratsun

**作成日**: 2022-05-24

@rstoyanchev could you please tell at which version of Spring Boot `MissingRequestValueException` can be used?

#### コメント 8 by wimdeblauwe

**作成日**: 2022-05-28

What is the difference between `org.springframework.web.server.MissingRequestValueException` which was added to Spring 6 and `org.springframework.web.bind.MissingRequestValueException` which is already in Spring 5?

#### コメント 9 by rstoyanchev

**作成日**: 2022-07-13

@wimdeblauwe, one depends on the Servlet API and is used in Spring MVC. The other is part of the `ResponseStatusException` hierarchy that's used in WebFlux.

@dpratsun, it's available as of 6.0.0-M4.

#### コメント 10 by rstoyanchev

**作成日**: 2022-10-05

@ascopes, please take a look at #28814, which may further help with concerns here, especially as it relates  to "governance prevents the exposure of the underlying implementation technology " and the need to customize Spring MVC / WebFlux error messages.



#### コメント 11 by ascopes

**作成日**: 2022-10-05

Looks good, thanks for taking this into consideration!

#### コメント 12 by skaba

**作成日**: 2022-10-24

Will this be backported to Spring 5?

---

## Issue #28160: Introduce RuntimeHintsRegistrar

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-03-11

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28160

**関連リンク**:
- Commits:
  - [38019d2](https://github.com/spring-projects/spring-framework/commit/38019d224930ac7b24225b882743c574498a1f56)

### 内容

In order to provide the possibility for registering `RuntimeHints`, the proposal is to introduce a `RuntimeHintsRegistrar` abstraction designed to address the same needs than [`BeanFactoryNativeConfigurationProcessor`](https://github.com/spring-projects-experimental/spring-native/blob/main/spring-aot/src/main/java/org/springframework/aot/context/bootstrap/generator/infrastructure/nativex/BeanFactoryNativeConfigurationProcessor.java) and [`BeanNativeConfigurationProcessor`](https://github.com/spring-projects-experimental/spring-native/blob/main/spring-aot/src/main/java/org/springframework/aot/context/bootstrap/generator/infrastructure/nativex/BeanNativeConfigurationProcessor.java) in Spring Native. It could even be used initially to register static hints as done with `@NativeHint` annotations.

```
package org.springframework.beans.factory.hint;

public interface RuntimeHintsRegistrar {

	void registerHints(RuntimeHints hints, ListableBeanFactory beanFactory);

	default void ifPresent(String className, Runnable runnable) {
		if (ClassUtils.isPresent(className, null)) {
			runnable.run();
		}
	}
}
```



The `registerIfPresent` method is designed to provide a more discoverable mechanism to prevent `ClassNotFoundException` errors than inner classes.

Since they are designed to be used only AOT, `spring.factories` is not a good fit here, so implementations could be registered via a `META-INF/spring/org.springframework.beans.factory.hint.RuntimeHintsRegistrar.imports` file with the same format than [`org.springframework.boot.autoconfigure.AutoConfiguration.imports`]( https://github.com/spring-projects/spring-boot/blob/main/spring-boot-project/spring-boot-autoconfigure/src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports).

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-03-11

> Since they are designed to be used only AOT, spring.factories is not a good fit here

I don't necessarily disagree but it is disruptive to introduce another mechanism for that reason alone. There are many other concepts in the core container that behave differently when AOT is involved. For instance, we could imagine a class-level annotation on the type that provides some opt-in metadata that the transformer can use to ignore those entries.

I am not huge fan of the `factory.hint` package. Perhaps it is a smell that something named `RuntimeHintsRegistrar` is taking the bean factory as an argument?

cc @philwebb as I know he's been brainstorming on this topic as well.

---

## Issue #28189: Support "application/problem+json" as the response Content-Type

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-03-16

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28189

**関連リンク**:
- Commits:
  - [8378af9](https://github.com/spring-projects/spring-framework/commit/8378af9e397afe6bf5d91d16a22edf69912af408)
  - [78ab4d7](https://github.com/spring-projects/spring-framework/commit/78ab4d711812c754dc8a9b3021805899bfc5c9fe)

### 内容

Once  #28187 provides `ProblemDetail` along with the `ErrorResponse` hierarchy of exceptions that encapsulate HTTP status, headers, and body, to support RFC 7807, it is also necessary to improve content negotiation and formatting specifically for error responses.

In Spring MVC it is possible to configure [content type resolution](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-config-content-negotiation) and [message conversion](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-config-message-converters) and likewise in WebFlux to configure [content type resolution](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#webflux-config-content-negotiation) and [message codecs](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html#webflux-config-message-codecs), but those apply to both `@RequestMapping` and `@ExceptionHandler` methods. 

Error handling however has a different perspective. The range of supported media types might be more limited and different, e.g. only `application/problem+json`. The resolution of the request content type might also be done differently, .e.g. defaulting to `application/problem+json` if not explicitly requested, or perhaps even enforcing it.

Such a mechanism is also a convenient place for other configuration related to how `ProblemDetail` should be rendered..


### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-05-09

On closer investigation, this can be handled transparently as follows.

Message converters and encoders indicate a preference for `application/problem+json` when `ProblemType` is serialized. This ensures `application/problem+json` is preferred when the client is flexible or has no preference.

If content negotiation fails to find an acceptable media type for serializing `ProblemDetail`, we try again with `application/problem+json` and `application/problem+xml` as the acceptable media types, in effect enforcing a fallback for `ProblemDetail`. 


---

## Issue #28190: Enable access to an RFC 7807 ProblemDetail formatted error response from the client side

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-03-16

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28190

**関連リンク**:
- Commits:
  - [6479566](https://github.com/spring-projects/spring-framework/commit/64795664b2ce928c3c86367a88b7a4eebac84491)
  - [922636e](https://github.com/spring-projects/spring-framework/commit/922636e85e7acb66bca1b39e8c18e88f9111913b)

### 内容

Currently `WebClientResponseException` exposes the body as a `byte[]` or `String` and so does `RestClientResponseException`. It would be useful if these exposed convenience methods to decode an RFC 7807 formatted response to `ProblemDetail`. 

The exceptions could be created with a `Callable<ProblemDetail>` or similar to decouple them from the details of decoding, or perhaps the decoding could be done automatically for such a response and the ProblemDetail passed in to the exception.

---

## Issue #28198: Remove obsolete org.springframework.core.NestedIOException

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-03-18

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28198

**関連リンク**:
- Commits:
  - [7f501fa](https://github.com/spring-projects/spring-framework/commit/7f501fabcba647b5fd05eec453b987c1310b3de5)
  - [4978180](https://github.com/spring-projects/spring-framework/commit/497818049ca329951a90004250a76299c8d12b7a)
  - [855cd23](https://github.com/spring-projects/spring-framework/commit/855cd236a05579638f058a82ce19518b0d8a7eb1)
  - [f0a4f5c](https://github.com/spring-projects/spring-framework/commit/f0a4f5c66eb8606077a3d1ed8b47bbaf98a8ff8c)
  - [0dc68a1](https://github.com/spring-projects/spring-framework/commit/0dc68a1fb9f3856c62b93e8b2bbae91e089b002f)
  - [5996a3c](https://github.com/spring-projects/spring-framework/commit/5996a3c0f4317bb4c0db4f3c69f813a521aaceca)
  - [8e5174b](https://github.com/spring-projects/spring-framework/commit/8e5174b0be8b6ca79e426d969927aace0f003d15)
  - [190eee0](https://github.com/spring-projects/spring-framework/commit/190eee019f60d8e740476e35220110b84a7154b7)
  - [2fb1dd1](https://github.com/spring-projects/spring-framework/commit/2fb1dd177b7b056f30a9de0739d8afdef37d72aa)
  - [8032af9](https://github.com/spring-projects/spring-framework/commit/8032af9c3367c55f5d7bdb93cf7d6d45ee9c2df4)
  - [8f68dc5](https://github.com/spring-projects/spring-framework/commit/8f68dc59ad7cf751ed056ed24ff048dc0d47da36)
  - [5bff7c0](https://github.com/spring-projects/spring-framework/commit/5bff7c041757ec0bcf3f42cd8057686bb0597a73)
  - [f15c324](https://github.com/spring-projects/spring-framework/commit/f15c324cd4fa7d32889d8e775e7afe795122559a)
  - [a14388a](https://github.com/spring-projects/spring-framework/commit/a14388a3a448a41ed6783fa53897e3bf0eb265d9)
  - [2ab6698](https://github.com/spring-projects/spring-framework/commit/2ab6698372b6afe09beae332160e665d550e4ca7)
  - [9841b97](https://github.com/spring-projects/spring-framework/commit/9841b9758f0995c34d9e2445b03d7a18cbf40dfa)
  - [91ec952](https://github.com/spring-projects/spring-framework/commit/91ec9521052221234fdb143d0b425fe52bf14512)
  - [eb576df](https://github.com/spring-projects/spring-framework/commit/eb576df1f9454a4392a85c9fd5374fc4f8d8f3c9)
  - [d4bcfd9](https://github.com/spring-projects/spring-framework/commit/d4bcfd9a746e0155f2929ad7225c29ca68fa7c8d)
  - [23c854a](https://github.com/spring-projects/spring-framework/commit/23c854ad0cc461992c5f76f53cd83fbcbf6c0e8a)
  - [d8aafda](https://github.com/spring-projects/spring-framework/commit/d8aafdafffc4eb3e7380dc4e20f78545b6324c38)
  - [78ab75c](https://github.com/spring-projects/spring-framework/commit/78ab75ca40494bb9dd1efed14822bd2a548177cf)
  - [3c29424](https://github.com/spring-projects/spring-framework/commit/3c294246b6581504b2402e0dcc9d24b0b0f7129f)

### 内容

Spring's custom `org.springframework.core.NestedIOException` is obsolete and can be replaced with standard `IOException` usage.

### コメント

#### コメント 1 by jingxiang

**作成日**: 2022-08-05

Why not mark as  Deprecated ? 
As far as I know, this class involves many downstream dependencies, and direct deletion may lead to the unavailability of many frameworks.
For example：mybatis-spring-boot:2.2.2

`Caused by: java.lang.NoClassDefFoundError: org/springframework/core/NestedIOException
	at org.mybatis.spring.boot.autoconfigure.MybatisAutoConfiguration.sqlSessionFactory(MybatisAutoConfiguration.java:141)
	at org.mybatis.spring.boot.autoconfigure.MybatisAutoConfiguration$$EnhancerBySpringCGLIB$$fde06b8c.CGLIB$sqlSessionFactory$2(<generated>)
	at org.mybatis.spring.boot.autoconfigure.MybatisAutoConfiguration$$EnhancerBySpringCGLIB$$fde06b8c$$FastClassBySpringCGLIB$$8baa1e6e.invoke(<generated>)
	at org.springframework.cglib.proxy.MethodProxy.invokeSuper(MethodProxy.java:244)`

#### コメント 2 by snicoll

**作成日**: 2022-08-05

@jingxiang this is a good point, `NestedIOException` should have been marked as deprecated in `5.3.x`. I've created #28929. If you're working on mybatis, please update the code to catch `IOException` directly. If you don't, can you please create an issue to notify them? Thanks!

---

## Issue #28202: Determine why previous isolation level is never set in R2dbcTransactionManager

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-03-20

**ラベル**: in: data, type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/28202

**関連リンク**:
- Commits:
  - [fae36e9](https://github.com/spring-projects/spring-framework/commit/fae36e98b4c3d72941e3f209a87047332ff51ba1)

### 内容

## Overview

Currently, the `previousIsolationLevel` is never set in `R2dbcTransactionManager.ConnectionFactoryTransactionObject`; however, there is code in place to read the previous isolation level in `R2dbcTransactionManager.doCleanupAfterCompletion(TransactionSynchronizationManager, Object)`.

## Deliverables

- [x] Determine why `previousIsolationLevel` is never set.
- [x] Introduce code to set the `previousIsolationLevel` if appropriate; otherwise, delete all code related to `previousIsolationLevel`.

### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-03-20

@mp911de, can you please take a look at this?

#### コメント 2 by mp911de

**作成日**: 2022-03-21

`previousIsolationLevel` should have been removed with the R2DBC 0.9 upgrade, it's an oversight.

Before R2DBC 0.9, we set and reset the Isolation Level on the connection (same as with JDBC). With R2DBC 0.9, if we set the Isolation Level, then the isolation level is only valid for the duration of a transaction and we expect the driver to reset the Isolation Level after the transaction. This is part of the `begin(TransactionDefinition)` contract.

#### コメント 3 by sbrannen

**作成日**: 2022-03-21

Thanks for the feedback and explanation, @mp911de.

I'll remove the obsolete code.

---

## Issue #28207: Introduce predicate for searching enclosing classes in MergedAnnotations

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-03-21

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28207

**関連リンク**:
- Commits:
  - [c23edf7](https://github.com/spring-projects/spring-framework/commit/c23edf7da6c403eeedb862e02b9a7293cfba38a1)
  - [1fe394f](https://github.com/spring-projects/spring-framework/commit/1fe394f11d7ab7f328402a04d13f4d12a89a9f87)
  - [23d0240](https://github.com/spring-projects/spring-framework/commit/23d0240dc724ddeacba5b5e84ce5c5f08e5d3dc3)

### 内容

## Overview

Due to the deprecation of `SearchStrategy.TYPE_HIERARCHY_AND_ENCLOSING_CLASSES` (see #28079), we will introduce a way for users to provide a `Predicate<Class<?>>` that is used to decide when the enclosing class for the class supplied to the predicate should be searched.

This will give the user complete control over the "enclosing classes" aspect of the search algorithm in `MergedAnnotations`.

- To achieve the same behavior as `TYPE_HIERARCHY_AND_ENCLOSING_CLASSES`, a user can provide `clazz -> true` as the predicate.
- To limit the enclosing class search to inner classes, a user can provide `ClassUtils::isInnerClass` as the predicate.
- To limit the enclosing class search to static nested classes, a user can provide `ClassUtils::isStaticClass` as the predicate.
- For any other use case (such as in `TestContextAnnotationUtils` in `spring-test`), the user can provide a custom predicate.

## Proposal

Based on the outcome of #28208, a `searchEnclosingClass` predicate could be supplied when using the `TYPE_HIERARCHY` search strategy as follows.

```java
MergedAnnotations annotations = MergedAnnotations
    .search(SearchStrategy.TYPE_HIERARCHY)
    .withEnclosingClasses(ClassUtils::isInnerClass)
    .from(myClass);
```

By limiting when a `searchEnclosingClass` predicate can be supplied in the fluent search API, we can prevent users from trying to supply such a predicate for other `SearchStrategy` types.

### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-03-21

Blocked until #28208 is implemented

---

## Issue #28208: Introduce fluent API for search options in MergedAnnotations

**状態**: closed | **作成者**: sbrannen | **作成日**: 2022-03-21

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28208

**関連リンク**:
- Commits:
  - [c23edf7](https://github.com/spring-projects/spring-framework/commit/c23edf7da6c403eeedb862e02b9a7293cfba38a1)

### 内容

## Overview

Inspired by the requirements for implementing #28207, we have decided to introduce a fluent API for search options in [`MergedAnnotations`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/core/annotation/MergedAnnotations.html).

The following is an example of how one would supply search options using the existing API.

```java
MergedAnnotations annotations = MergedAnnotations.from(myClass, SearchStrategy.TYPE_HIERARCHY,
		RepeatableContainers.of(MyRepeatable.class, MyRepeatableContainer.class),
		myCustomAnnotationFilter);
```

## Proposal

For each strategy in [`SearchStrategy`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/core/annotation/MergedAnnotations.SearchStrategy.html), we will introduce a corresponding `find*()` method that starts the fluent API. Methods such as `usingRepeatableContainers()` and `withAnnotationFilter()` will be optional. The fluent API culminates with an invocation of `from(...)` which performs the search and returns the `MergedAnnotations` instance.

With a fluent API, the above can be rewritten as follows.

```java
MergedAnnotations annotations = MergedAnnotations
    .findAnnotationsInTypeHierarchy()
    .usingRepeatableContainers(RepeatableContainers.of(MyRepeatable.class, MyRepeatableContainer.class))
    .withAnnotationFilter(myCustomAnnotationFilter)
    .from(myClass);
```

For a less involved use case that relies on the defaults for repeatable containers and filtering, the code would reduce to the following.

```java
MergedAnnotations annotations = MergedAnnotations.findAnnotationsInTypeHierarchy().from(myClass);
```



### コメント

#### コメント 1 by sbrannen

**作成日**: 2022-03-22

After putting more thought into this, I wonder if it's best to end the fluent API with `from(...)` instead of a verb or command like `search(...)`, `searchFrom(...)`, etc.

`MergedAnnotations` already has various `from(...)` and `on(...)` methods, so the new fluent API cannot start with either of those.

@philwebb recommended all new factory methods in `MergedAnnotations` start with the same prefix to make them easily discoverable, which of course makes a lot of sense. So we were thinking of `find*` and `search*` as a reasonable, meaningful prefix for these new methods.

However, if the final action in the fluent API is a method named `search*(...)`, it seems a bit odd to have the first method called `find*(...)` or `search*(...)`.

So, another idea I'm tinkering with is starting with a single static factory method for "search options" like this:

```java
MergedAnnotations annotations = MergedAnnotations.searchOptions()
	.typeHierarchy()
	.repeatableContainers(myRepeatableContainers)
	.annotationFilter(myCustomAnnotationFilter)
	.search(myClass);
```

One additional (unplanned) benefit of that is that the `SearchOptions` "builder" instance could actually be saved and reused to perform `.search(...)` on different classes/methods. However, I'm not sure how useful that would be in practice.

#### コメント 2 by sbrannen

**作成日**: 2022-03-22

Current proposal, based on brainstorming sessions and taking #28207 into account:

```java
MergedAnnotations
	.search(searchStrategy)
	.withEnclosingClasses(ClassUtils::isInnerClass)
	.withRepeatableContainers(repeatableContainers)
	.withAnnotationFilter(annotationFilter)
	.from(myClass);
```

#### コメント 3 by philwebb

**作成日**: 2022-03-22

Ha, I was about to suggest this :)

```java
MergedAnnotations
	.searching(searchStrategy)
	.withEnclosingClasses(ClassUtils::isInnerClass)
	.withRepeatableContainers(repeatableContainers)
	.withAnnotationFilter(annotationFilter)
	.from(myClass);
```

#### コメント 4 by philwebb

**作成日**: 2022-03-22

I think convenience search methods are also worth considering. `SearchStrategy` tends to be one of the more common things to want to define.

```java
MergedAnnotations.searchingTypeHierarchy().with...().from(myClass)
```

#### コメント 5 by sbrannen

**作成日**: 2022-03-22

> I think convenience search methods are also worth considering.

We definitely considered that approach, but the choice of meaningful (_and_ concise) names becomes challenging for any `SearchStrategy` other than `TYPE_HIERARCHY`.

```java
MergedAnnotations
	// .searchDirect()
	// .searchInheritedAnnotations()
	// .searchSuperclass()
	.searchTypeHierarchy()
	.withEnclosingClasses(ClassUtils::isInnerClass)
	.withRepeatableContainers(repeatableContainers)
	.withAnnotationFilter(annotationFilter)
	.from(myClass);
```

The above seems too vague, and the following seems too verbose.

```java
MergedAnnotations
	// .findDirectlyDeclaredAnnotations()
	// .findInheritedAnnotations()
	// .findSuperclassAnnotations()
	.findAnnotationsInTypeHierarchy()
	.withEnclosingClasses(ClassUtils::isInnerClass)
	.withRepeatableContainers(repeatableContainers)
	.withAnnotationFilter(annotationFilter)
	.from(myClass);
```

In the end, @jhoeller and I decided that it's probably best to let the user supply a `SearchStrategy` and rely on the documentation for those enum constants to _explain_ things, since people are accustomed to the increasing scope of the strategies in the context of enums; whereas, it becomes a bit more cumbersome to infer that increasing scope based solely on method names like the ones in the two preceding examples.

But... if you have better ideas for how to name all 4 convenience methods, by all means speak up. 👍 


---

## Issue #28212: Fix queriedMethods handling in ReflectionHintsSerializer

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-03-22

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28212

**関連リンク**:
- Commits:
  - [1ffc96b](https://github.com/spring-projects/spring-framework/commit/1ffc96be8c455cd3bdfd7193d1f9cef45fa31aa8)
  - [e7e843c](https://github.com/spring-projects/spring-framework/commit/e7e843cae2d3303a0e2d09d8a64f14ebbf314c00)

### 内容

As discovered by @snicoll, serialiation of `queriedMethods` is broken when there is no `methods`.
```json
[
  {
    "name": "com.example.nativex.sample.basic.SampleConfiguration"
    "queriedMethods": [
      {
        "name": "testBean",
        "parameterTypes": []
      }
    ]
  }
]
```

---

## Issue #28213: Throw a meaningful exception if a TypeReference does not use a fully qualified name

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-03-22

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28213

**関連リンク**:
- Commits:
  - [52d5452](https://github.com/spring-projects/spring-framework/commit/52d545238102c51f4f4d4227e4db6084aa4e2091)

### 内容

`TypeReference.of("int")` fails because a dot is expected in the type name.

```
begin 0, end -1, length 3
java.lang.StringIndexOutOfBoundsException: begin 0, end -1, length 3
	at java.base/java.lang.String.checkBoundsBeginEnd(String.java:4601)
	at java.base/java.lang.String.substring(String.java:2704)
	at org.springframework.aot.hint.SimpleTypeReference.createTypeReference(SimpleTypeReference.java:60)
	at org.springframework.aot.hint.SimpleTypeReference.of(SimpleTypeReference.java:48)
	at org.springframework.aot.hint.TypeReference.of(TypeReference.java:75)
```

### コメント

#### コメント 1 by snicoll

**作成日**: 2022-03-22

Ignoring the exception, this is the expected behaviour. Fully qualified name is expected as an input here so it should be `TypeReference.of("java.lang.int")`.

---

## Issue #28214: Introduce HttpStatusCode interface

**状態**: closed | **作成者**: poutsma | **作成日**: 2022-03-22

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28214

**関連リンク**:
- Commits:
  - [f49de92](https://github.com/spring-projects/spring-framework/commit/f49de92ac042b847b9d50bc5e9c606471383213a)
  - [28ac0d3](https://github.com/spring-projects/spring-framework/commit/28ac0d3883e0c683fb995dffc0af7c8a82f3c3d0)
  - [ca4b6e8](https://github.com/spring-projects/spring-framework/commit/ca4b6e86a4dd7f278049a6d91196d817c7953c43)
  - [05df42c](https://github.com/spring-projects/spring-framework/commit/05df42c58aa7d094d2b49b783bb525c8013ae93d)

### 内容

According to [the HTTP specification](https://datatracker.ietf.org/doc/html/rfc2616#section-6.1.1), the HTTP response status can be any 3-digit integer. 

In Spring Framework, the HTTP status codes are enumerated in `HttpStatus`. Because this type is a Java `enum`, we need to have workarounds to allow for status codes not in the enum. For instance, the `ClientHttpResponse` interfaces offers both `getStatusCode` as well as `getRawStatusCode`, as does WebClient's `ClientResponse`, and we have similar workarounds in other places.

We cannot change `HttpStatus` from a enum to a class like we did for `HttpMethod` in #27697, because `HttpStatus` is used in the `ResponseStatus` annotation, where class instances can not be used as values.

@philwebb suggested that we can introduce a new interface `HttpStatusCode`, which is implemented by `HttpStatus`. Code that currently returns a `HttpStatus` will return this new `HttpStatusCode` instead, and we will deprecate the methods that return the raw status codes. All methods that *accepts* the raw integer values will still be available, we will only deprecate the integer returning methods.

Instances of the `HttpStatusCode` are obtained via static `valueOf(int)` factory method, which returns a `HttpStatus` enum entry if one is available for the given integer, and a default implementation otherwise. This way, we can assure that `HttpStatus`  instance comparisons  (i.e. `if (statusCode == HttpStatus.OK)`) will keep working as they currently do.


---

## Issue #28244: Initialize NativeDetector at build time

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-03-29

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28244

**関連リンク**:
- Commits:
  - [cdb2463](https://github.com/spring-projects/spring-framework/commit/cdb2463dc88b721dd28845433f03ec6ed2cf5386)
  - [04b1b5d](https://github.com/spring-projects/spring-framework/commit/04b1b5d96e320a90961091cd9552dde8f78d9589)
  - [e681e71](https://github.com/spring-projects/spring-framework/commit/e681e713d4aa75be988d77f0108f80ecf15e21e9)
  - [c611561](https://github.com/spring-projects/spring-framework/commit/c6115619ebf15b89d048997944d7d0f516f49e2c)
  - [ff02c78](https://github.com/spring-projects/spring-framework/commit/ff02c787372431af9ca5a936d41f9f383c33af45)

### 内容

In order to allow code removal with constructs like `if (NativeDetector.inNativeImage()) { ... } else { ... }`, `NativeDetector` needs to be initialized at build time. `-H:+InlineBeforeAnalysis` is enabled by default as of GraalVM 21.3 so no further configuration is needed.

Since build time initialization is not necessarily something we want to expose in public APIs, embedding a `spring-core/src/main/resources/META-INF/native-image/org.springframework/spring-core/native-image.properties` file for that purpose is the solution chosen for now.

---

## Issue #28291: Add support for HEAD methods in Spring's Resource handling

**状態**: closed | **作成者**: hannosgit | **作成日**: 2022-04-06

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28291

**関連リンク**:
- Commits:
  - [5fc8a98](https://github.com/spring-projects/spring-framework/commit/5fc8a9839cb22b960d05d8e9b94d69ceb4297062)
  - [9adfa5e](https://github.com/spring-projects/spring-framework/commit/9adfa5e8b0f0cd65a0b14740e0a0f9832d80edcb)

### 内容

<!--
!!! For Security Vulnerabilities, please go to https://spring.io/security-policy !!!
-->
**Affects:**  Spring Web 5.3.18
**Tested with:** Tomcat and Jetty
**Tested with:** Linux and Windows

---

I want to download large files (>10GB) from a Spring Web Server, before I start the download I want to know the size of the remote file, so, therefore, I make a HEAD request on the remote file.

Static files are served via ResourceHandlers, eg.

``` Java
@Configuration
public class MvcConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry
            .addResourceHandler("/**")
            .addResourceLocations("file:download/");
    }

}
```

and then when I make a HEAD request on a large file (> 10 GB), on the first try I get the response within milliseconds but when I try again the response takes seconds ( >10s).



### コメント

#### コメント 1 by poutsma

**作成日**: 2022-04-07

The underlying reason for this is that resource handling in Spring MVC (and WebFlux) does not have explicit support for `HEAD` methods yet. Instead, we treat the request as a `GET`, write the entire file to the body, and rely on the standard `HttpServlet::doHead` functionality to ignore everything written.

I will introduce `HEAD` support in `ResourceHttpRequestHandler` and `ResourceWebHandler`.

---

## Issue #28312: GraalVM reflect config uses wrong format for inner classes

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-10

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28312

**関連リンク**:
- Commits:
  - [069aab3](https://github.com/spring-projects/spring-framework/commit/069aab37cd4392a6419148e37721ca4bdb748b1c)

### 内容

If we have a reflection hint for an inner class, GraalVM expects us to use a `$` to separate the parent from the inner class. Unfortunately, the serializer uses a `.` (canonical name).



---

## Issue #28328: Work around the fact that GraalVM detects that DataSize is safe to initialize at build time

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-12

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/28328

**関連リンク**:
- Commits:
  - [92f8ab7](https://github.com/spring-projects/spring-framework/commit/92f8ab774f6616a2c47b91ec74a95f96c596b954)
  - [64570a8](https://github.com/spring-projects/spring-framework/commit/64570a85b3db389b1e8c12b22ac61c867d1cc94c)

### 内容

Building a simple command-line leads to: 

```
Error: Classes that should be initialized at run time got initialized during image building:
 org.springframework.util.unit.DataSize was unintentionally initialized at build time. To see why org.springframework.util.unit.DataSize got initialized use --trace-class-initialization=org.springframework.util.unit.DataSize

com.oracle.svm.core.util.UserError$UserException: Classes that should be initialized at run time got initialized during image building:
 org.springframework.util.unit.DataSize was unintentionally initialized at build time. To see why org.springframework.util.unit.DataSize got initialized use --trace-class-initialization=org.springframework.util.unit.DataSize

	at com.oracle.svm.core.util.UserError.abort(UserError.java:73)
	at com.oracle.svm.hosted.classinitialization.ConfigurableClassInitialization.checkDelayedInitialization(ConfigurableClassInitialization.java:555)
	at com.oracle.svm.hosted.classinitialization.ClassInitializationFeature.duringAnalysis(ClassInitializationFeature.java:167)
	at com.oracle.svm.hosted.NativeImageGenerator.lambda$runPointsToAnalysis$10(NativeImageGenerator.java:704)
	at com.oracle.svm.hosted.FeatureHandler.forEachFeature(FeatureHandler.java:74)
	at com.oracle.svm.hosted.NativeImageGenerator.lambda$runPointsToAnalysis$11(NativeImageGenerator.java:704)
	at com.oracle.graal.pointsto.PointsToAnalysis.runAnalysis(PointsToAnalysis.java:755)
	at com.oracle.svm.hosted.NativeImageGenerator.runPointsToAnalysis(NativeImageGenerator.java:702)
	at com.oracle.svm.hosted.NativeImageGenerator.doRun(NativeImageGenerator.java:537)
	at com.oracle.svm.hosted.NativeImageGenerator.run(NativeImageGenerator.java:494)
	at com.oracle.svm.hosted.NativeImageGeneratorRunner.buildImage(NativeImageGeneratorRunner.java:426)
	at com.oracle.svm.hosted.NativeImageGeneratorRunner.build(NativeImageGeneratorRunner.java:587)
	at com.oracle.svm.hosted.NativeImageGeneratorRunner.main(NativeImageGeneratorRunner.java:126)
	at com.oracle.svm.hosted.NativeImageGeneratorRunner$JDK9Plus.main(NativeImageGeneratorRunner.java:617)
```

This looks wrong and could be addressed in Graal. In the meantime we'll add a flag to prevent that from happening.

---

## Issue #28339: Allow to register reflection hints for multiple types at once

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28339

**関連リンク**:
- Commits:
  - [5be6b3d](https://github.com/spring-projects/spring-framework/commit/5be6b3d2a7ed4f1ad980ae02cb8c3cf0a6a616b4)

### 内容

There is a recurrent pattern that some classes share the same hints and the API does not offer a shortcut to register those on multiple types at once..

cc @christophstrobl

---

## Issue #28342: Allow to register AotContributingBeanFactoryPostProcessor declaratively

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-14

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28342

**関連リンク**:
- Commits:
  - [7820804](https://github.com/spring-projects/spring-framework/commit/7820804bf6d07635d6f28c607ecde9243db4628f)

### 内容

`RuntimeHintsPostProcessor` is one of its kind. There are actually more needs like this. 

---

## Issue #28347: Reflection configuration for primitives have wrong name

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-15

**ラベル**: type: bug, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28347

**関連リンク**:
- Commits:
  - [f40a391](https://github.com/spring-projects/spring-framework/commit/f40a391916ed6c1f9e1130638a0bf19479e514dd)

### 内容

The json writer does not handle reflection target name properly for primitives. `java.lang.double` is generated instead of `double` for instance. This leads to warning when building a native image and those hints are obviously not taken into account.

---

## Issue #28363: MultiStatement#toCodeBlock should be name toLambdaBody

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-21

**ラベル**: type: task, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28363

**関連リンク**:
- Commits:
  - [d7391b1](https://github.com/spring-projects/spring-framework/commit/d7391b13ab48535d39bc9e5a66847ae9e8e976e7)
  - [10d2549](https://github.com/spring-projects/spring-framework/commit/10d254983f78a3faf190ec6fa32b648beda82827)

### 内容

`toCodeBlock` is confusing as it is heavily tailored for adding the code in the context of a lambda. We could use a `toCodeBlock` that actually creates a regular multi-statements code block.

---

## Issue #28364: AOT contribution for `@PersistenceContext` and `@PersistenceUnit`

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-21

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28364

**関連リンク**:
- Commits:
  - [7ef34b0](https://github.com/spring-projects/spring-framework/commit/7ef34b0949f9afea78b84fae4b146a9b9b826266)
  - [3e2ab2d](https://github.com/spring-projects/spring-framework/commit/3e2ab2dee8c4e218770f1ab69ceda38dc6d84b97)
  - [26054fd](https://github.com/spring-projects/spring-framework/commit/26054fd3d4aba89474f2173c7be44db6937aaf51)

### 内容

We don't process those at the moment.

---

## Issue #28383: Generate appropriate AOT bean registration for scoped proxies

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-26

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28383

**関連リンク**:
- Commits:
  - [f64fc4b](https://github.com/spring-projects/spring-framework/commit/f64fc4baff2625192aff02e0d192b1c678384eae)

### 内容

`ScopedProxyFactoryBean` are not handled property in an AOT optimized  context. As a result, such a bean cannot be injected properly.

---

## Issue #28384: BeanRegistrationContributionProvider should have access to the bean factory

**状態**: closed | **作成者**: snicoll | **作成日**: 2022-04-26

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28384

**関連リンク**:
- Commits:
  - [7ea0cc3](https://github.com/spring-projects/spring-framework/commit/7ea0cc3da2863c20e544d68f29edc3f66c1d1b13)

### 内容

_本文なし_

---

## Issue #28386: Support to Create a Proxy From an Annotated HTTP Service Interface

**状態**: closed | **作成者**: rstoyanchev | **作成日**: 2022-04-26

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28386

**関連リンク**:
- Commits:
  - [d2b6743](https://github.com/spring-projects/spring-framework/commit/d2b674391a01c4b4cc8424466e4cea5ef8167f35)
  - [bb44c0e](https://github.com/spring-projects/spring-framework/commit/bb44c0e13a2b0cb3e808f5b184ea7c7a1bcd63b1)
  - [8a46e96](https://github.com/spring-projects/spring-framework/commit/8a46e968751f566b3bc87623bc0a2957789d47ce)
  - [7797453](https://github.com/spring-projects/spring-framework/commit/7797453f2861c3eb64a869199ce8b9f95df76207)
  - [4bddbd3](https://github.com/spring-projects/spring-framework/commit/4bddbd30c4c5200b8e3e44d4b86ad26cfdd6fa76)
  - [d7ab5b4](https://github.com/spring-projects/spring-framework/commit/d7ab5b41327aa41e975fb82da57ac29855cc2dba)
  - [62ab360](https://github.com/spring-projects/spring-framework/commit/62ab360f64b57b2679f19a1dd9eb13d317c6e40e)
  - [a8c3c74](https://github.com/spring-projects/spring-framework/commit/a8c3c746afe7242d79713ba12f4696a5df81e801)
  - [2d2726b](https://github.com/spring-projects/spring-framework/commit/2d2726b8f77d7139c2dfdd0e4c0bc1b7591282d7)
  - [2794553](https://github.com/spring-projects/spring-framework/commit/2794553d2e12a7c74f7654fc093bcfc93de1723d)
  - [b1384dd](https://github.com/spring-projects/spring-framework/commit/b1384ddafa9c6aac76312c103ba69c901f7b75f1)
  - [564f8ba](https://github.com/spring-projects/spring-framework/commit/564f8ba7a005de1ef1c6484d3f36a120e500005e)
  - [c2a008f](https://github.com/spring-projects/spring-framework/commit/c2a008fc22df64cc6ee5e1f69c1a8069dedcfa5e)
  - [c418768](https://github.com/spring-projects/spring-framework/commit/c418768f05751b791434abb43a9ee6e68467b96e)

### 内容

This has been raised before, see #16747 and related (duplicate) issues, but was done under Spring Cloud instead, first as an [OpenFeign integration](https://github.com/spring-cloud/spring-cloud-openfeign) and more recently as a [Retrofit integration](https://github.com/spring-projects-experimental/spring-cloud-square).

The goal for this issue is first class support in the Spring Framework to create a client proxy from an annotated, HTTP service interface, since it is more generally applicable. Spring Cloud can then provide additional features around that. The same is also planned for RSocket with #24456. 

Methods on such an HTTP service interface will support many of the same [method arguments](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-ann-arguments) as for server side handling with `@RequestMapping` methods, but narrowing the choice down to those arguments that apply to both client and server side use. On the client side, argument values are used to populate the request, while on the server side, argument values are extracted from the request.

Methods of the HTTP service interface will require a new annotation, similar in purpose to `@RequestMapping`, but to declare an HTTP exchange in a way that is neutral to client or server perspective.


---

## Issue #28392: FormHttpMessageConverter should not have a dependency on the Jakarta Mail API

**状態**: closed | **作成者**: jomastel | **作成日**: 2022-04-28

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28392

**関連リンク**:
- Commits:
  - [217117c](https://github.com/spring-projects/spring-framework/commit/217117ced04da7e68d171c09b103bf1e91536a09)

### 内容

When working with `multipartCharset` the `FormHttpMessageConverter` uses the `MimeUtility.encodeText` method.
This forces a dependency for sending email inside a HTTP converter. 
In our case, we now need to import `org.springframework.boot:spring-boot-starter-mail` to fix this dependency.

Could an alternative import be used here to avoid such dependencies in the case of `Content-Type` `multipart`? 
We found this issue when using a simple REST API.

### コメント

#### コメント 1 by poutsma

**作成日**: 2022-04-28

The dependency to `MimeUtility` was [introduced in 2014](https://github.com/spring-projects/spring-framework/commit/9be0cf21e5d3537d2415fea5eaea152e7407d45b). In 2016, we [introduced the `Content-Disposition` type](https://github.com/spring-projects/spring-framework/commit/99a8510ace46af9b05b822e7c65f08aae885ca98), with its own MIME encoding logic in `encodeFilename`.

I will drop the call to `MimeUtility.encodeText` in favor of the mechanism in `Content-Disposition` as of 6.0 M4. This means that we will move from using RFC 2047 to RFC 5987 for filename parameters, as we already do in Spring WebFlux' multipart support.

---

## Issue #28400: Support for Jakarta Concurrency 3.0

**状態**: closed | **作成者**: jhoeller | **作成日**: 2022-04-29

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28400

**関連リンク**:
- Commits:
  - [0f6d459](https://github.com/spring-projects/spring-framework/commit/0f6d459de78f2c2cfc1410bc4f3859175f5ebf92)

### 内容

Jakarta EE 10 includes several significant additions to the Jakarta Concurrency API, including a `jakarta.enterprise.concurrent.Asynchronous` annotation similar to EJB's `jakarta.ejb.Asynchronous` which we detect as well. When the Jakarta Concurrency 3.0 API is present at runtime, we should aim for consistent auto-adapting.

---

## Issue #28414: Refactor AOT code to reduce coupling and improve generated code

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-05

**ラベル**: type: task

**URL**: https://github.com/spring-projects/spring-framework/issues/28414

**関連リンク**:
- Commits:
  - [b1e9565](https://github.com/spring-projects/spring-framework/commit/b1e95655819e79830fcd3912a2226f1387de16bf)
  - [c1b4e18](https://github.com/spring-projects/spring-framework/commit/c1b4e18ccb5b3b8c77633d5e28b105706b3d2ace)
  - [6c04c10](https://github.com/spring-projects/spring-framework/commit/6c04c10c8cca863597bdd31b55a83ea29cf7c65d)
  - [b063118](https://github.com/spring-projects/spring-framework/commit/b063118ab26a51862c8968462754bc6ef03c10cc)
  - [5c8c515](https://github.com/spring-projects/spring-framework/commit/5c8c515a515b5f1735c17a4f3678e3206638f1dd)
  - [033e499](https://github.com/spring-projects/spring-framework/commit/033e4997437384c73856887f6216caca3a3e38c7)
  - [bb5d874](https://github.com/spring-projects/spring-framework/commit/bb5d8740094f6b8f0a7a41e7ddf2dbba6edcd626)
  - [b33953c](https://github.com/spring-projects/spring-framework/commit/b33953cf6cbdd546e84d227e9d464f96d6081e82)
  - [7b4baec](https://github.com/spring-projects/spring-framework/commit/7b4baec9531e4d84fe79cdcaad7e2e96a408502a)
  - [b99bd0b](https://github.com/spring-projects/spring-framework/commit/b99bd0b432e27464599936706c4c08b11de90803)
  - [746eb63](https://github.com/spring-projects/spring-framework/commit/746eb634eeb60108fe4c1b8a737d5a720b0e7521)
  - [af80310](https://github.com/spring-projects/spring-framework/commit/af8031007c351e0c971c25bbdee0db9044c3548d)
  - [4e8987c](https://github.com/spring-projects/spring-framework/commit/4e8987c52543a2519bf244b1e90f241e45e50e5d)
  - [f3b66ed](https://github.com/spring-projects/spring-framework/commit/f3b66ed4d6951144ef10c93dc532362e0f2c028e)
  - [9731f21](https://github.com/spring-projects/spring-framework/commit/9731f213a09fa7732b666cde0c28738fa107f51b)
  - [8f1ec43](https://github.com/spring-projects/spring-framework/commit/8f1ec4311dd480423b1f9a2124f6356abc0169f9)
  - [c39a263](https://github.com/spring-projects/spring-framework/commit/c39a2638abaaf4f3546165559e64df529d76679b)
  - [73ef9e8](https://github.com/spring-projects/spring-framework/commit/73ef9e84b1c6c8e4e70ccb7ecdd31b4dfdd70aaa)
  - [3c74cb8](https://github.com/spring-projects/spring-framework/commit/3c74cb803041c49931ac25cbfd913247814f3a30)
  - [83089e0](https://github.com/spring-projects/spring-framework/commit/83089e0eaf18b4c288132de68d44053aee83036e)
  - [e3647bc](https://github.com/spring-projects/spring-framework/commit/e3647bcd6c16e121e75fd7bc9d9669cfe34256db)
  - [4a057a7](https://github.com/spring-projects/spring-framework/commit/4a057a7287e876ea76afd0cdd7d30319c481d55c)
  - [c409419](https://github.com/spring-projects/spring-framework/commit/c4094192e97af9618a12149756d10dda8e6d271a)
  - [d484686](https://github.com/spring-projects/spring-framework/commit/d4846861af7df3e78a1fffbaba4f2ea7d99d12a1)
  - [883e79a](https://github.com/spring-projects/spring-framework/commit/883e79a2008b2931c931f6aabd515b9dd43f3907)
  - [504f3f2](https://github.com/spring-projects/spring-framework/commit/504f3f26a933ee7a99977ef96a54a17e3f51bae5)
  - [e1ae0c0](https://github.com/spring-projects/spring-framework/commit/e1ae0c065cf3c862ecce34b6418e880598b70321)

### 内容

We'd like to refactor some of our current AOT code to reduce coupling and to improve the generated code.

---

## Issue #28415: Add position variant of ObjectUtils.addObjectToArray

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28415

**関連リンク**:
- Commits:
  - [d97ae4a](https://github.com/spring-projects/spring-framework/commit/d97ae4ac52e7a2c024515aa0b58a9afb73ebb253)
  - [f3e6697](https://github.com/spring-projects/spring-framework/commit/f3e669754170d8617360fe3608b890aee482b444)
  - [f17372e](https://github.com/spring-projects/spring-framework/commit/f17372ebea338a474947beaabae61a6e71f4d678)
  - [b7b52b8](https://github.com/spring-projects/spring-framework/commit/b7b52b8076b6c4ce2c6285d43142ecd0510f7ddd)

### 内容

Currently `ObjectUtils.addObjectToArray` only allows you to add an element to the end of the array. With #28414 we need to add an element to the start.


---

## Issue #28416: Support multiple SpringFactoriesLoader files

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28416

**関連リンク**:
- Commits:
  - [103b911](https://github.com/spring-projects/spring-framework/commit/103b911fc43c0385c8cafbee5010c423c953392f)
  - [4cebd9d](https://github.com/spring-projects/spring-framework/commit/4cebd9d3926a0208ffdc28cea04243e8ed97f023)
  - [d30e6bf](https://github.com/spring-projects/spring-framework/commit/d30e6bf647348651c3b3fc95396e9985c5e3c283)
  - [58c441f](https://github.com/spring-projects/spring-framework/commit/58c441f9610b14569907059d5d0ca64975fe7653)
  - [3a83ec1](https://github.com/spring-projects/spring-framework/commit/3a83ec1aa8d330bafb53f1e613b18e34f23b29f7)
  - [b784dfe](https://github.com/spring-projects/spring-framework/commit/b784dfe4172d998d7eb96f268e4f92d82f2eafc3)
  - [dbc0a8c](https://github.com/spring-projects/spring-framework/commit/dbc0a8c8b61ac75729917ddb1921ac6d7ca6e571)

### 内容

For AOT we'd like to be able to load a `META-INF/spring/aot.factories` files rather than `META-INF/spring.factories`.

---

## Issue #28417: Add Throwable functional interfaces

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28417

**関連リンク**:
- Commits:
  - [d205b8b](https://github.com/spring-projects/spring-framework/commit/d205b8b78ae14842d7a95966dbf85cec9b769e5b)
  - [37a2b3a](https://github.com/spring-projects/spring-framework/commit/37a2b3ab02724293197285145f11c669e5fef94f)
  - [b3efdf3](https://github.com/spring-projects/spring-framework/commit/b3efdf3c2b5b55624164d184d237795be6e7b3b5)

### 内容

Within the framework and portfolio projects we often need to deal with checked exceptions inside the body of a `Function`, `Supplier`, `Consumer`, etc. This usually involves writing `try`/`catch` blocks inside the body. Since exception handling is usually also handled by the framework, it would be nice if we could offer `Throwing...` versions of common functional interfaces that do the wrapping for us.

### コメント

#### コメント 1 by quaff

**作成日**: 2022-05-05

Please consider throwing generic exception like this
```java
@FunctionalInterface
public interface CheckedFunction<T, R, E extends Throwable> {

	R apply(T t) throws E;

}
```

#### コメント 2 by sbrannen

**作成日**: 2022-05-05

@quaff, can you please expound on your proposal with a rationale for needing the generic type declaration for the exception?

#### コメント 3 by sbrannen

**作成日**: 2022-05-05

> it would be nice if we could offer `Throwing...` versions of common functional interfaces that do the wrapping for us.

I agree: such types can be very useful.

I also agree with the `Throwing*` naming convention. Though I noticed you've introduced `Throwable*` types in your commit.

I think we should go with `Throwing*`. For example, `ThrowableSupplier` implies that the supplier supplies a `Throwable`, like a `StringSupplier` would supply a `String`. 

Furthermore, the `Supplier` itself is not "throwable" since it does not implement `Throwable`.

What we're really talking about is a "supplier that is capable of throwing a checked exception", but we cannot convert that to a type name because it's simply too long: `CheckedExceptionThrowingSupplier`. If we go with `ThrowingSupplier`, that's succinct and in line with the naming convention used in several other open source projects -- for example, Spring Data, JUnit, AssertJ, Kotlin internals, [some JDK internals](https://twitter.com/sam_brannen/status/1431250271523459078), [etc.](https://www.google.com/search?q=%22ThrowingSupplier%22).




#### コメント 4 by quaff

**作成日**: 2022-05-06

> @quaff, can you please expound on your proposal with a rationale for needing the generic type declaration for the exception?

@sbrannen  For example we can throw Throwable inside lambda
```java
@Aspect
public class Instrumentation {

	@Around("execution(* *.*(..))")
	public Object timing(ProceedingJoinPoint pjp) throws Throwable {
		return Tracing.execute(pjp, ProceedingJoinPoint::proceed);
	}
}
```
```java
public class Tracing {
	public static <T, R> R execute(T input, CheckedFunction<T, R, Throwable> function) throws Throwable {
		// create new span
		try {
			return function.apply(input);
		} finally {
			// finish span
		}
	}
}

```

#### コメント 5 by quaff

**作成日**: 2022-05-06

> some JDK internals

Many projects use `Checked*`, for example `vavr` `elasticsearch`

#### コメント 6 by sbrannen

**作成日**: 2022-05-06

> @sbrannen For example we can throw Throwable inside lambda

The Spring Framework typically tries to avoid throwing `Throwable` because that makes error handling more complex, and we don't want to have to catch `Throwable` and then decide if the exception should really be swallowed/handled/rethrown (e.g., OOME).

The commit Phil pushed declares `Exception` in the `throws` clauses in order to allow lambdas to throw unchecked and checked `Exception` types, and I think that is adequate for the needs of the framework.

> Many projects use `Checked*`, for example `vavr` `elasticsearch`

Indeed, that would be another option, but we've gone with `Throwing*`.

---

## Issue #28418: Add RootBeanDefinition constructor that accepts a ResolvableType

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28418

**関連リンク**:
- Commits:
  - [e519079](https://github.com/spring-projects/spring-framework/commit/e5190796394dbbd00382342c7467e648342c3bda)
  - [b9ed2f9](https://github.com/spring-projects/spring-framework/commit/b9ed2f9a1be9c374ccb10b7c05b9352b8386c428)
  - [6c8de96](https://github.com/spring-projects/spring-framework/commit/6c8de96992865c6d40d050726a60fa9a301b1ed8)
  - [65d43c7](https://github.com/spring-projects/spring-framework/commit/65d43c79c6c10e828c2ee657946b1bcb3bc955f2)
  - [d31eb4c](https://github.com/spring-projects/spring-framework/commit/d31eb4c0f14518e52bc55e2d23e4e6779d303911)

### 内容

Needing to use a builder in order to create a `RootBeanDefinition` with a `ResolvableType` is cumbersome. A new constructor would help simplify things, especially AOT generated code.

---

## Issue #28421: Add byte[] to supported types in SimpleJmsHeaderMapper

**状態**: closed | **作成者**: artembilan | **作成日**: 2022-05-05

**ラベル**: in: messaging, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/28421

**関連リンク**:
- Commits:
  - [12357fd](https://github.com/spring-projects/spring-framework/commit/12357fdf44f31c1f4aced29eeeb2784a8d6ffd62)

### 内容

See more info in the https://github.com/spring-projects/spring-integration/issues/3788 and its related PR.

For consistency it is better to have a good interoperability between Spring JMS and Spring Integration.


---

## Issue #28425: Remove obsolete SpEL expression grammar file

**状態**: closed | **作成者**: superdc | **作成日**: 2022-05-08

**ラベル**: type: task, in: core

**URL**: https://github.com/spring-projects/spring-framework/issues/28425

**関連リンク**:
- Commits:
  - [da112a7](https://github.com/spring-projects/spring-framework/commit/da112a7ea82fee786a309f24baeda57d15478ff7)

### 内容

Can you provide a SpEL expression grammar file for antlr4 as known as `SpringExpression.g4`?

### コメント

#### コメント 1 by superdc

**作成日**: 2022-05-08

@sbrannen need help 

#### コメント 2 by sbrannen

**作成日**: 2022-05-09

I am not aware of any formal grammar file for SpEL.

@aclement, please correct me if I'm wrong about that.

#### コメント 3 by superdc

**作成日**: 2022-05-09

@snicoll can you provide a spring expression language grammer file(https://github.com/spring-projects/spring-framework/blob/main/spring-expression/src/main/resources/org/springframework/expression/spel/generated/SpringExpressions.g) of anltr4，the grammer of this version is not suitable for antlr4

#### コメント 4 by sbrannen

**作成日**: 2022-05-09

The grammar file has apparently been around for a long time (unmodified):

https://github.com/spring-projects/spring-framework/blob/3.2.x/spring-expression/src/main/java/org/springframework/expression/spel/generated/SpringExpressions.g

Reopening to allow @aclement to elaborate on where `SpringExpressions.g` came from.

#### コメント 5 by sbrannen

**作成日**: 2022-05-10

As explained in commit da112a7ea82fee786a309f24baeda57d15478ff7:

> The antlr-based SpEL expression grammar file (`SpringExpressions.g`) was introduced during initial development and prototyping of the Spring Expression language; however, it was quickly abandoned in favor of a handcrafted implementation. Consequently, it has become obsolete over time and has never been actively maintained.

Since the grammar file is not used with the Spring Framework itself, the team has no plans to maintain it or release a new version compatible with later versions of antlr.

In light of that, I have repurposed this issue to remove the obsolete SpEL expression grammar file.


#### コメント 6 by superdc

**作成日**: 2022-05-10

> As explained in commit [da112a7](https://github.com/spring-projects/spring-framework/commit/da112a7ea82fee786a309f24baeda57d15478ff7):
> 
> > The antlr-based SpEL expression grammar file (`SpringExpressions.g`) was introduced during initial development and prototyping of the Spring Expression language; however, it was quickly abandoned in favor of a handcrafted implementation. Consequently, it has become obsolete over time and has never been actively maintained.
> 
> Since the grammar file is not used with the Spring Framework itself, the team has no plans to maintain it or release a new version compatible with later versions of antlr.
> 
> In light of that, I have repurposed this issue to remove the obsolete SpEL expression grammar file.

@sbrannen So now SpEL is not antlr-based，right？parser and lexer are produced by handcraft?

#### コメント 7 by sbrannen

**作成日**: 2022-05-10

> @sbrannen So now SpEL is not antlr-based，right？parser and lexer are produced by handcraft?

That's correct. 

Take a look at `org.springframework.expression.spel.standard.InternalSpelExpressionParser` and the types in the `org.springframework.expression.spel.ast` package for details.


#### コメント 8 by superdc

**作成日**: 2022-05-11

> > @sbrannen So now SpEL is not antlr-based，right？parser and lexer are produced by handcraft?
> 
> That's correct.
> 
> Take a look at `org.springframework.expression.spel.standard.InternalSpelExpressionParser` and the types in the `org.springframework.expression.spel.ast` package for details.

@sbrannen  Can I know the reasons why SpEL turns into not antlr-based？We want to parse SpEL in frontend and construct our custom ast tree. One method is used antlr4 to generate parser, lexer and visitor，but now this method looks impractical.

#### コメント 9 by sbrannen

**作成日**: 2022-05-11

> Can I know the reasons why SpEL turns into not antlr-based?

I was not the original developer of the Spring Expression language, but as far as I understand, using antlr turned out to be too cumbersome. Thus, the original developer, @aclement, decided it would be easier to handcraft the support. 

#### コメント 10 by deanmaster

**作成日**: 2024-01-29

hello @sbrannen we have intention to build tooling support for projects to expresison their own needs in more friendly and controllable way. 

1. Using antlr4 would help a lot since it can support code completion from many platforms.
2. If you don't use it any suggestion for testing a dedicate expression if it's working ? from unit test point of view.

Thanks a lot,
Tuan Do

#### コメント 11 by sbrannen

**作成日**: 2024-02-01

> If you don't use it any suggestion for testing a dedicate expression if it's working ? from unit test point of view.

You can use the tests in our test suite for inspiration -- for example, any of the tests in [`src/test/java`](https://github.com/spring-projects/spring-framework/tree/main/spring-expression/src/test/java/org/springframework/expression/spel) in the `spring-expression` project, in particular [`EvaluationTests`](https://github.com/spring-projects/spring-framework/blob/main/spring-expression/src/test/java/org/springframework/expression/spel/EvaluationTests.java).



#### コメント 12 by deanmaster

**作成日**: 2024-06-28

hello @sbrannen ,

Currently i'm implementation an autocompletion for SpEl in our project. Do you know how can I "extracted" from existing code? Or I have to manually create the grammar on my own ? Because everything in the package org.springframework.expression are basically java form which can't convert to any syntax which can be used to return as autocompletion suggestion.

Any suggestions are really helpful for me.

Thanks,
Tuan Do

#### コメント 13 by sbrannen

**作成日**: 2024-06-28

Hi @deanmaster,

> Do you know how can I "extracted" from existing code?

I doubt there is any way to _extract_ the grammar automatically from the code, since the lexing and parsing is now handwritten.

The classes you'll need to look at are `Tokenizer`, `TokenKind`, and `InternalSpelExpressionParser` in the `org.springframework.expression.spel.standard` package.

Those classes sometimes refer to the original antlr grammar in comments.

> Or I have to manually create the grammar on my own ?

Yes, I think you'll basically have to create your own grammar from scratch, but you can probably use the [original antlr grammar](https://github.com/spring-projects/spring-framework/blob/3.2.x/spring-expression/src/main/java/org/springframework/expression/spel/generated/SpringExpressions.g) as a starting point.

#### コメント 14 by deanmaster

**作成日**: 2024-07-11

thanks @sbrannen 

I successfully migrated the original antlr grammar. Thanks for pointing to those classes I will have a look.

#### コメント 15 by jakeboone02

**作成日**: 2024-08-27

@deanmaster I was curious if you've made any significant progress with your antlr4 grammar. I'd be willing to pitch in if you want help; I have a use case in my [`react-querybuilder`](/react-querybuilder/react-querybuilder) project where I'm currently using [`spel2js`](/benmarch/spel2js) (an old JavaScript port) but would like to move to a static grammar file.

#### コメント 16 by deanmaster

**作成日**: 2024-08-28

@jakeboone02 i'm able to convert the grammar file to latest v4 ANTLR but obviously it does not reflects newest "java syntax" with current version of SpEl. We are pending this topic for now. In the future when i'm able to complete the grammarfile I can share it here

---

## Issue #28442: Add native hints for core annotations

**状態**: closed | **作成者**: philwebb | **作成日**: 2022-05-10

**ラベル**: type: enhancement, theme: aot

**URL**: https://github.com/spring-projects/spring-framework/issues/28442

**関連リンク**:
- Commits:
  - [2961426](https://github.com/spring-projects/spring-framework/commit/2961426d8ad256983ffe1445acd4cbfaab4fd5db)
  - [e7e60f7](https://github.com/spring-projects/spring-framework/commit/e7e60f7cb9c73339294e3f078fe722ca28d49b44)

### 内容

In order to support native applications we need [hints for our core annotations](https://github.com/spring-projects-experimental/spring-native/blob/main/spring-native-configuration/src/main/java/org/springframework/core/annotation/CoreAnnotationHints.java).

---

