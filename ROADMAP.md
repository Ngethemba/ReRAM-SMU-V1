# ReRAM-SMU V1 — Roadmap

**Version:** 0.1.0 — Phase 0  
**Date:** 2026-08-24  
**Status:** Plan — entry/exit criteria are provisional and refined each phase.

> No phase is entered until its entry criteria are met. No phase is exited until its exit criteria are verified and `STATUS.md` is updated.

---

## Phase 0 — Workspace and Tooling

**Objective:** Clean, traceable workspace that enforces engineering discipline before any design.

| Entry Criteria | Exit Criteria |
|----------------|---------------|
| Project directory exists | Directory structure created and inspected |
| No prior hardware decisions finalized | Core docs exist: README, CHARTER, REQUIREMENTS, RULES, ROADMAP, STATUS, DECISIONS, RISKS, OPEN_QUESTIONS, AGENTS, CHANGELOG |
| — | `.gitignore` + initial commit |
| — | `docs/research/WORK_LOG.md` seeded |
| — | All provisional architecture marked `PROVISIONAL / REQUIRES VERIFICATION` |
| — | No schematic, no BOM order, no third-party skill/MCP installed |

**Deliverables:** This workspace.  
**Status:** `IN PROGRESS` (this session).

---

## Phase 1 — Requirements Verification

**Objective:** Harden provisional targets into testable requirements or re-scope them.

| Entry | Exit |
|-------|------|
| Phase 0 complete | Every `PROVISIONAL` REQ has a disposition: confirmed, revised, or moved to Future |
| — | NDA/licensing for reference docs checked |
| — | Measurement uncertainty goals quantified (not just “several nA”) |
| — | Requirements traceability to charter validated |

**Key questions:** What is the *demonstrated* several-nA floor? Is ±5 V / ±10 mA still the right envelope? Is four-quadrant mandatory for V1?

---

## Phase 2 — Architecture Research

**Objective:** Choose a defensible system architecture with evidence, without committing to final component values.

| Entry | Exit |
|-------|------|
| Requirements stabilized | Architecture doc in `docs/architecture/` (block diagram, power tree, signal chain) |
| Research tooling ready | Candidate components still provisional but with datasheet citations |
| — | Compliance architecture selected (approach, not final values) |
| — | Shunt topology + range-switching technology selected |
| — | Grounding / isolation / guarding strategy drafted |
| — | Connector + layer-stack decisions drafted |
| — | LTspice vs ngspice + KiCad automation workflow decided |

**Deliverables:** `docs/architecture/ARCHITECTURE.md`, `docs/research/*`, updated `DECISIONS.md`, `OPEN_QUESTIONS.md` triaged.

---

## Phase 3 — Precision Voltage-Source Subsystem

**Objective:** Design and simulate the voltage source chain: reference → DAC → conditioning amp → output stage.

| Entry | Exit |
|-------|------|
| Architecture approved | DAC + reference + output stage simulated (DC, transient, stability) |
| Models sourced | Error budget for ±5 V / ±2 V region calculated |
| — | Headroom / dropout / thermal analysis done |
| — | Design reviewed; no PCB yet |

---

## Phase 4 — Current Measurement Subsystem

**Objective:** Design and simulate the current measurement chain: shunts → mux/relays → sense amp → ADC.

| Entry | Exit |
|-------|------|
| Phase 3 review passed | Per-range shunt + amplifier + ADC chain simulated |
| Shunt topology chosen | Noise floor vs range analyzed; autoranging hysteresis defined |
| — | Leakage / relay / PCB contamination risks quantified |
| — | ADC noise / INL impact budgeted |

---

## Phase 5 — Hardware Compliance

**Objective:** Design and simulate the hardware compliance / protection loop independent of firmware.

| Entry | Exit |
|-------|------|
| Phases 3–4 reviewed | Compliance loop simulated (trip time, overshoot, recovery) |
| — | Fault injection plan written (`docs/test/`) |
| — | Compliance verified independent of MCU |

---

## Phase 6 — Integrated Simulation

**Objective:** Co-simulate source + measure + compliance + power as a system.

| Entry | Exit |
|-------|------|
| Subsystems simulated | End-to-end I–V sweep simulated (bipolar, range transitions) |
| — | Supply / ground / coupling effects simulated where practical |
| — | Simulation review checklist passed |

---

## Phase 7 — Schematic Capture

**Objective:** Capture full schematic in KiCad with ERC clean and traceable to requirements.

| Entry | Exit |
|-------|------|
| Integrated simulation reviewed | Full schematic in `hardware/kicad/` |
| Symbol/footprint library curated | ERC 0 errors (waivers documented) |
| — | BOM in `bom/candidates/` with datasheet citations |
| — | Schematic review passed (reviewer + checklist) |

---

## Phase 8 — PCB Layout

**Objective:** Layout for precision low-current performance.

| Entry | Exit |
|-------|------|
| Schematic review passed | PCB layout complete with stack-up documented |
| Guard/ground strategy finalized | DRC 0 errors; leakage/guard review passed |
| — | Fabrication package prepared (`manufacturing/`) but not yet ordered without authorization |

---

## Phase 9 — Prototype Manufacturing

**Objective:** Fabricate and assemble the first prototype — explicitly authorized.

| Entry | Exit |
|-------|------|
| PCB + design reviews passed | Boards fabricated and assembled |
| User authorized purchase/fabrication | Assembly inspected; bring-up checklist ready |
| — | No ReRAM sample attached |

---

## Phase 10 — Board Bring-Up

**Objective:** Power the board safely for the first time on dummy loads.

| Entry | Exit |
|-------|------|
| Boards in hand | Power rails verified; output defaults to disabled |
| Lab supply current-limited | Dummy-load I–V sweeps functional |
| — | Fault/compliance/watchdog tests passed |
| — | Bring-up log complete |

---

## Phase 11 — Calibration and Verification

**Objective:** Calibrate, quantify uncertainty, and verify against requirements.

| Entry | Exit |
|-------|------|
| Bring-up passed | Calibration procedure executed; report in `measurements/calibration/` |
| Reference standards available | Uncertainty budget published |
| — | Noise floor / “several nA” claim verified or revised |
| — | Kelvin advantage demonstrated |

---

## Phase 12 — ReRAM Characterization

**Objective:** First real ReRAM measurements — only after dummy-load verification.

| Entry | Exit |
|-------|------|
| Calibration report passed | ReRAM I–V sweeps acquired with documented conditions |
| Safety checks complete | Data in `measurements/raw/` + processed analysis |
| — | First-sample results reviewed; damage report if any |

---

## Phase 13 — V1 Release

**Objective:** Publish a reproducible V1.

| Entry | Exit |
|-------|------|
| ReRAM characterization reviewed | Release package in `manufacturing/release/` (Gerbers, BOM, firmware tag, calibration report, known limitations) |
| — | `CHANGELOG.md` + `STATUS.md` marked `V1 RELEASED` |
| — | V2 scope proposed from lessons learned |

---

## Cross-Cutting Gates (apply to every phase transition)

- `STATUS.md` updated
- `DECISIONS.md` entries for any new decision
- `RISKS.md` reviewed; new risks added
- `OPEN_QUESTIONS.md` triaged
- `docs/research/WORK_LOG.md` appended
- No silent requirement promotion

---

*This roadmap is intentionally conservative. Schedule pressure never overrides Rules 11–13.*
