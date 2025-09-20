# How to turn Stuller’s “price per 1 DWT” into **your** per-length material price

You gave me a slice of your Sizing Stock inventory. Key facts in that payload:
- `Price.Value` is the **price per 1 DWT** (unit-of-sale = `DWT`) for the specific SKU (fabricated stock).  
- The SKU carries geometry (`Width` mm, `Thickness` mm) and alloy identity (`Quality`, `Alloy Number`).  
These are enough to compute weight-per-inch and thus price for any cut length. :contentReference[oaicite:0]{index=0}

---

## Field mapping (from the product record)
Use these conceptual fields (names may vary by endpoint/path — both `DescriptiveElements` and `Specifications` contain them):
- `price_per_dwt = product.Price.Value`  (USD per DWT; **fabricated**, SKU-specific)  
- `width_mm`  (e.g., `"6.5 mm" → 6.5`)  
- `thickness_mm` (e.g., `"1.5 mm" → 1.5`)  
- `quality` (e.g., `14KY`, `14KW`, `Sterling Silver`, `Platinum Ruthenium`)  
- `alloy_code` (e.g., `0300`, `0401` — useful for density calibration)  
- `unit_of_sale` should be `DWT` (sanity check)  
- (Your own inputs) **bangle length** `L_in` (inches), computed from size using the mean-circumference method you already have.

All examples in your JSON are `UnitOfSale: "DWT"`, `WeightUnitOfMeasure: "DWT"`, and show geometry in millimeters. :contentReference[oaicite:1]{index=1}

---

## The conversion you need (per-inch weight from geometry)

Stuller prices by **weight** (DWT). To get cost for a length, you must convert the strip’s cross-section + length → **weight**.

1. Volume per inch (in cm³):

    ```
    volume_cm3_per_in = (width_mm * thickness_mm * 25.4) / 1000
    ```
    Explanation:
    - Cross-section area in mm² = `width_mm * thickness_mm`  
    - One inch of length = `25.4 mm`  
    - mm³ → cm³ conversion = ÷ `1000`

2. Grams per inch:

    ```
    g_per_in = volume_cm3_per_in * density_g_per_cm3
    ```

3. DWT per inch:

    ```
    dwt_per_in = g_per_in / 1.55517384
    ```

> **Constants**  
> - 1 inch = 25.4 mm  
> - 1 DWT = 1.55517384 g

4. DWT for your cut:

    ```
    weight_dwt = dwt_per_in * L_in
    ```

5. Material price for your cut **(fabricated, SKU-specific)**:

    ```
    material_cost = weight_dwt * price_per_dwt
    + per_piece_minimum (if any)
    + per_inch_fabrication * L_in (if any)
    ```

If the product record includes any minimums or adders (some do), apply them here. Your JSON slice doesn’t show explicit adders, but don’t assume they never exist across the catalog. :contentReference[oaicite:2]{index=2}

---

## Densities you’ll need (start here, then calibrate)

You can match Stuller to the cent by using **their** effective densities per alloy. If the API doesn’t expose density, start with standard values and **calibrate per alloy** (see next section).

**Typical starting points (g/cm³):**
- 24K Au: **19.32**  
- 22K Au: **17.7–18.3** (alloy-dependent)  
- 18K Yellow: **15.4–15.9**  
- 18K White: **14.7–15.9** (nickel/palladium systems differ)  
- 14K Yellow: **13.0–13.6**  
- 14K White: **12.5–14.0**  
- 10K Yellow: **11.3–12.0**  
- Sterling Silver (.925): **10.36**  
- Platinum-Ruthenium: **≈21.45**  
- Platinum-Cobalt: **≈20.8–21.1**

> These ranges reflect real alloy differences. Stuller’s “Alloy Number” (e.g., `0300`, `0401`) is a perfect key to maintain a **calibration table** so your computed weights track their production alloys, not generic textbook numbers. :contentReference[oaicite:3]{index=3}

---

## Calibration (do this once per alloy code)
To eliminate residual error from alloy composition, temper, and rolling reduction, capture **one known case** per `alloy_code` and back-solve an **effective density**:

Given a test cut with:
- `width_mm`, `thickness_mm`, `L_in`, invoice material price, and `price_per_dwt` for that exact SKU,

1) Compute `weight_dwt_from_invoice = invoice_price / price_per_dwt`.  
2) Convert to grams: `g_from_invoice = weight_dwt_from_invoice * 1.55517384`.  
3) Compute `volume_cm3 = (width_mm * thickness_mm * 25.4 * L_in) / 1000`.  
4) Solve `effective_density = g_from_invoice / volume_cm3`.

Store `effective_density` keyed by `(alloy_code, quality)` and reuse it for all future cuts of the same alloy family. This step makes your numbers **match Stuller exactly**, even if their alloy differs from generic references.

---

## Why your earlier mismatch happened
- You multiplied a **price per DWT** by an **assumed DWT weight** (e.g., `0.375 DWT`) that did not reflect the SKU’s actual weight per inch.  
- High-karat vs low-karat densities differ substantially; you can’t reuse the same `DWT/in` across qualities or alloys.  
- When you recompute `DWT/in` from geometry + (calibrated) density, then multiply by the SKU’s **fabricated** `price_per_dwt`, your totals line up with Stuller’s invoice.

---

## Worked micro-example (sanity check only)
SKU: “14K Yellow 6.5×1.5 mm Flat Sizing Stock”, `price_per_dwt ≈ $118.03` (from your slice), 3″ cut. :contentReference[oaicite:4]{index=4}

- `volume_cm3_per_in = (6.5 * 1.5 * 25.4) / 1000 = 0.24765 cm³/in`  
- Use a starting density for 14KY, say `13.3 g/cm³` → `g_per_in = 3.2945 g/in`  
- `dwt_per_in = 3.2945 / 1.55517384 ≈ 2.118 dwt/in`  
- 3″ cut → `weight_dwt ≈ 6.354 dwt`  
- Cost ≈ `6.354 * $118.03 ≈ $749` (before any minimums/adders)

This is only a **geometry + reference-density** estimate; after you calibrate density for `Alloy 0300` you’ll match their exact invoicing.

---

## Implementation checklist (no code assumptions)
1) Parse `width_mm`, `thickness_mm`, `quality`, `alloy_code`, `price_per_dwt`, `unit_of_sale` from the SKU payload. :contentReference[oaicite:5]{index=5}  
2) Compute your required length `L_in` from bangle size (mean circumference method).  
3) Look up `density_g_per_cm3` for `(alloy_code, quality)` from your **calibration table**; fall back to a standard density table if uncalibrated.  
4) Compute `dwt_per_in` via the geometry path above.  
5) Compute `weight_dwt = dwt_per_in * L_in`.  
6) Price: `material_cost = weight_dwt * price_per_dwt (+ adders/minimums if present)`.  
7) Log the full trace (inputs, conversions, density used, weight, price) so any drift is visible.  
8) When you have a confirmed Stuller invoice for a given alloy, back-solve and **update** that alloy’s `effective_density`.

Follow this and your system will harmonize Stuller’s “per DWT” pricing with your per-length workflow without guessing at weight.
