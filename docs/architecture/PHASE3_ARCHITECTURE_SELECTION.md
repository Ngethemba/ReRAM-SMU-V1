# Phase 3 Architecture Selection — ReRAM-SMU V1 (Corrected per P3IR-01..08)

**Project:** ReRAM-SMU V1 — Phase 3 Gate 6 + Corrective Review R1–R6
**Date:** 2026-08-24 (corrected 2026-08-24)
**Status:** CONDITIONAL — READY FOR SCHEMATIC WITH PROVISIONS (per PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md)
**Evidence:** simulation/results/phase3/PHASE3_RESULTS.md + gate1-6 + simulation/results/phase3/PHASE3_CORRECTIVE_RESULTS.md (R1–R6), simulation/phase3/MODEL_LIMITATIONS.md, docs/calculations/PHASE3_ERROR_BUDGET.md, docs/research/PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md

## Verdict Summary

| Candidate | A LT1970A direct | B ADA4522+BJT buffer | C Outer ADA4522/OPA140 + LT1970A booster |
|-----------|------------------|----------------------|------------------------------------------|
| **Verdict** | **SELECT (primary)** | **KEEP AS FALLBACK** | **REQUIRES PROTOTYPE** |
| DC @2V/1kΩ cal | 12µV | 0.7µV | 4µV |
| Load reg 100Ω↔1MΩ | 13µV | 3.3µV | 6µV |
| Cap 10nF PM / OS | 50° / 6.5% PASS (behavioral transient; 16.2% analytic historical superseded, see P3IR-05) | 60° /3.2% pref | 57° analytic /16.6% marginal ngspice |
| Kelvin 10Ω lead | PASS 5µV after R_iso (vs 20mV naive) | PASS | PASS |
| Compliance takeover | 4µs takeoff, 1% separate ISRC/ISNK, 20µs t_reg PASS (with shared canonical Rsense — fixed 10Ω fails <600µA, corrected per P3IR-01) | coarse >10µs FAIL 4µs envelope | 1% ±1% PASS 25µs |
| Source/sink symmetry | ±1% matched | ±3% β mismatch | ±1% inherits LT1970A |
| Disable | 0.6mA Hi-Z 10µs ENABLE+TSD | µA leak when off (needs switch) | inherits LT1970A |
| Lifecycle | ADI Active single TSSOP-20 pad, risk monitor LT1970(2%) fallback | multi-source jelly-bean | hedged multi-source |
| Effort | lowest | buffer poles hardest without BUF634 | highest nested Miller/lead-lag |

At least one candidate passes DC+cap+Kelvin+compliance+stability >45° → Gate O PASS.

## Component Selection Gate (Corrected per P3IR-03/04/06/07)

| Block | Primary (SELECTED FOR SCHEMATIC) | Alternate | Verdict |
|-------|----------------------------------|-----------|---------|
| **DAC** | **AD5764 @5V ref (LTC6655-5.0 / ADR435B 5V) ±10V span 20V 305µV LSB, half-codes for ±5V (±1LSB guaranteed at 5V), ±11.4-16.5V via raw ±12V Option A (0.6V margin) — P3IR-04** | AD5686R 0-5V→×2 with 0.01% 10ppm RG + LTC6655LN-2.5 (0.1% REJECT); DAC-B 2.5V full-span characterized not guaranteed | AD5764 5V ref SELECT, fallback AD5686R 0.01% |
| **ADC** | **ADS1262** 130dB Sinc4 20SPS single-cycle 50ms (NORMAL/LOW), internal PGA 1–32 (+ small 3.13× pre-gain for 25mV) — **PRIMARY (P3IR-03)** | AD7175-8-class 250kSPS 20µs/chan Sinc5+Sinc1 (needs external 100/50/25× per-range diff amp) — ALTERNATE with footprint, not invented unreviewed | ADS1262 PRIMARY (corrected), AD7175 ALTERNATE |
| **Reference DAC** | **LTC6655-5.0** (DAC-A spec) or ADR435B 5V | — | Above |
| **Reference ADC** | **LTC6655LN-2.5** 0.775µV p-p 0.8ppm + ADR4525 2.5V B 2ppm separate | Shared vs separate branch | — |
| **Voltage-sense buffer** | **OPA140-class JFET** 10pA max 5.1nV 0.8fA, 11MHz, input C 2-5pF, >10GΩ — **Guaranteed ≤100MΩ (<1%), Characterized 1GΩ@0.5–1V (<2% raw, <0.5% cal), Exploratory 1GΩ@0.1V (P3IR-07)** | ADA4522 50pA (shunt loop ok, DUT sense no) / OPA828 / ADA4625 | SELECT OPA140-class JFET |
| **Current-sense amp** | **ADA4522** zero-drift 5µV max for 25/50mV shunts (shunt loop) + **OPA140 JFET** for 1M/100k high-R (Ib 10pA) | OPA189 14MHz alt, LTC2057 HV | Hybrid role-dependent per REQ-MEAS-008 |
| **Comparator** | **TLV3501-class** as **emergency supervisor** 4.5ns 6.5mV max 6mV hyst, threshold 120-150% range-dependent (150%@1mA,130%@10µA,120%@100nA) | LT1716/MAX999 | Emergency only, not precision |
| **Output amp** | **LT1970A** (Candidate A, shared canonical Rsense — fixed 10Ω superseded per P3IR-01) | ADA4522+BJT buffer (B fallback), outer+LT1970A (C prototype) | Behavioral simulated — vendor model + prototype pending (P3IR-05) |

