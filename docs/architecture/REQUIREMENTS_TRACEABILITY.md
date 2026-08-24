# Requirements Traceability — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 1  
**Date:** 2026-08-24  
**Version:** Covers REQUIREMENTS.md v0.2.0 (Phase 1 verified)  
**Gateway:** Phase 1 evidence → Phase 2 architecture DECs.

Format: `Requirement → Evidence → Rationale → Verification method` per ENGINEERING_RULES §9.

---

| REQ | Statement (summarized) | Status v0.2.0 | Evidence (Phase 1) | Rationale | Verification method |
|-----|------------------------|---------------|--------------------|-----------|---------------------|
| **REQ-SRC-001** | Bipolar source approx. –5 V to +5 V | **PROVISIONAL — verified as reasonable** (as RESEARCH: supports forming +2.4–5 V without mains; ±10 V not needed) | Agent A §5.1 (HfO2 forming, [C12mim] types), Agent D (commercial ±21 V lowest tier) + PHASE1 §4 | Covers primary ±2 V + forming headroom; higher V deferred per safety | Bench: sourcing into R + C loads across –5→+5 V, DMM vs force/sense |
| **REQ-SRC-002** | Primary low-noise region ≈ –2 V to +2 V | **PROVISIONAL — well-supported** (>80% of Vset/Reset) | Agent A Table §2 (Vset +0.6–1.5 V, Vreset –0.7––1.5 V on dozens of stacks) | Best accuracy where most ReRAM switches | Linearity + noise sweep in ±2 V window vs DMM |
| **REQ-SRC-003** | Bipolar operation (source/measure both polarities) | **CONFIRMED** | Agent A UC-1 bipolar sweep, PHASE1 §9 (all agents agree) | Bipolar RS is dominant | Bipolar sweep test (0→+2→0→–2→0) |
| **REQ-SRC-004** | Source and sink (active load) | **CONFIRMED** | Agent C 4-quadrant theory, Agent D commercial 20–40 W 4-quad, RERAM §2 (negative-differential needs sink) | Memristor can drive back; quadrant-switch glitch avoidance | Load-step + quadrant test (force +V, DUT sources –I, verify sink) |
| **REQ-SRC-005** | Four-quadrant architecture preferred | **CONFIRMED (promoted from provisional-preferred)** — DEC-007 in Phase 1 | PHASE1 §9 + Agent D 4-quad tables + RERAM §2 (bipolar + NDR) | Simplifies bipolar characterization; sink accuracy footnote applies | Architecture review + quadrant transition scope capture |
| **REQ-SRC-006** | Max DUT current approx. ±10 mA | **PROVISIONAL — verified** (100 µA–1 mA typical, 10 mA margin; 100 mA not needed) | Agent A §2 (Icc 10 µA–1 mA, RESET 0.2–3 mA, Al2O3 1–15 mA edge), PHASE1 §5 | 10× margin over typical Icc; 100 mA would add SOA/thermal burden | Current-drive into low-R load at compliance |
| **REQ-SRC-007** | Output enable/disable, safe default | **CONFIRMED** | RISKS R-12, COMPLIANCE §6–8 (safe default = min Icc or disabled) | DUT protection | Power-cycle + watchdog + fault tests |
| **REQ-MEAS-001** | Current ranges 10 mA,1 mA,100 µA,10 µA,1 µA,100 nA | **CONFIRMED** (was provisional) | Agent B + BURDEN analysis (R=10 Ω–1 MΩ, Johnson <1% FS @10 Hz down to 100 nA), PHASE1 §5 (6 log decades covers 20 nA–2 mA platform) | Log cover from forming to HRS leakage; 10 nA is V2 | Per-range calibration vs DMM/resistor, shunt TC check |
| **REQ-MEAS-002** | V1 useful floor several nA (meaningful above noise) | **CONFIRMED as quantified** (was provisional) | Agent B LOW_CURRENT §3 (100 nA guard-required, leakage-limited) + PHASE1 §6 (MUC 1 nA quantitative, detection 1.5–6 pA 3σ) | Balances ambition with leakage limits without electrometer | Noise-floor time series (shorted input, NPLC=1, Allan deviation), system leakage open-input test |
| **REQ-MEAS-003** | Measure DUT voltage (Force & Sense) adequate for I–V | **CONFIRMED (extent still provisional)** (accuracy numbers in §7 are research targets) | PHASE1 §7 (source V ±0.02%+ offset), BURDEN (Kelvin corrects 100 mV burden) | Needed for I–V hysteresis | Vsense vs calibrated DMM at –2…+2 V |
| **REQ-MEAS-004** | Autoranging with hysteresis/dwell | **CONFIRMED** | RERAM §4 (autorange chatter at HRS↔LRS), COMPLIANCE §6 (range compliance) | Avoid chatter at compliance knee | Sweep crossing range boundaries, chatter count |
| **REQ-MEAS-005** | Resolution ≠ accuracy | **CONFIRMED (informational)** | LOW_CURRENT §1.1 table (24-bit LSB 5.96 fA vs Johnson 0.41 pA) + NOISE framework | Reporting discipline | Review docs + firmware display |
| **REQ-MEAS-006** | 10 nA / pA electrometer (FUTURE) | **FUTURE / NOT V1 — reconfirmed** | LOW_CURRENT §3.1 V2 analysis (10 MΩ, 10 GΩ leak→10 pA error, DA tails) | Requires guard-driven triax etc. | — (V2 daughter-card) |
| **REQ-SAFE-001** | Hardware current compliance independent of firmware | **CONFIRMED** | Agent A §3.2 (SPA 4.5 µs overflow, ST 110 ns, CLA 500 ps), COMPLIANCE §§2–5 (HW regulation loop) | Firmware alone is ms vs ns filament collapse | Fault injection: short + 100 Ω step, scope I overshoot & flag |
| **REQ-SAFE-002** | Software current limits (supplement) | **CONFIRMED** | COMPLIANCE §7 (envelope, pre-check, soft-start) | Redundant polygon | Software limit trip test |
| **REQ-SAFE-003** | Safe power-on / brown-out / reset → disabled | **CONFIRMED** | COMPLIANCE §5.5 (reference defaults to min I) + arch. safe state invariant | DUT safety | Power-cycle + watchdog reset with output monitored |
| **REQ-SAFE-004** | Output disabled on FW fault/watchdog | **CONFIRMED** | RISKS R-12 | Hang → safe | Watchdog timeout test |
| **REQ-SAFE-005** | Bipolar I–V sweeps (programmed V steps, measured I) | **CONFIRMED** | RERAM §4 WF-1…7, PHASE1 §10 (linear dual sweep) | ReRAM I–V is sweep, not spot | Sweep automation test (0→+2→0→–2→0) |
| **REQ-SAFE-006** | Temperature monitoring of critical subsections | **CONFIRMED** | PHASE1 §11 (output stage, shunts, ref; NTC/TMP117) | Thermal drift compensation / interlock | Thermal step test + over-temp response |
| **REQ-SAFE-007** | Fault monitoring (OC, OT, compliance, supply) | **CONFIRMED** | COMPLIANCE §§1,3 (fault flags vs compliance flag) | Operability | Fault-injection matrix |
| **REQ-SAFE-008** | Watchdog + error handling → safe state | **CONFIRMED** | — | — | Watchdog + error-path tests |
| **REQ-DUT-001** | Kelvin / 4-wire FORCE/SENSE HI/LO | **CONFIRMED** | BURDEN §1 (lead-drop correction), PHASE1 §11 (remote sense >10 GΩ, 5 V FS, 1 MΩ lead) | Required for low-R LRS and calibration | 2-wire vs 4-wire comparison on 1 kΩ & 10 Ω dummy |
| **REQ-DUT-002** | Connector type TBD, shielded/leakage-conscious path for future guard | **PROVISIONAL — verified as deferrable to Phase 2** | LOW_CURRENT §4 (guard ring checklist, triax provision) | Must support future guard | Architecture DEC in Phase 2 (banana/BNC/terminal) |
| **REQ-DUT-003** | Triax / driven guard / electrometer (FUTURE) | **FUTURE / NOT V1 — reconfirmed** | DCM / KLL §4, Agent D (triax required for sub-nA) | Not needed for several-nA V1 | — |
| **REQ-SW-001** | USB interface | **CONFIRMED** | — | Host control | Enumeration + round-trip |
| **REQ-SW-002** | SCPI-like subset | **CONFIRMED** | PHIL (SCPI types linear/log/custom/list) | Interop without full SCPI | Command-set tests |
| **REQ-SW-003** | Python control | **CONFIRMED** | — | Sweeps/config/readout | Python integration tests |
| **REQ-SW-004** | Automated sweep (start/stop/step/delay, bidirectional) | **CONFIRMED** | PHASE1 §10 | — | Sweep test with log |
| **REQ-SW-005** | Data export CSV + raw w/ metadata | **CONFIRMED** | — | Traceability | Export format check |
| **REQ-PWR-001** | No direct 230 V mains on PCB | **CONFIRMED** | — | Safety | Schematic/PCB review checklist |
| **REQ-PWR-002** | External lab supply for bring-up (~±12 V) | **CONFIRMED** | — | — | Bring-up procedure |
| **REQ-PWR-003** | Nominal analog rails ≈±12 V | **PROVISIONAL — still provisional** (needs headroom analysis for LT1970-class or alternative) | Not yet sized; ±12 V supports ±5 V with dropout margin | TBD | Headroom + dropout analysis |
| **REQ-PWR-004** | Separate analog/digital supply treatment | **CONFIRMED (principle) / PROVISIONAL (implementation)** | Noise budget (PSRR, mains nulling) + LOW_CURRENT §2.5 | Recommended | Power arch review + noise PSD |
| **REQ-CAL-001** | Documented calibration procedure with traceability | **CONFIRMED** | PHASE1 §11 (cal vs verification vs traceable, adjust hierarchy) | V1 ships with cal report | docs/calibration/ + report |
| **REQ-CAL-002** | Dummy loads first, no ReRAM as first DUT | **CONFIRMED** | RERAM §5.5 verification list, ENGINEERING_RULES #9–10 | Protect DUT/board | Bring-up log (DUT type logged) |
| **REQ-CAL-003** | Uncertainty budget (not just resolution) | **CONFIRMED** — now framework exists | UNCERTAINTY_BUDGET_FRAMEWORK (GUM, RSS, k=2, rectangular a/√3) | Scientific integrity | Budget review vs external DMM |
| **REQ-GEN-001** | Simulation before PCB where practical | **CONFIRMED** | — | — | simulation/results/ |
| **REQ-GEN-002** | Reviews before manufacturing (schematic+ERC+sim+design) | **CONFIRMED** | — | — | Review checklists |
| **REQ-GEN-003** | Traceability (requirements → decisions → evidence) | **CONFIRMED** | This file | — | DECISIONS.md coverage |

---

## Verification method index (summary)

Calculation: Johnson/burden/TC (BURDEN, NOISE, python .venv)  
SPICE: compliance loop step response, power-stage headroom (future Phase 3–5)  
Bench DMM: source/measure accuracy vs calibrated 6½-digit DMM per range  
Resistor: dummy-load hysteresis (1 kΩ,10 kΩ,100 kΩ,1 MΩ), burden/Kelvin delta  
Scope: compliance overshoot (short+step load, µs capture, flag timing)  
Thermal: drift vs T (20±10 °C chamber or bench), sensor logging  
Long-duration: retention drift, aging (hours–days)

If a REQ cannot be practically verified (above rows all have at least one), it was reconsidered — none fell into that case for V1.

---

*No hardware designed. Candidates remain provisional.*

