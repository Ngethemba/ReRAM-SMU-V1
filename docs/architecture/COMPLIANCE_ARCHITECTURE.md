# Compliance / Protection / Stability Architecture — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 (Agent C)
**Date:** 2026-08-24
**Status:** `ARCHITECTURE PROPOSAL — NOT YET DEC` — informs DEC-0XX; no component promoted until datasheet + simulation.
**Requirements in scope:** REQ-SAFE-001 (hardware compliance, CONFIRMED), REQ-SAFE-002 (software limits), REQ-SAFE-003/004 (safe state / watchdog), REQ-SAFE-007/008 (fault/watchdog), REQ-SRC-001/002 (±5 V / ±2 V primary), REQ-SRC-003..007 (bipolar/4-quadrant/enable), REQ-MEAS-001 (6 ranges), REQ-MEAS-004 (autoranging), REQ-DUT-001 (Kelvin), plus **CAUTION 1** (stored-energy overshoot) and **CAUTION 3** (per-segment/polarity programmability — no hard-coded SET=compliance).
**Companions:** `docs/research/COMPLIANCE_RESEARCH.md`, `docs/research/SMU_ARCHITECTURE_SURVEY.md` (Arch A–D), `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` (E=½CV²), `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md`
**Governance:** ENGINEERING_RULES.md §§1–6, 11, 14. Primary datasheet overrides AI claims. No kicad in this deliverable.

---

## 0. Executive Summary — Recommendation

**Only Option D — Dual Continuous Regulation + Independent Fast Trip + SOA Supervisor — fully satisfies REQ-SAFE-001 *and* CAUTION 1 *and* CAUTION 3.**

| Option | REQ-SAFE-001 hardware independent of firmware? | CAUTION 3 per-segment/polarity programmable? | CAUTION 1 stored-energy safe (≤1–2 nJ dump at 5 V)? | Verdict |
|---|---|---|---|---|
| **A — LT1970A built-in limiter** | ✅ yes (4 µs, 1%, independent flags) | ⚠️ partial — programmable *if* VCSRC/VCSNK driven per segment from DAC; hard-wired resistors **fail** | ❌ no — by itself does not limit downstream C; flag ≠ energy | Minimal viable, **fails CAUTION 1** unless augmented with R_iso + C budgeting + slew limit (at which point it becomes a subset of D) |
| **B — External diode-OR continuous loop** (CV+CC error amps) | ✅ yes — true flat CC regulation | ⚠️ partial — single compliance DAC, polarity needs mux; per-segment needs fast DAC update | ❌ no — regulation quality is best, but without an independent trip it has a single-point-of-failure window; no SOA hyperbola; large-compensation C still violates energy | Best *regulation*, but **fails CAUTION 1 + trip independence** |
| **C — Fast trip + coarse clamp** (comparator → crowbar/foldback) | ✅ yes — trip <5 µs with TLV3501-class | ✅ trip threshold can be per-segment via DAC, but coarse | ❌ regulation **not** flat CC — collapses/folds back → DUT leaves operating point; reading during fault is invalid; forming quality degraded (fabrication-scale ON/OFF spread) | Meets *protection* literal, **fails *compliance regulation* semantics** — instrument logs a fault, not a valid CC plateau |
| **D — Dual: continuous regulation (B) *plus* independent fast trip + SOA** | ✅ yes — two independent hardware paths | ✅ yes — dual DAC refs (VCSRC/VCSNK or CC-ref + trip-ref) per segment/polarity, swappable at segment rate | ✅ yes — D mandates **C_UPSTREAM ≤10 nF before R_iso; C_DOWNSTREAM ≤80–150 pF after R_iso** (recipe-dependent, IR-14), R_iso 33–47 Ω, slew limit, optional active discharge — validated against E=½CV²; fast trip via TLV3501-class as **emergency supervisor with loose 120–150% threshold (Vos 6.5 mV max, hyst 6 mV — IR-08), not precision regulation** | **Recommended for V1** — only one that covers the compliance triad correctly |

Practical V1 path: **Implement D with LT1970A as one of the two layers** (A⊂D) to reduce risk — i.e. Option B's diode-OR is emulated by LT1970A's built-in ISRC/ISNK transconductance limiters (already a CV→CC limiter with 4 µs takeover) **plus** an independent window comparator (TLV3501/TLV7031-class) that gates ENABLE/high-Z and drives a fault latch. Add R_iso + C budgeting per `COMPLIANCE_ENERGY_ANALYSIS.md`. This avoids designing two discrete error amps from scratch while keeping trip independence.

---

## 1. What REQ-SAFE-001 and the Two CAUTIONs Actually Require

### REQ-SAFE-001 (CONFIRMED) — Hardware Current Compliance Independent of Firmware

> *A **hardware** current compliance / protection loop shall limit DUT current independent of firmware, per compliance triad: compliance regulation (flat CC, flagged, SMU stays in circuit) distinct from range compliance and SOA trip (crowbar). Icc programmable as value within range (not decade-locked), min 0.1% of I_range (Keithley rule).*

Research targets (provisional, must be verified by scope): regulation settled <50 µs to Icc, trip <5 µs, overshoot <1% resistive / <5% into 1 nF with soft-start, SOA hyperbola |V·I| ≤50–60 mW DC, flag latency ≤1 NPLC, hardware functions with MCU halted.

### CAUTION 3 — Per-Segment / Per-Polarity Programmability

> *Must support **+sweep compliance, –sweep compliance, read compliance, disabled (RESET leg), per-segment limits** — not hard-coded SET=compliance.*

This is a *waveform compiler* requirement. ReRAM WF-1 (0→+Vmax→0→–Vmax→0) demands at least four compliance contexts in one sweep without operator intervention:

| Segment | Direction | Compliance expectation | Typical value |
|---|---|---|---|
| SET leg (forward) | +sweep (0 → +Vmax) | **Current compliance active** — limits filament formation | 10 µA / 100 µA / 1 mA selectable per recipe |
| RESET leg | –sweep (0 → –Vmax) | **Disabled or high limit** — must allow Ireset 0.2–3 mA to rupture filament | >10 mA or off (high-Z on limiter, foldback disabled) |
| Read | small ±Vread (0.1–0.5 V) | **Low compliance** — protect read disturbance but still measure nA–µA | ~2× expected Iread or 10–100 µA guard |
| Any disabled / high-Z | output disabled between sweeps | **Hardware safe default = minimum I** or high-Z via ENABLE | 10 µA floor or disabled |

Any architecture that ties Icc to a trimpot or a single fixed resistor on the PCB **fails CAUTION 3** by construction. The compliance reference must be a **voltage driven by a DAC channel** (or a low-R analog mux of DAC voltages) that firmware can update **before each segment** — ideally at sequencer rate (<1 ms segment switch).

