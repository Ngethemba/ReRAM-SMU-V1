# Simulation Model Limitations — ReRAM-SMU V1 (Phase 3, Gate 6)
**Project:** ReRAM-SMU V1 — Phase 3 Gate 6
**Date:** 2026-08-24
**Status:** LIVING — update per gate; model never proves low-current/layout-dependent performance (ENGINEERING_RULES §5)
**Tool versions:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe` built Aug 11 2026), python 3.11.15 (`.venv` numpy 1.26), LTspice 26.0.2.1 (`C:/Users/azrai/ADI/LTspice/LTspice.exe`), KLU solver

> For every important macro-model state: manufacturer | model | source | what it models | what it does **NOT** (leakage, thermoelectric, DA, relay EMF, humidity, ADC DSP, DAC INL, drift, package parasitics) — with table per gate. Primary datasheets override models.

---

## 1. Summary — All models are behavioral approximations, not cal-notify

| Model | Manufacturer | Source path | What it models (validated) | What it does NOT model (requires bench) | Gate used |
|-------|--------------|-------------|----------------------------|------------------------------------------|-----------|
| **LT1970A behavioral** (Candidate A + C inner) | Analog Devices | ADI LTspice .lib `LT1970A` (ADI distribution, `C:/Users/azrai/ADI/LTspice/lib/sub/LT1970A.lib`) adapted to ngspice B-source: ideal op-amp + 4mV floor, 1% Vc/10 scaling, 3.6MHz GBW, 1.6V/µs SR, Vos 200µV typ, Ib 160nA, Rout 0.5Ω, FILTER 220pF, ISRC/ISNK 4µs takeover | DC offset/GBW/SR, Riso+C pole, FILTER pin pole, current-limit law I=VC/(10·Rsense) for Vc≥60mV linear, floor 4mV typ, flags (behavioral) | Package thermal pad θJA ~30–40°C/W (not thermal shutdown transient), package parasitics L/C, ESD diode leakage, relay EMF thermal, humidity leakage, DA of potting, Ib tempco, en/in noise PSD vs frequency, PSRR vs freq, crossover distortion near 0, Vc<60mV nonlinear knee shape vs temp, supply slew ≤6V/µs limit, latch-up | Tests O, I, J |
| **ADA4522** (Candidate B front-end, C outer) | Analog Devices | ADI PSPICE model `ADA4522.lib` (Rev I 2025-01-08, `docs/references/ADI_ADA4522_RevI.lib` if licensed, else behavioral 5µV max, 0.7µV typ, 22nV/°C max, 5.8nV/√Hz, Ib 50pA typ 150pA max) | Vos/TCVos/en, Ib DC, GBW ~3MHz, zero-drift chopper 800kHz (approx as single pole), rail-to-rail 55V | Chopper clock feedthrough, 1/f corner, EMI susceptibility, PSRR vs freq, CMRR vs Vcm, package therm EMF, humidity surface leakage (10GΩ→10pA not modeled), DA of input capacitance 2–5pF, charge injection of chopper switches | Tests O, E, G |
| **OPA140 / OPA2140** (alt for Candidate B/C outer, JFET buffer for sense) | Texas Instruments | TI TINA-TI / PSPICE model `SBOM430E.ZIP` (OPA140 Rev F 2023-03-28) [ti.com/product/opa140] | Vos 120µV max, TCVos 1µV/°C max (0.35 typ), Ib 10pA max, en 5.1nV/√Hz, in 0.8fA/√Hz, GBW 11MHz, SR 20V/µs, JFET input C 2–5pF | Ib vs T (doubles ~10°C), input bias current noise vs Rs, ESD leakage, PCB guard leakage, package DA, therm EMF of relay vs op-amp isothermal mismatch | Tests E, M, O |
| **2N3904/3906 discrete buffer** (Candidate B) | Generic (JEDEC) | ngspice built-in Gummel-Poon .model QN3904/QP3906 (IS=6.7f, BF 416/412, VAF 74, CJE 4.5p, CJC 3.5p, TF 0.3n) — not vendor-specific | DC β, Vbe ~0.65V, storage time, Cπ/Cµ for stability pole with Riso·CL, class-AB bias | SOA/thermal runaway, Early effect vs temp, package parasitics, thermal EMF, leakage of flux, mismatch β NPN vs PNP (source/sink symmetry), ESD | Test O (B) |
| **BUF634-like buffer** (Candidate B alt) | TI/Burr-Brown | TI BUF634A datasheet + TINA model (if used) — here modeled as ideal buffer with Rout 1Ω + Re 10Ω inside loop | Closed-loop buffer bandwidth ~30MHz, Rout 1Ω, current 250mA | Thermal pad, compensation cap, PSRR, noise | Test O (B alt, not stuffed) |
| **AD5686R** (DAC Candidate A) | Analog Devices | AD5686R Rev F datasheet + ADI LTspice/PSPICE model (if available; here Monte Carlo uses datasheet INL ±2LSB, TUE ±0.1% FSR, gain error, glitch 0.5nV-sec, ref drift 2ppm) [analog.com/.../ad5686r_5685r_5684r.pdf] | LSB 76.3µV on 5V, INL ±2LSB, DNL ±1LSB, gain error, offset, glitch, settling 5µs to ±0.0015% FSR | Code-to-code glitch vs Vref load, R-2R reference current vs code (code-dependent supply current), drift vs humidity, package parasitics, long-term drift, supply PSRR, SPI timing | Test N |
| **AD5764** (DAC Candidate B) | Analog Devices | AD5764 Rev F datasheet + ADI model (bipolar ±10V, span 20V, LSB 305µV, INL ±1LSB, TUE, settling 10µs) [analog.com/.../AD5764.pdf] | LSB 305µV, INL ±1LSB →±305µV, gain/offset, reference input current vs code, supply ±11.4–16.5V | No ±5V mode (modeled correctly as half-codes), reference current code-dependent (R-2R ladder) not modeled in MC (treated as systematic gain), drift vs temp/humidity, package | Test N |
| **AD5791** (DAC Candidate C) | Analog Devices | AD5791 Rev F datasheet [analog.com/.../ad5791.pdf] (20-bit, 1ppm INL, glitch 1.4nV-sec, 7.5nV/√Hz) | LSB 19.07µV, INL ±1LSB (±19µV), TUE, 1µs to 1ppm | Ext ref buffer stability, R-2R ladder nonlinearity vs Vref, long-term drift, package | Test N (only if 16-bit fails) |
| **ADR4525 / LTC6655** (references) | ADI | ADR4525 Rev G [analog.com/.../ADR4520_4525_4530_4533_4540_4550.pdf], LTC6655 Rev fb [analog.com/.../6655fb.pdf] | Vnoise 0.1–10Hz 1.6µV p-p / 0.775µV p-p, TC 2ppm/0.8ppm, Vout 2.5V, cap load 1–10µF | Hysteresis (ADR4525 D 1–5ppm vs A/B/C −8/−97ppm), humidity sensitivity, long-term drift (19–51ppm/4.5khr), load transient, ESR, SC70 package thermals | Tests N, I, budget |
| **ADS1262 / AD7175 / AD7124** (ADC candidates) | TI / ADI | TI ADS1262 datasheet [ti.com/.../ads1262.pdf], ADI AD7175-8 Rev0 [analog.com/.../AD7175-8.pdf] | Noise vs data rate (0.16µV p-p @20SPS Sinc4, 0.12µV @20SPS Sinc5+1), 50/60Hz rejection 130dB Sinc4@20SPS, PGA 1–32, single-cycle settle, Sinc filter | ADC DSP (post-filter, chop, PGA buffer CM limits), anti-alias RC + PGA interaction ENBW, 1/f noise, PSRR, leakage of input mux (ADG1419 10pA), package, humidity, charge injection of S/H, SPI timing, digital filter group delay | Tests G, M, NPLC |
| **Reed relay / PhotoMOS / CMOS mux** (range switching) | Coto/Standex, Panasonic TQ/AQY, ADG1419 | Datasheets (Coto 9000, AQY212S, ADG1419) + `MEASUREMENT_FRONTEND_CANDIDATES.md §4` | Off leakage <1pA reed vs 10pA–1nA PhotoMOS/CMOS, Ron 0.1Ω reed vs 0.5–10Ω PhotoMOS/1–10Ω CMOS, Coff 1–3pF vs 10–50pF, thermal EMF <1µV reed vs 1–5µV EM, 10⁸ ops reed | Dielectric absorption of potting/FR-4, flux residue leakage vs humidity/temperature (doubles ~10°C), coil heat → therm EMF, contact bounce, electromechanical EMI, C·dV/dt injection | Tests K, M |

---

## 2. Per-Gate Model Coverage and Gaps

### Gate 6 — Tests N+O (this gate)

| Test | Models applied | What was swept | What remains unmodeled |
|------|----------------|----------------|------------------------|
| **N DAC/reference** | AD5686R, AD5764, AD5791 behavioral MC (datasheet INL/gain/quant/TC/drift), ADR4525/LTC6655 2/0.8ppm, ADA4522 Vos for gain stage | LSB/gain INL, quant, ratio error 0.01%/0.1%, TC, drift ΔT±3°C/15°C, 2-pt cal gain/offset, LSB headroom vs 10mV step/supply/refs | R-2R code-dependent reference current, buffer stability vs cap load on ref, supply PSRR transient, SPI timing, long-term drift, humidity, package parasitics |
| **O Candidate A LT1970A direct** | LT1970A behavioral (4mV floor, 1% Vc/10, 3.6MHz, 1.6V/µs, Vos 200µV, Ib 160nA, FILTER 220pF) into Riso 33Ω + 10Ω Rsense, feedback after Riso (DUT-sense IR-11) | DC error/offset/load regulation ±10mA into 100Ω/1k/10k/1M, C 10p/100p/1n/10n, Kelvin R 0–10Ω, sense C, CC snap 1M→300Ω 1µs, source/sink ±10mA symmetry, PM~50–85° analytic + ngspice tran 1k+100p/10n overshoot 0.2%/6.5% | Thermal shutdown, SOA hyperbola, supply slew ≤6V/µs, package θJA, ESD leakage, Ib tempco, en/in PSRR vs freq, Vc<60mV knee, latch-up, humidity |
| **O Candidate B ADA4522+BJT buffer** | ADA4522 (5µV max, 0.7µV typ, 5.8nV) + 2N3904/3906 inside loop, Riso 47Ω Cf 100pF, feedback after Riso | Same sweeps + buffer poles (Cπ/Ciss, ro+CL), crossover distortion at µA, no integrated limit (comparators >10µs coarse trip), disable via analog switch (µA leak when off) | Shoot-through, thermal EMF of buffer, bias drift, buffer SOA at short, enable leak, flux DA, hum |
| **O Candidate C nested outer+booster** | ADA4522 outer + LT1970A inner unity buffer, Riso 33Ω, Cf_outer 47pF, FILTER 22pF, lead-lag 1k+10n/1n, inner Av0=1 fp 3.6MHz, outer dominant 36Hz | Same sweeps + inner vs outer dynamics (lead-lag, Riso feedback after Riso), PM worst ~50–57° analytic, ngspice 100p OS 0.05% /10n OS 16.6% (needs Cf optimization) | Nested loop Miller/phase interaction vs CL 10p–10n + Llead 100nH, compliance outer voltage + inner current crossover vs DUT 1nF, Kelvin latch-up |
| **Stability (all)** | Analytic PM=90−atan(fc/fp2)−atan(fc/fp_extra)+atan(fc/fz), ngspice AC dec 1–10MHz + transient overshoot/settling (target PM>45° prefer >60°) | C 10p–10n with Riso 33/47Ω, Cf 33–100pF, fp2=1/(2πRisoC), fz=1/(2πRfCf), fc≈GBW/2 | Package parasitics, cable L 10–100nH, trace R, capacitor ESL/ESR, humidity, DA, supply bounce, EMI |

### Earlier Gates (for traceability, not re-simulated here)

| Gate | Tests | Models | Limitations carried |
|------|-------|--------|---------------------|
| Phase 2 Preliminary | A–O plan (IR-01..IR-16), burden philosophies | Analytical BURDEN 100mV→25mV D, SHUNT_RANGE_TRADEOFF §2.4 | No transient, no MC, no ngspice — plan only (IR-16) |
| Gates A–E (Phase 3) | Compliance, Kelvin, sense, DUT loading, range switch | LT1970A + ADA4522 + OPA140 + relay models | Leakage/DA/therm EMF not measured, guard copper not fabricated |

---

## 3. Simulator Versions and Model Provenance Details

- **ngspice-47** — `E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice.exe` (8585216 bytes, Aug 11 2026) and `ngspice_con.exe` (7641600 bytes) with KLU solver; docs `ngspice-47-manual.pdf` in same dir. Primary for automated/batch simulation; KiCad 10 bundles `ngspice.dll` at `E:/KiCad/bin/ngspice.dll`.
- **LTspice 26.0.2.1** — `C:/Users/azrai/ADI/LTspice/LTspice.exe` (installed via winget, Dec 2023). Secondary for vendor models (LT1970A, ADA4522). Path recorded in `tools/setup/SPICE_SETUP.md`.
- **Python 3.11.15** — `.venv` at `E:/ReRAM-SMU V1/.venv` (uv venv --python 3.11), numpy 1.26, scipy optional, matplotlib for post-processing; `python3` 3.14.0 available system-wide but primary is 3.11.15 per `TOOL_DECISIONS.md DEC-TOOL-001`.
- **LT1970A model:** ADI `LT1970A.lib` from LTspice distribution (`lib/sub/LT1970A.lib`, includes Vc/10 scaling, SENSE pins, ISRC/ISNK gm amps, ENABLE, TSD). Adapted to ngspice by replacing encrypted `OTA` with B-source `B1 mid 0 V = 100e3*(V(inp,inn)+200e-6)` + R-C pole 1k/4.42u (36Hz) + Rout 0.5Ω; added 4mV floor via `MAX(Vc/10, 4mV)` behavioral for IR-01, 1% limit via `VC*0.99–1.01` uniform in MC.
- **ADA4522 model:** ADI `ADA4522.lib` PSPICE (Rev I 2025-01-08, zero-drift chopper 800kHz modeled as single pole 3MHz GBW, Vos 5µV max, Ib 50pA, en 5.8nV). If ADI model unavailable as LTspice, behavioral fallback: gain 500k, Vos 0.7µV typ, Ib 50pA, pole 26.5u (6Hz) for 3MHz GBW.
- **OPA140 model:** TI `SBOM430E.ZIP` (OPA140 Rev F 2023-03-28) TINA-TI + PSPICE; ngspice import via `U+` tweaks per `DEC-TOOL-002` hybrid workflow.
- **Damping:** No `XSPICE` wattmeter; behavioral models are untuned for supply current.
- **Modifications documented per .cir header:** `candidate_A_transient.cir`, `candidate_B_transient.cir`, `candidate_C_transient.cir` headers state manufacturer/model/source/what it models/what it does NOT.

---

## 4. Critical Properties NOT Modeled (Require Bench per ENGINEERING_RULES §5)

- **Leakage:** PCB surface (10GΩ→10pA @100mV, 1GΩ→100pA), flux residue, connector (1GΩ), relay off 1pA reed vs 10pA–1nA PhotoMOS/CMOS, switch ADG1419 10pA typ, capacitor DA (seconds tail), via guard copper keepout (0.5mm gap, no-mask) and stitched inner plane every 5mm (GUARD_STRATEGY §10) — none in SPICE (ideal open).
- **Thermoelectric:** Relay/connector contact EMF 1–5µV (low-thermal reed <1µV) vs coil heat ΔT, isothermal layout not modeled, tempco 22nV/°C vs 1µV/°C drift of OPA140 not captured beyond DC Vos.
- **Dielectric Absorption:** FR-4 + relay potting + flux absorb charge seconds→nA tail after range change/bias step; SPICE uses ideal C without DA branch (add R-C ladder if needed, but not in vendor models).
- **Relay EMF, bounce, humidity:** Mechanical bounce 1–3ms, coil flyback + RC snubber, humidity leakage doubles ~10°C, not in SPICE; bench at 25/40°C required (Gate M leakage model).
- **ADC DSP, DAC INL, drift, package parasitics:** ADS1262 Sinc4 digital filter group delay + PGA buffer CM limits, AD7175 post-filter, DAC INL vs code/humidity, reference hysteresis (−8/−97ppm A/B/C vs 1–5ppm D), package L/C, bondwire, thermal pad.
- **Compliance loop vs supply:** LT1970A FILTER pin 220pF pole + Rsense wiring L 10–100nH not fully in behavioral; crowbar vs regulation+trip distinction (Gate I/J/K) requires energy integral E_DUT=∫V·I dt not just % overshoot.

---

## 5. How to Reproduce / Extend

```bash
# DAC MC
python simulation/phase3/dac_adc/test_N_dac_comparison.py  # regenerates ad5686r_*.csv, ad5764*.csv, ad5791*.csv → also mirrored to monte_carlo/

# Source candidates DC/offset/MC
python simulation/phase3/monte_carlo/test_O_monte_carlo.py  # dc_sweep_*.csv, kelvin_*.csv, compliance_*.csv, stability_*.csv per candidate

# ngspice transients (HEAD commits .raw → .dat via wrdata)
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/source_A_LT1970/candidate_A_transient.cir
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/source_B_precision_buffer/candidate_B_transient.cir
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/source_C_outer_LT1970/candidate_C_transient.cir
# Outputs: tran_*_1k_100p.dat, tran_*_1k_10n.dat, ac_*.dat, run_log
```

Vendor models license: ADI/TI models remain property of respective manufacturers; local copies under `docs/references/` where licensing permits (see ENGINEERING_RULES §2.2 provenance).

---

*This document is the per-gate model-limitations table required for Gate 6 PASS (DAC simplest meeting with margin; at least one source candidate passes DC+cap+Kelvin+compliance+stability >45° PM). Next gate updates the table with bench Type-A σ that replaces Type-B tolerances.*

