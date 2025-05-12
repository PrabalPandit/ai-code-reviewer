# Code Review Guidelines

## API Design and Structure

### API Design Patterns
- Follow RESTful principles and best practices
- Use appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Implement proper resource naming conventions
- Follow consistent URL structure
- Use appropriate status codes
- Implement proper error handling

### API Documentation
- Include comprehensive Swagger/OpenAPI annotations
- Document all endpoints, parameters, and responses
- Provide clear descriptions for each API
- Include example requests and responses
- Document error scenarios and status codes

### API Versioning
- Implement proper versioning strategy
- Use consistent versioning across all APIs
- Document version changes and deprecations
- Handle backward compatibility

## Integration and Dependencies

### Service Integration
- Review service-to-service communication
- Check proper use of message queues
- Analyze event handling patterns
- Review database interactions
- Check for proper use of DTOs and models

### Dependency Management
- Review external service dependencies
- Check for proper error handling in external calls
- Analyze timeout and retry strategies
- Review circuit breaker implementation
- Check for proper logging of external calls

## Security

### Authentication and Authorization
- Implement proper authentication mechanisms
- Use appropriate authorization checks
- Review role-based access control
- Check for proper session management
- Implement secure token handling

### Input Validation
- Validate all input parameters
- Implement proper sanitization
- Check for SQL injection prevention
- Review XSS protection
- Implement proper file upload validation

### API Security
- Implement rate limiting
- Configure proper CORS policies
- Use secure headers
- Implement request size limits
- Review API key management

## Performance

### Response Time
- Optimize database queries
- Implement proper caching
- Review N+1 query problems
- Optimize bulk operations
- Implement pagination for large datasets

### Resource Usage
- Monitor memory usage
- Review connection pooling
- Check for resource leaks
- Implement proper cleanup
- Review thread pool configuration

### Caching Strategy
- Implement appropriate caching
- Use cache invalidation
- Review cache consistency
- Implement proper cache headers
- Check for cache performance

## Code Quality

### Code Structure
- Follow clean code principles
- Implement proper separation of concerns
- Use appropriate design patterns
- Maintain consistent code style
- Follow SOLID principles

### Error Handling
- Implement proper exception handling
- Use appropriate error messages
- Log errors correctly
- Implement proper recovery mechanisms
- Handle edge cases

### Testing
- Include unit tests
- Implement integration tests
- Add performance tests
- Include security tests
- Document test scenarios

## Review Process

### Summary Section
- Provide a high-level overview
- List major findings
- Highlight critical issues
- Suggest improvements
- Note positive aspects

### Detailed Analysis
- Review code line by line
- Check for best practices
- Analyze potential issues
- Suggest optimizations
- Review documentation

### Recommendations
- Prioritize improvements
- Suggest specific changes
- Provide code examples
- Reference best practices
- Include security considerations

### Performance Notes
- Identify bottlenecks
- Suggest optimizations
- Review resource usage
- Check scalability
- Analyze response times

## API-Specific Checks

### REST API Best Practices
- Use proper HTTP methods
- Implement HATEOAS where appropriate
- Follow REST resource naming
- Use proper status codes
- Implement proper error responses

### API Documentation
- Check Swagger/OpenAPI annotations
- Review endpoint documentation
- Verify parameter documentation
- Check response documentation
- Review example documentation

### API Testing
- Verify endpoint functionality
- Check error handling
- Test edge cases
- Verify response formats
- Test security measures

### API Monitoring
- Implement proper logging
- Add performance metrics
- Monitor error rates
- Track response times
- Implement health checks

## Code Quality and Style
1. Follow language-specific style guides (PEP 8 for Python, Google Java Style for Java)
2. Use meaningful variable and function names
3. Keep functions small and focused on a single responsibility
4. Avoid code duplication (DRY principle)
5. Use appropriate design patterns where applicable
6. Maintain consistent formatting and indentation

## Documentation
1. Include clear and concise docstrings/comments
2. Document all public APIs and interfaces
3. Explain complex logic or business rules
4. Keep documentation up-to-date with code changes
5. Include examples for non-obvious usage

## Error Handling
1. Implement proper exception handling
2. Use appropriate error types
3. Include meaningful error messages
4. Handle edge cases and invalid inputs
5. Log errors appropriately

## Testing
1. Write unit tests for new functionality
2. Maintain good test coverage
3. Include edge cases in tests
4. Use meaningful test names
5. Follow the Arrange-Act-Assert pattern

## Security
1. Validate all user inputs
2. Use parameterized queries for database operations
3. Implement proper authentication and authorization
4. Follow the principle of least privilege
5. Avoid exposing sensitive information
6. Use secure communication protocols
7. Implement proper password handling

## Performance
1. Optimize database queries
2. Use appropriate data structures
3. Implement caching where beneficial
4. Consider memory usage
5. Profile and optimize bottlenecks
6. Use async/parallel processing where appropriate

## Architecture
1. Follow SOLID principles
2. Maintain proper separation of concerns
3. Use appropriate design patterns
4. Keep components loosely coupled
5. Consider scalability and maintainability
6. Follow the single responsibility principle

## Best Practices
1. Use version control effectively
2. Write clean, maintainable code
3. Consider code reusability
4. Follow the YAGNI principle
5. Keep dependencies up-to-date
6. Use appropriate logging levels
7. Implement proper monitoring

## Review Process
1. Check for potential bugs
2. Verify error handling
3. Review security implications
4. Assess performance impact
5. Consider maintainability
6. Look for code smells
7. Suggest improvements

## Output Format
Please format your review as follows:

### Summary
[Brief overview of the code and main findings]

### Detailed Analysis
[Break down findings by category]

### Recommendations
[Specific suggestions for improvement]

### Security Considerations
[Any security-related findings]

### Performance Notes
[Performance-related observations] 