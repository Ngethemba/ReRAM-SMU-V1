# Phase 1 Research Summary — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 1 Requirements Verification  
**Date:** 2026-08-24  
**Status:** `DRAFT / RESEARCH SYNTHESIS` — informs REQUIREMENTS.md v0.2.0; no schematic, no BOM. All hardware candidates remain `PROVISIONAL / REQUIRES VERIFICATION` per DECISIONS.md.

---

## 1. Objective

Answer: *What source, measurement, protection, accuracy, noise, speed, and interface capabilities are actually required for a practical V1 SMU intended for low-voltage ReRAM / memristive-device characterization?* Start from measurement problem, not previous architecture sketch.

---

## 2. Subagent decomposition and agreement

Four independent research agents were run in parallel (deleg_38b38ee3, 2026-08-24 17:33). Their outputs are in `docs/research/` and `docs/calculations/`:

| Agent | File(s) | Focus | Key conclusion |
|-------|---------|-------|----------------|
| A — ReRAM characterization | `RERAM_MEASUREMENT_REQUIREMENTS.md` (31 KB) | Bipolar RS, Vset/Vreset, Icc, HRS/LRS, sweeps | ±5 V outer / ±2 V primary, 10 µA–1 mA Icc, 10 mV/50–100 ms sweep, 4-quadrant mandatory |
| B — Precision / metrology | `LOW_CURRENT_MEASUREMENT.md` (29 KB) + `NOISE_BUDGET_FRAMEWORK.md` + `BURDEN_VOLTAGE_ANALYSIS.md` (lead+ B) | Noise, burden, guard | 100 nA floor leakage-limited, 100 mV FS shunt baseline, Johnson 0.41 pA @100 nA/10 Hz, TIA is V2 |
| C — Architecture + compliance | `SMU_ARCHITECTURE_SURVEY.md` (26 KB) + `COMPLIANCE_RESEARCH.md` (21 KB) + `UNCERTAINTY_BUDGET_FRAMEWORK.md` | Arch classes, compliance triad | Hybrid multi-range (Arch D) is Phase 2 candidate; compliance = regulation (flat CC) vs trip (crowbar) distinct |
| D — Commercial benchmark | `COMMERCIAL_SMU_BENCHMARK.md` (30 KB, 11 KB scaffold overwritten) | Keithley 2450/2400/2600B, Keysight B2900, NI PXIe-4139, Yokogawa GS610/820 | Minimum useful subset for ReRAM: ±5 V, ±10 mA, 100 nA–10 mA, 4-quad, Kelvin, HW compliance — explicitly defer guard/triax/fA |

**Cross-agent agreement:** All agree on voltage ±5 V / ±2 V primary, current 100 nA–10 mA 6 ranges, hardware compliance mandatory, 4-quadrant required, Kelvin required, guard/triax deferred. No disagreement on outer envelope; minor variance on compliance speed target (A: <500 ns ideal but <500 ns unrealistic on FR-4; C: <10–30 µs regulation, <5 µs trip — synthesized below as <50 µs regulation + <5 µs trip) — reconciled as aspirational <500 ns, realistic V1 <50 µs.

---

## 3. DUT use case — envelope (from Agent A, verified)

**Priority workflows:** UC-1 hysteretic I–V (0→+Vmax→0→–Vmax→0), UC-2 SET/RESET statistics, UC-3 read at 0.1–0.5 V (ON/OFF ratio 10–10³), UC-4 multilevel via Icc (10 µA/100 µA/1 mA) or Vstop, UC-5 short retention. UC-6 limited endurance, UC-7 bounded forming, UC-8 current-sweep is V2.

