"""GitHub Issue取得スクリプト"""
import argparse
import json
import os
from datetime import datetime
from typing import List, Dict
from config import Config
from github_client import GitHubClient


def save_issues_json(issues: List[Dict], filepath: str) -> None:
    """Issue情報をJSON形式で保存"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON保存完了: {filepath}")


def save_issues_markdown(issues: List[Dict], filepath: str) -> None:
    """Issue情報をMarkdown形式で保存"""
    # リポジトリ名からタイトルを生成
    repo_name = Config.GITHUB_REPO.split('/')[-1]  # "spring-projects/spring-batch" -> "spring-batch"
    repo_display_name = ' '.join(word.capitalize() for word in repo_name.split('-'))  # "spring-batch" -> "Spring Batch"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {repo_display_name} GitHub Issues\n\n")
        f.write(f"取得日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        f.write(f"取得件数: {len(issues)}件\n\n")
        f.write("---\n\n")
        
        for issue in issues:
            f.write(f"## Issue #{issue['number']}: {issue['title']}\n\n")
            f.write(f"**状態**: {issue['state']} | ")
            f.write(f"**作成者**: {issue['author']} | ")
            f.write(f"**作成日**: {issue['created_at'][:10]}\n\n")
            
            if issue.get('labels'):
                f.write(f"**ラベル**: {', '.join(issue['labels'])}\n\n")
            
            if issue.get('milestone'):
                f.write(f"**マイルストーン**: {issue['milestone']}\n\n")
            
            f.write(f"**URL**: {issue['url']}\n\n")
            
            # PR/commitリンクがある場合
            if issue.get('closing_references'):
                refs = issue['closing_references']
                if refs.get('pull_requests') or refs.get('commits'):
                    f.write("**関連リンク**:\n")
                    if refs.get('pull_requests'):
                        f.write("- Pull Requests:\n")
                        for pr_url in refs['pull_requests']:
                            f.write(f"  - {pr_url}\n")
                    if refs.get('commits'):
                        f.write("- Commits:\n")
                        for commit_sha in refs['commits']:
                            commit_url = f"https://github.com/{Config.GITHUB_REPO}/commit/{commit_sha}"
                            f.write(f"  - [{commit_sha[:7]}]({commit_url})\n")
                    f.write("\n")
            
            f.write("### 内容\n\n")
            if issue.get('body'):
                f.write(f"{issue['body']}\n\n")
            else:
                f.write("_本文なし_\n\n")
            
            # コメントがある場合
            if issue.get('comments'):
                f.write("### コメント\n\n")
                for i, comment in enumerate(issue['comments'], 1):
                    f.write(f"#### コメント {i} by {comment['author']}\n\n")
                    f.write(f"**作成日**: {comment['created_at'][:10]}\n\n")
                    f.write(f"{comment['body']}\n\n")
            
            f.write("---\n\n")
    
    print(f"✅ Markdown保存完了: {filepath}")


def save_issues_markdown_separate(issues: List[Dict], base_dir: str) -> None:
    """Issue情報を個別のMarkdownファイルとして保存"""
    # issuesディレクトリを作成
    issues_dir = os.path.join(base_dir, "issues")
    os.makedirs(issues_dir, exist_ok=True)
    
    for issue in issues:
        issue_filename = f"issue_{issue['number']}.md"
        issue_filepath = os.path.join(issues_dir, issue_filename)
        
        with open(issue_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {issue['title']}\n\n")
            f.write(f"**Issue番号**: #{issue['number']}\n\n")
            f.write(f"**状態**: {issue['state']} | ")
            f.write(f"**作成者**: {issue['author']} | ")
            f.write(f"**作成日**: {issue['created_at'][:10]}\n\n")
            
            if issue.get('labels'):
                f.write(f"**ラベル**: {', '.join(issue['labels'])}\n\n")
            
            if issue.get('milestone'):
                f.write(f"**マイルストーン**: {issue['milestone']}\n\n")
            
            f.write(f"**URL**: {issue['url']}\n\n")
            
            # PR/commitリンクがある場合
            if issue.get('closing_references'):
                refs = issue['closing_references']
                if refs.get('pull_requests') or refs.get('commits'):
                    f.write("**関連リンク**:\n")
                    if refs.get('pull_requests'):
                        f.write("- Pull Requests:\n")
                        for pr_url in refs['pull_requests']:
                            f.write(f"  - {pr_url}\n")
                    if refs.get('commits'):
                        f.write("- Commits:\n")
                        for commit_sha in refs['commits']:
                            commit_url = f"https://github.com/{Config.GITHUB_REPO}/commit/{commit_sha}"
                            f.write(f"  - [{commit_sha[:7]}]({commit_url})\n")
                    f.write("\n")
            
            f.write("## 内容\n\n")
            if issue.get('body'):
                f.write(f"{issue['body']}\n\n")
            else:
                f.write("_本文なし_\n\n")
            
            # コメントがある場合
            if issue.get('comments'):
                f.write("## コメント\n\n")
                for i, comment in enumerate(issue['comments'], 1):
                    f.write(f"### コメント {i} by {comment['author']}\n\n")
                    f.write(f"**作成日**: {comment['created_at'][:10]}\n\n")
                    f.write(f"{comment['body']}\n\n")
    
    print(f"✅ Markdown個別ファイル保存完了: {issues_dir}/ ({len(issues)}個のファイル)")


def save_issues_diff(issues: List[Dict], base_dir: str, github: GitHubClient, max_size: int = 50000) -> None:
    """IssueをクローズしたPR/Commitのdiffを個別ファイルとして保存
    
    Args:
        issues: issue情報のリスト
        base_dir: Markdownの基底ディレクトリ（issues_diffはこの下に作成）
        github: GitHubClientインスタンス
        max_size: diffの最大サイズ（文字数）
    """
    # issues_diffディレクトリを作成
    diff_dir = os.path.join(base_dir, "issues_diff")
    os.makedirs(diff_dir, exist_ok=True)
    
    saved_count = 0
    skipped_count = 0
    
    for issue in issues:
        issue_number = issue['number']
        issue_title = issue['title']
        
        print(f"  Issue #{issue_number} のdiffを取得中...")
        
        # 最新のクローズ参照のdiffを取得
        diff_info = github.get_latest_closing_diff(issue_number, max_size)
        
        if diff_info is None:
            print(f"    ⚠️ Issue #{issue_number}: 関連するPR/Commitが見つかりませんでした")
            skipped_count += 1
            continue
        
        # diff出力ファイル
        diff_filename = f"issue_{issue_number}.txt"
        diff_filepath = os.path.join(diff_dir, diff_filename)
        
        with open(diff_filepath, 'w', encoding='utf-8') as f:
            # ヘッダー情報
            f.write(f"Issue #{issue_number}: {issue_title}\n")
            
            if diff_info['type'] == 'pr':
                f.write(f"Reference: PR #{diff_info['number']} ({diff_info['created_at']})\n")
            else:
                f.write(f"Reference: Commit {diff_info['sha'][:7]} ({diff_info['created_at']})\n")
            
            f.write(f"URL: {diff_info['url']}\n")
            f.write("\n--- Diff ---\n")
            f.write(diff_info['diff'])
            
            # 切り詰め警告
            if diff_info['truncated']:
                f.write(f"\n\n[Warning: Diff truncated at {max_size} characters]")
        
        ref_desc = f"PR #{diff_info['number']}" if diff_info['type'] == 'pr' else f"Commit {diff_info['sha'][:7]}"
        truncated_msg = " (truncated)" if diff_info['truncated'] else ""
        print(f"    ✅ {ref_desc}{truncated_msg}")
        saved_count += 1
    
    print(f"✅ Diff保存完了: {diff_dir}/ ({saved_count}個のファイル, {skipped_count}個スキップ)")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='GitHub Issueを取得して保存します'
    )
    
    # Issue取得オプション
    parser.add_argument(
        '--max-issues',
        type=int,
        default=Config.MAX_ISSUES,
        help=f'取得する最大issue数 (デフォルト: {Config.MAX_ISSUES})'
    )
    parser.add_argument(
        '--state',
        choices=['open', 'closed', 'all'],
        default=Config.ISSUE_STATE,
        help=f'issueの状態 (デフォルト: {Config.ISSUE_STATE})'
    )
    parser.add_argument(
        '--issue-number',
        type=int,
        help='特定のissue番号を指定'
    )
    parser.add_argument(
        '--milestone',
        type=str,
        help='マイルストーンで絞り込み（番号、タイトル、"*"=任意、"none"=なし）'
    )
    parser.add_argument(
        '--labels',
        nargs='+',
        help='ラベルで絞り込み(複数指定可能)'
    )
    parser.add_argument(
        '--max-comments',
        type=int,
        default=Config.MAX_COMMENTS,
        help=f'取得する最大コメント数 (デフォルト: {Config.MAX_COMMENTS})'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='出力ファイルパス（指定しない場合は自動生成）'
    )
    parser.add_argument(
        '--no-diff',
        action='store_true',
        default=False,
        help='PR/Commitのdiff取得を無効化（デフォルト: diff取得する）'
    )
    parser.add_argument(
        '--max-diff-size',
        type=int,
        default=50000,
        help='diffの最大サイズ（文字数）超過分は切り詰め (デフォルト: 50000)'
    )
    
    args = parser.parse_args()
    
    try:
        # 出力ディレクトリの作成
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        # GitHub クライアントの初期化
        print("GitHub APIに接続中...")
        github = GitHubClient()
        
        # issueの取得
        print(f"\nissueを取得中...")
        if args.issue_number:
            print(f"Issue #{args.issue_number} を取得")
        else:
            print(f"状態: {args.state}, 最大件数: {args.max_issues}")
        
        issues = github.get_issues(
            state=args.state,
            max_count=args.max_issues,
            issue_number=args.issue_number,
            milestone=args.milestone,
            labels=args.labels
        )
        
        if not issues:
            print("取得できるissueがありません。")
            return
        
        print(f"{len(issues)}件のissueを取得しました。")
        
        # issue番号の若い順にソート
        issues.sort(key=lambda x: x['number'])
        
        # 取得したissueのURLを表示
        print("\n取得したissue:")
        for issue in issues:
            print(f"  - #{issue['number']}: {issue['html_url']}")
        
        # issueの整形
        print("\nissueを整形中...")
        formatted_issues = [
            github.format_issue(issue, include_comments=True, include_references=True)
            for issue in issues
        ]
        
        # コメント数の制限
        for issue in formatted_issues:
            if issue.get('comments') and len(issue['comments']) > args.max_comments:
                issue['comments'] = issue['comments'][:args.max_comments]
        
        # 出力ファイルパスの決定
        milestone_name = args.milestone.replace('/', '_').replace('\\', '_') if args.milestone else "all"
        
        if args.output:
            output_json_filepath = args.output
            output_dir = os.path.dirname(output_json_filepath)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            # Markdown用は別フォルダに出力
            md_base_dir = os.path.join(
                Config.OUTPUT_DIR,
                Config.get_repo_dirname(),
                milestone_name,
                args.state,
                "current",
                "markdown"
            )
            os.makedirs(md_base_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(output_json_filepath))[0]
            output_md_filepath = os.path.join(md_base_dir, f"{base_name}.md")
            md_output_dir = md_base_dir
        else:
            # 自動生成
            # 基底ディレクトリ: output/{repo}/{milestone}/{state}/current/
            base_output_dir = os.path.join(
                Config.OUTPUT_DIR,
                Config.get_repo_dirname(),
                milestone_name,
                args.state,
                "current"
            )
            
            # JSON: output/{repo}/{milestone}/{state}/current/json/issues.json
            json_output_dir = os.path.join(base_output_dir, "json")
            os.makedirs(json_output_dir, exist_ok=True)
            output_json_filepath = os.path.join(json_output_dir, "issues.json")
            
            # Markdown: output/{repo}/{milestone}/{state}/current/markdown/issues.md
            md_output_dir = os.path.join(base_output_dir, "markdown")
            os.makedirs(md_output_dir, exist_ok=True)
            output_md_filepath = os.path.join(md_output_dir, "issues.md")
        
        # JSONファイルとして保存
        save_issues_json(formatted_issues, output_json_filepath)
        
        # Markdownファイルとして保存
        save_issues_markdown(formatted_issues, output_md_filepath)
        
        # Markdown個別ファイルとして保存
        save_issues_markdown_separate(formatted_issues, md_output_dir)
        
        # Diff取得（--no-diffが指定されていない場合）
        if not args.no_diff:
            print("\nPR/Commitのdiffを取得中...")
            save_issues_diff(formatted_issues, md_output_dir, github, args.max_diff_size)
        
        print("\n✅ 処理が完了しました！")
        print(f"取得件数: {len(formatted_issues)}件")
        print(f"JSON出力先: {output_json_filepath}")
        print(f"Markdown出力先: {output_md_filepath}")
        print(f"Markdown個別ファイル: {os.path.join(md_output_dir, 'issues')}/")
        if not args.no_diff:
            print(f"Diff出力先: {os.path.join(md_output_dir, 'issues_diff')}/")
        
    except KeyboardInterrupt:
        print("\n\n処理を中断しました。")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
