*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月15日に生成されました）*

# AbstractCursorItemReader#doCloseのリソースクリーンアップ順序が不正で一貫性のない動作を引き起こす

**課題番号**: [#5109](https://github.com/spring-projects/spring-batch/issues/5109)

**状態**: open | **作成者**: banseok1216 | **作成日**: 2025-11-25

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5109

## 内容

**バグの説明**
`AbstractCursorItemReader#doClose`がJDBCリソースを不正な順序でクローズしています。

**環境**
Spring Batch: 6.0.0
Java: Java 21

**再現手順**
問題を再現する手順。

**期待される動作**
1. カーソルを開くシンプルな`JdbcCursorItemReader`を作成します。
2. `reader.open(executionContext)`を呼び出します。
3. `reader.close()`を呼び出します。
4. 以下を確認します:
   - `cleanupOnClose(connection)`がコネクションがすでにクローズされた後に呼び出される。
   - `setAutoCommit(initialAutoCommit)`はコネクションがクローズされているため実行されない。

問題のある実行順序の例:

```java
JdbcUtils.closeConnection(this.con);   // ここでコネクションがクローズされる

cleanupOnClose(this.con);              // クローズ後に実行される
// con.isClosed() == true

if (this.con != null && !this.con.isClosed()) {
    this.con.setAutoCommit(initialConnectionAutoCommit);  // スキップされる
}
```

**責任の所在に関する補足**

現在、`doClose()`はコネクションを作成し所有しているのが`AbstractCursorItemReader`であるにもかかわらず、最終的に`Connection`をクローズしています。これは所有権モデルの混在を招いています:

- 親がコネクションを開く
- 子がカーソルレベルのクリーンアップを実行する
- しかし子がコネクションもクローズする

コネクションを作成したコンポーネントがそのクローズも担当する方が一貫性があります。リーダーのサブクラスは`ResultSet`や`PreparedStatement`などのカーソル関連リソースのみを解放すべきです。

提案する変更は、クローズの動作をその所有権モデルに合わせるものです。
