# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose
Python system for real-time custom bangle pricing at Askew Jewelers. Integrates with Stuller's API for live material costs, replacing manual pricing with systematic calculations.

## Current Architecture
**Structure**: `src/bangler/` with modular components (api, core, models, utils, cli)
**Phases**: 1) Discovery tools → 2) CLI interface → 3) Web interface
**Key Files**: `docs/master_plan.md` (comprehensive plan), `bangle_size.txt` (size conversion), `.env` (Stuller credentials)

## Customer Variables (5 total)
- **Size**: 10-27 → MM via `bangle_size.txt` lookup
- **Metal Shape**: Flat, Comfort Fit, Low Dome, Half Round, Square, Triangle
- **Quality**: 14K/18K Yellow/White/Rose Gold, etc.
- **Width**: 1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 10mm
- **Thickness**: 0.75-1.75mm (shape-dependent availability)

## Stuller API Integration
- **Endpoint**: `POST /api/v2/products` with specific SKU lookup
- **Product Type**: "Sizing Stock" (complex variable dependencies)
- **Auth**: HTTP Basic Auth via `.env` credentials
- **Patterns**: Proven s2s2 client approach (`/home/chance/Code/s2s2/src/s2s2/api/stuller.py`)
- **SKU Challenge**: No predictable structure, requires discovery mapping

## Business Logic
1. Size → circumference → material length needed (math TBD)
2. Round to nearest inch (Stuller selling unit)
3. Real-time API call for current pricing (no cache - live metal markets)
4. Apply pricing: Material cost + $475 flat rate (configurable)

## Key Principles
- Real-time pricing (no stale cache)
- "Never assume anything" with Stuller API
- Modular design for CLI → web evolution
- Comprehensive error handling with fallback messaging

## Serena Workflow (Token-Efficient Code Analysis)
1. **Start with overview** - Use `get_symbols_overview` before reading files
2. **Navigate precisely** - Use `find_symbol` to target specific functions/classes
3. **Read selectively** - Only use `include_body=true` when you need implementation
4. **NEVER read entire files** unless absolutely necessary - use semantic tools first  