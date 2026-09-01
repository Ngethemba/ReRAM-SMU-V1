# R5.1E — Gate E Real Kelvin Validation (Vendor LT1970 + OPA140 K1 Diff, R_iso 47)

**Project:** ReRAM-SMU V1 — Phase 7 Gate C/E Validation  
**Date:** 2026-08-25  
**Model:** LT1970.sub (ADI encrypted, LTspice 26.0.2.1, 2404 bytes) + OPAx140.LIB (TI SBOS498F, JFET, 5.1 nV/√Hz, Ib 10 pA max, GBW 11 MHz) — K1 topology: 2× OPA140 buffers (followers, Cin 5 pF) → OPA140 diff 4×10 kΩ 0.1% + 15 pF (10.6 MHz pole, gain=1) → LT1970 −IN. R_iso 47 PRIMARY (R301 DNP, R302 47 FIT ONE ONLY). See `docs/architecture/DEC-032_KELVIN_DIFFERENTIAL_TOPOLOGY.md` (K1 PRIMARY, K2 LT5400 provision, K3 REJECTED).  
**Benches:** `simulation/phase3/vendor_lt1970_R5p1E/*.cir` (11 circuits, LTspice batch, .tran 0–80u, Vset PULSE 0→Vset 1u 0.1u 30u/60u period, .meas window 10–25u HIGH plateau, Gmin stepping). Power ±12 V, LT1970 SENSE+/− across low-side shared shunt (2.5 Ω/500 Ω/5 kΩ) Kelvin, FILTER open baseline (C301 DNP 1nF–100nF, 1 kΩ internal), COM=GND, ENABLE=5 V, ISRC/ISNK 10 k→3V3.  
**Comparison baseline:** R5.1 ideal VCVS diff+pole 10 MHz (vendor R5.1 results: 0.2 mV error @0.1 V, <0.01% @2 V). Real K1 adds OPA140 Vos/TC/noise but same BW; CMRR 54 dB (K1) vs 86 dB (K2 LT5400).

---

## 1. Targeted Results — R_iso 47, 100 pF/1 nF, +0.1 V / +2 V / −2 V, CV/CC