| Parameter | Well-supported | V1 envelope |
|-----------|----------------|-------------|
| Vset / Vreset | +0.6–+1.5 V / –0.7––1.5 V; forming +2–+5 V | **±2 V primary** (>80% of Vset/Reset), **±5 V capability** (forming headroom) — CONFIRMED |
| Read voltage | 0.1, 0.2, 0.5, 1.0 V (<Vset/3) | 0.05–1.0 V programmable — CONFIRMED |
| Icc (SET/forming) | 10 µA, 100 µA, 300 µA, 1 mA (10 µA→1 mA multilevel) | **10 µA / 100 µA / 1 mA mandatory** + 10 mA max — CONFIRMED as discrete |
| LRS / HRS | LRS 1 kΩ–10 MΩ (1 µA–2 mA @0.1–0.5 V); HRS 100 kΩ–100 MΩ (nA–µA); ratio 10–10³ (up to 10⁴ with optimized limiter) | 100 nA–10 mA covers single-device 5 decades — REVISED to 6 ranges |
| Step / dwell | 0.01–0.05 V dominate; 50 ms/100 ms/2 s; rr 0.1–2 V/s | **1–50 mV prog, 10 ms–2 s dwell, 0.05–2 V/s** — CONFIRMED |
| Points / polarity | 80–400 pts per ±2 V; bipolar | **≥200 pts/loop** (401 pts @10 mV for –2→+2 V), fully bipolar, sink required — CONFIRMED |

Current measurement range synthesis: platform demo 20 nA–2 mA (5 decades) and GCMO 10⁷–10⁸ Ω HRS at 0.1 V → 1–10 nA. **V1 floor “several nA” is consistent; pA is V2 with guard/triax (REQ-MEAS-006 FUTURE).**

---

## 4. Voltage range — verified (Task 3)

- **Source capability:** **–5 V to +5 V continuous, four-quadrant, source/sink** — REQ-SRC-001 remains **PROVISIONAL but verified as reasonable** (covers forming +2.4–5 V, not merely spec appeal; higher voltage explicitly deferred per safety REQ-PWR-001 no mains).
- **Primary accuracy region:** **–2 V to +2 V** — well-supported as lowest-noise linear zone (80%+ of SET/RESET). REQ-SRC-002 stays PROVISIONAL but strongly supported.
- **Resolution:** ≤1 mV step programmability (10 mV staircase) — firmware constraint, not yet a REQ.
- **±10 V would not materially improve V1 utility** for low-voltage stacks; it would increase complexity, SOA, and safety scope. Deferred to V1.x/V2 only if a specific material stack (thick polymer >4 V switching) is targeted — not in current V1 scope.

---

## 5. Current range — verified (Task 4)

| Range | V1? | Benefit / burden |
|-------|-----|------------------|
| 10 mA | **CONFIRMED** | Covers Al2O3 1–15 mA forming study, RESET 0.2–3 mA, compliance 10 mA max per REQ-SRC-006; R=10 Ω (100 mV FS), 1 mW; thermal/compliance headroom. |
| 1 mA | **CONFIRMED** | Standard SET 1 mA; R=100 Ω, 100 µW |
| 100 µA | **CONFIRMED** | Most common Icc; R=1 kΩ |
| 10 µA | **CONFIRMED** | Gentle multilevel 10 µA; R=10 kΩ |
| 1 µA | **CONFIRMED** | Read & HRS; R=100 kΩ, Johnson 1.29 pA @10 Hz |
| **100 nA** | **CONFIRMED floor** | HRS leakage (Mn3O4 OFF 4 nA, HRS 10 nA–0.4 µA); R=1 MΩ, Johnson 0.41 pA @10 Hz, **leakage-limited not Johnson-limited**; guard recommended, required at <1% accuracy. |
| 10 nA | **FUTURE V2** | Needs 10 MΩ, electrometer techniques (guard-driven triax, Teflon standoff, ADA4530-1, enclosure) — not reliable on FR-4; explicitly deferred (REQ-MEAS-006). |

**100 mA:** Not justified for V1 — adds power/thermal/relay burden with no ReRAM evidence inside ±5 V. **Rejected for V1, future if material demands.**

