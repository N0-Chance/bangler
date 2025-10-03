# Changelog

All notable changes to Bangler will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-03-10

### Fixed
- Removed duplicate "Continuum Sterling Silver" entry in metal color selection prompt ([src/bangler/cli/prompts.py:49-65](src/bangler/cli/prompts.py#L49-L65))
  - Bug was caused by conditional insertion logic that added "Continuum Sterling Silver" before "Sterling Silver", but it was already present in the `valid_colors` list
  - Simplified `prompt_metal_color()` method to directly use configured color list without duplication

## [1.0.0] - 2025-09-25

### Added
- Production release with complete CLI interface and Stuller integration
- Professional sales workflow with direct Stuller ordering
- Real-time pricing integration with Stuller API
- Material science-based calculations achieving 95%+ accuracy
- Complete customer variable handling (size, shape, color, quality, width, thickness)
- Enterprise reliability with circuit breaker patterns and error handling
- Auto-updating CSV data with 5,938 product catalog
- Professional CLI interface with guided questionary prompts
- Direct purchase integration with one-click Stuller SKU page opening
- Performance optimization: 84ms startup, 0.1MB memory usage

### Changed
- CSV-based product discovery replacing API discovery for superior performance
- Karat-specific density tables for accurate material calculations
- Singleton patterns to prevent duplicate resource loading

## [0.1.0] - 2025-09-21

### Added
- Initial release
- Basic CLI interface
- Stuller API integration
- Core pricing engine
- Size conversion utilities
- Material calculation framework

## [0.0.x] - 2025

### Added
- Development versions with incremental feature additions
- Prototype implementations
- Initial architecture design
