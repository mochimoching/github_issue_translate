# SQL Server DDL for metadata tables should use NVARCHAR to prevent performance degradation and deadlocks from implicit conversion

**Issue番号**: #5064

**状態**: closed | **作成者**: Chienlin1014 | **作成日**: 2025-10-30

**ラベル**: in: core, type: enhancement, related-to: ddl-scripts

**URL**: https://github.com/spring-projects/spring-batch/issues/5064

**関連リンク**:
- Commits:
  - [ee050d6](https://github.com/spring-projects/spring-batch/commit/ee050d66b0f00f7e03365835f160d4a3f133bda1)
  - [525d9b0](https://github.com/spring-projects/spring-batch/commit/525d9b0ee640898a6cf11f844e365adfb19b6dee)

## 内容

 Hello Spring Batch Team,

  I'm reporting a significant performance issue and a potential for deadlocks when using Spring Batch with a SQL Server database. The root cause is a data type mismatch between the default
   Spring Batch schema and the default behavior of the Microsoft JDBC driver.

  The Problem

  The default DDL for SQL Server metadata tables (e.g., BATCH_JOB_INSTANCE's JOB_NAME, JOB_KEY) defines these columns as VARCHAR. However, the Microsoft JDBC Driver for SQL Server sends
  string parameters as NVARCHAR by default.

  This mismatch forces SQL Server to perform an implicit data type conversion (CONVERT_IMPLICIT) on the VARCHAR column for every comparison.

  Impact: Performance Degradation and Deadlocks

  This implicit conversion prevents efficient index usage. The query optimizer, despite showing an Index Seek operation, actually performs a costly range scan due to the CONVERT_IMPLICIT
  in the WHERE clause and the use of GetRangeThroughConvert to define a search range. This behavior leads to substantial performance degradation that worsens linearly with data growth.

  This severe performance degradation causes transactions to hold locks for much longer. Under high concurrency, this dramatically increases lock contention and the risk of deadlocks. We
  have confirmed these deadlocks occur even at the READ COMMITTED isolation level, as the range scan acquires broader range locks, leading to mutual waiting during INSERT attempts.

  Proposed Solution

  To resolve this at its root, I propose updating the schema-sqlserver.sql file to change all relevant string columns in the metadata tables from `VARCHAR` to `NVARCHAR`. This aligns the
  database schema with the JDBC driver's default behavior, ensuring efficient index usage and preventing these performance and deadlock issues.

  Thank you for your consideration.


