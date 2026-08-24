# ReRAM-SMU V1 — Requirements

**Version:** 0.2.0 — Phase 1 verified  
**Date:** 2026-08-24  
**Status:** CONFIRMED / REVISED / PROVISIONAL / FUTURE per below. Provisional from v0.1.0 that is now supported has been promoted; promotions cite Phase 1 research.  
**Convention:** `REQ-<DOMAIN>-<NNN>` · Domains: SRC, MEAS, SAFE, DUT, SW, PWR, CAL, GEN

> **Rule:** Never silently convert a provisional target or future item into a confirmed requirement. Promotion requires a `DECISIONS.md` entry with evidence — this version's promotions are backed by DEC-007 through DEC-015 and Phase 1 research in `docs/research/` + `docs/calculations/`.

---

## How to Read This Document

- **CONFIRMED** — binding for V1 unless formally changed.
- **REVISED** — provisional target changed based on Phase 1 evidence (old → new shown).
- **PROVISIONAL** — still plausible but insufficient evidence; do not design to its limits without verification.
- **Future / V2+** — explicitly not V1; recorded to avoid scope creep.
- **REJECTED** — not justified for V1.

Each requirement lists ID, statement, rationale, verification method, status, and Phase 1 trace (`docs/research/` + `docs/calculations/`).

---

## 1. Source Capability — `REQ-SRC-*`

### REQ-SRC-001 — Bipolar Voltage Source Range (PROVISIONAL — verified as reasonable)

**Statement:** Nominal voltage source approximately **−5 V to +5 V** continuous, four-quadrant, source/sink.  
**Rationale:** Covers primary ±2 V ReRAM SET/RESET plus forming headroom (+2.4–5 V) without high-voltage/interlock complexity. ±10 V would not materially improve utility for low-voltage stacks.  
**Evidence:** `docs/research/RERAM_MEASUREMENT_REQUIREMENTS.md` §2/§5.1 (Vset +0.6–1.5 V on HfO2/TaOx/[C12mim], forming +2–+5 V); `COMMERCIAL_SMU_BENCHMARK.md` §4 (commercial lowest tier ±21 V; V1 ±5 V sits inside most accurate 2 V–20 V band).  
**Verification:** Sourcing into R + C loads across –5→+5 V; DMM vs FORCE/SENSE.  
**Status:** `PROVISIONAL — VERIFIED AS REASONABLE / REQUIRES MEASURED HEADROOM CHECK` — supported, not yet promoted to CONFIRMED pending power-stage headroom analysis (Phase 3).

### REQ-SRC-002 — Primary ReRAM Operating Region (PROVISIONAL — well-supported)

**Statement:** Primary region approximately **−2 V to +2 V** must be within linear, low-noise operating envelope with best accuracy.  
**Rationale:** >80% of reported SET/RESET on dozens of filamentary stacks (HfO2, TaOx, TiO2, Al2O3, GCMO, nanowire, polymer) falls here. Read bias 0.1–0.5 V also inside region.  
**Evidence:** RERAM §2 table (Vset +0.6–1.5 V, Vreset –0.7––1.5 V), 0.01–0.05 V step / 50–100 ms dwell literature.  
**Verification:** Linearity and noise characterization in ±2 V window.  
**Status:** `PROVISIONAL — WELL-SUPPORTED` — expected to be CONFIRMED at Phase 3 after source-stage simulated.

### REQ-SRC-003 — Bipolar Operation (Confirmed)

**Statement:** System shall source and measure both positive and negative voltages and currents.  
**Rationale:** ReRAM bipolar switching; four-quadrant I–V required (0→+Vmax→0→–Vmax→0).  
**Evidence:** RERAM UC-1/2 (bipolar dominates), PHASE1 §3.  
**Verification:** Bipolar sweep test.  
**Status:** `CONFIRMED`

### REQ-SRC-004 — Source and Sink Capability (Confirmed)

