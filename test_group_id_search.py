#!/usr/bin/env python3
"""
Test GroupId=69562 filtering vs current Milled Product approach
Compare efficiency and results
"""

import sys
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bangler.api.stuller_client import StullerClient
from bangler.config.settings import config

def test_group_id_vs_milled_product():
    """Compare GroupId filtering with current Milled Product approach"""
    print("🧪 TESTING: GroupId vs Milled Product Filtering")
    print("=" * 60)

    client = StullerClient()

    strategies = [
        {
            "name": "GroupId 69562 (Your hint)",
            "method": "group_id",
            "id": 69562,
            "max_pages": 3
        },
        {
            "name": "GroupId 10021846 (Discovered)",
            "method": "group_id",
            "id": 10021846,
            "max_pages": 3
        },
        {
            "name": "Milled Product (Current)",
            "method": "milled_product",
            "id": None,
            "max_pages": 2  # We know this works
        }
    ]

    results = {}

    for strategy in strategies:
        print(f"\n🔍 TESTING: {strategy['name']}")
        print("-" * 40)

        start_time = time.time()

        try:
            if strategy["method"] == "group_id":
                result = client.search_sizing_stock_by_group_id(
                    group_id=strategy["id"],
                    page_size=500,
                    max_pages=strategy["max_pages"]
                )
            else:
                result = client.search_sizing_stock(
                    page_size=500,
                    max_pages=strategy["max_pages"]
                )

            duration = time.time() - start_time

            if result["success"]:
                print(f"✅ SUCCESS:")
                print(f"   Total products: {result['product_count']}")
                print(f"   Sizing stock: {result['sizing_stock_count']}")
                print(f"   Pages fetched: {result['pages_fetched']}")
                print(f"   Duration: {duration:.2f}s")

                if "sizing_stock_ratio" in result:
                    print(f"   Sizing stock ratio: {result['sizing_stock_ratio']}")

                # Sample some products
                products = result["products"]
                if products:
                    print(f"   Sample SKUs:")
                    for product in products[:3]:
                        sku = product.get("SKU", "N/A")
                        desc = product.get("Description", "N/A")[:50]
                        print(f"     - {sku}")

                results[strategy["name"]] = {
                    "success": True,
                    "total_products": result["product_count"],
                    "sizing_stock": result["sizing_stock_count"],
                    "pages": result["pages_fetched"],
                    "duration": duration,
                    "efficiency": result["sizing_stock_count"] / result["product_count"] if result["product_count"] > 0 else 0
                }
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                results[strategy["name"]] = {"success": False, "duration": duration}

        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ EXCEPTION: {str(e)}")
            results[strategy["name"]] = {"success": False, "error": str(e), "duration": duration}

    # Comprehensive comparison
    print(f"\n" + "=" * 60)
    print("📊 COMPREHENSIVE COMPARISON")
    print("=" * 60)

    successful_strategies = []

    for name, result in results.items():
        if result.get("success"):
            successful_strategies.append(name)
            efficiency = result.get("efficiency", 0) * 100
            print(f"✅ {name}:")
            print(f"   Products: {result['total_products']:,}")
            print(f"   Sizing Stock: {result['sizing_stock']:,}")
            print(f"   Efficiency: {efficiency:.1f}% sizing stock")
            print(f"   Time: {result['duration']:.2f}s")
            print(f"   Pages: {result['pages']}")
        else:
            print(f"❌ {name}: FAILED ({result.get('duration', 0):.2f}s)")

    # Recommendations
    print(f"\n🎯 ANALYSIS & RECOMMENDATION:")
    if successful_strategies:
        # Find the most efficient strategy
        best_efficiency = max(successful_strategies,
                            key=lambda x: results[x].get("efficiency", 0))
        best_volume = max(successful_strategies,
                         key=lambda x: results[x].get("sizing_stock", 0))

        print(f"   Most Efficient: {best_efficiency}")
        print(f"     - {results[best_efficiency]['efficiency']*100:.1f}% of products are sizing stock")
        print(f"   Most Sizing Stock: {best_volume}")
        print(f"     - {results[best_volume]['sizing_stock']:,} sizing stock products found")

        if best_efficiency == best_volume:
            print(f"   🏆 WINNER: {best_efficiency} (both efficient AND comprehensive)")
        else:
            print(f"   📊 Trade-off: Efficiency vs Volume")

        # Scaling projection
        if results[best_efficiency]["efficiency"] > 0:
            total_pages_needed = 1660 * results["Milled Product (Current)"]["efficiency"] / results[best_efficiency]["efficiency"]
            print(f"   📈 Projected pages needed for complete discovery: {total_pages_needed:.0f} pages")
    else:
        print("   No successful strategies found - check API connectivity")

if __name__ == "__main__":
    test_group_id_vs_milled_product()