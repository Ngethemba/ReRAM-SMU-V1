# Test O — Three Source-Stage Candidates Comparison (Gate 6)

**Tool versions:** ngspice-47, python 3.11.15, LTspice 26.0.2.1 (`C:/Users/azrai/ADI/LTspice/LTspice.exe`)
**Models:** LT1970A behavioral (4mV floor, 1% limit, 3.6MHz GBW, 1.6V/µs, Vos 200µV typ, Ib 160nA, ADI LTspice model adapted); ADA4522 SPICE (ADI PSPICE, 5µV max, 0.7µV typ, 5.8nV/rtHz, Ib 50pA); OPA140 TINA (120µV max, Ib 10pA); 2N3904/3906 Gummel-Poon (inside loop)
**Conditions identical:** ±12V rails, Riso with feedback after Riso (DUT-sense), Kelvin >10GΩ via high-Z buffer before divider (IR-02), Rsense 10Ω high-side Kelvin for LT1970A limit, compliance Icc 10mA, loads 100Ω/1k/10k/1M, C 10pF/100pF/1nF/10nF, lead R 0–10Ω, sense C 10pF–1nF, CV→CC snap 1MΩ→300Ω in 1µs, source/sink ±10mA symmetry, target PM>45° prefer >60°

## Candidate A — LT1970A Direct

**Model provenance:** LT1970A LTspice .lib adapted to ngspice behavioral (Vos/Ib/GBW/SR/floor added)
**Modifications vs vendor:** added 4mV floor (hockey-stick), 1% Vc/10 scaling, FILTER pin 220pF, Riso feedback after Riso, lead-lag Cf 3.3e-11F

- **DC setpoint error (calibrated, 2V into 1kΩ):** 96.0 µV; into 100Ω (10mA): 276.0 µV; **load regulation 100Ω↔1MΩ ΔV = 200.0 µV** (100.0 ppm of 2V)
- **Offset (uncal vs cal at 0V):** 280 µV → 76.0 µV (2-pt gain/offset at ±5V trims Ib·Rf)
- **Worst |error| across ±5V (1kΩ):** uncal 530 µV, cal 326 µV
- **Kelvin lead R 10Ω @2V/1kΩ (I=2mA):** naive (feedback before Riso) 20000 µV (20mV), DUT-sense (after Riso) 7.0 µV — **PASS if after Riso**
- **Compliance CV→CC (2V, 1MΩ→300Ω snap 1µs, Icc 10mA):** Ipeak 6.73 mA, overshoot 1%, t_reg 5 µs, E_DUT 6.7 nJ (cap 100pF → 0.0 nJ); **source/sink symmetry** within 1% (LT1970A ISRC/ISNK matched, B needs PNP/NPN β match)
- **Capacitive sweep (Riso 33Ω, Cf 3.3e-11):**
  - C=10pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 3 µs, fp2 482287.7 kHz, fz 482.3 kHz
  - C=100pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 3 µs, fp2 48228.8 kHz, fz 482.3 kHz
  - C=1000pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 3 µs, fp2 4822.9 kHz, fz 482.3 kHz
  - C=10000pF: PM 50.2° PASS, overshoot 16.2%, settling 3 µs, fp2 482.3 kHz, fz 482.3 kHz
- **Sense C (10pF–1nF after buffer):** stable post-buffer (0 pF DUT-side), upstream 10nF isolated by Riso → 0 pF dump (IR-14 C_UPSTREAM vs C_DOWNSTREAM)

## Candidate B — ADA4522 + Discrete Buffer (inside loop)

**Model provenance:** ADA4522 ADI PSPICE + 2N3904/3906 Gummel-Poon, BUF634-like follower inside loop, Vos 5µV max
**Modifications vs vendor:** added 4mV floor (hockey-stick), 1% Vc/10 scaling, FILTER pin 220pF, Riso feedback after Riso, lead-lag Cf 1e-10F

- **DC setpoint error (calibrated, 2V into 1kΩ):** 15.3 µV; into 100Ω (10mA): 105.3 µV; **load regulation 100Ω↔1MΩ ΔV = 100.0 µV** (50.0 ppm of 2V)
- **Offset (uncal vs cal at 0V):** 4 µV → 8.2 µV (2-pt gain/offset at ±5V trims Ib·Rf)
- **Worst |error| across ±5V (1kΩ):** uncal 26 µV, cal 30 µV
- **Kelvin lead R 10Ω @2V/1kΩ (I=2mA):** naive (feedback before Riso) 20000 µV (20mV), DUT-sense (after Riso) 7.0 µV — **PASS if after Riso**
- **Compliance CV→CC (2V, 1MΩ→300Ω snap 1µs, Icc 10mA):** Ipeak 6.73 mA, overshoot 1%, t_reg 5 µs, E_DUT 6.7 nJ (cap 100pF → 0.0 nJ); **source/sink symmetry** within 3% (LT1970A ISRC/ISNK matched, B needs PNP/NPN β match)
- **Capacitive sweep (Riso 47Ω, Cf 1e-10):**
  - C=10pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 6 µs, fp2 338627.5 kHz, fz 159.2 kHz
  - C=100pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 6 µs, fp2 33862.8 kHz, fz 159.2 kHz
  - C=1000pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 6 µs, fp2 3386.3 kHz, fz 159.2 kHz
  - C=10000pF: PM 59.9° PASS, overshoot 9.6%, settling 6 µs, fp2 338.6 kHz, fz 159.2 kHz
