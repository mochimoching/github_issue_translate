# Spring Framework GitHub Issues

取得日時: 2025年12月31日 13:46:42

取得件数: 4件

---

## Issue #27837: StrictHttpFirewall rejects request when HtmlUnit WebClient is called with encoded URL

**状態**: closed | **作成者**: thuri | **作成日**: 2021-12-18

**ラベル**: in: test, type: bug

**URL**: https://github.com/spring-projects/spring-framework/issues/27837

**関連リンク**:
- Commits:
  - [9346c89](https://github.com/spring-projects/spring-framework/commit/9346c89f5c215456167799159ca5a8150762855d)
  - [3477ec0](https://github.com/spring-projects/spring-framework/commit/3477ec0a35c5d19d55431f756cc9c6056ee788da)

### 内容

**Affects:** 5.3.13

---

I'm trying to run a unit test on my spring boot project using the HtmlUnit Webclient. 
The test does a POST Request submitting form data to the Controller which will create a database entry and send a redirect to the client. The response will contain a URL in the Location header which will be encoded if necessary.

Everything works fine until the HtmlUnit Webclient tries to follow the redirect and the `org.springframework.security.web.firewall.StrictHttpFirewall.getFirewalledRequest(HttpServletRequest)` method is called which prevents the request from being processed. It complains about the % in the URL (see stack trace).

But when running the application and using an actual browser the problem does not occur. Searching the web I found #16067 which first looked familiar.

So I wrote a small [project](https://github.com/thuri/encoded-uri-test) to reproduce the issue, and I think that the problem with HtmlUnit WebClient is a little bit different. 

When running the `webClientTestStringWithEncoding` test method and debugging into `org.springframework.security.web.firewall.StrictHttpFirewall#rejectedBlocklistedUrls(HttpServletRequest)`, one can see that `request.getServletPath()` still contains the encoded path while the called method `decodedUrlContains` seems to expect that it has been decoded.

If you run the `mockMvcTestURI` test method and debug the same line you can see that `request.getServletPath()` is empty but `request.getPathInfo()` contains an decoded path. `request.getRequestURI()` contains the encoded path in both cases.

In case you're wondering why the first test uses the webclient and the other one the mockMvc: I didn't find a way to pass either the encoded URL or the unencoded version (with spaces and an Umlaut) to the HtmlUnit Webclient (as you can see by the other test methods)

Perhaps the problem lies in the `org.springframework.test.web.servlet.htmlunit.HtmlUnitRequestBuilder.buildRequest(ServletContext)` where the `servletPath` is set on the request and should be decoded. 

I think I can work around that issue in my test but would be happy if you could have a look at this. 

Thanks in advance,
Michael

```stacktrace
java.io.IOException: org.springframework.security.web.firewall.RequestRejectedException: The request was rejected because the URL contained a potentially malicious String "%"
	at org.springframework.test.web.servlet.htmlunit.MockMvcWebConnection.getResponse(MockMvcWebConnection.java:152)
	at org.springframework.test.web.servlet.htmlunit.MockMvcWebConnection.getResponse(MockMvcWebConnection.java:134)
	at org.springframework.test.web.servlet.htmlunit.DelegatingWebConnection.getResponse(DelegatingWebConnection.java:79)
	at com.gargoylesoftware.htmlunit.WebClient.loadWebResponseFromWebConnection(WebClient.java:1596)
	at com.gargoylesoftware.htmlunit.WebClient.loadWebResponse(WebClient.java:1518)
	at com.gargoylesoftware.htmlunit.WebClient.getPage(WebClient.java:493)
	at com.gargoylesoftware.htmlunit.WebClient.getPage(WebClient.java:413)
	at com.gargoylesoftware.htmlunit.WebClient.getPage(WebClient.java:548)
	at com.gargoylesoftware.htmlunit.WebClient.getPage(WebClient.java:529)
	at io.gitlab.thuri.spring.htmlunit.TestWithEncodedUriIssue.webClientTestStringWithEncoding(TestWithEncodedUriIssue.java:63)
	// cut junit and eclipse stacktrace entries
Caused by: org.springframework.security.web.firewall.RequestRejectedException: The request was rejected because the URL contained a potentially malicious String "%"
	at org.springframework.security.web.firewall.StrictHttpFirewall.rejectedBlocklistedUrls(StrictHttpFirewall.java:463)
	at org.springframework.security.web.firewall.StrictHttpFirewall.getFirewalledRequest(StrictHttpFirewall.java:429)
	at org.springframework.security.web.FilterChainProxy.doFilterInternal(FilterChainProxy.java:196)
	at org.springframework.security.web.FilterChainProxy.doFilter(FilterChainProxy.java:183)
	at org.springframework.web.filter.DelegatingFilterProxy.invokeDelegate(DelegatingFilterProxy.java:358)
	at org.springframework.web.filter.DelegatingFilterProxy.doFilter(DelegatingFilterProxy.java:271)
	at org.springframework.mock.web.MockFilterChain.doFilter(MockFilterChain.java:134)
	at org.springframework.web.filter.RequestContextFilter.doFilterInternal(RequestContextFilter.java:100)
	at org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:119)
	at org.springframework.mock.web.MockFilterChain.doFilter(MockFilterChain.java:134)
	at org.springframework.web.filter.FormContentFilter.doFilterInternal(FormContentFilter.java:93)
	at org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:119)
	at org.springframework.mock.web.MockFilterChain.doFilter(MockFilterChain.java:134)
	at org.springframework.web.filter.CharacterEncodingFilter.doFilterInternal(CharacterEncodingFilter.java:201)
	at org.springframework.web.filter.OncePerRequestFilter.doFilter(OncePerRequestFilter.java:119)
	at org.springframework.mock.web.MockFilterChain.doFilter(MockFilterChain.java:134)
	at org.springframework.test.web.servlet.MockMvc.perform(MockMvc.java:199)
	at org.springframework.test.web.servlet.htmlunit.MockMvcWebConnection.getResponse(MockMvcWebConnection.java:149)
	... 78 more
```

### コメント

#### コメント 1 by rstoyanchev

**作成日**: 2022-01-05

`HtmlUnitRequestBuilder` does not seem to support well URLs with encoded paths, including paths that are not encoded but become encoded when HtmlUnit's `WebClient` prepares a `java.net.URL`. The problem, as you pointed out, is that the servletPath is supposed to be decoded, but `HtmlUnitRequestBuilder` essentially [uses the full path](https://github.com/spring-projects/spring-framework/blob/338f8907ac752718b9432ca268d9e6de25cba705/spring-test/src/main/java/org/springframework/test/web/servlet/htmlunit/HtmlUnitRequestBuilder.java#L411) minus any contextPath, and without further decoding.

One reason this might not have failed as much is that Boot apps have alwaysUseFullPath set by default so effectively the servletPath is not used for mapping purposes, so only Spring Security's firewall is affected.

I think this can be corrected. I don't see another alternative, and hopefully it shouldn't cause issues since the servletPath is not often used for mapping purposes and in any case it should be decoded.

---

## Issue #27878: Upgrade to Kotlin Coroutines 1.6.0

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-01-03

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27878

**関連リンク**:
- Commits:
  - [a410f4c](https://github.com/spring-projects/spring-framework/commit/a410f4c0f2f9ce10eefd1f7141739d362730cd61)

### 内容

_本文なし_

---

## Issue #27879: Upgrade to Kotlin serialization 1.3.2

**状態**: closed | **作成者**: sdeleuze | **作成日**: 2022-01-03

**ラベル**: type: dependency-upgrade

**URL**: https://github.com/spring-projects/spring-framework/issues/27879

**関連リンク**:
- Commits:
  - [0b8c815](https://github.com/spring-projects/spring-framework/commit/0b8c815c6f9da128ed472b3bb40b5fe4eff18d21)

### 内容

_本文なし_

---

## Issue #27903: Stop defining a TaskScheduler bean in WebSocketConfigurationSupport

**状態**: closed | **作成者**: wilkinsona | **作成日**: 2022-01-07

**ラベル**: in: web, type: enhancement

**URL**: https://github.com/spring-projects/spring-framework/issues/27903

**関連リンク**:
- Commits:
  - [29fe109](https://github.com/spring-projects/spring-framework/commit/29fe1094403264c4f9583619fdd9e904fc463e8c)
  - [3682019](https://github.com/spring-projects/spring-framework/commit/368201975a0b9e65b051a71d0894783bcbc4c593)

### 内容

**Affects:** 5.3.x

`WebSocketConfigurationSupport` defines a `TaskScheduler` bean which causes [problems in Boot](https://github.com/spring-projects/spring-boot/issues/28449) as using `@EnableWebSocket` causes auto-configuration of a `ThreadPoolTaskScheduler` to back off, for example. My feeling is that this a very general contract for something that's more specific and largely an implementation detail. It would be helpful to Boot if Framework's WebSocket support could avoid defining a bean at all for its task scheduler or could use a different, WebSocket-specific type to do so.

While this affects 5.3.x, [we think](https://github.com/spring-projects/spring-boot/issues/28449#issuecomment-952632352) it may be a change that can't be made till 6.0.

---

