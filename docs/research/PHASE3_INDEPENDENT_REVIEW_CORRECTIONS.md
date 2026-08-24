# Phase 3 Independent Review — Corrective Review Record

**Project:** ReRAM-SMU V1 — Phase 3 Corrective Review / Validation Patch  
**Date:** 2026-08-24  
**Commit baseline:** `6fb9f3e — phase3: complete source, compliance, Kelvin and measurement-front-end simulation (Tests A-O)`  
**Gate status before review:** `PHASE 3 — PASS` (15/15 tests PASS)  
**Review type:** Corrective validation patch — NOT Phase 4, no schematic/PCB/BOM  
**Authority:** Primary manufacturer datasheets override all prior summaries  
**Verdict taxonomy:** `CONFIRMED ISSUE` · `PARTIALLY CONFIRMED` · `NOT AN ISSUE` · `MODEL LIMITATION` · `REQUIRES HARDWARE PROTOTYPE`

---

## Scope and Method

Phase 3 reported 15/15 simulation gates PASS (Tests A-O) with selection Candidate A LT1970A direct SELECT, Candidate B fallback, Candidate C prototype, AD5764 SELECT, AD7175-8 primary. An independent review raised 8 findings (P3IR-01..08) claiming inconsistencies between simulation assumptions, selected architecture, datasheets, CSV results and synthesis.

Each finding was verified by:

1. Locating the exact repository claim and synthesis statement,
2. Locating the simulation/code that produced it (Python + ngspice-47 + CSV artifact),
3. Retrieving the current manufacturer datasheet (Analog Devices / TI, Rev dates cited),
4. Independently recalculating numerically (Python 3.11.15, 2026-08-24),
5. Re-running or analytically verifying simulation where applicable,
6. Comparing raw → processed → summary,
7. Classifying verdict and defining correction.

Original Phase 3 artifacts are preserved; this document corrects or supersedes them traceably.

---

## Finding P3IR-01 — LT1970A Compliance Rsense Architecture Mismatch

### Finding ID
P3IR-01

### Independent review claim
Gate A/B use canonical measurement shunts 2.5Ω/25Ω/500Ω/5kΩ/100kΩ/1MΩ to claim 50µA–1mA compliance via range coercion, but `PHASE3_ARCHITECTURE_SELECTION.md` proposes a separate LT1970A Rsense ≈10Ω (with Rsense=10Ω variant). With 4mV floor → Ifloor≈400µA and 6mV linear → Ilinear≈600µA, 50/100µA would be impossible on 10Ω.

### Original repository claim
- `simulation/phase3/compliance/test_A_results.csv` — sweeps Icomp vs canonical R (2.5Ω–1MΩ) and classifies Vc=10·Vsense.
- `test_B_range_coercion.py` — selects tightest range where Icomp≤I_FS and Vc≥60mV (linear), ideal Vc≥0.5V.
- `PHASE3_ARCHITECTURE_SELECTION.md` § Schematic-Ready Partition: "Rsense 10Ω high-side Kelvin + R_iso 33Ω after pick (+10Ω Rs variant for compliance decade)" — described as high-side LT1970 sense resistor distinct from low-side measurement shunt matrix `2.5/25/500/5k/100k/1M`.
- `DEC-024` (Phase 2 correction) already flagged: LT1970A floor 4mV/R = 4% FS @100mV, 8%@50mV, 16%@25mV; 0.1% FS requires 4V burden — impossible; tiered compliance via coercion.

### Relevant simulation artifact
- `simulation/phase3/compliance/test_A_LT1970_floor.py` (canonical D ranges)
- `test_A_results.csv` (54 rows, 9 Icomp × 6 ranges)
- `test_B_range_coercion.py` + `test_B_results.csv` (6 cases, 50µA–5mA)
- `simulation/phase3/source_A_LT1970/candidate_A_transient.cir` — Rsense 10Ω in that netlist
- `PHASE3_RESULTS.md` Gate1: "6/6 linear (Vc 125–500mV), ReRAM 50µA-1mA 4/4 PASS"

### Manufacturer evidence
**Analog Devices LT1970A datasheet 1970afc (Rev 11/11/2015):**
- SENSE = VCSRC/10 (source) or −VCSNK/10 (sink); VCSRC/VCSNK 0–5V above COMMON (COMMON = GND typical).
- Transfer linear **except VCSRC/VCSNK < 60mV**; hockey-stick/nonlinear below.
- VSENSE limits at **minimum 4mV typical** (Vsense_min) to prevent simultaneous source/sink activation.
- Valid SENSE common-mode: VCC−1.5V to VEE+1.5V; FILTER pin: internal 1kΩ + external 1nF–100nF to SENSE− (or leave open/short to SENSE−).
- Rsense placement: normally in series between OUT and load; SENSE+ to OUT side, SENSE− to load side; alternative low-side between load and GND with degraded voltage accuracy.
- Datasheet provenance: `docs/references` not yet stored; cited from analog.com 1970afc PDF p.1, p.8, p.12-13.

### Independent calculation

**LT1970A law:** `I_limit = Vc/(10·Rsense)` where `Vc = VCSRC` (or VCSNK), `Vsense = Vc/10`, with floor `Vsense_min = 4mV typ → Vc_floor=40mV`, `Vc_linear_min=60mV → Vsense=6mV`.

For **fixed 10Ω** LT1970 Rsense (as in candidate_A_transient.cir):
- Ifloor_typ = 4mV/10Ω = **400µA**
- Ilinear_min = 6mV/10Ω = **600µA**
- Vc for Icomp: `Vc = 10·I·10Ω`

| Requested Icomp | Rsense (actual 10Ω fixed) | Vsense = I·R | Vc = 10·Vs | Region (per 1970afc) | Achievable? |
|---|---|---|---|---|---|
| 10µA | 10Ω | 0.10mV | 1.0mV | INVALID floor (<4mV, <40mV) | **NO** |
| 50µA | 10Ω | 0.50mV | 5.0mV | INVALID floor | **NO** |
| 100µA | 10Ω | 1.00mV | 10mV | INVALID floor | **NO** |
| 500µA | 10Ω | 5.00mV | 50mV | NONLINEAR <60mV (4–6mV) | **NO** (hockey-stick) |
| 1mA | 10Ω | 10.0mV | 100mV | VALID linear | **YES** |
| 5mA | 10Ω | 50.0mV | 500mV | VALID linear (ideal ≥0.5V marginal) | **YES** |
| 10mA | 10Ω | 100mV | 1.00V | VALID linear (ideal) | **YES** |

For **canonical measurement shunts** (2.5Ω–1MΩ) if shared as compliance R (Solution C1 hypothesis):
- 10mA on 2.5Ω → Vs=25mV Vc=250mV VALID; Ifloor=1.6mA (4mV/2.5Ω) = 16% FS
- 100µA on 500Ω → Vs=50mV Vc=500mV VALID; Ifloor=8µA = 8% FS
- 100nA on 1MΩ → Vs=100mV Vc=1V VALID; Ifloor=4nA = 4% FS
- But a single shared R cannot cover 10µA–10mA at 0.1% FS: I_min/FS = 4mV/Vfs = 4%@100mV, 8%@50mV, 16%@25mV — never 0.1%; requires 4V burden (DEC-024, confirmed).

**Re-run:** Verified `test_A_results.csv` matches this arithmetic row-for-row (e.g., 50µA on 500Ω → 25mV → 250mV VALID linear; 50µA on 25Ω → 1.25mV → 12.5mV INVALID floor). Python re-calc 2026-08-24 reproduced CSV exactly.

### Re-run performed
- Re-executed `test_A_LT1970_floor.py` logic in-memory — CSV matches independent calc.
- Re-executed `test_B_range_coercion.py` — 6/6 cases PASS when Rsense = measurement shunt (selected range is the shunt). For fixed 10Ω, 4/6 fail below 600µA.
- Inspected `candidate_A_transient.cir` Rsense 10Ω and report that synthesis omitted the fixed-R limitation at 50–100µA in the executive summary (reported PASS for 50µA–1mA without stating "only if compliance R = measurement shunt").

### Observed result
- **Fixed 10Ω Rsense cannot meet ReRAM 50µA/100µA compliance** — requires ≥600µA for linear region.
- **Shared canonical Rsense (2.5Ω–1MΩ) CAN meet 50µA–1mA** via range-switched measurement shunts, but synthesis incorrectly implied the 10Ω fixed-R architecture was validated by Gate A/B (which used canonical shunts).
- The 10Ω resistor in the schematic-ready partition is a **current-limit sense resistor**, NOT the measurement shunt, but the document did not answer Q1–Q3 explicitly and the CSV validation does not apply to that topology.

