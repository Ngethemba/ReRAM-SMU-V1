# Measurement Front-End Candidates — Shunt / TIA / Hybrid & Switching

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**Status:** CANDIDATE ARCHITECTURE — no selection; promotes only via DECISIONS.md with datasheet + measurement  
**Requirements:** REQ-MEAS-001 (6 ranges 10 mA→100 nA), REQ-MEAS-002 (MUC 1 nA, Johnson 0.41 pA @100 nA/10 Hz), REQ-MEAS-004/005/008, REQ-SRC-003/005 (4-quad), REQ-SAFE-001 (HW compliance), REQ-DUT-001 (Kelvin), REQ-PWR-003  
**Companion docs:** `docs/calculations/SHUNT_RANGE_TRADEOFF.md` (R/power/noise/gain tables), `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md`, `docs/calculations/NOISE_BUDGET_FRAMEWORK.md`, `docs/research/LOW_CURRENT_MEASUREMENT.md`, `docs/research/SMU_ARCHITECTURE_SURVEY.md`, `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md`

> **Deliverable scope:** No KiCad. This is the Phase-2 front-end trade that feeds schematic. Every quantitative claim cites a calc or a datasheet to be verified in Phase 2.

---

## 1. Summary recommendation (preview — not a DEC)

| Decision | Recommended candidate | Fallback |
|---|---|---|
| Shunt vs TIA vs hybrid | **Hybrid: shunts 10 mA→1 µA, TIA-ready for 100 nA** (but V1 ships as shunts-only with TIA footprint provision) | All-shunt 10 mA→100 nA (simplest, proven) |
| Burden philosophy | **Range-dependent D per SHUNT_RANGE_TRADEOFF §2.4 (IR-05)** — 10 mA 25 mV (2.5 Ω), 1 mA 25 mV (25 Ω), 100 µA 50 mV (500 Ω), 10 µA 50 mV (5 kΩ), 1 µA 100 mV (100 kΩ), 100 nA 100 mV (1 MΩ) — canonical, not fixed 100 mV | Fixed 100 mV on all ranges (Phase 1 baseline, superseded) |
| Placement | **Low-side shunt with Kelvin + forced guard-friendly layout**; high-side is alternative if compliance loop demands it — §3 | High-side shunt (if 4-quad compliance needs common-mode) |
| Range switching | **Reed relay (signal-grade, low-thermal) for 100 nA/1 µA**; **PhotoMOS or low-leakage CMOS mux for 10 µA→10 mA only if leakage verified** — §4 | All-reed-reed (6× reed) for uniformity |
| ADC strategy | **Hybrid: fixed shunt FS per §2.4 + per-range PGA (ADS1262 PGA 1–32)** — §5 | Fixed FS + fixed gain (simplest, wastes DR on low burden) |

These are **candidates**; Phase-2 DEC will close them after relay/switch leakage measurement and output-stage headroom simulation.

---

## 2. Shunt vs transimpedance (TIA) vs hybrid

### 2.1 Definitions

* **Shunt (resistive):** `V_shunt = I·R_shunt` in series with DUT. Measured differentially (instrumentation/diff amp → ADC). Burden = `I·R`. Johnson `vn = √(4kTRB)`, `in = √(4kTB/R)`. R as in SHUNT_RANGE_TRADEOFF.md.
* **TIA (feedback ammeter):** DUT current forced into op-amp virtual ground; `Vout = −I·Rf`. Burden `≈ Vos/Aol + Ib·R_source` ≈ 10–200 µV (often <20 µV on 100 nA per NI PXI-4022 spec) — essentially zero series voltage. Johnson is identical for same `Rf = R_shunt` — feedback resistor noise is indistinguishable from shunt noise. Stability needs `Cf` compensation (`Rf‖Cf` pole).
* **Hybrid:** Shunts for high/mid-I, TIA for low-I. Relay selects path. Commercial pattern: Keysight B2900 / Keithley 2600 use shunts to ~1 µA then TIA/electrometer below.

