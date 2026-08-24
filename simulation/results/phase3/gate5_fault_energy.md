# Gate 5 — Fault & Energy Summary (I+H+K+L)

**Date:** 2026-08-24 **Tooling:** ngspice-47 (`ngspice_con -b`), Python 3.11, matplotlib
**Status:** PASS: energy quantified, trip tolerance 99% within 20%, safe switch sequence defined, POR invariant holds

## I — Energy / Overshoot / Charge
- **Setup:** R 1M→1k linear, Trise 1ms/100µ/10µ/1µ/100ns; Vsrc 2V (5V check); C_down 150pF (100p @5V); Icomp 100µA (500Ω, 50mV FS); Rs+Riso 547Ω.
- **Architectures:** Ideal (0 delay), LT1970A 4µs, TLV3501 crowbar 120% (~5ns), Full-D (LT 4µs + TLV 130%).
- **Key result:** `E_cap=0.30nJ @2V150pF`, `1.25nJ @5V100pF`. For 1ms Trise, `E_dut≈18.5nJ` → `½CV²` underestimates by **61×** (sustained Icomp·V·t). For 100ns snap, ideal `E_dut≈0.85nJ ≈2.8× E_cap`; LT adds ~7nJ overshoot (1.29mA×≈1.3V×4µs); TLV crowbar diverts energy (E_dut<E_cap) to FET.
- **ngspice:** 10µs (60µs tran, 1291 rows) and 1µs (30µs, 2977 rows) show trip at ~14.9µs, RC 4µs ramp, foldback at 17.6µs collapsing Vdut 1.29→0.10V in 0.3µs. Unlimited reference branch stays 1.99→1.29V for comparison. Files `test_I_10us.raw/.wr.dat`, `test_I_1us.raw/.wr.dat`.
- **Files:** `simulation/phase3/compliance/test_I_energy.py` (40 rows =2V×5×4), `test_I_energy.cir`, `test_I_energy_1us.cir`, `test_I_results.csv`

## H — Trip tolerance
- **Inputs:** TLV3501 Vos N(0,2mV)±6.5mV, shunt 0.1% (0.01% sweep), DAC INL ±305µV, gain 0.05%, ref 6ppm, amp 5µV; 1000 runs per config (3 ranges ×3 multiples ×2 DAC =18 +3 0.01% =21 rows).
- **Result 99% interval (AD5764):** 100nA 8.7% span (1.149–1.252 @1.20×) — tight; 10µA 17.3% (1.092–1.300) — OK; 1mA 32.7% (1.004–1.398 @1.20×) — low end hits 1.00× (risk tripping at Icomp). Shunt tightening to 0.01% does not help (Vos dominates). AD5686R vs AD5764 INL difference <1%.
- **Recommendation:** **Range-dependent multiple** (150% @1mA/25mV, 130% @10µA/50mV, 120% @100nA/100mV) — not fixed multiple (fails at low burden) nor fixed ceiling. Histograms `hist_*.png` show distribution.
- **Files:** `simulation/phase3/compliance/test_H_trip_mc.py`, `test_H_results.csv`, 3 PNGs (99% lines marked)

## K — Range switching
- **Faults:** BBM correct, MBB (R∥), stuck, open, bounce 1ms, hot in compliance. Matrix 10 transitions ×6 faults =260 rows (`test_K_results.csv`). Worst MBB 10mA→1mA: R_eff 2.27Ω vs 25Ω → −90.9% Vsense → +1000% current in compliance; open → ∞ overload, blind compliance; 10mA through 1MΩ →100W (proves disable required).
- **Safe sequence:** Freeze 0.5ms → reduce/disable 0.5ms → break 1ms → wait 5ms → make 1ms → settle 10ms → zero 5ms → resume 0.5ms =**23.5ms** total blanking. Compliance flag inhibits autorange; Kelvin mandatory.
- **ngspice:** Scaled 1000× (5ms→5µs) ideal switches `SW(Ron0.1 Roff1G Vt2.5)`: BBM gap 6µs zero-V, MBB overlap 0.9µs parallel 2.27Ω (Vshunt 4.5mV vs 50mV). Files `test_K_switch.cir` (623 pts) `test_K_mbb.cir` (623 pts) `test_K*.raw/.wr.dat`.
- **Files:** `simulation/phase3/range_switch/test_K_switch.py`, `test_K_switch.cir`, `test_K_mbb.cir`, `test_K_results.csv`

