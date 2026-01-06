# Document how to migrate usage of EnableBatchProcessing(modular = true) to v6

**Issue番号**: #5072

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-11-02

**ラベル**: in: documentation, type: task

**URL**: https://github.com/spring-projects/spring-batch/issues/5072

## 内容

This is related to #4866. The goal is to document how to migrate the use of `EnableBatchProcessing(modular = true)` to  Spring's context hierarchies and `GroupAwareJob`s (as mentioned in the javadoc of `EnableBatchProcessing`).

cc @kzander91 (who provided a starting point in https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3478015935, thank you for that!)


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-19

Added example here: https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide#changes-related-to-the-modular-batch-configurations-through-enablebatchprocessingmodular--true

### コメント 2 by kzander91

**作成日**: 2025-11-25

@fmbenhassine I just had a chance to take a look at the example, and I find it a bit lacking:
* The old, modular implementation was also managing the lifecycle of the child contexts, properly shutting everything down when the parent context was closed. I would now have to reimplement that myself.
* Previously, through the parent context's `JobLocator`, I was able to retrieve the child context's `Job` by name. This is now no longer possible and my logic that is launching jobs would somehow need to get a hold of the child contexts... Especially this issue is I believe also relevant for @marbon87's [case in their app](https://github.com/spring-projects/spring-batch/issues/4866#issuecomment-3575452892).

I feel like the only proper migration path for all but the simplest of apps is either to _not_ use separate contexts and define all Job's in a shared context (likely they way I will be going), or to copy-paste Spring Batch's implementation from the previous version.

### コメント 3 by fmbenhassine

**作成日**: 2025-12-08

@kzander91 Thank you looking into that and for your feedback!

> * The old, modular implementation was also managing the lifecycle of the child contexts, properly shutting everything down when the parent context was closed. I would now have to reimplement that myself.

That feature is already implemented in Spring Boot and was duplicated in Spring Batch for no reason. Have you tried `new SpringApplicationBuilder(ParentConfig.class).child(ChildConfig.class).run(args);` from Boot? This will handle the lifecycle of the contexts for you.

>  Previously, through the parent context's JobLocator, I was able to retrieve the child context's Job by name. This is now no longer possible and my logic that is launching jobs would somehow need to get a hold of the child contexts

I think that that was due to #5122 which I already fixed and planned for the upcoming v6.0.1. With that fix in place, the `MapJobRegistry` can be populated with jobs from all contexts and the registration will be based on the job names (which should be globally unique anyway) and not the bean name (which could be the same in child contexts).

---

Another option I forgot about is using Spring profiles. I believe this is suitable for this kind of setup. Have you tried that approach? I can help with an example here as well. Just let me know if you need support on that.


### コメント 4 by kzander91

**作成日**: 2025-12-08

> Have you tried new `SpringApplicationBuilder(ParentConfig.class).child(ChildConfig.class).run(args);` from Boot?

I have, but that doesn't really work in my scenario, because I'm running an embedded Tomcat in my parent context, which Spring Boot doesn't support: https://github.com/spring-projects/spring-boot/blob/1c0e08b4c434b0e77a83098267b2a0f5a3fc56d7/core/spring-boot/src/main/java/org/springframework/boot/builder/SpringApplicationBuilder.java#L207-L210
Now I _could_ put the rest of my project in another child context, but again in both of these cases I wouldn't be able to see the Job beans from the child or sibling contexts (I'm launching jobs by name from a central service bean, and that bean thus needs to know all Jobs).

> With that fix in place, the `MapJobRegistry` can be populated with jobs from all contexts

I don't think that's true. Parent contexts are not aware of their child contexts, it's a unidirectional relationship (unless I'm missing something). `MapJobRegistry` _could_ get Job beans from its own _and its parent context(s)_, but it isn't because it's using `getBeansOfType()` which isn't considering beans from parent contexts: https://github.com/spring-projects/spring-batch/blob/088487bb803c6a7a9139228ea973035a1698d864/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/support/MapJobRegistry.java#L63-L66
Docs of `getBeansOfType()`: https://github.com/spring-projects/spring-framework/blob/b038beb85490c8a80711b1a6c8cfffbb21276b3e/spring-beans/src/main/java/org/springframework/beans/factory/ListableBeanFactory.java#L267-L269
But in any case: This would only find beans from the context that `MapJobRegistry` is running in and its parent(s), but not children/siblings.

