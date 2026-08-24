# Compliance Stored-Energy Analysis — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 (Agent C)
**Date:** 2026-08-24
**Status:** `ANALYSIS / PROVISIONAL` — informs DEC on output capacitance and discharge topology; no component promoted.
**Requirements:** REQ-SAFE-001 (hardware compliance), REQ-SRC-001 (±5 V), REQ-SRC-006 (±10 mA), CAUTION 1 (stored-energy overshoot), CAUTION 3 (per-segment compliance)
**Predecessors:** `docs/research/COMPLIANCE_RESEARCH.md`, `docs/research/RERAM_MEASUREMENT_REQUIREMENTS.md` §3.1–3.2, `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md`
**Rule:** ENGINEERING_RULES.md §3 — show formula, inputs with units, steps, result, tolerance. This file *is* the recalculation.

---

## 0. Why Energy Matters More Than Current Alone

ReRAM filament formation is a **positive-feedback, sub-microsecond snap** from ~MΩ→kΩ (see RERAM §3.2: SPA 4.5 µs/14 mA overshoot vs transistor 110 ns/1.5 mA vs CLA 500 ps/overshoot-free). The SMU's servo can only clamp what it *sees*; charge already stored on capacitance **between the servo's sense point and the DUT** will dump through the filament **before any loop can react**, no matter how fast the comparator is.

```
E_stored = ½ C_total V²          (J)

C_total = C_comp + C_cable + C_DUT + C_pcb + C_relay(Coff)
I_dump(t) ≈ V/R(t) · exp(-t/RC),   R(t) = R_iso + R_DUT(t) + ESR
Q_dump = C_total · V
```

Peak current is visible on a scope; **energy is what grows the filament** (Joule heating ∝ ∫I²R dt). Two limiters with the same 4 µs flag timing can differ 100× in delivered energy if one has 10 nF on the DUT node and the other has 50 pF. This is CAUTION 1.

A polymer PTC / polyfuse / poly-switch is **not** an alternative here: its trip time is **10 ms–1 s** (ABB TB82: PTC latch, time-delay-fuse-like), resistance 0.2–5 Ω when cold, >100 Ω when tripped, and it *latches until power cycle*. It protects a 24 V distribution rail against a shorted board, not a 100 µA filament against a 125 nJ dump in 100 ns. It must not be placed in series with the DUT for compliance.

---

## 1. Formula and Method

```
E = 0.5 · C · V²

V in volts, C in farads, E in joules (1 nJ = 1e-9 J, 1 pJ = 1e-12 J)
Q = C · V   (coulombs)
I_peak (resistive dump into R_LRS) ≈ V / (R_iso + R_LRS)   for t=0⁺
τ = (R_iso + R_LRS) · C   (first-order, R_LRS may be 1–10 kΩ during snap)
```

Reproduced with Python (commit alongside this file if promoted):

```python
def E_J(C_F, V): return 0.5*C_F*V*V
for C in [10e-12, 47e-12, 100e-12, 470e-12, 1e-9, 2.2e-9, 10e-9]:
    for V in [5.0, 2.0, 1.0, 0.5]:
        print(f"C={C*1e12:.0f} pF V={V:.1f} -> E={E_J(C,V)*1e9:.3f} nJ Q={C*V*1e9:.2f} nC")
```

All tables below are direct output of that one-liner; no hidden spreadsheet.

---


## 1.5 Upstream vs Downstream Capacitance Distinction (IR-14 canonical)

> **Canonical terminology (IR-14):** All synthesis rows stating "low output C ≤10 nF" are clarified as **C_UPSTREAM ≤10 nF before R_iso; C_DOWNSTREAM ≤80–150 pF after R_iso (recipe-dependent)**.

| Term | Definition | Location vs R_iso | Counts toward E = ½C·V² dump? | Typical V1 |
|---|---|---|---|---|
| **C_UPSTREAM** | Capacitance isolated from DUT by R_iso / servo (compensation C before R_iso, e.g., 4.7–10 nF) | **Before** R_iso | **No** — not directly dumpable into filament; absorbed via R_iso + loop | 4.7–10 nF (acceptable) |
| **C_DOWNSTREAM** | Capacitance that can dump directly into DUT during switching (post-R_iso: connector+trace+relay+Cable+DUT+ESD before isolation) | **After** R_iso | **Yes** — only this counts toward filament energy | ≤80–150 pF target (see budget table below) |

