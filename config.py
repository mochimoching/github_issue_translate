"""設定管理モジュール"""
import os
from typing import Optional
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class Config:
    """アプリケーション設定"""
    
    # GitHub設定
    GITHUB_TOKEN: Optional[str] = os.getenv('GITHUB_TOKEN', '').strip() or None
    # GITHUB_REPO: str = "spring-projects/spring-framework"
    GITHUB_REPO: str = "spring-projects/spring-batch"
    
    # AI API設定
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Azure OpenAI設定
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = os.getenv('AZURE_OPENAI_DEPLOYMENT')
    AZURE_OPENAI_API_VERSION: str = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    
    # Anthropic Claude設定
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL: str = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
    
    # 取得設定
    MAX_ISSUES: int = int(os.getenv('MAX_ISSUES', '100'))
    ISSUE_STATE: str = os.getenv('ISSUE_STATE', 'open')
    MAX_COMMENTS: int = int(os.getenv('MAX_COMMENTS', '20'))
    
    # 出力設定
    OUTPUT_DIR: str = 'output'
    
    @classmethod
    def get_repo_dirname(cls) -> str:
        """GitHubリポジトリ名からディレクトリ名を取得"""
        # "spring-projects/spring-batch" -> "spring-batch"
        return cls.GITHUB_REPO.split('/')[-1]
    
    @classmethod
    def get_ai_provider(cls) -> str:
        """使用するAIプロバイダーを判定"""
        if cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT:
            return 'azure'
        elif cls.OPENAI_API_KEY:
            return 'openai'
        elif cls.ANTHROPIC_API_KEY:
            return 'claude'
        else:
            raise ValueError(
                "AI APIキーが設定されていません。"
                ".envファイルにOPENAI_API_KEY、AZURE_OPENAI_API_KEY、"
                "またはANTHROPIC_API_KEYを設定してください。"
            )
    
    @classmethod
    def validate(cls) -> None:
        """設定の妥当性を検証"""
        cls.get_ai_provider()  # AIプロバイダーが設定されているか確認
        
        if cls.ISSUE_STATE not in ['open', 'closed', 'all']:
            raise ValueError(f"ISSUE_STATEは'open', 'closed', 'all'のいずれかである必要があります: {cls.ISSUE_STATE}")
        
        if cls.MAX_ISSUES < 1:
            raise ValueError(f"MAX_ISSUESは1以上である必要があります: {cls.MAX_ISSUES}")
