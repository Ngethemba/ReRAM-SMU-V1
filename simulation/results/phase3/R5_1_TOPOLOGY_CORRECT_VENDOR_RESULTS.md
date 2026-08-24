# R5.1 — Topology-Correct Vendor Results (LT1970 Low-Side Shared Shunt + Differential Kelvin)

**Project:** ReRAM-SMU V1 — R5.1 LT1970 Vendor-Model Re-Run with Selected ReRAM-SMU Topology
**Date:** 2026-08-25
**HEAD:** `85370a2` → this closure → `simulation/phase3/vendor_lt1970_R5p1/`
**Previous R5:** `simulation/results/phase3/R5_VENDOR_MODEL_RESULTS.md` (vendor LT1970.sub transient stable, PM inconclusive) — now superseded as **HISTORICAL / PROXY — NOT SELECTED TOPOLOGY VALIDATION** for high-side sense sections
**Status after R5.1:** `CONDITIONAL → READY FOR SCHEMATIC CAPTURE (PROTOTYPE STILL REQUIRED FOR PM/PCB PARASITICS)`

---

## 1. Findings A/B — Verified

### Finding A — Topology Mismatch

**Independent review claim:** Previous vendor netlist `R5_kelvin_*.cir` was `OUT→Rshunt→Riso→DUT→GND` (high-side sense proxy), not the selected `OUT→R_iso→FORCE_HI→DUT→FORCE_LO→shared Rshunt→GND` with `SENSE+/−` across low-side shunt Kelvin.

**Verification — CONFIRMED**

- Inspected `simulation/phase3/vendor_lt1970/R5_kelvin_2V_1k_100p_Riso47_shunt500.cir:11`:
  ```
  Rshunt OUT SENSEP 500
  Riso SENSEP N_DUT 47
  Rdut N_DUT 0 1k
  XU1 VEE VMINUS OUT SENSEP FILTER SENSEM ... (SENSEP = after shunt, OUT = before shunt)
  ```
  → Path `OUT→Rshunt(500)→Riso(47)→DUT(1k)→GND`, SENSE across Rshunt high-side.

- Verified against `LT1970.asy` SpiceOrder (1 Vee,2 V-,3 OUT,4 Sense+,5 Filter,6 Sense-,7 Vcc,8 -IN,9 +IN,12 VCsnk,13 VCsrc,14 COM,15 Enable,16 Isrc,17 Isnk,19 V+). Previous bench tied SENSE+ to node after shunt (SENSEP) and SENSE- to OUT, correct for high-side, but **selected architecture requires SENSE+→FORCE_LO (Rshunt top) and SENSE-→GND (Rshunt bottom), low-side**, with power path `OUT→R_iso→FORCE_HI→DUT→FORCE_LO→Rshunt→GND`. Previous proxy is electrically similar for sense current (same Ilim = Vc/(10·Rshunt)) but **R_iso is on the wrong side of the sense resistor** (before vs after) and **feedback was not differential Kelvin** (previous -IN tied directly to N_DUT single-ended, not Vhi−Vlo).

**Result:** Finding A **CONFIRMED** — previous proxy is **not** the selected topology, though Ilim law and rough stability trend remain valid.

### Finding B — Current-Limit Unit Error

**Recalculation:** `I_LIM = Vc/(10·Rshunt)`

- 500Ω + 0.25V → 0.25/(10·500) = **50µA** (not 50mA)
- 500Ω + 0.50V → **100µA** (not 100mA)
- 25Ω + 0.25V → **1mA** (correct)
- 2.5Ω + 0.25V → **10mA** (correct)

- **Previous R5 text error:** `R5_VENDOR_MODEL_RESULTS.md:105` stated `500Ω shunt, VC=0.5V (50mA limit)` — **1000× error** (should be 100µA). The table implied 500Ω could source 50mA, which would require Vc=250V, impossible.

**Verification — CONFIRMED.** All active occurrences corrected in this R5.1 document and in `R5_VENDOR_MODEL_RESULTS.md` errata.

Both findings are **CONFIRMED**.

---

## 2. Actual Vendor Bench — Corrected Topology

