# Gate 1 — Compliance Floor & Range Coercion Summary (Phase 3)

**Project:** ReRAM-SMU V1  
**Gate:** Phase 3 Gate 1 — Tests A+B (LT1970A compliance floor & range coercion)  
**Date:** 2026-08-24  
**Simulator:** ngspice 47 portable (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`) + Python 3.11 `.venv` (numpy)  
**Datasheet authority:** LT1970A 1970afc (Vc 0–5 V → Vsense Vc/10, floor 4 mV typ, linear Vc≥60 mV / Vsense≥6 mV, ideal Vc≥0.5 V)  
**Canonical ranges:** SHUNT_RANGE_TRADEOFF §2.4 D — 10 mA 2.5 Ω/25 mV, 1 mA 25 Ω/25 mV, 100 µA 500 Ω/50 mV, 10 µA 5 kΩ/50 mV, 1 µA 100 kΩ/100 mV, 100 nA 1 MΩ/100 mV

---

## Executive Verdict

**Gate 1 PASS (conditional).**

- **Test A — PASS:** Behavioral floor 4 mV / knee 60 mV reproduced exactly (ngspice 501-pt sweep, rc=0). Matrix confirms IR-01: `I_min = 4 mV/R` is **4% FS at 100 mV**, **8% at 50 mV**, **16% at 25 mV** — `0.1% FS` unreachable with LT1970A alone (40× over).
- **Test B — PASS:** Compliance-aware range coercion (Solution A, V1 REV-A) achieves linear `Vc≥60 mV` for all 6 probe Icomp, including ReRAM-typical `50 µA–1 mA` (4/4 PASS). Ideal `Vc≥0.5 V` only for the tightest 10 µA / 100 µA cases (2/6); the 500 µA / 5 mA cases sit at `125 mV` (still 2× knee) and are therefore **PASS but not ideal**.

**Coercion alone satisfies ReRAM recipes `50 µA–1 mA` for forming compliance.** Separate precision CC loop (Source Candidate C) remains required for:
- `0.1% FS` or sub-floor Icc (e.g., 10 nA on 10 µA, <8 µA on 100 µA),
- simultaneous nA-HRS read + mA-LRS write without autorange,
- MLC ladder needing ≤1% CC accuracy (LT1970A 1% + Rs Tol coarser).

No Gate 1 blocker for V1 REV-A build; coercion firmware + separate-compliance footprint reserved.

---

## Test A — Observed (Matrix 54 cells + ngspice)

**I_min per range (floor / linear / %FS):**

| Range | R | I_min 4 mV/R | floor %FS | I_min 6 mV/R | linear %FS | 0.1% FS | Meets? |
|-------|---|--------------|-----------|--------------|------------|---------|--------|
| 10 mA | 2.5 Ω | 1.60 mA | 16.0% | 2.40 mA | 24.0% | 10 µA | NO |
| 1 mA | 25 Ω | 160 µA | 16.0% | 240 µA | 24.0% | 1 µA | NO |
| 100 µA | 500 Ω | 8.0 µA | 8.0% | 12 µA | 12.0% | 0.1 µA | NO |
| 10 µA | 5 kΩ | 0.80 µA | 8.0% | 1.20 µA | 12.0% | 10 nA | NO |
| 1 µA | 100 kΩ | 40 nA | 4.0% | 60 nA | 6.0% | 1 nA | NO |
| 100 nA | 1 MΩ | 4.0 nA | 4.0% | 6.0 nA | 6.0% | 0.1 nA | NO |

Idempotent: `I_min/FS = 4 mV / V_FS`.

**Full matrix:** `test_A_results.csv` — 8 VALID linear (≤FS & ≥6 mV), 13 INVALID floor/NONLINEAR (<6 mV), 33 VALID-but-Rs-mismatch (>FS, yet linear) → all 33 correctly flagged `REQUIRES RANGE COERCION`. Example excerpt (Vc mV, code):

| Icomp | 10 mA 2.5Ω | 1 mA 25Ω | 100 µA 500Ω | 10 µA 5kΩ |
|-------|------------|----------|-------------|-----------|
| 10 µA | 0.2 FLOOR INVALID | 2.5 FLOOR INVALID | 50 NONLIN INVALID | **500 VALID** |
| 50 µA | 1.2 FLOOR | 12.5 FLOOR | **250 VALID** | 2500 MISMATCH |
| 100 µA | 2.5 FLOOR | 25 FLOOR | **500 VALID** | 5000 MISMATCH |
| 500 µA | 12.5 FLOOR | **125 VALID** | 2500 MISMATCH | 25000 MISMATCH |
| 1 mA | 25 FLOOR | **250 VALID** | 5000 MISMATCH | … |
| 5 mA | **125 VALID** | 1250 MISMATCH | … | … |

*(Full 9×6 table in CSV; 100 nA/1 µA columns overload for mA Icomp)*

**ngspice behavioral sweep:** `lt1970_floor.cir` — `V(vc)` 0–5 V, `Vsense_ideal=V(vc)/10`, `Vsense_floor=(V(vc)/10<4m)?4m:V(vc)/10`, region flag ternary. DC 0–5 V step 10 mV → 501 rows, log rc=0. Probes:

| Vc | Vs_ideal | Vs_floored | err | region | check |
|----|----------|------------|-----|--------|-------|
| 0 mV | 0.00 | 4.00 | 4.00 | 0 floor | PASS |
| 20 mV | 2.00 | 4.00 | 2.00 | 0 | PASS |
| 40 mV | 4.00 | 4.00 | 0.00 | 1 nonlin | PASS |
| 60 mV | 6.00 | 6.00 | 0.00 | 2 linear | PASS |
| 100 mV | 10.00 | 10.00 | 0 | 2 | PASS |
| 500 mV | 50.00 | 50.00 | 0 | 2 | PASS |
| 5 V | 500.0 | 500.0 | 0 | 2 | PASS |

CSV `lt1970_floor_results.csv` carries all 501 points with `LT1970_floor_OK` / `LT1970_linear_OK` flags.

---

## Test B — Observed (Coercion 6 vectors)

Algorithm: tightest `I_FS ≥ Icomp` with `Vc≥60 mV`; prefer `Vc≥0.5 V` among feasible. `Icomp ≤ I_range` enforced; headroom = `V_FS - Vsense`.

| User Icomp | Selected range | R | Vsense | Vc | Vs %FS | Headroom | Vc region | Ideal? | Imeas FS context | PASS? |
|------------|----------------|---|--------|----|--------|----------|-----------|--------|------------------|-------|
| 10 µA | 10 µA | 5 kΩ | 50.0 mV | 500 mV | 100% | 0.0 mV 0% | VALID ideal | YES | mid 5.8 pA Johnson, 50× gain, ties Imeas to 10 µA — LRS mA needs autorange; no snap margin | PASS |
| 50 µA | 100 µA | 500 Ω | 25.0 mV | 250 mV | 50% | 25 mV 50% | VALID linear | NO | 18 pA Johnson, 50% FS, balanced mid-range; needs autorange for HRS<1 µA | PASS |
| 100 µA | 100 µA | 500 Ω | 50.0 mV | 500 mV | 100% | 0 mV 0% | VALID ideal | YES | 18 pA, 100% FS no margin | PASS |
| 500 µA | 1 mA | 25 Ω | 12.5 mV | 125 mV | 50% | 12.5 mV 50% | VALID linear | NO | high-I 81 pA negligible, 100× gain, covers LRS mA; nA HRS <0.01% FS separate range | PASS |
| 1 mA | 1 mA | 25 Ω | 25.0 mV | 250 mV | 100% | 0 mV 0% | VALID linear | NO | 81 pA, 100% FS no margin | PASS |
| 5 mA | 10 mA | 2.5 Ω | 12.5 mV | 125 mV | 50% | 12.5 mV 50% | VALID linear | NO | 257 pA, 50% FS | PASS |

6/6 PASS linear, 2/6 ideal. Window `50 µA–1 mA`: 4/4 PASS.

**ReRAM recipe answer:** Yes — `50 µA` (Vc 250 mV), `100 µA` (500 mV), `500 µA` (125 mV), `1 mA` (250 mV) all linear with correct range. Limitations:
- `125 mV` cases (≈2× knee) have 4× less noise margin than the `500 mV` ideal — acceptable but not generous; size Icc to prefer ≥25 mV Vsense (≥50% FS) where possible.
- `0%` headroom at 10 µA / 100 µA / 1 mA means filament snap overshoot will hit range compliance — firmware must hold range and use slew limit + `R_iso`/C budgeting (IR-14) to keep `I=C·dV/dt < Icc`.

**When Candidate C required:** `Icc` below floor (e.g., <12 µA on 100 µA, <240 µA on 1 mA), demand for `0.1% FS` (10 nA on 10 µA would need 4 V FS), or decoupling measurement from compliance (e.g., limit 1 mA while reading 100 nA HRS without range coercion forcing Imeas FS=1 mA).

---

## Files (this gate)

| Path | Content | Simulator | Rows/Size |
|------|---------|-----------|-----------|
| `simulation/phase3/compliance/test_A_LT1970_floor.py` | Matrix + harness, Shunt tradeoff import, ternary ngspice gen | Python 3.11 | — |
| `simulation/phase3/compliance/test_A_results.csv` | Requested Icomp | Range | R | Required Vc | Region | Result | Python | 54 |
| `simulation/phase3/compliance/lt1970_floor.cir` | Behavioral LT1970A (Vc/10 floor 4 mV, ternary region) | ngspice 47 | — |
| `simulation/phase3/compliance/lt1970_floor.log` | ngspice stdout/stderr, 501 data rows, rc=0 | ngspice 47 | — |
| `simulation/phase3/compliance/lt1970_floor_results.csv` | Vc vs Vsense vs region (0–5 V, 501 pts) | ngspice 47 | 501 |
| `simulation/phase3/compliance/lt1970_floor_raw.txt` | ngspice print raw | ngspice 47 | 501 |
| `simulation/phase3/compliance/lt1970_floor_wrdata.txt` | ngspice wrdata (10-col interleaved, correctly parsed) | ngspice 47 | 501 |
| `simulation/phase3/compliance/test_B_range_coercion.py` | Coercion selector (tightest feasible ≥60 mV, prefer ≥0.5 V) | Python 3.11 | — |
| `simulation/phase3/compliance/test_B_results.csv` | User Icomp | Selected range | Vc | Headroom | Consequence | PASS? | Python | 6 |
| `simulation/phase3/compliance/README.md` | Per-test headers: Test, Requirement, Architecture, Simulator, Model versions, Conditions, Metric, PASS threshold, Observed, Verdict, Model limitations, Recommended action (A+B) | — | — |
| `simulation/results/phase3/gate1_compliance.md` | This file — gate summary | — | — |

Reproduce: see `simulation/phase3/compliance/README.md` “How to Reproduce”.

---

## Model Limitations (combined)

- Behavioral only — hard `max(4 mV, Vc/10)` + ternary knee; no gradual gm compression, offset/TC, DAC INL, Rs tolerance/TC, supply headroom, load dependence, or 4 µs loop dynamics. Vendor macro not used.
- `C_upstream`/`C_downstream`, `R_iso`, compliance energy `½CV²`, and stability under `10 pF–10 nF` + cable not in this DC threshold gate (deferred to I/J/K/O).
- Coercion table assumes `compliance_range = measurement_range` (Solution A). Decoupled Solutions B/C not simulated here; TLV3501 supervisor `Vos ±6.5 mV` / hysteresis 6 mV (IR-08) not in this gate.
- Johnson quoted at 10 Hz brickwall; `en`, ADC, and ENBW 1.253 included only as scaling, not as system noise simulation.

Datasheet override: any result contradicting `1970afc 4 mV / 60 mV` thresholds is a model fault.

---

## Recommended Actions

1. Keep coercion (Solution A) for V1 REV-A; implement firmware `select_range(Icomp)` as shipped in `test_B_range_coercion.py`, with autorange holdoff and per-sample logging. Forbid silent `VALID-but-Rs-mismatch` use.
2. Reserve PCB footprint for separate compliance-sense R bank (Solution B) and Candidate C outer precision loop (ADA4522/OPA140 + LT1970A booster) — Phase 3 tests O will decide promotion.
3. Maintain IR-14 downstream-C budget (`≤80–150 pF @5 V` for 1 nJ, `R_iso 33–47 Ω` upstream of `R_iso`) and slew-limited DAC ramps regardless of coercion.
4. Calibrate compliance by measuring clamped current into a short with the precision ADC; do not trust `Vc/10/R` open-loop (includes Rs, DAC, reference errors).

**Gate 1 closed — proceed to Phase 3 tests C–O per `PHASE3_SIMULATION_PLAN.md`.**
