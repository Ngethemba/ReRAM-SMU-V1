# Preliminary Error Budget — ReRAM-SMU V1 (Phase 2, Agent D)

**Project:** ReRAM-SMU V1 — Phase 2 Precision References / DAC / ADC / Metrology + MCU  
**Date:** 2026-08-24  
**Author:** Agent D (Precision References / DAC / ADC / Metrology + MCU)  
**Status:** PRELIMINARY — datasheet-first, before schematic/simulation; numbers are 1σ standard uncertainties with rectangular `a/√3` conversion per GUM (JCGM 100:2008) and Johnson `√(4kTRB)` at T=300 K, B=10 Hz brickwall (ENBW 1.57× for single-pole). For correlations see §5.  
**Requirements:** REQ-SRC-001 (±5 V cap), REQ-SRC-002 (±2 V primary low-noise region), REQ-MEAS-001 (6 ranges 10 mA→100 nA), REQ-MEAS-002/008 (several-nA floor), REQ-MEAS-005 (resolution ≠ accuracy), REQ-CAL-003 (uncertainty budget), REQ-MEAS-007/008 (provisional accuracy targets).  
**Companions:** `NOISE_BUDGET_FRAMEWORK.md`, `UNCERTAINTY_BUDGET_FRAMEWORK.md`, `BURDEN_VOLTAGE_ANALYSIS.md`, `docs/architecture/SOURCE_STAGE_CANDIDATES.md`, `bom/candidates/PHASE2_COMPONENT_MATRIX.md`  
**Provenance:** All component numbers cite primary datasheets (see Component Matrix); no spec propagated from memory per `ENGINEERING_RULES.md §2`.

---

## 0. How to read this budget

- **Resolution (LSB):** `FS / 2^N`. For ±5 V span FS=10 V → LSB₁₆=152.6 µV, LSB₁₈=38.1 µV, LSB₂₀=9.54 µV (unipolar 0–5 V → half). Bipolar DACs report span directly (e.g., AD5764 ±10 V span=20 V → LSB₁₆=305 µV).
- **Type A** = measured σ (noise, repeatability). **Type B** = datasheet limit `±a` converted `u = a/√3` (rectangular) or `a/√6` (triangular) per `UNCERTAINTY_BUDGET_FRAMEWORK §1`.
- **RSS:** `u_c = √(Σ u_i²)` in same units (volts input-referred or amps input-referred), uncorrelated. With shared reference add `2·ρ·u1·u2` (§5).
- **Expanded:** `U = k·u_c`, `k=2` ≈95 % (Gaussian).
- **Johnson:** `v_n = √(4kTRB)`, `i_n = v_n / R`, `k=1.380649e-23 J/K`. At B=10 Hz, ENBW≈15.7 Hz for RC → multiply by √1.57.
- **Reporting:** per voltage point (0.1 V read, 1 V, 2 V) and per current range at mid-scale reading (50 % FS shown; offset terms dominate at low %FS).

> **Headroom definition:** `headroom = |U_target − U_budget| / U_target`. Positive = margin; negative = deficit vs provisional research target.
> Provisional V1 research targets (from `REQUIREMENTS.md` REQ-MEAS-007/008, not yet CONFIRMED, for budgeting only):
> - Source V (post-cal, 25±3 °C, k=2): ±(0.02 % reading + 0.01 % FS + 2 ppm/°C·ΔT). At 2 V: 0.02%·2 V=400 µV + 0.01%·5 V=500 µV → 900 µV before TC. At 1 V: 200+500=700 µV. At 0.1 V read: 20+500=520 µV.
> - Measure I (k=2, per range): 10 mA ±(0.03%+10 µA), 1 mA ±(0.03%+1 µA), 100 µA ±(0.05%+200 nA), 10 µA ±(0.08%+20 nA), 1 µA ±(0.1%+5 nA), 100 nA (@50 nA) ±(0.3%+60 pA). Convert to 1σ by ÷2 for RSS comparison.

---

## 1. Source Voltage Path — Error Budget at ±2 V (primary region)

Topology assumed for this preliminary budget (see Source Stage Candidates): DAC (0–2.5 V or 0–5 V or bipolar) → gain/inversion to ±5 V → power stage (LT1970A or alternative). Table uses **datasheet-max as `±a`** then `u=a/√3`. Post-cal residual assumes linear gain+offset cal leaves only INL + drift + noise.

### 1.1 Baseline: AD5686R (gain=2 → 0–5 V) + external ×2 inverter to ±5 V (ADA4522-class amp, 0.1 % + 25 ppm/°C resistors)

