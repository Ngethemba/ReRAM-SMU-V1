# ReRAM-SMU V1 — Precision Source Measure Unit

**Homemade precision SMU for low-voltage ReRAM / memristive device characterization and precision-electronics education.**

> ⚠️ **Project Stage: Phase 0 — Workspace and Tooling**
> No schematic, no PCB, no BOM has been validated. All architecture is provisional and requires verification. This is an engineering instrument project, not a hobby circuit.

## What This Is

ReRAM-SMU V1 is a four-quadrant Source Measure Unit (SMU) targeting:

- Bipolar voltage source approx. **±5 V** (primary ReRAM region ±2 V), **±10 mA** sink/source
- Low-current measurement down to **several nA** (V1 useful floor), with six current ranges 100 nA – 10 mA
- Kelvin (4-wire) DUT interface: FORCE HI / SENSE HI / SENSE LO / FORCE LO
- Hardware current compliance, USB + SCPI-like control, Python-automated I–V sweeps

It is simultaneously an **educational platform** covering precision analog, DAC/ADC systems, four-quadrant operation, low-current design, compliance, Kelvin sensing, firmware, calibration, PCB layout, and automated characterization.

## Current Status

- **Phase:** `Phase 0 — Workspace and Tooling`
- **Dashboard:** [`STATUS.md`](STATUS.md)
- **Requirements:** [`REQUIREMENTS.md`](REQUIREMENTS.md) — confirmed / provisional / future separated
- **Risks & Decisions:** [`RISKS.md`](RISKS.md) · [`DECISIONS.md`](DECISIONS.md)
- **Open Questions:** [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)
- **Work Log:** [`docs/research/WORK_LOG.md`](docs/research/WORK_LOG.md)

No block is marked validated. All candidate components are `PROVISIONAL / REQUIRES VERIFICATION`.

## Repository Layout

```
ReRAM-SMU-V1/
├── README.md / PROJECT_CHARTER.md / REQUIREMENTS.md / ENGINEERING_RULES.md
├── ROADMAP.md / STATUS.md / DECISIONS.md / RISKS.md / OPEN_QUESTIONS.md / CHANGELOG.md / AGENTS.md
├── docs/            — architecture, research, calculations, calibration, safety, test, references
├── hardware/        — KiCad sources, symbols, footprints, mechanical, prototypes
├── simulation/      — SPICE, Python, results
├── firmware/        — MCU source, headers, tests, docs
├── software/        — instrument-control, gui, analysis, tests
├── bom/             — candidates / approved / sourcing
├── manufacturing/   — gerbers, assembly, release
├── measurements/    — raw / processed / calibration  (raw data is never deleted)
├── tools/           — scripts, setup
└── archive/         — superseded material
```

## Safety Statement

- **V1 has NO direct 230 V mains on the SMU PCB.** Development uses an external lab supply (nominal ±12 V analog rails).
- **Output defaults to DISABLED** on power-on, firmware reset, and fault. Never assume the output is safe.
- **First tests use dummy loads and precision resistors** — never a real ReRAM sample on a new revision.
- Prototype hardware must be tested with **current-limited bench supplies**.
- Exposed conductors and incorrect Kelvin wiring can damage the DUT, the SMU, and test equipment.
- Future higher-voltage revisions require a separate safety review — see [`docs/safety/`](docs/safety/).

## Engineering Philosophy (summary)

Primary datasheets override AI claims. Every critical decision needs documented justification and independent recalculation. Simulation is required before PCB but does not prove low-current performance. Resolution ≠ accuracy. Traceability is mandatory.

Full rules: [`ENGINEERING_RULES.md`](ENGINEERING_RULES.md) · Charter: [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md)

## For AI Agents

Read `AGENTS.md` and the five mandatory files (`PROJECT_CHARTER.md`, `REQUIREMENTS.md`, `STATUS.md`, `DECISIONS.md`, `ENGINEERING_RULES.md`) before any engineering work. Never invent specs; cite primary datasheets.

## License / Provenance

All datasheet-derived statements must record manufacturer, part number, document title/revision, page/section, and source URL or local path under `docs/references/`.

---
*Initialized 2026-08-24 — Phase 0. No hardware has been designed or ordered.*
