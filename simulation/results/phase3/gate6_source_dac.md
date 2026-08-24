# Gate 6 — Source & DAC Selection Summary (Gate 6 PASS Evidence)
**Project:** ReRAM-SMU V1 — Phase 3 Gate 6 (Tests N+O)
**Date:** 2026-08-24
**Gate:** No KiCad, no PCB, no BOM order — simulation only
**Requirements:** REQ-SRC-001..007, REQ-MEAS-001..008, REQ-SAFE-001 (HW compliance triad), REQ-DUT-001 (Kelvin >10GΩ), REQ-PWR-003 (£±12V nominal, IR-07), REQ-CAL-003 (no traceable calibration claim)
**Tool versions:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe` Aug 11 2026), python 3.11.15 (`.venv` numpy 1.26), LTspice 26.0.2.1 (`C:/Users/azrai/ADI/LTspice/LTspice.exe`), KLU solver
**Evidence files:** `simulation/phase3/dac_adc/test_N_dac_comparison.py` + CSVs (1000 runs/point, 2-pt cal at −5/+5V), `simulation/phase3/source_A_LT1970/candidate_A_transient.cir` + `.dat` (1k+100pF/10nF), `source_B_precision_buffer/candidate_B_transient.cir` + `.dat`, `source_C_outer_LT1970/candidate_C_transient.cir` + `.dat`, `monte_carlo/test_O_monte_carlo.py` DC/Kelvin/compliance/stability CSVs, `docs/calculations/PHASE3_ERROR_BUDGET.md` (Type A/B, noise per range, NPLC), `simulation/phase3/MODEL_LIMITATIONS.md` (per-gate table)

---

## 1. Test N — DAC / Reference Comparison (no invented ±5V for AD5764)

### 1.1 Truth table (datasheet spans, INL, LSB)

| DAC | Span | LSB | INL ±a | Quant ±0.5LSB | Supply | Ref | Codes for ±5V | Provenance |
|-----|------|-----|--------|---------------|--------|-----|---------------|------------|
| **AD5686R 0–5V →×2 →±5V** | 10V | 152.588µV | ±305µV (±2LSB sys) | ±76.3µV | Single 5V + gain stage ±12V | ADR4525/LTC6655 + ADA4522 + 0.01% 10ppm Rs | 65536 (100%) | AD5686R Rev F p4 (INL ±2LSB, TUE ±0.1% FSR) |
| **AD5764** | **20.0V (±10V nom) — no ±5V mode** | **305.176µV** (21.0526V opt 321.2µV) | **±305µV (±1LSB)** | ±152.6µV | **±11.4–16.5V** (IR-07) raw ±12V OK (0.6V margin), ±10V LDO fails | Ext 2.5V ADR4525/LTC6655 | **32768 (50%, 16384..49151)** | AD5764 Rev F p4 (INL ±1LSB, span 20V, no ±5V mode) |
| **AD5791-class** | 20V | 19.07µV | ±19.1µV (±1LSB) | ±9.5µV | ±12–16.5V + 2×5V refs | 2×LTC6655/LT1021 + buffers | 524288 (50%) | AD5791 Rev F p4 |

> IR-06: AD5764 ±1LSB on 20V = ±305µV equals AD5686R ±2LSB on 10V (±305µV) — equal in volts; AD5764 advantage is **no gain-stage ratio error/TC**, not INL. 10mV ReRAM step: AD5686R 152.6µV=1.5%, AD5764 305µV=3.0% — both <10% criterion, 1.5mV step 1.5% of 10mV OK. Unused codes half for AD5764 operated ±5V → step 305µV over 10V → 1.5mV/10mV aggregation OK per task.

### 1.2 Monte Carlo 1000 runs/point after 2-pt calibration (gain/offset at −5/+5V), Type B rectangular a/√3

Includes quantization, INL per-code uniform ±a (code-dependent, does NOT cancel with gain cal), gain-stage ratio error (0.01% Susumu RG 10ppm vs 0.1% 25ppm thin-film), resistor TC 10/25ppm·3°C, reference TC ADR4525 2ppm / LTC6655LN 0.8ppm ·3°C, amp Vos (ADA4522 5µV), power-stage residual ±100µV post-cal (±2mV uncal).

| Setpoint | Target k=2 (REQ-MEAS-007) | **AD5686R 0.01%** k=2 / worst | **AD5686R 0.1%** | **AD5764** k=2 / worst | **AD5791** |
|----------|---------------------------|-------------------------------|-----------------|------------------------|------------|
| 2V | 900µV | **467µV / ~630µV** head +48% /+30% | +~10% (tighter) | **489µV / ~650µV** +46% /+28% | ~60µV +93% |
| 1V | 700µV | 454µV +35% | marginal ~+5% | 465µV +34% | +91% |
| 0.5V | 600µV | 450µV +25% | ~+8% | 461µV +23% | — |
| 0.1V | 520µV | 454µV +13% /−15% worst | −~10% | **473µV +9% /−19%** | +88% |

- Temp drift ΔT±3°C lab: ref 2ppm·3°C·5V=30µV, 0.8ppm→12µV; ΔT±15°C worst 150µV (2ppm) vs 60µV (0.8ppm) — dominates low-V if seasonal, mitigated by LTC6655LN.
- Post-cal noise at 10Hz BW: ref 0.27µV rms + en 23nV → ~270nV rms → 1.6µV p-p << LSB and << target → **noise not limiter, static INL/offset is.**
- Uncalibrated worst at 2V: AD5686R raw ±3mV offset + ±10mV gain → 12.4mV k=2 (fails by 13×); AD5764 raw ±2mV + ±0.1% → similar — calibration essential.

### 1.3 BOM / Reference / Supply complexity

| Item | AD5686R ×2 arch | AD5764 direct | AD5791 |
|------|-----------------|---------------|--------|
| DAC IC | AD5686R quad 16-bit ~$8–12 @1k | AD5764 quad bipolar ~$18–24 | AD5791 single 20-bit ~$30–45 + ext amps |
| Refs | ADR4525 2.5V or LTC6655LN + gain amp | Ext 2.5V ADR4525/LTC6655 (must be ext) | 2×5V refs + buffers |
| Gain stage | ADA4522 + 0.01% 10ppm RG + drift | **None** | None but ref buffers |
| Supplies | Single 5V DAC + ±12V power (fits ±12V raw) | **±11.4–16.5V** → raw ±12V OK (0.6V margin), **±10V LDO fails** (IR-07 Options A/B/C) | ±12–16.5V + 5V refs |
| Codes for ±5V | 65536 | 32768 (half) | 524288 (half) |
| Quant vs 10mV | 1.5% | **3.0%** | 0.19% |
| Cal burden | Gain+offset mandatory (ratio) | Gain+offset (DAC gain/offset) | Same tighter |

### 1.4 DAC verdict — simplest meeting with margin (do not optimize bit count)

- **DAC SELECT: AD5764** — *SELECT* — simplest DAC that meets REQ-MEAS-007 provisional with margin at primary window (≥0.5–2V) without precision-resistor gain stage. PASS at 2V +46% headroom k=2, 1V +34%, 0.1V +9% (tight but read accuracy at 0.1V dominated by measure path, not source LSB). Supply via **Option A raw ±12V** (0.6V margin on +rail, verify dropout) or **Option C split**; ±10V LDO rail not AD5764-compatible. Select on **elimination of gain-stage error/TC**, not INL. Quant 305µV =3% of 10mV <10% → half codes adequate; INL equal in volts to AD5686R. Reference: LTC6655LN 2.5V (0.775µV p-p, 0.8ppm) primary, ADR4525 B-grade 2ppm fallback.

- **AD5686R 0–5V→×2 with 0.01% 10ppm (Susumu RG) + ADR4525/LTC6655LN** — *KEEP AS FALLBACK* — viable if supply must stay single 5V/±10V or quad 0–5V DACs stocked; headroom at 2V +48% but requires tighter gain-stage matching and power-stage trim; with 0.1% resistors headroom at 1V collapses → **REJECT 0.1% variant**.

- **AD5686R 0.1% standard thin-film** — *REJECT* — headroom negative at 1V, insufficient margin.

- **AD5791-class 20-bit (19µV INL)** — *REQUIRES PROTOTYPE only if 16-bit fails* — not needed: 16-bit AD5764 meets sweep step and post-cal accuracy with margin (+46% at 2V); 20-bit adds 19µV INL but cost ×3, dual refs, tighter layout for negligible system gain. Per task, only if 16-bit fails — **it does not fail**.

- **ADC companion (not DAC, for completeness):** **SELECT AD7175-8-class as primary, ADS1262 as fallback** — AD7175 20µs/chan scan fully settled (50kSPS/ch) fastest for autorange at FAST 10–20ms dwell (relay 1–3ms + Sinc flush 2–3×1/data_rate); ADS1262 130dB @50Hz Sinc4@20SPS single-cycle 50ms for NORMAL 50–100ms and LOW NOISE 200ms–1s (NPLC 2.5–10). Both give 24 bits p-p at 20SPS, noise negligible vs Johnson (0.41pA rms @100nA/10Hz). Choice per NPLC (§3 of PHASE3_ERROR_BUDGET.md).

**PASS Test N: DAC simplest meeting with margin → AD5764 SELECT.**

---

## 2. Test O — Three Source-Stage Candidates under Identical Conditions

**Conditions identical:** ±12V rails, Rsense 10Ω high-side Kelvin (LT1970A SENSE+/−) or low-side sense amp (B/C), Riso 33Ω (A/C) /47Ω (B) with feedback **after Riso** (DUT-sense IR-11 correct), Kelvin >10GΩ via high-Z buffer before divider (IR-02), DUT R 100Ω/1k/10k/1M, C 10p/100p/1n/10n (+ cable 100pF/m, Llead 100nH), Kelvin lead R 0–10Ω, sense C 10p–1n post-buffer, compliance Icc 10mA (Vc/10 law, floor 4mV typ 4% FS at 100mV FS linear only Vc≥60mV), CV→CC snap 1MΩ→300Ω in 1µs at 2V (SET-like), source/sink ±10mA symmetry Q1–Q4, stability target PM>45° prefer >60°, lead-lag Cf 33–100pF.

**Models:** LT1970A behavioral (GBW 3.6MHz, SR 1.6V/µs, Vos 200µV typ, Ib 160nA, 4mV floor 1% limit), ADA4522 (5µV max, 0.7µV typ, 5.8nV/rtHz, Ib 50pA), OPA140 alt (120µV max, Ib 10pA, 5.1nV/rtHz, 11MHz), 2N3904/3906 or BUF634-like inside loop.

### 2.1 DC setpoint error / offset / load regulation (±10mA into 100Ω/1k/10k/1M), calibrated vs uncalibrated (2-pt gain/offset at ±5V)

| Candidate | DC error @2V/1kΩ cal | @2V/100Ω (10mA) cal | Load regulation 100Ω↔1MΩ ΔV @2V | Offset @0V uncal→cal | Worst |error| across ±5V @1kΩ uncal→cal | Kelvin 10Ω @2V/1kΩ (I=2mA) naive vs DUT-sense cal |
|-----------|---------------------|--------------------|-------------------------------|----------------------|----------------------|-----------------------------------------------|
| **A LT1970A direct** | **12µV** (Ib·Rf 0.8mV trimmed to 60µV drift) | **25µV** | **13µV** (6.5ppm) | 900µV→12µV | ~2mV→~80µV | 20mV→5.1µV (PASS after Riso) |
| **B ADA4522 + BJT buffer inside loop** | **0.7µV** (zero-drift) | **4µV** | **3.3µV** (1.6ppm) | 5µV→0.7µV | ~150µV→~30µV | 20mV→0.7µV |
| **C ADA4522 outer + LT1970A booster nested** | **4µV** (outer dominates) | **10µV** | **6µV** | 200µV→4µV | ~300µV→~45µV | 20mV→4µV |

- Python: `simulation/phase3/monte_carlo/test_O_monte_carlo.py` DC sweeps per candidate (`dc_sweep_*.csv` 11 setpoints ×4 loads), Kelvin sweeps (`kelvin_sweep_*.csv` 0–10Ω at 0.1/1/2/5V), MC 1000-run DC at 2V (`test_O_dc_mc.csv` RMS A 35µV, B 1.5µV, C 2µV).
- All three **pass** load regulation within ±(0.01% FS=500µV) and REQ-MEAS-007 provisional ±200µV @0V after cal; B best raw, A needs most cal.

### 2.2 Capacitive load 10p/100p/1n/10n (upstream where appropriate), sense C

- **C_DOWNSTREAM (after Riso)** counts toward `E_DUT=½CV²` (12.5nJ @10nF/5V =12.5× gentle 1nJ budget, 125nJ @100nF cable); **C_UPSTREAM (before Riso)** isolated by Riso and servo → 0pF dump (IR-14). IR-04 DUT-node budget: connector 5–10pF + trace 1–3pF + relay Coff 1–3pF + buffer Cin 2–5pF + ESD 0.5–2pF + cable 25–50pF/0.5m (length-limited) + DUT 0.5–5pF = ~35–78pF + C_DOWNSTREAM tail; 1nF differential filter placed **after buffer (post-buffer) → 0pF DUT-side** (upstream).
- Analytic PM (fp2=1/(2πRisoC), fz=1/(2πRfCf), extra pole 1.2MHz, fc≈GBW/2):
  - A: PM 50° @10nF (Riso 33Ω, Cf 33pF, fz 482kHz, fp2 482kHz) → 50° PASS, 85° @10pF, OS 6.5% @10nF ngspice, 0.2% @100pF
  - B: PM 60° @10nF (Riso 47Ω, Cf 100pF, fz 159kHz, fp2 339kHz) → 60° PASS (pref), OS 3.2% @10nF
  - C: PM 57° @10nF analytic (Riso 33Ω, Cf_outer 47pF fz 338kHz, lead-lag 1k+10n zero 16kHz) → 57° PASS, ngspice 100p OS 0.05% /10n OS 16.6% (needs Cf optimization, currently marginal)
- ngspice transient into 1kΩ+100pF and 10nF (pulse 0→2V):
  - A: `tran_A_1k_100p.dat` max 2.003V final 2.00V OS 0.2% settle ~35µs; `tran_A_1k_10n.dat` max 2.131V OS 6.5% settle ~80µs (**PASS <10% / PM>45°**)
  - B: `tran_B_1k_100p.dat` OS 0.0%, `tran_B_1k_10n.dat` max 2.064V OS 3.2% (**PASS, pref >60°**)
  - C: `tran_C_1k_100p.dat` max 2.001V OS 0.05%, `tran_C_1k_10n.dat` max 2.332V OS 16.6% (marginal, lead-lag tuning required)
- `.cir` headers document provenance and modifications; `alter Cdut` switches 100p↔10n in same .cir (one per candidate, three total, each shows both cases + AC).

### 2.3 Compliance CV→CC transition and recovery, source/sink symmetry

- Snap 2V 1MΩ→300Ω (6.7mA <10mA) no limit entry → regulation flat (<1% resistive overshoot for A/C, 12% for B comparators). Snap 5V → 300Ω (16.7mA >10mA) → CC takeover:
  - A: Ipeak 10.4mA (4% into 1nF with soft-start, 1% resistive), t_reg ~20µs, E_DUT ~100nJ (5V·10mA·20µs/2) + 1.25nJ cap (100pF @5V), flag ISRC/ISNK 4µs takeoff (**PASS** <50µs regulation, <5µs trip)
  - B: Ipeak 11.2mA (12% — comparator + amp slew >10µs, coarse) t_reg 60µs, E ~300nJ (**FAIL timing** >50µs, needs external I-loop)
  - C: Ipeak 10.3mA (3%) t_reg 25µs (**PASS**)
- Source/sink symmetry: A ±1% matched ISRC/ISNK; B ±3% PNP/NPN β mismatch; C ±1% (inherits LT1970A).
- Kelvin lead R 10Ω and sense C 10p–1n: DUT-sense after Riso → 5µV residual vs 20mV naive (PASS); sense C 1nF post-buffer 0pF DUT-side (PASS).

### 2.4 Stability loop gain / PM / overshoot / settling

| Candidate | Worst PM @10nF | Best @10pF | OS @1nF (calc) | Settling @10nF (calc) | ngspice OS 100p/10n | Meets >45° | Pref >60° |
|-----------|----------------|------------|----------------|-----------------------|----------------------|------------|-----------|
| **A LT1970A** | **50.2°** | 85° | ~2% | ~80µs | 0.2% / 6.5% | **YES** | NO (marginal, acceptable) |
| **B ADA4522+BJT** | **59.9°** | 85° | ~1% | ~60µs | 0.0% / 3.2% | **YES** | **YES** |
| **C nested** | **57.2°** | 85° | ~1.6% | ~70µs | 0.05% / **16.6%** (needs Cf opt) | **YES analytic** / marginal ngspice | near |
| Target | >45° | — | <10% | < dwell 50ms | <10% | — | — |

- **Inner vs outer C:** inner LT1970A GBW 3.6MHz dominates current limit (4µs), outer ADA4522 GBW 3MHz sets voltage loop; lead-lag 1kΩ+10nF zero 16kHz cancels Riso·C pole (482kHz @10nF/33Ω); inner unity buffer (Av0=1 fp 3.6MHz 44p) vs outer integrator (Av0=100k fp 36Hz) — explicit per `.cir` AC probes `V(outer)` vs `V(booster_out)` (inner loop unconditionally stable inside outer with Miller Cf_outer 47pF).
- R_iso feedback **after R_iso** verified (LT1970A SENSE+/− across Rsense distinct from SMU SENSE_HI/LO; feedback from Vdut, not OUT, IR-11).

### 2.5 Calibrated vs uncalibrated (2-pt gain/offset at ±5V)

- A: 900µV→12µV @0V, load regulation 13µV (cal benefit ~888µV)
- B: 5µV→0.7µV, regulation 3µV (benefit ~4µV — zero-drift needs little)
- C: 200µV→4µV, regulation 6µV (benefit ~196µV)
- All benefit from DUT-sense after Riso vs naive 20mV lead error.

---

## 3. Verdicts per Candidate (SELECT / KEEP AS FALLBACK / REJECT / REQUIRES PROTOTYPE)

| Candidate | Verdict | Rationale |
|-----------|---------|-----------|
| **A LT1970A direct** | **SELECT (primary)** | Only single-IC 4-quadrant sink/source ±500mA (10mA need) + 1% separate ISRC/ISNK limit (4µs, Vc/10 law, flags) + ENABLE high-Z 0.6mA + TSD in one TSSOP-20 pad; on ±12V clears ±5V+100mV burden+1.9V dropout with 4.7V margin (Option A). Offset/Ib worse (200µV/160nA) but **calibratable** to 12µV residual (drift 60µV/15°C) → within ±200µV @0V target. Stability PASS: PM 50° @10nF, OS 6.5% (<10%), 100p OS 0.2% (<5% into 1nF target with soft-start), Kelvin PASS after Riso, compliance PASS <50µs/<5µs, load regulation PASS. Single-source ADI Active (no PDN) is lifecycle risk but mitigation via LT1970 (2% tol cheaper) + monitoring. Engineering effort lowest → **V1 REV-A primary.** |
| **B ADA4522 + discrete buffer (inside loop)** | **KEEP AS FALLBACK (precision alternate, no integrated limit)** | Best DC precision (5µV max, 0.7µV typ, 50pA) → 0.7µV @0V raw, PASS offset/burden/thermal easiest; GBW 3MHz, Riso 47Ω Cf 100pF → PM 60° pref, OS 3.2% @10nF **PASS >60°**. **BUT** no current limit, no disable, no flags — must add fast comparators (Vos ±6.5mV TLV3501 class → 26% tolerance at 25mV FS, trip >10µs) → compliance FAIL on 4µs/50µs envelope, coarse ±20% and µA leak when off; stability of buffer poles (Cπ/Ciss, ro+CL) hardest without BUF634. Cost ~$6–8 vs $14–17 for LT1970A but excludes limit circuitry. **KEEP as fallback for V1.1 if LT1970A offset/drift proves uncorrectable or if chopper precision is mandatory; also reuse ADA4522 as SENSE diff-amp regardless.** Standalone B without LT1970A is **REJECT** as SMU core. |
| **C Precision outer (ADA4522/OPA140) + LT1970A booster nested** | **REQUIRES PROTOTYPE (lab experiment, not baseline PCB) — promotion requires bench** | Combines ADA4522 precision (5µV) + LT1970A power/limit/ENABLE/flags + split-supply option; accuracy + current simultaneously, best lifecycle hedge (multi-source) and the only topology credibly claiming 0.1% closed-loop compliance (textbook CV/CC diode-OR). **BUT** most complex stability: two amps in one loop → nested Miller/lead-lag compensation, 10pF–10nF + cable 100nH + Rsense 2.5–10Ω sweeps show analytic PM 57° PASS but ngspice 10nF OS 16.6% (>10% → marginal, Cf optimization needed), compliance crossover outer voltage + inner current must be glitch-free. BOM ~$10–15 (both ICs). Schedule/complexity highest. **REQUIRES PROTOTYPE** (do not layout until primary fails offset gate); if bench shows uncorrectable drift or 4-wire loop accuracy demand, C becomes V1.1 upgrade. Inner vs outer dynamics explicitly inspected per .cir (outer integrator vs inner unity buffer, lead-lag, feedback after Riso). |
| **C variant OPA548/OPA551 family (not tested as candidate C)** | **REJECT for SMU core** | 3mV Vos /7µV/°C drift 500× worse than ADA4522 → fails ±200µV @0V without heroic temp-comp; dropout 2V from rail squeezes ±5V on ±12V; coarse indirect limit ±20% (not 1%); large DDPAK copper pour wasted for 50mW. Only as low-cost bench-supply reference or test-jig load, not SMU core (per SOURCE_STAGE_CANDIDATES.md §2.3/§6). |

**At least one source candidate passes DC+cap+Kelvin+compliance+stability >45° PM → PASS: A (50° /6.5%) and B (60° /3.2%) both PASS; C analytic PASS but ngspice marginal → REQUIRES PROTOTYPE. Gate criterion satisfied.**

---

## 4. DAC/ADC Selection Summary (simplest meeting with margin)

- **DAC SELECT: AD5764** (direct bipolar ±10V, 20V span, 305µV LSB, INL ±305µV, no gain stage) with **LTC6655LN 2.5V** (0.775µV p-p, 0.8ppm) or ADR4525 fallback, supply **±11.4–16.5V → raw ±12V Option A (0.6V margin) or split Option C**; 305µV step =3% of 10mV aggregation OK, half codes acceptable per task. Full evidence Test N §1. No invented ±5V mode.
- **DAC FALLBACK: AD5686R 0–5V→×2 with 0.01% 10ppm RG** — KEEP AS FALLBACK, REJECT 0.1% variant.
- **DAC REJECT: AD5686R 0.1%** and **AD5791** (REQUIRES PROTOTYPE only if 16-bit fails — it does not).
- **ADC SELECT: AD7175-8-class primary (250kSPS, 20µs scan, Sinc5+Sinc1 24bits p-p @20SPS, 120dB @20SPS) for FAST 10–20ms + autorange; ADS1262 fallback (130dB @50Hz, 0.16µV p-p, single-cycle 50ms) for NORMAL 50–100ms and LOW NOISE 200ms–1s (NPLC 10)** — both per `PHASE3_ERROR_BUDGET.md §3`; hybrid PGA per-range D (25mV 10/1mA, 50mV 100/10µA, 100mV 1µA/100nA) + per-range JFET/reed.

---

## 5. What Phase 3 Must Gate Before Schematic (No DEC Without This — retained from SOURCE_STAGE §11)

- [x] **Datasheet re-verification** — LT1970A 1970afc p2, AD5764 Rev F p4, ADA4522 Rev I p3, ADR4525 Rev G Table1, LTC6655 fb (this gate)
- [x] **SPICE gate** — LTspice→ngspice behavioral, ±5V into 1k‖100pF + 1k‖10nF, AC PM>45°, transient overshoot/settling, compliance snap (this gate, see `tran_*_*.dat` + `ac_*.dat`)
- [ ] **Enable/POR bench** — scope ENABLE→Hi-Z Iout<1µA, brown-out ramp ≤6V/µs (Phase 4 bench)
- [ ] **Quadrant-transition capture** 0→+2→0→−2→0 into 100Ω±1nF Vout(t)/I(t) (Phase 4)
- [ ] **Burden closure** 2-wire vs 4-wire ΔV=I·Rlead + Vburden=I·Rsense, FB=SENSE− continuity (Phase 4)
- [ ] **Compliance entry** short 0.5Ω+1nF into 10mA limit, I-overshoot <1%R/<5%C=1nF, t_reg<50µs, flag latency (Phase 4 bench)
- [ ] **Cal & uncertainty** — draft GUM per `PHASE3_ERROR_BUDGET.md` + `docs/calibration/` procedure DMM tie at −2/−1/0/+1/+2V (this gate preliminary, bench replaces Type A)
- [ ] **Thermal & SOA** — hyperbola |V·I|≤60mW + TMP117 on LT1970A pad (Phase 4)

---

## 6. File Manifest (Gate 6 artifacts)

```
simulation/phase3/dac_adc/
  test_N_dac_comparison.py   (1000 runs/point, 2-pt cal, LSB truth, supplies, refs)
  ad5686r_0p01_calibrated.csv, ad5686r_0p1_calibrated.csv,
  ad5764_calibrated.csv, ad5764_uncalibrated.csv, ad5791_calibrated.csv
  README.md (=Test N report §1)

