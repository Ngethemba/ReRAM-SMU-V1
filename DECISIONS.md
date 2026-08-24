# ReRAM-SMU V1 — Engineering Decision Log

**Purpose:** Traceable record of every significant architectural and component decision.  
**Rule:** No provisional architecture is a finalized decision. Decisions are added only after adequate evidence (datasheet, calculation, simulation, or measurement).

---

## Decision Record Format

Each decision uses this template:

```markdown
### DEC-XXX — <Subject>

- **Date:** YYYY-MM-DD
- **Status:** PROPOSED | ACCEPTED | REJECTED | SUPERSEDED
- **Requirement(s):** REQ-... 
- **Alternatives considered:**
- **Evidence examined:**
- **Decision:**
- **Rationale:**
- **Consequences:**
- **Verification status:** UNVERIFIED | SIMULATED | MEASURED | REVIEWED
- **Provenance:** (datasheet citations where applicable)
```

Copy the template for each new decision.

---

## Decisions

### DEC-000 — Workspace Structure and Project Governance

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-GEN-002, REQ-GEN-003
- **Alternatives considered:** Minimal flat structure vs full engineering hierarchy; ad-hoc docs vs numbered requirements.
- **Evidence examined:** Project charter, requirements draft, engineering rules, roadmap with 14 phases.
- **Decision:** Adopt the full hierarchy in `README.md` (docs/hardware/simulation/firmware/software/bom/manufacturing/measurements/tools/archive) with numbered requirements, phase-gated roadmap, and mandatory decision/risk/open-question logs.
- **Rationale:** Traceability and review gates are required for a precision instrument; flat structure would lose provenance.
- **Consequences:** Slightly higher upfront overhead; all future work must remain inside `E:/ReRAM-SMU V1`.
- **Verification status:** REVIEWED (inspected this session)
- **Provenance:** Charter + Engineering Rules v0.1.0

---

### DEC-007 — Four-Quadrant Architecture Mandatory for V1

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-SRC-003, REQ-SRC-004, REQ-SRC-005
- **Alternatives considered:** (a) voltage-source-only with sink via passive load, (b) two-quadrant (source only), (c) true four-quadrant.
- **Evidence examined:** Phase 1 synthesis `docs/research/PHASE1_RESEARCH_SUMMARY.md` §9 + `SMU_ARCHITECTURE_SURVEY.md` §0 + `RERAM_MEASUREMENT_REQUIREMENTS.md` §2/§5.5 (bipolar SET/RESET, NDR, DUT push-back) + `COMMERCIAL_SMU_BENCHMARK.md` §2 (all commercial SMUs are 4-quad, sink 4–8× offset penalty) + 4-agent agreement.
- **Decision:** Promote REQ-SRC-005 from PROVISIONAL-preferred to CONFIRMED: V1 shall be four-quadrant — source + sink, both polarities, continuous (Q1 +V/+I, Q2 +V/–I, Q3 –V/–I, Q4 –V/+I). Power ≈50 mW @±5 V·±10 mA; quadrant-switch glitch and sink accuracy characterized separately.
- **Rationale:** ReRAM bipolar switching plus NDR/thermal snap requires sink without relay click at zero-cross. Two-quadrant would require mode switching artifacts and fail hot-swap inrush.
- **Consequences:** Output stage must be bipolar (not single-supply); Kelvin and compliance loops must handle sink; sink accuracy is less than source (offset multipliers) — must be budgeted.
- **Verification status:** UNVERIFIED — requires architecture review + quadrant-transition scope capture (Phase 3–6).
- **Provenance:** DEC-007 in `docs/architecture/REQUIREMENTS_TRACEABILITY.md`; no component promoted.

### DEC-008 — Current Ranges 10 mA→100 nA (Six Ranges) Confirmed

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-MEAS-001, REQ-SRC-006
- **Alternatives considered:** (a) 5 ranges (omit 100 nA), (b) 6 ranges as provisional, (c) 7 ranges including 10 nA, (d) add 100 mA.
- **Evidence examined:** RERAM §2 (Icc 10 µA–1 mA std, RESET 0.2–3 mA, Al2O3 1–15 mA edge), BURDEN analysis (R=10 Ω–1 MΩ @100 mV FS, Johnson <1% FS @10 Hz down to 100 nA, TC 250 ppm), LOW_CURRENT §3.1 (10 nA needs 10 MΩ + electrometer), COMMERCIAL §4 (V1 ±10 mA is lowest commercial max tier).
- **Decision:** Confirm 6 ranges as listed in REQ-MEAS-001; explicitly reject 100 mA for V1 and defer 10 nA to V2 (FUTURE) per REQ-MEAS-006. Shunt values are not yet fixed; only range decade is confirmed.
- **Rationale:** Logarithmic 5-decade cover (20 nA–2 mA platform) needs 100 nA for HRS; 100 mA adds power/thermal/relay burden with no low-voltage evidence.
- **Consequences:** 6-way autoranging with hysteresis required; shunt TC + relay leakage per decade must be budgeted.
- **Verification status:** UNVERIFIED — per-range calibration + shunt TC + leakage measurement (Phase 4).
- **Provenance:** `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md` (k=1.380649e-23, T=300 K, B brickwall).

### DEC-009 — Low-Current Floor Quantified (Replaces “Several nA”)

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-MEAS-002, REQ-MEAS-005, REQ-CAL-003
- **Alternatives considered:** Keep vague “several nA” vs quantify as resolution vs RMS noise vs MUC vs accuracy per metrology.
- **Evidence examined:** LOW_CURRENT §1.1/3.1 + NOISE_BUDGET_FRAMEWORK (Johnson 0.41 pA @100 nA/10 Hz, 4.07 pA @1 kHz) + PHASE1 §6 synthesis.
- **Decision:** Quantify REQ-MEAS-002: 100 nA range (1 MΩ, 100 mV FS, 10 Hz BW, shorted input) — detection 3σ ≈1.5–6 pA, quantitative 10σ ≈5–20 pA, practical quantitative MUC ≈1 nA (≈10% of 100 nA) with averaging/shielding, leakage-corrected. Resolution (24-bit LSB ≈6 fA) is distinct and not the floor. Promoted to CONFIRMED.
- **Rationale:** Metrology requires separate reporting of resolution/noise/MUC/accuracy (REQ-MEAS-005). Vague phrase was not testable.
- **Consequences:** Verification is noise-floor time series + open-input leakage (100 s) at 100 nA range; docs/firmware must report four numbers separately.
- **Verification status:** UNVERIFIED — requires prototype measurement.
- **Provenance:** GUM terminology via UNCERTAINTY framework; Q-07 resolved.

### DEC-010 — Voltage Range Provisional-Verified (No Promotion)

- **Date:** 2026-08-24
- **Status:** ACCEPTED (note)
- **Requirement(s):** REQ-SRC-001, REQ-SRC-002
- **Alternatives considered:** ±5 V vs ±2 V primary vs ±10 V outer.
- **Evidence examined:** RERAM §2 (SET +0.6–1.5 V, forming +2–5 V) + COMMERCIAL §4 (V1 ±5 V inside most accurate commercial 2 V–20 V band).
- **Decision:** No status promotion; keep REQ-SRC-001/002 as PROVISIONAL (now annotated VERIFIED AS REASONABLE / WELL-SUPPORTED). ±5 V outer justified for forming headroom without mains; ±10 V explicitly deferred.
- **Rationale:** Higher voltage would increase complexity/SOA/safety scope with negligible ReRAM benefit for low-voltage stacks.
- **Consequences:** Headroom analysis still required (Phase 3, REQ-PWR-003).
- **Verification status:** UNVERIFIED — bench sourcing across –5→+5 V.
- **Provenance:** `docs/research/PHASE1_RESEARCH_SUMMARY.md` §4.

### DEC-011 — Compliance Triad and Timing Targets (Research)

- **Date:** 2026-08-24
- **Status:** ACCEPTED (research targets, not yet spec)
- **Requirement(s):** REQ-SAFE-001, REQ-SAFE-002, REQ-SAFE-007, REQ-MEAS-001
- **Alternatives considered:** Compliance as value vs range-locked decade, trip-only vs regulation, SOA hyperbola vs per-variable limits.
- **Evidence examined:** `COMPLIANCE_RESEARCH.md` §§1–8 (compliance ≠ range compliance ≠ SOA trip, Keithley/NI specs, hot-plug overshoot anecdote) + RERAM §3.2 (SPA 4.5 µs vs ST 110 ns vs CLA 500 ps).
- **Decision:** Adopt research envelope for V1 compliance: regulation (flat CC, flagged) + fast trip (<5 µs) + SOA `|V·I| ≤50–60 mW` DC; regulation settle <50 µs to Icc, trip <5 µs, overshoot <1% resistive / <5% into 1 nF with soft-start, flag latency ≤1 NPLC, min compliance 0.1% of I_range, continuous Icc within range (10 µA/100 µA/1 mA/10 mA subset mandatory).
- **Rationale:** Firmware alone is ms (ADS1262) vs filament ns–µs — hardware loop mandatory (REQ-SAFE-001); distinction prevents silent mis-data and over-forming overshoot.
- **Consequences:** Loop compensation, displacement-current holdoff, and scope fault-injection (short+step) are required gates before any ReRAM DUT.
- **Verification status:** UNVERIFIED — scope I(t) + flag timing per range.
- **Provenance:** `COMPLIANCE_RESEARCH.md` provenance list (NI, Tek/Keithley, icnavigator).

