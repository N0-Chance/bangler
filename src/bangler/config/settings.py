"""
Configuration management for Bangler project
Handles environment variables and application settings
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BanglerConfig:
    """Configuration settings for Bangler application"""

    def __init__(self):
        # Stuller API Configuration
        self.stuller_username = os.getenv("STULLER_USERNAME")
        self.stuller_password = os.getenv("STULLER_PASSWORD")
        self.stuller_api_url = os.getenv("STULLER_API_URL", "https://api.stuller.com/v2")

        # Business Configuration
        self.base_price = float(os.getenv("BASE_PRICE", "475.00"))
        self.markup_percentage = self._get_optional_float("MARKUP_PERCENTAGE")
        self.shop_overhead = self._get_optional_float("SHOP_OVERHEAD")

        # Application Configuration
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def _get_optional_float(self, key: str) -> Optional[float]:
        """Get optional float value from environment"""
        value = os.getenv(key)
        if value:
            try:
                return float(value)
            except ValueError:
                return None
        return None

    @property
    def has_stuller_credentials(self) -> bool:
        """Check if Stuller credentials are configured"""
        return bool(self.stuller_username and self.stuller_password)

    def validate(self) -> list:
        """Validate configuration and return list of errors"""
        errors = []

        if not self.has_stuller_credentials:
            errors.append("Stuller credentials not configured. Set STULLER_USERNAME and STULLER_PASSWORD.")

        if self.base_price <= 0:
            errors.append("BASE_PRICE must be greater than 0")

        return errors


# Global configuration instance
config = BanglerConfig()