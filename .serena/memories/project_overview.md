# Bangler Project Overview

## Purpose
A Python script project for pricing custom bangles at Askew Jewelers. The script integrates with Stuller's API to get real-time material costs and applies markup calculations for handmade jewelry pricing.

## Business Context
- Family jewelry business (Askew Jewelers)
- Father hand-pounds bangles into shape
- Currently uses manual/inconsistent pricing
- Simple product: no gems, just shaped metal bangles
- Goal: systematic pricing based on real material costs

## Current Status
- Project is in planning/documentation phase
- No source code files exist yet
- Ready for API exploration and SKU mapping implementation

## Core Functionality Requirements
The script takes 4 customer-determined variables:
- **Size**: 10-27 (maps to specific MM measurements via lookup table)
- **Metal Color + Quality**: e.g., 14K Yellow Gold, 18K White Gold
- **Width (MM)**: Variable width options
- **Thickness (MM)**: Variable thickness options

## Key Data Files
- `bangle_size.txt`: Size to MM conversion table (Size 10 = 52.37mm, etc.)
- `CLAUDE.md`: Claude Code project instructions
- `bangle_pricing_project_doc.md`: Detailed project documentation