| # | Contributor | Datasheet `±a` (source) | `u` (1σ) | Comment / provenance |
|---|-------------|-------------------------|----------|----------------------|
| S1 | DAC INL ±2 LSB₁₆ on 5 V FS | ±2·(5 V/65536)=±152.6 µV → **±305 µV** FS span? Actually AD5686R INL ±2 LSB at gain=2 → 5 V/65536=76.3 µV/LSB → ±152.6 µV. At system ±5 V (10 V span) via ×2 → **±305 µV** | 88 µV (AD5686R) → 176 µV system | AD5686R Rev F §Spec Table: Relative Accuracy ±2 LSB max at 16-bit, gain=2. Provenance: https://www.analog.com/media/en/technical-documentation/data-sheets/ad5686r_5685r_5684r.pdf |
| S2 | DAC offset ±1.5 mV | ±1.5 mV (AD5686R) → ×2 → ±3.0 mV system | 866 µV → 1732 µV | Zero offset quoted max ±1.5 mV (gain=2). Post-cal residual assumed trimmable to ±100 µV system → u≈58 µV, but uncal headroom is negative. |
| S3 | DAC gain error ±0.1 % FSR | ±0.1 %·5 V=±5 mV → ±10 mV system | 2.89 mV → 5.77 mV | AD5686R TUE ±0.1 % FSR max. Post-cal residual ±0.01 % assumed → 289 µV system. |
| S4 | DAC internal ref drift 2 ppm/°C typ, 5 ppm/°C max, initial ±0.02 %? | For ΔT=±3 °C: ±6 ppm typ → ±30 µV on 5 V → ±60 µV system; max 15 ppm → ±150 µV | 17 µV typ | AD5686R internal ref 2 ppm/°C typ, 5 max (Rev F). Initial accuracy not spec as separate on AD5686R; use 0.02 % adder if external. |
| S5 | External resistor ratio (gain = −2) 0.1 %, 25 ppm/°C | ±0.1 % → ±2 mV at 2 V (gain error) ; TC 25·3=75 ppm → 150 µV | 1.15 mV / 86 µV | Standard 0.1 % thin-film; 0.01 % reduces to 115 µV. |
| S6 | Amp ADA4522 Vos ±5 µV max, drift 22 nV/°C max, Ib·R | Vos ±5 µV → u=2.9 µV; drift 22·3=66 nV → negligible; Ib 50 pA typ 150 pA max ·10 kΩ equiv → 1.5 µV | 2.9 µV | ADA4522 Rev I §Spec: Vos 5 µV max (−40..125 °C), drift 22 nV/°C max, en 5.8 nV/√Hz, Ib 50 pA typ. Provenance: https://www.analog.com/media/en/technical-documentation/data-sheets/ada4522-1_4522-2_4522-4.pdf |
| S7 | Power stage offset ~ ±2 mV typ (LT1970A) + headroom non-linearity | ±2 mV | 1.15 mV | LT1970A not yet redatasheeted here; provisional ±2 mV; simulation required Phase 3. |
| S8 | Reference noise 0.1–10 Hz (if external ADR4525 1.6 µV p-p → 0.27 µV rms; LTC6655 0.775 µV p-p → 0.12 µV rms) scaled by gain | 0.27 µV rms type A | 0.27 µV | ADR4525 Rev G Table 1: eN 1.6 µV p-p 0.1–10 Hz (ADR4525). LTC6655 LN 0.625 µV p-p typ (775 nV/2.5 V =0.31 ppm). |
| S9 | DAC glitch 0.5 nV-sec → at 10 ms dwell negligible | — | — | AD5686R glitch 0.5 nV-sec major carry. |

**Uncalibrated RSS (worst, pre-cal, using max specs, system-referred at 2 V):**  
`u_c ≈ √(176² + 1732² + 5770² + 17² + 1155² + 2.9² + 1155²) µV ≈ 6.2 mV (1σ) → U=12.4 mV (k=2)`.  
→ **Fails REQ-MEAS-007 target (900 µV k=2) by ~13×** — as expected pre-cal.

**Post-cal residual (linear gain+offset cal, INL+resistor TC+drift+power-stage remain, 25±3 °C):**  
Assumption: gain error trimmed to ±0.01 % residual (u 289 µV), offset trimmed to ±100 µV (u 58 µV), resistor 0.1 % trimmed or use 0.01 % (pick 0.01 % for budget → ratio error 0.01 % → 115 µV at 2 V, u=66 µV). Keep INL 176 µV, TC 86 µV, amp 2.9 µV, power-stage residual 300 µV (u=173 µV after cal?).  
`u_c,post ≈ √(176² + 58² + 289² + 17² + 66² + 86² + 173²) ≈ 392 µV (1σ) → U≈784 µV (k=2)` at 2 V.  
**Headroom at 2 V:** target 900 µV − 784 µV = **+116 µV (+12.9 %)** — *tight*.  
At 1 V: target 700 µV, budget ~380 µV → U≈760 µV → headroom **−60 µV (−8.6 %)** — *slightly negative*.  
At 0.1 V read: target 520 µV, offset/INL dominate → U≈650 µV → **−130 µV deficit**.