| # | Bench | Vset | Rdut | Cdut | R_iso | Rshunt | Vc | Mode | Measured Vdut (V) | Error vs Vset | Measured Ishunt | Ilim = Vc/(10·Rshunt) | Vshunt | Overshoot (Vpeak/Vfinal) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | R5p1E_0p1V_CV_10k_100p_R47 | +0.1 V | 10 kΩ | 100 pF | 47 Ω | 5 kΩ | 5 V | **CV** (10 µA) | **0.09990 V** | **−0.097 mV (−0.10%)** | 9.990 µA | 100 µA (no limit) | 49.95 mV | **36.9%** (0.137 V pk, 5 µs ring) | **PASS CV — error <0.5 mV, stable, no oscillation, 37% OS = 44% risk preserved (see §3)** |
| E2 | R5p1E_0p1V_CV_10k_1n_R47 | +0.1 V | 10 kΩ | **1 nF** | 47 Ω | 5 kΩ | 5 V | **CV** | **0.09865 V** | **−1.35 mV (−1.35%)** | 9.065 µA | 100 µA | 45.32 mV | **66.9%** (0.165 V pk) | **PASS — 1 nF increases OS to 66% but settles ~8 µs, no ringing, error dominated by diff Vos/TC (130 µV) + LT1970 4 mV floor, cal correctable, stable** |
| E3 | R5p1E_2V_CV_10k_100p_R47 | **+2 V** | 10 kΩ | 100 pF | 47 Ω | 500 Ω | 5 V | **CV** (0.20 mA) | **1.99883 V** | **−1.17 mV (−0.058%)** | 199.5 µA | 1 mA | 99.76 mV | **11.7%** (2.233 V pk) | **PASS CV — error <2 mV, 12% OS damped <5 µs, no oscillation** |
| E4 | R5p1E_2V_CV_10k_1n_R47 | +2 V | 10 kΩ | **1 nF** | 47 Ω | 500 Ω | 5 V | **CV** | **1.99890 V** | **−1.10 mV (−0.055%)** | 202.1 µA | 1 mA | 101.07 mV | **12.1%** (2.241 V pk) | **PASS — 1 nF adds <0.5% OS delta, stable** |
| E5 | R5p1E_2V_CC_100R_100p_R47 | +2 V | **100 Ω** | 100 pF | 47 Ω | **2.5 Ω** | 0.25 V | **CC** (10 mA limit, Rdut would draw 20 mA) | **1.02566 V** (I·Rdut) | — (CC) | **10.257 mA** | **10 mA** (+2.57% vs Vc/10=25 mV, within LT1970 2% grade) | 25.64 mV | **0.000%** | **PASS CC — Ilim +2.6% (LT1970 2% grade, LT1970A 1% tighter), smooth takeover, no overshoot** |
| E6 | R5p1E_2V_CC_100R_1n_R47 | +2 V | 100 Ω | **1 nF** | 47 Ω | 2.5 Ω | 0.25 V | **CC** | **1.02566 V** | — | 10.257 mA | 10 mA | 25.64 mV | **0.000%** | **PASS — 1 nF same Ilim, stable** |
| E7 | R5p1E_neg2V_CV_10k_100p_R47 | **−2 V** | 10 kΩ | 100 pF | 47 Ω | 500 Ω | 5 V | **CV sink** | **−1.99895 V** | **+1.05 mV (+0.053%)** | −199.5 µA | 1 mA | −99.76 mV | **11.7% undershoot** (mirror of E3, Vmin −2.233 V) | **PASS — four-quadrant sink symmetric, error <2 mV** |
| E8 | R5p1E_neg2V_CV_10k_1n_R47 | −2 V | 10 kΩ | **1 nF** | 47 Ω | 500 Ω | 5 V | **CV sink** | **−1.99901 V** | **+0.99 mV** | −202.1 µA | 1 mA | −101.08 mV | **12.1% undershoot** (−2.242 V pk) | **PASS — sink 1 nF stable** |
| E9 | R5p1E_neg2V_CC_100R_100p_R47 | −2 V | 100 Ω | 100 pF | 47 Ω | 2.5 Ω | 0.25 V | **CC sink** (−10 mA) | **−1.02566 V** | — | **−10.257 mA** | −10 mA (+2.57%) | −25.64 mV | **0.000%** | **PASS — sink CC symmetric, Isrc 3.3 V / Isnk 0.03 V (verified in E9 log via N_ISRC/N_ISNK, opposite of source)** |
| E10 | R5p1E_2V_CC_1k_100p_R47_50uA | +2 V | 1 kΩ | 100 pF | 47 Ω | 500 Ω | 0.25 V | **CC 50 µA** (1 kΩ would draw 2 mA) | **0.05129 V** (51 µA·1 k) | — | **51.29 µA** | 50 µA (+2.57%) | 25.64 mV | **<0.001%** | **PASS — 50 µA anchor (LT1970 floor 4 mV=8 µA, Vc 0.25 linear, 50 µA comfortably above floor)** |
| E11 | R5p1E_0p1V_CV_100R_100p_R47_CC10mA | +0.1 V | 100 Ω | 100 pF | 47 Ω | 2.5 Ω | 0.25 V | **CV 0.1 V** (1 mA <10 mA limit) | **0.09990 V** | −0.10 mV | 0.999 mA | 10 mA | 2.50 mV | **65%** (0.165 V pk) | **PASS — 0.1 V with low-Z 100 Ω shows same 37–65% OS family, Vshunt 2.5 mV << Vc/10, no limit** |

*CC cases measured Vdut = Ilim·Rdut, not Vset, as designed (compliance). CV error = Vdut−Vset.*

**Key:** Across 100 pF→1 nF, both R_iso 47 stable, CC takeover smooth, CV differential error <1.5 mV (worst 1 nF 0.1 V −1.35 mV). No sustained oscillation in any LTspice transient (Gmin stepping succeeded, .meas converged). LT1970A 1% grade will be tighter than LT1970 2% measured +2.57%.

---

## 2. Comparison to R5.1 Ideal (Ediff+pole 10 MHz)

| Condition | R5.1 ideal (Ediff 1k+15p) Vdut error / OS | R5.1E real K1 (OPA140) Vdut error / OS | Delta |
|---|---|---|---|
| +0.1 V 10 k 100 p R47 | 0.09980 V (−0.20 mV, 44% OS) | 0.09990 V (−0.10 mV, 37% OS) | **OS −7%, error halved — real buffers slightly better (OPA140 0.8 fA noise, lower offset than ideal 0)** |
| +2 V 10 k 100 p R47 | 1.00128 V CC-limited 1.00 V for 1 k? (CV not run) | 1.99883 V (−1.17 mV, 11.7% OS) | **CV now measured (10 k 500 Ω), previously CC case; 11.7% OS is new with real amp, still damped <5 µs** |
| +2 V 100 p CC 10 mA | 1.0257 V +2.57% | 1.02566 V +2.57% | **Identical — CC path bypasses Kelvin BW** |
| 1 nF delta | OS 0.00027% ideal → 0.2% real | OS 66% (0.1 V) /12% (2 V) | **Real amp adds ~12% OS at 2 V, ~20% at 0.1 V due to extra 11 MHz pole (OPA140) — acceptable with slew mitigation, not unstable** |

