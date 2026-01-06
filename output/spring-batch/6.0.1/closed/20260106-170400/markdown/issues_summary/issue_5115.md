*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5115: MetaDataInstanceFactory.createJobParameters()が誤ったパラメータを使用する

## 課題概要

`JobOperator.restart()`でジョブを再起動する際、最新のジョブ実行のパラメータではなく、`MetaDataInstanceFactory`のコンストラクタで渡された古いパラメータが使用されてしまう問題です。

### 用語解説

- **JobOperator.restart()**: 失敗したジョブや停止したジョブを再実行するメソッド
- **JobParameters**: ジョブ実行時に渡されるパラメータ。同じジョブでも実行ごとに異なるパラメータを使用できる
- **MetaDataInstanceFactory**: ジョブやステップの実行メタデータ（実行情報）を生成するファクトリクラス

### 問題のシナリオ

以下のようなジョブで問題が発生します：

```java
Job job = new JobBuilder("sample", jobRepository)
    .incrementer(new RunIdIncrementer())
    .start(step1)
    .next(step2)
    .build();
```

```
【実行の流れ】
1. 最初の実行: パラメータ {'sample':'Glenn1'} でジョブを起動
   - step1完了
   - ジョブを停止（STATUS=STOPPED）
   
2. 再起動: パラメータ {'sample':'Glenn2'} で restart() を呼び出し
   - 期待: {'sample':'Glenn2'} が使われる
   - 実際: {'sample':'Glenn1'} が使われてしまう
```

### 期待される動作

```
実行1: Job: [SimpleJob: [name=sample]] launched with parameters: [{'sample':'Glenn1'}]
      Job: [SimpleJob: [name=sample]] completed with status: [STOPPED]

再起動: Job: [SimpleJob: [name=sample]] launched with parameters: [{'sample':'Glenn2'}]  ← 最新パラメータ
       Job: [SimpleJob: [name=sample]] completed with status: [COMPLETED]
```

### 実際の動作

```
実行1: Job: [SimpleJob: [name=sample]] launched with parameters: [{'sample':'Glenn1'}]
      Job: [SimpleJob: [name=sample]] completed with status: [STOPPED]

再起動: Job: [SimpleJob: [name=sample]] launched with parameters: [{'sample':'Glenn1'}]  ← 古いパラメータ
       Job: [SimpleJob: [name=sample]] completed with status: [COMPLETED]
```

## 原因

`MetaDataInstanceFactory`クラスが、コンストラクタで受け取ったジョブパラメータをフィールドに保持し、`createJobParameters()`メソッドでそのフィールドの値を返していました。しかし、再起動時には再起動対象のジョブ実行（`JobExecution`）から最新のパラメータを取得すべきでした。

### 詳細な原因

#### 1. MetaDataInstanceFactoryの構造（問題のあった実装）

```java
// MetaDataInstanceFactory（修正前のイメージ）
public class MetaDataInstanceFactory {
    private final JobParameters jobParameters;  // コンストラクタで受け取ったパラメータ
    
    public MetaDataInstanceFactory(JobParameters jobParameters) {
        this.jobParameters = jobParameters;  // 古いパラメータを保持
    }
    
    public JobParameters createJobParameters() {
        // 問題: フィールドの古いパラメータを返してしまう
        return this.jobParameters;
    }
}
```

#### 2. 再起動時の流れ

```
【再起動の処理フロー】
1. JobOperator.restart(long instanceId) 呼び出し
   ↓
2. 再起動可能な実行を取得
   JobExecution restartExecution = getJobExecution(...)
   // restartExecution.jobParameters = {'sample':'Glenn2'}（最新）
   ↓
3. MetaDataInstanceFactory生成
   factory = new MetaDataInstanceFactory(oldJobParameters)
   // oldJobParameters = {'sample':'Glenn1'}（古い）
   ↓
4. ジョブパラメータ作成
   JobParameters params = factory.createJobParameters()
   // params = {'sample':'Glenn1'}（古いパラメータが返される）
   ↓
5. ジョブ実行
   // 古いパラメータで実行されてしまう
```

#### 3. 問題の核心

`createJobParameters()`メソッドは、渡された`JobExecution`オブジェクトから最新のパラメータを取得すべきでしたが、コンストラクタで受け取った初期パラメータを返していました。

```java
// 問題のあったコード
public JobParameters createJobParameters() {
    // restartExecutionの最新パラメータを無視
    return this.jobParameters;  // コンストラクタで受け取った古いパラメータ
}
```

## 対応方針

`createJobParameters()`メソッドが、渡された`JobExecution`オブジェクトから直接ジョブパラメータを取得するように修正されました。

### 修正内容

[コミット 84e0afe](https://github.com/spring-projects/spring-batch/commit/84e0afe15da6f8ebfd0af8a38b4c6fa5fea30d08)

```java
// MetaDataInstanceFactory（修正後のイメージ）
public class MetaDataInstanceFactory {
    // jobParametersフィールドは不要
    
    // createJobParameters()メソッドに引数を追加
    public JobParameters createJobParameters(JobExecution jobExecution) {
        // 修正: jobExecutionから最新のパラメータを取得
        return jobExecution.getJobParameters();
    }
}
```

### 修正のポイント

| 項目 | 修正前 | 修正後 |
|-----|-------|-------|
| パラメータの取得元 | コンストラクタで受け取ったフィールド | `JobExecution`オブジェクト |
| メソッドシグネチャ | `createJobParameters()` | `createJobParameters(JobExecution)` |
| 使用されるパラメータ | 初回実行時のパラメータ | 再起動対象の最新パラメータ |

### 修正後の動作

```
【再起動の処理フロー（修正後）】
1. JobOperator.restart(long instanceId) 呼び出し
   ↓
2. 再起動可能な実行を取得
   JobExecution restartExecution = getJobExecution(...)
   // restartExecution.jobParameters = {'sample':'Glenn2'}（最新）
   ↓
3. MetaDataInstanceFactory生成
   factory = new MetaDataInstanceFactory()
   ↓
4. ジョブパラメータ作成
   JobParameters params = factory.createJobParameters(restartExecution)
   // restartExecution.getJobParameters()が返される
   // params = {'sample':'Glenn2'}（最新のパラメータ）
   ↓
5. ジョブ実行
   // 最新のパラメータで実行される
```

実際のログ：
```
実行1: Job: [SimpleJob: [name=sample]] launched with parameters: [{'sample':'Glenn1'}]
      Job: [SimpleJob: [name=sample]] completed with status: [STOPPED]

再起動: Job: [SimpleJob: [name=sample]] launched with parameters: [{'sample':'Glenn2'}]  ✅
       Job: [SimpleJob: [name=sample]] completed with status: [COMPLETED]
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `MetaDataInstanceFactory` - ジョブ/ステップのメタデータ生成ファクトリ
  - `SimpleJobOperator` - ジョブ操作の実装クラス
  - `JobExecution` - ジョブ実行情報を保持するクラス
  - `JobParameters` - ジョブパラメータを保持するクラス
- **影響範囲**: `JobOperator.restart()`を使用してジョブを再起動するすべてのケース
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5115
