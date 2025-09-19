"""
Stuller API Client for Bangler Project
Adapted from proven s2s2 patterns for reliable Stuller integration
"""

import os
import time
from typing import Dict, List, Any
import requests
from requests.auth import HTTPBasicAuth


class StullerClient:
    """Client for Stuller API with enterprise reliability features"""

    def __init__(self, username: str = None, password: str = None, base_url: str = "https://api.stuller.com/v2"):
        # Use environment variables if not provided
        self.username = username or os.getenv("STULLER_USERNAME")
        self.password = password or os.getenv("STULLER_PASSWORD")

        if not self.username or not self.password:
            raise ValueError("Stuller credentials required. Set STULLER_USERNAME and STULLER_PASSWORD environment variables.")

        self.base_url = base_url
        self.timeout = 30

        # Initialize session with authentication
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Bangler-Stuller-Client/1.0"
        })

        # Circuit breaker state (from s2s2 pattern)
        self.failure_count = 0
        self.max_failures = 5

    def _make_request(self, endpoint: str, request_body: dict) -> requests.Response:
        """Internal method to make HTTP requests with circuit breaker"""
        # Simple circuit breaker - open after max failures
        if self.failure_count >= self.max_failures:
            raise Exception(f"Circuit breaker is open after {self.max_failures} failures")

        try:
            response = self.session.post(endpoint, json=request_body, timeout=self.timeout)

            # Reset failure count on success
            if response.status_code == 200:
                self.failure_count = 0

            return response

        except Exception:
            self.failure_count += 1
            raise

    def search_products(self, filters: List[str] = None, includes: List[str] = None,
                       advanced_filters: List[Dict] = None, skus: List[str] = None,
                       page_size: int = 100) -> Dict[str, Any]:
        """
        Search for products using Stuller API with flexible filtering

        Args:
            filters: Basic filters like ["OnPriceList", "Orderable"]
            includes: Data to include like ["All", "Images"]
            advanced_filters: Complex filters for product type, etc.
            skus: Specific SKUs to lookup
            page_size: Number of results per page

        Returns:
            Dict with products, pagination info, and metadata
        """
        endpoint = f"{self.base_url}/products"

        # Build request body
        request_body = {}

        if filters:
            request_body["Filter"] = filters

        if includes:
            request_body["Include"] = includes

        if advanced_filters:
            request_body["AdvancedProductFilters"] = advanced_filters

        if skus:
            request_body["SKU"] = skus

        if page_size:
            request_body["PageSize"] = page_size

        start_time = time.time()

        try:
            response = self._make_request(endpoint, request_body)

            # Handle HTTP errors
            if response.status_code == 401:
                raise ValueError("Authentication failed - check Stuller credentials")
            elif response.status_code == 429:
                raise ValueError("API rate limit exceeded")
            elif response.status_code >= 400:
                response.raise_for_status()

            # Parse response
            data = response.json()
            products = data.get("Products", [])
            next_page = data.get("NextPage")
            total_products = data.get("TotalNumberOfProducts")

            request_time_ms = int((time.time() - start_time) * 1000)

            return {
                "products": products,
                "next_page_token": next_page,
                "total_products": total_products,
                "request_time_ms": request_time_ms,
                "success": True,
                "product_count": len(products)
            }

        except Exception as e:
            request_time_ms = int((time.time() - start_time) * 1000)
            return {
                "products": [],
                "next_page_token": None,
                "total_products": 0,
                "request_time_ms": request_time_ms,
                "success": False,
                "error": str(e),
                "product_count": 0
            }

    def search_sizing_stock_by_category(self, category_id: int, page_size: int = 500, max_pages: int = None) -> Dict[str, Any]:
        """
        Search for sizing stock using specific CategoryId filtering

        Args:
            category_id: Specific category ID to filter (e.g., 69562 or 10021846)
            page_size: Products per page (max 500)
            max_pages: Maximum pages to fetch (None = all pages)
        """
        all_products = []
        page_count = 0
        next_page_token = None
        total_products = 0

        print(f"🔄 Starting category-filtered search (CategoryId: {category_id})...")

        while True:
            page_count += 1
            print(f"📄 Fetching page {page_count}...")

            result = self.search_products(
                filters=["OnPriceList", "Orderable"],
                includes=["All"],
                page_size=page_size
            )

            # Need to add CategoryIds parameter support to search_products
            # For now, let's implement this directly

            endpoint = f"{self.base_url}/products"
            request_body = {
                "Filter": ["OnPriceList", "Orderable"],
                "Include": ["All"],
                "CategoryIds": [category_id],
                "PageSize": page_size
            }

            if next_page_token:
                request_body["NextPage"] = next_page_token

            try:
                response = self._make_request(endpoint, request_body)

                if response.status_code == 200:
                    data = response.json()
                    page_products = data.get("Products", [])
                    all_products.extend(page_products)

                    if not total_products and data.get("TotalNumberOfProducts"):
                        total_products = data.get("TotalNumberOfProducts")

                    print(f"   ✅ Page {page_count}: {len(page_products)} products")

                    # Check for next page
                    next_page_token = data.get("NextPage")
                    if not next_page_token:
                        print("📄 No more pages available")
                        break

                    # Check max pages limit
                    if max_pages and page_count >= max_pages:
                        print(f"📄 Reached max pages limit ({max_pages})")
                        break
                else:
                    print(f"❌ Page {page_count} failed: HTTP {response.status_code}")
                    break

            except Exception as e:
                print(f"❌ Page {page_count} failed: {str(e)}")
                break

        print(f"🎉 Category search complete: {page_count} pages, {len(all_products)} total products")

        return {
            "products": all_products,
            "sizing_stock_products": all_products,  # Assume all are sizing stock if filtered by category
            "sizing_stock_count": len(all_products),
            "product_count": len(all_products),
            "total_products": total_products,
            "pages_fetched": page_count,
            "category_id": category_id,
            "success": True
        }

    def search_sizing_stock(self, page_size: int = 500, max_pages: int = None) -> Dict[str, Any]:
        """
        Discover sizing stock products using "Milled Product" type with pagination

        Based on domain knowledge, sizing stock products are classified as "Milled Product"

        Args:
            page_size: Products per page (max 500)
            max_pages: Maximum pages to fetch (None = all pages)
        """
        # Use advanced filter for "Milled Product" type
        advanced_filters = [
            {
                "Type": "ProductType",
                "Values": [
                    {
                        "DisplayValue": "Milled Product",
                        "Value": "Milled Product"
                    }
                ]
            }
        ]

        all_products = []
        all_sizing_stock = []
        page_count = 0
        next_page_token = None
        total_products = 0

        print(f"🔄 Starting paginated search for Milled Products (max {max_pages or 'all'} pages)...")

        while True:
            page_count += 1
            print(f"📄 Fetching page {page_count}...")

            # Build request with pagination
            request_body = {
                "Filter": ["OnPriceList", "Orderable"],
                "Include": ["All"],
                "AdvancedProductFilters": advanced_filters,
                "PageSize": page_size
            }

            if next_page_token:
                request_body["NextPage"] = next_page_token

            # Make the request
            result = self.search_products(
                filters=["OnPriceList", "Orderable"],
                includes=["All"],
                advanced_filters=advanced_filters,
                page_size=page_size
            )

            if not result["success"]:
                print(f"❌ Page {page_count} failed: {result.get('error')}")
                break

            page_products = result["products"]
            all_products.extend(page_products)

            if "total_products" not in locals() and result.get("total_products"):
                total_products = result["total_products"]

            print(f"   ✅ Page {page_count}: {len(page_products)} products")

            # Filter for sizing stock on this page
            page_sizing_stock = []
            for product in page_products:
                sku = product.get("SKU", "").upper()
                description = product.get("Description", "").upper()
                short_desc = product.get("ShortDescription", "").upper()

                # Look for sizing stock indicators
                if any(indicator in sku for indicator in ["SIZING STOCK", "SIZING_STOCK"]):
                    page_sizing_stock.append(product)
                elif any(indicator in description for indicator in ["SIZING STOCK", "SIZING_STOCK"]):
                    page_sizing_stock.append(product)
                elif any(indicator in short_desc for indicator in ["SIZING STOCK", "SIZING_STOCK"]):
                    page_sizing_stock.append(product)

            all_sizing_stock.extend(page_sizing_stock)
            print(f"   🎯 Found {len(page_sizing_stock)} sizing stock products on this page")

            # Check for next page
            next_page_token = result.get("next_page_token")
            if not next_page_token:
                print("📄 No more pages available")
                break

            # Check max pages limit
            if max_pages and page_count >= max_pages:
                print(f"📄 Reached max pages limit ({max_pages})")
                break

        print(f"🎉 Pagination complete: {page_count} pages, {len(all_products)} total products, {len(all_sizing_stock)} sizing stock")

        return {
            "products": all_products,
            "sizing_stock_products": all_sizing_stock,
            "sizing_stock_count": len(all_sizing_stock),
            "product_count": len(all_products),
            "total_products": total_products,
            "pages_fetched": page_count,
            "success": True
        }

    def search_sizing_stock_by_group_id(self, group_id: int, page_size: int = 500, max_pages: int = None) -> Dict[str, Any]:
        """
        Search for sizing stock using DescriptiveElementGroup GroupId filtering

        This targets specific GroupId (e.g., 69562) to efficiently find all sizing stock
        without scanning all Milled Products.

        Args:
            group_id: DescriptiveElementGroup GroupId to filter (e.g., 69562)
            page_size: Products per page (max 500)
            max_pages: Maximum pages to fetch (None = all pages)
        """
        all_products = []
        page_count = 0
        next_page_token = None
        total_products = 0

        print(f"🔄 Starting GroupId-filtered search (GroupId: {group_id})...")

        # Try GroupId as AdvancedProductFilter
        advanced_filters = [
            {
                "Type": "GroupId",
                "Values": [
                    {
                        "DisplayValue": str(group_id),
                        "Value": str(group_id)
                    }
                ]
            }
        ]

        while True:
            page_count += 1
            print(f"📄 Fetching page {page_count}...")

            try:
                result = self.search_products(
                    filters=["OnPriceList", "Orderable"],
                    includes=["All"],
                    advanced_filters=advanced_filters,
                    page_size=page_size
                )

                if not result["success"]:
                    print(f"❌ Page {page_count} failed: {result.get('error')}")
                    break

                page_products = result["products"]
                all_products.extend(page_products)

                if not total_products and result.get("total_products"):
                    total_products = result["total_products"]

                print(f"   ✅ Page {page_count}: {len(page_products)} products")

                # Check for next page
                next_page_token = result.get("next_page_token")
                if not next_page_token:
                    print("📄 No more pages available")
                    break

                # Check max pages limit
                if max_pages and page_count >= max_pages:
                    print(f"📄 Reached max pages limit ({max_pages})")
                    break

            except Exception as e:
                print(f"❌ Page {page_count} failed: {str(e)}")
                break

        print(f"🎉 GroupId search complete: {page_count} pages, {len(all_products)} total products")

        # Analyze what we found
        sizing_stock_count = 0
        for product in all_products:
            sku = product.get("SKU", "").upper()
            description = product.get("Description", "").upper()

            if "SIZING STOCK" in sku or "SIZING STOCK" in description:
                sizing_stock_count += 1

        print(f"🎯 Sizing stock analysis: {sizing_stock_count}/{len(all_products)} products are sizing stock")

        return {
            "products": all_products,
            "sizing_stock_products": all_products,  # Assume all are relevant if GroupId filtering worked
            "sizing_stock_count": sizing_stock_count,
            "product_count": len(all_products),
            "total_products": total_products,
            "pages_fetched": page_count,
            "group_id": group_id,
            "sizing_stock_ratio": f"{sizing_stock_count}/{len(all_products)}" if all_products else "0/0",
            "success": True
        }

    def get_advanced_product_filters(self) -> Dict[str, Any]:
        """
        Get available advanced product filter types from Stuller API
        Useful for discovering how to filter for sizing stock products
        """
        endpoint = f"{self.base_url}/products/advancedproductfilters"

        try:
            response = self._make_request(endpoint, {})

            if response.status_code == 200:
                return {
                    "success": True,
                    "filters": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_specific_sku(self, sku: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific SKU
        Used for validating discovered sizing stock SKUs
        """
        return self.search_products(
            skus=[sku],
            includes=["All"],
            filters=["OnPriceList", "Orderable"]
        )