### 2.2 Comparison matrix (6 ReRAM ranges, V1 context)

| Criterion | Shunt only (10 mA→100 nA) | TIA only (all ranges) | **Hybrid: shunt 10 mA→1 µA + TIA 100 nA (±1 µA)** |
|---|---|---|---|
| **Burden** | 25–100 mV (range-dep) | <0.2 mV typ | 25–50 mV (mA/µA) + <0.2 mV (nA) — best of both |
| **Headroom cost** | FORCE must supply V_DUT+burden | Negligible | Negligible on nA; mA headroom still paid but less often at HRS reads |
| **Johnson floor** | Table §2.1 SHUNT doc (0.41 pA @100 nA/10 Hz) | Identical for same Rf | Identical — TIA does not improve thermal noise, only burden |
| **Settling** | `τ=R·C` 50 µs @1 MΩ/50 pF → 250 µs 5τ + DA seconds | TIA settling and stability are set by `Rf`, `Cf`, input capacitance (DUT + cable), op-amp GBW, noise gain, and phase margin — not by `R_shunt` alone; a TIA can be faster than a shunt only when its integration capacitor and compensation are sized for the specific `Rf`/`Cin`/`C_DUT` and validated for phase margin (IR-09, provision-only) | Fast on TIA range when validated; shunt ranges limited by RC+DA |
| **Stability** | Unconditional (resistive) | Needs per-Rf Cf tuning, phase margin vs C_DUT (nF) | TIA range needs compensation; shunt ranges trivial |
| **Output swing** | Diff amp handles ±100 mV | `I·Rf` must fit op-amp swing (100 mV FS still) | Same swing constraint on TIA |
| **Power / SOA** | Shunt dissipates I·V (1 mW @10 mA/100 mV) | Op-amp supplies I·V (same) plus quiescent | Same |
| **Leakage sensitivity** | Relay/PCB leakage shunts R (1 MΩ → 1 pA per 100 mV/100 GΩ) | Virtual-ground leakage + Ib + guard design | TIA virtual ground is **more** leakage-sensitive — needs guard ring, Teflon, electrometer amp |
| **Component count** | 6 shunts + mux + diff amp | 6× Rf+Cf + precision op-amp (low Ib/Vos) + guard | Most complex; relay selects shunt bus vs TIA input |
| **Proven for V1 MUC 1 nA** | Yes — with guard provision, 1 MΩ/100 mV gives Johnson 0.41 pA ≪ 1 nA; leakage is the limiter (see LOW_CURRENT §3) | Yes — but needs electrometer-grade amp (ADA4530-1 class, Ib<1 fA) + triax | Yes — best margin on 100 nA guard |
| **Commercial precedent** | Erickson DIY-SMU (shunt to 1 µA) | Lab electrometer (Keithley 6517) | Keysight HRSMU / Keithley 2600B — shunts to µA, TIA below |
| **Phase-2 risk** | Lowest — no stability loop | Highest — compensation vs C_DUT + guard PCB | Medium — TIA section is additive |

### 2.3 Why TIA does **not** automatically win at 100 nA

Two misconceptions to avoid:

1. *“TIA eliminates Johnson.”* False. `Rf` Johnson is identical to shunt `R` Johnson for same FS. TIA eliminates **burden**, not noise.
2. *“TIA eliminates leakage.”* False. Virtual-ground leakage (op-amp `Ib` + PCB surface + `Rf` leakage) replaces shunt leakage. At 100 nA / 1 MΩ, 1 pA leakage is 1% of reading — both topologies need the same guard/purity discipline. TIA at 10 GΩ PCBs without guard is not better; it is often worse because the summing node is high-impedance and exposed.

### 2.4 Recommendation and provisioning

