# ReRAM-SMU V1 — Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning: `0.y.z` pre-release (no hardware), `1.y.z` after V1 release.

---

## [0.1.0] — 2026-08-24

### Added
- Initial engineering workspace structure (`README.md`, `PROJECT_CHARTER.md`, `REQUIREMENTS.md`, `ENGINEERING_RULES.md`, `ROADMAP.md`, `STATUS.md`, `DECISIONS.md`, `RISKS.md`, `OPEN_QUESTIONS.md`, `AGENTS.md`, `CHANGELOG.md`, `.gitignore`, `docs/research/WORK_LOG.md`).
- Full directory hierarchy: `docs/`, `hardware/`, `simulation/`, `firmware/`, `software/`, `bom/`, `manufacturing/`, `measurements/`, `tools/`, `archive/`.
- Git repository initialized; initial commit `chore: initialize ReRAM-SMU V1 engineering workspace`.
- Phase 0 — Workspace and tooling. All candidate components marked `PROVISIONAL / REQUIRES VERIFICATION`.

### Notes
- No schematic, no PCB, no BOM, no third-party skill/MCP, no component order. Intentional.
- Next action: Tool / Skill / MCP Environment Bootstrap (separate session).

---

## [Unreleased]

### Added
- Toolchain bootstrap: `.venv` (uv, Python 3.11.15, pinned `pyproject.toml`/`requirements.txt`/`requirements-lock.txt`, 6 pytest tests PASS).
- KiCad 10.0.5 verified (`kicad-cli sch erc` + `pcb drc` smoke on disposable `tools/setup/smoke-tests/kicad-test/` → `erc.json`/`drc.json`).
- SPICE hybrid workflow (DEC-TOOL-002): ngspice 47 portable (`ngspice_con -b` 3 netlists PASS) + LTspice 26.0.2.1 batch (`Direct Newton succeeded`); wrappers `tools/scripts/run_spice.py`.
- Project-local Hermes skill `reram-smu-engineering` (`tools/skills/` + Hermes local mirror); no hub skill installed (DEC-TOOL-004); KiCad MCP candidate evaluated + deferred (DEC-TOOL-005) with security review.
- Tooling docs under `tools/setup/` (ENVIRONMENT_REPORT, INSTALL_LOG, TOOL_DECISIONS, SECURITY_REVIEW, SMOKE_TEST_RESULTS, PYTHON_ENVIRONMENT, KICAD_SETUP, SPICE_SETUP, HERMES_SKILLS, MCP_SETUP, UTILITIES_FIRMWARE_INSTRUMENT) + scripts (`fetch_datasheet.ps1`, `check_instruments.py`) + `bom/candidates/component_template.csv`.
- `.gitignore` hardened (`.env`/`!.env.example`, `tools/setup/ngspice-portable/`); `.env.example` added.
- `STATUS.md` marked Phase 0 tooling complete (Phase 1 ready).
- **Phase 1 research (4 parallel agents):** `RERAM_MEASUREMENT_REQUIREMENTS.md` (31 KB, 8 workflows, Vset 0.6–1.5 V, Icc 10 µA–1 mA), `LOW_CURRENT_MEASUREMENT.md` (29 KB, Johnson 0.41 pA @100 nA/10 Hz, guard), `SMU_ARCHITECTURE_SURVEY.md` (26 KB, Arch A–D), `COMPLIANCE_RESEARCH.md` (21 KB, triad regulation vs trip), `COMMERCIAL_SMU_BENCHMARK.md` (30 KB, Keithley 2450 vs 2400/2600B vs Keysight B2900 vs NI PXIe vs Yokogawa), `PHASE1_RESEARCH_SUMMARY.md` synthesis, `REQUIREMENTS_TRACEABILITY.md`, calculation frameworks `NOISE_BUDGET_FRAMEWORK.md` + `BURDEN_VOLTAGE_ANALYSIS.md` (100 mV FS shunt 10 Ω–1 MΩ, TIA ~20 µV) + `UNCERTAINTY_BUDGET_FRAMEWORK.md` (GUM RSS k=2).
- REQUIREMENTS.md v0.1.0→v0.2.0: promoted REQ-SRC-005 (4-quad), REQ-MEAS-001 (6 ranges), REQ-MEAS-002 quantified (detection 3σ 1.5–6 pA, practical MUC 1 nA), added REQ-MEAS-007/008 accuracy research targets, compliance triad/Kelvin/guard/sweep enriched, traceability cited.
- DECISIONS.md: DEC-007 (4-quad mandatory), DEC-008 (6 ranges), DEC-009 (MUC quantified), DEC-010 (voltage provisional-verified), DEC-011 (compliance <50 µs/<5 µs), DEC-012 (sweep/Kelvin/guard); OPEN_QUESTIONS Q-04/07/08/11/15/16 resolved; STATUS Phase 1 COMPLETE.
- **Phase 2 architecture (6 agents):** `ARCHITECTURE.md` (low-side hybrid shunts outside SENSE, SENSE feedback at DUT, dual compliance, 4-quad sink), `SOURCE_STAGE_CANDIDATES.md` (55 KB LT1970A primary + discrete alternate, CAUTION 1/2), `MEASUREMENT_FRONTEND_CANDIDATES.md` (21 KB) + `SHUNT_RANGE_TRADEOFF.md` (15 KB, range-dependent 100→50→25 mV) + `KELVIN_SENSE_ARCHITECTURE.md` (7.4 KB), `COMPLIANCE_ARCHITECTURE.md` (48 KB Option D) + `COMPLIANCE_ENERGY_ANALYSIS.md` (27 KB, 10 nF@5 V 125 nJ), `PRELIMINARY_ERROR_BUDGET.md` (28 KB, AD5764 preferred, GUM), `PHASE2_COMPONENT_MATRIX.md` (32 KB, lifecycle active), `GROUNDING_AND_RETURN_PATHS.md` (36 KB single plane), `ISOLATION_STRATEGY.md` (23 KB optional), `GUARD_STRATEGY.md` (2.7 KB), `POWER_TREE.md` + `SOURCE_HEADROOM_THERMAL.md` (70–170 mW vs 50 mW DUT), `PHASE2_DECISION_MATRIX.md` + `PHASE2_RESEARCH_SUMMARY.md` + `PHASE3_SIMULATION_PLAN.md` + DEC-013..023 + OPEN_QUESTIONS Q-01/02/03/05/06/12/18/20 partially resolved; STATUS Phase 2 COMPLETE.


