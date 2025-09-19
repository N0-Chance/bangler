# Tech Stack and Dependencies

## Language and Runtime
- **Python**: ^3.10 (minimum version)

## Dependencies
### Production Dependencies
- **requests**: ^2.31.0 (for Stuller API calls)

### Development Dependencies
- **pytest**: ^7.4.0 (testing framework)
- **black**: ^23.0.0 (code formatting)
- **isort**: ^5.12.0 (import sorting)

## Package Management
- **Poetry**: Used for dependency management and virtual environment
- **pyproject.toml**: Configuration file defining dependencies and project metadata

## API Integration
- **Target API**: Stuller API v2 products endpoint
- **Product Type**: "Sizing Stock" (not "blanks")
- **Method**: Specific SKU lookup rather than filtered search
- **Authentication**: Already established through S2S2 project experience

## Project Structure
```
bangler/
├── .venv/           # Poetry virtual environment
├── .claude/         # Claude Code configuration
├── .serena/         # Serena MCP configuration
├── bangle_size.txt  # Size to MM mapping data
├── CLAUDE.md        # Project instructions for Claude
├── pyproject.toml   # Poetry configuration
├── poetry.lock      # Locked dependencies
└── bangle_pricing_project_doc.md  # Detailed project docs
```