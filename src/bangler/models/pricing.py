from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class BanglePrice:
    """Complete pricing breakdown for customer display"""
    sku: str                        # Stuller SKU found
    material_cost_per_dwt: Decimal  # From Stuller API (DWT units)
    material_length_in: float       # Inches needed
    material_weight_dwt: Decimal    # Calculated weight needed (DWT)
    material_total_cost: Decimal    # Calculated material cost
    base_price: Decimal             # Configurable base ($475)
    total_price: Decimal            # Final customer price

    # Optional breakdown fields
    markup_percentage: Optional[float] = None
    labor_cost: Optional[Decimal] = None
    overhead_cost: Optional[Decimal] = None

    def get_breakdown_display(self) -> dict:
        """Return user-friendly pricing breakdown"""
        return {
            "Material Cost": f"${self.material_total_cost:.2f}",
            "Base Price": f"${self.base_price:.2f}",
            "Total Price": f"${self.total_price:.2f}",
            "SKU": self.sku,
            "Material Needed": f"{self.material_length_in:.2f} inches",
            "Material Weight": f"{self.material_weight_dwt:.4f} DWT",
            "Price per DWT": f"${self.material_cost_per_dwt:.2f}"
        }

@dataclass
class PricingError:
    """Structured error information for business-friendly display"""
    error_type: str         # 'sku_not_found', 'api_unavailable', 'invalid_spec'
    user_message: str       # Business-friendly message
    technical_details: str  # For logging
    suggested_action: str   # What user should do next