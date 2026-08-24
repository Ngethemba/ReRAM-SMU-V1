# Gate 4 — Measurement Front-End Summary (Tests G+E+M)

**Project:** ReRAM-SMU V1 | **Phase 3** | **Date:** 2026-08-24
**Gate:** 4 — Bipolar current, DUT loading, leakage
**Detailed report:** `simulation/phase3/measurement/README_GEM.md` (headers G/E/M)
**Plan ref:** `simulation/PHASE3_SIMULATION_PLAN.md` §G/§E/§M, `SHUNT_RANGE_TRADEOFF.md` §2.4
**Tooling:** ngspice `tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b` (primary), `.venv` Python 3.11

---

## Summary verdict

| Test | Topic | Verdict | Criterion |
|------|-------|---------|-----------|
| **G** | Bipolar current front-end (shunt ±Vs → ADC ±2.5V, strategies A/B/C) | **PASS** | Bipolar feasible with PGA (strategy B midscale VCM=2.5V + PGA32) |
| **E** | DUT sense loading (1M/10M/100M/1G @0.5/1V) | **PASS** | Loading <1% @1GΩ with JFET buffer (10pA worst; typ 0.05%, corrected <0.1%) |
| **M** | 100nA-range leakage (1pA–1nA scenarios, Johnson 0.41pA) | **PASS** | Good (1pA) & Moderate (10pA) still meet 1nA MUC with offset correction |

---

## G — Bipolar (±FS through zero)

- **Ranges:** 10mA/2.5Ω/25mV, 1mA/25Ω/25mV, 100µA/500Ω/50mV, 10µA/5kΩ/50mV, 1µA/100kΩ/100mV, 100nA/1MΩ/100mV
- **Points:** -FS, -50%, -5%, -0.5%, 0, +0.5%, +5%, +50%, +FS (9 per range)
- **Gains:** G_total 100×/50×/25× → G_post@PGA32 3.125×/1.562×/0.781×. Diff at ADC with PGA32 = 78.125mV for all ranges.
- **B midscale (VCM=2.5V):** `Vout = 2.5 ± 0.078V` → well inside RRIO 0.1–4.9V. Without PGA, `2.5 ± 2.5V` hits rails — **PGA required**, demonstrated in spice.
- **A true bipolar:** PASS only with AD7175-class (wide CM, dual supplies); ADS1262 fails CM (0V ∉ 0.3–4.7V).
- **C direct diff:** PASS only with AD7175 (GND CM); ADS1262 fails GND CM.
- **Zero-crossing:** 160µV worst (OPA140) → 0.64% FS @25mV; chopper 15µV → 0.06% — systematic & correctable.
- **Overload 150%:** 117mV at PGA32 >78mV limit → clips; requires PGA step-down / recovery <10ms.
- **Spice:** `test_G_bipolar.cir` — DC sweep -100…+100mV shows -100mV→2.4219V, 0→2.5V, +100mV→2.5781V (all PASS); full-gain path hits clamp, proving headroom argument.

## E — DUT Loading

- **Invalid (20MΩ divider across DUT):** 4.76%@1MΩ, 33.3%@10MΩ, 83.3%@100MΩ, 98.0%@1GΩ — **REJECTED**.
- **Corrected (buffer before divider, OPA140 10pA worst, Rin=1TΩ, Cin=5pF):**
  Resistive error 0.0001%@1M…0.10%@1G negligible; dominant term **Ib·R_DUT**: 0.01mV@1M, 0.1mV@10M, 1mV@100M (0.1%), **10mV@1G (1% @1V)** worst. Typical 0.5pA → 0.05% @1G. With 90% offset-cal residual <0.1% → **<1% @1GΩ PASS**.
