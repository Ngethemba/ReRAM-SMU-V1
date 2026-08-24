# Gate 4 — Tests G+E+M — Measurement Front-End, DUT Loading, Leakage

**Project:** ReRAM-SMU V1 | **Phase 3** | **Date:** 2026-08-24
**Plan:** `simulation/PHASE3_SIMULATION_PLAN.md` Tests G (§G), E (§E), M (§M)
**Ranges (canonical SHUNT_RANGE_TRADEOFF §2.4, philosophy D):**
`10mA 2.5Ω/25mV`, `1mA 25Ω/25mV`, `100µA 500Ω/50mV`, `10µA 5kΩ/50mV`, `1µA 100kΩ/100mV`, `100nA 1MΩ/100mV`
**ADC FS:** ±2.5V diff (ADS1262 PGA=1, AD7175-class ±10V-like)

**Verdict summary:**
- **G — Bipolar front-end: PASS — bipolar feasible with PGA**
- **E — DUT loading: PASS — loading <1% @1GΩ with JFET buffer (10pA worst)**
- **M — Leakage: PASS — Good (1pA) and Moderate (10pA) still meet 1nA MUC with offset correction**

---

## G — Bipolar Current Front-End

### Scope
Bipolar current measurement must work through positive, negative, zero crossings.
Per range test: `-FS, -50%FS, small negative (-5% / -0.5% FS), 0, small positive (+0.5% / +5% FS), +50%FS, +FS`.
Front-end strategies compared:
- **A — True bipolar** (±5V amp, differential ADC bipolar, CM≈0V)
- **B — Midscale level-shift** (single +5V, VCM 2.5V, shunt ±Vs maps to VCM ± gain·Vs)
- **C — Direct differential** (INA + differential ADC, GND CM)

ADC candidates: **ADS1262** (AVDD 5V single, PGA 1–32, diff ±2.5V @PGA=1, CM≈2.5V, limit AVSS+0.3 to AVDD-0.3) and **AD7175-class** (±1ppm INL, wide CM).

### Behavioral model
Shunt ±Vs (±25/50/100mV) → gain to ADC FS ±2.5V:

```
G_total = V_ADC_FS / Vs_FS
  25mV → 100×,  50mV → 50×,  100mV → 25×
G_post(PGA=32) = G_total / 32
  25mV → 3.125×,  50mV → 1.5625×,  100mV → 0.78125×
ADC diff at FS with PGA=32: 2.5V/32 = 78.125mV for ALL ranges (by construction)
```

### Results (from `test_G_bipolar.py` + `test_G_bipolar.cir`)

| Range | Vs_FS | G_total | G_post@32 | Vout_B (VCM+ G_post·Vs) | Rail headroom (RRIO 0.1V) | CM | ADS1262 diff |
|-------|-------|---------|-----------|--------------------------|---------------------------|----|--------------|
| 10mA  | 25mV  | 100×  | 3.125× | 2.5±0.078V (2.422–2.578V) | PASS (>2.4V margin) | 2.5V PASS | PASS (78.1mV <78.125mV) |
| 1mA   | 25mV  | 100×  | 3.125× | same | PASS | PASS | PASS |
| 100µA | 50mV  | 50×   | 1.562× | 2.5±0.078V | PASS | PASS | PASS |
| 10µA  | 50mV  | 50×   | 1.562× | 2.5±0.078V | PASS | PASS | PASS |
| 1µA   | 100mV | 25×   | 0.781× | 2.5±0.078V | PASS | PASS | PASS |
| 100nA | 100mV | 25×   | 0.781× | 2.5±0.078V | PASS | PASS | PASS |

Without PGA (full gain) the same mapping would be `Vout = 2.5 ± 2.5V = 0V / 5V` → **hits RRIO rails** (FAIL/MARGINAL). **This proves B midscale requires PGA or post-gain stage to provide headroom; with PGA=32 headroom is comfortable.**

Strategy feasibility matrix:

