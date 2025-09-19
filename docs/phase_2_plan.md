# Phase 2 CLI Implementation Plan - Complete Technical Specification

## Overview
Build a complete CLI interface for jewelry salespeople at Askew Jewelers that follows DRY principles for future web interface reuse. All business logic will be modular and reusable. This plan leverages the completed Phase 1 CSV-based discovery system (5,938 products) and implements the complete pricing workflow.

---

## Implementation Foundation

### Current Assets (Phase 1 Complete)
- ✅ **SizingStockLookup** - 5,938 products, 84ms load, instant lookups
- ✅ **StullerClient** - Real-time pricing API with circuit breaker
- ✅ **CSV Auto-detection** - Automatic latest file detection
- ✅ **Size Conversion Data** - `docs/bangle_size.txt` (sizes 10-27 → MM)
- ✅ **Material Math Formula** - `docs/bangle_math.md` (complete implementation)
- ✅ **CLI UX Specification** - `docs/CLI_steps.md` (questionary-based)

### Business Requirements Recap
- **Product**: Custom handmade bangles (no gems)
- **Current Problem**: Manual/inconsistent pricing
- **Users**: Jewelry salespeople (Phase 2) → customers (Phase 3)
- **Pricing Formula**: Material cost + $475 flat rate (configurable)
- **Real-time Requirement**: Fresh Stuller pricing for each consultation

---

## Ground-Up Implementation Order

### 1. Data Models (`src/bangler/models/`)

#### **File: `bangle.py`**
Core data structures for bangle specifications and business logic.

```python
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
        if self.metal_color == "Sterling Silver":
            return "Sterling Silver"
        return f"{self.metal_quality} {self.metal_color}"

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
```

#### **File: `pricing.py`**
Pricing calculation models and business logic.

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class BanglePrice:
    """Complete pricing breakdown for customer display"""
    sku: str                        # Stuller SKU found
    material_cost_per_dwt: Decimal  # From Stuller API (DWT units)
    material_length_in: float       # Inches needed
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
            "Material Needed": f"{self.material_length_in:.2f} inches"
        }

@dataclass
class PricingError:
    """Structured error information for business-friendly display"""
    error_type: str         # 'sku_not_found', 'api_unavailable', 'invalid_spec'
    user_message: str       # Business-friendly message
    technical_details: str  # For logging
    suggested_action: str   # What user should do next
