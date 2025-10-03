# Changelog

All notable changes to Bangler will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-03

### Added
- **Configurable base price per transaction** - Sales team can now customize base price for individual transactions ([src/bangler/cli/prompts.py:159-215](src/bangler/cli/prompts.py#L159-L215))
  - New Step 7 in customer specification workflow after thickness selection
  - Questionary Y/N prompt with "No" as default for fast-path workflow
  - Decimal input validation: must be >$0, automatically rounds to 2 decimal places
  - Deviation warning system: alerts if custom price differs from default by ±$200 (configurable threshold)
  - Back navigation support from base price prompt to thickness selection
  - Delta display showing difference in both dollar amount and percentage

- **Base price warning threshold configuration** - New `base_price_warning_threshold` setting in `PRICING` config ([src/bangler/config/settings.py:20](src/bangler/config/settings.py#L20))
  - Default threshold: $200.00
  - Triggers confirmation prompt when custom base price deviates significantly from default
  - Prevents accidental pricing errors while allowing intentional customization

- **Enhanced pricing breakdown display** - Base price now shows delta information when customized ([src/bangler/models/pricing.py:26-32](src/bangler/models/pricing.py#L26-L32))
  - Format: `Base Price: $550.00 (+$75.00 / +15.8% more than default)`
  - Automatically calculates and displays percentage difference
  - Shows clear indication when default base price is used

- **Specification summary enhancement** - Customer specification now includes custom base price details ([src/bangler/cli/display.py:86-103](src/bangler/cli/display.py#L86-L103))
  - Displays custom base price with delta before calculation begins
  - Consistent formatting with pricing breakdown display
  - Only shows when custom price differs from default

### Changed
- **Pricing engine updated** - Both `calculate_bangle_price()` and `calculate_bangle_price_with_progress()` methods now accept optional `custom_base_price` parameter ([src/bangler/core/pricing_engine.py:27-144](src/bangler/core/pricing_engine.py#L27-L144))
  - Uses custom base price if provided, otherwise defaults to configured base price
  - Calculates and stores delta information for display purposes
  - Maintains backward compatibility with existing code

- **CLI interface workflow** - Updated to handle custom base price throughout the flow ([src/bangler/cli/interface.py:52-108](src/bangler/cli/interface.py#L52-L108))
  - `_collect_specification()` now returns tuple: `(BangleSpec, Optional[Decimal])`
  - `run()` method unpacks and passes custom base price to pricing engine
  - `_calculate_and_display_pricing()` accepts custom base price parameter

- **BanglePrice model enhanced** - Added fields to track custom base price delta ([src/bangler/models/pricing.py:20-21](src/bangler/models/pricing.py#L20-L21))
  - New `base_price_delta` field stores dollar difference from default
  - New `base_price_delta_percent` field stores percentage difference
  - `get_breakdown_display()` method updated to format delta display

### Technical Details
- Input validation: Custom base price must be positive decimal, rounded to 2 decimal places
- Error handling: Invalid inputs trigger clear error messages and re-prompt for correct input
- Confirmation workflow: Significant deviations (>±threshold) require explicit user confirmation
- Display consistency: Delta format matches across specification summary and pricing breakdown
- Fast-path optimization: Default "No" selection allows quick Enter keypress for standard pricing

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
