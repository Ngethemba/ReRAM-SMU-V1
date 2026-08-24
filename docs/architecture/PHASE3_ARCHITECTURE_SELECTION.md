# Phase 3 Architecture Selection — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 3 Gate 6
**Date:** 2026-08-24
**Status:** SELECTED FOR SCHEMATIC — conditional
**Evidence:** simulation/results/phase3/PHASE3_RESULTS.md + gate1-6, simulation/phase3/MODEL_LIMITATIONS.md, docs/calculations/PHASE3_ERROR_BUDGET.md

## Verdict Summary

| Candidate | A LT1970A direct | B ADA4522+BJT buffer | C Outer ADA4522/OPA140 + LT1970A booster |
|-----------|------------------|----------------------|------------------------------------------|
| **Verdict** | **SELECT (primary)** | **KEEP AS FALLBACK** | **REQUIRES PROTOTYPE** |
| DC @2V/1kΩ cal | 12µV | 0.7µV | 4µV |
| Load reg 100Ω↔1MΩ | 13µV | 3.3µV | 6µV |
| Cap 10nF PM / OS | 50° / 6.5% PASS | 60° /3.2% pref | 57° analytic /16.6% marginal ngspice |
| Kelvin 10Ω lead | PASS 5µV after R_iso (vs 20mV naive) | PASS | PASS |
| Compliance takeover | 4µs takeoff, 1% separate ISRC/ISNK, 20µs t_reg PASS | coarse >10µs FAIL 4µs envelope | 1% ±1% PASS 25µs |
| Source/sink symmetry | ±1% matched | ±3% β mismatch | ±1% inherits LT1970A |
| Disable | 0.6mA Hi-Z 10µs ENABLE+TSD | µA leak when off (needs switch) | inherits LT1970A |
| Lifecycle | ADI Active single TSSOP-20 pad, risk monitor LT1970(2%) fallback | multi-source jelly-bean | hedged multi-source |
| Effort | lowest | buffer poles hardest without BUF634 | highest nested Miller/lead-lag |

At least one candidate passes DC+cap+Kelvin+compliance+stability >45° → Gate O PASS.

## Component Selection Gate

| Block | Primary (SELECTED FOR SCHEMATIC) | Alternate | Verdict |
|-------|----------------------------------|-----------|---------|
| **DAC** | **AD5764** direct bipolar ±10V 20V 305µV LSB, ±11.4-16.5V via raw ±12V Option A (0.6V margin), LTC6655LN 2.5V / ADR4525 B-grade | AD5686R 0-5V→×2 with 0.01% 10ppm RG + LTC6655LN (0.1% REJECT) | SELECT AD5764, fallback AD5686R 0.01% |
| **ADC** | **AD7175-8-class** 250kSPS 20µs/chan Sinc5+Sinc1 24b p-p @20SPS 120dB (FAST 10-20ms + autorange) | ADS1262 130dB Sinc4 20SPS single-cycle 50ms (NORMAL 50-100ms, LOW NOISE 200ms-1s) | SELECT AD7175 primary, ADS1262 fallback |
| **Reference** | **LTC6655LN-2.5** 0.775µV p-p 0.8ppm (primary DAC) + ADR4525 2.5V B 2ppm (ADC) separate | Shared vs separate branch | As above |
| **Voltage-sense buffer** | **OPA140-class JFET** 10pA max 5.1nV 0.8fA, 11MHz, input C 2-5pF, >10GΩ | ADA4522 50pA (shunt loop ok, DUT sense no) / OPA828 / ADA4625 | SELECT OPA140-class JFET |
| **Current-sense amp** | **ADA4522** zero-drift 5µV max for 25/50mV shunts (shunt loop) + **OPA140 JFET** for 1M/100k high-R (Ib 10pA) | OPA189 14MHz alt, LTC2057 HV | Hybrid role-dependent per REQ-MEAS-008 |
| **Comparator** | **TLV3501-class** as **emergency supervisor** 4.5ns 6.5mV max 6mV hyst, threshold 120-150% range-dependent (150%@1mA,130%@10µA,120%@100nA) | LT1716/MAX999 | Emergency only, not precision |
| **Output amp** | **LT1970A** (Candidate A) | ADA4522+BJT buffer (B fallback), outer+LT1970A (C prototype) | As above |

No procurement authorization — schematic may begin with primary selections, alternates kept for second-source.

## Schematic-Ready Partition

- Power: Option A raw ±12V bench for LT1970A/AD5764; +5V prec via LT3045/LT1763 + LC π + RC for AD7175/refs; negative via LT1964-class if AD5764 regulated; supervisor 10k pulldown + 200ms POR (Test L)
- Source: LT1970A TSSOP-20 pad with FILTER 220pF, Rsense 10Ω high-side Kelvin + R_iso 33Ω after pick (+10Ω Rs variant for compliance decade), Kelvin SENSE_HI/LO via OPA140 buffers (>10GΩ), diff amp to LT1970A +IN
- Compliance: LT1970A ISRC/ISNK 4µs + separate TLV3501 window vs DAC_trip (120-150% multiples), SOA 50mW hyperbola, Vc<60mV nonlinear floor documented, coercion firmware tightest FS≥Icomp
- Kelvin/Guard: SENSE buffers >10GΩ, feedback after R_iso (IR-11), switched open-sense ADG1419 behind 10MΩ before ON, latch OFF, guard ring top no-mask stitched inner 5mm, driven-guard footprint C prototype only
- Measurement: shunts 2.5/25/500/5k/100k/1M per SHUNT_RANGE_TRADEOFF §2.4, reed 1pA for 100nA/1µA, PhotoMOS/signal for higher, break-23.5ms seq (K), PGA per-range hybrid (25mV→3.13× @PGA32, etc.), strategy B midscale VCM2.5V + PGA32
- Ground: One continuous plane, placement/return-current/routing/decoupling, no etched split, tie at ADC measurement point
- Isolation: footprint optional, not stuffed REV-A

## Requirement Feedback

No requirement revision needed in Phase 3 — tiered compliance already DEC-024. If 0.1% universal re-established, Candidate C becomes mandatory (already provisioned).

## Next: Phase 4 — Schematic Architecture & KiCad Capture Preparation (on authorization)

