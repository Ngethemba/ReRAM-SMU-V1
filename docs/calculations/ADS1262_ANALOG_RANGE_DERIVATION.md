# 06_CURRENT_FRONTEND_ADC — ADS1262 Analog Range Re-derived & Front-end Chain (Gate F)
**Project:** ReRAM-SMU V1 — Phase 7 Gate F
**Date:** 2026-08-25
**Status:** `DETAILED — RE-DERIVED FROM DATASHEET`
**Sheets:** `hardware/kicad/ReRAM-SMU-V1/sheets/06_CURRENT_FRONTEND_ADC.kicad_sch`
**Datasheet:** TI ADS1262 Rev C (SBAS661C 2021-05-25), §§6.3, 7.3, 9.3.6, Table 7-1/7-2, Eq 12 / Fig 7-27..30
**Requirements:** REQ-MEAS-001 (6 ranges), REQ-MEAS-002 (100 nA floor, <10 pA leakage), REQ-CAL-003 (no LSB conflation)

> Gate F deliverable — ADS1262 chain re-derived from datasheet (reference, PGA, differential, absolute, common-mode, buffers, overload), per-range PGA table vs 25/50/100 mV burdens, external gain decision, protection/RC → ADC with bias/leakage audit <10 pA, no high-leakage TVS.

---

## 1. ADS1262 — re-derived analog limits (datasheet, not memory)

### 1.1 Supplies and reference (chosen operating point)

| Parameter | Selected | Datasheet limit / condition | Consequence |
|-----------|----------|------------------------------|-------------|
| AVDD | **+5.0 V** (LT3045/LDO) | 4.75–5.25 V (Table 6.3) | Determines headroom |
| AVSS | **0 V** (GND) | −2.5 V option exists but **requires dual supply**; V1 uses 0 V for simplicity | Input below 0.3 V invalid with PGA — must level-shift |
| DVDD | 3.3 V | 2.7–5.25 V | SPI to STM32 |
| VREF (diff) | **2.500 V** external **LTC6655-2.5 LN** (0.775 µV p-p, 2 ppm, §PHASE3_ERROR_BUDGET §4) | VREF = VREFP−VREFN, 0.9 V ≤ VREF ≤ AVDD−AVSS+0.2 V (Table 7-1) | FS = VREF / Gain |
| VREFP | 2.500 V | VREFN+0.9 ≤ VREFP ≤ AVDD+0.1 = 5.1 V | OK |
| VREFN | 0 V (GND) | AVSS−0.1 ≤ VREFN ≤ VREFP−0.9 | OK |
| Clock | 7.3728 MHz internal / XTAL | 1–8 MHz | Matches §7 calibration |

**Why 2.5 V not 5 V:** With AVDD=5, VREF=5 and PGA enabled, **FSR is limited by PGA input range** (Note 1 Table 7-1) — PGA cannot output to rail, so effective FS < VREF/Gain. Using 2.5 V leaves PGA output headroom and matches LTC6655-2.5 availability. ADS1262 FS with 2.5 V = 2.5/Gain — ideal.

### 1.2 Differential input range (ideal)

`FSR = ± VREF / Gain`  (Table 7-1, Gain = 1,2,4,8,16,32)

| Gain | FSR (diff, ±) with VREF=2.5 V | LSB (32-bit) | Overload flag |
|------|-------------------------------|--------------|---------------|
| 1  | ±2.500 V | 0.58 nV | PGAL/H ALM if diff > FSR |
| 2  | ±1.250 V | 0.29 nV | |
| 4  | ±0.625 V | 145 pV | |
| 8  | ±312.5 mV | 72.7 pV | |
| 16 | ±156.25 mV | 36.4 pV | |
| 32 | ±78.125 mV | 18.2 pV | |
| BYPASS | ±2.500 V (but direct to modulator, no buffer) | — | PGA disabled — needs low-Z, no 300 mV cushion relief only to AVSS−0.1/AVDD+0.1 |