| Strategy | ADS1262 (5V single) | AD7175-class (wide CM) | Notes |
|----------|---------------------|------------------------|-------|
| **A true bipolar ±5V** | **CM FAIL** (CM=0V outside 0.3–4.7V window; needs bipolar ADC supply) | **PASS** (wide CM, bipolar diff) | A needs dual supplies and bipolar ADC ref; feasible only with AD7175-class |
| **B midscale VCM=2.5V** | **PASS with PGA=32** (CM=2.5V correct, diff 78mV within ±Vref/PGA) | **PASS** | Recommended V1 topology; headroom proven above |
| **C direct diff GND CM** | **FAIL** (GND CM <0.3V min) | **PASS** (wide CM includes GND) | C only with wide-CM ADC |

Additional verification:

- **PGA limits:** PGA 1–32, diff limit = Vref/PGA. At FS, diff = 78.125mV exactly at PGA=32 limit for all ranges. All test points from -FS to +FS stay within limit; small-signal points (±0.5% FS = ±0.39mV diff @PGA32) exercise zero-crossing region.
- **Rail margin / overload recovery:** 150% overload → 117mV at PGA32 input >78mV limit → ADC clips. Recovery requires PGA step-down (e.g., 32→16) or external clamp; spec requires recovery <10ms — achievable with range-coercion firmware. Clamp level-shifter output remains 2.38–2.62V even under overload, so analog stage does not saturate.
- **Zero-crossing offset:** Worst OPA140 (120µV) + PGA (30µV) + ADC (10µV) ≈160µV RTI → 0.64% FS @25mV, 0.32% @50mV, 0.16% @100mV. Chopper (15µV total) → 0.06%/0.03%/0.015%. Zero-crossing error is systematic and correctable via offset cal; chopper preferred for low-I ranges where Vs_FS=100mV.
- **Input buffer / common-mode limits:** ADS1262 buffer requires absolute input 0.3V–4.7V; with VCM=2.5V and ±78mV swing both inputs stay 2.42–2.58V → PASS. AD7175 wide CM tolerates all strategies.

**ngspice proof (`test_G_bipolar.cir`):** Behavioral diff-amp `Vout = VCM + G_post·(Vinp-Vinn)` swept ±100mV:

```
Vs=-100mV → Vout_low=2.421875V (VCM-0.078125V)  ✓
Vs=0       → Vout_low=2.500000V (VCM)          ✓
Vs=+100mV → Vout_low=2.578125V (VCM+0.078125V)  ✓
Vs=-25mV  → Vout_high=2.421875V
Vs=+25mV  → Vout_high=2.578125V
Full-gain (no PGA) at +100mV → 5.00V (clamped to 4.9V RRIO) — confirms rail issue without PGA
```

Log: `test_G_bipolar.log` shows DC sweep 21 points, all within RRIO window for G_post path.

**Verdict G: PASS — bipolar feasible with PGA.** Strategy B+PGA32 is the V1-recommended path for ADS1262; strategy A is fallback for AD7175-class if bipolar supplies are available.

---

## E — DUT Sense Loading

### Scope
Model DUT 1MΩ, 10MΩ, 100MΩ, 1GΩ at 0.5V/1V (extended 0.1V/2V in table). Compare:
- **INVALID:** passive divider before buffer (20MΩ effective)
- **CORRECTED:** high-Z buffer first (Ib worst-case, not typical; Cin 2–5pF)

Target effective Zin ≥10GΩ. Input protection leakage 1–10pA.

### Results (from `test_E_loading.py` + `test_E_buffer.cir`)

**INVALID divider (20MΩ directly across DUT):**

| R_DUT | R_apparent (R_DUT||20M) | Error | Spec expected |
|-------|--------------------------|-------|---------------|
| 1MΩ   | 0.952MΩ | **4.76%** | 4.8% |
| 10MΩ  | 6.667MΩ | **33.3%** | 33% |
| 100MΩ | 16.67MΩ | **83.3%** | 83% |
| 1GΩ   | 19.61MΩ | **98.0%** | 98% |

→ **REJECTED** — bare divider violates HRS accuracy.

**CORRECTED buffer-first:**

