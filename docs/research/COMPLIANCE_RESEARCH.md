# Compliance Research — Regulation vs Protection for ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 1 Research  
**Date:** 2026-08-24  
**Status:** `DRAFT / RESEARCH ONLY` — no compliance architecture selected; satisfies OPEN_QUESTIONS Q-04 (plus Q-03/Q-05). REQ-SAFE-001 (hardware compliance), REQ-SAFE-002 (software limits), REQ-SAFE-007/008 (fault/watchdog) remain binding; numbers below are *provisional research targets* requiring DEC promotion.  
**Companion:** `SMU_ARCHITECTURE_SURVEY.md` (architectures A–D context), `docs/calculations/UNCERTAINTY_BUDGET_FRAMEWORK.md` (accuracy budgeting).

---

## 1. Terminology — Three Different Things Called "Limit"

| Term | What it is | Who sets it | What happens at the boundary | Logged as | Spec example |
|------|-----------|-------------|------------------------------|-----------|--------------|
| **Compliance regulation** (real / user compliance) | Programmable **closed-loop limit** the SMU regulates to. In V-source mode it's **I-compliance**; in I-source mode it's **V-compliance**. The SMU stays in control, just on the other variable. | User per test (e.g., ReRAM forming limit) | SMU transitions CV→CC (or CC→CV): current (or voltage) clamps flat at the compliance value; the other variable droops measurably. Flag `IN_COMPLIANCE=1`. No error. | `Vmeas`, `Imeas` (both still valid), `compliance_flag`, `compliance_type=I/V` | Keithley 2400/2600B: bipolar current limit settable 0.1% of range; compliance accuracy = base accuracy **+ 0.3% of range + 0.02% of reading** typ |
| **Range compliance** (range-bound clamp / instrument protect) | Clamp imposed by the **present measurement range's hardware** to protect the sense element (shunt or TIA feedback R). | Instrument physics (or driver auto-coercion) | SMU clamps to **max of that range**, not to user's value, if user compliance > range max. Display blinks on Keithley; `I ≤ I_range_max`. | `range_state` + implicit clamp; `:STAT:MEAS:COND? bit 14` on some instruments (real compliance only) | 2400 note: 10 nA…1.05 A ranges each carry their own compliance ceiling; 100 mA range trips sooner than a 300 mA user limit on the 100 mA range |
| **Over-current / over-voltage / SOA trip — shutdown / crowbar** | **Open-loop protection**: fast comparator, fuse, foldback, or SOA power limit that *removes or collapses* output to protect DUT + instrument. **Not regulation** — output does not stay at the limit. | Hardware supervisor (independent of main loop), sometimes software-assisted | Output disabled, crowbarred, or folded back abruptly. Latches or auto-retry with fault flag. Fault log entry. | `FAULT_OC`, `FAULT_OV`, `FAULT_SOA`, `OUTPUT_DISABLED` | NI SMU Best Practices: internal protection monitors halt output; R&S NGU electronic fuse; Keithley over-temp standby |

**Key sentence:** *Compliance keeps the SMU in the circuit and tells you so; a trip takes the SMU out of the circuit and tells you so.* Confusing them risks both silent mis-data (logging a clamped point as normal) and DUT damage (overshoot before a slow trip).

Sources for this triad: NI DCPower Compliance docs, NI forum "current limit means compliance or range?", Keithley 2400 range-compliance FAQ, NI SMU Best Practices, icnavigator SMU compliance-as-measurement-story.

---

## 2. Compliance Regulation in Detail

