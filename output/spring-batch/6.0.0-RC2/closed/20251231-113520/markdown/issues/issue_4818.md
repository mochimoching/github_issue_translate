# Use contextual lambdas to configure batch artefacts

**Issue番号**: #4818

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-04-28

**ラベル**: in: infrastructure, type: feature, related-to: item-readers-writers

**URL**: https://github.com/spring-projects/spring-batch/issues/4818

**関連リンク**:
- Commits:
  - [24a464f](https://github.com/spring-projects/spring-batch/commit/24a464fab859008ec54e7de34915f29d71763b3b)

## 内容

This request is about improving the builders of item readers and writers to use Lambdas for configuration options:

Current API:

```java
var reader = new FlatFileItemReaderBuilder()
 .resource(...)
 .delimited()
 .delimiter(",")
 .quoteCharacter('"')
 ...
 .build();
```

Proposal:

```java
var reader = new FlatFileItemReaderBuilder()
 .resource(...)
 .delimited ( config -> config.delimiter(',').quoteCharcter( '"' ))
 ...
 .build();
```

cc @joshlong



## コメント

### コメント 1 by kwondh5217

**作成日**: 2025-04-29

Hi @fmbenhassine,

This looks like a great improvement!
I would love to work on this issue. Could you please assign it to me if that's fine?

### コメント 2 by fmbenhassine

**作成日**: 2025-05-06

@kwondh5217 Sure! Thank you for your offer to help!

I believe Spring Security pioneered this configuration approach in the portfolio, so you can take a look there for inspiration.

### コメント 3 by kwondh5217

**作成日**: 2025-05-06

Hi @fmbenhassine, thank you for your guidance earlier!

I’d like to clarify the intended direction of the enhancement.

From what I understand, the idea is not just to support lambda-based configuration in FlatFileItemReaderBuilder, but to establish a general DSL-style configuration approach across all ItemReader and ItemWriter builders.

Would you recommend introducing a shared abstraction (e.g. a ConfigurerAwareBuilder base class similar to AbstractConfiguredSecurityBuilder in Spring Security) to support this pattern?

Also, in terms of behavior:

Should we throw an exception when both chaining and lambda styles are used?

Or should we allow overriding?

Or should we allow both and apply in order?

I want to align with the broader design direction before proceeding. Thank you again for your support.

### コメント 4 by fmbenhassine

**作成日**: 2025-05-08

I don't think we need new builders. My initial thinking was about adding new methods to existing builders that accept `Consumer<Spec>`, similar to the one in SF here: https://github.com/spring-projects/spring-framework/blob/main/spring-beans/src/main/java/org/springframework/beans/factory/BeanRegistry.java#L96

Here is also the original issue in Spring Security: https://github.com/spring-projects/spring-security/issues/5557

So we can imagine new configuration specifications like `DelimitedSpec`, `FixedLengthSpec`, etc and use them in current builders.

### コメント 5 by kwondh5217

**作成日**: 2025-05-08

Thanks for the detailed guidance @fmbenhassine !
The direction is clear now. I’ll proceed with adding Consumer<Spec>-based configuration methods to the existing builders using DelimitedSpec and FixedLengthSpec style objects as discussed.

I’ll share a draft PR soon for feedback. Appreciate your support!

### コメント 6 by kwondh5217

**作成日**: 2025-05-12

Hi @fmbenhassine,
I’ve submitted a pull request that addresses this issue.
Could you take a look? 🙇‍♂️
Thank you !

### コメント 7 by kwondh5217

**作成日**: 2025-10-31

Hi @fmbenhassine,
I’ve submitted a new pull request.
Could you take a look? 🙇‍♂️
Thank you !

