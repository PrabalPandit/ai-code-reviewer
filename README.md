# AI Code Reviewer

An AI-powered code review tool that uses Google's Gemini AI to analyze and review code files and projects.

## Features

- Review individual files or entire projects
- Maintains project package structure in reviews
- Line-by-line code analysis
- Detailed recommendations and improvements
- Support for multiple programming languages
- Configurable AI model parameters
- Automated Pull request review support for GitHub and Bitbucket
- Automated PR review comments in the overview section
- Progress tracking with rich console output

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
ai-code-reviewer /path/to/file reviews/ --mode file
```

Example:
```bash
ai-code-reviewer src/main/java/com/example/MyClass.java reviews/ --mode file
```

### Review a Project

```bash
ai-code-reviewer /path/to/project reviews/ --mode project --exclude venv --exclude .git
```

Example:
```bash
ai-code-reviewer ~/projects/my-project reviews/ --mode project --exclude venv --exclude .git --exclude node_modules
```

### Command Options

- `path`: Path to the file or project directory to review
- `output_dir`: Directory to save review reports
- `--mode` or `-m`: Review mode ('file' or 'project', default: 'project')
- `--exclude` or `-e`: Directories to exclude (only for project mode)
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
- `--platform`: Platform to use ('github' or 'bitbucket', default: 'bitbucket')
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

### PR Review Output

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
   - Review results posted in PR overview section
   - No file-specific comments in Files Changed tab

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