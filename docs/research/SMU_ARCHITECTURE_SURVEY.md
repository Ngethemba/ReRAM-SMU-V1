# SMU Architecture Survey — Conceptual Comparison (No Selection)

**Project:** ReRAM-SMU V1 — Phase 1 Research  
**Date:** 2026-08-24  
**Status:** `DRAFT / RESEARCH ONLY — NO SELECTION` — satisfies OPEN_QUESTIONS Q-03/Q-04/Q-05/Q-07 without deciding. All candidate components (STM32G431, AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525-class) remain `PROVISIONAL / REQUIRES VERIFICATION` per DECISIONS.md.  
**Requirements in scope:** REQ-SRC-001..007, REQ-MEAS-001..005, REQ-SAFE-001, REQ-DUT-001, REQ-PWR-003, REQ-CAL-003, REQ-GEN-001. Guard/triax (REQ-DUT-003) is explicitly FUTURE — not V1.  
**Convention:** `REQ-` promotion requires `DECISIONS.md` evidence; this document never promotes.

---

## 0. What an SMU Must Do (Common Ground)

A **Source-Measure Unit** is not a PSU + DMM glued together. It must:

* Force V **or** I and measure **both** simultaneously with a shared timing model (step → settle → measure), logging `{Vmeas, Imeas, range_state, compliance_flag, timestamp}` as one coherent dataset.
* Provide **four-quadrant** operation when required: source/sink current at either voltage polarity (Q1 +V/+I source, Q2 −V/+I sink, Q3 −V/−I source, Q4 +V/−I sink). V1 aspirational target is ±5 V at ±10 mA; primary ReRAM window ±2 V (REQ-SRC-001/002/006).
* Expose a **compliance / limit envelope** that is part of the measurement story: when the clamp is active the setpoint is no longer delivered and the measured partner variable must be read. See `COMPLIANCE_RESEARCH.md`.
* Support **Kelvin (4-wire) sensing** (REQ-DUT-001), **autoranging** with hysteresis (REQ-MEAS-004), and a **hardware compliance loop** independent of firmware (REQ-SAFE-001).

Provenance for 4-quadrant theory and instrument-practice surveys used below is at the end of this file (icnavigator, Tektronix SourceMeter, R&S NGU, InfinityPV, TI/NI app-notes, Erickson DIY-SMU).

---

## 1. Architecture Taxonomy

| Label | Short name | One-line topology | Quadrants | Current sense | Typical V1 instance |
|-------|------------|-------------------|-----------|---------------|---------------------|
| **A** | DAC + power amp + shunt | Unipolar/bipolar DAC → power op-amp in voltage-follower/gain stage → series shunt(s) for I-sense → ADC | 2 or 4 depending on rails/power stage | Resistive shunt(s) only | AD5686R → LT1970A (±12 V rails) → switched shunts → ADS1262 / STM32 ADC |
| **B** | Force/sense feedback (voltage- **and** current-loop) | DAC → error amp with selectable feedback: **voltage loop** (sense divider) *or* **current loop** (shunt) → power stage. Compliance is just the inactive loop's clamp. | 4 (with bipolar rails + bipolar amp) | Shunt in current-loop feedback; same shunt(s) for measurement | Classic SourceMeter/4080-style: separate CV/CC error amps with diode-OR/limiter |
| **C** | TIA low-current + source amp (split path) | Voltage source path (DAC → power amp) **+** separate **transimpedance (TIA)** path for nA/μA. Relay/switch selects path. | 4 for source; TIA is ideally Q1/Q3 receive but burden ≈ μV | TIA (op-amp + Rf) for low I; shunt for high I | Erickson DIY-SMU / NI PXI-4022 philosophy: 1 μA–100 mA shunts, TIA would be below 1 μA (V2) |
| **D** | Hybrid multi-range (commercial-grade) | Combines B + C + overlapping ranges: shunts for mA, TIAs for μA/nA/pA, guarded switching, sometimes digital control loop (FPGA/DSP) closing force | 4, with formal SOA/power envelope | Shunts (high) + TIAs (low), sometimes coulombmeter/integrating cap for fA | Keysight 4080 HRSMU / Keithley 2600B / NI STS pattern |

