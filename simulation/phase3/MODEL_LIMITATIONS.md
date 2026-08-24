# Simulation Model Limitations — ReRAM-SMU V1 (Phase 3, Gate 6 + Corrective R1–R6)
**Project:** ReRAM-SMU V1 — Phase 3 Gate 6 + Corrective Review
**Date:** 2026-08-24 (corrected 2026-08-24)
**Status:** LIVING — update per gate; model never proves low-current/layout-dependent performance (ENGINEERING_RULES §5)
**Tool versions:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe` built Aug 11 2026), python 3.11.15 (`.venv` numpy 1.26), LTspice 26.0.2.1, KLU solver
> For every important macro-model state: manufacturer | model | source | what it models | what it does NOT. Primary datasheets override models.
**Corrective note (P3IR-05 R5):** Candidate A `candidate_A_transient.cir` is behavioral (Aol 100k, fp 36Hz, GBW 3.6MHz, SR 1.6V/µs, Rout 0.5Ω) — NOT vendor LTspice macro-model. Vendor macro validation pending + prototype required; do not quote PM=50° as vendor-model.

---
## 6. Phase 3 Corrective Review — Additional Limitations (P3IR-01..08)

| Finding | What was corrected | What remains NOT modeled (requires bench/vendor) |
|---|---|---|
| P3IR-01 Shared Rsense | Behavioral Rsense now shared canonical shunt 2.5Ω–1MΩ; fixed 10Ω superseded | Separate compliance bank switching transient, Rsense wiring L 10–100nH, LT1970 SENSE input C, Vc<60mV knee shape vs temp not in behavioral |
| P3IR-02 C_UP/C_DOWN | Prose corrected — downstream 80–150pF @5V, upstream shared 95.5% @1kΩ/47Ω not free | Cable DA, FR-4 DA, connector leakage vs humidity, active amp sink dynamics for 10nF snap |
| P3IR-03 ADC | ADS1262 internal PGA 1–32 (+3.13× pre-gain) primary; AD7175 external 100/50/25× alternate | External diff amp gain error drift, relay therm EMF, PGA overload recovery at 25mV FS not in Python G model |
| P3IR-04 DAC ref | AD5764 @5V ref ±1LSB guaranteed (LTC6655-5.0); 2.5V full-span not guaranteed | REF input current code-dependent R-2R, reference buffer stability vs cap load, hysteresis |
| P3IR-05 Vendor model | Behavioral 6.5% OS @10nF traceable; 16.2% analytic historical superseded | **Vendor LT1970A.lib macro not run** — package L/C, thermal shutdown, supply slew, crossover — NEEDS LTspice + prototype step |
| P3IR-06 Open-sense | ADG1419 100pA typ rejected; reed <1pA selected | Reed bounce 1–3ms, coil flyback, humidity leakage doubling per 10°C not in SPICE |
| P3IR-07 OPA140 envelope | Regions Guaranteed ≤100MΩ / Characterized 1GΩ@0.5–1V / Exploratory 1GΩ@0.1V | Ib vs T (3nA @125°C), pkg DA, guard leakage, therm EMF mismatch not modeled beyond DC |
| P3IR-08 Traceability | 6.5% transient retained, 16.2% flagged historical, 95.5% prose fixed | — |

Vendor-model validation plan (LTspice): `LT1970A (ADI macro, unmodified) + ±12V, COMMON=GND, VCSRC/VCSNK DAC-driven, FILTER 220pF, Rsense=selected shunt 2.5Ω–1MΩ Kelvin, R_iso 33–47Ω, feedback after R_iso, C_down 10pF–1nF, C_up 4.7/10nF upstream only, DUT 100Ω–1MΩ, cable L, CV↔CC transitions` — Middlebrook injection at output; if macro hides, use transient OS/settling + classify REQUIRES PROTOTYPE.

---
## 1. Summary — All models are behavioral approximations, not cal-notify

| Model | Manufacturer | Source path | What it models (validated) | What it does NOT model (requires bench) | Gate used |
|-------|--------------|-------------|----------------------------|------------------------------------------|-----------|
| **LT1970A behavioral** (Candidate A + C inner) | Analog Devices | ADI LTspice .lib `LT1970A` adapted to ngspice B-source: ideal op-amp + 4mV floor, 1% Vc/10 scaling, 3.6MHz GBW, 1.6V/µs SR, Vos 200µV typ, Ib 160nA, Rout 0.5Ω, FILTER 220pF | DC offset/GBW/SR, Riso+C pole, FILTER pin pole, current-limit law I=VC/(10·Rsense) for Vc≥60mV linear, floor 4mV typ | Package thermal pad, parasitics, ESD leakage, relay EMF, humidity DA, Ib tempco, en/in PSRR, Vc<60mV knee shape vs temp, supply slew, latch-up | Tests O, I, J |
| **ADA4522** | Analog Devices | ADI PSPICE `ADA4522.lib` Rev I | Vos/TC/en, Ib, GBW ~3MHz | Chopper feedthrough, 1/f, EMI, PSRR vs freq, CMRR, package therm EMF, humidity leakage, DA | Tests O, E, G |
| **OPA140** | TI | TI `SBOM430E.ZIP` Rev F | Vos 120µV max, TCVos 1µV/°C, Ib 10pA max, en 5.1nV, in 0.8fA, GBW 11MHz, SR 20V/µs, JFET Cin 2–5pF | Ib vs T (doubles ~10°C), current noise vs Rs, ESD leakage, guard leakage, package DA, therm EMF of relay mismatch | Tests E, M, O |
| **AD5764** | ADI | AD5764 Rev F | LSB 305µV @5V ref, INL ±1LSB @5V →±305µV, supply ±11.4–16.5V | No ±5V mode (half-codes), reference current code-dependent not in MC, drift vs temp/humidity, package | Test N |
| **ADR4525 / LTC6655** | ADI | ADR4525 Rev G, LTC6655 fb | Vnoise 1.6µV p-p / 0.775µV p-p, TC 2ppm/0.8ppm, Vout 2.5V/5V | Hysteresis, humidity drift, long-term drift, load transient, ESR | Tests N, budget |
| **ADS1262 / AD7175** | TI / ADI | ADS1262 ds, AD7175 Rev0 | Noise vs ODR (0.16µV p-p @20SPS, 0.12µV @20SPS), 130dB notch, PGA 1–32 (ADS1262 only) | ADC DSP, anti-alias RC + PGA ENBW, 1/f, PSRR, mux leakage (ADG1419 100pA not 10pA), humidity, charge injection, SPI timing, digital filter group delay | Tests G, M, NPLC |
| **Reed relay / ADG1419** | Coto/ADI | Coto 9000, ADG1419 Rev A | Reed <1pA vs ADG1419 IS(off) 100pA typ 500pA max (25°C) 75nA (85°C) | DA, flux residue, humidity leakage doubles ~10°C, coil heat → therm EMF, bounce, EMI | Tests K, M, D |

*This document is the per-gate model-limitations table required for Gate 6 PASS (behavioral). Corrective review downgrades LT1970A to "BEHAVIORAL SIMULATED — VENDOR-MODEL SIMULATED PENDING, NEEDS PROTOTYPE" per P3IR-05.*

---
## 2. Per-Gate Model Coverage and Gaps

### Gate 6 — Tests N+O (behavioral)

| Test | Models applied | What was swept | What remains unmodeled |
|------|----------------|----------------|------------------------|
| **N DAC/reference** | AD5686R, AD5764 @5V ref 305µV half-codes, AD5791 behavioral MC | LSB/gain INL, quant, ratio 0.01%/0.1%, TC, drift ΔT±3/15°C, 2-pt cal, LSB headroom | R-2R reference current code-dependent, buffer vs cap load, supply PSRR, SPI timing, humidity |
| **O Candidate A LT1970A direct** | LT1970A behavioral (4mV floor, 1% Vc/10, 3.6MHz, 1.6V/µs, Vos 200µV, FILTER 220pF) into Riso 33Ω + shared Rsense 2.5Ω–1MΩ, feedback after Riso | DC error/offset, C 10p/100p/1n/10n behavioral, Kelvin R 0–10Ω, CC snap 1M→300Ω 1µs, PM~50–85° analytic + tran 6.5% @10nF | Thermal shutdown, SOA, supply slew ≤6V/µs, θJA, ESD, Ib tempco, en/in PSRR, Vc<60mV knee, latch-up, humidity |
| **Stability** | Analytic PM=90−atan(fc/fp2)−atan(fc/fp_extra)+atan(fc/fz), ngspice AC | C 10p–10n behavioral | Package parasitics, cable L, cap ESL/ESR, humidity, DA, supply bounce, EMI |

### Corrective Gates R1–R6

| Gate | Correction | Model note |
|---|---|---|
| R1 Shared Rsense | Fixed 10Ω superseded → shared canonical shunt | Behavioral Rsense not separate bank transient — banking transient needs prototype |
| R5 Vendor model | Behavioral 6.5% transient retained, 16.2% superseded | **Vendor macro not run** — REQUIRES PROTOTYPE |

---
## 3. Simulator Versions

- ngspice-47 `tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe` (Aug 11 2026)
- LTspice 26.0.2.1 `C:/Users/azrai/ADI/LTspice/LTspice.exe`
- Python 3.11.15 `.venv` numpy 1.26

---
## 4. Critical Properties NOT Modeled (Require Bench per ENGINEERING_RULES §5)

- Leakage: PCB surface (10GΩ→10pA), flux, connector, reed 1pA vs ADG1419 100pA (25°C) →75nA (85°C), capacitor DA, guard copper not fabricated.
- Thermoelectric: relay/contact EMF 1–5µV (reed <1µV), isothermal layout not modeled.
- Dielectric Absorption: FR-4 + relay potting charge seconds tail — SPICE ideal C.
- Relay bounce/humidity: bounce 1–3ms, humidity leakage doubles ~10°C — bench at 25/40°C required.
- ADC/DAC package parasitics, reference hysteresis, DAC INL vs humidity, LT1970A FILTER wiring L.

---
## 5. How to Reproduce / Extend

Updated to use shared Rsense — see corrective Rsense note in `candidate_A_transient.cir` header (should be 2.5Ω–1MΩ switched, not fixed 10Ω for compliance validation).

Vendor LT1970A.lib to be installed from `analog.com/media/en/simulation-models/spice-models/LT1970A.lib` then run LTspice bench per §6.

---
*Next: vendor LTspice run + prototype step (R5) before schematic final.*
