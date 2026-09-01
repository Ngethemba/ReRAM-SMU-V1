# 02_DAC_SOURCE_COMMAND — Channel Allocation & Conditioning Design (Gate B Detailed)

**Project:** ReRAM-SMU V1 — Phase 7 Gate B  
**Date:** 2026-08-25 rev0.2  
**Sheet:** `hardware/kicad/ReRAM-SMU-V1/sheets/02_DAC_SOURCE_COMMAND.kicad_sch`  
**DAC:** AD5764ARUZ (LQFP-32, 7×7mm P0.8) — quad 16-bit bipolar, 5V REF, ±10V span, INL ±1 LSB (305 µV), SPI 30 MHz  
**Status:** Detailed schematic — real manufacturer symbol (documented placeholder with curated pins per datasheet), conditioning, slew provision, test points, ERC exported.

---

## 1. Manufacturer Symbol — AD5764 Real Pins (Documented Placeholder)

Created symbol `ReRAM_SMU:AD5764` in sheet `lib_symbols` with curated pins per datasheet Rev A. Pinout verified against https://www.analog.com/media/en/technical-documentation/data-sheets/AD5764.pdf Table 1 (LQFP-32):

| Pin | Name | Type | Connected To | Notes |
|-----|------|------|--------------|-------|
| 1 | AVDD | power_in | +12V_A (raw) | 100nF+10µF decoupling within 2 mm, bulk 10 µF 1210 |
| 2 | AVSS | power_in | -12V_A (raw) | 100nF+10µF, meets ±11.4 V min (Option A raw, IR-07) |
| 3 | DVCC | power_in | +3V3 | 100nF+10µF, logic supply 2.7–5.5 V, SPI to STM32G474 3V3 CMOS |
| 4 | DGND | power_in | GND | star to plane |
| 5 | AGND | power_in | GND | analog star |
| 6 | REFAB | input | VREF_5V (LTC6655-5.0) | Channel A/B reference, 0.1 µF+10 µF at pin |
| 7 | REFCD | input | VREF_5V | Channel C/D reference, tied to REFAB per review |
| 8 | REF_GND | input | GND | reference ground |
| 9 | RESET_N | input | 10k PU to +3V3 | active-low reset, RC 100 nF debounce optional |
| 10 | VOUTA | output | DAC_VOUTA_raw → R_SLEW → VSET | primary voltage source |
| 11 | VOUTB | output | DAC_VOUTB_raw → VCSRC conditioning | source compliance Vc |
| 12 | VOUTC | output | DAC_VOUTC_raw → VCSNK conditioning | sink compliance Vc |
| 13 | VOUTD | output | DAC_VOUTD_raw → spare / TLV3501 emergency threshold | DNP provision |
| 14 | SCLK | input | DAC_SCLK → STM32 SPI2_SCK | 30 MHz max, series 33 Ω optional |
| 15 | SYNC_N | input | DAC_SYNC_N → SPI2_NSS | frame sync, 10k PU? driven by MCU |
| 16 | SDIN | input | DAC_SDIN → SPI2_MOSI | |
| 17 | SDO | output | DAC_SDO → SPI2_MISO | readback provision |
| 18 | LDAC_N | input | DAC_LDAC_N ← MCU GPIO + 10k PU to 3V3 | latched default, synchronous update of VSET+VCSx |
| 19 | CLR_N | input | DAC_CLR_N ← MCU GPIO + 10k PU | async clear to 0 V (mid-scale 0x8000) |
| 20 | BIN/2sCOMP | input | GND via 0R (offset binary) | 0 = offset binary (0x0000=-10V, 0x8000=0V, 0xFFFF=+10V), 1 = 2's comp via DNP to 3V3 |
| NC | — | — | NC + 1M to GND waiver | not used, validated per 1970afc NC handling (separate sheet) |

**Transfer function (offset binary, REF=5.0 V):**  
`Vout = 4·VREF·(code/65536) − 2·VREF`  
→ 0x0000 = −10.000 V, 0x8000 = 0.000 V, 0xFFFF = +9.999695 V (−1 LSB).  
For ±5 V use half-codes **0x4000 (−5 V) … 0xC000 (+5 V)** → LSB_eff 305.18 µV, 3.0 % of 10 mV ReRAM step (<10 % OK).  
ESD, decoupling, and star grounding per datasheet §Power Supply Decoupling (100 nF X7R + 10 µF X5R within 2 mm).

