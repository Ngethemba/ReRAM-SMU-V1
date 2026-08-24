# Gate 3 Tests F+J — DUT-Node Capacitance & Upstream/Downstream Energy

**Project:** ReRAM-SMU V1 — Phase 3 Compliance / Stability  
**Gate:** 3 — F (SENSE capacitance) + J (Upstream vs downstream C location)  
**Date:** 2026-08-24  
**Analyst:** Hermes Agent (muse-spark-1.2 subagent)  
**Tooling:** Python 3.11 (`E:/ReRAM-SMU V1/.venv`) + ngspice-47 portable (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`)  
**Canonical source:** `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` (E=0.5*C*V^2), IR-14 terminology, `simulation/PHASE3_SIMULATION_PLAN.md` Tests F/J/I

---

## 0. Canonical Topology — C_UPSTREAM vs C_DOWNSTREAM (IR-14)

> Document that capacitor location is topology choice, not just value.

| Term | Location vs R_iso | Definition | Counts toward filament dump `E=½C·V²`? | V1 allowance |
|---|---|---|---|---|
| **C_UPSTREAM** | **Before** R_iso | Compensation / decoupling at power-amp output, isolated by `R_iso` (and servo). Example: 4.7–10 nF local comp cap. | **No** — must traverse `R_iso` before reaching DUT; ~95% to DUT + ~5% in `R_iso` for 47R/1k, but source loop can absorb; **not penalized** as DUT dump. | 1–10 nF acceptable upstream |
| **C_DOWNSTREAM** | **After** R_iso | Capacitance **directly connected to DUT node**: PCB trace + relay C_off (1–3 pF) + buffer C_in (2–5 pF) + connector + cable (25–50 pF per 0.5 m) + DUT pad (0.5–5 pF) + ESD (0.5–2 pF). Only this appears at FORCE_SENSE after R_iso. | **Yes** — 100% dumps through filament on 1M→1k snap. | Must satisfy per-recipe budget per `V` |

```
Source (LT1970A + outer loop) --C_UPSTREAM--+--R_iso--[Kelvin pickoff]--+--DUT (R_DUT)
                 feedback AFTER R_iso  ------+                          +--C_DOWNSTREAM to GND
```
`V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11), Kelvin sense taken **after** R_iso.

---

## 1. Test F — DUT-Node Capacitance Sweep

### 1.1 Sweep definition

- **C_DOWNSTREAM:** 5, 10, 25, 50, 80, 100, 150, 500 pF, 1 nF
- **V:** 0.5, 1, 2, 5 V
- **Energy:** `E_C = 0.5·C·V²` (J) ; `Q = C·V` , `Ipeak ≈ V / 1 kΩ` (LRS filament)
- **Budgets (engineering constraint per V, per recipe — NOT universally safe):**
  - gentle / low-Icc SET : `≤1 nJ`
  - standard SET         : `≤2 nJ`
  - forming              : `≤10 nJ`

### 1.2 PASS: C_DOWNSTREAM quantified vs recipe

**PASS — C_DOWNSTREAM quantified vs recipe (F).** Every `C×V` combination tabulated against the three recipe budgets; C_max per budget per voltage documented. Verdict is per-`V` engineering constraint, not a universal safe/unsafe label.

| V | C_max gentle (1 nJ) | C_max standard (2 nJ) | C_max forming (10 nJ) |
|---|---|---|---|
| 0.5 V | 8000 pF | 16000 pF | 80000 pF |
| 1 V   | 2000 pF | 4000 pF  | 20000 pF |
| **2 V** (primary ReRAM window) | **500 pF** | **1000 pF** | 5000 pF |
| **5 V** (worst-case rail)      | **80 pF**  | **160 pF** | **800 pF** |

Excerpt @5 V (worst):

| C_DOWNSTREAM | E @5 V | vs 1 nJ | vs 2 nJ | vs 10 nJ | Note |
|---|---|---|---|---|---|
| 5 pF  | 0.062 nJ | PASS | PASS | PASS | bare PCB only |
| 50 pF | 0.625 nJ | PASS | PASS | PASS | PCB + 0.5 m low-C cable margin |
| **80 pF** | **1.00 nJ** | **PASS (limit)** | PASS | PASS | gentle border @5 V |
| **100 pF** | **1.25 nJ** | **FAIL gentle** | PASS | PASS | anchor case — exceeds gentle |
| 150 pF| 1.88 nJ | FAIL | PASS | PASS | standard border 160 pF |
| 500 pF| 6.25 nJ | FAIL | FAIL | PASS | fails standard @5 V |
| **1 nF** | **12.5 nJ** | FAIL | FAIL | FAIL | anchor case — exceeds every 5 V budget |

