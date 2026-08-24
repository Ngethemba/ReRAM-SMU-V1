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

---

### Candidate Architecture — Explicitly NOT Decisions

The following have been **discussed** but are **not decided**. They remain `PROVISIONAL / REQUIRES VERIFICATION` and must not be treated as decisions:

| Candidate | Notes | Required Evidence Before Promotion |
|-----------|-------|--------------------------------------|
| MCU STM32G431 family | Needs clock, ADC/DAC, USB, package review | Reference manual + datasheet, errata |
| DAC AD5686R quad 16-bit | Output range, INL, reference, SPI timing | AD5686R datasheet rev |
| Amp ADA4522-2 zero-drift | Offset, drift, noise, supply range | ADA4522-2 datasheet |
| Power amp LT1970A | Bipolar, current, thermal, stability | LT1970A datasheet |
| ADC ADS1262 precision | Noise, INL, reference, SPI | ADS1262 datasheet |
| Regulator LT1763 | Dropout, noise, PSRR | LT1763 datasheet |
| Reference ADR4525-class | Drift, accuracy, load | ADR4525 datasheet |
| Shunts + relay range switching | Leakage, TC, contact resistance | Shunt + relay datasheets + leakage analysis |

No DEC entry will be created for these until Phase 2 evidence exists. Specs must not be propagated from memory.

---

## Decision Index

| ID | Subject | Status | Date |
|----|---------|--------|------|
| DEC-000 | Workspace structure and governance | ACCEPTED | 2026-08-24 |
| — | (next decision) | — | — |

---

*Append new decisions at the end. Never delete a decision — supersede it with a new DEC entry referencing the old one.*
