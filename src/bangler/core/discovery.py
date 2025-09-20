"""
Phase 2 CSV-Based Sizing Stock Lookup
Direct CSV parsing for sizing stock products from Stuller export
"""

import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class SizingStockLookup:
    """Loads and searches sizing stock products from CSV export"""

    def __init__(self, csv_path: str = None):
        if csv_path:
            self.csv_path = Path(csv_path)
        else:
            # Auto-detect the most recent sizing stock CSV in data directory
            self.csv_path = self._find_latest_csv()

        self.products = []
        self._elements_cache = {}  # Cache for parsed DescriptiveElements
        self._load_csv()

    def _find_latest_csv(self) -> Path:
        """Find the most recent sizing stock CSV file based on date in filename"""
        data_dir = Path(__file__).parent.parent / "data"

        # Look for files matching pattern: sizingstock-YYYYMMDD.csv
        pattern = re.compile(r'sizingstock-(\d{8})\.csv')
        latest_date = None
        latest_file = None

        for csv_file in data_dir.glob("sizingstock-*.csv"):
            match = pattern.match(csv_file.name)
            if match:
                date_str = match.group(1)
                if latest_date is None or date_str > latest_date:
                    latest_date = date_str
                    latest_file = csv_file

        if latest_file is None:
            raise FileNotFoundError(f"No sizing stock CSV files found in {data_dir}")

        print(f"📅 Using sizing stock CSV: {latest_file.name} (date: {latest_date})")
        return latest_file

    def _load_csv(self) -> None:
        """Load sizing stock products from CSV file"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Sizing stock CSV not found: {self.csv_path}")

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.products = list(reader)

        # Memory usage logging
        memory_mb = sys.getsizeof(self.products) / 1024 / 1024
        print(f"✅ Loaded {len(self.products)} sizing stock products from CSV")
        print(f"📊 Memory usage: {memory_mb:.1f}MB (products list)")

        if hasattr(self, '_elements_cache'):
            cache_mb = sys.getsizeof(self._elements_cache) / 1024 / 1024
            print(f"📊 Cache initialized: {cache_mb:.3f}MB")

    def find_sku(self, shape: str, quality: str, width: str, thickness: str = None, length: str = None) -> Optional[str]:
        """
        Find sizing stock SKU based on customer specifications

        Args:
            shape: Metal shape (e.g., "Flat", "Half Round")
            quality: Metal quality (e.g., "14K Yellow")
            width: Width specification (e.g., "6.5 Mm")
            thickness: Thickness specification (optional)
            length: Length specification (optional, defaults to "Bulk")

        Returns:
            SKU string if found, or None if not found
        """
        for product in self.products:
            # Check descriptive elements for match (with caching)
            product_id = product.get("Id", "")
            if product_id in self._elements_cache:
                elements = self._elements_cache[product_id]
            else:
                elements = self._extract_descriptive_elements(product)
                if product_id:  # Only cache if we have a valid ID
                    self._elements_cache[product_id] = elements

            if (elements.get("Metal Shape", "").strip().lower() == shape.lower() and
                elements.get("Quality", "").strip().lower() == quality.lower() and
                elements.get("Width", "").strip().lower() == width.lower()):

                # Optional thickness check
                if thickness and elements.get("Thickness", "").strip().lower() != thickness.lower():
                    continue

                # Optional length check (default to Bulk if not specified)
                target_length = length or "Bulk"
                if elements.get("Length", "").strip().lower() != target_length.lower():
                    continue

                return product.get("Sku")

        return None

    def _extract_descriptive_elements(self, product: Dict[str, Any]) -> Dict[str, str]:
        """Extract descriptive elements from CSV product row"""
        elements = {}

        # CSV has paired columns: DescriptiveElementNameN, DescriptiveElementValueN
        for i in range(1, 7):  # Assuming up to 6 descriptive elements
            name_key = f"DescriptiveElementName{i}"
            value_key = f"DescriptiveElementValue{i}"

            if name_key in product and value_key in product:
                name = product[name_key]
                value = product[value_key]
                if name and value:
                    elements[name] = value

        return elements

    def get_available_options(self) -> Dict[str, List[str]]:
        """Get all available shapes, qualities, widths, etc. from CSV data"""
        options = {
            "shapes": set(),
            "qualities": set(),
            "widths": set(),
            "thicknesses": set(),
            "lengths": set()
        }

        for product in self.products:
            # Use caching for get_available_options too
            product_id = product.get("Id", "")
            if product_id in self._elements_cache:
                elements = self._elements_cache[product_id]
            else:
                elements = self._extract_descriptive_elements(product)
                if product_id:
                    self._elements_cache[product_id] = elements

            if "Metal Shape" in elements:
                options["shapes"].add(elements["Metal Shape"])
            if "Quality" in elements:
                options["qualities"].add(elements["Quality"])
            if "Width" in elements:
                options["widths"].add(elements["Width"])
            if "Thickness" in elements:
                options["thicknesses"].add(elements["Thickness"])
            if "Length" in elements:
                options["lengths"].add(elements["Length"])

        # Convert sets to sorted lists
        return {key: sorted(list(values)) for key, values in options.items()}

    def get_nested_options_for_cli(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """Get options structured for CLI prompts: shape -> quality -> width -> thicknesses"""
        nested_options = {}
        
        for product in self.products:
            # Use caching for performance
            product_id = product.get("Id", "")
            if product_id in self._elements_cache:
                elements = self._elements_cache[product_id]
            else:
                elements = self._extract_descriptive_elements(product)
                if product_id:
                    self._elements_cache[product_id] = elements
            
            # Extract the key elements we need
            shape = elements.get("Metal Shape")
            quality = elements.get("Quality") 
            width = elements.get("Width")
            thickness = elements.get("Thickness")
            
            # Skip if any required element is missing
            if not all([shape, quality, width, thickness]):
                continue
                
            # Build nested structure
            if shape not in nested_options:
                nested_options[shape] = {}
            
            if quality not in nested_options[shape]:
                nested_options[shape][quality] = {}
                
            if width not in nested_options[shape][quality]:
                nested_options[shape][quality][width] = []
                
            # Add thickness if not already present
            if thickness not in nested_options[shape][quality][width]:
                nested_options[shape][quality][width].append(thickness)
        
        # Sort all lists for consistent ordering
        for shape in nested_options:
            for quality in nested_options[shape]:
                for width in nested_options[shape][quality]:
                    nested_options[shape][quality][width].sort(
                        key=lambda x: float(x.replace(' Mm', ''))
                    )
        
        return nested_options

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get performance statistics about the cache"""
        cache_size = len(self._elements_cache)
        cache_memory_mb = sys.getsizeof(self._elements_cache) / 1024 / 1024

        return {
            "cached_products": cache_size,
            "total_products": len(self.products),
            "cache_hit_ratio": f"{cache_size}/{len(self.products)}" if self.products else "0/0",
            "cache_memory_mb": round(cache_memory_mb, 3)
        }