**C_DOWNSTREAM budget table per recipe (IR-14):**

| Recipe | E_budget | C_max @5 V | C_max @2 V | C_max @1 V | V1 guidance |
|---|---|---|---|---|---|
| Gentle multilevel (100 µA compliance, ≤2 V typical) | 1 nJ | **80 pF** | **500 pF** | 2.0 nF | Form at ≤2–3 V where possible |
| Standard SET (100 µA–1 mA, ≤2 V) | 2 nJ | **160 pF** | **1.0 nF** | 4.0 nF | Standard window |
| Forming / high-Icc (5–10 mA, ≤5 V) | 10 nJ | **800 pF** | **5.0 nF** | 20 nF | Relaxed but still prohibits 10 nF on DUT node |

*1 nJ is not a universal law — budgets are engineering constraints per test recipe / DUT.*

**Clarification:** 10 nF compensation is **not penalized** as DUT-dump; it is C_UPSTREAM. Only C_DOWNSTREAM is limited to 80–150 pF; focus downstream budget on cable/DUT fixture length (0.5 m limit, low-C coax).

## 2. Representative Capacitances (What Actually Exists on a V1 Board)

| Contributor | Typical value | Source / note | Where it sits relative to compliance sense |
|---|---|---|---|
| **Output compensation C** (power-amp local) | **1–10 nF** (LT1970-class compensation + Miller + local decoupling effective at output) | LT1970A GN=3.6 MHz, phase-margin cap on output; many reference designs add 1–4.7 nF to ground for stability. If placed **directly on FORCE_HI**, it is *between sense and DUT*. | **Before isolation R** if compensated correctly; **after** if laid out as DUT-node capacitor → worst case. |
| **PCB trace + relay Coff + connector** | **5–30 pF** | FR-4 50 Ω microstrip ~1 pF/cm; reed relay Coff 1–3 pF (Coto), signal relay 2–5 pF; BNC/banana 2–10 pF. Sum ≈10–30 pF. | After isolation R, before DUT. |
| **Cable** | **~100 pF/m** coax/BNC; **~50–80 pF/m** twisted/shielded pair; **~30 pF/m** low-C triax inner | Standard RG174/178 ≈100 pF/m; Keithley triax low-C ≈65 pF/m. | After isolation R, directly in parallel with DUT. |
| **Kelvin sense leads** | **~50–100 pF/m** per lead, but high-Z (GΩ input) — small AC contribution; DC burden negligible | Shielded sense pair. Its C adds a pole in the sense feedback path → stability, not energy. | In feedback, not DUT node. |
| **DUT + pad + probe** | **10 pF** (tiny pad, short wire) to **1 nF** (large crossbar, on-wafer array, decoupling on DUT board) | 100 µm×100 µm MIM + pad ≈0.5–5 pF; 1 mm² filament array + package can be 100 pF–1 nF. | Directly on DUT, always in parallel. |

> **Design rule:** Energy that the compliance loop **cannot** intercept = capacitance **downstream of the sense resistor / shunt** and **downstream of the isolation resistor** (if present). Capacitance upstream of Rsense or upstream of R_iso can be managed by the loop/isolation.

---

## 3. Energy Tables — E = ½CV²

### 3.1 At V = 5 V (worst-case forming / ±5 V rail, REQ-SRC-001 edge)

V² = 25, factor 12.5. E(J) = 12.5·C(F).

| C | E @ 5 V | Q @ 5 V | Context |
|---|---|---|---|
| **10 pF** | **0.125 nJ** = 125 pJ | 50 pC | Tiny pad only — ideal budget |
| **47 pF** | **0.588 nJ** | 235 pC | PCB + short lead, no cable |
| **100 pF** | **1.25 nJ** | 500 pC | 1 m cable, or DUT 100 pF |
| **470 pF** | **5.88 nJ** | 2.35 nC | 4.7 m cable or 470 pF decoupling mistakenly on DUT node |
| **1 nF** | **12.5 nJ** | 5 nC | Large DUT / array + 1 m cable |
| **2.2 nF** | **27.5 nJ** | 11 nC | Output compensation left on DUT node (bad) |
| **10 nF** | **125 nJ** | 50 nC | Classic output comp capacitor on DUT node — **catastrophic** for ReRAM |

