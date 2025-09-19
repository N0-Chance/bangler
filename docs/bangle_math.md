# Bangle Length Calculation Logic

## Purpose
Convert bangle size (inside diameter) + thickness into required strip length (inches).

## Inputs
- `size_to_mm`: dictionary mapping size → inside diameter in mm (from your chart)
- `size`: selected bangle size
- `thickness_mm`: metal thickness (mm)
- `k_factor`: neutral axis factor (tweakable; 0.5 ≈ mid-thickness, adjust 0.45–0.5 if needed)
- `seam_allow_in`: extra allowance in inches for kerf/fit/cleanup (tweakable; ~0.20–0.25")

## Formula
```
L = π × (ID_in + 2 × k_factor × thickness_in) + seam_allow_in
```
where:
- `ID_in` = inside diameter in inches
- `thickness_in` = thickness in inches
- `k_factor` ≈ 0.5 (default)
- `seam_allow_in` ≈ 0.25" (default)

## Notes
- Width does not affect length; only affects weight/price lookup.
- For oval bangles: use ellipse perimeter (Ramanujan) on mean axes.
- Round UP to your purchase increment (e.g., nearest 1/8").
- If overshooting or undershooting consistently, adjust k_factor.

## Python Implementation Example

```python
import math

MM_PER_IN = 25.4

def bangle_length_inches(size_to_mm: dict, size: int, thickness_mm: float,
                         k_factor: float = 0.5, seam_allow_in: float = 0.04) -> float:
    """
    Compute required strip length in inches for a round bangle.
    """
    id_mm = size_to_mm[size]            # inside diameter (mm) from table
    id_in = id_mm / MM_PER_IN
    t_in  = thickness_mm / MM_PER_IN
    length_in = math.pi * (id_in + 2 * k_factor * t_in)
    return length_in + seam_allow_in

# Example size mapping (from your chart)
size_to_mm = {
    10: 52.37, 11: 53.97, 12: 55.54, 13: 57.15, 14: 58.72, 15: 60.32,
    16: 61.89, 17: 63.50, 18: 65.07, 19: 66.67, 20: 68.24, 21: 69.85,
    22: 71.42, 23: 73.02, 24: 74.59, 25: 76.20, 26: 77.77, 27: 79.37
}

# Example usage:
print(bangle_length_inches(size_to_mm, size=20, thickness_mm=2.0))
# → ~8.73" (including seam allowance)
```
