# ReRAM-SMU V1 — Engineering Rules

**Version:** 0.1.0 — Phase 0  
**Date:** 2026-08-24  
**Status:** BINDING from Phase 0 onward. Amend only by explicit decision in `DECISIONS.md`.

---

## 1. Core Rules (from Project Charter — Authoritative)

1. **Primary manufacturer datasheets override AI-generated claims.**
2. **Every critical component decision must have documented justification.**
3. **Important equations must be independently recalculated.**
4. **Simulation is required before PCB implementation where practical.**
5. **Simulation does not prove real-world low-current performance.**
6. **Noise, leakage, offset, drift, temperature coefficient, dielectric absorption, guarding and PCB contamination must eventually be considered.**
7. **Resolution must never be confused with accuracy.**
8. **Component nominal specifications must not be confused with system-level performance.**
9. **First hardware tests must use dummy loads and precision resistors.**
10. **A real ReRAM sample must never be the first DUT attached to a new revision.**
11. **Power-on default must be a safe output-disabled state.**
12. **No PCB should be manufactured until schematic review, ERC, simulation review and design review are complete.**
13. **No BOM should be purchased solely because an AI model suggested a component.**
14. **Design decisions must remain traceable.**

Violation of 1, 11, 12, or 13 blocks manufacturing release.

---

## 2. Datasheet & Source Rules

### 2.1 Primary Source Priority
- Manufacturer datasheet / reference manual > application note > textbook > AI summary.
- Every quantitative claim about a component (accuracy, noise, drift, INL, leakage, etc.) must cite the datasheet.

### 2.2 Provenance Format
Later datasheet-derived statements should record:

```
Manufacturer | Part number | Document title | Revision / Date | Page / Section | URL or docs/references/<file>.pdf
```

Store local copies where licensing permits under `docs/references/<manufacturer>_<part>_<rev>.pdf`.

### 2.3 No Memory Propagation
- Do not propagate specifications from AI memory.
- Re-verify every important parameter against the primary document before promotion to `bom/approved/`.
- If a datasheet contradicts an earlier AI suggestion, the datasheet wins — file a `DECISIONS.md` correction.

### 2.4 Candidate vs Approved
- `bom/candidates/` — discussed parts, provisional, unverified.
- `bom/approved/` — only after datasheet verification + decision record.
- No purchase from `candidates` without promotion.

---

## 3. Calculation Rules

- Important equations (shunt sizing, noise, error budgets, compliance thresholds, headroom, filter poles) must be **independently recalculated** and stored under `docs/calculations/`.
- Show: formula, inputs with units, intermediate steps, result, and tolerance/uncertainty.
- Use Python (or equivalent) for non-trivial math and commit the script under `simulation/python/` or `docs/calculations/*.py` so it is reproducible.
- Never copy a single AI-generated number into a schematic without recalculation.
- Distinguish: **fact** (measured/cited), **calculation** (derived), **assumption** (explicitly stated), **recommendation** (judgment).

---

## 4. Simulation Rules

- Simulation is **required** before PCB where practical (analog front-end, compliance loop, output stage, filters).
- Preferred: LTspice and/or ngspice; Python for system-level / Monte Carlo / noise budgeting.
- Store sources in `simulation/spice/` and `simulation/python/`; results/plots in `simulation/results/` with date and tool version.
- Simulation passing **does not** prove low-current / leakage / contamination / layout-dependent performance — those require physical measurement (Rule 5).
- Record: simulator, version, models used, assumptions, and what was *not* simulated.
- A simulation that has not been reviewed is not a gate.

---

## 5. PCB & Layout Rules

- No manufacturing until: **schematic review + ERC + simulation review + design review** — all checked in `STATUS.md`.
- Precision sections require explicit attention to: leakage paths, guarding, creepage, dielectric absorption, thermocouple effects, contamination (flux, moisture), relay leakage, connector leakage.
- Stack-up, ground strategy, and isolation must be decided in Phase 8 and documented in `docs/architecture/`.
- KiCad sources are authoritative; generated Gerbers are artifacts under `manufacturing/gerbers/`.
- Do not ignore DRC/ERC warnings without a written waiver in the review record.

---

## 6. Firmware Safety Rules

- Power-on and any reset → **output disabled** (hardware default, not just firmware intent). Verify with power-cycle tests.
- Watchdog enabled; hang or fault → safe state.
- Hardware compliance must be **independent** of firmware — firmware limits are supplementary.
- Firmware shall expose explicit `OUTPUT:ENABLE` / `OUTPUT:DISABLE` with interlocks; no implicit enable on boot.
- Every firmware release that touches the output path requires a bring-up checklist entry in `docs/test/`.
- SCPI-like commands that affect the output must be bounded and validated; malformed input must not enable output.

---

## 7. Calibration & Verification Rules

- V1 ships with a documented calibration procedure in `docs/calibration/` and a verification report in `measurements/calibration/`.
- Calibration references themselves must be traceable (e.g., calibrated DMM, voltage reference with cert).
- Publish an **uncertainty budget**, not just resolution/LSB claims.
- Raw measurement data is **never deleted** (`measurements/raw/` is append-only). Processing goes to `measurements/processed/`.
- Dummy-load verification is a mandatory gate before any ReRAM sample — log DUT type in every measurement file.

---

## 8. Experimental Record Rules

- Every measurement file must include: date, operator, hardware revision, firmware version, DUT description (or “dummy load”), range, compliance setting, temperature, and notes.
- Photograph or sketch wiring for non-trivial setups; store under `docs/test/` or `measurements/`.
- Failures and anomalies are recorded — not discarded. A “failed” measurement is still a record.

---

## 9. Review & Traceability Rules

- Requirements (`REQUIREMENTS.md`) → Decisions (`DECISIONS.md`) → Evidence (datasheet, calculation, simulation, measurement) must be traceable. Every decision cites its requirement(s).
- No provisional target is silently promoted — promotion needs a decision entry with evidence.
- `STATUS.md` is updated after meaningful work; it is the single dashboard.
- Unresolved issues go to `OPEN_QUESTIONS.md`; risks to `RISKS.md`.

---

## 10. Tool & Change Rules

- Do not install tools, skills, or MCP servers without documenting what was installed, why, and the version — record in `tools/setup/` and `CHANGELOG.md`.
- Do not modify unrelated system files or scatter project files outside the project root.
- Changes to these rules require a `DECISIONS.md` entry and a `CHANGELOG.md` line.

---

*These rules exist to protect the builder, the instrument, and the science it will measure.*
