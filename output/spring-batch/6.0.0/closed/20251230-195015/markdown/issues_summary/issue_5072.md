*このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月5日に生成されました。*

# Issue #5072: モジュラーバッチ設定(EnableBatchProcessing modular=true)の移行ガイド

## 課題概要

Spring Batch 6.0で`@EnableBatchProcessing(modular = true)`が廃止されたため、この機能を使用していたユーザーのために、Springのコンテキスト階層と`GroupAwareJob`への移行方法をドキュメント化するタスクです。

**モジュラーバッチ設定とは**: 複数のジョブ定義を別々のSpringコンテキスト(子コンテキスト)に分離し、Bean名の衝突を避ける機能です。

## 原因と背景

Spring Batch 5.xまでは、複数のジョブで同じBean名を使用する際の衝突を避けるため、モジュラー設定が提供されていました。しかし、この機能はSpring BootやSpring Frameworkの標準機能と重複しており、保守コストが高いため廃止されました。

## 対応方針

### 移行オプション

#### オプション1: Springのコンテキスト階層を使用
```java
// 親コンテキスト設定
@Configuration
public class ParentConfig {
    @Bean
    public DataSource dataSource() {
        // 共通データソース
        return new HikariDataSource();
    }
    
    @Bean
    public JobRepository jobRepository() {
        // 共通ジョブリポジトリ
        return new JdbcJobRepositoryFactoryBean()
            .getObject();
    }
}

// 子コンテキスト1
@Configuration
public class Job1Config {
    @Bean
    public Job job1(JobRepository jobRepository) {
        return new JobBuilder("job1", jobRepository)
            .start(step1())
            .build();
    }
    
    @Bean
    public Step step1() {
        // Job1専用のStep
        return new StepBuilder("step", jobRepository)
            .tasklet(tasklet())
            .build();
    }
}

// 子コンテキスト2
@Configuration  
public class Job2Config {
    @Bean
    public Job job2(JobRepository jobRepository) {
        return new JobBuilder("job2", jobRepository)
            .start(step1())  // 同じBean名でもOK
            .build();
    }
    
    @Bean
    public Step step1() {
        // Job2専用のStep(Job1とBean名が同じでも衝突しない)
        return new StepBuilder("step", jobRepository)
            .tasklet(tasklet())
            .build();
    }
}
```

#### オプション2: Springプロファイルを使用
```java
@Configuration
public class AllJobsConfig {
    
    @Bean
    @Profile("job1")
    public Job job1(JobRepository jobRepository) {
        return new JobBuilder("job1", jobRepository)
            .start(job1Step())
            .build();
    }
    
    @Bean
    @Profile("job1")
    public Step job1Step() {
        return new StepBuilder("step", jobRepository)
            .tasklet(job1Tasklet())
            .build();
    }
    
    @Bean
    @Profile("job2")
    public Job job2(JobRepository jobRepository) {
        return new JobBuilder("job2", jobRepository)
            .start(job2Step())
            .build();
    }
    
    @Bean
    @Profile("job2")
    public Step job2Step() {
        return new StepBuilder("step", jobRepository)
            .tasklet(job2Tasklet())
            .build();
    }
}
```

実行時にプロファイルを指定:
```bash
java -jar app.jar --spring.profiles.active=job1
```

#### オプション3: Bean名を明示的に変更(最もシンプル)
```java
@Configuration
public class AllJobsConfig {
    
    @Bean
    public Job job1(JobRepository jobRepository) {
        return new JobBuilder("job1", jobRepository)
            .start(job1Step())
            .build();
    }
    
    @Bean("job1Step")  // 明示的なBean名
    public Step job1Step() {
        return new StepBuilder("step1", jobRepository)
            .tasklet(job1Tasklet())
            .build();
    }
    
    @Bean
    public Job job2(JobRepository jobRepository) {
        return new JobBuilder("job2", jobRepository)
            .start(job2Step())
            .build();
    }
    
    @Bean("job2Step")  // 明示的なBean名
    public Step job2Step() {
        return new StepBuilder("step2", jobRepository)
            .tasklet(job2Tasklet())
            .build();
    }
}
```

## 学習ポイント

### Bean名の衝突を避ける方法

| 方法 | 利点 | 欠点 |
|-----|------|------|
| コンテキスト階層 | 完全な分離 | 複雑な設定 |
| プロファイル | 実行時切り替え可能 | 全ジョブ同時実行不可 |
| Bean名変更 | シンプル | 命名規則の管理必要 |
