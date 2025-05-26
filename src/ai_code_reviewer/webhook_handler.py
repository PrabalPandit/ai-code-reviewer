import os
import json
import hmac
import hashlib
from typing import Dict, Optional
from flask import Flask, request, jsonify
from .pr_reviewer import PRReviewer
from .bitbucket_pr_reviewer import BitbucketPRReviewer

app = Flask(__name__)

def verify_github_signature(payload_body: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature or not secret:
        return False
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hashlib.sha1
    ).hexdigest()
    return hmac.compare_digest(f"sha1={expected_signature}", signature)

def verify_bitbucket_signature(payload_body: bytes, signature: str, secret: str) -> bool:
    """Verify Bitbucket webhook signature."""
    if not signature or not secret:
        return False
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

def get_github_reviewer() -> PRReviewer:
    """Initialize GitHub PR reviewer."""
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_REPOSITORY_OWNER')
    repo = os.getenv('GITHUB_REPOSITORY_NAME')
    
    if not all([token, owner, repo]):
        raise ValueError("Missing GitHub credentials")
    
    return PRReviewer(token, owner, repo)

def get_bitbucket_reviewer() -> BitbucketPRReviewer:
    """Initialize Bitbucket PR reviewer."""
    username = os.getenv('BITBUCKET_USERNAME')
    app_password = os.getenv('BITBUCKET_APP_PASSWORD')
    workspace = os.getenv('BITBUCKET_WORKSPACE')
    repo_slug = os.getenv('BITBUCKET_REPO_SLUG')
    
    if not all([username, app_password, workspace, repo_slug]):
        raise ValueError("Missing Bitbucket credentials")
    
    return BitbucketPRReviewer(username, app_password, workspace, repo_slug)

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events."""
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature')
    if not verify_github_signature(
        request.get_data(),
        signature,
        os.getenv('GITHUB_WEBHOOK_SECRET', '')
    ):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process the event
    event_type = request.headers.get('X-GitHub-Event')
    if event_type != 'pull_request':
        return jsonify({'message': 'Ignoring non-PR event'}), 200
    
    payload = request.json
    action = payload.get('action')
    
    # Only process opened and synchronize events
    if action not in ['opened', 'synchronize']:
        return jsonify({'message': f'Ignoring {action} action'}), 200
    
    try:
        reviewer = get_github_reviewer()
        pr_number = payload['pull_request']['number']
        
        # Review the PR
        review_results = reviewer.review_pr(pr_number)
        
        # Post the review as a comment
        reviewer.post_review_comment(pr_number, review_results)
        
        return jsonify({'message': 'PR review completed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/bitbucket', methods=['POST'])
def bitbucket_webhook():
    """Handle Bitbucket webhook events."""
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature')
    if not verify_bitbucket_signature(
        request.get_data(),
        signature,
        os.getenv('BITBUCKET_WEBHOOK_SECRET', '')
    ):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process the event
    event_type = request.headers.get('X-Event-Key')
    if event_type != 'pullrequest:created' and event_type != 'pullrequest:updated':
        return jsonify({'message': 'Ignoring non-PR event'}), 200
    
    payload = request.json
    pr_number = payload['pullrequest']['id']
    
    try:
        reviewer = get_bitbucket_reviewer()
        
        # Review the PR
        review_results = reviewer.review_pr(pr_number)
        
        # Post the review as a comment
        reviewer.post_review_comment(pr_number, review_results)
        
        return jsonify({'message': 'PR review completed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def start_server(host: str = '0.0.0.0', port: int = 5000):
    """Start the webhook server."""
    app.run(host=host, port=port) 