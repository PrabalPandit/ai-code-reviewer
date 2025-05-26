# AI Code Reviewer

An AI-powered code review tool that uses Google's Gemini AI to analyze and review code files and projects.

## Features

- Review individual files or entire projects
- Maintains project package structure in reviews
- Comprehensive API review guidelines
- Line-by-line code analysis
- Detailed recommendations and improvements
- Security and performance analysis
- Support for multiple programming languages
- Configurable AI model parameters

## Prerequisites

- Python 3.7 or higher
- A Gemini API key
- Git (for cloning the repository)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-code-reviewer.git
cd ai-code-reviewer
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

4. Create a `.env` file in the project root with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
MAX_RETRIES=3
RETRY_DELAY=2
```

## Environment Variables

The following environment variables can be configured in your `.env` file:

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `MAX_RETRIES`: Maximum number of retry attempts for API calls (default: 3)
- `RETRY_DELAY`: Delay between retries in seconds (default: 2)
- `MODEL_NAME`: Gemini model to use (default: models/gemini-2.5-flash-preview-04-17)
- `TEMPERATURE`: AI model temperature (default: 0.7)
- `MAX_TOKENS`: Maximum tokens for response (default: 2048)

## Usage

The tool can be used in two modes: file review and project review.

### Review a Single File

```bash
ai-code-reviewer /path/to/file reviews/ --mode file --guidelines guidelines.md
```

Example:
```bash
ai-code-reviewer src/main/java/com/example/MyClass.java reviews/ --mode file --guidelines guidelines.md
```

### Review a Project

```bash
ai-code-reviewer /path/to/project reviews/ --mode project --exclude venv --exclude .git --guidelines guidelines.md
```

Example:
```bash
ai-code-reviewer ~/projects/my-project reviews/ --mode project --exclude venv --exclude .git --exclude node_modules --guidelines guidelines.md
```

### Command Options

- `path`: Path to the file or project directory to review
- `output_dir`: Directory to save review reports
- `--mode` or `-m`: Review mode ('file' or 'project', default: 'project')
- `--exclude` or `-e`: Directories to exclude (only for project mode)
- `--guidelines` or `-g`: Path to review guidelines file
- `--max-retries` or `-r`: Maximum number of retry attempts (default: 3)
- `--retry-delay` or `-d`: Delay between retries in seconds (default: 2)

### Review Pull Requests

The tool can review Pull Requests from both GitHub and Bitbucket. Choose your platform below:

#### GitHub PR Review

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer Settings > Personal Access Tokens
   - Generate a new token with `repo` scope
   - Copy the token

2. Set up environment variables:
   ```bash
   export GITHUB_TOKEN='your-token-here'
   export GITHUB_REPOSITORY_OWNER='your-org-or-username'
   export GITHUB_REPOSITORY_NAME='your-repo-name'
   ```

3. Review a PR:
   ```bash
   python -m ai_code_reviewer.cli --pr 123 --platform github
   ```

4. Review and post comment:
   ```bash
   python -m ai_code_reviewer.cli --pr 123 --platform github --post-comment
   ```

#### Bitbucket PR Review

1. Create a Bitbucket App Password:
   - Go to Bitbucket Settings > App passwords
   - Create a new app password with `Pull requests: Read` and `Pull requests: Write` permissions
   - Copy the app password

2. Set up environment variables:
   ```bash
   export BITBUCKET_USERNAME='your-username'
   export BITBUCKET_APP_PASSWORD='your-app-password'
   export BITBUCKET_WORKSPACE='your-workspace'
   export BITBUCKET_REPO_SLUG='your-repo-slug'
   ```

3. Review a PR:
   ```bash
   python -m ai_code_reviewer.cli --pr 123 --platform bitbucket
   ```

4. Review and post comment:
   ```bash
   python -m ai_code_reviewer.cli --pr 123 --platform bitbucket --post-comment
   ```

#### Command Options

Common options:
- `--pr`: Pull request number to review
- `--platform`: Platform to use ('github' or 'bitbucket', default: 'github')
- `--post-comment`: Post review as a comment on the PR

GitHub specific options:
- `--owner`: Repository owner/organization name
- `--repo`: Repository name
- `--token`: GitHub personal access token

Bitbucket specific options:
- `--workspace`: Bitbucket workspace/team name
- `--repo-slug`: Bitbucket repository slug
- `--username`: Bitbucket username
- `--app-password`: Bitbucket app password

#### PR Review Output

The PR review includes:
1. **PR Details**
   - Title and description
   - Changed files
   - Overall assessment

2. **File Reviews**
   - Individual file analysis
   - Code quality assessment
   - Suggestions for improvement

3. **Summary**
   - Total files reviewed
   - Number of suggestions
   - Overall recommendations

4. **Platform Integration**
   - Optional automatic comment posting
   - Review results in PR discussion

### Automated PR Reviews with CI/CD

The tool can be integrated with CI/CD pipelines for automatic PR reviews. Here's how to set it up:

#### GitHub Actions Integration

1. The `.github/workflows/pr-review.yml` file is already configured to run on PR events.
2. No additional setup is required as GitHub Actions automatically provides the necessary environment variables.

#### Bitbucket Pipelines Integration

1. **Repository Setup**
   - Ensure your AI Code Reviewer is in a public repository
   - Add the following `bitbucket-pipelines.yml` to your repository:
   ```yaml
   image: python:3.9

   pipelines:
     pull-requests:
       '**':
         - step:
             name: AI Code Review
             script:
               - pip install git+https://github.com/yourusername/ai-code-reviewer.git
               - python -m ai_code_reviewer.cli --pr $BITBUCKET_PR_ID --platform bitbucket --post-comment
             caches:
               - pip
             env:
               BITBUCKET_USERNAME: $BITBUCKET_USERNAME
               BITBUCKET_APP_PASSWORD: $BITBUCKET_APP_PASSWORD
               BITBUCKET_WORKSPACE: $BITBUCKET_WORKSPACE
               BITBUCKET_REPO_SLUG: $BITBUCKET_REPO_SLUG

   definitions:
     caches:
       pip: ~/.cache/pip
   ```

2. **Required Environment Variables**
   Set these in your Bitbucket repository settings (Repository Settings > Repository Variables):
   - `BITBUCKET_USERNAME`: Your Bitbucket username
   - `BITBUCKET_APP_PASSWORD`: Bitbucket app password with PR read/write permissions
   - `BITBUCKET_WORKSPACE`: Your workspace/team name
   - `BITBUCKET_REPO_SLUG`: Your repository slug

3. **App Password Setup**
   - Go to Bitbucket Settings > App passwords
   - Create a new app password with these permissions:
     - Repositories: Read, Write
     - Pull requests: Read, Write

4. **Testing the Integration**
   - Create a new PR in your repository
   - The pipeline will automatically run and post a review comment
   - Check the Pipelines tab for execution status

## Supported File Types

The tool supports the following file types:
- Python (`.py`)
- Java (`.java`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- C++ (`.cpp`, `.h`, `.hpp`)
- C (`.c`, `.h`)

## Review Output

### File Review
For a single file review, the output will be saved as:
```
reviews/
└── filename_review.md
```

### Project Review
For a project review, the output will maintain the project structure:
```
reviews/
└── project_name/
    └── [package structure]/
        └── file_review.md
