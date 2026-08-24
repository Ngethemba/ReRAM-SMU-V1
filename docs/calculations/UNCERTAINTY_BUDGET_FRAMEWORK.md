# Uncertainty Budget Framework — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 1 research  
**Date:** 2026-08-24  
**Status:** Framework only — categories + combination method + placeholder numbers; final type-A/type-B evaluation after part selection and prototype measurement per GUM.  
**Requirements:** REQ-CAL-003 (uncertainty budget), REQ-GEN-001, ENGINEERING_RULES §3 (independent recalculation).  
**Companion:** `NOISE_BUDGET_FRAMEWORK.md` (random), `LOW_CURRENT_MEASUREMENT.md` (§1.1 ).

---

## 1. Purpose and method (GUM — Guide to the Expression of Uncertainty in Measurement)

Per JCGM 100:2008 (GUM):

- **Type A** evaluated by statistical analysis of repeated observations (e.g., noise standard deviation).
- **Type B** evaluated by other means (datasheet max, calibration cert, tolerance).
- Each contributor `u_i` is a **standard uncertainty** (1σ). For non-Gaussian or rectangular distributions, convert: `u = a / √3` for ±a rectangular, `u = a / √6` for triangular.
- Combined standard uncertainty for uncorrelated inputs: `u_c = √( Σ u_i² )` (RSS). With correlations, include covariance terms.
- Expanded uncertainty: `U = k·u_c` with `k=2` (≈95% confidence for Gaussian).

V1 reports **standard uncertainty per range** and expanded `k=2` for compliance with REQ-CAL-003. Do not conflate resolution (LSB) with `u_c`.

---

## 2. Expected categories (checklist — Phase 2 fills values)

### Source (force) voltage path — DAC → conditioning amp → power stage

| # | Contributor | Type | Distribution | Typical form in datasheet | Phase 2 action |
|---|-------------|------|--------------|---------------------------|----------------|
| S1 | DAC reference initial accuracy | B | rectangular (±%) | e.g., ADR4525 ±0.02% max → `u = 0.02%/√3` | datasheet rev/page |
| S2 | DAC reference tempco / aging | B | rectangular or Gaussian | e.g., 2 ppm/°C ·ΔT, 25 ppm/1khr → `u = drift/√3` | log ΔT range |
| S3 | DAC INL (integral non-linearity) | B | rectangular (±LSB or ppm FS) | e.g., AD5686R ±2 LSB (±305 µV on 10 V FS) → `u=INL/√3` | per-code or post-cal LUT residual |
| S4 | DAC offset error / zero-scale | B | Gaussian or rect. | mV or %FS | cal residual after zero trim |
| S5 | DAC gain error | B | rect. | %FS | cal residual |
| S6 | Conditioning amp offset Vos + TC VOS | B | Gaussian + rect. TC term | µV, µV/°C ·ΔT | zero-drift choice; verify |
| S7 | Amp bias current · R_eq | B | rect. | Ib·R_eq, TC Ib | check vs shunt source R |
| S8 | Resistor ratio error (force divider/gain set) | B | rect. (±tolerance) | 0.1% or 0.01% → `u=tol/√3` | specify tolerance/TC class |
| S9 | Resistor tempco ·ΔT | B | rect. | 25 ppm/°C ·ΔT=10 °C → 250 ppm | include self-heating `ΔT=P·θJA` |
| S10 | Power-stage offset / headroom non-linearity | B | rect./measured | µV–mV by load | simulation + bench |

### Measure current path — shunt / TIA → sense amp → ADC

| # | Contributor | Type | Distribution | Form |
|---|-------------|------|--------------|------|
| M1 | Shunt tolerance | B | rect. | 0.1% / 0.01% → `u=tol/√3` |
| M2 | Shunt tempco ·ΔT + self-heating | B | rect. | 25 ppm/°C·10 °C=250 ppm + `P·θJA` (1 mW→ ΔT≈ few °C) |
| M3 | Shunt Johnson noise (type A) | A | Gaussian | `√(4kTRB)` — use measured σ, not calc, for final |
| M4 | Sense amp Vos / TC / Ib·R / en/in noise | B+A | Gaussian (noise) + rect. (offset) | datasheet; type A from repeated shorts |
| M5 | Relay/MUX leakage Ileak (+ Ib of open switch) | B | rect. (±pA) or measured offset | 1 pA reed vs 100 pA MUX — directly adds to reading; guard reduces |
| M6 | Relay contact resistance + thermoelectric EMF | B | rect. (±mΩ, ±µV) | mΩ is negligible vs R_shunt but EMF µV adds |
| M7 | PCB/connector surface leakage R_leak | B | rect. or measured | `Ileak=V/R_leak`, guard reduces effective `V` |
| M8 | ADC reference accuracy / TC / noise | B+A | datasheet + measured σ | same as DAC ref but for ADC |
| M9 | ADC INL / gain / offset (post-cal residual) | B | rect. | LSB or ppm |
| M10 | ADC noise (type A) + quantization | A | Gaussian | measured σ at given NPLC/OSR |

### Measure voltage path — sense divider → ADC

