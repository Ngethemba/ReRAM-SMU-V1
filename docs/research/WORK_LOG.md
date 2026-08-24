# ReRAM-SMU V1 — Work Log

Append one entry per substantial agent session. Record concise, externally useful engineering rationale — not hidden chain-of-thought.

## Entry Template

```markdown
### YYYY-MM-DD HH:MM — <Objective>
- **Objective:**
- **Actions:**
- **Files changed:**
- **Evidence examined:**
- **Decisions / Outcomes:**
- **Unresolved issues:**
- **Next step:**
```

---

### 2026-08-24 16:45 — Phase 0 Workspace Initialization

- **Objective:** Create and organize the ReRAM-SMU V1 engineering workspace. No circuit design, no component ordering.
- **Actions:**
  - Created full directory hierarchy under `E:/ReRAM-SMU V1` (docs/hardware/simulation/firmware/software/bom/manufacturing/measurements/tools/archive).
  - Created 10 core docs: `README.md`, `PROJECT_CHARTER.md`, `REQUIREMENTS.md`, `ENGINEERING_RULES.md`, `ROADMAP.md`, `STATUS.md`, `DECISIONS.md`, `RISKS.md`, `OPEN_QUESTIONS.md`, `CHANGELOG.md`, `AGENTS.md` plus `.gitignore`.
  - Initialized Git repo; prepared initial commit `chore: initialize ReRAM-SMU V1 engineering workspace`.
  - Seeded `docs/research/WORK_LOG.md`, placeholder READMEs in subdirectories, and `docs/references/README.md` provenance guide.
  - Marked all candidate components (STM32G431, AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525-class) as `PROVISIONAL / REQUIRES VERIFICATION`.
  - Set phase to `Phase 0 — Workspace and tooling`; no block validated; no schematic/BOM/MCP/skill installed.
- **Files changed:** All files listed above; see Git initial commit for manifest.
- **Evidence examined:** User prompt with project purpose, V1 targets, provisional architecture, engineering philosophy, and workspace spec; charter/requirements/rules as authored this session.
- **Decisions / Outcomes:**
  - DEC-000 accepted: workspace structure and governance.
  - Requirements separated into Confirmed (27) / Provisional (8) / Future (3); see `REQUIREMENTS.md`.
  - Risk register seeded with 18 risks (R-01..R-18); open questions seeded with 20 entries (Q-01..Q-20).
- **Unresolved issues:** See `OPEN_QUESTIONS.md` Q-15/Q-16 (simulator and KiCad automation workflow) — deferred to next session (Tool/Skill/MCP Bootstrap). No design assumptions finalized.
- **Next step:** **Tool / Skill / MCP Environment Bootstrap** (next session, explicitly authorized). Do not auto-proceed.

---

### 2026-08-24 17:00–17:30 — Phase 0 Tool / Skill / MCP Environment Bootstrap