```

### Review Report Format

Each review report includes:
1. **Summary**
   - Overview of the code
   - Key findings
   - Overall assessment

2. **Detailed Analysis**
   - Code structure review
   - Best practices compliance
   - Potential issues
   - Line-by-line comments

3. **Recommendations**
   - Suggested improvements
   - Code optimization tips
   - Best practices to follow

4. **Security Considerations**
   - Security vulnerabilities
   - Best practices
   - Risk assessment

5. **Performance Notes**
   - Performance bottlenecks
   - Optimization opportunities
   - Resource usage analysis

## Review Guidelines

The tool uses comprehensive guidelines for code review, including:

### API Design and Structure
- RESTful principles and best practices
- API documentation requirements
- Versioning strategy

### Integration and Dependencies
- Service-to-service communication
- Message queue usage
- Database interactions
- DTO and model usage

### Security
- Authentication and authorization
- Input validation
- API security measures
- Rate limiting and CORS

### Performance
- Response time optimization
- Resource usage
- Caching strategy
- Query optimization

### Code Quality
- Clean code principles
- Error handling
- Testing requirements
- Documentation

## Security Considerations

### API Key Security
1. Never commit your `.env` file to version control
2. Use environment variables for sensitive data
3. Rotate your API keys regularly
4. Use the minimum required permissions for your API key

### Code Review Security
1. Be cautious when reviewing code containing sensitive information
2. Review outputs may contain code snippets and analysis
3. Consider using the tool in a private environment for sensitive code
4. Regularly clean up review outputs

### Best Practices
1. Keep dependencies updated
2. Use virtual environments
3. Review the code you're about to analyze
4. Be aware of rate limits and quotas
5. Monitor API usage

### Reporting Security Issues
If you discover a security vulnerability, please:
1. Do not create a public issue
2. Email security@yourdomain.com
3. Include detailed information about the vulnerability
4. We will respond within 48 hours

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Error: "Invalid API key"
   - Solution: Verify your API key in the `.env` file
   - Make sure the key is active and has sufficient quota

2. **Model Not Found**
   - Error: "Model not found"
   - Solution: Check the MODEL_NAME in your `.env` file
   - Ensure you're using a supported model version

3. **Rate Limiting**
   - Error: "Rate limit exceeded"
   - Solution: Increase RETRY_DELAY in `.env`
   - Consider upgrading your API quota

4. **File Access Issues**
   - Error: "Permission denied"
   - Solution: Check file permissions
   - Ensure you have read access to the files

5. **Memory Issues**
   - Error: "Out of memory"
   - Solution: Reduce MAX_TOKENS in `.env`
   - Review smaller files or projects

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
isort .
```

4. Type checking:
```bash
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details 