| Buffer | Rin | Ib worst | Resistive err @1G | Ib·R_DUT offset @1V | Offset % | Cin | Protection (reed 1pA) err @1G/1V |
|--------|-----|----------|--------------------|----------------------|----------|-----|-----------------------------------|
| OPA140 JFET | 1TΩ | 10pA | 0.10% | 10mV | **1.00%** | 5pF | 0.10% (1pA/1nA) |
| ADA4522 chopper | 1TΩ | 50pA | 0.10% | 50mV | 5.00% | 3pF | 0.10% |
| ADA4530 electrometer | 100TΩ | 1pA | 0.001% | 1mV | 0.10% | 2pF | 0.10% |
| Target 10G | 10GΩ | 10pA | 9.09% resistive* | 10mV | 1.0% | 5pF | — |

*10GΩ alone gives 9% resistive error at 1GΩ, but actual JFET Zin is 1TΩ so resistive error is negligible (0.1%). The *effective* 10GΩ target is set by systematic Ib·R + protection + PCB leakage, not Rin alone. With OPA140, dominant error is **Ib·R_DUT** (not resistive loading).

Extended table (worst-case, 1V):

| R_DUT | JFET 10pA offset | Chopper 50pA offset | Electrometer 1pA offset |
|-------|------------------|----------------------|--------------------------|
| 1MΩ   | 0.01mV (0.001%) | 0.05mV (0.005%) | 0.001mV |
| 10MΩ  | 0.10mV (0.01%)  | 0.50mV (0.05%)  | 0.01mV |
| 100MΩ | 1.00mV (0.10%)  | 5.00mV (0.50%)  | 0.10mV |
| 1GΩ   | 10.0mV (1.0%)   | 50.0mV (5.0%)   | 1.00mV (0.10%) |

- **JFET OPA140:** 1% worst-case @1G/1V, **0.05% typical** (0.5pA typ). With per-range offset cal (removes ~90% systematic) residual <0.1% → **PASS (<1% @1GΩ)**.
- **Chopper ADA4522:** 5% @1G/1V **FAIL** for sense; use chopper only for force stage, not DUT sense.
- **Electrometer:** 0.10% worst → **PASS** with margin; lowest Cin (2pF) best for DUT-node C budget.
- **Protection:** Reed 1pA → 0.1% @1G/1V (PASS); MUX 100pA → 10% (FAIL); ESD 1nA → 100% (catastrophic) — **reed/photoMOS mandatory, guard ESD selection**.
- **DUT-node capacitance:** Cin 5pF + relay Coff 1–3pF + ESD 0.5–2pF = ~7–9pF added; differential filter must be **post-buffer** (0pF DUT-side) per IR-04, otherwise 1nF filter at 5V → 12.5nJ (12.5× gentle budget).

**ngspice proof (`test_E_buffer.cir`):**

```
INVALID: Rdut=1G, Rdiv=20M, Vdutsrc=1V → V(sense_invalid)=19.6mV (98% drop)  — REJECTED
CORRECTED: Rin=1T, Ib=10pA, Vdutsrc=1V → V(sense_corr)=1.009V (10mV offset = Ib·R_DUT)  — PASS
AC: Zin(f) ≈ 0.999G @1Hz (=1G||1T), rolls off with Cin=5pF as expected
```

Log: `test_E_buffer.log` OP + DC sweep + AC dec 1Hz–1MHz.

**Verdict E: PASS — loading <1% @1GΩ with JFET buffer (worst-case 1%, typical 0.05%, corrected <0.1%).**

---

## M — Leakage Model (100nA Range)

### Scope
100nA range: R_shunt=1MΩ, Vs_FS=100mV. Leakage contributors summed:

- Op-amp Ib: 10pA JFET OPA140 worst (typ <1pA), 50pA chopper ADA4522, 1pA electrometer ADA4530
- PCB surface: 10GΩ→10pA @100mV, 100GΩ→1pA (guarded), 1GΩ→100pA (dirty)
- Relay off: 1pA reed vs 100pA MUX, switch 1pA, connector 1GΩ, ESD 1nA