* **V1 baseline: all-shunt 10 mA→100 nA** is sufficient to meet REQ-MEAS-002 quantified (detection 3σ 1.5–6 pA, practical MUC 1 nA ≈10% FS) with averaging/shielding and leakage correction. This is the lowest-risk path and matches Erickson DIY-SMU precedent.
* **Provision TIA for the 100 nA range** on the PCB: lay out a footprint for a low-Ib op-amp (ADA4530-1 class) with `Rf = 1 MΩ` (range-dep 100 mV FS → 100 nA) + `Cf` + guard ring, selectable by a DNP relay. Do not populate for V1 REV-A unless Phase-2 leakage measurement shows shunt leakage marginal. This costs one op-amp footprint + guard copper, and de-risks V2 (10 nA) where TIA becomes mandatory.
* **Hybrid (shunt 10 mA→1 µA, TIA 100 nA)** becomes V1.1 if 100 nA guard/shield data shows shunt leakage >0.5 pA systematic after guard — decide from measurement, not from simulation.

---

## 3. Placement: high-side vs low-side vs floating / remote-sense

“High-side” and “low-side” refer to **where the current sensor sits relative to the DUT and the return**.

### 3.1 Topologies

```
High-side shunt:  FORCE_HI → [SHUNT] → DUT_HI──DUT──DUT_LO → FORCE_LO (return)
                  diff amp sees shunt at ≈V_FORCE common-mode

Low-side shunt:   FORCE_HI → DUT_HI──DUT──DUT_LO → [SHUNT] → FORCE_LO
                  diff amp sees shunt near 0 V common-mode (ground-referenced)

Floating / remote-sense: FORCE_HI/LO are driven differentially; shunt is inside
                         the floating source; SENSE_HI/LO are Kelvin at DUT.
                         Compliance and guard are referenced to the floating common.
```

### 3.2 Comparison (4-quad context, ±5 V, ±10 mA)

| Criterion | **Low-side** (RECOMMENDED for V1) | High-side | Floating / remote-sense (ideal, more complex) |
|---|---|---|---|
| **Common-mode** | ~0 V (near ground). Diff amp / ADC can be ground-referenced, low CMRR needed. | Up to ±5 V CM (full FS). Needs high-CMRR diff amp (INA / ADA4522) or isolated sense. | Shunt CM is internal floating; external diff is at DUT. Needs isolation or diff supply. |
| **Amplifier needs** | Simple: ground-referenced, low Vos, low Ib; single-supply possible. | High-CMRR, wide CM range, high PSRR; often needs dual supplies or CM-tolerant topology. | Floating supply + isolation amp + careful star point. |
| **Kelvin correction** | Works, but burden is **outside** the Kelvin loop if SENSE is at DUT — FORCE must still drive V_DUT+burden. Lead R compensated; burden not magically removed. | Same: burden is still outside Kelvin unless shunt is Kelvin-sensed separately. | Kelvin naturally at DUT; floating reference can include burden in loop if shunt is inside regulation. |
| **Compliance / 4-quad** | Compliance must sense current regardless of placement — low-side is fine, but sink current polarity needs bipolar diff amp / sign handling. | High-side naturally bidirectional with same diff amp; Kelvin-force loop includes burden symmetrically. | Most elegant for 4-quad: floating source absorbs sink without ground bounce. |
| **Guarding** | Easy: low-side node near ground is low-leakage; guard ring to ground plane. | Hard: high-side guard must track V_FORCE (driven guard). Needs buffer. | Hardest: guard must track floating common; needs isolated driven guard. |
| **Grounding / return** | Single star point at FORCE_LO / shunt return. Digital ground partitioned. | Star point at DUT_LO; shunt return is not ground — care with ground loops. | Two domains: floating analog + ground-referenced digital; isolation bridge. |
| **Fault / ESD** | Shunt near ground is safer for ADC input (clamp). | Shunt at ±5 V needs overvoltage protection on diff amp inputs (resistor + clamp). | Floating adds isolation-barrier ESD path. |
| **Cable / lead R** | Lead R on HI side adds to force loop; Kelvin SENSE corrects DUT voltage. | Lead R split both sides; same Kelvin logic. | Kelvin corrects both force leads. |
| **Commercial precedent** | Common for bench SMU low-cost (ground-referenced sense) | Common for high-side current monitors (INA250 etc.) | High-end SMU (Keithley 2450) — floating source |
| **V1 risk** | Lowest — simplest, fewest high-CM pitfalls | Moderate — CMRR/PSRR budget needed | Highest — isolation + floating supply |