```

---

### 2. Configuration System Enhancement (`src/bangler/config/`)

#### **Enhanced `settings.py`**
Centralized configuration for pricing rules and math factors.

```python
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
        'round_up_increment': 1.0               # Round to nearest inch
    }

    # Business Rules
    BUSINESS_RULES = {
        'min_size': 10,
        'max_size': 27,
        'valid_shapes': ['Flat', 'Comfort Fit', 'Low Dome', 'Half Round', 'Square', 'Triangle'],
        'valid_colors': ['Yellow', 'White', 'Rose', 'Green', 'Sterling Silver'],
        'valid_qualities': ['10k', '14k', '18k']
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
```

---

### 3. Size Conversion Utilities (`src/bangler/utils/`)

#### **File: `size_conversion.py`**
Size-to-MM conversion using bangle_size.txt data.

```python
from typing import Dict
import os
from pathlib import Path

class SizeConverter:
    """Handles bangle size to MM circumference conversion"""

    def __init__(self):
        self.size_to_mm = self._load_size_data()

    def _load_size_data(self) -> Dict[int, float]:
        """Load size conversion data from bangle_size.txt"""
        # Path relative to project root
        size_file = Path(__file__).parent.parent.parent.parent / "docs" / "bangle_size.txt"

        size_map = {}
        try:
            with open(size_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ' - ' in line:
                        size_str, mm_str = line.split(' - ')
                        size_map[int(size_str)] = float(mm_str)
        except FileNotFoundError:
            raise FileNotFoundError(f"Size conversion file not found: {size_file}")
        except Exception as e:
            raise ValueError(f"Error parsing size conversion file: {e}")

        return size_map

    def size_to_circumference_mm(self, size: int) -> float:
        """Convert bangle size to MM circumference"""
        if size not in self.size_to_mm:
            raise ValueError(f"Invalid size: {size}. Valid sizes: {list(self.size_to_mm.keys())}")
        return self.size_to_mm[size]

    def size_to_circumference_in(self, size: int) -> float:
        """Convert bangle size to inch circumference"""
        mm = self.size_to_circumference_mm(size)
        return mm / 25.4

    def get_valid_sizes(self) -> list[int]:
        """Get list of valid bangle sizes"""
        return sorted(self.size_to_mm.keys())
```

#### **File: `material_calculation.py`**
Implementation of the bangle math formula from bangle_math.md.

```python
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
```

#### **File: `formatting.py`**
Business-friendly error messages and display formatting.

```python
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
```

---

### 4. Business Logic Layer (`src/bangler/core/`)

#### **File: `pricing_engine.py`**
Main pricing workflow orchestration - the heart of the system.

```python
import logging
from decimal import Decimal
from typing import Union, Tuple
from ..models.bangle import BangleSpec, MaterialCalculation
from ..models.pricing import BanglePrice, PricingError
from ..utils.size_conversion import SizeConverter
from ..utils.material_calculation import MaterialCalculator
from ..utils.formatting import BusinessFormatter
from ..api.stuller_client import StullerClient
from .discovery import SizingStockLookup
from ..config.settings import BanglerConfig

logger = logging.getLogger(__name__)

class PricingEngine:
    """Main pricing workflow orchestration"""

    def __init__(self):
        self.size_converter = SizeConverter()
        self.material_calculator = MaterialCalculator()
        self.sizing_stock = SizingStockLookup()
        self.stuller_client = StullerClient()
        self.config = BanglerConfig.get_pricing_config()

    def calculate_bangle_price(self, spec: BangleSpec) -> Union[BanglePrice, PricingError]:
        """
        Complete end-to-end pricing calculation

        Returns either a BanglePrice with full breakdown or PricingError for user display
        """
        try:
            # Step 1: Convert size to circumference
            logger.info(f"Converting size {spec.size} to circumference")
            circumference_mm = self.size_converter.size_to_circumference_mm(spec.size)

            # Step 2: Calculate material length needed
            logger.info(f"Calculating material length for circumference {circumference_mm}mm, thickness {spec.thickness}")
            thickness_mm = self.material_calculator.parse_thickness_string(spec.thickness)
            material_calc = self.material_calculator.calculate_material_length(circumference_mm, thickness_mm)

            # Step 3: Find SKU using existing SizingStockLookup
            logger.info(f"Finding SKU for spec: {spec.metal_shape}, {spec.to_quality_string()}, {spec.width}, {spec.thickness}")
            sku = self.sizing_stock.find_sku(
                shape=spec.metal_shape,
                quality=spec.to_quality_string(),
                width=spec.width,
                thickness=spec.thickness
            )

            if not sku:
                logger.warning(f"No SKU found for specification: {spec}")
                return BusinessFormatter.format_error_for_user(
                    'sku_not_found',
                    f"No SKU found for {spec.metal_shape} {spec.to_quality_string()} {spec.width} {spec.thickness}"
                )

            # Step 4: Get real-time pricing from Stuller
            logger.info(f"Getting real-time price for SKU: {sku}")
            price_data = self.stuller_client.get_sku_price(sku)

            if not price_data or 'Price' not in price_data:
                logger.error(f"Failed to get price for SKU {sku}: {price_data}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"Failed to get price for SKU {sku}"
                )

            # Step 5: Calculate final pricing
            material_cost_per_dwt = Decimal(str(price_data['Price']))
            # Note: DWT conversion logic may need refinement based on Stuller's pricing units
            material_total_cost = material_cost_per_dwt * Decimal(str(material_calc.rounded_length_in))

            base_price = self.config['base_price']
            total_price = material_total_cost + base_price

            logger.info(f"Pricing complete: Material ${material_total_cost}, Base ${base_price}, Total ${total_price}")

            return BanglePrice(
                sku=sku,
                material_cost_per_dwt=material_cost_per_dwt,
                material_length_in=material_calc.rounded_length_in,
                material_total_cost=material_total_cost,
                base_price=base_price,
                total_price=total_price
            )

        except ValueError as e:
            logger.error(f"Validation error in pricing calculation: {e}")
            return BusinessFormatter.format_error_for_user('calculation_error', str(e))
        except Exception as e:
            logger.error(f"Unexpected error in pricing calculation: {e}")
            return BusinessFormatter.format_error_for_user('unknown', str(e))

    def get_available_options_for_shape(self, shape: str) -> dict:
        """Get available widths and thicknesses for a given shape"""
        return self.sizing_stock.get_available_options().get(shape, {})

    def validate_specification(self, spec: BangleSpec) -> Union[bool, PricingError]:
        """Validate bangle specification against business rules"""
        rules = BanglerConfig.BUSINESS_RULES

        # Validate size
        if spec.size < rules['min_size'] or spec.size > rules['max_size']:
            return BusinessFormatter.format_error_for_user(
                'invalid_combination',
                f"Size {spec.size} not in valid range {rules['min_size']}-{rules['max_size']}"
            )

        # Validate shape
        if spec.metal_shape not in rules['valid_shapes']:
            return BusinessFormatter.format_error_for_user(
                'invalid_combination',
                f"Shape {spec.metal_shape} not in valid shapes: {rules['valid_shapes']}"
            )

        # Validate color
        if spec.metal_color not in rules['valid_colors']:
            return BusinessFormatter.format_error_for_user(
                'invalid_combination',
                f"Color {spec.metal_color} not in valid colors: {rules['valid_colors']}"
            )

        # Validate quality (skip if Sterling Silver)
        if spec.metal_color != "Sterling Silver":
            if not spec.metal_quality or spec.metal_quality not in rules['valid_qualities']:
                return BusinessFormatter.format_error_for_user(
                    'invalid_combination',
                    f"Quality {spec.metal_quality} not in valid qualities: {rules['valid_qualities']}"
                )

        return True
```

#### **File: `validation.py`**
Input validation and business rules enforcement.

```python
from typing import List, Union
from ..models.bangle import BangleSpec
from ..models.pricing import PricingError
from ..utils.formatting import BusinessFormatter
from ..config.settings import BanglerConfig

class BangleValidator:
    """Input validation and business rules enforcement"""

    def __init__(self):
        self.rules = BanglerConfig.BUSINESS_RULES

    def validate_size(self, size: int) -> Union[bool, str]:
        """Validate bangle size"""
        if not isinstance(size, int):
            return "Size must be a number"
        if size < self.rules['min_size'] or size > self.rules['max_size']:
            return f"Size must be between {self.rules['min_size']} and {self.rules['max_size']}"
        return True

    def validate_shape(self, shape: str) -> Union[bool, str]:
        """Validate metal shape"""
        if shape not in self.rules['valid_shapes']:
            return f"Shape must be one of: {', '.join(self.rules['valid_shapes'])}"
        return True

    def validate_color(self, color: str) -> Union[bool, str]:
        """Validate metal color"""
        if color not in self.rules['valid_colors']:
            return f"Color must be one of: {', '.join(self.rules['valid_colors'])}"
        return True

    def validate_quality(self, quality: str, color: str) -> Union[bool, str]:
        """Validate metal quality (context-dependent on color)"""
        if color == "Sterling Silver":
            if quality is not None:
                return "Quality should not be specified for Sterling Silver"
            return True

        if not quality:
            return "Quality is required for non-Sterling Silver metals"
        if quality not in self.rules['valid_qualities']:
            return f"Quality must be one of: {', '.join(self.rules['valid_qualities'])}"
        return True

    def validate_complete_spec(self, spec: BangleSpec) -> Union[bool, List[str]]:
        """Validate complete bangle specification"""
        errors = []

        size_result = self.validate_size(spec.size)
        if size_result is not True:
            errors.append(size_result)

        shape_result = self.validate_shape(spec.metal_shape)
        if shape_result is not True:
            errors.append(shape_result)

        color_result = self.validate_color(spec.metal_color)
        if color_result is not True:
            errors.append(color_result)

        quality_result = self.validate_quality(spec.metal_quality, spec.metal_color)
        if quality_result is not True:
            errors.append(quality_result)

        return True if not errors else errors
```

---

### 5. CLI Interface (`src/bangler/cli/`)

#### **File: `prompts.py`**
Questionary-based guided prompts following CLI_steps.md.

```python
import questionary
from typing import Optional, Dict, Any
from ..models.bangle import BangleSpec
from ..core.discovery import SizingStockLookup
from ..config.settings import BanglerConfig

class BanglePrompter:
    """Guided prompts for bangle specification collection"""

    def __init__(self):
        self.sizing_stock = SizingStockLookup()
        self.rules = BanglerConfig.BUSINESS_RULES

    def prompt_size(self) -> int:
        """Step 1: Size selection (10-27)"""
        size_choices = [str(i) for i in range(self.rules['min_size'], self.rules['max_size'] + 1)]

        size_str = questionary.select(
            "Select bangle size:",
            choices=size_choices,
            instruction="(Size determines the inside diameter of the bangle)"
        ).ask()

        return int(size_str)

    def prompt_metal_shape(self) -> str:
        """Step 2: Metal Shape selection"""
        return questionary.select(
            "Select metal shape:",
            choices=self.rules['valid_shapes'],
            instruction="(Shape affects available width and thickness options)"
        ).ask()

    def prompt_metal_color(self) -> str:
        """Step 3: Metal Color selection"""
        return questionary.select(
            "Select metal color:",
            choices=self.rules['valid_colors'],
            instruction="(Sterling Silver skips quality selection)"
        ).ask()

    def prompt_metal_quality(self, color: str) -> Optional[str]:
        """Step 4: Metal Quality selection (skipped if Sterling Silver)"""
        if color == "Sterling Silver":
            return None

        return questionary.select(
            f"Select {color} gold quality:",
            choices=self.rules['valid_qualities'],
            instruction="(Higher karat = more gold content = higher cost)"
        ).ask()

    def prompt_width(self, shape: str, quality_string: str) -> str:
        """Step 5: Width selection (filtered by shape)"""
        available_options = self.sizing_stock.get_available_options()

        if shape not in available_options:
            raise ValueError(f"No options available for shape: {shape}")

        # Get unique widths for this shape
        shape_data = available_options[shape]
        available_widths = set()

        for quality_data in shape_data.values():
            if quality_string in quality_data:
                available_widths.update(quality_data[quality_string].keys())

        if not available_widths:
            raise ValueError(f"No widths available for {shape} {quality_string}")

        width_choices = sorted(available_widths, key=lambda x: float(x.replace(' Mm', '')))

        return questionary.select(
            f"Select width for {shape} {quality_string}:",
            choices=width_choices,
            instruction="(Width affects the bangle's appearance and material cost)"
        ).ask()

    def prompt_thickness(self, shape: str, quality_string: str, width: str) -> str:
        """Step 6: Thickness selection (filtered by shape and width)"""
        available_options = self.sizing_stock.get_available_options()

        # Navigate to thickness options
        try:
            thickness_options = available_options[shape][quality_string][width]
        except KeyError:
            raise ValueError(f"No thickness options for {shape} {quality_string} {width}")

        thickness_choices = sorted(thickness_options, key=lambda x: float(x.replace(' Mm', '')))

        return questionary.select(
            f"Select thickness for {shape} {quality_string} {width}:",
            choices=thickness_choices,
            instruction="(Thickness affects strength and material needed)"
        ).ask()

    def collect_complete_specification(self) -> BangleSpec:
        """Complete guided workflow to collect all bangle specifications"""
        print("\n=== Bangle Pricing Calculator ===")
        print("Let's gather the specifications for your custom bangle.\n")

        # Step 1: Size
        size = self.prompt_size()
        print(f"✓ Size: {size}")

        # Step 2: Metal Shape
        metal_shape = self.prompt_metal_shape()
        print(f"✓ Shape: {metal_shape}")

        # Step 3: Metal Color
        metal_color = self.prompt_metal_color()
        print(f"✓ Color: {metal_color}")

        # Step 4: Metal Quality (conditional)
        metal_quality = self.prompt_metal_quality(metal_color)
        if metal_quality:
            print(f"✓ Quality: {metal_quality}")
        else:
            print("✓ Quality: Sterling Silver (no karat selection needed)")

        # Create quality string for lookup
        quality_string = f"{metal_quality} {metal_color}" if metal_quality else metal_color

        # Step 5: Width (filtered by shape)
        try:
            width = self.prompt_width(metal_shape, quality_string)
            print(f"✓ Width: {width}")
        except ValueError as e:
            print(f"Error: {e}")
            print("Please try a different shape or quality combination.")
            return None

        # Step 6: Thickness (filtered by shape and width)
        try:
            thickness = self.prompt_thickness(metal_shape, quality_string, width)
            print(f"✓ Thickness: {thickness}")
        except ValueError as e:
            print(f"Error: {e}")
            print("Please try a different width.")
            return None

        # Create and return complete specification
        spec = BangleSpec(
            size=size,
            metal_shape=metal_shape,
            metal_color=metal_color,
            metal_quality=metal_quality,
            width=width,
            thickness=thickness
        )

        print("\n=== Specification Complete ===")
        print(f"Size: {spec.size}")
        print(f"Metal: {spec.to_quality_string()}")
        print(f"Shape: {spec.metal_shape}")
        print(f"Dimensions: {spec.width} x {spec.thickness}")
        print("=" * 30)

        return spec
```

#### **File: `display.py`**
Price breakdown and result formatting for terminal display.

```python
import sys
from typing import Union
from ..models.bangle import BangleSpec
from ..models.pricing import BanglePrice, PricingError
from ..utils.formatting import BusinessFormatter

class CLIDisplay:
    """Terminal display formatting for CLI interface"""

    @staticmethod
    def show_welcome():
        """Display welcome message"""
        print("""
╔════════════════════════════════════════╗
║        Askew Jewelers Bangler          ║
║     Custom Bangle Pricing System       ║
╚════════════════════════════════════════╝

Real-time pricing based on current Stuller material costs.
""")

    @staticmethod
    def show_calculating():
        """Show calculation in progress"""
        print("\n🔄 Calculating pricing...")
        print("   • Converting size to circumference")
        print("   • Calculating material length needed")
        print("   • Finding Stuller SKU")
        print("   • Getting real-time pricing")
        print("   • Applying pricing formula")

    @staticmethod
    def show_price_result(result: Union[BanglePrice, PricingError]):
        """Display pricing result or error"""
        if isinstance(result, PricingError):
            CLIDisplay._show_error(result)
        else:
            CLIDisplay._show_success(result)

    @staticmethod
    def _show_success(price: BanglePrice):
        """Display successful pricing calculation"""
        breakdown = price.get_breakdown_display()

        print("\n✅ Pricing Calculation Complete!")
        print(BusinessFormatter.format_price_breakdown(breakdown))

        print(f"\n📋 Details:")
        print(f"   Stuller SKU: {price.sku}")
        print(f"   Material Cost per DWT: ${price.material_cost_per_dwt:.2f}")
        print(f"   Material Length Needed: {price.material_length_in:.2f} inches")

        # Highlight the final price
        print(f"\n💰 FINAL CUSTOMER PRICE: ${price.total_price:.2f}")
        print("=" * 50)

    @staticmethod
    def _show_error(error: PricingError):
        """Display error message with suggested action"""
        print(f"\n❌ {error.user_message}")
        print(f"\n💡 Suggested Action: {error.suggested_action}")

        if error.error_type == 'sku_not_found':
            print("\n🔍 Available alternatives:")
            print("   • Try a different width or thickness")
            print("   • Check with suppliers for special orders")
            print("   • Consider similar metal shapes")
        elif error.error_type == 'api_unavailable':
            print("\n🔄 Backup options:")
            print("   • Wait 5 minutes and try again")
            print("   • Use manual pricing methods")
            print("   • Contact technical support")

    @staticmethod
    def show_specification_summary(spec: BangleSpec):
        """Display customer specification summary"""
        print(f"\n📋 Customer Specification:")
        print(f"   Size: {spec.size}")
        print(f"   Metal: {spec.to_quality_string()}")
        print(f"   Shape: {spec.metal_shape}")
        print(f"   Dimensions: {spec.width} × {spec.thickness}")

    @staticmethod
    def prompt_continue() -> bool:
        """Ask if user wants to calculate another price"""
        response = input("\nWould you like to price another bangle? (y/n): ").lower().strip()
        return response in ['y', 'yes', '1', 'true']

    @staticmethod
    def show_goodbye():
        """Display goodbye message"""
        print("""
Thank you for using the Askew Jewelers Bangler!

For technical support or questions:
📧 Contact: support@askewjewelers.com
📞 Phone: [Business Phone Number]

Have a great day! 💍
""")
```

#### **File: `interface.py`**
Main CLI orchestration bringing everything together.

```python
#!/usr/bin/env python3
"""
Askew Jewelers Bangler CLI Interface

Main command-line interface for custom bangle pricing.
"""

import sys
import logging
from typing import Optional
from .prompts import BanglePrompter
from .display import CLIDisplay
from ..core.pricing_engine import PricingEngine
from ..core.validation import BangleValidator
from ..models.bangle import BangleSpec
from ..config.settings import BanglerConfig

# Configure logging
logging.basicConfig(
    level=getattr(logging, BanglerConfig.LOGGING['level']),
    format=BanglerConfig.LOGGING['format'],
    handlers=[
        logging.FileHandler(BanglerConfig.LOGGING['file_path']),
        logging.StreamHandler(sys.stdout)
    ]
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
                spec = self._collect_specification()
                if not spec:
                    continue

                # Validate specification
                if not self._validate_specification(spec):
                    continue

                # Calculate pricing
                self._calculate_and_display_pricing(spec)

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

    def _collect_specification(self) -> Optional[BangleSpec]:
        """Collect customer specification via guided prompts"""
        try:
            return self.prompter.collect_complete_specification()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error collecting specification: {e}")
            print(f"\n❌ Error collecting specification: {e}")
            return None

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

    def _calculate_and_display_pricing(self, spec: BangleSpec):
        """Calculate pricing and display results"""
        self.display.show_specification_summary(spec)
        self.display.show_calculating()

        logger.info(f"Calculating pricing for specification: {spec}")

        # Calculate pricing
        result = self.pricing_engine.calculate_bangle_price(spec)

        # Display result
        self.display.show_price_result(result)

def main():
    """CLI entry point"""
    cli = BanglerCLI()
    cli.run()

if __name__ == "__main__":
    main()
```

---

### 6. Entry Point Configuration

#### **File: `src/bangler/cli/main.py`**
Simple entry point for the CLI application.

```python
#!/usr/bin/env python3
"""
Bangler CLI Entry Point

Simple entry point that delegates to the main CLI interface.
"""

from .interface import main

if __name__ == "__main__":
    main()
```

#### **Update `pyproject.toml`**
Add questionary dependency and CLI script entry.

```toml
[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.31.0"
python-dotenv = "^1.0.0"
questionary = "^2.0.1"  # NEW: Beautiful CLI prompts

[tool.poetry.scripts]
bangler = "bangler.cli.main:main"  # NEW: CLI entry point
```

---

## Implementation Strategy

### Development Phases
1. **Data Models** → **Configuration** → **Utilities** (Foundation)
2. **Business Logic** → **Validation** (Core functionality)
3. **CLI Interface** → **Display** → **Integration** (User experience)
4. **Testing** → **Documentation** → **Polish** (Production ready)

### Testing Strategy
- **Unit Tests**: Each utility and business logic component
- **Integration Tests**: End-to-end pricing workflow
- **Manual Testing**: CLI user experience with sales staff
- **Error Testing**: All error scenarios and edge cases

### Error Handling Philosophy
- **User-Facing**: Business-friendly messages with clear next steps
- **Technical**: Detailed logging for debugging and monitoring
- **Graceful Degradation**: Fallback to manual methods when systems unavailable
- **Validation**: Early input validation to prevent downstream errors

---

## Integration with Existing Systems

### Leveraging Phase 1 Assets
- **SizingStockLookup**: Direct usage for SKU discovery and option filtering
- **StullerClient**: Use existing `get_sku_price()` method for real-time pricing
- **CSV Auto-detection**: Benefit from automatic latest file detection
- **Configuration**: Extend existing settings.py for pricing rules

### Data Flow Architecture
```
Customer Input → BangleSpec → Validation → Pricing Engine
                                              ↓
Size Conversion → Material Calculation → SKU Lookup → Stuller API
                                              ↓
                                       BanglePrice → Display
```

### Future Web Interface Compatibility
- **Shared Models**: BangleSpec, BanglePrice work for both CLI and web
- **Shared Business Logic**: PricingEngine, MaterialCalculator reusable
- **Shared Configuration**: Same pricing rules and math factors
- **API-Ready**: Business logic easily exposed via REST endpoints

---

## Configuration and Deployment

### Environment Variables
```bash
# Stuller API (existing)
STULLER_USERNAME=AskewDev
STULLER_PASSWORD=[existing]
STULLER_BASE_URL=https://api.stuller.com/v2
STULLER_TIMEOUT=30

# Application Configuration (new)
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/bangler.log
```

### File Structure (Complete)
```
src/bangler/
├── models/
│   ├── __init__.py
│   ├── bangle.py              # BangleSpec, MaterialCalculation
│   └── pricing.py             # BanglePrice, PricingError
├── config/
│   ├── __init__.py
│   └── settings.py            # Enhanced with pricing/math config
├── utils/
│   ├── __init__.py
│   ├── size_conversion.py     # SizeConverter
│   ├── material_calculation.py # MaterialCalculator
│   └── formatting.py          # BusinessFormatter
├── core/
│   ├── __init__.py
│   ├── discovery.py           # Existing SizingStockLookup
│   ├── pricing_engine.py      # Main workflow orchestration
│   └── validation.py          # BangleValidator
├── api/
│   ├── __init__.py
│   └── stuller_client.py      # Existing StullerClient
├── cli/
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── interface.py          # Main CLI orchestration
│   ├── prompts.py           # Questionary-based prompts
│   └── display.py           # Terminal display formatting
└── data/
    ├── .gitignore           # Existing
    ├── README.md            # Existing
    └── sizingstock-*.csv    # Existing auto-detected files
```

---

## Success Metrics and Validation

### Performance Targets
- **End-to-End Pricing**: < 2 seconds from spec collection to price display
- **SKU Lookup**: < 100ms (already achieved in Phase 1)
- **API Response**: < 3 seconds for real-time Stuller pricing
- **User Experience**: Intuitive prompts, clear error messages

### Business Validation
- **Sales Staff Testing**: Validate with actual jewelry salespeople
- **Pricing Accuracy**: Verify material calculations against manual methods
- **Error Scenarios**: Test all failure modes and recovery paths
- **Real-World Usage**: Deploy for actual customer consultations

### Technical Validation
- **Code Quality**: Type hints, documentation, clean architecture
- **Error Coverage**: All error scenarios handled gracefully
- **Logging**: Complete audit trail for troubleshooting
- **Maintainability**: Clear separation of concerns, modular design

---

## Future Enhancements (Phase 3 Ready)

### Web Interface Preparation
- **REST API**: Expose PricingEngine via web endpoints
- **Database Migration**: Replace CSV with PostgreSQL if needed
- **User Management**: Admin interface for pricing configuration
- **Mobile Responsive**: Customer-facing interface

### Advanced Features
- **Batch Pricing**: Multiple bangle calculations
- **Historical Pricing**: Track price trends over time
- **Inventory Integration**: Connect with shop inventory systems
- **Customer Profiles**: Save customer preferences and history

### Business Intelligence
- **Pricing Analytics**: Track most popular combinations
- **Cost Analysis**: Monitor material cost trends
- **Performance Metrics**: Usage statistics and performance monitoring
- **Business Reporting**: Sales insights and profitability analysis

---

This comprehensive Phase 2 plan provides complete technical specification for building a production-ready CLI interface that serves as the foundation for future web development. Every component is designed with modularity, maintainability, and business requirements in mind.