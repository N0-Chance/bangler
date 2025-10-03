#!/usr/bin/env python3
"""
Askew Jewelers Bangler CLI Interface

Main command-line interface for custom bangle pricing.
"""

import sys
import logging
from decimal import Decimal
from typing import Optional
from .prompts import BanglePrompter
from .display import CLIDisplay
from ..core.pricing_engine import PricingEngine
from ..core.validation import BangleValidator
from ..models.bangle import BangleSpec
from ..models.pricing import BanglePrice
from ..config.settings import BanglerConfig

# Configure logging: Only log to file for INFO, console only for WARNING/ERROR
file_handler = logging.FileHandler(BanglerConfig.LOGGING['file_path'])
file_handler.setLevel(getattr(logging, BanglerConfig.LOGGING['level']))
file_handler.setFormatter(logging.Formatter(BanglerConfig.LOGGING['format']))

console_handler = logging.StreamHandler(sys.stderr)  # Use stderr to avoid mixing with user interface
console_handler.setLevel(logging.WARNING)  # Only show warnings and errors on console
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

logging.basicConfig(
    level=getattr(logging, BanglerConfig.LOGGING['level']),
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

class BanglerCLI:
    """Main CLI application class"""

    def __init__(self):
        self.prompter = BanglePrompter()
        self.display = CLIDisplay()
        self.pricing_engine = PricingEngine()
        self.validator = BangleValidator()

    def run(self):
        """Main CLI execution loop"""
        self.display.show_welcome()

        try:
            while True:
                # Collect specification
                spec, custom_base_price = self._collect_specification()
                if not spec:
                    continue

                # Validate specification
                if not self._validate_specification(spec):
                    continue

                # Calculate pricing
                self._calculate_and_display_pricing(spec, custom_base_price)

                # Ask to continue
                if not self.display.prompt_continue():
                    break

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
        except Exception as e:
            logger.error(f"Unexpected error in CLI: {e}")
            print(f"\n❌ An unexpected error occurred: {e}")
            print("Please contact technical support.")
        finally:
            self.display.show_goodbye()

    def _collect_specification(self) -> tuple[Optional[BangleSpec], Optional[Decimal]]:
        """Collect customer specification via guided prompts"""
        try:
            return self.prompter.collect_complete_specification()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error collecting specification: {e}")
            print(f"\n❌ Error collecting specification: {e}")
            return (None, None)

    def _validate_specification(self, spec: BangleSpec) -> bool:
        """Validate specification and show errors if any"""
        validation_result = self.validator.validate_complete_spec(spec)

        if validation_result is True:
            return True

        print("\n❌ Specification Errors:")
        for error in validation_result:
            print(f"   • {error}")
        print("\nPlease try again with valid selections.")
        return False

    def _calculate_and_display_pricing(self, spec: BangleSpec, custom_base_price: Optional[Decimal] = None):
        """Calculate pricing and display results"""
        self.display.show_specification_summary(spec, custom_base_price)
        self.display.show_calculating()

        logger.info(f"Calculating pricing for specification: {spec}")

        # Calculate pricing with progress display
        result = self.pricing_engine.calculate_bangle_price_with_progress(spec, self.display, custom_base_price)

        # Display result
        self.display.show_price_result(result)

        # Ask to open SKU page if pricing was successful
        if isinstance(result, BanglePrice):  # Not PricingError
            if self.display.prompt_open_sku_page(result.sku):
                self.display.open_stuller_sku_page(result.sku)

def main():
    """CLI entry point"""
    cli = BanglerCLI()
    cli.run()

if __name__ == "__main__":
    main()