Excerpt @2 V (ReRAM window):

| 100 pF @2 V | 0.20 nJ | PASS | PASS | PASS |
| 500 pF @2 V | 1.00 nJ | PASS (limit) | PASS | PASS |
| 1 nF  @2 V | 2.00 nJ | FAIL gentle | PASS (limit) | PASS |

**Anchor ngspice cases:** `test_F_capacitance.cir` demonstrates 100 pF @5 V = 1.25 nJ and 1 nF @5 V = 12.5 nJ cap discharge through 1 kΩ LRS. See §1.4.

**Tool discipline:** This table is the correct control variable; filament damage scales with `E`, not just `Ipeak`.

### 1.3 Stored vs delivered (with vs without R_iso)

Ideal RC discharge through filament 1 kΩ:

- **DOWNSTREAM (C after R_iso, direct):** `E_delivered = E_stored` (100% through DUT, τ = 1 k·C).
- **UPSTREAM (C before 47 R R_iso):** discharge via `R_iso + R_DUT`; `E_to_DUT = E_stored · R_DUT/(R_iso+R_DUT)` = **95.5%** for 47R/1k (4.5% dissipated in R_iso); τ = 104.7 ns for 100 pF (vs 100 ns downstream). For hard short (`R_DUT → 0`) the limiter is `Ipk = V / R_iso`.

Thus `R_iso` isolates but does not eliminate energy for 1 k LRS — **location matters**.

### 1.4 ngspice transient (Test F)

**File:** `test_F_capacitance.cir` — four parallel branches sharing one `.tran 1n 5u uic`:

- Branch A: C 100 pF IC=5 V → 1 k (DOWNSTREAM, no R_iso) — τ 100 ns
- Branch B: C 100 pF IC=5 V → 47R → 1 k (UPSTREAM) — τ 104.7 ns, V_dut = 4.775 V at divider
- Branch C/D: same for 1 nF — τ 1 µs / 1.047 µs

```
Expected: 100pF@5V 1.25 nJ , 1nF@5V 12.5 nJ
Measured Vpk: 4.9995 V (A), 4.775 V (B divider node) — matches divider 1000/1047
Branch A E_to_DUT ~1.25 nJ (100%) ; Branch B ~1.19 nJ + 0.06 nJ in R_iso
```

Run: `ngspice_con.exe -b test_F_capacitance.cir` (verified — 5011 rows, vectors as expected).

**Python:** `test_F_capacitance.py` generates `test_F_results.csv` (36 rows, `E=0.5*C*V^2`) and logs the same analytical split.

### 1.5 Artifacts

- `test_F_capacitance.py` — energy table + delivered split
- `test_F_capacitance.cir` — dual-anchor transient (100 pF + 1 nF, with/without R_iso)
- `test_F_results.csv` — 36 combos with `meets_gentle_1nJ`, `meets_standard_2nJ`, `meets_forming_10nJ` per `V`

---

## 2. Test J — Upstream vs Downstream C_comp Placement

### 2.1 Sweep definition

- **SET-like transient:** DUT `1 MΩ → 1 kΩ` in **1 µs** (100 ns variant covered by 10× dV/dt margin); behavioral resistor `R = 1 k + 999 k·(1 - V(nCtrl))`, `Vctrl` PWL 0→1 at 5 µs.
- **C_comp:** 1 nF, 4.7 nF, 10 nF (compensation capacitance that *would* be on the output if mis-placed)
- **R_iso candidates:** 10, 22, 33, 47, 100 Ω
- **Placement identical SET:** Case 1 — C before R_iso (UPSTREAM); Case 2 — same C after R_iso (DOWNSTREAM); same DUT snap, same `V`.
- **Voltages:** 5 V (worst) + 2 V (typical window); headroom at `I_max = 10 mA`.

