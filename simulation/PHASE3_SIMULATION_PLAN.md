# Phase 3 Simulation Plan — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 → Phase 3 gate
**Date:** 2026-08-24 (corrected per PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md)
**Status:** PHASE2-CORRECTED — conceptual, no schematic/BOM
**Tooling:** Hybrid ngspice primary (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`) + LTspice secondary for vendor models (LT1970A, ADA4522, OPA140); Python `simulation/python/` for Monte Carlo and post-processing. Primary datasheets override all summaries.
**Gate:** No simulation executed in corrective session — plan only (IR-16).

## Pass/Fail Metrics from REQUIREMENTS

- **Source (REQ-SRC-001/002, REQ-MEAS-007 provisional):** ±5 V outer, ±2 V primary window; source accuracy ±(0.02% rdg + offset), U<900 µV @2 V, <700 µV @1 V, ±200 µV @0 V (k=2, 25±3°C); load regulation ±(0.01% FS).
- **Compliance (REQ-SAFE-001, DEC-024, CAUTION 1/3):** Hardware limit independent of firmware; regulation settled <50 µs to Icc, trip <5 µs, overshoot <1% resistive / <5% into 1 nF, flag latency <5 µs (trip) / <50 µs (regulation), SOA |V·I| ≤50–60 mW; minimum programmable Icc per IR-01: Vsense_min 4 mV typ → I_min ≈4% FS at 100 mV FS, ≈16% at 25 mV FS, linear only Vc≥60 mV (Vsense≥6 mV); 0.1% of I_range only via range coercion or Candidate C.
- **Kelvin (REQ-DUT-001):** Remote sense >10 GΩ (>10 GΩ achieved via high-Z buffer before any divider, IR-02); force–sense drop up to 5 V, lead tolerance 1 MΩ; canonical `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11); no DC load during measurement invariant (IR-03); DUT-node C accounted (IR-04).
- **Measurement (REQ-MEAS-001/002/004/008):** 6 ranges 10 mA→100 nA with range-dependent burden D per SHUNT_RANGE_TRADEOFF §2.4 (IR-05): 10 mA 25 mV (2.5 Ω), 1 mA 25 mV (25 Ω), 100 µA 50 mV (500 Ω), 10 µA 50 mV (5 kΩ), 1 µA 100 mV (100 kΩ), 100 nA 100 mV (1 MΩ); overload 150% FS recovery <10 ms; settling to 0.1% within dwell (50 ms); Johnson 0.41 pA @100 nA/10 Hz (ENBW 1.253); MUC 1 nA; leakage model per IR-13 leakage budget.
- **Stability (REQ-GEN-001):** Phase margin >45° where model available; overshoot <10% after R_iso+compensation; capacitive DUT 10 pF–10 nF + cable 100 pF/m; sense lead C 10 pF–100 pF, L 10 nH–100 nH.
- **Stored energy (CAUTION 1, IR-14):** C_UPSTREAM ≤10 nF before R_iso (compensation, isolated); C_DOWNSTREAM ≤80–150 pF after R_iso at 5 V for 1 nJ gentle budget (recipe-dependent; 500 pF @2 V, 160 pF @5 V for 2 nJ standard); `E_DUT = ∫ V_DUT·I_DUT dt` reported, not just % overshoot.
- **Bipolar / 4-quadrant (REQ-SRC-005):** +V±I and −V±I sink capability; bipolar front-end A/B/C taxonomy (IR-12); TLV3501 Vos ±6.5 mV max, hysteresis 6 mV as emergency supervisor loose threshold (IR-08), not precision.
- **Safe state (REQ-SAFE-003/004, REQ-PWR-003):** POR/brownout/watchdog → output disabled/high-Z, I_leak <1 µA disabled, Vc floor <4 mV behavior; AD5764 requires ±11.4–±16.5 V (IR-07), LSB 305.2 µV on 20 V span, no ±5 V mode (IR-06).

## Simulations A–O (IR-16) — Original Tests 1–7 Mapped

