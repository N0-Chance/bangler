from typing import Dict, Any
from ..models.pricing import PricingError

class BusinessFormatter:
    """Formats technical information for business-friendly display"""

    @staticmethod
    def format_error_for_user(error_type: str, technical_details: str = "") -> PricingError:
        """Convert technical errors to business-friendly messages"""

        error_mapping = {
            'sku_not_found': PricingError(
                error_type='sku_not_found',
                user_message="We couldn't find that exact combination in our current inventory. Please try a different width or thickness, or check with our suppliers.",
                technical_details=technical_details,
                suggested_action="Try different dimensions or contact supplier"
            ),
            'api_unavailable': PricingError(
                error_type='api_unavailable',
                user_message="Our pricing system is temporarily unavailable. Please use manual pricing methods or try again in a few minutes.",
                technical_details=technical_details,
                suggested_action="Retry in 5 minutes or use backup pricing"
            ),
            'invalid_combination': PricingError(
                error_type='invalid_combination',
                user_message="That combination of metal shape and dimensions isn't available. Please select from the available options.",
                technical_details=technical_details,
                suggested_action="Choose from filtered available options"
            ),
            'calculation_error': PricingError(
                error_type='calculation_error',
                user_message="There was an error calculating the material needed. Please double-check the size and try again.",
                technical_details=technical_details,
                suggested_action="Verify size input and retry"
            )
        }

        return error_mapping.get(error_type, PricingError(
            error_type='unknown',
            user_message="An unexpected error occurred. Please contact technical support.",
            technical_details=technical_details,
            suggested_action="Contact technical support"
        ))

    @staticmethod
    def format_price_breakdown(price_breakdown: Dict[str, str]) -> str:
        """Format pricing breakdown for terminal display"""
        lines = ["", "=== PRICING BREAKDOWN ==="]
        for key, value in price_breakdown.items():
            lines.append(f"{key:<15}: {value}")
        lines.append("=" * 25)
        return "\n".join(lines)

    @staticmethod
    def format_material_details(material_calc: 'MaterialCalculation') -> str:
        """Format material calculation details"""
        return f"""
=== MATERIAL CALCULATION ===
Circumference: {material_calc.circumference_in:.3f} inches
Thickness: {material_calc.thickness_in:.3f} inches
Calculated Length: {material_calc.calculated_length_in:.3f} inches
Seam Allowance: {material_calc.seam_allowance_in:.3f} inches
Final Length Needed: {material_calc.rounded_length_in:.2f} inches
============================
"""