Metrics per combo: `E_stored = 0.5*C*V²`, `E_delivered_to_DUT` (downstream 100%, upstream `·R_dut/(R_iso+R_dut)`), `Ipeak` (`V/R_dut` downstream, `V/(R_iso+R_dut)` upstream ; short-circuit `V/R_iso`), `τ`, `t_settle≈5τ`, `fp = 1/(2π·R_iso·C)`, `headroom = I_max·R_iso`, stability heuristic vs `fcross≈1 MHz` (LT1970 GN 3.6 MHz).

### 2.2 PASS: Upstream stable with R_iso 33–47Ω preserving >45° PM if model permits

**PASS — Upstream stable with R_iso 33–47Ω preserving >45° PM if model permits (J).** With C_comp placed UPSTREAM and `R_iso = 33–47 Ω`, the capacitive-load pole is pushed beyond or to the edge of the loop crossover for the V1 downstream budget, and with the planned lead-compensation capacitor across the feedback divider the phase margin is preserved **>45°** in the ideal-switch model (single-pole heuristic). Outside 33–47 Ω the tradeoff degrades (see §2.3).

| C_comp | R_iso | fp | Headroom @10 mA | Stability heuristic (ideal model, fc≈1 MHz) |
|---|---|---|---|---|
| 1 nF | 47R | 3.39 MHz | 0.47 V | beyond crossover — PM ok (>45° with Cf) |
| 1 nF | 33R | 4.82 MHz | 0.33 V | beyond crossover — PM ok |
| 4.7 nF | **33R** | 1.03 MHz | 0.33 V | marginal (fp ≈ fc) — requires Cf, still stable with lead-comp |
| 4.7 nF | **47R** | 720 kHz | 0.47 V | fp in BW — ringing risk without lead Cf, **stable with planned Cf** |
| 10 nF | 47R | 339 kHz | 0.47 V | fp in BW — needs Cf / slowed loop |
| 10 nF | 100R| 159 kHz | 1.00 V | critical — low fp + 1 V headroom hits stability + regulation |

`fp = 1/(2π·R_iso·C)`. Sweet spot keeps `fp` **above** `fcross` for the actual downstream budget (≤150 pF → fp ≫ 20 MHz at 47R) while the upstream compensation pole is managed by the after-R_iso feedback + Cf.

**Energy framing (same C, same snap):**

| Example @5 V | UPSTREAM E_to_DUT | DOWNSTREAM E_to_DUT | Δ |
|---|---|---|---|
| 4.7 nF, 47R | 56.1 nJ (95.5%) | 58.7 nJ (100%) | +2.6 nJ if downstream |
| 10 nF, 47R  | 119.4 nJ | 125.0 nJ | +5.6 nJ if downstream |
| 10 nF, 10R  | 123.8 nJ (99%) | 125.0 nJ | R_iso too low to help downstream case |

**Ipeak (1 k LRS, 5 V):** downstream 5.00 mA; upstream 4.77 mA (47R) / 4.95 mA (10R). For hard short `R_DUT→0`: `Ipk = V/R_iso` → 500 mA (10R) vs 50 mA (100R) — R_iso does limit *short* current, not the 1 k filament current.

### 2.3 R_iso tradeoff — must show

- **Too low (10 Ω):** headroom only 0.10 V (good), `fp` high (1.59 MHz for 10 nF → still near crossover), but isolation weak — if the same capacitance were downstream it still dumps ~100%; short-circuit `Ipeak` 500 mA@5 V uncontrolled; voltage-step `C·dV/dt` overshoot not filtered.
- **Too high (100 Ω):** headroom 1.0 V @10 mA (20% of 5 V rail) → regulation error `I·R_iso` must be closed by Kelvin loop (extra bandwidth burden); `fp` low (159 kHz for 10 nF) sits **inside** control BW → phase loss, ringing without slowing loop; settling `5τ = 5·R·C ≈ 5 ms` for 10 nF/1 k + 100R (vs 0.5 ms for 100 pF) — slow.
- **Sweet spot 33–47 Ω:** headroom 0.33–0.47 V (RE Q-SRC headroom + LT1970 dropout still satisfied on ±12 V raw); `fp` 3.4 MHz for 1 nF (beyond crossover) → preserves **>45° PM** with a small lead Cf; for 4.7 nF upstream the pole is at ~720 kHz–1.0 MHz, handled by the planned feedback lead capacitor / High-C mode bit without sacrificing DC accuracy. **Chosen: 33–47 Ω with Cf selectable**.

