# Task Completion Checklist

When completing development tasks in this project, follow these steps:

## Code Quality Checks
1. **Format code**: `poetry run black .`
2. **Sort imports**: `poetry run isort .`
3. **Check formatting**: `poetry run black --check .`
4. **Check import order**: `poetry run isort --check-only .`

## Testing
1. **Run all tests**: `poetry run pytest`
2. **Run with verbose output**: `poetry run pytest -v`
3. **Ensure all tests pass** before considering task complete

## Pre-commit Validation
Run the combined workflow to ensure code quality:
```bash
poetry run black . && poetry run isort . && poetry run pytest
```

## Documentation
- Update relevant documentation if functionality changes
- Ensure API integration changes are reflected in project docs
- Update CLAUDE.md if development patterns change

## Notes
- **No linting tool configured yet** (consider adding flake8 or pylint)
- **No type checking configured** (consider adding mypy)
- **No pre-commit hooks** (consider adding pre-commit framework)
- Project currently has no source code - these steps apply once development begins

## Future Considerations
As the project grows, consider adding:
- Type checking with mypy
- Linting with flake8 or pylint
- Pre-commit hooks for automated quality checks
- CI/CD pipeline configuration