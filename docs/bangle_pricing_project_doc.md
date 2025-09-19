# Bangle Pricing Script - Project Documentation

## Project Overview
Creating a Python script to accurately price custom bangles made by hand at Askew Jewelers. The script will integrate with Stuller's API to get real-time material costs and apply markup calculations.

## Core Requirements

### Input Variables (Customer Determined)
- **v1: Size** - 10 through 27 (maps to MM measurements)
- **v2: Metal Color + Quality** - e.g., 14K Yellow Gold, 18K White Gold, etc.
- **v3: Width (MM)** - Variable width options
- **v4: Thickness (MM)** - Variable thickness options

### Size to MM Mapping
```
10 - 52.37    15 - 60.32    20 - 68.24    25 - 76.20
11 - 53.97    16 - 61.89    21 - 69.85    26 - 77.77
12 - 55.54    17 - 63.50    22 - 71.42    27 - 79.37
13 - 57.15    18 - 65.07    23 - 73.02
14 - 58.72    19 - 66.67    24 - 74.59
```
*Size = inside to inside measurement in MM*

## Technical Approach

### API Integration
- **Primary Endpoint**: Stuller API v2 products endpoint
- **Product Type**: "Sizing Stock" (not "blanks")
- **SKU Pattern**: `SIZING STOCK:76835:P` (base pattern observed)
- **Method**: Specific SKU lookup rather than filtered search

### Key Discovery
From Stuller website analysis:
- Products are "Sizing Stock" not traditional blanks
- Each combination of options generates unique SKU
- Web interface options that affect SKU:
  - Metal Shape (e.g., Flat)
  - Quality (e.g., 14K Yellow)
  - Width (e.g., 3mm)
  - Thickness (e.g., 2.5mm)
  - Length (user input in inches)

## Next Steps - API Exploration

### Phase 1: SKU Discovery
1. **Option A**: Fetch all "sizing stock" products from Stuller API
2. **Option B**: Manual mapping by testing web interface combinations
3. Analyze product descriptions/attributes to understand SKU construction logic

### Phase 2: Script Architecture
```python
# Planned structure:
def get_bangle_price():
    # 1. Input prompts for 4 variables
    # 2. Size-to-MM conversion (dictionary lookup)
    # 3. Build appropriate SKU from options
    # 4. Stuller API call for specific SKU
    # 5. Apply markup calculations
    # 6. Return final customer price with breakdown
```

### Phase 3: Web Interface (Future)
- Convert Python script to web interface
- Integrate with existing business systems
- Potentially incorporate into larger, aspirational independent jewelry ecosystem

## Stuller API Context
- **Experience**: Extensive API familiarity through S2S2 project
- **Authentication**: Already established
- **Endpoints Available**: 
  - `GET/POST api/v2/products` - Main product search
  - `GET/POST api/v2/products/advancedproductfilters` - Available filter types
- **Response Structure**: Includes pricing, stock status, product details

## Business Context
- **Family Business**: Askew Jewelers custom jewelry
- **Current Method**: Manual/inconsistent pricing
- **Goal**: Systematic, accurate pricing based on real material costs
- **Handmade Process**: Father hand-pounds bangles into shape
- **Simple Product**: No gems, just shaped metal bangles

---

*Ready to move to Claude Code for hands-on API exploration and SKU mapping*