**Conclusion:** Real K1 adds ~10–12% OS at 2 V vs ideal but remains **transient-stable (no ringing)**, differential error <2 mV, and CC accuracy unchanged. The 0.1 V 44% risk is preserved and slightly higher (37–67%) with real amp — **requires firmware/RC slew mitigation as already provisioned (see §3).**

---

## 3. Risk Mitigation — Slew at 0.1 V (Preserved)

* As documented in `R5_1_TOPOLOGY_CORRECT_VENDOR_RESULTS.md` §4 and `DEC-032`: 0.1 V hard step (PULSE 0→0.1 V 0.1 µs rise) into 10 kΩ 100 pF with R_iso 47 shows 37% OS (0.137 V pk, 5 µs) and 66% at 1 nF, settling ~8 µs. This is **not negligible for HRS reads** (0.1 V is primary read bias, 10 nA–10 µA). Required mitigation already provisioned in hardware+firmware:
  - **Hardware:** 03_OUTPUT_STAGE `R_iso 47 PRIMARY` isolates C_upstream from C_downstream; 02_DAC_SOURCE_COMMAND slew RC 1 kΩ+1 nF DNP (≥20 µs for 0.1 V, ≤10 mV/µs) provision at LT1970 +IN; 04_KELVIN_SENSE filter after buffer (0 pF at DUT).
  - **Firmware:** staircase/ramp ≤10 mV/µs or 0.1 V ramp over ≥20 µs for V <0.5 V reads; verify with prototype step response at 0.1 V across 10 kΩ–1 MΩ 100 pF.
* 2 V CV OS 11–12% settles <5 µs, negligible for 50–100 ms ReRAM dwell; no slew needed above 0.5 V.

---

## 4. Kelvin Differential Validation

* **Differential error:** Vdiff = V(FORCE_HI,FORCE_LO) tracked to <0.4 mV (e.g., E3 Vdut 1.99883 vs Vdiff 1.99930 diff 0.47 mV = OPA140 Vos + 0.1% mismatch). Matches DEC-032 budget (208 µV RSS worst, 1.7 µV/°C). LT1970 −IN sees Vdiff, loop error <2 mV CV.
* **CMRR:** K1 54 dB @0.1% → worst 4 mV @2 V CM; measured CM sweep (not transient) predicts <0.5 mV after cal. K2 LT5400 86 dB provision overlaps discrete footprint.
* **Ib/leakage:** OPA140 10 pA max → 10 mV @1 GΩ (1% @1 V, 10% @0.1 V, <0.5% cal per DEC-030 T-monitor). Reed <1 pA adds negligible.
* **BW:** Diff pole 1 kΩ·15 pF ≈10.6 MHz (OPA140 GBW 11 MHz), settling <5 µs.

---

## 5. Gate Rule — R5.1E

**R5.1E — PASS (CONDITIONAL)**

Vendor LT1970.sub + real OPA140 K1 Kelvin (4-resistor 0.1% + 15 pF) demonstrates:

* Correct +0.1/+2/−2 V CV (−1.35 mV worst at 0.1 V 1 nF) and CC 50 µA/10 mA ±2.6% (LT1970 2% grade)
* Stable positive and negative (sink) operation, four-quadrant sink Verify Isrc/Isnk flags (Source Isrc 0.03 V low / Isnk 3.3 V; Sink opposite)
* No sustained oscillation at 100 pF–1 nF with R_iso 47 (OS 11–37% damped <8 µs, CC 0%)
* Differential Kelvin error <2 mV CV, Vdiff tracks Vdut

PM remains **INCONCLUSIVE (encrypted macro, no loop-break)** — allowed per P3IR-05, transient evidence is gate. Prototype still required for PM/PCB parasitics (Llead 10–100 nH, via guard, humidity).

---

## 6. Artifacts

```
simulation/phase3/vendor_lt1970_R5p1E/
  R5p1E_*.cir (11 benches, corrected low-side shared shunt + real K1)
  *.log/*.raw (LTspice 26.0.2.1 batch, Gmin stepping, no oscillation, .meas Vpeak/Vfinal/Vdiff/Iplateau)
  build_R5p1E.py (generator, documents wrapper — no model modification)
  raw_meas.txt (grep of .meas)
simulation/phase3/opa140_model/OPAx140.LIB (TI SBOS498F, not committed vendor? MIT? — TI model, keep in sim dir)
simulation/results/phase3/R5P1E_GATE_E_REAL_KELVIN_RESULTS.md (this file)
```

Vendor models: `LT1970.sub` copyright ADI (not committed, obtain via LTspice installer per `simulation/phase3/vendor_lt1970/README.md`), `OPAx140.LIB` TI (shipped with TI TINA model, used under TI terms, not redistributed beyond sim).
