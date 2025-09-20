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
                    if line and ' - ' in line and line[0].isdigit():
                        try:
                            size_str, mm_str = line.split(' - ')
                            size_map[int(size_str)] = float(mm_str)
                        except ValueError:
                            # Skip lines that can't be parsed (like footer text)
                            continue
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