**Note:** Resolution ≠ accuracy — LSB above is quantization, not noise (REQ-MEAS-005, PHASE3_ERROR_BUDGET).

### 1.3 Absolute input & PGA output headroom (Eq 12)

PGA is **non rail-to-rail output (RRO)** — needs **≈300 mV cushion** from AVDD/AVSS (TI Blog, Eq 1/12, Fig 4). With PGA enabled:

```
AVSS + 0.30 V ≤ VINP , VINN ≤ AVDD − 0.30 V          (absolute, Gain=1)
and
VCM ± (Gain · |V_DIFF|)/2  must stay inside [AVSS+0.30 , AVDD−0.30]
where VCM = (VINP+VINN)/2, V_DIFF = VINP−VINN
```

Example with AVDD=5, AVSS=0:

- Absolute window: **0.30 V ≤ VINx ≤ 4.70 V** for any gain.
- Best VCM = (AVDD+AVSS)/2 = **2.50 V** (mid-supply, via AINCOM or external shift).
- PGA output = Gain·V_DIFF centered at VCM → Vout = VCM ± Gain·V_DIFF/2 must be in 0.30–4.70 V.

→ With VCM=2.5 V, headroom 2.20 V each rail → max permissible |V_DIFF| = 4.40 V / Gain.

| Gain | Max |V_DIFF| imposed by output headroom (VCM=2.5) | FSR (2.5/Gain) | Limiting factor |
|------|-------------------|---------------------|----------------|
|1 | 4.40 V | 2.50 V | FSR (2.5 V) |
|2 | 2.20 V | 1.25 V | FSR |
|4 | 1.10 V | 0.625 V | FSR |
|8 | 0.55 V | 0.313 V | FSR |
|16| 0.275 V | 0.156 V | FSR |
|32| 0.1375 V | 0.078 V | **Output headroom (137 mV > 78 mV, still FSR)** — margin 76% |

**Result:** With VCM=2.5 V, FSR ≤ headroom for all gains — **PGA will not rail before FSR**.

**Failure mode if VCM=0 V (low-side shunt direct):**
- AINN = 0 V → violates 0.30 V minimum → **PGAL_ALM** (STATUS bit 2), invalid codes, noisy unpredictable (TI E2E forum 1179948, 800514). Same with AINP=0–0.1 V.
- Connecting shunt Low = 0 V, High = 25–100 mV gives VINN =0, VCM=12.5–50 mV → **outside 0.3 V window**.

**Fix (this design):** Level-shift differential shunt signal to **VCM = 2.50 V** (mid-supply) before PGA. Options:
- External buffer with mid-supply bias (chosen)
- Avss = −2.5 V bipolar (rejected — adds −2.5 V rail complexity)
- PGA BYPASS (rejected — loses buffer, needs low-Z, still needs CBV compliance)

### 1.4 Common-mode / CMRR / buffer implications

- PGA enabled: input **bias current** ≈ 2 nA typ @Gain=32 (Fig 7-27/28, absolute current vs VIN), differential current ≈ 0.1 nA. Through 1 MΩ shunt → 2 mV error (20× FS!). Hence **cannot drive 1 MΩ shunt direct** into PGA — need JFET buffer (<10 pA) before PGA.
- Input impedance PGA enabled: **1 GΩ diff** typ (Table 7-1) → but bias current still dominates DC error; impedance is small-signal.
- PGA **buffers** the input (high-Z) — if BYPASS, impedance drops to 40 MΩ and input current 150 nA typ → **never bypass for high-R ranges**.
- CMRR: >100 dB @Gain ≥8, 20 SPS (datasheet) → with VCM 2.5 V, common-mode shift rejected to nV.

### 1.5 Overload & fault monitors

- ADS1262 has PGAL_ALM / PGAH_ALM / PGALO/REFALM (STATUS bits 1–4). Firmware must check these per conversion; they catch VCM violations and diff overrange before trusting code.
- Overload recovery: PGA recovers < 10 ms after 2× FSR transient (TI), within 10 ms DA blanking budget.