Six ranges 10 mA→100 nA remain; no change from provisional REQ-MEAS-001, now with quantitative justification.

---

## 6. Low-current target — quantified (Task 5, replaces “several nA”)

Per `LOW_CURRENT_MEASUREMENT.md` §1 and `NOISE_BUDGET_FRAMEWORK.md`:

- **Resolution target (100 nA range, 100 mV FS = 1 MΩ shunt):** 24-bit ADC → LSB = 5.96 nV ≡ 5.96 fA (display). Noise-free bits ~18–20 at 10 SPS → effective resolution ~0.4 pA at 10 Hz BW. **Resolution is not the floor.**
- **RMS noise floor (100 nA range, 10 Hz brickwall, shorted input):** Johnson 0.41 pA + amp+ADC system → **total ~0.5–2 pA rms** (type A, T=300 K). Peak-to-peak (~6.6σ) ≈ 3–13 pA. At 1 kHz BW: Johnson alone 4.07 pA rms → system ~5–10 pA rms (table in §2.1).
- **Minimum useful measurable current (MUC):** detection 3σ ≈ 1.5–6 pA; quantitative 10σ ≈ 5–20 pA. With leakage/offset, **practical MUC ≈ 1 nA** quantitative (±10% useful) on 100 nA range with averaging/shielding — consistent with “several nA” meaning **useful above ~3 nA, not LSB.**
- **Accuracy target at 10 nA (100 nA range, example):** ±(0.06% reading + 30 pA offset) expanded k=2 → ±~30–40 pA @10 nA (dominated by shunt tolerance 0.1%/√3 + Ileak 5 pA/√3 + Johnson 0.41 pA). At 1 µA mid-range, offset fraction falls; at 10 mA, tolerance dominates.

**Reporting rule (REQ-MEAS-005 binding):** Firmware/docs report `resolution (LSB)`, `RMS noise (σ, BW)`, `MUC (k·σ)`, and `accuracy (±% + offset)` separately.

---

## 7. Accuracy targets — realistic V1 (Task 6, provisional numbers for Phase 2 refinement)

*These are research targets — final numbers require part selection + measurement before DEC promotion.*

| Quantity | @ points | Target (post-cal, 25±3 °C, k=2 expanded unless noted) | Verification |
|----------|----------|----------------------------------------------------------|--------------|
| Source V accuracy | –2, –1, 0, +1, +2 V | ±(0.02% reading + 0.01% FS + 2 ppm/°C·ΔT) ≈ ±0.5 mV @1 V, ±2 mV @2 V (plus drift) | vs calibrated 6½-digit DMM (e.g., 34465A) |
| Measure V accuracy | same | ±(0.02% reading + 100 µV + TC) | comparison vs DMM at FORCE/SENSE |
| Measure I accuracy | 10 mA | ±(0.03% + 10 µA) | precision resistor V/I |
| | 1 mA | ±(0.03% + 1 µA) | |
| | 100 µA | ±(0.05% + 200 nA) | |
| | 10 µA | ±(0.08% + 20 nA) | |
| | 1 µA | ±(0.1% + 5 nA) | leakage-corrected |
| | 100 nA @50 nA | ±(0.3% + 60 pA) (U=k2) — ~±30 pA 1σ → ±60 pA k2 | shorted-input σ + shunt tolerance RSS |
| | 10 nA (V2) | not specified for V1 — FUTURE | electrometer fixture |

*Calibration targets:* initial cal residual <½ accuracy spec; short-term repeatability (σ, N=10 at NPLC=1) <⅓ accuracy offset; drift < accuracy/2 over 30 days or ΔT=±10 °C.

*Assumption flagged:* Keithley-class specs (0.012% voltage) use 1-year, Tcal±1 °C conditions with triax guard and NPLC 5 — V1 educational/research targets are 2–5× looser intentionally.

