import argparse
import os
from .pr_reviewer import PRReviewer
from .bitbucket_pr_reviewer import BitbucketPRReviewer

def main():
    parser = argparse.ArgumentParser(description='AI Code Reviewer CLI')
    parser.add_argument('--pr', type=int, help='Pull request number to review')
    parser.add_argument('--platform', choices=['github', 'bitbucket'], default='bitbucket', help='Platform to use (github or bitbucket)')
    parser.add_argument('--token', help='GitHub token (for GitHub platform)')
    parser.add_argument('--username', help='Bitbucket username (for Bitbucket platform)')
    parser.add_argument('--app-password', help='Bitbucket app password (for Bitbucket platform)')
    parser.add_argument('--workspace', help='Bitbucket workspace (for Bitbucket platform)')
    parser.add_argument('--repo-slug', help='Bitbucket repository slug (for Bitbucket platform)')
    parser.add_argument('--owner', help='GitHub repository owner (for GitHub platform)')
    parser.add_argument('--repo', help='GitHub repository name (for GitHub platform)')
    parser.add_argument('--post-comment', action='store_true', help='Post review as a comment on the PR')
    parser.add_argument('--guidelines', help='Path to review guidelines file')
    
    args = parser.parse_args()
    
    if args.pr:
        if args.platform == 'github':
            # GitHub PR review
            github_token = args.token or os.getenv('GITHUB_TOKEN')
            if not github_token:
                raise ValueError("GitHub token must be provided either via --token or GITHUB_TOKEN environment variable")
            
            repo_owner = args.owner or os.getenv('GITHUB_REPOSITORY_OWNER')
            repo_name = args.repo or os.getenv('GITHUB_REPOSITORY_NAME')
            
            if not repo_owner or not repo_name:
                raise ValueError("Repository owner and name must be provided either via --owner/--repo or environment variables")
            
            reviewer = PRReviewer(github_token, repo_owner, repo_name)
        else:
            # Bitbucket PR review
            username = args.username or os.getenv('BITBUCKET_USERNAME')
            app_password = args.app_password or os.getenv('BITBUCKET_APP_PASSWORD')
            workspace = args.workspace or os.getenv('BITBUCKET_WORKSPACE')
            repo_slug = args.repo_slug or os.getenv('BITBUCKET_REPO_SLUG')
            
            if not all([username, app_password, workspace, repo_slug]):
                raise ValueError("Bitbucket credentials and repository info must be provided either via arguments or environment variables")
            
            # Set guidelines path in environment if provided
            if args.guidelines:
                os.environ['REVIEW_GUIDELINES_PATH'] = args.guidelines
            
            reviewer = BitbucketPRReviewer(username, app_password, workspace, repo_slug)
        
        # Review the specified PR
        review_results = reviewer.review_pr(args.pr)
        
        # Print line-specific reviews
        print("\nLine-Specific Reviews:")
        for file_review in review_results.get('file_reviews', []):
            print(f"\nFile: {file_review['path']}")
            print(file_review['review'])
        
        
        # Post comment if requested
        if args.post_comment:
            reviewer.post_review_comment(args.pr, review_results)
            print("\nReview comment posted to PR")
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 