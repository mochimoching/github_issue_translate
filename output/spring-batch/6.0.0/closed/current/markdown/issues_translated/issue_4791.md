*このドキュメントは生成AI(Claude Sonnet 4.5)によって2025年12月31日に生成されました。*

# リファレンスドキュメントにおけるジョブパラメータの例への不明確な参照

**Issue番号**: #4791

**状態**: closed | **作成者**: quaff | **作成日**: 2025-03-26

**ラベル**: in: documentation, type: bug

**URL**: https://github.com/spring-projects/spring-batch/issues/4791

**関連リンク**:
- Commits:
  - [8020331](https://github.com/spring-projects/spring-batch/commit/8020331dc0a0950f3f759bb520490c9a0ab611fc)

## 内容

https://docs.spring.io/spring-batch/reference/domain.html#jobParameters

>> 前述の例では、1月1日の1つのインスタンスと1月2日の別のインスタンスがありますが、実際にはJobは1つしかなく、2つのJobParameterオブジェクトを持っています。1つは01-01-2017というジョブパラメータで開始され、もう1つは01-02-2017というパラメータで開始されたものです。

この図には01-01-2017と01-02-2017の2つのインスタンスが表示されていません。

## コメント

### コメント 1 by fmbenhassine

**作成日**: 2025-11-19

テキストは前のセクション[JobInstance](https://docs.spring.io/spring-batch/reference/domain.html#jobinstance)の前述の例を参照して、現在のセクションで説明を続けていると思います。以下は前のセクションのテキストです:

```
たとえば、1月1日の実行、1月2日の実行などがあります。1月1日の実行が最初に失敗し、翌日に再実行された場合、それは依然として1月1日の実行です。(通常、これは処理するデータにも対応しており、1月1日の実行は1月1日のデータを処理することを意味します)。したがって、各JobInstanceは複数の実行(JobExecutionについては本章で後ほど詳しく説明します)を持つことができ、特定のJobと識別するJobParametersに対応する1つのJobInstanceのみが同時に実行できます。
```

テキストには「前述の図では」や「この図には2つのインスタンスがあります」とは書かれていません。例が最初に紹介された前のセクションへのリンクを追加してテキストを更新します。


