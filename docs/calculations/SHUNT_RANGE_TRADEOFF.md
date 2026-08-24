# Shunt Range Trade-off — Calculations & Philosophy Comparison

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**Status:** CALCULATION — informs DECISIONS.md, informs REQ-MEAS-001/002/005/008  
**Script:** `docs/calculations/shunt_range_tradeoff_calc.py` (run with `.venv` Python 3.11, numpy/scipy)  
**Constants:** `k = 1.380649e-23 J/K` exact (SI 2019), `T = 300 K`, `q = 1.602176634e-19 C`  
**Formulas:** `R = V_FS / I_FS`, `P = I_FS·V_FS = I_FS²·R`, `vn = √(4kTRB)` [V rms, brickwall], `in = vn/R`, `G = V_ADC_FS / V_FS`, `ΔT = P·θJA`, ENBW single-pole `1.57·fc → ×1.253`

> **Context / caution:** REQUIREMENTS v0.2.0 REQ-MEAS-001 is 6 ranges 10 mA→100 nA, MUC≈1 nA, baseline 100 mV FS shunt. CAUTION 2 applies: 100 mV = 5% of a ±2 V primary ReRAM window. Kelvin feedback corrects V_DUT at the sense point but does **not** eliminate burden — it moves the cost to output-stage headroom and settling. This document quantifies burden candidates so the 100 mV baseline can be kept, relaxed, or made range-dependent on evidence.

---

## 1. Candidate burden philosophies

| Philosophy | V_FS per range | Rationale |
|---|---|---|
| **A — Fixed 100 mV FS** (Phase-1 baseline) | 100 mV on all 6 ranges | Simplest; uniform ADC FS; best SNR where leakage/Johnson dominates (low-I ranges) |
| **B — Fixed 50 mV FS** | 50 mV on all ranges | Halves DUT perturbation and headroom, costs √2 SNR and 2× gain |
| **C — Fixed 25 mV FS** | 25 mV on all ranges | Quarters perturbation and power, costs 2× SNR (6 dB) and 4× gain → amplifies amp/ADC noise |
| **D — Range-dependent (RECOMMENDED)** | 25 mV on 10 mA/1 mA, 50 mV on 100 µA/10 µA, 100 mV on 1 µA/100 nA | Optimises where each error dominates: headroom/power at high-I, SNR/leakage at low-I |

Philosophy D is the quantitative favourite (see §4, §8). It is a strict superset of A: low-I ranges stay at the proven 100 mV SNR, high-I ranges reduce headroom by 75% where SNR is already abundant.

Note on SNR scaling: `SNR = V_FS / √(4kTRB)` with `R=V_FS/I_FS` → `SNR ∝ √(V_FS·I_FS) = √P`. So Johnson-limited SNR scales as **√V_FS**: 100 mV is √4 = 2× (6 dB) better than 25 mV, 100 mV is √2 = 1.41× better than 50 mV at the same I_FS. The cost is proportional power and headroom.

---

## 2. Fixed-burden tables (Python-verified, .venv)

All tables: `B = 10 Hz` brickwall (typical NPLC≈1 with modest averaging). For single-pole RC, multiply `vn` by `√1.57 ≈ 1.253` (§7). `TC_gain = 25 ppm/°C × ΔT`. Johnson current-noise fraction is small on high-I ranges; the `ppm FS` column uses `in_10Hz / I_FS × 1e6` (corrected — earlier BURDEN doc had a ×1000 unit error, see note below).

### 2.1 Fixed 100 mV FS — baseline

```
Range  |   R_shunt |     P@FS |  vn dens    | vn 10Hz | in 10Hz | in/FS 10Hz | Gain→2.5V | Gain→3.3V
 10 mA |   10.0 Ω  |  1.00 mW | 0.41 nV/√Hz | 0.001 µV | 128.7 pA | 0.013 ppm |  25.0× | 33.0×
  1 mA |  100.0 Ω  | 100.0 µW | 1.29 nV/√Hz | 0.004 µV |  40.7 pA | 0.041 ppm |  25.0× | 33.0×
100 µA |   1.00 kΩ |  10.0 µW | 4.07 nV/√Hz | 0.013 µV |  12.9 pA | 0.129 ppm |  25.0× | 33.0×
 10 µA |  10.00 kΩ |   1.0 µW |12.87 nV/√Hz | 0.041 µV |   4.07 pA | 0.407 ppm |  25.0× | 33.0×
  1 µA | 100.00 kΩ |   100 nW |40.70 nV/√Hz | 0.129 µV |   1.29 pA | 1.29  ppm |  25.0× | 33.0×
100 nA |   1.00 MΩ |    10 nW |128.7 nV/√Hz | 0.407 µV |   0.41 pA | 4.07  ppm |  25.0× | 33.0×
```