### 3.2 At V = 2 V (primary ReRAM window, REQ-SRC-002 typical SET/RESET)

V² = 4, factor 2. E = 2·C.

| C | E @ 2 V | Q @ 2 V |
|---|---|---|
| 10 pF | 20 pJ | 20 pC |
| 47 pF | 94 pJ | 94 pC |
| 100 pF | 0.20 nJ | 200 pC |
| 470 pF | 0.94 nJ | 940 pC |
| 1 nF | 2.0 nJ | 2 nC |
| 2.2 nF | 4.4 nJ | 4.4 nC |
| 10 nF | 20 nJ | 20 nC |

### 3.3 At V = 1.0 V (typical read / low-SET, ~1 V forming median)

Factor 0.5. E = 0.5·C.

| C | E @ 1 V |
|---|---|
| 10 pF | 5.0 pJ |
| 47 pF | 23.5 pJ |
| 100 pF | 50 pJ |
| 470 pF | 235 pJ |
| 1 nF | 0.50 nJ |
| 2.2 nF | 1.10 nJ |
| 10 nF | 5.0 nJ |

### 3.4 At V = 0.5 V (read bias — UC-3, non-perturbing)

Factor 0.125. E =0.125·C.

| C | E @ 0.5 V |
|---|---|
| 100 pF | 12.5 pJ |
| 1 nF | 125 pJ |
| 10 nF | 1.25 nJ |

**Reading guide:** At 5 V, **every 100 pF costs 1.25 nJ**. A seemingly innocent 10 nF output capacitor holds **100×** the energy of a 1 m coax.

---

## 4. What Is "Safe" for a ReRAM Filament?

Literature does not quote a single universal safe energy — it depends on stack, area, and whether multilevel control is required — but all sources agree on scale and on the harm of excess:

| Observation (from RERAM §3.2 + NIST/IOPscience) | Implication |
|---|---|
| Ideal CLA: **overshoot-free at 20 µA within 500 ps**, ON/OFF >10⁴ vs SPA 10²; Ireset <200 µA | Budget at 100 µA compliance is **sub-nJ** to keep ON/OFF variability low |
| Kinoshita SPA: Icc=0.2 mA → 14 mA/4.5 µs overflow → Ireset 10 mA vs transistor 1.5 mA/110 ns → 0.5 mA | Excess of **~10× in current, ~40× in time** → ~400× energy → filament thickened uncontrollably |
| NIST "Analysis and Control of RRAM Overshoot Current": peak is linked to **parasitic C**; larger C = larger peak, even with same limiter setting | Confirms E=½CV² is the correct control variable, not just comparator speed. Two systems with identical 1 µs limit but 50 pF vs 500 pF will produce 10× different filaments. |
| Filament volume ~ (5 nm)³ → atom count ~10³–10⁴; formation enthalpy order **pJ–nJ** per filament | Delivering **10–100 nJ** is 10–1000× what is thermodynamically required → thermal damage, electrode cratering (SEM in IOP 10.1088/0022-3727/45/39/395101: "10× expected current → electrode damage") |

**Working V1 budgets (provisional, for architecture sizing — must be validated on actual stack):**

| Scenario | Compliance target | Energy budget on DUT node (downstream of isolation) | Why |
|---|---|---|---|
| **Gentle multilevel / quantized conductance** (10–100 µA Icc) | 100 µA | **≤0.5–1 nJ** @ 1–2 V (i.e. ≤100 pF effective at 2–5 V) | Preserves distinct levels; avoids overshoot spreading that destroys HRS/LRS separation |
| **Standard SET** (100 µA–1 mA) | 1 mA | **≤2–5 nJ** @ 2 V (≤500 pF) | Still robust ON/OFF >10²; more tolerance because Intentional LRS is lower |
| **Forming / high-Icc** (5–10 mA) | 10 mA | **≤10 nJ** @ 5 V (≤800 pF) | Relaxed, but still prohibits 10 nF on DUT node |
| **Unacceptable** | any | **>20 nJ** @ 2 V or **>50 nJ** @ 5 V dumps | Will be flagged as CAUTION 1 violation; requires redesign |

