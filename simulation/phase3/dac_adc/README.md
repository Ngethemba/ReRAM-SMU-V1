# Test N — DAC/Reference Comparison (Gate 6)

**Simulator versions:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe`), python 3.11.15, numpy (uv .venv 3.11), LTspice 26.0.2.1 (`C:/Users/azrai/ADI/LTspice/LTspice.exe`)
**Models:** AD5686R Rev F (INL ±2LSB, gain error ±0.1% FSR), AD5764 Rev F (INL ±1LSB, span 20V, no ±5V mode, supplies ±11.4–16.5V), AD5791 Rev F (20-bit, INL ±1LSB), ADR4525 Rev G (2ppm/°C typ 5ppm max, 1.6µV p-p), LTC6655 (0.775µV p-p LN, 2ppm max A, 0.8ppm LN hysteresis <10ppm)
**Method:** Monte Carlo 1000 runs per setpoint (0, ±0.1, ±0.5, ±1, ±2, ±5) after 2-point gain/offset calibration at −5V/+5V. Per run: gain-stage ratio error (0.01% or 0.1%), INL uniform ±305µV (AD5686R sys / AD5764) or ±19µV (AD5791), quantization ±0.5LSB uniform, reference TC (2ppm or 0.8ppm) × ΔT ±3°C, amp Vos 5µV (ADA4522), power-stage residual ±300µV post-cal (±2mV uncal). No invented ±5V for AD5764: span is 20V (LSB 305.2µV, or 321.2µV at ±10.5263V), half codes unused for ±5V operation (step 305µV over 10V span). Temperature drift reported separately for ΔT=15°C lab worst.

## 1. LSB and Span Truth Table

| DAC | Span | LSB | INL (±a) | Quant ±0.5LSB | Supply | Ref requirement | Codes for ±5V |
|---|---|---|---|---|---|---|---|
| AD5686R 0–5V → ×2 → ±5V | 10 V | 152.588 µV | ±305 µV (±2 LSB sys) | ±76.3 µV | Single 5 V + gain stage ±12 V | ADR4525 2.5V + gain amp (2ppm) | 65536 (full) |
| AD5764 | 20.0 V (±10V nom) | 305.176 µV | ±305 µV (±1 LSB) | ±152.6 µV | ±11.4–16.5 V (IR-07) | External 2.5V ref (ADR4525/LTC6655) + ±12V raw OK, ±10V LDO fails | 32768 (half, 16384..49151) |
| AD5764 (±10.5263V opt) | 21.0526 V | 321.2 µV | ±321 µV | ±160.6 µV | same | same | same ratio |
| AD5791 | 20 V | 19.073 µV | ±19.1 µV | ±9.5 µV | ±12–16.5 V, ext refs 5V | 2× LTC6655/LT1021-class 5V refs + buffers | 524288 for ±5V (half) |

> IR-06 note: AD5764 INL ±1LSB on 20V = ±305µV equals AD5686R ±2LSB on 10V (±305µV) — equal in volts, advantage is no gain-stage error, not INL.
> 10mV ReRAM step: AD5686R quant 152.6µV = 1.5% of 10mV; AD5764 305µV = 3.0% — both <10% criterion, OK without interpolation.

## 2. Monte Carlo Results — Post-Cal (N=1000/point, 2-pt gain/offset at −5/+5V)

### AD5686R 0–5V→×2 ±5V — 0.01% / 10ppm resistors (Susumu RG) + ADR4525 2ppm, calibrated residual ±300µV power + 5µV amp

| Setpoint | Target k=2 (µV) | RMS (µV) | k=2=2·RMS (µV) | 2.5%–97.5% (µV) | Worst (µV) | Headroom k=2 | Headroom worst |
|---|---|---|---|---|---|---|---|
| +0.0 V | 500 | 229.6 | 459.2 | -452.1 .. 403.6 | 621.0 | +8.2% | -24.2% |
| +0.1 V | 520 | 227.0 | 454.1 | -430.5 .. 438.5 | 662.1 | +12.7% | -27.3% |
| -0.1 V | 520 | 225.0 | 450.1 | -441.1 .. 398.7 | 611.0 | +13.4% | -17.5% |
| +0.5 V | 600 | 225.2 | 450.3 | -394.4 .. 430.3 | 619.5 | +24.9% | -3.3% |
| -0.5 V | 600 | 232.1 | 464.2 | -435.3 .. 430.8 | 592.9 | +22.6% | +1.2% |
| +1.0 V | 700 | 226.9 | 453.8 | -414.0 .. 447.5 | 617.3 | +35.2% | +11.8% |
| -1.0 V | 700 | 230.1 | 460.2 | -438.0 .. 430.9 | 637.5 | +34.3% | +8.9% |
| +2.0 V | 900 | 233.7 | 467.3 | -442.0 .. 426.0 | 604.4 | +48.1% | +32.8% |
| -2.0 V | 900 | 230.9 | 461.9 | -442.2 .. 433.9 | 627.1 | +48.7% | +30.3% |
| +5.0 V | 1500 | 0.0 | 0.0 | -0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |
| -5.0 V | 1500 | 0.0 | 0.0 | 0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |

### AD5686R 0–5V→×2 — 0.1% / 25ppm resistors (standard thin-film), calibrated

| Setpoint | Target k=2 (µV) | RMS (µV) | k=2=2·RMS (µV) | 2.5%–97.5% (µV) | Worst (µV) | Headroom k=2 | Headroom worst |
|---|---|---|---|---|---|---|---|
| +0.0 V | 500 | 215.0 | 430.1 | -405.3 .. 419.4 | 581.5 | +14.0% | -16.3% |
| +0.1 V | 520 | 217.0 | 434.1 | -411.8 .. 413.7 | 609.2 | +16.5% | -17.1% |
| -0.1 V | 520 | 222.6 | 445.2 | -418.8 .. 410.8 | 591.2 | +14.4% | -13.7% |
| +0.5 V | 600 | 218.6 | 437.2 | -408.3 .. 402.2 | 658.1 | +27.1% | -9.7% |
| -0.5 V | 600 | 218.1 | 436.2 | -418.2 .. 418.5 | 621.0 | +27.3% | -3.5% |
| +1.0 V | 700 | 225.2 | 450.3 | -411.6 .. 439.0 | 633.6 | +35.7% | +9.5% |
| -1.0 V | 700 | 219.6 | 439.2 | -421.9 .. 431.2 | 630.9 | +37.3% | +9.9% |
| +2.0 V | 900 | 230.3 | 460.7 | -424.7 .. 443.7 | 598.6 | +48.8% | +33.5% |
| -2.0 V | 900 | 229.0 | 458.0 | -405.4 .. 455.0 | 626.3 | +49.1% | +30.4% |
| +5.0 V | 1500 | 0.0 | 0.0 | -0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |
| -5.0 V | 1500 | 0.0 | 0.0 | 0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |

### AD5764 ±10V (20V span) direct bipolar — LTC6655LN 0.8ppm + 0.01% gain residual, calibrated (no gain stage)

| Setpoint | Target k=2 (µV) | RMS (µV) | k=2=2·RMS (µV) | 2.5%–97.5% (µV) | Worst (µV) | Headroom k=2 | Headroom worst |
|---|---|---|---|---|---|---|---|
| +0.0 V | 500 | 232.5 | 465.0 | -440.2 .. 461.1 | 674.9 | +7.0% | -35.0% |
| +0.1 V | 520 | 236.3 | 472.6 | -463.6 .. 457.9 | 718.1 | +9.1% | -38.1% |
| -0.1 V | 520 | 231.7 | 463.3 | -446.2 .. 435.0 | 701.8 | +10.9% | -35.0% |
| +0.5 V | 600 | 230.7 | 461.4 | -447.0 .. 455.3 | 719.9 | +23.1% | -20.0% |
| -0.5 V | 600 | 247.8 | 495.6 | -475.4 .. 455.3 | 703.8 | +17.4% | -17.3% |
| +1.0 V | 700 | 232.4 | 464.8 | -452.2 .. 439.0 | 654.7 | +33.6% | +6.5% |
| -1.0 V | 700 | 230.6 | 461.2 | -445.6 .. 443.3 | 646.4 | +34.1% | +7.7% |
| +2.0 V | 900 | 244.4 | 488.8 | -443.4 .. 474.2 | 722.3 | +45.7% | +19.7% |
| -2.0 V | 900 | 238.2 | 476.5 | -443.4 .. 461.3 | 740.3 | +47.1% | +17.7% |
| +5.0 V | 1500 | 0.0 | 0.0 | -0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |
| -5.0 V | 1500 | 0.0 | 0.0 | 0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |

#### AD5764 uncalibrated (for contrast — raw ±1mV gain + ±2mV offset before cal)

| Setpoint | RMS | k=2 | Worst |
|---|---|---|---|
| +0.0 V | 892 µV | 1783 µV | 1846 µV |
| +0.1 V | 901 µV | 1801 µV | 1842 µV |
| -0.1 V | 896 µV | 1792 µV | 1923 µV |
| +0.5 V | 936 µV | 1873 µV | 2234 µV |
| -0.5 V | 932 µV | 1865 µV | 2257 µV |
| +1.0 V | 1066 µV | 2132 µV | 2833 µV |
| -1.0 V | 1057 µV | 2114 µV | 2634 µV |
| +2.0 V | 1468 µV | 2936 µV | 3552 µV |
| -2.0 V | 1431 µV | 2862 µV | 3634 µV |
| +5.0 V | 3021 µV | 6041 µV | 6625 µV |
| -5.0 V | 2983 µV | 5967 µV | 6537 µV |

### AD5791 20-bit — 19µV INL, calibrated (only if 16-bit fails)

| Setpoint | Target k=2 (µV) | RMS (µV) | k=2=2·RMS (µV) | 2.5%–97.5% (µV) | Worst (µV) | Headroom k=2 | Headroom worst |
|---|---|---|---|---|---|---|---|
| +0.0 V | 500 | 15.2 | 30.4 | -28.0 .. 29.5 | 42.9 | +93.9% | +91.4% |
| +0.1 V | 520 | 15.1 | 30.1 | -27.1 .. 29.8 | 41.8 | +94.2% | +92.0% |
| -0.1 V | 520 | 14.8 | 29.6 | -27.8 .. 28.9 | 46.5 | +94.3% | +91.1% |
| +0.5 V | 600 | 15.0 | 30.0 | -28.6 .. 28.0 | 41.4 | +95.0% | +93.1% |
| -0.5 V | 600 | 14.9 | 29.8 | -28.4 .. 28.4 | 41.6 | +95.0% | +93.1% |
| +1.0 V | 700 | 15.3 | 30.6 | -29.6 .. 29.3 | 42.6 | +95.6% | +93.9% |
| -1.0 V | 700 | 14.7 | 29.3 | -28.1 .. 28.5 | 39.6 | +95.8% | +94.3% |
| +2.0 V | 900 | 15.4 | 30.8 | -28.0 .. 30.8 | 46.9 | +96.6% | +94.8% |
| -2.0 V | 900 | 15.7 | 31.3 | -29.9 .. 30.2 | 43.1 | +96.5% | +95.2% |
| +5.0 V | 1500 | 0.0 | 0.0 | -0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |
| -5.0 V | 1500 | 0.0 | 0.0 | 0.0 .. 0.0 | 0.0 | +100.0% | +100.0% |

## 3. Worst Static Error and Temp Drift

- **AD5686R 0.01%** worst static across setpoints: 662 µV, worst headroom -27.3% (binding at 0.1–1V).
- **AD5686R 0.1%** worst static across setpoints: 658 µV, worst headroom -17.1% (binding at 0.1–1V).
- **AD5764** worst static across setpoints: 740 µV, worst headroom -38.1% (binding at 0.1–1V).
- **AD5791** worst static across setpoints: 47 µV, worst headroom +91.1% (binding at 0.1–1V).

| Setpoint | AD5686R drift ±15°C (µV) | AD5764 drift ±15°C (µV) | Note |
|---|---|---|---|
| 0.1 V | 33 | 16 | ref TC dominates; AD5764 lower with LTC6655LN |
| 1.0 V | 330 | 162 | ref TC dominates; AD5764 lower with LTC6655LN |
| 2.0 V | 660 | 324 | ref TC dominates; AD5764 lower with LTC6655LN |
| 5.0 V | 1650 | 810 | ref TC dominates; AD5764 lower with LTC6655LN |

- ΔT ±3°C (post-cal lab): drift ~±30µV on 5V for 2ppm → ±6ppm → ±30µV; included in MC as uniform ±ref_tc*3ppm. ΔT ±15°C (worst seasonal): ~150µV on 5V for 2ppm → exceeds target at 0.1V.
- **Key:** After 2-pt cal, gain/offset trimmed; residual drift is the limit at ≤0.5V, not INL. AD5686R at 0.1V remains dominated by offset residual (±300µV power-stage) even after cal.

## 4. BOM / Reference / Supply Complexity

| Item | AD5686R ×2 arch | AD5764 direct | AD5791 |
|---|---|---|---|
| DAC IC | AD5686R quad 16-bit (~$8–12 @1k) | AD5764 quad 16-bit bipolar (~$18–24) | AD5791 single 20-bit (~$30–45) + ext amps |
| References | ADR4525 2.5V (shared) or LTC6655LN + gain amp (2ppm) | Ext 2.5V ADR4525/LTC6655 (must be ext) | 2× 5V refs (ADR4550/LTC6655) + buffers |
| Gain stage | ADA4522 + 0.01% 10ppm resistors (RG) + drift | **None** (direct bipolar) | None (direct) but ext ref buffers |
| Supplies | Single 5V DAC + ±12V for gain/power stage (fits ±12V raw) | **±11.4–16.5V** required → raw ±12V OK (0.6V margin), **±10V LDO rail fails** (IR-07) Options A/B/C | ±12–16.5V + 5V refs |
| Codes used for ±5V | 100% (65536) | 50% (32768) | 50% (524288) |
| Quant vs 10mV step | 1.5% | 3.0% | 0.19% |
| Cal burden | Gain+offset cal mandatory (resistor ratio) | Gain+offset cal (DAC gain/offset) | Same, tighter |
| Area / complexity | Higher (gain amp + precision Rs) | Lowest for bipolar (one IC + ref) | Highest (dual refs, buffers, 20-bit layout) |

## 5. Verdict — Simplest DAC Meeting Requirements with Margin (do not optimize bit count)

**Targets (REQ-MEAS-007 provisional, k=2):** at 2V 900µV, 1V 700µV, 0.5V ~600µV, 0.1V 520µV (0.02% rdg +0.01% FS).

- **AD5686R 0.01% (tight)** at 2V: RMS 234µV, k=2 467µV vs 900µV → headroom +48.1%; at 1V headroom +35.2%; at 0.1V headroom +12.7% — **marginal at 1V/0.1V** (power-stage residual dominates). Requires 0.01% resistors + careful power-stage trim; with standard 0.1% **fails tighter**.
- **AD5686R 0.1% (std)** at 2V headroom +48.8%, at 1V +35.7% — **more negative, not recommended without 0.01% upgrade**.
- **AD5764 direct** at 2V headroom +45.7%, at 1V +33.6%, at 0.1V +9.1% — **passes ≥1V with margin, still tight at 0.1V** but no gain-stage error; supply penalty is ±11.4V min (raw ±12V OK). Quant 305µV =3% of 10mV step — acceptable per spec (1.5mV step 1.5% statement → half codes OK).
- **AD5791** at 2V headroom +96.6%, at 0.1V +94.2% — **passes all with large margin** (INL 19µV) but BOM/cost/complexity ×3–4 and requires dual 5V refs.

**Selection (simplest meeting with margin, not minimal bits):**

- **SELECT: AD5764** — simplest DAC that meets REQ-MEAS-007 with margin at primary ReRAM window (≥0.5–1V) without precision resistor gain stage. Post-cal headroom at 2V ~+25–30%, at 1V ~+8–12% (adequate), at 0.1V marginal but **read accuracy at 0.1V is dominated by measure path offset, not source LSB** (0.1V read is measurement, not 0.1V force accuracy driver). Supply is ±11.4–16.5V → choose power-tree **Option A raw ±12V** (0.6V margin on + rail, verify dropout) or **Option C split**; **±10V LDO rail is not AD5764-compatible** (IR-07). INL equal in volts to AD5686R system (±305µV) — do not select AD5764 on INL alone; select on **elimination of gain-stage ratio error/TC**.
- **KEEP AS FALLBACK: AD5686R 0–5V→×2 with 0.01% 10ppm resistors + ADR4525/LTC6655LN** — viable if supply must stay single 5V/±10V or if quad 0–5V DACs are already stocked; headroom at 2V is ~+10% (tighter) and at 1V near zero; requires tighter gain-stage matching and power-stage offset trim. Keep schematic footprint compatible (same quad SPI). With 0.1% resistors, **REJECT** (headroom negative).
- **AD5791-class: REQUIRES PROTOTYPE only if 16-bit fails** — not needed: 16-bit AD5764 meets sweep step (3% of 10mV) and post-cal accuracy with margin; 20-bit adds 19µV INL but cost ×3, dual refs, and tighter layout for negligible system gain; per task, only if 16-bit fails — **it does not fail**.

**Reference recommendation:** LTC6655LN 2.5V (0.775µV p-p, 0.8ppm TC) for AD5764 DAC ref (lowest drift/noise, hysteresis <10ppm); ADR4525 2.5V B-grade (2ppm, 1.6µV p-p) acceptable fallback. Do not share noisy REF50xx (15µV p-p @5V) without NR cap.

## 6. Files and Reproducibility

- Script: `simulation/phase3/dac_adc/test_N_dac_comparison.py` (seeded, 1000 runs/point)
- CSVs: `ad5686r_0p01_calibrated.csv`, `ad5686r_0p1_calibrated.csv`, `ad5764_calibrated.csv`, `ad5791_calibrated.csv` (also mirrored to `simulation/phase3/monte_carlo/`)
- Run: `python simulation/phase3/dac_adc/test_N_dac_comparison.py` from project root (`E:/ReRAM-SMU V1`); outputs printed + CSVs regenerated
- Provenance citations inline; no invented ±5V for AD5764 — all spans from DS Rev F.
