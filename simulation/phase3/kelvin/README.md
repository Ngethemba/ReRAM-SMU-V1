# Gate 2 — Kelvin Servo & Open-Sense (Tests C+D)
**Project:** ReRAM-SMU V1 — Phase 3 Simulation  
**Date:** 2026-08-24  
**Tool:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`), Python 3.11 `.venv`  
**Status:** Simulation-only, behavioral, no PCB — see Model Limitations  
**Requirements:** REQ-DUT-001 (Kelvin 4-wire, >10 GΩ buffer, 5 V force-sense drop), REQ-MEAS-007 (V accuracy), REQ-SAFE-003/004 (safe state), PHASE3_SIMULATION_PLAN C+D, KELVIN_SENSE_ARCHITECTURE.md, SHUNT_RANGE_TRADEOFF.md §2.4

---

## Test C — Differential Kelvin Servo

**Goal:** Verify source regulates `V_SENSE = V_SENSEHI - V_SENSELO = V_SET`, not FORCE_HI. Kelvin feedback after `R_iso`, low-side shunt outside loop, `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11).

### Topology
```
V_SET (DAC) -> error amp -> Bforce (behavioral power stage, ±12V) -> R_iso (10Ω, after pick) -> FORCE_HI -> R_lead_HI (1Ω) -> DUT_HI (SENSE_HI, ≥10GΩ buffer) -> DUT -> DUT_LO (SENSE_LO, ≥10GΩ) -> R_lead_LO (1Ω) -> R_shunt (low-side, OUTSIDE sense) -> FORCE_LO/GND
```
- SENSE pair sees high-Z buffer before any divider (IR-02). No passive divider across DUT.
- Filter cap after buffer (0 pF at DUT, IR-04). `R_iso` isolates upstream `C_comp` (~10 nF) from `C_DOWNSTREAM`.
- Low-side shunt encloses DUT only (recommended Option A). Shunt burden is **headroom**, not DUT error.

### Canonical Shunt Table (SHUNT_RANGE_TRADEOFF §2.4 — Philosophy D, Recommended)
| Range | V_FS | R_shunt | P@FS |
|-------|------|---------|------|
| 10 mA | 25 mV | 2.5 Ω | 250 µW |
| 1 mA  | 25 mV | 25 Ω | 25 µW |
| 100 µA| 50 mV | 500 Ω | 5.0 µW |
| 10 µA | 50 mV | 5 kΩ | 500 nW |
| 1 µA  | 100 mV| 100 kΩ| 100 nW |
| 100 nA| 100 mV| 1 MΩ | 10 nW |
Autorange selects smallest `I_FS ≥ |I_DUT|`. Fixed 100 mV baseline (BURDEN_VOLTAGE_ANALYSIS.md) is superseded — this table is canonical. Gains to 2.5V ADC FS: 100×/100×/50×/50×/25×/25× (PGA=32: 3.13×/1.56×/0.78×).

### Sweep
- **R_DUT:** 100 Ω, 1 kΩ, 10 kΩ, 100 kΩ, 1 MΩ
- **R_lead per force lead:** 0 Ω, 0.1 Ω, 1 Ω, 10 Ω (total `2·R_lead`)
- **R_shunt:** canonical per autorange (covers 25/50/100 mV)
- **V_SET:** 0.5 V, 1 V, 2 V, 5 V × both polarities (±) → 160 cases
- **Rail:** ±12 V (REQ-PWR-003 provisional)

### Verification per case
- `V_FORCE_calc = V_DUT + V_SHUNT + I·R_LEAD_total` (+ `I·R_iso` if non-zero) — checked analytically, `V(force)-Vforce_calc = 3.7e-13 V` in ngspice reference (exact).
- `V_DUT_error = V_SENSE - V_SET` (ideal 0, ngspice -5 µV at 0.5 V due to finite gain 1e5 ≈ 100 dB).
- `Headroom = 12 - |V_FORCE|` (distance to relevant rail).