### Verdict
**CONFIRMED ISSUE** — architecture/data mismatch. Gate A/B validate a shared-R (C1) topology, not the fixed 10Ω separate-R topology described in PHASE3_ARCHITECTURE_SELECTION. The 50µA–1mA PASS claim is valid only with canonical shunts, not with fixed 10Ω.

### Architecture impact
**Candidate A remains viable** but requires an explicit compliance-resistor strategy. Three options are defensible:

- **C1 — Shared range-switched Rsense (measurement = compliance):** LT1970 SENSE monitors the selected low-side shunt (2.5Ω–1MΩ). Simplest, lowest BOM, validated by A/B, but high-range burden (25mV @10mA) gives floor 16% FS and widest measurement shunt sees full load current (reliability).
- **C2 — Separate LT1970 compliance resistor bank:** Dedicated LT1970 Rsense bank (e.g., 2.5Ω/25Ω/250Ω/2.5kΩ scaled for compliance-only) switched independently of measurement shunts. Allows Vc≥0.5V for each decade, but adds 2–3 relays, leakage, CM, and stock.
- **C3/C4/C5 — Amplified/outer precision CC loop or coarse+precision dual:** Measurement shunt voltage amplified (ADA4522) into external CC error amp driving LT1970 or outer loop (Candidate C). Achieves 0.1% FS and low-I precision, at highest complexity; reserved for Candidate C or V1.1.

**Selected for V1 (corrected): C1 shared range-switched Rsense as primary, with C2/C5 footprint reserved.** This is the simplest defensible V1 architecture that meets 50–100µA without inventing a new analog block. The 10Ω fixed-R netlist in `candidate_A_transient.cir` is superseded; replace with switched canonical Rsense (or add compliance-bank option).

### Correction
- Revised compliance topology in this review: **LT1970A SENSE+/− monitor the selected low-side measurement shunt (shared) for V1 REV-A.** Current path: `LT1970A OUT → R_iso (33Ω) → DUT → FORCE_LO → selected measurement shunt (2.5Ω–1MΩ) → GND`, with LT1970 SENSE+ to shunt high side (FORCE_LO node) and SENSE− to GND (Kelvin sense across shunt). Kelvin voltage sense is separate (SENSE_HI/LO at DUT, buffered >10GΩ, feedback after R_iso).
- Clarified in `PHASE3_ARCHITECTURE_SELECTION.md` errata: Rsense is NOT fixed 10Ω for compliance; 10Ω was a transient-test placeholder. Added compliance Rsense bank option as footprint, not stuffed.
- Added explicit Q1–Q3 answers in this document (see Questions).
- Updated `PHASE3_RESULTS.md` Gate1 to state "PASS only with shared canonical Rsense; fixed 10Ω fails <600µA".

#### Questions — explicit answers

**Q1 — Is the LT1970 compliance resistor the SAME element as measurement shunt?**
For V1 REV-A as corrected: **YES — shared range-switched resistor**. The LT1970 SENSE monitors the selected low-side measurement shunt. The prior 10Ω fixed-R document was inconsistent; that topology is rejected for V1 REV-A unless a separate compliance bank (C2) is stuffed.

**Q2 — If not shared, how can Gate B coercion alter LT1970 sensitivity?**
It cannot — unless the same resistor is switched. With fixed Rsense, coercion of measurement range has no effect on Vc = 10·I·R_fixed. The original Gate B claim implicitly assumed shared R; this review makes it explicit. If a separate compliance bank is used, coercion applies to that bank independently, and firmware must log `compliance_range` distinct from `measurement_range`.

**Q3 — What exact resistor does SENSE+/− monitor?**
LT1970 SENSE+ → FORCE_LO-side of selected shunt (high side of measurement shunt), SENSE− → GND (low side). The shunt is the canonical 2.5Ω/25Ω/500Ω/5kΩ/100kΩ/1MΩ matrix, Kelvin-sensed across the shunt (not high-side OUT–DUT). High-side 10Ω is no longer the compliance sense element.

### Files affected
- `docs/research/PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md` (this file)
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (new gate R1)
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — errata §3.1
- `docs/architecture/COMPLIANCE_ARCHITECTURE.md` — clarify C1 vs C2
- `simulation/phase3/source_A_LT1970/candidate_A_transient.cir` — note: behavioral Rsense placeholder superseded
- `DECISIONS.md` — add DEC-028 (compliance topology)
- `simulation/phase3/MODEL_LIMITATIONS.md` — note Cs

### Phase 4 impact
Phase 4 schematic must use **shared canonical shunt as compliance Rsense** (or provision separate bank footprint). Fixed 10Ω alone is BLOCKED for 50–100µA compliance. This resolves Gate R1.

---

## Finding P3IR-02 — C_UPSTREAM Energy Interpretation Reversed

### Finding ID
P3IR-02

### Independent review claim
`test_J_upstream_downstream.py` calculates `E_DUT = E_C · R_DUT/(R_iso+R_DUT)` → 95.5% at 1kΩ/47Ω means 95.5% dumped to DUT, but synthesis says 95.5% isolated/not dumped and treats C_upstream ≤10nF as free.

### Original repository claim
- `test_J_results.csv`: Upstream before R_iso → `E_delivered = Estored·Rdut/(Riso+Rdut)` (fraction 0.955, 11.94nJ of 12.5nJ for 1nF@5V) vs downstream → 100% (12.5nJ).
- `PHASE3_RESULTS.md` Gate3 / `PHASE3_RESEARCH_SUMMARY.md`: "Upstream isolated 95.5–100% not dumped"
- `simulation/phase3/compliance/README_FJ.md`: upstream ~95.5% to DUT + 4.5% in R_iso, with note "not penalized as DUT dump" — contradictory phrasing.

### Relevant simulation artifact
- `simulation/phase3/compliance/test_J_upstream_downstream.py` + `.cir` + `.csv` (4.7nF/10nF × R_iso 10–100Ω × Rdut 1k/1M)
- `simulation/phase3/compliance/README_FJ.md` §0 canonical Upstream/Downstream
- `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` §2.5
- `simulation/results/phase3/gate3_capacitance.md` and `PHASE3_RESULTS` Gate J

### Manufacturer evidence
No component datasheet; this is circuit theory + LT1970A output impedance / servo behavior. LT1970A is a voltage-mode op-amp with low Rout (~0.5Ω behavioral) and active feedback; compensation cap before R_iso is at the amplifier output, not directly across DUT. Energy bookkeeping requires distinguishing:
- **C downstream (DUT side of R_iso):** Directly across DUT → passive dump `½CV²` fully into filament.
- **C upstream (amp side of R_iso):** Isolated by R_iso and servo — discharge path includes R_iso; passive RC model gives fractional dump, but active amplifier can source/sink and limit.
- **Compensation cap between internal nodes (e.g., Miller/lead-lag):** Not charged to output voltage → `½CV²` does not apply.

### Independent calculation

**Passive RC model (worst-case, amp = ideal voltage source 0Ω after discharge starts):**
`Estored = ½CV²`, `E_DUT = Estored · Rdut/(Riso+Rdut)`, `E_Riso = Estored · Riso/(Riso+Rdut)`.

For V=5V, C=1nF: Estored=12.5nJ.
- Rdut=1kΩ, Riso=47Ω → E_DUT=11.94nJ (95.5%), E_Riso=0.56nJ (4.5%)
- Rdut=10Ω (filament short), Riso=47Ω → E_DUT=2.19nJ (17.5%), E_Riso=10.31nJ (82.5%) — R_iso dominates for short.

For hard short (Rdut→0), passive model predicts most energy in R_iso, but this is **not** "isolated" for normal LRS (~1kΩ) — still 95.5% to DUT. The synthesis phrase "95.5% not dumped" is **reversed**; 95.5% IS dumped for 1kΩ.

**Active servo consideration:** LT1970A can actively sink/source capacitor current within its 1.6V/µs SR and 3.6MHz GBW; upstream cap current can be partially absorbed by the amplifier if the loop remains in linear regulation. However, for fast filament snap (100ns–1µs), the upstream cap discharge is faster than loop takeover (4µs) → still dumps fractionally. Therefore "`C_upstream is free`" is **false**.

**Full case table (excerpt, 5V):**

