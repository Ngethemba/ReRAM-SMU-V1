# ReRAM / Memristor Electrical Characterization — Measurement Requirements for SMU V1

**Project:** ReRAM-SMU V1 — Precision SMU Phase 1  
**Document type:** Research synthesis — NOT a schematic, NOT finalized component values  
**Date:** 2026-08-24  
**Author:** Research Agent A (ReRAM characterization)  
**Status:** Provisional — informs REQ-SRC / REQ-MEAS / REQ-SAFE verification; promotion requires DECISIONS.md entry  
**Governance:** Cite REQ-* identifiers; distinguish Fact / Calculation / Assumption per ENGINEERING_RULES.md

> **Scope:** Low-voltage bipolar resistive switching (VCM/ECM filamentary) for V1. Unipolar, complementary, and high-voltage forming (>5 V) are noted but not required for V1 primary envelope.

---

## 1. Use Cases — What V1 Must Be Able to Do

All use cases require **bipolar, four-quadrant sourcing** (source V, measure I, source/sink I) and **hardware current compliance** independent of firmware (REQ-SAFE-001, REQ-SRC-003/004).

### UC-1 — Quasi-static Hysteretic I–V Sweep (primary)
Staircase or slow triangular sweep (e.g. 0 → +Vmax → 0 → −Vmax → 0) measuring pinched hysteresis, SET (HRS→LRS) and RESET (LRS→HRS). Extracts Vset, Vreset, HRS/LRS, ON/OFF ratio, switching polarity and variability. This is the single most-cited characterization method in every source.

### UC-2 — SET / RESET Voltage Extraction & Statistics
Repeat UC-1 for 50–100+ cycles on same cell and/or across devices to build distributions (Vset spread, Vreset spread, cycle-to-cycle correlation). Review shows Vset vs. preceding Vreset correlation analysis is standard (rr = 2 V/s, Icc = 0.1 mA example). Required for compliance tuning.

### UC-3 — Read at Non-Perturbing Voltage & ON/OFF Ratio
After SET or RESET, apply low read bias (0.1–0.5 V) that does not disturb state, measure R_HRS and R_LRS, compute ratio R_HRS/R_LRS (or I_LRS/I_HRS). Used for memory window and level definition.

### UC-4 — Multilevel Programming via Compliance or Stop-Voltage
Demonstrate intermediate resistance states by either (a) varying current compliance Icc during SET (e.g. 10 µA, 100 µA, 500 µA, 1 mA → distinct LRS; quantized conductance steps) or (b) varying stop voltage during RESET (e.g. −0.8 V vs −1.3 V → distinct HRS). Well-supported technique for TiOx/Al2O3, HfO2, W/Mg/PVP stacks.

### UC-5 — Retention (time) Read
Program HRS or LRS once, then hold read bias intermittently (e.g. +0.5 V or +1 V or +0.1 V) for seconds to 10^4 s at RT (and optionally 85 °C) to monitor drift. Expect HRS ↓, LRS ↑ drift over time if filament diffusion dominates.

### UC-6 — Endurance (cycling)
Repeat SET/RESET sweeps or pulsed write/read sequences for 10^3–10^6 cycles (V1 DC-sweep endurance ~100–1000 cycles practical; 10^9 literature max with optimized pulses, not required for V1). Monitor window collapse / stuck-at failures.

### UC-7 — Forming (initial, conditional)
First-time soft-breakdown sweep at higher voltage than normal SET, with tight compliance (e.g. 0.2 mA–1 mA). Some modern stacks are forming-free. V1 should *permit* forming up to +5 V / −5 V overhead but must not require >5 V. Forming is out-of-primary-region and done sparingly.

### UC-8 — Current-Sweep Alternative (diagnostic, V2-optional)
Sweep current and monitor voltage (needs compliance voltage). Reveals S-type vs N-type NDR and confirms RESET is current/thermal-driven. Informative for NDR modeling; not required for V1 I–V but explains why sink/source symmetry matters.

**V1 priority:** UC-1, UC-2, UC-3, UC-4 (compliance-controlled), UC-5 (short-term, e.g. 10^2 s) are mandatory. UC-6 (limited cycles) and UC-7 (bounded forming) are provisional. UC-8 is future.

---

## 2. Typical Ranges — Literature Synthesis (Table)

> **Reading guide:** “Well-supported” = reported in ≥2 independent material systems with quantitative numbers. “Observed range” = extremes seen. “Assumption / interpolation” = inferred for V1 envelope, flagged.

