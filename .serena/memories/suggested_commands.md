# Suggested Development Commands

## Poetry Commands
- `poetry install` - Install all dependencies
- `poetry add <package>` - Add new dependency
- `poetry add --group dev <package>` - Add development dependency
- `poetry run python <script>` - Run Python script in virtual environment
- `poetry shell` - Activate virtual environment

## Development Tools
### Code Formatting
- `poetry run black .` - Format code with Black
- `poetry run black --check .` - Check code formatting without making changes

### Import Sorting
- `poetry run isort .` - Sort imports
- `poetry run isort --check-only .` - Check import sorting without making changes

### Testing
- `poetry run pytest` - Run all tests
- `poetry run pytest -v` - Run tests with verbose output
- `poetry run pytest <file>` - Run specific test file

## Combined Development Workflow
```bash
# Format and sort imports
poetry run black . && poetry run isort .

# Check code quality
poetry run black --check . && poetry run isort --check-only .

# Run tests
poetry run pytest
```

## System Commands
- `ls` - List files and directories
- `cd <directory>` - Change directory
- `grep <pattern> <file>` - Search for patterns in files
- `find <path> -name <pattern>` - Find files by name pattern
- `git status` - Check git repository status
- `git add .` - Stage all changes
- `git commit -m "<message>"` - Commit changes

## Notes
- Project uses Poetry for dependency management
- Virtual environment is automatically managed by Poetry
- No source code files exist yet - project in planning phase