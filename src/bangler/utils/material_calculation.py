import math
from typing import Dict, Any
from ..models.bangle import MaterialCalculation
from ..config.settings import BanglerConfig

class MaterialCalculator:
    """Calculates material length needed for bangle production"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or BanglerConfig.get_material_calc_config()

    def calculate_material_length(self, circumference_mm: float, thickness_mm: float) -> MaterialCalculation:
        """
        Calculate required strip length using the formula from bangle_math.md

        Formula: L = π × (ID_in + 2 × k_factor × thickness_in) + seam_allow_in
        """
        # Convert to inches
        circumference_in = circumference_mm / self.config['mm_per_inch']
        thickness_in = thickness_mm / self.config['mm_per_inch']

        # Calculate diameter from circumference (ID_in)
        id_in = circumference_in / math.pi

        # Apply bangle math formula
        k_factor = self.config['k_factor']
        seam_allowance = self.config['seam_allowance_in']

        calculated_length = math.pi * (id_in + 2 * k_factor * thickness_in)
        total_length = calculated_length + seam_allowance

        # Round up to nearest inch (Stuller selling unit)
        rounded_length = math.ceil(total_length / self.config['round_up_increment']) * self.config['round_up_increment']

        return MaterialCalculation(
            circumference_mm=circumference_mm,
            circumference_in=circumference_in,
            thickness_mm=thickness_mm,
            thickness_in=thickness_in,
            calculated_length_in=calculated_length,
            rounded_length_in=rounded_length,
            k_factor=k_factor,
            seam_allowance_in=seam_allowance
        )

    def parse_thickness_string(self, thickness_str: str) -> float:
        """Parse thickness string like '1.5 Mm' to float 1.5"""
        try:
            # Remove 'Mm' and any whitespace, convert to float
            return float(thickness_str.replace('Mm', '').strip())
        except ValueError:
            raise ValueError(f"Invalid thickness format: {thickness_str}")