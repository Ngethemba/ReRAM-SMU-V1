# ReRAM-SMU V1 — Requirements

**Version:** 0.1.0 — Phase 0  
**Date:** 2026-08-24  
**Status:** PROVISIONAL / REQUIRES VERIFICATION where marked. Confirmed requirements are binding.  
**Convention:** `REQ-<DOMAIN>-<NNN>` · Domains: SRC, MEAS, SAFE, DUT, SW, PWR, CAL, GEN

> **Rule:** Never silently convert a provisional target or future item into a confirmed requirement. Promotion requires a `DECISIONS.md` entry with evidence.

---

## How to Read This Document

- **Confirmed** — binding for V1 unless formally changed.
- **Provisional Target** — current engineering aim, subject to verification in Phase 1/2. Marked `PROVISIONAL`.
- **Future / V2+** — explicitly not V1; recorded to avoid scope creep.

Each requirement lists an ID, statement, rationale, verification method, and status.

---

## 1. Source Capability — `REQ-SRC-*`

### REQ-SRC-001 — Bipolar Voltage Source Range (PROVISIONAL)
**Statement:** Nominal voltage source approximately **−5 V to +5 V**.  
**Rationale:** Covers ReRAM operating window with headroom for forming/sweep overhead.  
**Verification:** Measure sourcing into resistive + capacitive loads across range; record in `measurements/`.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-SRC-002 — Primary ReRAM Operating Region (PROVISIONAL)
**Statement:** Primary region approximately **−2 V to +2 V** must be well within linear, low-noise operating envelope.  
**Rationale:** Most ReRAM SET/RESET occurs in this window; best accuracy needed here.  
**Verification:** Linearity and noise characterization in ±2 V window.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-SRC-003 — Bipolar Operation (Confirmed)
**Statement:** System shall source and measure both positive and negative voltages and currents.  
**Rationale:** ReRAM bipolar switching; four-quadrant I–V required.  
**Verification:** Bipolar sweep test.  
**Status:** `CONFIRMED`

### REQ-SRC-004 — Source and Sink Capability (Confirmed)
**Statement:** Output stage shall source and sink current (active load).  
**Rationale:** Memristor can drive current back; SMU must absorb.  
**Verification:** Load-step and quadrant test.  
**Status:** `CONFIRMED`

### REQ-SRC-005 — Four-Quadrant Architecture (PROVISIONAL, Preferred)
**Statement:** Architecture should be four-quadrant (source + sink, both polarities) — preferred, not yet mandatory.  
**Rationale:** Simplifies bipolar characterization; avoids quadrant-switching artifacts.  
**Verification:** Architecture study in Phase 2; simulation of quadrant transitions.  
**Status:** `PROVISIONAL — PREFERRED / REQUIRES VERIFICATION`

### REQ-SRC-006 — Maximum DUT Current (PROVISIONAL)
**Statement:** Target maximum DUT current approximately **±10 mA**.  
**Rationale:** ReRAM forming/compliance often 100 µA–1 mA; 10 mA provides margin.  
**Verification:** Current-drive test into low-impedance load with compliance active.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-SRC-007 — Output Enable / Disable (Confirmed)
**Statement:** Firmware and hardware shall provide explicit output enable/disable with safe default.  
**Verification:** Power-cycle and fault tests (see REQ-SAFE).  
**Status:** `CONFIRMED`

---

## 2. Measurement Capability — `REQ-MEAS-*`

### REQ-MEAS-001 — Current Ranges (PROVISIONAL)
**Statement:** Initial target current ranges: **10 mA, 1 mA, 100 µA, 10 µA, 1 µA, 100 nA**.  
**Rationale:** Logarithmic coverage from high forming currents to low HRS leakage.  
**Verification:** Shunt + amplifier + ADC chain analysis; per-range calibration.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-MEAS-002 — V1 Lower Measurement Region (PROVISIONAL)
**Statement:** Target V1 useful lower region: **several nA** (i.e., meaningful measurement above noise floor, not just LSB).  
**Rationale:** Balances V1 ambition with realistic PCB/leakage limits without guard/electrometer.  
**Verification:** Noise-floor and repeatability measurement per `docs/test/`.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-MEAS-003 — Voltage Measurement (Confirmed, extent provisional)
**Statement:** System shall measure DUT voltage (Force and Sense) with accuracy adequate for I–V characterization. Exact accuracy TBD after architecture study.  
**Verification:** Comparison against calibrated DMM / voltage reference.  
**Status:** `CONFIRMED (existence) / PROVISIONAL (numbers)`