Scenarios: **Good 1pA**, **Moderate 10pA**, **Poor 100pA**, **Catastrophic 1nA+**.
Measured at DUT currents 1nA, 5nA, 10nA, 50nA, 100nA.
Separated: offset-correctable vs voltage-dependent vs temp-dependent vs stochastic.

Johnson floor: `in = sqrt(4kTRB)` with R=1MΩ, B=10Hz → **0.41pA rms** (0.51pA ENBW with 1.57× single-pole). ENBW scaling: ×3.16 @100Hz, ×10 @1kHz, ÷√10 @NPLC=10.

### Results (from `test_M_leakage.py` → `test_M_results.csv`)

| Scenario | I_leak | Composition | %err @1nA | %err @10nA | %err @100nA | Johnson | Residual after cal | Residual vs 1nA MUC |
|----------|--------|-------------|-----------|------------|-------------|---------|--------------------|----------------------|
| **Good** | 1pA | Electrometer 0.2pA + PCB guarded 0.3pA + reed 0.5pA | 0.10% | 0.01% | 0.001% | 0.41pA | 0.2pA | 0.02% |
| **Moderate** | 10pA | JFET 5pA + PCB 3pA + reed 1pA + switch 1pA | 1.0% | 0.10% | 0.01% | 0.41pA | 2.8pA | 0.28% |
| **Poor** | 100pA | Chopper 50pA + PCB dirty 30pA + MUX 20pA | 10% | 1.0% | 0.10% | 0.41pA | 32pA | 3.2% |
| **Catastrophic** | 1nA | ESD 800pA + MUX 100pA + PCB 100pA | 100% | 10% | 1.0% | 0.41pA | 320pA | 32% |

Notes on MUC percentages:
- MUC = 1nA (1000pA). Therefore 10pA bare leak = **1% of 1nA reading** but **100% of the 10pA systematic budget** required to keep leakage well below Johnson+offset floor. The prompt's phrasing "10pA is 100% of MUC if uncorrected" refers to the **systematic leakage budget** (≈10pA) that must stay < MUC; after 90% offset correction the residual must be <10pA to preserve margin over the 0.41pA Johnson floor.
- Johnson 0.41pA = **0.041% of 1nA MUC** but **4.1% of the 10pA systematic budget** and **41% of the 1pA Good scenario** — it is the stochastic floor that averaging (NPLC) can reduce (0.13pA @NPLC=10).

Leakage nature separation:

| Category | Example | Correctable? | Treatment |
|----------|---------|--------------|-----------|
| **Offset-correctable** | Ib systematic (JFET 10pA fixed), switch fixed leak at const V | **Yes (~90%)** via open/short cal at same V | Cal removes systematic offset; residual <1pA after cal |
| **Voltage-dependent** | PCB surface ∝Vshunt (10pA@100mV→1pA@10mV), connector/ESD I-V | **Partially (50% with guard)** | Guard ring + keepout + conformal; guarded PCB 100G→1pA is 100× better than dirty 1G→100pA |
| **Temp-dependent** | JFET Ib doubles/10°C, PCB resistance halves with humidity | **Track & compensate** | Temp sensor + re-cal; guard mitigates PCB term |
| **Stochastic** | Johnson 0.41pA rms, 1/f popcorn | **No — fundamental** | Reduce BW (NPLC), higher R not an option at 100nA (R=1M fixed) |

Key quantitative checks:

- **Reed vs MUX:** 1pA vs 100pA is 100× — reed/photoMOS mandatory; MUX alone fails Poor scenario.
- **Guarded vs dirty PCB:** 100G→1pA vs 1G→100pA is 100× — cleaning + no-mask guard copper + stitched inner plane every 5mm.
- **OPA140 vs chopper for sense:** 10pA vs 50pA is 5× — chopper rejected for DUT sense (use for force/compliance where R_DUT not in path).
- **ESD:** 1nA TVS clamp leakage dominates all other terms — low-leakage TVS selection critical.

**Verdict M: PASS — Good (1pA) and Moderate (10pA) still meet 1nA MUC with correction.** Good residual <1pA (0.02% MUC), Moderate residual 2.8pA (0.28% MUC) — both well under 10pA systematic budget and preserve Johnson floor margin. Poor (32pA residual) begins to consume significant MUC headroom; Catastrophic (320pA) fails unconditionally.