In charge terms: at 5 V, **Q = C·V**; 1 nJ @5 V ≈ 0.4 nC ≡ ~2.5×10⁹ electrons — orders of magnitude more than filament atoms. The budget is therefore **capacitance**, not just current.

---

## 5. Consequence: Maximum Allowable Downstream Capacitance

Solve C_max = 2·E_budget / V²:

| E_budget | C_max @ 5 V | C_max @ 2 V | C_max @ 1 V |
|---|---|---|---|
| **1 nJ** (gentle) | **80 pF** | **500 pF** | 2.0 nF |
| **2 nJ** (standard) | **160 pF** | **1.0 nF** | 4.0 nF |
| **5 nJ** (relaxed SET) | **400 pF** | **2.5 nF** | 10 nF |
| **10 nJ** (forming only) | **800 pF** | **5.0 nF** | 20 nF |

**Single most important V1 rule from this table:** If you intend to SET at ≤2 V with 100 µA compliance with ≤1 nJ budget, **the total capacitance that can dump through the DUT at the instant of snap must be ≤500 pF**. At 5 V forming the same 1 nJ budget allows only **80 pF** — barely one BNC connector + 0.5 m cable.

A **10 nF** output capacitor violates the 1 nJ @5 V budget by **125×** and the 2 nJ @2 V budget by **10×**. It must not be placed on the DUT node.

---

## 6. Mitigations — From Physics to Circuit (Sizing Estimates)

### 6.1 Keep Output Compensation Capacitance Upstream of Isolation

The SMU's power stage needs compensation for stability, but that capacitor must be **decoupled from the DUT by a resistor**. Textbook technique (Keithley High-C mode, NI load considerations, Sun Yat-Sen SMU stability paper): add **damping / isolation resistor R_iso** between the power-amp output and the DUT node; take the voltage feedback **after** R_iso (Kelvin sense picks off at the DUT), and compensate the loop for the resulting RC.

| Parameter | Provision | Value / estimate | Note |
|---|---|---|---|
| **R_iso** | Series resistor between power-amp output (+ compensation C) and DUT FORCE node | **10 Ω – 100 Ω** (default **33–47 Ω**) | Limits dump current to I_dump≈V/R_iso for a short; isolates C_comp. Must be non-inductive (thin-film). Power 50 mW @10 mA → 10 Ω dissipates 1 mW; 100 Ω →10 mW — thermal negligible. |
| **I_dump with R_iso** | Into LRS=1 kΩ, V=5 V | Without R_iso: I_pk≈5 mA (filament alone). With 47 Ω: I_pk≈5 V/1.047 kΩ≈4.77 mA — barely changed (R_LRS dominates). **Benefit is isolating C_comp, not limiting resistive current**; for a *short* (R_DUT→0 during hard snap) I_pk limited to 5 V/47 Ω≈106 mA instead of amp's current limit, but for only RC time. | R_iso alone does NOT reduce E=½CV² — it **slows** delivery (τ=R·C) and **decouples** upstream C. It reduces di/dt and gives the comparator time to react, but the energy still arrives unless C is small. R_iso is necessary, not sufficient. |
| **Placement** | R_iso immediately after C_comp, before any cable/DUT branch | Feedback pickoff: FORCE_SENSE node is after R_iso at the connector; power-amp feedback divider senses after R_iso or Kelvin closes the loop. | See §8 (stability). |

**Compensation C choice (provisional):**

| Location | C_value | Energy @5 V | Verdict |
|---|---|---|---|
| DUT node (BAD) | 10 nF | 125 nJ | ❌ Rejected — violates every budget |
| DUT node | 2.2 nF | 27.5 nJ | ❌ Still 5× over gentle budget |
| DUT node | 470 pF | 5.9 nJ | ⚠️ Marginal for 2 V standard, fails 5 V gentle |
| DUT node | **47–100 pF** | **0.6–1.25 nJ** | ✅ Within 1–2 nJ budget at 5 V if no cable — but cable adds more |
| **Upstream** (before R_iso) | **4.7–10 nF** | **59–125 nJ upstream** (not dumped through DUT, only through R_iso) | ✅ Acceptable because R_iso + loop absorb it; the DUT sees only downstream C. |