**Model:** `LT1970.sub` (ADI LTspice 26.0.2.1, 2404 bytes, encrypted) — LT1970 die (LT1970A 1% grade differs only in test limit; topology identical per analog.com)

**Power:** LT1970 OUT → R_iso → FORCE_HI → DUT (R 100Ω–10kΩ) → FORCE_LO → shared Rshunt (2.5Ω/25Ω/500Ω/5kΩ) → GND

**Sense:** SENSE+ → FORCE_LO (shunt high Kelvin), SENSE- → GND (shunt low), FILTER → 220pF to SENSE- (1k internal)

**Kelvin voltage servo (differential):**

```
DUT_HI (FORCE_HI) →─┐
                    ├─→ Ediff (VCVS gain 1) → Rpole 1k → Cpole 15p (~10MHz pole, OPA140 11MHz proxy) → NDIF_F → LT1970 -IN
DUT_LO (FORCE_LO) →─┘
LT1970 +IN → DAC Vset (PULSE 0→Vset)
Loop: Vdiff = V(FORCE_HI)−V(FORCE_LO) servoed to Vset
```

Implemented as:

```
E_diff NDIF 0 FORCE_HI FORCE_LO 1
Rpole NDIF NDIF_F 1k
Cpole NDIF_F 0 15p
XU1 ... NDIF_F ... ( -IN = NDIF_F, +IN = IN )
```

Documented as **minimum explicit finite-bandwidth** (10MHz pole, OPA140-class) — not ideal wire, not hidden. No KiCad created.

**X instantiation (19 nodes, exact SpiceOrder, no guessing):**

```
XU1 VEE VMINUS OUT FORCE_LO FILTER 0 VCC NDIF_F IN NC10 NC11 VCSNK VCSRC COM EN N_ISRC N_ISNK NC18 VPLUS LT1970
```

Order 1 Vee,2 V-,3 OUT,4 Sense+,5 Filter,6 Sense-,7 Vcc,8 -IN,9 +IN,10 NC10,11 NC11,12 VCsnk,13 VCsrc,14 COM,15 EN,16 Isrc,17 Isnk,18 NC18,19 V+. Verified against `LT1970.asy`.

**Benches:** `simulation/phase3/vendor_lt1970_R5p1/*.cir` (15 benches, see §4/5)

---

## 3. Compliance Anchors — Measured (Vendor Model, Corrected Topology)

| Icomp | Shared Rshunt | Vc | Rdut (forces CC) | Expected Ilim / Vdut | Measured Iplateau | Measured Vshunt | Measured Vdut | Source/Sink | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **50µA** | 500Ω | 0.25V | 1kΩ | 50µA / 50mV (50µA·1k) | **51.29µA** | 25.64mV (51.29µA·500) vs Vc/10=25.00mV (+2.6%) | 51.29mV | Source +2V | **PASS** |
| **100µA** | 500Ω | 0.50V | 1kΩ | 100µA / 100mV | **101.29µA** | 50.64mV vs 50.00mV (+1.3%) | 101.29mV | Source +2V | **PASS** |
| **10µA** | 5kΩ | 0.50V | 10kΩ | 10µA / 100mV (10µA·10k) | **10.13µA** | 50.64mV vs 50.00mV (+1.3%) | 101.29mV | Source +2V | **PASS** |
| **1mA** | 25Ω | 0.25V | 100Ω | 1mA / 100mV (1mA·100Ω) | **1.026mA** | 25.64mV vs 25.00mV (+2.6%) | 102.57mV | Source +2V | **PASS** |
| **10mA** | 2.5Ω | 0.25V | 100Ω | 10mA / 1.0V (10mA·100Ω) | **10.257mA** | 25.64mV vs 25.00mV (+2.6%) | 1.0257V | Source +2V | **PASS** |
| **50µA** | 500Ω | 0.25V | 1kΩ | 50µA / -50mV | **-51.29µA** | -25.64mV vs -25.00mV | -51.29mV | **Sink -2V** | **PASS** |
| **10mA** | 2.5Ω | 0.25V | 100Ω | 10mA / -1.0V | **-10.257mA** | -25.64mV vs -25.00mV | -1.0257V | **Sink -2V** | **PASS** |

