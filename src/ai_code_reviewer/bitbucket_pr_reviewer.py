import os
import base64
import requests
import logging
import re
from typing import Dict, List, Optional
from .code_reviewer import CodeReviewer
from .gemini_client import GeminiAIClient
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")

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
        # Initialize GeminiAIClient with default retry settings
        self.code_reviewer = CodeReviewer(client=GeminiAIClient(max_retries=3, retry_delay=2))
        
        # Load guidelines
        guidelines_path = os.getenv('REVIEW_GUIDELINES_PATH', 'guidelines.md')
        self.guidelines = self.code_reviewer.load_guidelines(guidelines_path)
        if self.guidelines:
            logger.info(f"Loaded review guidelines from {guidelines_path}")
        else:
            logger.warning(f"No guidelines found at {guidelines_path}, using default review criteria")

    def get_pr_details(self, pr_number: int) -> Dict:
        """
        Fetch PR details from Bitbucket API.
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            Dict: PR details including title, description, and changed files
        """
        logger.info(f"Fetching PR details for PR #{pr_number}")
        url = f"{self.base_url}/pullrequests/{pr_number}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        pr_details = response.json()
        logger.info(f"Successfully fetched PR details: {pr_details['title']}")
        return pr_details

    def get_pr_files(self, pr_number: int) -> List[Dict]:
        """
        Fetch files changed in the PR.
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            List[Dict]: List of changed files with their details
        """
        logger.info(f"Fetching changed files for PR #{pr_number}")
        url = f"{self.base_url}/pullrequests/{pr_number}/diffstat"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        files = response.json()["values"]
        
        # Transform the response to match our expected format
        transformed_files = []
        for file in files:
            file_path = file['new']['path'] if file['new'] else file['old']['path']
            transformed_files.append({
                'path': file_path,
                'status': file['status']
            })
            logger.info(f"Found changed file: {file_path} (status: {file['status']})")
        return transformed_files

    def get_file_content(self, file_path: str, commit_hash: str) -> str:
        """
        Fetch content of a specific file at a given commit.
        
        Args:
            file_path (str): Path to the file
            commit_hash (str): Commit hash
            
        Returns:
            str: File content
        """
        logger.info(f"Fetching content for file: {file_path} at commit {commit_hash}")
        url = f"{self.base_url}/src/{commit_hash}/{file_path}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        
        # Handle both raw and base64 encoded content
        content_type = response.headers.get('content-type', '')
        if 'text' in content_type:
            content = response.text
            logger.info(f"Successfully fetched text content for {file_path}")
            return content
        else:
            logger.warning(f"Binary file detected: {file_path}")
            return f"[Binary file: {file_path}]"

    def get_file_diff(self, pr_number: int, file_path: str) -> str:
        """
        Get the raw diff for a specific file in the PR.
        
        Args:
            pr_number (int): Pull request number
            file_path (str): Path to the file
            
        Returns:
            str: Raw diff content
        """
        # First get the diffstat to find the file
        diffstat_url = f"{self.base_url}/pullrequests/{pr_number}/diffstat"
        try:
            diffstat_response = requests.get(diffstat_url, auth=self.auth, headers=self.headers)
            diffstat_response.raise_for_status()
            diffstat = diffstat_response.json()
            
            # Find the file in the diffstat
            for diff in diffstat["values"]:
                if diff["new"]["path"] == file_path:
                    # Get the patch content
                    patch_url = f"{self.base_url}/pullrequests/{pr_number}/patch"
                    headers = self.headers.copy()
                    headers["Accept"] = "text/plain"
                    
                    patch_response = requests.get(patch_url, auth=self.auth, headers=headers)
                    patch_response.raise_for_status()
                    patch_content = patch_response.text
                    
                    # Extract the diff for this specific file
                    file_diff = self._extract_file_diff(patch_content, file_path)
                    if file_diff:
                        return file_diff
                    else:
                        logger.warning(f"Could not find diff for {file_path} in patch content")
                        return ""
            
            logger.warning(f"File {file_path} not found in diffstat")
            return ""
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to get diff for {file_path}: {str(e)}")
            logger.error(f"URL: {diffstat_url}")
            logger.error(f"Response content: {e.response.content}")
            raise

    def _extract_file_diff(self, patch_content: str, file_path: str) -> str:
        """
        Extract the diff for a specific file from the patch content.
        
        Args:
            patch_content (str): The full patch content
            file_path (str): The file path to extract
            
        Returns:
            str: The diff content for the specific file
        """
        # Split the patch into file sections
        sections = patch_content.split('diff --git')
        for section in sections:
            if file_path in section:
                # Found the section for our file
                # Add back the 'diff --git' prefix that was removed by split
                return 'diff --git' + section
        
        return ""

    def get_changed_lines(self, diff_content: str) -> List[Dict]:
        """
        Parse the diff content to get changed lines with their context from the diff.
        
        Args:
            diff_content (str): Raw diff content
            
        Returns:
            List[Dict]: List of changed lines with their context from the diff
        """
        if not diff_content:
            return []
            
        changed_lines = []
        current_chunk = []
        current_line = 0
        
        for line in diff_content.split('\n'):
            if line.startswith('@@'):
                # If we have a chunk, process it
                if current_chunk:
                    changed_lines.extend(self._process_chunk(current_chunk))
                current_chunk = []
                # Parse the line numbers from the diff header
                match = re.search(r'@@ -\d+,?\d* \+(\d+),?\d* @@', line)
                if match:
                    current_line = int(match.group(1))
            else:
                current_chunk.append(line)
        
        # Process the last chunk
        if current_chunk:
            changed_lines.extend(self._process_chunk(current_chunk))
        
        return changed_lines

    def _process_chunk(self, chunk: List[str]) -> List[Dict]:
        """
        Process a chunk of diff lines to extract changed lines and their context.
        
        Args:
            chunk (List[str]): List of lines from a diff chunk
            
        Returns:
            List[Dict]: List of changed lines with their context
        """
        changed_lines = []
        context_lines = []
        current_line = 0
        
        for line in chunk:
            if line.startswith('@@'):
                # Skip the header line
                continue
            elif line.startswith('+') and not line.startswith('+++'):
                # This is an added line
                changed_lines.append({
                    'line_number': current_line,
                    'content': line[1:],  # Remove the '+' prefix
                    'type': 'addition',
                    'context': context_lines.copy()  # Copy the current context
                })
                current_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                # This is a deleted line
                changed_lines.append({
                    'line_number': current_line,
                    'content': line[1:],  # Remove the '-' prefix
                    'type': 'deletion',
                    'context': context_lines.copy()  # Copy the current context
                })
            elif not line.startswith(('---', '+++')):
                # This is a context line
                context_lines.append(line)
                if len(context_lines) > 3:  # Keep only last 3 context lines
                    context_lines.pop(0)
                current_line += 1
        
        return changed_lines

    def review_pr(self, pr_number: int) -> Dict:
        """
        Review a pull request and return the review results.
        
        Args:
            pr_number (int): Pull request number
            
        Returns:
            Dict: Review results including PR details and file reviews
        """
        logger.info(f"Starting review for PR #{pr_number}")
        
        # Get PR details
        pr_details = self.get_pr_details(pr_number)
        logger.info(f"PR Title: {pr_details['title']}")
        
        # Get changed files
        changed_files = self.get_pr_files(pr_number)
        logger.info(f"Found {len(changed_files)} changed files")
        
        # Review each file
        file_reviews = []
        for file in changed_files:
            if file['status'] != 'removed':  # Skip deleted files
                try:
                    logger.info(f"Reviewing file: {file['path']}")
                    file_content = self.get_file_content(file['path'], pr_details["source"]["commit"]["hash"])
                    file_review = self.code_reviewer.review_file(file['path'], content=file_content, guidelines=self.guidelines)
                    file_reviews.append({
                        'path': file['path'],
                        'review': file_review
                    })
                    logger.info(f"Successfully reviewed file: {file['path']}")
                except Exception as e:
                    logger.error(f"Error reviewing file {file['path']}: {str(e)}", exc_info=True)
                    continue
        
        # Generate overall assessment
        logger.info("Generating overall assessment")
        overall_assessment = self._generate_overall_assessment(file_reviews)
        
        result = {
            'pr_title': pr_details['title'],
            'pr_description': pr_details['description'],
            'changed_files': [f['path'] for f in changed_files],
            'file_reviews': file_reviews,
            'overall_assessment': overall_assessment
        }
        logger.info("PR review completed successfully")
        return result

    def _generate_overall_assessment(self, file_reviews: List[Dict]) -> str:
        """
        Generate an overall assessment of the PR based on individual file reviews.
        
        Args:
            file_reviews (List[Dict]): List of file reviews
            
        Returns:
            str: Overall assessment of the PR
        """
        logger.info("Generating overall assessment")
        total_files = len(file_reviews)
        
        assessment = f"PR Review Summary:\n"
        assessment += f"- Total files reviewed: {total_files}\n"
        
        if total_files == 0:
            assessment += "No files were reviewed."
        else:
            assessment += "\nFile Reviews:\n"
            for review in file_reviews:
                assessment += f"\n### {review['path']}\n"
                assessment += f"{review['review']}\n"
        
        return assessment

    def post_review_comment(self, pr_number: int, review_results: Dict) -> None:
        """
        Post the review results as comments in the PR.
        Summary goes to overview, detailed reviews go to Files Changed tab.
        
        Args:
            pr_number (int): Pull request number
            review_results (Dict): Results from the PR review
        """
        logger.info(f"Posting review comments for PR #{pr_number}")
        
        # First, post a summary comment in the overview
        summary_url = f"{self.base_url}/pullrequests/{pr_number}/comments"
        summary_payload = {
            "content": {
                "raw": review_results["overall_assessment"]
            }
        }
        
        try:
            response = requests.post(
                summary_url,
                auth=self.auth,
                headers=self.headers,
                json=summary_payload
            )
            response.raise_for_status()
            logger.info("Posted summary comment in overview")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to post summary comment: {str(e)}")
            logger.error(f"Response content: {e.response.content}")
        
        # Get PR details for the latest commit
        pr_details = self.get_pr_details(pr_number)
        commit_hash = pr_details["source"]["commit"]["hash"]
        
        # Then post file-specific comments in the Files Changed tab
        for file_review in review_results['file_reviews']:
            file_path = file_review['path']
            review_text = file_review['review']
            
            try:
                # Get the diff for this file
                diff_content = self.get_file_diff(pr_number, file_path)
                changed_lines = self.get_changed_lines(diff_content)
                
                if changed_lines:
                    # Post a comment for each added line only
                    for line in changed_lines:
                        if line['type'] == 'addition':  # Only comment on added lines
                            # Create a focused review for this specific change
                            change_context = "\n".join(line['context'])
                            change_review = ""
                            if change_context:
                                change_review += f"**Context**:\n```\n{change_context}\n```\n\n"
                            change_review += f"{review_text}"
                            
                            comment_url = f"{self.base_url}/pullrequests/{pr_number}/comments"
                            comment_payload = {
                                "content": {
                                    "raw": change_review
                                },
                                "inline": {
                                    "path": file_path,
                                    "from": line['line_number'],
                                    "to": line['line_number']
                                }
                            }
                            
                            try:
                                response = requests.post(
                                    comment_url,
                                    auth=self.auth,
                                    headers=self.headers,
                                    json=comment_payload
                                )
                                response.raise_for_status()
                                logger.info(f"Posted review comment for {file_path} at line {line['line_number']}")
                            except requests.exceptions.HTTPError as e:
                                logger.error(f"Failed to post comment for {file_path}: {str(e)}")
                                logger.error(f"Response content: {e.response.content}")
                                logger.error(f"Payload: {comment_payload}")
                else:
                    logger.warning(f"No changed lines found for {file_path}")
                    
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
                continue
        
        logger.info("Finished posting all comments") 