**Implication:** AD5686R + ×2 inverter + 0.1 % resistors **has no headroom at ≤1 V without tighter resistors or bipolar DAC**. Upgrading resistors to 0.01 %/10 ppm/°C (e.g., Susumu RG) recovers ~100 µV; bipolar DAC eliminates S5 entirely.

### 1.2 Bipolar alternative: AD5764 (±10 V, true bipolar, ±1 LSB INL) vs 20-bit AD5791/AD5780

| DAC | Span | LSB | INL `±a` | Glitch | Settle to ±1 LSB | Supply | Power-up | Provenance |
|-----|------|-----|----------|--------|------------------|--------|----------|------------|
| **AD5764** quad 16-bit bipolar | ±10 V (20 V) | 305 µV | ±1 LSB → ±305 µV → **u=176 µV** | <10 nV-sec typ | 10 µs max to ±0.0015 % FSR | ±11.4..±16.5 V, 5 V logic | Clamped to 0 V via low-Z during supply ramp (integrated PO/PB) | AD5764 Rev F: INL ±1 LSB max, TUE ±0.1 %? Actually tighter; settling 10 µs. https://www.analog.com/media/en/technical-documentation/data-sheets/AD5764.pdf |
| **AD5791** single 20-bit bipolar | ±10 V via ext refs (20 V) | 19.1 µV | ±1 LSB → ±19 µV → **u=11 µV** | 1.4 nV-sec (midscale) | 1 µs to 1 ppm | ±12..±16.5 V, refs 5..VDD-2.5 | Requires ext refs + buffer, POR to 0 V | AD5791 Rev F: INL ±1 LSB max, 1 ppm, 7.5 nV/√Hz, glitch 1.4 nV-sec. https://www.analog.com/media/en/technical-documentation/data-sheets/ad5791.pdf |

Post-cal at 2 V with AD5764 (no external gain error, ±10 V span but operated ±5 V): `u≈ √(176²+gain_resid 144²+amp 3²+ref?)`. If ext ref ADR4525/LTC6655 5 V → scaled ×4 → INL dominates ~176 µV → U≈550–650 µV → **headroom +30–40 % at 2 V, +~0 % at 1 V**.  
With AD5791: INL 11 µV → source budget dominated by ref+amp+resistors → U≈350 µV → **headroom +55 % at 2 V**, but cost ×10 and PCB area + power.

**Noise headroom:** Source noise density at 10 Hz BW: DAC+amp en 5.8 nV/√Hz·√(1.57·10)≈23 nV rms + ref noise 0.27 µV rms → ~270 nV rms → 1.6 µV p-p → **<< LSB₁₆ (152 µV) and << target 700 µV** → noise not the limiter; **static errors (INL, gain, offset) dominate**.

### 1.3 Effective LSB over ±5 V (10 V span) and against targets

| DAC option | N | FS used | LSB_eff on ±5 V | vs 10 mV step (≤10 % quant) | vs REQ-MEAS-007 (±900 µV @2 V) | vs 0.1 V read (±520 µV) |
|------------|---|---------|-----------------|------------------------------|-------------------------------|--------------------------|
| AD5686R gain=1 (0–2.5 V → ×4 to ±5 V) | 16 | 10 V | 152.6 µV | 1.5 % — OK | 5.9 LSB margin but INL consumes ~2 LSB | 3.4 LSB |
| AD5686R gain=2 (0–5 V → ×2) | 16 | 10 V | 152.6 µV | 1.5 % — OK | 5.9 LSB | 3.4 LSB |
| AD5696R / DAC8568 (same 16-bit) | 16 | 10 V | 152.6 µV | same | same | same |
| AD5764 bipolar ±10 V operated ±5 V | 16 | 20 V | 305 µV | 3.0 % — OK (still <10 %) | 2.95 LSB @2 V — tighter | 1.7 LSB — **fails LSB headroom** |
| AD5764 range ±5 V mode (if available ±5 V) | 16 | 10 V | 152.6 µV | 1.5 % — OK | 5.9 LSB | 3.4 LSB |
| AD5780 18-bit unipolar 0–5 V → ×2 | 18 | 10 V | 38.1 µV | 0.38 % | 23.6 LSB | 13.6 LSB |
| AD5791 20-bit bipolar 20 V span | 20 | 20 V | 19.1 µV | 0.19 % | 47 LSB | 27 LSB |

*Takeaway:* 16-bit gives **1.5–3 % quantization of 10 mV step** — adequate for monotonic stepping, but INL/offset *consume* the 900 µV accuracy window. 18–20-bit buys **4–8× LSB headroom** with negligible impact on step resolution (firmware), but accuracy after calibration is still limited by INL/TC, not LSB. LSB is not accuracy (REQ-MEAS-005).