### 3.3 Why low-side is V1-recommended (with caveats)

* **Recommended: LOW-SIDE shunt outside Kelvin sense loop (SENSE encloses DUT only, burden outside loop — headroom 100 mV not corrected by Kelvin, must be budgeted).** This matches KELVIN_SENSE_ARCHITECTURE.md §1.2 option A: SENSE_HI/LO at DUT_HI/LO, shunt between DUT_LO and FORCE_LO. Kelvin corrects `I·R_lead` but **not** `V_burden = I·R_shunt`; FORCE must supply `V_DUT + V_burden + I·R_lead`. With range-dep burden (25 mV on 10 mA/1 mA) worst headroom is only 25 mV on high-I where sink compliance matters most.
* **Lowest amplifier and guard burden:** Low-side is ground-referenced single-ended (or low-CM diff) — ADA4522-2 class zero-drift meets Vos/TCVos without high-CM tricks; guard can be passive copper pour to ground on the 100 nA node. **High-side shunt needs a true differential amp with wide CM (±5 V) and high CMRR/PSRR** — INA / diff-amp with matched resistors, dual supplies or CM-tolerant topology, higher cost and error budget.
* **Sufficient for REQ-SRC-005 4-quad:** Bidirectional measurement is handled by bipolar supply on the force stage + bipolar diff/single-ended amp + sign in firmware. The 4-quad issue is the **output stage** (sink), not the sense placement.
* **Caveat:** If compliance regulation (§6 of KELVIN doc) is implemented as a **current-loop error amp** (classic SourceMeter B topology), the current loop may want the shunt **inside** the force feedback — which is more natural high-side/floating. Phase-2 must decide compliance topology (series-pass vs shunt-clamp vs loop-OR) before freezing placement. **Provision both:** lay out shunt footprints Hi and Lo with DNP/resistor-OR so the DEC can choose without PCB respin.

### 3.4 Floating / remote-sense — when it matters

Floating is justified when: (a) DUT is truly floating (no chassis bond) and ground-loop hum dominates nA floor; (b) output stage needs clean sink without ground bounce; (c) driven guard must track V_FORCE accurately (V2 electrometer). For V1, a **remote-sense Kelvin pair** (FORCE_HI/LO driven, SENSE_HI/LO measured at DUT) already gives most of the benefit without full floating. Keep analog supply ground-referenced, partition digital via ferrite/star, and route SENSE as a Kelvin pair — see KELVIN_SENSE_ARCHITECTURE.md.

---

## 4. Range-switch technology (6 ranges, focus 100 nA / MUC 1 nA)

Switch selects which `R_shunt` (or TIA `Rf`) is in circuit. OFF-leakage, contact resistance, capacitance, dielectric absorption (DA), thermal EMF, and lifetime dominate at 100 nA.

### 4.1 Candidates