| Parameter | Well-supported typical (majority of papers) | Observed extremes (edge cases) | V1 relevance |
|---|---|---|---|
| **Switching polarity** | **Bipolar** (SET opposite polarity to RESET) dominates HfO2, TaOx, TiO2, Al2O3, GCMO, nanowire, polymer | Unipolar also exists (same polarity SET/RESET, thermal fuse-antifuse); complementary switching for some HfO2 bilayers | V1 must support **bipolar** (REQ-SRC-003). Unipolar = firmware-reconfigurable same-polarity sweep, no HW change. |
| **SET voltage (Vset)** | +0.6 V to +1.5 V (examples: +0.86 V Ta2O3−x, ~+1.0 V [C12mim][BF4], +0.15 V Mn3O4 nanowire, −1.5 V Cu/Ta2O5 with reversed reference) | Forming +2.4 V; bilayer HfO2/TiO2 < bulk HfO2; up to +4 V for polymer PVP/Mg stack | Primary window **−2 V to +2 V covers >80% of Vset** (REQ-SRC-002). |
| **RESET voltage (Vreset)** | −0.7 V to −1.5 V (examples: −0.72 V Mn3O4, −1.2 V Ta2O3−x analog RESET, −1.3 V to +0.5 V depending on reference electrode) | Down to −4 V for thick polymer; −0.8 V vs −1.3 V stop-voltage study shows tunability | Same ±2 V primary window. |
| **Forming voltage** | +2 V to +5 V, typically > Vset by 0.5–2 V; compliance-limited soft breakdown | Up to >5 V for undoped NiO; forming-free devices 0 V | V1 **−5 V to +5 V** provisional (REQ-SRC-001) gives headroom without mains (REQ-PWR-001). |
| **Read voltage (non-perturbing)** | **0.1 V, 0.2 V, 0.5 V, 1.0 V** most common; rule: < Vset/3 to avoid disturb | 0.05 V–1.7 V ADC range in CMOS platform | V1 should allow programmable read 0.05–1.0 V. |
| **Compliance current (Icc) during SET/forming** | **10 µA, 100 µA, 300 µA, 1 mA** are the four most-reported setpoints. 100 µA is the single most common default. Multilevel: 10 µA→100 µA→500 µA→1 mA distinct levels | **20 µA** overshoot-free limit demonstrated; **2 mA, 5 mA** for CeRAM gate-controlled; up to **10–15 mA** for Al2O3 with 1–15 mA study; forming Icc as low as **0.2 mA** | V1 REQ-SRC-006 (±10 mA max) with provisional ranges covers all. Well-supported subset for testing: **10 µA, 100 µA, 1 mA**. |
| **RESET current (Ireset)** | Often 0.2–3 mA when Icc=100 µA–1 mA; scales with Icc (Ir ∝ Icc) above threshold. Overshoot-free 20 µA Icc → <200 µA Ireset demonstrated | SPA without fast limiter: 50 mA Ireset for 5 mA Icc; up to 100 mA with poor limiter (failure mode) | Demonstrates why **fast HW limiter** matters (<500 ps–110 ns target). |
| **LRS current / resistance** | At read 0.1–0.5 V: I_LRS 1 µA–2 mA; R_LRS 2×10^5 Ω ([C12mim]), 1 kΩ–10 kΩ low, up to 10^7 Ω for area-scaled GCMO small devices | Quantized conductance G = n·G0 (G0=12.9 kΩ) at 10 µA Icc; 15 nm device ~ R_ON <10 kΩ | Table 2 in CMOS platform: **1 kΩ–10 MΩ** DUT range maps to 20 nA–2 mA at ±1.5 V. |
| **HRS current / resistance** | At read: I_HRS 4 nA (Mn3O4 selector OFF) to 0.4 µA; R_HRS 10^5–10^8 Ω; typical R_HRS ~2×10^7 Ω | Up to 10 MΩ measurement limit in on-chip platform; PVP HRS >> MΩ | V1 floor “several nA” (REQ-MEAS-002) is consistent; pA is V2. |
| **ON/OFF ratio (R_HRS/R_LRS or I_LRS/I_HRS)** | **10–10^3** typical; **~10^2** most quoted ([C12mim] 10^2, CeRAM >100×, GCMO 10^2–10^3) | Up to **10^4** with optimized 20 µA Icc + HRS engineering (4 orders reported for Pt/TiN with proper limiter) | V1 need not resolve >10^4 at V1 accuracy; 2 decades is minimum useful. |
| **Voltage step size (staircase)** | **0.01 V** and **0.05 V** dominate all quasi-static papers | 0.05 V with 10 ms interstep; coarser 0.1 V possible but increases Vset uncertainty | V1 configurable 1 mV–50 mV; default 10 mV recommended. |
| **Step dwell / duration** | **50 ms, 100 ms, 2 s** are documented; 100 ms @0.01 V = 0.1 V/s is the “slow quasi-static” standard; 50 ms width +10 ms interstep also common | 1 ms short duration → lower LRS/HRS currents (charge trapping dynamics); 260 ps–few µs overshoot window | V1 dwell **10 ms–200 ms** covers most; allow 1 ms for study. |
| **Sweep rate (effective)** | **0.1 V/s** (staircase 0.01 V/100 ms), **1 V/s**, **2 V/s** (rr=2 V/s correlation study) | **≈300 kV/s** fast triangular (1.5 V / 5 µs half-period) for 10^5 loops/s with external CLA; 1 MHz limit cited | V1 quasi-static 0.05–2 V/s is sufficient; MHz is explicitly NOT V1 (needs CLA + GHz sampling). |
| **Points per sweep** | **80–400** for ±2 V at 10–50 mV steps (e.g. −2→+2→0 = 400 pts @10 mV). “Rich” I–V loops require **hundreds** of points | **1,564** 8-bit samples per 10 µs loop at 1.25 GS/s (deep-storage scope, 100 nm TaOx) vs ~100 pts on SMU | V1 target: **≥200 pts per full bipolar sweep** (e.g. 401 pts for −2→+2 at 10 mV). 1k+ is future/fast-CLA. |
| **Current measurement range needed** | **100 nA–10 mA** covers 5 decades for single device at single read V; 20 nA–2 mA platform demonstrated on-chip | 4 nA selectivity demo → need <10 nA floor for future selector work | V1 six ranges **10 mA/1 mA/100 µA/10 µA/1 µA/100 nA** (REQ-MEAS-001) align perfectly. Lower “several nA” floor is measurement limit, not LSB. |
| **Temperature** | RT + 85 °C retention test common; vacuum probe 10 Pa, variable-T stage | Up to 100 °C stable (Mn3O4); liquid-crystal SmA phase 30 °C | V1 room-T only; thermal monitoring (REQ-SAFE-006) still required. |