### REQ-MEAS-004 — Autoranging (Confirmed)
**Statement:** System shall support autoranging across current ranges with documented hysteresis/dwell to avoid chatter.  
**Verification:** Automated sweep crossing range boundaries.  
**Status:** `CONFIRMED`

### REQ-MEAS-005 — Resolution ≠ Accuracy (Confirmed, informational)
**Statement:** Documentation and software shall never conflate ADC/DAC resolution with system accuracy; both shall be reported separately.  
**Verification:** Review of docs + software display.  
**Status:** `CONFIRMED`

### REQ-MEAS-006 — Future Low-Current Extension (Future / V2)
**Statement:** Future revisions may target 10 nA, pA, and electrometer-class measurements. Not required for V1.  
**Status:** `FUTURE / NOT V1`

---

## 3. Protection and Control — `REQ-SAFE-*`

### REQ-SAFE-001 — Hardware Current Compliance (Confirmed)
**Statement:** A **hardware** current compliance / protection loop shall limit DUT current independent of firmware.  
**Verification:** Fault injection: short + step load; scope compliance response.  
**Status:** `CONFIRMED`

### REQ-SAFE-002 — Software Current Limits (Confirmed)
**Statement:** Firmware/software shall enforce configurable current limits in addition to hardware compliance.  
**Verification:** Software limit trip test.  
**Status:** `CONFIRMED`

### REQ-SAFE-003 — Safe Power-On State (Confirmed)
**Statement:** On power-on, brown-out, firmware reset, or watchdog reset, output shall default to **disabled / high-impedance safe state**.  
**Verification:** Power-cycle + reset tests with output monitored.  
**Status:** `CONFIRMED`

### REQ-SAFE-004 — Output Disabled on Firmware Failure (Confirmed)
**Statement:** Firmware fault, hang, or watchdog timeout shall disable output.  
**Verification:** Watchdog timeout test.  
**Status:** `CONFIRMED`

### REQ-SAFE-005 — Bipolar I–V Sweeps (Confirmed)
**Statement:** System shall execute bipolar I–V sweeps (programmed voltage steps, measured current).  
**Verification:** Sweep automation test.  
**Status:** `CONFIRMED`

### REQ-SAFE-006 — Temperature Monitoring (Confirmed)
**Statement:** System shall monitor temperature of critical subsections (e.g., output stage, shunts, reference). Exact sensor count TBD.  
**Verification:** Thermal test + over-temperature response.  
**Status:** `CONFIRMED`

### REQ-SAFE-007 — Fault Monitoring (Confirmed)
**Statement:** System shall detect and report faults (over-current, over-temperature, compliance active, supply faults).  
**Verification:** Fault-injection matrix.  
**Status:** `CONFIRMED`

### REQ-SAFE-008 — Watchdog / Error Handling (Confirmed)
**Statement:** Firmware shall include watchdog and structured error handling that forces safe state on failure.  
**Verification:** Watchdog + error-path tests.  
**Status:** `CONFIRMED`

---

## 4. DUT Interface — `REQ-DUT-*`

### REQ-DUT-001 — Kelvin / 4-Wire Support (Confirmed)
**Statement:** DUT interface shall support **FORCE HI, SENSE HI, SENSE LO, FORCE LO** and support Kelvin/4-wire measurement.  
**Verification:** 2-wire vs 4-wire comparison on low-impedance DUT; sense-lead open detection.  
**Status:** `CONFIRMED`

### REQ-DUT-002 — Connector Strategy (Provisional)
**Statement:** V1 connector type TBD (banana, BNC, terminal block, or Kelvin clip). Must support shielded/leakage-conscious wiring path for future guard.  
**Verification:** Architecture decision in Phase 2.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-DUT-003 — Triax / Driven Guard / Electrometer Front-End (Future)
**Statement:** Triax connectors, driven guard, and electrometer front-end are **future revisions**, not V1.  
**Status:** `FUTURE / NOT V1`

---

## 5. Computer Interface — `REQ-SW-*`

### REQ-SW-001 — USB Interface (Confirmed)
**Statement:** Instrument shall be computer-controlled via **USB**.  
**Verification:** USB enumeration + command round-trip.  
**Status:** `CONFIRMED`

### REQ-SW-002 — SCPI-like Command Interface (Confirmed)
**Statement:** Firmware shall expose an **SCPI-like** command interface (subset, documented). Full SCPI compliance not required.  
**Verification:** Command-set tests against spec in `docs/`.  
**Status:** `CONFIRMED`

### REQ-SW-003 — Python Control (Confirmed)
**Statement:** A **Python** control library/client shall drive the instrument (sweeps, config, readout).  
**Verification:** Python integration tests.  
**Status:** `CONFIRMED`