---

## 8. Compliance — quantified (Tasks 10 + Agent C)

Triad (COMPLIANCE_RESEARCH.md Table 1): compliance regulation (flat CC, SMU stays in circuit), range compliance (range ceiling), SOA trip (crowbar — SMU out).

**V1 envelope (REQ-SAFE-001 HW + REQ-SAFE-002 SW):**

| Icc setpoint | Use | Resolution | Accuracy (research) | Polarity |
|--------------|-----|------------|---------------------|----------|
| **10 µA** | gentle forming | 10 nA | ±(1% + 50 nA) | SET polarity only, HW loop |
| **100 µA** | standard SET | 100 nA | ±(0.5% + 200 nA) | |
| **1 mA** | stable LRS | 1 µA | ±(0.3% + 1 µA) | RESET bypassed |
| **10 mA** | margin/LRS | 10 µA | ±(0.3% + 10 µA) | SOA 50–60 mW continuous |

*Adjustability:* continuous within range, not decade-locked; min programmable compliance = 0.1% of I_range (Keithley rule — e.g., 10 nA Icc needs 10 µA range, not 100 mA). Intermediates (20 µA, 50 µA, 200 µA, 500 µA, 5 mA) useful for multilevel without range click.

*Dynamics (research targets, to verify by scope, not datasheet):*
- **Regulation:** settle <50 µs to Icc for 50% load step into resistive load (<1% overshoot). Aspirational <500 ns is unrealistic on FR-4; commercial SMUs quote 70–230 µs (2450 voltage settling, 2600B current settling 80 µs–25 ms by range).
- **Fast trip / SOA crowbar:** <5 µs from threshold to foldback/disable — independent supervisor path, survives MCU halt (watchdog → disable).
- **SOA hyperbola:** `|V·I| ≤ 50–60 mW` DC continuous; pulse forming only if needed.

**Firm distinction:** Firmware limit alone is too slow (ADS1262 @1 kSPS → ms) vs filament collapse ns–µs — hardware loop is mandatory; software is secondary envelope + pre-check gate.

---

## 9. Four-quadrant — resolved (Task 11)

**True four-quadrant operation is CONFIRMED mandatory for V1** (REQ-SRC-003/004, REQ-SRC-005 promoted from provisional-preferred to confirmed — see DEC-007). Required quadrants: Q1 +V/+I (source), Q2 +V/–I (sink), Q3 –V/–I, Q4 –V/+I — bipolar switching + NDR + hot-swap inrush all exercise sink. Power is modest (≈50 mW max at ±5 V·±10 mA) but quadrant-switching glitch and sink accuracy (4–8× offset penalty on commercial SMUs) must be characterized separately.

Source/sink voltage-only mode is insufficient — DUT can push current back (e.g., low-R LRS at +2 V drives –I through SMU if compliance limits).

---

## 10. Source/measure modes & sweeps (Tasks 12–13)

**Required V1:**
- Source V / Measure I (primary)
- Source V / Measure V (FORCE and SENSE)
- Resistance derived = V_sense / I_measure
- Bipolar staircase sweep `0→+Vmax→0→–Vmax→0` as built-in preset

**Nice-to-have V1 (if low cost):** Source I / Measure V (for diagnostic I-sweep)

**Future:** Source I / Measure I (redundant), true pulse Arbitrary/AWG, log sweep (V1 linear suffices).

**Sweep requirements:**
- Step 1–50 mV prog (default 10 mV), dwell 10 ms–2 s prog (default 50–100 ms), interstep 10 ms, autorange hysteresis + dwell (≥2 samples post-trip), compliance-hit handling (flag + hold range, continue), abort on interlock/overtemp/watchdog.
- Points: ≥200/loop (401 for –2→+2 V @10 mV); max configurable ≥1000 (host-driven).
- Forward/reverse symmetric; zero crossing with no relay click (four-quadrant).

---

