*（このドキュメントは生成AI(Claude Opus 4.5)によって2026年1月20日に生成されました）*

# AbstractCursorItemReader#doCloseでのリソースクリーンアップ順序の誤りにより一貫性のない動作が発生する

**Issue番号**: #5109

**状態**: closed | **作成者**: banseok1216 | **作成日**: 2025-11-25

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5109

## 内容

**バグの説明**
`AbstractCursorItemReader#doClose`がJDBCリソースを誤った順序でクローズしています。

**環境**
Spring Batch: 6.0.0
Java: Java 21

**再現手順**
問題を再現する手順です。

**期待される動作**
1. カーソルを開くシンプルな`JdbcCursorItemReader`を作成します。
2. `reader.open(executionContext)`を呼び出します。
3. `reader.close()`を呼び出します。
4. 以下の現象が確認できます:
   - `cleanupOnClose(connection)`がコネクションのクローズ後に呼び出される。
   - コネクションがクローズされているため、`setAutoCommit(initialAutoCommit)`が実行されない。

問題のある実行順序の例:

```java
JdbcUtils.closeConnection(this.con);   // ここでコネクションがクローズされる

cleanupOnClose(this.con);              // クローズ後に実行される
// con.isClosed() == true

if (this.con != null && !this.con.isClosed()) {
    this.con.setAutoCommit(initialConnectionAutoCommit);  // スキップされる
}
```

**責任の所在に関する追加メモ**

現在、`doClose()`は`Connection`をクローズしてしまいますが、コネクションは`AbstractCursorItemReader`によって作成・管理されています。これにより、所有権モデルが混在することになります:

- 親クラスがコネクションを開く
- 子クラスがカーソルレベルのクリーンアップを行う
- しかし子クラスがコネクションもクローズしてしまう

コネクションを作成したコンポーネントがクローズの責任も持つほうが一貫性があります。リーダーのサブクラスは`ResultSet`や`PreparedStatement`などのカーソル関連のリソースのみを解放すべきです。

提案された変更は、クローズ動作をこの所有権モデルに合わせるものです。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-15

この問題を報告いただき、また修正に貢献いただきありがとうございます！
