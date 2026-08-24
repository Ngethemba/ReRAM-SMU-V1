# Gate 1 — Tests A+B — LT1970A Compliance Floor & Range Coercion

**Project:** ReRAM-SMU V1 — Phase 3 Gate 1  
**Date:** 2026-08-24  
**Authors:** Phase 3 simulation — Gate 1 compliance  
**Toolchain:** ngspice 47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`), Python 3.11 `.venv` (numpy), LT1970A datasheet 1970afc (primary authority)

---

## Canonical Range Table (per SHUNT_RANGE_TRADEOFF §2.4 D — sole source of truth)

| Range | V_FS | R_shunt | I_FS | Gain →2.5V | Johnson 10 Hz (brickwall) | ENBW 1.253× |
|-------|------|---------|------|------------|---------------------------|-------------|
| 10 mA | 25 mV | 2.5 Ω | 10 mA | 100× | 0.64 nV / 257 pA | 322 pA |
| 1 mA | 25 mV | 25 Ω | 1 mA | 100× | 2.04 nV / 81 pA | 102 pA |
| 100 µA | 50 mV | 500 Ω | 100 µA | 50× | 9.1 nV / 18 pA | 22.8 pA |
| 10 µA | 50 mV | 5 kΩ | 10 µA | 50× | 28.8 nV / 5.8 pA | 7.2 pA |
| 1 µA | 100 mV | 100 kΩ | 1 µA | 25× | 129 nV / 1.29 pA | 1.61 pA |
| 100 nA | 100 mV | 1 MΩ | 100 nA | 25× | 407 nV / 0.41 pA | 0.51 pA |

Constants: `k=1.380649e-23 J/K`, `T=300 K`, `vn=√(4kTRB)`, `in=vn/R`.

---

## Test A — LT1970A Compliance Floor & Linear Region

| Field | Entry |
|-------|-------|
| **Test** | A — LT1970A programmable compliance floor vs measurement shunt matrix |
| **Requirement** | REQ-SAFE-001 + IR-01 (1970afc): LT1970A `I_LIM = Vc/(10·Rsense)`, `Vsense = Vc/10`, floor `Vsense_min 4 mV typ` (Vc 40 mV), linear only `Vc≥60 mV` (Vsense≥6 mV). Minimum programmable Icc per range is `4 mV/R` (4% FS at 100 mV, 8% at 50 mV, 16% at 25 mV); `0.1% FS` not achievable with LT1970A alone — requires coercion or Candidate C. No unsafe Vc (floating/out-of-range) allowed. |
| **Architecture** | LT1970A power stage with compliance sense across `Rsense` (high-side Kelvin, distinct from low-side measurement shunt bank if separate). This test evaluates the *shared-R* hypothesis to prove why a single Rsense cannot cover 0.1% across decades. Candidate solutions A–D enumerated in IR-01; this test validates the floor that motivates Solution A (coercion) adopted for V1 REV-A. |
| **Simulator** | ngspice 47 (`ngspice_con.exe -b`) + Python/numpy post-processing |
| **Model versions** | LT1970A behavioral: `Vsense_floor = max(4 mV, Vc/10)`, `Vsense_ideal = Vc/10`, region flag `Vc<40 mV→0 INVALID floor`, `40–60 mV→1 NONLINEAR`, `≥60 mV→2 VALID linear`. No vendor macro — behavioral threshold model only. Ideal passives; `T=27 °C`. See `lt1970_floor.cir`. |
| **Conditions** | Vc swept 0–5 V DC (step 10 mV, 501 points). Per-range matrix: `Icomp = {10,20,50,100,200,500} µA, {1,5,10} mA` × 6 ranges (54 cells). Computed `Vc = Icomp·R·10`, `Vsense = Icomp·R`. Compared against `V_FS`, floor, knee. |
| **Metric** | For each cell: `Required Vc`, `Vsense`, LT1970 region (`INVALID floor` if `Vsense<4 mV`/`Vc<40 mV`, `NONLINEAR <60mV` if `4≤Vsense<6 mV`, `VALID linear` if `≤FS` and `≥6 mV`, `VALID but Rs mismatch` if `>FS` yet `≥60 mV`), Result (`VALID` / `INVALID` / `REQUIRES RANGE COERCION`). Plus per-range `I_min_floor=4 mV/R`, `I_min_linear=6 mV/R`, floor%FS, linear%FS. Floor/knee verification via ngspice DC sweep (Vsense vs Vc). |
| **PASS threshold** | (i) ngspice sweep reproduces floor 4.0±0.1 mV for `Vc<40 mV` and tracks `Vc/10` within 50 µV for `Vc≥60 mV` (PASS). (ii) Matrix correctly classifies floor as 16%/8%/4% FS per V_FS and shows `0.1% FS` unreachable (IR-01 recomputation). No cell claims linear where `Vc<60 mV`. |
| **Observed** | **I_min per range:** 10 mA: 1.60 mA floor (16%), 2.40 mA linear (24%); 1 mA: 160 µA (16%), 240 µA (24%); 100 µA: 8.0 µA (8%), 12 µA (12%); 10 µA: 0.80 µA (8%), 1.20 µA (12%); 1 µA: 40 nA (4%), 60 nA (6%); 100 nA: 4.0 nA (4%), 6.0 nA (6%). Target `0.1% FS` = 10 µA/1 µA/0.1 µA/10 nA/1 nA/0.1 nA → all **40× over** (NO). <br>**Matrix (54 cells):** 8 VALID, 13 INVALID, 33 VALID-but-Rs-mismatch (requires coercion). Example 10 µA: only 10 µA range gives `Vc=500 mV VALID`; 100 µA range is `Vc=50 mV NONLINEAR` (invalid), lower ranges overload (`>FS`), higher ranges `FLOOR`. 1 mA on 1 mA range is `Vc=250 mV VALID`; on 10 mA range `Vc=25 mV FLOOR` invalid. Full table in `test_A_results.csv`. <br>**ngspice sweep (501 pts):** At Vc 0 mV → Vsense_floored 4.00 mV (ideal 0 mV, err 4.00 mV, region 0); 20 mV→4.00 mV; 40 mV→4.00 mV (region 1); 60 mV→6.00 mV (region 2, err 0); 100 mV→10.00 mV; 500 mV→50.00 mV; 5 V→500 mV — all within spec. Log `lt1970_floor.log` rc=0, `lt1970_floor_results.csv` 501 rows PASS probes. |
| **Verdict** | **PASS** — Floor and 60 mV knee reproduced exactly; IR-01 recomputation confirmed (4%/8%/16% FS); matrix correctly flags no `0.1% FS` LT1970A capability. The 8 VALID cells are the only *physically linear* pairings; all other linear-Vc but over-FS cells correctly require coercion. |
| **Model limitations** | Behavioral only — models `Vsense = max(4 mV, Vc/10)` with hard ternary knee, not the datasheet's gradual nonlinear transconductance below 60 mV, offset/drift, TC, Rs tolerance, amp `Ib·Rf`, supply headroom, load regulation, or actual LT1970A loop dynamics (4 µs takeover, phase margin). No temperature, Monte Carlo, or vendor macro. Floor is taken as *typical* 4 mV (max not modeled). Compensation, `R_iso`, `C_downstream` energy not in this DC threshold test (covered in tests I/J). `VCSRC/VCSNK` common-mode `VCC-1.5` to `VEE+1.5` not enforced. |
| **Recommended action** | Keep canonical coercion (Test B) for V1 REV-A; footprint separate compliance-sense bank (Solution B) and Candidate C precision outer loop for Phase 3 evaluation. No schematic promotion of a single shared-R LT1970A claiming `0.1% FS`. Document calibration of clamped current into short via precision ADC (not open-loop trust). Downstream-C budgeting (`C_UPSTREAM ≤10 nF`, `C_DOWNSTREAM ≤80–150 pF @5 V`) remains mandatory per IR-14. |

**Artifacts:** `test_A_LT1970_floor.py` (generator + sweep harness), `lt1970_floor.cir` (ngspice netlist, ternary corrected for ngspice 47), `lt1970_floor.log` (ngspice 47 stdout, rc=0, 501 data rows), `lt1970_floor_results.csv` / `lt1970_floor_raw.txt` / `lt1970_floor_wrdata.txt` (sweep 0–5 V, wrdata 10-col interleaved correctly parsed), `test_A_results.csv` (54-row matrix)

---

## Test B — Compliance-Aware Range Coercion

| Field | Entry |
|-------|-------|
| **Test** | B — Range coercion matrix (IR-01, DEC-024) — firmware selects safe compliance range |
| **Requirement** | REQ-SAFE-001 (revised DEC-024) + REQ-MEAS-004 autorange hysteresis: requested `Icomp` → firmware selects measurement/compliance range whose `Vsense_FS` yields achievable `Vc≥60 mV` (ideally `Vc≥0.5 V`). Enforce invariant `Icomp ≤ I_range` unless autorange raises range before voltage step; log `Icomp_requested`, `I_range`, `compliance_range`, `Vc`, `Rsense_compliance`. No silent clamping to wrong range; no `Vc<60 mV` linear claim; range-change holdoff to absorb `I=C·dV/dt`. |
| **Architecture** | Solution A (adopted for V1 REV-A): single shunt bank shared between compliance and measurement; coercion steers *both* together (compliance range = measurement range). Alternative Solutions B–D footnoted but not executed here. Coercion picks tightest `I_FS ≥ Icomp` satisfying `Vc≥60 mV` (largest `R` that fits), preferring `Vc≥0.5 V` among feasible. If no feasible linear range → error / require Candidate C. |
| **Simulator** | Python 3.11 `.venv` (numpy) deterministic table; no SPICE (coercion is firmware logic, verified by recomputing the same physics as Test A). Johnson/gain values use canonical `SHUNT_RANGE_TRADEOFF` calculation (`vn=√(4kTR·10 Hz)`, ENBW 1.253×). |
| **Model versions** | Same thresholds as Test A (`4 mV floor`, `6 mV linear`, `60 mV`/`0.5 V` ideals). Range table canonical D. No vendor model. |
| **Conditions** | Test vectors `Icomp = 10, 50, 100, 500 µA, 1, 5 mA` (6 cases covering decades + mid-decade, including ReRAM typical `50 µA–1 mA`). Evaluated against all 6 ranges, then selected best per algorithm. Headroom computed as `V_FS - Vsense` and `%FS`. |
| **Metric** | Per vector: Selected range, `R`, `Vsense`, `Vc`, `Vsense%FS`, Headroom `mV`/`%`, `Vc` region, Ideal met (`≥0.5 V`?), Measurement consequence (range mismatch vs `Imeas FS`, Johnson `pA@10 Hz`/`ENBW`, gain), PASS? (`Vc≥60 mV` ∧ `Icomp≤I_FS` ∧ no negative headroom). Overall gate: does coercion alone cover ReRAM recipes `50 µA–1 mA` or is Candidate C required? |
| **PASS threshold** | Each selected range must satisfy `Vc≥60 mV` (linear), `Icomp≤I_FS` (no shunt overload), headroom `≥0`. No `NONLINEAR`/`INVALID floor` selection; no silent `VALID-but-Rs-mismatch`. |
| **Observed** | All 6 coercion cases **PASS** linear: <br>• 10 µA → **10 µA** (`5 kΩ`, `Vs=50 mV`, `Vc=500 mV`, `100% FS`, `0 mV head`, ideal YES, Johnson 5.8 pA, gain 50×, measurement ties `Imeas FS=10 µA` — cannot meter mA LRS without autorange, at 100% FS no snap margin). <br>• 50 µA → **100 µA** (`500 Ω`, `Vs=25 mV`, `Vc=250 mV`, `50% FS`, `25 mV head`, linear but not ideal, Johnson 18 pA, 50% utilization, needs autorange for HRS<1 µA). <br>• 100 µA → **100 µA** (`500 Ω`, `50 mV`, `500 mV`, `100% FS`, ideal YES, 0 mV head, same 50× gain). <br>• 500 µA → **1 mA** (`25 Ω`, `12.5 mV`, `125 mV`, `50% FS`, `12.5 mV head`, 2× knee, not ideal, Johnson 81 pA negligible at high-I, 100× gain). <br>• 1 mA → **1 mA** (`25 Ω`, `25 mV`, `250 mV`, `100% FS`, `0 mV head`, linear). <br>• 5 mA → **10 mA** (`2.5 Ω`, `12.5 mV`, `125 mV`, `50% FS`, `12.5 mV head`, linear). <br>6/6 PASS linear, 2/6 ideal (`≥0.5 V`). ReRAM window `50 µA–1 mA`: **4/4 PASS**. Headroom at `100% FS` cases (10 µA, 100 µA, 1 mA) warns no transient margin — snap overshoot would trip range compliance. |
| **Verdict** | **PASS** for ReRAM-typical `50 µA–1 mA`: coercion alone achieves linear `Vc≥125 mV` (2–8× knee) with proper range, satisfying forming Icc without external loop. **Conditional PASS** — ideal `0.5 V` only for `10 µA` and `100 µA` (tightest ranges at 100% FS); the `500 µA`/`5 mA` cases sit at `125 mV` (8× above floor but 4× below ideal, still linear). `1 mA` at `0%` headroom is legal but fragile to snap transient. |
| **Model limitations** | Table-logic only — no firmware state machine, hysteresis/dwell, or range-change holdoff timing simulated; no autorange chatter, `C·dV/dt` blanking, or relay PhotoMOS `R_on`/`Coff` modeled. No DAC `INL`/`DNL`, reference TC, `Rs` tolerance/TC, `Ib·Rf` error, or TLV3501 supervisor `Vos` (IR-08) included. Johnson is brickwall-10 Hz, not including amplifier `en` or ADC noise. Assumes `compliance_range = measurement_range` (Solution A); decoupled Solution B/C not evaluated here. |
| **Recommended action** | **V1 REV-A:** Ship Solution A coercion with firmware invariant `Icomp ≤ I_range`, autorange holdoff `≥10 ms` after range steer, per-sample logging of `{Icomp_requested, I_range, compliance_range, Vc, Rs_compliance, compliance_flag}`, and error path when no `Vc≥60 mV` range exists (prompt autorange enable or Recipe error, not silent clamp). Size recipe Icc to prefer `Vsense≥25 mV` (≥50% FS on mid ranges) to improve margin above the `125 mV` cases; allow HV recipes to use `1 MΩ` not for mA but for HRS reads on a *different* range via autorange. <br>**V1 REV-B / Candidate C trigger:** If recipe demands `Icc <8 µA` on `100 µA` range or `Icc≤1 µA` with `0.1% FS` accuracy, or simultaneous nA-HRS + mA-LRS without range change, or MLC ladder needing <1% CC accuracy — promote Candidate C (precision outer loop + LT1970A booster) per IR-15/`SOURCE_STAGE_CANDIDATES`. No change to IR-14 `C_downstream`/`R_iso` budgeting. |

**Artifacts:** `test_B_range_coercion.py` (algorithm + table generator), `test_B_results.csv` (6-row coercion matrix with measurement consequence)

---

## How to Reproduce

```bash
# From repo root E:/ReRAM-SMU V1, with .venv Python 3.11
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/compliance/test_A_LT1970_floor.py
# -> test_A_results.csv, lt1970_floor.cir, lt1970_floor.log, lt1970_floor_results.csv
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/compliance/test_B_range_coercion.py
# -> test_B_results.csv
# Re-run ngspice alone:
E:/ReRAM-SMU\ V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/lt1970_floor.cir
```

Primary datasheet override: `1970afc` floor 4 mV typ / 60 mV Vc linear thresholds govern; any simulation contradicting them is a model fault.

---

## Traceability

| Requirement / Finding | Test | Provenance |
|-----------------------|------|------------|
| REQ-SAFE-001 + IR-01 (compliance floor/coercion) | A, B | LT1970A 1970afc 4 mV/60 mV, DEC-024, PHASE2_CORRECTIONS IR-01 |
| SHUNT_RANGE_TRADEOFF §2.4 D (25/50/100 mV) | A, B | Canonical D table |
| PHASE3_SIMULATION_PLAN tests A, B (IR-16) | A, B | This gate |