| Technology | Example class (verify datasheet) | OFF leakage | R_on / contact | Capacitance | Thermal EMF | Lifetime | Drive |
|---|---|---|---|---|---|---|---|
| **Reed relay** (signal, low-thermal) | Coto 9000, Standex-Meder, Pickering 100-series | <1 pA (glass seal, guarded) | <100 mΩ | ~1 pF open | <1 µV (low-thermal) | 10^8 ops mechanical | Coil + flyback |
| **Signal relay** (EM, non-reed) | Omron G6K, Panasonic TQ | 10 pA–1 nA (plastic, flux leakage) | <50 mΩ | ~2 pF | 1–5 µV | 10^6 ops | Coil |
| **PhotoMOS / solid-state relay** | Panasonic AQY212S, AQV25x | ~1 pA–1 nA (photovoltaic leakage) | 0.5–10 Ω | ~10–50 pF | ~0 µV (no thermocouple) | Unlimited (solid-state) | LED drive |
| **CMOS analog switch / mux** | ADG1419, ADG1408, DG412 | 10 pA–1 nA per switch (25 °C; doubles ~10 °C) | 1–10 Ω | 5–30 pF per channel | ~0 µV | Unlimited | Logic |
| **JFET / discrete low-leakage** | JFET clamp (custom) | <10 pA (if guarded, selected) | ~10 Ω (Rds) | ~5 pF | ~0 | Unlimited | Gate drive |

*Values typical; **every** leakage/R_on/EMF number must be re-verified against the chosen part's datasheet at 25 °C and 40 °C (leakage doubles ~10 °C).*

### 4.2 Quantitative impact at 100 nA / 1 MΩ

Leakage budget at MUC: REQ-MEAS-008 allows ~60 pA systematic at 50 nA (0.3% reading + offset). Johnson is 0.41 pA — leakage dominates. Requirement is **leakage-corrected** accuracy, but uncorrected leakage must be <~5 pA to keep residual after cal <MUC.

| Ratio | Consequence |
|---|---|
| OFF-switch leakage 1 pA | 1% of 100 nA FS, 20% of MUC (1 nA) — significant; must be guard-compensated or cal'd |
| OFF-switch leakage 100 pA | 100% of 1 nA MUC — **fails** without guard |
| R_on 0.1 Ω (reed) on 10 mA/2.5 Ω shunt | 4% series error if not Kelvin-sensed — needs 4-wire shunt sensing |
| R_on 5 Ω (PhotoMOS) on 10 mA/2.5 Ω | 200% error — **unusable** on low-R ranges without Kelvin or buffer |
| C_open 30 pF on 1 MΩ shunt | Extra τ = 30 µs — OK for DC, but charge injection on switch (pC) creates 30 mV transient (Q/C) → needs dwell blanking |
| Thermal EMF 5 µV on 100 mV FS | 50 ppm systematic — cal'able, but drifts with coil heat → prefer low-thermal reed |

### 4.3 DA (dielectric absorption) note

Flux residue, relay potting, and FR-4 absorb charge and release over seconds — visible as nA tail after a range change or bias step. Guard copper + cleaning (isopropanol, no-clean with guard gapping) + DNP conformal coat on low-I node is mandatory. CMOS switch DA is often worse than reed due to package dielectric.

### 4.4 Recommendation

* **100 nA and 1 µA ranges: reed relay, low-thermal, hermetically sealed (Coto/Pickering class).** Lowest OFF leakage (<1 pA) and lowest DA; break-before-make sequencing; flyback diode + RC snubber; coil drive with 10 ms settle blanking.
* **10 µA / 100 µA / 1 mA / 10 mA: reed relay is also acceptable** (all-reed 6-relay matrix is the simplest uniform BOM and avoids mixed-leakage surprises). **Alternative:** PhotoMOS for mid/high ranges if relay count/lifetime is a concern — but **only after** measuring OFF leakage <1 pA at 40 °C and verifying R_on ≤0.5 Ω with Kelvin sensing (PhotoMOS R_on drifts with LED current and temp).
* **Avoid CMOS mux on the 100 nA path** unless the part is explicitly low-leakage (ADG14xx “low-leakage” variant) and measured — typical DG412 leakage 100 pA would violate MUC.
* **Break-before-make is mandatory** (make-before-break would short shunts). Sequence: disable output or clamp to 0 V → open old relay → 5 ms coil settle → close new relay → 10 ms DA blanking → resume. Firmware must log range state per sample; compliance flag inhibits autorange during a limit event.
* **Shunt Kelvin:** Each R_shunt gets a 4-wire Kelvin sense pair (separate sense traces to diff amp) so relay R_on does not enter the measurement equation. Without Kelvin, reed 0.1 Ω on 2.5 Ω (10 mA) is 4% error — unacceptable.
* **Lifetime:** Reed 10^8 ops → >10 years at 100 range-changes/hour; not a limiter for lab SMU.

