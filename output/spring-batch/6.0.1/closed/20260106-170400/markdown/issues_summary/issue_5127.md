*(このドキュメントは生成AI(Claude Sonnet 4.5)によって2026年1月6日に生成されました)*

# Issue #5127: フォールトトレラントステップにおける例外処理の一貫性がない

## 課題概要

Spring Batch 6.0.0で導入された新しい再試行・スキップポリシーにおいて、対象外の例外が発生した際の処理が、読み込み・処理・書き込みの各フェーズで一貫していない問題です。

### 用語解説

- **フォールトトレラントステップ**: エラーが発生しても処理を継続できるステップ。特定の例外を再試行したりスキップしたりできる
- **スキップポリシー**: どの例外が発生したときにアイテムをスキップするかを定義するポリシー
- **再試行ポリシー**: どの例外が発生したときに処理を再試行するかを定義するポリシー
- **サブクラス包含**: Spring Batch 6では、例外のサブクラスも自動的に対象に含まれるようになった

### 問題のシナリオ

以下のような設定のステップで問題が発生します：

```java
Step step = new StepBuilder("step", jobRepository)
    .<String, String>chunk(10, transactionManager)
    .reader(itemReader)
    .processor(itemProcessor)
    .writer(itemWriter)
    .faultTolerant()
    .skipLimit(Integer.MAX_VALUE)
    .skip(IllegalStateException.class)  // IllegalStateExceptionのみスキップ
    .build();
```

#### ケース1: スキップポリシーの不一致

```java
// ItemProcessor内で発生
class MyProcessor implements ItemProcessor<String, String> {
    @Override
    public String process(String item) {
        if (item.equals("3")) {
            // IOExceptionは skip対象外
            throw new UncheckedIOException(new IOException("Expected"));
        }
        return item;
    }
}
```

```
【期待される動作】
processing中にIOException発生
  → skip対象外の例外
  → ステップは失敗すべき

【実際の動作】
processing中にIOException発生
  → skip対象外にもかかわらずスキップされる ❌
  → アイテム "3" がスキップされる
  → ステップは成功してしまう
```

#### ケース2: 再試行ポリシーの不一致

```java
// ItemReader内で発生
class MyReader extends ListItemReader<String> {
    int count = 0;
    
    @Override
    public String read() {
        count++;
        if (count == 3) {
            // IOExceptionは retry対象外
            throw new UncheckedIOException(new IOException("Expected"));
        }
        return super.read();
    }
}
```

```
【期待される動作】
reading中にIOException発生
  → retry対象外の例外
  → ステップは失敗すべき

【実際の動作】
reading中にIOException発生
  → retry対象外にもかかわらず再試行される ❌
  → 何度も再試行が実行される
  → 最終的に失敗する（予期しない再試行が発生）
```

### 動作の不一致

| フェーズ | 対象外のスキップ例外 | 対象外の再試行例外 |
|---------|-------------------|------------------|
| Reading（読み込み） | ✅ スキップされない（正しい） | ❌ 再試行される（誤り） |
| Processing（処理） | ❌ スキップされる（誤り） | ✅ 再試行されない（正しい） |
| Writing（書き込み） | - | - |

## 原因

Spring Batch 6.0.0で再試行・スキップポリシーがデフォルトでサブクラスを含むように変更されましたが、各フェーズでの例外判定ロジックが統一されていませんでした。

### 詳細な原因

#### 1. Spring Batch 5までの動作

```java
// Spring Batch 5
.skip(IOException.class)
  → IOExceptionのみスキップ（サブクラスは含まない）

.skip(IOException.class)
.include(FileNotFoundException.class)  // 明示的にサブクラスを追加
  → IOExceptionとFileNotFoundExceptionをスキップ
```

#### 2. Spring Batch 6での変更

```java
// Spring Batch 6
.skip(IOException.class)
  → IOExceptionとそのすべてのサブクラスをスキップ（自動）
```

これは便利な変更ですが、**対象外の例外**（設定されていない例外）の扱いが不統一でした。

#### 3. 問題のあった実装（イメージ）

```java
// FaultTolerantChunkProcessor（修正前）
class FaultTolerantChunkProcessor {
    
    // Processing phase
    void process(Item item) {
        try {
            processor.process(item);
        } catch (Exception e) {
            // ❌ すべての例外をスキップ判定に回してしまう
            if (shouldSkip(e)) {
                skip(item);
            } else {
                throw e;
            }
        }
    }
    
    // Reading phase
    Item read() {
        try {
            return reader.read();
        } catch (Exception e) {
            // ❌ すべての例外を再試行してしまう
            if (shouldRetry(e)) {
                return retry();
            } else {
                // ここに到達すべきだが、実際は再試行される
                throw e;
            }
        }
    }
}
```