*At B=1 kHz multiply `vn` and `in` by √100 = 10× (100 nA: 4.07 pA rms). Gain column is ideal to map shunt FS to ADC FS (PGA=1, diff ±2.5 V). With ADS1262 PGA=32 the required gain collapses to ~0.8×/1.6×/3.1× for 100/50/25 mV — see §5.*

> **Correction vs BURDEN_VOLTAGE_ANALYSIS.md Rev 2026-08-24:** that doc's `i_n/I_FS` column reported 13 ppm at 10 mA; correct is **0.013 ppm** (0.13 nA / 10 mA = 13 ppb). The numerical `vn`/`in` values were correct; only the ppm conversion had a ×1000 error. This document is the corrected record.

### 2.2 Fixed 50 mV FS

```
 10 mA |    5.0 Ω  | 500.0 µW | 0.29 nV/√Hz | 0.001 µV | 182.0 pA | 0.018 ppm |  50.0× | 66.0×
  1 mA |   50.0 Ω  |  50.0 µW | 0.91 nV/√Hz | 0.003 µV |  57.6 pA | 0.058 ppm |  50.0× | 66.0×
100 µA |  500.0 Ω  |   5.0 µW | 2.88 nV/√Hz | 0.009 µV |  18.2 pA | 0.182 ppm |  50.0× | 66.0×
 10 µA |   5.00 kΩ |   500 nW | 9.10 nV/√Hz | 0.029 µV |   5.76 pA | 0.576 ppm |  50.0× | 66.0×
  1 µA |  50.00 kΩ |    50 nW |28.78 nV/√Hz | 0.091 µV |   1.82 pA | 1.82  ppm |  50.0× | 66.0×
100 nA | 500.00 kΩ |     5 nW |91.02 nV/√Hz | 0.288 µV |   0.58 pA | 5.76  ppm |  50.0× | 66.0×
```

### 2.3 Fixed 25 mV FS

```
 10 mA |    2.5 Ω  | 250.0 µW | 0.20 nV/√Hz | 0.001 µV | 257.4 pA | 0.026 ppm | 100.0× |132.0×
  1 mA |   25.0 Ω  |  25.0 µW | 0.64 nV/√Hz | 0.002 µV |  81.4 pA | 0.081 ppm | 100.0× |132.0×
100 µA |  250.0 Ω  |   2.5 µW | 2.04 nV/√Hz | 0.006 µV |  25.7 pA | 0.257 ppm | 100.0× |132.0×
 10 µA |   2.50 kΩ |   250 nW | 6.44 nV/√Hz | 0.020 µV |   8.14 pA | 0.814 ppm | 100.0× |132.0×
  1 µA |  25.00 kΩ |    25 nW |20.35 nV/√Hz | 0.064 µV |   2.57 pA | 2.57  ppm | 100.0× |132.0×
100 nA | 250.00 kΩ |     2 nW |64.36 nV/√Hz | 0.204 µV |   0.81 pA | 8.14  ppm | 100.0× |132.0×
```

**Reading:** Fixed low burden (25 mV) needs 4× the voltage gain of 100 mV. That gain multiplies amplifier `en` and ADC input noise. Johnson `in` is √4 = 2× worse (129 → 257 pA-equivalent at 10 mA is still negligible; at 100 nA 0.41→0.81 pA is the floor you cannot average away without lower BW). Self-heating power quarters (1.00 → 0.25 mW at 10 mA).

### 2.4 Range-dependent (D) — RECOMMENDED