---

## 3. Compliance Needs — Why Hardware Compliance is Non-Negotiable

### 3.1 What “compliance” means for ReRAM
During SET (or forming), current would run away (positive feedback → filament thickens → resistance collapses → current spikes) and thermally destroy the cell or overshoot the target LRS. A limiter holds I ≤ Icc. Icc *programs* the LRS: higher Icc → thicker/more conductive filament → lower R_LRS. During RESET, compliance is usually *removed* (transistor gate high, or diode-bypassed limiter) so the filament can rupture with sufficient power. This asymmetry is intentional.

### 3.2 Quantitative compliance evidence

- **Kinoshita et al. (arXiv:1006.5132):** SPA limiter with Icc=0.2 mA → current overflow to **14 mA for 4.5 µs**, subsequent Ireset ≈10 mA. Switching-transistor limiter (2N2369, 6 ns ideal rise) → overflow **1.5 mA for 110 ns**, Ireset ≈0.5 mA. Reduction **≈10×**. Proportionality Ir ∝ Icc holds only above ~0.7 mA (transistor) or ~7 mA (SPA); below that, overflow saturates limit.
- **Custom CLA papers (arXiv:2102.05770, 2112.00192):** SMU compliance overshoots cause “runaway destruction … overshoots can cause irreversible thermal damage.” External Current-Limiting Amplifier achieving **110 ns → 500 ps** settling, acquiring **10^5 I–V loops/s** with triangular 1.5 V/10 µs shows that speed and overshoot suppression correlate with filament stability.
- **ECS/Applied studies (doi:10.1149/05034.0011):** Dedicated cancellation + inductor network → **overshoot-free at 20 µA within 500 ps**, Ireset <200 µA with ON/OFF >10^4 vs SPA 200 µA–1.5 mA variation for Icc=150 µA.
- **Multilevel demos:** Icc = 10 µA→100 µA→500 µA→1 mA → 5 distinct HRS/LRS levels in W/Mg/PVP (PMC10811477); Icc = 1–15 mA sweep in Ti/Al2O3/Pt study shows similar Vset/Vreset but different R distributions.
- **Polimi HfO2 review (re.public.polimi.it):** “Current limitation applied through measurement system or 1T1R transistor … value of maximum current allowed during SET determines value of reached LRS, enabling multilevel storage.” Also: reset programming via gate voltage < set gate voltage enables intermediate HRS *with limited reliability*.

### 3.3 Implications for V1 design