## L — POR / Brownout
- **Rails:** +12V 10ms, −12V 20ms, +5V 15ms, ref 5ms, DAC POR 2ms, MCU Hi-Z 100ms, supervisor POR 200ms (10k pulldown + open-drain, dominates Hi-Z), watchdog 200ms; brownout dip 8V at 50–55ms.
- **Invariant:** Full timeline `test_L_timing.csv` (251×11, 1ms steps) shows `LT1970 ENABLE=LOW` until 200ms regardless of DAC full-scale 5V fault (50mA on 10Ω) or Hi-Z — hardware dominates firmware. 200–210ms FW holds low; enable only after checks. No violation before 200ms → **PASS**.
- **ngspice:** Supervisor `R100k·C2u (200ms)` with `Ssup Vt4.5`, pullup 10k, brownout PWL dip, DAC 5V fault injection 55–60ms; tran 0.2m–250m (1314 pts) shows `V(en)` 0V despite Vc=5V until `V(n_sup)>4.5`.
- **Files:** `simulation/phase3/fault/test_L_por.py`, `test_L_por.cir`, `test_L_timing.csv`, `test_L.raw/.wr.dat`

## Traceability
| Requirement | Test | Evidence |
|-------------|------|----------|
| CAUTION 1 + IR-14 (C 80pF @5V/500pF @2V) | I,J | `½CV²` vs `∫V·I` table, 10nF upstream isolated by 47Ω |
| IR-08 TLV3501 6.5mV/6mV hyst | H | MC 99% intervals, range-dependent recommendation |
| IR-04 MECHANIC §4 BBM | K | BBM gap 5ms + settle 10ms, fault matrix |
| REQ-SAFE-003/004 POR | L | 200ms supervisor +10k pulldown, timing csv + spice |

## Model limitations
Ideal DUT switch (no physics), no package L/C, no real relay coil L/flyback (behavioral RC only), LT1970A foldback behavioral (no PSRR/thermal), statistical error models independent.

## Repro
```bash
.venv/Scripts/python.exe simulation/phase3/compliance/test_I_energy.py   # 40 rows
.venv/Scripts/python.exe simulation/phase3/compliance/test_H_trip_mc.py  # 21 rows +3 png
.venv/Scripts/python.exe simulation/phase3/range_switch/test_K_switch.py # 260 rows
.venv/Scripts/python.exe simulation/phase3/fault/test_L_por.py           # 251 rows
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_I_energy.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_I_energy_1us.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/range_switch/test_K_switch.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/range_switch/test_K_mbb.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/fault/test_L_por.cir
```

## Files created (this gate)
```
simulation/phase3/compliance/test_I_energy.py
simulation/phase3/compliance/test_I_energy.cir
simulation/phase3/compliance/test_I_energy_1us.cir
simulation/phase3/compliance/test_I_results.csv
simulation/phase3/compliance/test_I_10us.raw / .wr.dat
simulation/phase3/compliance/test_I_1us.raw / .wr.dat
simulation/phase3/compliance/test_H_trip_mc.py
simulation/phase3/compliance/test_H_results.csv
simulation/phase3/compliance/hist_*.png (3)
simulation/phase3/compliance/README_IH.md  ← PASS: energy quantified, trip tolerance 99% within 20%
simulation/phase3/range_switch/test_K_switch.py
simulation/phase3/range_switch/test_K_switch.cir
simulation/phase3/range_switch/test_K_mbb.cir
simulation/phase3/range_switch/test_K_results.csv
simulation/phase3/range_switch/test_K.raw / .wr.dat etc
simulation/phase3/range_switch/README_K.md ← PASS: safe switch sequence defined
simulation/phase3/fault/test_L_por.py
simulation/phase3/fault/test_L_por.cir
simulation/phase3/fault/test_L_timing.csv
simulation/phase3/fault/test_L.raw / .wr.dat
simulation/phase3/fault/README_L.md ← PASS: POR invariant holds
simulation/results/phase3/gate5_fault_energy.md (this file)
```

*Authority: primary datasheets (LT1970A 1970afc 4µs, TLV3501 Rev E 6.5mV/6mV, AD5764 Rev F ±305µV, AD5686R) override this plan.*
