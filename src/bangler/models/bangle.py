from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass
class BangleSpec:
    """Customer bangle specifications - all 5 required variables"""
    size: int                    # 10-27
    metal_shape: str            # Flat, Comfort Fit, Low Dome, Half Round, Square, Triangle
    metal_color: str            # Yellow, White, Rose, Green, Sterling Silver
    metal_quality: Optional[str] # 10k, 14k, 18k (None if Sterling Silver)
    width: str                  # 1 Mm, 2 Mm, etc. (from CSV available options)
    thickness: str              # 0.75 Mm, 1 Mm, etc. (from CSV available options)

    def to_quality_string(self) -> str:
        """Convert to Stuller quality format (e.g., '14K Yellow')"""
        if self.metal_color in ["Sterling Silver", "Continuum Sterling Silver"]:
            return self.metal_color

        # Handle CSV format where quality may already include color
        if self.metal_quality and self.metal_color.lower() in self.metal_quality.lower():
            return self.metal_quality  # Quality already includes color (e.g., "24K Yellow")
        elif self.metal_quality:
            return f"{self.metal_quality} {self.metal_color}"  # Combine quality + color
        else:
            return self.metal_color  # Fallback to just color

@dataclass
class MaterialCalculation:
    """Results of material length calculation with detailed breakdown"""
    circumference_mm: float      # Converted from size
    circumference_in: float      # Circumference in inches
    thickness_mm: float          # From thickness string
    thickness_in: float          # Thickness in inches
    calculated_length_in: float  # Raw calculated length
    rounded_length_in: float     # Rounded up to nearest inch
    k_factor: float             # Neutral axis factor used
    seam_allowance_in: float    # Seam allowance used

    @property
    def material_needed_display(self) -> str:
        """User-friendly display of material needed"""
        return f"{self.rounded_length_in:.2f} inches"