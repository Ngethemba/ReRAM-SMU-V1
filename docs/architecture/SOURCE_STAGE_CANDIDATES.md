# Source / Output-Stage Candidates vs LT1970A — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 Architecture & Candidate Component Verification  
**Date:** 2026-08-24  
**Status:** `CONCEPTUAL — NO SCHEMATIC / NO BOM / NO LAYOUT`  
**Scope:** Output-stage candidates for REQ-SRC-001..007, REQ-SAFE-001..004, REQ-PWR-003, REQ-DUT-001, REQ-MEAS-007 (provisional)  
**Gate:** Informs Phase 3 selection; promotion requires DECISIONS.md + simulation.  
**Author:** Agent A — Source/Output Architecture

> **Ground rule:** No component is promoted from `PROVISIONAL / REQUIRES VERIFICATION` by this document. All specs below are from primary datasheets (rev cited). Prices/stock are spot checks on 2026-08-24 via public distributor indexes (DigiKey/Mouser/TI/ADI store) and will move. Verify before any DEC.

---

## 0. Requirements Recap & Constraints (What the Stage Must Do)

| Parameter | Requirement | Value / note |
|-----------|-------------|--------------|
| Voltage | REQ-SRC-001/002 (PROVISIONAL-verified) | **±5 V** outer, **±2 V** primary low-noise window; continuous |
| Current | REQ-SRC-006 (PROVISIONAL-verified) | **±10 mA** continuous DC, source **and** sink, four-quadrant (REQ-SRC-005 CONFIRMED) |
| Power | Derived | `|V·I| ≤ 50 mW` @ ±5 V · ±10 mA (+ 100 mV burden headroom → ~51 mW) |
| Compliance | REQ-SAFE-001 (CONFIRMED, DEC-011) | HW loop independent of FW; regulation <50 µs, trip <5 µs, overshoot <1% R / <5% into 1 nF |
| Rails | REQ-PWR-003 (PROVISIONAL) | Nominal **±12 V** analog (headroom TBD); no mains on PCB |
| Load | Derived from DUT + cabling | Resistive 10 Ω–1 MΩ + **capacitive 10 pF–10 nF** (+ cable ~100 pF/m); must be stable **without** oscillation/ringing at any `V` in ±5 V |
| Accuracy target (provisional) | REQ-MEAS-007 | Source V at 0 V within ±200 µV; ±(0.02% rdg + 0.01% FS) ~ ±0.5 mV @1 V |
| Kelvin | REQ-DUT-001 (CONFIRMED) | FORCE HI / SENSE HI / SENSE LO / FORCE LO, remote sense >10 GΩ, open-sense detect |
| Burden | BURDEN_VOLTAGE_ANALYSIS.md §4 (candidate) | `Vburden ≤100 mV @ FS`; shunt baseline 10 Ω (10 mA)–1 MΩ (100 nA) |
| Enable | REQ-SRC-007 / REQ-SAFE-003,004 | HW safe disable, high-Z, defaults to OFF on POR/brown-out/watchdog; min-I on enable |
| Thermal | REQ-SAFE-006 | Sensor on output stage; SOA/derating documented; no heatsink if possible at 50 mW |

**What "good" looks like for V1:**
- Bipolar, continuous — not single-supply, not polarity-reversing relay.
- One analog voltage loop that stays stable into 10 nF (with or without isolation R/comp).
- An external, DAC-programmable **current control** (limit or regulation) that actually meets the <50 µs / <5 µs envelope and flags correctly.
- A **safe disable** that is truly high-Z and survives MCU halt.
- Offset/bias/noise that can meet the ±200 µV @0 V / ±0.5 mV @1 V targets after calibration — or can be credibly calibrated out.

---

## 1. Candidate Taxonomy

| Label | Topology | Quadrants without extra relay | Current sense/control |
|-------|----------|-------------------------------|-----------------------|
| **A — LT1970A** | Monolithic 500 mA power op-amp with dual precision current-limit amplifiers + SENSE pins | **4-quadrant** natively (bipolar rails, push-pull) | External `Rsense` + `VCSRC/VCSNK` (0–5 V → /10 → Isrc/Isnk); regulated takeover in ~4 µs; flags + thermal |
| **B — Precision op-amp + discrete buffer** | `ADA4522-2` or `OPA140` (precision front-end) → complementary BJT or MOSFET follower/buffer (inside or outside loop) | **4-quadrant** if buffer is complementary push-pull on ±12 V | Shunt + comparator/limiter (external) or I-loop amp; not integrated |
| **C — OPA548/OPA551 class** | Power op-amp on ±30 V / 60 V single; internal adjustable current limit (indirect sense) | **4-quadrant** natively; bipolar rails required (not single-supply for SMU) | `R_CLS` or DAC; indirect sense; also E/S disable + thermal flag |
| **D — Composite amplifier** | Precision op-amp (ADA4522-2 class) as `A1` driving power booster (LT1970A or OPA551 or discrete) inside `A1`'s loop; precision sets offset/noise, booster sets current | **4-quadrant** (inherits booster's) | Any of above — composite does not itself add current-limit semantics |
| **E — Dedicated source/sink (dual amp + diode-OR)** | Two amps: V-error amp (sense divider) + I-error amp (shunt) diode-OR'd into shared power stage — classic SourceMeter CV/CC crossover (SMU_ARCHITECTURE_SURVEY.md Arch B) | **4-quadrant** true VI source with seamless CV↔CC crossover + flag | Compliance reference **is** the inactive loop's setpoint → true regulation |

> **Excluded here:** Single-quadrant bench-supply tricks, H-bridge polarity reversers, and TIA-based current measurement — those belong to the measurement-path trade (`docs/research/SMU_ARCHITECTURE_SURVEY.md`). This document is the **source** side only.

---

## 2. Candidate Detail

### 2.1 Candidate A — LT1970A (Baseline)

**Datasheet:** `1970afc.pdf` (LT1970A, 2015-11), supplemented by `1970fe.pdf` (LT1970). Product page lists LTspice model.

| Item | Spec (LT1970A) |
|------|----------------|
| **Supply** | **3.5 V–36 V total** (single or split); split ±2.5 V to ±18 V. Input stage `VCC/VEE` and output stage `V+/V−` can be split — e.g. input ±12 V, output ±7 V to cut dissipation. Need ±12 V for V1 headroom (see §4). |
| **Offset** | `Vos` typ ~200 µV, max not precision-grade; `TCVos` typ **−4 µV/°C**, drift spec −10…+10 µV/°C. `en` ~15 nV/√Hz @1 kHz, `in` ~3 pA/√Hz. Not zero-drift. **Calibratable but not ADA4522-class.** |
| **Bias** | `Ib` typ −160 nA (bipolar), limits −600 nA; `Ios` ±100 nA. Must tie feedback through ~10 kΩ-class R; source accuracy needs cal at 0 V. |
| **Swing** | `Voh ≈ V+ −1.7 V`, `Vol ≈ V− +1.9 V` (typ, full load). On ±12 V rails → ~±10.3 V unloaded, ~±10 V at modest load — plenty of headroom for ±5 V + 100 mV burden + 1.5 V dropout budget. On ±7 V rails still ±5.3 V/±5.1 V — tight but feasible. |
| **Source/sink current** | **±500 mA min** continuous; fail-safe fixed limit ±800 mA; output can be boosted to ±5 A with external transistors. V1 needs ±10 mA → huge margin → SOA is trivial at 50 mW. |
| **Stability / cap load** | Unity-gain stable, GBW **3.6 MHz**, SR **1.6 V/µs**. TI DS says "can drive capacitive and inductive loads directly" with improved reactive-load stability in the **A** rev. In practice: `Cload = 10 nF` needs the usual power-amp treatment — isolation R (1–10 Ω) with feedback pickoff after Rsense (Kelvin) + optional snubber; no heroic comp. The `Rsense + SENSE+/−` pins are **inside** the precision-limit loop; keep Kelvin tight and add `CFILTER` per DS. |
| **Current limit / compliance** | **Integrated, precision, 4 µs takeover.** Two gm amps (`ISRC`/`ISNK`) watch `SENSE+ − SENSE−` vs `VCSRC/10` / `VCSNK/10`. `Ilim = VC/(10·Rsense)` only when **Vc ≥60 mV** (Vsense ≥6 mV, linear); **Vc=0–5 V → Vsense=Vc/10** (IR-01). **Floor Vsense_min 4 mV typ** to prevent simultaneous source/sink → **I_min = 4 mV/Rsense** ≈ **4% FS at 100 mV FS** (or 16% at 25 mV FS, 8% at 50 mV). Vc <60 mV is nonlinear — do not claim 0.1%·I_range with LT1970A alone; 0.1% only via range coercion (Solution A) or precision outer loop / Candidate C (§2.6, IR-01/DEC-024). Example for V1: `Rsense = 10 Ω` → 500 mV/10 Ω = 50 mA @5 V; 10 mA @1 V; 1 mA @0.1 V — but **I_min = 400 µA on 10 Ω (4% of 10 mA)**, **1.6 mA on 2.5 Ω/25 mV (16%)** — see IR-01 table. For finer DAC resolution pick `Rsense = 20–50 Ω` and use DAC 0–2.5 V to reach 10 mA with better granularity, still bounded by 4 mV floor. Open-collector flags `ISRC`, `ISNK`, `TSD`. AC bandwidth VC→output **2 MHz**. **Setting VC=0 still allows ±4 mV/Rsense quiescent.** |
| **Shutdown / safe disable** | Logic `ENABLE` → **0.6 mA standby**, high-Z output, `tON/tOFF ≈10 µs`. TTL w.r.t. COMMON. Correctly tied (pull-down + POR default) → meets REQ-SAFE-003/004. **Setting `VC=0` does NOT guarantee 0 mA** — hockey-stick min ≈4 mV/RS → ~0.4 mA @10 Ω — so ENABLE is the true zero-current means. |
| **Package / thermal** | **20-lead TSSOP (4.4×6.5 mm) with exposed copper pad** (θJA ~30–40 °C/W on 2 s-pads, per copper). At 50 mW DC worst-case (short to GND at 5 V ·10 mA = 50 mW + quiescent ~100 mW → ~150 mW total) → ΔT ~5 °C — no heatsink. Thermal shutdown at ~150 °C + flag. Supply slew on start-up must be ≤6 V/µs per DS (add soft-start or RC on rails). |
| **Lifecycle** | ADI **Active**, two temp grades: `LT1970ACFE` (0–70 °C) and `LT1970AIFE` (−40–85 °C). No PDN at time of writing; LT1970 (non-A, 2% tol) is older rev of same die. Single-source (ADI) risk exists — keep second-source plan in Phase 3. |
| **SPICE** | **LTspice model included in LTspice distribution** — search `LT1970` (and `LT1970A` shares model; verify Vc/10 scaling). ngspice: no native model — use ADI LTspice macro or vendor PSPICE wrapper (importable with minor edits). Demo boards `DC453A/B` available. |
| **Cost / availability (spot 2026-08-24)** | ADI store: **from $6.87 @1k** (ADI list). Octopart/DigiKey aggregator spot: **~$13.87 @1, $17.47 @single** and **~1,400+ in stock** across authorized distributors (DigiKey family). **More expensive than a precision op-amp**, but replaces an external limit loop + comparators + flags. Not a jelly-bean, but not NRND. |
| **Strength for V1** | Four-quadrant with no extra relay; 4 µs precision limit meets DEC-011; external DAC sets Ilim per-quadrant; unity-gain stable; ±12 V→±5 V headroom easy; enable+flags give safe-state. |
| **Weakness for V1** | Offset/bias/noise are **an order worse** than ADA4522-2 → ±200 µV @0 V needs careful cal and low-TC Rsense/reference. TSSOP-20 with thermal pad is harder to prototype than SOIC-8. Single-source. |