- **Objective:** Build, audit, test, document, and version-control the engineering toolchain for future ReRAM-SMU V1 development. No SMU circuit design; all candidates remain `PROVISIONAL / REQUIRES VERIFICATION`.
- **Actions:**
  - **Inventory:** Inspected Windows 11 Pro 10.0.26200, PS 5.1, Git 2.51.0, Python 3.14/3.11, uv 0.12.5, Node 22.23.2, KiCad 10.0.5 at `E:\KiCad`, LTspice 26.0.2.1, 7-Zip 26.02, ripgrep 15.2.0, VS Code 1.133.0, Hermes v0.20.5, 80 enabled skills, 0 MCPs. Found KiCad/LTspice already installed; `choco install ngspice` blocked by admin lock — extracted portable ngspice 47 from Chocolatey cache via `7z` to `tools/setup/ngspice-portable/`.
  - **Python env:** `uv venv --python 3.11 .venv` (CPython 3.11.15) with `UV_LINK_MODE=copy` (E: vs C: hardlink error 17). Installed `numpy 2.4.6, scipy 1.17.1, pandas 3.0.5, matplotlib 3.11.1, sympy 1.14.0, pint 0.25.3, uncertainties 3.2.3, pyvisa 1.16.2, pyvisa-py 0.8.1, pyserial 3.5, pytest 9.1.1, jupyter+ipykernel`. Pinned `pyproject.toml` + `requirements.txt` + `requirements-lock.txt`. Created `simulation/python/tests/test_infra.py` + `software/tests/test_software_infra.py` (6 tests PASS).
  - **SPICE:** Verified hybrid workflow (DEC-TOOL-002): ngspice primary for regression, LTspice secondary for vendor models. Smoke tests at `tools/setup/smoke-tests/spice/`: A divider 5.0 V, B RC tau 10 ms transient (423 rows), C op-amp VCVS gain 1.99996 V, LTspice `*.net` batch Operating Point — all PASS. Created wrapper `tools/scripts/run_spice.py`.
  - **KiCad:** Verified `kicad-cli 10.0.5` (`sch erc --help`, `pcb drc --help`). Smoke test cloned `E:\KiCad\share\kicad\demos\ecc83\ecc83-pp.*` → `tools/setup/smoke-tests/kicad-test/smoke.*`; ran `sch erc` → `erc.json` (37 warnings) and `pcb drc` → `drc.json` (17 warnings) — PASS, no corruption.
  - **Skills:** Searched `kicad`, `spice`, `pdf`, `datasheet`, `python`, `jupyter`; inspected `aklofas/kicad-happy/kicad` etc. Rejected Zener-coupled hub skills (mismatch); installed no hub skills. Created local `tools/skills/reram-smu-engineering/SKILL.md` (mirrored to `C:\Users\azrai\AppData\Local\hermes\skills\`) encoding datasheet-first, calculation, simulation, PCB, calibration, safe-bring-up discipline (DEC-TOOL-004).
  - **MCP:** `hermes mcp catalog` 20 available, none relevant; GitHub search `kicad mcp server` → `mixelpixx/KiCAD-MCP-Server` (1947★, MIT, Python, updated 2026-08-24). Decision DEC-TOOL-005: 0 MCP installed; KiCad MCP deferred with scope-narrowing requirement. Filesystem scope must be `E:\ReRAM-SMU V1` if ever installed.
  - **Docs:** Created `tools/setup/` 10 required files (`ENVIRONMENT_REPORT.md`, `INSTALL_LOG.md`, `TOOL_DECISIONS.md`, `SECURITY_REVIEW.md`, `SMOKE_TEST_RESULTS.md`, `PYTHON_ENVIRONMENT.md`, `KICAD_SETUP.md`, `SPICE_SETUP.md`, `HERMES_SKILLS.md`, `MCP_SETUP.md`) plus `UTILITIES_FIRMWARE_INSTRUMENT.md`, `tools/scripts/fetch_datasheet.ps1`, `check_instruments.py`, `bom/candidates/component_template.csv`, `.env.example`, and updated `.gitignore` (`.env`/`!.env.example`, `tools/setup/ngspice-portable/` ignore).
  - **Git:** `git status` verified; no secrets; no real schematic/PCB/BOM created (`hardware/kicad/` empty, `bom/approved/` empty). Prepared commit `chore: bootstrap ReRAM-SMU engineering toolchain`.
- **Files changed:** `.gitignore`, `.env.example`, `pyproject.toml`, `requirements*.txt`, `simulation/python/tests/test_infra.py`, `software/tests/test_software_infra.py`, `tools/setup/*` (10+ md), `tools/setup/smoke-tests/**/*`, `tools/scripts/*`, `tools/skills/*`, `bom/candidates/component_template.csv`, `STATUS.md`.
- **Evidence examined:** `kicad-cli --help` / `version` / `sch erc` / `pcb drc` outputs, `ngspice_con --help` / `--version` / `-b` netlists, `LTspice.exe -b` log (`Direct Newton iteration succeeded`), `hermes skills list` / `mcp catalog` / `tools list`, `winget list` + registry `HKLM Uninstall`, PyPI wheel metadata via `uv pip freeze`, `pytest -v` 6 passed, GitHub API `kicad mcp server` search (top `mixelpixx/KiCAD-MCP-Server`).
- **Decisions / Outcomes:**
  - DEC-TOOL-001 `uv` + `.venv` at `E:\ReRAM-SMU V1\.venv`
  - DEC-TOOL-002 Hybrid SPICE (ngspice primary, LTspice secondary) — resolves Q-15
  - DEC-TOOL-003 `kicad-cli` primary, Python scripting allowed, MCP deferred — addresses Q-16
  - DEC-TOOL-004 No hub skills; local `reram-smu-engineering` skill
  - DEC-TOOL-005 No MCP in Phase 0; KiCad MCP candidate deferred
- **Unresolved issues:** None blocking Phase 0; STM32 toolchain intentionally deferred until MCU selection verified (Phase 2). `jq`/`fd`/`Graphviz`/`pandoc` deferred as not needed for Phase 0 exit.
- **Next step:** Awaiting explicit authorization to enter **Phase 1 — Requirements Verification** (do not auto-start). Final inspection + commit pending in this session.