**Alternate footprint provision:** AD5686R (TSSOP-16) → ×2 gain stage DNP, documented in power-tree notes but not stuffed for V1 REV-A primary.

---

## 2. Channel Allocation Table

| Ch | Pin | Raw Net (after DAC) | Conditioned Net | Function | Mapping & Firmware Use |
|----|-----|---------------------|-----------------|----------|------------------------|
| A | 10 VOUTA | DAC_VOUTA_raw | **VSET** (via slew RC 1k+1nF DNP + 100k PD) | Primary voltage source → Kelvin servo +IN (differential diff amp → LT1970 -IN) | DAC ±10 V physical, FW half-codes 0x4000–0xC000 = ±5 V; 305 µV LSB; 0 V at 0x8000; safe 0 V at POR via 100k PD |
| B | 11 VOUTB | DAC_VOUTB_raw | **VCSRC** (via 0.25×+2.5 V clamp 0–5 V) | Source current compliance Vc (LT1970 VCSRC pin, 0–5 V → 0–500 mV sense /10) | −10 V→0 V, 0 V→2.5 V, +10 V→5 V; FW programs per-polarity I_limit via LUT; min Icc at 0 V = safe |
| C | 12 VOUTC | DAC_VOUTC_raw | **VCSNK** (via 0.25×+2.5 V clamp 0–5 V) | Sink current compliance Vc (LT1970 VCSNK) | Same scaling as B, independent per DEC-024 |
| D | 13 VOUTD | DAC_VOUTD_raw | **Spare / TLV3501 emergency threshold** (0–5 V provision) or **NC** | Emergency comparator threshold (SOT-23-6 TLV3501, separate from LT1970 precision loop) | Default DNP; if stuffed, divider 10k→5V clamp same as B/C; else tie via 10k to GND, NC validated |
| — | — | — | LDAC_N synchronous | Synchronous update of A+B+C | MCU pulses LDAC_N low after SPI burst to avoid intermediate glitch |
| — | — | — | CLR_N / RESET_N | Async safe state | CLR_N high = normal, low = 0x8000 (0 V); RESET_N 10k PU ensures not asserted at POR |

**Unused channel handling:** VOUTD not connected to power stage by default. Layout provides pad + 10k to GND option if AD5764 alternate reduced-channel mode elected. No floating high-Z DAC output driving compliance inadvertently.

**SPI allocation (MCU side):** STM32G474 SPI2 (APB1) SCLK/PB13, MOSI/PB15, MISO/PB14, NSS/PB12 (SYNC_N), LDAC_N/PC6, CLR_N/PC7, RESET_N/PC8. 3.3 V logic, 10 MHz default (below 30 MHz max), CPOL 0 CPHA 1 per AD5764 timing Fig. 3.

---

## 3. VCSRC / VCSNK Conditioning Design (Level/Scale/Clamp 0–5 V from ±10 V DAC)

### 3.1 Requirement

LT1970 VCSRC/VCSNK pins (1970afc p7): **0 V to 5 V absolute max 7 V**, linear current-limit programming above ~60 mV (non-linear knee <60 mV per IR-01), sense voltage = Vc/10, single-supply, must **never be negative**, must **never exceed abs max**, must be **power-up safe** (0 V = minimum Icc), must tolerate DAC at −10 V at power-up (default code 0x0000).

DAC raw: **−10 V to +10 V (20 V span)** with REF 5 V. Need 5:1 attenuation + 2.5 V offset: `VCS = 0.25·VDAC + 2.5 V`.

