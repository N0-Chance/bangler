# Code Style and Conventions

## Code Formatting
- **Black**: Automatic code formatting tool configured
- **Line length**: Black default (88 characters)
- **String quotes**: Black will standardize quote usage

## Import Organization
- **isort**: Configured for import sorting
- **Import order**: Standard Python convention (stdlib, third-party, local)

## Python Version
- **Minimum version**: Python 3.10
- **Type hints**: Use modern Python 3.10+ type hints
- **f-strings**: Preferred for string formatting

## Project Conventions
Since no source code exists yet, establish these conventions:

### Naming Conventions
- **Functions**: snake_case (e.g., `get_bangle_price`)
- **Variables**: snake_case (e.g., `metal_quality`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **Classes**: PascalCase (e.g., `BanglePricer`)

### Docstrings
- Use Google-style docstrings for consistency
- Document all public functions and classes
- Include parameter and return type documentation

### Error Handling
- Use specific exception types
- Log errors appropriately for API failures
- Provide meaningful error messages for user input validation

### API Integration Style
- Based on S2S2 project experience with Stuller API
- Use requests library with proper error handling
- Implement retry logic for API calls
- Structure API responses clearly

## Code Organization
When source code is created, follow this structure:
```
src/
├── main.py              # Main entry point
├── api/
│   ├── __init__.py
│   └── stuller.py       # Stuller API integration
├── models/
│   ├── __init__.py
│   └── bangle.py        # Bangle data models
└── utils/
    ├── __init__.py
    └── pricing.py       # Pricing calculations
```

## Dependencies
- Prefer established, well-maintained packages
- Pin versions in poetry.lock for reproducibility
- Keep dependencies minimal and purposeful