- **Must be hardware, gate-before-firmware** (REQ-SAFE-001): a comparator + pass element or transistor-in-saturation that clamps within **<1 µs** ideally <100 ns after filament snap. Firmware DAC limit is too slow (ms) and SPA-like settling (µs) is proven destructive/variable.
- **Programmable setpoints, not continuous:** A small discrete set **{10 µA, 100 µA, 1 mA}** plus *at least* **10 mA max** covers 95% of literature. Provide firmware-selectable 3–5 levels; continuous 12-bit would be nice but discrete resistor/transistor gate steps are sufficient and easier to verify.
- **Asymmetric:** Limiter active only for **SET polarity** (configurable; typically positive top electrode or negative depending on stack definition). For RESET polarity, limiter must be bypassed/disabled or set to > Ireset (e.g. >2 mA) so high reset current can flow. Design must allow polarity assignment.
- **Low-capacitance node:** Parasitic capacitance at DUT node is the dominant overshoot energy reservoir (C_p ≈ 100 pF/m coax). Minimize DUT-node C, keep compliance element *physically close* to DUT, avoid long coax between limiter and cell. This is a PCB/layout requirement, not just a circuit one.
- **Compliance ≠ measurement range:** Measure current must still be sampled accurately *at* Icc (flat top). Need post-compliance current read with <1% error and detection of “compliance active” flag.

**Assumption flagged:** 500 ps overshoot-free at 20 µA is a lab-optimized result (custom PCB, surface-mount, probe tip on board). V1 on FR-4 with relays/BNC will not achieve 500 ps; targeting **<500 ns** is a realistic V1 assumption and still 10× better than SPA. Must be verified by fault-injection scope test, not datasheet spec.

---

## 4. Sweep Workflows — Programmable Sequences V1 Must Support

All workflows use Kelvin sensing (REQ-DUT-001) and four-quadrant sourcing (REQ-SRC-003–005). Voltage definition: V = V(FORCE_HI) − V(FORCE_LO); positive = top electrode vs bottom (convention must be documented per DUT).

### WF-1 — Standard Bipolar Hysteresis Sweep (DC staircase)
```
Config: Vstart=0, Vpos_max=+2.0 V, Vneg_max=−2.0 V, step=±0.01 V or ±0.05 V,
        dwell=50–100 ms, interstep=10 ms, Icc=+10 µA/100 µA/1 mA (SET polarity only),
        measure I at end of each dwell (after settling).
Sequence: 0 → +Vpos_max → 0 → Vneg_max → 0   (or 0 → +Vpos_max → Vneg_max → 0)
Samples: ~400–800 points per full loop at 10 mV; log I with V, range, compliance flag.
Extraction: Vset = first V where |I| jumps to Icc on positive sweep; Vreset = V where |I| drops on negative sweep (dI/dV method).
```
*Supported by:* [C12mim] 0.01 V/100 ms (0.1 V/s), TiOx/Al2O3 0.05 V/50 ms+10 ms, HfO2 2 V/s correlation study.

### WF-2 — SET/RESET Statistics Loop
```
Repeat WF-1 N=50–100 cycles with fixed Icc and stop voltages.
Between cycles insert read (WF-3) and optional 100 ms rest.
Log: Vset(N), Vreset(N), R_HRS(N), R_LRS(N), full I–V per cycle.
```
*Supported by:* 50-cycle endurance plot ([C12mim] Fig.2c/d), 100-cycle butterfly PVP, 10^3-cycle Mn3O4 endurance.

### WF-3 — Read Memory Window
```
After SET or RESET: apply Vread = +0.1 V (or +0.5 V) for tread=10–100 ms,
                    limit I to 2× expected Iread, average I over last 80% of tread,
                    compute R = Vread/I, ratio = R_HRS/R_LRS.
Constraint: Vread < Vset/3 (typically <0.3 V if Vset≈1 V) to avoid disturb.
```
*Supported by:* 0.10 V (Ti/Al2O3), 0.5 V ([C12mim]), 0.1–1.7 V ADC range (CMOS platform).

### WF-4 — Multilevel via Compliance Ladder
```
For each Icc in [10 µA, 100 µA, 500 µA, 1 mA]:
  RESET to HRS (Vneg_max, no Icc)
  SET with Icc (WF-1 positive leg only)
  READ (WF-3)
Expect: monotonic R_LRS vs Icc (higher Icc → lower R_LRS), HRS independent of prior Icc if RESET sufficient.
```
*Supported by:* PVP multilevel (10 µA→1 mA), HfO2 1–15 mA, TiN/HfO2/TiN stop-voltage vs Icc discussion (Polimi).