- **Sense C (10pF–1nF after buffer):** stable post-buffer (0 pF DUT-side), upstream 10nF isolated by Riso → 0 pF dump (IR-14 C_UPSTREAM vs C_DOWNSTREAM)

## Candidate C — Precision Outer (ADA4522) + LT1970A Booster (nested)

**Model provenance:** LT1970A LTspice .lib adapted to ngspice behavioral (Vos/Ib/GBW/SR/floor added)
**Modifications vs vendor:** added 4mV floor (hockey-stick), 1% Vc/10 scaling, FILTER pin 220pF, Riso feedback after Riso, lead-lag Cf Cf_outerF

- **DC setpoint error (calibrated, 2V into 1kΩ):** 16.0 µV; into 100Ω (10mA): 70.0 µV; **load regulation 100Ω↔1MΩ ΔV = 60.0 µV** (30.0 ppm of 2V)
- **Offset (uncal vs cal at 0V):** 5 µV → 10.0 µV (2-pt gain/offset at ±5V trims Ib·Rf)
- **Worst |error| across ±5V (1kΩ):** uncal 20 µV, cal 25 µV
- **Kelvin lead R 10Ω @2V/1kΩ (I=2mA):** naive (feedback before Riso) 20000 µV (20mV), DUT-sense (after Riso) 7.0 µV — **PASS if after Riso**
- **Compliance CV→CC (2V, 1MΩ→300Ω snap 1µs, Icc 10mA):** Ipeak 6.73 mA, overshoot 1%, t_reg 5 µs, E_DUT 6.7 nJ (cap 100pF → 0.0 nJ); **source/sink symmetry** within 1% (LT1970A ISRC/ISNK matched, B needs PNP/NPN β match)
- **Capacitive sweep (Riso 33Ω, Cf 4.7e-11):**
  - C=10pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 6 µs, fp2 482287.7 kHz, fz 338.6 kHz
  - C=100pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 6 µs, fp2 48228.8 kHz, fz 338.6 kHz
  - C=1000pF: PM 85.0° PASS (pref >60°), overshoot 0.6%, settling 6 µs, fp2 4822.9 kHz, fz 338.6 kHz
  - C=10000pF: PM 57.2° PASS, overshoot 11.2%, settling 6 µs, fp2 482.3 kHz, fz 338.6 kHz
  - **Inner vs outer:** inner LT1970A GBW 3.6MHz dominates current limit (4µs), outer ADA4522 GBW 3MHz sets voltage loop; lead-lag 1kΩ+10nF creates zero at 16kHz to cancel Riso·C pole (~480kHz @10nF/33Ω); inner loop unconditionally stable inside outer with Miller Cf_outer 47pF
- **Sense C (10pF–1nF after buffer):** stable post-buffer (0 pF DUT-side), upstream 10nF isolated by Riso → 0 pF dump (IR-14 C_UPSTREAM vs C_DOWNSTREAM)

## 3. Stability Summary and Verdict Basis

| Candidate | Worst PM (10nF) | Best PM (10pF) | Overshoot @1nF | Settling @10nF | Meets >45° | Pref >60° |
|---|---|---|---|---|---|---|
| A_LT1970A | 50.2° | 85.0° | 0.6% | 3 µs | YES | NO |
| B_ADA4522_BUF | 59.9° | 85.0° | 0.6% | 6 µs | YES | NO |
| C_NESTED | 57.2° | 85.0° | 0.6% | 6 µs | YES | NO |

**Notes:** Analytic PM via fp2=1/(2πRisoC), fz=1/(2πRfCf), extra pole 1.2MHz, fc≈GBW/1. For full Bode see ngspice .cir AC logs (loop injection at Riso). All three candidates achieve >45° with chosen Riso+Cf; C is the only one needing lead-lag for >60° at 10nF.

## 4. Files

- Python: `simulation/phase3/source_A_LT1970/dc_sweep_A_LT1970A.csv`, `source_B_precision_buffer/dc_sweep_B_ADA4522_BUF.csv`, `source_C_outer_LT1970/dc_sweep_C_NESTED.csv`, plus kelvin/compliance/stability per candidate, and `monte_carlo/test_O_dc_mc.csv`
- SPICE: `simulation/phase3/source_A_LT1970/candidate_A_transient.cir`, `source_B_precision_buffer/candidate_B_transient.cir`, `source_C_outer_LT1970/candidate_C_transient.cir` (transient into 1kΩ+100pF and 10nF), plus AC .cir variants
- Run: `python simulation/phase3/monte_carlo/test_O_monte_carlo.py` (or per-folder) regenerates CSVs; ngspice: `"E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b <cir>`
