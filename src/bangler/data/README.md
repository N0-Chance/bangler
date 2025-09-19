# Sizing Stock Data Directory

This directory contains CSV exports from Stuller's sizing stock catalog.

## File Format

Place your sizing stock CSV exports here with the naming pattern:
```
sizingstock-YYYYMMDD.csv
```

Example: `sizingstock-20250919.csv`

## How it Works

The `SizingStockLookup` class automatically detects and uses the most recent CSV file based on the date in the filename. This means you can:

1. Export a new CSV from Stuller
2. Save it here with the current date
3. The system automatically uses the newest data

## CSV Requirements

The CSV should be a direct export from Stuller with these key columns:
- `Id` - Product ID
- `Sku` - Sizing stock SKU
- `Price` - Current price
- `UnitOfSale` - Unit (typically "DWT")
- `DescriptiveElementName1-6` and `DescriptiveElementValue1-6` - Product specifications

## Current Status

The system currently has data for **5,938 sizing stock products** covering all shapes, qualities, widths, and thicknesses needed for bangle calculations.