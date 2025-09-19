# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose
Python system for real-time custom bangle pricing at Askew Jewelers. Integrates with Stuller's API for live material costs, replacing manual pricing with systematic calculations.

## Current Architecture (Phase 1 Complete)
**Structure**: `src/bangler/` with modular components (api, core, models, utils, cli)
**Phases**: 1) ✅ CSV-based discovery complete → 2) 🔄 CLI interface → 3) Web interface
**Key Files**: `docs/master_plan.md` (comprehensive plan), `docs/bangle_size.txt` (size conversion), `.env` (Stuller credentials)
**Data**: `src/bangler/data/sizingstock-YYYYMMDD.csv` (5,938 products, auto-detection)

## Customer Variables (5 total)
- **Size**: 10-27 → MM via `bangle_size.txt` lookup
- **Metal Shape**: Flat, Comfort Fit, Low Dome, Half Round, Square, Triangle
- **Quality**: 14K/18K Yellow/White/Rose Gold, etc.
- **Width**: 1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 10mm
- **Thickness**: 0.75-1.75mm (shape-dependent availability)

## Stuller API Integration
- **Endpoint**: `POST /api/v2/products` with specific SKU lookup
- **Product Type**: "Sizing Stock" - now sourced from CSV export (5,938 products)
- **Auth**: HTTP Basic Auth via `.env` credentials
- **Client**: `StullerClient.get_sku_price(sku)` for real-time pricing only
- **Discovery**: Replaced API discovery with direct CSV export (much more efficient)

## Business Logic (Phase 2 Ready)
1. Customer variables → `SizingStockLookup.find_sku()` → SKU
2. Size → circumference → material length needed (math TBD)
3. Round to nearest inch (Stuller selling unit)
4. SKU → `StullerClient.get_sku_price()` → Real-time pricing (no cache - live metals)
5. Apply pricing: Material cost + $475 flat rate (configurable)

## Key Principles
- Real-time pricing (no stale cache)
- "Never assume anything" with Stuller API
- Modular design for CLI → web evolution
- Comprehensive error handling with fallback messaging

## Git Workflow & Commit Standards
**Follow this proven git cadence for clean development:**

### Commit Frequency
- **Frequent commits** for incremental progress (every major feature/fix)
- **Descriptive messages** explaining what was done and why
- **Always include** the Claude Code footer in commit messages

### Commit Message Format
```
Short descriptive title (50 chars max)

Optional longer description explaining:
- What was changed
- Why it was changed
- Any important technical details
- Performance impacts or benefits

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### When to Commit
1. **After completing a logical unit of work** (feature, fix, optimization)
2. **Before major refactoring** (create checkpoint)
3. **After performance improvements** (document metrics)
4. **When cleaning up code** (document what was removed/why)
5. **Before context loss** (compaction, restart, etc.)

### Git Best Practices
- Use `git add -A` to stage all changes (including deletions)
- Always push to `origin main` after committing
- Include performance metrics in commit messages when relevant
- Document file movements and major architecture changes
- Explain business value of technical changes

## Context Preservation & Hot-Start Docs
**Maintain comprehensive context for seamless development continuation:**

### Hot-Start Documentation
- **Create `docs/hs/hs_N.md`** before major context loss (compaction, restart) or on user request
- **Include**: Current status, completed work, performance metrics, next steps
- **Format**: Technical details + business context + immediate priorities
- **Commit**: Always commit hot-start docs to preserve context permanently

### What to Preserve
1. **Current project status** and phase completion
2. **Performance benchmarks** and optimization results
3. **Technical decisions** made and reasoning
4. **Working code examples** and test results
5. **Business requirements** and pricing logic
6. **Next steps** with specific priorities
7. **File locations** and architecture changes

### TodoWrite Usage
- Use `TodoWrite` tool frequently to track multi-step tasks
- Mark todos as `in_progress` before starting work
- Mark as `completed` immediately after finishing
- Keep only one task `in_progress` at a time
- Clean up completed tasks regularly

## Serena Workflow (Token-Efficient Code Analysis)
1. **Start with overview** - Use `get_symbols_overview` before reading files
2. **Navigate precisely** - Use `find_symbol` to target specific functions/classes
3. **Read selectively** - Only use `include_body=true` when you need implementation
4. **NEVER read entire files** unless absolutely necessary - use semantic tools first  