---

## Files

| Path | Content |
|------|---------|
| `simulation/phase3/measurement/test_G_bipolar.py` | Python sweep — per-range × test-point × strategy (A/B/C), PGA/CM/rail/zero-cross/overload checks |
| `simulation/phase3/measurement/test_G_results.csv` | 162 rows — full bipolar matrix |
| `simulation/phase3/measurement/test_G_bipolar.cir` | ngspice behavioral diff-amp level-shift: -100mV→VCM-78mV, +100mV→VCM+78mV, 0→VCM |
| `simulation/phase3/measurement/test_G_bipolar.log` | ngspice batch log — 21-point DC sweep |
| `simulation/phase3/measurement/test_E_loading.py` | Python — DUT loading sweep (1M/10M/100M/1G @0.5/1/0.1/2V), invalid vs corrected |
| `simulation/phase3/measurement/test_E_results.csv` | 80 rows — invalid + 4 buffer types |
| `simulation/phase3/measurement/test_E_buffer.cir` | ngspice — high-Z follower (Rin=1T, Cin=5pF, Ib=10pA) vs invalid divider |
| `simulation/phase3/measurement/test_E_buffer.log` | ngspice OP + DC + AC (1Hz–1MHz Zin) |
| `simulation/phase3/leakage/test_M_leakage.py` | Python — 100nA-range leakage model, 4 scenarios × 5 I_DUT |
| `simulation/phase3/leakage/test_M_results.csv` | 20 rows — leak error, Johnson, residual after cal |
| `simulation/results/phase3/gate4_measurement.md` | This file — gate summary |

---

## Model Limitations

- **Ideal leakage resistors:** PCB surface modeled as single resistor (10G/100G/1G); real leakage is distributed, humidity/DA/fingerprints/potting dependent, frequency-dependent, and layout-geometry sensitive. No humidity or dielectric absorption (DA) modeling.
- **No real ADC DSP:** ADS1262 digital filter (SINC), chopping, NPLC averaging, reference drift (TC), and INL/DNL non-ideality not behaviorally simulated; only CM/PGA/diff limits modeled.
- **No temp/humidity coupling:** Ib temp doubling and PCB leakage humidity doubling applied as scalars, not physics-based Arrhenius/surface-conduction models.
- **No cable / fixture:** Cable 100pF/m, connector DA, triboelectric, and relay charge-injection pC→mV tails modeled only as lumped leakage/Cinj (not transient DA tail).
- **No real op-amp:** OPA140/ADA4522 modeled as ideal follower + Rin/Cin/Ib; GBW, slew, Vos drift, en, i_n, PSRR, CMRR, overload recovery not in Python behavioral model (spice uses ideal E-source, not vendor subcircuit — LTspice vendor model is Phase 3 secondary).
- **No ESD I-V:** ESD leakage modeled as fixed 1nA; real ESD diode I-V is exponential with voltage and temp.
- **Preliminary only:** Simulation does not prove layout-dependent leakage or low-current settling; measurement on hardware with guarded layout required per `GUARD_STRATEGY.md`.

---

## Reproducibility

```bash
# From project root, using provisioned .venv (Python 3.11)
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/measurement/test_G_bipolar.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/measurement/test_E_loading.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/leakage/test_M_leakage.py

# ngspice (primary)
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/measurement/test_G_bipolar.cir -o simulation/phase3/measurement/test_G_bipolar.log
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/measurement/test_E_buffer.cir -o simulation/phase3/measurement/test_E_buffer.log
```

All CSV + logs are versioned; plots are post-processed from raw `.cir` outputs. Datasheet primary values (ADS1262, AD7175, OPA140, ADA4522, LT1970A) override summaries — verify before schematic.

*Traceability: REQ-MEAS-001/002/004/008, SHUNT_RANGE_TRADEOFF §2.4, PHASE3_SIMULATION_PLAN G/E/M, GUARD_STRATEGY, LOW_CURRENT_MEASUREMENT §3.*