Original 1–7: 1 Source transfer → G/C/N/O, 2 Four-quadrant → C/G/O, 3 Compliance → A/B/H/I/J, 4 Stability → F/J/K/C, 5 Measurement front-end → E/F/G/M, 6 Monte Carlo → H/N, 7 Temperature → H/M (drift). All original coverage retained, expanded per IR-01..IR-15.

### A — Compliance minimum-range capability (IR-01)
**Goal:** Verify LT1970A programmable compliance floor vs requirement.
- Sweep every range (10 mA/2.5 Ω … 100 nA/1 MΩ, both fixed-100 mV baseline and philosophy D 25/50/100 mV): compute desired Icomp vs LT1970A achievable I_min = 4 mV/Rsense (floor) and I_min,linear = 6 mV/Rsense (Vc=60 mV → Vsense=6 mV, linear threshold). Table: R, I_FS, Vc for I_FS (=10·R·I_FS), I_min floor, I_min linear, I_min/I_FS (4% at 100 mV, 8% at 50 mV, 16% at 25 mV), target 0.1%·I_FS, verdict. Confirm Vc<60 mV nonlinear, Vsense_min 4 mV typ. No unsafe Vc (floating/out-of-range) allowed.
- Variants: shared vs separate compliance-sense R (Solution B), amplified shunt into external loop (Solution C), Candidate C outer loop (Solution D). Reference: LT1970A 1970afc linear-except-VC<60 mV, VSENSE_MIN 4 mV.
- **Pass:** Table matches IR-01 recomputation; floor correctly classified as 4%/16% of FS; solutions A–D documented per DEC-024.

### B — Range coercion matrix (IR-01, DEC-024)
**Goal:** Validate compliance-aware automatic range coercion (Solution A adopted for V1 REV-A).
- Matrix: requested Icomp (decade and mid-decade, e.g., 0.1%·FS to 100%·FS) × measurement range (6 ranges) → firmware selects compliance_range whose Vsense_FS yields achievable Vc≥60 mV (ideally ≥0.5 V). Examples: requested 100 µA on 100 µA range (500 Ω D) → Vc=0.50 V achievable; requested 1 µA on 10 mA range → coercion to 10 µA range or error if autorange disabled. Verify no configuration leaves Vc<60 mV in linear-claimed region or VSENSE<4 mV. Log `Icomp_requested`, `I_range`, `compliance_range`, `Vc`, `Rsense_compliance`.
- Include autorange-disabled error path and range-change holdoff (measure range steered before voltage step to absorb C·dV/dt, IR-01 §4d).
- **Pass:** All matrix cells either achieve linear Vc with flat CC or correctly coerce/error; no silent clamping to wrong range (cf. Keithley range-compliance bit); firmware invariant `Icomp ≤ I_range` unless autorange raises range enforced.

