*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5152: Spring Batch 6.0マイグレーションガイドを6.0.1に更新

## 課題概要

Spring Batch 6.0のマイグレーションガイドを6.0.1の変更内容を含めて更新する提案です。6.0.1で導入された新しいAPIや廃止された機能をガイドに反映することで、ユーザーがスムーズにアップグレードできるようにします。

### 用語解説

- **マイグレーションガイド**: バージョン間の移行手順や変更点をまとめたドキュメント。アップグレード時に必要な対応を説明する
- **非推奨（Deprecated）**: 将来のバージョンで削除される予定の機能やAPI。使用は非推奨だが、まだ動作する
- **破壊的変更（Breaking Change）**: 既存のコードが動作しなくなる変更。アップグレード時にコード修正が必要
- **リファレンスドキュメント**: Spring Batchの公式ドキュメント。各機能の使い方や設定方法を詳しく説明
- **Javadoc**: Javaのソースコードに記述されたAPIドキュメント

### マイグレーションガイドの役割

```
【バージョンアップの流れ】
Spring Batch 5.0使用中
  ↓
Spring Batch 6.0にアップグレードしたい
  ↓
マイグレーションガイドを確認
  ├─ 何が変わったか？
  ├─ どのAPIが廃止されたか？
  ├─ コードをどう修正すればよいか？
  └─ 新機能は何か？
  ↓
コードを修正
  ↓
テスト
  ↓
アップグレード完了 ✅
```

### 主な内容

マイグレーションガイドには以下のような情報が含まれます：

| セクション | 内容 | 例 |
|----------|------|-----|
| 破壊的変更 | 既存コードが動作しなくなる変更 | `@EnableBatchProcessing`の動作変更 |
| 非推奨API | 将来削除される予定のAPI | `JobBuilderFactory`の非推奨化 |
| 新機能 | 新しく追加された機能 | MongoDBサポート、Micrometer連携 |
| 推奨される変更 | 必須ではないが推奨される変更 | 新しいビルダーAPIの使用 |
| 削除されたAPI | 完全に削除されたAPI | 古い非推奨APIの削除 |

### 更新が必要な理由

```
【Spring Batch 6.0.0時点】
マイグレーションガイド
  └─ 6.0.0での変更内容のみ

【6.0.1がリリース】
新しい変更が発生:
  ├─ JobOperatorTestUtilsの非推奨化（#5123）
  ├─ MapJobRegistryのbean name動作変更（#5122）
  ├─ パーティショニング機能の改善（#5138）
  └─ その他の修正とAPI変更

【問題】
6.0.1にアップグレードするユーザーが:
  ❌ 6.0.1での変更内容を把握できない
  ❌ 新しい非推奨APIに気づかない
  ❌ 動作変更に対応できない

【解決策】
マイグレーションガイドを6.0.1に更新 ✅
```

## 原因

Spring Batch 6.0.0のリリース時にマイグレーションガイドが作成されましたが、6.0.1でさらに変更や改善が加えられたため、ガイドの更新が必要になりました。

### 6.0.1での主な変更

以下のような変更がマイグレーションガイドに追加される必要があります：

#### 1. 非推奨APIの追加

```java
// Issue #5123: JobOperatorTestUtilsの非推奨化
public class JobOperatorTestUtils {
    
    // ❌ 非推奨になった（6.0.1）
    @Deprecated(since = "6.0.1", forRemoval = true)
    public JobOperatorTestUtils(JobOperator jobOperator) {
        // ...
    }
    
    // ✅ 新しいコンストラクタ
    public JobOperatorTestUtils(JobOperator jobOperator, JobRepository jobRepository) {
        // ...
    }
}
```

```
【マイグレーションガイドに追加する内容】
### JobOperatorTestUtilsのコンストラクタ変更

#### 変更内容
`JobOperatorTestUtils`の1引数コンストラクタが非推奨になりました。

#### 修正前
```java
JobOperatorTestUtils testUtils = new JobOperatorTestUtils(jobOperator);
```

#### 修正後
```java
JobOperatorTestUtils testUtils = new JobOperatorTestUtils(jobOperator, jobRepository);
```

#### 理由
内部で使用される`JobRepository`を明示的に指定する必要があるため。
```