> This survey deliberately omits: single-quadrant bench-PSU+relay-polarity-reverser hacks (quadrant-switching artefacts, REQ-SRC-005), and V2 electrometer/guarded-triax front ends (REQ-DUT-003).

---

## 2. Architecture A — DAC + Bipolar Power Amp + Shunt Measurement

### Topology
```
Ref (ADR4525-class) → DAC (AD5686R) → buffer/gain → LT1970A power amp (±12 V) → FORCE HI
                                                        │            │
                                                     shunt mux ──→ diff amp (ADA4522-2) → ADC (ADS1262)
                                                        │            │
                                                     FORCE LO ←── star gnd   SENSE HI/LO → diff amp → ADC
```
Shunt mux is typically CMOS switch or relay. SENSE is Kelvin-routed to DUT sense pins; ideally also Kelvin across each shunt individually.

### Source performance
* **Pros:** Simplest concept; bandwidth and transient set by op-amp + decoupling alone; achieves ±5 V easily with ±12 V rails and rail-to-rail power amp; LT1970A-class parts offer >±100 mA with thermal flag.
* **Cons:** No inherent current-source mode — current is only *measured*, not regulated, unless you add loop B. Load regulation is open-loop (depends on amp's OL gain + feedback divider ratio). Capacitive DUT needs explicit compensation (isolating R + snubber).

### Low-current performance
* Entirely shunt-bound. With a 5 MΩ shunt (Erickson DIY-SMU's 1 μA range) 100 nA gives 500 mV, but **voltage burden** = I×Rshunt appears in series with DUT — at 10 mA a 50 Ω shunt burdens 0.5 V and dissipates 5 mW (self-heating → TC error). Low-current floor is limited by: shunt thermal noise `√(4kTRB)`, relay/switch leakage, amp input bias, and PCB leakage (see uncertainty doc). Practically V1 "several nA" requires 100 nA range noise < ~1 nA rms, which is marginal without guard or TIA.

### Compliance implementation
Compliance is **not inherent**. Must be added as an *auxiliary clamp*: comparator + reference → fold-back on DAC or pull on power-amp input, or a dedicated current-limit pin on the power amp (if present). Response is comparator-limited (~μs) plus amp slewing. Without B's second loop, compliance is a **trip/clamp**, not **regulation** — the I–V at the limit is not a flat CC line until the loop settles, and overshoot depends on unclamped drive. This distinction is dissected in `COMPLIANCE_RESEARCH.md`.

### Complexity / stability / calibration / PCB
* **Complexity:** Low — fewest active loops.
* **Stability:** One voltage loop; easy to compensate, but load C can still peal the LT1970A. Shunt switching glitches are not inside the loop, so switching under power disturbs output unless DAC is co-stepped.
* **Calibration:** Straightforward: gain/offset for voltage force, and per-shunt gain/offset for current. No CC-loop crossover to characterize. However per-shunt TC and contact R must be calibrated individually.
* **PCB difficulty:** Moderate. No TIA guard. But Kelvin shunts + star ground + relay drive isolation still matter. Risk: high-side shunt forces sense amp CM to include FORCE voltage; low-side shunt avoids CM but exposes DUT LO to shunt burden — tradeoff.
* **V1 suitability:** **Highest V1 viability for a first build.** Matches "several nA" floor without promising pA; uses only parts already on provisional BOM; lowest risk of oscillation; hardware compliance can be added as fast comparator trip (meets REQ-SAFE-001 literal, if not ideal regulation).

---

## 3. Architecture B — Force/Sense Feedback with Dedicated Current Control

### Topology
```
                    ┌─ V-error amp (SENSE divider) ─┐
DAC → selector ─────┤                                  ├─ diode-OR / limiter → power stage → FORCE
                    └─ I-error amp (shunt sense)  ────┘                    ↑
                         ↑ compliance ref                               feedback mux
                    CV/CC mode bit (or auto crossover)
```
This is the Keithley 2400 / TI DAC reference-drive / NI Best Practices pattern: two error amplifiers share a common output node via limiter; whichever demands lower drive wins. Implemented with zero-drift amps (ADA4522-2 class) for both loops.

### Source performance
* **Pros:** Real **VI source** — can source V with CC compliance *regulation* and source I with VC compliance regulation, both four-quadrant. Load regulation is closed-loop in either mode. Best for ReRAM forming compliance (flat current).
* **Cons:** Must design **two stable loops that hand off cleanly** (CV→CC crossover). Requires careful compensation for each loop's load (R vs C). Mode switching or seamless crossover adds analog mux + reference DACs for compliance setpoint.

### Low-current performance
Same shunt limitation as A for measurement, but *forcing* low current is now quieter because the I-loop bandwidth can be intentionally limited. Still no TIA, so sub-μA noise/burden same physics as A.

### Compliance implementation
*Compliance is the inactive loop.* In V-source mode the I-loop is the compliant clamp; its reference **is** the compliance value. When DUT current exceeds it, the I-amp takes over, output voltage droops to hold I = Icomp — true **regulation**, not just trip. This yields the flat "CV→CC" knee logged with a compliance flag. Overshoot is set by loop crossover speed (<0.1% typ on 2400, 30–70 μs recovery) and by DAC slew if you step into compliance.

### Complexity / stability / calibration / PCB
* **Complexity:** Medium-high — two error amps, reference DACs for compliance, mode logic (or auto), SOAs, fast flag.
* **Stability:** Hardest of A–C. Each loop needs its own compensation; crossover must be glitch-free; capacitive DUT + shunt L + lead L can provoke oscillation in current mode especially. TI app-note warns R-2R DAC reference current is code-dependent — without buffered force/sense reference drive, both loops inherit INL bow.
* **Calibration:** Per-loop offsets/gains, compliance accuracy (add 0.3% of range + 0.02% reading typ on Keithley) must be verified. Need compliance DAC INL separate from force DAC.
* **PCB difficulty:** High — two high-impedance error nodes, force/sense routing, guard-like care near I-sense even if not formal guard. Relay switching glitch now *is* inside the feedback path if shunts are in-loop (cf. US7903008B2 shunt-inside-loop).
* **V1 suitability:** **Most faithful to commercial SMU behavior** and best ReRAM compliance; but highest analog risk for a first PCB. Feasible for V1 if team has SPICE + prototyping bandwidth and accepts longer bring-up. Otherwise defer to V1.1.

---

## 4. Architecture C — Transimpedance-Based Low-Current + Source Amp

### Topology
```
Force path: DAC → power amp → FORCE (as in A)
Measure path: DUT LO → TIA (FET op-amp + Rf = 1 MΩ…1 GΩ // Cf) → ADC
              (high-I ranges still use shunt, selected by relay)
Guard (V2): TIA summing node → driven shield (triax) — NOT V1
```
Feedback ammeter principle: DUT current flows through Rf, amp holds summing node at virtual ground; Vout = −I×Rf. Burden voltage is Vos + Ib×Rf, typically **0.2–2 mV** vs **hundreds of mV** for shunts (NI PXI-4022 AN).

### Source performance
Source amp is same as A (no current-loop regulation unless combined with B). TIA is measure-only.

### Low-current performance
* **Pros:** Dramatically lower burden (2% error vs 50% shunt on a 1 MΩ DUT example), faster settling (effective R = Rf/Aol), lower Johnson noise for same transimpedance. Enables "several nA" with margin and points toward future 10 nA/1 nA/pA. Feedback C stabilizes TIA against DUT capacitance.
* **Cons:** High-value Rf is expensive, drifts with T/voltage coefficient, and needs Cf tuning per range. Input bias current of TIA op-amp **directly adds** to DUT current — requires fA-grade FET amp (not ADA4522-2) for <10 nA, and ultra-clean PCB (flux, humidity, triboelectric). Without guard/triax (FUTURE per REQ-DUT-003) leakage still limits to ~1 nA corridor (Erickson notes ~0.1 nA per switch). Settling is Cf×Rf limited — a 1 GΩ ∥ 1 pF TIA slews ~1 s.

### Compliance implementation
Same as A — TIA does not provide current *forcing*. If compliance regulation is needed you still need B's loop or a series clamp that *includes* the TIA in the sense path, which couples TIA saturation to compliance speed. Most C+V1 hybrids keep compliance as fast trip, not regulation.

### Complexity / stability / calibration / PCB
* **Complexity:** Medium — adds a precision TIA channel, reed/photoMOS mux, Cf per range, and separate supply for TIA (low noise).
* **Stability:** TIA stability is driven by Cin (DUT + cable + relay Coff) vs Cf; noise gain peaks. Needs per-range Cf and careful layout. Force amp stability is same as A.
* **Calibration:** Rf ratio/TC dominates (0.1% thick-film vs 1% RF, but TC <25 ppm/°C needed). Offset = Vos/Rf + Ib. Each Rf needs its own calibration table and dielectric-absorption soak characterization.
* **PCB difficulty:** **Highest for low-I.** The TIA summing node is a ~fA node: any solder flux, via, or unguarded trace is a GΩ leak. 2-layer PCB is inadequate; 4-layer with slot/milled moat, PTFE standoffs, and air-wiring may be needed even before formal guard. Erickson and TI femtoampere AN (SBOA597) devote pages to this.
* **V1 suitability:** **Not recommended as V1 baseline.** Overkill for "several nA" (achievable with careful shunt + averaging) and highest risk of silent leakage failure. Keep as explicit V2 path; a V1 PCB can provision a TIA footprint/mux without stuffing.

---

## 5. Architecture D — Hybrid Multi-Range (Commercial Pattern)

### Topology
Synthesis of A+B+C plus:
* Overlapping shunt + TIA ranges (e.g., 10 A/3 A/1 A/100 mA/10 mA/1 mA/100 μA/10 μA/1 μA/100 nA/10 pA in 2600B/4080).
* Guarded relay tree (guarded-T mux), sometimes Kelvin across every element.
* Digital control loop option: ADCs → FPGA/DSP → DAC, with range-change holdoff, weighted averaging, and compliance flagging (US7903008B2 / US20090121908A1). TI-style force/sense buffered reference drive for DAC ladder.
* Hardware SOA/power foldback in addition to compliance.

### Source / low-current / compliance
* **Source:** Best — seamless CV/CC crossover, high-capacitance mode compensated separately, PowerFlex autoranging (constant-power hyperbola) in some instruments.
* **Low-current:** Best — each decade gets its optimal sensor (low-Ω shunt for A-range, high-Rf TIA or integrating coulombmeter for pA). The 4080 HRSMU reaches 10 pA range with 1 fA resolution using guard + integrating techniques.
* **Compliance:** Full matrix: compliance regulation (CV/CC), range compliance (range-protect clamp), over-voltage/over-current crowbar, and foldback, each flagged distinctly.

### Complexity / stability / calibration / PCB
* **Complexity:** Highest — bill of relays/switches alone exceeds V1 BOM; digital loop adds FPGA firmware and calibration tables per range/mode/temperature.
* **Stability:** Managed by partitioning compensation per mode/range and by holdoff timing (Keithley's "range change holdoff" steers measure range to compliance range before a voltage step to absorb C×dV/dt).
* **Calibration:** Per-range, per-mode, temperature-compensated tables; factory tri-temp calibration; user self-cal via internal references.
* **PCB difficulty:** 6+ layers, partitioned analog/mixed-signal, guarded triax routing end-to-end, shielded compartments. Well beyond V1's "no triax / no electrometer" constraint.
* **V1 suitability:** **Aspirational reference, not a V1 build.** Its value is as a checklist: autorange hysteresis, compliance flagging, range-change sequencing, guard provisioning, and digital-loop calibration concepts can be *borrowed* at small scale into A/B.

---

## 6. Side-by-Side Comparison

| Dimension | **A — DAC+power+shunt** | **B — Force/sense feedback** | **C — TIA + source** | **D — Hybrid multi-range** |
|-----------|-------------------------|------------------------------|----------------------|----------------------------|
| **Source accuracy** | Good (OL-gain limited); no I-source regulation | Best of V1 options: true V & I source, closed-loop both | Same as A | Best overall |
| **Low-current (≤1 μA) noise/burden** | Burden I×R; noise ∝√R; marginal at 100 nA without guard | Same as A (sensor unchanged) | Excellent: μV burden, lower Johnson, faster on high-C DUT | Excellent across decades |
| **Compliance behavior** | Trip/clamp only; foldback possible but not flat regulation | **Regulation** (flat CC) with measurable knee; flag | Same as A unless merged with B | Regulation + range protect + SOA foldback |
| **Overshoot on compliance entry** | Set by comparator + amp slewing; highest | Lowest (loop bandwidth) — typ <0.1% step, 30–70 μs recovery on commercial refs | Same as A | Managed with holdoff/soft-start |
| **Analog loop count** | 1 | 2 + crossover | 1 + TIA loop | 2+ + digital loop |
| **Stability risk** | Low | **High** (crossover, dual comp) | Medium (TIA Cin×Rf) | High but partitioned |
| **Calibration effort** | Per-shunt gain/offset + V force | Per-shunt + per-loop (+ compliance DAC) | Per-Rf + Ib/Vos + dielectric soak | Per-range/per-mode/temp tables |
| **Relay/switch stress** | Outside loop; lower risk | Inside loop if shunt switches in feedback → glitch-sensitive | TIA input node is fA-sensitive; switching leakage dominates | Guarded-T, make-before-break, break-before-make strategies mandatory |
| **PCB difficulty** | Moderate (Kelvin, star, supply) | High (two error nodes) | **Very high** on TIA node | Highest (guard, triax, shields) |
| **BOM cost** | Lowest | + error amps + compliance DAC/refs | + fA amp + GΩ Rs + Cf + reeds | Highest |
| **Firmware load** | Light | Medium (mode, crossover flag) | Medium (TIA range, leakage cal) | Heavy (DSP loop, autorange state machine) |
| **Autoranging fit** | Simple range mux; chatter near threshold | Needs holdoff to avoid ranging into compliance | TIA ranges need extra dwell (Cf settle) | Full state machine with overlap hysteresis |
| **Failure mode if mis-applied** | Silent burden error, compliance overshoot damages DUT | Oscillation/crossover glitch | Silent leakage/IB error, soak drift | Over-engineered for V1 schedule |
| **V1 suitability (no selection)** | **Lowest risk; meets several-nA with care** | **Most correct SMU semantics; higher bring-up risk** | **Not V1 — reserve for V2** | **Reference only — not V1 build** |

---

## 7. Cross-Cutting Design Notes (Apply to Any V1 Choice)

* **Shunt vs TIA rule of thumb** (NI AN, TI SBOA597, Erickson): shunt ≤ ~20 mA (small R, fast), TIA for ≤ ~1 μA (μV burden, faster than MΩ shunt on capacitive DUT because effective R = Rf/Aol). V1's 100 nA range sits exactly at the uncomfortable boundary — both are feasible, shunt with averaging/guarding is the conservative V1 pick.
* **Shunt placement:** high-side keeps LO clean but imposes CM = Vforce on sense amp (needs wide CMR or level shift); low-side keeps CM near 0 but LO burden corrupts 2-wire measurements — Kelvin 4-wire is non-negotiable either way.
* **Compliance vs range compliance:** user-set compliance ("real compliance", e.g., 5 mA to protect ReRAM) vs range-bound limit (shunt/range protects the sense resistor). Instrument clamps to the **lower** of the two; blinking units on Keithley = range compliance, steady CMPL = real compliance. Autorange must respect `I_compliance ≤ I_range` unless it auto-raises range.
* **Stability into capacitive DUT:** ReRAM + cabling is not purely resistive. Any power stage driving nF needs isolation R + feedback pickoff after the R, plus optional snubber. TIA needs Cf ≥ √(Cin/Cf) style tuning per range.
* **Kelvin correctness:** FORCE carries current; SENSE carries ~nA (ADC buffer bias). Sense must be differential, star-pointed only at DUT, not at shunt. Sense-open detection belongs in any choice.
* **Power:** ±12 V rails (REQ-PWR-003 provisional) suffice for ±5 V + headroom for a 10 mA LT1970A-class stage and for TIA headroom on higher ranges. Split analog/digital supply and star ground are confirmed (REQ-PWR-004).
* **Simulation prerequisite (REQ-GEN-001):** Each architecture's loops must be SPICEd (ngspice primary, LTspice secondary per DEC-TOOL-002) before PCB — especially current-loop and TIA noise gain.

---

## 8. What This Survey Does Not Decide

* No architecture is selected; no component is promoted from `PROVISIONAL`.
* No shunt values, Rf values, compensation values, or relay part numbers are finalized.
* Guard/triax/electrometer remain FUTURE (REQ-DUT-003) — any guard provision on a V1 PCB is a *hook*, not a promise.
* Compliance envelope is researched separately in `COMPLIANCE_RESEARCH.md`; uncertainty math in `docs/calculations/UNCERTAINTY_BUDGET_FRAMEWORK.md`.

Next gate: Phase 2 architecture study must re-check every provisional part against its **primary datasheet** and against simulation before any `DEC-XXX ACCEPTED`.

---

## 9. Provenance (URLs consulted)

* ICNavigator — Source Measure Unit (SMU) Design: 4-Quadrant & Autorange — https://icnavigator.com/applications/test-measurement-instrumentation/source-measure-unit-smu/
* Tektronix — Technical Information: SourceMeter SMU Instruments — https://download.tek.com/document/TechInfo_SourceMeasureSMU.pdf  and  https://download.tek.com/document/TechInfo_SourceMeas.pdf
* Tektronix — How Does an SMU Work (video) — https://www.tek.com/en/video/product-demo/how-does-an-smu-work
* InfinityPV — The Four Quadrants of SMU Operation Explained — https://www.infinitypv.com/roll-to-roll-academy/the-four-quadrants-of-source-measure-unit-smu-operation-explained-applications-in-electronics-and-solar-cell-testing
* Rohde & Schwarz — NGU401/201 Source Measure Units (four-quadrant architecture) — https://www.rohde-schwarz.com/us/products/test-and-measurement/source-measure-units-smu_250948.html  and  https://www.electrorent.com/us/products/lcr--impedance-analyzers/semiconductor-test-equipment/rohde-and-schwarz/ngu401-3639376303/01t5Y00000DEe3oQAD
* Saelig/AIM-TTi SMU4000 (PowerFlex autoranging context) — https://www.testandmeasurementtips.com/saelig-source-measure-unit-combines-four-quadrant-voltage-current-source-with-6-5-digit-meter
* Wikipedia — Source measure unit (overview, 4-quadrant) — https://en.wikipedia.org/wiki/Source_measure_unit
* NI Community — "current limit means compliance or range?" (range vs real compliance, autorange coercion) — https://forums.ni.com/t5/PXI/quot-current-limit-quot-means-quot-compliance-quot-or-quot-range/td-p/3838546  and  page 2
* NI — SMU Best Practices: Understanding Compliance and Device Protection — https://www.ni.com/en/support/documentation/supplemental/19/smu-best-practices--understanding-compliance-and-device-protecti.html
* NI — Compliance (DCPower) — https://documentation.help/NI-DC-Power-Supply-SMU/compliance.html
* NI — Configuring Current Limit on PXI SMU — https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DsYCCA0&l=en-US
* Keithley 2400 SMU Datasheet (20 W, compliance/overshoot specs) — https://www.cmc.ca/wp-content/uploads/2019/07/Keithley-2400-SMU-Datasheet.pdf
* Keithley 2600B System SourceMeter Data Sheet (wide-range, overshoot, guard, derating) — https://assets-us-01.kc-usercontent.com/ecb176a6-5a2e-0000-8943-84491e5fc8d1/d134001e-6806-4586-9325-278f8a8aa8f9/Keithley%202600B%20System%20SourceMeter%20SMU%20Instruments%20Data%20Sheet.pdf  and  https://res.cloudinary.com/iwh/image/upload/q_auto,g_center/assets/1/26/Keithley_2600B_System_SourceMeter_SMU_Instruments_Data_Sheet.pdf
* Tek — SMU overshoot / range-compliance FAQ (70946) — https://www.tek.com/en/support/faqs/compliance-what-does-it-mean-when-units-compliance-value-blink-front-panel
* TekTalk Community — 2400 SMU range compliance & :STAT:MEAS:COND? — https://my.tek.com/tektalk/source-measure-units/18162425-c77b-ed11-a81c-00224806f130
* EEVblog Forum — Potential Keithley 2400 Regulation issue (load-transient overshoot anecdote, “SMU not a bench PSU”) — https://www.eevblog.com/forum/testgear/potential-keithley-2400-regulation-issue/
* NI — Minimizing Errors for Low-Current Measurements (shunt vs feedback ammeter, burden, settling) — https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x1AZCAY&l=en-US
* Keithley Low Level Measurements Handbook 7th Ed (electrometer/picoammeter/TIA/coulombmeter context) — https://assets.testequity.com/te1/Documents/pdf/keithley/KeithleyLowLevelHandbook_7Ed.pdf
* TI — Measurement and Calibration Techniques for Ultra-low Current (SBOA597, coulombmeter vs TIA, zero-cross IB, dielectric absorption) — https://www.ti.com/lit/an/sboa597/sboa597.pdf
* EE Times — Tips and tricks for optimizing low-current measurements (feedback ammeter vs shunt) — https://www.eetimes.com/tips-and-tricks-for-optimizing-low-current-and-high-resistance-measurements-part-1/
* Keysight 4080 Parametric Test System — Low Current Technologies (HRSMU 10 pA/1 fA, guarded probe card, SMART integration) — https://www.keysight.com/us/en/assets/7018-02816/technical-overviews/5990-7123.pdf
* TI — Building a Stable DAC External Reference Circuit (SLAA172, force/sense buffer) — https://www.ti.com/lit/an/slaa172/slaa172.pdf
* TI — DAC force and sense reference drive (SBAA332, ladder transient, bow INL) — https://www.ti.com/lit/an/sbaa332/sbaa332.pdf
* NI — Best Practices for Maximizing DC Measurement Performance (20042758, guarded-T relay, leakage cadence) — https://www.ni.com/content/dam/web/pdfs/niconnect/2023/product/5_Best_Practices_for_Maximizing_DC_Measurement_Performance.pdf
* Erickson DIY-SMU — design notes (shunt values 5 MΩ→50 Ω, DG441 leakage, 30:1/3:1 sense dividers) — https://www.djerickson.com/diy_smu/
* US Patent 7,903,008 B2 & US20090121908A1 — Source-Measure Unit Based on Digital Control Loop (shunt switching inside/outside loop, DCL, multiplexer) — https://eureka.patsnap.com/patent-US7903008B2  and  https://eureka.patsnap.com/patent-US20090121908A1

---

*Generated for research only. Accuracy of third-party specs must be re-checked against primary manufacturer datasheets before any DEC promotion. See `ENGINEERING_RULES.md` rules 1–3, 6–8.*
