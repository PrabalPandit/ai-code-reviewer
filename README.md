# AI Code Reviewer

An intelligent code review tool that uses Google's Gemini AI to analyze Java code and provide detailed reviews based on predefined guidelines.

## Features

- Review individual Java files or entire projects
- Comprehensive code analysis based on best practices
- Detailed review reports in Markdown format
- Configurable review guidelines
- Support for both single file and project-wide reviews

## Prerequisites

- Java 11 or higher
- Maven
- Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer
```

2. Configure the application:
   - Copy `src/main/resources/application.properties.template` to `src/main/resources/application.properties`
   - Replace `YOUR_API_KEY_HERE` with your Gemini API key:
   ```properties
   gemini.api.key=your-actual-api-key-here
   ```

3. Build the project:
```bash
mvn clean package
```

## Usage

### Review a Single File

```bash
java -jar target/ai-code-reviewer-1.0-SNAPSHOT-jar-with-dependencies.jar <source-file> <output-file>
```

Example:
```bash
java -jar target/ai-code-reviewer-1.0-SNAPSHOT-jar-with-dependencies.jar src/main/java/com/example/MyClass.java review-output.md
```

### Review an Entire Project

```bash
java -jar target/ai-code-reviewer-1.0-SNAPSHOT-jar-with-dependencies.jar --project <project-path> <output-dir>
```

Example:
```bash
java -jar target/ai-code-reviewer-1.0-SNAPSHOT-jar-with-dependencies.jar --project /path/to/your/project reviews/
```

## Review Guidelines

The tool uses guidelines defined in `src/main/resources/guidelines.md`. These guidelines cover:

- Code Style
- Documentation
- Code Quality
- Security
- Testing
- Performance
- Best Practices
- Class Layering and Structure

You can customize these guidelines by modifying the `guidelines.md` file.

## Output

The tool generates detailed review reports in Markdown format, including:

1. Violations of guidelines
2. Suggested improvements
3. Security issues
4. Performance concerns
5. Specific recommendations

## Configuration

The application can be configured through `src/main/resources/application.properties`:

```properties
# API Configuration
gemini.api.key=your-api-key
gemini.api.url=https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent

# File Paths
guidelines.path=src/main/resources/guidelines.md

# Logging
logging.file.path=logs/code-reviewer.log
```

## Security Notes

- Never commit your API key to version control
- Keep the `application.properties` file secure
- Consider using environment variables or a secure vault for production environments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 