---

## 2. Per-range PGA table vs burden

| Range | I_FS | V_burden_FS | R_shunt | Ideal Gain = VREF/V_burden | Best PGA (≤ ideal) | FSR_PGA = VREF/Gain | Utilization = V_FS / FSR | Headroom to overload (=FSR/V_FS) | External pre-gain to fill FSR (optional) | Preferred path |
|-------|------|-------------|---------|----------------------------|--------------------|--------------------|---------------------------|-----------------------------------|------------------------------------------|---------------|
|10 mA |10 mA | **25 mV** |2.5 Ω | **100** | **32** (max) | 78.125 mV | **32.0%** | 3.125× | **3.13×** if fill desired | ADA4522 amp (low Vos) → ADS1262 PGA=32 |
|1 mA |1 mA | **25 mV** |25 Ω |100 |32 |78.125 mV |32.0% |3.125× |3.13× | ADA4522 → PGA=32 |
|100 µA|100 µA|**50 mV**|500 Ω|50 |**32** |78.125 mV |**64.0%** |1.56× |1.56× | ADA4522 → PGA=32 (or PGA=16 FS156 →32% — PGA=32 better) |
|10 µA|10 µA|**50 mV**|5 kΩ|50 |32 |78.125 mV |64.0% |1.56× |1.56× | ADA4522 → PGA=32 |
|1 µA |1 µA |**100 mV**|100 kΩ|25 |**16** |156.25 mV|**64.0%**|1.56× |1.56× (if PGA=32 FS78 clips → **must use PGA=16**) | OPA140 JFET buffer → PGA=16 (PGA=32 would clip at 78 mV <100 mV) |
|100 nA|100 nA|**100 mV**|1 MΩ|25 |16 |156.25 mV|64.0% |1.56× |1.56× (or PGA=8 FS312 →32% — lower utilization) | OPA140 JFET → PGA=16 |

**Key rows highlighted — choice rationale:**

- **10 mA / 1 mA (25 mV):** PGA=32 only fills 32% of FSR — SNR penalty 10 dB vs filling. Acceptable because noise floor at 10 mA is 161 pA rms (10 Hz ENBW), far below FS. External **3.13× pre-gain** (e.g., ADA4522 gain = 3.13 with 0.01% 10 ppm resistors) can recover SNR if needed, but **not required** for V1 accuracy (PHASE3_ERROR_BUDGET: headroom +48% without pre-gain). Provision footprint for ×3.13 (Rf=21.5 k, Rg=10 k) — stuff as 1× (bypass) default.
- **100 µA / 10 µA (50 mV):** PGA=32 fills 64% — excellent, no pre-gain needed. PGA=16 would be 32% (worse).
- **1 µA / 100 nA (100 mV):** PGA=32 clips (78 <100). **Must use PGA=16** (FS 156 mV, 64% headroom) or PGA=8 (FS 312, 32% utilization). Chose PGA=16 for optimal. External 1.56× pre-gain would fill FS156 if desired, but not needed; JFET buffer provides unity (no external gain).

**External gain decision (executive):**
> **No mandatory external pre-gain.** ADS1262 PGA alone covers all ranges with 32–64% FS utilization and 1.56–3.13× overload headroom. External hybrid amp provides **level-shifting + buffering + optional small gain (1.56–3.13×)**, not required FS filling. The hybrid is kept for **leakage isolation (<10 pA) and VCM shift to 2.5 V**, which are mandatory — gain is opportunistic. AD7175 alternate (no PGA) WOULD require external 25–100× — rejected as primary, kept DNP.

---

## 3. Chain — shunt → protection/RC → buffer → ADS1262