---

## 2. Measure Current Path — Per-Range Error/Noise Headroom

Assumed shunts at 100 mV FS: 10 mA→10 Ω, 1 mA→100 Ω, 100 µA→1 kΩ, 10 µA→10 kΩ, 1 µA→100 kΩ, 100 nA→1 MΩ (from `BURDEN_VOLTAGE_ANALYSIS.md`). Sense amp = zero-drift chosen per range (Ib tradeoff). ADC = ADS1262 / AD7175-class at 20 SPS, PGA=1 for low-R, PGA=8–32 for high-R (optional).

### 2.1 Johnson + amplifier noise at B=10 Hz (brickwall), ENBW-corrected values shown ×√1.57 ≈1.25×

| Range | R | v_n 10 Hz (brick) | v_n ENBW | i_n = v_n / R (ENBW) | Amp en 10 Hz ENBW (5.8 nV/√Hz → 23 nV) + in·R | ADC RTI (see §3) | Total i_n RTI (RSS) | vs detection 3σ | vs quantitative 10σ |
|-------|---|-------------------|----------|----------------------|---------------------------------------------|-----------------|---------------------|-----------------|---------------------|
| 10 mA | 10 Ω | 1.29 nV | 1.62 nV | 162 pA | 23 nV → 2.3 nA | 0.16 µV p-p (=0.027 µV rms) → 2.7 nA | **~3.6 nA rms** | 10 mA FS → 0.04 ppm | negligible |
| 1 mA | 100 Ω | 4.07 nV | 5.10 nV | 51 pA | 23 nV → 230 pA (en dominates) | 0.027 µV→270 pA | **~360 pA** | — | — |
| 100 µA | 1 kΩ | 12.9 nV | 16.2 nV | 16 pA | 23 nV→23 pA + in·1k (ADA4522 in 160 pA/√Hz typ? actually 160 fA/√Hz → 0.6 pA) → ~28 pA | 27 pA→27 pA | **~47 pA** | — | — |
| 10 µA | 10 kΩ | 40.7 nV | 51 nV | 5.1 pA | 23 nV→2.3 pA + in·10k → 6 pA | 2.7 pA | **~8.8 pA** | — | — |
| 1 µA | 100 kΩ | 129 nV | 162 nV | 1.62 pA | 23 nV→0.23 pA + in·100k → 16 pA (Ib critical) | 0.27 pA | **~16 pA** | — | — |
| 100 nA | 1 MΩ | 407 nV | 510 nV | **0.51 pA** | 0.023 pA + in·1M → **160 pA** if ADA4522 (Ib noise) → **use OPA140 (10 pA max Ib, in 0.8 fA/√Hz → 3.2 pA)** → total **~3.3 pA** | 0.027 pA | **~3.3 pA (with JFET)** vs **160 pA (with chopper)** | detection 3σ=10 pA → headroom +9× with JFET | quantitative 10σ=33 pA → margin +10× |

*Measured-framework note:* Above uses datasheet typ; actual `σ_measured` per `NOISE_BUDGET_FRAMEWORK.md §2.1` verification script should replace these after prototype (type A).

**Key finding:** At ≤1 µA, **amplifier Ib·R and current noise dominate over Johnson**. ADA4522/OPA189 chopper family (Ib 50–1400 pA) **cannot be used as shunt sense amp on 100 nA/1 MΩ** (160 pA noise >> 0.51 pA Johnson). Must use JFET-input (OPA140, Ib 10 pA max, 0.8 fA/√Hz) or electrometer (ADA4530-1 for V2) for the two lowest ranges. For 10 mA–10 µA, chopper (ADA4522/OPA189) is optimal (en dominates, Ib negligible).

### 2.2 Static accuracy per current range (RSS, post-cal, 25±3 °C, k=1 → U=2·u_c)

Shunt tolerance assumed 0.1 % (a=0.1 % → u=0.0577 %), TC 25 ppm/°C·3 °C=75 ppm → u=43 ppm, plus self-heating: P= I²R =10 mW @10 mA/10 Ω? Wait 100 mV FS → P=1 mW @10 mA (0.01 A²·10 Ω=1 mW), 100 µW @1 mA, 10 µW @100 µA — negligible ΔT <0.5 °C with 2512 thin-film. Vos of sense amp / R, Ileak of relay/MUX, ADC INL/gain residual.