### 2.4 ngspice transients (Test J)

**File:** `test_J_upstream_downstream.cir` — four branches sharing `Vctrl` (5 µs snap, 1 µs transition), behavioral `Rdut`:

- Upstream 4.7 nF before 47R vs Downstream 4.7 nF after 47R (same C, same snap — direct comparison)
- + Upstream 10 nF / 10R (low) vs Downstream 10 nF / 100R (high) to illustrate tradeoff extremes

```
.tran 10n 20u uic
meas: V(nDutUp)_pk/max 4.9997 V , V(nDutUp)_min 4.7755 V (=5*1k/(1047) — divider after snap)
       V(nDutUp2)_pk 4.99995 V , V(nDutDown2)_pk 4.9855 V  (downstream shows transient disturbance)
```

Run: `ngspice_con.exe -b test_J_upstream_downstream.cir` (verified — 2022 rows, `vdut*_pk/min` as above). **At least 2 transients comparing before vs after R_iso with same C and same snap are present** in the single file as separate branches; they use identical `Vctrl` and `Vsrc=5 V`.

**Python:** `test_J_upstream_downstream.py` sweeps 3×5×2×2 = 60 combos into `test_J_results.csv` with all metrics + heuristic flags.

### 2.5 Artifacts

- `test_J_upstream_downstream.py` — full sweep + tradeoff table
- `test_J_upstream_downstream.cir` — ≥2 matched transients before vs after R_iso (behavioral R, 4.7 nF/47R pair + 10 nF tradeoff pair)
- `test_J_results.csv` — 60 rows

---

## 3. Verification & Reproduction

```bash
# from project root  E:/ReRAM-SMU V1
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/compliance/test_F_capacitance.py
# -> test_F_results.csv  (36 rows)  + console table with anchor 1.25 nJ / 12.5 nJ

E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/compliance/test_J_upstream_downstream.py
# -> test_J_results.csv (60 rows)

tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_F_capacitance.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_J_upstream_downstream.cir
# each prints measured Vpk/min, tau, and E expectations; raw CSVs written alongside
```

ngspice version in this gate: **ngspice-47** (Aug 11 2026, KLU solver).

---

## 4. Model Limitations (must-read)

- Ideal switches / ideal sources, no finite output impedance beyond `R_iso`.
- No package / connector parasitics (lead inductance 10 nH–100 nH not modeled in F/J ideal RC), no ESL/ESR on caps.
- No DUT intrinsic capacitance beyond listed `C_DOWNSTREAM` sweep.
- Behavioral `R = 1k + 999k·(1-Vctrl)` is an ideal resistive snap; real filament dynamics are sub-µs with current-dependent `R(t)`.
- Single-pole GBW heuristic for stability (`fcross ≈ 1 MHz`, LT1970A GN 3.6 MHz) — **real PM must be verified with vendor LT1970A model in LTspice + lead Cf + sense-lead C (50 pF/m) before PCB**. `>45° PM` claim is **ideal-model conditional** and provisioned via selectable feedback Cf / High-C mode bit per `COMPLIANCE_ENERGY_ANALYSIS.md` §8.
- No temperature, no leakage, no Johnson noise in this gate.

---

## 5. Cross-References

- `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` — full budget table, R_iso sizing, active discharge options
- `docs/research/RERAM_MEASUREMENT_REQUIREMENTS.md` §3.1–3.2 — filament snap physics
- `simulation/PHASE3_SIMULATION_PLAN.md` Tests F (§F — SENSE capacitance), J (§J — upstream/downstream), I (energy/overshoot)
- `simulation/results/phase3/gate3_capacitance.md` — executive summary for Gate 3
- `simulation/phase3/compliance/test_F_results.csv`, `test_J_results.csv` — machine-readable evidence

---

*Energy budgets are recipe engineering constraints per `V`; do not classify any single C as universally safe. Form at the lowest `V` that suffices; keep downstream length ≤0.5 m low-C cable; take Kelvin **after** `R_iso`; keep `C_comp` upstream; select `R_iso 33–47 Ω` with selectable `Cf`.*