## 11. Speed, Kelvin, guard, calibration, temperature, safety — resolutions

- **Speed (Task 14):** DC characterization only — measurements/s ≈ 1/(NPLC·20 ms). Default NPLC 1 (20 ms @50 Hz → ~50 rdg/s) to 10 PLC (200 ms) for low-noise. Relay 5–10 ms + autorange dwell 2× + USB <10 ms. Pulse characterization explicitly FUTURE (REQ-MEAS-006 family) — do not optimize for MHz.
- **Kelvin (Task 15):** 4-wire **CONFIRMED required** (REQ-DUT-001) — FORCE_HI/SENSE_HI/SENSE_LO/FORCE_LO, sense >10 GΩ, 5 V force–sense drop, 1 MΩ lead tolerance, open-sense detection. Useful for ReRAM LRS (<10 kΩ) and mandatory for calibration (<0.1 Ω lead correction). Connector not designed yet.
- **Guard/triax (Task 16):** **DEFERRED to V2/V3** (REQ-DUT-003 FUTURE) — correct to defer. V1 should provision guard-ring copper (exposed, no mask, stitched inner guard plane) and C0G-only on high-Z paths, clean+bake, shielded enclosure for <1 µA, but not claim 10⁻¹⁴ Ω guard/triax. Electrometer front-end and driven guard are V2.
- **Calibration (Task 17):** Feasible V1 concept — adjustment vs verification vs calibration vs traceable calibration (GUM terminology). References: calibrated 6½-digit DMM, class 0.01% precision resistors (1 kΩ–1 MΩ), 2.5 V precision voltage reference (cert). Per-range zero/offset (shorted input), gain (shunt ratio), source V zero/gain, temperature logged not compensated. Traceable calibration later via accredited lab.
- **Temperature (Task 18):** Assumed operating 15–30 °C lab; internal sensors **required** on output stage, shunts, reference (NTC or digital like TMP117, 1 per zone — Q-18 still needs count DEC but principle confirmed). Logging is sufficient for V1; closed-loop compensation is V1.x/V2.
- **Safety (Task 19):** Low-voltage V1 remains ≤±12 V rails, no mains (REQ-PWR-001). Confirmed: output-off startup, watchdog→disable, independent HW compliance, overtemp (standby), overcurrent trip (≤5 µs), reverse-energy dissipation, external supply fault detection, DUT ESD checklist, dummy-load gate (REQ-CAL-002) before ReRAM. E-18, R-12.

---

## 12. Architecture classes — survey (Task 20), no selection

| Arch | Summary | Source | Low-current | Compliance | Complexity / PCB | V1 verdict |
|------|---------|--------|-------------|------------|------------------|------------|
| A DAC+bipolar power amp+shunt | Precision DAC → conditioning → LT1970-class stage, shunt-switched ranges | Good, needs headroom/thermal study | Shunt-limited, guard helps | Comparator-driven limit (trip) | Moderate / FR-4 fine | Simple, but compliance is trip-dominant |
| B Force/sense feedback w/ dedicated current control | Dual loop (CV + CC diode-OR into power stage), Kelvin sense | Excellent (loop-corrected) | Same as A (still shunt) | True regulation (flat CC) | Higher / compensation-critical | Best ReRAM compliance — most textbook-correct |
| C Transimpedance low-current + source amp | TIA for nA–µA, shunt for mA | Similar | Superior settling & near-zero burden (20 µV vs 100 mV), identical Johnson at same Rf | Similar | Moderate-high / stability with Rf||Cf | Best V2 pA path,adds drive limits at high I |
| D Hybrid multi-range | Shunt (10 mA–10 µA) + TIA (1 µA–100 nA guard) + range logic | Best overall | Best (choose per decade) | Regulation + trip combined | Highest / PCB guard + switching discipline | **Natural V1 target for Phase 2** — combines A/B core with C for low end |

