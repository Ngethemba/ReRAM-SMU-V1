# Noise Budget Framework — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 1 research  
**Date:** 2026-08-24  
**Status:** Framework only — categories + equations + example numbers; final numbers require part selection in Phase 2 and measurement.  
**Requirements:** REQ-MEAS-002/003/005, REQ-CAL-003, REQ-GEN-001; distinguishes resolution vs accuracy per ENGINEERING_RULES §7.

---

## 1. Principle — Resolution ≠ Noise ≠ Accuracy

- **Resolution (LSB):** Smallest DAC/ADC code step. Example: 16-bit DAC over ±5 V → LSB = 10 V / 65536 ≈ 153 µV.
- **RMS noise:** Standard deviation of repeated readings under defined conditions (bandwidth, NPLC, temperature). Sets **repeatability**.
- **Accuracy:** Maximum deviation from true value after calibration (includes systematic bias + noise + drift + tempco). Reported as ±(%reading + %range + offset).
- **Minimum useful current:** Lowest current where `3σ_noise < I_signal` and `accuracy << I_signal` such that measurement is scientifically useful (not just detectable).

V1 reports all three separately (REQ-MEAS-005).

Bandlimited white noise and averaging: single-pole filtered noise scales as `σ ∝ sqrt(BW)` and averaging `N` samples improves `σ_N = σ_1 / sqrt(N)` (σ of mean) for uncorrelated white noise only. 1/f and drift do not average away.

---

## 2. Noise sources and equations

### 2.1 Johnson (thermal) noise — resistive elements

For any resistance `R` at temperature `T` (Kelvin, ~300 K) over noise bandwidth `B` (Hz, brickwall):

```
v_n,rms = sqrt(4·k·T·R·B)     [V rms]
i_n,rms = v_n / R = sqrt(4·k·T·B / R)   [A rms]

k = 1.380649e-23 J/K
```

ENBW correction for real filters: single-pole RC `ENBW = π/2 · fc ≈ 1.57·fc`; brickwall (`B`) is quoted below; multiply by sqrt(ENBW/B). NPLC integration gives `BW ≈ 0.44 / (NPLC·20ms @50Hz)` approximation for averaging.

**Example — V1 shunts at B=10 Hz (brickwall) for 100 mV FS:**

| Range | R_shunt (100 mV FS) | v_n 10 Hz | i_n = v_n/R (10 Hz) | i_n / I_FS |
|-------|---------------------|-----------|---------------------|------------|
| 10 mA | 10 Ω | 1.29 nV → 0.0013 µV (1 Hz: 0.41 nV) | 0.129 nA | 13 ppm |
| 1 mA | 100 Ω | 4.07 nV | 0.041 nA | 41 ppm |
| 100 µA | 1 kΩ | 12.9 nV | 0.013 nA | 130 ppm |
| 10 µA | 10 kΩ | 40.7 nV | 0.0041 nA | 410 ppm |
| 1 µA | 100 kΩ | 129 nV | 0.00129 nA | 1290 ppm |
| 100 nA | 1 MΩ | 407 nV | 0.00041 nA (0.41 pA) | 4100 ppm |
| 10 nA (V2) | 10 MΩ | 1287 nV | 0.00013 nA (0.13 pA) | 13000 ppm |

*Calculation:* `python: v=math.sqrt(4*k*T*R*B)`. At B=1 Hz, divide by sqrt(10). Johnson is negligible for 10 mA range but dominates resolution on 100 nA range without averaging. At B=100 Hz, multiply by sqrt(10).

*Python verification (lead, 2026-08-24, .venv):*

```
10 mA R=10 vn@1Hz=0.41 nV in=40.7 pA (0 ppm FS)
100 nA R=1M vn@1Hz=129 nV in=0.129 pA (1.3 ppm FS)
```

### 2.2 Amplifier voltage noise (en) and current noise (in)

- `en` (nV/√Hz) dominates at low R_shunt (current ranges via small R). Refer to datasheet at 1 kHz and 0.1–10 Hz peak-to-peak.
- `in` (pA or fA/√Hz) dominates at high R_shunt (100 nA–1 µA) — bias-current shot/capacitive. For zero-drift chopper amps (e.g., ADA4522 class), `en ≈ 5–10 nV/√Hz`, `in ≈ few pA/√Hz` check datasheet per part — **do not use memory**; leave placeholder for Phase 2 verification.

Total input-referred noise: `v_total = sqrt( en^2 + (in·R_shunt)^2 + (en_Johnson)^2 )` over BW.

### 2.3 ADC noise