### CAUTION 1 — Stored-Energy / Overshoot

> *Even a perfect limiter with zero steady-state error will still deliver **E = ½ C V²** already stored on the DUT node before the limiter can react. That energy must be budgeted.*

Quantified in `COMPLIANCE_ENERGY_ANALYSIS.md`: at 5 V, every 100 pF costs 1.25 nJ; 10 nF costs **125 nJ** (100× the ~1 nJ gentle-filament budget). CAUTION 1 requires:

- Total **downstream** capacitance (after the sense/isolation point) ≤80 pF for 1 nJ @5 V, ≤500 pF for 1 nJ @2 V.
- **R_iso** (33–47 Ω) to decouple upstream compensation C from the DUT.
- **Slew-limited DAC ramps** (0.1–1 V/ms) so I=C·dV/dt stays well below Icc.
- Optional **active discharge / series switch**, hardware-gated by the compliance flag, for long-cable users.

An architecture that spec-quotes "4 µs limit" without specifying downstream C **does not satisfy CAUTION 1**.

---

## 2. The Compliance Triad — Three Different Things Called "Limit"

This distinction (NI Best Practices, Keithley 2400/2600B, Tek compliance FAQ) is load-bearing and must be reflected in firmware's per-sample log.

| Term | What it is | Who programs it | What happens at the boundary | Logged as | Example failure if confused |
|---|---|---|---|---|---|
| **Compliance *regulation*** (real/user compliance) | Programmable **closed-loop limit** the SMU **regulates to** — in V-source mode it is I-compliance, in I-source mode V-compliance. The SMU stays in the circuit, just on the other variable. | User per test (e.g. forming limit) — must be per-segment, per-polarity, variable within range (CAUTION 3) | SMU transitions **CV→CC**: current clamps flat at Icc, voltage droops to Icc·R_DUT; flag `IN_COMPLIANCE=1`; reading remains valid but must be labeled. | `compliance_flag=I/V`, `compliance_type=regulation`, `Icomp`, `Vmeas` (drooped) | Logging a compliant point as "normal I–V" without flag → silent mis-data; forming variability inflated |
| **Range compliance** (range protect) | Clamp imposed by the **present current range's hardware** to protect that range's sense element (e.g. 10 µA range caps at ~10.5 µA regardless of user 1 mA request) | Instrument physics / driver auto-coercion (must enforce `Icomp ≤ I_range` unless autorange raises range) | Clamp to range ceiling, not to user's value; display blinks on Keithley; bit 14 `STAT:MEAS:COND?` on some instruments is *real compliance only* | `range_state`, implicit clamp, `range_compliance_flag` distinct from real compliance | User sets 1 mA compliance on the 100 µA range, manually locks range → silently clamped at 100 µA, 10× surprise |
| **SOA / emergency trip** (crowbar / foldback / shutdown) | **Open-loop protection**: fast comparator, foldback, supply-rail fuse, or hyperbola `|V·I| ≤50–60 mW` that *removes or collapses* output to protect DUT + instrument. **Not regulation** — output does not stay at the limit. | Hardware supervisor *independent* of main loop, survives MCU hang | Output disabled / crowbarred / folded back abruptly; latches or auto-retries with fault; reading during fault is **not** a valid operating point. | `FAULT_OC`, `FAULT_SOA`, `OUTPUT_DISABLED`, latched | Treating a crowbar as "compliance entered" → interpreting a collapsed reading as LRS, or restarting without dwell → relay chatter / inductive kick |

**Key sentence for the codebase:** *Compliance keeps the SMU in the circuit and tells you so; a trip takes the SMU out of the circuit and tells you so.*

