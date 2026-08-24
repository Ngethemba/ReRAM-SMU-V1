# ReRAM-SMU V1 — Project Charter

**Version:** 0.1.0 — Phase 0  
**Date:** 2026-08-24  
**Status:** PROVISIONAL — requires verification in Phase 1  
**Author:** Project initialization (Hermes Agent)

---

## 1. Purpose

ReRAM-SMU V1 is a **homemade precision Source Measure Unit** designed primarily for **low-voltage electrical characterization of ReRAM / memristive devices** and other experimental electronic / material samples.

It serves a dual purpose:

1. **Scientific instrument** — to perform controlled, repeatable bipolar I–V sweeps, compliance-limited sourcing, and low-current measurement for ReRAM research.
2. **Educational precision-electronics platform** — to teach and document precision analog electronics, DAC/ADC systems, four-quadrant sourcing, low-current measurement, hardware compliance, Kelvin sensing, instrumentation firmware, SCPI-style control, calibration/verification, precision PCB layout, and automated data acquisition.

The project is explicitly an **engineering instrument build**, not a hobby circuit assembled from unverified suggestions.

## 2. Scope

### In scope (V1)

- Bipolar, four-quadrant voltage sourcing with sink/source capability
- Precision current measurement across multiple ranges (V1 floor: several nA)
- Hardware and software current compliance / protection
- Kelvin (4-wire) DUT interface (FORCE HI/SENSE HI/SENSE LO/FORCE LO)
- USB computer control, SCPI-like command set, Python automation, CSV/raw export
- Autoranging, bipolar sweeps, temperature/fault monitoring, watchdog handling
- Safe power-on (output disabled), enable/disable control
- Calibration and verification procedures with traceable records
- Simulation before PCB; schematic/ERC/design reviews before manufacturing
- First-light testing on dummy loads and precision resistors only

### Out of scope (V1) — see Future

- Triaxial connectors, driven guard, electrometer front-end (pA and below)
- Direct 230 V mains circuitry on the SMU PCB
- Production certification (CE/UL), medical or safety-critical use
- Guaranteed electrometer-class performance

## 3. Non-Goals

- Replacing a commercial Keithley / Keysight SMU in absolute performance.
- Providing a “quick hobby SMU” without engineering rigor.
- Optimizing for cost or size at the expense of measurement integrity.
- Publishing a BOM or PCB based solely on AI-generated component suggestions.
- Connecting an unverified revision directly to a valuable ReRAM sample.

## 4. Engineering Philosophy

The twelve project rules (authoritative in `ENGINEERING_RULES.md`):

1. Primary manufacturer datasheets override AI claims.
2. Every critical component decision must have documented justification.
3. Important equations must be independently recalculated.
4. Simulation is required before PCB where practical.
5. Simulation does not prove real-world low-current performance.
6. Noise, leakage, offset, drift, TC, dielectric absorption, guarding, contamination must eventually be considered.
7. Resolution ≠ accuracy.
8. Nominal specs ≠ system performance.
9. First tests use dummy loads / precision resistors.
10. No real ReRAM sample is the first DUT on a new revision.
11. Power-on default is safe output-disabled.
12. No PCB manufactured until schematic/ERC/simulation/design reviews pass.
13. No BOM purchased solely because an AI suggested a component.
14. Design decisions remain traceable.

Supporting rules on datasheet citation, calculation, simulation, PCB review, firmware safety, calibration, and experimental records are defined in `ENGINEERING_RULES.md`.

## 5. Intended Users

- The project owner as primary researcher / builder.
- Future students, collaborators, or open-hardware contributors who want a documented, reproducible precision SMU platform.
- AI agents (Hermes and successors) working under `AGENTS.md` constraints — treated as junior engineers requiring supervision and datasheet grounding.

Not intended for unsupervised replication without reading safety and calibration documentation.

## 6. Success Criteria (V1)

V1 is successful when **all** of the following are demonstrated and documented:

| # | Criterion | Verification |
|---|-----------|--------------|
| S-01 | Bipolar source ±5 V (usable ±2 V ReRAM region) with four-quadrant operation at ±10 mA | Measured into resistive loads, documented in `measurements/` |
| S-02 | Six current ranges (10 mA down to 100 nA) functional with autoranging | Range-switching tests, shunt + relay characterization |
| S-03 | Useful measurement floor of several nA with documented noise and uncertainty | Noise-floor measurement, calibration report |
| S-04 | Hardware compliance trips reliably; software limits enforced; output disabled on reset/fault | Fault-injection tests |
| S-05 | Kelvin 4-wire measurement functional and demonstrably better than 2-wire on low-impedance DUT | Comparative measurement report |
| S-06 | USB + SCPI-like + Python sweep automation with CSV export | Software integration tests |
| S-07 | Safe power-on (output disabled) verified in every firmware build | Power-cycle test log |
| S-08 | Calibration procedure documented, performed, with uncertainty budget | `docs/calibration/` report |
| S-09 | First-light validated on dummy loads before any ReRAM sample | Bring-up log |
| S-10 | Full design traceability: requirements → decisions → simulation → schematic → PCB → test | Review checklists complete |

Performance numbers remain **provisional targets** until Phase 11 verification.

## 7. Long-Term Direction

```
V1  — Core SMU: ±5 V, ±10 mA, several-nA floor, Kelvin, compliance, USB/SCPI/Python
         (this document)
V1.x — Refinements: improved noise, tighter calibration, isolation/grounding lessons

V2  — Low-current extension: 10 nA range, guarding, triax option, tighter leakage control

V3  — Electrometer class: pA range, driven guard, electrometer front-end,
      possibly separate low-current head
```

Each revision requires its own requirements review and safety review; higher voltages or mains integration would trigger a new charter section.

## 8. Governance

- Requirements authority: `REQUIREMENTS.md` (REQ-* identifiers). Provisional targets must not be silently promoted.
- Decision authority: `DECISIONS.md` — no finalized decision without evidence.
- Risk authority: `RISKS.md` — reviewed each phase.
- Status authority: `STATUS.md` — single dashboard.
- Changes to charter require an entry in `CHANGELOG.md` and `DECISIONS.md`.

---

*This charter is a living document. It is binding from Phase 0 onward and is amended only by explicit decision.*
