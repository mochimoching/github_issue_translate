# Optimize step executions counting in MongoStepExecutionDao

**Issue番号**: #5061

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-29

**ラベル**: in: core, type: enhancement, related-to: performance, for: backport-to-5.2.x

**URL**: https://github.com/spring-projects/spring-batch/issues/5061

## 内容

As of v5.2.4 / v6.0.0-RC1, the method `MongoStepExecutionDao#countStepExecutions` is not optimized, it uses nested loops to count step executions.

This method should be optimized to perform a count query using a `MongoOperations#count` operation.


## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-05

Resolved in ddbb6174c522999fc697a1603ac4e2c69a676a49, many thanks to @quaff !

