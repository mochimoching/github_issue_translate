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
    
    def get_commit_diff(self, sha: str) -> Optional[str]:
        """
        コミットのdiffを取得
        
        Args:
            sha: コミットのSHA
        
        Returns:
            diff文字列、取得失敗時はNone
        """
        url = f"{self.base_url}/repos/{self.repo}/commits/{sha}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Commit diff取得エラー ({sha[:7]}): {e}")
            return None
    
    def get_pull_request_diff(self, pr_number: int) -> Optional[str]:
        """
        Pull Requestのdiffを取得
        
        Args:
            pr_number: PR番号
        
        Returns:
            diff文字列、取得失敗時はNone
        """
        url = f"{self.base_url}/repos/{self.repo}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"PR diff取得エラー (#{pr_number}): {e}")
            return None
    
    def get_closing_references_with_timestamps(self, issue_number: int) -> Dict:
        """
        issueをクローズしたPRやcommitのリンクをタイムスタンプ付きで取得
        
        Args:
            issue_number: issue番号
        
        Returns:
            {
                'pull_requests': [{'url': str, 'number': int, 'created_at': str}, ...],
                'commits': [{'sha': str, 'created_at': str}, ...],
                'latest_reference': {'type': 'pr'|'commit', 'number': int|None, 'sha': str|None, 'url': str, 'created_at': str} | None
            }
        """
        pull_requests = []
        commits = []
        
        # Timeline APIを使用して詳細な情報を取得
        timeline_url = f"{self.base_url}/repos/{self.repo}/issues/{issue_number}/timeline"
        timeline_headers = self.headers.copy()
        timeline_headers["Accept"] = "application/vnd.github.mockingbird-preview+json"
        
        try:
            response = requests.get(timeline_url, headers=timeline_headers, timeout=30)
            response.raise_for_status()
            timeline_events = response.json()
            
            for event in timeline_events:
                event_type = event.get('event')
                created_at = event.get('created_at', '')
                
                # closedイベントでcommit_idがある場合
                if event_type == 'closed' and event.get('commit_id'):
                    commit_sha = event['commit_id']
                    commits.append({
                        'sha': commit_sha,
                        'created_at': created_at
                    })
                
                # cross-referencedイベント: PRからの参照
                if event_type == 'cross-referenced':
                    source = event.get('source', {})
                    issue_data = source.get('issue', {})
                    if issue_data.get('pull_request'):
                        pr_url = issue_data['html_url']
                        pr_number = issue_data['number']
                        pull_requests.append({
                            'url': pr_url,
                            'number': pr_number,
                            'created_at': created_at
                        })
                
                # referencedイベント
                if event_type == 'referenced' and event.get('commit_id'):
                    commit_sha = event['commit_id']
                    commits.append({
                        'sha': commit_sha,
                        'created_at': created_at
                    })
        
        except requests.exceptions.RequestException as e:
            print(f"Timeline取得エラー (issue #{issue_number}): {e}")
        
        # 重複を削除（PRはnumber、commitはshaで判定）
        seen_pr_numbers = set()
        unique_prs = []
        for pr in pull_requests:
            if pr['number'] not in seen_pr_numbers:
                seen_pr_numbers.add(pr['number'])
                unique_prs.append(pr)
        
        seen_shas = set()
        unique_commits = []
        for commit in commits:
            if commit['sha'] not in seen_shas:
                seen_shas.add(commit['sha'])
                unique_commits.append(commit)
        
        # 最新の参照を特定（created_atでソート）
        latest_reference = None
        all_refs = []
        
        for pr in unique_prs:
            all_refs.append({
                'type': 'pr',
                'number': pr['number'],
                'sha': None,
                'url': pr['url'],
                'created_at': pr['created_at']
            })
        
        for commit in unique_commits:
            all_refs.append({
                'type': 'commit',
                'number': None,
                'sha': commit['sha'],
                'url': f"https://github.com/{self.repo}/commit/{commit['sha']}",
                'created_at': commit['created_at']
            })
        
        if all_refs:
            # created_atでソートして最新を取得
            all_refs.sort(key=lambda x: x['created_at'], reverse=True)
            latest_reference = all_refs[0]
        
        return {
            'pull_requests': unique_prs,
            'commits': unique_commits,
            'latest_reference': latest_reference
        }
    
    def get_latest_closing_diff(self, issue_number: int, max_size: int = 50000) -> Optional[Dict]:
        """
        issueをクローズした最新のPRまたはcommitのdiffを取得
        PRがある場合はPRを優先（マージコミットとの重複を避けるため）
        
        Args:
            issue_number: issue番号
            max_size: diffの最大サイズ（文字数）
        
        Returns:
            {
                'type': 'pr' | 'commit',
                'number': int | None,
                'sha': str | None,
                'url': str,
                'created_at': str,
                'diff': str,
                'truncated': bool
            } | None
        """
        refs = self.get_closing_references_with_timestamps(issue_number)
        
        # PRを優先
        if refs['pull_requests']:
            # 最新のPRを使用
            prs_sorted = sorted(refs['pull_requests'], key=lambda x: x['created_at'], reverse=True)
            latest_pr = prs_sorted[0]
            
            diff = self.get_pull_request_diff(latest_pr['number'])
            if diff is not None:
                truncated = len(diff) > max_size
                if truncated:
                    diff = diff[:max_size]
                
                return {
                    'type': 'pr',
                    'number': latest_pr['number'],
                    'sha': None,
                    'url': latest_pr['url'],
                    'created_at': latest_pr['created_at'],
                    'diff': diff,
                    'truncated': truncated
                }
        
        # PRがない場合はcommitを使用
        if refs['commits']:
            # 最新のcommitを使用
            commits_sorted = sorted(refs['commits'], key=lambda x: x['created_at'], reverse=True)
            latest_commit = commits_sorted[0]
            
            diff = self.get_commit_diff(latest_commit['sha'])
            if diff is not None:
                truncated = len(diff) > max_size
                if truncated:
                    diff = diff[:max_size]
                
                return {
                    'type': 'commit',
                    'number': None,
                    'sha': latest_commit['sha'],
                    'url': f"https://github.com/{self.repo}/commit/{latest_commit['sha']}",
                    'created_at': latest_commit['created_at'],
                    'diff': diff,
                    'truncated': truncated
                }
        
        return None