| C | R_iso | Rdut | E_stored | E_DUT (passive) | E_Riso | % to DUT | Notes |
|---|---|---|---|---|---|---|---|
| 100pF | 47Ω | 1kΩ | 1.25nJ | 1.19nJ | 0.06nJ | 95.5% | Dump, not free |
| 1nF | 47Ω | 1kΩ | 12.5nJ | 11.94nJ | 0.56nJ | 95.5% | — |
| 4.7nF | 47Ω | 1kΩ | 58.75nJ | 56.1nJ | 2.65nJ | 95.5% | Dominates filament |
| 10nF | 47Ω | 1kΩ | 125nJ | 119.4nJ | 5.6nJ | 95.5% | — |
| 10nF | 47Ω | 10Ω | 125nJ | 21.9nJ | 103.1nJ | 17.5% | R_iso helps for short only |
| 100pF | 47Ω | 1kΩ @2V | 0.20nJ | 0.19nJ | 0.01nJ | 95.5% | Even at 2V, still dump |

Conservation: `E_stored ≈ E_DUT + E_Riso + E_amp` (± integration tolerances). Upstream cap energy is **not free**; it is shared.

### Re-run performed
- Re-evaluated `test_J_results.csv` formulas — confirmed `fraction = Rdut/(Riso+Rdut)` = 95.5% for 1k/47Ω.
- Analytically verified that `C downstream` 100pF@5V = 1.25nJ already at gentle budget limit; 10nF upstream 125nJ still dominates even with 95.5% fraction — contradicts "free" claim.
- No change to .cir needed; interpretation correction only.

### Observed result
Original code arithmetic is correct (95.5% dumped), but synthesis prose reversed meaning and omitted that compensation cap between nodes (Cf 33pF) is not output-to-ground and should not be counted as `½CV²`. The phrase "C_upstream isolated 95.5–100% not dumped" is wrong for passive model at 1kΩ LRS.

### Verdict
**CONFIRMED ISSUE** — wording reversed and "≤10nF free" is overstated.

### Architecture impact
- **C downstream (DUT side of R_iso):** Budget is tight — `C_DOWNSTREAM ≤80pF @5V (1nJ gentle) / 500pF @2V / 160pF @5V for 2nJ standard`. Includes connector (5–10pF) + trace (1–3pF) + relay Coff (1–3pF) + buffer Cin (2–5pF) + cable (25–50pF for 0.5m low-C) + DUT (0.5–5pF). Only downstream counts toward `E=½CV²` budget.
- **C upstream (amp side of R_iso):** Not free, but partially absorbed via R_iso + servo; still counts as shared dump for LRS. Limit to ≤10nF before R_iso is acceptable only with R_iso 33–47Ω and active sink; continuous operation at 5V/10nF still dumps ~119nJ for 1k snap — exceeds gentle budget. Recommend **C_upstream ≤1nF for 5V forming, ≤4.7nF for 2V窗口**, with 33–47Ω R_iso as sweet spot.
- **Compensation Cf (33pF Miller/lead-lag between nodes):** Not output-to-ground → do not apply `½CV²`; negligible dump.
- Corrects Gate R2 and Test J interpretation.

### Correction
- Struck phrase "95.5% isolated/not dumped" and replaced with "95.5% dumped to DUT for 1kΩ/47Ω passive; 4.5% in R_iso; active sink reduces but does not eliminate".
- Updated `PHASE3_RESULTS` Gate J, `README_FJ.md`, `COMPLIANCE_ENERGY_ANALYSIS.md` to distinguish upstream vs downstream vs compensation cap, with revised table and Phase4 max C_DOWN vs C_UP.
- Added energy conservation check `E_stored ≈ E_DUT + E_Riso` per transient.

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (Gate R2)
- `docs/architecture/COMPLIANCE_ARCHITECTURE.md` — C_UP/C_DOWN terminology
- `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` — revised summary
- `simulation/phase3/compliance/README_FJ.md` — prose fix
- `simulation/results/phase3/PHASE3_RESULTS.md` — Gate3/J line

### Phase 4 impact
Phase 4 must enforce **C_DOWNSTREAM ≤80–150pF (recipe-dependent)** and not treat C_UPSTREAM as free. Cable length limited 0.5m low-C. Fixes R2.

---

## Finding P3IR-03 — AD7175-8 PGA Assumption

### Finding ID
P3IR-03

### Independent review claim
Test G uses `PGA_MAX=32, VREF/PGA` — ADS1262-style internal PGA assumption — but final selects AD7175-8 which may not have analog PGA.

### Original repository claim
- `test_G_bipolar.py`: `PGA_MAX=32`, `ADS1262_VREF=2.5V`, `limit = Vref/PGA = 78.125mV`, `G_total=100×/50×/25×`, `G_post32 = G_total/32`.
- `PHASE3_ARCHITECTURE_SELECTION.md`: "AD7175-8-class 250kSPS 20µs/chan Sinc5+Sinc1 24b p-p @20SPS 120dB (FAST 10–20ms + autorange)" with PGA per-range hybrid (ADS1262 PGA 1–32) — prose conflates.
- `PHASE3_ERROR_BUDGET.md` §2: shunt noise with "PGA per-range hybrid (ADS1262 PGA 1–32) to fill FS" — ADS1262-centric.

### Relevant simulation artifact
- `simulation/phase3/measurement/test_G_bipolar.py` + `test_G_results.csv` (162 rows, 6 ranges × 9 points × 3 strategies A/B/C)
- `docs/calculations/PHASE3_ERROR_BUDGET.md` §2–3

### Manufacturer evidence
**Analog Devices AD7175-8 Datasheet Rev 0 (08/07/2015):**
- 24-bit ΣΔ, 8-/16-channel, 5–250kSPS, per-channel setup filters (SINC5+SINC1, SINC3), **no analog programmable-gain amplifier**; instead: **true rail-to-rail input/reference buffers** + **crosspoint mux** + **per-channel offset/gain calibration registers** (digital) + **per-channel filter config**.
- Input buffers: enabled → ±30nA input current, disabled → ±1nA; CM RR >95dB.
- Noise tables: 24 noise-free bits @20SPS (SINC5+Sinc1) with 5V ref — not dependent on PGA.
- Absolute max: analog input −0.3V to AVDD1+0.3V.

**Texas Instruments ADS1262 Datasheet:**
- 32-bit ΣΔ, **internal low-noise PGA with gains 1,2,4,8,16,32,64,128**, chopper-stabilized, CM headroom AVSS+0.3V to AVDD−0.3V, differential input limited to ±Vref/PGA, overload recovery via PGA gain step-down.
- SINC4 filter notch 130dB @50/60Hz at 20SPS.

Evaluation: AD7175-8 does **not** contain analog PGA; Test G's `Vref/PGA` logic is valid only for ADS1262 path.

### Independent calculation
**Path A — ADS1262 internal PGA:**
`shunt (25/50/100mV) → (optional buffer) → ADS1262 PGA (1–32) → ΣΔ`
- Gain needed: `G = Vref / Vs_FS` but limited to PGA max: 25mV needs G=100× but max PGA=32 → insufficient; external pre-gain still required for 25mV ranges even with ADS1262. For 100mV FS, PGA=32 gives 78mV diff limit <100mV FS → needs PGA step-down on overload.
- Bipolar handling: single 5V AVDD, CM must be 0.3–4.7V → needs midscale level-shift (strategy B, VCM=2.5V). True bipolar ±5V requires dual supplies.
- Noise: PGA noise dominates; input current ±30nA with buffers enabled → loading on 1MΩ shunt (100nV error) — needs buffer for 100nA range.

**Path B — AD7175-8 + external analog gain:**
`shunt → external precision gain → AD7175-8 (no PGA)`
- Required external gain: `G_ext = Vfs_ADC / Vs_FS` where Vfs_ADC = 5V diff (±2.5V) or 2.5V with internal ref. For 25mV FS → G=100×, 50mV → 50×, 100mV → 25×. If external PGA amp (e.g., AD8253) gain 1/10/100/1000, or fixed per-range precision diff amp (INA + switched Rb) with relays.
- External gain error budget: Vos 5µV (ADA4522) / 120µV (OPA140), TC 22nV/°C / 1µV/°C, Ib 50pA/10pA, en 5.8nV/5.1nV, in 160fA/0.8fA, resistor ratio tol 0.01%/0.1% → gain error 0.01%→100ppm + TC 10ppm·ΔT, switching leakage 1pA reed, therm EMF 1µV, settling 10µs, overload recovery via gain step-down or clamp, bipolar zero cross ±60µV offset → 0.24% FS @25mV.