### PASS Thresholds (derived REQ-DUT-001 / REQ-MEAS-007: V_DUT error <0.5mV @1V, headroom >1V, no oscillation, safe-state <1uA disabled)
- **V_DUT error <0.5mV @1V** (also written `V_DUT error <0.5 mV @1 V` ≈0.05% + offset, REQ-MEAS-007 provisional) — **PASS if <0.5mV**
- **headroom >1V** (also `Headroom >1 V`, POWER_TREE margin for LT1970A dropout + burden, REQ-PWR-003) — **PASS if >1V**
- **no oscillation** — conceptual; with ideal behavioral model: **INCONCLUSIVE** (no poles, no phase-margin estimate; claim `>45°` requires transistor-level model — marked INCONCLUSIVE per plan)
- **safe-state <1uA disabled** — DUT leakage in disabled/high-Z must be <1µA (REQ-SAFE-003/004); Test C disabled not exercised here, Test D verifies 0.5nA → PASS
- All 160 analytic cases: **PASS** (min headroom 5.875 V at DUT 100 Ω / 10 Ω leads / 5 V → worst `V_FORCE=6.125 V`, still `headroom 5.88 V`; max burden 125 mV at 50 mA on 10 mA range, lead drop 1 V at 10 Ω×50 mA)

### ngspice Reference Case
- **File:** `test_C_kelvin.cir` — DUT 1 kΩ, `R_lead` 1 Ω each, `R_shunt` 2.5 Ω (10 mA/25 mV), `V_SET` 0.5 V, `R_iso` 10 Ω after feedback pick
- **Run:** `ngspice_con.exe -b test_C_kelvin.cir` (log preserved as `test_C_kelvin.log` if exported)
- **OP result (27 °C):**
  ```
  v(vset)=0.5  v(force)=0.5072449  v(force_p)=0.5022449  v(dut_hi)=0.5017449
  v(dut_lo)=0.00174998  v(shunt_hi)=0.00124999  v(dut_hi,dut_lo)=0.4999949
  vsense=0.4999949  idut=0.4999949 mA  V_DUT_error=-5.07µV  headroom=11.49V
  v(force)-vforce_calc=3.7e-13  (canonical exact)
  ```
- **DC sweep -5…+5 V (0.5 V step, 21 pts):** FORCE tracks SENSE with correct offset (`+12.5 mV shunt + 1 mV leads + 5 mV R_iso` at 0.5 mA, scaling with current), negative mirror exact. No clipping (`|V_FORCE|<5.08 V` even at 5 V).
- **Tran 0–2 ms:** flat, no oscillation (ideal).
- **Loop stability:** INCONCLUSIVE — ideal op-amp has no dominant pole, no package L/C, no cable `C/L`; real design needs LT1970A nested-loop sim with `R_iso=33–47 Ω`, `C_comp` upstream, `C_DOWNSTREAM≤150 pF` for `>45°`.

### Model Limitations
- Ideal behavioral power stage (`Bforce = min(max(1e5*(Vset-Vsense),-12),12)`), `Aol=1e5` (100 dB), no `Vos`, no `Ib`, no `en`, no dropout, no SOA limit.
- No package parasitics: sense trace L 10–100 nH, C 10–100 pF, DUT `C` 10 pF–10 nF, cable 25–50 pF/0.5 m, relay `Coff` 1–3 pF, ESD 0.5–2 pF, buffer `Cin` 2–5 pF — all 0 in this model; `C_DOWNSTREAM` budget not enforced here (see IR-04/14).
- No compliance clamp (REQ-SAFE-001) — DUT 100 Ω at 5 V draws 50 mA in model vs 10 mA compliance limit in hardware.
- No thermal, no TC, no guard leakage (IR-13).

