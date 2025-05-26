import os
import base64
import requests
from typing import Dict, List, Optional
from .code_reviewer import CodeReviewer
from .gemini_client import GeminiAIClient

class BitbucketPRReviewer:
    def __init__(self, username: str, app_password: str, workspace: str, repo_slug: str):
        """
        Initialize the Bitbucket PR Reviewer with credentials and repository information.
        
        Args:
            username (str): Bitbucket username
            app_password (str): Bitbucket app password
            workspace (str): Bitbucket workspace/team name
            repo_slug (str): Repository slug
        """
        self.username = username
        self.app_password = app_password
        self.workspace = workspace
        self.repo_slug = repo_slug
        self.base_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"
        self.auth = (username, app_password)
        self.headers = {
            "Accept": "application/json"
        }
        self.code_reviewer = CodeReviewer(GeminiAIClient())

    def get_pr_details(self, pr_number: int) -> Dict:
        """
        Fetch PR details from Bitbucket API.
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            Dict: PR details including title, description, and changed files
        """
        url = f"{self.base_url}/pullrequests/{pr_number}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_pr_files(self, pr_number: int) -> List[Dict]:
        """
        Fetch files changed in the PR.
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            List[Dict]: List of changed files with their details
        """
        url = f"{self.base_url}/pullrequests/{pr_number}/diffstat"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()["values"]

    def get_file_content(self, file_path: str, commit_hash: str) -> str:
        """
        Fetch content of a specific file at a given commit.
        
        Args:
            file_path (str): Path to the file
            commit_hash (str): Commit hash
            
        Returns:
            str: File content
        """
        url = f"{self.base_url}/src/{commit_hash}/{file_path}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.text

    def review_pr(self, pr_number: int) -> Dict:
        """
        Review a pull request using AI code review capabilities.
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            Dict: Review results including comments and suggestions
        """
        pr_details = self.get_pr_details(pr_number)
        pr_files = self.get_pr_files(pr_number)
        
        review_results = {
            "pr_title": pr_details["title"],
            "pr_description": pr_details["description"],
            "files_reviewed": [],
            "overall_assessment": "",
            "suggestions": []
        }
        
        for file in pr_files:
            if file["status"] == "modified":
                file_content = self.get_file_content(file["new"]["path"], pr_details["source"]["commit"]["hash"])
                file_review = self.code_reviewer.review_code(file_content)
                
                review_results["files_reviewed"].append({
                    "filename": file["new"]["path"],
                    "review": file_review
                })
                
                if file_review.get("suggestions"):
                    review_results["suggestions"].extend(file_review["suggestions"])
        
        # Generate overall assessment
        review_results["overall_assessment"] = self._generate_overall_assessment(review_results)
        
        return review_results

    def _generate_overall_assessment(self, review_results: Dict) -> str:
        """
        Generate an overall assessment of the PR based on individual file reviews.
        
        Args:
            review_results (Dict): Results from reviewing individual files
            
        Returns:
            str: Overall assessment of the PR
        """
        total_files = len(review_results["files_reviewed"])
        total_suggestions = len(review_results["suggestions"])
        
        assessment = f"PR Review Summary:\n"
        assessment += f"- Total files reviewed: {total_files}\n"
        assessment += f"- Total suggestions: {total_suggestions}\n"
        
        if total_suggestions == 0:
            assessment += "No issues found. The code looks good!"
        else:
            assessment += "Please review the following suggestions:\n"
            for suggestion in review_results["suggestions"]:
                assessment += f"- {suggestion}\n"
        
        return assessment

    def post_review_comment(self, pr_number: int, review_results: Dict) -> None:
        """
        Post the review results as a comment on the PR.
        
        Args:
            pr_number (int): Pull request number
            review_results (Dict): Results from the PR review
        """
        url = f"{self.base_url}/pullrequests/{pr_number}/comments"
        comment_body = review_results["overall_assessment"]
        
        response = requests.post(
            url,
            auth=self.auth,
            headers=self.headers,
            json={"content": {"raw": comment_body}}
        )
        response.raise_for_status() 