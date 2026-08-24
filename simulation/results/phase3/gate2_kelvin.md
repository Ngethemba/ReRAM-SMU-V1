# Gate 2 — Kelvin Servo & Open-Sense — Summary (Tests C+D)
**Project:** ReRAM-SMU V1 — Phase 3 Gate 2  
**Date:** 2026-08-24  
**Sim root:** `simulation/phase3/kelvin/` → results here `simulation/results/phase3/gate2_kelvin.md`  
**Tools:** ngspice-47 `tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b` (primary), `.venv` Python 3.11  
**Requirements:** REQ-DUT-001, REQ-MEAS-007 provisional, REQ-PWR-003, REQ-SAFE-003/004; PHASE3_SIMULATION_PLAN C/D

## Outcome
| Test | Result | Evidence |
|------|--------|----------|
| **C — Differential Kelvin servo** | **PASS** (analytic 160/160); ngspice reference confirms `Vsense=Vset` within -5µV, canonical `V_FORCE=V_DUT+V_SHUNT+I·R_LEAD(+I·R_iso)` exact (3.7e-13 V), headroom >1 V, no oscillation (INCONCLUSIVE ideal) | `test_C_kelvin.py` + `test_C_results.csv` (160 rows) + `test_C_kelvin.cir` run via `ngspice_con.exe -b` (OP+DC+tran log) |
| **D — Open-sense failure** | **PASS** with latched OUTPUT OFF (6/6 scenarios); FAIL without protection (rail to 12V) | `test_D_open_sense.py` + `test_D_results.csv` + `test_D_timing.csv` (sense-open → rail vs latch trace) |

## Test C Highlights
- **Canonical table used (SHUNT_RANGE_TRADEOFF §2.4 D):** 10mA 2.5Ω/25mV, 1mA 25Ω/25mV, 100µA 500Ω/50mV, 10µA 5kΩ/50mV, 1µA 100kΩ/100mV, 100nA 1MΩ/100mV — Johnson/SNR and burden correct, not the superseded fixed-100mV baseline.
- **Sweep:** R_DUT 100/1k/10k/100k/1M × R_lead per lead 0/0.1/1/10 Ω × V_SET ±0.5/1/2/5 V → 160 ideal cases. Autorange per `I_DUT`; `V_HEADROOM=12-|V_FORCE|`, `V_DUT_error=0` ideal.
- **PASS thresholds derived REQ-DUT-001/REQ-MEAS-007:** `|V_DUT_error|<0.5mV @1V` PASS (ideal 0, ngspice -5µV), `headroom>1V` PASS (min 5.88V at worst 100Ω/10Ω/5V), `no oscillation` INCONCLUSIVE (ideal model has no poles — `>45°` requires transistor-level LT1970A nested-loop sim, not claimed).
- **ngspice reference:** DUT 1kΩ, lead 1Ω, shunt 2.5Ω @10mA, V_SET 0.5V, R_iso 10Ω after feedback pick, low-side shunt outside loop. `V_FORCE=0.50724V =0.49999(V_DUT)+0.00125(V_SHUNT)+0.001(V_LEADS)+0.005(R_iso)`; DC sweep -5…+5 mirrors; tran flat. Both polarities verified: `V_FORCE=V_DUT+V_SHUNT+V_LEADS` holds signed.
- **Worst headroom:** 5 V DUT still leaves >6V rail margin; even 100Ω/50mA/10Ω leads → V_FORCE 6.125V, headroom 5.88V (compliance would clamp before this in hardware — model has no compliance).
- **Limitations:** Ideal op-amp Aol 1e5, no Vos/Ib/en, no package L/C, no DUT/cable/relay C, no compliance clamp — see `kelvin/README.md`.

## Test D Highlights
- **Faults covered:** SENSE_HI open, SENSE_LO open, both open, intermittent 1ms chatter, open while output active (2V→5V), sense restored after fault — all 6 scenarios in `test_D_results.csv`.
- **Detection:** Switched continuity before OUTPUT ON via ADG1419-class switch (10pA) + 10MΩ test resistor *behind* switch → window `|Vsense-Vforce|>1V` for >10µs → flag <5µs, latched. During measurement switch OPEN → ≥10GΩ (disconnected); permanent 10MΩ **rejected** (100nA @1V =100% FS on 100nA range).
- **Leakage:** `5V/10GΩ=0.5nA` max (0.05nA @0.5V read, 0.01nA @0.1V) — 50% MUC worst at 5V, <5% at reads; safe-state `<1µA` PASS (0.0005µA).
- **Timing vs latched disable (scenario 5):** Without protection FORCE sails to 12V in ~12µs (1V/µs), DUT 1kΩ →10.8nJ on 150pF C_DOWNSTREAM (vs 1nJ gentle budget) and 36× power overstress; **with latch** glitch 5V/5µs → 1.87nJ then 0V/high-Z. Chatter latch prevents retrigger; restoration stays OFF until `SENS:REM ON`/power-cycle (no auto-resume). `test_D_timing.csv` 0–200µs trace documents this.
- **Fallback evaluation:** `OUTPUT OFF` (high-Z, compliance min-I) **recommended** over `FORCE regulation` (degraded 2-wire, hides fault). FORCE fallback only if explicitly requested with sticky `FAULT_SENSE_OPEN`.
- **Phase-margin note:** Same ideal limitation as C — no analog poles, so <5µs flag is functional, not phase-margin proven; real comparator+switch needs bench timing.

## Files Created
```
simulation/phase3/kelvin/test_C_kelvin.py          # analytic sweep (160 rows)
simulation/phase3/kelvin/test_C_results.csv        # C sweep results
simulation/phase3/kelvin/test_C_kelvin.cir         # ngspice behavioral Kelvin (run: ngspice_con.exe -b)
simulation/phase3/kelvin/test_D_open_sense.py      # D scenario + timing model
simulation/phase3/kelvin/test_D_results.csv        # D 6 scenarios
simulation/phase3/kelvin/test_D_timing.csv         # D timing trace (0–200us, rail vs latch)
simulation/phase3/kelvin/README.md                 # full docs, PASS thresholds, limitations, reproduce steps
simulation/results/phase3/gate2_kelvin.md          # this summary
```

## Reproduce
```powershell
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/kelvin/test_C_kelvin.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/kelvin/test_D_open_sense.py
& "E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b "E:/ReRAM-SMU V1/simulation/phase3/kelvin/test_C_kelvin.cir"
```

## Verdict
- **Kelvin servo correctly regulates SENSE, compensates leads, and budgets burden as headroom** — canonical D table saves 75mV headroom on mA ranges while preserving SNR on nA ranges. Headroom >1V and 0.5mV accuracy PASS under ideal model; real stability needs Candidate C nested-loop sim with `R_iso` and `C_DOWNSTREAM`.
- **Open-sense safe with latched OUTPUT OFF** — switched test meets ≥10GΩ invariant, 0.5nA perturbation, <5µs flag, explicit re-arm. **Do not use permanent 10MΩ pull; do not auto-resume on restoration; prefer OUTPUT OFF over silent FORCE fallback.**
- **Gate 2 C+D: PASS** subject to model limitations (ideal, no parasitics) — hardware must still validate leakage, guard, and LT1970A nested stability on PCB.

*Authority: KELVIN_SENSE_ARCHITECTURE.md, SHUNT_RANGE_TRADEOFF §2.4, PHASE3_SIMULATION_PLAN C/D, REQUIREMENTS.md v0.2.0.*
