# Bangler Project - Master Implementation Plan

## Project Overview
Bangler is a Python system that calculates real-time pricing for custom bangles at Askew Jewelers by integrating with Stuller's API for live material costs. The system replaces manual and inconsistent pricing with systematic calculations based on current material costs.

## Business Context
- **Family Business**: Askew Jewelers specializes in handmade bangles
- **Current Problem**: Manual/inconsistent pricing methods
- **Product**: Simple shaped metal bangles (no gems), hand-pounded by craftsman
- **Goal**: Systematic pricing based on real-time Stuller material costs
- **Primary Users**: Jewelry salespeople, with future customer-facing capability

## Customer Variables (Core Inputs)
Based on project requirements and Stuller website analysis:

1. **Size**: 10-27 (maps to MM measurements via `bangle_size.txt`)
2. **Metal Shape**: Comfort Fit, Flat, Half Round, Low Dome, Square, Triangle
3. **Metal Quality**: 14K Yellow, 14K White, 18K Yellow, 18K White, etc.
4. **Width**: 1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 10mm
5. **Thickness**: 0.75mm, 1mm, 1.25mm, 1.5mm, 1.75mm (shape-dependent availability)

## Size Conversion Reference
From `bangle_size.txt` (inside-to-inside measurements in MM):
- Size 10 = 52.37mm
- Size 15 = 60.32mm
- Size 20 = 68.24mm
- Size 25 = 76.20mm
- Size 27 = 79.37mm
- (Complete mapping available in file)

## Three-Phase Development Plan

### Phase 1: Data Discovery & SKU Mapping
**Status**: Next Phase
**Goal**: Build tools to discover and cache all sizing stock products and their specifications

**Key Challenges**:
- Stuller SKUs have no predictable structure (e.g., "# SIZING STOCK:76483:P")
- Must discover relationships between shapes and available options programmatically
- Need to identify sizing stock products via API filters or SKU patterns

**Deliverables**:
- Complete inventory of sizing stock SKUs from Stuller API
- Shape-to-available-options mapping (which shapes support thickness, length options)
- Cached JSON database of all sizing stock specifications
- Validation of sizing stock identification methods

**Technical Components**:
- `bangler/src/bangler/core/discovery.py` - API discovery tools
- `bangler/src/bangler/data/sizing_stock_inventory.json` - Cached results
- `bangler/src/bangler/api/stuller_client.py` - Adapted from s2s2 patterns

### Phase 2: CLI Interface
**Status**: Planned
**Goal**: Build command-line tool for jewelry salespeople to price bangles

**User Experience Flow**:
1. Select Shape: [Flat, Comfort Fit, Low Dome, Half Round, Square, Triangle]
2. Select Quality: [14K Yellow, 14K White, 18K Yellow, 18K White, etc.]
3. Select Width: [1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 10mm] (filtered by shape)
4. Select Thickness: [0.75mm, 1mm, 1.25mm, 1.5mm, 1.75mm] (if applicable to shape)
5. Enter Customer Size: [10-27] (converted to MM via lookup table)
6. Display: Material needed, cost breakdown, final customer price

