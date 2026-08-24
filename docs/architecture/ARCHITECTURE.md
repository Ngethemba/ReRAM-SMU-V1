# Architecture — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 Architecture & Candidate Component Verification  
**Date:** 2026-08-24 (corrected 2026-08-24 per IR-01..IR-16)  
**Status:** `PHASE 2 — CORRECTED / READY FOR PHASE 3` (no schematic/PCB/BOM, conceptual). Cautions 1–5 addressed; independent review IR-01..IR-16 reconciled; decisions require Phase 3 simulation gates A–O.

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
  FH --> SHUNT[Current-sense matrix\nLow-side shunts 2.5Ω–1MΩ\n(range-dependent 25/50/100 mV FS per SHUNT_RANGE_TRADEOFF §2.4)\nReed for 1µA/100nA]
  SHUNT --> FL[FORCE_LO\n→ ±12V bulk GND]
  DUT[DUT\nReRAM cell] --- FH
  DUT --- FL
  DUT --- SH[SENSE_HI via high-Z buffer\n>10 GΩ, ≤10 pA]
  DUT --- SL[SENSE_LO via high-Z buffer]
  SH --> VSENSE[Voltage sense\nHi-Z diff AFTER buffer\nAttenuator → ADC]
  SL --> VSENSE
  VSENSE --> ADC
  SHUNT --> ISENSE[Current sense\nLow-side diff (ground-ref)\nZero-drift amp; bipolar ±FS]
  ISENSE --> ADC
  DAC --> COMP[Compliance controller\nDual: continuous limit (LT1970A\nISRC/ISNK, 4mV floor + range coercion)\n+ fast emergency TLV3501 latch\n(<5 µs, loose 120-150% thr) + SOA 50 mW]
  COMP --> SRC
  COMP -.-> ADC
  REF[Voltage ref\nADR4525 or LTC6655/REF5040\nShared vs separate TBD] --> DAC & ADC
  PWR[Power tree\nExt ±12 V → LDOs:\n±12 raw for power stage (Option A)\n+5 prec, 3.3 dig; ±11.4V req for AD5764;\nNeg rails via LT1964-class (not LT1763)] --> SRC & DAC & ADC & REF & MCU
  TEMP[Temp sensors\nOutput stage, shunt block, ref] --> MCU
```

**Key placements (CAUTION 2/4 + IR-01..04,11 answered):**

- **Shunt:** **Low-side, between FORCE_LO and power GND**, outside DUT-sense loop (SENSE encloses DUT only, not shunt). Canonical burden table is `SHUNT_RANGE_TRADEOFF.md` §2.4 (range-dependent 25/50/100 mV FS, 2.5 Ω–1 MΩ). Source loop headroom equation (IR-11): `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD`. Kelvin does not eliminate burden — it prevents it becoming DUT error by forcing headroom. Burden-corrected mode (SENSE encloses DUT+shunt) is diagnostic only, not default.
- **DUT relative to shunts:** DUT sits between FORCE_HI (source) and FORCE_LO side of shunt. Current flows FH→DUT→FL→shunt→GND, so measured current equals DUT current.
- **Source-loop feedback point:** **Remote SENSE via high-Z buffers (≥10 GΩ, ≤10 pA, IR-02) — differential SENSE_HI/SENSE_LO after buffering drives source error amp (not LT1970A internal SENSE+/− alone).** LT1970A internal SENSE+/− is the compliance sense across Rsense; SMU Kelvin SENSE_HI/LO is the voltage-measurement path. FORCE tracks buffered SENSE with gain, correcting lead drops.
- **Compliance-loop sensing point:** **Low-side shunt voltage** (same ISENSE) vs compliance DAC reference — independent of SENSE, so compliance regulates I irrespective of V_DUT. Per-segment/polarity programmable (DAC channels). LT1970A floor 4 mV → I_min ≈4% FS (100 mV) or 16% (25 mV); minimum 0.1% only via precision outer loop (Candidate C) or range coercion (IR-01).
- **Protection-loop sensing point:** Same shunt + separate fast emergency comparator (TLV3501, Vos 6.5 mV max, hyst 6 mV) vs trip reference at 120–150% Icomp — **supervisor, not precision comparator** (IR-08) — independent latch, survives MCU halt.

## 2. Caveats addressed

### CAUTION 1 — Bipolar vs full 4-quadrant

Phase 1 promoted REQ-SRC-005 to 4-quad. Architecture is **true bipolar Source-V/Measure-I with controlled sink (±5 V·±10 mA, 50 mW)**, not arbitrary I-source arbitrary Q. For ReRAM workflows (0→+Vmax→0→–Vmax→0), required behaviors are +V±I, –V±I — sink when DUT in LRS pushes current back or when compliance limits. Full Source-I/Measure-V is not required for V1 primary mode; Source-I is *available* as secondary mode if DAC/ADC ranges allow (nice-to-have). No weakening of REQ-SRC-005.

### CAUTION 2 — 100 mV burden is not harmless

100 mV = 5% @2 V, 16.7% @0.6 V. Canonical burden is **range-dependent 25/50/100 mV FS** from `SHUNT_RANGE_TRADEOFF.md` §2.4 (single source of truth per IR-05: 25 mV on 10 mA/1 mA, 50 mV on 100 µA/10 µA, 100 mV on 1 µA/100 nA). Burden is **outside** SENSE — Kelvin does not eliminate it — canonical equation `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11). Low-side placement does not magically correct it; it is budgeted as headroom (see `SOURCE_HEADROOM_THERMAL.md`). Reversed ordering (100 mV on mA, 25 mV on nA) would be opposite of optimal and is **rejected**.