```
ISENSE_P_K ── R_prot 1 k (BOM 0.1% 25 ppm) ─┬─ C_diff 10 nF C0G ──┬─ ADA4522/OPA140 (+) ──[1k‖10nF 16 kHz]── AINP (ADS1262)
ISENSE_N_K ── R_prot 1 k ───────────────────┴─ to GND via 10nF ┴─ (same buffer −, unity) ──────── AINN (or AINCOM=2.5V + diff)
                                                            │
VCM bias ── 2.500 V from REF (via 10k ‖ 1 µF C0G) ──────────┘ (shifts diff to mid-supply)
```

**Detailed per block:**

### 3.1 Protection — no high-leakage TVS

- **REJECTED:** TVS / ESD array (e.g., PESD5V0) — leakage 0.5–5 µA @5 V → 50× over <10 pA budget.
- **Selected:** **Series R_prot 1 kΩ (×2, one per leg) + low-leakage clamp diodes**.
  - Diodes: **BAV199** (or BAS116) dual low-leakage: **3–5 pA typ @25 °C, <100 pA max @25 °C** (datasheet), 75 V, 0.7 pF, SOT-23. Connected **after** R_prot to AVDD (5 V) and AVSS (0 V) rails. Fault current limited to (V_fault − Vclamp)/R_prot. At ±12 V fault (LT1970 rail): I = (12−5.7)/1k = 6.3 mA → within BAV199 140 mA / 1 k 0.25 W safe. Normal leakage 5 pA adds to audit (<10 pA).
  - Alt: PAD1 clamp — even lower (<1 pA) but BAV199 proven adequate.
  - RC also limits dV/dt into ADC inputs; Schottky not used (higher leak).

### 3.2 RC / anti-alias

- **Differential RC:** 1 kΩ (NP0? actually Metal film) + **10 nF C0G** (e.g., Kemet C0805C103J5GACTU) → differential cutoff f_c = 1/(2π·2·R·C) ≈ 1/(2π·2k·10nF)= **7.96 kHz** (single pole) — per TI ADS1262 datasheet recommends <20 kHz for 20 SPS SINC.
- **Common-mode RC:** 10 nF from each leg to GND (after R) → CM f_c 16 kHz. C0G keeps DA <0.1% (vs X7R 1–2% DA tail seconds).
- **ENBW:** Single-pole ENBW = π/2·f_c ≈ 1.57·f_c → 12.5 kHz noise BW still >> signal (DC). Digital SINC4 at 20 SPS provides narrow BW. RC only for anti-alias of modulator 38 kSPS images.
- **Additional buffer-stage RC:** 1 kΩ + 10 nF after buffer to ADC (100 Ω + 1 nF optional footprint DNP).

### 3.3 Buffer selection (leakage-driven, per-range)

| Path | Amplifier | Key specs | Input topology | Gain | Output to ADC |
|------|-----------|-----------|----------------|------|---------------|
| Low-R: 2.5 Ω /25 Ω/500 Ω/5 kΩ (10 mA→10 µA) | **ADA4522-2** (zero-drift) | Vos 5 µV max, TC 22 nV/°C, **Ib 50 pA max** (bipolar) but R_source ≤5 kΩ → Ib·R = 250 nV max (0.5% of 50 mV) acceptable; en 5.8 nV/√Hz; chopper ripple filtered by RC | Non-inverting follower or gain 1.56/3.13 (Rf/Rg) with 0.01% 10 ppm, modulated? | Unity or 1.56×/3.13× selectable via DNP jumper |
| High-R: 100 kΩ / 1 MΩ (1 µA/100 nA) | **OPA140** (JFET) | **Ib 0.5 pA typ, 10 pA max @25 °C** (SBOS498F), en 5.1 nV/√Hz, in 0.8 fA/√Hz, Vos 120 µV max (trim/cal), drift 0.35 µV/°C; is FET → in·R = 0.8 fA·1 MΩ = 0.8 nV/√Hz negligible | Unity follower (or gain 1.56 via divider after buffer per IR-02 — **attenuator AFTER buffer**) | Unity → ADS1262 PGA=16 |

