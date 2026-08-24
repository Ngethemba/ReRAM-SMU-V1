# ReRAM-SMU V1 — Status Dashboard

**Single source of truth for quick project status. Updated after meaningful work.**

---

## Current Phase

> **Phase 0 — Workspace and Tooling** · `TOOLING COMPLETE — Phase 1 ready (awaiting authorization)`

No circuit block validated. All candidate architecture remains `PROVISIONAL / REQUIRES VERIFICATION`. No schematic/PCB/BOM has been created in this phase (correct).

---

## At a Glance

| Item | State |
|------|-------|
| Workspace structure | ✅ Created — inspected |
| Core documentation | ✅ 10 files created |
| Git repository | ✅ Initialized — `d5a6100` + pending `chore: bootstrap ReRAM-SMU engineering toolchain` |
| Simulation environment | ✅ ngspice 47 (portable) + LTspice 26.0.2.1 — smoke 3 netlists PASS |
| Python scientific env | ✅ `.venv` 3.11.15, numpy 2.4.6 / scipy 1.17.1 / pytest 9.1.1 — 6 tests PASS |
| KiCad | ✅ 10.0.5 at `E:\KiCad`, CLI 10.0.5, ERC/DRC smoke PASS (erc.json/drc.json) |
| KiCad automation | ✅ `kicad-cli` primary; MCP evaluated + DEFERRED (DEC-TOOL-003/005) |
| SPICE workflow | ✅ Hybrid: ngspice primary / LTspice secondary (DEC-TOOL-002) |
| Hermes skills | ✅ 80 enabled + local `reram-smu-engineering`; no hub skill installed (DEC-TOOL-004) |
| MCP servers | ✅ 0 installed is correct; KiCad MCP candidate deferred + security reviewed |
| Instrument-control env | ✅ pyvisa/pyserial, graceful without hardware |
| Requirements verification | ⬜ Awaiting Phase 1 (Phase 0 exit satisfied — ready) |
| Schematic / PCB | ⬜ Not started — intentionally blocked (hardware/kicad empty, correct) |
| Prototype hardware | ⬜ Not manufactured |
| Calibration / Verification | ⬜ Not started |

---

## Completed Work

- [2026-08-24] Workspace structure created under `E:/ReRAM-SMU V1` (see `README.md` for layout).
- [2026-08-24] Core docs created: `README.md`, `PROJECT_CHARTER.md`, `REQUIREMENTS.md`, `ENGINEERING_RULES.md`, `ROADMAP.md`, `STATUS.md`, `DECISIONS.md`, `RISKS.md`, `OPEN_QUESTIONS.md`, `CHANGELOG.md`, `AGENTS.md`, `.gitignore`, `docs/research/WORK_LOG.md`.
- [2026-08-24] Git initialized; initial commit `chore: initialize ReRAM-SMU V1 engineering workspace`.
- [2026-08-24] **Tool/Skill/MCP Bootstrap — COMPLETE:**
  - Python `.venv` (uv, 3.11.15, `pyproject.toml` + `requirements.txt` + `requirements-lock.txt`, 6 pytest PASS)
  - KiCad 10.0.5 verified (`kicad-cli sch erc` + `pcb drc` on disposable `tools/setup/smoke-tests/kicad-test/smoke.*` → erc.json/drc.json)
  - SPICE hybrid: ngspice-47 portable (`ngspice_con.exe -b` divider 5.0 V, RC tau, op-amp gain 1.99996 V) + LTspice 26.0.2.1 batch divider Operating Point
  - LTspice vs ngspice decision (DEC-TOOL-002 hybrid), KiCad automation decision (DEC-TOOL-003 CLI primary), skill decision (DEC-TOOL-004 local skill), MCP decision (DEC-TOOL-005 defer)
  - Project-local skill `reram-smu-engineering` created (`tools/skills/reram-smu-engineering/SKILL.md` + Hermes local mirror)
  - Scripts: `tools/scripts/run_spice.py`, `fetch_datasheet.ps1`, `check_instruments.py`; template `bom/candidates/component_template.csv`
  - Security review + smoke-test results + environment/install logs under `tools/setup/` (10+ docs)
  - `.gitignore` hardened (`.env`/`.env.*`/`!.env.example`, `tools/setup/ngspice-portable/`, portable cache ignored; `.env.example` added)
  - **No ReRAM-SMU schematic/PCB/BOM/hardware design performed — correct for tooling session.**

---

## Active Work

- None — tooling deliverables complete; awaiting authorization to enter Phase 1.

---

## Blocked Work

- None — Phase 0 exit criteria satisfied. Phase 1 (Requirements Verification) is ready to begin on explicit authorization.

---

## Next Actions

1. **Phase 1 — Requirements Verification** (requires explicit authorization — DO NOT auto-start):
   - Harden every `PROVISIONAL` REQ (e.g., Q-07/Q-08 several-nA floor, ±5 V/±10 mA envelope) into confirmed/revised/future with evidence.
   - Quantify uncertainty goals; review charter traceability.
2. **Phase 2 — Architecture Research** after requirements are stabilized (compliance, shunt topology, grounding, etc.).

---

## Latest Validation State

| Gate | Result | Evidence |
|------|--------|----------|
| Schematic review | ⬜ Not applicable | No schematic exists (correct for Phase 0) |
| ERC | ✅ PASS (smoke disposable) | `tools/setup/smoke-tests/kicad-test/erc.json` (37 warnings, 0 fatal; valid JSON) |
| Simulation review | ✅ PASS (smoke) | ngspice 3 tests + LTspice batch in `tools/setup/smoke-tests/spice/` |
| DRC | ✅ PASS (smoke disposable) | `tools/setup/smoke-tests/kicad-test/drc.json` (17 warnings) |
| Design review | ⬜ Not applicable | No design |
| Power-on safe state | ⬜ Not tested | No hardware |
| Dummy-load verification | ⬜ Not tested | — |
| Calibration | ⬜ Not performed | — |

---

## Change Log Pointer

Detailed history: [`CHANGELOG.md`](CHANGELOG.md)  
Work log: [`docs/research/WORK_LOG.md`](docs/research/WORK_LOG.md)

---

*Last updated: 2026-08-24 17:30 — Phase 0 tooling complete; Phase 1 ready. No hardware designed or ordered.*
