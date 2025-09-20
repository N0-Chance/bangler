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