---

## 5. Fixed FS vs PGA vs hybrid (ADC strategy)

### 5.1 Taxonomy

* **Fixed FS (fixed gain):** Shunt FS (e.g., 100 mV) → fixed gain → ADC at PGA=1. Simplest; ADC dynamic range is wasted on low burden (25 mV would use only 1% of 2.5 V FS).
* **PGA (programmable gain):** Shunt FS varies, PGA compensates per-range to fill ADC FS. Example: ADS1262 PGA=1,2,4,8,16,32 (gain = Vref/PGA). 100 mV→PGA≈32 would be ~3.9 mV FS per code? Actually PGA 32 gives diff FS = ±78 mV — near-perfect for 100 mV with slight attenuation.
* **Hybrid:** Per-range shunt FS (range-dep D) **plus** per-range PGA. Gives best DR utilisation and SNR; needs per-range cal gain+offset.

### 5.2 Quantitative (from SHUNT_RANGE_TRADEOFF §5)

| Strategy | 10 mA (25 mV) gain to 2.5 V | 100 nA (100 mV) gain to 2.5 V | DR utilisation @2.5 V FS | Amp noise penalty |
|---|---|---|---|---|
| Fixed 100 mV, PGA=1 | 25× (wasted 75 mV headroom) | 25× | 100% on 100 mV; 25% on 25 mV if mixed | 25× on all |
| Fixed 25 mV, PGA=1 | 100× | 100× | 100% on 25 mV; low-I over-amplifies `en` | 100× on all — worse |
| PGA only (100 mV FS → PGA 32) | PGA≈32 → FS 78 mV | PGA≈32 → FS 78 mV | 78–100% | PGA noise adds but less than external gain |
| **Hybrid D + PGA (REC)** | 100 mV-eq: PGA 3.1× (≈25 mV→78 mV) | PGA 0.78× (100 mV→78 mV, slight atten) | **~100% every range** | **Minimal — PGA handles range scaling** |

### 5.3 Recommendation

**Hybrid — range-dependent shunt FS + per-range PGA** (ADS1262 PGA per range, or equivalent ΔΣ).

* Gives ~100% DR utilisation on every range without heroic external gain.
* Low-I ranges (1 µA/100 nA) at 100 mV FS use PGA ≤1 (or unity buffer) — no extra `en` amplification where `en` already competes with Johnson.
* High-I ranges use PGA 1.5–3.1× — modest, low-noise internal PGA.
* Costs only per-range PGA setting + per-range gain/offset cal (already required for 6-range autorange). Firmware logs `{range, PGA, shunt, cal_gain, cal_offset}` per sample.
* Fallback: fixed 100 mV FS + PGA=32 uniform is acceptable if per-range PGA sequencing is deferred — wastes 75 mV of headroom on high-I but simplifies firmware.

**Anti-alias / Sinc filter note:** ΔΣ Sinc filter + decimation sets effective BW; PGA and shunt RC jointly set ENBW (§6 SHUNT doc). Settling after PGA/range change needs Sinc flush (ADS1262: `t_settle ≈ 2–3 / data_rate`) — budget 10–20 ms blanking after switch before valid sample.

---

### 5.4 Bipolar front-end taxonomy (IR-12) — topologies A/B/C for Phase 3 test G

Per MEASUREMENT IR-12: low-side shunt voltage changes sign in source vs sink quadrants (±Vshunt). Each range (10 mA…100 nA) must measure +FS/−FS/zero/±0.01·FS/±0.10·FS around zero for each ADC candidate (ADS1262 vs AD7175-class vs alternatives) evaluating input range, bipolar supply, CM limits, PGA restrictions, buffer behavior, zero-crossing.

