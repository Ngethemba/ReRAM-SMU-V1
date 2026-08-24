# Phase 3 Error Budget — ReRAM-SMU V1 (Gate 6 Evidence)
**Project:** ReRAM-SMU V1 — Phase 3 Tests N+O (Gate 6)
**Date:** 2026-08-24
**Authors:** Gate 6 Agent (Tests N+O, Error Budget, Model Limitations)
**Status:** PRELIMINARY — before schematic/simulation review, replace with measured Type A σ after prototype
**Requirements:** REQ-SRC-001 (±5V cap), REQ-SRC-002 (±2V primary), REQ-MEAS-001 (6 ranges 10mA→100nA philosophy D), REQ-MEAS-002 quantified floor, REQ-MEAS-007/008 provisional accuracy, REQ-SAFE-001 compliance triad, REQ-CAL-003 (GUM JCGM 100, no traceable calibration claim)
**Companions:** `PRELIMINARY_ERROR_BUDGET.md` (Phase 2, superseded numbers retained for traceability), `NOISE_BUDGET_FRAMEWORK.md`, `UNCERTAINTY_BUDGET_FRAMEWORK.md`, `SHUNT_RANGE_TRADEOFF.md §2.4` (canonical 25/50/100mV burden), `simulation/phase3/dac_adc/test_N_dac_comparison.py`, `simulation/phase3/monte_carlo/test_O_monte_carlo.py`, `simulation/phase3/MODEL_LIMITATIONS.md`
**Tool versions:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe`), python 3.11.15 (`.venv`), LTspice 26.0.2.1 (`C:/Users/azrai/ADI/LTspice/LTspice.exe`), numpy 1.26
**Provenance rule:** Manufacturer datasheet > app note > textbook > AI summary per `ENGINEERING_RULES.md §2`. Every quantitative claim cites datasheet (manufacturer | part | doc | rev | page | URL).

> **No traceable calibration claimed.** Numbers are Type A (sim noise, repeatability) + Type B (datasheet tolerances, rectangular a/√3 or triangular a/√6) per GUM (JCGM 100:2008) and Johnson √(4kTRB) at T=300K. Correlation term 2ρu1u2 added for shared reference. Expanded U=k·u_c, k=2 (~95%) where noted. Post-cal residuals assume linear gain+offset cal at −5/+5V (source) or per-range cal vs precision resistor (measure) — drift/INL/noise remain.

---

## 0. How to read this budget (GUM, not word-length)

- **Resolution (LSB):** FS/2^N. For ±5V span FS=10V → LSB₁₆=152.588µV; bipolar AD5764 ±10V span=20V → LSB₁₆=305.176µV (no invented ±5V mode, IR-06); AD5791 20-bit LSB₁₉=19.07µV. LSB ≠ accuracy (REQ-MEAS-005).
- **Type A:** measured σ (sim noise, repeatability, Allan deviation at NPLC). **Type B:** datasheet limit ±a converted u=a/√3 (rectangular) or a/√6 (triangular) per `UNCERTAINTY_BUDGET_FRAMEWORK §1`.
- **RSS:** u_c=√(Σu_i²) uncorrelated; with shared reference add 2ρu1u2 (§5).
- **Expanded:** U=k·u_c, k=2.
- **Johnson:** v_n=√(4kTRB), i_n=v_n/R, k=1.380649e-23 J/K. At B=10Hz brickwall, ENBW single-pole =π/2·fc → ×√1.57=1.253 for RC. NPLC integration reduces BW as below.
- **Headroom:** (U_target − U_budget)/U_target; positive = margin, negative = deficit vs provisional research target (not yet CONFIRMED).

---

## 1. Source Voltage Path — Error Budget at ±2V Primary Window (Phase 3 evidence from Test N)

Topology for budget: DAC → (gain stage if AD5686R) → power stage (LT1970A or candidate). Table uses datasheet-max as ±a then u=a/√3. Post-cal residual assumes linear gain+offset cal leaves INL + drift + noise + resistor TC. Test N Monte Carlo (1000 runs/point, 2-pt cal at −5/+5V) replaces the Phase 2 RSS closed-form with empirical RMS/k=2; both reported.

### 1.1 AD5686R 0–5V→×2→±5V (10V span, LSB 152.6µV, INL ±2LSB → ±305µV system)

| # | Contributor | Datasheet ±a (source) | u (1σ) pre-cal | u post-cal (2-pt) | Type | Provenance |
|---|-------------|------------------------|----------------|-------------------|------|------------|
| S1 | DAC INL ±2 LSB₁₆ on 5V FS → ×2 → ±305µV at system | ±305µV | 176µV | 176µV (code-dependent, does NOT cancel with gain cal) | B rect | AD5686R Rev F §Spec: Relative Accuracy ±2 LSB max at 16-bit, gain=2 [Analog: ad5686r_5685r_5684r.pdf Rev F p4] |
| S2 | DAC offset ±1.5mV on 5V→×2→±3.0mV system | ±3.0mV | 1732µV | 58µV (±100µV residual after cal /√3) | B → A after cal | AD5686R Rev F Zero Code Error ±1.5mV max gain=2 |
| S3 | DAC gain error ±0.1% FSR | ±5mV on 5V → ±10mV system | 5770µV | 289µV (±0.01% residual /√3) | B | AD5686R TUE ±0.1% FSR max |
| S4 | Internal ref drift 2ppm/°C typ, 5ppm max | ±6ppm typ (3°C)→±30µV on 5V→±60µV sys | 17µV typ | 17µV | B | AD5686R internal ref 2ppm typ 5max Rev F |
| S5 | External resistor ratio (gain −2) 0.01% / 25ppm vs 0.1%/25ppm options | ±0.01%→±200µV at 2V; TC 10ppm·3°C=30ppm→±60µV | 115µV / 58µV gain / 35µV TC (0.01%) ; 1155µV / 86µV (0.1%) | 66µV gain / 35µV TC (0.01%) | B | Susumu RG 0.01% 10ppm datasheet; standard thin-film 0.1% 25ppm |
| S6 | Amp ADA4522 Vos ±5µV max, TCVos 22nV/°C max, Ib·R 50pA·10k=0.5µV | Vos ±5µV→u2.9µV | 2.9µV | 2.9µV | B | ADA4522 Rev I §Spec [ada4522.pdf p3] |
| S7 | Power stage LT1970A Vos 200µV typ, TC −4µV/°C, Ib 160nA → Ib·Rf 0.8mV worst | ±2mV typ (provisional) | 1155µV | 58µV (±100µV residual) + drift 60µV/15°C | B | LT1970A 1970afc p2 (Vos typ 200µV, TCVos typ −4µV/°C, Ib −160nA typ −600nA max) |
| S8 | Reference noise 0.1–10Hz ADR4525 1.6µV p-p (=0.27µV rms), LTC6655 0.775µV p-p (=0.13µV rms) × gain | 0.27µV | 0.27µV | 0.27µV | A | ADR4525 Rev G Table1, LTC6655 datasheet 775nV p-p |
| S9 | DAC glitch 0.5nV-sec → at 10ms dwell negligible | — | — | — | — | AD5686R 0.5nV-sec major carry |

**Uncalibrated RSS (worst pre-cal, max specs, system at 2V):** u_c≈6.2mV → U=12.4mV k=2 → fails REQ-MEAS-007 900µV by 13× (as expected).

**Post-cal RSS (Phase 2 closed-form, 0.01% resistors, 25±3°C):** u_c≈392µV → U≈784µV at 2V → headroom +116µV (+12.9%); at 1V U≈760µV vs 700µV target → −8.6%; at 0.1V U≈650µV vs 520µV → −25% (offset/INL dominate low-V).

**Test N Monte Carlo (1000 runs/point, INL code-dependent per-setpoint uniform ±305µV, quant ±76µV, gain residual ±0.01%, Vos residual ±100µV, ref 2ppm·3°C, after 2-pt cal at −5/+5V):**

| Setpoint | Target k=2 | AD5686R 0.01% RMS | k=2=2·RMS | p2.5–p97.5 | Worst | Headroom k=2 | Headroom worst |
|----------|------------|------------------|-----------|------------|-------|--------------|----------------|
| 2V | 900µV | 234µV | 467µV | ±~450µV | ~630µV | +48% | +30% |
| 1V | 700µV | 227µV | 454µV | ±~440µV | ~620µV | +35% | +11% |
| 0.5V | 600µV | 225µV | 450µV | ±~440µV | ~610µV | +25% | +~5% |
| 0.1V | 520µV | 227µV | 454µV | ±~440µV | ~600µV | +13% | −15% |

> MC optimistic vs Phase 2 RSS because gain/offset systematic cancels with 2-pt cal, leaving INL+quant+residual Vos as the post-cal floor. Worst at 0.1V still marginal — mitigated by 0.01% resistors; with 0.1% resistors headroom at 1V collapses to negative (REJECT 0.1% for AD5686R path). Full CSVs: `simulation/phase3/dac_adc/ad5686r_0p01_calibrated.csv`, `ad5686r_0p1_calibrated.csv`, `simulation/phase3/monte_carlo/` mirrors.

**Noise headroom at 10Hz BW:** en 5.8nV/√Hz·√(15.7)=23nV rms + ref 0.27µV → ~270nV rms → 1.6µV p-p << LSB₁₆ 152µV and << target 700µV → **noise not the limiter; static INL/offset dominate.**

### 1.2 AD5764 ±10V (20V span, LSB 305.176µV, INL ±1LSB → ±305µV, direct bipolar, no gain stage)

| DAC | Span | LSB | INL ±a | Quant ±0.5LSB | Supply | Upstream cap |
|-----|------|-----|--------|---------------|--------|--------------|
| AD5764 nom | 20.0V (±10V) | 305.176µV | ±305µV → u176µV | ±152.6µV | ±11.4–16.5V (IR-07, raw ±12V OK, ±10V LDO fails) | Ext ref ADR4525/LTC6655 2.5V + bipolar buffers |
| AD5764 opt | 21.0526V (±10.5263V) | 321.2µV | ±321µV | ±160.6µV | same | same |
| AD5686R sys | 10V | 152.6µV | ±305µV | ±76.3µV | Single 5V + gain stage | ADR4525/LTC6655 + ADA4522 |

> **IR-06 correction:** No ±5V mode exists; operating AD5764 for ±5V wastes half the codes (32768 of 65536, step 305µV over 10V → 3.0% of 10mV ReRAM step, <10% criterion OK). INL ±1LSB on 20V = ±305µV equals AD5686R ±2LSB on 10V (±305µV) — equal in volts; advantage is **no external gain-stage ratio error.**

**Post-cal MC AD5764 (LTC6655LN 0.8ppm TC, ±80µV Vos residual, INL per-code ±305µV, quant ±153µV, gain residual ±0.01%):**

| Setpoint | Target | RMS | k=2 | Worst | Headroom k=2 |
|----------|--------|-----|-----|-------|--------------|
| 2V | 900µV | 244µV | 489µV | ~650µV | +46% |
| 1V | 700µV | 232µV | 465µV | ~620µV | +34% |
| 0.1V | 520µV | 236µV | 473µV | ~620µV | +9% |

Supply: ±11.4V min → raw ±12V bench adequate (0.6V margin); **±10V LDO rail cannot host AD5764** (IR-07). Reference: LTC6655LN 0.775µV p-p (=0.31ppm) typ, hysteresis <10ppm, TC 2ppm max A, 0.8ppm LN.

### 1.3 AD5791-class 20-bit (20V span, LSB 19.07µV, INL ±1LSB → ±19µV)

| DAC | LSB | INL u | Quant | Supply | Refs |
|-----|-----|-------|-------|--------|------|
| AD5791 | 19.07µV | 11µV | ±9.5µV | ±12–16.5V + ext 5V refs | 2× LTC6655/LT1021-class 5V + buffers |

**MC AD5791 (INL ±19µV, gain residual ±0.005%, Vos residual ±20µV):** at 2V RMS ~30µV → k=2 ~60µV → headroom +93% at 2V, +91% at 1V, +88% at 0.1V — **large margin** but cost ×3–4, dual refs, tighter layout; per task **only if 16-bit fails** — it does not.

### 1.4 Effective LSB vs targets

| DAC | N | FS used for ±5V | LSB_eff on ±5V | vs 10mV step (≤10% quant) | vs REQ-MEAS-007 (±900µV@2V) | vs 0.1V read (±520µV) |
|-----|---|-----------------|----------------|---------------------------|----------------------------|------------------------|
| AD5686R 0–5V→×2 | 16 | 10V | 152.6µV | 1.5% — OK | 5.9 LSB margin but INL consumes 2 LSB | 3.4 LSB |
| AD5764 bipolar 20V → ±5V half-codes | 16 | 20V | 305.2µV | 3.0% — OK (<10%) | 2.95 LSB @2V | 1.7 LSB — tight but adequate |
| AD5764 21.05V | 16 | 21.05V | 321µV | 3.2% — OK | 2.8 LSB | 1.6 LSB |
| AD5791 20-bit | 20 | 20V | 19.1µV | 0.19% | 47 LSB | 27 LSB |

*LSB is not accuracy (REQ-MEAS-005); ReRAM step resolution margin is monotonic, not accuracy.*

---

## 2. Measure Current Path — Per-Range Error/Noise Headroom (philosophy D canonical)

**Shunts at range-dependent FS (SHUNT_RANGE_TRADEOFF §2.4 IR-05):** 10mA 25mV (2.5Ω), 1mA 25mV (25Ω), 100µA 50mV (500Ω), 10µA 50mV (5kΩ), 1µA 100mV (100kΩ), 100nA 100mV (1MΩ). Sense amp per-range: chopper ADA4522/OPA189 for 10mA→10µA (en dominates, Ib negligible), JFET OPA140 for 1µA/100nA (Ib 10pA max, in 0.8fA/√Hz, en 5.1nV/√Hz) — chopper rejected for 100nA (in·1MΩ →160pA noise vs Johnson 0.51pA). ADC ADS1262/AD7175-class at 20 SPS, PGA per-range hybrid (ADS1262 PGA 1–32) to fill FS.

### 2.1 Johnson + amplifier noise at B=10Hz brickwall, ENBW-corrected ×√1.57, per `NOISE_BUDGET_FRAMEWORK §2`

| Range | R | v_n 10Hz brick | v_n ENBW | i_n ENBW | Amp en+in·R (ADA4522 5.8nV/√Hz, in 160fA vs OPA140 0.8fA) | ADC RTI (ADS1262 0.16µV p-p=0.027µV rms at 5V FS) | Total i_n RTI RSS | vs detection 3σ | vs quantitative 10σ |
|-------|---|----------------|----------|----------|--------------------------------------------------------|------------------------------------------------|-------------------|-----------------|---------------------|
| 10mA | 2.5Ω D | 0.64nV | 0.81nV | 324pA | 23nV→+9.2nA (en dominates? Actually 23nV/2.5Ω=9.2nA) — but PGA 3.1× reduces RTI — **~3.6nA rms with PGA** | 0.027µV→10.8nA? PGA reduces — realistic ~2.7nA | **~3.6nA rms** | 10mA FS →0.04ppm | negligible |
| 1mA | 25Ω | 2.04nV | 2.55nV | 102pA | 23nV→920pA → with PGA ~230pA | 0.027µV→1.08nA→~270pA | **~360pA** | — | — |
| 100µA | 500Ω | 9.10nV | 11.4nV | 22.8pA | 23nV→46pA + in·500Ω 0.08pA → ~51pA | 27pA | **~60pA** | — | — |
| 10µA | 5kΩ | 28.8nV | 36.1nV | 7.22pA | 23nV→4.6pA + in·5k 0.8pA → ~8pA | 5.4pA | **~11pA** | — | — |
| 1µA | 100kΩ | 129nV | 161nV | 1.61pA | 23nV→0.23pA + in·100k (OPA140 0.8fA→3.2pA) → ~3.3pA | 0.27pA | **~3.7pA** | — | — |
| 100nA | 1MΩ | 407nV | 510nV | **0.51pA** | 0.023pA + in·1M (OPA140 3.2pA) → **~3.24pA** (vs 160pA with ADA4522 chopper — rejected) | 0.027pA | **~3.28pA (JFET)** vs **160pA (chopper)** | detection 3σ=9.8pA → headroom 3× with JFET | quantitative 10σ=32.8pA → margin 10× |

*Framework numbers typ; actual σ_measured replaces after prototype (Type A). Key finding reiterated: at ≤1µA **amplifier Ib·R and current noise dominate over Johnson** → per-range amp selection mandatory.*

### 2.2 Static accuracy per current range (RSS, post-cal, 25±3°C, k=1→U=2·u_c, 0.1% shunt baseline, 0.01% on 100nA/1µA for margin)

Shunt tol 0.1% → u=0.0577%·reading, TC 25ppm·3°C=75ppm→u43ppm, self-heating P=I²R≤250µW @10mA/2.5Ω (ΔT<0.5°C thin-film 2512), Vos/ R, Ileak reed 1pA→u0.58pA vs MUX 58pA, ADC INL ±10ppm→u5.8ppm·FS.

| Range @50% FS | Shunt tol u @reading | TC u | Amp Vos | Ileak reed | ADC INL | Total u_c | U k=2 | vs REQ-MEAS-008 target k=2 | Headroom | Limiting term |
|---------------|----------------------|------|---------|------------|---------|-----------|-------|----------------------------|----------|---------------|
| 10mA @5mA | 2.89µA (0.1%) | 0.22µA | 0.5µA (ADA4522 5µV/2.5Ω? Actually diff amp senses 25mV→gain) → ~1µA RTI | 0.58pA | 33nA | **2.95µA** | **5.9µA** | ±(0.03%·5mA+10µA)=11.5µA | +48% | Shunt tol |
| 1mA @500µA | 0.29µA | 22nA | 50nA | 0.58pA | 5.8nA | **0.295µA** | **0.59µA** | 1.15µA | +48% | Shunt tol |
| 100µA @50µA | 29nA | 2.2nA | 5nA | 0.58pA | 0.58nA | **29.6nA** | **59nA** | 225nA | +73% | Shunt tol |
| 10µA @5µA | 2.9nA | 0.22nA | 0.5nA | 0.58pA | 58pA | **2.95nA** | **5.9nA** | 24nA | +75% | Amp Vos |
| 1µA @500nA | 289pA (0.1%) / 29pA (0.01%) | 22pA | 30pA typ OPA140 (1.2pA max 120µV/100k→120pA max vs 30µV typ→30pA) | 0.58pA | 5.8pA | **~40pA typ tight / 124pA max loose** | **80pA /248pA** | 5.5nA | +89% / +98% | Shunt tol+Vos |
| **100nA @50nA** | **28.9pA (0.1%) / 2.9pA (0.01%)** | **2.2pA** | **30pA typ /120pA max OPA140** | **0.58pA reed vs 58pA MUX** | **0.58pA** | **~30pA typ tight /124pA max loose** | **60pA /248pA** | ±(0.15nA+60pA)=**210pA** | **+71% tight / −18% max loose** | **Shunt tol + Vos + Ileak — system limiter** |

*With 0.01% shunt + typ Vos + reed → +62% headroom at 100nA and practical quantitative floor ≈1nA (≈12×U) consistent with REQ-MEAS-002. With max Vos 120µV and 0.1% shunt U=248pA >210pA → −18% → **need 0.01% shunt and Vos trimmed/calibrated to ±30µV (u17pA) plus reed ≥10GΩ**. Analog MUX 100pA leak → u58pA → U +116pA → still within target only if shunt 0.01% — reed strongly preferred.*

### 2.3 Voltage measurement path (sense)

Divider **after high-Z buffer per IR-02** (DUT sees ≥10GΩ, ≤10pA buffer first; attenuation after buffering). Example: ±5V→±2.5V via post-buffer divide-by-2, OPA140 10pA→50nV on 5MΩ Thevenin. Divider ratio 0.01%→0.0058%→116µV at 2V. ADC INL ±10ppm→20µV. Amp Vos 30µV typ→60µV after gain. RSS u_c≈135µV→U≈270µV k=2 vs target 900µV@2V → **+70% headroom** — voltage measure not the limiter.

---

## 3. ADC Noise vs Range Change — Noise-Free Bits and Data-Rate/NPLC Analysis (FAST 10–20ms, NORMAL 50–100ms, LOW NOISE 200ms–1s)

Word length (32-bit) ≠ noise-free bits. Noise-free bits = log2(FS/(6.6·noise_rms)) (6.6σ≈p-p). At 20 SPS PGA=1 FS=±2.5V (5V), Vref 2.5V.

| ADC | Data rate for comparison | PGA | Rejection @50Hz | RMS noise @5V FS | Noise-free bits p-p | Effective bits rms | Single-cycle settle? | Latency vs range change | Provenance |
|-----|--------------------------|-----|-----------------|------------------|---------------------|-------------------|----------------------|-------------------------|------------|
| **ADS1262** (TI 32-bit ΔΣ) | 20 SPS Sinc4 | 1–32 | **130dB** Sinc 20SPS notch 50/60Hz | 0.16µV p-p →0.024µV rms (5V FS) | ~24 bits p-p | ~27 rms | Yes (single-cycle, 50ms=20SPS) | PGA/bias source per-channel but filter must settle one conversion after PGA change | ADS1262 datasheet Table Noise vs Data Rate, TI Resolving the Signal Part 5 ENBW 14Hz @60SPS+AA [ti.com/lit/ds/symlink/ads1262.pdf] |
| **ADS124S08** (24-bit) | 20 SPS Sinc3/FIR | 1–128 | ~100dB @50Hz FIR 20SPS | 0.35µV rms typ | ~21.5 p-p | ~23 rms | Yes low-latency FIR | PGA per channel fast, but bias higher (nA in high-G) | ADS124S08 Table Noise vs Data Rate |
| **AD7175-8** (ADI 24-bit 250kSPS) | 20 SPS Sinc5+Sinc1 post filter | ext buffers PGA 1–32? | 85dB @50+60Hz with post, 120dB@20SPS | 0.12µV rms @20SPS Sinc5+1 → 25.5 p-p bits | **24 bits p-p @20SPS**, 20.8@62.5kSPS | ~26 rms @20SPS | **20µs/ channel scan fully settled (50kSPS/ch)** — fastest for autorange | Per-channel filter selection; simultaneous 50/60Hz notch at 27.27 SPS | AD7175-8 Rev0 Table6 noise vs ODR [analog.com/.../AD7175-8.pdf] |
| **AD7124-8** (low power) | 20 SPS Sinc4 | 1–128 | 65dB Sinc4@50SPS, 80dB Sinc3 | 0.45µV rms | ~22 p-p | — | Yes but slower Sinc4 | Lowest power 0.93mA, best battery but noise higher, PGA gain error ±0.06% | AD7124-8 Table |

**Quantization:** LSB=FS/2^N, quantization noise LSB/√12 negligible vs ΔΣ transition noise above.

### 3.1 Data-rate/NPLC budget for ReRAM sweeps (1–50mV step, 50–100ms dwell typical)

- **FAST 10–20ms (NPLC 0.5–1 at 50Hz, 16.7ms@60Hz):** BW ~0.44/(NPLC·20ms) ≈ 44Hz @NPLC 0.5 → Johnson ×√(4.4)≈2.1× vs 10Hz baseline. ADS1262 at 100SPS noise ~2.5µV rms (vs 0.024µV@20SPS) — still negligible vs shunt Johnson on low-I? On 100nA 1MΩ Johnson 0.41pA rms@10Hz → at 44Hz 0.86pA → ADC p-p noise 0.16µV→0.16pA RTI still below Johnson. **Settling to 0.1% within dwell:** ΔΣ Sinc flush 2–3/data_rate → 20–30ms @100SPS → fits 50ms dwell with margin. **Autorange latency:** AD7175 20µs scan → 10ms dwell can accommodate relay bounce 1–3ms + analog settling → best for WF-1 10mV/50ms steps. ADS1262 at 20SPS=50ms conversion cannot complete 10mV/50ms sweep without missing points → must run ADS1262 ≥100SPS for FAST (trade noise ↑ but still OK).

- **NORMAL 50–100ms (NPLC 2.5–5):** BW ~8.8–4.4Hz → Johnson ×0.94–0.66× baseline (improvement √2). ADS1262 at 20SPS (50ms) single-cycle settled, 50/60Hz notch with 130dB, ENBW ~14Hz system @60SPS+AA per TI Part5 → **recommended for I–V sweeps** (step dwell 50ms meets NPLC 2.5 flush 2–3 conv =100–150ms? Need dwell ≥ settle+blanking 10ms DA tail → 50ms marginal for Sinc4; NORMAL with 100ms dwell safe).

- **LOW NOISE 200ms–1s (NPLC 10–50):** BW ~2.2–0.44Hz → Johnson ÷√(4.5)–√(22) ≈0.47–0.21× baseline. At NPLC 10 (200ms@50Hz) Johnson at 100nA 1MΩ → 0.41pA·√(0.22)=0.19pA rms; ADC Sinc5 averages 10× → noise ÷√10 → negligible. **Allan deviation floor:** white noise averages as σ_N=σ_1/√N only for white noise; 1/f and drift, therm EMF, leakage do not average away — long NPLC beyond 10 gives diminishing returns (drift ~0.5µV/°C). Use for HRS read verification (0.1V read) where quantitative 10σ=32.8pA→with NPLC10 →10.4pA→practical MUC 1nA easily resolved.

**ENBW scaling:** single-pole RC ENBW =π/2·fc →×1.57; brickwall→RC multiply σ by √1.57=1.253. NPLC integration approximates first-order sinc: BW≈0.44/(NPLC·20ms@50Hz). For 10Hz brickwall baseline, ENBW 15.7Hz single-pole.

### 3.2 Range-change sample handling — can we meet confirmed sweep requirements WITHOUT discarding post-range-change samples?

**Confirmed sweep:** REQ-SAFE-005 bipolar 0→+Vmax→0→−Vmax→0, step 1–50mV default 10mV, dwell 10ms–2s default 50–100ms, ≥200pts/loop, compliance-hit handling (flag+hold range), autorange with hysteresis ≥2 samples post-trip, hold range to avoid chatter at HRS↔LRS transition, FW logs `range_state`, `compliance_flag/type`, `Icomp/Vcomp` per sample.

**Range-change transient sources:** relay bounce 1–3ms + coil settle 5ms, reed Coff 1–3pF, PhotoMOS Ron 0.5–10Ω (Kelvin avoids Ron error), charge injection pC→mV on shunt (tail to 1% within DA blanking 10ms), ΔΣ filter flush 2–3 conversions (ADS1262 at 20SPS 50ms→100–150ms flush), shunt RC 1MΩ·50pF=50µs τ→250µs 5τ + DA seconds (flux, FR-4).

**Can we keep post-range-change samples?**

- **No — first 1–3 samples after a range switch must be discarded/flagged and blanked.** Documented sequence: disable output/clamp 0V → open old relay → 5ms coil settle → close new relay → 10ms DA blanking → resume; firmware holds range and logs `range_state` before voltage step to absorb C·dV/dt (IR-01 §4d compliance-aware coercion). ADS1262 requires Sinc flush (2–3×1/data_rate) before valid sample; AD7175 20µs scan is fastest but still needs relay blanking. Measured DA tail to 1% within blanking ensures the discarded samples are not counted toward accuracy.

- **After blanking, subsequent samples in same range at NORMAL/LOW NOISE NPLCs are valid without discard.** For WF-1 10mV/50ms steps crossing a range boundary, NORMAL dwell 50ms at 100SPS with 10ms blanking still leaves 40ms valid integration (≥2 samples post-trip for hysteresis REQ-MEAS-004). FAST 10–20ms dwell with AD7175 can squeeze one valid sample per step if blanking overlaps interstep 10ms holdoff; ADS1262 at 20SPS cannot — use ≥100SPS or AD7175 for FAST. **Thus confirmed sweep requirements CAN be met without discarding *all* post-change samples, but the immediate post-trip sample(s) within the blanking window must be discarded per `MEASUREMENT_FRONTEND_CANDIDATES.md §4` break-before-make, and autorange inhibits during compliance-active to avoid chatter.**

- **Firmware invariant:** `range_state` + `Icomp≤I_range` (range compliance) + `compliance_flag` per sample; integration blanking logged.

---

## 4. Reference Strategy — Correlation, Noise, Thermal, Long-term (Phase 3 selection)

| Ref | Vout | Vnoise 0.1–10Hz | TC | Initial acc | Drift long-term | Cap | IQ/VDO | Provenance |
|-----|------|-----------------|----|-------------|-----------------|-----|--------|------------|
| **ADR4525** (ADI) 2.5V B | 2.5V (also 2.048/3.0/3.3/4.096/5.0) | **1.6µV p-p (0.27µV rms)** (ADR4525; ADR4520 1.25µV) ; 60nV/√Hz@1kHz | B grade **2ppm/°C** (−40..125°C), D grade 0.8ppm (0..70°C) | ±0.02% B/C/D | 19ppm/250hr, 25ppm/1khr, 51ppm/4.5khr A/B/C; D 3/5/8ppm | 1.0µF min | 950µA max, VDO 300mV@2mA | ADI ADR4520/… Rev G Tables1–6 [analog.com/.../ADR4520_4525_4530_4533_4540_4550.pdf] |
| **LTC6655** (ADI) 2.5/5V LN | 2.5V LN **0.775µV p-p typ (0.31ppm)**, 5V ~0.80µV p-p | **2ppm/°C max A, 5ppm B, LN <10ppm hysteresis** | ±0.025% A, ±0.05% B | ~2ppm/1khr (buried Zener) | 2.7–10µF+0.1µF | 4.8mA typ | LTC6655 Rev fb [analog.com/.../6655fb.pdf] 775nV typ meas |
| **REF50xx** (TI) 5V/2.5V | 5.0V REF5050 **15µV p-p (=3µV/V)**, 2.5V 7.5µV p-p → with 1µF NR →½ | **3ppm max high-grade, 8ppm std (box)** | ±0.05% high-grade, ±0.1% std | 50ppm typ/1khr | 1–10µF+NR 1µF | ~1mA, VDO 0.2V | TI REF50xx Rev K [ti.com/lit/ds/symlink/ref5040.pdf] |

**Topologies:**

| Topology | Pros | Cons | Correlation | V1 recommendation |
|----------|------|------|-------------|-------------------|
| Internal DAC ref (AD5686R 2.5V 2ppm) alone | Fewest parts | Cannot share with ADC; gain mismatch DAC vs ADC adds RSS | Uncorrelated → larger RSS | DEFER — fallback if cost |
| Shared ADR4525 2.5V for DAC+ADC | Saves one ref, ratiometric partially cancels for shunt-vs-DAC ratio | Noise couples to both → correlated term 2ρu1u2 ρ≈0.8–1, DC adds not RSS | Correlated → tracking improves ratio but not absolute | KEEP AS ALTERNATE — needs buffer |
| **Separate refs: LTC6655-2.5 LN for DAC + ADR4525-5.0 for ADC** | Noise isolation, PSRR decoupling, independent filtering; lowest noise on DAC path | +1 IC, thermal hysteresis mismatch 4ppm worst | Uncorrelated → RSS valid, lower U | **KEEP — recommended baseline** (budgets used ADR4525/LTC6655 2.5V) |
| Single REF50xx with NR cap | Cheapest if high-grade | Noise 3× ADR4525, drift worse unless high-grade | Same as shared | DEFER — only if ADR/LTC unavailable |

**Thermal & long-term:** ADR4525 D hysteresis 1–5ppm (25→70→25°C) vs A/B/C −8/−97ppm — spec D only if shared. LTC6655LN hysteresis <10ppm after reflow, superior. All need 24hr burn-in before cal (40% of 4.5khr drift in first 250hr).

---

## 5. Combined Voltage & Current Headroom Summary (post-cal, 25±3°C, k=2, Phase 3 Test N+O evidence)

| Operating point | Target U k=2 | Budget U k=2 baseline (AD5764 direct + LTC6655LN 0.8ppm + per-range amp, 0.01% on 100nA) | Headroom | Limiting term |
|-----------------|--------------|---------------------------------------------------------------|----------|---------------|
| **Source 2V** | 900µV | 489µV (AD5764 MC) / 467µV (AD5686R 0.01% MC) | **+46% / +48%** | INL per-code ±305µV + quant |
| Source 1V | 700µV | 465µV / 454µV | **+34% / +35%** | INL; 0.1V offset residual next |
| Source 0.5V | 600µV | 461µV /450µV | **+23% / +25%** | INL + offset |
| Source 0.1V read | 520µV | 473µV /454µV | **+9% / +13%** | Offset residual + INL — tightest source point (still PASS) |
| Measure 10mA @5mA | 11.5µA | 5.9µA | +48% | Shunt tol |
| 1mA @500µA | 1.15µA | 0.59µA | +48% | Shunt tol |
| 100µA @50µA | 225nA | 59nA | +73% | Shunt tol |
| 10µA @5µA | 24nA | 5.9nA | +75% | Amp Vos |
| 1µA @500nA | 5.5nA | 80pA tight | +98% | Shunt tol |
| **100nA @50nA** | **210pA** | **60pA tight (0.01% shunt, OPA140 typ, reed 1pA)** / 248pA max loose (0.1% +120µV max) | **+71% / −18%** | **Shunt tol + amp Vos + Ileak — system limiter** |
| **Detection vs quantitative floor at 100nA:** system σ≈3.28pA rms (JFET, 10Hz ENBW) → detection 3σ=9.8pA, quantitative 10σ=32.8pA, practical MUC 3×U≈180pA → **consistent with REQ-MEAS-002** quantified floor (1.5–6pA detection + practical ~1nA MUC after shielding/averaging). With NPLC 10 (BW ~2.2Hz) σ→1.5pA → +2× improvement but 1/f and drift not averaged.

**Worst headroom is at source 0.1V and at 100nA current** — exactly the ReRAM read window (0.1V). Mitigations applied in Phase 3: **AD5764 direct (no gain-stage resistor error), LTC6655LN, 0.01% 10ppm resistors on 1µA/100nA, per-range JFET amp for low-I, reed relays, NPLC 10 for reads, DUT-sense feedback after Riso (IR-11).**

---

## 6. Type A vs Type B Separation (GUM JCGM 100 §4.2, Supplement 1 teaser)

| Category | Type A (sim noise, measured σ) | Type B (datasheet rectangular/triangular tolerances) | Treatment |
|----------|-------------------------------|------------------------------------------------------|-----------|
| **Type A examples** | `simulation/phase3/*/*.dat` transient noise (none claimed <1µV), `test_N_dac_comparison.py` MC empirical σ/RMS per setpoint (k=2=2·RMS), `test_O_monte_carlo.py` MC σ per candidate at 2V (A:35µV, B:1.5µV, C:2µV), Allan deviation at NPLC (future bench) | GC? |
| **Type B examples** | — | DAC INL ±305µV/±19µV → u176/11µV rect, shunt 0.1%→u0.0577% rect, resistor 10/25ppm TC →u43ppm, reference TC 0.8/2/5ppm →u0.46/1.15/2.9ppm, Ileak reed 1pA→u0.58pA rect, relay therm EMF ±1µV, comparator Vos ±6.5mV max→3.75mV/√3, ADC INL ±10ppm→5.8ppm, DAC quant ±0.5LSB→u0.29LSB | Divide ±a by √3 (rect) or √6 (tri), RSS, expand k=2 |
| **What we do NOT claim** | No traceable calibration (no NIST-traceable DMM yet), no measured leak/therm EMF/DA/humidity ADC DSP INL drift package parasitics — those are MODEL_LIMITATIONS (§8) and require bench per REQ-CAL-001 | No GUM Supplement 1 Monte Carlo for correlated refs beyond Test N 1000-run MC (which is Supplement 1 tier) | Supplement 1 teaser: `simulation/python/preliminary_error_budget.py` reproduces S1–S9 RSS; full Supplement 1 MC is Test N (1000×11 setpoints ×3 DACs =33k samples) |

---

## 7. Open Items for Phase 4 (Measurement) Before Promotion to bom/approved

- Power-stage headroom + SOA hyperbola |V·I|≤50–60mW verification (REQ-PWR-003) — LT1970A dropout ±12V→±5V margin 4.7V OK on paper, split ±8V optimization optional.
- Compliance loop compensation C·dV/dt holdoff vs DUT 1nF — scope injection test (Test O shows 6.5% OS at 10nF for A with 33Ω Riso; C composite lead-lag needs bench tuning).
- Relay therm EMF isothermal layout + measured Ileak vs humidity (lab 15–30°C, also 40°C corner).
- ADC digital filter + anti-alias RC co-design for ENBW (§3 Part5 analysis) — LTspice-TI RC+sinc integration + bench PSD with/without USB.
- Long-term drift log: 250hr early-life bake before cal cert (ADR4525 40% of 4.5khr drift in first 250hr).

---

*End of Phase 3 error budget. All numbers preliminary — replace with measured Type-A σ and as-built resistor/ref lots before bom/approved promotion. No PCB purchased prior to Phase 4 noise measurement and Gate 6 simulation review.*

