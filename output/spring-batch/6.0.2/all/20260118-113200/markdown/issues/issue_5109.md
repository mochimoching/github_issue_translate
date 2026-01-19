# Incorrect resource cleanup order in AbstractCursorItemReader#doClose leads to inconsistent behavior

**Issue番号**: #5109

**状態**: open | **作成者**: banseok1216 | **作成日**: 2025-11-25

**ラベル**: in: infrastructure, type: bug, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5109

## 内容

**Bug description**
AbstractCursorItemReader#doClose closes JDBC resources in an incorrect order

**Environment**
Spring Batch: 6.0.0
java: Java 21
**Steps to reproduce**
Steps to reproduce the issue.

**Expected behavior**
1. Create a simple JdbcCursorItemReader that opens a cursor.
2. Call `reader.open(executionContext)`.
3. Call `reader.close()`.
4. Observe that:
   - `cleanupOnClose(connection)` is invoked after the connection is already closed.
   - `setAutoCommit(initialAutoCommit)` is never executed because the connection is closed.

Example of the problematic execution order:

```java
JdbcUtils.closeConnection(this.con);   // connection is closed here

cleanupOnClose(this.con);              // executed after close
// con.isClosed() == true

if (this.con != null && !this.con.isClosed()) {
    this.con.setAutoCommit(initialConnectionAutoCommit);  // skipped
}
```

**Additional note on responsibility**

Currently, `doClose()` ends up closing the `Connection` even though the
connection is created and owned by `AbstractCursorItemReader`. This leads to a
mixed ownership model:

- the parent opens the connection,
- the child performs cursor-level cleanup,
- but the child also closes the connection.

It is more consistent for the component that creates the connection to be the
one responsible for closing it. The reader subclass should only release
cursor-related resources such as the `ResultSet` and `PreparedStatement`.

The proposed change aligns the close behavior with that ownership model.