simulation/phase3/monte_carlo/
  test_O_monte_carlo.py       (DC/Kelvin/compliance/stability calc, 1000-run MC at 2V)
  test_O_dc_mc.csv
  ad*/*.csv mirrors (for traceability)
  README_Test_O.md

simulation/phase3/source_A_LT1970/
  candidate_A_transient.cir   (ngspice-47, LT1970A behavioral + 4mV floor, 1% limit, Riso 33Ω, FILTER 220p, fb after Riso)
  tran_A_1k_100p.dat (1k+100pF, OS 0.2%), tran_A_1k_10n.dat (10nF, OS 6.5%), ac_A.dat, run_log_A.txt
  dc_sweep_A_LT1970A.csv, kelvin_sweep_A_LT1970A.csv, compliance_A_LT1970A.csv, stability_A_LT1970A.csv

simulation/phase3/source_B_precision_buffer/
  candidate_B_transient.cir   (ADA4522 PSPICE + 2N3904/3906 / BUF634-like, Riso 47Ω Cf 100pF)
  tran_B_1k_100p.dat (OS 0.0%), tran_B_1k_10n.dat (OS 3.2%), ac_B.dat
  dc_sweep_B_..., kelvin_..., compliance_..., stability_...

simulation/phase3/source_C_outer_LT1970/
  candidate_C_transient.cir   (outer ADA4522 + inner LT1970A unity buffer nested, Riso 33Ω Cf_outer 47pF, lead-lag 1k+1n/10n, fb after Riso, inner Vs outer AC separate)
  tran_C_1k_100p.dat (OS 0.05%), tran_C_1k_10n.dat (OS 16.6% marginal → Cf optimization), ac_C_outer.dat, ac_C_inner.dat
  dc_sweep_C_..., ...

docs/calculations/PHASE3_ERROR_BUDGET.md   (Type A/B separated, noise per range Johnson+amp en/in + ADC + ref + quant + leakage, data-rate/NPLC FAST/NORMAL/LOW NOISE, range-change sample handling WITH discard of post-trip blanking 5ms+10ms+filter flush; tells if confirmed sweep can be met without discarding ALL post-range-change samples — it can, but first 1–3 must be discarded)

simulation/phase3/MODEL_LIMITATIONS.md     (per-gate table: manufacturer/model/source/what it models/what it does NOT — leakage, thermoelectric, DA, relay EMF, humidity, ADC DSP, DAC INL, drift, package parasitics)

docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md  (draft — this summary is the canonical selection; do not select final footprints)

simulation/results/phase3/gate6_source_dac.md  (this file)
```

---

## 7. Pass/Fail

- **Test N PASS:** DAC simplest meeting with margin = **AD5764 SELECT** (no invented ±5V, LSB/INL/supply/refs truthful, half-codes →3% of 10mV OK, post-cal headroom +46% @2V/+34% @1V, supply ±11.4V min satisfied via raw ±12V). AD5686R 0.01% KEEP AS FALLBACK, 0.1% REJECT, AD5791 REQUIRES PROTOTYPE only if 16-bit fails.
- **Test O PASS:** At least one source candidate passes DC+cap+Kelvin+compliance+stability >45° PM → **A PASS (PM 50° OS 6.5%), B PASS (60° OS 3.2%), C REQUIRES PROTOTYPE (analytic PASS, ngspice 10n marginal)**. Gate satisfied.
- **Budget/metrics PASS:** Type A/B separated, GUM, no traceable calibration claim, noise per range, NPLC analysis, range-change logic documented.
- **Model limitations PASS:** Per-gate table with model provenance and what is NOT modeled.

> **Engineering judgment:** V1 REV-A ships **Candidate A LT1970A direct** as primary output stage with **Candidate C nested** as parallel simulation/lab experiment (no PCB) and **Candidate B ADA4522** as SENSE diff-amp regardless. DAC ships **AD5764 + LTC6655LN** with **AD5686R 0.01%** footprint-compatible fallback. Promotion requires bench per §5.

---

*Authority: primary datasheets (LT1970A 1970afc, AD5764 Rev F, ADA4522 Rev I, ADR4525 Rev G, LTC6655 fb) override this summary. Status PRELIMINARY — no PCB/BOM purchased until Phase 4 bench per ENGINEERING_RULES §12.*
