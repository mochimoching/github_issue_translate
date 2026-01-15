*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月14日に生成されました）*

# AbstractCursorItemReader#doCloseでのリソースクリーンアップ順序の誤りにより一貫性のない動作が発生する

**Issue番号**: [#5109](https://github.com/spring-projects/spring-batch/issues/5109)

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
1. カーソルを開く単純な`JdbcCursorItemReader`を作成
2. `reader.open(executionContext)`を呼び出す
3. `reader.close()`を呼び出す
4. 以下を確認:
   - `cleanupOnClose(connection)`がコネクションがすでにクローズされた後に呼び出される
   - コネクションがクローズされているため`setAutoCommit(initialAutoCommit)`が実行されない

問題のある実行順序の例:

```java
JdbcUtils.closeConnection(this.con);   // コネクションはここでクローズされる

cleanupOnClose(this.con);              // クローズ後に実行される
// con.isClosed() == true

if (this.con != null && !this.con.isClosed()) {
    this.con.setAutoCommit(initialConnectionAutoCommit);  // スキップされる
}
```

**責任分担に関する追加メモ**

現在、`doClose()`は`Connection`をクローズすることになってしまっていますが、コネクションは`AbstractCursorItemReader`によって作成・所有されています。これにより、所有モデルが混在してしまっています:

- 親がコネクションを開く
- 子がカーソルレベルのクリーンアップを実行する
- しかし子もコネクションをクローズする

コネクションを作成したコンポーネントがクローズの責任も持つ方がより一貫性があります。リーダーサブクラスは、`ResultSet`や`PreparedStatement`などのカーソル関連リソースのみを解放すべきです。

提案された変更は、クローズ動作をその所有モデルに合わせるものです。