- Chopper 50pA → 5%@1G **FAIL** for sense; electrometer 1pA → 0.1% PASS.
- Protection: reed 1pA (0.1% @1G/1V) PASS vs MUX 100pA (10% FAIL) vs ESD 1nA (100% catastrophic).
- DUT-node C: +7–9pF (Cin+relay+ESD); diff filter must be **post-buffer** per IR-04.
- **Spice:** `test_E_buffer.cir` — INVALID 19.6mV vs CORRECTED 1.009V @1V/1G; AC Zin ≈0.999G @1Hz (1G||1T) with Cin roll-off.

## M — Leakage (100nA range, R=1MΩ, BW=10Hz)

- **Floor:** Johnson 0.41pA rms (0.51pA ENBW) = 0.041% of 1nA MUC / **4.1% of 10pA systematic budget** / 41% of 1pA Good scenario. NPLC10 → 0.13pA.
- **Scenarios @100nA FS:** Good 1pA→0.001% err / residual 0.2pA; Moderate 10pA→0.01% / 2.8pA; Poor 100pA→0.10% / 32pA; Catastrophic 1nA→1.0% / 320pA. @1nA reading: Good 0.10%, Moderate 1%, Poor 10%, Catastrophic 100%.
- **Budget:** **<10pA systematic residual after guard/correction** preserves Johnson floor; Good/Moderate meet it, Poor exceeds it.
- **Separation:** Offset-correctable (Ib systematic, ~90% removable), voltage-dependent (PCB surface ∝V, 50% with guard), temp-dependent (Ib doubles/10°C), stochastic (Johnson/1f, BW-limited).
- **100× effects:** Guarded 100G→1pA vs dirty 1G→100pA; reed 1pA vs MUX 100pA — both mandate guard + reed selection + cleaning.

---

## Artifacts

```
simulation/phase3/measurement/test_G_bipolar.py       # sweep: gain/CM/rail/zero-cross/overload
simulation/phase3/measurement/test_G_results.csv       # 162 rows (9 points × 6 ranges × 3 strategies)
simulation/phase3/measurement/test_G_bipolar.cir       # behavioral Vout=VCM+G_post·Vs
simulation/phase3/measurement/test_G_bipolar.log       # 21-point DC sweep
simulation/phase3/measurement/test_E_loading.py        # DUT 1M–1G @0.5/1V, invalid vs 4 buffers
simulation/phase3/measurement/test_E_results.csv       # 80 rows
simulation/phase3/measurement/test_E_buffer.cir        # high-Z follower vs invalid divider
simulation/phase3/measurement/test_E_buffer.log        # OP+DC+AC 1Hz–1MHz
simulation/phase3/leakage/test_M_leakage.py            # 100nA-range 4×5 matrix
simulation/phase3/leakage/test_M_results.csv           # 20 rows
simulation/phase3/measurement/README_GEM.md            # detailed G/E/M report
simulation/results/phase3/gate4_measurement.md         # this gate summary
```

Repro:

```bash
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/measurement/test_G_bipolar.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/measurement/test_E_loading.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/leakage/test_M_leakage.py
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/measurement/test_G_bipolar.cir -o simulation/phase3/measurement/test_G_bipolar.log
"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b simulation/phase3/measurement/test_E_buffer.cir -o simulation/phase3/measurement/test_E_buffer.log
```

---

## Model limitations (preliminary — hardware verification required)

Ideal leakage resistors (no humidity/DA/fingerprints), no real ADC DSP/filter/NPLC, no PCB distributed leakage or cable DA, linearized temp/humidity scalars, op-amps as Rin/Cin/Ib idealized (E-source not vendor subcircuit), ESD as fixed 1nA not exponential I-V. Simulation does not prove layout-dependent leakage; guarded layout + measurement on guarded hardware required per `GUARD_STRATEGY.md`.

---

*Authority: datasheets (ADS1262, AD7175, OPA140, ADA4522/4530, LT1970A) override this simulation. Traceability: REQ-MEAS-001/002/004/008, REQ-DUT-001, SHUNT_RANGE_TRADEOFF §2.4, PHASE3_SIMULATION_PLAN G/E/M.*