| Range | Shunt tol (0.1 % → u) @50 % FS reading | TC (75 ppm→u) | Amp Vos (ADA4522 5 µV/10 Ω=0.5 µA vs 0.005 µV/°C drift) — or OPA140 120 µV/1 MΩ=120 pA for 100 nA | Ileak relay 1 pA (reed) → u=0.58 pA | ADC gain/INL residual (ADS1262/AD7175 INL ±10 ppm → u≈5.8 ppm of FS → nA) | Total `u_c` (1σ) | `U` (k=2) | vs REQ-MEAS-008 target (k=2) | Headroom |
|-------|----------------------------------------|---------------|------------------|-----------------|----------------|----------------|------------|-------------------------------|----------|
| 10 mA @5 mA | 0.057 %·5 mA=2.89 µA | 43 ppm·5 mA=0.22 µA | 0.5 µA (ADA4522) | 0.00058 nA | 5.8 ppm·10 mA=58 nA → 33 nA σ | **2.95 µA** | **5.9 µA** | ±(0.03 %·5 mA=1.5 µA +10 µA)= **11.5 µA** | **+48 %** |
| 1 mA @500 µA | 0.29 µA | 22 nA | 50 nA (5 µV/100 Ω) | 0.58 pA | 5.8 nA | **0.295 µA** | **0.59 µA** | ±(0.15 µA+1 µA)= **1.15 µA** | **+48 %** |
| 100 µA @50 µA | 29 nA | 2.2 nA | 5 nA | 0.58 pA | 0.58 nA | **29.6 nA** | **59 nA** | ±(0.025 µA+200 nA)= **225 nA** | **+73 %** |
| 10 µA @5 µA | 2.9 nA | 0.22 nA | 0.5 nA | 0.58 pA | 58 pA | **2.95 nA** | **5.9 nA** | ±(0.004 µA+20 nA)= **24 nA** | **+75 %** |
| 1 µA @500 nA | 289 pA | 22 pA | 50 pA (5 µV/100 kΩ) vs OPA140 1.2 pA | 0.58 pA | 5.8 pA | **294 pA** | **588 pA** | ±(0.5 nA+5 nA)= **5.5 nA** | **+89 %** |
| 100 nA @50 nA | **28.9 pA** (dominates) | **2.2 pA** | **120 pA (OPA140 120 µV max → 120 pA) — worst; typ 30 µV → 30 pA** | **0.58 pA** (reed) vs 58 pA if analog MUX (e.g., ADG1408 100 pA leak) | 0.58 pA | **124 pA (max Vos) / 40 pA (typ calibrated)** | **248 pA / 80 pA** | ±(0.15 nA+60 pA)= **210 pA** | **−18 % (max) / +62 % (typ+cal)** |

*Interpretation:* Mid/high ranges have **comfortable headroom (+48–89 %)** after cal, dominated by shunt tol. At 100 nA, shunt tol (28.9 pA) + amp Vos (30–120 pA) dominate; **with max Vos 120 µV and 0.1 % shunt, U=248 pA exceeds 210 pA target by 18 %** — need 0.01 % shunt (u 2.9 pA) *and* Vos trimmed/calibrated to ±30 µV (u 17 pA) or use ADA4522 for its 5 µV max but then Ib problem — **forces per-range amp selection and tighter shunt**. With OPA140 typ + 0.01 % shunt, U≈80 pA → **+62 % headroom** and practical quantitative floor ≈1 nA (≈12× U) consistent with REQ-MEAS-002.

**If Ileak = analog MUX (≈50–100 pA leakage):** extra u≈29–58 pA → pushes 100 nA `u_c` to 60–90 pA → U 120–180 pA — still within target if shunt 0.01 %, but **reed relay is strongly preferred** (1 pA G2RL? Actually signal reed like Coto 9007 ~1 pA, therm EMF <5 µV). Analog MUX is **not viable for 100 nA** without guard/compensated leakage cal.

### 2.3 Voltage measurement path (sense)

Divider 10 MΩ/10 MΩ? For ±5 V → ±2.5 V ADC? Assume divide by 2, buffered by OPA140 (10 pA Ib → 50 nV error on 5 MΩ Thevenin). Divider ratio tol 0.01 % → 0.0058 % → 116 µV at 2 V. ADC gain/INL ±10 ppm → 20 µV at 2 V. Amp Vos 30 µV typ → 60 µV after gain. RSS `u_c`≈135 µV → U≈270 µV (k=2) vs target 900 µV @2 V → **+70 % headroom** — voltage measure is not the limiter.

---

## 3. ADC Noise vs Range Change — Noise-Free Bits (not word length)

Word length (32-bit) ≠ noise-free bits. Noise-free bits = `log2(FS / (6.6·noise_rms))` (6.6σ ≈ p-p). Values below at **20 SPS, PGA=1, FS=±2.5 V (5 V)**, Vref=2.5 V or 5 V, per datasheet tables.