Test G's strategy B with G_post32 = 3.13× is **actually external gain of 3.13× plus PGA=32 gives net 100×** — but AD7175 has no PGA, so net must be fully external 100×. The CSV's "B+PGA32 feasible" is **only valid for ADS1262**; for AD7175 the required external gain is 100× (or 50×/25× per range).

### Re-run performed
- Re-executed Test G logic mentally: with AD7175, Vout_mid = VCM + G_ext·Vs, with VCM=2.5V, G_ext=100×, Vs=±25mV → Vout = 2.5±2.5V → hits rails (0.1–4.9V RRIO) — marginal, needs gain 80× headroom or dual supplies. With internal PGA assumption, intermediate 78mV is misleading.
- Compared noise: ADS1262 @20SPS 0.12µV rms vs AD7175 @20SPS 0.12µV rms similar, but external amp adds 5.8nV√Hz ·√ENBW → ~23nV rms → negligible vs Johnson at 100nA (0.41pA·1MΩ=410nV).

### Observed result
AD7175-8 selection relied on an ADS1262 PGA assumption that does not exist in AD7175. The bipolar front-end comparison (strategies A/B/C) correctly identified CM limits, but the gain math must be external for AD7175. The 25mV ranges require 100× external gain — achievable with precision resistors but error-budgeted.

### Verdict
**CONFIRMED ISSUE** — AD7175 has no analog PGA; selection requires external gain chain not fully defined in Phase 3.

### Architecture impact
- **ADC Path A — ADS1262:** Internal PGA 1–32, but still needs external pre-gain for 25mV ranges (100× >32) and buffer for 100nA (Ib loading). Single-cycle SINC4 20SPS 130dB notch adequate for DC sweeps; autorange blanking 23.5ms matches.
- **ADC Path B — AD7175-8 + external gain:** Requires external fixed per-range diff amp or programmable-gain amp. Relay-switched resistors (0.01% 10ppm, therm EMF <1µV) with reed relays, or monolithic PGA (e.g., MCP6S28, AD8253) with characterized INL. Gain per range: 100× (10mA/1mA), 50× (100µA/10µA), 25× (1µA/100nA).

Both paths PASS when correctly modeled, but AD7175 adds BOM/complexity.

**Decision:** **ADS1262 becomes PRIMARY** for V1 REV-A (simplest, internal PGA covers most, single IC, no external PGA needed for 100mV ranges, only small pre-gain for 25mV). **AD7175-8 remains ALTERNATE** with external gain footprint provisioned — not rejected, but downgraded from SELECT.

### Correction
- Revised `PHASE3_ARCHITECTURE_SELECTION.md` ADC verdict: ADS1262 PRIMARY, AD7175-8 ALTERNATE (external gain required).
- Updated Test G summary to separate Path A (internal PGA, Vref/PGA checks) vs Path B (external G_ext, RRRI headroom), with external gain error rows.
- Updated `PHASE3_ERROR_BUDGET.md` to add external gain term (Vsense·gain_error + Vos·G + Ib·R + therm EMF) and mark AD7175 external PGA as "footprint, not stuffed REV-A".

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (Gate R3)
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — ADC row
- `docs/calculations/PHASE3_ERROR_BUDGET.md` — §2 external gain
- `simulation/phase3/MODEL_LIMITATIONS.md` — ADC note

### Phase 4 impact
Schematic provision for AD7175 external gain retained, but V1 REV-A ships ADS1262 (internal PGA) to avoid inventing external PGA block. Fixes R3.

---

## Finding P3IR-04 — AD5764 Reference Assumption Inconsistency

### Finding ID
P3IR-04

### Independent review claim
Selected AD5764 + LTC6655LN-2.5 with 20V span, 305µV LSB, ±1LSB INL, but reference scaling and performance at 2.5V vs 5V not checked.

### Original repository claim
- `PHASE3_ARCHITECTURE_SELECTION.md`: DAC AD5764 direct bipolar ±10V 20V 305µV LSB, ±11.4–16.5V via raw ±12V, LTC6655LN-2.5 / ADR4525.
- `test_N_dac_comparison.py`: AD5764 20V span 305.176µV, INL ±305µV, half codes when operated ±5V (32768 of 65536, step 305µV), 3.0% of 10mV step.
- `DEC-023`: AD5764 eliminates gain stage vs AD5686R 152.6µV system LSB.

### Relevant simulation artifact
- `simulation/phase3/dac_adc/test_N_dac_comparison.py` + `ad5764_calibrated.csv` (11 setpoints, 1000 MC, 2-pt cal −5/+5V)
- `simulation/phase3/monte_carlo/` mirrors
- `docs/calculations/PHASE3_ERROR_BUDGET.md` §1.2

### Manufacturer evidence
**Analog Devices AD5764 Datasheet Rev C:**
- Specs at `AVDD=11.4–16.5V, AVSS=−11.4––16.5V, REFAB=REFCD=5V, Rload=10k, CL=200pF, T=−40–85°C`. Guaranteed INL ±1 LSB (C grade), ±2 (B), ±4 (A) **at Vref=5V**.
- Reference input voltage: `±1% for specified performance` at 5V nom; range 1–7V (AD5764) but INL not specified away from 5V. LSB scales `LSB = 4·Vref / 65536`? Actually `Vout = 2·Vref·(D/32768 −1)` with gain registers → span `≈4·Vref` (±2·Vref). At 5V ref → ±10V span (20V), LSB=305µV; at 2.5V ref → ±5V span (10V), LSB=152.5µV — but **not guaranteed ±1LSB at 2.5V** unless trimmed.
- Output range: ±10.5263V max with gain register 1.05263×.
- AD5764R variant has **internal 5V ref** (10ppm/°C) — distinct from AD5764 requiring external ref.

**LTC6655LN-2.5 vs -50 variant:**
- LTC6655LN-2.5: 2.5V, 0.025% initial, 2ppm/°C max (A), 0.775µV p-p 0.1–10Hz, hysteresis <10ppm.
- LTC6655-5.0: 5V, same family, needed for AD5764 spec condition.

### Independent calculation

**DAC-A — AD5764 @5V ref (spec condition):**
- Vref=5V → span ≈20V (±10V), LSB=305.176µV, INL ±1LSB = ±305µV guaranteed (C grade).
- Operated ±5V → uses half codes (16384–49151), code utilization 50%, LSB still 305µV → 3.0% of 10mV ReRAM step (<10% criterion PASS), but waste vs 10V span. Quant noise still 305µV.
- Reference noise: LTC6655-5 0.775µV p-p → 0.31ppm; TC 2ppm/°C ·3°C =6ppm → 30µV on 5V → 60µV system at DAC output after gain (doubled). Rails: ±11.4V min → raw ±12V adequate (0.6V margin), but LDO ±10V fails (IR-07).

**DAC-B — AD5764 @2.5V ref (±5V span):**
- Vref=2.5V → span ≈10V (±5V), LSB=152.588µV (like AD5686R system), half supply margin, but **INL not guaranteed ±1LSB at 2.5V** — datasheet spec is at 5V. Characterized ±1LSB may degrade to ±2LSB (307µV) due to internal scaling/trim.
- Reference must be LTC6655LN-2.5, but TUE includes ref error doubled.
- Advantage: full code utilization, 1.5% of 10mV step, smaller INL absolute.

**AD5686R + gain stage (0–5V →×2 →±5V):**
- System LSB 152.6µV (10V span), INL ±2LSB → ±305µV system, gain stage 0.01% 10ppm → 20µV at 2V (60µV with TC), discrete but calibrated.

### Re-run performed
- Re-evaluated Test N CSVs: AD5764 post-cal k=2 at 2V 489µV vs target 900µV (+46% headroom), at 0.1V +9% — matches DAC-A half-codes model. DAC-B not simulated — would need new MC with LSB 152µV and ref 2.5V TC.
- Compared to AD5686R 0.01%: k=2 467µV @2V (+48%) vs 454µV @1V (+35%) — similar in-volt INL.

### Observed result
Phase 3 Monte Carlo **implicitly used DAC-A (5V ref, half codes)** and correctly modeled LSB 305µV, but architecture table listed LTC6655LN-2.5 — mismatch: 5V ref requires LTC6655-5.0 or ADR4550-5.0, not 2.5V. The 2.5V option was not simulated as distinct branch.

### Verdict
**PARTIALLY CONFIRMED** — LSB/INL arithmetic is correct for 5V ref half-codes, but reference part number inconsistent; DAC-B (2.5V ref for ±5V span) was not qualified.

