import logging
from decimal import Decimal
from typing import Union, Tuple
from ..models.bangle import BangleSpec, MaterialCalculation
from ..models.pricing import BanglePrice, PricingError
from ..utils.size_conversion import SizeConverter
from ..utils.material_calculation import MaterialCalculator
from ..utils.material_density import MaterialDensity
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
        self.material_density = MaterialDensity()
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
            api_response = self.stuller_client.get_sku_price(sku)

            # Check if API call succeeded - FIXED: correct logical check
            if not api_response or api_response.get('success') != True:
                logger.error(f"Failed to get price for SKU {sku}: {api_response}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"Failed to get price for SKU {sku}"
                )

            # Extract product data from successful response
            products = api_response.get('products', [])
            if not products:
                logger.error(f"No products returned for SKU {sku}: {api_response}")
                return BusinessFormatter.format_error_for_user(
                    'sku_not_found',
                    f"SKU {sku} not found in Stuller catalog"
                )

            product = products[0]  # Get first (should be only) product

            # Extract price and weight data from API response
            price_obj = product.get('Price')
            weight = product.get('Weight')
            weight_unit = product.get('WeightUnitOfMeasure')
            unit_of_sale = product.get('UnitOfSale')

            if not price_obj:
                logger.error(f"No price data in product for SKU {sku}: {product}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"No price available for SKU {sku}"
                )

            # Handle both old and new price formats
            if isinstance(price_obj, dict):
                # New format: {'Value': 87.08678, 'CurrencyCode': 'USD'}
                price_value = price_obj.get('Value')
            else:
                # Old format: '87.086780000000000' or 87.08678
                price_value = price_obj

            if price_value is None:
                logger.error(f"Invalid price format for SKU {sku}: {price_obj}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"Invalid price format for SKU {sku}"
                )

            # Step 5: Calculate final pricing using weight-based calculation
            material_cost_per_dwt = Decimal(str(price_value))

            # Calculate material weight needed based on dimensions and length
            material_weight_dwt = self._calculate_material_weight_dwt(
                material_calc, spec, weight, weight_unit, unit_of_sale
            )

            material_total_cost = material_cost_per_dwt * material_weight_dwt

            base_price = self.config['base_price']
            total_price = material_total_cost + base_price

            logger.info(f"Pricing complete: Material ${material_total_cost}, Base ${base_price}, Total ${total_price}")

            return BanglePrice(
                sku=sku,
                material_cost_per_dwt=material_cost_per_dwt,
                material_length_in=material_calc.rounded_length_in,
                material_weight_dwt=material_weight_dwt,
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

    def _calculate_material_weight_dwt(self, material_calc: MaterialCalculation, spec: BangleSpec,
                                       api_weight: float, weight_unit: str, unit_of_sale: str) -> Decimal:
        """
        Calculate the weight in DWT needed using proper material science

        This method uses karat-specific material densities to calculate accurate weights,
        replacing the flawed reference-based approach that caused pricing errors.

        Args:
            material_calc: Material calculation with length needed
            spec: Bangle specification with dimensions
            api_weight: Weight from API response (not used - always normalized to 1.0)
            weight_unit: Weight unit from API (should be 'DWT')
            unit_of_sale: Unit of sale from API (should be 'DWT')

        Returns:
            Weight in DWT needed for the calculated length
        """
        # Get material dimensions
        width_mm = float(spec.width.replace(' Mm', '').strip())
        thickness_mm = float(spec.thickness.replace(' Mm', '').strip())
        length_inches = material_calc.rounded_length_in

        # Use proper material science calculation
        calculation = self.material_density.calculate_theoretical_weight(
            width_mm=width_mm,
            thickness_mm=thickness_mm,
            length_inches=length_inches,
            quality=spec.metal_quality or spec.metal_color,
            color=spec.metal_color
        )

        # Comprehensive logging for verification and debugging
        logger.info(f"=== MATERIAL WEIGHT CALCULATION ===")
        logger.info(f"Dimensions: {width_mm}mm × {thickness_mm}mm × {length_inches}in")
        logger.info(f"Quality: {spec.metal_quality or spec.metal_color} {spec.metal_color}")
        logger.info(f"Density used: {calculation['density_g_per_cm3']:.3f} g/cm³")
        logger.info(f"Volume per inch: {calculation['volume_cm3_per_in']:.6f} cm³/in")
        logger.info(f"Weight per inch: {calculation['dwt_per_in']:.6f} DWT/in")
        logger.info(f"Total weight: {calculation['total_weight_dwt']:.6f} DWT")
        logger.info(f"==================================")

        return Decimal(str(calculation['total_weight_dwt']))

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

        # Quality validation removed - now using dynamic options from CSV data
        # If user selects invalid quality, the SKU lookup will fail gracefully

        return True

    def calculate_bangle_price_with_progress(self, spec: BangleSpec, display=None):
        """
        Complete end-to-end pricing calculation with progress display

        Returns either a BanglePrice with full breakdown or PricingError for user display
        """
        try:
            # Step 1: Convert size to circumference
            logger.info(f"Converting size {spec.size} to circumference")
            if display:
                display.show_progress_step("Converting size to circumference", f"Size {spec.size}", thinking_time=0.06)
            circumference_mm = self.size_converter.size_to_circumference_mm(spec.size)
            if display:
                display.show_progress_step("Circumference", f"{circumference_mm:.2f}mm", thinking_time=0.05)

            # Step 2: Calculate material length needed
            logger.info(f"Calculating material length for circumference {circumference_mm}mm, thickness {spec.thickness}")
            if display:
                display.show_progress_step("Calculating material length needed", thinking_time=0.06)
            thickness_mm = self.material_calculator.parse_thickness_string(spec.thickness)
            material_calc = self.material_calculator.calculate_material_length(circumference_mm, thickness_mm)
            if display:
                display.show_progress_step("Material length needed", f"{material_calc.rounded_length_in:.2f} inches", thinking_time=0.05)

            # Step 3: Find SKU using existing SizingStockLookup
            logger.info(f"Finding SKU for spec: {spec.metal_shape}, {spec.to_quality_string()}, {spec.width}, {spec.thickness}")
            if display:
                display.show_progress_step("Finding Stuller SKU", thinking_time=0.08)
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

            if display:
                display.show_progress_step("Stuller SKU", sku, thinking_time=0.05)

            # Step 4: Get real-time pricing from Stuller
            logger.info(f"Getting real-time price for SKU: {sku}")
            if display:
                display.show_progress_step("Getting real-time pricing", thinking_time=0.08)
            api_response = self.stuller_client.get_sku_price(sku)

            # Check if API call succeeded - FIXED: correct logical check
            if not api_response or api_response.get('success') != True:
                logger.error(f"Failed to get price for SKU {sku}: {api_response}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"Failed to get price for SKU {sku}"
                )

            # Extract product data from successful response
            products = api_response.get('products', [])
            if not products:
                logger.error(f"No products returned for SKU {sku}: {api_response}")
                return BusinessFormatter.format_error_for_user(
                    'sku_not_found',
                    f"SKU {sku} not found in Stuller catalog"
                )

            product = products[0]  # Get first (should be only) product

            # Extract price and weight data from API response
            price_obj = product.get('Price')
            weight = product.get('Weight')
            weight_unit = product.get('WeightUnitOfMeasure')
            unit_of_sale = product.get('UnitOfSale')

            if not price_obj:
                logger.error(f"No price data in product for SKU {sku}: {product}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"No price available for SKU {sku}"
                )

            # Handle both old and new price formats
            if isinstance(price_obj, dict):
                # New format: {'Value': 87.08678, 'CurrencyCode': 'USD'}
                price_value = price_obj.get('Value')
            else:
                # Old format: '87.086780000000000' or 87.08678
                price_value = price_obj

            if price_value is None:
                logger.error(f"Invalid price format for SKU {sku}: {price_obj}")
                return BusinessFormatter.format_error_for_user(
                    'api_unavailable',
                    f"Invalid price format for SKU {sku}"
                )

            # Step 5: Calculate final pricing using weight-based calculation
            material_cost_per_dwt = Decimal(str(price_value))
            if display:
                display.show_progress_step("Stuller pricing", f"${material_cost_per_dwt:.2f} per DWT", thinking_time=0.05)

            if display:
                display.show_progress_step("Calculating material weight needed", thinking_time=0.06)

            # Calculate material weight needed based on dimensions and length
            material_weight_dwt = self._calculate_material_weight_dwt(
                material_calc, spec, weight, weight_unit, unit_of_sale
            )

            if display:
                display.show_progress_step("Material weight", f"{material_weight_dwt:.4f} DWT", thinking_time=0.05)
                display.show_progress_step("Applying pricing formula", thinking_time=0.05)

            material_total_cost = material_cost_per_dwt * material_weight_dwt

            base_price = self.config['base_price']
            total_price = material_total_cost + base_price

            if display:
                display.show_progress_step("Final price", f"${material_total_cost:.2f} + ${base_price:.2f} = ${total_price:.2f}", thinking_time=0.05)

            logger.info(f"Pricing complete: Material ${material_total_cost}, Base ${base_price}, Total ${total_price}")

            return BanglePrice(
                sku=sku,
                material_cost_per_dwt=material_cost_per_dwt,
                material_length_in=material_calc.rounded_length_in,
                material_weight_dwt=material_weight_dwt,
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

    def _calculate_material_weight_dwt(self, material_calc: MaterialCalculation, spec: BangleSpec,
                                       api_weight: float, weight_unit: str, unit_of_sale: str) -> Decimal:
        """
        Calculate the weight in DWT needed using proper material science

        This method uses karat-specific material densities to calculate accurate weights,
        replacing the flawed reference-based approach that caused pricing errors.

        Args:
            material_calc: Material calculation with length needed
            spec: Bangle specification with dimensions
            api_weight: Weight from API response (not used - always normalized to 1.0)
            weight_unit: Weight unit from API (should be 'DWT')
            unit_of_sale: Unit of sale from API (should be 'DWT')

        Returns:
            Weight in DWT needed for the calculated length
        """
        # Get material dimensions
        width_mm = float(spec.width.replace(' Mm', '').strip())
        thickness_mm = float(spec.thickness.replace(' Mm', '').strip())
        length_inches = material_calc.rounded_length_in

        # Use proper material science calculation
        calculation = self.material_density.calculate_theoretical_weight(
            width_mm=width_mm,
            thickness_mm=thickness_mm,
            length_inches=length_inches,
            quality=spec.metal_quality or spec.metal_color,
            color=spec.metal_color
        )

        # Comprehensive logging for verification and debugging
        logger.info(f"=== MATERIAL WEIGHT CALCULATION ===")
        logger.info(f"Dimensions: {width_mm}mm × {thickness_mm}mm × {length_inches}in")
        logger.info(f"Quality: {spec.metal_quality or spec.metal_color} {spec.metal_color}")
        logger.info(f"Density used: {calculation['density_g_per_cm3']:.3f} g/cm³")
        logger.info(f"Volume per inch: {calculation['volume_cm3_per_in']:.6f} cm³/in")
        logger.info(f"Weight per inch: {calculation['dwt_per_in']:.6f} DWT/in")
        logger.info(f"Total weight: {calculation['total_weight_dwt']:.6f} DWT")
        logger.info(f"==================================")

        return Decimal(str(calculation['total_weight_dwt']))