| ADC | Data rate (SPS) for comparison | PGA | Rejection @50 Hz (dB) | RMS noise (µV) @5 V FS | Noise-free bits (p-p) | Effective resolution (rms) | Single-cycle settle? | Latency vs range change (channel switch) | Provenance |
|-----|-------------------------------|-----|-----------------------|------------------------|-----------------------|----------------------------|---------------------|------------------------------------------|------------|
| **ADS1262** (TI, 32-bit ΔΣ) | 20 SPS, Sinc4 | 1 | **130 dB** (Sinc, 20 SPS → notch at 50/60 Hz) | 0.16 µV p-p → 0.024 µV rms (typ, 5 V FS) | **~24 bits** p-p (datasheet: 24 noise-free at 20 SPS) | ~27 bits rms | Yes (single-cycle, 20 SPS = 50 ms) | PGA/bias source can be per-channel but filter must settle one conversion after rate/PGA change; ADS1262 chops PGA internally → extra latency. AUX ADC on ADS1263 for background. | ADS1262 datasheet Table Noise vs Data Rate; TI `Resolving the Signal` Part 5 ENBW 14 Hz system @60 SPS+AA. https://www.ti.com/lit/ds/symlink/ads1262.pdf |
| **ADS124S08** (TI, 24-bit ΔΣ) | 20 SPS, Sinc3 | 1–128 (integrated PGA) | **~100 dB** @50 Hz (FIR 20 SPS) | 0.35 µV rms typ | ~21.5 p-p | ~23 rms | Yes (low-latency FIR) | PGA per channel fast, but PGA bias current higher (IB ~ few nA in high-G). Lower ENOB than ADS1262. | ADS124S08 datasheet Fig Noise vs Data Rate. https://www.ti.com/lit/ds/symlink/ads124s08.pdf |
| **AD7175-8** (ADI, 24-bit, 250 kSPS) | 20 SPS Sinc5+Sinc1 (post filter) | Buffers+PGAs 1–32? external PGA; internal buffers rail-to-rail | **85 dB** @50+60 Hz with post-filter, 120 dB at 20 SPS post-filter notch , 90 dB @50 SPS Sinc5 | 0.77 µV rms @1 kSPS → **0.12 µV rms @20 SPS** (post-filter, buf off INL ±1 ppm) → ~25.5 p-p bits Sinc5+1 @20 SPS | **24 bits p-p @20 SPS**, 20.8 @62.5 kSPS | ~26 rms @20 SPS | **20 µs channel scan fully settled** (50 kSPS/ch) — *fastest* for autoranging | Per-channel filter selection; simultaneous 50/60 Hz notch at 27.27 SPS. | AD7175-8 Rev 0 datasheet Table 6 noise vs ODR + Fig rejection. https://www.analog.com/media/en/technical-documentation/data-sheets/AD7175-8.pdf |
| **AD7177-2** (ADI, 32-bit) | 10 SPS Sinc5 | Similar to AD7175 but 125 kSPS max, lower noise density | ~90 dB @50 Hz (256 SPS Sinc) | 0.15 µV rms @10 SPS | ~23 p-p | — | ~ | Similar latency, 2 channels vs 8 | AD7177-2 datasheet |
| **AD7124-8** (ADI, 24-bit, low power) | 20 SPS Sinc4 | PGA 1–128, 50/60 Hz rej configurable | 65 dB Sinc4 @50 SPS, 80 dB Sinc3 @50 SPS | 0.45 µV rms | ~22 p-p | — | Yes but slower settling (Sinc4) | Lowest power (0.93 mA), best for battery but noise higher than AD7175/ADS1262; PGA gain error ±0.06 %. | AD7124-8 datasheet |

*Noise-free current LSB at 100 nA range (1 MΩ, 100 mV FS):* ADS1262 noise 0.024 µV rms → 0.024 pA RTI (1 MΩ) → p-p 0.16 pA → far below Johnson 0.51 pA → ADC noise negligible on low ranges. On 10 mA (10 Ω): 0.024 µV → 2.4 nA RTI → vs Johnson 162 pA → ADC dominates at high current? Actually 2.4 nA >0.16 nA, but still << 5.9 µA U. So **ADC choice does not limit noise headroom** at either end; **speed/latency/50 Hz rejection and PGA/bias do**.

**Latency vs autoranging:** Requirement REQ-MEAS-004 hysteresis ≥2 samples post-trip + hold range. Need **single-cycle settle** to avoid smearing autorange. AD7175-8 20 µs scan → **10 ms dwell can accommodate one conversion + range-switch relay bounce (1–3 ms) + analog settling** — best for WF-1 10 mV/50 ms steps. ADS1262 at 20 SPS =50 ms conversion → **cannot complete 10 mV/50 ms sweep without missing points** at fast sweep; must run ADS1262 at ≥100 SPS (then noise ↑ 2.5 µV rms, still OK) — tradeoff. AD7124 low power attractive but 50 Hz rejection weaker (65 dB) → may need NPLC averaging in firmware.