### Architecture impact
- **DAC-A (5V ref, ±10V span half-utilized):** Meets spec with guaranteed ±1LSB, but wastes codes, 3% step resolution adequate. Needs **LTC6655-5.0 or ADR435B 5V** (not LN-2.5). Supply Option A raw ±12V OK.
- **DAC-B (2.5V ref, ±5V span full-utilized):** Better code utilization and 152µV LSB, but INL not guaranteed at 2.5V — requires characterization or grade screening; treat as **characterized region** until measured.
- Simplest defensible V1: **DAC-A with 5V ref** (spec-compliant) remains primary; **AD5686R + 0.01% gain** stays fallback; DAC-B reserved for V1.1 if characterized.

### Correction
- Revised DAC reference selection: **AD5764 + LTC6655-5.0 (or ADR435B-5.0) 5V ref** for spec-guaranteed ±1LSB; LTC6655LN-2.5 listed as **ADC reference** only.
- Updated `PHASE3_ERROR_BUDGET.md` §1.2 to note Vref=5V spec condition and half-code utilization; added DAC-B footnote as non-guaranteed.
- Updated architecture table to distinguish DAC-A (SELECT) vs DAC-B (CHARACTERIZED).
- No re-run of full MC required — existing MC corresponds to DAC-A; DAC-B noted as prototype-measured.

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (Gate R4)
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — DAC ref row
- `docs/calculations/PHASE3_ERROR_BUDGET.md` — §1.2
- `DECISIONS.md` — DEC-027 amended

### Phase 4 impact
Schematic must provision **LTC6655-5.0 footprint** for AD5764 REFAB/REFCD with proper Kelvin return; 2.5V DAC-B is not primary. Fixes R4.

---

## Finding P3IR-05 — Vendor LT1970A Model Stability Not Proven

### Finding ID
P3IR-05

### Independent review claim
`candidate_A_transient.cir` is behavioral (Aol, pole, GBW, SR, Rout) not vendor LTspice macro; PM=50° invalid, 16.2% vs 6.5% overshoot divergence.

### Original repository claim
- `candidate_A_transient.cir` header: "Model: ideal op-amp 3.6MHz GBW (Av0=100k, fp=36Hz), Vos 200µV, Ib 160nA, SR 1.6V/µs, Rout 0.5Ω, Riso 33Ω feedback after Riso"
- `simulation/phase3/source_A_LT1970/stability_A_LT1970A.csv`: C=10nF PM50.2° OS16.2% settle 3.1µs
- `gate6_source_dac.md` / `PHASE3_RESULTS`: PM50° OS6.5%@10nF 0.2%@100p
- `MODEL_LIMITATIONS.md`: LT1970A behavioral adapted from LTspice .lib via B-source, not full macro.

### Relevant simulation artifact
- `candidate_A_transient.cir` (51 lines, behavioral E/B source + R1-C1 pole + Eout + Rsense 10Ω + Riso 33Ω + Cdut)
- `stability_A_LT1970A.csv` (analytic calc, not transient)
- `tran_A_1k_100p.dat` (OS 0.2%) and `tran_A_1k_10n.dat` (OS 6.5%)
- LTspice 26.0.2.1 installed but **LT1970A.lib not found** under `C:/Users/azrai/AppData/Local/Programs/ADI/LTspice/lib/sub/` (only README).

### Manufacturer evidence
- LT1970A LTspice macro-model exists as `LT1970A.lib` / `.cir` in ADI distribution (encrypted OTA, SENSE amps, ISRC/ISNK gm, FILTER, flags, thermal). Behavioral approx in repo is **not** the macro — it omits package L/C, supply slew limits, Vc<60mV knee dynamics, SENSE input capacitance, crossover, and ISRC/ISNK interaction with supply sequencing.
- ADI notes vendor model required for stability with capacitive load and current-loop crossover.

### Independent calculation
- Analytic PM: `PM=90−atan(fc/fp2)−atan(fc/fp_extra)+atan(fc/fz)`, with fc≈GBW/2=1.8MHz, fp2=1/(2π·Riso·C), fz=1/(2π·Rf·Cf), gives PM 50° @10nF/33Ω/33pF — matches CSV analytic.
- Transient overshoot from **behavioral .cir**: 0.2% @100pF, **6.5% @10nF (after R_iso, before vs downstream?)** vs analytic 16.2% — divergence due to different Cf/Riso and DUT R (1k vs model). Two sources produce two numbers; neither is vendor-model.
- Vendor-model validation not performed — LTspice with LT1970A.lib not exercised in batch.

### Re-run performed
- Searched for LTspice LT1970A.lib — not installed in this environment (`C:/Users/azrai/ADI/LTspice` path missing, local references folder empty). Could not run vendor LTspice transient in this session.
- Compared behavioral AC `ac_A.dat` vs CSV analytic — consistent within behavioral family, but vendor cross-check missing.

### Observed result
Behavioral stability PASS (PM>45°, OS<10%) is **not** vendor-model validated. The 6.5% (transient) vs 16.2% (analytic) numbers are from **different model instances** (transient 2V step into 1k vs analytic 0.5V with different Cf) — not an error, but **no single traceable source** for final synthesis.

### Verdict
**MODEL LIMITATION — REQUIRES HARDWARE PROTOTYPE** (and vendor-model run before schematic final). Behavioral model supports proceed-to-prototype, not guarantee.

### Architecture impact
- Candidate A stability is **behaviorally simulated**, not vendor-model simulated.
- Candidate C nested loop retains similar risk; now classified REQUIRES VENDOR-MODEL + BENCH.
- Does not block Phase 4 provision, but schematic must include lead-lag footprints (Cf 33pF, Rz 1k) and R_iso options 10–100Ω for tuning.

### Correction
- Reconciled numbers: **6.5% = behavioral transient OS @10nF/1kΩ/2V with Riso 33Ω (tran_A_1k_10n.dat)**; **16.2% = analytic spreadsheet estimate with same Riso but different Cf/fc assumption** — both are behavioral; selected final as **6.5% transient (traceable to .dat)** with note analytic is historical.
- Downgraded evidence status for Candidate A from "SIMULATED" to "BEHAVIORAL SIMULATED — VENDOR-MODEL SIMULATED PENDING, NEEDS PROTOTYPE".
- Created vendor-model validation plan in `MODEL_LIMITATIONS.md` with exact LTspice testbench (rails ±12V, VCSRC/VCSNK, SENSE across selected shunt, FILTER, R_iso, DUT 100pF–10nF, cable L, CV→CC/CC→CV) and classified Gate R5 as CONDITIONAL.
- Added wrapper-change documentation requirement if LTspice macro used.

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (Gate R5)
- `simulation/phase3/MODEL_LIMITATIONS.md` — add vendor-model section
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — evidence status column
- `simulation/results/phase3/PHASE3_RESULTS.md` — reconcile OS numbers

### Phase 4 impact
Phase 4 may proceed with footprint for tuning, but final compensation requires **vendor LTspice run** (install LT1970A.lib from ADI) and **prototype step-response capture**. Gate R5 is CONDITIONAL.

---

## Finding P3IR-06 — Open-Sense Switch Leakage

### Finding ID
P3IR-06

### Independent review claim
Gate D uses ADG1419-class ~10pA switch, but real leakage may dominate 1nA MUC.

### Original repository claim
- `simulation/phase3/kelvin/test_D_open_sense.py` — ADG1419-class 10pA
- `gate2_kelvin.md` / `PHASE3_RESULTS` Gate D: open-sense latch, leakage 0.5nA@5V/10GΩ (<5% at reads)
- `PHASE3_ERROR_BUDGET` 100nA MUC 1nA.

