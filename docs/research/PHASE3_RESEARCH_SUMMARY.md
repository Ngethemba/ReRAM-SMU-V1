# Phase 3 Research Summary — ReRAM-SMU V1

**Date:** 2026-08-24
**Phase:** 3 — Source, Compliance, Kelvin & Measurement-Front-End Simulation
**Status:** PASS — 15/15 tests PASS (2 conditional/inconclusive per note), 1 architecture SELECT, 1 fallback, 1 prototype-gated

## Gates 1-6 Overview

Phase 3 executed the expanded plan (tests A-O per PHASE3_SIMULATION_PLAN:IR-16) with ngspice-47 + Python 3.11.15 + LTspice 26.0.2.1 hybrid. Results in `simulation/results/phase3/PHASE3_RESULTS.md`.

## Key Quantitative Outcomes

- **Compliance floor (A):** LT1970A Vsense floor 4mV typ (Vc 40mV) → I_min 4% FS @100mV, 8%@50mV, 16%@25mV; Vc≥60mV (6mV Vsense) linear knee verified 501-pt ngspice DC; 0.1% unreachable 40× over — coercion required (DEC-024).
- **Coercion (B):** Tightest FS≥Icomp with Vc≥60mV yields 6/6 linear (Vc 125-500mV), 2/6 ideal Vc≥0.5V; ReRAM 50µA-1mA 4/4 PASS — satisfies REV-A recipes.
- **Kelvin (C):** Ideal 160/160 cases V_DUT error -5µV max (<0.5mV@1V), headroom min 5.88V@5V, V_FORCE=V_DUT+V_SHUNT+V_LEADS signed exact; DUT-sense after R_iso PASS; PM ideal INCONCLUSIVE → proven via O (PM 50-60°).
- **Open-sense (D):** Switched continuity before ON (<5µs flag) → latch OFF PASS; without protection rail to 12V in 12µs (10.8nJ vs 1nJ budget); leakage 0.5nA@5V/10GΩ.
- **DUT loading (E):** Passive 20MΩ divider rejected (33-98% error @10M-1G); buffered JFET 10pA worst 2% @1GΩ/0.5V (typ 0.05%<1%) PASS.
- **Capacitance (F):** C_DOWN budget E=0.5CV² tabulated 5pF-1nF ×0.5-5V vs gentle≤1nJ/standard≤2nJ/forming≤10nJ: 80pF@5V/500pF@2V gentle, 160pF/1nF standard — recipe dependent.
- **Bipolar (G):** Midscale VCM2.5V+PGA32: 2.5±0.078V inside 0.1-4.9V RRIO (PGA 0.78-3.13×); true bipolar only AD7175, direct diff GND only AD7175; PGA required.
- **Trip (H):** MC 1000×21 configs 120/130/150%: 99% 8.7%@100nA/17.3%@10µA/32.7%@1mA — range-dependent multiple 150/130/120% recommended.
- **Energy (I):** 1M→1k 1ms E_dut 18.5nJ 61× 0.30nJ cap underest; 100ns ideal 0.85nJ 2.8× cap; LT 4µs takeoff 7nJ; TLV crowbar diverts.
- **Up/Down C (J):** Upstream isolated 95.5-100% not dumped; R_iso 33-47Ω tradeoff (too low dumps, too high hurts regulation) — 33Ω @10nF 50° PM PASS.
- **Switch faults (K):** BBM OK, MBB -90.9% Vsense →1000% compliance current, open ∞, 100W on 1MΩ→disable; safe seq 23.5ms (freeze0.5+reduce0.5+break1+wait5+make1+settle10+zero5+resume0.5).
- **POR (L):** Supervisor 200ms (R100k·C2u Vt4.5) holds ENABLE LOW despite 5V fault, Hi-Z, brownout 8V dip — hardware dominates firmware PASS.
- **Leakage (M):** Good 1pA & Moderate 10pA still meet 1nA MUC with offset correction (Johnson 0.41pA 4%); Poor 100pA destroys 10nA read.
- **DAC (N):** AD5764 SELECT (20V 305µV, INL±305µV equal in volts to AD5686R ±2LSB, advantage no gain-stage; 2V +46% headroom k=2, 0.1V +9%/−19%, 3% vs 1.5% for 10mV step OK, half codes acceptable, ±11.4V raw ±12V 0.6V margin, LTC6655LN 0.775µV p-p). AD5686R 0.01% 10ppm fallback, 0.1% REJECT, AD5791 only if 16-bit fails (not needed).
- **Source (O):** Candidate A SELECT (LT1970A direct PM50° OS6.5%@10nF 0.2%@100p, DC 12µV@2V, 4µs takeoff 1% separate ISRC/ISNK 20µs/1% resistive PASS), B fallback (PM60% OS3.2% best DC 0.7µV but coarse trip >10µs), C prototype (PM57° analytic OS16.6% marginal → needs Cf optimization, gains 4µV, nested lead-lag).

## Architecture Selection

- **SELECT primary:** LT1970A direct (Candidate A)
- **KEEP AS FALLBACK:** ADA4522+BJT buffer (B)
- **REQUIRES PROTOTYPE:** Outer+LT1970A nested (C)
- **DAC:** AD5764 vs **ADC:** AD7175 primary / ADS1262 fallback

## Model Limitations & Remaining Risks

See `simulation/phase3/MODEL_LIMITATIONS.md` per gate — SPICE never proves low-current/layout-dependent performance; bench validation required for leakage/DA/therm EMF/humidity/ADC DSP/DAC R-2R current/package parasitics/thermal shutdown/SOA.

## Traceability

All tests A-O map to REQUIREMENTS/DECISIONS per PHASE3_SIMULATION_PLAN tables; error budget updated in PHASE3_ERROR_BUDGET.md (Type A/B per GUM, k=2, Johnson, ENBW NPLC FAST/NORMAL/LOW).