### DEC-012 — Sweep & Kelvin & Guard Resolutions

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-SAFE-005, REQ-MEAS-004, REQ-DUT-001, REQ-DUT-003, REQ-PWR-004
- **Alternatives considered:** Linear vs log sweep, pulse vs DC, triax now vs later.
- **Evidence examined:** RERAM §4 (step 0.01–0.05 V, dwell 50 ms–2 s, ≥200 pts/loop), LOW_CURRENT §4 (guard-ring checklist), COMMERCIAL §4 (guard/triax required for fA).
- **Decision:** REQ-SAFE-005 confirmed with parametric table (step 1–50 mV default 10 mV, dwell 10 ms–2 s default 50–100 ms, ≥200 pts/loop, built-in preset 0→+Vmax→0→–Vmax→0, hold range + flag). REQ-MEAS-004 hysteresis ≥2 samples post-trip confirmed. REQ-DUT-001 Kelvin confirmed (remote sense >10 GΩ, 5 VFS, 1 MΩ lead). REQ-DUT-003 triax/guard explicitly FUTURE/V2 — V1 provisions guard-ring copper (exposed, stitched plane, C0G-only) without claiming performance. NPLC mains nulling added to REQ-PWR-004.
- **Rationale:** Slow DC staircase covers >90% ReRAM quasi-static literature; pulse is explicitly future; guard deferred avoids electrometer complexity yet leaves upgrade path.
- **Verification status:** UNVERIFIED — sweep automation test, 2-wire vs 4-wire on dummy, guard-ring visual + leakage test.
- **Provenance:** `PHASE1_RESEARCH_SUMMARY.md` §§10–11.

### DEC-013 — Functional Architecture Selected for Phase 3

- **Date:** 2026-08-24
- **Status:** SELECTED FOR PHASE 3 (not FINAL)
- **Requirement(s):** REQ-SRC-001..007, REQ-MEAS-001..008, REQ-SAFE-001..008, REQ-DUT-001, REQ-PWR-003/004
- **Alternatives considered:** Architecture A (DAC+amp+shunt), B (dual-loop), C (TIA), D (hybrid multi-range).
- **Evidence examined:** `docs/architecture/ARCHITECTURE.md` (block diagram low-side shunt outside SENSE, SENSE feedback at DUT, dual compliance, 4-quad sink, Kelvin), `PHASE2_DECISION_MATRIX.md` scoring, Phase 1 RERAM/COMPLIANCE/LOW_CURRENT.
- **Decision:** Select conceptual architecture: Host→USB→MCU→DAC (Source+Compliance refs)→Source/Sink stage (LT1970A primary, §DEC-014) → FORCE_HI → DUT → FORCE_LO→low-side shunt matrix (10Ω–1MΩ + TIA provision for 100 nA, §DEC-015) → GND; SENSE_HI/LO differential >10 GΩ to ADC; compliance dual; power tree ±12 V ext → LDO domains; grounding single plane partitioned (§DEC-020).
- **Rationale:** Hybrid D gives lowest complexity for 10 mA→100 nA with clear pA upgrade; low-side shutter avoids high-CM.
- **Consequences:** Shunt outside SENSE → 100 mV burden budgeted as headroom (5% @2 V, 16% @0.6 V → range-dependent burden §DEC-017).
- **Verification status:** UNVERIFIED — Phase 3 simulations (SOURCE_HEADROOM, compliance transient, stability).
- **Provenance:** `ARCHITECTURE.md` + 6-agent Phase 2.

### DEC-014 — Output-Stage Candidate

- **Date:** 2026-08-24
- **Status:** SELECTED FOR PHASE 3 (primary) / ALTERNATE
- **Requirement(s):** REQ-SRC-001/002/006 (±5 V/±10 mA, ±2 V primary), REQ-SAFE-001
- **Alternatives considered:** LT1970A (±500 mA, 1% limiter, ISRC/ISNK separate, LTspice model, DFN, $6.87 1k) vs OPA548 (£, 30 mA drift, thermal), OPA551, OPA140/ADA4522+discrete buffer composite, dedicated source/sink amps.
- **Evidence examined:** `SOURCE_STAGE_CANDIDATES.md` (51 KB, LT1970A specs: ±500 mA, ±% limit, shutdown, thermal 70–170 mW worst, lifecycle active), CAUTION 1 analysis (bipolar Source-V/Measure-I with sink = true 4-quad experimental behavior, not arbitrary I-source), CAUTION 2 burden feedback point.
- **Decision:** **Primary: LT1970A** SELECTED FOR PHASE 3 simulation; **Alternate: precision op-amp + complementary discrete buffer (OPA140/ADA4522 + BJT/MOS)** kept as fallback if LT1970A lifecycle/cap-load stability fails.
- **Rationale:** LT1970A is only candidate with precise externally controlled bidirectional current limit and LTspice model for compliance loop; OPA548-class is high-current but not precision for ±2 V.
- **Verification status:** UNVERIFIED — load regulation + cap-load stability sim (Phase 3).
- **Provenance:** ADI datasheet 1970afc, Digikey stock, LTspice model.

### DEC-015 — Current-Measurement Topology

- **Date:** 2026-08-24
- **Status:** SELECTED FOR PHASE 3
- **Requirement(s):** REQ-MEAS-001/002/008, REQ-PWR-003
- **Alternatives considered:** Pure shunt, pure TIA, hybrid (shunt 10 mA→1 µA + TIA 100 nA).
- **Evidence examined:** `MEASUREMENT_FRONTEND_CANDIDATES.md` (21 KB) + `SHUNT_RANGE_TRADEOFF.md` (Python tables: R 10Ω–1 MΩ @100 mV FS, Johnson 0.41 pA @100 nA/10 Hz, gain to 2.5 V 25×).
- **Decision:** **Hybrid:** shunts for 10 mA→1 µA (ship REV-A), TIA footprint provisioned for 100 nA (stuff option). Low-side outside SENSE.
- **Rationale:** Shunt simple to 1 µA; TIA burden 20 µV vs 100 mV helps 100 nA guard/leakage and settling ÷Aol; pure TIA not needed for V1.
- **Verification status:** UNVERIFIED — per-range overload recovery + noise @NPLC sim/measurement.
- **Provenance:** Burden analysis 25/50/100 mV range-dependent table.

### DEC-016 — Shunt Location

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-MEAS-001, REQ-DUT-001, REQ-SAFE-001
- **Alternatives considered:** High-side (common-mode >5 V → diff amp CMRR burden), low-side (ground-ref), floating/remote-sense.
- **Evidence examined:** `MEASUREMENT_FRONTEND_CANDIDATES.md` §3 + `KELVIN_SENSE_ARCHITECTURE.md` (SENSE encloses DUT only, burden outside loop).
- **Decision:** **Low-side, between FORCE_LO and GND, outside DUT-sense loop.** SENSE_HI/LO at DUT terminals correct lead drop, not burden.
- **Rationale:** Ground-ref diff amp meets Vos/TC without high-CM; simplifies guard; compliance sense ground-ref; tradeoff is extra headroom (see DEC-017).
- **Verification status:** UNVERIFIED — Kelvin vs 2-wire on dummy + compliance sense accuracy.
- **Provenance:** CAUTION 2 analysis.

### DEC-017 — Burden-Voltage Philosophy

- **Date:** 2026-08-24
- **Status:** SELECTED FOR PHASE 3
- **Requirement(s):** REQ-MEAS-001/007/008, REQ-PWR-003, REQ-CAL-003
- **Alternatives considered:** Fixed 25/50/100 mV FS and range-dependent.
- **Evidence examined:** `SHUNT_RANGE_TRADEOFF.md` (R 10Ω–1 MΩ, P 1 mW→10 nW, Johnson table) + `BURDEN_VOLTAGE_ANALYSIS.md`; CAUTION 2: 100 mV =5% @2 V/16.7% @0.6 V not harmless; Kelvin does NOT eliminate burden.
- **Decision:** **Range-dependent FS:** 100 mV on 10 mA–10 µA, 50 mV on 1 µA, 25–50 mV on 100 nA (tradeoff: Johnson 3.16× noisier but burden halves). V1 provisional range-dependent candidate for Phase 3 sim.
- **Rationale:** Halving burden on low-V ranges materially improves DUT voltage accuracy where ReRAM read is 0.1–0.6 V.
- **Verification status:** UNVERIFIED — DUT impact vs ADC gain/noise headroom sim.
- **Provenance:** Python .venv Johnson `√(4kTRB)` recomputation + source headroom 70–170 mW.

### DEC-018 — Compliance Architecture

- **Date:** 2026-08-24
- **Status:** SELECTED FOR PHASE 3
- **Requirement(s):** REQ-SAFE-001/002/007, REQ-MEAS-001
- **Alternatives considered:** A LT1970A internal limiter only, B external analog loop, C fast trip+coarse, D dual continuous+trip/SOA.
- **Evidence examined:** `COMPLIANCE_ARCHITECTURE.md` (48 KB, diode-OR vs limiter, stored-energy E=0.5CV²: 10 nF@5 V 125 nJ dominates, 100 nF cable 1.25 µJ) + `COMPLIANCE_ENERGY_ANALYSIS.md`.
- **Decision:** **Option D dual:** continuous regulation via LT1970A ISRC/ISNK (1% accuracy, 4 µs) + independent fast comparator latch (TLV3501-class, <5 µs) + SOA hyperbola 50 mW, per-segment/polarity programmable (CAUTION 3), not hard-coded SET=compliance. Add low output C ≤10 nF + 10 Ω isolation.
- **Rationale:** Only D satisfies REQ-SAFE-001 hardware independence + per-segment programmable + CAUTION 1 sink/source separate limits; A alone fails downstream-C overshoot; B alone lacks trip independence; C alone is crowbar not regulation.
- **Verification status:** UNVERIFIED — transient sim (load step, filament R 1 MΩ→1 kΩ in 1 µs) + scope fault injection.
- **Provenance:** LT1970A datasheet 1970afc + Keithley/NI compliance specs.

