"""
Phase 2 CSV-Based Sizing Stock Lookup
Direct CSV parsing for sizing stock products from Stuller export
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


class SizingStockLookup:
    """Loads and searches sizing stock products from CSV export"""

    def __init__(self, csv_path: str = None):
        if csv_path:
            self.csv_path = Path(csv_path)
        else:
            # Default to the sizing stock CSV in docs
            self.csv_path = Path(__file__).parent.parent.parent.parent / "docs" / "sizingstock-20250919.csv"

        self.products = []
        self._load_csv()

    def _load_csv(self) -> None:
        """Load sizing stock products from CSV file"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Sizing stock CSV not found: {self.csv_path}")

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.products = list(reader)

        print(f"✅ Loaded {len(self.products)} sizing stock products from CSV")

    def find_sku(self, shape: str, quality: str, width: str, thickness: str = None, length: str = None) -> Optional[Dict[str, Any]]:
        """
        Find sizing stock SKU based on customer specifications

        Args:
            shape: Metal shape (e.g., "Flat", "Half Round")
            quality: Metal quality (e.g., "14K Yellow")
            width: Width specification (e.g., "6.5 Mm")
            thickness: Thickness specification (optional)
            length: Length specification (optional, defaults to "Bulk")

        Returns:
            Product dict with SKU and pricing info, or None if not found
        """
        for product in self.products:
            # Check descriptive elements for match
            elements = self._extract_descriptive_elements(product)

            if (elements.get("Metal Shape", "").lower() == shape.lower() and
                elements.get("Quality", "").lower() == quality.lower() and
                elements.get("Width", "").lower() == width.lower()):

                # Optional thickness check
                if thickness and elements.get("Thickness", "").lower() != thickness.lower():
                    continue

                # Optional length check (default to Bulk if not specified)
                target_length = length or "Bulk"
                if elements.get("Length", "").lower() != target_length.lower():
                    continue

                return product

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
            elements = self._extract_descriptive_elements(product)

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