### C — Differential Kelvin servo (IR-02, IR-11)
**Goal:** Verify SENSE_HI/SENSE_LO differential regulation encloses DUT only.
- Topology: DUT → high-Z buffers (≥10 GΩ, Ib ≤10 pA, OPA140-class primary, ADA4625/OPA828-class alternate; IR-02) → diff attenuator (after buffer, never passive divider directly across DUT) → error amp → LT1970A +IN → FORCE via Rsense+R_iso. Verify canonical `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11); LT1970A alone not 4-terminal servo (SENSE+/− is compliance sense across Rsense, distinct from SMU SENSE_HI/LO). Tests: lead R 0 Ω, 10 Ω, 1 kΩ, 10 kΩ, 100 kΩ, 1 MΩ; shunt burden 25–100 mV (philosophy D); ± current source/sink (±10 mA) in Q1–Q4; common-mode sweep −5…+5 V; V_DUT = V_SENSE within source accuracy (±0.02%+offset). Kelvin feedback pickoff after R_iso, C_comp upstream of R_iso.
- **Pass:** V_DUT error < source accuracy envelope across lead R and CM; feedback after R_iso confirmed; no divider loading DUT.

### D — Open-sense faults (IR-03)
**Goal:** Verify open-sense detection with invariant: no DC load during valid measurement.
- Faults: SENSE_HI open, SENSE_LO open, both open, intermittent chatter (1 ms break/make), high-R (1 MΩ to FORCE). Detection: switched continuity test before OUTPUT ON + analog-switch disconnect during measurement (e.g., ADG1419-class 10 pA leakage); weak pull network (10 MΩ) only behind switch, or ≥10 GΩ if permanent; no low-value DC pull remains across SENSE during measurement. Verify fallback FORCE-regulation + fault flag (`FAULT_SENSE_OPEN`), output clamped/disabled, no 10 MΩ permanent pull across DUT (would be 100 nA at 1 V on 100 nA range). Test detection before OUTPUT ON, and verify residual leakage <1 pA at 25/40 °C when disconnected.
- **Pass:** All opens flagged <5 µs, fallback safe, invariant holds (no DC load during measurement); 10 MΩ only as switched test resistor behind disconnect.

### E — DUT loading sweep (IR-02)
**Goal:** Quantify sense-input loading error vs HRS DUT.
- R_DUT = 1 MΩ, 10 MΩ, 100 MΩ, 1 GΩ at 0.1 V, 0.5 V, 1 V, 2 V bias (HRS read window). Measure error with (a) bare 20 MΩ divider directly across DUT (rejected baseline, expect 5–98% error), (b) high-Z buffer before divider (OPA140 10 pA max, typ <1 pA; ADA4625 <1 pA), (c) electrometer option (ADA4530 <1 fA) for reference. Compute `R_eff = R_DUT || R_sense`, `I_sense = V_DUT/R_sense`, extra current vs I_DUT. Include buffer input C (2–5 pF) contribution to DUT-node budget (IR-04).
- **Pass:** Buffered error <0.2% typical on 1 GΩ (10 pA max → 2% worst, electrometer 0.0002%); bare divider rejected; buffer class documented per DEC.

### F — SENSE capacitance (IR-04)
**Goal:** Distinguish DUT-side vs post-buffer capacitance; enforce DUT-node budget.
- Sweep front-panel DUT-connected C: 5 pF, 10 pF, 50 pF, 100 pF, 500 pF, 1 nF — distinguish (i) DUT-side: connector 5–10 pF + trace 1–3 pF + relay Coff 1–3 pF + buffer Cin 2–5 pF + ESD 0.5–2 pF + cable 25–50 pF (0.5 m low-C, length-limited) + DUT 0.5–5 pF vs (ii) post-buffer: 1 nF differential filter after buffer (0 pF DUT-side). Simulate placement before vs after buffer; show 1 nF DUT-side at 5 V → 12.5 nJ (12.5× gentle budget) vs after buffer → 0 pF dump. Report `E = ½ C V²` per C (@0.5/1/2/5 V).
- **Pass:** 1 nF filter confirmed post-buffer only; DUT-node C budget tallied; C_DOWNSTREAM contribution to E_DUT tracked to IR-14 limits.

### G — Bipolar front-end (IR-12)
**Goal:** Verify low-side shunt bipolar measurement path per range and ADC candidate.
- Per range (10 mA…100 nA) test +FS, −FS, zero, small bipolar ±0.01·FS, ±0.10·FS around zero via I_shunt with range-dependent burden D. Per ADC candidate: (A) True bipolar amp output (dual supplies ±5 V, diff centered at 0 V, ADC differential bipolar), (B) Level-shift around ADC midscale (single-supply amp + VCM 2.5 V/1.65 V, shunt ±V maps to midscale ±gain), (C) Differential ADC directly (INA + differential ADC, GND CM). Evaluate for ADS1262 (PGA 1–32, diff ±2.5 V at PGA=1, CM near mid-supply, buffer/mux) vs AD7175-class (±10 V-like, 250 kSPS, INL ±1 ppm) vs alternatives: input range, bipolar supply requirement, common-mode limits, PGA restrictions, input buffer behavior, zero-crossing error, negative shunt measurement (FORCE_LO as ADC ref).
- **Pass:** Each range × each ADC candidate reports feasible topology A/B/C, CM compliance, zero-crossing within error budget; topology selected per range logged with PGA/NPLC/leakage.

### H — Trip tolerance Monte Carlo (IR-08)
**Goal:** Quantify emergency trip threshold distribution (supervisor tolerance, not precision).
- Monte Carlo ≥500 runs: comparator Vos max ±6.5 mV (TLV3501, typ ±1 mV, hyst 6 mV), shunt tolerance 0.1% (→0.01% sweep), DAC threshold INL (±1 LSB AD5764 on 20 V = ±305 µV, ±2 LSB AD5686R on 10 V = ±305 µV), amp offset (ADA4522 5 µV / OPA140 120 µV, drift 22 nV/°C / 0.35 µV/°C). Compute trip threshold error at FS burden: 25 mV → 26% (Vos max) +12% hyst + shunt/DAC/amp terms; 50 mV → 13% +12%; 100 mV → 6.5% +6%. Report mean ±σ, min/max; emergency trip tolerance spec 10–25% at 120–150% Icc_reg, distinct from precision CC regulation (1%).
- **Pass:** Distribution reported separately from regulation accuracy; TLV3501 correctly scoped as catastrophic supervisor with loose 120–150% threshold (IR-08).

### I — Energy / overshoot / charge (IR-14)
**Goal:** Report delivered energy, not only % overshoot.
- For SET-like transition (R 1 MΩ→1 kΩ in 1 µs, filament snap; load step 5 V into 1 kΩ→300 Ω per original test 3): capture I_peak, V compliance flatness, flag latency. Compute `E_DUT = ∫ V_DUT(t)·I_DUT(t) dt`, Q = ∫ I dt = C·V, Ipeak, recovery time. Compare LT1970A limiter vs external loop vs crowbar vs full D (dual regulation+trip). Include slew-limited ramps (0.1–1 V/ms) and R_iso 33–47 Ω decoupling upstream C.
- **Pass:** Overshoot <1% R / <5% into 1 nF with soft-start, E_DUT within per-recipe budget (1 nJ gentle @5 V→80 pF, 2 nJ standard→160 pF @5 V / 1 nF @2 V); Q/Ipeak tabulated; architecture D meets triad.

### J — Upstream vs downstream C location (IR-14)
**Goal:** Verify only C_DOWNSTREAM counts toward filament dump.
- Two matched simulations: C_comp 4.7–10 nF before R_iso (C_UPSTREAM, isolated by R_iso and servo) vs capacitor of same value after R_iso (C_DOWNSTREAM, post-R_iso connector/trace/relay/cable/DUT/ESD before isolation). Drive SET step, measure dump energy and Ipeak. Vary R_iso 10–100 Ω, confirm `E = ½ C_DOWNSTREAM·V²` alone, upstream C decouples (τ=R_iso·C not dumped). Corroborate with test I J.
- **Pass:** Upstream 10 nF not penalized; downstream C budget ≤80–150 pF @5 V / ≤500 pF @2 V per recipe; terminology C_UPSTREAM/C_DOWNSTREAM used consistently (no "low output C ≤10 nF" conflation).

### K — Range switching faults (IR-04, MECHANIC §4)
**Goal:** Verify break-before-make and fault tolerance.
- Sequences: disable output/clamp 0 V → open old relay → 5 ms coil settle → close new relay → 10 ms DA blanking → resume; accidental make-before-break (two shunts simultaneously), stuck relay (open/closed), open shunt, shorted shunt, charge-injection tail (pC → mV on shunt). Test per range with relay Coff 1–3 pF, PhotoMOS R_on 0.5–10 Ω (if provisioned), CMOS mux leakage. Verify Kelvin sense for each R_shunt (R_on 0.1 Ω reed on 2.5 Ω → 4% if not Kelvin). Firmware logs range_state per sample; compliance flag inhibits autorange during limit.
- **Pass:** Break-before-make mandatory, no shunt-shorted state undetected, DA tail to 1% within blanking, Kelvin avoids R_on error, fault flagged and logged.

### L — POR / brownout (REQ-SAFE-003/004)
**Goal:** Verify output remains disabled during undefined states.
- Stimuli: supply ramp 0→±12 V at ≤6 V/µs (LT1970A limit), Vref ramp 0→2.5 V in 10 ms, DAC mid-ramp undefined codes (0x0000/0x8000), MCU held in reset / watchdog timeout, brown-out (<90% of 3.3 V rail). Verify supervisor POR holds ENABLE low 200 ms, heartbeat required; compliance refs pulled to ~50 mV via 100 kΩ to GND/COMMON (min-I safe default) so spurious ENABLE cannot energize at high current; hardware defaults to disabled/high-Z; measure leakage <1 µA disabled and Vsense floor <4 mV/Rsense quiescent (≈400 µA on 10 Ω). Re-test original test 1/2 power sequencing.
- **Pass:** No enable at POR/brownout/watchdog; leakage and floor within spec; ENABLE low until explicit arm.

### M — Leakage model (IR-13, LOW_CURRENT §3)
**Goal:** Preserve MUC 1 nA and Johnson 0.41 pA @100 nA/10 Hz against leakage.
- Behavioral sources summed for 100 nA range: amp Ib (JFET 10 pA max / typ <1 pA vs chopper 50 pA typ → 160 pA noise on 1 MΩ rejected for DUT sense), PCB surface leakage (10 GΩ→10 pA @100 mV, 1 GΩ→100 pA → guard keepout/cleaning/conformal), relay off 1 pA reed vs 10 pA–1 nA PhotoMOS/CMOS, switch leakage (ADG1419 10 pA typ), connector leakage (1 GΩ). Test quantitative: open-input leakage 100 s at 25/40 °C (leakage doubles ~10 °C), shorted vs open DUT; DUT-node budget from IR-04. Johnson 0.41 pA (10 Hz) and ENBW scaling (×3.16 at 100 Hz, ×10 at 1 kHz, ÷√10 at NPLC=10) vs leakage systematic.
- **Pass:** Uncorrected leakage <5 pA to keep residual <MUC after cal; leakage-corrected accuracy <60 pA systematic at 50 nA; Johnson floor preserved; guard provision (no-mask copper, stitched inner plane every 5 mm, no driven guard stuffed in V1 REV-A) verified.

### N — DAC comparison with actual ranges (IR-06/07)
**Goal:** Compare DACs on real spans, supplies, and error contributions.
- Devices: AD5686R architecture 0–5 V → ×2 → ±5 V (10 V span, LSB 152.588 µV, requires gain-stage error/TC), AD5764 actual ±10 V (span 20.0 V, LSB 305.176 µV; ±10.5263 V option 21.0526 V span 321.2 µV; no ±5 V mode, INL ±1 LSB = ±305 µV), AD5791-class only if LSB headroom at 0.1 V read demands it. Include supplies: AD5764 needs ±11.4–±16.5 V (raw ±12 V bench adequate, ±10 V LDO rail fails — IR-07 Options A/B/C), AD5686R single 5 V. Evaluate vs ≤1 mV programming target at 1 V, source accuracy U<700 µV, calibration burden, BOM, power rails, reference complexity (R-2R DAC code-dependent reference current, buffered force/sense per TI SBAA332). Note AD5764 half-codes used for ±5 V operation → resolution halved, INL in volts equal (±305 µV both).
- **Pass:** LSB and span corrected (no 153 µV claim for AD5764); supply compatibility table present; selection criterion: gain-stage removal vs supply cost, not INL alone; Q-01 reopened correctly.

### O — Three source-stage candidates (IR-15)
**Goal:** Compare source architectures under common load and compliance conditions.
- **Candidate A — LT1970A direct voltage loop** (baseline): LT1970A +IN driven via gain from DAC, feedback after R_iso (DUT-sense), Rsense high-side Kelvin for ISRC/ISNK limit, 4 µs takeover, flags, ENABLE. Test offset 200 µV, Ib 160 nA, Ib·Rf, en 15 nV/√Hz, headroom on ±12 V (≥4.7 V margin for ±5 V+burden+dropout).
- **Candidate B — Precision op-amp + discrete/composite buffer** (e.g., ADA4522-2/OPA140 + BJT/MOS follower inside feedback): precision sets Vos/drift/noise, buffer sets current; no integrated limit (external comparators, >10 µs, coarse).
- **Candidate C — Precision outer loop + LT1970A booster/current-limit stage** (IR-15, SOURCE_STAGE §2.6): ADA4522/OPA140 outer amp drives LT1970A +IN or booster input, LT1970A as unity-gain power stage retaining 4 µs limit/ENABLE/flags while outer amp provides 5 µV Vos. Nested-loop stability (Miller/lead-lag Cf across Rf, R_iso with feedback after R_iso) sweeps CL 10 pF–10 nF + cable, compliance crossover (outer voltage + inner current), Kelvin remote-sense latch-up, phase margin >45°. Document per-range burden D 25/50/100 mV impact on headroom/thermal (10 mA·25 mV=250 µW on 2.5 Ω vs 1 mW at 100 mV).
- Tests shared: ±5 V and ±2 V sweeps (1 mV–10 mV steps, R 1 kΩ–1 MΩ), quadrant-transition 0→+2→0→−2→0 into 100 Ω±1 nF with sink/source Vos, compliance entry via 0.5 Ω step/SET snap, cap-load pole with R_iso 33–47 Ω. Candidate D composite (A1+A2) cost/complexity noted but only C is mandated Phase 3 candidate per IR-15 (A/B/C taxonomy, not generic composite).
- **Pass:** Three candidates simulated under identical conditions; stability, offset/burden/thermal, compliance flag, and BOM/risk reported; no candidate promoted without simulation; V1 primary remains LT1970A unless Candidate C proves precision need.

## Outputs

`simulation/spice/*.cir` + `simulation/results/<date>_<sim>_vX/` with .raw, .log, plots, PASS/FAIL table per test A–O, Monte Carlo histograms, energy/charge integrals, and range-coercion matrix. Fail → architecture revisit per DEC-024, not BOM. Raw data and scripts versioned; Python post-processing in `simulation/python/`.

## Traceability

| Requirement / Finding | Test(s) | Provenance |
|---|---|---|
| REQ-SAFE-001 + IR-01 (compliance floor/coercion) | A, B, H | LT1970A 1970afc 4 mV/60 mV, DEC-024 |
| REQ-DUT-001 + IR-02 (high-Z buffer) | C, E | OPA140 10 pA, ADA4625 <1 pA |
| REQ-DUT-001 + IR-03 (open-sense) | D | ADG1419 10 pA, ≥10 GΩ rule |
| CAUTION 1 + IR-04 (DUT-node C) | F, I, J | COMPLIANCE_ENERGY_ANALYSIS |
| SHUNT_RANGE_TRADEOFF §2.4 + IR-05 (burden D) | A, E, N, O | 25/50/100 mV canonical |
| IR-06/07 (AD5764) | N | AD5764 Rev F 20 V/305 µV, ±11.4 V |
| IR-08 (TLV3501) | H | TLV3501 Rev E 6.5 mV/6 mV hyst |
| IR-09 (TIA settling) | F, O | Qualified, provision-only |
| IR-10 (guard) | F, M | GUARD_STRATEGY taxonomy |
| IR-11 (Kelvin equation) | C | V_FORCE=V_DUT+V_SHUNT+I·R_LEAD |
| IR-12 (bipolar front-end) | G | ADS1262/AD7175 |
| IR-13 (grounding, not simulated) | — | GROUNDING doc, no sim |
| IR-14 (C_UPSTREAM/DOWNSTREAM) | I, J | E=½CV², 80 pF @5 V / 500 pF @2 V |
| IR-15 (Candidate C) | O | SOURCE_STAGE §2.6 |
| IR-16 (plan completeness) | A–O | This plan |

Original tests mapped: 1→C/G/N/O, 2→C/G/O, 3→A/B/H/I/J, 4→C/F/J/K, 5→E/F/G/M, 6→H/N, 7→H/M. All 1–7 content retained per IR-16.

---
*Authority: primary datasheets (LT1970A 1970afc, AD5764 Rev F, TLV3501 Rev E) override this plan. Status PHASE2-CORRECTED per PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md 2026-08-24.*