**Statement:** Output stage shall source and sink current (active load).  
**Rationale:** Memristor/LRS can drive current back; SMU must absorb without quadrant-switch glitch.  
**Evidence:** `docs/research/SMU_ARCHITECTURE_SURVEY.md` §0 4-quadrant, `COMPLIANCE_RESEARCH.md` (sink needed for NDR).  
**Verification:** Load-step and quadrant test.  
**Status:** `CONFIRMED`

### REQ-SRC-005 — Four-Quadrant Architecture (CONFIRMED — promoted from PROVISIONAL-preferred)

**Statement:** Architecture shall be four-quadrant (source + sink, both polarities) — now mandatory for V1.  
**Rationale:** Phase 1 synthesis (all agents agree) shows ReRAM requires Q1 +V/+I, Q2 +V/–I sink, Q3 –V/–I, Q4 –V/+I; source/sink voltage-only is insufficient; power is modest (~50 mW @±5 V·±10 mA) but sink accuracy (4–8× offset penalty on commercial SMUs) must be characterized.  
**Evidence:** PHASE1 §9, `SMU_ARCHITECTURE_SURVEY.md`, RERAM §2/§5.5.  
**Verification:** Architecture review + quadrant-transition scope capture (sink vs source error separate).  
**Status:** `CONFIRMED` — DEC-007 (Phase 1).

### REQ-SRC-006 — Maximum DUT Current (PROVISIONAL — verified)

**Statement:** Target maximum DUT current approximately **±10 mA** continuous (DC; pulse forming not in V1).  
**Rationale:** HfO2/TiO2 standard Icc 100 µA–1 mA, RESET 0.2–3 mA, Al2O3 forming 1–15 mA edge — 10 mA gives 10× margin over typical Icc without pulse/high-power. 100 mA not justified (no low-voltage evidence) and would add SOA/thermal burden.  
**Evidence:** RERAM §2 (10 µA–1 mA most common Icc; 10 mA max with headroom) + COMMERCIAL §4 (V1 ±10 mA is lowest commercial max-current tier, cheapest precision tier).  
**Verification:** Current-drive test into low-impedance load at compliance.  
**Status:** `PROVISIONAL — VERIFIED AS REASONABLE` — confirmed against evidence; promotion pending output-stage headroom: REQ-PWR-003 analysis.

### REQ-SRC-007 — Output Enable / Disable (Confirmed)

**Statement:** Firmware and hardware shall provide explicit output enable/disable with safe default.  
**Verification:** Power-cycle and fault tests (see REQ-SAFE).  
**Status:** `CONFIRMED`

---

## 2. Measurement Capability — `REQ-MEAS-*`

### REQ-MEAS-001 — Current Ranges (CONFIRMED — promoted from PROVISIONAL)

**Statement:** V1 current measurement ranges: **10 mA, 1 mA, 100 µA, 10 µA, 1 µA, 100 nA** (6 log ranges, autoranging). **10 nA and 100 mA are explicitly not V1** (see REQ-MEAS-006).  
**Rationale:** Logarithmic cover from forming (mA) to HRS leakage (hundreds nA): CMOS on-chip platform 20 nA–2 mA (5 decades) + GCMO HRS 10⁷–10⁸ Ω needs nA; R=10 Ω–1 MΩ at 100 mV FS gives Johnson <1% FS @10 Hz down to 100 nA (BURDEN table).  
**Evidence:** RERAM §2 (Icc 10 µA–1 mA → LRS mA, HRS nA), `LOW_CURRENT_MEASUREMENT.md` §3 + `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md` (R 10–1 MΩ, 1.0 mW→10 nW, TC 0.025%).  
**Verification:** Shunt + amplifier + ADC chain analysis; per-range calibration vs precision resistor.  
**Status:** `CONFIRMED` — DEC-008.

### REQ-MEAS-002 — V1 Lower Measurement Region (CONFIRMED as quantified — was PROVISIONAL “several nA”)

