# Burden Voltage Analysis — ReRAM-SMU V1

> **Phase 1 baseline — superseded by SHUNT_RANGE_TRADEOFF §2.4 (IR-05); retained for traceability. Do not use this fixed 100 mV table as authoritative — SHUNT_RANGE_TRADEOFF §2.4 (range-dependent 25/50/100 mV) is canonical. Reversed ordering rejected.**

**Project:** ReRAM-SMU V1 — Phase 1 research  
**Date:** 2026-08-24  
**Status:** Framework only — shunt values are *not* final resistor values (Phase 2 DEC). All use 100 mV FS provisional target; compare philosophies for requirement decision.  
**Requirements:** REQ-MEAS-001/002, REQ-PWR-003, REQ-SAFE-001 (burden interacts with compliance), REQ-DUT-001 (Kelvin).

---

## 1. What burden voltage is

In shunt measurement, `V_burden = I_DUT · R_shunt`. It appears in series with the DUT and, if not Kelvin-compensated, subtracts from the programmed force voltage:

```
Ideal: V_DUT = V_force
Real:  V_DUT = V_force – V_burden – I·R_lead  (R_lead = wiring)
```

Kelvin sensing (FORCE_HI/SENSE_HI) can correct V_DUT to the sense point, but V_burden still limits headroom (output stage must supply V_force = V_DUT + V_burden) and influences settling/power.

For transimpedance (TIA) measurement, V_burden ≈ Vos/Aol + Ib·Rs ≈ 10–200 µV (NI PXI-4022: <20 µV on 100 nA) — near-zero by design, at the cost of stability complexity.

---

## 2. Candidate range table — fixed 100 mV full-scale shunt (V1 baseline, provisional)

Formula: `R_shunt = V_FS / I_FS`, `V_FS = 100 mV` (provisional). `P = I_FS²·R = I_FS·V_FS`, `TC_gain_error = TC·ΔT` (gain, not offset).

| Range (I_FS) | R_shunt (100 mV FS) | Standard E96 nearest | P @ FS | V_burden @ 10% FS | Johnson vn density | Johnson i_n density | i_n 10 Hz (brickwall) | i_n/IFS (10 Hz) |
|--------------|----------------------|----------------------|--------|-------------------|--------------------|---------------------|----------------------|-----------------|
| 10 mA | 10 Ω | 10.0 Ω | 1.0 mW | 10 mV | 0.41 nV/√Hz | 40.7 pA/√Hz | 0.13 nA | 13 ppm |
| 1 mA | 100 Ω | 100 Ω | 100 µW | 10 mV | 1.29 nV/√Hz | 12.9 pA/√Hz | 0.041 nA | 41 ppm |
| 100 µA | 1.00 kΩ | 1.00 kΩ | 10 µW | 10 mV | 4.07 nV/√Hz | 4.07 pA/√Hz | 0.013 nA | 130 ppm |
| 10 µA | 10.0 kΩ | 10.0 kΩ | 1.0 µW | 10 mV | 12.9 nV/√Hz | 1.29 pA/√Hz | 0.0041 nA | 410 ppm |
| 1 µA | 100 kΩ | 100 kΩ | 100 nW | 10 mV | 40.7 nV/√Hz | 407 fA/√Hz | 0.00129 nA (1.29 pA) | 1290 ppm |
| 100 nA | 1.00 MΩ | 1.00 MΩ | 10 nW | 10 mV | 129 nV/√Hz | 129 fA/√Hz | 0.00041 nA (0.41 pA) | 4100 ppm |
| 10 nA (V2, for comparison) | 10.0 MΩ | 10.0 MΩ | 1.0 nW | 10 mV | 407 nV/√Hz | 40.7 fA/√Hz | 0.00013 nA (0.13 pA) | 13000 ppm |

*Constants:* `k=1.380649e-23 J/K`, `T=300 K`, `vn=√(4kTRB)`, `B` per column as noted; TC example 25 ppm/°C → ΔT=±10 °C → gain error = 0.025% (250 ppm) → 25 µV on 100 mV FS for all ranges.

**Python verification (lead, .venv, brickwall B=10 Hz):**

```
10 mA R=10 vn=0.0013 µV (1 kHz: 0.0129 µV) i=0.129 nA (1 kHz: 1.29 nA)
100 nA R=1M vn=0.407 µV i=0.407 pA (1 kHz: 4.07 pA)
```

ENBW correction: single-pole ENBW=1.57·fc → multiply vn by √1.57≈1.25.

### 2.1 What this means for ReRAM DUTs

| DUT example | R_DUT | I @0.5 V read | V_burden (shunt 100 nA range, worst) | V_burden (10 mA range) |
|-------------|-------|---------------|--------------------------------------|------------------------|
| LRS low 1 kΩ | 1 kΩ | 500 µA | — not on 100 nA range (would be compliance-limited) | 5 mV @500 µA on 10 mA/10Ω → 1% error if not Kelvin-corrected |
| HRS 1 MΩ | 1 MΩ | 0.5 µA | — | — (use 1 µA range, 50 mV burden @0.5 µA → 10% error) |
| HRS 100 MΩ | 100 MΩ | 5 nA | 5 mV @5 nA on 1 MΩ → 1% of 0.5 V read (acceptable with averaging) | — out of range |