#### 2. 動作変更の追記

```java
// Issue #5122: MapJobRegistryの動作変更
@Configuration
public class JobConfiguration {
    
    @Bean
    public MapJobRegistry jobRegistry() {
        return new MapJobRegistry();
    }
    
    @Bean("myJobBeanName")
    public Job job(JobRepository jobRepository) {
        return new JobBuilder("actualJobName", jobRepository)
                .start(step1())
                .build();
    }
}
```

```
【マイグレーションガイドに追加する内容】
### MapJobRegistryのジョブ登録優先順位変更

#### 変更内容
6.0.0では`MapJobRegistry`がBean名でジョブを登録していましたが、
6.0.1では`Job.getName()`で返されるジョブ名で登録されるようになりました。

#### 影響
- Bean名とジョブ名が異なる場合、登録名が変わる
- `@SpringBatchTest`でのジョブ実行に影響する可能性がある

#### 対応
Bean名とジョブ名を一致させることを推奨します。

```java
// 推奨: Bean名とジョブ名を一致させる
@Bean("myJob")
public Job myJob(JobRepository jobRepository) {
    return new JobBuilder("myJob", jobRepository)  // 同じ名前
            .start(step1())
            .build();
}
```
```

#### 3. バグ修正の追記

```
【マイグレーションガイドに追加する内容】
### バグ修正

6.0.1では以下のバグが修正されました：

- **パーティションステップの永続化** (#5138)
  - ワーカーステップの`StepExecution`がデータベースに正しく保存されるようになりました
  
- **フォールトトレラントステップの例外処理** (#5127)
  - スキップ・再試行ポリシーの対象外例外の処理が統一されました
  
- **ChunkTrackerのリセット** (#5126)
  - ステップ完了後に`ChunkTracker`が正しくリセットされるようになりました

これらのバグ修正により、6.0.0で問題が発生していた場合は6.0.1へのアップグレードを推奨します。
```

#### 4. 新機能・改善の追記

```
【マイグレーションガイドに追加する内容】
### 改善・機能追加

6.0.1では以下の改善が行われました：

- **ResourcelessJobRepositoryの並行処理改善** (#5139)
  - `synchronized`から`java.util.concurrent`を使った実装に変更
  - テストでの並行実行パフォーマンスが向上

- **RemotePartitioningWorkerStepBuilderのメソッド公開** (#5150)
  - `repository()`, `transactionManager()`, `listener()`などのメソッドが使用可能に
  - リモートパーティショニングの設定がより柔軟に

```java
// 6.0.1で可能になった設定
Step workerStep = new RemotePartitioningWorkerStepBuilder("worker")
        .inputChannel(inputChannel)
        .outputChannel(outputChannel)
        .repository(customJobRepository)  // ✅ 6.0.1で追加
        .transactionManager(customTxManager)  // ✅ 6.0.1で追加
        .listener(customListener)  // ✅ 6.0.1で追加
        .chunk(100)
        .reader(reader)
        .writer(writer)
        .build();
```
```

## 対応方針

マイグレーションガイドに6.0.1での変更内容を追加し、ユーザーが6.0.0から6.0.1へスムーズにアップグレードできるようにドキュメントを更新しました。

### 更新内容