Correct topology: **C_comp upstream, R_iso = 33–100 Ω, downstream C ≤ 100–200 pF** (PCB+connector+Coff) plus cable managed by length limit.

### 6.2 Minimize Downstream Capacitance

| Source | Mitigation | Expected residual C | Cost |
|---|---|---|---|
| Cable | **Short cable, low-C type, length limit** — mandate ≤0.5 m of ~50 pF/m low-C coax or twisted shielded pair → ≤25 pF. If user needs 1 m, warn in software that gentle compliance (<100 µA) is degraded. Alternative: mount mini-SMU head at probe (remote sense + local clamp) — V2. | 25–50 pF | User procedure, not PCB |
| DUT fixture | Minimal pad area, no decoupling capacitor on DUT rails for ReRAM fixture (decoupling is for digital boards, not ReRAM DC). Remove any 100 nF "just in case" cap on FORCE_HI — it would be 1.25 µJ @5 V (1000× budget). | 10–30 pF | Design discipline |
| PCB + relay | Use **low-Coff** reed relays (Coto 9007-series ~1 pF) or photoMOS for shunt switching where possible; keep FORCE trace short, no copper pour under high-Z node; minimize connector C. | 10–20 pF | Relay selection |
| **Total downstream budget** | Sum above | **≈45–100 pF** without cable, **≈70–150 pF** with 0.5 m cable | Meets 80 pF @5 V for 1 nJ only with short cable; at 2 V meets 500 pF easily. |

**Practical V1 target:** Downstream C ≤ 150 pF → **E ≤1.9 nJ @5 V, 0.30 nJ @2 V, 75 pJ @1 V** — within the standard/relaxed budgets; gentle 100 µA multilevel will still be at the edge at 5 V and should be done at ≤2 V or with the active discharge below.

### 6.3 Active Discharge / Clamp (Not a PTC — a Fast FET)

A resistor alone only slows delivery; an **active clamp** can remove charge *without going through the DUT*. Two distinct functions are needed:

1. **Pre-charge / soft-start slew limiter** (prevents I=C·dV/dt transient on a voltage step). Firmware ramps the DAC at controlled **dV/dt ≤ 0.1–1 V/ms** (e.g. 5 V in 5–50 ms) so I_slew = C·dV/dt ≤ 0.5 µA–5 µA for 100 pF–1 nF — well below compliance. This is a sweep-level mitigation, not a hardware dump.

2. **Fast discharge switch** on the DUT node, gated by hardware compliance flag (or by OUTPUT_DISABLE):
   - **Shunt FET** (N-FET or analog switch, R_on 1–5 Ω) from FORCE_HI to FORCE_LO / GND, placed **between R_iso and DUT** so it can dump the cable+DUT capacitance without filament path. Controlled by ISRC/ISNK flag (LT1970) or comparator output.
   - Sizing: to dump 100 pF @5 V in ≤1 µs needs R_discharge ≤ t/(5·C) ~2 kΩ — any FET qualifies. The point is speed of activation (<5 µs), not R_on.
   - **Caveat:** Discharging *through* the FET still creates a current spike if the FET is across the DUT (DUT sees V drop to 0). The safe variant is to **open the source** (high-Z the power stage via ENABLE) and clamp the *cable* to ground through a resistor, letting the DUT see a controlled droop rather than a crowbar di/dt. A series isolation FET (load switch) between R_iso and DUT, opened on fault, plus a dump resistor on the amp side, can quarantine upstream C.

| Discharge element | Placement | R_on / R_dump | Activation | Leakage concern |
|---|---|---|---|---|
| **N-MOS shunt** (e.g. BSS138-class, low-leakage analog switch ADG1419 ~10 pA) | Across FORCE_HI–LO **downstream** of isolation-switch | 2–10 Ω shunt; leakage must be <50 pA to not corrupt 100 nA range | Hardware flag (<5 µs) + firmware enable gate; must be disabled during normal measurement or it *is* the DUT | Select **low-leakage** FET/switch; gate driver must have <1 nA leakage to node |
| **Series load switch** (cut upstream C away from DUT) | In series after R_iso | R_on <0.5 Ω desired | Opens on fault / disable | Leakage same constraint; use photoMOS or low-leakage NMOS with charge pump |