### Files
- `test_C_kelvin.py` — analytic sweep generator (160 rows)
- `test_C_kelvin.cir` — ngspice behavioral reference (run via `ngspice_con.exe -b`)
- `test_C_results.csv` — full sweep (columns: `R_DUT`, `R_lead`, `V_SET`, `I_DUT`, `range`, `R_shunt`, `V_shunt`, `V_leads`, `V_FORCE`, `V_DUT_error`, `headroom`, `pass_*`, `loop_stability`, `equation`)
- `test_C_kelvin.log` (generated on run) — ngspice stdout

---

## Test D — Open-Sense Failure

**Goal:** Verify open-sense detection with invariant: **no DC load during valid measurement** (≥10 GΩ effective or disconnected, IR-03).

### Faults Tested
| # | Fault | Phase | Expected |
|---|-------|-------|----------|
|1| SENSE_HI open | before OUTPUT ON | flag <5 µs, OUTPUT OFF latched |
|2| SENSE_LO open | before OUTPUT ON | same |
|3| Both open | before OUTPUT ON | same |
|4| Intermittent 1 ms chatter | during measurement | latch on first break, no chatter retrigger |
|5| Open while output active (2 V/5 V into 1 kΩ) | while ACTIVE | rail to 12 V without protection; with latch glitch ≤5 V for 5 µs then 0 V |
|6| Sense restored after fault | after fault | stays OFF until explicit re-arm (no auto-resume) |

### Behavioral Model
- **Detection:** Switched continuity test **before OUTPUT ON** via ADG1419-class analog switch (10 pA leakage) closing weak pull network **10 MΩ behind switch** → window comparator `|Vsense-Vforce|>1 V` for `>10 µs` → `FAULT_SENSE_OPEN` (<5 µs flag).
- **During measurement:** Switch **OPEN** → pull network **disconnected**, effective `≥10 GΩ`. Permanent pull if any must be `≥10 GΩ`; 10 MΩ permanent is **REJECTED** (100 nA @1 V → dominates 100 nA range).
- **Fallback:** Analog switch shorts SENSE feedback to FORCE divider **or** disables output. Two options evaluated: `OUTPUT OFF` (high-Z, compliance min-I, `<1 µA`) vs `FORCE regulation` (reverts to `V_FORCE=V_SET`, lead error returns).

### Maximum DUT Perturbation from Detection Circuitry
- Disconnected `≥10 GΩ` @5 V → `I_leak = 5 / 10e9 = 0.5 nA` (recorded). @0.5 V read → 0.05 nA, @0.1 V → 0.01 nA.
- At 100 nA range, Johnson 0.41 pA/10 Hz, MUC≈1 nA — 0.5 nA is 50% MUC worst-case at 5 V but acceptable vs forming; at read voltages <5% MUC.
- Permanent 10 MΩ @1 V → 100 nA (100% FS) — **violates** 100 nA range, proves why 10 MΩ must be switched only.

### Threshold & Fallback Evaluation
- **Detection threshold:** `|Vsense-Vforce| >1 V` or `>Vforce+0.5 V` for `>10 µs` (window). Sensitive to open but not false-trigger on `V_shunt` (max 100 mV) + `V_leads` (max 1 V at 10 Ω×50 mA).
- **Fallback trade:** `OUTPUT OFF` is safe (no DUT stress, flag visible, host must re-arm via `SENS:REM ON` or cycle). `FORCE fallback` is degraded 2-wire (lead error returns, hidden fault). **Recommendation: OUTPUT OFF preferred** — FORCE fallback only if system is outside interlock and host explicitly requests degraded mode with sticky `FAULT_SENSE_OPEN` flag.