- **A — True bipolar output from sense amp** (dual supplies ±5 V, diff output centered at 0 V, ADC differential bipolar)
- **B — Level shift around ADC midscale** (single-supply amp + VCM 2.5 V/1.65 V, shunt ±V maps to midscale ±gain)
- **C — Differential ADC directly** (INA + differential ADC inputs, CM at GND, requiring ADC with bipolar input or external level shift)

Phase 3 test G reports per-range × per-ADC feasible topology and leakage/NPLC budget. No schematic until then.

### 5.5 Guard cross-ref (IR-10)
Guard strategy per GUARD_STRATEGY.md: **passive keepout / clean high-Z zone** (no-mask, 0.5 mm gap), **grounded shield** (1 MΩ||10 nF bleed), **driven guard** (low-leakage follower powered from normal rails, input tracks high-Z sense node, output drives guard — not powered through 1 GΩ from SENSE_HI — IR-10). V1 REV-A: no driven guard stuffed, no arbitrary ground guard around SENSE_HI; keepout + optional driven-guard footprint; §6 leakage budget assumes this.


## 5a. Bipolar Current Front-End (IR-12) — Topologies for ±Vshunt

Low-side shunt voltage changes sign: sourcing +10mA → shunt +Vs, sinking -10mA → -Vs. ADC must handle ±Vshunt and zero crossing.

| Topology | Supply | How it handles -Vs | CM limit | When it fits |
|---|---|---|---|---|
| **A — True bipolar output from sense amp** | ±5 V dual supplies, diff output centered at 0 V | Sense amp drives bipolar; ADC in differential bipolar mode (e.g., AD7175 with ± supplies or ADS1262 differential bipolar) | Wide CM (~0 V ground-ref) but needs dual supply for amp | Preferred if amp can run dual and PCB allows |
| **B — Level shift around ADC midscale** | Single +5 V, VCM=2.5 V (or 1.65 V) | Single-supply amp with VCM shift: shunt ±Vs maps to ADC code midscale ± gain·Vs; 0 V shunt at midscale code | ADC single-supply; amp CM must include GND + VCM offset | Fits ADS1262 single-supply 5 V mode; needs precision VCM reference |
| **C — Differential ADC directly** | Instrumentation amp + differential ADC inputs | In-amp handles ground-ref shunt differential (FORCE_LO reference), ADC differential input captures bipolar without level shift; CM at GND | ADC must handle bipolar diff near GND — requires input buffers enabled or external shift if ADS1262 internal PGA buffer CM restricts | Best CM rejection but buffer noise/leakage tradeoff |

Phase 3 must evaluate each topology per ADC candidate (ADS1262 vs AD7175-class): input range, bipolar supply requirement, CM limits, PGA restrictions, buffer behavior, zero crossing error, negative shunt signal measurement. No final schematic; Phase 3 test G covers +FS/-FS/zero/small bipolar per range.

## 6. Risks & Phase-2 verification

| Risk | Mitigation | Verification |
|---|---|---|
| Reed leakage >1 pA at 40 °C | Guard ring + cleaning + sealed reed; measure open-input leakage 100 s per range | Bench leakage test (shorted + open DUT) at 25/40 °C, 100 nA range, report mean±σ; REQ-MEAS-002 quantified |
| PhotoMOS R_on drift / leakage | Kelvin shunt sensing + selection/characterisation | R_on vs T and Ileak vs Vcom sweep; compare to reed baseline |
| DA tail after range change | Guard gapping + no-clean flux control + dwell blanking | Step-response capture (scope on shunt diff amp) 0→FS, measure tail to 1% |
| High-side CMRR fails at ±5 V | Stay low-side unless compliance topology forces high-side — then qualify CMRR | Diff amp CMRR sweep −5→+5 V, measure gain error |
| PGA gain error / offset | Per-range cal vs precision resistor; firmware applies correction | 6-point resistor calibration (1 MΩ 0.01%, etc.) per REQ-MEAS-008 |
| 4-quad sink oscillation | Output-stage compensation into capacitive DUT (C_DUT up to 10 nF) | Load-step (R || C) quadrant-transition scope capture |

