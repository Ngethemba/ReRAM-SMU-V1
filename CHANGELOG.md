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

### Notes
- No ReRAM-SMU schematic/PCB/BOM simulated or created in this session — correct for tooling phase. All candidates remain `PROVISIONAL / REQUIRES VERIFICATION`.

---