**Verdict at conceptual level:** Only part that natively satisfies **four-quadrant + precision current limit + disable + flags in one package** without designing a discrete compliance loop.

---

### 2.2 Candidate B — Precision Op-Amp + Discrete Buffer (e.g., OPA140 or ADA4522-2 + Complementary BJT/MOS)

Two common wirings:
- **(B1) Inside-the-loop buffer:** Precision amp `A1` drives `Q1/Q2` emitter-follower inside `A1`'s feedback — `A1` corrects buffer offset/drift; output is after `Rsense` with Kelvin feedback to `A1 −IN`.
- **(B2) Diamond / BUF634-class buffer:** Closed-loop buffer IC after precision amp — fewer discretes, more cost.

#### B2a: ADA4522-2 as Precision Front-End

| Item | Spec (ADA4522-2, Rev I, 2025-01-08) |
|------|------------------------------------|
| Supply | **4.5–55 V single** / **±2.25–±27.5 V dual** — covers ±12 V directly. |
| Offset | **Vos max 5 µV**, typ 0.7–1 µV; **TCVos max 22 nV/°C**, typ 4 nV/°C. **Best-in-class for V1 accuracy.** |
| Bias | `Ib` typ **50 pA**, max 150 pA; `Ios` 80 pA. Essentially no bias error through 10 kΩ feedback. |
| Noise | `en` **5.8 nV/√Hz**, 117 nV p-p (0.1–10 Hz); `in` ~??? (zero-drift chopper ~800 kHz). Far better than LT1970A for the ±200 µV target. |
| Output | Rail-to-rail **but only 14 mA continuous** (22 mA short source, 29 mA sink). **Cannot drive ±10 mA into 5 V + capacitive load alone** at low distortion — needs buffer. |

#### B2b: OPA140 as Alternative Front-End

| Item | Spec (OPA140, Rev F, 2023-03-28) |
|------|----------------------------------|
| Supply | **4.5–36 V / ±2.25–±18 V** — covers ±12 V. |
| Offset | Vos max **120 µV**, drift max **1 µV/°C** (typ 0.35 µV/°C). JFET input. Good, but **worse than ADA4522** for the ±200 µV cal target. |
| Bias | `Ib` max **10 pA** — excellent. `en` **5.1 nV/√Hz**, ultra-low `in` **0.8 fA/√Hz** — best current noise of the set. |
| GBW/SR | **11 MHz**, **20 V/µs** — fastest loop, but buffer will dominate. |
| Output | ~±30 mA short; still needs buffer for sustained ±10 mA into ±5 V + cable C beyond 1 nF when thermal/SOA considered. |

#### Discrete Buffer Stage (Complementary)

Typical devices: `2N3904/2N3906`, `BC847/857`, `DTC114`, or small MOSFETs `2N7002/BSS84`, or diamond `BUF634A`. Inside `A1`'s loop the buffer's `Vbe` (~0.7 V) and mismatch are **corrected** by the loop — DC offset is still `A1`'s Vos.

| Item | Assessment |
|------|------------|
| **Supply** | Rails pass through — use ±12 V. Buffer dropout `Vbe + Vce,sat` ~1–2 V → on ±12 V gives ±10 V swing — ample for ±5 V. |
| **Offset/bias/swing** | In-loop → offset is `A1`'s. Out-of-loop → buffer offset adds directly — do not do. |
| **Source/sink current** | Sized by transistor SOA. `2N3904` 200 mA, SOT-23 fine for 10 mA DC (150 mW max). MOSFETs give lower bias error but add `Vgs` and Ciss → loop compensation needed. |
| **Stability / cap load** | **Hardest part of B.** Capacitive load + buffer creates two poles: `A1` output → buffer `Cπ/Ciss` and buffer output `ro + CL`. Without `Riso + Cf` or a small local loop, `C = 10 nF` will oscillate. Inside-the-loop composite needs **nested Miller or Riso+feedback pickoff after Riso/Rsense** (see §2.4). Requires SPICE and bench tuning. Must also prevent shoot-through / crossover distortion at µA levels — class-AB bias or small emitter resistors mandatory. |
| **Current limit** | **None integrated.** Must add: either (i) fast comparators watching `Rsense` → clamp `A1` input (trip only), or (ii) second error amp (→ Candidate E). Accuracy depends on comparator Vos + Rsense TC, not 1%. Response is comparator + amp slew — **>10 µs typ**, worse than LT1970A's 4 µs. |
| **Shutdown** | No native. Needs analog switch or `A1` shutdown + buffer disable (e.g., pull buffer bases to rails). Must be verified high-Z; many B-stage buffers leak µA when "off". |
| **Package/thermal** | SOT-23 + SOIC-8: cheap, easy layout. At 50 mW, no heatsink. SOA is trivial, but bias resistor dissipation at short-circuit can be ~100 mW — size for worst-case (5 V · 10 mA through buffer = 50 mW + quiescent). |
| **Lifecycle** | ADA4522-2 and OPA140 are **Active, multi-source TI/ADI, long-lived** (5+ year horizon typical). Jelly-bean buffers are second-sourced. **Lowest supply risk** of any candidate. |
| **SPICE** | ADA4522: ADI PSPICE/LTspice model (ADI library). OPA140: **TINA-TI and PSPICE models on TI.com** (SBOM430E.ZIP) — excellent for stability sims. Discrete buffers: standard Gummel-Poon / VDMOS models in ngspice. Overall → **best sim fidelity** of any candidate for the precision loop. |
| **Cost / availability (spot)** | ADA4522-2: **$3.61–$6.39** (DigiKey $6.39 @1, $3.71 @1k; Mouser $6.23 @1; ~2.5k+ in stock). OPA140: ~**$3.50–$5.00** class (@1k ~$2–3 on TI store, ~$4 on distribution — verify per package). Buffers + passives add **~$1–2**. So **~$5–8 total** → **cheaper than LT1970A** but **excludes limit circuitry**. |
| **Strength** | Lowest offset/drift/noise → easiest path to REQ-MEAS-007 provisional accuracy; modern zero-drift/bias; excellent SPICE coverage. |
| **Weakness** | **No current limit, no disable, no flags.** Stability into 10 nF is the design burden. Buffer adds parts and compensation risk. Compliance accuracy will be worse than LT1970A unless you build a full I-loop (then you are at Candidate E cost). |

**Verdict:** Best **precision** candidate, worst **compliance** candidate. It solves the accuracy problem by creating a new compliance/stability problem.

---

### 2.3 Candidate C — OPA548 / OPA551 Family (Power Op-Amps with Adjustable Current Limit)

This is a **family** — pick one per V1; they differ enough to matter:

#### OPA551 / OPA552

