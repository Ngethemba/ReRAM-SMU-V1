# Gate 3 — Capacitance & Energy (Tests F+J) — Executive Summary

**Date:** 2026-08-24  
**Gate:** 3 (F: DUT-node C, J: Upstream/Downstream)  
**Spec:** `simulation/PHASE3_SIMULATION_PLAN.md` Tests F/J (IR-14, CAUTION 1)  
**Artifacts:** `simulation/phase3/compliance/` (F+J) → `simulation/results/phase3/gate3_capacitance.md` (this file)

## Result — PASS

| Test | Required header verdict | Evidence | Status |
|---|---|---|---|
| **F — SENSE capacitance** | **PASS: C_DOWNSTREAM quantified vs recipe** | `test_F_results.csv` 36 rows, `E=0.5*C*V²` per 9×4 sweep; per-V `C_max` table; ngspice dual anchors 100 pF@5V 1.25 nJ / 1nF@5V 12.5 nJ | **PASS** |
| **J — Upstream vs downstream** | **Upstream stable with R_iso 33-47Ω preserving >45° PM if model permits** | `test_J_results.csv` 60 rows; matched 4.7 nF/47R & 10 nF tradeoff transients; `fp=1/(2πR_isoC)` analysis; tradeoff documented | **PASS (ideal-model conditional)** |

Both tests satisfy their gate headers with ideal-switch model; real PM needs vendor LT1970A loop model before PCB.

---

## What was built

- **`test_F_capacitance.py`** — sweep `C_DOWNSTREAM` 5/10/25/50/80/100/150/500pF/1nF × 0.5/1/2/5 V; classifies per `gentle ≤1 nJ / standard ≤2 nJ / forming ≤10 nJ` **per V** (not universal). Writes `test_F_results.csv`.
- **`test_F_capacitance.cir`** — ngspice transient with four branches: 100 pF and 1 nF each with/without 47 R R_iso (IC=5 V → 1 k filament, τ 100 ns–1.047 µs). Verifies `1.25 nJ` and `12.5 nJ` anchors; shows upstream `≈95.5%` to DUT vs downstream `100%`.
- **`test_J_upstream_downstream.py`** — sweep `C_comp` 1/4.7/10 nF × `R_iso` 10/22/33/47/100 Ω × `V` 5/2 V × placement before/after R_iso (60 combos); computes `E_stored/delivered`, `Ipeak`, `τ`, `fp`, `headroom`, stability heuristic. Writes `test_J_results.csv`.
- **`test_J_upstream_downstream.cir`** — ≥2 matched ngspice transients (4.7 nF/47R upstream vs downstream same C/snap + 10 nF/10R vs 100R tradeoff), behavioral `Rdut` 1M→1k in 1 µs at 5 µs. Verifies location effect.
- **`README_FJ.md`** — full gate dossier with required PASS headers, topology, tables, ngspice logs, and model limitations.

## Numbers that decide hardware

**Per-voltage downstream budget (same as `COMPLIANCE_ENERGY_ANALYSIS.md`):**
`C_max = 2·E_budget / V²` → gentle/standard 80/160 pF @5 V, **500/1000 pF @2 V**, forming 800/5000 pF. Form at ≤2 V where possible.

**Anchors:** 80 pF @5 V = 1 nJ limit; 100 pF @5 V = **1.25 nJ FAIL gentle**; 500 pF @5 V = 6.25 nJ; **1 nF @5 V = 12.5 nJ FAIL all @5 V** but at 2 V: 1 nF = 2.0 nJ PASS standard.

**Upstream isolation:** `C_UPSTREAM` 4.7–10 nF before `R_iso` not penalized as dump; downstream same value catastrophic (125 nJ @5 V for 10 nF). **Location is topology choice, not just value.**

**R_iso tradeoff (ideal, `V=5 V`, `I_max=10 mA`, `fc≈1 MHz`):**
Too low 10R → headroom 0.1 V, `I_short` 500 mA, `fp` 1.59 MHz (10 nF) still near crossover, weak isolation. Too high 100R → headroom 1 V (20% rail), `fp` 159 kHz in BW, `5τ` up to 5 ms, regulation error. **Sweet spot 33–47R** → 0.33–0.47 V headroom, `fp` 3.39 MHz for 1 nF (beyond crossover), 339–482 kHz for 10 nF manageable with selectable lead `Cf` → **>45° PM in ideal model**.

**Ipeak (1 k LRS, 5 V):** downstream 5.00 mA; upstream 4.78 mA at 47R (difference <5% — R_iso alone does not remove energy for 1 k filament, it limits *short* and isolates compensation).

## V1 provisioning rule

- Keep `C_comp` upstream, feedback after `R_iso` (Kelvin).
- Downstream budget ≤150 pF total (PCB ≈10–20 pF + 0.5 m low-C cable ≤25 pF + DUT ≤30 pF) → **≈75–100 pF → 0.94–1.25 nJ @5 V** within standard.
- `R_iso` **33–47 Ω** (thin-film, non-inductive) + selectable `Cf` (lead-comp) + High-C mode bit (slowed loop).
- Cable length limit **0.5 m** low-C coax for gentle compliance; warn in SW if longer.
- Slew-limited DAC ramp mandatory (0.1–1 V/ms) to keep `C·dV/dt` below compliance.

## How to reproduce

```bash
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/compliance/test_F_capacitance.py
E:/ReRAM-SMU\ V1/.venv/Scripts/python.exe simulation/phase3/compliance/test_J_upstream_downstream.py
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_F_capacitance.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/compliance/test_J_upstream_downstream.cir
```

ngspice-47 results logged in `README_FJ.md` (§1.4, §2.4); CSVs are the machine-readable gate record.

## Limitations — not a layout sign-off

Ideal switches/sources, no ESL/ESR, no package `L`, no sense-lead `C=50 pF/m` in this ideal RC, single-pole PM heuristic. Full LT1970A vendor loop (with `Cf`, lead `L`/`C`, sense pole) to be rerun in LTspice before PCB; guard/probe and leakage (Tests E/M) are separate gates.

---

*Gate 3 F+J: E is `½CV²`; budget is per-recipe per-`V`; topology defeats value alone — `C_DOWNSTREAM` is the only dump, `C_UPSTREAM` is free with `R_iso 33–47 Ω` and `>45° PM` conditional.*
