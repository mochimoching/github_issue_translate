# improve experience when configuring an alternative `JobRepository` 

**Issue番号**: #4718

**状態**: closed | **作成者**: joshlong | **作成日**: 2024-11-24

**ラベル**: type: bug, in: core, api: breaking-change

**URL**: https://github.com/spring-projects/spring-batch/issues/4718

**関連リンク**:
- Commits:
  - [f7fcfaa](https://github.com/spring-projects/spring-batch/commit/f7fcfaa4fdb1f762a3bc16c30750d646dc52a6ed)

## 内容

improve experience when configuring an alternative `JobRepository`, as the DefaultBatchConfiguration, upon which Spring Boot in turn relies, assumes only JDBC-based infrastructure. This means that, when using Spring Boot, you can't simply replace one bean of type `JobRepository` and have things work. Everything must be redone from scratch, as we used to do before Spring Boot existed.  

This will be a problem for users of Spring Batch who want to avail themselves of the new "resourceless" and MongoDB job repository alternatives.

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2024-12-03

`@EnableBatchProcessing` (and in turn `DefaultBatchConfiguration`) was designed as the Java counterpart of the XML element `job-repository` from the batch namespace where a datasource is required:

```xml
<batch:job-repository id="jobRepository" data-source="dataSource" transaction-manager="transactionManager"/>
```

So yes, `@EnableBatchProcessing` assumes a JDBC infrastructure, and this should change now that we introduced the mongo job repository and the resourceless job repository.

I have a couple ideas on how we can address this issue and of course I am open to any thoughts about this as well. I will share these ideas with the community when we start working on this design issue for the next major release. This comment is only to validate and acknowledge the issue. Thank you for reporting it, @joshlong !

### コメント 2 by krewetka

**作成日**: 2025-03-10

Hi @fmbenhassine as proper fix is planned for next major version is there any earlier workaround solution? 🤔 

I mean especially to overcome shutdown problem. It is quite a  big deal to be honest for production usage and as fixing it not in 5.3 but in 6 seems like it will be not fixed for at least few years 🤔 

Unless we simply are doing something wrong but we didn't manage to configure proper shutdown despite many attempts .

We moved from starting the job in regular container to starting it with AWS batch so at least regular CI/CD deployment is not breaking long running jobs but let's say it is only workaround we found.

### コメント 3 by fmbenhassine

**作成日**: 2025-03-11

@krewetka which shutdown problem are you referring to? How is that related to this issue? Please open a separate [discussion](https://github.com/spring-projects/spring-batch/discussions) to explain your problem and I will be happy to help there.

FTR, v6 is planned for November this year and there is no plan for v5.3 at the moment. In the meantime and for those who want to use a non-jdbc job repository with v5.2, please check this [SO thread](https://stackoverflow.com/a/79492398/5019386) in which I attached a complete example.

### コメント 4 by krewetka

**作成日**: 2025-03-12

Hi, sorry my bad. I am referring to https://github.com/spring-projects/spring-batch/issues/4728#issuecomment-2578356238 which was marked as duplicate of this issue.  Should I still open another one then?🤔

We have mongo setup running properly (but with H2 still there).

We did try to exclude DataSourceAutoConfiguration.class but then we were still facing some issues but let me try again one more time and see the exact results.

### コメント 5 by fmbenhassine

**作成日**: 2025-03-12

@krewetka 

> Should I still open another one then?

Yes please. The shutdown lifecycle issue is different than requiring h2 for a mongo setup.

### コメント 6 by krewetka

**作成日**: 2025-03-12

Ok, will try to provide full example in new issue when it comes to shutdown. Maybe it will be solved when I manage to get rid of h2 in my code finally 🤞 

Btw, I checked  [SO thread](https://stackoverflow.com/a/79492398/5019386)  and noticed it is not using `EnableBatchProcessing`

We have it in our code still and when we remove H2 we are facing:
`Error creating bean with name 'jobExplorer': Cannot resolve reference to bean 'dataSource' while setting bean property 'dataSource'`
with added:`@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`

I guess we need to not use `EnableBatchProcessing` then but still somehow setup somewhere almost all other piecies from it like `tablePrefix` , `isolationLevelForCreate` , `taskExecutorRef` etc.

Do you have any recommendation for it how do to proper workaround for the time-being? 

I did copy of EnableBatchProcessing  with ` String dataSourceRef() default "";` and used this one but there are imports on not public packages  like `AutomaticJobRegistrarBeanPostProcessor` and  `BatchRegistrar` ( which then define `registerJobExplorer` ) etc. which I could not keep in custom version.

I skiped them and it seems to work and the jobs are run but not sure if this is good idea as some important parts of sprint batch internal logic are not missing ( for example jobExplorer is not wired-up) 🤔 

After doing it I realized that it can be even still with `String dataSourceRef() default "dataSource";` as it is not used anymore when there is no import of `BatchRegistrar` which is creating jobExplorer 😆 

### コメント 7 by fmbenhassine

**作成日**: 2025-05-21

@krewetka Thank you for your feedback, really appreciated! I understand, that's confusing. And I must admit that the default configuration of Spring Batch is not ideal, especially after the introduction of the resourceless job repository and the mongo job repository. I believe the introduction of these two new implementations has made the issues with previous design decisions more visible (ie the fact the default batch configuration assumes a JDBC infrastructure, the requirement of a `JobExplorer`, etc).

I started working on the next major release and wanted to share a few things:

- When using a `ResourcelessJobRepository`, there are no metadata to explore (there is no `ResourcelessJobExplorer`, this does not make sense). Therefore, the default batch configuration should not require a `JobExplorer`. This was fixed in https://github.com/spring-projects/spring-batch/issues/4825
- With Spring Boot, using `ResourcelessJobRepository` or `MongoJobRepository` should not require the user to exclude `DataSourceAutoConfiguration` or have to add a dependency to H2 or HSQLDB. Therefore, I think the resourceless job repository is a better default than the JDBC one in Spring Boot. I will discuss that with the Boot team.
- `EnableBatchProcessing` should not be tied to a JDBC infrastructure (this is historical, see my [previous comment](https://github.com/spring-projects/spring-batch/issues/4718#issuecomment-2514623019)). Therefore, all attributes related to the configuration of the JDBC job repository should be moved elsewhere. My idea is to follow the same approach of configuring Spring Security's session store with `@EnableJdbcHttpSession`, `@EnableRedisHttpSession`, etc. We could have the same for Spring Batch with `@EnableJdbcJobRepository`, `@EnableMongoJobRepository`, etc where each annotation have specific attributes to configure the metadata store.

And more generally, and after gathering feedback from the community over the years, I believe we need to simplify the API "surface" that batch users have to deal with. Currently, there are many different APIs to do the same things, which is confusing. I will open a separate issue for that with more details.