## [Unreleased] — Phase 2 Corrective Review (IR-01..IR-16) — 2026-08-24

### Corrected
- Independent review IR-01..IR-16 verified against primary datasheets (LT1970A 1970afc 4mV floor, AD5764 RevF 20V span LSB 305.2uV ±11.4V, TLV3501 RevE 6.5mV) and Python recomputations; documented in docs/research/PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md (67 KB).
- REQ-SAFE-001 revised per DEC-024: tiered compliance minimum (LT1970A 4% FS at 100mV, 16% at 25mV, 0.1% only via range coercion or Candidate C); REQ-DUT-001 buffer-first (>10GΩ, ≤10pA) and switched open-sense (≥10GΩ or disconnected); REQ-PWR-003/004 Options A/B/C and one-continuous-plane wording (IR-13).
- DECISIONS.md: DEC-019/020/022 wording corrected; DEC-023 corrected (AD5764 LSB/supply); new DEC-024 (compliance coercion) and DEC-025 (Source Candidate C outer+LT1970A booster).
- ARCHITECTURE.md: block diagram and §3 corrected (range-dependent 25/50/100mV canonical, TLV3501 supervisor, Candidate C, grounding no-split, power options).
- PHASE2_DECISION_MATRIX.md: burden, stored-energy (C_UP/DOWN), DAC, amps, ADC bipolar, Kelvin equation, grounding, power, and new row 21 Candidate C corrected.
- GUARD_STRATEGY.md: taxonomy passive/grounded/driven + corrected powering (from rails, not SENSE_HI via 1GΩ).
- POWER_TREE.md: Options A/B/C, AD5764 ±11.4V incompatibility, LT1763 positive-only / negative LT1964-class.
- KELVIN_SENSE_ARCHITECTURE.md: high-Z buffer first, V_FORCE equation canonical, switched open-sense, DUT-node C budget, filter after buffer.
- GROUNDING_AND_RETURN_PATHS.md: one continuous plane wording (IR-13).
- SHUNT_RANGE_TRADEOFF.md: declared canonical §2.4 (IR-05); reversed ordering rejected; BURDEN_VOLTAGE_ANALYSIS marked superseded.
- PRELIMINARY_ERROR_BUDGET.md: AD5764 LSB 305.2uV (no ±5V mode), INL headroom corrected, divider after buffer, TLV3501 not in compliance.
- COMPLIANCE_ENERGY_ANALYSIS.md: C_UPSTREAM/C_DOWNSTREAM distinction (IR-14).
- COMPLIANCE_ARCHITECTURE.md: LT1970A floor/coercion (IR-01), TLV3501 supervisor tolerance (IR-08), C_UP/DOWN (IR-14), switched open-sense (IR-03).
- SOURCE_STAGE_CANDIDATES.md: LT1970A floor table, new §2.6 Candidate C (IR-15), canonical equation (IR-11), DAC LSB/supply.
- MEASUREMENT_FRONTEND_CANDIDATES.md: burden canonical, TIA settling qualified (IR-09), bipolar A/B/C (IR-12).
- simulation/PHASE3_SIMULATION_PLAN.md: expanded from 43 lines to canonical tests A-O (IR-16).
- OPEN_QUESTIONS.md (Q-01/02/03/05/10/11) and REQUIREMENTS_TRACEABILITY updated; STATUS marked PHASE 2 — CORRECTED / READY FOR PHASE 3.
- No schematic/PCB/BOM created; no component order.