**D is the Phase 2 candidate to detail, but no final value selection in Phase 1** (per gateway). If only one fits, fast trip is the safety must-have.

---

## 13. Uncertainty & noise frameworks (Tasks 7–8)

- **Uncertainty:** `docs/calculations/UNCERTAINTY_BUDGET_FRAMEWORK.md` (351 lines, GUM JCGM 100) — categories S1–S10 (DAC/ref), M1–M10 (shunt/amp/ADC/leakage), V1–V4 (sense), C1–C7 (cal/temp/soakage); RSS `u_c=√(Σu_i²)` with `U=k·u_c, k=2`; rectangular `a/√3` conversion; Monte Carlo Supplement 1 teaser. **Framework only — no final numbers.**
- **Noise:** `NOISE_BUDGET_FRAMEWORK.md` + `LOW_CURRENT_MEASUREMENT.md` §2 — Johnson `vn=√(4kTRB)` table above, amplifier en/in, ADC quant/INL/ENOB, reference PSRR, digital coupling, relay charge/leakage/EMF/DA, BW/integration (ENBW, NPLC), environmental (mains, tribo, humidity, light). **Increasing R_shunt improves RTI current noise (`i_n ∝ 1/√R`) but worsens burden/settling** — trade flagged.
- **Burden:** `BURDEN_VOLTAGE_ANALYSIS.md` — fixed 100 mV FS baseline recommended (5% of ±2 V, Kelvin-correctable) vs 10 mV low-burden (3.16× noisier for same FS). TIA burden ~20 µV with same Johnson as shunt but 10⁶× faster settling via loop gain. **Requirement candidate:** burden ≤100 mV @FS with Kelvin headroom.

---

## 14. Traceability & verification (Tasks 24–25)

`docs/architecture/REQUIREMENTS_TRACEABILITY.md` (created) maps each REQ → Evidence (agent reports + calculations) → Rationale → Verification method (calculation, SPICE, DMM/resistor/scope/thermal/long-duration). Every CONFIRMED hardware REQ carries a planned verification (DMM sweep, resistor substitution, scope compliance overshoot, Kelvin delta, thermal drift, buffer dump).

---

## 15. Risks & open questions update

RISKS.md: R-01 leakage — now quantified (1 GΩ→100 pA @100 mV, 5 nA @5 V) + guard-ring checklist; R-03 compliance — now with <50 µs / <5 µs targets + SOA; R-08 ADC noise — now with NPLC/ENBW mitigation. No new risk added; severities unchanged.

OPEN_QUESTIONS.md: Q-07/08 several-nA/accuracy — **RESOLVED** (quantified §6–7); Q-04 compliance — **RESOLVED** research (needs Phase 2 DEC for topology); Q-15/16 tooling — already resolved in Phase 0 (hybrid, kicad-cli). Remaining ARCH-blockers for Phase 2: Q-01/Q-02/Q-03 (DAC/ADC/output stage), Q-05/06 (shunt values & relay tech), Q-09–12 (isolation/ground/guard/connector — deferred but Phase 2 must draft). No Phase 1 block persists.

---

## 16. Exit criteria — Phase 1 checklist

1–21 all met (see §3–14); 22–24 met (no schematic/PCB/BOM, git clean). **READY FOR PHASE 2.**

---

## 17. Provenance

Primary: Agent A–D reports cited in §2 + calculation python (`k=1.380649e-23, T=300 K, B brickwall`) independently recomputed in lead (Johnson table verified). Datasheet hierarchy per ENGINEERING_RULES §2.1 was respected; arXiv used for instrumentation claims complementary to peer-reviewed ReRAM papers. URLs in sibling reports are preserved under `docs/research/` and `docs/calculations/`.

*No component promoted. STM32G431/AD5686R/ADA4522/LT1970A/ADS1262/LT1763/ADR4525 remain PROVISIONAL / REQUIRES VERIFICATION.*

