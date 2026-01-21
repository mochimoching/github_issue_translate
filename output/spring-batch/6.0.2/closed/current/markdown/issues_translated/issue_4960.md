*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月21日に生成されました）*

# 並列ジョブ実行時にMongoSequenceIncrementerでWriteConflictが発生する

**Issue番号**: #4960

**状態**: closed | **作成者**: benoit-charpiepruvost | **作成日**: 2025-08-21

**ラベル**: type: bug, in: core, has: minimal-example, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4960

**関連リンク**:
- コミット:
  - [d0aef64](https://github.com/spring-projects/spring-batch/commit/d0aef64e33ae3f9189ac447bed730c2c714bd82b)
  - [eac1ff5](https://github.com/spring-projects/spring-batch/commit/eac1ff5e85b5b22d841dcfce62afc87e233ce762)
  - [efbce13](https://github.com/spring-projects/spring-batch/commit/efbce13f0faf512f22281f8e54c3d637b2eacd5c)

## 内容

**バグの説明**
`MongoDBJobRepository`を使用して複数のSpring Batchジョブを並列実行すると、ジョブインスタンスIDのシーケンス生成時に書き込み競合が発生します。`MongoSequenceIncrementer.nextLongValue()`メソッドはシーケンスドキュメントをアトミックに検索・更新しようとしますが、同時実行によりMongoDBのWriteConflictエラーが発生してしまいます。

根本原因: `MongoSequenceIncrementer`の`findAndModify`操作が、並行アクセスパターンを適切に処理できていません。
影響: 並列ジョブ実行ができなくなり、`DataIntegrityViolationException`でジョブが失敗します。

```
2025-08-21T08:42:16.167+02:00 ERROR 1 --- [Container#1-223] .d.a.f.s.s.MaterializedCollectionService : Cannot execute job sync job correctly
org.springframework.dao.DataIntegrityViolationException: Command failed with error 112 (WriteConflict): 'Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.' on server xxx.mongodb.net:1026. The full response is {"errorLabels": ["TransientTransactionError"], "ok": 0.0, "errmsg": "Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.", "code": 112, "codeName": "WriteConflict", "$clusterTime": {"clusterTime": {"$timestamp": {"t": 1755758536, "i": 4}}, "signature": {"hash": {"$binary": {"base64": "xxx=", "subType": "00"}}, "keyId": xxx}}, "operationTime": {"$timestamp": {"t": 1755758536, "i": 4}}}
    at org.springframework.data.mongodb.core.MongoExceptionTranslator.doTranslateException(MongoExceptionTranslator.java:141) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.data.mongodb.core.MongoExceptionTranslator.translateExceptionIfPossible(MongoExceptionTranslator.java:74) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.data.mongodb.core.MongoTemplate.potentiallyConvertRuntimeException(MongoTemplate.java:3033) ~[spring-data-mongodb-4.5.0.jar:3.5.0]
    at org.springframework.data.mongodb.core.MongoTemplate.execute(MongoTemplate.java:609) ~[spring-data-mongodb-4.5.0.jar:4.5.0]
    at org.springframework.batch.core.repository.dao.MongoSequenceIncrementer.nextLongValue(MongoSequenceIncrementer.java:47) ~[spring-batch-core-5.2.2.jar:5.2.2]
    at org.springframework.batch.core.repository.dao.MongoJobInstanceDao.createJobInstance(MongoJobInstanceDao.java:80) ~[spring-batch-core-5.2.2.jar:5.2.2]
    at org.springframework.batch.core.repository.support.SimpleJobRepository.createJobExecution(SimpleJobRepository.java:168) ~[spring-batch-core-5.2.2.jar:5.2.2]
    ...（省略）...
Caused by: com.mongodb.MongoCommandException: Command failed with error 112 (WriteConflict): 'Caused by :: Write conflict during plan execution and yielding is disabled. :: Please retry your operation or multi-document transaction.' on server xxx.mongodb.net:1026.
    ...（省略）...
```

**環境**
- Spring Boot 3.5.0
- Spring Batch 5.2.2
- Spring Data MongoDB 3.5.0
- MongoDB Driver: 5.4.0
- Java 21
- MongoDB Server Version: 8.x
- MongoDB Cluster Type: Atlas

**再現手順**
複数のスレッドを起動し、それぞれでジョブを実行するだけで再現できます。

**最小再現コード**
`MongoDBJobRepositoryIntegrationTests`に以下のテストを追加してください:
```java
@Test
	void testParallelJobExecution(@Autowired JobOperator jobOperator, @Autowired Job job) throws Exception {
		int parallelJobs = 10;
		Thread[] threads = new Thread[parallelJobs];
		JobExecution[] executions = new JobExecution[parallelJobs];

		for (int i = 0; i < parallelJobs; i++) {
			final int idx = i;
			threads[i] = new Thread(() -> {
				JobParameters jobParameters = new JobParametersBuilder()
					.addString("name", "foo" + idx)
					.addLocalDateTime("runtime", LocalDateTime.now())
					.toJobParameters();
				try {
					executions[idx] = jobOperator.start(job, jobParameters);
				} catch (Exception e) {
					throw new RuntimeException(e);
				}
			});
			threads[i].start();
		}

		for (Thread t : threads) {
			t.join();
		}

		for (JobExecution exec : executions) {
			Assertions.assertNotNull(exec);
			Assertions.assertEquals(ExitStatus.COMPLETED, exec.getExitStatus());
		}

		MongoCollection<Document> jobInstancesCollection = mongoTemplate.getCollection("BATCH_JOB_INSTANCE");
		MongoCollection<Document> jobExecutionsCollection = mongoTemplate.getCollection("BATCH_JOB_EXECUTION");
		MongoCollection<Document> stepExecutionsCollection = mongoTemplate.getCollection("BATCH_STEP_EXECUTION");

		Assertions.assertEquals(parallelJobs, jobInstancesCollection.countDocuments());
		Assertions.assertEquals(parallelJobs, jobExecutionsCollection.countDocuments());
		Assertions.assertEquals(parallelJobs * 2, stepExecutionsCollection.countDocuments());

		// 検査用に結果をダンプ
		dump(jobInstancesCollection, "job instance = ");
		dump(jobExecutionsCollection, "job execution = ");
		dump(stepExecutionsCollection, "step execution = ");
	}
```



## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-18

この課題の報告と、失敗するテストコードの提供をありがとうございます！

これは確かに有効な課題です。驚いたのは、ジョブリポジトリレベルで`Isolation.SERIALIZABLE`を設定しても問題が発生することです（これは [#4956](https://github.com/spring-projects/spring-batch/issues/4956) の作業の一環として確認します）。さらに驚いたのは、`MongoSequenceIncrementer#nextLongValue`へのスレッドアクセスを同期化しても効果がないように見えることです。MongoDBの専門家にも確認して、MongoDBにおける書き込み保証設定のベストプラクティスを調べ、Spring Batchのデフォルト設定を改善できるか検討します。

### コメント 2 by diydriller

**作成日**: 2025-12-05

@fmbenhassine 
この課題に興味があります。取り組んでもよろしいでしょうか？

### コメント 3 by fmbenhassine

**作成日**: 2025-12-05

@diydriller もちろんです！ご協力いただきありがとうございます 🙏

### コメント 4 by quaff

**作成日**: 2025-12-08

@diydriller 参考までに、[#5145](https://github.com/spring-projects/spring-batch/pull/5145) を提案しました。これは新しいIDアルゴリズムを導入せず、IDの後方互換性を維持しています。

### コメント 5 by diydriller

**作成日**: 2025-12-08

@quaff 
フィードバックありがとうございます。
あなたのPRで`testParallelJobExecution`テストコードを実行したところ、書き込み競合がまだ発生することを確認しました。
書き込み競合は、複数のスレッドが同じドキュメントにアクセスしてインクリメント操作を行うために発生しており、リトライロジックだけでは解決できないようです。

### コメント 6 by quaff

**作成日**: 2025-12-09

> あなたのPRで`testParallelJobExecution`テストコードを実行したところ、書き込み競合がまだ発生することを確認しました。書き込み競合は、複数のスレッドが同じドキュメントにアクセスしてインクリメント操作を行うために発生しており、リトライロジックだけでは解決できないようです。

私のPRは書き込み競合を「排除」するのではなく「緩和」するものです。楽観的ロック失敗に対しては、限られた回数のリトライを行うことが推奨されています。

### コメント 7 by banseok1216

**作成日**: 2025-12-09

私も`MongoDBJobRepository`でこの問題に遭遇しています。

私の考えでは、[#5145](https://github.com/spring-projects/spring-batch/pull/5145) と [#5144](https://github.com/spring-projects/spring-batch/pull/5144) は異なる目的を持っています。[#5145](https://github.com/spring-projects/spring-batch/pull/5145) は小規模で後方互換性のある修正（現在の数値シーケンスIDを維持しつつ、一時的な書き込み競合に対するリトライを追加）であり、[#5144](https://github.com/spring-projects/spring-batch/pull/5144) はより大きな変更（TSID導入、一部のユーザーは現在のIDに依存している可能性あり）です。

6.0.0がすでにリリースされているため、[#5145](https://github.com/spring-projects/spring-batch/pull/5145) は6.xのバグ修正リリースに含めて（そして最新の5.2.xにもバックポートして）いただき、[#5144](https://github.com/spring-projects/spring-batch/pull/5144) はID変更を破壊的変更として扱える次のメジャーバージョンをターゲットにしていただきたいです。

### コメント 8 by fmbenhassine

**作成日**: 2026-01-21

> 6.0.0がすでにリリースされているため、[#5145](https://github.com/spring-projects/spring-batch/pull/5145) は6.xのバグ修正リリースに含めて（そして最新の5.2.xにもバックポートして）いただき、[#5144](https://github.com/spring-projects/spring-batch/pull/5144) はID変更を破壊的変更として扱える次のメジャーバージョンをターゲットにしていただきたいです。

@banseok1216 まさにその通りです！[#5145](https://github.com/spring-projects/spring-batch/pull/5145) を6.0.2にマージして5.2.5にバックポートし、[#5144](https://github.com/spring-projects/spring-batch/pull/5144) はv7向けにスケジュールします。

@diydriller PRをありがとうございます！v7の作業を開始する際にレビューするため、オープンのままにしておきます。
