import os
from decimal import Decimal
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class BanglerConfig:
    """Centralized configuration for bangler system"""

    # Stuller API Configuration
    STULLER_USERNAME = os.getenv('STULLER_USERNAME')
    STULLER_PASSWORD = os.getenv('STULLER_PASSWORD')
    STULLER_BASE_URL = os.getenv('STULLER_BASE_URL', 'https://api.stuller.com/v2')
    STULLER_TIMEOUT = int(os.getenv('STULLER_TIMEOUT', '30'))

    # Pricing Configuration
    PRICING = {
        'base_price': Decimal('475.00'),        # Current flat rate
        'markup_percentage': None,              # Future feature
        'shop_overhead': None,                  # Future feature
        'labor_rate': None,                     # Future feature
        'tax_rate': None                        # Future feature
    }

    # Material Calculation Configuration (from bangle_math.md)
    MATERIAL_CALC = {
        'k_factor': 0.5,                        # Neutral axis factor (tweakable)
        'seam_allowance_in': 0.04,              # Seam allowance inches (tweakable)
        'mm_per_inch': 25.4,                    # Conversion constant
        'round_up_increment': 0.25              # Round to nearest 0.25 inch (Stuller selling unit)
    }

    # Business Rules
    BUSINESS_RULES = {
        'min_size': 10,
        'max_size': 27,
        'valid_shapes': ['Flat', 'Comfort Fit', 'Low Dome', 'Half Round', 'Square', 'Triangle'],
        'valid_colors': ['Yellow', 'White', 'Rose', 'Green', 'Continuum Sterling Silver', 'Sterling Silver'],
        'valid_qualities': ['10K', '14K', '18K']  # Fixed: uppercase K to match CSV data
    }

    # Logging Configuration
    LOGGING = {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file_path': os.getenv('LOG_FILE_PATH', 'logs/bangler.log')
    }

    @classmethod
    def get_pricing_config(cls) -> Dict[str, Any]:
        """Get current pricing configuration"""
        return cls.PRICING.copy()

    @classmethod
    def get_material_calc_config(cls) -> Dict[str, Any]:
        """Get material calculation configuration"""
        return cls.MATERIAL_CALC.copy()

    @classmethod
    def update_base_price(cls, new_price: Decimal):
        """Update base price (for future admin interface)"""
        cls.PRICING['base_price'] = new_price

    @classmethod
    def has_stuller_credentials(cls) -> bool:
        """Check if Stuller credentials are configured"""
        return bool(cls.STULLER_USERNAME and cls.STULLER_PASSWORD)

    @classmethod
    def validate(cls) -> list:
        """Validate configuration and return list of errors"""
        errors = []

        if not cls.has_stuller_credentials():
            errors.append("Stuller credentials not configured. Set STULLER_USERNAME and STULLER_PASSWORD.")

        if cls.PRICING['base_price'] <= 0:
            errors.append("BASE_PRICE must be greater than 0")

        return errors


# Global configuration instance for backward compatibility
config = BanglerConfig()