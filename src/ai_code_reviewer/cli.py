import argparse
import os
from .pr_reviewer import PRReviewer
from .bitbucket_pr_reviewer import BitbucketPRReviewer

def main():
    parser = argparse.ArgumentParser(description='AI Code Reviewer CLI')
    parser.add_argument('--pr', type=int, help='Pull request number to review')
    parser.add_argument('--platform', type=str, choices=['github', 'bitbucket'], default='github',
                      help='Platform to use for PR review (github or bitbucket)')
    
    # GitHub specific arguments
    parser.add_argument('--owner', type=str, help='Repository owner/organization name (GitHub)')
    parser.add_argument('--repo', type=str, help='Repository name (GitHub)')
    parser.add_argument('--token', type=str, help='GitHub personal access token')
    
    # Bitbucket specific arguments
    parser.add_argument('--workspace', type=str, help='Bitbucket workspace/team name')
    parser.add_argument('--repo-slug', type=str, help='Bitbucket repository slug')
    parser.add_argument('--username', type=str, help='Bitbucket username')
    parser.add_argument('--app-password', type=str, help='Bitbucket app password')
    
    parser.add_argument('--post-comment', action='store_true', help='Post review as a comment on the PR')
    
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
            
            reviewer = BitbucketPRReviewer(username, app_password, workspace, repo_slug)
        
        # Review the specified PR
        review_results = reviewer.review_pr(args.pr)
        
        # Print review results
        print("\n=== PR Review Results ===")
        print(f"PR Title: {review_results['pr_title']}")
        print(f"PR Description: {review_results['pr_description']}")
        print("\nOverall Assessment:")
        print(review_results['overall_assessment'])
        
        # Post comment if requested
        if args.post_comment:
            reviewer.post_review_comment(args.pr, review_results)
            print("\nReview comment posted to PR")
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 