For V1, the **slew limiter is mandatory; the fast shunt is a CAUTION 1 hardening option**. If the energy budget is met by low downstream C, the shunt can be left unstuffed. If 1 m cable is required, stuff it.

### 6.4 Clamp Diode / TVS (Leakage-Limited)

A TVS or clamp diode (e.g. ESD diode to supply rails) across the DUT node can limit voltage excursion on snap-back, but its **reverse leakage at 5 V** (often 0.1–10 nA) directly adds to the 100 nA measurement floor and must be budgeted — typically **rejected for the 100 nA range** unless a low-leakage (<10 pA) diode is chosen. Place any TVS **upstream of R_iso** or leave unstuffed.

---

## 7. Interaction With Measurement — I = C·dV/dt Transients

Even when the DUT is well-behaved, sweeping voltage deposits displacement current:

```
I_disp = C_total · dV/dt
```

| Sweep | dV/dt | C | I_disp | Compare to compliance |
|---|---|---|---|---|
| 0→5 V in 50 ms (100 mV/s triangle) | 100 V/s | 100 pF | 10 nA | ≪ 10 µA — fine |
| 10 mV step in 10 µs (fast DAC step, no slew limit) | 1000 V/s | 1 nF | 1 µA | 10× DISP at 100 µA compliance — may false-trip range compliance |
| 5 V step in 10 µs (hot-plug or autorange glitch) | 500 000 V/s | 100 pF | 50 µA | Exceeds 10–100 µA compliance → nuisance flag |
| 5 V in 1 ms (soft-start ramp) | 5000 V/s | 100 pF | 0.5 µA | Safe |

**Lesson:** Without slew limiting, a single DAC step can inject a compliance-exceeding spike that is **not** a filament event but looks identical to the compliance flag. Mitigations: **soft-start ramp (10–50 ms for a forming step)** + **range-change holdoff** (switch measure range to compliance range *before* the voltage step, as Keithley does) + per-range blanking (2-sample hold before declaring compliance).

---

## 8. Stability — Why the Cure (R_iso, C_comp) Can Be Worse Than the Disease if Done Wrong

### 8.1 Capacitive Load Pole

A power stage driving C_load through its output impedance R_out creates a load pole:

```
f_p = 1 / (2π · R_out · C_load)
```

For LT1970A open-loop R_out ~0.1–1 Ω (closed-loop even lower), C_load=1 nF → f_p ≈ 160 kHz–1.6 MHz — right near the loop's crossover (3.6 MHz GBW), eroding phase margin → ringing or oscillation. Datasheet load-considerations (NI, TI) confirm: certain C + sense-R combos ring.

Introducing **R_iso** moves the pole to f_p≈1/(2π·R_iso·C_load): with R_iso=47 Ω, C=100 pF → f_p≈34 MHz (well beyond crossover, stable); with C=10 nF → f_p≈340 kHz (still problematic). So R_iso helps *and* large C downstream still hurts.

Compensation must be verified in ngspice (REQ-GEN-001) with a realistic load sweep: R_DUT 10 Ω–1 MΩ, C_load 10 pF–10 nF, with Kelvin feedback modeled including lead inductance (10 nH/cm) and sense lead C (50 pF).

### 8.2 Kelvin Sense Lead Capacitance (Feedback-Site Pole)

The sense lines (SENSE_HI/LO) feed a high-impedance diff-amp/ADC buffer. Their capacitance to ground/shield (50–100 pF/m) adds phase lag **inside the feedback path** if the feedback divider is taken at the sense connector and loaded by cable C. This is the pole Keithley warns about: sense resistor + cable + DUT C forms a pole that can destabilize the CV loop (2450 High-C mode: "sense resistor and external capacitance form a pole → internal capacitor across sense resistor").

