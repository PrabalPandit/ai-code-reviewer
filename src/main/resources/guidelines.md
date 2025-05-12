# Java Code Review Guidelines

## Project Structure
1. Follow standard Maven/Gradle project layout
2. Clear separation of source and test directories
3. Proper package structure following domain-driven design
4. Consistent naming conventions across the project
5. Clear module boundaries and dependencies

## Architecture
1. Adherence to defined layering structure
2. Proper separation of concerns
3. Clear dependency direction (no circular dependencies)
4. Appropriate use of design patterns
5. Scalable and maintainable architecture

## Code Style
1. Class names should be in PascalCase
2. Method and variable names should be in camelCase
3. Constants should be in UPPER_SNAKE_CASE
4. Maximum line length should be 120 characters
5. Use 4 spaces for indentation

## Documentation
1. All public classes and methods must have JavaDoc comments
2. Complex logic should have inline comments explaining the approach
3. TODO comments should include ticket numbers

## Code Quality
1. Methods should not exceed 50 lines
2. Classes should not exceed 500 lines
3. Cyclomatic complexity should not exceed 15
4. No duplicate code blocks
5. No commented-out code

## Security
1. No hardcoded credentials
2. Input validation for all user inputs
3. Proper exception handling
4. No sensitive data in logs
5. Use of secure encryption algorithms

## Testing
1. Unit tests required for all public methods
2. Test coverage should be at least 80%
3. Test names should be descriptive
4. Each test should test one specific scenario

## Performance
1. No infinite loops
2. Proper resource cleanup in finally blocks
3. Use of StringBuilder for string concatenation in loops
4. Efficient collection usage

## Best Practices
1. Use of final for immutable variables
2. Proper use of access modifiers
3. Interface-based programming
4. Dependency injection
5. SOLID principles adherence

## Class Layering and Structure

### Types of Classes
1. Configuration classes - For application setup/startup
2. Business Layer classes - For business logic and data flow (mostly stateless)
3. Model classes - For data carrying
4. Helper/Util classes - For static reusable functions

### Layering Structure
1. **Internal Layer**
   - Contains all business logic
   - Handles business validations
   - Performs data normalization
   - Manages database operations

2. **External Layer**
   - Wraps internal layer
   - Handles input validation
   - Manages request/response conversion
   - Communicates with internal layer

### Model Classes
1. **Form Classes**
   - Use Boxed Types only
   - Include validation annotations
   - Input to Controllers, passed to DTO
   - Never flow to Internal Layers
   - Fields should have single purpose

2. **Data Classes**
   - Use Boxed Types only
   - Created by DTO layer
   - Returned to controller layer
   - Fields filled unless database null

3. **Entity/Pojo Classes**
   - Use Boxed Types
   - Use Table generation for IDs
   - Use Integer for IDs (Long for high velocity)
   - Avoid JPA mapping annotations
   - Use @Column(nullable = false)
   - Use @Enumerated String value
   - Extend AbstractEntity
   - Maintain parent-child relationships

### Business Layer Classes
1. **Controller**
   - Expose endpoints
   - Define payloads
   - Use spinal case for paths
   - Use plural nouns
   - Follow RESTful conventions

2. **DTO**
   - Transform data formats
   - Perform structural validation
   - Route to appropriate APIs
   - Avoid @Transactional unless needed

3. **Flow (Optional)**
   - Handle complex business logic
   - Use @Transactional at class level

4. **API**
   - Contain entity business logic
   - Handle DAO communication
   - Use @Transactional at class level

5. **DAO**
   - Database communication
   - No business logic
   - No checked exceptions
   - Return only Pojo objects
   - Implement pagination
   - Use @Transactional at class level

### Helper/Util Classes
1. Provide abstraction for reusable functions
2. Use static methods
3. Require all data to be passed by calling function

## Project-Level Considerations

### Dependencies
1. Minimal and necessary external dependencies
2. Up-to-date dependency versions
3. No conflicting dependencies
4. Proper version management
5. Clear dependency documentation

### Build and Deployment
1. Clean and reproducible builds
2. Proper environment configuration
3. Clear deployment process
4. Version management
5. CI/CD pipeline integration

### Code Organization
1. Consistent package structure
2. Logical grouping of related classes
3. Clear module boundaries
4. Proper use of interfaces and abstractions
5. Reusable components

### Project Standards
1. Consistent coding style across the project
2. Standardized error handling
3. Uniform logging approach
4. Common utility classes
5. Shared constants and configurations

### Technical Debt
1. Identify and document technical debt
2. Plan for debt reduction
3. No accumulation of TODO items
4. Regular code cleanup
5. Performance optimization opportunities

### Integration Points
1. Clear API contracts
2. Well-documented external integrations
3. Proper error handling for external calls
4. Retry mechanisms where appropriate
5. Circuit breakers for critical services

### Monitoring and Maintenance
1. Proper logging strategy
2. Performance metrics
3. Error tracking
4. Health checks
5. Maintenance documentation 