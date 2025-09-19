# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose
This is a Python script project for pricing custom bangles at Askew Jewelers. The script integrates with Stuller's API to get real-time material costs and applies markup calculations for handmade jewelry pricing.

## Core Functionality
The project aims to create a script that takes 4 customer-determined variables:
- **Size**: 10-27 (maps to specific MM measurements via lookup table)
- **Metal Color + Quality**: e.g., 14K Yellow Gold, 18K White Gold
- **Width (MM)**: Variable width options
- **Thickness (MM)**: Variable thickness options

## Key Data Mappings
Size to MM conversion table is defined in `bangle_size.txt`:
- Size 10 = 52.37mm, Size 15 = 60.32mm, Size 20 = 68.24mm, Size 25 = 76.20mm, etc.
- These represent inside-to-inside measurements in MM

## API Integration Approach
- **Target API**: Stuller API v2 products endpoint
- **Product Type**: "Sizing Stock" (not "blanks")
- **Method**: Specific SKU lookup rather than filtered search
- **Experience Note**: Developer has extensive API familiarity through S2S2 project

## Architecture Plan
```python
def get_bangle_price():
    # 1. Input prompts for 4 variables
    # 2. Size-to-MM conversion (dictionary lookup)
    # 3. Build appropriate SKU from options
    # 4. Stuller API call for specific SKU
    # 5. Apply markup calculations
    # 6. Return final customer price with breakdown
```

## Business Context
- Family jewelry business (Askew Jewelers)
- Father hand-pounds bangles into shape
- Currently uses manual/inconsistent pricing
- Simple product: no gems, just shaped metal bangles
- Goal: systematic pricing based on real material costs

## Development Status
Project is in planning/documentation phase. No code files exist yet. Ready for API exploration and SKU mapping implementation.