#### 4. 本来あるべき動作

```java
// 正しい動作（修正後のイメージ）
void process(Item item) {
    try {
        processor.process(item);
    } catch (Exception e) {
        // ✅ skip対象の例外かチェック
        if (isSkippable(e)) {
            if (shouldSkip(e)) {  // 回数制限などをチェック
                skip(item);
            } else {
                throw e;
            }
        } else {
            // ✅ skip対象外の例外は即座にスロー
            throw e;
        }
    }
}
```

### 不一致の整理

```
【Reading phase】
対象外のスキップ例外:
  ✅ 正しく即座にスローされる
対象外の再試行例外:
  ❌ 誤って再試行される

【Processing phase】
対象外のスキップ例外:
  ❌ 誤ってスキップされる
対象外の再試行例外:
  ✅ 正しく即座にスローされる

【問題】
各フェーズで判定ロジックが異なっている
```

## 対応方針

各フェーズ（読み込み、処理、書き込み）で例外判定ロジックを統一し、対象外の例外は即座にスローされるように修正されました。

### 修正内容

[コミット b95be1a](https://github.com/spring-projects/spring-batch/commit/b95be1ad1f5b67b6ae2b8b10c0d9e766f9d56f8b)

```java
// FaultTolerantChunkProcessor（修正後のイメージ）
class FaultTolerantChunkProcessor {
    
    void process(Item item) {
        try {
            processor.process(item);
        } catch (Exception e) {
            // ✅ 修正: まず対象例外かチェック
            if (!skipPolicy.isSkippable(e.getClass())) {
                // 対象外の例外は即座にスロー
                throw e;
            }
            
            // 対象例外の場合のみスキップ判定
            if (skipPolicy.shouldSkip(e, skipCount)) {
                skip(item);
            } else {
                throw e;
            }
        }
    }
    
    Item read() {
        try {
            return reader.read();
        } catch (Exception e) {
            // ✅ 修正: まず対象例外かチェック
            if (!retryPolicy.isRetryable(e.getClass())) {
                // 対象外の例外は即座にスロー
                throw e;
            }
            
            // 対象例外の場合のみ再試行判定
            if (retryPolicy.shouldRetry(retryContext)) {
                return retry();
            } else {
                throw e;
            }
        }
    }
}
```

### 修正のポイント

#### 処理の流れ（修正後）

```
【例外発生時の判定フロー】
1. 例外が発生
   ↓
2. ポリシーの対象例外かチェック
   ├─ 対象外 → 即座にスロー ✅
   └─ 対象内 → 次へ
   ↓
3. 回数制限などをチェック
   ├─ スキップ/再試行する
   └─ 制限に達している → スロー
```

#### 統一された動作

| フェーズ | 対象外のスキップ例外 | 対象外の再試行例外 |
|---------|-------------------|------------------|
| Reading（読み込み） | ✅ スキップされない | ✅ 再試行されない |
| Processing（処理） | ✅ スキップされない | ✅ 再試行されない |
| Writing（書き込み） | ✅ スキップされない | ✅ 再試行されない |

### 修正後の動作

#### スキップポリシーの例

```java
Step step = new StepBuilder("step", jobRepository)
    .skip(IllegalStateException.class)  // これだけが対象
    .build();

// Processing中
throw new IOException();  
// → skip対象外 → 即座にスロー → ステップ失敗 ✅

throw new IllegalStateException();  
// → skip対象 → スキップ → 処理継続 ✅
```

#### 再試行ポリシーの例

```java
Step step = new StepBuilder("step", jobRepository)
    .retry(IllegalStateException.class)  // これだけが対象
    .build();

// Reading中
throw new IOException();  
// → retry対象外 → 即座にスロー → ステップ失敗 ✅

throw new IllegalStateException();  
// → retry対象 → 再試行 → 処理継続 ✅
```

## 参考情報

- **対象バージョン**: Spring Batch 6.0.0で発生、6.0.1で修正
- **関連クラス**:
  - `FaultTolerantChunkProcessor` - フォールトトレラントなチャンク処理
  - `SkipPolicy` - スキップポリシーのインターフェース
  - `RetryPolicy` - 再試行ポリシーのインターフェース
  - `FaultTolerantStepBuilder` - フォールトトレラントステップのビルダー
- **Spring Batch 6での変更**:
  - デフォルトでサブクラスを含むポリシーに変更
  - `.skip(IOException.class)` → `IOException`とそのすべてのサブクラスが対象
- **関連ディスカッション**: https://github.com/spring-projects/spring-batch/discussions/4920#discussioncomment-11406031
- **課題URL**: https://github.com/spring-projects/spring-batch/issues/5127
