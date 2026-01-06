*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5123: JobOperatorTestUtilsで非推奨警告が発生する

## 課題概要

Spring Batchのテストユーティリティクラス`JobOperatorTestUtils`内で、非推奨（deprecated）となった`JobBuilder`コンストラクタが使用されているため、コンパイル時に警告が発生していました。

### 用語解説

- **JobOperatorTestUtils**: `JobOperator`のテストを支援するユーティリティクラス
- **@Deprecated**: メソッドやコンストラクタが非推奨であることを示すアノテーション。将来のバージョンで削除される可能性がある
- **JobBuilder**: ジョブを構築するためのビルダークラス。Spring Batch 6で新しいコンストラクタが導入された

### 問題のシナリオ

Spring Frameworkのビルドログで以下のような警告が表示されていました：

```
warning: [deprecation] JobBuilder(String) in JobBuilder has been deprecated
    JobBuilder jobBuilder = new JobBuilder("myJob");
                            ^
```

この警告は、Spring BatchのCI/CD（継続的インテグレーション）パイプラインで発生し、ビルドログを汚していました。

## 原因

Spring Batch 6でAPIが変更され、`JobBuilder`のコンストラクタシグネチャが以下のように変更されました：

### Spring Batch 5までの実装

```java
// Spring Batch 5
public class JobBuilder {
    public JobBuilder(String name) {
        this.name = name;
    }
}

// 使用例
JobBuilder builder = new JobBuilder("myJob");
```

### Spring Batch 6での変更

```java
// Spring Batch 6
public class JobBuilder {
    @Deprecated  // 非推奨
    public JobBuilder(String name) {
        this.name = name;
    }
    
    // ✅ 新しいコンストラクタ
    public JobBuilder(String name, JobRepository jobRepository) {
        this.name = name;
        this.jobRepository = jobRepository;
    }
}
```

Spring Batch 6では、`JobRepository`をコンストラクタで受け取る新しい形式が推奨されています。

### 問題のあったコード

```java
// JobOperatorTestUtils.java（修正前）
public class JobOperatorTestUtils {
    private Job createJob(String jobName) {
        // ❌ 非推奨のコンストラクタを使用
        JobBuilder jobBuilder = new JobBuilder("myJob");
        
        return jobBuilder
            .start(createStep("step1"))
            .build();
    }
}
```

このコードは動作しますが、コンパイル時に警告が発生します。

## 対応方針

非推奨となった古いコンストラクタから、`JobRepository`を受け取る新しいコンストラクタに変更しました。

### 修正内容

[コミット 63a4c13](https://github.com/spring-projects/spring-batch/commit/63a4c136ad0c83e52f5f91a1b5e36c25bc5c6c80)

```java
// JobOperatorTestUtils.java（修正後）
public class JobOperatorTestUtils {
    private final JobRepository jobRepository;
    
    public JobOperatorTestUtils(JobRepository jobRepository) {
        this.jobRepository = jobRepository;
    }
    
    private Job createJob(String jobName) {
        // ✅ 新しいコンストラクタを使用
        JobBuilder jobBuilder = new JobBuilder(jobName, this.jobRepository);
        
        return jobBuilder
            .start(createStep("step1"))
            .build();
    }
}
```

### 修正のポイント

| 項目 | 修正前 | 修正後 |
|-----|-------|-------|
| コンストラクタ | `new JobBuilder("myJob")` | `new JobBuilder("myJob", jobRepository)` |
| 引数 | ジョブ名のみ | ジョブ名 + JobRepository |
| 非推奨警告 | ❌ 発生する | ✅ 発生しない |

### APIの変更理由

Spring Batch 6では、ジョブビルダーの設計が以下のように変更されました：

#### Spring Batch 5までの設計

```java
// 2段階での設定
JobBuilder jobBuilder = new JobBuilder("myJob");
Job job = jobBuilder
    .repository(jobRepository)  // 後で設定
    .start(step1)
    .build();
```

#### Spring Batch 6以降の推奨設計

```java
// 1段階での設定（より明確）
Job job = new JobBuilder("myJob", jobRepository)  // 最初から必須
    .start(step1)
    .build();
```

**変更の理由**:
- `JobRepository`はジョブに必須のコンポーネントであるため、最初から明示的に渡す方が分かりやすい
- 設定忘れを防ぐ
- より簡潔なAPI

### 修正の影響範囲

この修正は、Spring Batchのテストモジュール内部のみに影響し、ユーザーコードには影響しません。

```
【影響範囲】
Spring Batch内部:
  ✅ JobOperatorTestUtils（修正済み）
  ✅ 他のテストユーティリティ

ユーザーコード:
  変更不要（影響なし）
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `JobOperatorTestUtils` - JobOperatorのテストユーティリティ
  - `JobBuilder` - ジョブ構築ビルダー
  - `JobRepository` - ジョブメタデータの管理
- **非推奨API**: `JobBuilder(String)`コンストラクタ
- **推奨API**: `JobBuilder(String, JobRepository)`コンストラクタ
- **検出元**: Spring FrameworkのCIビルド
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5123

### マイグレーションガイド

既存のコードを更新する場合は、以下のように変更してください：

```java
// 修正前
JobBuilder builder = new JobBuilder("myJob");
Job job = builder
    .repository(jobRepository)
    .start(step1)
    .build();

// 修正後
Job job = new JobBuilder("myJob", jobRepository)
    .start(step1)
    .build();
```