Mitigations: keep sense leads **short and symmetrical**, add small **lead-compensation capacitor** across the feedback divider (10–47 pF), or enable a **High-C mode** (loop slowed, GBW reduced, phase margin recovered at cost of speed). The NI SourceAdapt topology solves this digitally with a programmable pole-zero compensator — analog V1 must instead provide a **jumper-selectable feedback cap** and a **slow/fast loop mode bit** (software-selectable compensation).

### 8.3 Transimpedance / Sense Shunt Noise Gain

If a shunt or sense resistor is in the loop, its value changes with range → noise gain and phase shift change. Each range may need its own compensation (different Cf or R_iso). D-architecture handles this with a state machine; V1 must at least **verify the worst-case range** (1 MΩ / 100 nA and 10 Ω / 10 mA are opposite extremes) and document the compensation table.

---

## 9. Cross-Check Against LT1970A Limiter

The LT1970A (Analog Devices 1970Afc datasheet, 20-TSSOP with thermal pad) provides:

- **Adjustable precision current limit:** VCSRC/VCSNK 0–5 V above COMMON, attenuated ×1/10, compared to V_sense = I·R_sense; limit I = V_C/(10·R_sense); **1%** accuracy on the limit amplifier; source and sink limits independent.
- **Takeover time:** ~**4 µs** from sense threshold cross to loop taking control (datasheet § Operation, "time required for current limit amplifiers to take control is typically 4 µs"). Inside REQ-SAFE-001 <5 µs trip / <50 µs regulation envelope.
- **Flags:** open-collector ISRC/ISNK pull low when limit amp is in control; thermal shutdown TSD flag; enable pin puts output high-Z.
- **Caveat:** Limit is **uni-directional per threshold** — to meet CAUTION 3 (per-segment/polarity programmability: +sweep, –sweep, read, disabled), firmware must drive VCSRC and VCSNK from DAC channels per segment (see `COMPLIANCE_ARCHITECTURE.md` Option A/D). Hard-wired resistor divider fails CAUTION 3.
- **Energy blind spot:** LT1970A's power-stage compensation and any capacitance on its OUT pin **upstream of R_sense** is still protected by the limit amp, but capacitance **downstream of R_sense** (cable, DUT) dumps outside the loop — hence §§5–6 still apply even with LT1970A. R_sense must be placed **upstream of R_iso** and measured differentially with Kelvin sense (SENSE+/–) to avoid burden in the feedback.

---

## 10. Poly Fuse / PTC — Why It Is Not Compliance

| Property | PTC PolySwitch (e.g. miniSMD) | ReRAM compliance need |
|---|---|---|
| Trip mechanism | I²·R heating of polymer → PTC snap | Closed-loop analog servo or fast comparator |
| Trip time at 2× hold | **10 ms–1 s** (thermal mass), faster only at >> hold (e.g. 10 A) | **<5 µs** to load-side flag, **<50 µs** to settled CC regulation |
| Trip ratio | Hold : trip ≈ 1:2 (must over-spec hold to avoid nuisance) | Must trip at exactly Icc, not 2× Icc |
| Resistance when cold | 0.05–5 Ω (dominant over DUT LRS) | <100 mΩ desirable; any series R adds burden + self-heating + TC error |
| Resistance when hot | ~100–10 kΩ, latches until power cycle | Must return to flat CC instantly, not latch high-R |
| Current handling | Bidirectional but single threshold (magnitude) | Needs **separate + and – thresholds**, programmable per segment |
| Reproducibility | ±30–50% trip current spread, strongly T-dependent | 1% or better, calibrated via shunt |

**Verdict:** Poly fuse is appropriate as a **supply-rail SOA fuse** (protect the ±12 V regulator from a dead-short on the board) or as a **battery-distribution fuse**, not as a ReRAM current compliance. It may coexist as a **non-compliance safety element** upstream, but must never be described as "the compliance" and must not be in the DUT current path for the 100 nA–1 mA decades (its leakage and burden defeat those ranges).

---

## 11. Summary of Numerical Takeaways (for DEC)