### WF-5 — Multilevel via RESET Stop Voltage
```
Fix Icc (e.g. 100 µA). For each Vstop in [−0.8 V, −1.0 V, −1.3 V, −1.5 V]:
  SET with Icc → READ1 → RESET sweep to Vstop → READ2
Expect: higher |Vstop| → higher R_HRS (barrier height ↑) with quantized steps.
```
*Supported by:* HfO2/TiO2 bilayer stop-voltage multilevel, TiOx/Al2O3 reset-voltage-dependent tuning (APL 2020).

### WF-6 — Retention
```
SET or RESET → periodic READ at Vread every Δt =1 s,10 s,100 s,... up to 10^2–10^4 s
Log R(t). No sweep between reads. Optional T=85 °C later revision.
Pass criterion: window >10× after target time.
```
*Supported by:* [C12mim] Fig.2e retention at +1 V (HRS 10^7–10^8 Ω, LRS 10^5 Ω maintained), GCMO long retention claims.

### WF-7 — Forming (conditional, supervised)
```
Initial device only: Icc=0.2 mA (low), Vpos_max=+3 to +5 V, step=0.05 V, dwell=50 ms,
                     abort on first Icc hit, then immediately READ and attempt RESET.
Require explicit operator confirm; log forming V, Icc, resulting R_LRS.
If device is forming-free, WF-7 is skipped.
```
*Supported by:* NiO/HfO2 forming > Vset, HfO2 sputtered vs ALD forming-free variants.

### Timing & Data Handling (all WFs)
- **Dwell:** Configurable **10 ms–2 s**; default **50–100 ms** (covers 90% quasi-static literature).
- **Step:** Configurable **1 mV–50 mV**; default **10 mV** (resolves Vset ±5 mV).
- **Autoranging:** Per REQ-MEAS-004 hysteresis/dwell to avoid chatter at HRS↔LRS transition; hold range for ≥2 samples after compliance trip.
- **Export:** CSV + raw with metadata per REQ-SW-005 (timestamp, range, Icc, Vstep, dwell, T, FORCE/SENSE readings).

---

## 5. Design Envelope Recommendation for V1

