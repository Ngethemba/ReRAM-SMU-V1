# Architecture — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 Architecture & Candidate Component Verification  
**Date:** 2026-08-24  
**Status:** `PROVISIONAL — SELECTED FOR PHASE 3` (no schematic/PCB/BOM, conceptual). Cautions 1–5 addressed; decisions require Phase 3 simulation gates.

---

## 1. Functional block diagram (conceptual — no values)

```mermaid
flowchart TB
  PC[Host PC\nPython + SCPI-like]
  PC <--> USB[USB CDC/TMC\nisolator provision]
  USB <--> MCU[MCU: STM32G4-class\nSTM32G431 provisional\nSPI×2, USB FS, timers,\nGPIO 12 relay, watchdog]
  MCU --> DAC[DAC: 16-bit quad/bipolar\nAD5686R or AD5764 class\nSource + Compliance refs]
  MCU <--> ADC[ADC: ΔΣ 24-bit\nADS1262 or AD7175 class\nPGA, 50 Hz NPLC]
  MCU --- FAULT[Fault/Watchdog/OT]
  DAC --> SRC[Source / Sink Stage\nPrimary: LT1970A ±500 mA with\nprecise ±% current limit\nAlternate: precision op+discrete buffer\n±5 V / ±10 mA, safe disable]
  SRC --> FH[FORCE_HI]
  FH --> SHUNT[Current-sense matrix\nLow-side shunts 10Ω–1MΩ\n(10 mA→100 nA, 100 mV FS)\nReed for 1µA/100nA]
  SHUNT --> FL[FORCE_LO\n→ ±12V bulk GND]
  DUT[DUT\nReRAM cell] --- FH
  DUT --- FL
  DUT --- SH[SENSE_HI]
  DUT --- SL[SENSE_LO]
  SH --> VSENSE[Voltage sense\nHi-Z diff amp\n>10 GΩ, 5 VFS]
  SL --> VSENSE
  VSENSE --> ADC
  SHUNT --> ISENSE[Current sense\nLow-side diff (ground-ref)\nZero-drift amp]
  ISENSE --> ADC
  DAC --> COMP[Compliance controller\nDual: continuous limit (LT1970A\nISRC/ISNK) + fast TLV3501\ntrip <5 µs, SOA 50 mW]
  COMP --> SRC
  COMP -.-> ADC
  REF[Voltage ref\nADR4525 or LTC6655/REF5040\nShared vs separate TBD] --> DAC & ADC
  PWR[Power tree\nExt ±12 V → LDOs:\n±10 for source, +5 prec, 3.3 dig] --> SRC & DAC & ADC & REF & MCU
  TEMP[Temp sensors\nOutput stage, shunt block, ref] --> MCU
```

**Key placements (CAUTION 2/4 answered):**

- **Shunt:** **Low-side, between FORCE_LO and power GND**, outside DUT-sense loop (SENSE encloses DUT only, not shunt). This avoids high common-mode on sense amp (ground-ref diff amp meets Vos/TC without CM), simplifies guard, and keeps compliance sense ground-ref. Tradeoff: source loop regulates FORCE against SENSE_HI/SENSE_LO, so 100 mV burden appears as headroom (≈5.1 V needed for +5 V DUT at 10 mA FS → 7 V headroom from ±12 V → OK). Burden-corrected mode (SENSE encloses DUT+shunt) is possible in firmware as diagnostic, not default.
- **DUT relative to shunts:** DUT sits between FORCE_HI (source) and FORCE_LO side of shunt. Current flows FH→DUT→FL→shunt→GND, so measured current equals DUT current.
- **Source-loop feedback point:** **Remote SENSE (SENSE_HI/SENSE_LO differential)** at DUT terminals — source amp in non-inverting force mode with SENSE feedback divider. FORCE tracks SENSE with gain, correcting lead drops (2-wire vs 4-wire delta).
- **Compliance-loop sensing point:** **Low-side shunt voltage** (same ISENSE) vs compliance DAC reference — independent of SENSE, so compliance regulates I irrespective of V_DUT. Per-segment/polarity programmable (DAC channels).
- **Protection-loop sensing point:** Same shunt + separate fast comparator (TLV3501) vs trip reference — independent latch, survives MCU halt.

## 2. Caveats addressed

### CAUTION 1 — Bipolar vs full 4-quadrant

Phase 1 promoted REQ-SRC-005 to 4-quad. Architecture is **true bipolar Source-V/Measure-I with controlled sink (±5 V·±10 mA, 50 mW)**, not arbitrary I-source arbitrary Q. For ReRAM workflows (0→+Vmax→0→–Vmax→0), required behaviors are +V±I, –V±I — sink when DUT in LRS pushes current back or when compliance limits. Full Source-I/Measure-V is not required for V1 primary mode; Source-I is *available* as secondary mode if DAC/ADC ranges allow (nice-to-have). No weakening of REQ-SRC-005.

