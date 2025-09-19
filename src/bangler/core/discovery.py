"""
Phase 1 Discovery Tools for Sizing Stock Inventory
Maps all Stuller sizing stock products and their specifications
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..api.stuller_client import StullerClient
from ..config.settings import config


class SizingStockDiscovery:
    """Discovers and maps all sizing stock products from Stuller API"""

    def __init__(self, client: StullerClient = None):
        self.client = client or StullerClient()
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # Discovery results
        self.discovered_products = []
        self.shape_options = set()
        self.quality_options = set()
        self.width_options = set()
        self.thickness_options = set()
        self.length_options = set()

    def run_full_discovery(self) -> Dict[str, Any]:
        """
        Run complete discovery process for sizing stock products

        Returns comprehensive mapping of all sizing stock products
        """
        print("🔍 Starting Phase 1: Sizing Stock Discovery")
        start_time = time.time()

        results = {
            "discovery_time": None,
            "total_products_found": 0,
            "sizing_stock_products": 0,
            "success": False,
            "errors": [],
            "strategies_attempted": []
        }

        try:
            # Strategy 1: Search for advanced product filters
            print("📋 Discovering available product filters...")
            filter_result = self._discover_advanced_filters()
            results["strategies_attempted"].append("advanced_filters")

            if filter_result["success"]:
                print(f"✅ Found {len(filter_result.get('filters', []))} advanced filter types")

            # Strategy 2: Paginated search for Milled Products (sizing stock)
            print("🔎 Searching for sizing stock products with pagination...")
            search_result = self._search_sizing_stock_products(max_pages=5)  # Start with 5 pages for testing
            results["strategies_attempted"].append("product_search")

            if search_result["success"]:
                results["total_products_found"] = search_result["product_count"]
                results["sizing_stock_products"] = search_result["sizing_stock_count"]
                self.discovered_products = search_result["sizing_stock_products"]

                print(f"✅ Found {results['sizing_stock_products']} sizing stock products out of {results['total_products_found']} total")

                # Strategy 3: Analyze discovered products
                print("📊 Analyzing product specifications...")
                analysis_result = self._analyze_product_specifications()
                results.update(analysis_result)
                self._last_analysis = analysis_result.get("analysis", {})

                # Strategy 4: Save discovery results
                print("💾 Saving discovery results...")
                save_result = self._save_discovery_results()
                results["saved_to"] = save_result.get("file_path")

                results["success"] = True
            else:
                results["errors"].append(f"Product search failed: {search_result.get('error')}")

        except Exception as e:
            results["errors"].append(f"Discovery failed: {str(e)}")

        results["discovery_time"] = time.time() - start_time
        print(f"⏱️  Discovery completed in {results['discovery_time']:.2f} seconds")

        return results

    def _discover_advanced_filters(self) -> Dict[str, Any]:
        """Discover available advanced product filter types"""
        return self.client.get_advanced_product_filters()

    def _search_sizing_stock_products(self, max_pages: int = None) -> Dict[str, Any]:
        """Search for sizing stock products using paginated Milled Product search"""
        return self.client.search_sizing_stock(page_size=500, max_pages=max_pages)

    def _analyze_product_specifications(self) -> Dict[str, Any]:
        """
        Analyze discovered sizing stock products to extract specifications
        Maps out available shapes, qualities, widths, thicknesses, etc.
        """
        if not self.discovered_products:
            return {"analysis": "No products to analyze"}

        analysis = {
            "shapes_found": set(),
            "qualities_found": set(),
            "widths_found": set(),
            "thicknesses_found": set(),
            "sku_patterns": [],
            "sample_products": []
        }

        print(f"🔬 Analyzing {len(self.discovered_products)} sizing stock products...")

        for product in self.discovered_products:
            # Extract product information
            sku = product.get("SKU", "")
            description = product.get("Description", "")
            short_desc = product.get("ShortDescription", "")

            # Look for patterns in descriptions
            desc_upper = description.upper()
            short_upper = short_desc.upper()

            # Shape detection
            shapes = ["FLAT", "COMFORT FIT", "LOW DOME", "HALF ROUND", "SQUARE", "TRIANGLE"]
            for shape in shapes:
                if shape in desc_upper or shape in short_upper:
                    analysis["shapes_found"].add(shape)

            # Quality detection (metal types)
            qualities = ["14K", "18K", "10K", "YELLOW", "WHITE", "ROSE", "GOLD", "SILVER", "PLATINUM"]
            for quality in qualities:
                if quality in desc_upper or quality in short_upper:
                    analysis["qualities_found"].add(quality)

            # Width detection (look for mm measurements)
            import re
            width_pattern = r'(\d+)\s*MM'
            width_matches = re.findall(width_pattern, desc_upper)
            for width in width_matches:
                analysis["widths_found"].add(f"{width}mm")

            # Thickness detection
            thickness_pattern = r'(\d+\.?\d*)\s*MM\s*THICK'
            thickness_matches = re.findall(thickness_pattern, desc_upper)
            for thickness in thickness_matches:
                analysis["thicknesses_found"].add(f"{thickness}mm")

            # SKU pattern analysis
            if sku and len(analysis["sku_patterns"]) < 10:
                analysis["sku_patterns"].append(sku)

            # Sample products for manual review
            if len(analysis["sample_products"]) < 5:
                analysis["sample_products"].append({
                    "sku": sku,
                    "description": description,
                    "short_description": short_desc,
                    "price": product.get("Price", {})
                })

        # Convert sets to lists for JSON serialization
        analysis["shapes_found"] = list(analysis["shapes_found"])
        analysis["qualities_found"] = list(analysis["qualities_found"])
        analysis["widths_found"] = list(analysis["widths_found"])
        analysis["thicknesses_found"] = list(analysis["thicknesses_found"])

        print(f"📈 Analysis complete:")
        print(f"   Shapes: {len(analysis['shapes_found'])}")
        print(f"   Qualities: {len(analysis['qualities_found'])}")
        print(f"   Widths: {len(analysis['widths_found'])}")
        print(f"   Thicknesses: {len(analysis['thicknesses_found'])}")

        return {"analysis": analysis}

    def _save_discovery_results(self) -> Dict[str, Any]:
        """Save discovery results to JSON file for caching"""
        timestamp = int(time.time())
        filename = f"sizing_stock_discovery_{timestamp}.json"
        file_path = self.data_dir / filename

        # Also save as latest
        latest_path = self.data_dir / "sizing_stock_inventory.json"

        discovery_data = {
            "timestamp": timestamp,
            "discovery_metadata": {
                "total_products": len(self.discovered_products),
                "discovery_tool_version": "1.0",
                "stuller_api_base": self.client.base_url
            },
            "products": self.discovered_products,
            "analysis": getattr(self, '_last_analysis', {})
        }

        try:
            # Save timestamped version
            with open(file_path, 'w') as f:
                json.dump(discovery_data, f, indent=2)

            # Save as latest
            with open(latest_path, 'w') as f:
                json.dump(discovery_data, f, indent=2)

            print(f"💾 Saved discovery results to: {file_path}")
            print(f"💾 Updated latest inventory: {latest_path}")

            return {
                "success": True,
                "file_path": str(file_path),
                "latest_path": str(latest_path)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def load_cached_discovery(self) -> Optional[Dict[str, Any]]:
        """Load previously cached discovery results"""
        latest_path = self.data_dir / "sizing_stock_inventory.json"

        if latest_path.exists():
            try:
                with open(latest_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Failed to load cached discovery: {e}")

        return None


def run_discovery_cli():
    """Command-line interface for running discovery"""
    print("🎯 Bangler Phase 1: Sizing Stock Discovery Tool")
    print("=" * 50)

    # Validate configuration
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        return

    print(f"🔑 Using Stuller API: {config.stuller_api_url}")
    print(f"👤 Username: {config.stuller_username}")

    # Run discovery
    discovery = SizingStockDiscovery()
    results = discovery.run_full_discovery()

    # Print results
    print("\n" + "=" * 50)
    print("📋 DISCOVERY RESULTS")
    print("=" * 50)

    if results["success"]:
        print(f"✅ Discovery successful!")
        print(f"📊 Total products found: {results['total_products_found']}")
        print(f"🎯 Sizing stock products: {results['sizing_stock_products']}")
        print(f"⏱️  Time taken: {results['discovery_time']:.2f} seconds")

        if "analysis" in results and isinstance(results["analysis"], dict) and "analysis" in results["analysis"]:
            analysis = results["analysis"]["analysis"]
            print(f"\n📈 SPECIFICATION ANALYSIS:")
            print(f"   Shapes discovered: {analysis['shapes_found']}")
            print(f"   Qualities found: {analysis['qualities_found']}")
            print(f"   Widths found: {analysis['widths_found']}")
            print(f"   Thicknesses found: {analysis['thicknesses_found']}")

    else:
        print(f"❌ Discovery failed!")
        for error in results["errors"]:
            print(f"   - {error}")


if __name__ == "__main__":
    run_discovery_cli()