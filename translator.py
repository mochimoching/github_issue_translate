"""AI翻訳モジュール"""
from typing import Dict, List, Optional
from config import Config


class Translator:
    """AI翻訳クラス"""
    
    def __init__(self, translation_style: str = 'balanced'):
        """
        Args:
            translation_style: 翻訳スタイル ('literal'=直訳, 'free'=意訳, 'balanced'=バランス型)
        """
        self.provider = Config.get_ai_provider()
        self._client = None
        self.translation_style = translation_style
    
    def _get_client(self):
        """AIクライアントを取得（遅延初期化）"""
        if self._client is not None:
            return self._client
        
        if self.provider == 'openai':
            from openai import OpenAI
            self._client = OpenAI(api_key=Config.OPENAI_API_KEY)
        elif self.provider == 'azure':
            from openai import AzureOpenAI
            self._client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
        elif self.provider == 'claude':
            from anthropic import Anthropic
            self._client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        return self._client
    
    def translate_text(self, text: str, context: str = "", is_title: bool = False) -> str:
        """
        テキストを日本語に翻訳
        
        Args:
            text: 翻訳するテキスト
            context: コンテキスト情報（オプション）
            is_title: タイトルかどうか（タイトルの場合はコードフォーマット不要）
        
        Returns:
            翻訳されたテキスト
        """
        if not text or not text.strip():
            return ""
        
        prompt = self._build_translation_prompt(text, context, is_title)
        
        try:
            if self.provider in ['openai', 'azure']:
                return self._translate_openai(prompt)
            elif self.provider == 'claude':
                return self._translate_claude(prompt)
        except Exception as e:
            print(f"翻訳エラー: {e}")
            return f"[翻訳エラー: {str(e)}]"
    
    def _build_translation_prompt(self, text: str, context: str = "", is_title: bool = False) -> str:
        """翻訳用のプロンプトを構築"""
        
        # 翻訳スタイルに応じた要件を設定
        if self.translation_style == 'literal':
            style_instruction = """翻訳スタイル: 直訳
- 原文の構造と表現をできるだけ忠実に保つ
- 原語の順序を尊重し、直接的な翻訳を行う
- 意訳や意訳的な表現を避ける
- 文字通りの翻訳を優先する"""
        elif self.translation_style == 'free':
            style_instruction = """翻訳スタイル: 意訳
- 原文の意図とニュアンスを正確に伝える
- 日本語として最も自然で読みやすい表現を使用
- 必要に応じて文構造を変更しても良い
- 日本語読者にとって理解しやすい表現を優先する"""
        else:  # balanced
            style_instruction = """翻訳スタイル: バランス型
- 原文の意図を正確に伝えながら、自然な日本語を使用
- 直訳と意訳のバランスを取る
- 技術的な正確さと読みやすさを両立させる"""
        
        # タイトルの場合はコードフォーマット不要
        if is_title:
            code_format_rule = "- クラス名やメソッド名もそのまま翻訳し、バッククォート(``)で囲まないこと"
        else:
            code_format_rule = """- クラス名、メソッド名、変数名、ファイル名などのプログラムコードは必ずバッククォート(``)で囲むこと
  例: "JobRepository class" → "`JobRepository`クラス"
  例: "the execute method" → "`execute`メソッド"
  例: "StepExecution object" → "`StepExecution`オブジェクト\""""
        
        base_prompt = f"""以下の英語のテキストを日本語に翻訳してください。

{style_instruction}

共通要件:
- Spring Batchなどの固有名詞はそのまま保持すること
- コードブロックやマークダウン記法はそのまま保持すること
{code_format_rule}
- 技術用語は適切な日本語訳を使用すること(例: "issue" → "課題"、"feature" → "機能")
- 丁寧で読みやすい文章にすること

"""
        if context:
            base_prompt += f"コンテキスト: {context}\n\n"
        
        base_prompt += f"翻訳するテキスト:\n{text}\n\n翻訳結果のみを出力してください。"
        return base_prompt
    
    def _translate_openai(self, prompt: str) -> str:
        """OpenAI APIで翻訳"""
        client = self._get_client()
        model = Config.AZURE_OPENAI_DEPLOYMENT if self.provider == 'azure' else Config.OPENAI_MODEL
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは技術文書の翻訳に特化した翻訳アシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
    
    def _translate_claude(self, prompt: str) -> str:
        """Claude APIで翻訳"""
        client = self._get_client()
        
        response = client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=4000,
            temperature=0.3,
            system="あなたは技術文書の翻訳に特化した翻訳アシスタントです。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text.strip()
    
    def _convert_issue_refs_to_links(self, text: str) -> str:
        """
        テキスト内のissue番号参照（#XXXX）をリンクに変換
        
        Args:
            text: 変換するテキスト
        
        Returns:
            issue番号がリンクに変換されたテキスト
        """
        import re
        # #数字のパターンを検出（コードブロック内やURLの一部でない場合）
        # 例: #5093 -> [#5093](https://github.com/{Config.GITHUB_REPO}/issues/5093)
        def replace_issue_ref(match):
            issue_num = match.group(1)
            return f"[#{issue_num}](https://github.com/spring-projects/spring-batch/issues/{issue_num})"
        
        # バッククォートで囲まれていない #数字 をリンクに変換
        # (?<!`) は直前にバッククォートがないことを確認（ネガティブ後読み）
        # (?!`) は直後にバッククォートがないことを確認（ネガティブ先読み）
        pattern = r'(?<!`)#(\d+)(?!`)'
        return re.sub(pattern, replace_issue_ref, text)
    
    def translate_issue(
        self,
        issue: Dict,
        translate_comments: bool = False,
        max_comments: int = 5
    ) -> Dict:
        """
        issueを翻訳
        
        Args:
            issue: 翻訳するissue
            translate_comments: コメントも翻訳するか
            max_comments: 翻訳する最大コメント数
        
        Returns:
            翻訳されたissue
        """
        print(f"Issue #{issue['number']} を翻訳中: {issue['title'][:50]}...")
        
        translated = issue.copy()
        
        # タイトルを翻訳（issue番号は除外、コードフォーマットなし）
        translated['title_ja'] = self.translate_text(
            issue['title'],
            context="issueタイトル。Issue番号は含めずにタイトル部分のみを翻訳してください。",
            is_title=True
        ).strip()
        
        # "Issue #" や "issue #" などのプレフィックスを削除
        import re
        translated['title_ja'] = re.sub(r'^[Ii]ssue\s*#\d+:\s*', '', translated['title_ja'])
        
        # 本文を翻訳
        translated['body_ja'] = self.translate_text(
            issue['body'],
            context=f"issue本文 (タイトル: {issue['title']})"
        )
        # issue番号参照をリンクに変換
        translated['body_ja'] = self._convert_issue_refs_to_links(translated['body_ja'])
        
        # コメントを翻訳
        if translate_comments and 'comments' in issue:
            translated['comments_ja'] = []
            for i, comment in enumerate(issue['comments'][:max_comments]):
                if i >= max_comments:
                    break
                
                print(f"  コメント {i+1}/{min(len(issue['comments']), max_comments)} を翻訳中...")
                translated_comment = comment.copy()
                translated_comment['body_ja'] = self.translate_text(
                    comment['body'],
                    context=f"Issue #{issue['number']} のコメント"
                )
                # issue番号参照をリンクに変換
                translated_comment['body_ja'] = self._convert_issue_refs_to_links(translated_comment['body_ja'])
                translated['comments_ja'].append(translated_comment)
        
        print(f"Issue #{issue['number']} の翻訳完了")
        return translated
    
    def translate_issues(
        self,
        issues: List[Dict],
        translate_comments: bool = False,
        max_comments: int = 5
    ) -> List[Dict]:
        """
        複数のissueを翻訳
        
        Args:
            issues: 翻訳するissueのリスト
            translate_comments: コメントも翻訳するか
            max_comments: 各issueで翻訳する最大コメント数
        
        Returns:
            翻訳されたissueのリスト
        """
        translated_issues = []
        
        for i, issue in enumerate(issues, 1):
            print(f"\n[{i}/{len(issues)}] ", end="")
            translated = self.translate_issue(issue, translate_comments, max_comments)
            translated_issues.append(translated)
        
        return translated_issues