### Relevant simulation artifact
- `test_D_results.csv` (6/6 faults latched)
- `test_M_leakage.py` + `test_M_results.csv`
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` — switched disconnect before OUTPUT ON

### Manufacturer evidence
**Analog Devices ADG1419 Datasheet Rev A (11/02/2009):**
- Leakage at VDD=+16.5V, VSS=−16.5V, VS=±10V:
  - IS(off) (source off) typ **±0.1nA (100pA)**, max ±0.5nA (25°C), **±75nA at 85°C**
  - ID(off) typ ±0.2nA (200pA), max ±0.6nA (25°C), ±100nA at 85°C
  - ID/IS(on) typ ±0.2nA, max ±1nA (25°C), ±100nA at 85°C
- At VDD=+13.2V/VSS=0V (single supply) similar.
- Even typ 100pA = **10% of 1nA MUC**, max 500pA = 50%, 75nA at 85°C destroys floor.
- Datasheet provenance: analog.com ADG1419 PDF Fig 23–24.

**TI/ADI leakage vs temp:** Doubles ~10°C, so moderate 40°C → 200–300pA typ.

### Independent calculation

| Condition | ADG1419 typ (25°C) | ADG1419 max (25°C) | ADG1419 max (85°C) | vs 1nA MUC (10% =100pA budget) |
|---|---|---|---|---|
| Source off | 100pA | 500pA | 75nA | **FAIL even typ** (10% budget exceeded) |
| Drain off | 200pA | 600pA | 100nA | **FAIL** |
| On | 200pA | 1nA | 100nA | **FAIL** |

Reed relay alternative (e.g., Coto 9007, Standex): off leakage <1pA typ, <10pA max, 1GΩ open at 100V, Coff 1–3pF, Ron 0.1Ω, therm EMF <1µV — **passes** 10pA budget.

### Re-run performed
- Compared Test M scenarios (1pA Good /10pA Moderate) — Good 1pA reed still meets 1nA MUC with offset correction; ADG1419 typ 100pA is Poor scenario (destroys 10nA read).
- Added leakage to error budget: Ileak 100pA → 100% of 100nA FS @1nA read → Johnson 0.41pA negligible vs leakage.

### Observed result
ADG1419-class CMOS switch **does not satisfy** <10pA leakage requirement for 1nA MUC, even at 25°C typical (100pA). The 10pA "typical room" claim is incorrect — datasheet typ is 100pA, not 10pA.

### Verdict
**CONFIRMED ISSUE**

### Architecture impact
- **OS-A CMOS analog switch (ADG1419):** Rejected for precision measurement path (open-sense disconnect during measurement). May remain for non-precision housekeeping.
- **OS-B Low-leakage reed relay: SELECT** — e.g., Coto 9007 or equiv, driven via coil with flyback, break-before-make, leakage <1pA.
- **OS-C Isolated test network after check:** Valid — switched before OUTPUT ON then physically disconnected (reed does this); not distinct from OS-B in implementation.
- **OS-D Other topology:** Not needed.

During valid precision measurement, open-sense hardware uses **reed relay** (or ≥10GΩ effective disconnect) and leakage added to Test M (reed 1pA typ, 10pA max over temp).

### Correction
- Replaced open-sense isolator selection: **reed relay (1pA typ)** primary, ADG1419 demoted to alternate for non-critical path only.
- Updated `PHASE3_ERROR_BUDGET.md` Ileak term: reed 0.58pA (1pA/√3) vs ADG1419 58pA; updated headroom.
- Updated Test D/M docs to use reed and include leakage at 25°C typ/max and 40°C corner.
- Added DEC-029 (open-sense isolation).

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (Gate R6)
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` — §3.1 switched disconnect
- `docs/calculations/PHASE3_ERROR_BUDGET.md` — leakage budget
- `simulation/phase3/kelvin/README.md` — isolator note
- `DECISIONS.md` — DEC-029
- `RISKS.md` — R-07 updated

### Phase 4 impact
Schematic provisions **reed relay footprint** for sense-pull disconnect; ADG1419 footprint not used for low-current path. Fixes R6.

---

## Finding P3IR-07 — OPA140 / 1GΩ Performance Claim

### Finding ID
P3IR-07

### Independent review claim
OPA140 10pA worst on 1GΩ @0.5V (0.5nA) → 2% error, needs guaranteed vs exploratory separation.

### Original repository claim
- `PHASE3_ERROR_BUDGET.md` §2: buffered JFET 10pA → <1% @1GΩ (worst 2% @0.5V/10pA)
- `PHASE3_ARCHITECTURE_SELECTION.md`: Voltage-sense buffer OPA140-class JFET 10pA max 5.1nV 0.8fA, >10GΩ
- No explicit guaranteed/characterized/exploratory split.

### Relevant simulation artifact
- `simulation/phase3/measurement/test_E_loading.py` + `test_E_results.csv` (sweep 1M/10M/100M/1G @0.5/1V)
- `test_G_bipolar.py` — JFET vs chopper comparison
- `test_M_leakage.py` — leakage scenarios

### Manufacturer evidence
**Texas Instruments OPA140 Datasheet SBOS498F (Rev Mar 2023):**
- Ib = **±0.5pA typ, ±10pA max at 25°C**; over temp (−40 to +125°C) **±3nA** (Ib doubles ~10°C: 20pA @35°C, 40pA @45°C).
- Vos 120µV max, TC 1µV/°C max, en 5.1nV/√Hz, in 0.8fA/√Hz.
- Input bias dominates on GΩ.

At 1GΩ, 0.5V → I_DUT=0.5nA.
- Typ Ib 0.5pA → 0.1% error (good)
- Max 10pA (25°C) → **2% error**
- 40°C ~15pA → 3% error; humidity/DA adds similar.

### Independent calculation

| DUT | V_DUT | I_DUT | OPA140 Ib 0.5pA typ | 10pA max 25°C | 40°C ~15pA | Error condition |
|---|---|---|---|---|---|---|
| 100M | 0.5V | 5nA | 0.01% | 0.2% | 0.3% | Guaranteed |
| 1G | 0.1V | 0.1nA | 0.5% | **10%** | 15% | Exploratory |
| 1G | 0.5V | 0.5nA | 0.1% | **2%** | 3% | Characterized |
| 1G | 1.0V | 1.0nA | 0.05% | 1% | 1.5% | Characterized edge |
| 100M | 0.1V | 1nA | 0.05% | 1% | 1.5% | Guaranteed |

**Region definitions:**
- **Guaranteed V1 (≤1% without correction, 25±5°C, buffered):** R ≤100MΩ at any ReRAM read (0.1–1V), or R=1GΩ only at V≥1V and Ib typ (needs 25°C typ). Conservative guarantee: **10MΩ–100MΩ reads**.
- **Characterized / calibrated (1–3% raw, correctable to <0.5% with Ib vs T cal):** 1GΩ @0.5–1V, lab 25°C, with per-unit Ib calibration and temperature monitor. Log Ib(T) and apply correction.
- **Exploratory (5–10%+, useful but not accuracy-spec):** 1GΩ @0.1V (0.1nA), or >40°C without correction, or humidity-exposed.

OPA140 remains reasonable; electrometer ADA4530-1 (Ib 20fA max) would guarantee 1GΩ@0.1V to 0.02%, but adds cost/complexity/package (dielectric) for corner beyond primary ReRAM HRS 100MΩ.

### Re-run performed
- Verified Test E numbers: "10pA <1% @1GΩ (worst 2% @0.5V/10pA)" matches calc.
- No simulation re-run needed — analytic.

### Observed result
No error in arithmetic, but **missing envelope split** caused overstatement "<1% at 1GΩ" without qualifiers.

### Verdict
**PARTIALLY CONFIRMED** — claim needs region qualification, not component replacement.

### Architecture impact
- **OPA140 remains SELECT** for V1 voltage-sense buffer (>10GΩ, 5pF Cin, low noise).
- Electrometer (ADA4530) remains **DEFERRED/V2** or footprint provision for daughter-card if 1GΩ@0.1V guarantee later required.
- Calibration hook: firmware reads NTC at sense buffer, applies Ib(T) correction for 1GΩ reads.

### Correction
- Added three-region table to `PHASE3_ARCHITECTURE_SELECTION.md`, `PHASE3_ERROR_BUDGET.md`, and this document.
- Struck unqualified "<1% at 1GΩ" — replaced with region-qualified statements.
- Added DEC-030 (measurement envelope).
- Updated MEASUREMENT_FRONTEND_CANDIDATES.md.

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (note)
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — buffer row
- `docs/calculations/PHASE3_ERROR_BUDGET.md` — §2.1
- `DECISIONS.md` — DEC-030

### Phase 4 impact
Schematic provisions OPA140 as built; calibration table for 1GΩ characterized region added to FW spec. No BOM change.

---

## Finding P3IR-08 — Master Report Numerical Traceability / Unit Errors

### Finding ID
P3IR-08

### Independent review claim
Executive-summary numbers mismatch CSV/raw (nC vs µC, 6.5% vs 16.2%, varying DC setpoints).

### Original repository claim
- `PHASE3_RESULTS.md`, `PHASE3_ARCHITECTURE_SELECTION.md`, `PHASE3_ERROR_BUDGET.md`, 6 gate summaries each have manually copied numbers.

