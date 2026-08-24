# Low-Current Measurement — Precision, Noise, and Metrology

**Project:** ReRAM-SMU V1 — Phase 1 / Subagent B  
**Date:** 2026-08-24  
**Scope:** Metrology of nA–fA measurement; noise mechanisms relevant to 10 mA → 100 nA (and 10 nA) SMU ranges; burden-voltage trade-offs; guard/leakage. No hardware design — research and calculation scaffold only.  
**Governance:** Complements `REQUIREMENTS.md` (REQ-MEAS-001/002/005) and `ENGINEERING_RULES.md` rules 6–8. Every quantitative claim cites a primary or secondary source (see References).

> **One-line summary:** Resolution is what the ADC can *count*; RMS noise is what the analog chain *actually fluctuates*; minimum useful current is the smallest signal you can *see repeatably* above that noise; accuracy is how far that reading is *from truth* after calibration. Never conflate them.

---

## Table of Contents

1. [Resolution vs RMS Noise vs Minimum Useful Current vs Accuracy](#1-resolution-vs-rms-noise-vs-minimum-useful-current-vs-accuracy)
2. [Noise Sources — Catalog and Scaling](#2-noise-sources--catalog-and-scaling)
3. [Low-Current Constraints for ReRAM-SMU V1](#3-low-current-constraints-for-reram-smu-v1)
4. [Guard, Leakage, and Insulation](#4-guard-leakage-and-insulation)
5. [Shunt Burden-Voltage — Summary and Comparison](#5-shunt-burden-voltage--summary-and-comparison)
6. [References](#6-references)

---

## 1. Resolution vs RMS Noise vs Minimum Useful Current vs Accuracy

These four terms are routinely conflated in SMU/DMM marketing. They are orthogonal.

### 1.1 Definitions (metrology)

| Term | Symbol | Definition | What limits it | Typical misuse |
|------|--------|------------|----------------|----------------|
| **Resolution** | LSB = FS / 2^N | Smallest code step the converter can report. Purely digital. | ADC bits, FS, decimation / oversampling | "24-bit = 24-bit accurate" |
| **RMS noise** | σ = √(Σ vn²) | One-sigma fluctuation of repeated readings with input shorted/open, in same units as signal. Includes analog noise integrated over bandwidth. | Johnson, amplifier, reference, PSU, digital coupling | Quoted as resolution |
| **Peak-to-peak noise** | ≈ 6.6 · σ (Gaussian, 99.9% of samples) | Worst-case envelope seen on a bench. What the user *sees*. | Same as RMS, scaled | Confused with σ |
| **Minimum useful current (MUC)** | k · σ (k = 3…10) | Smallest current you can distinguish from zero with acceptable confidence. Not a spec — a *policy* choice. | RMS noise, required SNR, settling/leakage | Claimed as "sensitivity = LSB" |
| **Accuracy** | ±(% reading + offset + drift) | Distance from true value (traceable standard), after gain/offset calibration, over temp/time. | Shunt tolerance + TC, amplifier Vos/TCVos, INL/DNL, reference, leakage, burden error | "LSB = accuracy" or "noise = accuracy" |

**REQ-MEAS-005 is binding:** documentation and firmware must report resolution and accuracy separately.

### 1.2 Numerical illustration (100 mV shunt FS)

| ADC | LSB (100 mV FS) | LSB as current on 100 nA range (R=1 MΩ) | Johnson σ, B=10 Hz (100 nA range) | Johnson σ, B=1 kHz |
|-----|-----------------|------------------------------------------|------------------------------------|--------------------|
| 16-bit | 1.53 µV → 1.53 pA | 1.53 pA | 0.41 pA rms | 4.07 pA rms |
| 18-bit | 381 nV → 0.38 pA | 0.38 pA | 0.41 pA rms | 4.07 pA rms |
| 24-bit | 5.96 nV → 5.96 fA | 5.96 fA | 0.41 pA rms | 4.07 pA rms |

*Interpretation:* A 24-bit ADC resolves 6 fA — but you still have 400 fA rms of Johnson noise alone at 10 Hz on the 100 nA range. Extra bits below the noise floor add *codes*, not *information*. Oversampling + averaging reduces noise only as √N and quickly hits the analog floor.

### 1.3 How to report correctly

```text
Range 100 nA (R = 1 MΩ, FS = 100 mV):
  Resolution (24b):       5.96 nV  ≡ 5.96 fA
  RMS noise (10 Hz BW):   407 nV   ≡ 0.41 pA   (Johnson only; system higher)
  Peak-peak noise (~6.6σ): 2.69 µV  ≡ 2.69 pA
  Minimum useful current
    3σ (detection):       1.22 pA
    10σ (quantitative):   4.07 pA  (≈ 4% of FS)
  Accuracy (example):
    ±(0.05% reading + 0.02% FS + TC·ΔT + offset)
    At 50 nA, 25 °C ±10 °C, 25 ppm shunt: ±25 nA·0.05% ≈ ±12.5 pA plus ±25 µV/R = ±25 pA (+ drift)
```

Accuracy is *always* quoted as **% reading + offset + temperature coefficient + time drift**, never as a single LSB.

### 1.4 The three most common fallacies

1. **"24-bit ADC → 1 part in 16 million accuracy."** False. ENOB is 5–8 bits worse than nominal bits once reference noise, INL, and analog noise are included. A 24-bit ΔΣ at 10 SPS may deliver 18–20 noise-free bits.
2. **"Noise-free resolution = usable sensitivity."** False. Datasheets quote noise-free bits at one fixed filter. Changing bandwidth, range, or source impedance invalidates it.
3. **"Minimum current = LSB current."** False. The LSB is a *quantization* floor; the measurement floor is set by total RMS noise and leakage/bias.

---

## 2. Noise Sources — Catalog and Scaling

Total RMS noise adds in quadrature: `σ_total² = Σ σ_i²`. Dominant source dominates.

### 2.1 Johnson (thermal) noise — the inescapable floor

```
vn = √(4·k·T·R·B)     [V rms]        (1)
in =  vn / R = √(4·k·T·B / R)  [A rms]  (2)

k = 1.380649e-23 J/K (exact, SI 2019)
T = 300 K (27 °C) nominal;  ~ √T scaling, ~ +0.16% per °C
B = noise bandwidth (ENBW) in Hz — NOT the –3 dB frequency unless brick-wall
```

**ENBW correction:** Single-pole RC → ENBW = (π/2)·fc ≈ 1.57·fc → vn is √1.57 ≈ 1.25× the brick-wall value at fc. Higher-order filters → lower overhead (e.g., 4th-order Butterworth ~1.03·fc). Always state which is used.

**Representative Johnson values for the ReRAM-SMU candidate shunts (100 mV FS):**

Full table and derivation in `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md` and `NOISE_BUDGET_FRAMEWORK.md`. Key excerpt (T=300 K, brick-wall):

| Range | R (100 mV FS) | vn density | in density | σ_i (B=10 Hz) | σ_i (B=1 kHz) | σ_i as %FS (B=10 Hz) |
|-------|---------------|-----------|-----------|---------------|---------------|----------------------|
| 10 mA | 10 Ω | 0.41 nV/√Hz | 40.7 pA/√Hz | 129 pA | 1.29 nA | 0.001% |
| 1 mA | 100 Ω | 1.29 nV/√Hz | 12.9 pA/√Hz | 40.7 pA | 407 pA | 0.004% |
| 100 µA | 1 kΩ | 4.07 nV/√Hz | 4.07 pA/√Hz | 12.9 pA | 129 pA | 0.013% |
| 10 µA | 10 kΩ | 12.9 nV/√Hz | 1.29 pA/√Hz | 4.07 pA | 40.7 pA | 0.041% |
| 1 µA | 100 kΩ | 40.7 nV/√Hz | 407 fA/√Hz | 1.29 pA | 12.9 pA | 0.13% |
| 100 nA | 1 MΩ | 129 nV/√Hz | 129 fA/√Hz | 0.41 pA | 4.07 pA | 0.41% |
| 10 nA | 10 MΩ | 407 nV/√Hz | 40.7 fA/√Hz | 0.13 pA | 1.29 pA | 1.29% |

*Lesson:* Johnson *voltage* noise grows as √R; Johnson *current* noise *falls* as 1/√R. On the 100 nA range, 1 kHz of Johnson alone already eats 4% of FS. Bandwidth limiting (integration/averaging) is not optional at low currents.

> Source: Equation (1) is the Nyquist (1928) result; Keithley *Low Level Measurements Handbook* 7th Ed. §2.6.5/3.2.6 and TI SBOA597 §2 derive and tabulate it identically.

### 2.2 Amplifier noise

An op-amp/instrumentation amplifier contributes:

- **Voltage noise** `en` (nV/√Hz, plus 1/f corner typically 0.1–10 Hz). Multiplied by **noise gain** `1 + Rf/Rin` (or `1 + R_shunt_source/R_feedback` for TIA). For a shunt front-end with gain G, output `en_out = en · G`, input-referred current `en / R_shunt`.
- **Current noise** `in` (fA/√Hz to pA/√Hz). Flows through source/shunt impedance → `vn = in · R_eq`. CMOS/JFET inputs: ~0.1–10 fA/√Hz (good), bipolar: ~100 fA–1 pA/√Hz (poor for nA ranges).
- **1/f (flicker) noise** — dominates below the corner frequency. At 0.1–10 Hz, en can be 10× the broadband density. Must use chopper/zero-drift (e.g., ADA4522, OPA388) or explicitly budget it. Datasheet "0.1–10 Hz p-p noise" is the right number to use, not the 1 kHz density.
- **Offset drift** `TCVos` (nV/°C, µV/°C). Not noise, but indistinguishable from signal after temperature change. A 1 µV/°C Vos drift on a 100 nA range (1 MΩ) is 1 pA/°C — already 1% of FS per 10 °C.

**Rule of thumb:** Choose an amplifier whose `in · R_shunt` and `en` are each ≤ ⅓ of the Johnson `vn` at the target bandwidth, otherwise the amplifier, not the shunt, sets the floor.

Example (100 nA range, 10 Hz):
- Johnson vn = 407 nV rms.
- A chopper amp with en = 5 nV/√Hz → input-referred ~ 5·√10 ≈ 16 nV rms (negligible vs 407 nV).
- But `in = 1 fA/√Hz` through 1 MΩ → 1 µV/√Hz? Wait: `in·R = 1 fA·1 MΩ = 1 nV/√Hz` — negligible. `in = 1 pA/√Hz` → 1 µV/√Hz → dominates. So bipolar-input amps are disqualified for ≥100 kΩ shunts.

### 2.3 ADC noise

- **Quantization noise** `q / √12` where `q = LSB`. Usually negligible vs analog noise once oversampled.
- **Input-referred noise** `e_adc` — from datasheet SNR/SINAD or "input noise" in µV rms at a given data rate. For a 24-bit ΔΣ (ADS1220, ADS1263, LTC2500): typically 1–5 µV rms at 20 SPS, 10–30 µV rms at 1 kSPS (depends on PGA gain). Refer back to shunt: `i_adc = e_adc / (G · R_shunt)`.
- **INL/DNL** — systematic non-linearity, not random. INL of ±2 ppm FS at 24-bit is 200 nV on 100 mV FS → 0.2 pA on 100 nA range. Calibratable, but sets the *accuracy* floor.
- **Reference noise** `e_ref` — multiplied by signal (ratiometric not; absolute is). A 2.5 V reference with 3 µV p-p (0.1–10 Hz) → 1.2 ppm. On 100 mV FS with gain 25, contributes 3 µV·(0.1/2.5) = 120 nV input-referred.

**Takeaway:** On the lowest ranges, ADC + reference noise often exceeds Johnson. Budget them as input-referred currents.

### 2.4 Voltage reference noise

`vn_ref` is amplified by the same gain as the signal if the ADC is not ratiometric to the shunt. Low-frequency (0.1–10 Hz) p-p is the critical number (e.g., ADR4525: 1.25 µV p-p, LTC6655: 0.5 µV p-p, LM4040: 15 µV p-p). Keep reference bandwidth limited (RC filter 1–10 Hz) and use Kelvin routing.

### 2.5 Power-supply noise and PSRR

- Switch-mode ripple (100 kHz–2 MHz) → aliased by ADC → use LDO post-reg + LC π-filter, PSRR ≥ 80 dB at ripple frequency.
- 50/60 Hz mains → dominant spur in low-current measurements. Use integration over PLC (power-line cycles): `Tint = N · 20 ms` (50 Hz) or `N · 16.67 ms` (60 Hz) → notch at mains and harmonics (sinc response). Keithley 6517B and 4200-SCS use NPLC = 1–10 for this reason.
- Low-frequency supply drift → modulates amplifier Vos through PSRR.

### 2.6 Digital coupling (the hidden budget-killer)

- MCU/FPGA switching currents through shared ground → mV spikes at the analog input via ground bounce. Keep **star ground** or **partitioned AGND/DGND** with a single tie at the ADC. Route digital traces away from high-Z nodes (shunt sense lines).
- Clock harmonics (e.g., 16 MHz SPI) alias into the passband if not filtered. Add **RC anti-alias** before the ADC (cutoff ≈ ½ sample rate) and choose sample rates that avoid coherent spurs.
- Charge injection from range-switching relays/MUXes (see §2.7).

### 2.7 Relay / switch / MUX noise

Every range switch injects:

- **Charge injection** `Qinj` (pC) from MOSFET/MUX gate capacitance → `ΔV = Qinj / C_load` → appears as a transient that decays as `R·C`. For a 10 pC injection into 100 pF + 1 MΩ → 100 mV transient → seconds to settle at low currents.
- **Leakage** `Ileak` (pA–nA) of open switch → adds to signal. Reed relays: ~1 pA (good), solid-state MUX (ADG1408): ~10–100 pA (problematic for 100 nA range). For 10 nA range, even 1 pA is 10% error. Use **guarding** or **T-switch** topology, or avoid solid-state on the lowest range.
- **Thermoelectric EMF** from relay contacts (Cu–Kovar junction ~ 40 µV/°C) → µV offsets modulated by thermal gradients. Use low-EMF relays (Coto 9007, Pickering 131) and keep away from hot regulators.
- **Dielectric absorption** in the switch package and PCB → long-tail settling (10–100 s) after overload.

*Implication for ReRAM-SMU V1:* Keep 10 mA–10 µA on solid-state + reed; reserve dedicated reed or no-switch (fixed-gain + software range) for 1 µA/100 nA if <10 pA error is required.

### 2.8 Bandwidth, integration, and filtering — where noise is *decided*

Noise is *bandwidth*. Halving bandwidth halves noise power (σ ∝ √B). Options:

| Method | Noise scaling | Settling | Aliasing | Use |
|--------|--------------|----------|----------|-----|
| **Analog RC** (single pole) | +1.25× ENBW overhead | `τ = RC`, 5τ to 1% | No anti-alias alone — needs higher-order or digital decimation | Front-end anti-alias |
| **Higher-order analog** (Sallen-Key, 3-pole) | ~1.03× | Slower step | Good anti-alias | Before ADC |
| **ADC sinc / averaging** (ΔΣ) | `σ ∝ 1/√N` (N = samples averaged) | `Tint = N / f_s` | Built-in sinc notches | Always |
| **PLC integration** | Sinc nulls at `k / Tint` — e.g., NPLC=1 nulls 50/60 Hz | Multiples of 20/16.67 ms | Excellent for mains | DC/low-rate |
| **Digital IIR/FIR after sampling** | Further √B reduction | Extra group delay | Must not alias first | Post-processing |

**Recommended V1 stance (provisional):**

- Front-end: 2nd- or 3rd-order anti-alias ~1–10 kHz (above max ReRAM sweep rate, below ADC Nyquist).
- ADC: ΔΣ with configurable data rate; default NPLC=1 (20 ms at 50 Hz mains, i.e., TR mains = 50 Hz assumed; auto-detect 50/60 Hz in firmware.
- Additional firmware integration: selectable 10/100/1000 PLC or exponential averaging, trading speed for resolution.

### 2.9 Environmental interference

| Source | Coupling mechanism | Magnitude (order) | Mitigation |
|--------|-------------------|-------------------|------------|
| 50/60 Hz mains E-field | Capacitive to high-Z node (C≈1 pF, dV/dt≈ 300 V·2π·50 ≈ 100 kV/s → 100 nA) | nA–µA if unshielded | **Shielded enclosure**, coaxial/triaxial cabling, guard |
| Magnetic (transformer, motor) | Inductive loop (area × dB/dt) | nV–µV (small for current, large for voltage) | Twisted pairs, minimal loop area, mu-metal if needed |
| Triboelectric (cable flex) | Charge on dielectric movement | pA–nA spikes | Low-tribo coax (Keithley SC-93), fix cables, avoid flex during measurement |
| Piezoelectric (PCB, connector stress) | Mechanical strain → charge | pA–nA | Avoid ceramic caps on high-Z nodes (use C0G/NP0 or film), strain relief |
| Humidity / surface leakage | Ionic film on PCB → R_surface drops from 10^12 to 10^9 Ω | 100 pA–10 nA at 100 mV (1 GΩ leak = 100 pA) | Conformal coat, guard ring, clean + bake (IPA + DI water), controlled storage |
| Light | Photocurrent in diodes/junctions | pA–nA | Opaque enclosure, cover DUT, avoid clear packages |
| Temperature gradients | Thermoelectric + TCR drift | µV–mV equivalent | Isothermal layout, keep shunts/amps away from regulators, warm-up 30–60 min |
| Air currents / vibration | Modulates capacitance + thermoelectric | fA–pA drift | Draft shield, vibration isolation on bench |

Measured practice (Keithley 4200-SCS AppNote): consistent sub-nA measurement requires a **shielded, light-tight, vibration-isolated fixture** and 60 min warm-up — bench-top PCB alone cannot reliably hold <1 nA without enclosure discipline.

---

## 3. Low-Current Constraints for ReRAM-SMU V1

### 3.1 Where V1 stops and why

| Range / Target | Status | Feasibility on PCB without electrometer measures | Limiting factor |
|----------------|--------|---------------------------------------------------|-----------------|
| 10 mA | Confirmed target | Easy | Thermal / compliance headroom |
| 1 mA | Provisional | Easy | Shunt TC, amplifier drift minor |
| 100 µA | Provisional | Easy | Offset <0.1% achievable with zero-drift amp |
| 10 µA | Provisional | Moderate | Johnson + amplifier `in·R` still small; guard nice-to-have |
| 1 µA | Provisional | Moderate | Leakage (~pA) is <0.1% of 1 µA; no guard strictly required but recommended |
| **100 nA** | **V1 floor (provisional)** | **Challenging — achievable with care** | Leakage/pA, relay/MUX leakage, cable tribo, Johnson 0.4% at 10 Hz; needs guard ring, reed isolation, shield |
| **10 nA** | **V2 (explicitly future)** | **Not reliable on standard PCB** — requires electrometer-grade techniques: guard-driven triax, Teflon standoffs / floating input, femto-amp op-amp (ADA4530-1, LMC662), air-wiring, humidity control, full enclosure. Discussed here for completeness only. |

**10 nA analysis (for completeness, not V1):**
- Shunt R = 10 MΩ (100 mV FS). Johnson σ = 0.13 pA (10 Hz) / 1.29 pA (1 kHz) → 1.3% / 12.9% of FS.
- A 10 GΩ surface leak at 100 mV → 10 pA error = 100% of FS. At 5 V source bias, leakage through a 1 GΩ contamination path → 5 nA error = 500× FS. Guard is *mandatory*, not optional.
- Relay/MUX charge injection (10 pC) onto 1 pF stray → 10 V transient → minutes to recover. Requires dedicated electrometer MUX (ADG1211, DG419 with guard) or manual range.
- Recommendation: **Do not promise 10 nA in V1.** Document it as a V2 research track with a separate electrometer daughter-card and triaxial fixture.

### 3.2 Error-budget preview by range (100 mV FS, ΔT = ±10 °C, 25 ppm shunt, B=10 Hz, chopper amp)

| Range | Johnson σ (10 Hz) | Amp `en`+`in` contrib. (typ.) | Relay leak (est.) | TC drift (10 °C) | Combined 3σ floor | As %FS |
|-------|-------------------|-------------------------------|-------------------|------------------|-------------------|--------|
| 1 mA | 40 pA | ~10 pA | <1 pA | 250 ppm → 250 nA (0.025%) | ~0.13 nA | 0.013% |
| 10 µA | 4 pA | ~5 pA | <2 pA | 250 ppm → 2.5 nA (0.025%) | ~19 pA | 0.19% |
| 1 µA | 1.3 pA | ~3 pA | ~5 pA | 250 ppm → 250 pA (0.025%) | ~10 pA | 1% |
| 100 nA | 0.41 pA | ~2 pA | ~5–20 pA | 250 ppm → 25 pA (0.025%) | ~15–60 pA | 15–60% at 3σ? Wait — TC dominates |

*Correction:* The TC row above is **gain error** (scales with reading), not an absolute offset. At 10% of FS, TC error is 0.25 nA on 10 µA, not 2.5 nA. The absolute floor is dominated by leakage on the 100 nA range. See `NOISE_BUDGET_FRAMEWORK.md` for the full RSS budget with worked numbers. Bottom line: **100 nA is leakage-limited, not Johnson-limited.**

### 3.3 Settling vs speed

- Shunt + input capacitance `τ = R_shunt · C_total` where `C_total ≈ C_cable + C_pcb + C_input` (typically 10–100 pF). For 100 nA (1 MΩ, 50 pF) → τ = 50 µs → 5τ ≈ 250 µs to 1%. Sounds fast — but leakage/DA adds seconds of tail. For 10 nA (10 MΩ, 50 pF) → τ = 500 µs, and relay charge tails dominate.
- Transimpedance alternative: `τ_eff = Rf · Cf / Aol` feedback — effectively much faster for same Rf, which is why feedback ammeters settle 100–1000× faster for high-R measurements (NI AppNote: factor = open-loop gain A ≈ 10^6).

---

## 4. Guard, Leakage, and Insulation

### 4.1 What leakage does

Every unwanted resistance `R_leak` across a voltage `V` injects `I_leak = V / R_leak` into the measurement node. Guarding makes `V ≈ 0` across that resistance, so `I_leak → 0` even if `R_leak` is modest.

```
Without guard:  I_meas = I_DUT + V_force / R_leak
With guard:     I_meas = I_DUT + (V_force - V_guard) / R_leak ≈ I_DUT
                where V_guard is driven to V_force (or V_sense) by a buffer
```

**Numbers:**

| R_leak | V across leak | I_leak |
|--------|--------------|--------|
| 1 GΩ | 100 mV | 100 pA |
| 1 GΩ | 5 V (source bias) | 5 nA |
| 10 GΩ | 100 mV | 10 pA |
| 10 GΩ | 5 V | 500 pA |
| 100 GΩ | 100 mV | 1 pA |
| 1000 GΩ | 5 V | 5 pA |

Standard FR4 after humidity/contamination: 1–10 GΩ surface. Clean + guard ring: >100 GΩ. Teflon/ceramic standoff: >10^4 GΩ.

### 4.2 PCB leakage mechanisms

1. **Surface ionic film** — flux residue + humidity → conductive electrolyte. Fix: ultrasonic clean (IPA → DI water → IPA), bake 60 °C/2 h, conformal coat or keep in dry cabinet.
2. **Solder mask absorption** — absorbs water → leakage. Fix: guard ring *on copper* surrounding high-Z node, with mask *removed* over the guard trace (keeps contaminants on guard, not signal).
3. **Via leakage** — plating cracks + moisture. Fix: no vias on the high-Z node; keep signal on one layer to the amplifier input.
4. **Capacitor DA / soakage** — dielectric absorption in X7R/X5R → long tail after overload. Fix: C0G/NP0 or film only on high-Z paths; no X7R on sense lines.
5. **Connector/package leakage** — plastic packages ~10^10–10^11 Ω pin-to-pin. Fix: guard-driven connector, or air-wire the critical node.

### 4.3 Guarding techniques

**Guard ring:** Copper trace encircling the high-Z node(s), driven by a low-impedance copy of the node voltage (usually the non-inverting input or the output of the input buffer). Intercepts leakage currents and shunts them to the guard driver instead of the signal node.

```
Top layer:   Signal pad ──[guard ring]── guard trace ──► guard buffer output
                │              │
                └─ amp input   └─ intercepts PCB surface leakage
Solder mask:  REMOVE over guard trace & ring (expose copper)
Inner layers: Flood guard plane under the high-Z node (stitching vias to guard)
Bottom layer: Guard plane continuation (optional)
```

**When to guard (V1 guidance):**

- ≥100 kΩ shunt: guard recommended.
- ≥1 MΩ shunt (100 nA range): guard *required* for repeatability <1% at low current.
- <10 kΩ shunt: guard optional; conventional layout suffices if kept clean.

**Triaxial guard:** For cable/fixture, the inner shield (guard) is driven to signal potential; outer shield is chassis ground. Extends the PCB guard ring through the cable to the DUT. Keithley 6517B uses this to hold >10^14 Ω effective insulation.

### 4.4 Practical checklist for V1 (100 nA guard implementation)

- [ ] Remove solder mask over guard ring and high-Z signal trace.
- [ ] No vias on the high-Z node between DUT terminal → shunt → amplifier input.
- [ ] Guard buffer: low-Ib op-amp (Ib < 1 pA), low Vos, unity-gain stable, driven from sense node. Verify stability with capacitive load (guard plane = ~10–50 pF).
- [ ] C0G/NP0 caps only on sense; no X7R/X5R.
- [ ] Clean board: ultrasonic IPA + DI water, no-clean flux avoided on high-Z area, bake before test.
- [ ] Shielded, light-tight enclosure for <1 µA measurements; specify warm-up time (30 min minimum, 60 min preferred) before accuracy claims.
- [ ] Measure system leakage before claiming floor: open-input + 0 V bias, measure offset current over 100 s, report mean and σ.

---

## 5. Shunt Burden-Voltage — Summary and Comparison

Full range table and derivation in `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md`. Summary here.

### 5.1 Fixed ~100 mV FS shunt (V1 baseline, provisional)

| Range | R (Ω) | Burden @ FS | Power @ FS | Johnson σ_i (10 Hz) | Johnson σ_i (1 kHz) |
|-------|-------|-------------|------------|---------------------|---------------------|
| 10 mA | 10 | 100 mV | 1.0 mW | 129 pA | 1.29 nA |
| 1 mA | 100 | 100 mV | 100 µW | 40.7 pA | 407 pA |
| 100 µA | 1 k | 100 mV | 10 µW | 12.9 pA | 129 pA |
| 10 µA | 10 k | 100 mV | 1 µW | 4.07 pA | 40.7 pA |
| 1 µA | 100 k | 100 mV | 100 nW | 1.29 pA | 12.9 pA |
| 100 nA | 1 M | 100 mV | 10 nW | 0.41 pA | 4.07 pA |
| 10 nA (V2) | 10 M | 100 mV | 1 nW | 0.13 pA | 1.29 pA |

*Assumes T=300 K, brick-wall B. Multiply by 1.25 for single-pole ENBW. TC drift: 25 ppm ·10 °C → 25 µV on 100 mV = 0.025% gain error on every range (plus self-heating negligible at ≤1 mW).*

**Pros:** Simple; consistent ADC drive (same FS voltage for all ranges → same gain chain); power negligible below 1 mA; room-temperature Johnson well below 1% FS down to 100 nA at 10 Hz.

**Cons:** 100 mV burden perturbs low-voltage DUT bias — e.g., 100 mV across a ReRAM in LRS (≈1 kΩ) at 1 mA is 10% voltage error if not Kelvin-sensed; source must compensate (force-sense loop). Settling limited by `R·C`.

### 5.2 Low-burden variant (10 mV FS)

| Range | R (Ω) | Burden @ FS | Johnson σ_i (10 Hz) |
|-------|-------|-------------|---------------------|
| 10 mA | 1 | 10 mV | 407 pA |
| 1 mA | 10 | 10 mV | 129 pA |
| 100 µA | 100 | 10 mV | 40.7 pA |
| 100 nA | 100 k | 10 mV | 1.29 pA |

*Trade-off:* 10× lower burden → 10× lower R → Johnson *current* noise is √10 ≈ 3.16× *higher* (eq. 2: `in ∝ 1/√R`). Signal-to-Johnson ratio *degrades* by 10/√10 ≈ 3.16×. Requires ~10× more post-gain (more amplifier noise) to reach same ADC FS. Chosen only when DUT voltage error from burden is intolerable and extra noise is acceptable — e.g., high-current ranges where burden perturbs compliance.

### 5.3 Transimpedance (feedback ammeter) — near-zero burden

`V_burden ≈ Vos / Aol + Ib·R_source` → typically 10–200 µV (NI PXI-4022: <20 µV on 100 nA), versus 100 mV shunt. Feedback resistor `Rf` still sets sensitivity (`Vout = –I·Rf`), so Johnson is *identical* to a shunt of the same Rf — but input capacitance charging is divided by loop gain `A`, so **settling is 10^5–10^6× faster** for high-R ranges.

| Topology | Burden @100 nA FS | Rf (=R_shunt equiv.) | Johnson σ_i (same) | Settling (C_tot=50 pF) | High-current limit |
|----------|-------------------|----------------------|--------------------|-------------------------|--------------------|
| Shunt 100 mV | 100 mV | 1 MΩ | 0.41 pA (10 Hz) | τ=50 µs, but DA tails ~ms | Limited by power (1 mW @10 mA fine) |
| Shunt 10 mV | 10 mV | 100 kΩ | 1.29 pA (10 Hz) | τ=5 µs | Same |
| **TIA** | **~20 µV** | 1 MΩ | **0.41 pA** (same) | **τ_eff ≪ 1 µs** (loop-gain divided) | Output swing / op-amp drive → ~10–20 mA max; needs power stage beyond |

**Recommendation for V1:** Shunt architecture with ~100 mV FS (good noise, manageable burden with Kelvin force/sense) is the conservative V1 baseline. TIA is superior for settling and burden but adds op-amp stability/feedback-cap compensation complexity and output-drive limits at high current. It is the natural **V2 10 nA/pA upgrade path** (often combined with capacitive-integration / coulombmeter for sub-pA, per TI SBOA597).

---

## 6. References

Sources used; listed in priority order per `ENGINEERING_RULES.md §2.1`. Datasheets take precedence where they conflict with secondary summaries.

1. **Keithley / Tektronix — *Low Level Measurements Handbook*, 7th Ed.** — Primary reference for Johnson noise (§2.6.5, §3.2.6), noise vs source impedance (§2.3.2), generated currents (§2.3.4), guarding/shielding, PLC integration (§3.3). PDF: `https://download.tek.com/document/LowLevelHandbook_7Ed.pdf`. Also mirrored as `pearl-hifi.com/.../Keithley_Low-level_Measurements.pdf` (6th Ed.).
2. **TI Application Note SBOA597 — *Measurement and Calibration Techniques for Ultra-low Current Measurement Systems*** — Feedback vs coulombmeter trade-offs, integration capacitor leakage (Ω·F product), zero-cross method, settling vs parasitic R. PDF: `https://www.ti.com/lit/an/sboa597/sboa597.pdf`.
3. **NI / National Instruments — *Minimizing Errors for Low-Current Measurements Using NI Hardware* (Knowledge Article kA03q000000x1AZCAY)** — Shunt vs feedback ammeter, voltage burden (200 µV feedback vs 200 mV–2 V shunt), settling `R·C/A`, minimum source-resistance table, NI PXI-4022 (<20 µV burden on 100 nA). Page: `https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x1AZCAY`.
4. **Analog Devices — RAQ Issue 133: *Common Sense for Current Sensing*** — Shunt vs TIA vs in-amp vs difference amplifier; TIA burden→virtual-zero discussion; shunt-burden vs gain trade-off. Page: `https://www.analog.com/en/resources/analog-dialogue/raqs/raq-issue-133.html`.
5. **Tektronix / Keithley Application Note — *Optimizing Low Current Measurements with the Model 4200-SCS*** — 0.1 fA resolution with Model 4200-PA preamp, settling-time measurement method, noise vs source R/C (Fig. 20), minimum source-resistance table, shielding/grounding/light discipline. PDF: `https://download.tek.com/document/200SCS%20Low%20Current%20Application%20Note.pdf`.
6. **Zhang et al. — *Noise Analysis and Performance Comparison of Low Current Measurement Systems* (TBioCAS 2012)** — Resistive vs capacitive feedback vs current conveyor, 750 fA rms (capacitive) vs 4 pA (resistive) at 10 kHz, correlated double sampling (CDS) thermal-noise doubling. PDF: `http://e-lab.github.io/data/papers/TBioCAS-lowcurrnoise-2012.pdf`.
7. **Wendt et al. — *Ultra-low noise current meter for measuring quickly changing currents from attoampere to nanoampere* (tm – Technisches Messen 2022)** — Capacitive TIA with active reset, σ = 2.6 fA at 50 Hz BW, 8.7 aA at 0.45 mHz, ±25 aA zero stability. DOI: `https://doi.org/10.1515/teme-2022-0049`.
8. **Nyquist (1928) — Thermal noise formula `vn = √(4kTRB)`** — Original derivation; constants per SI 2019: `k = 1.380649×10⁻²³ J/K` exact, `T = 300 K` conventional lab reference.

> **Note on provenance:** Calculation results in this document and companions were independently recomputed with Python (`k=1.38e-23`, `T=300 K`, brick-wall B) — see `docs/calculations/*.md` for scripts and step-by-step. Re-derive before promoting any shunt value to `bom/approved/`.

---

*Document status: Phase-1 research scaffold — provisional numbers pending measured verification per `ENGINEERING_RULES.md` §3. Promote ranges/values only after datasheet + measurement confirmation recorded in `DECISIONS.md`.*
