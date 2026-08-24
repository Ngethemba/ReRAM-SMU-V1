# Phase 2 Decision Matrix — ReRAM-SMU V1

**Date:** 2026-08-24  
**Gate:** SELECTED FOR PHASE 3 = sufficient evidence to simulate; FINAL requires Phase 3 sim gates.

| # | Decision | Options scored | Verdict | Why | Needs sim? |
|---|----------|---------------|---------|-----|------------|
| 1 | Current measurement topology | A shunt, B TIA, C hybrid (shunt 10 mA→1 µA + TIA 100 nA) | **C hybrid (shunt ships REV-A, TIA footprint)** | Shunt simple/stable to 1 µA; TIA burden ~20 µV vs 100 mV helps 100 nA guard/leakage and settling ÷Aol | Yes — stability with Rf\|\|Cf |
| 2 | Shunt location | high-side, low-side, floating | **Low-side (outside SENSE)** | Ground-ref amp without high CM, guard simple, compliance ground-ref; SENSE encloses DUT only | No |
| 3 | Burden philosophy | 25/50/100 mV and range-dependent | **Range-dependent 100 mV (10 mA–10 µA) + 50 mV (1 µA) + 25–50 mV (100 nA)** | 100 mV =5% @2 V/16% @0.6 V not harmless — halving burden on low-V ranges costs 3.16× Johnson but halves DUT error | Yes — headroom vs noise |
| 4 | Output-stage architecture | LT1970A, OPA548, precision+discrete, composite | **LT1970A primary + precision+discrete alternate** | LT1970A: ±500 mA, 1% limiter, separate ISRC/ISNK, LTspice model, DFN; OPA548 single-supply not bipolar without extra rails; precision+discrete higher BOM but lower Vos | Yes — cap load |
| 5 | Compliance architecture | A limiter only, B external loop, C trip+coarse, D dual | **D dual continuous+trip/SOA** (LT1970A limit + TLV3501 latch + 50 mW hyperbola) | Per-segment/polarity programmable, hardware independence, survive MCU halt | Yes — transient |
| 6 | Stored-energy management | low C, damping R, isolation R, active discharge | **Low output C (≤10 nF) + series 10 Ω isolation + damping RC** | E=0.5CV²: 10 nF@5 V=125 nJ dominates filament; 100 nF cable=1.25 µJ → limit cable length/C | Yes |
| 7 | DAC class | AD5686R (16-bit 2 LSB INL), AD5764 (±10 V ±1 LSB), AD5791 20-bit | **AD5764-class preferred** (INL ±1 LSB vs AD5686R post-cal @1 V headroom -11%) | 10 V span → LSB 153 µV @16-bit =1.5 mV step 1.5% → 16-bit adequate but INL matters; AD5764 (±10 V, ±1 LSB) gives margin | Yes — error budget |
| 8 | Reference | ADR4525, LTC6655, REF50xx | **Deferred** — shared vs separate after DAC choice | Correlation: shared ref cancels DAC/ADC drift ratiometrically; separate gives absolute accuracy | Yes |
| 9 | Precision amps | ADA4522 (zero-drift 55 V), OPA189/188, ADA4528, OPA140 (JFET), LTC2057 | **Role-dependent: ADA4522-2 for shunt sense, OPA140 for voltage sense (Ib), ADA4528 for DAC conditioning if needed** | Not one amp everywhere; Ib matters for high-Z | No |
| 10 | ADC class | ADS1262 (38 kSPS), ADS124S08, AD7175 (±1 ppm INL), AD7124 | **ADS1262 vs AD7175** (both PGA, 50 Hz rejection) | ADS1262 32-bit word ≠ performance; compare RMS/noise-free at 50 Hz | Yes — noise @NPLC |
| 11 | Range-switch tech | reed, signal relay, PhotoMOS, CMOS MUX | **Reed 100 nA/1 µA + PhotoMOS/signal relay for 10 µA→10 mA** | Off-leakage: CMOS MUX 100 pA–nA fails 100 nA; reed ~1 pA | No |
| 12 | Kelvin loop | FORCE vs SENSE feedback, burden placement | **SENSE feedback at DUT, burden outside, open-sense pull-up + fallback** | Kelvin correctness: V_DUT = V_SENSE, not V_FORCE - V_burden | Yes — stability |
| 13 | Grounding | single plane partitioned, split, star, isolated | **Single continuous plane, partitioned, single bridge** | Return-path analysis > generic “star best”; split invites antenna | No |
| 14 | Isolation | direct USB, external isolator, onboard isolated DC/DC | **Optional footprint, external adaptor recommended, not required** | Ground loops via scope/PSU/DUT; direct USB ships with warning | No |
| 15 | Guard provision | reserved copper, driven guard | **Reserved copper+stitching, optional driven guard on SENSE_HI buffer** | Not arbitrary node; 100 nA needs it, but V1 not electrometer | No |
| 16 | Connector | banana, BNC, SMA, triax | **Banana 4 mm + BNC provision** (Kelvin clip via banana, shield via BNC) | Triax is V2; banana robust, low leakage with guard | No |
| 17 | Power tree | ±12 V ext → LDO domains | **±12 V → ±10 (LT1763/3045), +5 prec, 3.3 dig** | Headroom 7 V to ±5 V +100 mV burden | No |
| 18 | Thermal | Pd vs θJA, sensor count | **Pd 70–170 mW worst-case, ΔT 6–15 °C, no heatsink** | DUT 50 mW ≠ amp Pd | No |
| 19 | MCU | STM32G431 vs simpler G474/RP2040 | **STM32G431 provisional, G474/RP2040 alternates** — needs SPI×2, USB FS, timers, GPIO 12, watchdog | **Deferred** — not perf-critical | No |
| 20 | Safe state | pull-down vs supervisor | **Enable pull-down (output relay open) + supervisor + DAC safe code** | Hardware default disabled on power/ramp/reset/hang/USB disconnect | No |

**Overall:** 14 SELECTED/PROVISIONED for Phase 3, 6 DEFERRED pending sim (DAC/ref/ADC decisions need error-budget sim).