| Item | Spec (OPA551, Rev B 2016-01) |
|------|-------------------------------|
| Supply | **8–60 V total** / **±4–±30 V dual** — **minimum ±4 V** → cannot run from ±3.3 V, but ±12 V is fine. |
| Offset | **Vos max 3 mV** (typical ~1 mV), drift **7 µV/°C** — **2–3 orders worse than ADA4522**; accuracy target requires DAC cal + temp compensation. |
| Bias | `Ib` max **100 pA** (FET input) — good. `en` 14 nV/√Hz, `in` ~? — not low-noise grade. |
| Output | **±200 mA continuous** (380 mA typ), thermally limited, short ~500 mA. Plenty for ±10 mA. |
| Swing | ~**2 V from rail** (Voh = V+ −2.1 V @600 mA; Vol = V− +1.0 V @ 600 mA). On ±12 V → **±10 V/±11 V swing** — **fails ±5 V in the positive direction by ~2 V at high load** — tight; need ±13–15 V rails for full ±5 V + burden. On ±12 V still works for ±5 V at 10 mA with margin but less than LT1970A. |
| Stability | GBW **3 MHz** (OPA551), SR **15 V/µs**; unity-gain stable (OPA551) / gain≥5 (OPA552 — avoid for SMU). Cload stability is documented; driving 10 nF needs **Riso 2–10 Ω + Cf 100 pF–1 nF** or datasheet RC snubber. |
| Current limit | **Indirect, adjustable 0–200 mA** (OPA551) via `R_CLS` to `V−`. **Accuracy is poor** at <10 mA — DS tolerance is ~±20% and drifts with temp; not 1% like LT1970A. Programmable via DAC current/voltage is possible but still indirect sense → **regulation is coarse trip, not precision compliance.** |
| Disable | **E/S pin**: input disables output (high-Z, low Iq) and output **reports thermal shutdown** — matches LT1970A's enable. Useful for REQ-SAFE. |
| Package/thermal | DDPAK-7 / TO-263 (153 mm²) or PDIP-8. **Large power package; needs copper area** even at 50 mW for 200 mA SOA margin. Not as compact as TSSOP-20. |
| Lifecycle | TI **Active**, two packages, no PDN flagged. PDIP variant shows "out of stock" spot but SO-8/DDPAK active. |
| SPICE | **PSpice macro on TI.com** + TINA-TI model; importable to ngspice with `U+` tweaks. Good. |
| Cost | Spot: **~$4.6–5.1 GBP/EUR (~$6–7 USD)** per unit — **cheapest power amp**. |

#### OPA548 / OPA549 / OPA544 (High-Current Variants)

| Part | Cont. I | Min supply | Vos | Swing @10 mA | Current limit | Disable | Package | Note for V1 |
|------|---------|------------|-----|--------------|---------------|---------|---------|-------------|
| **OPA548** | **±3 A** (5 A peak) | ±4 V | **10 mV** max, 30 µV/°C | ~2–3 V from rail | Adj 0–5 A indirect, ±250 mA tol @2.5 A | E/S | TO-220 / DDPAK | Vast overkill; offset is worst of set → **reject for precision**. |
| **OPA549** | **±8 A** | ±4 V | 5 mV max | ~4 V from rail @8 A | Adj 0–10 A | E/S | Power ZIP-11 + heatsink | Absurd for 10 mA; thermal design dominates → **reject**. |
| **OPA544** | **±2 A** | **±10 V (!)** | ~? | large dropout | Fixed ~4 A internal | None / thermal only | TO-220-5 | Min ±10 V supply violates low-voltage plan; fixed limit useless for ±10 mA → **reject**. |

**Verdict on family:**
- **OPA551** is the only member worth carrying as a Candidate C for V1 — it's the **cheap, available, FET-input ~200 mA** option.
- But its **3 mV offset**, **7 µV/°C drift**, **2 V rail loss**, and **coarse indirect limit** make it a **poor SMU core** compared to LT1970A or a precision composite. It fits a "cheap PSU + measurement after the fact" build (Arch A), not a precision SMU.

---

### 2.4 Candidate D — Composite Amplifier (Precision Front-End + Power Booster Inside the Loop)

Topology:

```
Ref/DAC ──→ R_f/R_in ──→ [A1: ADA4522-2/OPA140] ──→ [A2: LT1970A or OPA551 or discrete BJT] ──┬──→ FORCE_HI (after Rsense)
                  ↑ feedback after Rsense (Kelvin) ← Rs ← SENSE_HI ──────────────────────────┘
                  └── Cf + Riso comp ─────────────────────────────┘
```

`A1` sets precision (Vos/drift/noise); `A2` sets current/thermal; loop is closed **after** `Rsense` and after any `Riso`.

| Item | Assessment |
|------|------------|
| **Supply** | Can exploit split: `A1` on ±12 V (or ±15 V), `A2` on ±7 V (LT1970A split) to reduce dissipation; or both on ±12 V for simplicity. |
| **Offset/bias** | **Dominated by A1** — so ADA4522→ ~5 µV system, OPA140 → ~120 µV, regardless of A2. Best of both worlds. |
| **Swing** | Dominated by A2 — see A or C tables. LT1970A composite swings closest to rail; OPA551 composite loses ~2 V. |
| **Current** | Dominated by A2 — same as A or C. |
| **Stability / cap load** | **Most challenging to get right.** Two amps in one loop → need **loop-in-loop compensation**: dominant pole at A1, A2 inside unity. 10 pF–10 nF on FORCE interacts with `Riso·CL` pole and `Rsense·CL`. Requires **nested Miller or lead-lag (Cf across Rf) + Riso with feedback after Riso** (the classic "keep it stable with Riso inside loop" trick). Each booster needs its own measured open-loop gain; composite GBW is roughly `A1` GBW / gain-of-A2 — slower than either alone, which actually **helps** with cap load (lower crossover). Still demands **rigorous SPICE (AC + transient into 10 nF) and bench verification.** Many texts call composite "best precision, hardest stability" and V1's simplest is not composite. |
| **Current limit** | Inherits booster's — so LT1970A composite = 1% / 4 µs with flags; OPA551 composite = coarse. Composite itself adds no limit. |
| **Shutdown** | Inherits booster's ENABLE + `A1` shutdown — coordinate so both go Hi-Z; glitch-free sequencing needed. |
| **Package/thermal** | Two packages + comp network → larger area, more routing, more supply decoupling — but each device dissipates less than standalone at same output. Still no heatsink at 50 mW. |
| **Lifecycle** | Multi-source by construction — if one amp goes NRND, swap. **Best lifecycle hedge.** |
| **SPICE** | Two models in one sim → **most predictive** (A1 precision model + A2 power model). TINA-TI / LTspice both support composite loops. ngspice: possible with careful `.lib` includes. |
| **Cost** | Sum of both + comp passives → **~$10–15** (ADA4522 $4 + LT1970A $7 + passives) → **most expensive** BOM. |
| **Strength** | Combines LT1970A's limit/flags with ADA4522's accuracy; handles accuracy+current simultaneously. |
| **Weakness** | Adds complexity without solving the "LT1970A offset is too high" problem more cheaply than calibration; stability risk is highest of all single-stage options; BOM and verification cost jump. |

**Verdict:** Technically superior but **schedule/complexity cost is high for V1**. It is the natural **V1.1 upgrade** if bench shows LT1970A offset/drift dominates post-cal error and simple one-point cal is insufficient.

---

### 2.5 Candidate E — Dedicated Source/Sink Amplifiers (True CV/CC Crossover = Classic SMU Arch B)

Topology (conceptual, per SMU_ARCHITECTURE_SURVEY.md §3):

```
DAC ──→ selector ──┬── V-error amp (ADA4522-2, senses SENSE_HI/LO via divider)
                    └── I-error amp (ADA4522-2, senses Rsense)
                         ↘ diode-OR / limiter → Power stage (LT1970A or BJT) → FORCE
                              ↑ compliance DACs (VCLIM/ICLIM) + flags
```

- Whichever error amp demands **lower** output wins — seamless CV↔CC crossover, flat compliance, no relay click.
- In **V-source mode**, the I-amp **is** the compliance loop — `Icompliance = VCLIM/(10·Rsense)` (if LT1970A stage) or `VCLIM/Rsense` (if discrete). In **I-source mode**, roles swap.

| Item | Assessment |
|------|------------|
| **Supply** | ±12 V for error amps + power stage; same split tricks as above. |
| **Offset / accuracy** | Two precision amps → two Vos terms, but each is calibrated per-mode; CC-mode accuracy is set by I-amp + shunt, not by power stage. |
| **Source/sink** | True 4-quadrant VI source by design; sourcing and sinking are symmetric in CV, and also CC can be bipolar if error amps are bipolar. |
| **Stability** | **Two loops + crossover = highest analog risk on the list.** Each loop needs its own compensation for **both** resistive and capacitive DUT (R-loop vs C-loop). Crossover must be glitch-free; a poorly chosen OR diode / limiter creates a "dead zone" at the knee. Oscillation at crossover into 1–10 nF is the canonical failure mode of DIY SMUs. Requires per-loop SPICE + transient into RCL loads + compliance-entry slew test. |
| **Current control** | **Best semantics:** compliance is **regulation**, not just trip. Flag correctly distinguishes compliance-active vs fault. Accuracy is I-loop + DAC, typically **~0.2–0.5% + offset** with ADA4522-grade amps — close to LT1970A's 1% but tunable per range. |
| **Disable** | Disable the power stage; error amps can stay alive to hold flag logic. Still need POR-safe defaults. |
| **Package/thermal** | 2–3 amps + power stage + OR/limiter → **largest area, most passives**. Same 50 mW thermal but more quiescent. |
| **Lifecycle** | Excellent — all generic. |
| **SPICE** | Two loops interacting → model fidelity is critical; can sim but bench will diverge without parasitics (diode capacitance, Rsense ESL, cable L). |
| **Cost** | **~$12–20** before calibration overhead — most expensive in parts + engineering hours. |

