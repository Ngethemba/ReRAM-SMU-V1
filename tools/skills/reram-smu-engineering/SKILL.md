---
name: reram-smu-engineering
description: Use when working on ReRAM-SMU V1 — precision SMU for ReRAM characterization. Enforces datasheet-first validation, calculation recalculation, simulation gates, uncertainty budgeting, precision PCB rules, provenance, design-review gates, and safe bring-up. Do not use for generic Python/KiCad help outside this project.
---

# ReRAM-SMU Engineering

Project-local Hermes skill for **ReRAM-SMU V1** (`E:\ReRAM-SMU V1`). Encodes `ENGINEERING_RULES.md` and `AGENTS.md` discipline without unverified component claims.

> All candidate components (STM32G431, AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525-class, etc.) remain `PROVISIONAL / REQUIRES VERIFICATION` until a `DECISIONS.md` entry with datasheet evidence promotes them. This skill never defaults to any of them.

## When to use

- Any task that touches requirements, calculations, simulation, schematic, PCB, firmware, calibration, measurements, or sourcing for ReRAM-SMU V1.
- Hermes should load this skill before answering those tasks.

## Datasheet-first workflow

1. **Manufacturer first.** Source hierarchy: manufacturer datasheet/reference manual → app note → manufacturer reference design → standard/doc → authorized distributor → secondary only if unavoidable. Never use random blogs, marketplace listings, or AI summaries as authoritative specs.
2. **Provenance tuple** for every quantitative claim:
   `Manufacturer | Part | Document title | Rev/Date | Page/Section | URL or docs/references/<manufacturer>_<part>_<rev>.pdf`
   Store local copy under `docs/references/` when licensing permits.
3. **No memory propagation.** Re-verify every critical parameter (offset, drift, INL/DNL, noise, leakage, TC, dropout, PSRR) against the primary document before promotion to `bom/approved/`. If datasheet contradicts an earlier suggestion, datasheet wins — file a `DECISIONS.md` correction.
4. **Tool:** `tools/scripts/fetch_datasheet.ps1` scaffolds download; built-in `pdf`/`ocr-and-documents`/`arxiv` skills extract text/tables. Keep source URL and revision.

## Calculation verification

- Important equations (shunt sizing, noise, error budgets, compliance thresholds, headroom, filter poles) must be **independently recalculated** and stored under `docs/calculations/` or `simulation/python/` with: formula, inputs+units, intermediate steps, result, tolerance/uncertainty.
- Commit the Python script (pinned `.venv`) — e.g. `docs/calculations/shunt_100nA.py`. Distinguish **fact** (measured/cited), **calculation** (derived), **assumption** (explicit), **recommendation** (judgment).

## Simulation gates

- Simulation required before PCB where practical (analog front-end, compliance loop, output stage, filters). Save sources in `simulation/spice/` + `simulation/python/` and results/plots in `simulation/results/` with `date + simulator + version + models + assumptions + what was NOT simulated`.
- Passing sim **does not prove** low-current/leakage/contamination/layout performance (ENGINEERING_RULES Rule 5).
- Workflow: **hybrid** — `ngspice` primary (headless `ngspice_con.exe -b` + Python wrapper `tools/scripts/run_spice.py`) for regression/CI; `LTspice` secondary for vendor-model validation. Example:
  ```powershell
  & "E:\ReRAM-SMU V1\tools\setup\ngspice-portable\Spice64\bin\ngspice_con.exe" -b simulation/spice/source_stage.cir
  ```

## Precision PCB rules (checklist before manufacturing)

- Leakage paths, guarding, creepage, dielectric absorption (prefer C0G/NP0 in signal path), thermocouple effects, contamination (flux, moisture), relay leakage, connector leakage — all considered.
- Stack-up, ground strategy (star point, analog/digital partition, compliance-loop return), isolation — decided in Phase 8 and documented in `docs/architecture/`.
- No PCB fabricated until **schematic review + ERC + simulation review + design review** pass (check `STATUS.md`).

## Calibration & measurement

- Raw data under `measurements/raw/` is **append-only** — never deleted. Processed → `measurements/processed/`, calibration → `measurements/calibration/`.
- First hardware tests on **dummy loads / precision resistors** only. No ReRAM sample is the first DUT on a new revision.
- Publish **uncertainty budget**, not just resolution/LSB. Traceability via calibrated DMM/voltage reference with cert.

## Firmware safety invariant

- **Output disabled is the safe state.** Every firmware path that touches the output must default to disabled on power-on, brown-out, reset, watchdog timeout, or fault. Verify with power-cycle tests and bring-up checklist in `docs/test/`.

## Traceability & housekeeping

- Path: `Requirements (REQUIREMENTS.md REQ-*) → Decisions (DECISIONS.md) → Evidence (datasheet/calculation/sim/measurement)`.
- Never silently promote `PROVISIONAL` — needs `DECISIONS.md` entry with evidence.
- After meaningful work: update `STATUS.md`, append `docs/research/WORK_LOG.md`, triage `OPEN_QUESTIONS.md` / `RISKS.md`.

## Safe file locations

- KiCad sources: `hardware/kicad/`; symbols `hardware/symbols/`; footprints `hardware/footprints/`
- Python: `.venv/` (gitignored), `pyproject.toml` + `requirements.txt` + `requirements-lock.txt` are the contract
- SPICE: `simulation/spice/`, `simulation/results/`
- Firmware: `firmware/src/` + `include/` + `tests/`
- Software: `software/`
- Sourcing: `bom/candidates/` (provisional) → `bom/approved/` (datasheet-verified only)

## What this skill does NOT do

- Does not invent component specs or encode AD5686R/LT1970A/etc. as mandatory.
- Does not duplicate `AGENTS.md` or `ENGINEERING_RULES.md` — references them.
- Does not hide chain-of-thought as rationale — only concise, externally useful reasoning is recorded.
