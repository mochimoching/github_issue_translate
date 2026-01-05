"""GitHub Issue翻訳スクリプト"""
import argparse
import json
import csv
import os
from datetime import datetime
from typing import List, Dict
from config import Config
from translator import Translator


def load_issues_json(filepath: str) -> List[Dict]:
    """JSONファイルからissue情報を読み込み"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: List[Dict], filepath: str) -> None:
    """JSON形式で保存"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON保存完了: {filepath}")


def save_csv(data: List[Dict], filepath: str) -> None:
    """CSV形式で保存"""
    if not data:
        return
    
    fieldnames = [
        'number', 'title', 'title_ja', 'state', 'author',
        'created_at', 'updated_at', 'url', 'labels',
        'body', 'body_ja'
    ]
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for issue in data:
            # labelsをカンマ区切りの文字列に変換
            row = issue.copy()
            row['labels'] = ', '.join(issue.get('labels', []))
            writer.writerow(row)
    
    print(f"CSV保存完了: {filepath}")


def save_markdown(data: List[Dict], filepath: str, separate_files: bool = False, include_original: bool = False) -> None:
    """Markdown形式で保存
    
    Args:
        data: 翻訳されたissueのリスト
        filepath: 保存先ファイルパス
        separate_files: issueごとに個別ファイルに保存するか
        include_original: 元の英語テキストを含めるか
    """
    # リポジトリ名からタイトルを生成
    repo_name = Config.GITHUB_REPO.split('/')[-1]  # "spring-projects/spring-batch" -> "spring-batch"
    repo_display_name = ' '.join(word.capitalize() for word in repo_name.split('-'))  # "spring-batch" -> "Spring Batch"
    
    # 統合ファイルを常に作成
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {repo_display_name} GitHub Issues 翻訳結果\n\n")
        f.write(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        f.write(f"取得件数: {len(data)}件\n\n")
        f.write("---\n\n")
        
        for issue in data:
            f.write(f"## Issue #{issue['number']}: {issue['title_ja']}\n\n")
            
            if include_original:
                f.write(f"**元のタイトル**: {issue['title']}\n\n")
            
            f.write(f"**状態**: {issue['state']} | ")
            f.write(f"**作成者**: {issue['author']} | ")
            f.write(f"**作成日**: {issue['created_at'][:10]}\n\n")
            
            if issue.get('labels'):
                f.write(f"**ラベル**: {', '.join(issue['labels'])}\n\n")
            
            f.write(f"**URL**: {issue['url']}\n\n")
            
            f.write("### 内容\n\n")
            f.write(f"{issue['body_ja']}\n\n")
            
            if include_original and issue.get('body'):
                f.write("<details>\n")
                f.write("<summary>元の内容（英語）</summary>\n\n")
                f.write(f"{issue['body']}\n\n")
                f.write("</details>\n\n")
            
            # コメントがある場合
            if issue.get('comments_ja'):
                f.write("### コメント\n\n")
                for i, comment in enumerate(issue['comments_ja'], 1):
                    f.write(f"#### コメント {i} by {comment['author']}\n\n")
                    f.write(f"{comment['body_ja']}\n\n")
                    
                    if include_original:
                        f.write("<details>\n")
                        f.write("<summary>元のコメント（英語）</summary>\n\n")
                        f.write(f"{comment['body']}\n\n")
                        f.write("</details>\n\n")
            
            f.write("---\n\n")
    
    print(f"Markdown保存完了: {filepath}")
    
    # separate_filesオプションが有効な場合は個別ファイルも作成
    if separate_files:
        save_markdown_separate(data, filepath, include_original)


def save_markdown_separate(data: List[Dict], base_filepath: str, include_original: bool = False) -> None:
    """issueごとに個別のMarkdownファイルで保存
    
    Args:
        data: 翻訳されたissueのリスト
        base_filepath: ベースとなるファイルパス
        include_original: 元の英語テキストを含めるか
    """
    base_dir = os.path.dirname(base_filepath)
    base_name = os.path.splitext(os.path.basename(base_filepath))[0]
    
    # issueごとのディレクトリを作成
    output_dir = os.path.join(base_dir, base_name)
    os.makedirs(output_dir, exist_ok=True)
    
    for issue in data:
        issue_filename = f"issue_{issue['number']}.md"
        issue_filepath = os.path.join(output_dir, issue_filename)
        
        with open(issue_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {issue['title_ja']}\n\n")
            f.write(f"**Issue番号**: #{issue['number']}\n\n")
            
            if include_original:
                f.write(f"**元のタイトル**: {issue['title']}\n\n")
            
            f.write(f"**状態**: {issue['state']} | ")
            f.write(f"**作成者**: {issue['author']} | ")
            f.write(f"**作成日**: {issue['created_at'][:10]}\n\n")
            
            if issue.get('labels'):
                f.write(f"**ラベル**: {', '.join(issue['labels'])}\n\n")
            
            f.write(f"**URL**: {issue['url']}\n\n")
            
            f.write("## 内容\n\n")
            f.write(f"{issue['body_ja']}\n\n")
            
            if include_original and issue.get('body'):
                f.write("<details>\n")
                f.write("<summary>元の内容（英語）</summary>\n\n")
                f.write(f"{issue['body']}\n\n")
                f.write("</details>\n\n")
            
            # コメントがある場合
            if issue.get('comments_ja'):
                f.write("## コメント\n\n")
                for i, comment in enumerate(issue['comments_ja'], 1):
                    f.write(f"### コメント {i} by {comment['author']}\n\n")
                    f.write(f"{comment['body_ja']}\n\n")
                    
                    if include_original:
                        f.write("<details>\n")
                        f.write("<summary>元のコメント（英語）</summary>\n\n")
                        f.write(f"{comment['body']}\n\n")
                        f.write("</details>\n\n")
    
    print(f"Markdown保存完了: {output_dir}/ ({len(data)}個のファイル)")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='取得済みのGitHub Issueを日本語に翻訳します'
    )
    
    # 入力オプション
    parser.add_argument(
        'input',
        type=str,
        help='入力JSONファイルパス（fetch.pyで取得したファイル）'
    )
    
    # 翻訳オプション
    parser.add_argument(
        '--translation-style',
        choices=['literal', 'free', 'balanced'],
        default='balanced',
        help='翻訳スタイル (literal=直訳, free=意訳, balanced=バランス型, デフォルト: balanced)'
    )
    parser.add_argument(
        '--translate-comments',
        action='store_true',
        help='コメントも翻訳する'
    )
    parser.add_argument(
        '--max-comments',
        type=int,
        default=Config.MAX_COMMENTS,
        help=f'翻訳する最大コメント数 (デフォルト: {Config.MAX_COMMENTS})'
    )
    
    # 出力オプション
    parser.add_argument(
        '--output-formats',
        nargs='+',
        choices=['json', 'csv', 'markdown'],
        default=['json', 'csv', 'markdown'],
        help='出力形式 (デフォルト: すべて)'
    )
    parser.add_argument(
        '--separate-files',
        action='store_true',
        help='issueごとに個別のファイルに保存する'
    )
    parser.add_argument(
        '--include-original',
        action='store_true',
        help='元の英語テキストを翻訳結果に含める'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='出力ディレクトリ（指定しない場合は自動生成）'
    )
    
    args = parser.parse_args()
    
    try:
        # 設定の検証
        print("設定を検証中...")
        Config.validate()
        print(f"AIプロバイダー: {Config.get_ai_provider()}")
        
        # issueの読み込み
        print(f"\nIssueデータを読み込み中: {args.input}")
        issues = load_issues_json(args.input)
        print(f"{len(issues)}件のissueを読み込みました。")
        
        # 翻訳
        print("\n翻訳を開始します...")
        print(f"翻訳スタイル: {args.translation_style}")
        translator = Translator(translation_style=args.translation_style)
        translated_issues = translator.translate_issues(
            issues,
            translate_comments=args.translate_comments,
            max_comments=args.max_comments
        )
        
        # 出力ディレクトリの決定
        if args.output_dir:
            output_base_dir = args.output_dir
        else:
            # 入力ファイルのパスから情報を抽出
            # 例: output/spring-batch/6.0.0/closed/issues_20251229-223743.json
            #  -> output/6.0.0/closed/free/20251229-223743
            input_path_parts = args.input.replace('\\', '/').split('/')
            
            # milestone, state を抽出
            try:
                repo_dirname = Config.get_repo_dirname()
                repo_idx = input_path_parts.index(repo_dirname)
                milestone_name = input_path_parts[repo_idx + 1]
                state_name = input_path_parts[repo_idx + 2]
                filename = os.path.basename(args.input)
                # issues_20251229-223743.json -> 20251229-223743
                datetime_str = filename.replace('issues_', '').replace('.json', '')
            except (ValueError, IndexError):
                # 抽出できない場合は現在時刻を使用
                milestone_name = "unknown"
                state_name = "unknown"
                datetime_str = datetime.now().strftime('%Y%m%d-%H%M%S')
            
            output_base_dir = os.path.join(
                Config.OUTPUT_DIR,
                milestone_name,
                state_name,
                args.translation_style,
                datetime_str
            )
        
        os.makedirs(output_base_dir, exist_ok=True)
        base_filename = "translations"
        
        print("\n結果を保存中...")
        print(f"出力先: {output_base_dir}")
        
        if 'json' in args.output_formats:
            save_json(
                translated_issues,
                os.path.join(output_base_dir, f"{base_filename}.json")
            )
        
        if 'csv' in args.output_formats:
            save_csv(
                translated_issues,
                os.path.join(output_base_dir, f"{base_filename}.csv")
            )
        
        if 'markdown' in args.output_formats:
            save_markdown(
                translated_issues,
                os.path.join(output_base_dir, f"{base_filename}.md"),
                separate_files=args.separate_files,
                include_original=args.include_original
            )
        
        print("\n✅ 処理が完了しました！")
        print(f"翻訳件数: {len(translated_issues)}件")
        print(f"出力先: {output_base_dir}/")
        
    except KeyboardInterrupt:
        print("\n\n処理を中断しました。")
    except FileNotFoundError:
        print(f"\n❌ エラー: 入力ファイルが見つかりません: {args.input}")
        return 1
    except json.JSONDecodeError:
        print(f"\n❌ エラー: 入力ファイルのJSON形式が不正です: {args.input}")
        return 1
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
