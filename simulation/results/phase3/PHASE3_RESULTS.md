# Phase 3 — Master Results — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 3 Source, Compliance, Kelvin & Measurement-Front-End Simulation
**Date:** 2026-08-24
**Gate:** No KiCad schematic/PCB/BOM/hardware — simulation & calculation only
**Simulators:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`), LTspice 26.0.2.1 (`C:/Users/azrai/AppData/Local/Programs/ADI/LTspice/LTspice.exe`), Python 3.11.15 `.venv` (numpy 1.26, scipy)
**Canonical ranges:** SHUNT_RANGE_TRADEOFF §2.4 D — 10mA 2.5Ω/25mV, 1mA 25Ω/25mV, 100µA 500Ω/50mV, 10µA 5kΩ/50mV, 1µA 100kΩ/100mV, 100nA 1MΩ/100mV

## Summary Table

| Test | Candidate | Result | Key metric | Requirement | Action |
|------|-----------|--------|------------|-------------|--------|
| A — LT1970A min floor | LT1970A behavioral vs 1970afc | **PASS** | I_min 4mV/R = 4% FS @100mV, 8%@50mV,16%@25mV; 0.1% unreachable (40× over); Vc<60mV NONLINEAR | REQ-SAFE-001 (DEC-024 tiered) | Range coercion (Sol A) + reserve Sol C/D footprint |
| B — Range coercion | Coercion tightest FS≥Icomp Vc≥60mV | **PASS** | 6/6 linear (Vc 125–500mV), 2/6 ideal Vc≥0.5V; ReRAM 50µA-1mA 4/4 PASS; 10µA 50mV tight 0% headroom | REQ-SAFE-001/005 | Coercion satisfies 50µA-1mA; <12µA on 100µA needs C |
| C — Kelvin servo | Ideal 160/160 + ngspice 1kΩ/1Ω/2.5Ω/0.5V | **PASS** | V_DUT error 0 ideal (-5µV ngspice) <0.5mV@1V, headroom >1V (min 5.88V@5V), V_FORCE=V_DUT+V_SHUNT+V_LEADS signed exact | REQ-DUT-001/007, DEC-019 | Keep high-Z buffer>10GΩ, feedback after R_iso |
| D — Open-sense | Switched continuity before ON, latch | **PASS** | 6/6 faults latched OFF; without latch rail to 12V in 12µs (10.8nJ/150pF vs 1nJ budget); leakage 0.5nA@5V/10GΩ (<5% at reads) | REQ-SAFE-003/004, IR-03 | OUTPUT OFF (not FORCE fallback) recommended |
| E — DUT loading | 1M/10M/100M/1G @0.5/1V | **PASS** | Passive 20MΩ divider 4.8%@1M 33%@10M 83%@100M 98%@1G → rejected; buffered JFET 10pA → 0.05% typ <1% @1GΩ (worst 2% @1GΩ 0.5V/10pA) | REQ-DUT-001 ≥10GΩ | JFET OPA140-class buffer first |
| F — DUT-node C | C_DOWN 5p-1nF ×0.5/1/2/5V | **PASS** | E=0.5CV² tabulated vs gentle≤1nJ/standard≤2nJ/forming≤10nJ per V; C_max 80pF@5V/500pF@2V gentle, 160pF/1nF standard | IR-04/14, CAUTION 1 | Enforce recipe-dependent C_DOWN budget |
| G — Bipolar | ±FS 9pts ×6 ranges ×3 front-ends | **PASS** | B midscale VCM2.5V + PGA32: Vout 2.5±0.078V inside 0.1-4.9V RRIO; A true bipolar only AD7175; C direct diff AD7175; PGA required (without PGA rail fail) | REQ-SRC-005 | Select B midscale + PGA32 for single-5V |
| H — Trip tolerance | TLV3501 MC 1000×21 configs 120/130/150% | **PASS** | 99% interval 8.7%@100nA 17.3%@10µA 32.7%@1mA (1mA hits 1.00×); AD5764 vs AD5686R <1% diff | REQ-SAFE-001 trip <5µs | Range-dependent multiple 150%@1mA/130%@10µA/120%@100nA |
| I — Filament energy | 1M→1k 1ms-100ns @2V 150pF/100pF@5V | **PASS** | E_cap 0.30nJ@2V150pF 1.25nJ@5V100pF; 1ms E_dut 18.5nJ (61× underest); 100ns ideal 0.85nJ≈2.8×E_cap; LT 4µs 7nJ overshoot; TLV crowbar diverts | CAUTION 1 | Report Q+E_DUT not just % overshoot |
| J — Up/Down C | C_comp 1/4.7/10nF ×R_iso 10-100Ω before/after | **PASS** | Upstream isolated 95.5-100% not dumped; Downstream 100% dumped; R_iso 33-47Ω preserves PM, too low dumps, too high hurts regulation | IR-14 | C_UP≤10nF before R_iso, C_DOWN≤80-150pF after |
| K — Range switch | 10 trans×6 faults 260 rows + ngspice SW | **PASS** | BBM OK, MBB -90.9% Vsense →1000% current, open ∞, 100W on 1MΩ→100W→disable required; safe seq 23.5ms (freeze 0.5+reduce0.5+break1+wait5+make1+settle10+zero5+resume0.5) | REQ-MEAS-004 | Disable output if hot-switch at high I; flag inhibits autorange |
| L — POR/brownout | +12 10ms -12 20ms +5 15ms ref5ms DAC2ms MCU100ms sup200ms | **PASS** | ENABLE LOW until 200ms via 10k pulldown+supervisor despite 5V fault 55-60ms; brownout 8V dip no enable; 251pts 1ms timeline verified ngspice R100k·C2u 200ms Vt4.5 | REQ-SAFE-003/004 | Hardware dominates firmware |
| M — 100nA leakage | 1pA/10pA/100pA/1nA scenarios ×5 DUT Is | **PASS** | Good 1pA & Moderate 10pA still meet 1nA MUC with offset correction (Johnson 0.41pA 4% of MUC); Poor 100pA destroys 10nA read; Catastrophic 1nA fails 100nA | REQ-MEAS-002 | Need <10pA systematic after guard (reed 1pA not MUX 100pA) |
| N — DAC/reference | AD5686R 0.01%/0.1% vs AD5764 305µV vs AD5791 1000MC 2-pt cal | **PASS** | AD5764 2V +46% headroom k=2, 0.1V +9%/−19%; AD5686R 0.01% +48% at 2V (0.1% REJECT at 1V); half codes OK 3% vs 1.5% for 10mV step | REQ-MEAS-007 | **SELECT AD5764** (CR+O), fallback AD5686R 0.01% |
| O — Source candidates | A LT1970A / B ADA4522+BJT / C nested outer+LT1970A | **PASS (A+B pass, C prototype)** | A PM50° OS6.5% @10nF 0.2%@100p, 13µV load reg, 4µs takeoff PASS; B PM60% OS3.2% best DC but coarse trip >10µs; C PM57° analytic OS16.6% marginal ngspice | REQ-SRC-001..007 | **SELECT A**, **FALLBACK B**, **REQUIRES PROTOTYPE C** |

## Failed / Inconclusive Tests

| Test | Status | Why | Next |
|------|--------|-----|------|
| C stability | **INCONCLUSIVE** (ideal) | Ideal Aol 1e5 no poles → no PM calc; real LT1970A loop needs vendor model bench | Latched to Candidate A/B ngspice AC (see O) for PM>45° proof |
| A 0.1% FS | **FAIL by design** (LT1970A physics) | LT1970A alone cannot meet 0.1% — requires 4V burden; documented as DEC-024 tiered, not failure to tune | Use coercion or Candidate C for 0.1% |

No unexpected SPICE non-convergence hidden; 501-row DC, 623-pt switch, 2977-row I-energy transients all rc=0.

## Model Limitations (summary per simulation/phase3/MODEL_LIMITATIONS.md)

- LT1970A behavioral 4mV floor +1% Vc/10 +3.6MHz/1.6V/µs, not thermal shutdown/SOA/package L/C/ESD/humidity/DA
- ADA4522/OPA140 behavioral Vos/TC/en/Ib, not chopper feedthrough/EMI/PSRR vs freq/leakage/DA
- 2N3904/3906 Gummel-Poon not thermal runaway/SOA/mismatch β
- AD5686R/5764/5791 MC datasheet INL/gain/quant/TC not R-2R code-dependent current/drift vs humidity
- ADR4525/LTC6655 1.6µV/0.775µV p-p not hysteresis −97ppm vs 1ppm/long-term 51ppm/humidity
- ADS1262/AD7175 Sinc/noise/PGA/rejection not DSP group delay/mux leakage/humidity
- Relay 1pA reed vs 10pA-1nA PhotoMOS/CMOS not DA/EMF/humidity/bounce/EMI
- No PCB guard copper/FR-4 DA/flux residue/cleaning/conformal explicit in SPICE

All limitations require bench validation per ENGINEERING_RULES §5.

## Requirement Changes

- None newly revised in Phase 3 — DEC-024 tiered compliance (IR-01) already from Phase 2 correction. If future evidence re-establishes universal 0.1% as true ReRAM experimental requirement, architecture must satisfy via Candidate C (already provisioned).

