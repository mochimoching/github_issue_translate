"""AI翻訳モジュール"""
import os
from typing import Dict, List, Optional
from config import Config


class Translator:
    """AI翻訳クラス"""
    
    def __init__(self, translation_style: str = 'free', prompts_dir: str = 'prompts'):
        """
        Args:
            translation_style: 翻訳スタイル ('literal'=直訳, 'free'=意訳, 'balanced'=バランス型)
            prompts_dir: プロンプトテンプレートファイルのディレクトリパス
        """
        self.provider = Config.get_ai_provider()
        self._client = None
        self.translation_style = translation_style
        self.prompts_dir = prompts_dir
        self._load_prompt_templates()
    
    def _load_prompt_templates(self):
        """プロンプトテンプレートファイルを読み込み"""
        # ベーステンプレートを読み込み
        base_template_path = os.path.join(self.prompts_dir, 'translation_base.md')
        with open(base_template_path, 'r', encoding='utf-8') as f:
            self.base_template = f.read()
        
        # スタイル別の指示を読み込み
        style_template_path = os.path.join(self.prompts_dir, f'style_{self.translation_style}.md')
        with open(style_template_path, 'r', encoding='utf-8') as f:
            self.style_instruction = f.read()
        
        # コードフォーマットルールを読み込み
        code_format_title_path = os.path.join(self.prompts_dir, 'code_format_title.md')
        with open(code_format_title_path, 'r', encoding='utf-8') as f:
            self.code_format_title = f.read()
        
        code_format_body_path = os.path.join(self.prompts_dir, 'code_format_body.md')
        with open(code_format_body_path, 'r', encoding='utf-8') as f:
            self.code_format_body = f.read()
    
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
        """翻訳用のプロンプトを構築（外部テンプレートを使用）"""
        
        # タイトルか本文かでコードフォーマットルールを選択
        code_format_rule = self.code_format_title if is_title else self.code_format_body
        
        # コンテキスト情報を追加
        context_section = f"コンテキスト: {context}\n" if context else ""
        
        # テンプレートに変数を埋め込んでプロンプトを構築
        prompt = self.base_template.replace('{STYLE_INSTRUCTION}', self.style_instruction)
        prompt = prompt.replace('{CODE_FORMAT_RULE}', code_format_rule)
        prompt = prompt.replace('{CONTEXT}', context_section)
        prompt = prompt.replace('{TEXT}', text)
        
        return prompt
    
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
