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

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-DUT-001, REQ-SRC-001/002
- **Alternatives considered:** Source regulates FORCE vs SENSE; burden inside vs outside loop.
- **Evidence examined:** `KELVIN_SENSE_ARCHITECTURE.md` (7.4 KB, SENSE differential >10 GΩ, 5 VFS, open-sense pull-up + comparator fallback to FORCE, lead R ≤1 MΩ limit, bias current).
- **Decision:** **Source regulates SENSE at DUT; burden outside loop.** Open SENSE_HI/LO detected via pull-up (100 kΩ to FORCE) + comparator → fallback to FORCE mode + fault flag.
- **Rationale:** Kelvin correctness: V_DUT = V_SENSE, not V_FORCE – V_burden; fallback prevents oscillation on open sense.
- **Verification status:** UNVERIFIED — open-sense test + 2-wire vs 4-wire on 10 Ω dummy.
- **Provenance:** CAUTION 4 (Kelvin not tied to 10 kΩ threshold).

### DEC-020 — Grounding Philosophy

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-PWR-004, REQ-MEAS-002/008
- **Alternatives considered:** Single continuous plane partitioned vs split AGND/DGND vs star vs isolated analog domain.
- **Evidence examined:** `GROUNDING_AND_RETURN_PATHS.md` (36 KB, return paths: DAC ref, ADC ref, MCU, relay, USB, FORCE_LO).
- **Decision:** **Single continuous ground/reference plane with physical partitioning + single AGND/DGND bridge + partitioned current claims** (not generic star). CAUTION 5 explicitly not pre-decided as split/star.
- **Rationale:** Return-path analysis > “star best”; split invites antenna; isolated domain adds DC/DC noise.
- **Verification status:** UNVERIFIED — noise PSD with/without USB + partitioning review (Phase 8).
- **Provenance:** CAUTION 5.

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

- **Date:** 2026-08-24
- **Status:** ACCEPTED (provision)
- **Requirement(s):** REQ-MEAS-002/006, REQ-DUT-002/003
- **Alternatives considered:** Reserved copper+stitching vs active driven guard now vs triax now.
- **Evidence examined:** `GUARD_STRATEGY.md` (reserved copper, stitching, optional driven guard amp on SENSE_HI buffer — not arbitrary node) + `LOW_CURRENT_MEASUREMENT.md` §4.
- **Decision:** **V1 provision:** guard ring copper (exposed, no mask, stitched inner guard plane) encircling high-Z nodes (100 nA shunt/sense) + optional driven guard amplifier footprint tied to SENSE_HI buffer, shield tied to FORCE_LO via 1 MΩ||10 nF. Triax is V2.
- **Rationale:** V1 does not claim electrometer but must leave upgrade path without re-spin.
- **Verification status:** UNVERIFIED — visual + leakage <10 pA.
- **Provenance:** CAUTION 4 + low-current guard checklist.

### DEC-023 — Component Adversarial Verdicts (Phase 2)

- **Date:** 2026-08-24
- **Status:** ACCEPTED (K/C/R/A/D)
- **Requirement(s):** REQ-GEN-002, lifecycle/sourcing
- **Alternatives considered:** Previously suggested AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525, STM32G431 vs new candidates.
- **Evidence examined:** `PHASE2_COMPONENT_MATRIX.md` (32 KB, 10+ web_search batches, datasheets rev F/G/K, DigiKey/Mouser stock, SPICE model column) + `PRELIMINARY_ERROR_BUDGET.md` (post-cal U 805 µV @2 V for AD5686R vs 638 µV @2 V for AD5764).
- **Decision:** Verdicts: **AD5686R — KEEP AS ALTERNATE** (±2 LSB INL, post-cal @1 V -11% headroom vs target 700 µV); **ADA4522-2 — KEEP** (zero-drift, but role-dependent vs OPA140/ADA4528); **LT1970A — KEEP (primary)** (active, 1% limiter, LTspice model); **ADS1262 — KEEP AS ALTERNATE** (vs AD7175 preferred for 50 Hz rejection/noise-free bits); **LT1763 — KEEP** (active, LDO) but LT3045 for precision rail as alternate; **ADR4525 — KEEP** but LTC6655/REF50xx deferred branch; **STM32G431 — KEEP AS ALTERNATE** (meets SPI/USB/GPIO/watchdog but G474/RP2040 alternates lower cost).
- **Rationale:** Would not have blindly preserved AI history — independent DSP shows AD5764-class beats AD5686R on INL, etc.
- **Verification status:** UNVERIFIED — simulation gates before `bom/approved/`.
- **Provenance:** Manufacturer datasheets (AD5686R Rev F, LT1970A 1970afc, OPA140 Rev F, etc.) + counterfeit policy (precision parts authorized distributors only).

---

### Candidate Architecture — Explicitly NOT Decisions (remaining after Phase 2 selections)

The following remain `PROVISIONAL / REQUIRES VERIFICATION` and must not be treated as decisions beyond the SELECTED FOR PHASE 3 gates above. Final values require simulation:

| Candidate | Notes | Required Evidence Before Promotion |
|-----------|-------|--------------------------------------|
| DAC AD5686R quad 16-bit | KEEP AS ALTERNATE pending AD5764 sim | AD5764 vs AD5686R error-budget sim + DMM |
| DAC AD5764 ±10 V 16-bit | PREFERRED for Phase 3 sim (±1 LSB INL) | Same |
| Amp ADA4522-2 zero-drift | KEEP role-dependent (shunt sense) | Noise/TC sim + bench |
| Power amp LT1970A | KEEP primary (500 mA, 1% limiter) | Load regulation + cap stability sim |
| ADC ADS1262 / AD7175 | Both CANDIDATE (noise @NPLC) | NPLC sweep sim vs measured noise |
| Regulator LT1763 / LT3045 | Both CANDIDATE per rail | Dropout/PSRR sim |
| Reference ADR4525 / LTC6655 | Shared vs separate branch | Drift/correlation sim |
| Shunts + relay matrix | Hybrid 10 mA→1 µA + TIA provision | Leakage/TC + burden headroom sim |
| MCU STM32G431 family | KEEP AS ALTERNATE (G474/RP2040 alternates) | SPI/USB/timer check |

No FINAL promotion until Phase 3 simulation gates pass. Specs must not be propagated from memory.

---

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
| DEC-017 | Burden-voltage philosophy (range-dependent) | SELECTED FOR PHASE 3 | 2026-08-24 |
| DEC-018 | Compliance architecture (dual) | SELECTED FOR PHASE 3 | 2026-08-24 |
| DEC-019 | Kelvin sense loop (SENSE feedback) | ACCEPTED | 2026-08-24 |
| DEC-020 | Grounding (single plane partitioned) | ACCEPTED | 2026-08-24 |
| DEC-021 | Isolation (optional) | ACCEPTED | 2026-08-24 |
| DEC-022 | Guard provision | ACCEPTED | 2026-08-24 |
| DEC-023 | Component adversarial verdicts | ACCEPTED | 2026-08-24 |

---

*Append new decisions at the end. Never delete a decision — supersede it with a new DEC entry referencing the old one.*