### DEC-019 — Kelvin Sense Loop

- **Date:** 2026-08-24 (amended 2026-08-24 per IR-02/03/04/11)
- **Status:** ACCEPTED (amended)
- **Requirement(s):** REQ-DUT-001, REQ-SRC-001/002
- **Alternatives considered:** Source regulates FORCE vs SENSE; burden inside vs outside loop; passive divider vs buffered sense; permanent 10 MΩ pull vs switched.
- **Evidence examined:** `KELVIN_SENSE_ARCHITECTURE.md` (SENSE differential >10 GΩ via high-Z buffer before attenuation, DUT-node capacitance budget, switched open-sense) + PRELIMINARY_ERROR_BUDGET IR-02 loading table (20 MΩ passive divider: 83% error @100 MΩ DUT) + LT1970A 1970afc + COMPLIANCE_ENERGY.
- **Decision:** **Source regulates SENSE at DUT via high-Z buffers (≥10 GΩ, ≤10 pA) before any divider; burden outside loop:** `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (canonical). Open SENSE_HI/LO detected via **switched** continuity test before OUTPUT ON + analog-switch disconnect during measurement (≥10 GΩ effective or disconnected; no DC load invariant per IR-03). 1 nF filter is **after buffer**, not at DUT. Fallback to FORCE mode on open, latched.
- **Rationale:** Kelvin correctness: V_DUT = V_SENSE; passive divider loads HRS; permanent 10 MΩ violates nA budget; filter cap at DUT violates energy budget.
- **Verification status:** UNVERIFIED — open-sense switched test + 2-wire vs 4-wire + DUT-loading sweep 1 MΩ–1 GΩ + sense-C sweep (Phase 3 IR-16 D,E,F).
- **Provenance:** CAUTION 4 + IR-02/03/04 independent recalculations.

### DEC-020 — Grounding Philosophy

- **Date:** 2026-08-24 (amended per IR-13)
- **Status:** ACCEPTED (wording corrected)
- **Requirement(s):** REQ-PWR-004, REQ-MEAS-002/008
- **Alternatives considered:** Single continuous plane partitioned vs split AGND/DGND vs star vs isolated analog domain.
- **Evidence examined:** `GROUNDING_AND_RETURN_PATHS.md` (36 KB, return paths: DAC ref, ADC ref, MCU, relay, USB, FORCE_LO).
- **Decision:** **One continuous reference plane. Analog/digital separation is achieved by placement, local return-current control, routing discipline, and decoupling. There is no etched AGND/DGND split and no physical AGND/DGND bridge.** Detailed geometry (precision reference return, shunt Kelvin reference, FORCE_LO reference, relay return, USB return, chassis/shield) defined separately. A single tie at the ADC is a measurement point, not a gap-bridging element.
- **Rationale:** Return-path analysis > “star best”; split invites antenna; "single continuous plane + single bridge" was self-contradictory phrasing; isolated domain adds DC/DC noise.
- **Verification status:** UNVERIFIED — noise PSD with/without USB + partitioning review (Phase 8).
- **Provenance:** CAUTION 5 + IR-13.

### DEC-021 — Isolation Classification

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-SW-001, REQ-PWR-001
- **Alternatives considered:** Direct USB, external isolator dongle, onboard isolated DC/DC (ADuM3160-class).
- **Evidence examined:** `ISOLATION_STRATEGY.md` (23 KB, ground loops via scope/PSU/DUT, noise injection, cost/complexity).
- **Decision:** **Isolation classified as OPTIONAL/RECOMMENDED — not required for V1.** Provide isolator footprint (ADuM3160 + isolated DC/DC) but ship REV-A direct USB with warning; external dongle is acceptable path to V2.
- **Rationale:** V1 low-voltage bench with external ±12 V can manage loops via wiring discipline; onboard isolation adds cost/complexity.
- **Verification status:** UNVERIFIED — loop injection test.
- **Provenance:** Phase 1 calibration philosophy.

### DEC-022 — Guard and Connector Provision

- **Date:** 2026-08-24 (amended per IR-10)
- **Status:** ACCEPTED (provision, wording corrected)
- **Requirement(s):** REQ-MEAS-002/006, REQ-DUT-002/003
- **Alternatives considered:** Reserved copper+stitching vs active driven guard now vs triax now; passive keepout vs grounded shield vs driven guard.
- **Evidence examined:** `GUARD_STRATEGY.md` (corrected taxonomy) + `LOW_CURRENT_MEASUREMENT.md` §4 + IR-10.
- **Decision:** **V1 provision:** guard ring copper (exposed, no mask, stitched inner guard plane) encircling high-Z nodes (100 nA shunt/sense) as **passive keepout / grounded shield** (no driven guard stuffed in REV-A — no arbitrary ground guard around SENSE_HI). Optional **driven-guard footprint** if provisioned: amplifier is **powered from normal rails, input tracks SENSE_HI, output drives guard** — corrected from "powered from SENSE_HI through 1 GΩ." Shield tied to FORCE_LO via 1 MΩ||10 nF. Triax is V2.
- **Rationale:** V1 does not claim electrometer but must leave upgrade path without re-spin; mis-tied passive guard worsens leakage.
- **Verification status:** UNVERIFIED — visual + leakage <10 pA.
- **Provenance:** CAUTION 4 + IR-10 + low-current guard checklist.

### DEC-023 — Component Adversarial Verdicts (Phase 2)

- **Date:** 2026-08-24
- **Status:** ACCEPTED (K/C/R/A/D)
- **Requirement(s):** REQ-GEN-002, lifecycle/sourcing
- **Alternatives considered:** Previously suggested AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525, STM32G431 vs new candidates.
- **Evidence examined:** `PHASE2_COMPONENT_MATRIX.md` (32 KB, 10+ web_search batches, datasheets rev F/G/K, DigiKey/Mouser stock, SPICE model column) + `PRELIMINARY_ERROR_BUDGET.md` (**corrected:** AD5764 LSB 305.2 µV on 20 V span, 20 V span, ±11.4 V supplies — IR-06/07; post-cal headroom recomputed).
- **Decision:** Verdicts: **AD5686R — KEEP AS ALTERNATE** (correct LSB 152.6 µV on 10 V system; post-cal headroom still better vs AD5764 when span waste accounted for); **ADA4522-2 — KEEP role-dependent** (shunt sense, not DUT sense on 100 nA); **LT1970A — KEEP (primary)** (active, 1% limiter, LTspice model; floor 4 mV); **ADS1262 — KEEP AS ALTERNATE** (vs AD7175 preferred for bipolar front-end per IR-12); **LT1763 — KEEP positive regulator only** (negative rail requires LT1964-class, IR-07); **ADR4525 — KEEP** but LTC6655/REF50xx deferred branch; **STM32G431 — KEEP AS ALTERNATE**.
- **Rationale:** Independent datasheets show AD5764-class requires ±11.4 V and wastes half codes at ±5 V; INL in volts equalizes — do not promote on INL alone.
- **Verification status:** UNVERIFIED — simulation gates before `bom/approved/`.
- **Provenance:** Manufacturer datasheets (AD5686R Rev F, **AD5764 Rev F ±11.4 V, LSB 305.2 µV**, LT1970A 1970afc 4 mV floor, TLV3501 Rev E Vos 6.5 mV) + counterfeit policy.

### DEC-024 — Compliance Minimum Programmability and Range-Coercion Architecture

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-SAFE-001, REQ-SRC-006, REQ-MEAS-001
- **Alternatives considered:** (A) keep 0.1% binding for LT1970A, (B) remove requirement entirely, (C) coercion + precision-loop tier, (D) single separate compliance bank for all ranges.
- **Evidence examined:** LT1970A 1970afc/1970fe (VSENSE_MIN 4 mV typ, Vc<60 mV nonlinear, I=Vc/(10·R)), SHUNT_RANGE_TRADEOFF burden table, COMPLIANCE_ARCHITECTURE cautions, independent recomputation IR-01 (I_min≈4% FS at 100 mV, 16% at 25 mV).
- **Decision:** Tiered rule: (1) LT1970A limiter: minimum compliance = max(4 mV/Rsense, 60 mV/(10·Rsense)) — about 4% FS at 100 mV burden, 16% at 25 mV. Firmware implements compliance-aware range coercion; (2) Precision external CC loop (Source Candidate C) — 0.1%·I_range is research retention for Candidate C, validated in Phase 3; (3) Separate compliance-sense bank is provisioning option but not required for REV-A if coercion satisfies typical ReRAM Icc 10 µA–1 mA.
- **Rationale:** Primary datasheets override the copied Keithley rule; 0.1% as closed-loop servo semantics, not LT1970A Vc/10 threshold physics; forcing LT1970A to 0.1% requires 4 V burden — destructive.
- **Consequences:** COMPLIANCE_ARCHITECTURE solutions A–D formalized; Phase 3 tests A,B,H added; REQUIREMENTS REQ-SAFE-001 revised; host driver logs compliance_range.
- **Verification status:** UNVERIFIED — Phase 3 sims IR-16 A,B,H + scope fault injection.
- **Provenance:** LT1970A 1970afc p.12–13 (VCSRC/VCSNK 4 mV floor, 60 mV linear) + PHASE2_CORRECTIONS IR-01.

### DEC-025 — Source Composite Candidate

- **Date:** 2026-08-24
- **Status:** SELECTED FOR PHASE 3
- **Requirement(s):** REQ-SRC-001/002/006, REQ-SAFE-001
- **Alternatives considered:** LT1970A direct, precision+discrete, composite (Candidate C) — precision outer loop + LT1970A booster.
- **Evidence examined:** `SOURCE_STAGE_CANDIDATES.md` new §2.6 + `docs/research/PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md` IR-15.
- **Decision:** **Source Candidate C — Precision outer loop + LT1970A inner/power stage:** outer ADA4522/OPA140-class drives LT1970A as power/current-limit booster; LT1970A provides sink drive, 4 µs limit, enable/flags while outer amp sets precision offset. Phase 2 defines only; do not assume stability.
- **Rationale:** Retains LT1970A drive/limit/enable while reducing reliance on its 200 µV offset; promising third architecture between monolithic and discrete.
- **Consequences:** Phase 3 must test nested loop interaction, phase margin, compliance crossover, Kelvin sense, capacitive DUT (IR-16 O).
- **Verification status:** UNVERIFIED — nested-loop AC + transient per PHASE3 plan O.
- **Provenance:** SOURCE_STAGE_CANDIDATES + IR-15.

---

### Candidate Architecture — Explicitly NOT Decisions (remaining after Phase 2 selections)

The following remain `PROVISIONAL / REQUIRES VERIFICATION` and must not be treated as decisions beyond the SELECTED FOR PHASE 3 gates above. Final values require simulation:

| Candidate | Notes | Required Evidence Before Promotion |
|-----------|-------|--------------------------------------|
| DAC AD5686R quad 16-bit | KEEP AS ALTERNATE (LSB 152.6 µV on 10 V system; gain-stage error) | AD5764 vs AD5686R error-budget sim with actual 20 V span (LSB 305.2 µV, ±11.4 V rail — IR-06/07) + DMM |
| DAC AD5764 ±10 V 16-bit | PREFERRED candidate only if gain-stage removal justifies ±11.4 V / cost / span waste (IR-06/07) | Same |
| Amp ADA4522-2 zero-drift | KEEP role-dependent (shunt sense, not DUT sense on 100 nA per IR-02) | Noise/TC sim + bench |
| Power amp LT1970A | KEEP primary (500 mA, 1% limiter, floor 4 mV per IR-01) | Load regulation + cap stability sim + range coercion |
| Source Candidate C outer+LT1970A booster | SELECTED FOR PHASE 3 (DEC-025) — precision outer loop + LT1970A power stage | Nested-loop stability O |
| ADC ADS1262 / AD7175 | Both CANDIDATE (bipolar front-end A/B/C per IR-12, NPLC sweep) | Bipolar front-end + NPLC sweep sim vs measured noise |
| Regulator LT1763 positive / negative LT1964-class | Both CANDIDATE per rail — LT1763 positive only (IR-07) | Dropout/PSRR sim with complementary neg |
| Reference ADR4525 / LTC6655 | Shared vs separate branch | Drift/correlation sim |
| Shunts + relay matrix | Hybrid 10 mA→1 µA + TIA provision; range-dependent D canonical per IR-05 | Leakage/TC + burden headroom sim |
| MCU STM32G431 family | KEEP AS ALTERNATE (G474/RP2040 alternates) | SPI/USB/timer check |

No FINAL promotion until Phase 3 simulation gates pass. Specs must not be propagated from memory.

---


### DEC-026 — Phase 3 Source Architecture Selection

- **Date:** 2026-08-24
- **Status:** SELECTED FOR SCHEMATIC (Phase 3 evidence)
- **Requirement(s):** REQ-SRC-001/002/006, REQ-SAFE-001, REQ-PWR-003
- **Alternatives considered:** Candidate A LT1970A direct, Candidate B ADA4522+BJT buffer, Candidate C outer+LT1970A nested (DEC-025).
- **Evidence examined:** simulation/results/phase3/PHASE3_RESULTS.md + gate6_source_dac.md (Tests O, A+B, C+D, F+J, I); ngspice A PM50° OS6.5%@10nF (0.2%@100p) 12µV@2V 4µs 1% ISRC/ISNK, B PM60° OS3.2% 0.7µV but coarse trip >10µs, C PM57° analytic OS16.6% marginal; Kelvin 160/160 PASS, compliance coercion 6/6 PASS, POR 200ms PASS.
- **Decision:** **Candidate A LT1970A direct SELECT (primary)** for REV-A schematic; **Candidate B KEEP AS FALLBACK** (precision alternate, no integrated limit); **Candidate C REQUIRES PROTOTYPE** (do not layout until bench, lead-lag tuning needed).
- **Rationale:** Only A delivers 4-quadrant ±500mA (10mA need) + 1% separate source/sink limit 4µs + ENABLE/TSD in one pad with lowest effort and PASS >45° (50°/6.5%). B best DC (0.7µV) but fails 4µs envelope; C best lifecycle/accuracy but 16.6% OS marginal → prototype-gated per Phase 3 exit criteria.
- **Consequences:** Schematic capture may begin with A; B kept for V1.1 if LT1970A offset uncorrectable; C lab experiment parallel.
- **Verification status:** SIMULATED — bench POR/leakage/DA/therm EMF/humidity still required per MODEL_LIMITATIONS.
- **Provenance:** LT1970A 1970afc, ADA4522 RevI, OPA140 RevF, ngspice-47, LTspice 26.0.2.1, PHASE3_RESULTS.

### DEC-027 — Phase 3 DAC/ADC/Reference Selection

- **Date:** 2026-08-24
- **Status:** SELECTED FOR SCHEMATIC
- **Requirement(s):** REQ-MEAS-007/008, REQ-SRC-001/002, REQ-PWR-003
- **Alternatives considered:** AD5686R 0-5V→×2 (0.01% 10ppm RG vs 0.1% REJECT), AD5764 actual 20V 305µV half codes ±11.4V, AD5791 20-bit prototype-only; ADS1262 vs AD7175-8; ADR4525 vs LTC6655LN.
- **Evidence examined:** simulation/phase3/dac_adc/test_N_dac_comparison.py 1000 MC 2-pt cal at ±5V; AD5764 2V +46% headroom k=2, 0.1V +9%/−19%, AD5686R 0.01% +48% @2V; 10mV step 1.5% AD5686R vs 3.0% AD5764 <10% criterion; PHASE3_ERROR_BUDGET Type A/B.
- **Decision:** **DAC SELECT AD5764** (20V 305µV, INL±305µV, no gain-stage, half codes OK, raw ±12V Option A 0.6V margin) with LTC6655LN-2.5 primary / ADR4525 fallback; fallback AD5686R 0-5V→×2 with 0.01% RG kept; **ADC SELECT AD7175-8 primary** (250kSPS 20µs Sinc5+1) for FAST 10-20ms + autorange, **ADS1262 fallback** for NORMAL/LOW; hybrid PGA per-range D (25mV 10/1mA→3.13×, etc.) + per-range JFET/reed.
- **Rationale:** AD5764 simplest meeting REQ-MEAS-007 with margin at ±2V primary without precision-resistor gain stage; LSB equal in volts to AD5686R; supply via raw ±12V (IR-07). AD7175 fastest for 23.5ms switch seq + NPLC without discarding samples.
- **Consequences:** Schematic capture with primary selections; alternates kept second-source; no procurement.
- **Verification status:** SIMULATED — drift/hysteresis/humidity/package parasitics bench required.
- **Provenance:** AD5686R RevF, AD5764 RevF (no ±5V mode), AD5791 RevF, ADR4525 RevG, LTC6655 fb, ADS1262/AD7175 datasheets, ngspice-47, PHASE3_RESULTS.

## Decision Index

| ID | Subject | Status | Date |
|----|---------|--------|------|
| DEC-000 | Workspace structure and governance | ACCEPTED | 2026-08-24 |
| DEC-007 | Four-quadrant architecture mandatory | ACCEPTED | 2026-08-24 |
| DEC-008 | Current ranges 10 mA→100 nA confirmed | ACCEPTED | 2026-08-24 |
| DEC-009 | Low-current floor quantified | ACCEPTED | 2026-08-24 |
| DEC-010 | Voltage range provisional-verified | ACCEPTED | 2026-08-24 |
| DEC-011 | Compliance triad and timing | ACCEPTED | 2026-08-24 |
| DEC-012 | Sweep & Kelvin & Guard | ACCEPTED | 2026-08-24 |
| DEC-013 | Functional architecture for Phase 3 | SELECTED FOR PHASE 3 | 2026-08-24 |
| DEC-014 | Output-stage candidate (LT1970A primary) | SELECTED FOR PHASE 3 | 2026-08-24 |
| DEC-015 | Current-measurement topology (hybrid) | SELECTED FOR PHASE 3 | 2026-08-24 |
| DEC-016 | Shunt location (low-side) | ACCEPTED | 2026-08-24 |
| DEC-017 | Burden-voltage philosophy (range-dependent) | SELECTED FOR PHASE 3 (canonical IR-05) | 2026-08-24 |
| DEC-018 | Compliance architecture (dual) | SELECTED FOR PHASE 3 (amended IR-01/08/14) | 2026-08-24 |
| DEC-019 | Kelvin sense loop (SENSE feedback) | ACCEPTED (amended IR-02/03/04/11) | 2026-08-24 |
| DEC-020 | Grounding (single plane, no split) | ACCEPTED (wording corrected IR-13) | 2026-08-24 |
| DEC-021 | Isolation (optional) | ACCEPTED | 2026-08-24 |
| DEC-022 | Guard provision | ACCEPTED (wording corrected IR-10) | 2026-08-24 |
| DEC-023 | Component adversarial verdicts | ACCEPTED (corrected IR-06/07) | 2026-08-24 |
| DEC-024 | Compliance minimum programmability / coercion | ACCEPTED | 2026-08-24 |
| DEC-025 | Source composite candidate (outer+booster) | SELECTED FOR PHASE 3 | 2026-08-24 |
| DEC-026 | Phase 3 Source Architecture Selection | SELECTED FOR SCHEMATIC (amended R1/R5) | 2026-08-24 |
| DEC-027 | Phase 3 DAC/ADC/Reference Selection | SELECTED FOR SCHEMATIC (amended R3/R4) | 2026-08-24 |
| DEC-028 | P3IR-01 Shared Rsense Topology | ACCEPTED (corrects DEC-026 Rsense) | 2026-08-24 |
| DEC-029 | P3IR-06 Reed Relay for Open-Sense | ACCEPTED | 2026-08-24 |
| DEC-030 | P3IR-07 1GΩ Measurement Envelope | ACCEPTED | 2026-08-24 |
| DEC-031 | Phase 3 Corrective Review Overall | CONDITIONAL — PROTOTYPE GATE | 2026-08-24 |
| DEC-032 | MCU Selection — STM32G474 RET6 PRIMARY | SUPERSEDED by DEC-038 | 2026-08-24 |
| DEC-033 | 05_CURRENT_RANGES 6-Shunt Shared Low-Side with Kelvin & BBM | SELECTED FOR SCHEMATIC | 2026-08-25 |
| DEC-034 | 06_CURRENT_FRONTEND_ADC ADS1262 Re-derived Chain | PARTIALLY SUPERSEDED by DEC-042 (supply/VCM) | 2026-08-25 |
| DEC-035 | 03_OUTPUT_STAGE + 04_KELVIN_SENSE Detailed (Gates C/E) | SELECTED FOR SCHEMATIC | 2026-08-25 |
| DEC-036 | Pre-ERC LT1970A Physical Pinout Correction | ACCEPTED | 2026-08-25 |
| DEC-037 | Pre-ERC ADS1262 Package TSSOP-28 | ACCEPTED | 2026-08-25 |
| DEC-038 | Pre-ERC MCU G431RBT6 LQFP64 (supersedes DEC-032) | SELECTED FOR SCHEMATIC | 2026-08-25 |
| DEC-039 | Pre-ERC FAST_TRIP Latch (74LVC1G74, not MAX16054) | ACCEPTED | 2026-08-25 |
| DEC-040 | Pre-ERC Kelvin LT5400 Promotion | ACCEPTED | 2026-08-25 |
| DEC-041 | Pre-ERC AD5764 Rail Margin Guaranteed at IC | ACCEPTED | 2026-08-25 |
| DEC-042 | Pre-ERC ADS1262 Bipolar ±2.5V Preference | SELECTED FOR SCHEMATIC | 2026-08-25 |
| DEC-043 | Pre-ERC Gate 3 ADS1262 Table 6-1 Correct Pinout | ACCEPTED | 2026-08-25 |
| DEC-044 | Pre-ERC Gate 3 AD5764 32-Pin C-Grade | ACCEPTED | 2026-08-25 |
| DEC-045 | Pre-ERC Gate 3 Buffer Arithmetic Correction | ACCEPTED | 2026-08-25 |
| DEC-046 | Pre-ERC Gate 3 BAV199 & LT5400 EP Floating | ACCEPTED | 2026-08-25 |

---

### DEC-026 — Phase 3 Source Architecture Selection (Amended per P3IR-01/05)

- **Date:** 2026-08-24 (amended 2026-08-24 per R1/R5)
- **Status:** SELECTED FOR SCHEMATIC WITH PROVISIONS — CONDITIONAL (see P3IR-05)
- **Requirement(s):** REQ-SRC-001/002/006, REQ-SAFE-001
- **Evidence (corrected):** Original behavioral PASS (A 50°/6.5%@10nF, B 60°/3.2%) retained; fixed 10Ω Rsense superseded → shared canonical shunt 2.5Ω–1MΩ (DEC-028); vendor LTspice macro NOT run → MODEL LIMITATION.
- **Decision:** Candidate A LT1970A direct **remains SELECT** but with **shared Rsense** and **vendor-model + prototype pending**; B fallback unchanged; C prototype as before.
- **Verification:** **BEHAVIORAL SIMULATED — VENDOR-MODEL SIMULATED PENDING, NEEDS PROTOTYPE** (R5)

### DEC-027 — Phase 3 DAC/ADC/Reference Selection (Amended per P3IR-03/04)

- **Date:** 2026-08-24 (amended 2026-08-24)
- **Status:** SELECTED FOR SCHEMATIC (amended)
- **Evidence (corrected):** AD5764 20V 305µV half-codes 3.0% @10mV PASS with 5V ref (LTC6655-5.0/ADR435B) guaranteed ±1LSB; 2.5V full-span not guaranteed (characterized). AD7175-8 HAS NO analog PGA → needs external 100/50/25×; ADS1262 internal PGA 1–32 needs only small pre-gain.
- **Decision:** **DAC SELECT AD5764 @5V ref (LTC6655-5.0) — fallback AD5686R 0.01%; ADC SELECT ADS1262 PRIMARY — AD7175-8 ALTERNATE with external gain footprint.**
- **Verification:** DATASHEET VERIFIED + BEHAVIORAL (Test N/G)

### DEC-028 — P3IR-01 Shared Rsense Topology

- **Date:** 2026-08-24
- **Status:** ACCEPTED (corrects DEC-026)
- **Requirement(s):** REQ-SAFE-001, REQ-MEAS-001
- **Alternatives:** C1 shared canonical shunt (2.5Ω–1MΩ) as LT1970 Rsense; C2 separate compliance bank; C3 amplified loop; C4/5 outer/coarse+precision.
- **Evidence:** 1970afc (Vs=Vc/10, floor 4mV, Vc<60mV nonlinear), test_A/B CSV (fixed 10Ω fails <600µA, shared passes 50µA–1mA).
- **Decision:** **C1 shared range-switched canonical shunt SELECT for V1 REV-A** — LT1970 SENSE+ to FORCE_LO node, SENSE− to GND, Kelvin buffered. 10Ω high-side fixed-R is placeholder superseded. C2 footprint reserved.
- **Consequences:** Schematic captures shared low-side Rsense with Kelvin; R1 PASS. See Q1–Q3 in PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md.

### DEC-029 — P3IR-06 Reed Relay for Open-Sense

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-DUT-001, REQ-MEAS-002
- **Evidence:** ADG1419 Rev A: IS(off) 100pA typ 500pA max (25°C) 75nA (85°C) → fails 10pA budget (1nA MUC). Reed <1pA typ passes.
- **Decision:** **Reed relay (<1pA, Coto 9007 class) SELECT** for switched SENSE pull disconnect; ADG1419 rejected for precision path (housekeeping only). Leakage included in Test M as 1pA typ.
- **Verification:** DATASHEET VERIFIED

### DEC-030 — P3IR-07 1GΩ Measurement Envelope

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Evidence:** OPA140 SBOS498F: Ib 0.5pA typ 10pA max (25°C) 3nA (125°C), 10pA→2%@1GΩ@0.5V.
- **Decision:** Envelope split — **Guaranteed V1: ≤100MΩ (<1%); Characterized: 1GΩ@0.5–1V (2% raw → <0.5% cal with T-monitor); Exploratory: 1GΩ@0.1V (10–15%)**. OPA140 remains SELECT; electrometer ADA4530 deferred/V2.

### DEC-031 — Phase 3 Corrective Review Overall

- **Date:** 2026-08-24
- **Status:** CONDITIONAL — PROTOTYPE GATE REQUIRED
- **Evidence:** 8 findings reviewed: 4 CONFIRMED (01,02,03,06), 3 PARTIALLY (04,07,08), 1 MODEL LIMITATION (05). 6 corrective gates R1–R6: R1 PASS, R2 PASS, R3 PASS, R4 PASS, R5 CONDITIONAL, R6 PASS.
- **Decision:** **PHASE 3 — CONDITIONAL / PROTOTYPE GATE REQUIRED** — not PASS, not BLOCKED. All architectures resolved except vendor-model stability (R5). Schematic may proceed with provisions (see DEC-028/029/030, R_iso options, LTC6655-5.0, ADS1262 primary).
- **Verification:** See PHASE3_CORRECTIVE_RESULTS.md and PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md

---

### DEC-032 — MCU Selection: STM32G474RET6 PRIMARY (aligns schematic, resolves G431 sizing)

- **Date:** 2026-08-24
- **Status:** SELECTED FOR SCHEMATIC
- **Requirement(s):** REQ-SW-001/002/004, REQ-SAFE-003/004/008, REQ-MEAS-004, lifecycle 10-yr
- **Alternatives considered:** STM32G431KBT6 LQFP-32 (128 KB/32 KB, 26 GPIOs) vs STM32G431CBT6 LQFP-48 (128 KB, 39 GPIOs) vs STM32G431RBT6 LQFP-64 (128 KB, 51 GPIOs, pin-compatible) vs STM32G474RET6 LQFP-64 (512 KB/128 KB + HRTIM + 5 ADC/7 DAC, 51 GPIOs) vs RP2040/RP2350 (PIO + ext QSPI flash, $0.70, no FPU)
- **Evidence examined:** ST DS STM32G431C6 (128 KB Flash / 32 KB SRAM+CCM, 3× SPI, USB FS, 2× DAC/3× comp/2× op-amp) + ST DS STM32G474xB (512 KB dual-bank ECC / 128 KB SRAM+CCM, 4× SPI + QUADSPI, USB FS+BCD+UCPD, 7 DAC/5 op-amp/7 comp, HRTIM 184 ps) — both Active Until 2036 (ST longevity program); GPIO need calc 30–36 (7 relay coils: 6 shunt + SENSE, ENABLE, ISRC/ISNK/TSD 3, TLV3501 FLAG 1, SPI 4 + DRDY/CS 4, I2C TMP117 2, USB 2, SWD 2, LEDs 3, supervisor 1); FW sizing 85–95 KB (USB 20–30K + HAL 15K + SCPI 10K + cal 10K + app 30K) → <30 KB margin on G431 vs ~400 KB on G474; PHASE2_COMPONENT_MATRIX §2 U-MCU lifecycle + §4b KEEP AS ALTERNATE condition (“only if flash fills”); ARCHITECTURE.md §3.1 deferred MCU choice; PHASE7_SCHEMATIC_REVIEW.md §2 Sheet 08 value STM32G474 PRIMARY LQFP-64 without matching DEC (red flag); `docs/architecture/PHASE7_POWER_DOMAIN_TABLE.md` §7 audit
- **Decision:** **PRIMARY: STM32G474RET6 LQFP-64 (10×10, P0.5)** for REV-A schematic + layout + FW. **FALLBACK:** STM32G431RBT6 (pin-compatible LQFP-64, same 64-pin power map) and STM32G431CBT6 LQFP-48 kept as DNP alternate footprints. **RP2040/RP2350 rejected for V1** (cost alternate only — PIO MUX, ext flash, 5-V buffering, no FPU add risk for <$4 saving).
- **Rationale:** Dual-bank 512 KB removes FW ceiling for SCPI+TMC+cal tables+DMA double-buffer; 128 KB SRAM removes sweep/ADC buffer pressure (200 pts × 4 × 4B + USB heap); 51 GPIOs in LQFP-64 leaves 12 spare for guard/2nd ADC/R_iso-tune header vs 26 GPIOs on KBT6 (fails 30-GPIO need) and 39 on CBT6 (passes but no flash headroom). Price delta ~$4 (<3 % of $150–180 BOM) vs RP2040 risk. Identical CubeMX/HAL/IBIS family — downgrade is soft if later proven.
- **Consequences:** `08_MCU_USB_CONTROL.kicad_sch` value “STM32G474 PRIMARY LQFP-64” is now DEC-aligned (closes Phase 7 review finding). Fallback footprints provisioned as DNP. No procurement.
- **Verification status:** FW build must report `text+bss /128K vs /512K` each release; CubeMX pin report + SPI/USB/timer smoke + watchdog brown-out (REQ-SAFE-004) before DUT.
- **Provenance:** ST STM32G431C6 DS + ST STM32G474xB DS + ST longevity Until 2036 + PHASE2_COMPONENT_MATRIX + ARCHITECTURE.md + PHASE7_SCHEMATIC_REVIEW.md + PHASE7_POWER_DOMAIN_TABLE.md §7

---

*Append new decisions at the end. Never delete a decision — supersede it with a new DEC entry referencing the old one.*

### DEC-033 — Phase 7 Gate D: 05_CURRENT_RANGES 6-Shunt Shared Low-Side with Kelvin & BBM

- **Date:** 2026-08-25
- **Status:** SELECTED FOR SCHEMATIC (Gate D — for review)
- **Requirement(s):** REQ-MEAS-001 (10 mA→100 nA 6 ranges D canonical), REQ-MEAS-002 quantified floor, REQ-SAFE-003 safe default, REQ-DUT-001 Kelvin, REQ-SAFE-001 shared compliance shunt
- **Alternatives considered:** Series shunt stack vs shared single-shunt selector; MOSFET/PhotoMOS vs reed vs signal relay; contact inside vs outside Kelvin; NC default 10 mA vs 1 MΩ; daisy-chain GND vs star
- **Evidence examined:** `SHUNT_RANGE_TRADEOFF.md §2.4` (D canonical 25/50/100 mV → 2.5Ω/25Ω/500Ω/5k/100k/1M, power ≤250 µW, Johnson 0.51 pA @1 MΩ/10 Hz), `PHASE3_ERROR_BUDGET §2.2` (100 nA headroom +71% tight with 0.01% 10 ppm, −18% if 0.1% + max Vos), `GROUNDING_AND_RETURN_PATHS GND-05/07`, `GUARD_STRATEGY` keepout, Coto 9007 <1 pA / G6K 50 pA / AQV212 1 nA / ADG1419 500 pA leakage table, relay timing 0.5–3 ms + 5 ms BBM + 10 ms DA
- **Decision:** **06 shared low-side shunts** — 10 mA 2.49R/25 mV, 1 mA 24.9R/25 mV, 100 µA 499R/50 mV, 10 µA 4.99k/50 mV, 1 µA 100k/0.01% 10 ppm/100 mV, 100 nA 1M/0.01% 10 ppm/100 mV (NC). Kelvin taps at resistor pad (NOT relay pole) → Force contact R (50–150 mΩ) **outside** measurement (0% error, 6% headroom on 2.5Ω only). Sense via companion reed (<1 pA) per range to `ISENSE_P_K`/`ISENSE_N_K (=GND star)`. Safe default **K6/K6B NC** → de-energized spring-closed 1 MΩ between FORCE_LO–GND. BBM via one-hot shift + 5 ms break + 10 ms settle (23.5 ms seq) — hardware + firmware invariant `Σclosed≤1`, no parallel. FORCE_LO star at shunt bottom, 4 vias to plane.
- **Rationale:** D canonical preserves SNR at 100 nA (100 mV) where Johnson 0.51 pA/leakage dominate, reduces headroom/power 4× at 10 mA (25 mV vs 100 mV → 250 µW vs 1 mW). Contact inside Kelvin would inject 6% gain error on 2.5Ω uncorrectable; reed <1 pA keeps 100 nA leakage budget (<10 pA) vs PhotoMOS 1 nA reject. NC 1 MΩ defaults to least invasive / max protection.
- **Consequences:** Schematic `05_CURRENT_RANGES 0.2` wired; layout must obey 0.3 mm Kelvin diff, no vias on high-R sense, guard keepout on R5/R6 (exposed copper 0.5 mm gap, stitched plane DNP, C0G only), GND star single point, coil flyback to supply entry (GND-05). Per-range cal required; E96 nearest 2.49/24.9/499 values calibrated.
- **Verification status:** CALCULATED + SCHEMATIC WIRED — UNVERIFIED bench (continuity, contact R, leak <10 pA @1 V, BBM scope, autorange chatter).
- **Provenance:** `docs/calculations/CURRENT_RANGES_RELAY_TOPOLOGY_AUDIT.md` + TI Coto 9007 DS (<1 pA) + `PHASE3_ERROR_BUDGET` + this gate.

### DEC-034 — Phase 7 Gate F: 06_CURRENT_FRONTEND_ADC ADS1262 Re-derived Chain (PARTIALLY SUPERSEDED by DEC-042 for supply/VCM — see DEC-042)

- **Date:** 2026-08-25
- **Status:** SELECTED FOR SCHEMATIC (Gate F — for review)
- **Requirement(s):** REQ-MEAS-001/002, REQ-CAL-003 (LSB ≠ accuracy)
- **Alternatives considered:** AVDD 5/AVSS 0 vs ±2.5 bipolar; VREF 2.5 vs 5.0; PGA bypass vs 1–32; external pre-gain 100× (AD7175) vs PGA-only vs hybrid 1.56–3.13×; TVS vs BAV199 clamp; single amp vs per-range ADA4522/OPA140
- **Evidence examined:** TI ADS1262 Rev C SBAS661C Table 7-1/7-2 Eq12 Fig7-27..30: `FSR=±VREF/G` (Gain 1–32), `VREF` 0.9–5.2 V, absolute `AVSS+0.30≤AIN≤AVDD−0.30` with VCM ±G·Vdiff/2 inside same, PGAL/H ALM, bias 2 nA @G32 /1 GΩ Zin; VREF LTC6655-2.5 vs ADR4525; SHUNT D table 25/50/100 mV; OPA140 0.5 pA typ/10 pA max SBOS498F vs ADA4522 50 pA; BAV199 3 pA vs TVS 1 µA vs PAD5 0.1 pA; C0G DA <0.1% vs X7R 1%
- **Decision:** **ADS1262 PRIMARY** with AVDD 5 V/AVSS 0 V/VREF 2.5 LTC6655 LN/DVDD 3.3, gain per-range **PGA table:** 10 mA/1 mA 25 mV→PGA32 FS78.125 mV 32% 3.13× headroom; 100 µA/10 µA 50 mV→PGA32 FS78 64% 1.56×; 1 µA/100 nA 100 mV→**PGA16 FS156 64%** (PGA32 clips FS78<100). **External pre-gain NOT mandatory** (hybrid provides VCM shift + leakage isolation, optional 1.56/3.13× DNP). Chain: `ISENSE_P/N_K → R_prot 1k 0.1% → BAV199 clamp to AVDD/AVSS (3pA, NO TVS) → RC 1k+10n C0G diff 8 kHz (CM 16k) → buffer → VCM=2.5V (divider 100k/100k+1u) → 1k+1n → AIN0/1`, PGA per-range + STATUS PGAL/H check, REFP/REFN 10u+100n, AINCOM 2.5. Buffers: **ADA4522** (5 µV 50 pA) for 2.5Ω–5kΩ low-R, **OPA140 JFET** (0.5pA) for 100k/1M high-R — per-range reed mux <1 pA. RC anti-alias + RC after buffer.
- **Rationale:** With AVSS=0, direct shunt 0–100 mV violates 0.30 V PGA window → PGAL_ALM (TI E2E). VCM shift to 2.5 (mid-supply) restores headroom: 2.5±G·Vdiff/2 stays in 0.30–4.70 for all 6 shunts (max 3.3 V). ADC 2 nA bias through 1 MΩ would be 2 mV/20× FS → needs JFET buffer isolation (<10 pA audit: OPA140 0.5pA + BAV199 3pA + reed <1pA + PCB guard 2pA ≈7.5 pA typ <10 pA; max 18 pA requires guard+binned). TVS 1 µA would destroy 100 nA budget; BAV199 3 pA passes. PGA utilization 32–64% leaves 1.56–3.13× overload headroom.
- **Consequences:** Schematic `06_CURRENT_FRONTEND_ADC 0.2` wired; layout: BAV199+RC+buffers colocated, guard ring on OPA140 inputs (exposed 0.5 mm, stitched DNP), C0G only on high-Z, no vias on sense, PGAL/H firmware trap, REFP Kelvin. Alternate AD7175 DNP (needs ext 25–100×) retained. Verify VCM compliance and leak <10pA per audit.
- **Verification status:** DATASHEET RE-DERIVED + SCHEMATIC WIRED — UNVERIFIED bench (VCM window scope, pA leak open-input 100 s, noise PSD vs PGA, PGAL trigger, overload recovery <10 ms).
- **Provenance:** `docs/calculations/ADS1262_ANALOG_RANGE_DERIVATION.md` + `pga_table_calc.py` (100/50/25 ideal → 32/32/16) + TI SBAS661C Eq12 + TI blog “Riding the Rails” + OPA140 SBOS498F + BAV199 DS.

### DEC-035 — Phase 7 Gate C/E: 03_OUTPUT_STAGE LT1970A Detailed + 04_KELVIN_SENSE K1 Differential + Reed Isolation (Gates C/E)

- **Date:** 2026-08-25
- **Status:** SELECTED FOR SCHEMATIC (Gate C — 03_OUTPUT_STAGE rev0.2 + Gate E — 04_KELVIN_SENSE rev0.2, DEC-032, R5.1E)
- **Requirement(s):** REQ-SRC-001/002/005/006 (±5 V/±2 V 4-quad ±10 mA), REQ-DUT-001 Kelvin >10 GΩ, REQ-SAFE-001/003, REQ-MEAS-002/003/007, REQ-PWR-003
- **Alternatives considered:** Gate C — R_iso 33 vs 47 vs 0Ω/wire vs parallel; FILTER 220 pF fixed vs DNP/open baseline 1 nF–100 nF; VCSRC/SNK direct vs clamped; ISRC/ISNK pull-down vs pull-up; COM tied vs reference. Gate E — K1 2×OPA140+4×10k 0.1% diff vs K2 LT5400 0.01% tracking vs K3 INA AD8422/INA826/INA116 (see `docs/architecture/DEC-032_KELVIN_DIFFERENTIAL_TOPOLOGY.md`).
- **Evidence examined:** LT1970A 1970afc (p12 Vsense=Vc/10 floor 4 mV Vc<60 mV nonlinear, FILTER 1 kΩ internal 1 nF–100 nF range, TSSOP-20 EP=V−, ±12 V→±10.3 V swing, GBW 3.6 MHz SR 1.6 V/µs, ISRC/ISNK OC), OPA140 SBOS498F (Ib 0.5 pA typ/10 pA max, Vos 120 µV, 1 µV/°C, 5.1 nV, 11 MHz), LT5400 0.01% 0.2 ppm tracking, AD8422 500 pA fail, INA826 35 nA fail, R5.1 vendor LT1970.sub ±12 V OUT→R_iso→DUT→shunt low-side + differential Kelvin (transient stable PM inconclusive), R5.1E vendor+real OPA140 K1 11 benches 100 pF/1 nF +0.1/+2/−2 V CV/CC (LTspice 26.0.2.1, OPAx140.LIB, 10 MHz pole)
- **Decision:** **Gate C — LT1970A detailed (U301 TSSOP-20):** OUT→R_iso **FIT ONE ONLY** R302 47 PRIMARY + R301 33 DNP (not parallel, overlapping pads, default 47 sweet spot P3IR-02, 33 DNP loop-tune), FILTER→C301 DNP/open baseline 1 nF–100 nF footprint to SENSE− (1970afc range, prev 220 p outside → DNP), VCSRC/SNK 0–5 V via 1 kΩ + BZX84C5V1 5.1 V Zener to COM (clamped), ENABLE 47 k pull-down HW-safe default, ISRC/ISNK 10 k→+3V3 OC (R304/R305, verified Source 0.03/3.3 V, Sink opposite in R5.1), COM=GND, NC10/11/18 1 MΩ→GND, supplies VCC/V+ +12 V (100 nF+10 µF C302/C303/C304) / VEE/V− −12 V (100 nF+10 µF C305/C306), EP=V− stitched 4 vias. **Gate E — K1 PRIMARY:** SENSE_HI→K301 Coto9007 (<1 pA 1 pF) →U401A OPA140 follower (5 pF Cin, 10 GΩ) →R401/R402 10 k 0.1% →U402 OPA140 diff (R403/R404 10 k, C401 15 pF 10.6 MHz → VDIFF→LT1970 −IN); SENSE_LO same via K302→U401B; diff gain=1. **K2 provision:** U403 LT5400-3 QFN overlapping R401–404 DNP (K1 FIT/K2 DNP) for 86 dB vs 54 dB if CMRR insufficient. **K3 REJECTED.** Open-sense reed isolation: weak 10 MΩ pulls R405/R406 behind K301/K302 NO contacts → window comp U404 TLV3501 |Vdiff−Vforce|>0.5 V flags OPEN_SENSE_FLAG→SR latch (08 MCU) → reeds OPEN before OUTPUT ON, latch OFF (sticky, fallback to FORCE divider, re-arm only SENS:REM ON + OUTPUT cycle), Coff <1 pA disconnected during meas (IR-03 switched, ≥10 GΩ). Guard keepout on sense pair, TP401–403.
- **Rationale:** Gate C preserves R5.1 sweet spot (47 stable 10 pF–1 nF, 33 alt) without parallel FIT risk; FILTER DNP baseline matches 1970afc 1 n–100 n (220 p outside → DNP); Zener clamp protects Vc 0–5 V (Vc>5 destroys Vsense); pull-ups to 3V3 match MCU logic (open-collector, R5.1 proven) vs pull-down fails. Gate E Ib is gate — only K1/K2 meet ≤10 pA (INA 350 pA–35 nA fails 1 GΩ 1% →35 V error); K1 simplest single BOM (3×OPA140) with adequate CMRR 54 dB (4 mV @2 V CM, cal removes gain, prototype K2 upgrade no re-spin), R5.1E vendor+real K1 shows CV error <1.35 mV, OS 12% @2 V /37% @0.1 V damped <8 µs (44% risk preserved, slew mitigation provisioned in 02 1 k+1 n + fw ≤10 mV/µs), CC +2.57% within LT1970 2% grade, sink symmetric, no oscillation.
- **Consequences:** Schematics 03 rev0.2 + 04 rev0.2 wired per above; BOM: LT1970AIFE, OPA140×3, LT5400 DNP, Coto9007×2, TLV3501, BZX84×2; layout: overlapping R_iso pads (FIT ONE), FILTER keepout, sense pair guard, reed Coff routing, EP vias; fw: slew ramp for <0.5 V reads, latch OFF handling.
- **Verification status:** SCHEMATIC WIRED+LTSPICE VENDOR+REAL KELVIN (R5.1E 11 benches PASS CONDITIONAL, PM inconclusive encrypted macro — prototype gate remains per P3IR-05). Bench pending: 0.1 V step 10 k–1 MΩ 100 pF/1 nF prototype OS, 1 GΩ@0.5 V Ib/T-monitor, CMRR sweep, open-sense latch scope.
- **Provenance:** 1970afc + SBOS498F + LT5400 DS + AD8422/INA826 DS + `docs/architecture/DEC-032_KELVIN_DIFFERENTIAL_TOPOLOGY.md` + `simulation/results/phase3/R5P1E_GATE_E_REAL_KELVIN_RESULTS.md` + R5.1 results.


### DEC-036 — Pre-ERC LT1970A Physical Pinout Correction

- **Date:** 2026-08-25
- **Status:** ACCEPTED — SUPERSEDES embedded LT1970A symbol pin 10/11/18 NC assumption
- **Requirement(s):** REQ-SRC-001/002, REQ-SAFE-001
- **Evidence:** Analog Devices 1970afc.pdf TSSOP-20 physical pin table: 10 VEE, 11 VEE, 18 TSD, 19 V+, 20 VEE, EP21 VEE (LTspice SpiceOrder ≠ package). Previous sheet NC10/11/18 1M→GND was physical error.
- **Decision:** **LT1970A symbol rebuilt: 10/11/20/21 VEE power_in -> -12V_A (4x + EP), 18 TSD open_collector -> 10k to 3V3.** VEE pins directly tied to -12V_A with PWR_FLAG, not via 1M. TSD flagged to MCU. Never connect physical 10/11/18 as NC — project rule.
- **Verification:** DATASHEET VERIFIED — KiCad DRC pin_not_connected resolved via -12V power stubs.

### DEC-037 — Pre-ERC ADS1262 Package Correction

- **Date:** 2026-08-25
- **Status:** ACCEPTED
- **Evidence:** TI SBAS661C Rev C: ADS1262 PW = TSSOP-28 9.7×4.4 P0.65, not TQFP-32 5×5. Previous QFP footprint wrong.
- **Decision:** **ADS1262 footprint corrected to Package_SO:TSSOP-28_9.7x4.4mm_P0.65mm, value ADS1262IPW TSSOP-28 PW.** Curated symbol in lib/ReRAM-SMU-V1.kicad_sym to be rebuilt from SBAS661C pin table before final wiring.
- **Verification:** DATASHEET VERIFIED.

### DEC-038 — Pre-ERC MCU Package Resolution (Supersedes DEC-032)

- **Date:** 2026-08-25
- **Status:** SELECTED FOR SCHEMATIC — SUPERSEDES DEC-032 (G474 PRIMARY)
- **Requirement(s):** REQ-SW-001/002/004
- **Evidence:** STM32G431KBT6 LQFP32 5×5 32 pins (26 GPIOs) insufficient for 30-36 GPIO need (see PRE_ERC_MANUFACTURER_CORRECTIONS §3). G431RBT6 LQFP64 10×10 64 pins (51 GPIOs) matches 64-pin power map, same G431 family as KBT6. G474 RET6 (512KB HRTIM) was placeholder without DEC justification.
- **Decision:** **PRIMARY: STM32G431RBT6 LQFP64 10×10 P0.5** for REV-A. KBT6 LQFP32 kept as DNP alternate if pin count can be reduced later. G474 RET6 rejected for V1 — no G4 feature gap requires 512KB/HRTIM for <95KB FW. Identical HAL/CubeMX family, soft downgrade.
- **Consequences:** 08_MCU_USB_CONTROL value G474RET6 -> G431RBT6.

### DEC-039 — Pre-ERC FAST_TRIP Latch Correction

- **Date:** 2026-08-25
- **Status:** ACCEPTED
- **Evidence:** Maxim MAX16054 datasheet: IN debounced 50ms typ, only _RST undelayed. FAST_TRIP 50ms delay would allow DUT damage.
- **Decision:** **FAST_TRIP direct hardware kill: TLV3501 (4.5ns) -> diode-OR -> 74LVC1G74 D-FF async SET (ns/µs) + direct ENABLE LOW via 74LVC1G08 AND.** MAX16054 retained only for POR debounce. Latch stores fault for MCU; kill is independent of firmware and debounce-free.
- **Verification:** DATASHEET VERIFIED — timing <10µs Kill vs 50ms debounce.

### DEC-040 — Pre-ERC Kelvin CMRR Promotion (Supersedes K1 discrete PRIMARY)

- **Date:** 2026-08-25
- **Status:** ACCEPTED — PROMOTES LT5400
- **Evidence:** Discrete 4×10k 0.1%/25ppm CMRR ≈54dB -> 5V CM error 10mV >>0.5mV target; TC drift 6.25mV/50°C. LT5400 0.01%/0.2ppm -> 86dB -> 0.25mV, TC 0.05mV (see PRE_ERC §5).
- **Decision:** **LT5400A-3 matched network 0.01% 0.2ppm PROMOTED to PRIMARY for Kelvin diff.** Discrete 4×10k kept as DNP alternate overlapping LT5400 footprint (K1 FIT / LT5400 DNP swap). Rerun DC CM/ratio-TC + LTspice with vendor LT1970 before freezing.
- **Verification:** CALCULATED + SCHEMATIC PROVISIONAL — LTspice re-run pending.

### DEC-041 — Pre-ERC AD5764 Rail Margin

- **Date:** 2026-08-25
- **Status:** ACCEPTED
- **Evidence:** AD5764 Rev C: AVDD min 11.4V. ±12V ±5% gives 11.4V exactly at connector, no 50mV drop + 20mV ripple + wiring margin -> 11.23V fails at IC.
- **Decision:** **Guaranteed at IC: AVDD ≥11.8V, AVSS ≤-11.8V.** Bench supply nominal **+12.5V ±2% (12.25–12.75V)** OR **±12V ±2% + rail-valid comparator 11.6V (divider + TPS3808) holding ENABLE**. Connector drop <50mV, ripple <20mV (ferrite LC π). Absolute max 16.5V safe (<12.8V).
- **Consequences:** 01_POWER note updated; bench spec updated; rail-valid holds LT1970 ENABLE.

### DEC-042 — Pre-ERC ADS1262 Supply Topology Preference

- **Date:** 2026-08-25
- **Status:** SELECTED FOR SCHEMATIC
- **Evidence:** TI SBAS661C §7: ADS1262 supports ±2.5V bipolar analog (AVDD +2.5V, AVSS -2.5V) for ground-centered ±100mV direct measurement without VCM shift. Single-supply 5V/0V + VCM 2.5V requires 2 extra opamps, 2× Ib, extra leakage vs bipolar.
- **Decision:** **PREFER bipolar ±2.5V (AVDD +2.5V LT3045, AVSS -2.5V LT1964) for 100nA low-leakage.** Direct 0V-centered ±100mV shunt, PGA 16, no level shift. Single-supply VCM 2.5V kept as DNP alternate.
- **Verification:** DATASHEET VERIFIED — leakage audit favors bipolar (<5pA vs +2× bias).

---
*Append new decisions at the end. Never delete a decision — supersede it with a new DEC entry referencing the old one.*


### DEC-043 — Pre-ERC Gate 3 ADS1262IPW Table 6-1 Correct Pinout

- **Date:** 2026-08-25
- **Status:** ACCEPTED — SUPERSEDES previous ADS1262 symbol (AVDD 1 etc)
- **Evidence:** TI SBAS661C Table 6-1 TSSOP-28 PW: 1 AIN8 2 AIN9 3 AINCOM 4 CAPP 5 CAPN 6 AVDD 7 AVSS 8 REFOUT 9 START 10 CS 11 SCLK 12 DIN 13 DOUT/DRDY 14 DRDY 15 XTAL1/CLKIN 16 XTAL2 17 BYPASS 18 DGND 19 DVDD 20 RESET/PWDN 21 AIN0 22 AIN1 23 AIN2 24 AIN3 25 AIN4 26 AIN5 27 AIN6 28 AIN7 — no REFP/REFN, ref via AIN0-5 multifunction, mandatory CAPP-CAPN 4.7nF C0G, REFOUT 1uF+0.1uF, BYPASS 1uF, XTAL1->DGND internal.
- **Decision:** **ADS1262IPW symbol rebuilt per Table 6-1, 28 pins, correct types, C-grade not needed (TI only one grade). Allocation: AIN0=SHUNT_P, AIN1=SHUNT_N, AIN2=REFP LTC6655-2.5, AIN3=REFN GND.**
- **Verification:** PIN AUDIT PASS (28 pins), KiCad parser exit 0.

### DEC-044 — Pre-ERC Gate 3 AD5764 32-Pin TQFP Rev F & C-Grade

- **Date:** 2026-08-25
- **Status:** ACCEPTED — SUPERSEDES 20-pin placeholder and ARUZ A-grade
- **Evidence:** ADI Rev F Table 6-1: 1 SYNC 2 SCLK 3 SDIN 4 SDO 5 CLR 6 LDAC 7 D0 8 D1 9 RSTOUT 10 RSTIN 11 DGND 12 DVCC 13 AVDD 14 PGND 15 AVSS 16 ISCC 17 AGNDD 18 VOUTD 19 VOUTC 20 AGNDC 21 AGNDB 22 VOUTB 23 VOUTA 24 AGNDA 25 REFAB 26 REFCD 27 NC 28 REFGND 29 NC 30 AVSS 31 AVDD 32 BIN/2sCOMP — VOUTA-D output, not input. Grade: C-grade INL ±1LSB (CSUZ) vs A-grade ±4LSB (ARUZ) — Phase-3 ±1LSB assumption requires C-grade.
- **Decision:** **AD5764 symbol rebuilt 32-pin TQFP, VOUTA-D output, value AD5764CSUZ (was ARUZ), footprint TQFP-32 7x7 P0.8 correct.**
- **Verification:** PIN AUDIT PASS (32 pins), parser exit 0.

### DEC-045 — Pre-ERC Gate 3 Buffer Arithmetic Correction

- **Date:** 2026-08-25
- **Status:** ACCEPTED — CORRECTS 1000× unit errors in ADS1262_BUFFER_TABLE.md
- **Evidence:** OPA140 0.5pA×100k=50nV (was 50µV), 0.5pA×1M=0.5µV (was 0.5mV), 10pA×1M=10µV (was 10mV), 7.5pA×1M=7.5µV (was 7.5mV). Recalculated: 1µA 0.00005% typ (was 0.05%), 100nA 0.0005% typ (was 0.5%).
- **Decision:** **Buffer table corrected, MUC impact: 1nA MUC on 100nA FS 1% — 0.5µV/100mV=0.0005% <<1% — buffer easily meets, direct 2% would fail — buffer mandatory proven.**
- **Verification:** CALCULATED.

### DEC-046 — Pre-ERC Gate 3 BAV199 Leakage & LT5400 EP

- **Date:** 2026-08-25
- **Status:** ACCEPTED
- **Evidence:** BAV199 3pA typical at VR=25V 25°C, max nA at VR=75V — not guaranteed. LT5400A-1 MSOP-8 EP pin 9 floating per datasheet (not GND).
- **Decision:** **PRIMARY 1µA/100nA clamp AFTER OPA140 buffer (BAV199 after buffer, 3pA does not load shunt), pre-buffer BAV199 DNP/prototype with max-leak justification. LT5400 EP pin 9 floating (passive, not power_in GND).**
- **Verification:** SCHEMATIC NOTE + PIN AUDIT PASS (LT5400 9 pins, EP passive).

---

---