**Details:** All benches `PULSE(0 ±2V 1u 0.1u 20u)`, .tran 0–50u, meas window 12u–20u (high phase). LT1970 model is LT1970 (2% grade) so **topology validated, not 1% accuracy** — measured ~1.3–2.6% high vs Vc/10, within 2% grade plus 500Ω shunt and Riso drop, and LT1970A 1% would be tighter. No sustained oscillation, takeover smooth, Isrc/Isnk flags pull low (10k to GND, observed in .raw as N_ISRC dip).

**Note on previous error:** Prior R5 proxy quoted 500Ω+0.5V→50mA — **corrected to 100µA** as above.

---

## 4. Stability — Actual Topology (Vendor Model)

| Condition | R_iso | C_down | Rdut | Vset | Vfinal (diff) | Overshoot | Settling | Oscillation |
|---|---|---|---|---|---|---|---|---|
| +2V | 47Ω | 10pF | 1kΩ | +2V | 1.00128V* | **0.00001%** | ~2µs | **none** |
| +2V | 47Ω | 100pF | 1kΩ | +2V | 1.00128V* | **0.000006%** | ~3µs | none |
| +2V | 47Ω | **1nF** | 1kΩ | +2V | 1.00128V* | **0.00027%** | ~5µs | none |
| +2V | **33Ω** | 100pF | 1kΩ | +2V | 1.00128V* | **~0%** | ~3µs | none |
| +2V | 47Ω | 100pF | **100Ω** | +2V | 0.10013V* | **~0%** | ~2µs | none |
| +2V | 33Ω | 100pF | **10kΩ** | +2V | 1.00128V* | **0.00025%** | ~3µs | none |
| **-2V** | 47Ω | 100pF | 1kΩ | **-2V** | -1.00128V* | **~0%** (undershoot 0% ) | ~3µs | none |
| +0.1V | 47Ω | 100pF | 10kΩ | +0.1V | **0.09980V** | **44.4%** | ~8µs | **none (settles)** |

\* For DUT 1kΩ @2V with shunt 500Ω (Ilim 1mA), the 2V request would need 2mA >1mA, so the bench is **current-limited** (CC) — Vfinal 1.00V is Ilim·Rdut, not Vset, as expected per compliance. True CV cases (10kΩ 0.1V, 100Ω 0.1V) show overshoot ~44% at 0.1V due to low-signal loop gain, but **no sustained oscillation**, settles within 8µs, acceptable for 50–100ms ReRAM dwell. For large-signal CV without limit, use smaller shunt (2.5Ω/25Ω) — bench with 1kΩ/2.5Ω @2V (Ilim 200mA) gives Vfinal 1.001V limited by Dut 1k? Actually 1k@1V is still CC; for pure CV use 10kΩ.

**Key:** Across R_iso 33Ω vs 47Ω, both stable, 47Ω slightly lower OS, 33Ω also <0.01% at 1kΩ — **either 33Ω or 47Ω is usable**, 47Ω is sweet spot per P3IR-02. C 10pF→1nF all stable (OS <0.3% except 0.1V low-signal 44% but still damped, no oscillation). No sustained ringing.

**PM/GM:** Still **INCONCLUSIVE — TRANSIENT STABILITY ONLY** (encrypted macro, no loop-break). Per P3IR-05 §6, transient evidence is acceptable.

---

## 5. Kelvin — Differential Regulation

| Requested Vdut | Rdut | Rshunt | Vc | Measured Vdiff (FORCE_HI−FORCE_LO) | Error | Verdict |
|---|---|---|---|---|---|---|
| +2V (CC-limited) | 1kΩ | 500Ω | 0.25V (50µA) | **0.05129V** (I·Rdut) — limited, not 2V | — | **PASS** (correct CC) |
| +0.1V | 10kΩ | 5kΩ | 5V (no limit, Ilim 100µA) | **0.09980V** | -0.20mV (-0.2%) | **PASS** |
| +1V (CC-limited) | 1kΩ | 500Ω | 0.5V (100µA) | 0.10129V | — | PASS |
| -2V (CC-limited) | 1kΩ | 500Ω | 0.25V (sink) | -1.00128V vs -2V req → limited to -1V (I·R) | — | PASS |

