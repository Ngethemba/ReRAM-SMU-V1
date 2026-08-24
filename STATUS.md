# ReRAM-SMU V1 — Status Dashboard

**Single source of truth for quick project status. Updated after meaningful work.**

---

## Current Phase

> **Phase 3 — CONDITIONAL / PROTOTYPE GATE REQUIRED (corrective review R1–R6)** · `simulation/results/phase3/PHASE3_RESULTS.md` (historical 15/15 behavioral PASS) + `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (R1 PASS, R2 PASS, R3 PASS, R4 PASS, R5 CONDITIONAL, R6 PASS) · Corrective record `docs/research/PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md` (P3IR-01..08: 4 confirmed, 3 partial, 1 model limitation)

Phase 3 + corrective review executed tests A-O plus 6 corrective gates R1–R6 (ngspice-47 + Python 3.11.15). Historical behavioral 15/15 PASS retained; corrective review reconciles Rsense topology (shared canonical 2.5Ω–1MΩ, not fixed 10Ω), C_down ≤80–150pF, ADS1262 primary (AD7175 needs external gain), AD5764 @5V ref + LTC6655-5.0, behavioral 6.5% transient (16.2% analytic historical), reed relay <1pA (ADG1419 100pA fails), 1GΩ envelope split. No schematic/PCB/BOM/hardware created — Phase 4 schematic may proceed **with provisions** (see DEC-028/029/030), final LT1970 vendor-model + prototype required (R5).

---

## At a Glance

| Item | State |
|------|-------|
| Workspace structure | ✅ Created |
| Core documentation | ✅ 10 core + Phase 1 research + Phase 2 architecture |
| Git repository | ✅ `414120f` + `Phase 3` `PHASE3_RESULTS` + `PHASE3_ERROR_BUDGET` + `MODEL_LIMITATIONS` (pushed) |
| Simulation environment | ✅ ngspice-47 + LTspice 26.0.2.1 hybrid — 15/15 tests PASS (116 sim files, 251-pt POR, 2977-row energy) |
| Python scientific env | ✅ `.venv` 3.11.15 — 6 tests PASS + error/burden calcs |
| KiCad | ✅ 10.0.5 — ERC/DRC smoke PASS |
| Architecture | ✅ `ARCHITECTURE.md` (7.8 KB) — low-side hybrid shunts outside SENSE, SENSE feedback at DUT, dual compliance |
| Current measurement | ✅ Hybrid shunt 10 mA→1 µA + TIA provision for 100 nA (DEC-015) |
| Source stage | ✅ LT1970A primary + discrete alternate (DEC-014) |
| Compliance | ✅ Dual continuous+trip/SOA, per-segment/polarity (DEC-018) |
| Kelvin | ✅ SENSE feedback at DUT, open-sense fallback (DEC-019) |
| Grounding | ✅ Single plane partitioned, single bridge (DEC-020) |
| Guard/Isolation/Connector/Power | ✅ Provisioned (DEC-022/021, GUARD 2.7 KB, POWER_TREE, ISOLATION) |
| Requirements verification | ✅ v0.2.0 (31 confirmed) + traceability |
| Schematic / PCB | ⬜ Not started — intentionally blocked (hardware/kicad empty) |
| Prototype hardware | ⬜ Not manufactured |
| Calibration / Verification | ⬜ Frameworks exist — measurement pending |

---

## Completed Work

- [2026-08-24] Workspace + tooling (as before).
- [2026-08-24] Phase 1 complete (RERAM, LOW_CURRENT, ARCH survey, COMPLIANCE, COMMERCIAL, PHASE1 summary, traceability, frameworks).
- [2026-08-24] **Phase 2 — Architecture & Candidate Component Verification COMPLETE (6 agents):**
  - Source: `SOURCE_STAGE_CANDIDATES.md` (55 KB, LT1970A vs OPA140/ADA4522+buffer vs OPA548, CAUTION 1/2 resolved)
  - Measurement: `MEASUREMENT_FRONTEND_CANDIDATES.md` (21 KB) + `SHUNT_RANGE_TRADEOFF.md` (15 KB, R 10Ω–1 MΩ, Johnson, gain) + `KELVIN_SENSE_ARCHITECTURE.md` (7.4 KB, low-side outside SENSE, open-sense pull-up)
  - Compliance: `COMPLIANCE_ARCHITECTURE.md` (48 KB, Option D dual) + `COMPLIANCE_ENERGY_ANALYSIS.md` (27 KB, 10 nF@5 V 125 nJ, 100 nF cable 1.25 µJ, ≤10 nF +10 Ω)
  - Precision: `PRELIMINARY_ERROR_BUDGET.md` (28 KB, GUM, post-cal AD5686R -11% @1 V vs AD5764 +8.8%) + `SOURCE_STAGE_CANDIDATES.md` appendix for DAC/ADC/ref/amp adversarial
  - Grounding: `GROUNDING_AND_RETURN_PATHS.md` (36 KB, single plane partitioned) + `ISOLATION_STRATEGY.md` (23 KB, optional footprint) + `GUARD_STRATEGY.md` (2.7 KB, reserved copper, SENSE_HI guard) + `POWER_TREE.md` + `SOURCE_HEADROOM_THERMAL.md` (70–170 mW vs DUT 50 mW, ΔT 6–15 °C)
  - Sourcing: `PHASE2_COMPONENT_MATRIX.md` (32 KB, lifecycle active for LT1970A/AD5686R/ADA4522/ADS1262/LT1763/ADR4525/STM32G431, AD5764/LTC6655/REF50xx/OPA140 alternates, SPICE models)
  - Synthesis: `ARCHITECTURE.md` (block diagram low-side hybrid, SENSE feedback, dual compliance) + `PHASE2_DECISION_MATRIX.md` (20 decisions) + `PHASE2_RESEARCH_SUMMARY.md` + `PHASE3_SIMULATION_PLAN.md` (source transfer, 4-quad, compliance decades, stability, per-range, Monte Carlo, temp) + DEC-013..023 + OPEN_QUESTIONS Q-01/02/03/05/06/12/18/20 partially resolved
  - **No schematic/PCB/BOM simulated or created — correct for Phase 2.**

---

## Active Work

- None — Phase 2 deliverables complete; awaiting authorization for Phase 3.

---

## Blocked Work

- None — Phase 2 exit criteria 1–25 satisfied (all architecture/component classes evaluated, Cautions 1–5 addressed). Phase 3 ready on authorization.

---

## Next Actions

1. **Phase 3 — Source, Compliance & Stability Simulation** (requires explicit authorization — DO NOT auto-start):
   - Simulate source transfer ±5 V/±2 V, 4-quad sink, compliance load steps/filament, stability with 10 pF–10 nF DUT + cable, per-range measurement, Monte Carlo, temp.

2. Phase 4 — Current Measurement Subsystem after source/compliance sim review.

---

## Latest Validation State

| Gate | Result | Evidence |
|------|--------|----------|
| Schematic review | ⬜ Not applicable | No schematic (correct) |
| ERC / DRC | ✅ PASS (smoke) | tools/setup/smoke-tests/kicad-test/erc.json (37 warn) / drc.json (17 warn) |
| Simulation review | ⬜ Planned | simulation/PHASE3_SIMULATION_PLAN.md |
| Architecture review | ✅ PASS | docs/architecture/ARCHITECTURE.md + DEC-013..023 |
| Requirements traceability | ✅ PASS | docs/architecture/REQUIREMENTS_TRACEABILITY.md |
| Research synthesis | ✅ PASS | docs/research/PHASE2_RESEARCH_SUMMARY.md |
| Design review | ⬜ Not applicable | No design |
| Power-on safe state | ⬜ Concept | DEC-018/020 safe pull-down + supervisor |
| Dummy-load verification | ⬜ Not tested | — |
| Calibration | ⬜ Framework exists | docs/calculations/UNCERTAINTY_BUDGET_FRAMEWORK.md + PRELIMINARY_ERROR_BUDGET.md |

---

## Change Log Pointer

Detailed history: [`CHANGELOG.md`](CHANGELOG.md)  
Work log: [`docs/research/WORK_LOG.md`](docs/research/WORK_LOG.md)

---

*Last updated: 2026-08-24 18:30 — Phase 2 complete, Phase 3 ready. No hardware designed or ordered.*
