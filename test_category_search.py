#!/usr/bin/env python3
"""
Test different search strategies for sizing stock discovery
Compare CategoryId filtering vs AdvancedProductFilters
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bangler.api.stuller_client import StullerClient
from bangler.config.settings import config

def test_search_strategies():
    """Test different approaches to find sizing stock"""
    print("🧪 TESTING SIZING STOCK SEARCH STRATEGIES")
    print("=" * 50)

    client = StullerClient()

    strategies = [
        {"name": "CategoryId 69562 (Your hint)", "method": "category", "id": 69562},
        {"name": "CategoryId 10021846 (Discovered)", "method": "category", "id": 10021846},
        {"name": "Milled Product filter (Current)", "method": "milled", "id": None}
    ]

    results = {}

    for strategy in strategies:
        print(f"\n🔍 TESTING: {strategy['name']}")
        print("-" * 30)

        try:
            if strategy["method"] == "category":
                result = client.search_sizing_stock_by_category(
                    category_id=strategy["id"],
                    page_size=500,
                    max_pages=2  # Limit for testing
                )
            else:
                result = client.search_sizing_stock(
                    page_size=500,
                    max_pages=2  # Limit for testing
                )

            if result["success"]:
                print(f"✅ SUCCESS: {result['product_count']} products found")
                print(f"   Pages fetched: {result['pages_fetched']}")
                print(f"   Sizing stock: {result['sizing_stock_count']}")

                # Sample some products
                products = result["products"]
                if products:
                    print(f"   Sample SKUs:")
                    for product in products[:3]:
                        sku = product.get("SKU", "N/A")
                        desc = product.get("Description", "N/A")[:50]
                        print(f"     - {sku}: {desc}...")

                results[strategy["name"]] = {
                    "success": True,
                    "count": result["product_count"],
                    "sizing_stock": result["sizing_stock_count"],
                    "pages": result["pages_fetched"]
                }
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                results[strategy["name"]] = {"success": False}

        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results[strategy["name"]] = {"success": False, "error": str(e)}

    # Summary comparison
    print(f"\n" + "=" * 50)
    print("📊 STRATEGY COMPARISON")
    print("=" * 50)

    for name, result in results.items():
        if result.get("success"):
            print(f"✅ {name}:")
            print(f"   Products: {result['count']}")
            print(f"   Sizing Stock: {result['sizing_stock']}")
            print(f"   Pages: {result['pages']}")
        else:
            print(f"❌ {name}: FAILED")

    # Recommendation
    print(f"\n🎯 RECOMMENDATION:")
    successful_strategies = [name for name, result in results.items() if result.get("success")]

    if successful_strategies:
        # Find the strategy with the most sizing stock products
        best_strategy = max(successful_strategies,
                           key=lambda x: results[x].get("sizing_stock", 0))
        print(f"   Use: {best_strategy}")
        print(f"   Reason: Found {results[best_strategy]['sizing_stock']} sizing stock products")
    else:
        print("   No successful strategies found - check API credentials or connectivity")


if __name__ == "__main__":
    test_search_strategies()