| Range | V_FS | R_shunt | P@FS | vn dens | vn 10 Hz | in 10 Hz | in/FS |
|---|---|---|---|---|---|---|---|
| 10 mA | 25 mV | 2.5 Ω | 250 µW | 0.20 nV/√Hz | 0.64 nV* | 257 pA | 0.026 ppm |
| 1 mA | 25 mV | 25 Ω | 25 µW | 0.64 nV/√Hz | 2.04 nV | 81.4 pA | 0.081 ppm |
| 100 µA | 50 mV | 500 Ω | 5.0 µW | 2.88 nV/√Hz | 9.10 nV | 18.2 pA | 0.182 ppm |
| 10 µA | 50 mV | 5.0 kΩ | 500 nW | 9.10 nV/√Hz | 28.8 nV | 5.76 pA | 0.576 ppm |
| 1 µA | 100 mV | 100 kΩ | 100 nW | 40.7 nV/√Hz | 129 nV | 1.29 pA | 1.29 ppm |
| 100 nA | 100 mV | 1.00 MΩ | 10 nW | 129 nV/√Hz | 407 nV | 0.41 pA | 4.07 ppm |

*10 Hz brickwall; ENBW single-pole add 25%.* Gains to 2.5 V ADC FS: **100×, 100×, 50×, 50×, 25×, 25×**. With ADS1262 PGA=32: **3.1×, 3.1×, 1.6×, 1.6×, 0.78×, 0.78×** — i.e. low-I ranges can run with PGA ≤1 or small gain, high-I ranges need moderate gain.

Power total at worst-case simultaneous FS (not realistic — only one range active): dominated by 10 mA range; D saves 0.75 mW vs fixed 100 mV at 10 mA.

---

## 3. DUT impact (burden as fraction of read voltage)

Assume autoranging selects the tightest range with `I_FS ≥ I_DUT` (correct ranging; wrong ranging would be larger error). `V_burden = I·R_shunt`; fractional error if **not** Kelvin-corrected = `V_burden / V_DUT`.

| DUT R | I @ 0.5 V read | Autorange (tightest) | V_burden (fixed 100 mV R) | V_burden (range-dep R) | Error 100 mV FS | Error range-dep |
|---|---|---|---|---|---|---|
| 1 kΩ | 500 µA | 1 mA (100 Ω / 25 Ω) | 50.0 mV | 12.5 mV | 10.0% | 2.5% |
| 10 kΩ | 50 µA | 100 µA (1 kΩ / 500 Ω) | 50.0 mV | 25.0 mV | 10.0% | 5.0% |
| 100 kΩ | 5 µA | 10 µA (10 kΩ / 5 kΩ) | 50.0 mV | 25.0 mV | 10.0% | 5.0% |
| 1 MΩ | 0.5 µA | 1 µA (100 kΩ) | 50.0 mV | 50.0 mV | 10.0% | 10.0% |
| 10 MΩ | 50 nA | 100 nA (1 MΩ) | 50.0 mV | 50.0 mV | 10.0% | 10.0% |
| 100 MΩ | 5 nA | 100 nA (1 MΩ) | 5.0 mV | 5.0 mV | 1.0% | 1.0% |

**Implication:** At mid-range reads, burden is 5–10% of DUT voltage — not negligible. Kelvin **must** regulate V_DUT at the sense point, paying the burden as headroom in the force amplifier. Range-dependent reduces the worst-case error from 10%→2.5% at 1 kΩ LRS (500 µA) and 10%→5% at 10–100 kΩ, where LRS reads after SET are most error-sensitive. Low-I HRS stays at 10% burden but HRS error tolerance is higher and averaging helps.

---

## 4. Power, self-heating, TC drift

`ΔT = P·θJA`. Typical θJA for 0805/1206 on FR-4 with copper pour: 40–125 K/W (depends on pad, airflow). Gain error from TC = `ΔT · TC`.

| Range | P (100 mV) | ΔT @50 K/W | gain err | ΔT @125 K/W | gain err | P (range-dep) | ΔT @50 K/W | gain err |
|---|---|---|---|---|---|---|---|---|
| 10 mA | 1.00 mW | 50 mK | 1.25 ppm | 125 mK | 3.1 ppm | 0.25 mW | 12.5 mK | 0.31 ppm |
| 1 mA | 100 µW | 5.0 mK | 0.13 ppm | 12.5 mK | 0.31 ppm | 25 µW | 1.25 mK | 0.031 ppm |
| 100 µA | 10 µW | 0.50 mK | 0.013 ppm | 1.25 mK | 0.031 ppm | 5 µW | 0.25 mK | — |
| 10 µA | 1.0 µW | 0.05 mK | — | 0.13 mK | — | 500 nW | — | — |
| 1 µA | 100 nW | — | — | — | — | 100 nW | — | — |
| 100 nA | 10 nW | — | — | — | — | 10 nW | — | — |