### CAUTION 2 — 100 mV burden is not harmless

100 mV = 5% @2 V, 16.7% @0.6 V. V1 adopts **range-dependent effective burden** proposal from `SHUNT_RANGE_TRADEOFF.md`: keep 100 mV on 10 mA–10 µA, **50 mV on 1 µA, 25–50 mV on 100 nA** (trade Johnson 3.16× noisier but burden halves). Burden is **outside** SENSE, so Kelvin does not eliminate it — it is budgeted as headroom (see `SOURCE_HEADROOM_THERMAL.md`). Low-side placement does not magically correct it; it simply makes it manageable.

### CAUTION 3 — Compliance per segment/polarity

Hardware limiter has separate ISRC/ISNK control voltages (LT1970A pin pair) + per-range compliance DAC values. Firmware can program +sweep limit, –sweep limit, read limit, disabled independently. Not hard-coded SET=compliance.

### CAUTION 4 — Kelvin not tied to 10 kΩ threshold

Kelvin is required for **lead-drop + calibration**, not resistance threshold. 4-wire eliminates `R_lead` (≈0.1–1 Ω) error for LRS and is mandatory for calibration (<0.1 Ω). Analysis in `KELVIN_SENSE_ARCHITECTURE.md`.

### CAUTION 5 — Grounding not pre-decided

`GROUNDING_AND_RETURN_PATHS.md` compares single continuous plane with partitioning vs split vs star vs isolated analog domain — recommends **single continuous ground/reference plane with physical partitioning + single AGND/DGND bridge + partitioned current claims** (not generic star), analyzed via return paths (DAC ref, ADC ref, MCU, relay, USB, FORCE_LO).

## 3. Decisions for Phase 3 (SELECTED FOR PHASE 3 vs DEFER)

| Block | Selection for Phase 3 | Verdict |
|-------|-----------------------|---------|
| Source stage | **LT1970A primary** (500 mA, ±% limiter, LTspice model, DFN) + **precision+buffer composite (OPA140/ADA4522+discrete) alternate** | SELECTED FOR PHASE 3 |
| Current sense | **Hybrid**: shunts 10 mA→1 µA + TIA *provision* for 100 nA (shunt ships REV-A, TIA footprint) — low-side, 50–100 mV FS range-dependent | SELECTED FOR PHASE 3 |
| Shunt location | **Low-side** (ground-ref, outside SENSE) | SELECTED |
| Compliance | **Dual continuous (LT1970A limit) + independent fast trip (TLV3501 latch) + SOA 50 mW** — per-segment/polarity | SELECTED FOR PHASE 3 |
| Kelvin | **SENSE feedback at DUT**, burden outside, open-sense pull-up + comparator fallback | SELECTED |
| DAC | **AD5764-class (±10 V, ±1 LSB INL) preferred over AD5686R** (AD5686R post-cal @1 V fails headroom -11%) — needs sim; AD5686R kept as alternate | DEFER (sim required) |
| Reference | **Shared vs separate deferred** — ADR4525 vs LTC6655/REF50xx branch to be sized after DAC choice | DEFER |
| ADC | **ADS1262 vs AD7175 class** (noise-free bits at 50 Hz, PGA, latency) — ADS1262 keeps if noise meets 100 nA @10 Hz; AD7175 as alternate | DEFER |
| Range switch | **Reed for 100 nA/1 µA, PhotoMOS/signal relay for higher** — not one tech for all | SELECTED |
| Grounding | **Single continuous plane, partitioned, single bridge** | SELECTED |
| Isolation | **Onboard isolator optional footprint, external adaptor recommended** (not required for V1) | CLASSIFIED |
| Guard | **Reserved copper + stitching, optional driven amp footprint on SENSE_HI** | PROVISIONED |
| Power | **Ext ±12 V → LDO domains** (source ±10, precision +5, digital 3.3) | CONCEPT SELECTED |
| MCU | **STM32G431 meets SPI/USB/timers but simpler STM32G474/RP2040 alternates to compare** | DEFER |

## 4. Block responsibilities

- **Host:** Python + SCPI-like, CSV/raw export.
- **USB:** CDC/TMC; isolator footprint (ADuM3160-class) but direct USB ships REV-A with ground-loop warning.
- **MCU:** SPI×2 (DAC+ADC), I²C/SPI for sensor, GPIO 12 (relays+enable+fault), watchdog, timers for sweep dwell.
- **DAC:** Two channels minimum: Source V, Compliance I (per polarity). Quad DAC (AD5686R/AD5764 quad) leaves spare for compliance V if I-source added.
- **Source stage:** LT1970A with ISRC/ISNK programming via DAC + enable pull-down safe default.

Traceability: `docs/architecture/REQUIREMENTS_TRACEABILITY.md` extended in Phase 2.
