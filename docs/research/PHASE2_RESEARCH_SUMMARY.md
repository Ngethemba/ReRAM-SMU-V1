# Phase 2 Research Summary — ReRAM-SMU V1

**Date:** 2026-08-24  
**Gate:** Architecture & Candidate Component Verification — 6 agents A–F + lead calculations; no schematic/PCB/BOM.

## Subagent outputs integrated

| Agent | Primary file(s) | Outcome |
|-------|-----------------|---------|
| A Source | `SOURCE_STAGE_CANDIDATES.md` (55 KB) | LT1970A primary + precision+discrete alternate; CAUTION 1/2 resolved |
| B Front-end | `MEASUREMENT_FRONTEND_CANDIDATES.md` (21 KB) + `SHUNT_RANGE_TRADEOFF.md` + `KELVIN_SENSE_ARCHITECTURE.md` (7.4 KB) | Hybrid shunt+TIA, low-side outside SENSE, range-dependent burden (100→50→25 mV), reed/PhotoMOS |
| C Compliance | `COMPLIANCE_ARCHITECTURE.md` (48 KB) + `COMPLIANCE_ENERGY_ANALYSIS.md` (27 KB) | Option D dual continuous+trip/SOA recommended; E=0.5CV² (10 nF@5 V=125 nJ dominates) |
| D Precision | `PRELIMINARY_ERROR_BUDGET.md` (28 KB) + `PHASE2_COMPONENT_MATRIX.md` contribution + py budget | AD5764 preferred over AD5686R (-11% @1 V), ADR4525/LTC6655/REF50xx branch, ADA4522/OPA140 role-dependent, ADS1262 vs AD7175, STM32G431 provisional |
| E Grounding | `GROUNDING_AND_RETURN_PATHS.md` (36 KB) + `ISOLATION_STRATEGY.md` (23 KB) + guard/power/thermal stubs (lead completed) | Single plane partitioned, isolation optional footprint, guard reserved copper |
| F Lifecycle | `PHASE2_COMPONENT_MATRIX.md` (32 KB, 6-agent merged) | AD5686R/ADA4522/LT1970A active production, ADS1262 active, LT1763 active, ADR4525 active, STM32G431 active; SPICE models LT1970A (LTspice), ADA4522 (Pspice) etc. |

## Lead calculations (independent)

- Burden: 100 mV =5% @2 V/16.7% @0.6 V → range-dependent 100→50→25 mV proposal; Johnson 0.41 pA @100 nA/10 Hz, 1.29 pA @1 MΩ with 10 nF load.
- Thermal: Pd 70–170 mW worst-case (source +5 V/10 mA 70 mW, sink +5 V/–10 mA 170 mW) vs DUT 50 mW — not same; ΔT 6–15 °C no heatsink.
- Energy: 10 nF@5 V 125 nJ, 100 nF cable 1.25 µJ → limit output C ≤10 nF + 10 Ω isolation.

## Architecture synthesis

`ARCHITECTURE.md` (7.8 KB) + `PHASE2_DECISION_MATRIX.md` (4.9 KB) integrate above: functional block diagram with USB→MCU→DAC→LT1970A source + low-side hybrid shunts (outside SENSE) + TIA provision, SENSE feedback at DUT, compliance dual, Kelvin with open-sense pull-up, single-plane grounding, optional isolator/guard, banana+BNC, ±12 V → LDO tree.

Cautions resolved: CAUTION 1 bipolar Source-V/Measure-I with sink = true 4-quad experimental behavior (not arbitrary I-source); CAUTION 2 burden outside SENSE is not corrected — budgeted as headroom; CAUTION 3 per-segment/polarity programmable compliance; CAUTION 4 Kelvin for lead-drop not resistance threshold; CAUTION 5 single-plane partitioned not split AGND/DGND.

No component promoted to FINAL — SELECTED FOR PHASE 3 requires simulation gates per ENGINEERING_RULES.