**Statement:** Target V1 useful lower region: **several nA** — quantified as **detection 3σ ≈ 1.5–6 pA, quantitative 10σ ≈ 5–20 pA on 100 nA range (1 MΩ, 10 Hz BW, Johnson 0.41 pA rms), practical quantitative MUC ≈ 1 nA (≈10% of 100 nA range) with averaging/shielding, leakage-corrected.** Resolution (e.g., 24-bit LSB ≈6 fA) is reported separately and is not the floor.  
**Rationale:** Mn3O4 selector OFF 4 nA, HRS 10 nA–0.4 µA range; pA is V2 with guard-driven triax/electrometer (REQ-MEAS-006). “Several nA” was not an acceptable final requirement — now measurable per above.  
**Evidence:** LOW_CURRENT §1.1/3.1 (100 nA guard-required, leakage-limited), NOISE_BUDGET framework (Johnson 0.41 pA @10 Hz/1 MΩ), PHASE1 §6.  
**Verification:** Noise-floor time series (shorted input, NPLC=1, Allan deviation) + system leakage open-input test (100 s); report mean ±σ at 100 nA range.  
**Status:** `CONFIRMED` (quantified) — DEC-009.

### REQ-MEAS-003 — Voltage Measurement (Confirmed, extent provisional — accuracy targets added as research)

**Statement:** System shall measure DUT voltage (Force and Sense) with accuracy adequate for I–V characterization. Phase 1 research accuracy targets (not yet CONFIRMED): source/measure V ±(0.02% reading + 0.01% FS + 2 ppm/°C·ΔT), e.g., ±0.5 mV @1 V, ±2 mV @2 V; cal residual <½ spec; NPLC 1–10 trade.  
**Evidence:** PHASE1 §7 (targets are 2–5× looser than Keithley 0.012% intentionally), UNCERTAINTY framework.  
**Verification:** Comparison against calibrated DMM (e.g., 34465A) at –2,–1,0,+1,+2 V.  
**Status:** `CONFIRMED (existence) / PROVISIONAL (numbers)` — numbers are research targets pending Phase 3 simulation + measurement.

### REQ-MEAS-004 — Autoranging (Confirmed)

**Statement:** System shall support autoranging across current ranges with documented hysteresis/dwell (≥2 samples post-trip, hold range to avoid chatter at HRS↔LRS transition) to avoid chatter. Must respect `I_compliance ≤ I_range` invariant (range compliance).  
**Evidence:** RERAM §4 WF-1 autorange note + COMPLIANCE §6 (range compliance, holdoff for C·dV/dt).  
**Verification:** Automated sweep crossing range boundaries; chatter count.  
**Status:** `CONFIRMED`

### REQ-MEAS-005 — Resolution ≠ Accuracy (Confirmed, informational)

**Statement:** Documentation and software shall never conflate ADC/DAC resolution with system accuracy; both shall be reported separately per MEASUREMENT_ENVELOPE table; LSB (e.g., 6 fA on 100 nA/24-bit) is not accuracy.  
**Evidence:** LOW_CURRENT §1.1 table (LSB 5.96 fA vs Johnson 0.41 pA), REQ-CAL-003.  
**Verification:** Review of docs + software display.  
**Status:** `CONFIRMED`

### REQ-MEAS-006 — Future Low-Current Extension (Future / V2)

**Statement:** Future revisions may target 10 nA, pA, and electrometer-class measurements (10 MΩ shunt, guard-driven triax, Teflon standoffs, ADA4530-1, enclosure). Not required for V1; 10 nA is explicitly FUTURE and needs electrometer daughter-card.  
**Evidence:** LOW_CURRENT §3.1 V2 analysis (10 GΩ leak →10 pA @100 mV, 5 nA @5 V →100% FS).  
**Status:** `FUTURE / NOT V1`

### REQ-MEAS-007 — Voltage Source Accuracy (NEW — provisional research target)

