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





    def get_sku_price(self, sku: str) -> Dict[str, Any]:
        """
        Get current price for a specific SKU
        Used for real-time pricing in Phase 2
        """
        return self.search_products(
            skus=[sku],
            includes=["All"],
            filters=["OnPriceList", "Orderable"]
        )