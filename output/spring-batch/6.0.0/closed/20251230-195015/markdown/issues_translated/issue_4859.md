*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# リファレンスドキュメントでMongoDBジョブリポジトリの設定を明確化

**Issue番号**: #4859

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-06-03

**ラベル**: in: documentation, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/4859

**関連リンク**:
- Commits:
  - [17bc8f7](https://github.com/spring-projects/spring-batch/commit/17bc8f70087e9e264c65551f47c1ea6601c53905)

## 内容

v5.2の時点で、MongoDBをジョブリポジトリとして使用するための前提条件が[Configuring a JobRepository](https://docs.spring.io/spring-batch/reference/job/configuring-repository.html)セクションで詳細に説明されていません。[What's new in Spring Batch 5.2](https://docs.spring.io/spring-batch/reference/whatsnew.html#mongodb-job-repository-support)セクションにはそれに関する注記がありますが、十分に明確ではありません。

リファレンスドキュメントでは、ジョブを実行する前にMongoDBに対して実行するDDLスクリプトと、正しく動作させるために必要なその他の設定(例えば、Mongoコンバーターで定義する必要がある`MapKeyDotReplacement`など)を明確にする必要があります。


