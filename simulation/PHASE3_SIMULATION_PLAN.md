# Phase 3 Simulation Plan — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 → Phase 3 gate  
**Date:** 2026-08-24  
**Tooling:** Hybrid ngspice primary (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`), LTspice secondary for vendor models; Python `simulation/python/` for Monte Carlo.

## Pass/Fail metrics from REQUIREMENTS

- Source: ±5 V outer, ±2 V primary zone accuracy per REQ-MEAS-007 provisional (±0.02%+ offset, U<900 µV @2 V, <700 µV @1 V).
- Compliance: regulation <50 µs, trip <5 µs, overshoot <1% resistive / <5% into 1 nF, SOA 50 mW.

## Simulations

### 1 Source transfer — Vset accuracy

- ±5 V and ±2 V sweeps, load R 1 kΩ–1 MΩ, steps 1 mV–10 mV. Measure V_DUT (SENSE) vs V_set; load regulation ±(0.01% FS).

### 2 Four-quadrant / source-sink

- Resistive load 500 Ω @±2 V ±4 mA; active back-driven load (current source -5 mA into +2 V output); zero crossing ±10 mV with 10 mA step — check sink accuracy and glitch.

### 3 Compliance

- Every decade Icc 10 µA,100 µA,1 mA,10 mA: load step from below to above limit (e.g., 5 V into 1 kΩ→300 Ω), simulated filament SET transition (R 1 MΩ→1 kΩ in 1 µs), capture I_peak, V compliance line flatness, flag latency. Pass: overshoot <1%, settle <50 µs.

### 4 Stability

- Resistive DUT 100 Ω–1 MΩ, capacitive DUT 10 pF–10 nF + cable 100 pF/m, Kelvin sense lead C 10 pF–100 pF, sense wiring inductance 10 nH–100 nH. Phase margin target >45° (where model available).

### 5 Measurement front-end — each range

- 10 mA→100 nA shunts: FS 100/50/25 mV, overload 150% FS recovery <10 ms, range change transients (charge injection), settling to 0.1% within dwell (50 ms), noise 10 Hz BW vs Johnson table.

### 6 Monte Carlo

- Resistor ratios 0.1% tolerance, ref 0.02%, amp Vos 5 µV, shunt 0.1% — 1000 runs, verify Vset @2 V U <900 µV.

### 7 Temperature

- ±10 °C sweep: reference 2 ppm/°C, shunt 25 ppm/°C, amp TC 1 µV/°C — drift < accuracy/2.

## Outputs

`simulation/spice/*.cir` + `simulation/results/<date>_<sim>_vX/` with .raw, .log, plots, PASS/FAIL table. Fail → architecture revisit, not BOM.
