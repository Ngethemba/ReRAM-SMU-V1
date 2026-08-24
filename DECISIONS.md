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

---

*Append new decisions at the end. Never delete a decision — supersede it with a new DEC entry referencing the old one.*