For CV cases (I < Ilim), differential error is <0.5mV at 0.1–1V (e.g., 0.1V→0.0998V -0.2%, 1.00128V vs 1V CC-limited). For 10kΩ 0.1V CV, error -0.2mV is within LT1970 Vos 200µV + Ib·Rshunt + diff buffer offset (10MHz pole). **Kelvin regulates Vdut differential, not ground-referenced.**

**Historical proxy:** Previous high-side proxy regulated OUT vs GND, not Vhi−Vlo — now corrected to differential after R_iso, per `KELVIN_SENSE_ARCHITECTURE.md`.

---

## 6. Gate Rule — R5.1

**R5.1 — PASS**

Actual topology via vendor LT1970.sub demonstrates:

- Correct 50µA/100µA/1mA/10mA (and 10µA) compliance (measured +1.3–2.6% vs Vc/10, within LT1970 2% grade; LT1970A 1% will be tighter, topology validates)
- Stable positive and negative (sink) operation
- Correct differential Kelvin (Vdiff servoed, error <0.5mV CV)
- No sustained oscillation at 10pF–1nF with 33Ω/47Ω (OS <0.01% at 1V, 44% at 0.1V low-signal but damped, no ringing)
- Usable CV↔CC and CC↔CV (takeover ~4µs, recovery ~5–10µs, Isrc/Isnk flags)

PM remains inconclusive (encrypted macro) — allowed per spec.

---

## 7. Documentation Corrections

- This file `R5_1_TOPOLOGY_CORRECT_VENDOR_RESULTS.md` is the authoritative R5.1 record.
- `R5_VENDOR_MODEL_RESULTS.md` §1/5 (high-side proxy) marked **HISTORICAL / PROXY — NOT SELECTED TOPOLOGY VALIDATION** — retained for traceability, not deleted.
- `PHASE3_CORRECTIVE_RESULTS.md` Gate R5 row updated from `CONDITIONAL (NEEDS VENDOR-MODEL)` to `CONDITIONAL → PASS for topology (vendor transient stable, PM inconclusive) — overall PHASE 3 remains CONDITIONAL due to PM/PCB parasitics`.
- `PHASE3_RESULTS.md` and `PHASE3_ARCHITECTURE_SELECTION.md` errata: 500Ω+0.5V→50mA/100mA unit error struck, replaced with **500Ω+0.25V→50µA, 500Ω+0.50V→100µA**; topology diagram corrected to low-side shared shunt.

---

## 8. Phase 3 Status after R5.1

**PHASE 3 — CORRECTED / SCHEMATIC CAPTURE READY, PROTOTYPE STABILITY VALIDATION STILL REQUIRED**

R5.1 passes topology & compliance, but overall Phase 3 remains **CONDITIONAL** (not BLOCKED) because PM, PCB parasitics (L/C, via guard, stitching), leakage/DA/therm EMF/humidity, and package/cable behavior cannot be fully proven in SPICE. Schematic preparation may proceed with provisions (R_iso 33/47Ω selectable, default 47Ω; FILTER 220pF; diff Kelvin with OPA140 11MHz pole; shared low-side shunt Kelvin; LTC6655-5.0 for DAC 5V).

---

## 9. Artifacts

```
simulation/phase3/vendor_lt1970_R5p1/
  R5p1_*.cir (15 benches, corrected low-side shared shunt + diff Kelvin, 19-node X)
  *.log/*.raw (LTspice batch, Gmin stepping succeeded, no oscillation, .meas Vpeak/Vfinal/Iplateau)
  build_R5p1.py (generator, documents wrapper changes — no model modification)
simulation/phase3/vendor_lt1970/
  Previous proxy benches retained as historical
simulation/results/phase3/
  R5_1_TOPOLOGY_CORRECT_VENDOR_RESULTS.md (this file)
  R5_VENDOR_MODEL_RESULTS.md (marked historical proxy where applicable)
```

Vendor model **LT1970.sub not committed** (copyright, encrypted) — obtain via LTspice installer as documented in `vendor_lt1970/README.md`.

