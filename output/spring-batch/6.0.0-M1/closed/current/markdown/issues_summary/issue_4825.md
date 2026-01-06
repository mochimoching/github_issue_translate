*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

## 課題概要

課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824)（`JobRepository`を`JobExplorer`の拡張とする）と課題 [#4817](https://github.com/spring-projects/spring-batch/issues/4817)（`SimpleJobOperator`の`JobExplorer`依存削除）の実装後、デフォルトのバッチ設定で`JobExplorer` Beanを自動登録する必要がなくなりました。

**デフォルトのバッチ設定とは**: `@EnableBatchProcessing`や`DefaultBatchConfiguration`により、Spring Batchの基本的なインフラストラクチャBean（`JobRepository`、`JobLauncher`、`JobExplorer`等）が自動的に登録される仕組みです。

### v5.2のデフォルト設定

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

package "DefaultBatchConfiguration (v5.2)" {
  [JobRepository Bean] as Repo
  [JobExplorer Bean] as Explorer
  [JobLauncher Bean] as Launcher
  [JobOperator Bean] as Operator
}

Operator --> Repo
Operator --> Explorer

note right of Explorer #FFE4B5
  JobExplorerは
  JobRepositoryと別に
  自動登録されていた
end note

note bottom of Operator #FF6B6B
  問題：RepositoryとExplorerの
  両方に依存している
end note

@enduml
```

### 特にResourcelessJobRepositoryでの問題

**ResourcelessJobRepositoryとは**: ジョブのメタデータを永続化せず、メモリ内でのみ管理する軽量なJobRepository実装です。テストや一時的なジョブ実行に便利です。

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

class "ResourcelessJobRepository" {
  .. 特徴 ..
  - メタデータを永続化しない
  - メモリ内のみで動作
  - 探索すべき履歴データなし
}

class "DefaultBatchConfiguration" {
  + jobRepository()
  + jobExplorer()
}

ResourcelessJobRepository <.. DefaultBatchConfiguration: 自動設定しようとする

note right of ResourcelessJobRepository #FF6B6B
  問題：
  履歴データがないのに
  JobExplorerを作成しようとして
  設定が複雑化
  
  探索機能が不要な
  リポジトリに対して
  Explorer Beanは無意味
end note

@enduml
```

## 原因

v5.2では、`JobRepository`と`JobExplorer`が独立した2つのインターフェースだったため、デフォルト設定で両方のBeanを作成する必要がありました。しかし、課題 [#4824](https://github.com/spring-projects/spring-batch/issues/4824) で`JobRepository`が`JobExplorer`を継承するよう変更されたため、この設計は不要になりました。

### 課題 #4824 の変更内容（再掲）

```java
// v6.0での新しい設計
public interface JobRepository extends JobExplorer {
    // JobExplorerの全メソッドを継承
    // + 追加の書き込みメソッド
    void update(JobExecution jobExecution);
    void add(StepExecution stepExecution);
    // ...
}
```

この変更により、`JobRepository` Beanが`JobExplorer`の機能も提供するようになったため、別途`JobExplorer` Beanを登録する必要がなくなりました。

## 対応方針

**コミット**: [ae2df53](https://github.com/spring-projects/spring-batch/commit/ae2df5396baa25cc5abe68e43508f6d0981dcf68)

`DefaultBatchConfiguration`から`JobExplorer` Beanの自動登録を削除しました。

### v6.0の改善されたデフォルト設定

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

package "DefaultBatchConfiguration (v6.0)" {
  [JobRepository Bean] as Repo
  [JobLauncher Bean] as Launcher
  [JobOperator Bean] as Operator
}

Operator --> Repo

note right of Repo #90EE90
  JobRepositoryが
  JobExplorerを継承
  
  1つのBeanで
  両方の機能を提供
end note

note bottom of Operator #90EE90
  改善：Repositoryのみに依存
  シンプルな設計
end note

@enduml
```

### ResourcelessJobRepositoryでの改善

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

start

:@EnableBatchProcessing;

if (JobRepository Bean定義あり?) then (yes)
  :ユーザー定義のRepositoryを使用;
  note right
    ResourcelessJobRepository等
    任意の実装が使用可能
  end note
else (no)
  :デフォルトのJdbcJobRepositoryを作成;
endif

:JobOperatorにRepositoryを注入;

note right #90EE90
  JobExplorer Beanの作成は不要
  
  ResourcelessJobRepositoryでも
  問題なく動作する
end note

stop

@enduml
```

### 設定の比較

#### v5.2（変更前）

```java
@Configuration
@EnableBatchProcessing
public class BatchConfig {
    
    @Bean
    public JobRepository jobRepository() {
        return new ResourcelessJobRepositoryFactoryBean()...build();
    }
    
    // 問題：ResourcelessなのにExplorerの設定が必要
    @Bean
    public JobExplorer jobExplorer() {
        // どう実装すればいい？
        // 探索すべきデータがないのに...
        return ???;
    }
}
```

#### v6.0（変更後）

```java
@Configuration
@EnableBatchProcessing
public class BatchConfig {
    
    @Bean
    public JobRepository jobRepository() {
        return new ResourcelessJobRepositoryFactoryBean()...build();
    }
    
    // JobExplorer Beanの定義は不要！
    // JobRepositoryが自動的にExplorerとしても機能
}
```

### メリット

| 項目 | v5.2 | v6.0 |
|------|------|------|
| 自動登録されるBean数 | 2個（Repository + Explorer） | 1個（Repositoryのみ） |
| ResourcelessJobRepository対応 | 困難（Explorerの設定が課題） | 容易（Repository設定のみ） |
| 設定の複雑さ | 高い | 低い |
| 理解しやすさ | 低い（なぜ2つ必要？） | 高い（Repository1つで完結） |

### 影響範囲

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

package "影響を受けるコンポーネント" {
  [DefaultBatchConfiguration] #90EE90
  [SimpleJobOperator] #90EE90
  [ResourcelessJobRepository] #90EE90
}

package "自動設定" {
  [Spring Boot Auto-configuration] #90EE90
}

note right of DefaultBatchConfiguration
  JobExplorer Bean登録を削除
  よりシンプルな設定
end note

note right of SimpleJobOperator
  #4817でExplorer依存を削除
  Repositoryのみに依存
end note

note right of ResourcelessJobRepository
  Explorer不要で使いやすく
end note

@enduml
```

### 後方互換性

既存のユーザーが明示的に`JobExplorer` Beanを定義している場合でも、問題なく動作します。`JobRepository`は`JobExplorer`のサブインターフェースなので、既存コードに影響はありません。

```java
// v5.2からの移行コード（そのまま動作）
@Service
public class MyService {
    // JobExplorerを注入していても問題なし
    // JobRepositoryがJobExplorerを実装しているため
    @Autowired
    private JobExplorer jobExplorer;
    
    public void checkJobHistory() {
        Set<String> jobNames = jobExplorer.getJobNames();
        // 正常に動作
    }
}
```

この変更により、Spring Batchの設定がよりシンプルかつ柔軟になり、特に非JDBC実装のJobRepositoryを使用するケースで大幅に改善されました。