### CAUTION 3 — Compliance per segment/polarity

Hardware limiter has separate ISRC/ISNK control voltages (LT1970A pin pair) + per-range compliance DAC values. Firmware can program +sweep limit, –sweep limit, read limit, disabled independently. Not hard-coded SET=compliance.

### CAUTION 4 — Kelvin not tied to 10 kΩ threshold

Kelvin is required for **lead-drop + calibration**, not resistance threshold. 4-wire eliminates `R_lead` (≈0.1–1 Ω) error for LRS and is mandatory for calibration (<0.1 Ω). Analysis in `KELVIN_SENSE_ARCHITECTURE.md`.

### CAUTION 5 — Grounding not pre-decided

`GROUNDING_AND_RETURN_PATHS.md` compares grounding topologies — recommends **one continuous reference plane with no etched AGND/DGND split** (IR-13 corrected wording) — separation by placement, local return-current control, routing discipline, and decoupling; analyzed via return paths (DAC ref, ADC ref, MCU, relay, USB, FORCE_LO).

## 3. Decisions for Phase 3 (SELECTED FOR PHASE 3 vs DEFER)

| Block | Selection for Phase 3 | Verdict |
|-------|-----------------------|---------|
| Source stage | **LT1970A primary** (500 mA, ±% limiter, LTspice model, 4 mV floor, range coercion — IR-01) + **precision+buffer composite alternate + Candidate C outer-loop+LT1970A booster (DEC-025)** | SELECTED FOR PHASE 3 |
| Current sense | **Hybrid**: shunts 10 mA→1 µA (2.5 Ω–100 kΩ, 25/50/100 mV FS per SHUNT_RANGE_TRADEOFF §2.4) + TIA *provision* for 100 nA | SELECTED FOR PHASE 3 |
| Shunt location | **Low-side** (ground-ref, outside SENSE) — Kelvin SENSE_HI/LO are high-Z buffered (IR-02), burden equation `V_FORCE=V_DUT+V_SHUNT+I·R_LEAD` (IR-11) | SELECTED |
| Compliance | **Dual: continuous LT1970A limit (with 4 mV floor/coercion IR-01) + independent fast emergency TLV3501 supervisor at 120–150% Icomp + SOA 50 mW** — per-segment/polarity; upstream/downstream C distinction IR-14 | SELECTED FOR PHASE 3 |
| Kelvin | **SENSE via high-Z buffers (>10 GΩ, ≤10 pA) before attenuation; burden outside; switched open-sense disconnect (IR-02/03/04)** | SELECTED |
| DAC | **AD5686R vs AD5764 (±10 V 20 V span, LSB 305.2 µV, ±11.4 V supplies — IR-06/07) — no ±5 V mode; INL in volts equal; do not promote on INL alone** | DEFER (Phase 3 N,M) |
| Reference | **Shared vs separate deferred** — ADR4525 vs LTC6655/REF50xx branch to be sized after DAC choice | DEFER |
| ADC | **ADS1262 vs AD7175 class** with bipolar front-end A/B/C per IR-12 (ADS1262 vs AD7175 ± range, CM, PGA, zero-crossing) | DEFER (Phase 3 G) |
| Range switch | **Reed for 100 nA/1 µA, PhotoMOS/signal relay for higher** — break-before-make, relay faults per Phase 3 K | SELECTED |
| Grounding | **One continuous reference plane, no etched AGND/DGND split** (IR-13) | SELECTED |
| Isolation | **Onboard isolator optional footprint, external adaptor recommended** (not required for V1) | CLASSIFIED |
| Guard | **No driven guard stuffed; passive keepout/grounded shield; optional driven-guard footprint (powered from rails, IR-10)** | PROVISIONED |
| Power | **Ext ±12 V → Option A raw ±12 for power stage + LT1763 positive / LT1964-class negative regulators (IR-07)** | CONCEPT SELECTED |
| MCU | **STM32G431 meets SPI/USB/timers but simpler STM32G474/RP2040 alternates to compare** | DEFER |

## 4. Block responsibilities

- **Host:** Python + SCPI-like, CSV/raw export.
- **USB:** CDC/TMC; isolator footprint (ADuM3160-class) but direct USB ships REV-A with ground-loop warning.
- **MCU:** SPI×2 (DAC+ADC), I²C/SPI for sensor, GPIO 12 (relays+enable+fault), watchdog, timers for sweep dwell.
- **DAC:** Two channels minimum: Source V, Compliance I (per polarity). Quad DAC (AD5686R/AD5764 quad) leaves spare for compliance V if I-source added.
- **Source stage:** LT1970A with ISRC/ISNK programming via DAC + enable pull-down safe default.

Traceability: `docs/architecture/REQUIREMENTS_TRACEABILITY.md` extended in Phase 2.
