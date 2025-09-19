#!/usr/bin/env python3
"""
Test the category IDs we actually discovered in sizing stock products
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bangler.api.stuller_client import StullerClient

def test_discovered_categories():
    """Test the category IDs we found in actual sizing stock products"""
    print("🧪 TESTING DISCOVERED CATEGORY IDs")
    print("=" * 50)

    client = StullerClient()

    # Categories found in actual sizing stock products
    categories = [
        {"id": 30500, "name": "Sizing Stock (jewelry-repair)"},
        {"id": 30063, "name": "Sizing Stock (ring-resizing)"},
        {"id": 1571, "name": "Stock (metals)"}
    ]

    results = {}

    for category in categories:
        print(f"\n🔍 TESTING CategoryId: {category['id']} ({category['name']})")
        print("-" * 40)

        try:
            result = client.search_sizing_stock_by_category(
                category_id=category["id"],
                page_size=500,
                max_pages=1  # Just test first page
            )

            if result["success"] and result["product_count"] > 0:
                print(f"✅ SUCCESS: {result['product_count']} products found")

                # Check if they're actually sizing stock
                products = result["products"]
                sizing_stock_count = 0
                sample_skus = []

                for product in products[:10]:  # Check first 10
                    sku = product.get("SKU", "")
                    desc = product.get("Description", "").upper()

                    if "SIZING STOCK" in sku.upper() or "SIZING STOCK" in desc:
                        sizing_stock_count += 1

                    if len(sample_skus) < 5:
                        sample_skus.append(sku)

                print(f"   Sizing stock in sample: {sizing_stock_count}/10")
                print(f"   Sample SKUs: {sample_skus}")

                results[category["id"]] = {
                    "success": True,
                    "total_products": result["product_count"],
                    "sizing_stock_ratio": f"{sizing_stock_count}/10"
                }
            else:
                print(f"❌ No products found")
                results[category["id"]] = {"success": False}

        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results[category["id"]] = {"success": False, "error": str(e)}

    # Summary
    print(f"\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)

    for category in categories:
        cat_id = category["id"]
        cat_name = category["name"]
        result = results.get(cat_id, {})

        if result.get("success"):
            print(f"✅ {cat_id} ({cat_name}): {result['total_products']} products")
            print(f"   Sizing stock ratio: {result['sizing_stock_ratio']}")
        else:
            print(f"❌ {cat_id} ({cat_name}): FAILED")

if __name__ == "__main__":
    test_discovered_categories()