No procurement authorization — schematic may begin with primary selections, alternates kept for second-source.

## Schematic-Ready Partition (Corrected per P3IR-01..08)

- Power: Option A raw ±12V bench for LT1970A/AD5764 @5V ref (LTC6655-5.0, ±11.4V min 0.6V margin); +5V prec via LT3045/LT1763 + LC π + RC for ADC/refs; negative via LT1964-class if regulated; supervisor 10k pulldown + 200ms POR (Test L)
- Source: LT1970A TSSOP-20 pad with FILTER 220pF, **shared low-side canonical shunt (2.5Ω–1MΩ) as LT1970 Rsense via Kelvin (SENSE+ to FORCE_LO node, SENSE− to GND) — fixed 10Ω high-side placeholder superseded per P3IR-01** + R_iso 33–47Ω after pick (sweet spot 33–47Ω; 10Ω too low, 100Ω too high, P3IR-02), Kelvin SENSE_HI/LO via OPA140 buffers (>10GΩ, see P3IR-07 regions), diff amp to LT1970A +IN
- Compliance: LT1970A ISRC/ISNK 4µs + separate TLV3501 window vs DAC_trip (120-150% multiples, Vos 6.5mV max loose threshold only), SOA 50mW hyperbola, Vc<60mV nonlinear floor, **range coercion on shared shunt** (tightest FS≥Icomp, Vc≥60mV ideal ≥0.5V)
- Kelvin/Guard: SENSE buffers >10GΩ, feedback after R_iso, **switched open-sense via reed relay (<1pA, not ADG1419 100pA — P3IR-06)** before ON latch OFF, guard ring top no-mask stitched inner 5mm, driven-guard footprint C prototype only
- Measurement: shunts 2.5/25/500/5k/100k/1M per SHUNT_RANGE_TRADEOFF §2.4, reed 1pA for 100nA/1µA, PhotoMOS/signal for higher, break-23.5ms seq (K), **ADS1262 internal PGA 1–32 (+3.13× pre-gain for 25mV) primary; AD7175 external 100/50/25× footprint provisioned (P3IR-03)**, strategy B midscale VCM2.5V
- Capacitance: **C_DOWNSTREAM ≤80pF@5V/160pF@5V/500pF@2V (direct dump, recipe-dependent); C_UPSTREAM ≤1nF@5V/4.7nF@2V (shared dump 95.5%@1kΩ/47Ω, not free — P3IR-02); Cf 33pF compensation not counted**
- Ground: One continuous plane, placement/return-current/routing/decoupling, no etched split, tie at ADC measurement point
- Isolation: footprint optional, not stuffed REV-A
- Stability: **Behavioral 6.5% OS @10nF 50° PASS — 16.2% analytic historical superseded; vendor LTspice macro-model + prototype required for final (P3IR-05)**

## Requirement Feedback (Corrected)

Phase 3 Corrective Review added 6 gates R1–R6 (P3IR-01..08). R1–R4,R6 PASS after corrections; R5 CONDITIONAL (behavioral PASS, vendor-model + prototype required). DEC-028 (shared Rsense), DEC-029 (reed), DEC-030 (1GΩ regions), DEC-027 amended (ADS1262 primary, AD5764 5V ref).

## Next: Phase 4 — Schematic Architecture & KiCad Capture Preparation (CONDITIONAL — with provisions, on authorization)

Schematic provision checklist per corrective review: shared canonical Rsense Kelvin, R_iso 33–47Ω options + Cf 33pF lead-lag, LTC6655-5.0 for DAC 5V ref, ADS1262 primary pads + AD7175 external-gain footprint, reed relay for open-sense, OPA140 buffer with T-monitor for 1GΩ cal region, C_DOWNSTREAM budget enforcement, vendor LTspice validation plan.

