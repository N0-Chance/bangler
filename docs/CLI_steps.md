# This file is a guide for the CLI interface of the bangler project.

## Customer Variables - Phase 1

Step by step:
1. Size (quesionary select: accepts any size from 10 to 27)
2. Metal Shape (questionary select: Flat, Comfort Fit, Low Dome, Half Round, Square, Triangle)
3. Metal Color (questionary select: Yellow, White, Rose, Green, Sterling Silver)
4. Metal Quality (questionary select: 10k, 14k, 18k - skipped if Sterling Silver)
5. Width (questionary select: determined by Metal Shape)
6. Thickness (questionary select: determined by Metal Shape)

## Business Logic - Phase 2

1. Size → MM circumference conversion
2. Circumference → length of sizing stock needed (math formula TBD)
3. Round up to nearest inch (Stuller's selling unit)
4. Real-time API call for current pricing on specific sizing stock SKU
5. Apply pricing formula: Material cost + configurable markup
6. Return final customer price with breakdown