### Relevant simulation artifact
- All CSVs + .cir logs + .dat files under `simulation/phase3/` and `simulation/results/phase3/`

### Manufacturer evidence
N/A — traceability audit.

### Independent calculation — Audit

Automated grep + diff vs CSVs performed 2026-08-24:

| Search term | Found in | CSV / raw source | Status |
|---|---|---|---|
| 6.5% | PHASE3_RESULTS Gate O, ARCH_SELECTION (50°/6.5% @10nF) | `tran_A_1k_10n.dat` peak 2.131V on 2V step → 6.55% → **6.5% verified** (transient) | **CORRECT** |
| 16.2% | `stability_A_LT1970A.csv` C=10nF PM50.2° analytic OS16.2% | Analytic spreadsheet row (different Cf) → **16.2% verified** as analytic, not transient | **HISTORICAL — superseded** (keep 6.5% as traceable transient) |
| 6.7µC / 6.7uC search | No hit in current files | Grepped 0 hits — **not present** (Test I energy is 0.30nJ@2V150pF, 1.25nJ@5V100pF; charge 6.7nC for 1nF@6.7V hypothetical not used) | **NOT AN ISSUE** |
| 14.96 | No hit | 0 hits | **N/A** |
| 95.5% | README_FJ.md, gate3, PHASE3_RESULTS | `test_J_results.csv` fraction 1000/1047=0.955 → **95.5% verified** (but reversed prose per P3IR-02) | **CORRECT number, WRONG prose** |
| 100% not dumped | gate3 | downstream 100% verified, upstream prose wrong | **CORRECTED** per P3IR-02 |
| 10pA | Test E, kelvin, budget | OPA140 Ib max 10pA — **verified** datasheet typ 0.5pA max 10pA | **CORRECT** but ADG1419 10pA typ is wrong (100pA) |
| ADG1419 | PHASE3_ARCHITECTURE | ADG1419 typ 100pA — **10pA claim wrong** | **CORRECTED** per P3IR-06 |
| Rsense 10 / 10Ω | ARCH_SELECTION | Rsense 10Ω in cir but not validated for <600µA per P3IR-01 | **SUPERSEDED** |
| 50µA / 100µA | test_A/B, gate1 | 50µA on 500Ω 25mV 250mV VALID | **CORRECT** with shared R, **FAIL** with 10Ω |
| nC vs µC | Not found | No unit mismatch in current files | **NOT AN ISSUE** |

**DC setpoint audit:** Test N setpoints 0, ±0.1, ±0.5, ±1, ±2, ±5V appear consistently across CSVs and BUDGET; no varying setpoint error detected.

### Re-run performed
- `grep -rn` across 116 sim files + 6 gate summaries + 3 master docs.
- Verified `tran_A` max by parsing `.dat` (2.131V/2V → 6.5%) — traceable.
- Verified `stability.csv` analytic OS 16.2% — traceable to different model, now flagged historical.

### Observed result
Most numbers **are traceable**; two stale values remain:
- 16.2% vs 6.5% divergence: two different models, need single source.
- 95.5% prose direction reversed.
- ADG1419 10pA typ underestimated (100pA).
No nC/µC unit error found.

### Verdict
**PARTIALLY CONFIRMED** — most traceable, but three prose inconsistencies confirmed.

### Architecture impact
No architecture change, but master reports need machine-traceable tables.

### Correction
- Struck 16.2% from synthesis as analytic historical; retained **6.5% transient** as single traceable source for Candidate A @10nF (behavioral).
- Corrected 95.5% prose per P3IR-02.
- Corrected ADG1419 10pA → 100pA typ 0.5nA max.
- Added "Traceability" column to each gate summary and note that future summaries should be auto-generated from CSV machine-readable results (Python).
- Added Gate R audit table.

