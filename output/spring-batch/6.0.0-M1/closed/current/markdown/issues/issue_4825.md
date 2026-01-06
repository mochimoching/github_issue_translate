# Remove JobExplorer bean registration from the default batch configuration

**Issue番号**: #4825

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2025-05-05

**ラベル**: in: core, type: enhancement

**URL**: https://github.com/spring-projects/spring-batch/issues/4825

**関連リンク**:
- Commits:
  - [ae2df53](https://github.com/spring-projects/spring-batch/commit/ae2df5396baa25cc5abe68e43508f6d0981dcf68)

## 内容

After #4824 and #4817  , there is no need to auto-configure an additional `JobExplorer` in the default batch configuration since a `JobRepository` is already defined.

This is required to make the default batch configuration work with a `ResourcelessJobRepository` (where there is no meta-data to explore).

