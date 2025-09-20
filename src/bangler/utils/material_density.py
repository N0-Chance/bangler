"""
Material density lookup system for accurate weight calculations across different gold karats.

This module provides karat-specific density data to enable precise material weight calculations
for the bangler pricing system. Different gold karats have significantly different densities
due to varying alloy compositions.
"""

import logging
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)

class MaterialDensity:
    """Provides material density lookup for different gold karats and alloys"""

    # Standard density table (g/cm³) based on typical jewelry alloys
    # Sources: Industry standards and materials engineering data
    STANDARD_DENSITIES = {
        '24K': 19.32,  # Pure gold
        '22K': 18.0,   # Average of 17.7-18.3 range (alloy-dependent)
        '18K': 15.65,  # Average of 15.4-15.9 range (yellow gold)
        '14K': 13.3,   # Average of 13.0-13.6 range (yellow gold)
        '10K': 11.65,  # Average of 11.3-12.0 range (yellow gold)
        'Sterling Silver': 10.36,  # 92.5% silver alloy
    }

    # White gold tends to be slightly different due to palladium/nickel alloys
    WHITE_GOLD_ADJUSTMENTS = {
        '18K': 15.2,   # Slightly lower due to palladium/nickel
        '14K': 13.0,   # Slightly lower due to palladium/nickel
        '10K': 11.4,   # Slightly lower due to palladium/nickel
    }

    # Calibrated densities based on empirical Stuller data
    # These override standard densities when available
    CALIBRATED_DENSITIES = {
        # Format: (karat, color, alloy_code): density_g_per_cm3
        # Will be populated as we calibrate against actual Stuller pricing
    }

    def __init__(self):
        """Initialize the density lookup system"""
        pass

    def get_density_for_quality(self, quality: str, color: str = 'Yellow') -> float:
        """
        Get material density for a specific quality and color combination

        Args:
            quality: Quality string (e.g., '10K', '14K', '18K', '24K', 'Sterling Silver')
            color: Metal color ('Yellow', 'White', 'Rose', 'Green')

        Returns:
            Density in g/cm³

        Raises:
            ValueError: If quality is not recognized
        """
        # Handle special cases
        if quality in ['Sterling Silver', 'Continuum Sterling Silver']:
            logger.info(f"Using Sterling Silver density: {self.STANDARD_DENSITIES['Sterling Silver']:.2f} g/cm³")
            return self.STANDARD_DENSITIES['Sterling Silver']

        # Extract karat from quality string
        karat = self._extract_karat(quality)

        if not karat:
            raise ValueError(f"Could not extract karat from quality: {quality}")

        # Check for calibrated density first
        calibrated_density = self._get_calibrated_density(karat, color)
        if calibrated_density:
            logger.info(f"Using calibrated density for {karat} {color}: {calibrated_density:.2f} g/cm³")
            return calibrated_density

        # Use standard density with color adjustments
        density = self._get_standard_density(karat, color)
        logger.info(f"Using standard density for {karat} {color}: {density:.2f} g/cm³")
        return density

    def _extract_karat(self, quality: str) -> Optional[str]:
        """
        Extract karat designation from quality string

        Args:
            quality: Quality string like '10K Yellow', '14K', '24K Yellow', etc.

        Returns:
            Karat string like '10K', '14K', etc. or None if not found
        """
        # Look for pattern like '10K', '14K', '18K', '24K'
        match = re.search(r'(\d+K)', quality.upper())
        if match:
            return match.group(1)

        # Handle special cases
        if 'sterling' in quality.lower() or 'silver' in quality.lower():
            return 'Sterling Silver'

        return None

    def _get_calibrated_density(self, karat: str, color: str) -> Optional[float]:
        """
        Get calibrated density if available

        Args:
            karat: Karat designation (e.g., '10K', '14K')
            color: Metal color

        Returns:
            Calibrated density or None if not available
        """
        # Check for exact match with color
        key = (karat, color, None)  # No alloy code for now
        if key in self.CALIBRATED_DENSITIES:
            return self.CALIBRATED_DENSITIES[key]

        return None

    def _get_standard_density(self, karat: str, color: str) -> float:
        """
        Get standard density with color adjustments

        Args:
            karat: Karat designation (e.g., '10K', '14K')
            color: Metal color

        Returns:
            Standard density in g/cm³

        Raises:
            ValueError: If karat is not in standard table
        """
        if karat not in self.STANDARD_DENSITIES:
            raise ValueError(f"Unknown karat type: {karat}")

        # Get base density
        base_density = self.STANDARD_DENSITIES[karat]

        # Apply white gold adjustment if applicable
        if color.lower() == 'white' and karat in self.WHITE_GOLD_ADJUSTMENTS:
            return self.WHITE_GOLD_ADJUSTMENTS[karat]

        return base_density

    def add_calibrated_density(self, karat: str, color: str, alloy_code: str,
                             density: float, source: str = "manual"):
        """
        Add a calibrated density value based on empirical data

        Args:
            karat: Karat designation (e.g., '10K', '14K')
            color: Metal color
            alloy_code: Stuller alloy code (e.g., '0300', '0401')
            density: Empirically determined density in g/cm³
            source: Source of calibration data
        """
        key = (karat, color, alloy_code)
        self.CALIBRATED_DENSITIES[key] = density

        logger.info(f"Added calibrated density: {karat} {color} (alloy {alloy_code}) = {density:.3f} g/cm³ (source: {source})")

    def get_conversion_constants(self) -> Dict[str, float]:
        """
        Get conversion constants used in calculations

        Returns:
            Dictionary of conversion constants
        """
        return {
            'mm_per_inch': 25.4,
            'grams_per_dwt': 1.55517384,
            'mm3_per_cm3': 1000.0
        }

    def calculate_theoretical_weight(self, width_mm: float, thickness_mm: float,
                                   length_inches: float, quality: str,
                                   color: str = 'Yellow') -> Dict[str, float]:
        """
        Calculate theoretical weight using material science principles

        Args:
            width_mm: Width in millimeters
            thickness_mm: Thickness in millimeters
            length_inches: Length in inches
            quality: Quality string (e.g., '10K Yellow')
            color: Metal color

        Returns:
            Dictionary with calculation breakdown
        """
        constants = self.get_conversion_constants()
        density = self.get_density_for_quality(quality, color)

        # Volume calculation (exact formula from materials engineering)
        volume_cm3_per_in = (width_mm * thickness_mm * constants['mm_per_inch']) / constants['mm3_per_cm3']

        # Material science conversion
        g_per_in = volume_cm3_per_in * density
        dwt_per_in = g_per_in / constants['grams_per_dwt']
        total_weight_dwt = dwt_per_in * length_inches

        return {
            'width_mm': width_mm,
            'thickness_mm': thickness_mm,
            'length_inches': length_inches,
            'quality': quality,
            'density_g_per_cm3': density,
            'volume_cm3_per_in': volume_cm3_per_in,
            'g_per_in': g_per_in,
            'dwt_per_in': dwt_per_in,
            'total_weight_dwt': total_weight_dwt
        }