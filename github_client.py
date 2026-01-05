"""GitHub APIクライアント"""
import requests
from typing import List, Dict, Optional
from config import Config


class GitHubClient:
    """GitHub API クライアント"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.repo = Config.GITHUB_REPO
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Spring-Batch-Issue-Translator"
        }
        
        if Config.GITHUB_TOKEN:
            # Ensure token is ASCII-compatible
            try:
                Config.GITHUB_TOKEN.encode('ascii')
                self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"
            except UnicodeEncodeError:
                print("警告: GITHUB_TOKENに非ASCII文字が含まれています。トークンを無効化します。")
                pass
    
    def get_milestone_number(self, milestone_title: str) -> Optional[str]:
        """
        マイルストーンのタイトルから番号を取得
        
        Args:
            milestone_title: マイルストーンのタイトル
        
        Returns:
            マイルストーン番号（文字列）、見つからない場合はNone
        """
        url = f"{self.base_url}/repos/{self.repo}/milestones"
        
        try:
            # ページネーションで全マイルストーンを取得
            page = 1
            while True:
                params = {"state": "all", "per_page": 100, "page": page}
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                milestones = response.json()
                
                if not milestones:
                    break
                
                for milestone in milestones:
                    if milestone['title'] == milestone_title:
                        return str(milestone['number'])
                
                page += 1
            
            return None
        except requests.exceptions.RequestException as e:
            print(f"マイルストーン取得エラー: {e}")
            return None
    
    def get_issues(
        self,
        state: str = 'open',
        max_count: int = 10,
        issue_number: Optional[int] = None,
        milestone: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        issueを取得
        
        Args:
            state: issue状態 ('open', 'closed', 'all')
            max_count: 取得する最大件数
            issue_number: 特定のissue番号を指定する場合
            milestone: マイルストーン番号または名前 ('*'=任意のマイルストーン, 'none'=マイルストーンなし)
            labels: ラベルのリスト（複数指定可能）
        
        Returns:
            issueのリスト
        """
        if issue_number is not None:
            # 特定のissueを取得
            return [self._get_single_issue(issue_number)]
        
        # 複数のissueを取得
        url = f"{self.base_url}/repos/{self.repo}/issues"
        params = {
            "state": state,
            "per_page": min(max_count, 100),  # APIの上限は100
            "sort": "created",
            "direction": "desc"
        }
        
        # オプションのフィルタを追加
        if milestone:
            # 特殊な値でない場合、タイトルから番号を取得
            if milestone not in ['*', 'none']:
                # 数値かどうかチェック
                if not milestone.isdigit():
                    print(f"マイルストーン '{milestone}' の番号を検索中...")
                    milestone_number = self.get_milestone_number(milestone)
                    if milestone_number:
                        milestone = milestone_number
                        print(f"マイルストーン番号: {milestone}")
                    else:
                        print(f"警告: マイルストーン '{milestone}' が見つかりませんでした。フィルタなしで取得します。")
                        milestone = None
            
            if milestone:
                params["milestone"] = milestone
        
        if labels:
            params["labels"] = ",".join(labels)
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            issues = response.json()
            print(f"デバッグ: {len(issues)}件のissue/PRを取得")
            
            # Pull Requestを除外 (GitHubではPRもissueとして扱われる)
            issues = [issue for issue in issues if 'pull_request' not in issue]
            print(f"デバッグ: PR除外後: {len(issues)}件のissue")
            
            return issues[:max_count]
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API エラー: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"レスポンス: {e.response.text[:500]}")
            raise
    
    def _get_single_issue(self, issue_number: int) -> Dict:
        """
        特定のissueを取得
        
        Args:
            issue_number: issue番号
        
        Returns:
            issueの詳細
        """
        url = f"{self.base_url}/repos/{self.repo}/issues/{issue_number}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"GitHub API エラー (issue #{issue_number}): {e}")
            raise
    
    def get_issue_comments(self, issue_number: int) -> List[Dict]:
        """
        issueのコメントを取得
        
        Args:
            issue_number: issue番号
        
        Returns:
            コメントのリスト
        """
        url = f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/comments"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"コメント取得エラー (issue #{issue_number}): {e}")
            return []
    
    def get_issue_events(self, issue_number: int) -> List[Dict]:
        """
        issueのイベントを取得（PR/commitリンクを含む）
        
        Args:
            issue_number: issue番号
        
        Returns:
            イベントのリスト
        """
        url = f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/events"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"イベント取得エラー (issue #{issue_number}): {e}")
            return []
    
    def get_closing_references(self, issue_number: int) -> Dict[str, List[str]]:
        """
        issueをクローズしたPRやcommitのリンクを取得
        
        Args:
            issue_number: issue番号
        
        Returns:
            {'pull_requests': [PR URLs], 'commits': [commit SHAs]} の辞書
        """
        events = self.get_issue_events(issue_number)
        
        pull_requests = []
        commits = []
        
        for event in events:
            # closedイベントでcommit_idがある場合
            if event.get('event') == 'closed' and event.get('commit_id'):
                commit_sha = event['commit_id']
                commits.append(commit_sha)
            
            # PRによるクローズの場合（commit_url経由）
            if event.get('commit_url'):
                commits.append(event['commit_url'].split('/')[-1])
        
        # Timeline APIも使用してより詳細な情報を取得
        timeline_url = f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/timeline"
        timeline_headers = self.headers.copy()
        timeline_headers["Accept"] = "application/vnd.github.mockingbird-preview+json"
        
        try:
            response = requests.get(timeline_url, headers=timeline_headers, timeout=30)
            response.raise_for_status()
            timeline_events = response.json()
            
            for event in timeline_events:
                # merged, referenced, closed イベントを確認
                if event.get('event') in ['merged', 'referenced', 'closed']:
                    # PRへの参照がある場合
                    if event.get('source') and event['source'].get('issue'):
                        pr_data = event['source']['issue']
                        if 'pull_request' in pr_data:
                            pull_requests.append(pr_data['html_url'])
                    
                    # commit_idがある場合
                    if event.get('commit_id'):
                        commits.append(event['commit_id'])
                    
                    # sha（commit SHA）がある場合
                    if event.get('sha'):
                        commits.append(event['sha'])
        
        except requests.exceptions.RequestException as e:
            print(f"Timeline取得エラー (issue #{issue_number}): {e}")
        
        # 重複を削除
        return {
            'pull_requests': list(set(pull_requests)),
            'commits': list(set(commits))
        }
    
    def format_issue(self, issue: Dict, include_comments: bool = False, include_references: bool = False) -> Dict:
        """
        issueを整形されたフォーマットに変換
        
        Args:
            issue: 生のissueデータ
            include_comments: コメントを含めるか
            include_references: PR/commitリンクを含めるか
        
        Returns:
            整形されたissueデータ
        """
        formatted = {
            'number': issue['number'],
            'title': issue['title'],
            'state': issue['state'],
            'created_at': issue['created_at'],
            'updated_at': issue['updated_at'],
            'author': issue['user']['login'],
            'url': issue['html_url'],
            'body': issue['body'] or '',
            'labels': [label['name'] for label in issue.get('labels', [])],
        }
        
        if include_comments:
            comments = self.get_issue_comments(issue['number'])
            formatted['comments'] = [
                {
                    'author': comment['user']['login'],
                    'created_at': comment['created_at'],
                    'body': comment['body']
                }
                for comment in comments
            ]
        
        if include_references:
            references = self.get_closing_references(issue['number'])
            formatted['closing_references'] = references
        
        return formatted