*(TC = 25 ppm/°C assumed; 0.1% thin-film typical. Use 10–25 ppm low-TC for shunts — BOM decision.)*

**Lesson:** Self-heating is negligible (<4 ppm even worst-case 10 mA/100 mV/125 K/W). The dominant TC error is ambient ΔT, not self-heating: `±10 °C × 25 ppm = 250 ppm = 25 µV on 100 mV FS` — same for all ranges at fixed FS, and scales with V_FS for range-dependent (6.25 µV on 25 mV ranges). Cal corrects absolute, but inter-cal drift must be budgeted.

---

## 5. ADC amplitude & gain required

Three ADC FS assumptions (provisional Phase-2 candidates):

* **ADS1262 PGA=1 diff ±2.5 V** (5 V span, 2.5 V magnitude) — baseline ΔΣ
* **ADS1262 PGA=32 diff ±78 mV** (±Vref/PGA, Vref=2.5 V)
* **STM32G4 internal 12-bit 3.3 V FS** (for comparison; not recommended as primary)

| Burden | Gain to 2.5 V | Gain to 78 mV (PGA=32) | Gain to 3.3 V |
|---|---|---|---|
| 100 mV | 25.0× | 0.78× (attenuate/buffer) | 33.0× |
| 50 mV | 50.0× | 1.56× | 66.0× |
| 25 mV | 100.0× | 3.13× | 132.0× |
| Range-dep: 10 mA/1 mA 25 mV | 100× | 3.13× | 132× |
| Range-dep: 100 µA/10 µA 50 mV | 50× | 1.56× | 66× |
| Range-dep: 1 µA/100 nA 100 mV | 25× | 0.78× | 33× |

**Interpretation:**

* With ADS1262 at PGA=1, fixed 25 mV needs 100× gain — amplifies `en` 100×. With PGA=32 the same shunt is only 3.1× post-PGA. Strategy matters (§6).
* Range-dependent keeps PGA ≤3.13× even at the harshest 25 mV range; low-I ranges even run attenuate/unity.
* STM32G4 internal ADC needs 33–132× — not practical without a dedicated low-noise gain stage; supports ADS1262 (or equivalent ΔΣ) as primary.

### LSB vs Johnson (at 100 nA, R=1 MΩ, V_FS=100 mV)

| ADC bits | LSB (V) | LSB as current (100 nA range) | Johnson `in` (10 Hz) | Conclusion |
|---|---|---|---|---|
| 16 | 1.53 µV | 1.53 pA | 0.41 pA | LSB ≈ 3.7× Johnson — quantisation dominates |
| 18 | 381 nV | 0.38 pA | 0.41 pA | LSB ≈ Johnson — balanced |
| 24 | 5.96 nV | 6.0 fA | 0.41 pA | LSB ≪ Johnson — ADC resolves well below analog floor; extra bits add codes, not information |
| 32 | 0.023 nV | 0.023 fA | 0.41 pA | Far below floor |

**Rule:** 18-bit is enough to quantise Johnson at 10 Hz on 100 nA. 24-bit is chosen for margin, oversampling, and PGA headroom — not because 6 fA is measurable. Never report LSB as accuracy (REQ-MEAS-005).

---

## 6. ENBW correction

Brickwall values above assume ideal rectangular BW. For a real single-pole RC anti-alias: `ENBW = (π/2)·fc ≈ 1.57·fc → vn_ENBW = vn_brickwall × √1.57 ≈ 1.253×`.

| R | vn @10 Hz brickwall | vn @10 Hz single-pole ENBW | in @10 Hz ENBW |
|---|---|---|---|
| 10 Ω | 1.29 nV | 1.61 nV | 161 pA |
| 1 kΩ | 12.9 nV | 16.1 nV | 16.1 pA |
| 100 kΩ | 129 nV | 161 nV | 1.61 pA |
| 1 MΩ | 407 nV | 510 nV | 0.51 pA |