[コミット c3e6eb6](https://github.com/spring-projects/spring-batch/commit/c3e6eb6f4862e3f0b1e2ff046c23dd7dc11f48d7)

マイグレーションガイドに以下のセクションが追加・更新されました：

#### 1. 非推奨APIセクション

```markdown
## Deprecated APIs in 6.0.1

### JobOperatorTestUtils Constructor

The single-argument constructor `JobOperatorTestUtils(JobOperator)` has been deprecated
in favor of the two-argument constructor `JobOperatorTestUtils(JobOperator, JobRepository)`.

**Before:**
```java
JobOperatorTestUtils utils = new JobOperatorTestUtils(jobOperator);
```

**After:**
```java
JobOperatorTestUtils utils = new JobOperatorTestUtils(jobOperator, jobRepository);
```

See issue [#5123](https://github.com/spring-projects/spring-batch/issues/5123) for more details.
```

#### 2. 動作変更セクション

```markdown
## Behavior Changes in 6.0.1

### MapJobRegistry Registration Strategy

The `MapJobRegistry` now registers jobs using the job name (from `Job.getName()`)
instead of the bean name. This provides more consistent behavior.

**Impact:**
- Jobs are registered by their logical name rather than bean name
- Affects job lookup in `@SpringBatchTest` scenarios

**Recommendation:**
Ensure bean names and job names match to avoid confusion.

See issue [#5122](https://github.com/spring-projects/spring-batch/issues/5122) for more details.
```

#### 3. バグ修正セクション

```markdown
## Bug Fixes in 6.0.1

The following bugs were fixed in 6.0.1:

- **Partition Step Persistence** (#5138): Worker step executions are now correctly 
  persisted to the JobRepository
  
- **Fault-Tolerant Step Exception Handling** (#5127): Skip and retry policy exception
  handling is now consistent across read/process/write phases
  
- **ChunkTracker Reset** (#5126): ChunkTracker is now properly reset after step completion

If you experienced these issues in 6.0.0, upgrading to 6.0.1 is recommended.
```

#### 4. 改善セクション

```markdown
## Enhancements in 6.0.1

### ResourcelessJobRepository Concurrency

The `ResourcelessJobRepository` now uses `java.util.concurrent` collections
for better concurrency support, replacing synchronized methods.

**Benefit:** Improved performance in test scenarios with concurrent job executions.

### RemotePartitioningWorkerStepBuilder API

Additional builder methods are now available:

```java
Step workerStep = new RemotePartitioningWorkerStepBuilder("worker")
        .repository(customRepository)      // New in 6.0.1
        .transactionManager(customTxMgr)   // New in 6.0.1
        .listener(customListener)          // New in 6.0.1
        // ... other configuration
        .build();
```

See issue [#5150](https://github.com/spring-projects/spring-batch/issues/5150) for more details.
```

### ドキュメント構成

```
【マイグレーションガイドの構成】
# What's New in Spring Batch 6.0
  ├─ Major Changes in 6.0.0
  │   ├─ Breaking Changes
  │   ├─ Deprecated APIs
  │   ├─ New Features
  │   └─ Recommended Practices
  │
  └─ ✅ Updates in 6.0.1（新規追加）
      ├─ Deprecated APIs in 6.0.1
      ├─ Behavior Changes in 6.0.1
      ├─ Bug Fixes in 6.0.1
      └─ Enhancements in 6.0.1
```

### ユーザーへの影響

#### 6.0.0から6.0.1へのアップグレード

```
【アップグレード手順】
1. マイグレーションガイドを確認
   └─ "Updates in 6.0.1"セクションを読む

2. 非推奨APIをチェック
   └─ JobOperatorTestUtilsを使っている場合は修正

3. 動作変更を確認
   └─ MapJobRegistryを使っている場合は影響を確認

4. バグ修正の恩恵を受ける
   └─ 6.0.0で問題があった機能が修正されている

5. 新機能を活用（オプション）
   └─ RemotePartitioningWorkerStepBuilderの新しいメソッドなど

6. テスト
   └─ 既存のテストが通ることを確認

7. デプロイ ✅
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.1でマイグレーションガイドを更新
- **マイグレーションガイドの場所**:
  - リファレンスドキュメント: https://docs.spring.io/spring-batch/docs/current/reference/html/
  - "What's New"セクション
- **関連するIssue**:
  - #5123: JobOperatorTestUtilsの非推奨化
  - #5122: MapJobRegistryの動作変更
  - #5138: パーティションステップの永続化
  - #5127: フォールトトレラントステップの例外処理
  - #5126: ChunkTrackerのリセット
  - #5139: ResourcelessJobRepositoryの並行処理改善
  - #5150: RemotePartitioningWorkerStepBuilderのAPI公開
- **ドキュメントの種類**:
  - **マイグレーションガイド**: バージョン間の移行方法
  - **リファレンスドキュメント**: 各機能の詳細な説明
  - **Javadoc**: APIの仕様
  - **サンプルコード**: GitHub上のサンプルプロジェクト
- **アップグレードの推奨事項**:
  - 6.0.0で問題が発生している場合は6.0.1へのアップグレードを推奨
  - 非推奨APIは将来削除されるため、早めの対応を推奨
  - 新機能は必要に応じて活用
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5152