1. **10 nF on the DUT node is never acceptable** — 125 nJ @5 V is 25–250× the gentle filament budget. Move compensation upstream of R_iso.
2. **Budget downstream C to ≤80 pF for 1 nJ @5 V** (gentle), ≤160 pF for 2 nJ @5 V (standard). At the primary ±2 V window the same budgets allow 500 pF / 1 nF, so **forming should be done at the lowest voltage that suffices**, not at the rail.
3. **Standard V1 hardware recipe that meets budget:** C_comp upstream 4.7–10 nF, R_iso 33–47 Ω, downstream PCB+Coff ≤20 pF, cable ≤0.5 m low-C (≤25 pF), DUT fixture ≤30 pF → total **~75–100 pF → 0.9–1.25 nJ @5 V, 0.15–0.20 nJ @2 V** → within standard budget; gentle 100 µA multilevel requires either short cable or active discharge.
4. **Active protections needed:** slew-limited DAC ramp (0.1–1 V/ms), range-change holdoff, and (if 1 m cable required) a hardware-gated FET discharge/series switch driven by the <5 µs compliance flag.
5. **Stability verification required before PCB:** ngspice sweep of C_load 10 pF–10 nF + R_DUT 10 Ω–1 MΩ + sense lead C 0–100 pF, with R_iso and feedback cap values; phase margin >45° at every range. Record worst-case step response (scope-verified later) into R+1 nF.

---

## 12. Verification Checklist (Joins COMPLIANCE_ARCHITECTURE.md § Verification)

- [ ] Scope-captured **short + step load** into precision 100 Ω and 10 kΩ with 47 pF / 1 nF load caps; measure overshoot <1% resistive / <5% with 1 nF + soft-start, flag latency, settled Icc accuracy.
- [ ] **MCU-halted** fault injection (processor held in reset): short output, verify hardware flag asserts <5 µs and output enters safe state without firmware.
- [ ] **Capacitive dump** direct measurement: pre-charge DUT node to 5 V, snap DUT relay to LRS resistor, integrate I(t) on scope → verify delivered energy vs ½CV² table within 10%.
- [ ] **Slew-rate test:** step 0→5 V with 10 µs vs 5 ms ramp into 100 pF; compare displacement current spike vs compliance threshold.
- [ ] **Long-soak drift:** at Icc=100 µA, monitor I_clamped over 100 s with temperature log; verify drift within accuracy envelope.

---

## Appendix — Raw Python for Audit

```python
# docs/calculations/compliance_energy.py — run with any Python 3
C_vals = [10e-12, 47e-12, 100e-12, 470e-12, 1e-9, 2.2e-9, 10e-9]
V_vals = [5.0, 2.0, 1.0, 0.5]
for C in C_vals:
    for V in V_vals:
        E = 0.5*C*V*V
        print(f"C={C:5.2e} F  V={V:.1f} V  E={E*1e9:.4f} nJ  Q={C*V*1e9:.3f} nC")
# solve Cmax for budget
for E_budget in [1e-9, 2e-9, 5e-9, 10e-9]:
    for V in [5.0, 2.0, 1.0]:
        Cmax = 2*E_budget/(V*V)
        print(f"E_budget={E_budget*1e9:.0f} nJ V={V:.0f} -> Cmax={Cmax*1e12:.0f} pF")
```

Constants: k=1.380649e-23 J/K not needed here; only geometry. Tolerance: C values ±10% (C0G) to ±20% (X7R, not allowed on DUT node); V tolerance ±0.5% (source accuracy) → E tolerance dominated by C.

---

*Provenance:* LT1970A datasheet 1970Afc (Analog Devices) — 1% limit, 4 µs takeover, ISRC/ISNK flags, sense range VCC–1.5 to VEE+1.5; NI SourceAdapt (Figure 2a/2b — dual-loop + FPGA compensator); NIST RRAM overshoot paper; IOPscience Control of Current Compliance … (parasitics = compliance spread) + Elimination of high transient currents … (10× overshoot → electrode damage); Keithley 2400/2600B (0.3% of range + 0.02% reading compliance add-on, 30–70 µs recovery, 0.1% overshoot typ); icnavigator SMU Design (CV→CC diode-OR); EEVblog 2400 hot-plug overshoot anecdote; TI OPA547 (internal current limit as contrast). Web searches 2026-08-24 confirm LT1970A specs and polyfuse PTC thermal-trip nature (ABB TB82).