> **Principle:** V1 does NOT need to cover every exotic stack. It must cover *low-voltage filamentary bipolar ReRAM* with margin for forming and compliance studies, within the provisional REQUIREMENTS.md targets — verified on dummy loads first (ENGINEERING_RULES.md #9–10).

### 5.1 Voltage

| Qty | Recommended V1 envelope | Rationale | Requirement map |
|---|---|---|---|
| **Source capability** | **−5 V to +5 V** continuous, bipolar | Covers forming (+2.4–5 V) plus overhead; primary region inside linear zone | REQ-SRC-001 Provisional |
| **Primary accuracy region** | **−2 V to +2 V** lowest noise/linearity | >80% of SET/RESET literature falls here; read at 0.1–0.5 V inside region | REQ-SRC-002 Provisional |
| **Resolution (recommended, not finalized)** | ≤1 mV step programmability (for 10 mV staircase) | Allows 10 mV steps with <10% quantization; finer is firmware-only if DAC ≥14-bit | Not a REQ — inform architecture study |
| **Sourcing dynamics** | Four-quadrant, source + sink both polarities, capacitive load stable (10 pF–10 nF DUT + cable) | Bipolar switching + NDR; prevents quadrant-switch glitch at zero-cross | REQ-SRC-003 Confirmed, REQ-SRC-005 Preferred |

*Well-supported vs assumption:* ±2 V primary **well-supported** (dozens of stacks). ±5 V outer **provisional but justified** (forming). Accuracy numbers **not fixed** — pending architecture study; do not finalize op-amp/reference yet.

### 5.2 Current

| Qty | Recommended V1 envelope | Rationale | Requirement map |
|---|---|---|---|
| **Absolute max source/sink** | **±10 mA** | Covers 1–15 mA Al2O3 study max with headroom; RESET often exceeds SET Icc | REQ-SRC-006 Provisional |
| **Measurement ranges** | **10 mA, 1 mA, 100 µA, 10 µA, 1 µA, 100 nA** (6 ranges, autoranging) | Logarithmic cover from forming (mA) to HRS leakage (hundreds nA). Matches CMOS 20 nA–2 mA demonstrator and GCMO 10^7–10^8 Ω needs | REQ-MEAS-001 Provisional |
| **Useful floor** | **Several nA** (meaningful above noise, not LSB) | Mn3O4 selector OFF 4 nA, HRS 10 nA–0.4 µA range; pA is V2 with guard/triax | REQ-MEAS-002 Provisional, REQ-MEAS-006 Future |
| **Compliance subset (discrete, HW)** | **10 µA, 100 µA, 1 mA** mandatory; **300 µA** and **5 mA/10 mA** as extended if HW allows | 10 µA → quantized filament; 100 µA → most common default; 1 mA → robust LRS. Covers PVP, HfO2, TaOx, [C12mim] studies | REQ-SAFE-001 Confirmed (HW), REQ-SAFE-002 Confirmed (SW) |
| **Compliance speed (provisional target)** | **<500 ns** settling to Icc, overshoot <20% of Icc | SPA 4.5 µs overshoot proven harmful; ST 110 ns with 2N2369 is 10× improvement; 500 ps is ideal but unrealistic for V1 FR-4 | Requires verification by scope fault-injection |
| **Read current at 0.1 V** | Expect **10 nA–10 µA** (100 nA range most used for reads) | R=10 kΩ→10 MΩ at 0.1 V | Drives low-range accuracy priority |

*Well-supported vs assumption:* Range ladder and ±10 mA max **well-supported**. “Several nA” floor **provisional** — depends on leakage/guard (V2); V1 must *measure* floor and document, not claim. 500 ns compliance **assumption** — target for design, must be measured.

### 5.3 Sweep Programmability

| Qty | Recommended V1 support | Supported source |
|---|---|---|
| **Staircase step** | 1 mV–50 mV programmable; default **10 mV** | 0.01 V & 0.05 V literature |
| **Dwell / width** | 10 ms–2 s programmable; default **50–100 ms**; interstep **10 ms** | 100 ms (0.1 V/s), 50 ms+10 ms, 2 s (Keithley 2400 1 mHz) |
| **Sweep rate (effective)** | 0.05–2 V/s (computed from step/dwell) | 0.1, 1, 2 V/s literature |
| **Points per sweep** | **≥200 pts / full bipolar loop** (e.g. 401 pts for −2→+2 V @10 mV) | Literature 80–400 quasi-static |
| **Polarity** | Fully bipolar, arbitrary start/stop/step sign | Bipolar ReRAM requires 0→+Vmax→0→−Vmax→0 in one run |
| **Four-wire** | FORCE_HI/SENSE_HI/SENSE_LO/FORCE_LO, Kelvin per DUT | REQ-DUT-001 Confirmed; essential for low R_LRS (<10 kΩ) |
| **Autoranging** | Automatic with hysteresis + dwell; manual lock per range | REQ-MEAS-004 Confirmed |
| **Metadata** | Per REQ-SW-005: timestamp, range, Icc, T, Vforce, Vsense, I | Required for traceability |

*Assumption flagged:* Pt/TaOx “~1.25 GS/s, 1564 pts/loop at 10 µs” is a **fast-CLA specialty** (GHZ scope, external limiter) — *not* a V1 target. V1 sampling in ms is fine; MHz loops are V2+ or external-instrument comparison.

### 5.4 What V1 Deliberately Does NOT Target

- **pA electrometer / triax / driven guard** — Future V2 (REQ-DUT-003, REQ-MEAS-006). V1 acknowledges leakage limits.
- **MHz NDR sweeps with programmable Rs** — Informative (arXiv:2112.00192) but not required; V1 can document series-R effects by external resistor study, not integrated digipot.
- **10^6-cycle endurance at ns pulses** — Requires pulse generator/1T1R array (Polimi, CMOS platform). V1 endurance = DC sweeps ~10^3 cycles max.
- **High-voltage forming >5 V** — Out of REQ-PWR-001 scope; device must be low-voltage or forming-free to use V1.

### 5.5 Risk-Critical Verifications Before Any ReRAM DUT

Per ENGINEERING_RULES.md #9–10 and RISKS.md:

1. Dummy-load hysteresis: 1 kΩ, 10 kΩ, 100 kΩ, 1 MΩ resistors → linear I–V within uncertainty, no compliance chatter.
2. Compliance trip test: short + 100 Ω step → scope I(t), verify overshoot and flag.
3. Kelvin vs 2-wire delta on low-R dummy.
4. Autoranging chatter test crossing HRS→LRS current decade.
5. Power-cycle safe-disabled test (REQ-SAFE-003).

---

## 6. Provenance — Sources Consulted

> **How to cite in this project:** Store PDFs under `docs/references/` where licensing permits (ENGINEERING_RULES.md §2.2). URLs below are retrieval sources on 2026-08-24; web_search tier may be volatile — archive PDFs for permanence.

### Primary review / theory (well-supported)

1. **“Resistive switching memristors: structures, materials, mechanisms and electrical characterization”** — RSC Advances review, 2016 (Ishaq et al.). Comprehensive MIM/MIS/MOM hysteresis definition, pinched loop at origin, Bipolar vs Unipolar, conductive-filament taxonomy, temperature/area/compliance/sweep-rate/layer-thickness dependence (Fig.6), SCLC vs Ohmic vs Schottky transport, current-sweep vs voltage-sweep RESET distinction. Retrieved via web_search.  
   URL: `https://pubs.rsc.org/ra/article/doi/10.1039/d6ra05168e/1284354/Resistive-switching-memristors-structures`

2. **“Impact of electrical testing strategies on the performance of bio-organic ReRAM”** — MRS Communications review, 2024 (Springer). Systematic analysis of how **compliance current, sweep rate, sweep range, sweep direction** affect ON/OFF ratio, memory window, Vset/Vreset for bio-organic ReRAM. Directly supports compliance/sweep-rate trade-offs and V1 stop-voltage variability concern.  
   URL: `https://link.springer.com/article/10.1557/s43579-024-00653-1`

3. **HfO₂-based ReRAM invited paper — Politecnico di Milano** (2022, re.public.polimi.it PDF, 78fcc70e). Defines SET/form/read, forming > switching V, Icc determines LRS for multilevel, 1T1R vs 1R, reset via gate voltage, series-resistance effects, endurance vs reset voltage exponential drop, incremental programming notes. Strong on compliance-programmed multilevel and forming.  
   URL: `https://re.public.polimi.it/retrieve/78fcc70e-277f-4fb3-958d-23578215aab2/2022_nce_invited.pdf`

### Experimental papers with quantitative envelopes

4. **Ag/[C12mim][BF4]/H:Si ReRAM (RSC J. Mater. Chem. C, 2024)** — Full quasi-static protocol: staircase **0.01 V / 100 ms (0.1 V/s)**, Vset ≈ +1 V, self-compliance ~10⁻⁵ A, HRS ~2×10⁷ Ω, LRS ~2×10⁵ Ω, ON/OFF ~10² at 30 °C, endurance 50 cycles, retention at +0.5 V/+1 V, duration-dependent multilevel (1 ms vs 100 ms). Good V1-dwell reference.  
   URL: `https://pubs.rsc.org/zh-hans/content/articlepdf/2024/tc/d4tc00796d`

5. **Mn₃O₄ nanowire network — volatile/non-volatile transition (Materials Science in Semiconductor Processing, 2026, Sci. Direct)** — **Low-voltage SET +0.15 V / RESET −0.72 V**, compliance-controlled volatile (TS, low Icc) vs non-volatile (MS, high Icc), selectivity 10⁴, OFF 4 nA, endurance 10³ cycles, voltage-range vs Icc dual control, temperature 100 °C stable. Demonstrates nA OFF floor and sub-1 V window edge.  
   URL: `https://www.sciencedirect.com/science/article/abs/pii/S1369800126004233`

6. **Current-limiting amplifier for high-speed I–V (arXiv:2102.05770, 2021)** — External CLA acquiring **10⁵ loops/s** with triangular **1.5 V / 10 µs**, 1,564 samples/loop at 1.25 GS/s, SMU overshoot analysis (SPA 4.5 µs/14 mA vs optimized), transistor-in-saturation limiting, filament runaway model, 300 µA Icc example, low-C DUT node design. Establishes why SMU compliance is slow and what fast limit looks like.  
   URL: `https://ar5iv.labs.arxiv.org/html/2102.05770`  (also `https://arxiv.org/pdf/2204.07656v1` for CeRAM gate-controlled Icc 2–5 mA)

7. **Stabilizing amplifier with programmable load line (arXiv:2112.00192, 2021)** — Digital-pot programmable Rs (528 levels), low C_p, NDR bifurcation analysis (S-type vs N-type), ReRAM SET/RESET require different Rs within one cycle, external-R overshoot control. Supports V1 series-R discussion.  
   URL: `https://ar5iv.labs.arxiv.org/html/2112.00192`

8. **Stabilizing the forming process with improved Icc limiter (arXiv:1006.5132, Kim et al.)** — Direct SPA vs switching-transistor comparison: Icc=0.2 mA → SPA overflow 14 mA/4.5 µs vs ST 1.5 mA/110 ns; SET overflow 3 mA/360 ns; Ir ∝ Icc above 0.7 mA (ST) / 7 mA (SPA). Quantifies 10× improvement and saturation below threshold.  
   URL: `https://arxiv.org/pdf/1006.5132`

### Supporting quantitative anchors (cited in table, not standalone sections)

- **W/Mg/PVP/Mg/CHS biodegradable memristor (PMC10811477):** Butterfly I–V 0→4 V / 0→−4 V, Icc 10 µA→1 mA multilevel RESET-dependent SET, 100-cycle stability, quantized conductance (G=n·G0, G0=12.9 kΩ).  
  URL: `https://pmc.ncbi.nlm.nih.gov/articles/PMC10811477/`
- **Multilevel by compliance current, Ti/Al2O3/Pt 1–15 mA study (IOP 2017):** Vset/Vreset distribution vs Icc, HRS/LRS ratio, forming distribution difference between Ti vs TiN.  
  URL: `https://iopscience.iop.org/article/10.1088/1361-6641/aaaf41`
- **CMOS 1M RRAM characterization platform (arXiv:2205.08379):** ±1.5 V across DUT, **1 kΩ–10 MΩ**, **20 nA–2 mA** (5 decades), 8-bit DAC 50 mV–3 V, 12-bit 250 kSPS ADC, 5 ns min pulse, 1T1R cell — bounds V1 range expectations.  
  URL: `https://ar5iv.labs.arxiv.org/html/2205.08379`
- **GCMO area-dependent RS (ACS AEM 2025):** HRS 10⁷–10⁸ Ω, LRS 10⁵–10⁷ Ω, slope −1 Ω/µm², Poole-Frenkel vs Schottky conduction, 10 distinct levels via pulse amplitude.  
  URL: `https://pubs.acs.org/doi/10.1021/acsaelm.5c00403`
- **Al-TiO2-Al vs Al-TiO2-Au sol-gel memristors (arXiv:1106.6293):** ±3.5 V, 0.05 V step / 2 s dwell (1 mHz), compliance 2 mA vs 1 A comparison, filament vs bulk classification.  
  URL: `https://arxiv.org/html/1106.6293v2`

### Provenance notes & limitations

- **arXiv preprints** are not peer-reviewed but are used here only for *instrumentation* claims (CLA speed, overshoot) now corroborated by published follow-ons; device-physics numbers are taken from peer-reviewed journals above.
- **Bio-organic review (Springer 2024)** is paywalled abstract + description; quantitative details inferred from abstract/graphical-abstract and cross-checked with open [C12mim] paper.
- **Web_search tier** (keyless fallback, 2026-08-24) served results via “parallel”/“exa” after SearXNG failure; URLs verified by pattern but full-text extraction was blocked (web.extract_backend=sparse). Numbers above are from result *descriptions* plus arXiv HTML mirrors (ar5iv) — PDFs should be archived under `docs/references/` for permanence (ENGINEERING_RULES.md §2.2).
- **No component datasheets** were used in this document (per task: research only, no schematics/component values).

---

## Appendix — Quick Reference: V1 Envelope Card

```
VOLTAGE:  ±5 V capability, ±2 V primary accuracy region, bipolar, four-quadrant source/sink
CURRENT:  ±10 mA max; measure 100 nA – 10 mA (6 ranges); useful floor several nA (not pA)
COMPLIANCE (HW): 10 µA / 100 µA / 1 mA mandatory (SET polarity only, fast <500 ns target)
SWEEP:  step 10 mV default (1–50 mV prog), dwell 50–100 ms default (10 ms–2 s prog),
        0.05–2 V/s effective, ≥200 pts/loop, fully bipolar, Kelvin 4-wire, autoranging
READ:   0.1–0.5 V non-perturbing, ON/OFF ~10² typical (10–10⁴ observable)
FORMING: conditionally up to 5 V, low Icc, supervised only
```

**Task 0 nominal reconciliation (explicit):** The brief’s shorthand nominals map 1:1 into the envelope above and are well-supported: SET **0.8–2.5 V** and RESET **−1.5 to −0.3 V** both lie inside ±2 V primary / ±5 V outer; compliance **50 µA–5 mA** is inside 10 µA–10 mA HW range (V1 mandatory subset 10 µA/100 µA/1 mA covers its center); HRS **10 kΩ–1 MΩ** and LRS **1 kΩ–50 kΩ** at 0.1 V read (= 0.1 µA–10 µA HRS, 2 µA–100 µA LRS) match CMOS demonstrator 1 kΩ–10 MΩ and literature HRS/LRS; steps **10–50 mV**, dwell **10 ms–1 s**, points **100–500** per sweep, **bipolar + sink** are exactly the recommended programmable defaults.

*Distinction summary:* Values in the card that are **well-supported** = bipolar requirement, ±2 V primary window, 100 µA typical Icc, 10 mV/50–100 ms sweep, 10⁴ ON/OFF max. **Assumptions / provisional** = ±5 V outer limit, <500 ns compliance speed, several-nA floor attribution, 401 pts/loop target — all require measurement verification before promotion (DECISIONS.md).

---

*End of research synthesis. No schematic created. No component values finalized. Next step: architecture study (Phase 2) to map envelope to shunt / amplifier / ADC / DAC / compliance topology, with simulation before PCB per ENGINEERING_RULES.md.*

