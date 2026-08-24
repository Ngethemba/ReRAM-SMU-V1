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

### Notes
- No ReRAM-SMU schematic/PCB/BOM simulated or created in this session — correct for research phase. All candidates remain `PROVISIONAL / REQUIRES VERIFICATION`.

---