### 2.1 V-source / I-compliance (ReRAM primary mode)
* Setpoint: `V_force = Vset` (DAC-driven).
* Limit: `I_limit = Icomp` (user programmable per test).
* Below limit: SMU is **CV** — regulates `Vmeas = Vset`, `Imeas` is whatever the DUT draws.
* At limit: SMU is **CC** — regulates `Imeas = I_limit`, `Vmeas` falls to `I_limit × R_DUT` (or to whatever the DUT's I–V dictates). The I–V knee is **flat current**, vertical voltage drop — a characteristic compliance line on the I–V plot.
* Data rule: once `in_compliance==true`, **do not** trust `Vset` as the applied voltage — use `Vmeas` and label the point distinctively.

### 2.2 I-source / V-compliance (less common for ReRAM, needed for completeness)
Mirror image: force current, clamp voltage. Used for e.g., high-R forming diagnostics or for future I-sweep modes. Same flagging rule reversed.

### 2.3 Why compliance is not a bench-PSU current limit
A commodity bench supply's CC limit may be a foldback or a slow trip that sags, oscillates, or needs manual reset. A proper SMU compliance is a **second control loop** (Architecture B) or a well-compensated limiter that still meets regulation specs (line/load regulation ±0.01% of range + 100 μV/100 pA on 2600B-class). The user must be able to see *where* the DUT's I–V is limited vs where it is intrinsic.

---

## 3. Desired Compliance Envelope for ReRAM-SMU V1

Derived from REQ-SRC-006 (±10 mA max), REQ-MEAS-001/002 (100 nA floor, several nA useful), and ReRAM forming physics (100 μA–1 mA typical, with some stacks needing 10–50 mA for forming; HRS leakage nA–μA). Values are **research window, not spec** — Phase 2 must tighten against measured DUT population.

| Compliance setting | Use case | Provisional resolution needed | Provisional accuracy target (research) | Note |
|--------------------|----------|-------------------------------|----------------------------------------|------|
| **10 μA** | First gentle forming on ultra-low-current stacks; safety floor | 10 nA steps | ±(1% + 50 nA) | Floor limited by TIA vs shunt choice; burden ≤ a few mV |
| **100 μA** | Standard SET compliance for many HfO₂/TiO₂ stacks | 100 nA steps | ±(0.5% + 200 nA) | Most common ReRAM forming bin |
| **1 mA** | Higher-power stacks, filament stability test | 1 μA steps | ±(0.3% + 1 μA) | Typical "hero" forming value |
| **10 mA** | Stack forming margin, LRS characterization, RESET current | 10 μA steps | ±(0.3% + 10 μA) | Max per REQ-SRC-006; SOA/power must be checked (≈50 mW at 5 V) |
| **Intermediates (e.g., 50 μA, 500 μA, 3 mA)** | Smooth search without range switch | DAC LSB limited | — | Log-spaced coverage; autorange should not be forced to re-range on compliance tweak alone |

**Adjustability:** Continuous within each current range, not just decade steps. Minimum programmable compliance is 0.1% of the active current range on Keithley-like instruments (e.g., 10 nA compliance needs the 10 μA range minimum → ~10 nA granularity). V1 should expose compliance as a *value*, not just a range.

**V-compliance partner:** For I-source mode (if supported), provisional V-limit ≈ ±5 V in 10 mV steps, accuracy tracking voltage source accuracy.

**Power/SOA compliance (implicit):** Even if I ≤ 10 mA and V ≤ 5 V, simultaneous max violates SOA at elevated temperature (Keithley 2600B derates above 30 °C; full power only in sink ≤30 °C). V1 must define a **power hyperbola** `|V×I| ≤ 50–60 mW` continuous or use a duty-limited pulse for forming if needed.

---

## 4. Accuracy, Response Time, Overshoot, and Need for Hardware Loop vs Fast Trip

### 4.1 Accuracy
* Compliance accuracy is **sourcing accuracy**, not just measurement accuracy. Keithley 2400/2600B add `0.3% of range + 0.02% of reading` to the base current-source accuracy when quoting compliance. V1 should budget the same stack: DAC INL/gain/offset + reference + sense-amp errors + shunt tolerance/TC + ADC gain — see uncertainty framework.
* A compliance value that is *less accurate* than the measurement chain can create a systematic forming bias (e.g., 100 μA compliance ±5% spreads SET resistance distribution). Calibrate compliance by **measuring** actual clamped current into a short with the precision current ADC — don't trust open-loop DAC code.

### 4.2 Response time (how fast the SMU must clamp)
* Threat model: ReRAM filament formation is a **positive-feedback, sub-microsecond event** — DUT resistance collapses from MΩ to kΩ in nanoseconds. Even a 10 μs loop can let current spike before clamping.
* **Hardware compliance loop target:** ≤ **10–30 μs** to settle into regulation for a 1 mA step into a resistive load (2400: 30 μs transient recovery; 2600B: 70 μs to 0.1% for 10–90% load step; Erickson DIY: ~μs comparator path but range-switch dependent). Faster is better, but loop bandwidth vs stability tradeoff applies.
* **Fast trip / crowbar target:** ≤ **1–5 μs** from threshold cross to output crowbar/foldback if regulation is not feasible (e.g., instrument is in Architecture A with shunt-only). This is a **safety net**, not the forming compliance.
* Firmware/software clamp alone (ADC → MCU → DAC) is **too slow**: ADS1262 at 1 kSPS ≈ 1 ms + MCU jitter + DAC settling → milliseconds, orders of magnitude beyond filament time. Therefore REQ-SAFE-001 hardware compliance is load-bearing, not decorative. Software limit (REQ-SAFE-002) is a secondary envelope and a pre-check gate.

### 4.3 Overshoot tolerance
* **Overshoot = (I_peak − I_limit)/I_limit** on entry to compliance, measured into a resistive load that steps from below to above limit (including C×dV/dt transient on a range change).
* Commercial SMU spec: **<0.1% typical** for a 10–90% range step into resistive load (2400); `< ±(0.1% + 10 mV)` for voltage. V1 should adopt **<1–2% for I ≤ 1 mA** as an initial *research goal*; >10% overshoot would risk irreversible forming overstress and widen SET distribution. EEVblog 2400 anomaly thread shows that load hot-plug + autorange can produce **volts of overshoot** even on a commercial SMU — test with hot-plug and step waveforms, not just static load.
* Measurement method: step `Vset` into a precision resistor sized so `Vset/R > Icomp`; capture `Imeas` with FastLog / scope shunt at µs resolution; record peak, settled value, and compliance flag timing. Test every range and at range boundaries (Overshoot into adjacent range: Keithley notes 100 mV typical into 100 kΩ).
* Mitigations: soft-start / slew-limited DAC stepping (STM32G431 ramp or analog slew limiter), **range-change holdoff** (force measure range to compliance range *before* the voltage step to absorb displacement current — Keithley "current range holdoff"), output C minimization (but not below stability), and isolation resistor to decouple DUT capacitance.

### 4.4 Hardware loop vs fast trip — decision matrix

| Criterion | Hardware compliance **regulation** loop (preferred when Arch B) | Fast comparator **trip / foldback** (fallback when Arch A/C) |
|-----------|---------------------------------------------------------------|--------------------------------------------------------------|
| Behavior at limit | Flat CC, SMU stays in circuit, reading stays valid + flagged | Output collapses/shuts; reading during fault is not a valid operating point |
| Filament protection | Best — regulates through the negative-resistance snap | May still overshoot before trip; crowbar can cause inductive kick if wiring has L |
| Need for range awareness | Loop reference = Icomp, independent of range until headroom runs out | Threshold = I_range_max or user limit; must coordinate with range |
| False-trip risk | Low if well compensated; but crossover oscillation possible | Higher with noisy DUT / capacitive inrush unless blanking/dwell added |
| Implementation cost | 2nd error amp + reference DAC + compensation (Arch B) | Comparator + ref + latch + gate on power stage (Arch A/C) |
| Firmware role | Log flag, declare mode, handle recovery | Log fault, disable output, enforce retry/dwell policy |
| Suitability when DUT inrush is expected (hot swap, relay) | Loop absorbs inrush if sized; may still hit range compliance first | Must blank or it will nuisance-trip; needs post-trip autorange logic |
| **V1 verdict (research)** | **Needed if V1 claims "compliance regulation"**; otherwise call the feature a **current-limited source**, not an SMU compliance | **Mandatory safety fallback in every architecture** (REQ-SAFE-001 literal); worst case it is the compliance |

> Bottom line from surveyed practice (NI Best Practices, Keithley 2xxx, Erickson): ship **both** — a regulation loop for normal ReRAM compliance *and* an independent fast trip/crowbar/SOA supervisor that survives MCU hang. If only one fits the V1 PCB, the fast trip is the one that keeps REQ-SAFE-003/004 satisfied and must be proven with a **short-circuit + step-load scope capture** before any ReRAM DUT.

---

## 5. Implementation Patterns (Conceptual)

### 5.1 Series-pass limiter embedded in power stage
LT1970A-class stage with current-sense in emitter/source path; loop folds back drive. Fast, but couples thermal drift to compliance accuracy; needs Kelvin sensing of the pass element.

### 5.2 Shunt-clamp / diode-OR (Arch B pattern)
CV amp and CC amp outputs diode-OR'd into power stage input; clamp amp drives through precision limiter. Most textbook-correct; demonstrated in icnavigator diagram (CV loop + CC loop + limiter).

### 5.3 Comparator-driven limit (Arch A pattern, also supervisor)
Window comparator on shunt/TIA output vs compliance DAC ref → gates DAC or pulls power-amp enable low via latch. Can be made <5 μs with a fast comparator (TLV3501-class) + analog switch, independent of MCU clock. Must have hysteresis and blanking to avoid chatter on noisy DUT.

### 5.4 Foldback / SOA supervisor
Multiplies measured V×I and compares to SOA hyperbola; folds back or disables when exceeded. Particularly relevant if V1 ever pulses forming (W = V×I×t can exceed DC SOA even if per-variable limits are respected).

### 5.5 Digital control loop variant (Arch D teaser)
ADC → FPGA/DSP → DAC closing the loop in digital domain (US7903008B2). Corrects DAC INL upstream, handles glitch-free shunt handover by reading two shunts simultaneously, and can do coulombmeter integration for pA. Not V1 baseline but worth knowing for calibration-table thinking.

All patterns must meet REQ-SAFE-003 (safe default on power-on/reset/watchdog) — compliance reference must default to **lowest current** (or output disabled) until MCU proves life via heartbeat + supervisor.

---

## 6. Interaction with Range System

* **`I_compliance ≤ I_range`** invariant unless autorange is enabled (Keithley rule; NI driver coerces). Autorange must be able to **raise range to honor a larger compliance** before the source step, not after.
* **Range compliance is not a substitute for user compliance.** A user who sets 1 mA compliance on the 100 mA range and then manually locks the 100 μA range will be range-clamped at ~100 μA — a factor-10 surprise. Firmware should reject `Icomp > I_range` when autorange is off, and log the coercion.
* **Displacement current:** stepping 5 V in ~10 μs into 1 nF DUT+cable deposits `I = C·dV/dt ≈ 0.5 mA` transiently. If the current range is 10 μA, the range will saturate before the regulation loop sees the true filament current. Solution: **holdoff** — momentarily switch to compliance-current range for the step, then settle back.
* Log on every reading: `{range_state, compliance_flag, compliance_type, Icomp, Vcomp, I_range, V_range}` — that's the dataset (NI/Keithley) that makes post-hoc compliance labeling auditable.

---

## 7. Compliance Adjunct: Software Envelope (REQ-SAFE-002)

Firmware/software provides a **second, redundant polygon**: per-test `isw_limit`, `v_limit`, `power_limit`, plus sanity gates (`if |Imeas| > 1.2×Icomp for N samples → trip`). This layer:

* Pre-validates user recipe before arming output ("requested compliance exceeds connected range" rejection).
* Enforces dwell/hysteresis so autorange chatter doesn't ping-pong compliance.
* Implements soft-start: ramp DAC at controlled dV/dt, not full-scale jumps into an unknown DUT.
* Cannot be the only compliance — a hung MCU must not leave the DUT energized (watchdog → disable).

---

## 8. Provisional V1 Compliance Requirement Sketch (For Phase-2 Refinement)

> Not a spec — a testable starting envelope for whoever writes the Phase-2 compliance DEC.

| Parameter | Provisional target | Verification |
|-----------|-------------------|--------------|
| Compliance modes | V-source with I-compliance at minimum; V-compliance for I-source if I-source implemented | Mode matrix test |
| I-compliance range | 10 μA – 10 mA continuous, plus hardware floor (e.g., range-minimum) | Short-circuit sweep per range |
| Step granularity | 0.1% of range or 1 nA, whichever larger | DAC code vs measured |
| Accuracy | Compliance regulation error within ±(0.3% of range + measured I accuracy) | Compare Icomp set vs Imeas clamped into precision short |
| Response | Regulation settled <50 μs for 50% load step; trip <5 μs to clamp | Scope shunt + flag timing |
| Overshoot | <1% into resistive load, <5% into 1 nF load with soft-start | Peak capture per range |
| Flag latency | Compliance flag coherent with settled data within one NPLC/ADC conversion | Timestamp correlation |
| Safe default | Compliance = minimum of enabled range on power-on/reset/watchdog | Power-cycle + watchdog test |
| Independence | Hardware loop/trip functions with MCU halted or held in reset | MCU-halted fault injection |
| Logging | Every sample carries `in_compliance`, range, V/I comp values, temperature | CSV/raw export audit |

---

## 9. Open Questions This Research Leaves for Phase 2

* Q-04 resolved in research, but DEC still needed: **exact loop topology** (limiter vs diode-OR, component choice for comparator/amp, compensation).
* Whether STM32G431 DAC/PWM can generate compliance reference with sufficient stability, or a dedicated DAC channel is required.
* Shunt vs TIA boundary for the 100 nA range — dictates whether I-compliance in the 100 nA–1 μA decade is even meaningful without TIA.
* Thermal drift of compliance on long soaks (filament stress tests) — needs tempco budgeting in uncertainty framework.

---

## 10. Provenance

* NI — Compliance (DCPower) : https://documentation.help/NI-DC-Power-Supply-SMU/compliance.html
* NI Community — "current limit means compliance or range?" : https://forums.ni.com/t5/PXI/quot-current-limit-quot-means-quot-compliance-quot-or-quot-range/td-p/3838546 (+ page 2)
* NI — Configuring Current Limit on PXI SMU : https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DsYCCA0&l=en-US
* NI — SMU Best Practices: Understanding Compliance and Device Protection (compliance vs protection errors, voltage compliance risks, holdoff, load transient) : https://www.ni.com/en/support/documentation/supplemental/19/smu-best-practices--understanding-compliance-and-device-protecti.html
* Tektronix SourceMeter compliance / CV→CC illustration (TechInfo_SourceMeas) : https://data.embeddedcomputing.com/uploads/whitepapers/files-aT0xMTg4NDYyJnY9MSZpc3N1ZU5hbWU9c211LWZ1bmRhbWVudGFscyZjbWQ9ZCZzaWc9ZTZkYzAxZWE2OWFjOGQ3NzA5ZjE4MjU3Zjk3ZDQ0NzI253D
* Keithley 2400 SMU Datasheet (overshoot, compliance accuracy) : https://www.cmc.ca/wp-content/uploads/2019/07/Keithley-2400-SMU-Datasheet.pdf
* Keithley 2600B Data Sheet (wide-range compliance accuracies, power envelopes) : https://assets-us-01.kc-usercontent.com/ecb176a6-5a2e-0000-8943-84491e5fc8d1/d134001e-6806-4586-9325-278f8a8aa8f9/Keithley%202600B%20System%20SourceMeter%20SMU%20Instruments%20Data%20Sheet.pdf
* Tek FAQ 70946 — Compliance vs range compliance (blinking units, range clamp) : https://www.tek.com/en/support/faqs/compliance-what-does-it-mean-when-units-compliance-value-blink-front-panel
* TekTalk — 2400 SMU range compliance & `:STAT:MEAS:COND?` bit 14 : https://my.tek.com/tektalk/source-measure-units/18162425-c77b-ed11-a81c-00224806f130
* ICNavigator — SMU Design: 4-Quadrant & Autorange (compliance as measurement story, CV/CC limiter diagram) : https://icnavigator.com/applications/test-measurement-instrumentation/source-measure-unit-smu/
* Embedded Computing / Keithley SMU Fundamentals (CV/CC mode, constant V/I illustration with 1.5 mA / 20 kΩ example) : https://data.embeddedcomputing.com/uploads/whitepapers/files-aT0xMTg4NDYyJnY9MSZpc3N1ZU5hbWU9c211LWZ1bmRhbWVudGFscyZjbWQ9ZCZzaWc9ZTZkYzAxZWE2OWFjOGQ3NzA5ZjE4MjU3Zjk3ZDQ0NzI253D
* EEVblog — 2400 Regulation Issue (hot-plug overshoot anecdote) : https://www.eevblog.com/forum/testgear/potential-keithley-2400-regulation-issue/
* Rohde & Schwarz NGU / Keithley 2600B power/SOA context : https://www.rohde-schwarz.com/us/products/test-and-measurement/source-measure-units-smu_250948.html
* US7903008B2 / US20090121908A1 — Digital Control Loop SMU (shunt switching, dual ADC) : https://eureka.patsnap.com/patent-US7903008B2

---

*All limits/accuracies above are literature-observed values for reference only. V1 values must be re-derived from primary datasheets of the actual chosen parts and from scope-verified prototypes before promotion to a requirement.*