**Verdict:** The **textbook-correct SMU** and the best ReRAM compliance (flat CC, low overshoot, R-02/R-03 mitigation). Also the **highest bring-up risk for a first PCB**. Recommended to **defer to V1.1** unless Phase 3 sim + prototype bandwidth is explicitly funded.

### 2.6 Source Candidate C — Precision Outer Loop + LT1970A Booster (IR-15)

**Status:** Phase 3 candidate (IR-15) — promoted from footnote; no PCB commitment until simulation.

```
precision outer voltage-loop amplifier (ADA4522/OPA140-class, Vos 5 µV / Ib 10 pA, e.g., ADA4522-2)
       ↓ (drives LT1970A +IN or booster input, filtered 1 kΩ+10 nF)
LT1970A used as power/current-limit booster, unity-gain buffer (SENSE+/− across Rsense, ISRC/ISNK flags retained)
       ↓
FORCE via Rsense + R_iso (feedback after R_iso to outer amp — DUT-sense loop, not OUT)
```

- **Retains:** precision DC offset/drift from outer amplifier (5 µV vs LT1970A ~200 µV), LT1970A source/sink drive (±500 mA), integrated 4 µs limit (Vc/10 law, same floor/linear limits as §2.1), ENABLE high-Z + TSD/ISRC/ISNK flags, split-supply option (outer ±12 V, LT1970A V+/V− ±7–8 V to cut dissipation).
- ** Solves IR-01 0.1%:** precision loop is the only topology that can credibly claim 0.1% closed-loop compliance accuracy (textbook SMU dual-error-amp CV/CC diode-OR) — at cost of nested-loop complexity (Solutions C/D of IR-01).
- **Stability (explicit Phase 3 gate — do not assume):** nested loop interaction (outer voltage + inner current), phase margin vs capacitive DUT 10 pF–10 nF + cable, Kelvin remote-sense latch-up; requires Miller/lead-lag compensation (Cf across Rf, R_iso with feedback after R_iso) and COMPLIANCE_ARCHITECTURE R_iso + C_UPSTREAM/C_DOWNSTREAM budgeting. Must sweep CL 10 pF–10 nF + Llead 100 nH, Rsense 2.5–10 Ω, and compliance-entry step (IR-16 O/J).
- **Trade:** ~$10–15 BOM (ADA4522 $4 + LT1970A $7 + comp) vs ~$7 LT1970A alone; highest stability risk of single-stage options but best lifecycle hedge (multi-source) and accuracy. V1 REV-A ships LT1970A direct (Candidate A) with Candidate C as parallel simulation; promotion requires Phase 3 AC + transient + compliance crossover validation per IR-15/16 O.

---

## 3. CAUTION 1 — Bipolar vs Full Four-Quadrant (Why "Bipolar" ≠ "4-Quad", and How Much 4-Quad V1 Actually Needs)

**CAUTION 1:** *Team must not confuse "bipolar voltage source" (±5 V, i.e., can force +5 V and −5 V) with "four-quadrant operation" (can force ±V while sinking or sourcing ±I in any combination).*

### What the spec actually requires — and what V1 can *not* require

- **Bipolar (2-quadrant):** `Q1 (+V/+I)` and `Q3 (−V/−I)` only. The source **sources** current; the load/DUT never drives current back into the source. Implemented by a single-supply stage with level shift, or a push-pull that only sources, or a relay that flips polarity.
- **Four-quadrant (REQ-SRC-005 CONFIRMED, DEC-007):** `Q1` source +V, `Q2` sink +V (DUT pushes −I at +V), `Q3` source −V, `Q4` sink −V.
- **V1 experimental reality (Task-0 update):** ReRAM V1 waveforms are **Source-V / Measure-I bipolar sweeps** (`0→+Vmax→0→−Vmax→0`) with **active sink** — i.e. the SMU must hold `+V` while the DUT sinks `−I` (Q2) and hold `−V` while the DUT sources `+I` (Q4). This demands **+V±I and −V±I** — true 4-quadrant **voltage-source** operation. It does **NOT** demand an arbitrary **Source-I** (galvanostat) with full bipolar current programming and arbitrary I→V compliance. Source-I / Measure-V is at most a diagnostic (nice-to-have, PHASE1 §10) and is **not a V1 gate.** Conflating the two inflates complexity from "bipolar V-source that can sink" to "full VI source with CC regulation" (Candidate E). V1 is satisfied by a **bipolar Source-V / Measure-I SMU that can sink ±10 mA at any `V` in ±5 V** — exactly what LT1970A and a complementary-buffer stage provide.

Reasons Q2/Q4 sink matters even without Source-I:
  - ReRAM in LRS at +2 V is a **low-R load** — transiently the DUT looks like a source when filament forms or NDR snaps (COMPLIANCE_RESEARCH.md §2).
  - "Read" verification, hot-swap, and **quadrant-switch glitch** at zero-cross must be characterized — commercial SMUs show **4–8× offset penalty** on sink vs source.
  - REQ-SRC-004 + PHASE1 §9 + RERAM §2/§5.5: NDR and thermal snap require sink without relay click.

### What each candidate provides