---

## 7. Open decisions for DEC

1. Final shunt R values (E96 nearest, TC 10 vs 25 ppm, power rating, network vs discrete).
2. Reed part number (Coto vs Pickering — datasheet OFF-leakage and thermal EMF side-by-side).
3. PhotoMOS vs all-reed on mid/high ranges (conditional on leakage data).
4. Compliance topology lock (affects placement — low-side vs high-side) — see KELVIN doc §2.
5. ADC primary (ADS1262 vs alternatives) and final PGA table per range.

---

## 8. Phase 3 Gate 6 Evidence Update (2026-08-24 — Tests N+O, no footprint selection)

**Evidence:** `docs/calculations/PHASE3_ERROR_BUDGET.md` (post-cal Type A/B, noise per range, NPLC FAST/NORMAL/LOW NOISE, range-change blanking), `simulation/phase3/MODEL_LIMITATIONS.md`, `simulation/results/phase3/gate6_source_dac.md` §2, `simulation/phase3/monte_carlo/test_O_monte_carlo.py` (DC offset/load regulation, Kelvin 0–10Ω, compliance snap, stability calc 50–60° PM).

**Per-range error after Gate 6 (philosophy D, per-range amp, 0.01% on 100nA/1µA, reed, OPA140 JFET for low-I):** 10mA@5mA U 5.9µA +48% headroom, 1mA@500µA 0.59µA +48%, 100µA@50µA 59nA +73%, 10µA@5µA 5.9nA +75%, 1µA@500nA 80pA +98%, 100nA@50nA 60pA +71% (with max Vos 120µV +0.1% shunt → 248pA −18% → need 0.01% + typ Vos). **Johnson at 10Hz ENBW:** 100nA 1MΩ 0.51pA + OPA140 3.24pA → 3.28pA rms; detection 3σ 9.8pA, quantitative 10σ 32.8pA, MUC 3×U 180pA → consistent REQ-MEAS-002 quantified. **Chopper ADA4522 rejected for 100nA** (160pA noise vs 0.51p Johnson) — per-range amp mandatory (§6 of FRONTEND_CANDIDATES).

**NPLC / data-rate:** FAST 10–20ms (44Hz BW ~0.86pA Johnson) via AD7175 20µs scan fits 10mV/50ms step with relay 1–3ms + Sinc flush 2–3×1/data_rate; ADS1262 at 20SPS 50ms cannot complete 10mV/50ms → must run ≥100SPS for FAST; NORMAL 50–100ms (NPLC 2.5–5) recommended for sweeps with 130dB @50Hz notch; LOW NOISE 200ms–1s (NPLC 10–50) for HRS read. **Range-change samples:** first 1–3 samples after switch within 5ms coil +10ms DA blanking + filter flush must be discarded/flagged; after blanking, NORMAL/LOW NOISE samples valid without discard → confirmed sweep CAN be met without discarding ALL post-range-change samples, but immediate post-trip samples must be discarded per `MEASUREMENT_FRONTEND_CANDIDATES.md §4`.

**No footprint selected** — footprints remain TBD pending Phase 4 bench (leakage vs humidity/40°C, DA tail, PGA gain error, 4-quad sink oscillation scope capture).

*Traceability: REQ-MEAS-001/002/004/005/008, REQ-SRC-005/006, REQ-SAFE-001, REQ-DUT-001/003, Q-05/Q-06, DEC-008/009, SHUNT_RANGE_TRADEOFF.md (Python-verified), LOW_CURRENT_MEASUREMENT, SMU_ARCHITECTURE_SURVEY.*