Every sample must log `{range_state, compliance_flag, compliance_type, Icomp, Vcomp, I_range, V_range, temperature}` (REQ-SAFE-007) plus the **DUT type** (ENGINEERING_RULES #9–10). Post-hoc labeling depends on it.

---

## 3. Architecture Options — Detailed Evaluation

### 3.1 Option A — Power-Amp Built-In Limiter (LT1970A-Class)

```
Ref (ADR4525-class 5 V → filtered)
  → DAC (AD5686R Ch A: V_FORCE) → gain → LT1970A +IN
  → LT1970A OUT → Rsense (e.g. 0.5–10 Ω depending on max I) → R_iso (33 Ω) → FORCE_HI → cable → DUT → FORCE_LO → return
                 SENSE+/– Kelvin across Rsense → LT1970A internal ISRC/ISNK sense amp
                 VCSRC / VCSNK ← DAC Ch B/C (0–5 V above COMMON, ÷10)
                 ISRC / ISNK / TSD open-collector flags → MCU GPIO + supervisor latch
                 ENABLE ← supervisor + watchdog + GPIO (active-high, defaults low via pulldown)
```

**Strengths (datasheet-proven, 1970Afc):**

- Already a **dual transconductance CC limiter**: SENSE voltage compared to VCSRC/10 or VCSNK/10; when VSENSE ≥ limit, the appropriate ISRC/ISNK amp (very high Gm) **takes control from GM1** — diode-OR shown as D1/D2 in block diagram; functionally identical to the external diode-OR of Option B but integrated.
- **4 µs takeover** (typ) from threshold cross to control — inside REQ-SAFE-001 <5 µs trip / <50 µs regulation targets.
- **1% limit accuracy** on VCSRC/VCSNK; per-polarity independent (VCSRC sources, VCSNK sinks) — meets bipolar CAUTION 3 *if DAC-driven*.
- **Flags + thermal + ENABLE**: ISRC/ISNK pull low when that limiter is active (visible to firmware and hardware); TSD flags thermal shutdown; ENABLE puts output high-Z; 800 mA fixed ultimate limit plus thermal shutdown survive a dead short; sense common-mode VCC–1.5 to VEE+1.5 (so Rsense placement relative to rails matters).
- Fewest external loops → **lowest stability risk** (one voltage loop, the limit amps decouple via diodes when not active).

**Weaknesses / CAUTION fail modes:**

- **Downstream-C blindness** (§6.1): any C after Rsense still dumps. LT1970A data sheet does not claim compliance energy budgeting — system must add R_iso + C budgeting externally. Alone, Option A violates CAUTION 1 if the 10 nF compensation is taken to be "on the DUT".
- **Rsense tradeoff:** Icc = VC/(10·Rsense). For Icc=100 µA with VC=0.5 V (mid-range) → Rsense=500 Ω. But at Icc=10 mA the drop is 5 V (Rsense=500 Ω → 5 V burden) — impossible. Hence **Rsense cannot be single-valued across 100 nA–10 mA** unless VC range is adapted or Rsense is switched per range. Datasheet shows most apps tie SENSE+ to OUT with load on far side of RSENSE — i.e. RSENSE is in series with the load, dissipates P=I²R, and burdens headroom. A single Rsense covering 10 µA–10 mA needs either a very low VC for low I (noise/tolerance limited) or a high VC for high I (headroom). Practical solution: **two Rsense values** or a **range-switched shunt** (at which point the system is drifting toward B's range system).
- **Accuracy stack beyond 1%:** LT1970A's 1% is the *limit amplifier offset* only. System Icc also inherits RSENSE tolerance/TC, DAC INL/gain/offset, reference drift, sense-amp CMR. KI 2400 note: compliance accuracy = sourcing accuracy **+ 0.3% of range + 0.02% of reading** — the same must be budgeted for even an LT1970A limiter. The compliance must be **calibrated by measuring clamped current into a short with the precision ADC**, not trusted open-loop.
- **Programmability required for CAUTION 3:** VCSRC/VCSNK must be driven by **DAC channels, not trimpots**. DAC update rate must be ≤ segment rate (tens of ms); DAC noise on VCSRC injects directly into Icc. Firmware must update VCSRC/VCSNK **before** each sweep segment and verify with a read-after-write; a hard-wired divider fails.

**When Option A passes:** Only if it is augmented with (i) per-segment DAC-driven VCSRC/VCSNK, (ii) downstream-C budgeting and R_iso, (iii) slew limit, and (iv) an independent supervisor (ENABLE latch) — at which point it **is** Option D with LT1970A as the regulation leg.

> **IR-01 constraint (LT1970A floor):** Vc <60 mV is nonlinear, Vsense_min 4 mV typ (VCSRC/VCSNK <60 mV not linear, VSENSE limited to 4 mV to prevent simultaneous source/sink). → I_min = 4 mV/Rsense ≈ **4% FS at 100 mV FS** or **16% FS at 25 mV FS** (8% at 50 mV). A universal **0.1% of I_range** is not achievable with LT1970A alone (would require 4 V burden); 0.1% only via **compliance-aware range coercion (Solution A)** or **precision external loop / Candidate C (Solution C/D)** — see `docs/research/PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md` IR-01 solutions A–D and `DEC-024`. Phase 3 tests A,B verify per-range floor and coercion; see also `simulation/PHASE3_SIMULATION_PLAN.md` tests A,B.

---

### 3.2 Option B — External Analog CV/CC Loop (Diode-OR / Limiter Pattern)

```
                ┌─ V-error amp (SENSE divider, ADA4522-2) ─┐
DAC ─┤ mux ├───┤                                              ├── diode-OR/limiter ─→ power stage ─→ Rsense ─→ R_iso ─→ DUT
     (V/I mode) └─ I-error amp (shunt-sense, ADA4522-2)  ───┘               ↑
                                      ↑ compliance ref (DAC)             feedback mux
                                   CV/CC mode auto-crossover
```

ICNavigator / Keithley 2400 / TI DAC reference-drive / NI Best Practices pattern: two error amplifiers share a common node via limiter; whichever demands lower drive wins.

**Strengths:**

- True **flat CC regulation** with measurable compliance knee; best forming quality (fabrication-scale ON/OFF variability lowest). Overshoot typ <0.1% into resistive load on 2400, 30–70 µs recovery — best of the four.
- Closed-loop both in CV and CC; load regulation is servo-grade in either mode. In V-source mode the I-loop *is* the compliance; its reference is Icc — so the compliance value is the servo's setpoint, not an auxiliary clamp.
- Most faithful to commercial SMU semantics; calibration of compliance is simply calibration of the I-loop.

**Weaknesses:**

- **Two stable loops that must hand off cleanly.** Each loop needs its own compensation for its load (R vs C). Crossover must be glitch-free; capacitive DUT + shunt L + lead L can provoke oscillation in current mode especially. TI app-note warns R-2R DAC reference current is code-dependent — without buffered force/sense reference drive, both loops inherit INL bow.
- **No independent trip:** the diode-OR structure *is* single-point. If the CC amp oscillates or a rail sags, there is no catcher. SOA still needs a separate supervisor.
- **Moderate–high complexity:** +2 zero-drift amps + compensation networks + analog mux + compliance DAC. Calibration doubles (per-loop offsets/gains, compliance DAC INL separate from force DAC).
- **Energy blind spot identical to A:** diode-OR does not remove downstream C. Still needs R_iso + budgeting.

**Verdict on CAUTIONs:** B is the best *regulation* topology but by itself fails CAUTION 1 (downstream C) and fails trip independence (single-loop). Upgrading B with an independent comparator + SOA is exactly **D**.

---

### 3.3 Option C — Fast Trip + Coarse Clamp (Comparator-Driven)

```
Shunt/TIA sense ─→ window comparator (TLV3501 4.5 ns / TLV7031 low-power) vs compliance DAC ref
                    → latch (SR) → ENABLE / gate on power stage (or foldback pull on amp input)
                    → flag + firmware fault; hysteresis + blanking to avoid chatter on DUT noise/inrush
Coarse regulation: optional foldback resistor or power-amp internal 800 mA limit as coarse envelope
```

- Can be made **<1–5 µs** threshold-to-clamp with a modern comparator + analog switch, independent of MCU clock; survives MCU halt because it is pure hardware.
- Hysteresis and **blanking/dwell** are mandatory to avoid chatter on a noisy ReRAM DUT or on a hot-plug / relay-switch inrush (which can inject `I=C·dV/dt` spikes that exceed Icc momentarily).

**Strengths:** Mandatory safety fallback in *every* architecture (REQ-SAFE-001 literal minimum); cheapest, most testable protection; deterministic with MCU dead.

**Weaknesses — why it fails as "compliance":**

- Behavior at limit is **collapse/shutdown**, not **regulation**. The I–V at the limit is not a flat CC line; reading during fault is not a valid operating point. ReRAM multilevel formation (UC-4: Icc ladder → distinct LRS) requires a *controlled current plateau*, not an abrupt crowbar — crowbar'd SET still overshoots before trip and then loses the plateau that sizes the filament, worsening cycle-to-cycle spread.
- **Inductive kick** if wiring has series L and the crowbar opens fast; **oscillatory ping-pong** if it auto-retries without dwell (relay/autorange chatter).
- Coarse clamp adds little — before trip the only regulation is whatever the DAC + Rsense tolerate.

**CAUTION 3 note:** Trip threshold is programmable via DAC, so per-segment thresholds are feasible, but the *semantics* per segment should not be "±sweep limit = crowbar level" — the read segment expects a low CC plateau, not a trip that aborts the read. The trip is properly configured **above** the highest regulation limit (e.g. I_regulation=100 µA, I_trip=150 µA) as a safety net, not as the regulation itself.

**Verdict:** C is **required as the supervisor**, but **not sufficient as the compliance**. In taxonomy terms, ship **both** loops — C as the fault layer, B (or LT1970A's built-in limiters) as the regulation layer. That's D.

> **IR-08 — TLV3501 as emergency supervisor (not precision):** TLV3501 Vos max **6.5 mV** (typ 1 mV), hysteresis **6 mV** → at 100 mV FS **6.5% error** (100 mV) and **26% at 25 mV FS** (worst-case Vos alone; plus 6 mV hysteresis adds 6% at 100 mV, 24% at 25 mV). Even typical 1 mV is 4% at 25 mV. Therefore the window comparator is a **loose emergency threshold (e.g., 120–150% of Icc_reg, <5 µs, hardware latch/disable)** with **10–25% tolerance**, not a precision CC regulator. Precision CC is the LT1970A / external error-amp loop; trip tolerance is a separate Monte Carlo deliverable (IR-16 H: shunt 0.1% + DAC INL + amp offset + comparator Vos). See `PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md` IR-08.

---

### 3.4 Option D — Dual Continuous Regulation + Independent Trip/SOA (Recommended)

```
                    ┌─────────────────────────── continuous regulation ──────────────────────┐
                    │  (Option B diode-OR OR LT1970A ISRC/ISNK built-in limiters)            │
 DAC_force ───────────► takes control at Icc_reg, flat CC, valid reading                   ├──► power stage ─→ Rsense ─→ R_iso ─→ DUT
                    │  reference = DAC_cc (per segment, per polarity)                        │
                    └─────────────────────────────────────────────────────────────────────────┘
                                              ↕ independent
                    ┌─────────────────────── fast emergency trip ───────────────────────────┐
 Shunt/TIA ─────────────► window comparator (TLV3501-class, <5 µs) + SR latch               ├──► ENABLE / load switch (high-Z) + fault
                    │  threshold = DAC_trip (typically 1.3–1.5× Icc_reg, or SOA hyperbola) │
                    └─────────────────────────────────────────────────────────────────────────┘
                                              ↕
                    ┌─────────────────────── SOA / power monitor ──────────────────────────┐
     Vmeas × Imeas ─────► analog multiplier or fast MCU-less hyperbola comparator           ├──► foldback / disable if |V·I| >50–60 mW
                                                            (or thermal flag TSD)
                    └─────────────────────────────────────────────────────────────────────────┘
                                     All flags: OR'd to supervisor latch
                                     Downstream-C budget + R_iso + slew limit always mandatory
```

**Why only D satisfies the full triad:**

1. **Compliance regulation (flat CC, flagged, reading stays valid)** — the *continuous* leg handles forming and multilevel. It logs `IN_COMPLIANCE=1`, `compliance_type=regulation`, `Imeas≈Icc±error`. The DUT is never removed from circuit.
2. **Range compliance** — firmware invariant `Icomp ≤ I_range` (or autorange raises range before the step); range-change holdoff (measure range steered to compliance range *before* the voltage step to absorb C·dV/dt) as on Keithley/NI.
3. **SOA / emergency trip (shutdown)** — the *independent* fast comparator + latch removes output when regulation cannot hold (short, DUT snap with large C, thermal, or `|V·I|` > hyperbola). It logs `FAULT_OC/FAULT_SOA`, `OUTPUT_DISABLED`, latched until explicit clear or power cycle. It is **independent** of the regulation loop's amplifier (different supply, different reference), survives MCU hang, and covers the single-failure case of the regulation loop oscillating.

**CAUTION 3 realization in D:**

- Two DAC channels: **DAC_cc** (regulation reference) + **DAC_trip** (emergency threshold), or equivalently single DAC for LT1970A's VCSRC/VCSNK plus a second comparator reference. Firmware updates both **once per segment** before arming that segment; recommended API `SEG_CONFIG[seg].Icc_reg`, `SEG_CONFIG[seg].Icc_trip`, `SEG_CONFIG[seg].polarity_enable` (`SRC_ENABLE`/`SNK_ENABLE` independently). Example waveform compile:
  ```
  seg0: 0→+Vmax  Icc_reg=+100µA  Icc_trip=+150µA  snk_disable
  seg1: +Vmax→0  Icc_reg=+100µA  Icc_trip=+150µA  (same)
  seg2: 0→-Vmax  Icc_reg=DISABLED  Icc_trip=-15mA (high, RESET needs current)
  seg3: Vread=+0.2V  Icc_reg=+50µA  Icc_trip=+100µA  autorange 10µA range
  ```
- DAC voltages must settle to <1% before segment start (AD5686R settling ~5–10 µs → 1 ms inter-segment dwell is ample). Software pre-check: reject `Icomp > I_range` when autorange is off; when autorange is on, schedule a range raise *before* the segment.

**LT1970A embedding within D (low-risk V1 instance):**

- Use LT1970A's built-in ISRC/ISNK limiters as the **continuous regulation** leg (they already are transconductance CC amps with diode-OR behavior, 4 µs, 1%, flags). Drive VCSRC/VCSNK from two DAC channels via COMMON-referenced, filtered, unity-gain buffer (sense: DAC → RC 1 kΩ + 10 nF → ADA4522-2 buffer → VCSRC pin to filter DAC noise).
- Add an **external window comparator** (e.g. TLV3501 dual) on the system shunt/TIA sense (post-power-stage, downstream of Rsense but upstream of R_iso) vs an independent **DAC_trip** reference, with ~5% hysteresis, blanking 2 µs for capacitive inrush. Its output drives a **hardware SR latch** (cross-coupled NAND or dedicated supervisor like MAX16054) whose Q gates the LT1970A ENABLE pin (active-low disable via pulldown + latch) and a **series load switch** (ADG1419 / OPA load switch) after R_iso to quarantine upstream C.
- Add an **SOA hyperbola check**: simplest is `|V_force_measured| × |I_measured| > 60 mW` — implemented as window comparator on a coarse analog multiplier (e.g. AD633) or, if analog multiplier is deemed excessive for V1, as continuous firmware check (REQ-SAFE-002 polygon) *plus* an analog V-limit comparator (voltage across DUT >5.5 V → trip) and current-limit comparator (above) whose coincidence implicitly limits power on this ±5 V/±10 mA envelope. Explicit analog `V×I` is preferred for hardware independence; at V1 power the product check reduces to "if |I|>12 mA regardless, trip" because 5 V×12 mA=60 mW — a fixed current ceiling already enforces SOA on the ±5 V rail.

This embedding reuses a characterized power stage (LT1970A thermal + flags proven) while still providing the mandatory trip independence — a lower schematic risk than designing a discrete CV/CC diode-OR from scratch under Phase-2 schedule.

---

## 4. What "Programmable Per-Segment" Means Electrically (CAUTION 3 Detail)

**Not programmable = rejected.**

| Bad (fails CAUTION 3) | Why it fails | Fix (CAUTION 3 compliant) |
|---|---|---|
| Trimpot on VCSRC to set one global Icc | Cannot change between +sweep / –sweep / read; forming recipe is hard-wired; RESET and read cannot share the same limit | DAC channel per limiter (VCSRC and VCSNK) via filtered buffer; firmware writes per segment |
| Single resistor on comparator ref | Same — one threshold for all polarities; bipolar RESET needs opposite polarity disabled | Two thresholds (or window), independently DAC-set; polarity-gating logic selects which limiter/comparator is armed per segment |
| `if compliance_hit → loop forever` firmware while, no hardware latch | Firmware-alone fails REQ-SAFE-001 "independent of firmware" plus watchdog case | Hardware SR latch + supervisor; firmware only *logs* and *clears* with explicit command after dwell; watchdog timeout → latch disables output |
| Range-locked compliance (10 µA decade only as range max) | Requested 50 µA requires 100 µA range → silently 100 µA range compliance, not 50 µA; violates "value within range, down to 0.1% of range" | Continuous Icc within range; calibration LUT per range; compliance DAC INL separate from force DAC; log both `Icomp_set` and `Imeas_clamped` |

**Firmware contract for CAUTION 3:**

- SCPI-like: `SOURCE:VOLT:SWEEP:SEGment<n>:CURRent:LIMit:REGulation <value|DISABLED>` and `...:LIMit:TRIP <value>` plus `...:POLarity SRC|SNK|BOTH|NONE`.
- Pre-arm check: driver rejects `Icomp_reg > I_range` unless autorange enabled; if autorange enabled it **raises range first**, then ramps DAC, then enables segment (range-change holdoff avoids C·dV/dt false trip).
- Logging: every ADC conversion logs `{range_state, Icomp_reg, Icomp_trip, compliance_flag, compliance_type=REG|TRIP|RANGE|SOA|NONE, fault_flags, ENABLE_state}`. A point taken while `compliance_flag=REG` is marked "compliant — Vmeas drooped"; a point during `FAULT` is **not** entered as a valid operating point.
- Safe default: on power-on, brown-out, firmware reset, or watchdog, the hardware defaults to **lowest-current limit** (VCSRC/VCSNK pulled to ~50 mV via pulldown/divider → smallest Icc, e.g. 10 µA with Rsense=500 Ω → 10 µA) **or** output disabled (ENABLE pulled low via supervisor's power-on-reset) — per REQ-SAFE-003, whichever is wired as safer. Most designs choose "disabled" as safest and also pull VCSRC/VCSNK low via 100 kΩ to GND so a spurious ENABLE cannot energize at high current.

---

## 5. Stored Energy and the Mandatory Output-Node Design (CAUTION 1)

Full numerics live in `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md`. Summary for architecture choice — canonical per IR-14: **C_UPSTREAM ≤10 nF before R_iso** (compensation/decoupling, isolated from DUT); **C_DOWNSTREAM ≤80–150 pF after R_iso** (connector+trace+relay+cable+DUT+ESD, recipe-dependent — 80 pF @5 V for 1 nJ gentle, 500 pF @2 V, 160 pF @5 V for 2 nJ standard). Only C_DOWNSTREAM counts toward `E = ½ C V²` filament dump. A synthesis line stating "low output C ≤10 nF" without upstream/downstream distinction is superseded.:

### E = ½ C V² — Cost per Capacitance at V1 Rails

| Capacitance on DUT node | Energy @ 5 V | Energy @ 2 V | vs ~1 nJ gentle budget |
|---|---|---|---|
| **10 pF** (tiny pad only) | 0.125 nJ | 0.02 nJ | ✅ well within |
| **100 pF** (1 m coax) | 1.25 nJ | 0.20 nJ | ⚠️ at 5 V already over gentle 1 nJ; OK at 2 V |
| **470 pF** (long coax + deco cap) | 5.9 nJ | 0.94 nJ | ❌ fails gentle at 5 V |
| **1 nF** (array DUT + cable) | 12.5 nJ | 2.0 nJ | ❌ fails all but forming-tolerant |
| **10 nF** (output compensation on DUT node) | **125 nJ** | **20 nJ** | ❌ catastrophic — 25–125× over budget |

**Implication:** No architecture can advertise "<5 µs trip" while leaving 10 nF directly on FORCE_HI. The trip flag may assert in 4 µs while 125 nJ has already been delivered in <1 µs through the filament.

### Mandatory Output-Node Topology (all options, but required for D)

```
LT1970A OUT  →  C_comp (4.7–10 nF) + local decoupling ──→ (feedback pickoff after R_iso, not before)
               │
               Rsense (Kelvin SENSE+/–; for LT1970A tie SENSE+ to OUT, load on far side of Rsense
                        — check datasheet linear range VCC–1.5 to VEE+1.5)
               │
               R_iso (33–47 Ω thin-film, non-inductive) ──→ isolation switch (ADG1419 / load switch, optional) ──→ FORCE_HI connector
                                                            │                          │
                                                         FORCE_SENSE_HI pickoff ──────┘ (Kelvin)
                                                            │
                                                      cable (≤0.5 m, ≤50 pF) → DUT
                                                      downstream C budget ≤80–150 pF
```

- **C_comp upstream of R_iso:** Stability capacitor is *between Rsense and R_iso* (or before Rsense with feedback after R_iso), not on the DUT-side of R_iso. R_iso decouples upstream C from the DUT's RC — the filament sees only downstream C.
- **R_iso 33–47 Ω:** Slows delivery (τ=R·C, ~1.6–4.7 ns per 50 pF) and gives the comparator finite time; limits dump current into a short to V/R_iso ≈106 mA @5 V/47 Ω for only RC time. Thin-film, 100 ppm/°C, 100 mW rating is ample (10 mA DC →1–4.7 mW).
- **Feedback after R_iso (Kelvin):** The SMU's voltage error amp or LT1970A's +IN divider must sense **after** R_iso (at the FORCE connector or ideally at SENSE_HI) so R_iso drop is corrected. Otherwise load regulation = R_iso + wiring and the force accuracy collapses with current. See §7 (stability).
- **Downstream-C budget:** PCB + relay Coff ≤20 pF, cable ≤25 pF (0.5 m low-C coax), DUT fixture ≤30 pF → ~75–100 pF total → **0.9–1.25 nJ @5 V, 0.15–0.20 nJ @2 V** → within budget at primary ±2 V window; at 5 V forming the same budget is right at the edge, so advise forming at ≤3 V where possible or stuff the active-discharge FET.

### Supplemental Actuation (grade by necessity)

| Actuator | When to stuff | Sizing | Leakage constraint |
|---|---|---|---|
| **DAC slew limiter** (firmware ramp, analog RC) | **Always** — cheapest, always effective | dV/dt ≤0.1–1 V/ms → I=C·dV/dt ≤0.05–0.5 µA @100 pF–1 nF, well below any Icc | None |
| **R_iso** | **Always** | 33–47 Ω | Must not add TC error in force path if feedback not Kelvin (but Kelvin fixes it) |
| **Series isolation switch** (load switch between R_iso and DUT) | When user requests 1 m+ cable or active-discharge policy | R_on <0.5 Ω, leakage <1 nA (photoMOS or ADG1419 ~10 pA typ) | Must be ≤50 pA to keep 100 nA range honest; gate leakage matters more than channel |
| **Shunt discharge FET** (across FORCE_HI–LO, downstream of switch) | When long cable is contractually allowed; otherwise unstuffed | R_on 2–10 Ω, dumps 100 pF@5 V in <1 µs to ground without filament | Must be **disabled** during normal measure or it *is* the DUT; include hardware interlock "discharge only when latch says FAULT" |

A **poly fuse (PTC / poly-switch)** — sometimes proposed as "compliance" — is explicitly **not** any of these. Its trip time at 2× hold is **10 ms–1 s** (ABB TB82 — polymer heating, latches until power cycle), with ~1:2 hold:trip ratio, ±30–50% spread, and 0.05–5 Ω cold resistance that corrupts low-current ranges. It protects the ±12 V supply rail against a board short, not the DUT against a filament overshoot. It may coexist as a **supply-rail SOA fuse upstream** but must never be in the DUT path for the 100 nA–10 mA decades.

---

## 6. Stability — Capacitive Load, Kelvin Leads, and Compensation

### 6.1 Capacitive-Load Pole (NI / Keithley High-C Mode)

A power stage driving C_load through output impedance R_out creates a load pole `f_p=1/(2π R_out C_load)`. For an un-isolated LT1970A, R_out≈0.1–1 Ω closed-loop; C_load=1 nF → f_p≈160 kHz–1.6 MHz — inside the 3.6 MHz GBW → phase margin collapse → ringing or oscillation. With **R_iso=47 Ω**, f_p=1/(2π·47·100pF)≈34 MHz (benign); even with 10 nF upstream, f_p≈340 kHz but that C is *isolated* by R_iso and the loop's phase shift is now dominated by the upstream network that the compensation was designed around.

Sun Yat-Sen SMU stability paper (IOP 2383-012059) makes the same point: the capacitive-load loop must be modeled as `SMU output impedance + cable R/L + DUT C` inside the feedback. The **NI SourceAdapt** topology solves it with a fully programmable integrator (GBW) + pole-zero compensator in an FPGA; an analog V1 must instead provide:

- **Lead-compensation capacitor** across the voltage feedback divider (10–47 pF) to cancel sense-cable phase lag.
- **Selectable High-C mode**: slow the loop (reduce GBW via larger miller C or a series R-C to ground on the compensation pin) when driving >470 pF — trades speed for stability, exactly as Keithley 2450 High-C does ("internal capacitor across sense resistor").
- **ngspice sweep** (REQ-GEN-001) over `R_DUT 10 Ω–1 MΩ`, `C_load 10 pF–10 nF`, `R_iso 10–100 Ω`, `sense lead C 0–100 pF`, with open-loop gain/phase and closed-loop step response; require PM >45°, overshoot <10% after R_iso+compensation. Worst-case ranges are the extremes: **10 Ω @10 mA** (low-R, high-current, needs current headroom) and **1 MΩ with 100 pF @100 nA** (high-R, high-Z, most noise-gain). The 1 MΩ case is the phase-margin limiter for the *voltage* loop; the 10 Ω case for the *current* loop.

### 6.2 Kelvin Sense Lead C (Feedback-Site Pole)

SENSE_HI/LO are high-Z (≈GΩ input to sense diff-amp/ADC buffer) but their capacitance to ground/shield (50–100 pF/m) adds phase lag **inside the feedback path** when the feedback divider is taken at the sense connector and loaded by that C. Keithley 2450 High-C note: "sense resistor and external capacitance form a pole → internal capacitor across sense resistor". Same physics at V1 scale.

Mitigations: keep sense leads **short, matched, shielded but not capacitively loaded**; add the feedback divider's pole-zero cap; consider **shield driver** (sense guard buffered to cable shield) in V1.1 if 100 nA noise suffers — but triax guard proper is V2 (REQ-DUT-003 deferred).

### 6.3 Shunt/Range-Dependent Noise Gain

In a range-switched architecture each range has different R_shunt (10 Ω @10 mA →1 MΩ @100 nA) → noise gain + feedback attenuation change → phase shift moves. A single compensation cannot cover all ranges optimally — commercial D does it with a state machine. V1 should at least **compensate for the two extremes** and document the compromise table; auto-compensation switching per range via analog mux is a V1.1 stretch goal.

---

## 7. Compliance Regulation vs Range Overload vs SOA / Emergency — How Firmware Tells Them Apart

Firmware must never conflate these three into a single `COMPLIANCE=1` bit.

| Event | Source that asserts it | Hardware vs firmware | Latching | How to clear | What the log entry must contain | What operator action is implied |
|---|---|---|---|---|---|---|
| **Compliance *regulation* (flat CC)** | Analog limit amp (LT1970 ISRC/ISNK or I-error amp diode-OR) + flag ISRC/ISNK | **Hardware** (DAC sets ref) — firmware only logs; survives MCU halt | **Not latched** — flag follows the operating point; de-asserts when DUT exits CC | Automatic when `|I_DUT| < Icc` again | Flag, Icc_reg, Vmeas drooped, range, timestamp, temperature | **Continue** — point is valid, label it; consider raising stop voltage or lowering Icc next sweep per recipe |
| **Range overload/compliance** | Range shunt rating / range comparator (`I > I_range_max`) | Hardware + firmware coercion (`Icomp ≤ I_range` invariant); autorange may raise range | **Not latched** (range state changes) | Autorange raises range (with 2-sample hysteresis, per REQ-MEAS-004) or user changes range | New `range_state`, coerced `Icomp_effective`, warning "range compliance — not user compliance" | **Check recipe**: user Icc may be silently clamped by range → 10× surprise; re-configure range/compliance before repeating |
| **SOA / emergency trip** (crowbar / foldback / thermal / product trip) | Window comparator `|I| > I_trip` (independent ref) *or* `|V·I|>60 mW` hyperbola *or* TSD thermal *or* supply fault | **Hardware latch** — SR latch + supervisor; **independent of MCU** (REQ-SAFE-001 "with MCU halted" test) | **Latched** — output disabled/high-Z until explicit clear; survives transient | Explicit `OUTPUT:PROTECTION:CLEAR` or `*CLS` + re-enable after dwell + operator acknowledge; watchdog also requires re-arm | `FAULT_OC/SOA/OT`, latched, Vmeas/Imeas at fault, supply status, temperature | **Halt sweep** — do not log fault point as valid; inspect DUT/wiring; do not auto-retry without dwell (prevents relay chatter / inductive kick) |

Visual rule for plots and CSV: **never** interpolate between a normal point and a fault point — gap the line. A tripped sweep must show a distinct marker.

---

## 8. Recommended V1 Instance — D Built Around LT1970A (Lowest Risk)

The text above already specifies it; here for the PCB team as a wiring checklist (still provisional, no kicad):

**Power and signal:**

- [ ] ADR4525-class 5 V reference → RC filter (1 kΩ + 4.7 µF // 10 nF) → LT1634 buffer → star to DAC reference pins. Reference drives both force DAC and compliance DACs via buffered force/sense (TI SBAA332 guidance: do not load R-2R ladder directly).
- [ ] AD5686R Ch A → RC → gain stage → LT1970A +IN.
- [ ] LT1970A rails ±12 V (REQ-PWR-003 provisional, verify headroom for ±5 V + burden 100 mV + dropout), thermal pad to copper pour + vias, bulk decoupling 22 µF // 100 nF per rail at the chip.
- [ ] LT1970A OUT → Rsense (two-value or range-switched; Kelvin SENSE+ at OUT side, SENSE– after Rsense) → R_iso 33–47 Ω → optional series switch (ADG1419) → FORCE_HI banana/BNC (guard provision per LOW_CURRENT §4, no mask, stitched inner plane).
- [ ] C_comp 4.7–10 nF **between the node after Rsense and ground**, but **before R_iso** — with feedback pickoff after R_iso (sense point), so C_comp is not on the DUT side.

**Compliance refs and flags (CAUTION 3):**

- [ ] AD5686R Ch B → buffer → VCSRC (LT1970 source limit), Ch C → buffer → VCSNK (sink), each with 1 kΩ + 10 nF RC for DAC noise filtering (DAC noise injects directly into Icc). VCSRC/VCSNK pulled to ~50 mV via 100 kΩ to COMMON via supervisor's safe-default network so a floating DAC cannot command max current.
- [ ] LT1970A ISRC/ISNK (open-collector, up to 10 mA sink) → 10 kΩ pull-ups to 3.3 V rail → MCU GPIO (with interrupt) **and** supervisor OR input. ISRC = source limiter active, ISNK = sink limiter active.
- [ ] Independent trip DAC: AD5686R Ch D → buffer → window comparator reference (TLV3501/TLV7031 dual, <5 µs). Inputs: shunt/TIA differential sense (amplified via ADA4522-2) vs DAC_trip. Threshold typically **1.3–1.5× Icc_reg**; per-segment programmable. Add 5% hysteresis + 2 µs blanking (RC + latch) to reject C·dV/dt inrush on range changes.

**SOA and supervisor (trip layer, D):**

- [ ] Fixed thermal flag: LT1970A TSD open-collector → supervisor OR input, also MCU GPIO.
- [ ] Optional analog hyperbola: `V_force_after_R_iso × I_sense` via AD633 (or a fast dual-threshold coincidence: `|V|>5.5 V` comparably plus trip comparator — enforces 60 mW only at the V1 rails without a multiplier). Selected as V1 stretch — if omitted, firmware polygon + `I_trip` coincidence already enforces SOA at ±5 V/±10 mA.
- [ ] Hardware latch: cross-coupled NAND (SN74LVC2G00) or MAX16054 supervisor + SR latch → output Q drives LT1970A ENABLE (low = disable) and series switch OFF; MCP supervisor (e.g. STM809) holds ENABLE low during supply ramp / watchdog. Q is **latched** until MCU writes `PROTECTION:CLEAR` which issues a pulsed clear after dwell and only if fault source has de-asserted.

**Safe state (REQ-SAFE-003/004):**

- [ ] Power-on RESET (supervisor POR) holds ENABLE low for 200 ms; then release only if MCU heartbeat GPIO is toggling. Watchdog timeout pulls ENABLE low directly (no firmware mediation). Brown-out (<90% of 3.3 V rail) → same.
- [ ] Compliance refs default to **lowest current** via pulldowns described; firmware must *actively* raise them to the recipe value — no passive high-current default.
- [ ] All faults/states logged with temperature (REQ-SAFE-006: sensor per zone — output stage, shunt, reference → NTC or TMP117) and raw ADC codes.

**Kelvin and guard:**

- [ ] SENSE_HI/LO are high-Z, differential, star at DUT connector (not at shunt). Sense input bias <<100 pA, ESD leakage <50 pA on 100 nA range path. **Sense-open detection: switched continuity test before OUTPUT ON + analog-switch disconnect during measurement (e.g., ADG1419-class, ~10 pA leakage); weak pull network (10 MΩ) only behind switch, not permanent — no DC load invariant during valid measurement (IR-03); if a fallback bias must remain, ≥10 GΩ effective and characterized at 40 °C/humidity.**
- [ ] Guard provision (REQ-DUT-002): exposed guard ring around high-Z sense nodes, no-mask copper, stitched inner guard plane, C0G-only on high-Z path — not claimed as guard performance, but not precluding V2 electrometer daughter card (REQ-DUT-003 future). DUT-node capacitance budget per IR-04 / COMPLIANCE_ENERGY_ANALYSIS §2.5: connector+trace+relay+Cable+buffer Cin+ESD+DUT ≤ C_DOWNSTREAM budget (80–150 pF @5 V, not the 1 nF post-buffer filter — IR-04/IR-14).

**Verification gates before any ReRAM DUT (REQ-CAL-002, ENGINEERING_RULES #9–10, RISKS R-03/R-12):**

- [ ] **Short + step load** into precision 100 Ω (10 mA regime) and 10 kΩ (100 µA regime) with 47 pF / 470 pF / 1 nF capacitive loads; scope shunt voltage and ISRC/flag timing; check overshoot <1% resistive / <5% into 1 nF with slew limit, flag latency <5 µs trip / <50 µs regulation settled.
- [ ] **MCU-halted** fault injection: hold MCU in reset (or remove its supply jumper), short FORCE_HI to FORCE_LO, ramp V_force manually → verify latch asserts <5 µs and output enters high-Z without firmware.
- [ ] **Capacitive dump** integration: pre-charge DUT node to 5 V, close relay onto LRS resistor, integrate I(t) on scope → delivered energy must match ½CV calculation within 10% and remain inside the per-segment budget.
- [ ] **Slew-rate** test: 0→5 V in 10 µs vs 5 ms into 100 pF; verify displacement spike vs compliance threshold with range-change holdoff.
- [ ] **Thermal soak** at Icc=100 µA: monitor I_clamped over 100 s with temperature log; verify drift within accuracy envelope (LT1970A junction temp + Rsense TC + DAC drift).

---

## 9. Firmware / Software Envelope (REQ-SAFE-002, REQ-MEAS-004)

The hardware above is **complemented** by a secondary software polygon that is not the compliance (it is too slow to be, but it is valuable as a pre-check gate and a reporting layer):

- Pre-validate recipe before arming output: reject `Icomp_reg > I_range` unless autorange enabled; if autorange enabled, **schedule range raise before the voltage step** (range-change holdoff) to absorb displacement current; enforce dwell/hysteresis (≥2 samples post-trip, hold range) so compliance chatter does not ping-pong autorange.
- Soft-start: ramp DAC at controlled dV/dt (see §5), not full-scale jumps into an unknown DUT (RERAM §4 step 0.01–0.05 V / 50 ms).
- Sanity gate: `if |Imeas| >1.2×Icomp for N samples → trip` (firmware declares fault even if hardware flag has not yet latched — defense in depth, but not relied upon for filament-speed events nibb).
- SW command that respects the triad: expose `SOURce:CURRent:LIMit:REGulation`, `...:LIMit:TRIP`, `...:LIMit:SOA`, and query `STATus:MEASurement:CONDition?` bits separately for real compliance vs range vs fault (mirrors Keithley `:STAT:MEAS:COND? bit 14` pattern).

---

## 10. Open Points for Phase-3 DEC (What This Document Does Not Decide)

- Exact Rsense values / range-switched Rsense set vs single LT1970A Rsense (trade: simplicity vs per-range burden/TC). Burden table in `BURDEN_VOLTAGE_ANALYSIS.md` is the starting point — values must be re-derived with headroom + dropout (REQ-PWR-003 analysis) and with actual LT1970A SENSE common-mode limits (VCC–1.5 to VEE+1.5).
- Whether to stuff the analog multiplier or defer SOA hyperbola to coincidence + firmware polygon (cost vs hardware-independence).
- STM32G431 DAC/PWM vs dedicated AD5686R for compliance refs — jitter/noise/T C tradeoff (Q-01/Q-20).
- Confirmation that TLV3501 (4.5 ns) supply rails are compatible with the analog front-end partitioning (or TLV7031 3.5 µA alternative for low-I ranges).
- Confirmation that the chosen relays (read Coff, leakage) meet the downstream-C budget — procurement must provide Coff/Isolation numbers, not "similar to" specs.
- Detailed loop-compensation values (C_comp, feedback cap) — must come from **ngspice** (primary, per DEC-TOOL-002) before any DEC promotion. No value in this file is a schematic directive.

---

## 11. Provenance (Primary Datasheets and Sources That Informed This Architecture)

| Claim | Source |
|---|---|
| Compliance as measurement story, CV→CC limiter illustration, 4-quadrant theory | icnavigator SMU Design: 4-Quadrant & Autorange — https://icnavigator.com/applications/test-measurement-instrumentation/source-measure-unit-smu/ |
| SMU control loop = superposed V-loop + I-loop (Figure 2a/2b), integrator + pole-zero, SourceAdapt digital variant | NI SourceAdapt Next-Gen SMU — https://www.ni.com/en/shop/electronic-test-instrumentation/source-measure-units/what-are-source-measure-units/ni-sourceadapt-next-generation-smu-technology.html |
| LT1970A 1% limit, VCSRC/VCSNK ÷10, Rsense law I=V/(10·Rs), 4 µs takeover, ISRC/ISNK/TSD flags, 800 mA ultimate limit, thermal shutdown, ENABLE | Analog Devices LT1970A datasheet 1970Afc — https://www.analog.com/media/en/technical-documentation/data-sheets/1970afc.pdf |
| Range compliance vs real compliance (blinking units), `:STAT:MEAS:COND? bit 14` | Tek FAQ 70946 — https://www.tek.com/en/support/faqs/compliance-what-does-it-mean-when-units-compliance-value-blink-front-panel + TekTalk 2400 community |
| Compliance accuracy add-on 0.3% of range + 0.02% reading, 30–70 µs recovery, 0.1% overshoot typ | Keithley 2400 SMU datasheet + Keithley 2600B data sheet (referenced in COMPLIANCE_RESEARCH.md) |
| Best-practices: compliance vs protection errors, holdoff, load transient, autorange | NI SMU Best Practices: Understanding Compliance and Device Protection — https://www.ni.com/en/support/documentation/supplemental/19/smu-best-practices--understanding-compliance-and-device-protecti.html |
| High-C mode (sense resistor + C forms pole, internal cap across sense resistor, load-consideration) | Tek FAQ 2450 High-Capacitance Mode — https://www.tek.com/en/support/faqs/2450-high-capacitance-mode + NI Load Considerations |
| Load stability / capacitive-load pole / control-loop analysis for SMU | IOP 2383-012059 Research and experiment on control loop system of SMU; Texas Technologies High-C discussion |
| PTC / PolySwitch thermal trip 10 ms–1 s, hold:trip ≈1:2, latches until power cycle — not suitable for filament compliance | ABB Technical Bulletin 82 (PTC/polymer PTC section) + general PolySwitch application notes (web_search 2026-08-24) |
| RRAM overshoot = parasitic-C driven; optimum energy argument | NIST Analysis and Control of RRAM Overshoot Current + IOPscience Control of Current Compliance in RRAM: Optimized vs Minimized Parasitics |
| Transient current 10× expected → electrode damage on TiO2 | IOP 10.1088/0022-3727/45/39/395101 Elimination of high transient currents … (electroformation) |
| SMU compliance design: fallback vs regulation trade, supervisor must survive MCU hang | EEVblog forum SMU CC→CV impedance discussion + COMPLIANCE_RESEARCH.md §§4.2–4.4 |

No quantitative spec above is quoted from AI memory. Per ENGINEERING_RULES.md §1–2, the primary datasheet or scope measurement wins on every conflict. This file is provisional until Phase-3 ngspice + bench verification.

---

*Generated by Agent C for Phase 2 compliance review. Place alongside `COMPLIANCE_ENERGY_ANALYSIS.md` and `REQUIREMENTS_TRACEABILITY.md`; update STATUS.md and DECISIONS.md when a DEC promotes a topology.*