- Quantization: `LSB = FS / 2^N`; quantization noise `v_q,rms = LSB / sqrt(12)`.
- Transition noise / ENOB: `ENOB = (SINAD – 1.76)/6.02`.
- Input-referred RTI noise vs OSR/averaging: datasheet gives `µVpp` or `µVrms` at given data rate / PGA.

Example placeholder: ADS1262-class 32-bit ΔΣ at 20 SPS, PGA=1, 5 VFS → ENOB ~ 23 bits → `LSB ≈ 0.6 µV`, noise ~1–2 µVpp — must be verified per actual ADC and data rate for V1.

### 2.4 Reference noise

Precision references (e.g., ADR4525-class) spec: 1/f noise 0.1–10 Hz (µVpp), wideband (µVrms 10 Hz–10 kHz), drift (ppm/°C). Reference noise modulates both DAC and ADC gain → direct accuracy term.

### 2.5 Power-supply noise / PSRR

`v_out_noise = v_supply_noise / PSRR` + regulator noise density. LT1763-class LDO: ~20 µVrms 10 Hz–100 kHz (verify). Analog supply ripple after LC+ferrite must be <10 µVpp in measurement BW.

### 2.6 Digital coupling

MCU clocks (16–170 MHz STM32G4-class), USB FS (12 MHz), SPI/I²C edges couple via ground bounce and mutual inductance. Quantified by PSD with/without USB activity; mitigated by partition, star point, filtering.

### 2.7 Relay / switch charge injection

Reed/signal relay charge injection (pC) on range switch creates transient; thermal EMF (µV) of contacts drifts. Low-thermal relays (<1 µV) preferred.

### 2.8 Bandwidth, integration, filtering

- Measurement BW set by: anti-alias RC → ADC Sinc filter → digital averaging → host NPLC.
- For V1: default NPLC ≈ 1 (20 ms @50 Hz → BW≈22 Hz single-pole → ENBW≈35 Hz). Slower NPLC=10 (200 ms) improves white noise √10 but not drift.
- Bandwidth tradeoff: wider BW → more noise but faster step response and less aliasing of charge injection.

### 2.9 Environmental

- 50 Hz mains hum, microphonics, thermal drifts, airflow, PCB contamination/leakage (R-01).

---

## 3. Example V1 budget skeleton (illustrative, not final)

| Contributor | 10 mA term | 100 nA term | Mitigation |
|-------------|------------|-------------|------------|
| Shunt Johnson (10 Hz) | 1.3 nV (0.13 nA RTI) | 407 nV (0.41 pA RTI) | average, low BW |
| Amp en (5 nV/√Hz, 10 Hz) | 16 nV RTI | 16 nV RTI | zero-drift |
| Amp in (1 pA/√Hz, 10 Hz) | 0.01 nA RTI | 3.2 nA? check part | choose low-in amp for high-R |
| ADC noise (1 µV RTI) | 0.1 µA (10 Ω) | 1 nA (1 MΩ) | PGA, OSR, averaging |
| Reference 0.1–10 Hz 1 µVpp | 0.17 µVrms | same | low-noise ref |

*Numbers are order-of-magnitude placeholders — replace with datasheet values in Phase 2.*

---

## 4. How increasing R_shunt helps and hurts

- **Helps:** `I_sensitivity ∝ 1/R` is not right — actually signal `V = I·R` scales with R, so RTI current noise `i_n = v_n / R` *improves* (falls) as R grows — see table: 100 nA 1 MΩ gives 0.12 pA/√Hz vs 10 mA 10 Ω gives 40 pA/√Hz.
- **Hurts:** burden voltage `V_burden = I·R = 100 mV FS` constant if scaling R ∝ 1/I_FS, but absolute burden matters for DUT (error for 1 Ω DUT vs 1 MΩ DUT); settling time `τ = R_shunt·(C_DUT + C_cable)` grows with R; power `I²R` at full scale constant 100 mV·I_FS (1 mW @10 mA) but TC error `ΔR/R = TC·ΔT` scales with self-heating.

---

## 5. Verification plan (per REQ-CAL-003)

- Measure time series at each range with input shorted (or precision resistor) at fixed T, compute Allan deviation vs averaging time, report `σ_white` vs BW.
- Sweep BW/NPLC and plot noise vs BW to separate white vs 1/f.
- Log with metadata: range, BW, NPLC, T, averaging, supply config.

---

*No hardware simulated. All component numbers require datasheet citation before promotion. Scripts that produce the tables must be committed under `simulation/python/` or `docs/calculations/*.py`.*