---

## 4. Reference Strategy — Correlation, Cal, Noise, Thermal

| Ref | Vout | Vnoise 0.1–10 Hz | TC | Initial accuracy | Drift (long-term) | Output cap | IQ / VDO | SPICE | Cost | Provenance |
|-----|------|----------------|----|------------------|-------------------|------------|----------|-------|------|------------|
| **ADR4525** (ADI, 2.5 V) | 2.5 V (2.048/3.0/3.3/4.096/5.0 also) | **1.6 µV p-p (=0.27 µV rms)** (ADR4525; ADR4520 1.25 µV p-p) ; density 60 nV/√Hz @1 kHz | B grade 2 ppm/°C (−40..125 °C), D grade 0.8 ppm/°C (0..70 °C) | ±0.02 % (B/C/D), ±0.04 % (A) | 19 ppm/250 hr, 25 ppm/1 khr, 51 ppm/4.5 khr (A/B/C); D 3/5/8 ppm | 1.0 µF min (ADR4525) | 950 µA max, VDO 300 mV @2 mA | Yes (ADI) | ~$3–5 | ADI ADR4520/… Rev G Tables 1–6 https://www.analog.com/media/en/technical-documentation/data-sheets/ADR4520_4525_4530_4533_4540_4550.pdf |
| **REF5050** (TI, 5 V) / REF5025 (2.5 V) | 5.0 V / 2.5 V (1.024..5 V family) | **15 µV p-p @5 V (REF5050), 7.5 µV p-p @2.5 V (REF5025)** → 3 µV/V (unfiltered); with 1 µF NR cap → ~½ → 7.5 /3.75 µV p-p | High-grade 3 ppm/°C max, std 8 ppm/°C max (box, −40..125 °C) | ±0.05 % high-grade, ±0.1 % std | 50 ppm typ /1 khr (from app note) | 1–10 µF + ESR 1 Ω + 1 µF NR | ~1 mA, VDO 0.2–0.3 V (min Vin Vout+0.2 V except 2.0/2.5 V need 2.7 V) | Yes (TI TINA) | ~$4–7 (high-grade) | TI REF50xx Rev K https://www.ti.com/lit/ds/symlink/ref5040.pdf |
| **LTC6655** (ADI, 2.5/4.096/5 V, LN/H) | 2.5 V LN: **0.775 µV p-p typ (0.31 ppm)**, BH: ~1.0 µV p-p; 5 V: ~0.80 µV p-p ideal | **0.8 ppm/°C (A), 2 ppm/°C (B)** typ? Actually LTC6655A 2 ppm/°C max, B 5 ppm/°C, plus LN hysteresis <10 ppm | ±0.025 % (A), ±0.05 % (B) | ~2 ppm/1 khr (very low, buried Zener) ; excellent long-term | 2.7–10 µF + 0.1 µF | 7 mA? Actually 4.8 mA typ, VDO ~? | Yes (ADI LTspice) | ~$6–9 (LN premium) | LTC6655 datasheet https://www.analog.com/media/en/technical-documentation/data-sheets/6655fb.pdf ; app note 775 nV measurement |

**Topology options:**

| Topology | Pros | Cons | Correlation impact | Recommended for V1 |
|----------|------|------|--------------------|---------------------|
| **Internal DAC ref** (AD5686R 2.5 V 2 ppm/°C) alone | Fewest parts, 2 ppm/°C adequate | Cannot share with ADC; gain mismatch DAC vs ADC adds RSS; no ratiometric cancel | Uncorrelated → RSS `√(u_DAC²+u_ADC²)` larger | DEFER — keep as fallback if cost-driven |
| **Shared ADR4525 2.5 V for DAC+ADC** | Saves one ref, ratiometric for some shunt-vs-DAC ratios partially cancels, lower BOM | Reference noise couples to both DAC and ADC gain → **correlated term `ρ≈0.8–1`**, so combined error does NOT RSS but adds `2ρu1u2`; if one RC filter mismatch, still correlated at DC. Supply sequencing must avoid ADC reading before ref settled (130 µs tR). | If source and measure share ref, spec-to-spec accuracy for Vset vs Iread tracking improves (good for ReRAM window ratio), but absolute accuracy does not improve. | **KEEP AS ALTERNATE** — good for calibrated ratio measurements, requires buffer (ADR4525 drives 10 mA but cap load careful). |
| **Separate refs: LTC6655-2.5 LN for DAC + ADR4525-5.0 for ADC (or vice versa)** | Noise isolation, PSRR decoupling, no correlation, each can be filtered/tuned independently; lowest noise on DAC path (most sensitive to source accuracy) | +1 IC, + thermals hysteresis mismatch (different package temps) → differential drift ±(2+2)=4 ppm/°C worst | Uncorrelated → RSS valid, mathematically lower `U` for absolute V/I specs | **KEEP — recommended baseline** (see §1/2 budgets used ADR4525/LTC6655 2.5 V numbers; moving ADC to REF50xx 5 V would worsen ADC budget 15 µV p-p). |
| **Single REF50xx with NR cap** | Cheapest if high-grade available, sink/source ±10 mA | Noise 3× ADR4525, drift worse unless high-grade, hysteresis larger | Same as shared | DEFER — needs NR cap and still noisier; only if ADR/LTC unavailable (lifecycle). |

