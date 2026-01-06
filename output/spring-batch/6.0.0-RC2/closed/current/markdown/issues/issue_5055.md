# Change configuration log level to debug

**Issue番号**: #5055

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-10-28

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/5055

**関連リンク**:
- Commits:
  - [c1ec7cc](https://github.com/spring-projects/spring-batch/commit/c1ec7cc9d8de3633718d99526d2dcade056c3aad)
  - [136bc8a](https://github.com/spring-projects/spring-batch/commit/136bc8a81a4329054c776ae6614f8d1b9bd40b65)

## 内容

Currently, the log level for batch infrastructure configuration is set to `INFO`, which makes the output quite verbose for no real added value. Configuration details should be logged at `DEBUG` level.