## [Unreleased] — Phase 3 Corrective Review (P3IR-01..08 / R1–R6) — 2026-08-24

### Corrected
- Independent review P3IR-01..08 verified against primary datasheets (LT1970A 1970afc floor 4mV/linear 60mV, ADG1419 100pA typ, OPA140 10pA max, ADS1262 PGA 32 vs AD7175 NO PGA, AD5764 REF 5V spec) and Python/traceability audit; documented in `docs/research/PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md` (57KB) and `simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md` (R1–R6).
- P3IR-01 CONFIRMED: fixed 10Ω Rsense fails <600µA — corrected to **shared canonical shunt 2.5Ω–1MΩ as LT1970 Rsense (C1)** for V1 REV-A (50–100µA PASS Vc 250–500mV); separate bank footprint reserved. Current path LT1970 OUT→R_iso 33–47Ω→DUT→selected shunt→GND with SENSE+→FORCE_LO node. Gate R1 PASS.
- P3IR-02 CONFIRMED reversed: 1000/1047=95.5% is **dumped** to DUT not isolated — corrected C_DOWNSTREAM ≤80pF@5V/500pF@2V vs C_UPSTREAM shared dump ≤1nF@5V (not free), Cf 33pF not counted. Gate R2 PASS.
- P3IR-03 CONFIRMED: AD7175-8 HAS NO analog PGA (only buffers/mux/digital register) — corrected to **ADS1262 PRIMARY (internal PGA 1–32 + 3.13× pre-gain)** vs AD7175 ALTERNATE with external 100/50/25× per-range diff amp footprint. Gate R3 PASS.
- P3IR-04 PARTIALLY: AD5764 LSB 305µV at REF 5V guaranteed is DAC-A half-codes (3.0% @10mV); corrected reference to **LTC6655-5.0/ADR435B 5V** (not LN-2.5) for spec-guaranteed ±1LSB; DAC-B 2.5V full-span characterized not primary. Gate R4 PASS.
- P3IR-05 MODEL LIMITATION: `candidate_A_transient.cir` is behavioral not vendor macro — **6.5% transient OS @10nF traceable**, 16.2% analytic historical superseded; vendor LTspice `LT1970A.lib` not run in this env — classified **CONDITIONAL / REQUIRES PROTOTYPE** (Gate R5).
- P3IR-06 CONFIRMED: ADG1419 typ 100pA (500pA max 25°C, 75nA 85°C) fails 10pA budget — corrected to **reed relay <1pA (Coto 9007 class) SELECT** for open-sense disconnect. Gate R6 PASS.
- P3IR-07 PARTIALLY: OPA140 envelope split — **Guaranteed ≤100MΩ (<1%), Characterized 1GΩ@0.5–1V (<2% raw → <0.5% cal), Exploratory 1GΩ@0.1V** — OPA140 remains SELECT, electrometer deferred.
- P3IR-08 PARTIALLY: grep audit — 6.5% verified transient, 16.2% historical, 95.5% prose fixed, ADG1419 10pA corrected, nC/µC no hit; all master numbers now machine-traceable.
- `docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md`: status CONDITIONAL with provisions, DAC ref 5V, ADS1262 primary, OPA140 regions, R_iso/C_up/C_down budget.
- `simulation/phase3/MODEL_LIMITATIONS.md`: downgraded LT1970A to BEHAVIORAL SIMULATED — VENDOR-MODEL PENDING, added §6 R1–R6 table.
- `DECISIONS.md`: new DEC-026 amended (source), DEC-027 amended (DAC/ADC swap), DEC-028 (shared Rsense), DEC-029 (reed), DEC-030 (1GΩ regions), DEC-031 (overall CONDITIONAL).
- `STATUS.md`: Phase 3 marked **CONDITIONAL / PROTOTYPE GATE REQUIRED** (R1–R4,R6 PASS, R5 CONDITIONAL); no schematic/PCB/BOM.