### REQ-SW-004 — Automated Sweep Execution (Confirmed)
**Statement:** Software shall support automated sweep execution (configurable start/stop/step/delay, bidirectional).  
**Verification:** Sweep test with logged data.  
**Status:** `CONFIRMED`

### REQ-SW-005 — Data Export (Confirmed)
**Statement:** Software shall export data as **CSV and raw data** with metadata (timestamp, range, compliance, temperature).  
**Verification:** Export format test; raw data preservation check.  
**Status:** `CONFIRMED`

---

## 6. Power Architecture — `REQ-PWR-*`

### REQ-PWR-001 — No Direct Mains on SMU PCB (Confirmed)
**Statement:** V1 SMU PCB shall have **no direct 230 V mains circuitry**.  
**Rationale:** Safety and isolation; avoids mains design review scope.  
**Verification:** Schematic/PCB review checklist.  
**Status:** `CONFIRMED`

### REQ-PWR-002 — External Lab Supply for Development (Confirmed)
**Statement:** Development and bring-up shall use an **external laboratory supply**.  
**Verification:** Bring-up procedure.  
**Status:** `CONFIRMED`

### REQ-PWR-003 — Nominal Analog Rails (PROVISIONAL)
**Statement:** Nominal analog rails approximately **±12 V**, subject to output-stage headroom analysis.  
**Verification:** Headroom + dropout analysis (regulators, LT1970A or alternative).  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION`

### REQ-PWR-004 — Analog / Digital Supply Treatment (Confirmed, extent provisional)
**Statement:** Design shall provide **separate analog/digital supply treatment** as needed (regulation, filtering, star-point, isolation TBD).  
**Verification:** Power architecture review + noise measurement.  
**Status:** `CONFIRMED (principle) / PROVISIONAL (implementation)`

---

## 7. Calibration & Quality — `REQ-CAL-*`

### REQ-CAL-001 — Calibration Procedure (Confirmed)
**Statement:** V1 shall have a documented calibration procedure with traceability.  
**Verification:** `docs/calibration/` + calibration report.  
**Status:** `CONFIRMED`

### REQ-CAL-002 — Verification on Dummy Loads First (Confirmed)
**Statement:** First hardware tests shall use **dummy loads and precision resistors**; no ReRAM sample as first DUT.  
**Verification:** Bring-up log.  
**Status:** `CONFIRMED`

### REQ-CAL-003 — uncertainty Budget (Confirmed)
**Statement:** V1 shall publish a measurement uncertainty discussion (not just resolution).  
**Verification:** Calibration/verification report.  
**Status:** `CONFIRMED`

---

## 8. General / Process — `REQ-GEN-*`

### REQ-GEN-001 — Simulation Before PCB (Confirmed)
**Statement:** Simulation is required before PCB implementation where practical.  
**Verification:** Simulation results in `simulation/results/`.  
**Status:** `CONFIRMED`

### REQ-GEN-002 — Reviews Before Manufacturing (Confirmed)
**Statement:** No PCB manufactured until schematic review, ERC, simulation review, and design review are complete.  
**Verification:** Review checklists in `docs/`.  
**Status:** `CONFIRMED`

### REQ-GEN-003 — Traceability (Confirmed)
**Statement:** Design decisions remain traceable (requirements → decisions → evidence).  
**Verification:** `DECISIONS.md` coverage check.  
**Status:** `CONFIRMED`

---

## Summary Counts

| Category | Confirmed | Provisional | Future |
|----------|:---------:|:-----------:|:------:|
| SRC      | 2 | 4 | 0 |
| MEAS     | 3 | 2 | 1 |
| SAFE     | 8 | 0 | 0 |
| DUT      | 1 | 1 | 1 |
| SW       | 5 | 0 | 0 |
| PWR      | 2 | 1(+1 partial) | 0 |
| CAL/GEN  | 6 | 0 | 0 |

**Total confirmed V1 requirements:** 27 · **Provisional targets:** 8 · **Future:** 3

---

## Candidate Components (Informational — Not Requirements)

The following have been discussed and are recorded in `bom/candidates/` and `DECISIONS.md` as **PROVISIONAL / REQUIRES VERIFICATION**. They are not requirements and must be validated against primary datasheets before use:

- MCU: STM32G431 family
- DAC: AD5686R quad 16-bit
- Precision amp: ADA4522-2 zero-drift
- Power op-amp: LT1970A bipolar
- ADC: ADS1262 precision
- Regulator: LT1763 analog
- Reference: ADR4525-class precision reference
- Shunts + relay-based range switching

Do not propagate specs from memory. Every parameter must be re-checked in the manufacturer datasheet before promotion to `bom/approved/`.
