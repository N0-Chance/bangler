#!/usr/bin/env python3
"""
Debug Discovery Tool - Let's see what's actually in the Stuller API
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bangler.api.stuller_client import StullerClient
from bangler.config.settings import config
import json

def debug_stuller_products():
    """Debug tool to see what's actually available in Stuller API"""
    print("🔍 DEBUG: Exploring Stuller API Products")
    print("=" * 50)

    client = StullerClient()

    # Get a sample of products to understand the structure
    print("📦 Fetching sample products...")
    result = client.search_products(
        filters=["OnPriceList", "Orderable"],
        includes=["All"],
        page_size=20  # Just a small sample
    )

    if result["success"]:
        print(f"✅ Found {result['product_count']} products")

        print("\n🔍 SAMPLE PRODUCT ANALYSIS:")
        print("=" * 30)

        for i, product in enumerate(result["products"][:5]):  # Just first 5
            print(f"\n📋 Product {i+1}:")
            print(f"   SKU: {product.get('SKU', 'N/A')}")
            print(f"   Description: {product.get('Description', 'N/A')[:100]}...")
            print(f"   Short Desc: {product.get('ShortDescription', 'N/A')}")
            print(f"   Price: {product.get('Price', 'N/A')}")

            # Look for any sizing stock indicators
            sku = str(product.get('SKU', '')).upper()
            desc = str(product.get('Description', '')).upper()
            short_desc = str(product.get('ShortDescription', '')).upper()

            sizing_indicators = []
            if 'SIZING' in sku: sizing_indicators.append('SKU has SIZING')
            if 'STOCK' in sku: sizing_indicators.append('SKU has STOCK')
            if 'SIZING' in desc: sizing_indicators.append('DESC has SIZING')
            if 'STOCK' in desc: sizing_indicators.append('DESC has STOCK')
            if 'SIZING' in short_desc: sizing_indicators.append('SHORT_DESC has SIZING')
            if 'STOCK' in short_desc: sizing_indicators.append('SHORT_DESC has STOCK')

            if sizing_indicators:
                print(f"   🎯 SIZING STOCK INDICATORS: {', '.join(sizing_indicators)}")
            else:
                print(f"   ❌ No sizing stock indicators found")

        # Try different search strategies
        print("\n🔎 TESTING DIFFERENT SEARCH STRATEGIES:")
        print("=" * 40)

        # Strategy 1: Search with different filters
        strategies = [
            {"name": "Basic search", "filters": ["OnPriceList"]},
            {"name": "Orderable only", "filters": ["Orderable"]},
            {"name": "No filters", "filters": []},
        ]

        for strategy in strategies:
            result = client.search_products(
                filters=strategy["filters"],
                page_size=10
            )
            print(f"📊 {strategy['name']}: {result['product_count']} products found")

        # Strategy 2: Check advanced filters
        print("\n🔧 CHECKING ADVANCED FILTERS:")
        filter_result = client.get_advanced_product_filters()
        if filter_result["success"]:
            filters = filter_result["filters"]
            print(f"✅ Available filter types: {len(filters)}")
            if filters:
                print("📋 Filter types:")
                if isinstance(filters, list):
                    for filter_type in filters[:10]:  # Show first 10
                        print(f"   - {filter_type}")
                else:
                    print(f"   Filter data: {filters}")

    else:
        print(f"❌ Failed to fetch products: {result.get('error')}")

if __name__ == "__main__":
    debug_stuller_products()