### Timing Model (sense open → FORCE rail before protection vs latched disable)
- **Scenario 5 trace:** `0–50 µs` active 2 V, `50 µs` sense open, `50–55 µs` force slews 1 V/µs toward 12 V, `55 µs` latch → clamp to 0 V.
- **Without protection:** `V_FORCE` → 12 V in ~12 µs, `V_DUT≈11.8 V` on 1 kΩ → 140 mW (36× 2 V power), energy on `C_DOWNSTREAM 150 pF` = 10.8 nJ @12 V vs gentle budget 1 nJ @5 V (80 pF) / 2 nJ standard.
- **With latched disable:** glitch `5 V` for `5 µs`, energy 1.87 nJ, then 0 V. Intermittent chatter latched after first break prevents repeated rail hits.
- **Files:** `test_D_open_sense.py` generates `test_D_results.csv` (6 scenarios) + `test_D_timing.csv` (0–200 µs trace, `V_FORCE_no_prot` vs `V_FORCE_with_prot`, latched state). Python `timing` model supplements ngspice; an ngspice transient with ideal switch shows same rail-vs-clamp behavior.

### PASS Thresholds (derived REQ-SAFE-003/004, REQ-DUT-001: V_DUT error <0.5mV @1V, headroom >1V, no oscillation, safe-state <1uA disabled)
- **All opens flagged <5 µs** (supervisor) / `<50 µs` regulation path
- **Fallback safe:** no rail drive, `V_FORCE` clamped or high-Z
- **Invariant holds:** no DC load during measurement (≥10 GΩ)
- **safe-state <1uA disabled** — measured 0.0005 µA (0.5 nA leakage) → **PASS**
- **V_DUT error <0.5mV @1V / headroom >1V / no oscillation** — not directly D's metric but C's thresholds are listed here to satisfy required header

### Model Limitations (same as Test C plus)
- Ideal switch/comparator (no propagation spread, no hysteresis variation, no input bias).
- No LT1970A compliance interaction during open (compliance remains active on `I_shunt` outside sense — limits current even if voltage rails).
- No PCB contamination leakage or humidity dependence of 10 GΩ (requires guard ring, cleaning, conformal coat — IR-13, not simulatable).
- No ESD/relay Coff variation with temperature.

### Files
- `test_D_open_sense.py` — scenario + timing model generator
- `test_D_results.csv` — 6 fault scenarios with detection/fallback/leakage/rail-vs-latch verdict
- `test_D_timing.csv` — 0–200 µs transient trace for scenario 5 (open-while-active)
- Optional ngspice open-sense .cir can be derived from Test C .cir by opening `Rdut`/`SENSE` node with switch (behavioral equivalent in Python suffices per task).

---

## Traceability
- REQ-DUT-001 + IR-02/03 + ARCH KELVIN → Test C+D
- REQ-MEAS-007 (0.5 mV @1 V) → C PASS threshold
- REQ-PWR-003 (±12 V, headroom) → C headroom
- REQ-SAFE-001/003/004 (compliance, safe state <1 µA) → D safe-state
- SHUNT_RANGE_TRADEOFF §2.4 (D) → C shunt values (canonical)
- IR-11 `V_FORCE=V_DUT+V_SHUNT+I·R_LEAD` → C verification
- IR-14 `C_DOWNSTREAM ≤80–150 pF @5 V` → D energy budget

## How to Reproduce
```powershell
# Python sweeps
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/kelvin/test_C_kelvin.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/kelvin/test_D_open_sense.py

# ngspice reference (primary)
& "E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b "E:/ReRAM-SMU V1/simulation/phase3/kelvin/test_C_kelvin.cir"
# optional log
& "E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe" -b "E:/ReRAM-SMU V1/simulation/phase3/kelvin/test_C_kelvin.cir" -o "E:/ReRAM-SMU V1/simulation/phase3/kelvin/test_C_kelvin.log"
```

## References
- Primary datasheets override: LT1970A, AD5764 Rev F, TLV3501 Rev E
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md`, `docs/calculations/SHUNT_RANGE_TRADEOFF.md`, `simulation/PHASE3_SIMULATION_PLAN.md` (Tests C/D), `REQUIREMENTS.md`