**Statement:** Provisional source accuracy target for V1 (post-cal, 25±3 °C, k=2 expanded where noted): at –2,–1,0,+1,+2 V — research aim ±(0.02% reading + 0.01% FS + 2 ppm/°C·ΔT + drift); bias at 0 V within ±200 µV. Promoted only after Phase 3 simulation + DMM comparison.  
**Verification:** DMM sweep tie against calibrated reference.  
**Status:** `PROVISIONAL / RESEARCH TARGET`

### REQ-MEAS-008 — Current Measurement Accuracy (NEW — provisional research target)

**Statement:** Provisional current measurement accuracy (research, k=2): 10 mA ±(0.03%+10 µA), 1 mA ±(0.03%+1 µA), 100 µA ±(0.05%+200 nA), 10 µA ±(0.08%+20 nA), 1 µA ±(0.1%+5 nA), 100 nA (@50 nA) ±(0.3%+60 pA) ≈1σ 30 pA (dominant: shunt 0.1%/√3 + Ileak 5 pA/√3 + Johnson 0.41 pA).  
**Verification:** Precision resistor V/I tie per range; leakage-corrected.  
**Status:** `PROVISIONAL / RESEARCH TARGET`

---

## 3. Protection and Control — `REQ-SAFE-*`

### REQ-SAFE-001 — Hardware Current Compliance (Confirmed — revised per DEC-024)

**Statement:** A **hardware** current compliance / protection loop shall limit DUT current independent of firmware, per compliance triad: compliance regulation (flat CC, flagged, SMU stays in circuit) distinct from range compliance and SOA trip (crowbar). Icc programmable as value within range (not decade-locked). For LT1970A-based limiters the minimum programmable compliance is limited by the 4 mV VSENSE floor (~4% of FS at 100 mV FS, ~16% at 25 mV FS) and the Vc<60 mV nonlinear region — see DEC-024 and `docs/research/PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md` IR-01. A `0.1%·I_range` target applies only to the precision external CC-loop (Source Candidate C) and is otherwise satisfied via **compliance-aware automatic range coercion** (requested Icomp selects an achievable hardware range). The compliance reference shall be DAC-driven per segment (no hard-wired trimpot), with per-polarity source/sink control.  
**Verification:** Fault injection: short + step load; scope I overshoot & flag timing. Targets (research): regulation settle <50 µs to Icc, trip <5 µs, overshoot <1% (resistive) / <5% into 1 nF with soft-start, SOA hyperbola |V·I|≤50–60 mW DC, flag latency ≤1 NPLC. Hardware must function with MCU halted.  
**Status:** `CONFIRMED (revised 2026-08-24, DEC-024 — original 0.1% Keithley rule retained only for precision-loop tier)`

### REQ-SAFE-002 — Software Current Limits (Confirmed)

**Statement:** Firmware/software shall enforce configurable current limits in addition to hardware compliance (secondary polygon: isw_limit, v_limit, power_limit, pre-check gate, soft-start ramp).  
**Verification:** Software limit trip test.  
**Status:** `CONFIRMED`

### REQ-SAFE-003 — Safe Power-On State (Confirmed)

**Statement:** On power-on, brown-out, firmware reset, or watchdog reset, output shall default to **disabled / high-impedance safe state** with compliance reference defaulting to minimum I-range.  
**Verification:** Power-cycle + reset tests with output monitored.  
**Status:** `CONFIRMED`

### REQ-SAFE-004 — Output Disabled on Firmware Failure (Confirmed)

**Statement:** Firmware fault, hang, or watchdog timeout shall disable output.  
**Verification:** Watchdog timeout test.  
**Status:** `CONFIRMED`

### REQ-SAFE-005 — Bipolar I–V Sweeps (Confirmed)