**Business Logic Requirements**:
- Size → MM circumference conversion using `bangle_size.txt`
- Circumference → length of sizing stock needed (math formula TBD)
- Round up to nearest inch (Stuller's selling unit)
- Real-time API call for current pricing (no caching due to live metal markets)
- Apply pricing formula: Material cost + configurable markup

### Phase 3: Web Interface
**Status**: Future
**Goal**: Web-based interface for customer-facing use
**Strategy**: Reuse Phase 2 business logic with modern web UI
**Features**: Customer interface + admin interface for pricing configuration

## Technical Architecture

### Project Structure
```
bangler/
├── src/bangler/
│   ├── core/           # Business logic, discovery tools, pricing engine
│   ├── api/            # Stuller API client (adapted from s2s2)
│   ├── data/           # Cached discovery results (JSON files)
│   ├── cli/            # Phase 2 command-line interface
│   ├── config/         # Pricing configuration management
│   ├── models/         # Data models (BangleSpec, BanglePrice, etc.)
│   └── utils/          # Size conversion, math utilities
├── docs/               # Documentation including this master plan
├── tests/              # Test suite
├── .env               # Stuller API credentials (already configured)
├── bangle_size.txt    # Size-to-MM conversion table
└── pyproject.toml     # Poetry dependencies
```

### Stuller API Integration Strategy

**Authentication**: HTTP Basic Auth using credentials from `.env`:
- Username: `AskewDev`
- Password: `732yruhdvjfl32asd847jndsjf121392jnSJHSIAuw718^@*c8bh@@jmasd`

**API Approach**:
- **Target Endpoint**: `POST /api/v2/products`
- **Product Type**: "Sizing Stock" products (not "blanks")
- **Method**: Specific SKU lookup rather than filtered search
- **Pattern**: Based on s2s2 project's proven StullerClient implementation

**Request Structure**:
```json
{
  "Include": ["All"],
  "Filter": ["Orderable", "OnPriceList"],
  "SKU": ["<calculated_sku>"]
}
```

**Key Technical Decisions**:
- Real-time API calls (no pricing cache due to live metal market fluctuations)
- Circuit breaker pattern for reliability (from s2s2)
- Comprehensive error handling with fallback messaging
- "Never assume anything" approach to Stuller API patterns

### Data Management Strategy

**Phase 1-2**: JSON files for cached discovery results
- Simple, file-based storage for SKU mappings
- No persistent database required initially
- Fast lookups for shape/option relationships

**Phase 3 Consideration**: PostgreSQL if needed for web interface scale

### Material Calculation Logic

**Current Understanding**:
1. Customer size (10-27) → MM circumference (via `bangle_size.txt` lookup)
2. Circumference + shape considerations → length of sizing stock needed
3. Round up to nearest inch (Stuller selling unit)
4. Quantity = 1 (one pipeline run = one bangle calculation)
5. SKU lookup with exact specifications
6. Apply pricing formula

**Math Requirements** (TBD):
- Formula for converting circular circumference to flat material length
- Factor in thickness considerations for certain shapes
- Account for standard material allowances

### Pricing Configuration

**Current Business Rules**:
- **Base Price**: $475 per bangle (flat rate, configurable)
- **Material Cost**: Real-time from Stuller API
- **Future Options**: Markup percentage, overhead calculations

**Configuration Structure**:
```python
# Example configuration
{
    "base_price": 475.00,          # Current flat rate
    "markup_percentage": None,      # Optional future feature
    "shop_overhead": None,          # Optional future feature
    "labor_rate": None             # Optional future feature
}
```

### Error Handling Strategy

**Philosophy**: Graceful degradation for jewelry salespeople
- Display clear error messages to users
- Log detailed errors for developer debugging
- Maintain fallback to manual pricing methods
- One log file per pipeline run for traceability

**Error Scenarios**:
- SKU not found in Stuller API
- No stock available for needed sizing stock
- API unavailable during customer consultation
- Invalid customer input combinations

## Implementation Experience & Patterns

### Leveraging s2s2 Project Experience
The bangler project builds on proven patterns from the s2s2 Stuller integration:

**Successful Patterns to Reuse**:
- `StullerClient` class with HTTP Basic Auth
- Circuit breaker implementation for API reliability
- Session management with proper headers
- Error handling and retry logic
- Response parsing and data extraction

**Key s2s2 Code References**:
- `/home/chance/Code/s2s2/src/s2s2/api/stuller.py` - Client implementation
- `/home/chance/Code/s2s2/src/s2s2/cli/fetch.py` - Integration patterns

### Sizing Stock Complexity
Based on Stuller website analysis, sizing stock has complex variable dependencies:
- Some shapes support thickness options, others don't
- Length options vary by shape (3in, 12in, Bulk, custom)
- Width availability may be shape-dependent
- No predictable SKU structure for programmatic building

**Discovery Requirements**:
- Must map all available combinations programmatically
- Cannot assume consistent SKU patterns
- Need to identify sizing stock via API exploration
- Cache results for performance but allow updates

## Dependencies & Technology Stack

**Current Setup** (from `pyproject.toml`):
- Python 3.10+
- Poetry for dependency management
- `requests` for HTTP API calls
- `python-dotenv` for environment variable management

**Additional Requirements**:
- No new major dependencies planned for Phase 1-2
- JSON for data storage (built-in)
- Standard library for CLI interface

## Future Considerations

### Scalability Planning
- **Phase 2**: CLI tool for validation and development
- **Phase 3**: Web interface as primary customer-facing tool
- **Architecture**: Modular design supporting both CLI and web frontends

### Business Growth
- **Current Focus**: Flat shape (90% of use cases)
- **Expansion Ready**: Square, Low Dome, and potential Triangle bangles
- **Pricing Flexibility**: Configurable rates for business changes

### Technical Evolution
- **Database Migration**: Easy path from JSON to PostgreSQL if needed
- **API Caching**: Real-time pricing requirement may evolve
- **Integration**: Potential for inventory management connections

## Decision Log

### Key Architectural Decisions
1. **Real-time API calls**: No pricing cache due to live metal market fluctuations
2. **JSON storage**: Simple file-based approach for Phase 1-2
3. **Modular structure**: CLI and web interface share business logic
4. **s2s2 patterns**: Proven Stuller integration approach
5. **Discovery-first**: Map all SKUs before building calculators
6. **Guided UX**: Step-by-step prompts rather than free-form input

### Business Rule Decisions
1. **Flat rate pricing**: $475 per bangle (configurable)
2. **Material rounding**: Round up to nearest inch (Stuller selling unit)
3. **Error handling**: Display to users, log for developers
4. **Real-time requirement**: Fresh pricing for each customer consultation

### Technical Choices
1. **Project structure**: `src/bangler/` layout for proper Python packaging
2. **No database**: JSON files sufficient for current requirements
3. **Circuit breaker**: Reliability pattern from s2s2 experience
4. **Environment config**: `.env` file for API credentials

## Next Steps (Phase 1 Implementation)
1. Create project structure with `src/bangler/` directories
2. Implement Stuller API client adapted from s2s2 patterns
3. Build discovery tools for sizing stock inventory
4. Create data models for BangleSpec and BanglePrice
5. Implement size conversion utilities using `bangle_size.txt`
6. Research and implement material calculation math

---

*This master plan provides complete context for future development and maintains all business requirements, technical decisions, and implementation details for the bangler project.*