**Lesson:** V_burden is not negligible for low-R LRS on high-current ranges, and dominates read error on HRS if forced onto a high-current shunt. Autoranging to the correct decade is essential, and Kelvin sense must be at the DUT terminals, not at the shunt.

---

## 3. Design philosophies compared

### 3.1 Fixed ~100 mV FS shunt (V1 baseline, recommended)

- **How:** `R ∝ 1/I_FS` as table above; all ranges present 0–100 mV to the sense amplifier → same post-gain.
- **Pros:** Simple; consistent ADC FS; Johnson-limited floor <1% FS down to 100 nA at 10 Hz; power ≤1 mW; TC gain error uniform.
- **Cons:** 100 mV burden perturbs DUT bias — source must compensate (force-sense loop with extra headroom). Settling `τ = R·C_tot` (C_tot≈50 pF typ): 1 MΩ×50 pF=50 µs (5τ=250 µs) plus DA tail seconds — acceptable for DC sweeps but not fast pulse.

### 3.2 Fixed low burden — e.g., 10 mV FS (or 5 mV FS)

| Range | R (10 mV FS) | Johnson i_n 10 Hz | Burden @ FS | Gain needed vs 100 mV |
|-------|--------------|-------------------|-------------|----------------------|
| 10 mA | 1 Ω | 0.41 nA (3.2× worse than 100 mV) | 10 mV | 10× more gain |
| 1 mA | 10 Ω | 0.129 nA | 10 mV | 10× |
| 100 nA | 100 kΩ | 1.29 pA (3.2× worse) | 10 mV | 10× |

- **Pros:** 10× lower perturbation of DUT and compliance headroom.
- **Cons:** Johnson current noise √10 worse; needs 10× more voltage gain before ADC → amplifies amplifier `en` and ADC noise 10×; TC gain error still 0.025% but now against smaller FS → SNR degrades 3.16× (`10 / √10`). Chosen only when DUT voltage accuracy from burden is critical and extra noise is acceptable (e.g., high-current compliance where burden pushes output stage headroom).

### 3.3 Transimpedance (feedback ammeter) — near-zero burden

- **How:** `Vout = –I·Rf`, `V_burden ≈ Vos/Aol + Ib·Rs` ≈ 10–200 µV (feedback divider, not series). Rf values equal to R_shunt table for same sensitivity, so **Johnson is identical** for same Rf.
- **Pros:** Burden ~20 µV (Ni spec) vs 100 mV — negligible perturbation; settling divided by loop gain `A≈10^6` → τ_eff≪1 µs even for 1 MΩ/50 pF (vs 50 µs shunt).
- **Cons:** Stability/phase margin with Rf||Cf compensation; output swing / drive current limited (Rf·I_FS ≤ op-amp swing → 100 mV still); needs power stage for ≥10 mA; feedback capacitor selection per range.

| Topology | Burden @100 nA FS | Rf (equiv. R) | Johnson (same) | Settling (50 pF) | High-current limit |
|----------|-------------------|---------------|----------------|------------------|--------------------|
| Shunt 100 mV | 100 mV | 1 MΩ | 0.41 pA (10 Hz) | 50 µs (plus DA) | 1 mW @10 mA fine |
| Shunt 10 mV | 10 mV | 100 kΩ | 1.29 pA | 5 µs | fine |
| **TIA** | **~20 µV** | 1 MΩ | **0.41 pA** | **≪1 µs** (gain-divided) | op-amp drive ~10–20 mA max |

**V1 recommendation (provisional):** Fixed 100 mV FS shunt baseline — conservative, well-characterized, manageable burden with Kelvin force/sense can be compensated by the source loop. TIA is the natural **V2 10 nA/pA upgrade path** (often with capacitive integration/coulombmeter for sub-pA).

---

## 4. Maximum acceptable burden (requirement candidate)

**Candidate requirement (for discussion, not yet CONFIRMED):**

> For V1, maximum measurement burden at full-scale of any range shall be ≤100 mV when measured at the DUT terminals via Kelvin sensing; the source shall provide sufficient headroom to maintain `V_DUT = V_force_set` within specified source accuracy for all `|I| ≤ I_FS` up to V_burden.

*Rationale:* 100 mV is 5% of primary ±2 V region worst-case, correctable by force-sense loop; 10 mV burden alternative is 0.5% but costs 10× gain/noise. Burden above 100 mV (e.g., 1 V FS) would consume excessive headroom and self-heat (10 mA·1 V=10 mW).

*Verification:* Apply precision resistor as DUT, force V=1.0 V on each range, measure Vsense vs Vforce, confirm `Vsense = Vforce_set ± source accuracy` within 100 mV burden budget; log headroom vs supply rails.

---

## 5. Calculations — provision for Phase 2

All numbers above recomputed with `k=1.380649e-23`, `T=300 K`, `B` brickwall. Phase 2 must re-derive with actual shunt TC (e.g., Vishay 25 ppm vs 100 ppm), self-heating `ΔT=P·θJA`, amplifier `en/in` per datasheet, and ADC input noise at chosen NPLC. Script to commit: `docs/calculations/burden_voltage.py` (or embed in this markdown's python snippets).

---

*No resistor values are final BOM — this is requirement scoping only. Promotion to REQ-MEAS-001 revised table requires DECISIONS.md evidence.*

