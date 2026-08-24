# ReRAM-SMU V1 — Status Dashboard

**Single source of truth for quick project status. Updated after meaningful work.**

---

## Current Phase

> **Phase 0 — Workspace and Tooling** · `IN PROGRESS`

No circuit block validated. All candidate architecture is `PROVISIONAL / REQUIRES VERIFICATION`.

---

## At a Glance

| Item | State |
|------|-------|
| Workspace structure | ✅ Created — inspected this session |
| Core documentation | ✅ 10 files created |
| Git repository | ✅ Initialized — initial commit on this session |
| Simulation environment | ⬜ Not started (next session: Tool/Skill/MCP Bootstrap) |
| Requirements verification | ⬜ Awaiting Phase 1 |
| Schematic / PCB | ⬜ Not started — intentionally blocked |
| Prototype hardware | ⬜ Not manufactured |
| Calibration / Verification | ⬜ Not started |

---

## Completed Work

- [2026-08-24] Workspace structure created under `E:/ReRAM-SMU V1` (see `README.md` for layout).
- [2026-08-24] Core docs created: `README.md`, `PROJECT_CHARTER.md`, `REQUIREMENTS.md`, `ENGINEERING_RULES.md`, `ROADMAP.md`, `STATUS.md`, `DECISIONS.md`, `RISKS.md`, `OPEN_QUESTIONS.md`, `CHANGELOG.md`, `AGENTS.md`, `.gitignore`, `docs/research/WORK_LOG.md`.
- [2026-08-24] Git initialized; initial commit `chore: initialize ReRAM-SMU V1 engineering workspace`.

---

## Active Work

- Phase 0 close-out inspection (this session).

---

## Blocked Work

- None — Phase 0 is unblocked.

---

## Next Actions

1. **Tool / Skill / MCP Environment Bootstrap** (next session — do not auto-start).
   - Decide LTspice vs ngspice workflow, KiCad automation approach, Python environment, and required skills/MCPs.
   - Document in `tools/setup/` and `DECISIONS.md` once chosen.

2. Enter **Phase 1 — Requirements Verification** once tooling is ready.

---

## Latest Validation State

| Gate | Result | Evidence |
|------|--------|----------|
| Schematic review | ⬜ Not applicable | No schematic exists (correct for Phase 0) |
| ERC | ⬜ Not applicable | — |
| Simulation review | ⬜ Not applicable | — |
| Design review | ⬜ Not applicable | — |
| Power-on safe state | ⬜ Not tested | No hardware |
| Dummy-load verification | ⬜ Not tested | — |
| Calibration | ⬜ Not performed | — |

---

## Change Log Pointer

Detailed history: [`CHANGELOG.md`](CHANGELOG.md)  
Work log: [`docs/research/WORK_LOG.md`](docs/research/WORK_LOG.md)

---

*Last updated: 2026-08-24 — Phase 0. Next update after Tool/Skill/MCP Bootstrap.*