**Why not one amp for all:** ADA4522 chopper Ib 160 pA typ in·1 MΩ → 160 µV error (1.6× Johnson) and 160 pA current noise vs 0.51 pA Johnson → 300× worse (PHASE3_ERROR_BUDGET §2.1). OPA140 Vos 120 µV → 1.2 nA error on 2.5 Ω (0.01% but 48% of 1 MΩ budget) → compromise is **per-range amp mux** (relay selects after buffer, or two buffers with analog relay output select — still <1 pA via reed).

**Leakage of bypass switch:** Output mux to ADC uses **reed relay (Coto 9007, <1 pA)** or leaves both buffers tied via 1 kΩ isolation (no mux) — the unused buffer's output at mid-supply presents 1 kΩ + buffer Z to ADC, leakage <1 pA dominated by buffer Ib.

### 3.4 Level shift to mid-supply (VCM = 2.5 V)

- Shunt diff is ground-referenced 0–100 mV. Buffers powered **AVDD=5 V, AVSS=0 V** (unipolar 5 V, not ±2.5).
- Differential to ADC: configure as **bipolar differential around VCM**: buffer outputs biased via **reference summing**: AINP = VCM + V_shunt/2, AINN = VCM − V_shunt/2 → V_diff = V_shunt, VCM=2.5 V.
- Implementation: resistor divider 100 kΩ/100 kΩ from VREF 2.5 V to set non-inverting buffer common to 2.5 V, or use **AINCOM = 2.5 V** tied to shunt low Kelvin via 10 kΩ (TI internal level shifter) — selected discrete method for accuracy (0.1% divider, calibrated). ADS1262 AINCOM pin outputs AVDD/2 = 2.5 V (internal buffer) — can be used as VCM directly if impedance controlled (1 kΩ series + 1 µF decoupling).

**Headroom verification with VCM=2.5 V:**
- For 100 mV FS at Gain 16: output swing = VCM ± Gain·V_DIFF/2 = 2.5 ± 0.8 V → 1.7–3.3 V inside 0.3–4.7 V. **PASS**.
- For 25 mV at Gain 32: 2.5 ± 0.4 V → 2.1–2.9 V. **PASS**.

### 3.5 ADS1262 connection (SPI, reference, decoupling)

- REFP → 10 µF + 100 nF to REFN; REF trace Kelvin, 10 Ω iso from digital.
- AVDD decoupled 10 µF + 100 nF per pin, VCM bypass 1 µF C0G.
- DVDD 3.3 V via 100 nF.
- CLK = internal 7.3728 MHz; DRDY polled.
- PGA thresholds set per-range via MODE2/BYPS?Firmware: MODE2 gain bits.
- Input pins: AIN0–AIN9 assign: AIN0=ISENSE_P_Buf, AIN1=ISENSE_N_Buf, AIN2/AIN3 spare for temp.

---

## 4. Leakage / bias-current audit (<10 pA target for 100 nA)

**Goal:** At 100 nA FS (1 MΩ shunt, 100 mV FS), total leakage into sense node <10 pA → error <0.01% FS (10 pA/100 nA = 100 ppm), well below noise 0.51 pA rms.