At `B=1 kHz`, multiply by 10×; at `B=100 Hz`, multiply by √10 ≈ 3.16×. NPLC=10 (200 ms @50 Hz) reduces white-noise BW by ~10× → noise ÷√10.

---

## 7. Settling (`τ = R·C_tot`)

With `C_tot ≈ 50 pF` (relay + trace + amp input + cable stub; verify per layout):

| R | τ | 5τ (0.7% settling) | Comment |
|---|---|---|---|
| 10 Ω | 0.5 ns | 2.5 ns | Negligible |
| 1 kΩ | 50 ns | 250 ns | Negligible |
| 10 kΩ | 500 ns | 2.5 µs | Fine |
| 100 kΩ | 5 µs | 25 µs | Within 10 ms dwell |
| 500 kΩ | 25 µs | 125 µs | Within dwell; DA tail dominates |
| 1 MΩ | 50 µs | 250 µs | Within 10 ms dwell; DA tail seconds |

TIA settling is `τ_eff = R_f·C_f / A_OL` effective — microseconds even for 1 MΩ with proper `Cf`. Shunt needs relay-break-before-make sequencing to avoid glitch.

---

## 8. Trade-off summary & recommendation

| Criterion | 100 mV fixed | 50 mV fixed | 25 mV fixed | **Range-dep D (REC)** |
|---|---|---|---|---|
| Johnson SNR (high-I) | Best | −1.5 dB | −6 dB | −6 dB only where SNR is abundant |
| Johnson SNR (100 nA) | Best | −1.5 dB | −6 dB | **Best (100 mV)** — where it matters |
| DUT perturbation (LRS) | 10% @500 µA | 5% | 2.5% | **2.5% @500 µA, 5% @50 µA** |
| Headroom cost | 100 mV worst | 50 mV | 25 mV | **25 mV on high-I (saves 75 mV rail)** |
| Power @10 mA | 1.00 mW | 0.50 mW | 0.25 mW | **0.25 mW** |
| Gain to 2.5 V | 25× uniform | 50× uniform | 100× uniform | 25–100× (PGA handles) |
| Gain-amplified `en` | 25× | 50× | 100× | 25× where `en` matters (low-I) |
| Firmware complexity | Simplest | Simplest | Simplest | Needs per-range cal + gain switch (minor) |

**Recommendation:** Adopt **philosophy D (range-dependent)** as V1 target; keep **philosophy A (fixed 100 mV)** as the fallback/simplicity candidate if per-range gain switching is deferred.

* Rationale: D gives the headroom/power benefit of low burden exactly where the output stage needs it (mA ranges, forming/RESET compliance), while preserving the SNR/leakage margin of 100 mV where the system is Johnson- and leakage-limited (100 nA/1 µA HRS reads). It costs only a per-range gain/PGA setting and per-range cal — both already required for 6-range autoranging.
* If schedule risk outweighs the 75 mV headroom saving, fallback to fixed 100 mV is acceptable with verified headroom (LT1970A ±12 V rails have ample margin on ±5 V + 100 mV).

**Open for Phase-2 DEC:** Final R values are E96 nearest (10.0 Ω vs 2.49 Ω vs 2.5 Ω nominal; 100 Ω vs 24.9 Ω; etc.), TC choice (25 ppm vs 10 ppm), power rating (≥4× P@FS for pulse SOA), and whether to use discrete precision resistors or integrated shunt network.

---

## 9. Reproducibility

```bash
# From project root, using provisioned .venv
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe docs/calculations/shunt_range_tradeoff_calc.py
```

Commit the script; do not hand-copy numbers into the schematic. Every shunt value on the schematic must trace to this calc + datasheet TC/power + cal procedure.

---

*Traceability: REQ-MEAS-001/002/005/008, REQ-SRC-001/002/006, REQ-PWR-003, REQ-SAFE-001, REQ-DUT-001, DEC-008/009/011, ENGINEERING_RULES §3, LOW_CURRENT_MEASUREMENT §3/§5, BURDEN_VOLTAGE_ANALYSIS (corrected).*
