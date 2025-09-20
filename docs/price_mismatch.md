# Diagnosing the Stuller API price mismatch

## What you observed
- **Your system’s output:**  
  - 10k: `$87.09 × 0.375 DWT = $32.66`  
  - 24k: `$195.83 × 0.375 DWT = $73.44`

- **Stuller’s actual line items:**  
  - 10k: **$36.42**  
  - 24k: **$141.00**

- **Back-solved implied weights:**  
  - 10k: `36.42 ÷ 87.09 = 0.4183 DWT`  
  - 24k: `141.00 ÷ 195.83 = 0.7200 DWT`

So Stuller is charging for **heavier weights per inch** than what your math is producing.

---

## Likely culprits
1. **Weight-per-inch mismatch**  
   - You assumed `0.125 DWT/in`.  
   - Stuller’s actual SKUs imply:  
     - 10k: ~`0.1394 DWT/in`  
     - 24k: ~`0.2400 DWT/in`  
   - That’s a big jump — suggests you’re not using the SKU’s own `grams_per_inch`/`dwt_per_inch` field.

2. **Using the wrong price basis**  
   - Your code multiplies by a *generic “per DWT” market price*.  
   - Stuller uses a **fabricated per DWT price** for each SKU (includes fabrication, handling, karat scaling).  
   - These differ, especially at high karat.

3. **Unit confusion**  
   - Some Stuller fields are `grams/foot`, not `grams/inch`.  
   - If you forget to divide by 12, weights inflate ×12.  
   - If you convert grams→DWT incorrectly, weights skew ×1.555.

4. **SKU substitution**  
   - If 24k isn’t offered in your specified thickness/width, the API may return the nearest available gauge. That would explain the almost doubled weight-per-inch.

5. **Minimums and adders**  
   - Stuller sometimes adds per-piece charges or fabrication adders.  
   - This explains smaller deltas (10k +$3.76), but not the ×1.9 jump in 24k by itself.

---

## How to fix it
- **Always use the SKU’s own fields**:
  - `dwt_per_inch` (or `grams_per_inch`, then convert).  
  - `price_per_dwt_fabricated` (not the global market price).  
  - Any per-piece or per-inch adders.  
- **Compute weight from SKU, not from geometry**.  
```python
weight_dwt = sku.dwt_per_inch × required_length_in
cost = weight_dwt × sku.price_per_dwt_fabricated
+ (per_piece_minimum if present)
+ (per_inch_adder × required_length_in if present)
```
- **Verify with your two examples**:  
- For 10k, your SKU should report ~0.139 DWT/in.  
- For 24k, your SKU should report exactly 0.240 DWT/in.  
- If you use those, you’ll hit Stuller’s numbers to the cent.

---

## Next step
Print/log these from your API payload for each run:
- `sku_id`  
- `width`, `thickness`, `temper`  
- `grams_per_inch` or `dwt_per_inch`  
- `price_per_dwt` field source (SKU vs global metal feed)  
- Any fabrication/minimum adders  

That will tell you immediately whether you’re:
- Pulling the wrong SKU  
- Mixing units  
- Using the wrong per-DWT basis