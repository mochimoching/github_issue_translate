# Update project template in issue reporting guide

**Issue番号**: #5212

**状態**: closed | **作成者**: fmbenhassine | **作成日**: 2026-01-14

**ラベル**: type: task, status: for-internal-team

**URL**: https://github.com/spring-projects/spring-batch/issues/5212

## 内容

The project template in the [issue reporting guide](https://github.com/spring-projects/spring-batch/blob/main/ISSUE_REPORTING.md) is still using Spring Batch 5. This issue is to update the dependencies and upload a new zip file.

PS: We need to think about a better way to provide such a starter without having to update/upload a zip file every time (maybe a project template under source control to clone by issue reporters)

## コメント

### コメント 1 by scordio

**作成日**: 2026-01-14

> PS: We need to think about a better way to provide such a starter without having to update/upload a zip file every time (maybe a project template under source control to clone by issue reporters)

Not sure if it helps but GitHub has the concept of [template repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

### コメント 2 by fmbenhassine

**作成日**: 2026-01-14

Thank you for the suggestion! We do [not](https://github.com/spring-projects?q=&type=template&language=&sort=) use template repositories in our org as we might end up with many of them which will become unmanageable for us.