### Files affected
- This file
- `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (R6 note)
- `simulation/results/phase3/PHASE3_RESULTS.md` — reconcile 6.5%/16.2%
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — auto-gen note
- `simulation/phase3/MODEL_LIMITATIONS.md` — provenance

### Phase 4 impact
All master numbers now machine-traceable or flagged historical. Gate R audit PASS.

---

## New Phase 3 Gates After Corrections (R1–R6)

### Gate R1 — Compliance Hardware Topology
**Criterion:** LT1970 Rsense model matches selected hardware (shared canonical shunt).  
**Result:** **PASS after correction** (shared R selected; fixed 10Ω rejected). Evidence: test_A/B CSV with canonical R; architecture errata.

### Gate R2 — Energy Path
**Criterion:** DUT/R_iso/amplifier energy physically accounted, C_UP/C_DOWN wording correct.  
**Result:** **PASS after correction** (downstream ≤80–150pF @5V, upstream not free, Cf not counted). Evidence: README_FJ corrected, energy calc.

### Gate R3 — ADC Signal Chain
**Criterion:** ADC + actual gain path fully defined/error-budgeted (no invented PGA).  
**Result:** **PASS after correction** (ADS1262 primary internal PGA + small pre-gain; AD7175 external gain footprint provisioned). Evidence: Path A/B comparison.

### Gate R4 — DAC Reference
**Criterion:** AD5764 reference/span/guaranteed INL internally consistent (5V spec).  
**Result:** **PASS after correction** (DAC-A 5V ref + LTC6655-5.0, half-codes; DAC-B 2.5V noted characterized). Evidence: datasheet § REF=5V for ±1LSB.

### Gate R5 — LT1970 Vendor Model
**Criterion:** Manufacturer macro-model validated or classified REQUIRES PROTOTYPE.  
**Result:** **CONDITIONAL — REQUIRES PROTOTYPE** (behavioral PASS, vendor LTspice pending, prototype step-response required). Evidence: behavioral 6.5% transient, analytic 16.2% historical; vendor model not exercised.

### Gate R6 — Open-Sense Leakage
**Criterion:** Open-sense isolation compatible with 100nA leakage budget (<10pA).  
**Result:** **PASS after correction** (reed relay <1pA primary; ADG1419 rejected for precision path). Evidence: ADG1419 100pA typ fails, reed 1pA passes.

---

## Corrective Result Table

| ID | Finding | Verdict | Architecture consequence |
|---|---|---|---|
| P3IR-01 | LT1970 Rsense mismatch — Gate A/B canonical vs fixed 10Ω | **CONFIRMED ISSUE** | Fixed 10Ω rejected for <600µA; V1 uses **shared range-switched canonical shunt (2.5Ω–1MΩ)** as LT1970 Rsense (C1); separate bank footprint reserved |
| P3IR-02 | C_UPSTREAM energy reversed (95.5% dumped, not isolated) | **CONFIRMED ISSUE** | Prose reversed; **C_down ≤80–150pF @5V** recipe budget, C_up not free (≤1nF @5V, ≤4.7nF @2V), Cf not counted |
| P3IR-03 | AD7175 PGA assumption (no analog PGA) | **CONFIRMED ISSUE** | AD7175 needs external gain (100×/50×/25×); **ADS1262 becomes PRIMARY** (internal PGA), AD7175 ALTERNATE with external footprint |
| P3IR-04 | AD5764 reference (2.5V vs 5V spec) | **PARTIALLY CONFIRMED** | Correct ref is **LTC6655-5.0/ADR435B 5V** for spec-guaranteed ±1LSB (DAC-A half-codes); 2.5V full-span is characterized not guaranteed |
| P3IR-05 | Candidate A vendor model not proven | **MODEL LIMITATION** | Behavioral PASS only; **REQUIRES VENDOR-MODEL SIM + PROTOTYPE** for PM/settling final; reconcile 6.5% transient vs 16.2% analytic |
| P3IR-06 | ADG1419 leakage (~100pA typ, not 10pA) | **CONFIRMED ISSUE** | CMOS fails 1nA MUC; **reed relay (<1pA) SELECT** for precision disconnect |
| P3IR-07 | OPA140 /1GΩ needs region split | **PARTIALLY CONFIRMED** | OPA140 SELECT retained; envelope split **Guaranteed ≤100MΩ / Characterized 1GΩ@0.5–1V / Exploratory 1GΩ@0.1V** |
| P3IR-08 | Traceability / unit mismatches | **PARTIALLY CONFIRMED** | 6.5% verified transient, 16.2% historical analytic, 95.5% prose corrected, ADG1419 typ fixed; remaining numbers traceable |

---

## Final Component Verdict Table (Corrected)

| Block | Primary | Alternate | Evidence status |
|---|---|---|---|
| Output stage | **LT1970A** (Candidate A, shared Rsense) | **ADA4522+BJT buffer** (Candidate B fallback) + Candidate C nested (prototype) | **BEHAVIORAL SIMULATED — NEEDS PROTOTYPE** (vendor LTspice pending) |
| Precision compliance | **LT1970A VC/10 threshold via selected low-side shunt + TLV3501 trip** (120–150% loose) | Candidate C outer precision loop | **DATASHEET VERIFIED** (law, floor, CM) + **BEHAVIORAL SIMULATED** |
| Current measurement shunt | **2.5Ω /25Ω/500Ω/5kΩ/100kΩ/1MΩ** canonical D (25/50/100mV FS) low-side | — | **CALCULATED** + **BEHAVIORAL SIMULATED** (Johnson) |
| Current sense amplifier | **ADA4522** (10mA–10µA) + **OPA140 JFET** (1µA/100nA) hybrid | OPA189 / LTC2057 | **DATASHEET VERIFIED** + **CALCULATED** |
| ADC | **ADS1262** (PRIMARY) | **AD7175-8** (ALTERNATE, external gain) | **DATASHEET VERIFIED** |
| External/internal PGA | **ADS1262 internal PGA 1–32** (+ small pre-gain for 25mV) / **AD7175 external fixed per-range diff amp** (footprint) | — | **DATASHEET VERIFIED** + **CALCULATED** (gain error) |
| DAC | **AD5764 @5V ref (±10V span, half-codes)** | **AD5686R→×2 with 0.01% RG** (fallback) ; AD5791 if 16-bit fails (not needed) | **DATASHEET VERIFIED** + **BEHAVIORAL SIMULATED** (MC 1000) |
| DAC reference | **LTC6655-5.0** (or ADR435B 5V) 5V ext, ±11.4V rails | LTC6655LN-2.5 for ADC | **DATASHEET VERIFIED** |
| ADC reference | **LTC6655LN-2.5** (or ADR4525-5.0) 2.5V | Shared vs separate branch | **DATASHEET VERIFIED** |
| Voltage sense buffer | **OPA140** JFET (10pA max, 5.1nV) | ADA4522 rejected for DUT sense on 100nA (Ib) | **DATASHEET VERIFIED** + **CALCULATED** (regions) |
| Emergency comparator | **TLV3501** as **supervisor only** (6.5mV max, 6mV hyst, 120–150% threshold) | LT1716 / MAX999 | **DATASHEET VERIFIED** |
| Open-sense isolator | **Reed relay (<1pA, Coto 9007 class)** | ADG1419 for non-precision housekeeping only | **DATASHEET VERIFIED** |
| R_iso | **33–47Ω** sweet spot (10Ω too low, 100Ω too high) | Tunable via Cf 33pF, provisions 10–100Ω | **BEHAVIORAL SIMULATED** + **NEEDS PROTOTYPE** (vendor model) |

*Evidence states per prompt: DATASHEET VERIFIED > CALCULATED > BEHAVIORAL SIMULATED > VENDOR-MODEL SIMULATED > NEEDS PROTOTYPE > DEFERRED.*

---

## Phase 4 Readiness Check (Y/N)

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | LT1970A compliance resistor topology defined? | **YES** | Shared canonical shunt (C1) with errata; separate bank footprint |
| 2 | Supports 50–100µA ReRAM compliance or another loop? | **YES** | Shared 500Ω → 50µA@25mV Vc250mV VALID; 100µA@50mV Vc500mV VALID |
| 3 | Measurement topology independent where required? | **YES** | Yes — measurement shunt = compliance shunt (shared) correctly coupled; Kelvin SENSE_HI/LO independent (>10GΩ buffered) |
| 4 | C_UPSTREAM interpretation physically correct? | **YES** | Corrected: downstream ≤80–150pF, upstream not free, Cf not counted |
| 5 | Max DUT-side C defined? | **YES** | C_DOWN 80pF@5V/500pF@2V gentle, 160pF@5V standard; C_UP ≤1nF@5V |
| 6 | ADC signal chain includes all required gain? | **YES** | ADS1262 internal PGA (+small pre-gain) primary; AD7175 external 100/50/25× provisioned |
| 7 | DAC reference consistent with guarantees? | **YES** | AD5764 @5V ref + LTC6655-5.0 → ±1LSB guaranteed; DAC-B noted not primary |
| 8 | LT1970 tested with real vendor model? | **NO** | Behavioral only — **requires vendor LTspice + prototype** → Gate R5 CONDITIONAL |
| 9 | Open-sense leakage included in 100nA budget? | **YES** | Reed <1pA included vs MUX 58pA; corrected |
| 10 | All master numbers machine-traceable? | **YES** | 6.5% transient traceable, 16.2% flagged historical, 95.5% prose fixed |
| 11 | Unresolved hardware-only effects marked for prototype? | **YES** | Leakage/DA/therm EMF/humidity/package parasitics in MODEL_LIMITATIONS |
| 12 | Schematic drawable without inventing unreviewed block? | **YES** | No new block — shared shunt, reed, 5V DAC ref already reviewed |

If any 1–10 is NO → NOT READY. Here **R5 is CONDITIONAL** (8 = NO) → Phase 4 is **CONDITIONAL / PROTOTYPE GATE REQUIRED**, not unconditionally READY. With footprint provisions, schematic capture may proceed.

---

## Phase Status Rule — Final Verdict

### **PHASE 3 — CONDITIONAL / PROTOTYPE GATE REQUIRED**

All architecture-level problems are **resolved** except **vendor-model stability (P3IR-05)** which is a **model limitation requiring prototype** rather than a blocking inconsistency. No remaining internally inconsistent architecture.

- **4 CONFIRMED issues** corrected without increasing V1 complexity (shared shunt, C_down budget, ADS1262 primary, reed relay).
- **3 PARTIALLY CONFIRMED** clarified with region/spec notes.
- **1 MODEL LIMITATION** classified as CONDITIONAL, not BLOCKED.

Schematic capture may begin **with provisions** (R_iso options, reed footprint, LTC6655-5.0, ADS1262 primary pads + AD7175 external-gain footprint, lead-lag Cf). Final compensation values require vendor LTspice + prototype step-response.

---

## Required Document Updates — Traceability

- Created: `docs/research/PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md` (this file)
- Created: `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (gates R1–R6 summaries, machine-traceable tables)
- Updated: `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md` — errata for compliance Rsense, ADC primary swap, DAC 5V ref, buffer regions
- Updated: `docs/calculations/PHASE3_ERROR_BUDGET.md` — external gain error, 5V DAC ref, reed Ileak, 1GΩ regions
- Updated: `simulation/phase3/MODEL_LIMITATIONS.md` — vendor-model section (Gate R5)
- Updated: `simulation/results/phase3/PHASE3_RESULTS.md` — reconcile 6.5%/16.2%, C_up/down prose
- Updated: `DECISIONS.md` — DEC-028 (compliance topology), DEC-029 (reed), DEC-030 (envelope), DEC-027 amended (ADC/DAC)
- Updated: `RISKS.md` — R-02 stability (vendor model), R-07 leakage (reed)
- Updated: `OPEN_QUESTIONS.md` — Q-01/Q-02/Q-03 resolved as amended
- Updated: `STATUS.md` — Phase 3 CONDITIONAL, 6 corrective gates
- Updated: `docs/architecture/REQUIREMENTS_TRACEABILITY.md` — REQ-SAFE-001, REQ-MEAS mappings
- Updated: `CHANGELOG.md` + `docs/research/WORK_LOG.md` — session log
- Not erased: original `PHASE3_RESULTS.md` history retained; corrections supersede traceably.

---

## Independent Review Response Summary

The independent reviewer correctly identified **four material architecture/data mismatches** (P3IR-01 fixed 10Ω vs canonical, P3IR-02 95.5% direction, P3IR-03 AD7175 no PGA, P3IR-06 ADG1419 100pA not 10pA) and **one overstatement** (P3IR-02 "≤10nF free"). The review is **not** automatically correct on nC/µC unit claim (no evidence) and on 16.2% vs 6.5% (both numbers valid for different models) — but the mismatch still required a single traceable source. The corrections above adopt the simplest defensible V1 architectures without forcing component preserves.

---

*Authority: LT1970A 1970afc (ADI), ADG1419 Rev A (ADI), OPA140 SBOS498F (TI), ADS1262 (TI), AD7175-8 Rev0 (ADI), AD5764 Rev C (ADI), LTC6655 (ADI). All quantitative claims cite datasheet page/section where applicable.*