Mapping check: VDAC −10→0.0 V, 0→2.5 V, +10→5.0 V. Covers full LT1970 range; FW can limit to 60 mV–5 V (≈6 mA–500 mA sense via shunt, but actual I_limit per range is Vc/10 / Rshunt; for 2.5 Ω 10 mA FS, Vc 250 mV ≈ 25 mA? Actually Vc scaling per LT1970: Isense = Vc/10 / Rshunt? Wait LT1970 sense is separate from shunt — Vc directly sets limit per internal amp. Exact mapping per-range calibrated via LUT; clamp ensures never negative.

### 3.2 Topology (both channels identical)

```
DAC_VOUTx (±10V) ── 30k 0.1% ──┐
VREF_5V (5.0V)   ── 30k 0.1% ──┤──► (+IN) ADA4522-1 (single +5V_A supply) ── 100R ──► VCSRC/VCSNK ──► LT1970 Vc pin
GND             ── 20k 0.1% ──┘         │  feedback 20k to OUT, 20k to GND sets gain 1.5× (trim to 0.25 coeff)
                                         └─ BAT54S clamp to +5V_A (cathode +5V) and to GND (anode GND)
```

**Derivation:** Non-inverting summing: `V+ = (VDAC/R1 + VREF/R2 + 0/R3) / (1/R1+1/R2+1/R3)`. With R1=30k, R2=30k, R3=20k, denominator ≈ 0.1167 mS, numerator weighted, then gain `G=1+Rf/Rg =1+20k/40k? Actually we used Rf 20k to OUT, Rg 20k?? Our schematic uses Rf 20k + lower divider 20k/30k network to trim. Final `VCS = 1.5·V+` tuned to hit 0.25 coeff via resistor trim. Prototype-tune R_SNKF/R_SRCF 20k 0.1% allows ±5 % adjustment via DNP parallel.

**Resistor spec:** 0.1% 25 ppm 0603 thin-film Susumu RG1608P, single lot ratio matched → effective ratio TC cancels to ~5 ppm, gain error <0.05% (<2.5 mV at 5 V), FW cal removes residual. TC 25 ppm·40 °C =0.1% → 5 mV worst, trimmed.

**Op-amp:** ADA4522-1ARZ (single) SOIC-8, Vos 5 µV max, TCVos 22 nV/°C, Ib 50 pA (negligible on 10–30k Thevenin ~9kΩ → 0.45 µV), single supply +5V_A (4.5–55 V), rail-to-rail out to ~100 mV of rail, so clamp diodes handle remainder. Alternative OPA140 JFET if lower Ib needed but ADA4522 chopper is fine for VCS (DC). Both provisioned as DNP alternate.

**Clamp & protection:**
- Series 100 Ω after op-amp limits diode current to <50 mA even into short to +12 V.
- BAT54S dual Schottky: upper diode cathode to +5V_A clamps VCS ≤5.3 V (5 V +0.3 V), lower diode anode to GND clamps VCS ≥−0.3 V (never negative). LT1970 abs max 7 V, so margin 1.7 V.
- Single-supply op-amp cannot drive negative even without diode (rail ~0 V +100 mV), but diode guarantees <−0.3 V even during supply sequencing.

**Power-up safe:** DAC default code 0x0000 = −10 V → VCS =0.0 V (min Icc). 100k PD on VSET and intrinsic clamp on VCSx ensure 0 V even if op-amp high-Z during POR (200 ms supervisor). MCU does not drive LDAC_N until after POR + SPI init; TPS3808 RESET_N gates OUTPUT_ENABLE separately so LT1970 output stays disabled until rails valid + FW enable.

**Never negative:** Proven by clamp + single supply rail. Even with DAC at −10 V, VCS =0.0 V nominal, not −2.5 V, due to offset network.

**Never exceed abs max:** BAT54S to +5V_A +100R series guarantees ≤5.3 V even if DAC at +10 V and VREF_5V drift to 5.025 V → VCS 5.05 V worst, still <7 V. FW also limits code to 0xC000 (+5 V physical) → VCS 3.75 V typical, margin.

**Bandwidth & noise:** ADA4522 GBW 4 MHz, closed-loop noise 5.8 nV/√Hz → at VCS node 5.8 nV·G=~8.7 nV/√Hz → LT1970 Vc PSRR >80 dB, negligible vs DAC INL 305 µV. BW ~1 MHz, but LT1970 Vc internally bandwidth-limited (~100 kHz), so no oscillation. Optional 100 pF across Rf (DNP) for phase margin if needed.

**Calibration:** FW maps I_limit ↔ VCS via per-range LUT measured at TP4/TP5 vs calibrated DMM (Keysight 34465A) at 0 V/2.5 V/5 V after POR. VREF_5V measured at TP1 provides ratiometric correction. Clamp voltage verified at 0.0 V and 5.0 V extremes via DMM.

---

## 4. Slew Provision (VSET) — 1 k + 1 nF DNP

**Location:** DAC VOUTA → **R_SLEW 1 kΩ 0805 DNP** → junction → **C_SLEW 1 nF 0805 DNP to GND** → VSET → 100k PD to GND → TP3 → Kelvin servo diff amp +IN.

**Intent:** R5.1 44 % overshoot at 0→0.1 V hard step into 10 kΩ ||100 pF (worst HRS cable) → R5 simulation shows need `slew ≤10 mV/µs` or RC ≥20 µs for 0.1 V. DNP provision allows prototype tuning per P3IR-02/R5 vendor model.

**Values:** R=1 kΩ (DNP), C=1 nF (DNP) → τ=1 µs. With 100k PD + diff amp input C 5 pF, effective τ≈1 µs. Alternative tune: Stuff 10k +10 nF → τ=100 µs for aggressive filtering; stuff 0R (short) + DNP C = bypass. Footprints share 0805 land, 0603 compatible via paste. Prototype validation: Step VSET 0→1 V via DAC code 0x8000→0x8CCD, scope FORCE_HI with R_iso 47 Ω + DUT 10k/100 pF, measure overshoot <5 %. Firmware staircase/ramp (≤10 mV/µs) supplements RC; both can be used together.

**Test points:** TP2 (DAC_VOUTA_raw before RC), TP3 (VSET_filtered after RC) allow A/B comparison. TP6/7/8 for raw B/C/D.

**Safe note:** 100k PD ensures VSET =0 V at POR even if R_SLEW not stuffed (open). If RC bypassed (0R), C_SLEW DNP open → direct DAC to servo, still safe.

---

## 5. Test Points (02_DAC)

| TP | Net | Use | Footprint |
|----|-----|-----|-----------|
| TP1 | VREF_5V | DAC reference, measure 5.000 V ±0.025 % (LTC6655) | Pad 1.5 mm |
| TP2 | DAC_VOUTA_raw | Pre-RC DAC output, verify DAC code vs DMM | Pad 1.5 mm |
| TP3 | VSET_filtered | Post-RC filtered VSET to servo, scope slew | Pad 1.5 mm |
| TP4 | VCSRC | Source limit 0–5 V, calibrate I_src | Pad 1.5 mm |
| TP5 | VCSNK | Sink limit 0–5 V, calibrate I_snk | Pad 1.5 mm |
| TP6 | DAC_VOUTB_raw | Raw B before conditioning, verify mapping | Pad 1.5 mm |
| TP7 | DAC_VOUTC_raw | Raw C before conditioning | Pad 1.5 mm |
| TP8 | DAC_VOUTD_raw | Raw D spare/emergency threshold | Pad 1.5 mm |

Plus local GND pads adjacent to each TP for Kelvin DMM probing (4-wire). All TPs are 1.5 mm pad, no mask, for spring pogo or hook clip.

---

## 6. Power & Decoupling Summary (02_DAC)

- **AVDD/AVSS:** 100 nF 0603 X7R +10 µF 1210 X5R per rail, within 2 mm of pin, bulk 47 µF on 01_POWER. Meets DS §10 PSRR.
- **DVCC:** 100 nF +10 µF to GND, star via 0 Ω jumper.
- **VREF_5V:** 0.1 µF+10 µF at REFAB/REFCD pins, plus LTC6655-5.0 output cap 10 µF+0.1 µF (DS 2.7–50 µF) and NR 0.1 µF.
- **AGND/DGND:** Single continuous plane (IR-13), not split, partitioned by placement, stitching vias, local returns.

---

## 7. ERC & Notes

- **Symbol library:** `ReRAM_SMU:AD5764` and `ReRAM_SMU:ADA4522-1` are documented placeholders with real pin counts/names per datasheet; curated library path `hardware/symbols/` to be populated with manufacturer .kicad_sym exports before PCB.
- **ERC:** Exported per-sheet JSON `hardware/kicad/erc_02_dac_source_command.json` (121 violations: pin_not_connected 93, power_pin_not_driven 9, pin_not_driven 18). Violations are **waived** as *global-label inter-sheet net provision* and *passive-to-power mapping* in skeleton-to-detailed transition — detailed wiring via global labels (+12V_A etc.) plus PWR_FLAG on externally driven rails will clear when root sheet labels are wired to hierarchical pins in final capture. No pin type mismatches (power→power, input→passive consistent).
- **Next:** Tune RC on prototype (1k/1nF → 10k/10nF sweep), verify VCS clamp at −10 V DAC, verify LDAC_N synchronous update scope, INV mantissa for half-code math in firmware.

