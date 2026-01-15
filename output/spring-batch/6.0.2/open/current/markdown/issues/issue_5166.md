# Wrong database migration to spring-batch 6.x for DB2LUW

**Issue番号**: #5166

**状態**: open | **作成者**: bekoenig | **作成日**: 2025-12-15

**ラベル**: type: bug, in: core

**URL**: https://github.com/spring-projects/spring-batch/issues/5166

## 内容

Hi,

[this migration](https://github.com/spring-projects/spring-batch/blob/98c10cd981b5f4ddc65e7071f6a603a3781514fd/spring-batch-core/src/main/resources/org/springframework/batch/core/migration/6.0/migration-db2.sql#L2) is only applicable to Informix servers. IBM DB2 LUW (10.1+) does not support sequence renaming (see [reference](https://www.ibm.com/docs/en/db2/12.1.x?topic=statements-rename)).

To address this lack of support, we implemented a Java-based migration that retrieves the last sequence number and creates a new sequence starting from this value.

Best regards,
Ben

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2026-01-13

Thank you for reporting this!

> To address this lack of support, we implemented a Java-based migration that retrieves the last sequence number and creates a new sequence starting from this value.

Indeed, if IBM DB2 LUW (10.1+) does not support sequence renaming, then users should find a way to create a new sequence starting from the last value of the previous one. I will add a note about that in the migration script.