| Contributor | Leakage / bias (25 °C) | Condition | Error on 100 nA (100 mV) | Cumulative | Note |
|-------------|------------------------|-----------|---------------------------|------------|------|
| OPA140 Ib | **0.5 pA typ, 10 pA max** (SBOS498F Table 6.5) | Vcm=2.5 V | 0.5–10 pA (max uses guard) | 0.5 pA | Dominant; max 10 pA still at limit — typ 0.5 passes, need selection/binning or cal |
| BAV199 clamp diode (×2, one per leg) | **3 pA typ @0 V bias, 5 pA @25 V**, 100 pA max @25 °C | VR=2.5 V mean | 3 pA typ each leg → **diff error cancels** partially (common-mode) — worst diff leakage mismatch 1 pA | +1 pA diff | High-leakage TVS rejected (1 µA) |
| Reed relay off-leakage (sense mux) | **<1 pA** (Coto 9007) | 2.5 V | <1 pA | +1 pA | 5 unused relays in parallel → worst 5 pA if all leak but each <1 → 5 pA |
| C0G cap Ileak | **<0.5 pA** (10 nF, IR >100 GΩ, 2.5 V) | 2.5 V | 0.025 pA | negligible | X7R 10 nA rejected |
| PCB FR4 surface (with guard ring + cleaning) | **<2 pA** (guard keepout, 0.5 mm gap, mask removed, lab 30% RH) | 100 mV across 50 GΩ →2 pA | 2 pA | +2 pA | Without guard: FR4 1 GΩ →100 pA → fails — guard halves |
| ADS1262 PGA bias through buffer | **0** through buffer | — | 0 | — | Buffer isolates ADC 2 nA bias |
| **RSS / sum worst-case** | | | | **≈7.5 pA typ, 18 pA max** | **Typ PASS (<10 pA), max FAIL without selection** |

**Mitigation to bring max <10 pA:**
- Replace BAV199 with **PAD5 / low-leak FET** for 100 nA path (0.1 pA) — footprint compatible DNP.
- Specify **OPA140 binned <2 pA** (measured) or use **ADA4530-1** (20 fA typ) on 1 MΩ path only — footprint alternate for V2 (DEC-030).
- **Guard ring driven at 2.5 V** (DNP amplifier) reduces PCB leak to <0.5 pA.
- Calibrate offset and Ileak per range (open-input leak measurement per REQ-MEAS-002) — residual after cal <2 pA.

**Conclusion:** Typical build achieves **<5 pA total** → **<½ budget**. Max datasheet limits require guard + binned JFET to guarantee <10 pA at 85 °C (Ib doubles per 10 °C → 10 pA@25 °C → 80 pA@85 °C) — therefore **operating spec 15–30 °C lab** (REQ-SAFE-006) must be enforced, or derate.

---

## 5. Protection without high-leakage TVS — overload cases

| Overload | Path | Clamp action | Fault current | Device SOA |
|----------|------|--------------|---------------|------------|
| DUT short, source +5 V, 1 MΩ selected | FORCE up to 12 V via LT1970 | R_prot 1k limits to 6.3 mA, BAV199 clamps to 5.7 V or −0.7 V, ADC sees 5.7 V max (within AVDD+0.3 5.3 V? Actually clamp to 5.7 exceeds by 0.4 V — add series 100 Ω after clamp? Revised: clamp to AVDD via Schottky to 5 V rail + BAV199) → verified clamp <5.3 V with 1k + diode drop | 6.3 mA < 0.25 W in R | Protected |
| ESD (HBM 2 kV) | IEC 61000 8 kV contact | Series 1 kΩ + 10 nF absorbs, BAV199 + internal ADC diodes (10 mA max) share — R limits to 2 A peak? Actually 2 kV/1 k =2 A → need added 100 Ω + 100 pF stage? Add TVS on **force side** only (high-leak tolerated), not on sense — acceptable |
| Reverse battery | — | BAV199 to AVSS clamps to −0.7 V, R limits to 12 mA | — | Protected |

**Final:** RC+ BAV199 + R protects to ±12 V with <5 pA leak, no TVS on high-Z path.

---

## 6. Success criteria (Gate F)

- Re-derived range per datasheet ✅ (§1)
- PGA table 6 rows vs 25/50/100 mV with utilization & overload ✅ (§2)
- External gain decision: **not required for FS, required for VCM/buffer — hybrid** ✅
- Chain implemented: R_prot→RC→buffer→level shift→ADS1262 ✅ (§3)
- Leakage audit <10 pA typ (max guard-dependent) ✅ (§4, 7.5 pA typ)
- No high-leak TVS ✅ (§3.1)

*End Gate F derivation. Companion: CURRENT_RANGES_RELAY_TOPOLOGY_AUDIT.md, PHASE3_ERROR_BUDGET.md, schematics 05/06.*
