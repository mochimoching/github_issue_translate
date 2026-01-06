*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5122: MapJobRegistryにBean名ではなくジョブ名で登録される問題

## 課題概要

Spring Batch 6で、Bean名が明示的に指定されていない場合、`MapJobRegistry`がジョブをBean名ではなくジョブ名で登録してしまう問題です。これにより、Bean名による登録を前提とした`@SpringBatchTest`などのテストユーティリティが正常に動作しません。

### 用語解説

- **MapJobRegistry**: ジョブを名前で管理するレジストリ。ジョブの検索や実行に使用される
- **Bean名**: Springコンテキスト内でのBean（オブジェクト）の識別子。通常はメソッド名やクラス名から自動生成される
- **ジョブ名**: Spring Batchのジョブに付けられる論理的な名前。`JobBuilder`で明示的に指定できる
- **@SpringBatchTest**: Spring Batchのテストを簡単に書くためのアノテーション。`JobLauncherTestUtils`などを自動設定する

### 問題のシナリオ

#### 例1: Bean名とジョブ名が異なる場合

```java
@Configuration
public class JobConfig {
    @Bean
    public Job myJobBean(JobRepository jobRepository, Step step1) {
        return new JobBuilder("actualJobName", jobRepository)  // ジョブ名: "actualJobName"
            .start(step1)
            .build();
        // Bean名: "myJobBean"
    }
}
```

**期待される動作**: 
- ジョブは Bean名 `"myJobBean"` で登録される
- `jobRegistry.getJob("myJobBean")` で取得できる

**実際の動作**:
- ジョブはジョブ名 `"actualJobName"` で登録される
- `jobRegistry.getJob("myJobBean")` は失敗する
- `jobRegistry.getJob("actualJobName")` でしか取得できない

#### 例2: @SpringBatchTestが動作しない

```java
@SpringBatchTest  // Bean名を使ってJobLauncherTestUtilsを設定する
@SpringBootTest
public class MyJobTest {
    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;
    
    @Test
    public void testJob() {
        // ❌ Bean名でジョブが登録されていないため、
        // jobLauncherTestUtilsが正しく初期化されない
        JobExecution execution = jobLauncherTestUtils.launchJob();
    }
}
```

## 原因

Spring Batch 6の`MapJobRegistry`の実装が、Bean名とジョブ名の両方が利用可能な場合に、優先順位を間違えてジョブ名を使用していました。

### 詳細な原因

#### 従来の動作（Spring Batch 5以前）

```java
// Spring Batch 5以前の動作
@Bean
public Job myJob(JobRepository jobRepository) {
    return new JobBuilder("myJob", jobRepository)
        .start(step1)
        .build();
}

// Bean名 = "myJob"
// ジョブ名 = "myJob"  （同じ）
// 登録名 = "myJob"  （Bean名が使われる）
```

Bean名とジョブ名が同じ場合が多かったため、問題が顕在化していませんでした。

#### Spring Batch 6での問題

```java
// MapJobRegistry（問題のあった実装イメージ）
public void registerJob(String beanName, Job job) {
    String registrationName;
    
    if (job.getName() != null) {
        // ❌ ジョブ名が優先される
        registrationName = job.getName();
    } else if (beanName != null) {
        registrationName = beanName;
    } else {
        throw new IllegalArgumentException("Name required");
    }
    
    registry.put(registrationName, job);
}
```

この実装では、ジョブ名が指定されている場合は常にジョブ名が使用され、Bean名が無視されていました。

#### 期待される動作

```java
// 期待される動作
public void registerJob(String beanName, Job job) {
    String registrationName;
    
    if (beanName != null) {
        // ✅ Bean名が優先されるべき
        registrationName = beanName;
    } else if (job.getName() != null) {
        registrationName = job.getName();
    } else {
        throw new IllegalArgumentException("Name required");
    }
    
    registry.put(registrationName, job);
}
```

### Spring Batchのエコシステムへの影響

```
【影響を受けるコンポーネント】

@SpringBatchTest
  ↓ Bean名でジョブを検索
JobLauncherTestUtils
  ↓ Bean名が必要
MapJobRegistry
  ↓ ❌ ジョブ名で登録されている
検索失敗
```

## 対応方針

`MapJobRegistry`の登録ロジックを修正し、Bean名が利用可能な場合は常にBean名を優先して使用するようにしました。

### 修正内容

[コミット 69ff97d](https://github.com/spring-projects/spring-batch/commit/69ff97dea77f97a5f74cfd1bad2f03c4c41b3862)

```java
// MapJobRegistry（修正後のイメージ）
public void registerJob(String beanName, Job job) {
    String registrationName;
    
    // ✅ 修正: Bean名を優先
    if (beanName != null && !beanName.isEmpty()) {
        registrationName = beanName;
    } else if (job.getName() != null && !job.getName().isEmpty()) {
        registrationName = job.getName();
    } else {
        throw new IllegalArgumentException("Either beanName or job name is required");
    }
    
    registry.put(registrationName, job);
}
```

### 修正のポイント

| 条件 | 修正前の登録名 | 修正後の登録名 |
|-----|-------------|-------------|
| Bean名: "myJobBean"<br>ジョブ名: "actualJobName" | "actualJobName"（ジョブ名） | "myJobBean"（Bean名）✅ |
| Bean名: null<br>ジョブ名: "myJob" | "myJob"（ジョブ名） | "myJob"（ジョブ名） |
| Bean名: "myJobBean"<br>ジョブ名: "myJobBean" | "myJobBean"（ジョブ名） | "myJobBean"（Bean名）✅ |

### 修正後の動作

#### テストが正常に動作

```java
@Configuration
public class JobConfig {
    @Bean
    public Job myJobBean(JobRepository jobRepository, Step step1) {
        return new JobBuilder("actualJobName", jobRepository)
            .start(step1)
            .build();
    }
}

@SpringBatchTest
@SpringBootTest
public class MyJobTest {
    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;
    
    @Test
    public void testJob() {
        // ✅ Bean名でジョブが登録されているため、正常に動作
        JobExecution execution = jobLauncherTestUtils.launchJob();
        assertThat(execution.getStatus()).isEqualTo(BatchStatus.COMPLETED);
    }
}
```

#### ジョブの取得

```java
// Bean名で取得できる
Job job = jobRegistry.getJob("myJobBean");  // ✅ 成功

// ジョブ名では取得できない（期待通り）
Job job = jobRegistry.getJob("actualJobName");  // ❌ NoSuchJobException
```

### 優先順位の整理

```
【登録名の決定優先順位】
1. Bean名（最優先）
   ↓ Bean名がない場合
2. ジョブ名
   ↓ どちらもない場合
3. IllegalArgumentException
```

この優先順位により、Spring Frameworkの一般的な規約（BeanはBean名で識別される）と整合性が取れます。

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `MapJobRegistry` - ジョブをMap形式で管理するレジストリ
  - `@SpringBatchTest` - Spring Batchのテストサポートアノテーション
  - `JobLauncherTestUtils` - テストでジョブを起動するユーティリティ
- **影響範囲**:
  - `@SpringBatchTest`を使用したテスト
  - Bean名でジョブを検索するコード
  - 複数のジョブを持つアプリケーション
- **Spring Frameworkとの整合性**: この修正により、Spring FrameworkのBean管理の原則（BeanはBean名で識別される）に従うようになりました
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5122