| Candidate | Is it 4-quadrant at ±5 V / ±10 mA? | What proves it | Risk if misread as "just bipolar" |
|-----------|------------------------------------|----------------|-----------------------------------|
| **A LT1970A** | **Yes**, natively — complementary push-pull on ± supplies, `ISRC/ISNK` independent. | DS Block Diagram `Q1/Q2` + VCSRC/SNK + 4-quadrant demo Fig.1 (charges 1 µF to ±5 V with asymmetric limits). | Low — but need −rail charge pump if wanting 0 V inclusive (DS Fig.9). |
| **B Prec+Discrete** | **Only if buffer is complementary push-pull and rails are bipolar.** A single NPN or N-MOS buffer is **1-quadrant**. | Inside-loop emitter-follower with PNP/NPN (or N/P FET) — must bias class-AB. | **High** — choosing a single-ended buffer silently collapses to 2-quadrant; ReRAM RESET will fail quadrant-transition test. |
| **C OPA551** | **Yes** on **dual supplies**; **No** on single-supply (then it's just positive). | DS Fig.1 with ±15 V rails and load to GND. Single-supply OPA551 can only swing to V− +2 V → not ±5 V. | **Medium** — TI datasheets show many single-supply examples that mislead; explicitly require ±12 V rails in Phase 3 schematic notes. |
| **D Composite** | Inherits booster's quadrant. LT1970A composite = yes; OPA551 composite = yes (dual). | Same as A/C. | Same as A/C; plus composite crossover must not create a dead zone near 0 V that mimics a relay click. |
| **E Dual amp** | **Yes by definition** — that's the point. | Arch B crossover diagram, both error amps bipolar. | Low — but crossover tuning is what makes 4-quad clean vs glitchy. |

### Phase 3 gate for CAUTION 1

Every candidate that reaches layout must pass a **quadrant-transition scope capture** before any ReRAM DUT (REQ-CAL-002): `0→+2→0→−2→0` staircase into resistive + 1 nF loads, measuring `Vout(t)` and `I(t)` for relay-click-free crossing and sink vs source Vos separately. Two-quadrant stages will fail at `0→−`.

---

## 4. CAUTION 2 — Where the Burden Sits: FORCE vs SENSE Feedback Point (Kelvin Correctness)

**CAUTION 2:** *Shunt burden `Vburden = I·Rshunt` is NOT automatically eliminated by "having Kelvin sense" — it depends on WHERE the sense element sits and WHERE feedback is taken. High-side vs low-side placement, remote-sense loop closure point, and range-dependent 100 mV burden all interact with headroom, 2-wire vs 4-wire error, and stability. See BURDEN_VOLTAGE_ANALYSIS.md §§1–4. Critically: the voltage-loop feedback must be taken from **Kelvin sense at the DUT terminals (SENSE_HI/LO)**, not from the FORCE node before the shunt — otherwise `Vdut = Vforce − Vburden` and Kelvin is defeated.*

### 4.1 The two placements — and where 100 mV hurts

```
HIGH-SIDE sensing (LT1970A default; Rsense INSIDE the LT1970A's current-limit loop):

DAC → Power amp → OUT ── Rsense ── FORCE_HI ── DUT_HI
                       SENSE+ ─┘  SENSE_HI ────────── DUT_HI (Kelvin, nA bias)
                       SENSE− ─┐  SENSE_LO ────────── DUT_LO
                                └─── FORCE_LO ── DUT_LO (star GND)
LT1970A feedback: SENSE− → −IN  (Rsense is INSIDE the LT1970A's own loop)
SMU voltage-loop (ideal Phase-3 DUT-sense): SENSE_HI/LO → diff-amp → −IN (Rsense BURDEN is OUTSIDE the DUT voltage loop — see §4.1b)
Burden seen by op-amp output: Vout must be Vdut + I·Rsense + I·Rlead
Headroom: need V+ ≥ Vdut,max + I·Rsense@FS + Vsat + margin
4-wire error: DUT voltage is correct (SENSE_HI/LO encloses DUT only — Kelvin corrects)
2-wire error: Vdut = Vforce − Vburden → 100 mV systematic error — unacceptable for ReRAM
Stability: Rsense + sense wiring L inside LT1970A's limit loop → need RC deglitch (FILTER pin)


LOW-SIDE sensing (alternative — recommended for V1 *measurement* perspective, DUT-sense loop encloses DUT only):

DAC → Power amp → FORCE_HI ── DUT_HI ──┐
                  FORCE_LO ── Rsense ──┘ GND-side (sense amp across Rsense, CM≈0)
                  SENSE_HI ── DUT_HI (Kelvin)
                  SENSE_LO ── DUT_LO (Kelvin)
Feedback pickoff: SENSE_HI/LO diff-amp → −IN  (Rsense is OUTSIDE the voltage loop; loop encloses DUT only)
Burden seen: DUT LO burden-free; Rsense drop does NOT enter Vdut (it is outside loop, but consumes headroom at FORCE_LO)
Headroom: V+ still must supply Vdut + headroom; V− must sink I·Rsense + Vsat
2-wire error: same — 100 mV if you short SENSE to FORCE
Stability: Rsense outside voltage loop → loop is simpler (no Rsense L inside); current-limit loop is separate
```

#### 4.1b The recommended Phase-3 wiring (combines both correctly)

> **Canonical Kelvin equation (IR-11):** `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` for the topology where SENSE encloses DUT only and shunt sits low-side outside loop. Kelvin sensing does not physically eliminate shunt burden — it prevents burden from becoming DUT-voltage error by forcing the source to provide additional headroom. **LT1970A alone is not a 4-terminal remote servo** — its internal SENSE+/− is the compliance sense across Rsense; remote DUT-sense requires external differential feedback (post-buffer IR-02 → diff/attenuation → error amp → LT1970A +IN → FORCE).

- **LT1970A's SENSE+/−** = **current-limit sense across Rsense only** (high-side or low-side, kelvin-routed to Rsense pads, FILTER cap optional).
- **SMU's SENSE_HI/LO** = **Kelvin voltage measurement across DUT only** (high-Z diff-amp → ADS1262). The **voltage-source feedback** for accuracy must close on **SENSE_HI/LO at the DUT**, i.e. **burden is OUTSIDE the DUT voltage loop** — DUT sees the set `V` regardless of `I·Rsense`. This is the "DUT-sense loop with headroom" drawn above.
- Consequence: in **4-wire** mode `Vdut = Vset` is correct by construction, even with 100 mV burden. In **2-wire** mode (SENSE shorted to FORCE at the connector) `Vdut = Vset − I·Rsense` and the **full burden error appears** — 100 mV is **5.0% @ 2 V, 16.7% @ 0.6 V (typical Vset), 20% @ 0.5 V read, 50% @ 0.2 V read** — per CAUTION 2. For LRS reads at 0.2 V on the 1 mA range, a 100 mV burden is catastrophic without Kelvin.
- **Design tradeoff to document in Phase 3:**
  - Option A — **Keep 100 mV FS and require 4-wire for any accuracy-critical measurement.** Supply headroom on ±12 V still covers `5 V + 0.1 V + 1.9 V = 7.0 V` (§5) → feasible, but low-V 2-wire is explicitly 5–50% in error (must be flagged in firmware: warn when `Vset < 1 V` in 2-wire + `|I| > 0.1·IFS`).
  - Option B — **Lower burden on low-current / low-voltage ranges.** E.g. switch to `Rshunt` giving **10–20 mV FS on the 10 µA/1 µA ranges** (higher voltage gain in current-measure amp, lower headroom impact, but 3× worse Johnson noise — still <1% FS at 10 Hz) or provision a **secondary 10 mV-FS shunt** for the 0.5–0.6 V SET region. Phase 3 will simulate both and pick per-range FS (the BURDEN table's 100 mV is a *baseline*, not a per-range law).
  - Phase 3 DEC must state per-range FS and whether the DUT-sense loop is closed in hardware (precision divider + diff-amp driving −IN) or corrected in software (DMM-anchored cal that logs `range_state` + `I·Rsense` — see §4.3).

### 4.2 What this means per candidate

| Candidate | Natural Rsense placement | Feedback point that meets REQ-DUT-001 | Burden at 10 mA FS (10 Ω) | Consequence for V1 |
|-----------|--------------------------|----------------------------------------|---------------------------|--------------------|
| **A LT1970A** | **High-side, mandatory** — DS Fig.1: `OUT ─ Rsense ─ load`, `SENSE+ = OUT`, `SENSE− = load side`, `FB = SENSE−`. | `SENSE− → −IN` → burden **inside loop** → `Vdut = Vset` by construction, no software correction, even in 2-wire. | **100 mV** at 10 mA. On ±12 V rails: need `12 −1.9 (Vol) −0.1 (burden) ≥ 5 V` → **5 >> ok** (6.9 V margin). Even on ±7 V: `7−1.9−0.1=5.0 V` exactly → choose ±8 V min for LT1970A. | **Correct by construction.** Use LT1970A as DS intends; Kelvin SENSE_HI/LO are **the voltage-measure path** (differential amp → ADS1262), distinct from LT1970A SENSE+/− which is the **current-limit** path. Keep the two sense pairs **star-pointed only at DUT**. |
| **B Discrete** | Either, but **high-side recommended** if inside-loop buffer. | If high-side: `load side → −IN`. If low-side: need software `Vdut = Vforce − I·Rsense` (fragile, range-dependent) or extra diff-amp to close loop on DUT. | Same 100 mV physics. Buffer Vos not in current path. | High-side is **simpler to get right** — choose it; document low-side as rejected with rationale. |
| **C OPA551** | Either — no SENSE pins. Current limit is internal indirect sense, **not across Rsense**. Measurement Rsense is outside the voltage loop unless you choose to close it. | Voltage loop closes on a **divider from FORCE_HI** — **not** on the measurement Rsense → burden is **outside loop** → **software correction required** for 2-wire; Kelvin SENSE fixes it only for 4-wire. | Same 100 mV inside DUT series path, but amp's `Vout` does not include it → 2-wire accuracy is degraded by 100 mV unless corrected. | **Accuracy trap:** If firmware forgets `I` changes with `V`, 2-wire readings at 500 µA on 10 mA range show ~5 mV systematic error. 4-wire masks it at DUT, but headroom calc must still include burden. |
| **D Composite** | Same as booster. LT1970A composite → high-side inside; OPA551 composite → divider outside. | Follow booster. | Same. | Same traps as A or C. |
| **E Dual-amp** | **High-side, inside the I-loop** (shunt is the I-feedback element); V-loop senses SENSE, I-loop senses Rsense. | Diode-OR output stage — both loops' feedback points matter; V-loop on SENSE, I-loop on Rsense. | 100 mV is inside I-loop but outside V-loop until compliance trips → crossover is the hand-off point. | Cleanest burden handling — dedicated loops. Still need distinct SENSE pairs. |

### 4.3 Key traps to document in Phase 3 schematic

1. **Two sense pairs, two jobs.** `LT1970A:SENSE+/−` = current-limit sense across `Rsense` (low-value, high-side, kelvin-routed to `Rsense` pads). `SMU:SENSE_HI/LO` = **Kelvin voltage measurement** across DUT (high-Z diff-amp → ADS1262, per REQ-DUT-001). Do not merge or short them.
2. **Feedback after burden.** The **voltage loop feedback** must be from **SENSE− (LT1970A) / FORCE-side of Rsense** or from `SENSE_HI` (if the SMU voltage sense drives the loop) — **not from `OUT` before Rsense**. Taking feedback from `OUT` makes `Vdut = Vset − I·Rsense` and reproduces the "Kelvin does not fix burden" bug.
3. **Range-dependent burden is not fixed.** `Vburden` = 100 mV only on the **selected measurement range** (REQ-MEAS-001 autoranging). On the wrong range it's smaller; on a 10 Ω shunt at 500 µA it's only 5 mV. Docs/firmware must log `range_state` with every sample (REQ-SAFE-007) so the headroom/burden correction is traceable.
4. **High-side CM.** High-side `SENSE−` slews with `Vforce` (±5 V) → sense stages see **common-mode = Vdut**. LT1970A SENSE CM range is `VCC −1.5 V` to `VEE +1.5 V` → on ±12 V that's ±10.5 V, fine. The **voltage-measure** diff-amp (ADA4522-2 class) must be chosen with **CMR ±12 V** and `>10 GΩ` Z (FET or zero-drift) — verified in Phase 3.
5. **FILTER pin.** LT1970A's `FILTER` → `SENSE−` internal 1 kΩ + external C creates a pole that **band-limits the current-limit loop** and tames Rsense wiring inductance → include pad for `CFILTER` (100 pF–1 nF) and note in Phase 3.

---

## 5. Headroom & Dropout Check (REQ-PWR-003)

Worst-case headroom stack at **+5 V, +10 mA** (range-dependent burden D per SHUNT_RANGE_TRADEOFF §2.4, IR-05):

```
V+ ≥ Vdut,max + Vburden@FS + Vsat(amp) + margin
# Philosophy D: 10 mA range is 25 mV FS (2.5 Ω), not 100 mV — worst headroom is on 10 mA/25 mV, not 100 mV
V+≥ 5.0 V   + 0.025 V (10 mA D)  + 1.7–2.0 V    + 0.5 V ≈ 7.2–7.5 V  (100 mV FS would be 7.6 V)
# 1 µA/100 nA ranges are 100 mV FS (100 kΩ/1 MΩ) but at ≤1 µA headroom cost is negligible vs accuracy
V−≤ −5.0 V  − 0.025 V            − 1.9 V        − 0.5 V ≈ −7.4 V
# Thermal: 10 mA·25 mV = 250 µW on 2.5 Ω (vs 1 mW at 100 mV/10 Ω); 100 µA·50 mV=5 µW; 1 µA·100 mV=100 nW — range-dependent.
```

| Candidate | Vsat (typ) | Required V+/V− for ±5 V+100 mV | On nominal ±12 V | On LT1970A split (VCC ±12, V+/V− ±7–8) |
|-----------|------------|-------------------------------|------------------|------------------------------------------|
| **A LT1970A** | +1.7 / −1.9 V | **±7.2–7.3 V** (25 mV burden D @10 mA; 7.6 V if 100 mV FS) | ✔︎ **4.7 V margin on ±12 V** (range-dependent) | ✔︎ still works at ±8 V; ±7 V is marginal (+5 V exactly — give +1 V) |
| **B Prec+Discrete (BJT)** | ~1.0–1.5 V (Vbe+Vce) | ±6.6 V | ✔︎ | ✔︎ (tighter with MOSFET Vgs ~2–3 V) |
| **C OPA551** | ~2.0 V from rail @200 mA | **±7.1 V** but DS says min ±4 and dropout curve is ~2.4 V @0.6 A → **±7.6 V for guaranteed ±5 V** | ✔︎ on ±12 V with 4.4 V margin | Not applicable (no split) |
| **D/E** | As booster | As booster | As booster | As booster |

**Conclusion:** Nominal **±12 V** (REQ-PWR-003) is **comfortable for all candidates**. No rail change is justified by this analysis. A later optimization can split the LT1970A's `V+/V−` to ±8 V to cut dissipation (~50 mW → 30 mW) — optional, not required.

---

## 6. Comparison Table

Scored qualitatively against V1 requirements — **5 = best, 1 = worst** for the V1 envelope (not absolute). Cost is lower-is-better.

| Criterion → | **A LT1970A** | **B Prec+Discrete (ADA4522/OPA140+BJT)** | **C OPA551** | **D Composite (ADA4522+booster)** | **E Dual source/sink (CV/CC)** |
|-------------|---------------|------------------------------------------|--------------|-----------------------------------|--------------------------------|
| **Supply fit (±12 V → ±5 V)** | 5 — 4.7 V margin on ±12 | 5 | 4 — needs 2 V clearance | 5 (as A) / 4 (as C) | 5 |
| **Offset / bias / swing** | 2 — 200 µV/160 nA, cal required | **5** — ADA4522 5 µV/50 pA | 1 — 3 mV/100 pA | **5** — as A1 | **4** — two loops, still ADA4522 grade |
| **4-quadrant source+sink @±10 mA** | **5** — native | 3 — only if push-pull built | 3 — needs dual rails, not single | 5 / 3 (as booster) | **5** |
| **Cap-load stability (10 pF–10 nF + cable)** | 4 — unity-gain stable + improved RL drive; Riso+pickoff still needed | 2 — hardest (buffer poles) | 3 — needs datasheet RC network | 2 — two amps, nested comp | 1 — two loops + crossover |
| **Current limit / compliance (external control, flag, speed)** | **5** — 1%, 4 µs, separate src/snk, flags, 2 MHz VC BW | 1 — none integrated; comparators → coarse, slow | 2 — coarse indirect, ±20% | 5 / 2 (as booster) | **5** — true CV→CC regulation, best semantics |
| **Safe disable (Hi-Z, POR-safe, thermal)** | **5** — ENABLE 0.6 mA Hi-Z + TSD + fixed 800 mA | 1 — design-your-own | 4 — E/S + TSD | 4 — as booster, sequencing needed | 3 — must co-disable power stage |
| **Thermal @50 mW (no heatsink)** | **5** — ~5 °C rise, no sink | 5 | 3 — DDPAK copper pour needed | 4 | 3 — more devices |
| **Package / layout ease** | 3 — TSSOP-20 w/ pad | 4 — SOIC+SOT-23, easy | 2 — DDPAK-7 large | 2 — two ICs + comp | 1 — most area |
| **Lifecycle / second-source** | 3 — single-source ADI, active | **5** — TI+ADI jelly-bean | 4 — TI active | 4 — hedged | 5 — generic |
| **SPICE availability / fidelity** | 4 — LTspice model (import to ngspice) | **5** — TI/ADI TINA+PSpice | 4 — TI model | 4 | 3 — interaction hard |
| **Cost @1 unit (distributor spot)** | 3 — ~$14–17 @1 (~$7 @1k) | **5** — ~$6–8 + discretes | **5** — ~$6–7 | 2 — ~$10–15 (both ICs) | 1 — ~$12–20 |
| **Engineering effort to first DUT** | 4 | 2 | 3 | 1 | 1 |
| **OVERALL for V1 (±5 V·±10 mA SMU)** | **Strong contender** | **Precision-only** | **Weak fit** | **Next-gen** | **Textbook but heavy** |

*Weights: source/sink + compliance + safe disable count **2×** others for REQ-SRC-005/REQ-SAFE-001 — those alone drove DEC-007/011.*

---

## 7. Recommendation for Phase 3

### SELECTED FOR PHASE 3 — Primary: Candidate A LT1970A

**Selected as the primary output-stage candidate to simulate and prototype in Phase 3.**

**Rationale:**
- The **only** single-IC candidate that simultaneously delivers **four-quadrant** (+V±I / −V±I, sink-capable — CAUTION 1) without needing a full Source-I CC regulation loop, **precision 1% separate src/snk current control** with **4 µs takeover** and **2 MHz VC bandwidth** (REQ-SAFE-001, DEC-011), **ENABLE high-Z + thermal + flags** (REQ-SAFE-003/004, REQ-SRC-007), and **unity-gain stability** into reactive loads — matching the `I = VC/(10·Rs)` compliance law needed for ReRAM forming (10 µA/100 µA/1 mA/10 mA via DAC).
- On **±12 V** it clears the **±5 V + 100 mV burden + 1.9 V dropout + DUT-sense headroom** (§4.1b, §5) with **>4 V margin** — no rail redesign, but Phase 3 must provision the **DUT-sense loop** (SENSE_HI/LO → diff-amp → feedback) so 100 mV = **5% @2 V / 16.7% @0.6 V / 50% @0.2 V** does not corrupt 2-wire low-V SET reads (CAUTION 2).
- Offset/bias (`200 µV / 160 nA`, `15 nV/√Hz`) are **worse than zero-drift** but **calibratable** to the provisional REQ-MEAS-007 targets (±200 µV @0 V, ±0.5 mV @1 V) with a one-point force-offset + gain trim anchored to `ADR4525` class ref + precision `Rfb` — Phase 3 will quantify residual vs temp.
- The alternative that wins on offset (B) **loses** on compliance/disable/stability and would require designing exactly the limiter that LT1970A already integrates. The alternative that wins on cost (C) **loses** on offset by **orders** and on limit accuracy.

**Phase 3 actions for LT1970A (must gate any DEC promotion):**
1. **LTspice → ngspice port:** run AC + transient with `CL = 10 pF, 100 pF, 1 nF, 10 nF` + `Llead = 100 nH` (cable) and `Rsense = 10 Ω` (V1 10 mA) + `Riso = 1–10 Ω` with **SMU voltage feedback taken from SENSE_HI/LO (DUT), not from OUT** (CAUTION 2) and `CFILTER = 220 pF` on LT1970A `FILTER`. Sweep ±5 V staircase and compliance-entry (0.5 Ω step into 10 mA limit) → verify `Vring <5%`, `I-overshoot <1% R / <5% C=1 nF`, `t_reg <50 µs`, `t_trip <5 µs`, and `TSD` trip.
2. **Enable/POR:** verify `ENABLE` defaults low (pull-down 47 k + POR RC) → Hi-Z at brown-out; measure `Iout <1 µA` disabled.
3. **Burden-closed loop:** confirm high-side wiring `OUT─Rsense─FORCE`, `SENSE+ = OUT`, `SENSE− = FORCE`, `FB = DUT SENSE_HI/LO diff-amp` (not OUT) per §4.1b; Kelvin `SENSE_HI/LO` is a **separate** differential amp to the ADS1262 — document the **two-sense-pair** rule and measure CMR. Log per-range FS choice (100 mV vs 10–20 mV on low-V ranges) for the 5%/16% tradeoff.
4. **Offset budget:** model `Vos·(1+Rf/Rin)` + `Ib·Rf` + `en·√(π/2·BW)` at NPLC 1–10; define cal procedure (force 0 V trim + gain trim at +2 V against 6½-digit DMM) and temp sweep 15–30 °C.
5. **Second-source plan:** record LT1970 (2% tol, cheaper) as fallback and monitor ADI PDN; no PCB change.

### SELECTED FOR PHASE 3 — Alternate: Candidate D Composite (Precision Front-End + LT1970A/Discrete Buffer Inside Loop)

**Selected as the alternate / risk-mitigating candidate to simulate in parallel (Lab experiment, not baseline PCB) — per Task-0 directive: primary = LT1970A, alternate = precision+buffer composite.**

- **Topology:** `ADA4522-2` (preferred) or `OPA140` as precision `A1` → `LT1970A` (or complementary BJT pair `2N3904/06`) as booster `A2` inside `A1`'s loop, closed on **DUT SENSE_HI/LO** (CAUTION 2). `A1` contributes `5 µV / 22 nV/°C / 50 pA` (ADA4522) so system `Vos` drops 40× vs LT1970A alone; `A2` still provides 4-quadrant sink + 1% limit + ENABLE.
- **Why alternate (not primary):** Fixes LT1970A's offset/drift without ad-hoc cal, at the cost of **nested-loop stability into 10 nF** (two poles + `Riso·CL`) and **~$10–15 BOM** (vs ~$7 LT1970A). For V1 DC staircase at NPLC≥1, cal likely closes the gap more cheaply — composite is insurance if bench shows uncorrectable drift or if 4-wire DUT-loop accuracy demands A1's zero-drift.
- **Phase 3 actions (simulation only):** Build composite AC model (ADA4522 PSPICE + LT1970A/bjt) with `A1 G=1`, `A2` inside loop, `Rf/Rin` for ±5 V, `Cf` lead-lag + `Riso` after Rsense with feedback after `Riso` (DUT-sense). Sweep `CL 10 pF–10 nF`, check **phase margin >45°** and compliance step. Do NOT layout until/unless primary fails its offset gate.

### DEFER — Remaining Candidates (Carried as Informational, Not Built in V1)

| Candidate | Status for Phase 3 | Why deferred | When to revisit |
|-----------|-------------------|---------------|-----------------|
| **B Precision + discrete buffer standalone** | **DEFER — absorbed into composite alternate** | Gives lowest Vos but **no integrated limit/disable** → standalone B would need the same LT1970A/bjt compliance you already have in the composite. Keep ADA4522-2 as **SENSE diff-amp** regardless. | If composite wins, B's discrete buffer is its `A2`. |
| **C OPA551 / OPA548 family** | **DEFER — reject for SMU core; keep as low-cost bench-supply reference** | **3 mV Vos / 7 µV/°C drift = 500× worse than ADA4522** → provisional REQ-MEAS-007 fails without heroic temp-comp. Dropout **2 V from rail** squeezes ±5 V on ±12 V. Indirect current limit is **coarse (±20%)**, not precision compliance. Large power package wastes area for 50 mW. | **Only if BOM must drop <$8** and accuracy is relaxed to ±5 mV — not V1's charter. `OPA551PA` could be a **V1 test-jig programmable load**, not the SMU output. |
| **E Dedicated source/sink (CV/CC diode-OR)** | **DEFER — research path to true SMU compliance regulation** | **Textbook-correct**: flat CC regulation, lowest overshoot, best ReRAM forming control (R-03). But **two compensations + crossover tuning into 10 nF** = longest bring-up and largest area. DEC-011 trip targets can be met by LT1970A's 4 µs limiter **without** this complexity for V1 DC sweeps. | **V2 SMU** where `Source I / Measure V` and seamless CV↔CC with hardware flag accuracy (<0.5%) are mandatory. Borrow its **flag/hysteresis and range-change holdoff ideas** into the LT1970A firmware envelope (REQ-SAFE-002 secondary polygon). |

**Explicitly not selected in any phase without a new DEC:** OPA549/OPA544 (8 A/4 A, fixed limit, ±10 V min) — rejected as gross overkill with unacceptable offset and thermal overhead for ±10 mA.

---

## 8. Accuracy Note — Why LT1970A's Offset Is Acceptable for V1 (Provisioned Cal, Not Heroic)

REQ-MEAS-007 provisional target (post-cal, 25 ±3 °C, k=2): `±200 µV @0 V`, `±0.5 mV @1 V` (`0.02% rdg + 0.01% FS + 2 ppm/°C·ΔT`).

- LT1970A raw `200 µV Vos` **plus** `Ib·Rf` (e.g. `160 nA·5 kΩ = 0.8 mV`) would **fail** without cal.
- With **single-point offset cal at 0 V** (DMM-tied, stored in NVM) the residual is dominated by **drift** (`4 µV/°C·15 °C ≈ 60 µV`) + reference/ divider TC, not raw Vos — **inside ±200 µV**.
- Gain error is set by `Rfb` ratio and `ADR4525` class ref, not by LT1970A `Aol` — **design Rf/Rin with 25 ppm or matched network** and the ±0.5 mV @1 V budget closes.
- ADA4522-2 still wins on raw drift (`22 nV/°C` → `0.33 µV` over 15 °C), but LT1970A **after cal** wins on **system cost + compliance + disable** for a DC staircase SMU where NPLC 1–10 averages `en`.

**Consequence:** Phase 3 will publish the full `S1–S10/M1–M10` uncertainty stack per `UNCERTAINTY_BUDGET_FRAMEWORK.md` and a cal procedure per `REQ-CAL-001` before any accuracy DEC is accepted.

---

## 9. Kelvin & Burden Prescription for Phase 3 Schematic (CAUTION 2 Closure)

For the **selected LT1970A** path (and any future composite):

1. **Schematic:** Draw **two distinct sense pairs** — `LT1970A:SENSE+`/`SENSE−` across `Rsense` (10 Ω, 0.1%, 25 ppm, kelvin pads, low-ESL) and `SMU:SENSE_HI`/`SENSE_LO` across DUT (high-Z differential amp). Tie them **only at FORCE terminals** — never at the IC.
2. **Feedback:** `LT1970A −IN` is fed from **`SENSE−` (load side of Rsense)**, not from `OUT`. Optional footprints: `Riso = 1–10 Ω` (0201/0402) **before** `FORCE` and `Cf = 22–100 pF` across `Rfb` for lead-lag.
3. **FILTER:** Pad for `CFILTER` on LT1970A `FILTER → SENSE−` (DNP default, stuff 220 pF if ringing).
4. **Range burden:** Document per-range `Vburden@FS = 100 mV` and `Icc = f(VC)` law in the schematic notes; log `range_state` + `VC` with every sample.
5. **Verification:** 2-wire vs 4-wire delta on `10 Ω` and `1 kΩ` dummies (REQ-DUT-001); max-drop `5 V force–sense` test; open-sense detect; `CL = 10 nF` step with and without `Riso`.

---

## 10. Distributor & Lifecycle Spot Check (2026-08-24 — Informational, Not a Quote)

| Part | Package (prioritized) | DigiKey spot | Mouser spot | TI/ADI store | Lifecycle (mfg) | Note |
|------|------------------------|--------------|-------------|--------------|-----------------|------|
| **LT1970AIFE#PBF** | TSSOP-20 w/ pad | **~1.4k in stock** across ADI distributors per Octopart; **~$17.47 @1, ~$13.87 @100** (aggregator); ADI list **$6.87 @1k** | Newark/Farnell mirrors | ADI: Active, 4 models (CFE/IFE × PBF/TRPBF), rev 2015 | **Active — no PDN** (Aug 24) | Single-source; keep LT1970 (non-A, 2% limit, lower price) as second-source; verify TSSOP-20 thermal pad footprint. |
| **ADA4522-2ARMZ / ARZ** | MSOP-8 / SOIC-8 | **~600–4k per variant in stock**; **$6.39 @1, $3.71 @1k** | Similar, **$6.23 @1** | ADI: **Active** (Rev I 2025) | **Active** | Jelly-bean precision; used as SENSE amp regardless of source choice. |
| **OPA140AID / OPA2140** | SOIC-8 / SOT-23-5 | **In stock** (TI store + distribution) | In stock | TI: **Active** | **Active** | JFET precision alt to ADA4522; best bias current. |
| **OPA551PA / OPA551FA** | PDIP-8 / SOIC-8 / TO-263-7 | **PDIP out-of-stock spot**, SOIC/DDPAK in stock | Similar | TI: **Active** (Rev B 2016) | **Active** | FET 200 mA; PDIP is the cheap eval variant but not SMU-recommended. |
| **OPA548F/500** | TO-263-7 / TO-220-7 | **Active** | **Active** | TI: **Active** | **Active** | 3 A; gross overkill — not used for V1 core. |
| **OPA549 / OPA544** | Power ZIP-11 / TO-220-5 | Active but high-price power | Active | TI: Active | Active | **Rejected** — not quoted for V1. |

> **Method:** `web_search` across ADI/TI product pages + DigiKey/Mouser aggregator + Octopart/FindChips on 2026-08-24. All parts returned **Active** with no PDN/EOL notice. Prices are pre-tax, pre-shipping, single-unit vs 1k reel. **Re-check at Phase 3 DEC with `bom/sourcing/` live query.**

---

### Appendix A — DAC Comparison (IR-06 / IR-07)

| Device | System span | LSB | Supplies | Notes |
|---|---|---|---|---|
| **AD5686R** 0–5 V → ×2 → **±5 V** | 10 V | **152.588 µV** (10 V/65536) | Single 5 V (+ gain stage) | Requires external ×2 gain amp + resistor TC/gain error; INL ±2 LSB → ±305 µV in system volts |
| **AD5764** nominal **±10 V** (no ±5 V mode — IR-06) | **20.0 V** (21.0526 V at ±10.5263 V option) | **305.176 µV** nominal (20 V/65536); **321.2 µV** at ±10.5263 V | **±11.4–±16.5 V** (IR-07) | **No ±5 V range exists**; operating AD5764 for ±5 V wastes half the codes (resolution halved, LSB still 305 µV). INL ±1 LSB = ±305 µV — equal in volts to AD5686R system ±2 LSB. Advantage is **no external gain-stage error**, not INL alone. Raw ±12 V bench satisfies 11.4 V with ~0.6 V margin; **±10 V LDO rail cannot host AD5764** (IR-07). |
| **AD5764** ≠ 153 µV | — | Deprecated 153 µV claim for AD5764 was 10 V span mis-attributed — **superseded** | — | See PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md IR-06 |
| **AD5791-class** (if needed) | 20 V | 19.07 µV (20-bit) | ±7.5–±16.5 V | Only if LSB headroom at 0.1 V read demands it; higher cost; Q-01 trade |

Power-tree Options per IR-07: **A — Raw ±12 V for AD5764/LT1970A power stage** (simplest V1, precision +5 V regulated only), **B — Regulated complementary rails** (positive LT1763/LT3045-class + **negative LT1964/LT3091/TPS7A30-class** — LT1763/LT3045 are positive-only, not negative), **C — Separate rails for power stage vs precision chain**. Decision per actual error-budget headroom (PRELIMINARY_ERROR_BUDGET §1.2 post-cal @1 V: AD5764 headroom ≈+8.8% vs AD5686R −8.6% with gain stage) and calibration burden.

## 11. What Phase 3 Must Do Before Promotion (Gate Checklist — No DEC Without This)

- [ ] **Datasheet re-verification** — re-read LT1970A `1970afc.pdf` Rev + errata, clamp the table in §2.1 to page/line, attach to `DEC-01X` evidence.
- [ ] **SPICE gate** — LTspice model of LT1970A driving `±5 V` into `10 Ω‖+ 10 nF` and `1 kΩ + 10 nF` (cable `100 nH + 100 pF/m`) — AC (phase margin >45°) + transient (burst into compliance, staircase `0→+5→0→−5→0`) — save to `simulation/results/` per `REQ-GEN-001`.
- [ ] **Enable/POR bench** — scope `ENABLE` → `Hi-Z` with `Iout <1 µA`; brown-out ramp ≤6 V/µs test.
- [ ] **Quadrant-transition capture** (CAUTION 1) — `0→+2→0→−2→0` into `100 Ω` + `100 Ω‖10 nF`, log `Vout(t), I(t)`.
- [ ] **Burden closure** (CAUTION 2) — 2-wire vs 4-wire `ΔV = I·Rlead` + `Vburden = I·Rsense`; `FB = SENSE−` continuity test.
- [ ] **Compliance entry** — short via `0.5 Ω` + `1 nF` into `10 mA` limit, measure `I-overshoot <1%/5%`, `t_reg <50 µs`, flag latency.
- [ ] **Cal & uncertainty** — draft `UNCERTAINTY_BUDGET_FRAMEWORK` numbers for LT1970A path + `docs/calibration/` procedure; DMM tie at `−2,−1,0,+1,+2 V` (REQ-MEAS-007).
- [ ] **Thermal & SOA** — compute `Pd(max)` hyperbola `|V·I| ≤ 60 mW` and log `TMP117` on `LT1970A` pad.

---

## 12. References (Primary Datasheets + Phase 1 Provenance)

1. Analog Devices — **LT1970A** 500 mA Power Op Amp with Adjustable Precision Current Limit, `1970afc.pdf` (Rev 2015-11-11) — ADI product page `analog.com/en/products/lt1970a.html` (LTspice model + DC453A/B demo boards)
2. Analog Devices — **LT1970** (non-A, 2% tol) `1970fe.pdf` — same die, fallback
3. Analog Devices — **ADA4522-1/2/4** Zero-Drift, `ada4522.pdf` Rev I (2025-01-08) — 55 V, 5 µV, 22 nV/°C, 5.8 nV/√Hz, 50 pA
4. Texas Instruments — **OPA140 / OPA2140 / OPA4140**, `opa140.pdf` Rev F (2023-03-28) — 5.1 nV/√Hz, 10 pA, 11 MHz, TINA-TI model `SBOM430E.ZIP`
5. Texas Instruments — **OPA551/OPA552**, `opa55x` Rev B (2016-01-07) — ±200 mA, 3 MHz, FET input
6. Texas Instruments — **OPA548**, `opa548.pdf` Rev D (2019-12-18) — 3 A/5 A, adjustable limit, E/S
7. Texas Instruments — **OPA549** Rev E (2005) / **OPA544** (FET 2 A, fixed limit) — power-family comparison
8. ReRAM-SMU V1 Phase 1 — `docs/research/SMU_ARCHITECTURE_SURVEY.md` (Arch A–D taxonomy), `docs/research/COMPLIANCE_RESEARCH.md` (compliance triad, DEC-011), `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md` (100 mV FS), `docs/calculations/UNCERTAINTY_BUDGET_FRAMEWORK.md`, `docs/research/PHASE1_RESEARCH_SUMMARY.md`, `REQUIREMENTS.md v0.2.0`, `DECISIONS.md DEC-007..012`, `docs/architecture/REQUIREMENTS_TRACEABILITY.md`

---

## 13. Phase 3 Gate 6 Evidence Update (2026-08-24 — Tests N+O, no footprint selection)

**Evidence:** `simulation/phase3/dac_adc/test_N_dac_comparison.py` (1000 runs/point, 2-pt cal −5/+5V, INL code-dependent, quant, 0.01%/0.1% ratio, TC, drift), `source_A/B/C` `candidate_*_transient.cir` ngspice-47 + `.dat` (1k+100pF/10nF, AC decode), `monte_carlo/test_O_monte_carlo.py` (DC/Kelvin/compliance/stability calc), `docs/calculations/PHASE3_ERROR_BUDGET.md` (Type A/B, noise per range, NPLC FAST/NORMAL/LOW NOISE, range-change blanking), `simulation/phase3/MODEL_LIMITATIONS.md` (per-gate table), `simulation/results/phase3/gate6_source_dac.md` (verdicts). **No footprint selected.**

| Candidate | Gate 6 result | DC @2V/1kΩ cal | Kelvin 10Ω @2V | Cap 10p/100p/1n/10n PM | OS 100p/10n ngspice | Compliance CV→CC snap 1M→300Ω 1µs | Load reg 100Ω↔1MΩ @2V | Verdict retained |
|-----------|---------------|-----------------|----------------|-----------------------|---------------------|----------------------------------|----------------------|------------------|
| A LT1970A direct | MC RMS 35µV @2V, offset 12µV cal | 5.1µV after Riso (20mV naive) | 50° @10nF (Riso33Ω Cf33p fz482kHz fp2 482kHz) PASS, 85° @10p | 0.2%/6.5% PASS (<10%) | Ipk 10.4mA 4% into 1nF t_reg20µs flag4µs PASS | 13µV | **SELECT (primary)** — §7 of gate6_source_dac.md |
| B ADA4522+BJT inside loop | RMS 1.5µV, offset 0.7µV | 0.7µV | 60° @10nF (Riso47Ω Cf100p) PASS pref >60° | 0.0%/3.2% PASS | 11.2mA 12% t_reg60µs FAIL timing >50µs coarse trip (TLV3501 26% tol) | 3.3µV | **KEEP AS FALLBACK** (also SENSE diff-amp; standalone REJECT as SMU core) |
| C nested outer ADA4522+inner LT1970A | RMS 2µV, offset 4µV | 4µV | 57° analytic PASS but ngspice 10n OS 16.6% marginal (Cf opt needed) | 0.05%/16.6% marginal | 10.3mA 3% t_reg25µs PASS | 6µV | **REQUIRES PROTOTYPE** (lab, not PCB) — inner Vs outer lead-lag 1k+10n zero 16kHz, Cf_outer47p, fb after Riso |

DAC companion: AD5764 SELECT (§1 of gate6_source_dac.md, 305µV LSB on 20V, half-codes 3% of 10mV, post-cal +46% @2V, supply ±11.4V via raw ±12V Option A), AD5686R 0.01% KEEP AS FALLBACK (REJECT 0.1%), AD5791 REQUIRES PROTOTYPE only if 16-bit fails. ADC: AD7175-8 primary for FAST + autorange (20µs scan), ADS1262 fallback for NORMAL/LOW NOISE (NPLC 2.5–10).

*Do not select final footprints — V1 REV-A footprints remain TBD pending Phase 4 bench (quadrant-transition 0→+2→0→−2→0, compliance short 0.5Ω+1nF, relay therm EMF, leakage vs humidity/40°C).*

## 13. Changelog

- 2026-08-24 — Initial issue — Agent A — covers LT1970A vs `OPA140/ADA4522+buffer` vs `OPA548/551` vs composite vs dedicated `source/sink` for `±5 V/±10 mA/10 pF–10 nF`; distributor spot check; CAUTION 1/2 closure; recommendation `SELECTED: LT1970A` / `DEFER: all others` for Phase 3.
- 2026-08-24 — Gate 6 update — Phase 3 evidence injected (Tests N+O MC 1000 runs/point, ngspice-47 transients 1k+100pF/10nF, stability PM>45°) — verdicts SELECT A / KEEP B / REQUIRES PROTOTYPE C / REJECT OPA548, DAC AD5764 SELECT; no footprint selection.

---

*No schematic, PCB, or BOM is created or modified by this document. Promotion of any candidate to a `DEC-XXX ACCEPTED` requires the gate in §11 plus `ENGINEERING_RULES.md` review.*
