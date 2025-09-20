import math

class SizeConverter:
    """Handles bangle size to MM circumference conversion"""

    # Hardcoded size-to-diameter mapping (inside-to-inside measurements in MM)
    # Source: Original bangle_size.txt reference data
    SIZE_TO_DIAMETER_MM = {
        10: 52.37, 11: 53.97, 12: 55.54, 13: 57.15, 14: 58.72, 15: 60.32,
        16: 61.89, 17: 63.50, 18: 65.07, 19: 66.67, 20: 68.24, 21: 69.85,
        22: 71.42, 23: 73.02, 24: 74.59, 25: 76.20, 26: 77.77, 27: 79.37
    }

    def __init__(self):
        # No file loading needed - using hardcoded data
        pass

    def size_to_circumference_mm(self, size: int) -> float:
        """
        Convert bangle size to MM circumference

        Args:
            size: Bangle size (10-27)

        Returns:
            Circumference in millimeters (π × diameter)

        Note:
            The SIZE_TO_DIAMETER_MM mapping contains inside diameter measurements.
            This method calculates the actual circumference using π × diameter.
        """
        if size not in self.SIZE_TO_DIAMETER_MM:
            raise ValueError(f"Invalid size: {size}. Valid sizes: {list(self.SIZE_TO_DIAMETER_MM.keys())}")

        diameter_mm = self.SIZE_TO_DIAMETER_MM[size]
        circumference_mm = math.pi * diameter_mm
        return circumference_mm

    def size_to_circumference_in(self, size: int) -> float:
        """Convert bangle size to inch circumference"""
        mm = self.size_to_circumference_mm(size)
        return mm / 25.4

    def get_valid_sizes(self) -> list[int]:
        """Get list of valid bangle sizes"""
        return sorted(self.SIZE_TO_DIAMETER_MM.keys())