# Gate 5 Tests I + H — Compliance Energy & Trip Tolerance

**Status: PASS: energy quantified, trip tolerance 99% within 20%**

## I — Filament energy
*Model: R 1MΩ→1kΩ, Trise = 1ms,100µs,10µs,1µs,100ns; Vsrc 2V (5V check); C_down 150pF (100pF @5V); Icomp 100µA @500Ω (50mV FS); architectures Ideal / LT1970A 4µs / TLV3501 crowbar 120% / Full-D (LT+TLV130%)*

| Metric | Method |
|--------|--------|
| `Q=∫I_DUT dt` (nC) | Python time-step integration, dt = Trise/500 (0.5ns floor) |
| `E_DUT=∫V·I dt` (nJ) | same |
| `E_cap=½CV²` (nJ) | analytical, reported alongside E_DUT |
| `I_peak, V_final, takeover` | captured per run |

**Key numbers @2V 150pF (E_cap=0.30nJ):**

| Trise | Ideal E_dut | LT1970A E_dut | TLV120 E_dut | Full-D | Takeaway |
|-------|------------|--------------|-------------|--------|----------|
| 1ms | 18.5 nJ | 18.7 nJ | 16.4 nJ | 17.9 nJ | Slow transition: E_dut >> E_cap (61×) — ½CV² **underestimates** by sustained Icomp·V·t. |
| 100µs | 2.66 nJ | 6.88 nJ | 1.79 nJ | 7.16 nJ | — |
| 10µs | 0.99 nJ | 7.40 nJ | 0.33 nJ | 6.99 nJ | Fast snap: E_cap now comparable but LT 4µs adds ~7nJ overshoot (1.29mA×1.3V×4µs ≈6.7nJ). |
| 1µs | 0.85 nJ | 7.43 nJ | 0.20 nJ | 6.95 nJ | — |
| 100ns | 0.85 nJ | 7.42 nJ | 0.18 nJ | 6.94 nJ | Ideal ≈3× E_cap; LT dominates; TLV crowbar diverts cap energy to FET (E_dut < E_cap). |

*5V 100pF check: E_cap=1.25nJ already exceeds 1nJ gentle budget.*

**ngspice:** Two transients at 10µs (`test_I_energy.cir`, 60µs tran, 1291 points) and 1µs (`test_I_energy_1us.cir`, 30µs, 2977 points). Topology `Vsrc→Rsense500→Riso47→C150p∥R_dut(t)` with behavioral `Bdut = V/(1M+(1k-1M)*clamp((t-5µ)/Trise))`, comparator `Ecomp = Vsense>Vthr?5:0`, RC `10k·400p =4µs` for LT takeover, foldback `E1 = Vdel>2.5 ? Vdut+Ilim·Rseries : 2V`. At 10µs, trip detected ~14.9µs, `V(del)` ramps, foldback at 17.6µs collapses `Vdut 1.29V→0.10V` in 0.3µs (captured in `test_I_10us_wr.dat`). Unlimited reference branch shows 1.99V→1.29V without clamp for comparison.

**Verdict:** PASS — energy quantified for all Trise; both `½CV²` and `∫V·I dt` reported, demonstrating `½CV²` underestimates when transition slow or limiter slow.

**Artifacts:** `test_I_energy.py`, `test_I_energy.cir`, `test_I_energy_1us.cir`, `test_I_results.csv` (40 rows =2 V ×5 Trise ×4 arch), `test_I_10us.raw/.wr.dat`, `test_I_1us.raw/.wr.dat`

## H — Trip tolerance Monte Carlo
*TLV3501 emergency supervisor at 120/130/150% Icomp; 1000 runs per range; 100nA (1M 100mV), 10µA (5k 50mV), 1mA (25Ω 25mV)*

**Error models:** Vos N(0,2mV) clip ±6.5mV; shunt N(σ=tol/3) tol 0.1% (0.01% sweep); DAC INL N(σ=INL/3) INL±305µV (AD5686R 2LSB ≈ AD5764 1LSB); gain 0.05% σ; ref 15µV σ (6ppm); amp 5µV σ.

**Results (AD5764, shunt 0.1%, 1000 runs):**

| Range | Nominal | Mean mult | 99% interval | 99% span | Within ±20%? |
|-------|---------|-----------|--------------|----------|--------------|
| 100nA 120% (120mV) | 1.20× | 1.199 | 1.149–1.252 | 8.7% | YES |
| 100nA 130% |1.30×|1.300|1.250–1.350|7.6%|YES|
| 100nA 150% |1.50×|1.500|1.452–1.553|6.7%|YES|
| 10µA 120% (60mV) |1.20×|1.200|1.092–1.300|17.3%|YES (margin 9%)|
| 10µA 130% |1.30×|1.300|1.196–1.405|16%|YES|
| 10µA 150% |1.50×|1.502|1.394–1.599|13.6%|YES|
| 1mA 120% (30mV) |1.20×|1.205|1.004–1.398|32.7%|YES but near edge (low end 1.00× ≈ Icomp)|
| 1mA 130% |1.30×|1.300|1.111–1.511|30.8%|YES|
| 1mA 150% |1.50×|1.504|1.310–1.702|26%|YES|

*Shunt 0.01% at 100nA gives same span (≈8%) — Vos dominates.*

**Recommendation:** **Range-dependent multiple** is best (e.g., 150% @1mA/25mV, 130% @10µA/50mV, 120% @100nA/100mV) — fixes low-burden Vos penalty without over-permitting high-burden. Fixed multiple fails at 25mV (Vos 6.5mV=22% +hyst 20% → trip can hit 1.00×). Fixed ceiling has same burden dependence. DAC choice (AD5686R vs AD5764) INL difference (<1% at 25–100mV) negligible vs Vos; select by supply.

**Histograms:** `hist_100nA_130pct.png`, `hist_10uA_130pct.png`, `hist_1mA_130pct.png` (counts vs effective multiple, red nominal, orange 0.5/99.5% lines).

**Artifacts:** `test_H_trip_mc.py`, `test_H_results.csv` (21 rows includes 0.01% sweep), 3 PNGs

## Model limitations
- Ideal switch DUT (no package L/C, no filament physics, linear R ramp)
- No package L/C, no real relay coil L/flyback except behavioral RC
- LT1970A behavioral foldback (no PSRR, no thermal, no dropout)
- Vos/hyst sampled independent; temperature drift not fully time-correlated

## Repro
```bash
.venv/Scripts/python.exe simulation/phase3/compliance/test_I_energy.py
.venv/Scripts/python.exe simulation/phase3/compliance/test_H_trip_mc.py
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_I_energy.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_I_energy_1us.cir
```

PASS: energy quantified, trip tolerance 99% within 20%
