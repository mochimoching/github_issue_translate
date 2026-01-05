# Issue #5152: マイグレーションガイドのクラス名誤記

**Issue URL**: https://github.com/spring-projects/spring-batch/issues/5152

---

## 課題概要

### 問題の説明

[Spring Batch 6.0 Migration Guide](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-6.0-Migration-Guide)に、クラス名の誤記がありました。

ガイドには「**JobParametersInvalidException**」が新しいパッケージに移動したと記載されていましたが、実際にはSpring Batch 6.0.0で「**InvalidJobParametersException**」に名前が変更されていました。

### 背景知識の補足

**クラス名の変遷**:
| バージョン | クラス名 |
|-----------|---------|
| Spring Batch 5.x | `JobParametersInvalidException` |
| Spring Batch 6.0.0-M3 | `JobParametersInvalidException` |
| Spring Batch 6.0.0 | `InvalidJobParametersException` ← 名前変更 |

**パッケージの変更**:
- 旧: `org.springframework.batch.core.repository`
- 新: `org.springframework.batch.core.job`

### 影響範囲

| 項目 | 内容 |
|------|------|
| **影響するバージョン** | ドキュメントのみ |
| **影響する領域** | マイグレーションガイド |
| **重大度** | 低（ドキュメントの誤記） |
| **関連Issue** | [#5013](https://github.com/spring-projects/spring-batch/issues/5013) |

---

## 原因

### 根本原因の詳細

Issue [#5013](https://github.com/spring-projects/spring-batch/issues/5013)で例外クラスの命名規則が統一された際、このクラスが「**Invalid**で始まる命名」に変更されましたが、マイグレーションガイドが更新されませんでした。

**実際の変更**:
```java
// Spring Batch 5.x
package org.springframework.batch.core.repository;

public class JobParametersInvalidException extends JobExecutionException {
    // ...
}
```

↓

```java
// Spring Batch 6.0.0
package org.springframework.batch.core.job;

public class InvalidJobParametersException extends JobExecutionException {
    // ...
}
```

**マイグレーションガイドの誤記**:
```markdown
### Exception Renaming

The following exceptions have been renamed:

- `JobParametersInvalidException` → moved to new package  ← 誤り
```

**正しい記載**:
```markdown
### Exception Renaming

The following exceptions have been renamed:

- `JobParametersInvalidException` → `InvalidJobParametersException`
- Moved to package: `org.springframework.batch.core.job`
```

---

## 対応方針

### 修正内容

マイグレーションガイドを修正し、正しいクラス名を記載しました。

**修正後のマイグレーションガイド**:
```markdown
## API Changes

### Exception Renaming and Package Changes

| Old Name (5.x) | New Name (6.0) | Package |
|---------------|---------------|---------|
| `JobParametersInvalidException` | `InvalidJobParametersException` | `org.springframework.batch.core.job` |
| `JobInstanceAlreadyCompleteException` | `AlreadyCompleteException` | `org.springframework.batch.core.job` |
| `JobExecutionAlreadyRunningException` | `AlreadyRunningException` | `org.springframework.batch.core.job` |
```

### 移行コードの例

**修正前のコード（Spring Batch 5.x）**:
```java
import org.springframework.batch.core.repository.JobParametersInvalidException;

@Component
public class JobLauncher {
    
    public void launchJob(Job job, JobParameters params) {
        try {
            jobLauncher.run(job, params);
        } catch (JobParametersInvalidException e) {
            logger.error("Invalid parameters", e);
        }
    }
}
```

**修正後のコード（Spring Batch 6.0）**:
```java
import org.springframework.batch.core.job.InvalidJobParametersException;

@Component
public class JobLauncher {
    
    public void launchJob(Job job, JobParameters params) {
        try {
            jobLauncher.run(job, params);
        } catch (InvalidJobParametersException e) {
            logger.error("Invalid parameters", e);
        }
    }
}
```

### IDE自動インポートの注意

**IntelliJ IDEA / Eclipse**:
```java
// 古いクラス名で検索すると見つからない
import org.springframework.batch.core.repository.JobParametersInvalidException;  // ❌

// 正しいインポート
import org.springframework.batch.core.job.InvalidJobParametersException;  // ✅
```

### 変更の影響

| 項目 | 内容 |
|------|------|
| **コード変更** | importとcatch句のクラス名 |
| **互換性** | 破壊的変更（クラス名変更） |
| **ドキュメント** | マイグレーションガイド修正 |
| **リリース** | ドキュメント修正のみ |

### 例外クラスの命名規則統一

Spring Batch 6.0では、例外クラスの命名規則が統一されました:

| パターン | 例 |
|---------|-----|
| **Invalid*** | `InvalidJobParametersException` |
| **Already*** | `AlreadyCompleteException`, `AlreadyRunningException` |
| **NoSuch*** | `NoSuchJobException`, `NoSuchJobInstanceException` |

### 使用例

**JobParametersValidatorでの使用**:
```java
public class CustomJobParametersValidator implements JobParametersValidator {
    
    @Override
    public void validate(JobParameters parameters) throws InvalidJobParametersException {
        if (parameters == null || parameters.isEmpty()) {
            throw new InvalidJobParametersException(
                "Job parameters cannot be null or empty"
            );
        }
        
        if (parameters.getString("inputFile") == null) {
            throw new InvalidJobParametersException(
                "Required parameter 'inputFile' is missing"
            );
        }
    }
}
```

**例外ハンドリング**:
```java
@Service
public class JobExecutionService {
    
    @Autowired
    private JobLauncher jobLauncher;
    
    @Autowired
    private Job myJob;
    
    public Long executeJob(Map<String, Object> params) {
        try {
            JobParameters jobParameters = new JobParametersBuilder()
                .addString("inputFile", (String) params.get("inputFile"))
                .toJobParameters();
            
            JobExecution execution = jobLauncher.run(myJob, jobParameters);
            return execution.getId();
            
        } catch (InvalidJobParametersException e) {
            // パラメータ検証エラー
            logger.error("Invalid job parameters: {}", e.getMessage());
            throw new IllegalArgumentException("Invalid parameters", e);
            
        } catch (JobInstanceAlreadyCompleteException e) {
            // 既に完了済み
            logger.warn("Job instance already completed");
            return null;
        }
    }
}
```

### まとめ

この課題はドキュメントの誤記のみで、コードの動作には影響しません。Spring Batch 6.0への移行時は、マイグレーションガイドの正しい情報を参照してください。