**Statement:** System shall execute bipolar I–V sweeps (programmed voltage steps, measured current) with built-in preset `0→+Vmax→0→–Vmax→0`, step 1–50 mV (default 10 mV), dwell 10 ms–2 s (default 50–100 ms, interstep 10 ms), ≥200 pts/loop, compliance-hit handling (flag+hold range), autorange, abort on interlock/OT/watchdog.  
**Verification:** Sweep automation test.  
**Status:** `CONFIRMED`

### REQ-SAFE-006 — Temperature Monitoring (Confirmed)

**Statement:** System shall monitor temperature of critical subsections (output stage, shunts, reference) — 1 per zone (NTC or digital e.g., TMP117); logging is sufficient for V1 (compensation is V1.x/V2). Assumed operating 15–30 °C lab.  
**Verification:** Thermal test + over-temperature response.  
**Status:** `CONFIRMED`

### REQ-SAFE-007 — Fault Monitoring (Confirmed)

**Statement:** System shall detect and report faults (over-current, over-temperature, compliance active distinct from fault, supply faults, reverse energy). Every sample logs `range_state`, `compliance_flag/type`, `Icomp/Vcomp`, `I_range/V_range`.  
**Verification:** Fault-injection matrix.  
**Status:** `CONFIRMED`

### REQ-SAFE-008 — Watchdog / Error Handling (Confirmed)

**Statement:** Firmware shall include watchdog and structured error handling that forces safe state on failure.  
**Verification:** Watchdog + error-path tests.  
**Status:** `CONFIRMED`

---

## 4. DUT Interface — `REQ-DUT-*`

### REQ-DUT-001 — Kelvin / 4-Wire Support (Confirmed — addendum per IR-02/03)

**Statement:** DUT interface shall support **FORCE HI, SENSE HI, SENSE LO, FORCE LO** and Kelvin/4-wire measurement with remote sense **>10 GΩ achieved via a high-Z buffer before any attenuation/dividing stage (IR-02)**, 5 V force–sense drop, 1 MΩ lead tolerance, open-sense detection via switched disconnect (≥10 GΩ effective or disconnected during measurement — IR-03), 2-write/4-wire mode.  
**Verification:** 2-wire vs 4-wire comparison on 1 kΩ and 10 Ω dummy (LRS); max-drop test; DUT loading sweep 1 MΩ/10 MΩ/100 MΩ/1 GΩ (IR-02).  
**Status:** `CONFIRMED (addendum 2026-08-24 — buffer-first, switched open-sense)`

### REQ-DUT-002 — Connector Strategy (Provisional — deferrable to Phase 2)