### Notes
- No schematic/PCB/BOM/hardware — corrective review only, next Phase 4 schematic provision on authorization.

## [Unreleased] — Phase 3 Simulation (Tests A-O) — 2026-08-24

### Added
- simulation/phase3/ 11 subdirs (common, source_A/B/C, compliance, kelvin, measurement, leakage, range_switch, fault, dac_adc, monte_carlo) + simulation/results/phase3/ 6 gate summaries (116+ sim files, 251-pt POR, 2977-row energy transients rc=0).
- Tests A-O per corrected plan: A LT1970A floor 4mV/4% FS coercion, B coercion 6/6 PASS, C Kelvin 160/160 V_FORCE equation, D open-sense latch OFF 0.5nA, E JFET buffer <1%@1GΩ, F C_DOWN budget 80pF@5V, G bipolar B midscale+PGA32, H trip MC 150/130/120%, I energy 61× cap underest, J R_iso 33-47Ω tradeoff, K safe seq 23.5ms, L POR 200ms supervisor, M leakage 1pA Good PASS, N AD5764 SELECT 20V 305µV half codes, O Candidate A SELECT 50°/6.5% B fallback 60°/3.2% C prototype 57°→16.6%.
- docs/calculations/PHASE3_ERROR_BUDGET.md (29KB Type A/B k=2, Johnson+en/in+ADC+leakage, NPLC FAST 10-20ms/NORMAL 50-100ms/LOW 200ms-1s).
- simulation/phase3/MODEL_LIMITATIONS.md (15KB per-gate table, LT1970A/ADA4522/OPA140/AD5686R/5764/ADR4525/LTC6655/ADS1262/AD7175/reed, what models vs bench).
- simulation/results/phase3/PHASE3_RESULTS.md (15/15 PASS, summary table Candidate/DAC/ADC, failed/inconclusive, model limitations).
- docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md (SELECT A LT1970A, FALLBACK B, REQUIRES PROTOTYPE C; DAC AD5764, ADC AD7175/ADS1262).
- docs/research/PHASE3_RESEARCH_SUMMARY.md (gates 1-6 quantitative).

### Notes
- No KiCad schematic/PCB/BOM/hardware — Phase 3 simulation only, next Phase 4 on authorization.

### Notes
- No ReRAM-SMU schematic/PCB/BOM simulated or created in this session — correct for architecture phase. All candidates `PROVISIONAL / REQUIRES VERIFICATION` until simulation.

---