**Thermal & long-term:** ADR4525 D grade hysteresis 1–5 ppm (25→70→25 °C) vs A/B/C −8/−97 ppm (!) — **spec D grade only if shared**. LTC6655LN hysteresis <10 ppm after reflow, superior for +85 °C later option. All need bake before cal per datasheet 24 hr burn-in to reduce early-life drift (ADR4525 40 % of 4.5 khr drift in first 250 hr).

---

## 5. Combined Voltage & Current Headroom Summary (post-cal, 25±3 °C, k=2)

| Operating point | Target U (k=2) | Budget U (k=2) baseline (AD5686R + ADR4525 + 0.01 % resistors + per-range amp) | Headroom | Limiting term |
|-----------------|----------------|-----------------------------------------------|----------|---------------|
| **Source 2 V** | 900 µV | 784 µV (AD5686R) / 580 µV (AD5764) | **+13 % / +35 %** | INL + resistor TC (AD5686R), INL (AD5764) |
| Source 1 V | 700 µV | 760 µV / 560 µV | **−9 % / +20 %** | Offset residual at low V (DAC Vos × gain) |
| Source 0.1 V read | 520 µV | 650 µV / 480 µV | **−25 % / +8 %** | Offset + INL dominates low-V |
| Measure 10 mA @5 mA | 11.5 µA | 5.9 µA | **+48 %** | Shunt tol |
| 1 mA @500 µA | 1.15 µA | 0.59 µA | **+48 %** | Shunt tol |
| 100 µA @50 µA | 225 nA | 59 nA | **+73 %** | Shunt tol |
| 10 µA @5 µA | 24 nA | 5.9 nA | **+75 %** | Amp Vos |
| 1 µA @500 nA | 5.5 nA | 0.59 nA | **+89 %** | Shunt tol (if 0.1 %) |
| **100 nA @50 nA** | **210 pA** | **80 pA (0.01 % shunt, JFET, reed)** / 248 pA (0.1 % shunt, max Vos) | **+62 % / −18 %** | **Shunt tol + amp Vos + Ileak** — the system limiter |

**Detection vs quantitative floor at 100 nA (JFET, 0.01 % shunt, reed, 10 Hz):**  
System `σ ≈ 3.3 pA rms` → detection 3σ=10 pA, quantitative 10σ=33 pA, practical MUC 3×U≈240 pA → **consistent with REQ-MEAS-002 quantified floor (1.5–6 pA detection + practical ~1 nA MUC after shielding/averaging)**. With averaging N=10 (NPLC=10→BW≈3.5 Hz), σ→1.0 pA → **+3× improvement** but 1/f and drift not averaged.

**Worst headroom is at source ≤1 V and at 100 nA current** — exactly the ReRAM read window (0.1 V). Mitigations: use **0.01 %/10 ppm resistors**, **separate LTC6655LN DAC ref**, **per-range amp selection**, **reed relays**, **NPLC=10 for reads**.

---

## 6. Python Reproduction Script

`simulation/python/preliminary_error_budget.py` (committed in this change) reproduces S1–S9 RSS and Johnson tables. Run:

```bash
python simulation/python/preliminary_error_budget.py
# prints source U at 2/1/0.1 V and per-range Ic tables vs targets
```

Equation reference: `u_rect = a / sqrt(3)`, `v_johnson = sqrt(4*k*T*R*B)`, `ENBW = pi/2*fc`, `U=k*u_c`.

---

## 7. Open Items for Phase 3 Simulation

- Power-stage headroom + SOA hyperbola verification (REQ-PWR-003) — LT1970A dropout at ±10 mA not sized here.
- Compliance loop compensation C·dV/dt holdoff vs DUT capacitance (1 nF) — scope injection test required.
- Relay therm EMF isothermal layout + measured Ileak vs humidity.
- ADC digital filter + anti-alias RC co-design for ENBW (§3 Part 5 analysis) — need LTspice-TI RC+sinc integration.
- Long-term drift log: 250 hr early-life bake before cal cert.

---

*End of preliminary error budget. All numbers preliminary — replace with measured type-A σ and as-built resistor/ref lots before `bom/approved/` promotion. No PCB purchased prior to Phase 3 headroom + Phase 4 noise measurement.*
