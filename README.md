# Bangler - Custom Bangle Pricing Tool

A Python script for pricing custom bangles at Askew Jewelers. This tool integrates with Stuller's API to get real-time material costs and applies markup calculations for handmade jewelry pricing.

## Overview

This project automates the pricing process for custom bangles by taking customer specifications and calculating accurate pricing based on current material costs. The tool replaces manual and inconsistent pricing with a systematic approach based on real material costs.

## How It Works

The script takes 4 customer-determined variables:
- **Size**: 10-27 (maps to specific MM measurements)
- **Metal Color + Quality**: e.g., 14K Yellow Gold, 18K White Gold
- **Width (MM)**: Variable width options
- **Thickness (MM)**: Variable thickness options

The tool then:
1. Converts size to MM measurements using a lookup table
2. Builds appropriate SKU from metal and size options
3. Makes API calls to Stuller for current material pricing
4. Applies markup calculations
5. Returns final customer price with breakdown

## Business Context

- Family jewelry business specializing in handmade bangles
- Simple product: shaped metal bangles (no gems)
- Goal: systematic pricing based on real material costs
- Replaces manual pricing with automated calculations

## Development Status

Project is currently in development phase. The foundation is set up with project documentation, dependencies, and size conversion data ready for implementation.

## Technical Stack

- Python 3.10+
- Poetry for dependency management
- Stuller API v2 integration
- Size-to-MM conversion lookup table