> Another option I forgot about is using Spring profiles.

Are you talking about putting all beans in a single context and guarding each job's configuration with a profile? 🤔 I don't really see how this would help. At runtime, my app needs to know all Jobs anyways and so would need to enable all these profiles...

### コメント 5 by fmbenhassine

**作成日**: 2025-12-09

> that doesn't really work in my scenario, because I'm running an embedded Tomcat in my parent context, which Spring Boot doesn't support

OK I see. The fact that you are embedding Tomcat in the parent context is an important detail, which was not mentioned in your initial request nor present in the minimal example you shared (all my previous answers were based on the assumption that you have a non-web setup). But no problem, I will provide guidance for your case.

First thing: modularisation of Spring contexts to avoid bean name clashes is definitely NOT a Spring Batch concern. Trying to do this in Spring Batch with `EnableBatchProcessing(modular = true)` or any other way would definitely lead to an overly complex code to maintain or at best, worse than any solution provided by Spring Framework or Spring Boot. And BTW, this problem is not specific to Spring Batch per se, and could be encountered in any other project where users can define project-specific named artefacts as Spring beans (Like integration flows in Spring Integration or shell commands in Spring Shell, etc).

Now the fact that Spring Boot does not support your use case becomes a Spring Boot issue, not a Spring Batch issue. And more importantly, I believe it is this setup of running several batch jobs in a servlet container within a single JVM that makes things difficult (I personally never recommended that setup, and always promoted the "single job per context per jar" packaging/deployment model). That monolithic model was used in Spring Batch Admin which had several issues that led the project to be deprecated in favor of the modular approach in SCDF (see issues and migration recommendations [here](https://github.com/spring-attic/spring-batch-admin/blob/master/MIGRATION.md)).

That said, you can still continue to use the web model you have, but you definitely need a smarter job registry than the one provided by Spring Batch. 

> Parent contexts are not aware of their child contexts, it's a unidirectional relationship (unless I'm missing something). MapJobRegistry could get Job beans from its own and its parent context(s), but it isn't because it's using getBeansOfType() which isn't considering beans from parent contexts

I am open to making `MapJobResgitry` smarter to handle bidirectional relationships if this does not break things for most typical use cases. But if this will make the code on the framework side overly complex for a very specific use case, then I would leave that to users to provide their own custom smart registry. I always try to control how much accidental complexity goes in the framework (which is one of the main themes of v6 BTW).

> Are you talking about putting all beans in a single context and guarding each job's configuration with a profile? 🤔 I don't really see how this would help. At runtime, my app needs to know all Jobs anyways and so would need to enable all these profiles...

Please forget about profiles for your use case, it won't work with a web setup. As mentioned, I was assuming a non-web setup and thought you would spin up each job in its own context/JVM, and in which case you would specify the profile at startup to only load the bean definitions for that specific job.

---

Looking forward to your feedback and if I can help further.


### コメント 6 by kzander91

**作成日**: 2025-12-10

Thank you for your continued input and your explanations! 🙏

> The fact that you are embedding Tomcat in the parent context is an important detail, which was not mentioned in your initial request nor present in the minimal example you shared

True, sorry about that. I wasn't aware that this particular detail would be an issue (and therefore relevant), I just found out about that limitation when trying your suggestion with Boot's `SpringApplicationBuilder#child`.

> Looking forward to your feedback

Given the additional context and reasoning you provided I can understand better _why_ you have decided to remove that support. Before, it just seemed that a feature that was working perfectly fine (and on the surface didn't appear to be _that_ complex) was "just" removed to reduce complexity.

Regarding the other points, I want to say again (see https://github.com/spring-projects/spring-batch/issues/5126#issuecomment-3611770749) that I have already refactored my app to define all jobs in a single context.
Thus, I _personally_ have no further need for migration help regarding the removed support for modularized contexts and am fine with stopping things here.

For others that are considering doing the same: I basically just removed my `ApplicationContextFactory` beans and adjusted my root component scan to include all my job configurations.
Inside those, I renamed beans to ensure that no bean name clashes exist.
A few additional adjustments were needed in some places that are specific to my particular app, so YMMV.