| # | Contributor | Type | Notes |
|---|-------------|------|-------|
| V1 | Divider ratio tolerance + TC | B | as S8/S9 |
| V2 | Sense amp (if any) | B+A | as M4 |
| V3 | Input bias/leakage on sense node | B | Ib·R_divider; guard if high-Z |
| V4 | ADC path | B+A | as M8–M10 |

### System / calibration

| # | Contributor | Type | Notes |
|---|-------------|------|-------|
| C1 | Calibration reference standard uncertainty | B | cert value, e.g., 6½-digit DMM 0.0035% + 0.0005% or voltage reference cert |
| C2 | Calibration procedure residual (fit, LUT interpolation) | B/A | residual of linear or piecewise cal |
| C3 | Temperature measurement uncertainty → correction residual | B | sensor accuracy ±1 °C · TC |
| C4 | Time drift / aging (post-cal) | B | ppm/√3 per interval |
| C5 | Thermoelectric EMF (junctions, relays) | B | µV level, reduced by isothermal layout |
| C6 | Dielectric absorption / soakage (post-overload recovery) | B | tested by step recovery |
| C7 | Handling/contamination drift (humidity) | B | enclosure + bake verification |

*Categories not in V1 baseline but noted for completeness: transformer/instrument isolation leakage, cable tribo (type A, measured during flex).*

---

## 3. How uncertainties combine

### 3.1 Uncorrelated RSS (default)

If contributors are independent and expressed as standard uncertainties in the **same units** (volts input-referred, or amps input-referred), combined:

```
u_c = sqrt( u_S1² + u_S2² + … + u_M1² + … + u_A² )

Example (current 100 nA range, input-referred amps, 1σ):
  shunt tol 0.1%/√3 = 0.058% → on 50 nA reading → 29 pA
  shunt TC 250ppm/√3 = 144 ppm → 7.2 pA
  amp Vos 1 µV/1 MΩ = 1 pA → 1 pA
  Ileak 5 pA (rect.) → u=5/√3=2.9 pA
  ADC offset residual 100 nV/1 MΩ=0.1 pA
  Johnson 0.41 pA (type A) → type A term is σ_measured
  u_c = √(29²+7.2²+1²+2.9²+0.1²+0.41²) pA ≈ 29.9 pA (≈60% of reading at 50 nA — dominates by shunt tolerance)
```

*Takeaway:* At mid-range, tolerance/gain terms dominate; at low end, offset/leakage/noise dominate. Quote both %reading and absolute offset.

### 3.2 Including correlations

If DAC and ADC share the same reference, their errors are **correlated** — do not RSS blindly; include `2·ρ·u1·u2` term. If ratiometric (e.g., shunt voltage measured vs DAC reference ratio), reference error cancels partially.

### 3.3 Expanded uncertainty

Report `U = k·u_c` with `k=2` (≈95% Gaussian) and state coverage factor. For non-Gaussian dominant terms, use Monte Carlo per GUM Supplement 1 (simulate using `simulation/python/monte_carlo_uncertainty.py` with distributions).

---

## 4. V1 reporting template (per current / voltage range)

```text
Range 100 nA (FS 100 mV, R=1 MΩ, T=25±3 °C, NPLC=1, 10 Hz BW, post-cal):
  Source V accuracy (at 1.00 V): ±(0.02% reading + 0.01% FS + 2 ppm/°C·ΔT + drift)  [DAC+amp+divider]
  Measure V accuracy (at 1.00 V): ±(0.02% reading + 100 µV + TC)                  [divider+ADC+ref]
  Measure I accuracy (at 50 nA):  u_c = 30 pA (1σ), U = 60 pA (k=2)              [shunt tol + TC + Vos + Ileak + ADC + noise]
                                → ±(0.06% reading + 30 pA offset) equivalent
  Minimum useful I (10σ noise + 3× offset): ≈ 5 pA + 90 pA ≈ 100 pA detection,  ~1 nA quantitative
  Noise (type A, shorted input, 1 Hz BW): 0.13 pA rms (Johnson only) + 0.5 pA system → total 0.52 pA rms
```

*Numbers are placeholders — Phase 2 fills with measured σ and datasheet B values.*

---

## 5. Calibration hierarchy (terminology — correct per metrology)

- **Adjustment:** Change instrument constants (gain/offset LUT) to reduce error.
- **Verification:** Measure against standard without changing constants — pass/fail.
- **Calibration:** Comparison to traceable standard with documented result; may include adjustment and As-Found/As-Left report.
- **Traceable calibration:** Chain to national standard via accredited lab with uncertainty stated. V1 uses *verified* adjustment against a calibrated 6½-digit DMM / precision resistor / voltage reference — traceability depth increases in V1.x.

---

## 6. Phase 2 action

For each range, collect datasheet `a` (±tol) per row, convert to `u=a/√3`, measure type-A σ per `SMOKE_TEST_RESULTS` protocol (shorted input time series, Allan deviation), then compute `u_c`/`U` by RSS and validate by Monte Carlo (`uncertainties` + `numpy` random sampling). Commit script `docs/calculations/uncertainty_budget.py`.

---

*No component promoted. All tolerances/TCs must be cited per `ENGINEERING_RULES.md §2.2` before promotion.*