**Statement:** V1 connector type TBD (banana, BNC, terminal block, or Kelvin clip). Must support shielded/leakage-conscious wiring path for future guard (guard-ring copper, exposed no-mask, inner guard plane, C0G-only on high-Z path) without claiming guard performance.  
**Verification:** Architecture decision in Phase 2 per LOW_CURRENT §4 checklist.  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION` — updated to note guard-ring provision even though triax is deferred.

### REQ-DUT-003 — Triax / Driven Guard / Electrometer Front-End (Future)

**Statement:** Triax connectors, driven guard, and electrometer front-end are **future revisions**, not V1. Explicitly includes 10 nA range electrometer daughter-card. V1 acknowledges this as the path to 10⁻¹⁴ Ω guard.  
**Status:** `FUTURE / NOT V1`

---

## 5. Computer Interface — `REQ-SW-*`

### REQ-SW-001 — USB Interface (Confirmed)

**Statement:** Instrument shall be computer-controlled via **USB** (USB-TMC or USB-CDC class; GPIB/LXI not required).  
**Verification:** USB enumeration + command round-trip.  
**Status:** `CONFIRMED`

### REQ-SW-002 — SCPI-like Command Interface (Confirmed)

**Statement:** Firmware shall expose an **SCPI-like** command interface (subset: SOURCE:VOLT, SOURCE:CURR:LIM, MEAS:VOLT?, MEAS:CURR?, OUTPUT:ENABLE, sweeps; linear dual sweep + list/custom as minimum). Full SCPI compliance not required.  
**Verification:** Command-set tests against spec in `docs/`.  
**Status:** `CONFIRMED`

### REQ-SW-003 — Python Control (Confirmed)

**Statement:** A **Python** control library/client shall drive the instrument (sweeps, config, readout).  
**Verification:** Python integration tests.  
**Status:** `CONFIRMED`

### REQ-SW-004 — Automated Sweep Execution (Confirmed)

**Statement:** Software shall support automated sweep execution (configurable start/stop/step/delay/dwell, bidirectional, holdoff, compliance-flag handling, timestamped buffer).  
**Verification:** Sweep test with logged data.  
**Status:** `CONFIRMED`

### REQ-SW-005 — Data Export (Confirmed)

**Statement:** Software shall export data as **CSV and raw data** with metadata (timestamp, range, compliance_flag/type, Icomp/Vcomp, range_state, temperature).  
**Verification:** Export format test; raw data preservation check.  
**Status:** `CONFIRMED`

---

## 6. Power Architecture — `REQ-PWR-*`

### REQ-PWR-001 — No Direct Mains on SMU PCB (Confirmed)

**Statement:** V1 SMU PCB shall have **no direct 230 V mains circuitry**.  
**Verification:** Schematic/PCB review checklist.  
**Status:** `CONFIRMED`

### REQ-PWR-002 — External Lab Supply for Development (Confirmed)

**Statement:** Development and bring-up shall use an **external laboratory supply**.  
**Verification:** Bring-up procedure.  
**Status:** `CONFIRMED`

### REQ-PWR-003 — Nominal Analog Rails (PROVISIONAL — still provisional)

**Statement:** Nominal analog rails approximately **±12 V**, subject to output-stage headroom analysis (must supply ±5 V + 25–100 mV burden + dropout + SOA). AD5764, if selected, requires **±11.4 V minimum** (see IR-07) — ±10 V LDO rails are **not** AD5764-compatible; V1 power-tree Options A/B/C defined in `POWER_TREE.md`.  
**Verification:** Headroom + dropout analysis (regulators, LT1970A or alternative; AD5764 ±11.4 V spec).  
**Status:** `PROVISIONAL / REQUIRES VERIFICATION` — compatible with LT1970A on raw ±12 V (Option A).

### REQ-PWR-004 — Analog / Digital Supply Treatment (Confirmed, extent provisional)

**Statement:** Design shall provide **separate analog/digital supply treatment** as needed (regulation, filtering, star-point/partition, **one continuous reference plane with no etched AGND/DGND split — separation by placement, local return-current control, routing discipline, and decoupling (IR-13)**, LC π-filter, PSRR ≥80 dB at ripple, NPLC mains nulling).  
**Verification:** Power architecture review + noise PSD with/without USB.  
**Status:** `CONFIRMED (principle) / PROVISIONAL (implementation) — wording corrected per IR-13`

---

## 7. Calibration & Quality — `REQ-CAL-*`

### REQ-CAL-001 — Calibration Procedure (Confirmed)

**Statement:** V1 shall have a documented calibration procedure with traceability, distinguishing adjustment vs verification vs calibration vs traceable calibration (GUM). References: calibrated 6½-digit DMM, class 0.01% precision resistors (1 kΩ–1 MΩ), 2.5 V reference cert.  
**Verification:** `docs/calibration/` + calibration report.  
**Status:** `CONFIRMED`

### REQ-CAL-002 — Verification on Dummy Loads First (Confirmed)

**Statement:** First hardware tests shall use **dummy loads and precision resistors** (1 kΩ,10 kΩ,100 kΩ,1 MΩ linear I–V + compliance trip + Kelvin delta + autorange chatter); no ReRAM sample as first DUT; DUT type logged in every measurement file.  
**Verification:** Bring-up log + risk verifications per RERAM §5.5.  
**Status:** `CONFIRMED`

### REQ-CAL-003 — Uncertainty Budget (Confirmed)

**Statement:** V1 shall publish a measurement uncertainty discussion (not just resolution), per `docs/calculations/UNCERTAINTY_BUDGET_FRAMEWORK.md` (GUM JCGM 100): categories S1–S10, M1–M10, V1–V4, C1–C7; RSS `u_c=√(Σu_i²)`, rectangular `a/√3`, expanded `U=k·u_c (k=2)`; type A from measured σ; Monte Carlo Supplement 1 teaser.  
**Verification:** Calibration/verification report vs external DMM.  
**Status:** `CONFIRMED` — framework now exists.

---

## 8. General / Process — `REQ-GEN-*`

### REQ-GEN-001 — Simulation Before PCB (Confirmed)

**Statement:** Simulation is required before PCB implementation where practical (now with hybrid workflow: ngspice primary, LTspice secondary).  
**Verification:** Simulation results in `simulation/results/` with date/tool-version/models.  
**Status:** `CONFIRMED`

### REQ-GEN-002 — Reviews Before Manufacturing (Confirmed)

**Statement:** No PCB manufactured until schematic review, ERC, simulation review, and design review are complete (guard-ring checklist included).  
**Verification:** Review checklists in `docs/`.  
**Status:** `CONFIRMED`

### REQ-GEN-003 — Traceability (Confirmed)

**Statement:** Design decisions remain traceable (requirements → decisions → evidence), now via `docs/architecture/REQUIREMENTS_TRACEABILITY.md` mapping each REQ to evidence.  
**Verification:** `DECISIONS.md` coverage check.  
**Status:** `CONFIRMED`

---

## Summary Counts (v0.2.0)

| Category | Confirmed | Provisional | Future | Notes vs v0.1.0 |
|----------|:---------:|:-----------:|:------:|-----------------|
| SRC | 4 (was 2) | 3 (was 4) | 0 | REQ-SRC-005 promoted |
| MEAS | 6 (was 3) | 2 (was 2) | 1 | REQ-MEAS-001/002 promoted, 007/008 added provisional |
| SAFE | 8 | 0 | 0 | unchanged count, REQ-SAFE-001/005 enriched |
| DUT | 1 | 1 | 1 | unchanged |
| SW | 5 | 0 | 0 | unchanged |
| PWR | 2 | 1(+1 partial) | 0 | unchanged |
| CAL/GEN | 6 | 0 | 0 | unchanged |

**Total confirmed V1 requirements:** 31 (was 27) · **Provisional targets:** 7 (was 8) + 2 new research provisional = 9 · **Future:** 3

---

## Candidate Components (Informational — Not Requirements)

Unchanged — still **PROVISIONAL / REQUIRES VERIFICATION**: STM32G431 family, AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525-class, shunts + relay range switching. No component promoted in Phase 1. Do not propagate specs from memory.

---

## Change Log (v0.1.0 → v0.2.0)

- DEC-007: REQ-SRC-005 four-quadrant promoted to CONFIRMED.
- DEC-008: REQ-MEAS-001 six ranges promoted to CONFIRMED; 100 mA rejected, 10 nA FUTURE.
- DEC-009: REQ-MEAS-002 several-nA quantified (detection 3σ ~1.5–6 pA, quantitative 10σ ~5–20 pA, practical 1 nA) and CONFIRMED.
- REQ-SRC-001/002/006 wording unchanged but status updated to PROVISIONAL-verified with evidence citations.
- NEW REQ-MEAS-007/008 accuracy research targets added as PROVISIONAL.
- REQ-SAFE-001/005 enriched with compliance triad and sweep parametric table (research targets for timing).
- REQ-DUT-002 updated to require guard-ring provision despite triax deferral.
- REQ-PWR-004 enriched with NPLC mains nulling.
- REQ-CAL-003 now references uncertainty framework.
- Traceability to Phase 1 research added per REQ.
