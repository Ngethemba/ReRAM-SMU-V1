# Phase 2 Independent Review — Corrective Review Record

**Project:** ReRAM-SMU V1 — Phase 2 Corrective Review / Design-Review Patch
**Date:** 2026-08-24
**Status:** Corrective review complete — repository synchronized for Phase 3
**Gate:** No schematic/PCB/BOM/hardware created — conceptual corrections only
**Authority:** Primary manufacturer datasheets override all prior summaries and this prompt

---

## Scope and Method

Phase 2 was PASS with architecture SELECTED FOR PHASE 3. An independent review identified 16 findings (IR-01..IR-16) concerning compliance limits, sense impedance, guard/grounding terminology, stored-energy budgeting, and simulation completeness. Each finding was independently verified:

1. located original repository claim,
2. retrieved primary datasheet / project calculation,
3. independently recomputed numerical claims (Python, 2026-08-24),
4. classified verdict,
5. defined required correction.

**Verdict taxonomy:** `CONFIRMED ISSUE` · `PARTIALLY CONFIRMED` · `NOT AN ISSUE` · `REQUIRES PHASE 3 SIMULATION`

---

## Finding IR-01 — LT1970A Compliance Range vs Measurement Shunt

### Independent review claim
LT1970A internal programmable current limiter may use the same shunt bank as measurement; its law `I_LIMIT = Vc / (10·R_SENSE)` with a finite low-end nonlinear region may make a requirement such as "minimum programmable compliance ~0.1% of I_range" incompatible with proposed range shunts (10 mA … 100 nA).

### Original repository claim
- REQUIREMENTS REQ-SAFE-001 (CONFIRMED): "Icc programmable as value within range (not decade-locked), min 0.1% of I_range (Keithley rule)" — research target per DEC-011.
- ARCHITECTURE phase-2 narrative ambiguous whether LT1970A `SENSE+/−` Rsense is the same as low-side measurement shunt matrix (10 Ω–1 MΩ at 100 mV FS).
- SOURCE_STAGE_CANDIDATES: Rsense = 10 Ω example → 1 V for 10 mA etc., but per-range mapping never enumerated.

### Primary evidence
- Analog Devices LT1970A datasheet 1970afc (2015-11), LT1970 datasheet 1970fe:
  - SENSE = `VCSRC/10` (source) or `−VCSNK/10` (sink); `VCSRC/VCSNK` = 0–5 V above COMMON.
  - Transfer linear **except VCSRC/VCSNK < 60 mV**; VSENSE limits at **minimum 4 mV typical** to prevent simultaneous source/sink activation.
  - `I_LIMIT = VCSRC/(10·Rsense)` only when VCSRC ≥ 60 mV and VSENSE ≥ ~4–6 mV.
  - Setting `VCSRC=VCSNK=0` still allows `±4 mV/Rsense` quiescent (≈400 µA on 10 Ω).
- SHUNT_RANGE_TRADEOFF measurement shunts:
  - Fixed 100 mV FS → R = 10 Ω (10 mA), 100 Ω (1 mA), 1 kΩ (100 µA), 10 kΩ (10 µA), 100 kΩ (1 µA), 1 MΩ (100 nA)
  - Range-dependent D → R = 2.5 Ω (10 mA, 25 mV FS), 25 Ω (1 mA), 500 Ω (100 µA, 50 mV), 5 kΩ (10 µA), 100 kΩ (1 µA, 100 mV), 1 MΩ (100 nA)

### Independent calculation
For any shared R where the compliance law uses the same resistor:

```
I_LIMIT,ideal = Vc / (10·R)
I_min,LT1970A ≈ 4 mV / R          (nonlinear floor)
I_min,linear  ≈ 6 mV / R          (Vc = 60 mV → Vsense = 6 mV)
```

| Measurement R | I_FS | Vc for I_FS (=10·R·I_FS) | I_min (4 mV) | I_min / I_FS | Target 0.1%·I_FS | Meets 0.1%? |
|---|---|---|---|---|---|---|
| 10 Ω | 10 mA | 1.00 V | 400 µA | **4.0%** | 10 µA | **NO — 40× over** |
| 100 Ω | 1 mA | 1.00 V | 40 µA | 4.0% | 1 µA | **NO** |
| 1 kΩ | 100 µA | 1.00 V | 4 µA | 4.0% | 0.1 µA | **NO** |
| 10 kΩ | 10 µA | 1.00 V | 0.40 µA | 4.0% | 10 nA | **NO** |
| 100 kΩ | 1 µA | 1.00 V | 40 nA | 4.0% | 1 nA | **NO** |
| 1 MΩ | 100 nA | 1.00 V | 4 nA | 4.0% | 0.1 nA | **NO** |

With range-dependent D (25 mV FS on high ranges) the ratio worsens to **16%** on 10 mA/1 mA (Rs=2.5 Ω, 25 Ω → I_min 1.6 mA, 160 µA) and **8%** on 100 µA/10 µA.

*Idempotent:* I_min / I_FS = (4 mV) / (I_FS·R) = (4 mV) / (V_FS). For any V_FS = 25 mV, 50 mV, or 100 mV, `I_min = 16%, 8%, or 4%` of FS — never 0.1%. Solving `4 mV / V_FS = 0.1%` requires **V_FS = 4 V** — incompatible with headroom/burden constraints.

A separate compliance Rsense does not rescue the rule unless its V_FS is 4 V. Example: LT1970A Rs=10 Ω gives I_min 400 µA; to reach the 10 µA decade (100 µA range, 0.01 µA floor) would require Rs=400 kΩ — then Vc for 10 mA would be `10 mA·10·400 kΩ = 40 kV`, impossible. Therefore **no single Rsense satisfies 10 mA … 100 nA at 0.1% with LT1970A alone**.

### Verdict
**CONFIRMED ISSUE** — architecture A (measurement shunt = compliance shunt) cannot satisfy a strict 0.1%·I_range rule with LT1970A. The 0.1% requirement was copied from commercial benchtop SMUs whose compliance is a closed-loop servo, not an LT1970A Vc/10 threshold.

### Required correction
1. Declare architecture A **rejected** for the 0.1% rule. Canonical architecture: measurement shunt bank and compliance-sense are **distinct functions** (separate resistor networks or a precision external CC loop).
2. Reclassify the four options:
   - **Solution A — Compliance-aware automatic range coercion (lowest-risk, adopted for V1 REV-A):** requested Icomp → firmware selects the measurement/compliance range whose Vsense_FS yields an achievable Vc ≥ 60 mV (ideally Vc ≥ 0.5 V). If requested Icomp is below the LT1970A floor on the requested measurement range, the driver **raises the compliance range** (or reports error if autorange disabled). Logged as `Icomp_requested`, `I_range`, `compliance_range`, `Vc`, `Rsense_compliance`.
   - **Solution B — Separate range-switched compliance-sense resistor bank (parallel to measurement shunts):** dedicated Rs per compliance decade (e.g., 10 Ω for 10 mA, 100 Ω for 1 mA, 1 kΩ for 100 µA, etc.) switched by relay/MUX independent of measurement range. Adds relays/leakage but achieves finer Vc granularity.
   - **Solution C — Amplify shunt signal into external precision CC loop:** measurement shunt voltage amplified (ADA4522/OPA140 gain stage) → precision comparator/error amp driving LT1970A VC pin or overriding its output. Requires stabilization; moves 0.1% performance from LT1970A offset to amplifier offset/TC.
   - **Solution D — LT1970A as power stage / coarse limiter + separate precision compliance loop (textbook SMU):** precision outer voltage loop + LT1970A booster, or full dual-error-amp CV/CC diode-OR. This is **Source Candidate C** (IR-15) and is the only topology that can credibly claim 0.1% closed-loop compliance accuracy — at highest complexity.
3. Revise REQ-SAFE-001 (see DEC-024) to remove a universal "0.1% of I_range" as a CONFIRMED binding law; retain it as a **research target for the precision-loop configuration** and as a **coercion rule** for LT1970A.
4. Add Phase 3 simulations (IR-16 A,B): sweep every range for desired Icomp vs LT1970A achievable minimum, linear/nonlinear VCS region, range coercion behavior, no unsafe configuration.

### Files affected
- `REQUIREMENTS.md` — REQ-SAFE-001 revised + DEC-024 provenance
- `DECISIONS.md` — new DEC-024 (compliance minimum programmability)
- `docs/architecture/COMPLIANCE_ARCHITECTURE.md` — §3.1 rewritten to enumerate four solutions + coercion logic
- `docs/architecture/SOURCE_STAGE_CANDIDATES.md` — §2.1/§4 clarified with Vc <60 mV nonlinearity + floor table
- `docs/calculations/SHUNT_RANGE_TRADEOFF.md` — §1 note + §2.1 footnote on compliance vs measurement R
- `simulation/PHASE3_SIMULATION_PLAN.md` — tests IR-16 A,B
- `docs/architecture/REQUIREMENTS_TRACEABILITY.md` — REQ-SAFE-001 row updated

### Phase 3 impact
LT1970A primary remains for Phase 3, but **only with range coercion (A) or separate compliance bank (B) footprint** and explicit CC-loop Candidate C (D) as a parallel simulation. The 0.1% rule is no longer a pass/fail gate for the LT1970A limb alone.

---

## Finding IR-02 — Voltage Sense Input Impedance / DUT Loading

### Independent review claim
`PRELIMINARY_ERROR_BUDGET.md` models a 10 MΩ / 10 MΩ divider while architecture claims `>10 GΩ` sense impedance; a 20 MΩ differential load would severely load 100 MΩ–1 GΩ HRS devices.

### Original repository claim
- REQUIREMENTS REQ-DUT-001: Kelvin "remote sense >10 GΩ, 5 V force–sense drop, 1 MΩ lead tolerance"
- KELVIN_SENSE_ARCHITECTURE: sense lines high-Z (≈GΩ input to diff amp/ADC buffer)
- PRELIMINARY_ERROR_BUDGET §2.3: "Divider 10 MΩ/10 MΩ? For ±5 V → ±2.5 V ADC? Assume divide by 2, buffered by OPA140 (10 pA Ib → 50 nV error on 5 MΩ Thevenin). Divider ratio tol 0.01% → …" — provisional analysis hypothesis, not a schematic directive.

### Primary evidence
- ReRAM RERAM_MEASUREMENT_REQUIREMENTS: HRS 100 kΩ–100 MΩ typical, up to 1 GΩ on nanowire/polymer; read bias 0.1–0.5 V.
- Measurement requirement: DUT loading error must be << accuracy target (0.02% + offset at 100 MΩ is nA-scale).

### Independent calculation
Effective DUT impedance with a passive 20 MΩ (10 MΩ+10 MΩ) divider tied directly to DUT:

```
R_eff = R_DUT || R_sense,  R_sense = 20 MΩ differential
I_sense ≈ V_DUT / 20 MΩ
```

| R_DUT | R_eff | Error = (R−R_eff)/R | I_sense @0.5 V | I_DUT @0.5 V | Extra current |
|---|---|---|---|---|---|
| 1 MΩ | 0.95 MΩ | **4.8%** | 25 nA | 500 nA | 5% |
| 10 MΩ | 6.67 MΩ | **33%** | 25 nA | 50 nA | 50% |
| 100 MΩ | 16.7 MΩ | **83%** | 25 nA | 5 nA | 500% |
| 1 GΩ | 19.6 MΩ | **98%** | 25 nA | 0.5 nA | 5000% |

The 20 MΩ path dominates HRS measurement — unacceptable. A bare divider **cannot** be the DUT-facing element.

With a high-Z buffer (JFET/CMOS) before the divider:

```
SENSE_HI → high-Z buffer (Ib ≤10 pA) ─┐
                                      ├→ attenuation/divider → ADC
SENSE_LO → high-Z buffer (Ib ≤10 pA) ─┘
Effective R_in ≈ V_DUT / Ib
```

For OPA140-class (Ib max 10 pA, typ <1 pA): at 0.5 V on 1 GΩ (0.5 nA DUT current), buffer leakage 10 pA = **2%** of signal (max), ~0.2% typical. Electrometer-class (ADA4530-1, Ib <1 fA) would be 0.0002% but not required for V1 MUC 1 nA.

Candidate classes (verified families, not specific MPN promotion):
- **JFET-input precision** (OPA140/OPA2140 class): Ib 10 pA max, en 5.1 nV/√Hz, drift 1 µV/°C — optimal for ≤100 nA guard budget.
- **CMOS precision auto-zero** (ADA4522-2 class): en 5.8 nV/√Hz, Vos 5 µV, but Ib 50 pA typ → 160 pA noise on 1 MΩ — **unsuitable as shunt sense on 100 nA range** (see PRELIMINARY_ERROR_BUDGET §2.1) though fine as DUT voltage buffer if input capacitance acceptable.
- **CMOS precision JFET-competitive** (ADA4625-class, OPA828-class): Ib <1 pA, low 1/f, higher BW — viable alternate; parameterize per Phase 3.

### Verdict
**CONFIRMED ISSUE** — the draft divider hypothesis would violate REQ-DUT-001 >10 GΩ by three orders of magnitude. The architecture intent was already "high-Z diff amp >10 GΩ" but PRELIMINARY_ERROR_BUDGET wording was provisional and now inconsistent.

### Required correction
1. Canonical rule: **DUT terminals see a high-impedance buffer first; attenuation/division occurs after buffering, never directly across DUT.**
   ```
   SENSE_HI → high-Z buffer (≥10 GΩ, ≤10 pA Ib) ─┐
                                                  ├→ differential attenuator → ADC
   SENSE_LO → high-Z buffer (≥10 GΩ, ≤10 pA Ib) ─┘
   ```
2. Remove any active document statement implying a passive 10 MΩ/10 MΩ divider is the DUT load. Retain divider only as a **post-buffer** optional scaling block with explicit "after buffer" qualifier.
3. Specify buffer class for Phase 3 comparison: JFET-input (OPA140-class) as primary, CMOS precision (ADA4625/OPA828-class) as alternate; ADA4522 is for shunt/loop sense, not DUT sense on 100 nA.
4. Add Phase 3 tests IR-16 E: DUT loading sweep at 1 MΩ/10 MΩ/100 MΩ/1 GΩ, measuring error caused by sense input.

### Files affected
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` — §1 loop now shows explicit buffers + routing note
- `docs/calculations/PRELIMINARY_ERROR_BUDGET.md` — §2.3 rewritten to post-buffer topology; pre-buffer divider explicitly rejected
- `docs/architecture/MEASUREMENT_FRONTEND_CANDIDATES.md` — §2 note on buffer class
- `simulation/PHASE3_SIMULATION_PLAN.md` — test E

### Phase 3 impact
No BOM impact; adds one dual high-Z buffer footprint (SO-8/MSOP-8) before the differential/attenuation stage. Input capacitance of buffers now enters the DUT-node capacitance budget (IR-04).

---

## Finding IR-03 — Open-Sense Detection Load

### Independent review claim
Kelvin doc proposes weak pull resistors ~10 MΩ for open-sense detection; at 1 V, 1 V/10 MΩ = 100 nA, dominating nA DUT current.

### Original repository claim
KELVIN_SENSE_ARCHITECTURE §3.1: "SENSE_HI weak pull to V_FORCE/2 via 10 MΩ + SENSE_LO weak pull to ground via 10 MΩ (high-Z so normal operation unaffected). Window comparator on |V_SENSE − V_FORCE| …" and COMPLIANCE_ARCHITECTURE §8: "SENSE_HI/LO weak pull-up/down 10 MΩ + comparator."

### Primary evidence
- Benchmark: HRS read 5 nA at 0.5 V on 100 MΩ; 100 nA range MUC 1 nA.
- Any DC load tied permanently across DUT nodes contributes `I_pull = V_DUT / R_pull` to measured current.

### Independent calculation

| V_DUT | I (10 MΩ) | I (1 GΩ) | I (10 GΩ) | vs DUT current on 100 MΩ @V |
|---|---|---|---|---|
| 0.1 V | **10 nA** | 0.10 nA | 0.01 nA | DUT 1.0 nA → 10 nA dominates |
| 0.5 V | **50 nA** | 0.50 nA | 0.05 nA | DUT 5.0 nA → 50 nA dominates |
| 1 V | **100 nA** | 1.0 nA | 0.10 nA | DUT 10 nA → 100 nA dominates |
| 2 V | **200 nA** | 2.0 nA | 0.20 nA | DUT 20 nA → 200 nA dominates |
| 5 V | **500 nA** | 5.0 nA | 0.50 nA | DUT 50 nA → 500 nA dominates |

A permanent 10 MΩ pull is 10–1000× the HRS signal on 100 nA range — **not weak** at this scaling.

### Verdict
**CONFIRMED ISSUE** — 10 MΩ is 4–5 orders of magnitude too low for a permanently connected pull on the 100 nA path. Wording "high-Z so normal operation unaffected" is false.

### Required correction
Architecture must guarantee: **open-sense detection cannot meaningfully perturb nA-scale DUT current.**

Canonical strategy (adopted, matches review options):

- **Primary (A+E): Switched continuity test before OUTPUT ON + analog-switch disconnect during measurement.**
  - Firmware sequence: with output disabled, close analog switch (e.g., ADG1419-class, 10 pA leakage) connecting weak pull network → window comparator detects open vs closed → log `sense_continuity` → **open the switch** before enabling output. During valid measurement the pull network is **galvanically disconnected** by the switch/relay.
  - Alternative equivalent: very-high-value switched network (B — 1–10 GΩ) with series switch, or test-current injection only while output disabled (C), or FORCE-SENSE tracking monitor without DC loading (D). All are logically equivalent to "no DC load during measurement."

- Subsidiary specification: If a fallback "force-mode" resistor must remain (e.g., bias for undriven comparator), its value is **≥10 GΩ** and its leakage is characterized at 40 °C/humidity; 10 MΩ is retained only as a **switched test resistor behind the disconnect**, never as a permanent rail.

- New hard rule in KELVIN and COMPLIANCE docs: "No low-value DC pull network shall remain connected across SENSE_HI/SENSE_LO during a valid DUT measurement."

### Files affected
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` — §3.1 rewritten: switched detection before OUTPUT ON + E-switch disconnect; 10 MΩ now behind switch, ≥10 GΩ if permanent
- `docs/architecture/COMPLIANCE_ARCHITECTURE.md` — §8 checklist corrected
- `simulation/PHASE3_SIMULATION_PLAN.md` — test D (open-sense faults) with "no DC load during measurement" invariant

### Phase 3 impact
Adds one low-leakage analog-switch footprint (or reed) for the sense-pull network and a Phase 3 leakage verification (pull-network disconnected: residual <1 pA at 25/40 °C).

---

## Finding IR-04 — Sense Filter Capacitance vs Stored-Energy Budget

### Independent review claim
~100 Ω + 1 nF differential filter at SENSE input, if directly across DUT-connected SENSE_HI/SENSE_LO, becomes DUT-node capacitance and dominates filament overshoot (`E = ½CV²`).

### Original repository claim
KELVIN_SENSE_ARCHITECTURE §2: Kelvin lead limits — "add 100 Ω series + 1 nF diff cap at sense amp input (verify vs SENSE amp BW)…"
GROUNDING doc and others note sense lead C 50–100 pF/m but do not assign 1 nF differential cap to DUT node; placement ambiguous.

### Primary evidence
COMPLIANCE_ENERGY_ANALYSIS: at 5 V, 100 pF → 1.25 nJ, 10 nF → 125 nJ; working V1 gentle multilevel budget ≤0.5–1 nJ @1–2 V, standard ≤2–5 nJ.

### Independent calculation

| C | E @0.5 V | E @1 V | E @2 V | E @5 V | vs 1 nJ gentle budget |
|---|---|---|---|---|---|
| **1 nF** | 0.125 nJ | **0.50 nJ** | **2.0 nJ** | **12.5 nJ** | **12.5× over at 5 V** |
| 100 pF | 0.013 nJ | 0.05 nJ | 0.20 nJ | 1.25 nJ | At limit |
| 50 pF | 0.006 nJ | 0.025 nJ | 0.10 nJ | 0.63 nJ | OK |
| 10 pF | 0.001 nJ | 0.005 nJ | 0.020 nJ | 0.13 nJ | OK |

A 1 nF cap directly across DUT nodes at 5 V forming exceeds every provisional budget.

### Verdict
**CONFIRMED ISSUE**

### Required correction
1. Canonical rule: filtering after high-Z buffering, not at DUT terminals.
   ```
   DUT ─→ high-Z buffer ─→ RC/filter ─→ ADC
   ```
   The DUT sees only buffer input capacitance (≈2–5 pF) plus connector/trace parasitics, not the 1 nF filter cap.

2. Define explicit **DUT-NODE CAPACITANCE BUDGET** (counted before isolation/active buffering). All capacitance directly connected to DUT before isolation/buffer must be tallied:

| Contributor | Typical V1 | Location vs isolation |
|---|---|---|
| Connector (banana/BNC + Kelvin clip) | 5–10 pF | DUT-side |
| PCB trace (FORCE+SENSE, 1 cm each) | 1–3 pF | DUT-side |
| Relay/switch off-capacitance (Coto 9007) | 1–3 pF | DUT-side (when open) |
| Sense input (buffer input C) | 2–5 pF | DUT-side |
| ESD/protection diode (low-leakage) | 0.5–2 pF | DUT-side (if present) |
| Cable (if used, 0.5 m low-C) | 25–50 pF | DUT-side — length-limited |
| DUT package + pad | 0.5–5 pF | DUT |
| Optional diff filter cap | **must NOT be DUT-side** — placed after buffer (0 pF DUT-side) | Upstream of buffer |

Target: total **C_DOWNSTREAM** is the sum above that can dump into the filament; Phase 3 target per IR-14 determines limit (see IR-14).

### Files affected
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` — §2 lead cap moved to after buffer; DUT-node budget added
- `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` — new §2.5 "DUT-Node Capacitance Budget" cross-ref
- `simulation/PHASE3_SIMULATION_PLAN.md` — test F distinguishes sense input C from cable/DUT C

### Phase 3 impact
No change to gentle budget; clarifies that the 1 nF filter is a valid post-buffer design element.

---

## Finding IR-05 — Shunt Burden Table Conflict

### Independent review claim
Repository contains conflicting range-dependent burden assignments. `SHUNT_RANGE_TRADEOFF.md` recommends `10 mA→25 mV, 1 mA→25 mV, 100 µA→50 mV, 10 µA→50 mV, 1 µA→100 mV, 100 nA→100 mV` while some synthesis documents reverse ordering.

### Original repository claim
- SHUNT_RANGE_TRADEOFF §2.4 (RECOMMENDED D): 10 mA 25 mV (2.5 Ω), 1 mA 25 mV (25 Ω), 100 µA 50 mV (500 Ω), 10 µA 50 mV (5 kΩ), 1 µA 100 mV (100 kΩ), 100 nA 100 mV (1 MΩ). Consistent across MEASUREMENT_FRONTEND_CANDIDATES §1, DEC-017.
- BURDEN_VOLTAGE_ANALYSIS (older Phase 1 framework): fixed 100 mV FS on all ranges — intentionally superseded and explicitly marked "Phase 1 baseline" but still present.
- ARCHITECTURE block diagram: "low-side shunts 10 Ω–1 MΩ (100 mV FS)" — stale shorthand.

### Primary evidence
Recompute burden philosophy D — rationale: headroom-limited at high-I (mA), SNR/leakage-limited at low-I (nA).

### Independent calculation
Philosophy D canonical table (Python-verified, `k=1.380649e-23`, `T=300 K`, `B=10 Hz` brickwall, single-pole ENBW ×1.253):

| Range | V_FS | R_shunt | P@FS | vn 10 Hz | in 10 Hz | in/FS | Gain →2.5 V | Gain →78 mV (PGA=32) |
|---|---|---|---|---|---|---|---|---|
| 10 mA | **25 mV** | **2.5 Ω** | 250 µW | 0.64 nV | 257 pA | 0.026 ppm | 100× | 3.13× |
| 1 mA | **25 mV** | **25 Ω** | 25 µW | 2.04 nV | 81.4 pA | 0.081 ppm | 100× | 3.13× |
| 100 µA | **50 mV** | **500 Ω** | 5.0 µW | 9.10 nV | 18.2 pA | 0.182 ppm | 50× | 1.56× |
| 10 µA | **50 mV** | **5.0 kΩ** | 500 nW | 28.8 nV | 5.76 pA | 0.576 ppm | 50× | 1.56× |
| 1 µA | **100 mV** | **100 kΩ** | 100 nW | 129 nV | 1.29 pA | 1.29 ppm | 25× | 0.78× |
| 100 nA | **100 mV** | **1.0 MΩ** | 10 nW | 407 nV | 0.41 pA | 4.07 ppm | 25× | 0.78× |

Single-pole ENBW: ×1.253 → 100 nA in = 0.51 pA. At B=1 kHz ×10; at B=100 Hz ×3.16. NPLC=10 BW ÷10 → noise ÷√10.

*Reversed ordering (100 mV on 10 mA, 25 mV on 100 nA) would give 100 mV burden where Johnson is most abundant and 25 mV burden where Johnson/SNR is scarcest — opposite of optimal and inconsistent with CAUTION 2.*

### Verdict
**CONFIRMED ISSUE** — stale copies conflict with the current recommendation, but the recommended philosophy D ordering itself is correct.

### Required correction
1. Canonical section §2.4 in `SHUNT_RANGE_TRADEOFF.md` is declared **single source of truth**. All other documents shall reference it rather than duplicating independent tables.
2. ARCHITECTURE block diagram text corrected to "low-side shunts 2.5 Ω–1 MΩ (range-dependent 25/50/100 mV FS per SHUNT_RANGE_TRADEOFF §2.4)."
3. BURDEN_VOLTAGE_ANALYSIS §2 header now explicitly marks "Phase 1 baseline — superseded by SHUNT_RANGE_TRADEOFF §2.4; retained for traceability."
4. MEASUREMENT_FRONTEND_CANDIDATES §1 range-dep line retained as reference, not contradiction.
5. DEC-017 footnote added: "For Phase 3, canonical D; fallback fixed 100 mV is acceptable if per-range gain switching deferred, at cost of 75 mV extra headroom at 10 mA."

Canonical table is adopted for all Phase 3 simulations.

### Files affected
- `docs/calculations/SHUNT_RANGE_TRADEOFF.md` — header declares canonical
- `docs/architecture/ARCHITECTURE.md` — block diagram + CAUTION 2 text synchronized
- `docs/architecture/MEASUREMENT_FRONTEND_CANDIDATES.md` — §1 citation clarified
- `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md` — superseded banner
- `DECISIONS.md` — DEC-017 note

### Phase 3 impact
None on physics; ensures consistency across noise/gain/power/headroom budgets.

---

## Finding IR-06 — AD5764 Range / LSB Calculation

### Independent review claim
Phase 2 documents treat AD5764 as if a ±5 V output range exists or calculate an effective ±5 V LSB ≈153 µV.

### Original repository claim
- PRELIMINARY_ERROR_BUDGET §1.3: "AD5764 ±10 V operated ±5 V — 305 µV LSB (20 V span)" correctly noted 305 µV but also listed "AD5764 range ±5 V mode (if available ±5 V) → 152.6 µV" as an **if** — ambiguous.
- PHASE2_DECISION_MATRIX §14: "10 V span → LSB 153 µV @16-bit =1.5 mV step 1.5% → 16-bit adequate but INL matters; AD5764 (±10 V, ±1 LSB) gives margin" — mis-stated AD5764 span as 10 V.
- PHASE2_COMPONENT_MATRIX §3 (alternate DAC): AD5764 "eliminates external ×2 gain amp … INL ±1 LSB vs ±2 LSB. Requires ±12 V rails" — correct.

### Primary evidence
Analog Devices AD5764 datasheet Rev F: quad 16-bit, **programmable output range ±10 V, ±10.2564 V, or ±10.5263 V**; operates from **±11.4 V to ±16.5 V** (see IR-07). **No ±5 V range**. LSB = span / 65536.

```
Nominal ±10 V  → span 20.0 V    → LSB = 20 V / 65536 = 305.176 µV
±10.5263 V     → span 21.0526 V → LSB = 321.2 µV
```

AD5686R internal ref 2.5 V, gain=2 → 0–5 V; external ×2 → ±5 V (10 V span) → LSB = 10 V / 65536 = **152.588 µV**. The repo mixed these two.

### Independent calculation
| Device | Span used in system | LSB_eff |
|---|---|---|
| AD5686R (0–5 V → ×2 → ±5 V) | 10 V | 152.6 µV |
| **AD5764 nominal ±10 V** | **20 V** | **305.2 µV** |
| AD5764 operated ±5 V (only ±5 V of DAC codes used) | 20 V physical, 10 V used | **305.2 µV per code** (half the codes cover 10 V → resolution halved) |

Using AD5764 for ±5 V does **not** give 153 µV steps — it gives 305 µV steps with half the code range utilized. Requirement REQ-MEAS-007 source accuracy target ≤1 mV at 1 V is still met (305 µV < 700 µV target), but the budget in PRELIMINARY_ERROR_BUDGET must be re-evaluated.

### Verdict
**CONFIRMED ISSUE** — the decision matrix line "10 V span → LSB 153 µV" attributing 153 µV to AD5764 is wrong; AD5764's minimum span is 20 V.

### Required correction
1. Correct all references: AD5764 LSB = **305.2 µV** (nominal 20 V span). The "±5 V mode" row in PRELIMINARY_ERROR_BUDGET §1.3 is removed (no such mode).
2. Re-run error-budget headroom with correct LSB: PRELIMINARY_ERROR_BUDGET §1.2 post-cal at 1 V — AD5764 INL ±1 LSB = ±305 µV → u=176 µV → with correctly sized resistors/bypass the headroom at 1 V is still **≈+20%** (vs +8.8% quoted with correct LSB, still better than AD5686R −8.6% with gain stage). At 0.1 V read, LSB headroom is tighter (1.7 LSB vs 3.4 LSB for AD5686R) — acknowledged without changing the provisional accuracy targets.
3. Update comparison criteria: AD5764's INL advantage (±1 LSB vs ±2 LSB) must be weighed against its **larger span** — INL in volts is `1 LSB·span`: AD5764 ±305 µV vs AD5686R system ±305 µV (±2 LSB on 10 V span) — **equal in volts** on this comparison. The AD5764 advantage is **no external gain-stage error** (resistor TC/gain), not INL alone.
4. Decision DWG notes: do not promote AD5764 solely for "better INL" — promote only if gain-stage removal, calibration burden reduction, or BOM/reference simplification justifies its ±11.4 V supplies, higher cost, and larger span waste.

### Files affected
- `docs/calculations/PRELIMINARY_ERROR_BUDGET.md` — §1.2/1.3 tables + §5 summary corrected
- `docs/architecture/PHASE2_DECISION_MATRIX.md` — row 7 LSB corrected
- `bom/candidates/PHASE2_COMPONENT_MATRIX.md` — Decision note corrected to LSB in volts
- `docs/architecture/SOURCE_STAGE_CANDIDATES.md` — appendix DAC comparison note

### Phase 3 impact
Reopens DAC decision (Q-01) correctly — per REQUIREMENTS policy, neither DAC is promoted until Phase 3 simulation recomputes the error budget with actual span.

---

## Finding IR-07 — AD5764 Power Supply Compatibility

### Independent review claim
AD5764 bipolar operation may require analog supplies ≈±11.4 V minimum; current power-tree proposal includes precision ±10 V rails — incompatible. Robust positive LDOs (LT1763/LT3045) do not regulate negative rails.

### Original repository claim
POWER_TREE.md: "External bench ±12 V → LDOs: ±10 for source, +5 prec, 3.3 dig" and "LT1763 or 3045 ADR4525 etc." — implies ±10 V LDO rails.
PRELIMINARY_ERROR_BUDGET: AD5764 requires "±11.4..±16.5 V, 5 V logic."

### Primary evidence
- AD5764 Rev F: `AVDD +11.4 V to +16.5 V`, `AVSS −11.4 V to −16.5 V`. Nominal ±10 V output needs these rails; device offers power-up clamped to 0 V, integrated reference buffers, short-circuit protection.
- LT1763 family (Analog Devices) and LT3045: **positive LDO only** — regulate positive input to positive output; negative regulation requires complementary parts. The repo's "±10 (LT1763/3045)" conflates families.
- TLV3501 and TLK families similarly: supply 2.7–5.5 V single (or ±1.35–±2.75 V dual) — not relevant here.
- Negative regulator families: LT1964 / LT3092 / TPS7A30-class, etc., or discrete negative post-regulation.

### Independent calculation
Headroom stack for AD5764 at +10 V output:

```
AVDD ≥ VOUT + dropout_amp + margin = 10 V + ~0.8 V + 0.5 V = 11.3 V → spec 11.4 V minimum (confirmed)
```

A ±10 V LDO rail (11.0 V with 300 mV dropout from 12 V, or exact 10.0 V) **cannot** host AD5764. External ±12 V bench is adequate (1.4 V headroom above 11.4 V before LDO), but if the LDO is set to 10 V it fails.

### Verdict
**CONFIRMED ISSUE**

### Required correction
1. Power-tree options explicitly separated:
   - **Option A — Raw ±12 V bench for power stage, regulated only precision low-power blocks:** simplest for V1; AD5764 runs directly from raw ±12 V (11.4 V spec satisfied with ~0.6 V margin). Precision rail +5 V is regulated; bench ripple handled by LT1763/LT3045 post-filter on +5 V path. Accepted as V1 baseline.
   - **Option B — Regulated complementary rails:** positive rail via LT1763/LT3045-class, **negative rail via true negative regulator class** (e.g., LT1964, LT3091, TPS7A30 — placeholder families, no MPN promotion). Requires negative LDO footprint and sequencing.
   - **Option C — Separate rails for power amplifier vs precision signal chain:** power stage (LT1970A) on raw ±12 V; precision signal (AD5764/DAC/ADC/ref) on post-regulated ±12 V (positive + negative regulators) or on single-supply + charge-pump negative for the DAC alone.
2. Remove "LT1763/LT3045 for ±10 V" wording; replace with "LT1763 (positive) / **LT1964-class (negative)** pair for bipolar post-regulation" with explicit footnote that ±10 V is **not** a viable AD5764 rail.
3. Add regulator-compatibility table to POWER_TREE.md and PRELIMINARY_ERROR_BUDGET §1.2.

### Files affected
- `docs/architecture/POWER_TREE.md` — new §2.2 "Complementary regulator class" + Options A/B/C
- `docs/calculations/PRELIMINARY_ERROR_BUDGET.md` — AD5764 supply note corrected
- `bom/candidates/PHASE2_COMPONENT_MATRIX.md` — LDO alternate table: LT3045 positive vs TPS7A30/LT1964 negative branch
- `REQUIREMENTS.md` — REQ-PWR-003 headroom note now references AD5764 supply

### Phase 3 impact
No schematic promotion; adds negative-regulator family footprint option to Phase 3 trade. Option A ships REV-A; Option B/C are mutually exclusive provisioning paths.

---

## Finding IR-08 — TLV3501 Fast Trip Accuracy

### Independent review claim
TLV3501-class devices are very fast but may have input offset of order millivolts; directly comparing a 25–100 mV shunt signal, comparator offset creates large threshold error.

### Original repository claim
COMPLIANCE_ARCHITECTURE Option D: independent fast comparator latch (TLV3501-class, <5 µs) with window comparator on shunt/TIA sense vs DAC_trip; threshold typically 1.3–1.5× Icc_reg.

### Primary evidence
Texas Instruments TLV3501/TLV3502 datasheet Rev E (2015-04-17):
- Vos max **±6.5 mV** at 25 °C, typical ±1 mV; offset drift ±5 µV/°C; hysteresis **6 mV** internal; Ib typ ±2 pA, max ±10 pA; 4.5 ns propagation; supply 2.7–5.5 V single (or ±1.35–±2.75 V dual).

### Independent calculation

| FS burden (shunt) | Threshold error (Vos max 6.5 mV) | Threshold error (Vos typ 1 mV) | Hysteresis (6 mV) | Total worst |
|---|---|---|---|---|
| 25 mV (10 mA, 1 mA D) | **26.0%** | 4.0% | 24.0% | 50% |
| 50 mV (100 µA, 10 µA D) | **13.0%** | 2.0% | 12.0% | 25% |
| 100 mV (1 µA, 100 nA D) | **6.5%** | 1.0% | 6.0% | 12.5% |

Even on the most favorable 100 mV FS, worst-case Vos equals 6.5% of threshold — unacceptable as a precision compliance regulator (which requires ~1% at DEC-011). As a coarse emergency trip at 120–150% of Icomp, 10–25% is acceptable **if and only if** it is distinguished from precision regulation.

### Verdict
**CONFIRMED ISSUE** — TLV3501 cannot serve as the precision threshold for continuous compliance; it is a valid emergency overcurrent trip / supervisor.

### Required correction
1. Architecture text now explicitly distinguishes (new figure + table):
   ```
   Precision CC loop (AD4522/OPA140-class, Vos 5 µV / drift 22 nV/°C or JFET 120 µV typ)
     → accurate Icomp, flat CC regulation, flagged, reading remains valid

   Separate fast comparator (TLV3501-class, Vos 6.5 mV, hyst 6 mV)
     → looser emergency threshold, e.g. 120–150% Icomp, <5 µs, hardware latch/disable
     → does NOT need calibration-grade accuracy; 10–25% tolerance is specified
   ```
2. Compliance threshold tolerance is now a Phase 3 Monte Carlo deliverable (IR-16 H): shunt tolerance + DAC threshold INL + comparator offset + amplifier offset → trip threshold distribution reported separately from regulation accuracy.
3. Compare alternate fast low-offset comparator classes conceptually (e.g., LT1716, MAX999, ADCMP600) without MPN promotion; TLV3501 retained as **catastrophic supervisor candidate**, not precision comparator.

### Files affected
- `docs/architecture/COMPLIANCE_ARCHITECTURE.md` — Option D §3.3 rewritten + Figure updated
- `docs/calculations/PRELIMINARY_ERROR_BUDGET.md` — §1.2 note on comparator offset not in compliance budget
- `simulation/PHASE3_SIMULATION_PLAN.md` — new test H

### Phase 3 impact
No de-selection of TLV3501; re-scopes it. Adds Monte Carlo of trip tolerance including Vos max.

---

## Finding IR-09 — TIA Settling Claim

### Independent review claim
Documentation includes "TIA settling ≈ Rf·Cf/Aol" and possibly "10^6× faster" — too general. Actual settling depends on Rf, Cf, input capacitance, DUT capacitance, op-amp GBW, noise gain, parasitics, phase margin.

### Original repository claim
- MEASUREMENT_FRONTEND_CANDIDATES §2.1/§2.2: "Settling τ=R·C 50 µs @1 MΩ/50 pF → 250 µs 5τ + DA seconds" and "τ_eff=Rf·Cf/Aol → µs even at 1 MΩ with Cf" and §2.2 row "Settling — τ_eff≈Rf·Cf/Aol → µs even at 1 MΩ with Cf | Fast on TIA range; shunt ranges limited by RC+DA"
- BURDEN_VOLTAGE_ANALYSIS §3.3: "Settling divided by loop gain A≈10^6 → τ_eff≪1 µs even for 1 MΩ/50 pF (vs 50 µs shunt)"
- SHUNT_RANGE_TRADEOFF §7: "TIA settling is τ_eff=Rf·Cf/Aol effective — microseconds even for 1 MΩ with proper Cf. Shunt needs relay sequence."

### Primary evidence
Engineering review: TIA noise gain = 1+Rf/R_source + Cf effects, input C (DUT + cable 10–100 pF + op-amp Cin), Cf phase compensation, stability criterion `1/(2π·Rf·Cf) ≈ √(GBW/(2π·Rf·Cin))`.

### Independent calculation
For Rf=1 MΩ, Cf=1 pF → Rf·Cf=1 µs. With Aol≈10^6 (120 dB), naive τ_eff=1 ps — physically meaningless without considering `Cf` selection, noise gain, and GBW limit. Actual closed-loop pole: `f_{-3dB} ≈ GBW / noise_gain`; stabilization requires `Cf ≈ √(Cin/(2π·Rf·GBW))` → Cf is determined, not arbitrarily small. Settling is dominated by input C and DUT capacitance, not Rf alone. "10^6× faster" without defining Rf, Cf, Cin, and DUT C is not defensible.

### Verdict
**CONFIRMED ISSUE** (wording superseded by physics)

### Required correction
1. Remove or qualify any generic "10^6× faster" statement unless rigorously derived for a defined circuit (`Rf`, `Cf`, `Cin`, `C_DUT`, op-amp GBW, noise gain, parasitics, target phase margin). Replace with:
   > "TIA burden is ~µV, but TIA settling and stability are set by `Rf`, `Cf`, input capacitance (DUT + cable), op-amp GBW, noise gain, and phase margin, not by `R_shunt` alone; a TIA can be faster than a shunt only when its integration capacitor and compensation are sized for the specific `Rf`/`Cin`/`C_DUT` and validated for phase margin."
2. Retain V1 risk policy: **REV-A all-shunt measurement, TIA footprint/provision only.** TIA promotion requires Phase 3 AC stability sim or prototype leakage proof (per DEC-015).
3. Measurement and burden documents updated to qualified language.

### Files affected
- `docs/architecture/MEASUREMENT_FRONTEND_CANDIDATES.md` — §2.1–2.2 settling language qualified
- `docs/calculations/BURDEN_VOLTAGE_ANALYSIS.md` — §3.3 qualified
- `docs/calculations/SHUNT_RANGE_TRADEOFF.md` — §7 qualified
- `DECISIONS.md` — DEC-015 note restated as "provision only; settling claim qualified"

### Phase 3 impact
None — corrects rationale; REV-A decision unchanged.

---

## Finding IR-10 — Guard Strategy Contradiction

### Independent review claim
Guard doc says active guard is not populated in V1 REV-A but also discusses `Vguard ≈ Vsense`. A passive guard tied to the wrong node may worsen leakage rather than improve it. Rephrase distinct concepts.

### Original repository claim
GUARD_STRATEGY.md: §1 "No active guard amp in V1 REV-A — footprint optionally placed but not stuffed; driven buffer would be powered from SENSE_HI via 1 GΩ-isolated follower (not from arbitrary rail)" and §2 "guard copper … optional guard amp footprint (not stuffed)" — but later §3 "powered from SENSE_HI via 1 GΩ-isolated follower" is physically incorrect.

### Primary evidence
- Low-current guard rule: effective guard requires `V_guard ≈ V_sense` to null `I_leak = (V_sense − V_guard)/R_surface`. A guard tied to an arbitrary node injects leakage.
- Guard amplifier powering: amplifier is powered from normal rails (±12 V / +5 V), **input** tracks the relevant high-Z node, **output** drives the guard copper. It is not "powered from SENSE_HI through 1 GΩ."

### Verdict
**CONFIRMED ISSUE** — correct intent, physically incorrect phrasing.

### Required correction
1. Define canonical taxonomy (separate subsections):
   - **Passive keepout / clean high-Z zone** — no-mask copper, 0.5 mm gap, no supply; leakage is shunted to floating copper
   - **Grounded shield** — chassis/guard tied to FORCE_LO via 1 MΩ||10 nF bleed + ESD path
   - **Driven guard** — low-leakage follower (e.g., OPA140-class input) whose **output** drives the guard ring/plane, **powered from normal rails**
   - **Guard copper provision** — top ring + inner guard plane stitched every 5 mm, kept isolated from GND plane (≥0.5 mm)
2. For V1 REV-A determine: **no driven guard stuffed; no arbitrary ground guard around SENSE_HI; controlled keepout; optional driven-guard footprint; high-quality cleaning / conformal / enclosure strategy.** All §1–§3 wording "powered from SENSE_HI through 1 GΩ" removed and replaced with:
   > "The guard amplifier, if provisioned, is powered from normal power rails; its input tracks the relevant high-Z sense node and its output drives the guard."
3. If driven guard is provisioned: amplifier footprint inputs SENSE_HI, outputs to guard plane — explicitly correct node assignment.

### Files affected
- `docs/architecture/GUARD_STRATEGY.md` — rewritten §1–§3 with taxonomy + corrected powering
- `docs/architecture/MEASUREMENT_FRONTEND_CANDIDATES.md` — guard cross-ref
- `docs/research/LOW_CURRENT_MEASUREMENT.md` — §4 cross-ref unchanged (informational)

### Phase 3 impact
None on BOM; corrects footprint power pin assignment for layout review.

---

## Finding IR-11 — Kelvin Burden Terminology

### Independent review claim
Repository sometimes says burden is "not corrected by Kelvin." Can be misunderstood — if `V_SENSE_HI − V_SENSE_LO = V_SET` and SENSE is at DUT, DUT voltage is corrected despite shunt drops; physical burden remains as headroom cost.

### Original repository claim
KELVIN_SENSE_ARCHITECTURE §1: correct overall but shorthand "Kelvin corrects lead I·R_lead, it does not eliminate burden; headroom V_FORCE = V_DUT + V_burden + I·R_lead must be budgeted" — accurate but not equation-prominent.
MEASUREMENT_FRONTEND_CANDIDATES §3.3: "Kelvin corrects lead drop; burden not magically removed" — similarly shorthand.

### Primary evidence
Kirchhoff: `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` for the topology where SENSE encloses DUT only and shunt sits low-side outside loop. LT1970A alone does not inherently implement a remote differential four-terminal servo — outer loop or precise diff feedback is required.

### Verdict
**PARTIALLY CONFIRMED** — physics was largely correct, but terminology was ambiguous and LT1970A role overstated in synthesis.

### Required correction
1. Adopt canonical sentence (quoted in every architecture document):
   > Kelvin sensing does not physically eliminate shunt burden. It prevents the burden from becoming DUT-voltage error by forcing the source to provide additional headroom: `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` for the relevant polarity/topology.

2. Explicitly define differential SENSE entry into source loop (post-buffer IR-02 → diff/attenuation → error amp → LT1970A +IN → FORCE). Note: LT1970A's internal SENSE+/− is the **compliance sense across Rsense**, distinct from SMU Kelvin SENSE_HI/LO. Remote sense requires **external** differential feedback driving the source — not an inherent LT1970A four-terminal servo.

### Files affected
- `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` — canonical equation promoted to §1 header + feedback diagram
- `docs/architecture/ARCHITECTURE.md` — CAUTION 2 sentence reconciled to canonical
- `docs/architecture/SOURCE_STAGE_CANDIDATES.md` — §4.1b "feedback after burden" + LT1970A SENSE+/− vs SMU SENSE_HI/LO clarified
- `docs/calculations/SHUNT_RANGE_TRADEOFF.md` — §3 DUT-impact preamble links to canonical equation

### Phase 3 impact
None — terminology only; loop wiring is now unambiguous for simulation.

---

## Finding IR-12 — Bipolar Current Measurement Path

### Independent review claim
Low-side shunt voltage changes sign in source vs sink quadrants; measurement front-end must correctly measure ±Vshunt and zero crossing while respecting ADC/PGA CM constraints.

### Original repository claim
DEC-013/015: hybrid hybrid low-side shunt outside SENSE, ground-ref diff; MEASUREMENT_FRONTEND_CANDIDATES §1: "Hybrid — range-dependent shunt FS + per-range PGA (ADS1262 PGA 1–32)" — PCC but bipolar path not explicitly partitioned.
PRELIMINARY_ERROR_BUDGET §2.1: per-range noise/accuracy at ±50% FS but centered at 0 V; polarity transition not discussed.
Grounding doc: FORCE_LO Kelvin star correctly, but ADC common-mode requirements for negative shunt not listed.

### Primary evidence
Manufacturer families:
- **ADS1262** (TI, Rev C): differential inputs with PGA 1–32, internal 2.5 V ref, AVDD 5 V single, input range ±2.5 V differential at PGA=1 with common-mode near mid-supply; bipolar differential achievable but single-ended near GND needs bias/attenuation and buffer (internal buffers / mux inputs). Negative shunt requires level-shift or true differential measurement with FORCE_LO as ADC reference.
- **AD7175-class** (ADI): differential ±10 V-like families have wider CM but still require supply consideration; AD7175-8 ±1 ppm INL, 250 kSPS, 20 µs/ch scan — preferred for latency (Phase 2 alternate). Input buffers handle near-ground CM only if enabled (added noise).

### Verdict
**REQUIRES PHASE 3 SIMULATION** — not a typo but an omitted analysis; no schematic exists so no hardware is wrong, but Phase 3 gates are incomplete.

### Required correction
1. Add explicit Phase 3 test to PHASE3_SIMULATION_PLAN.md (test G — bipolar current front-end):
   - For **each current range** (10 mA … 100 nA): measure +FS, −FS, zero, and small bipolar signals (±0.01·FS, ±0.10·FS) around zero via I_shunt.
   - For **each ADC candidate** (ADS1262 vs AD7175-class + alternatives): evaluate input range, bipolar supply requirement, common-mode limits, PGA restrictions, input buffer behavior, zero-crossing error, negative shunt measurement.
2. Define front-end topologies for Phase 3 comparison:
   - **A — True bipolar output from sense amp** (dual supplies ±5 V, diff output centered at 0 V, ADC in differential bipolar mode)
   - **B — Level shift around ADC midscale** (single-supply amp + VCM=2.5 V/1.65 V, shunt ±V maps to ADC code midscale ±gain)
   - **C — Differential ADC directly** (instrumentation amplifier + differential ADC inputs, common-mode at GND, requiring ADC with bipolar input or external level shift)
3. No final schematic; Phase 3 must report which topology satisfies per-range PGA + NPLC + leakage budgets and which ADC supply/buffer configuration respects common-mode at −100 mV across 10 kΩ–1 MΩ.

### Files affected
- `simulation/PHASE3_SIMULATION_PLAN.md` — new tests B,G,H with bipolar front-end section
- `docs/architecture/MEASUREMENT_FRONTEND_CANDIDATES.md` — §5.3 "ADC bipolar-front-end strategy" added with A/B/C taxonomy
- `docs/calculations/PRELIMINARY_ERROR_BUDGET.md` — §2.1 footnote: zero-crossing and polarity-dependent offset

### Phase 3 impact
Adds one simulation group (bipolar front-end) and de-risks the low-side ground-ref assumption for sink operation (REQ-SRC-005 four-quadrant).

---

## Finding IR-13 — Grounding Terminology

### Independent review claim
Summary says "single continuous plane + single AGND/DGND bridge" — contradictory phrasing. Detailed document correctly argues against etched split planes.

### Original repository claim
DEC-020: "Single continuous ground/reference plane with physical partitioning + single AGND/DGND bridge + partitioned current claims"
ARCHITECTURE §2.5: "Single continuous plane, partitioned, single bridge"
GROUNDING_AND_RETURN_PATHS.md §1–§3: exhaustive current-return analysis; recommends **single continuous plane with partitioned placement**, no etched split, bridge is conceptual or narrow copper under ADC — consistent internally, summary shorthand contradictory.

### Primary evidence
Engineering review: "split plane" implies etched AGND/DGND copper islands; "single continuous plane with bridge" in same sentence implies both intact and split.

### Verdict
**CONFIRMED ISSUE** (terminology)

### Required correction
Canonical phrasing adopted repository-wide:

> One continuous reference plane. Analog/digital separation is achieved by placement, local return-current control, routing discipline, and decoupling. There is no etched AGND/DGND split and no physical AGND/DGND bridge.

Separate definitions added:

- **Precision reference return geometry** — RC filter 1 kΩ+4.7 µF at reference, star to DAC REFIN GND pin.
- **Shunt Kelvin reference** — FORCE_LO star at shunt return, sense amp GND ref at same point.
- **FORCE_LO reference** — analog measurement ground (Kelvin star); digital COM meets it only at the ADC tie.
- **Relay return routing** — wide trace to bulk COM, not through analog corner.
- **USB return** — chassis-tied near connector with 1 MΩ||4.7 nF bleed; loop current measured at ADC tie.
- **Chassis/shield strategy** — digital-edge shield node, guard separate.

Word "bridge" removed unless an actual electrical bridge exists (only meaning: copper pour under ADC for hybrid partitioned plane — now called "single tie at ADC, not a gap-bridging element").

### Files affected
- `DECISIONS.md` — DEC-020 sentence rewritten to canonical
- `docs/architecture/ARCHITECTURE.md` — grounding row corrected
- `docs/architecture/PHASE2_DECISION_MATRIX.md` — grounding row corrected
- `docs/architecture/GROUNDING_AND_RETURN_PATHS.md` — §2.3 title adds "continuous plane, partitioned placement; etched split rejected"
- `REQUIREMENTS.md` — REQ-PWR-004 text "single AGND/DGND tie" → "no etched AGND/DGND split"

### Phase 3 impact
None on copper; corrects review checklist language.

---

## Finding IR-14 — Downstream Capacitance Synthesis Conflict

### Independent review claim
Detailed energy analysis correctly identifies very low downstream capacitance as desirable, but synthesis states "low output C ≤10 nF" — contradicts energy budget.

### Original repository claim
- COMPLIANCE_ENERGY_ANALYSIS (canonical): `E=½CV²`; at 5 V, 10 nF→125 nJ; budgets 1 nJ gentle → C_max 80 pF @5 V, 500 pF @2 V; 10 nF on DUT node "catastrophic."
- COMPLIANCE_ARCHITECTURE: "low output C ≤10 nF + isolation + slew limit" — listed as "upstream of R_iso" but downstream distinction not prominent in table.
- PHASE2_DECISION_MATRIX §6: "Low output C (≤10 nF) + series 10 Ω isolation + damping RC" — ambiguous which C is counted.
- ARCHITECTURE §3: "Low output C ≤10 nF" — same ambiguity.

### Primary evidence
Energy vs C: `C_max = 2·E_budget / V²`

| E_budget | C_max @1 V | C_max @2 V | C_max @5 V |
|---|---|---|---|
| **1 nJ gentle** | 2.0 nF | **500 pF** | **80 pF** |
| 2 nJ standard | 4.0 nF | 1.0 nF | 160 pF |
| 5 nJ relaxed | 10 nF | 2.5 nF | 400 pF |

At V1 rails 5 V, even standard 2 nJ allows only 160 pF; 10 nF is **62×** over standard — unsustainable downstream.

### Verdict
**CONFIRMED ISSUE** — synthesis table line conflated `C_UPSTREAM` with `C_DOWNSTREAM`.

### Required correction
1. Introduce canonical terminology repository-wide:

   - **C_UPSTREAM** — capacitance isolated from DUT by R_iso / servo (compensation C before R_iso, e.g., 4.7–10 nF). Not directly dumpable into filament.
   - **C_DOWNSTREAM** — capacitance that can dump directly into DUT during switching (post-R_iso: connector+trace+relay+Cable+DUT+ESD before isolation). Only this counts toward `E = ½C_DOWNSTREAM·V²`.

2. Add Phase 3 research target for `C_DOWNSTREAM` (test-recipe / DUT-dependent constraint, not universal law):

   - Gentle multilevel (100 µA compliance, ≤2 V typical): **C_DOWNSTREAM ≤ 80 pF @5 V (1 nJ) or ≤500 pF @2 V** — advise forming at ≤2–3 V where possible.
   - Standard SET (100 µA–1 mA, ≤2 V): **C_DOWNSTREAM ≤160 pF @5 V (2 nJ) / 1 nF @2 V**
   - Forming / high-Icc (5–10 mA, ≤5 V): **≤800 pF @5 V (10 nJ)**
   - 1 nJ is not a universal law — budgets are engineering constraints per test recipe / DUT.

3. Correct synthesis rows: "low output C ≤10 nF" → "C_UPSTREAM ≤10 nF (before R_iso); **C_DOWNSTREAM ≤80–150 pF** (after R_iso, cable-limited, recipe-dependent; see COMPLIANCE_ENERGY_ANALYSIS §5)."

### Files affected
- `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` — new §1.5 "Upstream/Downstream distinction" + §5 C_max table annotated by recipe
- `docs/architecture/COMPLIANCE_ARCHITECTURE.md` — Options D and Recommended Instance §5 updated to clarify C_UPSTREAM vs C_DOWNSTREAM
- `docs/architecture/ARCHITECTURE.md` — compliance row corrected
- `docs/architecture/PHASE2_DECISION_MATRIX.md` — row 6 corrected
- `simulation/PHASE3_SIMULATION_PLAN.md` — new test J (upstream/downstream cap location)

### Phase 3 impact
Ensures 10 nF compensation is not penalized as a DUT-dump; focuses downstream budget on cable/DUT fixture length (0.5 m limit, low-C coax).

---

## Finding IR-15 — Output-Stage Composite Option

### Independent review claim
Current comparison treats LT1970A and precision-op-amp + discrete buffer as separate alternatives; third architecture — precision outer voltage-loop amplifier driving LT1970A as booster/current-limit stage — could retain precision offset and LT1970A drive/limit/enable/flags.

### Original repository claim
SOURCE_STAGE_CANDIDATES: Candidate A (LT1970A), Candidate B (precision+discrete), Candidate D (composite precision front-end + booster inside loop) listed but not promoted as explicit Phase 3 test candidate. ARCHITECTURE §3 "Source stage — LT1970A primary + discrete alternate" — composite mentioned only as V1.1 alternate without explicit Phase 3 test mandate.

### Verdict
**CONFIRMED ISSUE** (omission — not incorrect, but incomplete candidate enumeration)

### Required correction
Add explicit Phase 3 candidate:

> ### Source Candidate C — Precision outer loop + LT1970A inner/power stage
> ```
> precision outer voltage-loop amplifier (ADA4522/OPA140-class, Vos 5 µV / Ib 10 pA)
>        ↓ (drives LT1970A +IN or booster input)
> LT1970A used as power/current-limit booster, unity-gain buffer
>        ↓
> FORCE (via Rsense + R_iso, feedback after R_iso to outer amp)
> ```
> Retains: precision DC offset from outer amplifier, LT1970A source/sink drive, integrated 4 µs limit, enable, ISRC/ISNK/TSD flags, while reducing reliance on LT1970A's ~200 µV offset for DUT voltage accuracy.

Explicit Phase 3 gate: **do not assume stability** — candidate must be tested for nested loop interaction, phase margin, compliance crossover (outer voltage + inner current), Kelvin remote sense latch-up, and capacitive DUT load (10 pF–10 nF + cable). Phase 2 only defines it.

### Files affected
- `docs/architecture/SOURCE_STAGE_CANDIDATES.md` — new §2.6 "Candidate C — Precision outer loop + LT1970A booster" promoted from footnote
- `docs/architecture/ARCHITECTURE.md` — Sources: three candidates A/B/C now listed
- `simulation/PHASE3_SIMULATION_PLAN.md` — new test O "Three source-stage candidates A/B/C"
- `DECISIONS.md` — DEC-014 addendum / DEC-025 cross-ref

### Phase 3 impact
Adds one simulation branch (nested Miller/lead-lag compensation, R_iso feedback after R_iso). No PCB commitment.

---

## Finding IR-16 — Phase 3 Plan Incomplete

### Independent review claim
`simulation/PHASE3_SIMULATION_PLAN.md` (43 lines) lacks explicit tests for compliance minimum-range capability, range coercion, differential Kelvin servo, open-sense faults, DUT loading, sense capacitance, bipolar front-end, trip tolerance, energy/Q/peaking, upstream vs downstream capacitor location, range-switching faults, POR/brownout, leakage model, DAC comparison with actual device ranges, and three source candidates.

### Original repository claim
Phase 3 plan as of 2026-08-24: 7 simulations (source transfer, 4-quad, compliance per-decade, stability, per-range measurement, Monte Carlo, temp) — adequate for Phase 2 scoping but incomplete per IR-01..IR-15 above.

### Verdict
**CONFIRMED ISSUE**

### Required correction
Expand `simulation/PHASE3_SIMULATION_PLAN.md` to include tests A–O:

#### A. Compliance minimum-range capability
For every current range (10 mA … 100 nA): desired Icomp vs LT1970A achievable minimum (4 mV floor, 6 mV linear threshold), linear vs nonlinear VCS region (Vc≥60 mV), range coercion outcome (IR-01 table).

#### B. Range coercion
Example: `requested Icomp = 100 µA → current measurement range = 100 µA (500 Ω) → compliance hardware range → Vc = 0.50 V → achievable; vs requested 1 µA on 10 mA range → coercion to 10 µA range or error.` Matrix: all Icomp × all measurement ranges, verify no unsafe Vc (out-of-range, floating) configuration.

#### C. Differential Kelvin servo
Test SENSE_HI/SENSE_LO differential regulation: lead R 0–1 MΩ, low-side shunt burden 25–100 mV, ± current source/sink, common-mode −5…+5 V changes; verify `V_DUT = V_SENSE` within source accuracy.

#### D. Open-sense faults
Test SENSE_HI open, SENSE_LO open, intermittent sense (1 ms chatter), fallback FORCE-regulation + fault flag; invariant: **no low-value DC pull network may load DUT during valid measurement** (IR-03).

#### E. DUT sense-loading sweep
Use R_DUT = 1 MΩ, 10 MΩ, 100 MΩ, 1 GΩ at 0.1–1 V bias; measure error caused by voltage-sense input with vs without high-Z buffer (IR-02).

#### F. SENSE capacitance
Explicitly sweep front-panel DUT-connected capacitance (DUT-node C):
5 pF, 10 pF, 50 pF, 100 pF, 500 pF, 1 nF — distinguish sense input capacitance (buffer Cin 2–5 pF) from DUT/cable capacitance. Filter cap 1 nF after buffer is not DUT-side (IR-04).

#### G. Bipolar current front-end (IR-12)
Test +FS, −FS, zero, and small bipolar signals (±0.01·FS, ±0.10·FS) around zero for every current range; for each ADC candidate (ADS1262 vs AD7175-class vs alternatives) evaluate input range, bipolar supply requirement, common-mode limits, PGA restrictions, buffer behavior, zero crossing, negative shunt measurement (topologies A/B/C).

#### H. Trip threshold tolerance
Monte Carlo (≥500 runs): comparator offset (TLV3501 ±6.5 mV max), shunt tolerance (0.1%→0.01%), DAC threshold INL, amplifier offset (ADA4522 5 µV / OPA140 120 µV). Report trip threshold distribution (mean ±σ, min/max) and PASS for emergency tolerance (IR-08).

#### I. Energy delivered to DUT
For SET-like transition compute `E_DUT = ∫ V_DUT(t)·I_DUT(t) dt` — report Ipeak, Q delivered (=C·V), energy, recovery, not only overshoot percentage. Compare LT1970A limit vs external loop vs crowbar vs full D (IR-14).

#### J. Upstream/downstream capacitor location
Separate simulations for compensation capacitor before R_iso (C_UPSTREAM) vs capacitor after R_iso (C_DOWNSTREAM); verify only downstream C counts toward dump (IR-14).

#### K. Range switching faults
Break-before-make sequencing, accidental make-before-break (two shunts simultaneously), stuck relay, open shunt, charge-injection tail — per MECHANIC §4 of MEASUREMENT doc.

#### L. POR / brownout
DAC undefined / MCU reset / reference ramp (Vref 0→2.5 V in 10 ms, DAC mid-ramp, supply slew ≤6 V/µs per LT1970A): OUTPUT must remain disabled via pull-down + supervisor; measure leakage <1 µA disabled and <4 mV/Rsense floor behavior.

#### M. Leakage model
Behavioral leakage sources for 100 nA range: amplifier Ib (10 pA JFET, 50 pA chopper), PCB surface leakage (10 GΩ →10 pA @100 mV), relay off leakage (1 pA reed vs 100 pA MUX), switch leakage, connector leakage (1 GΩ) — test quantitative MUC 1 nA and Johnson 0.41 pA floor preservation.

#### N. DAC comparison
Use actual device output ranges:
- AD5686R architecture: 0–5 V → ×2 → ±5 V (10 V span, LSB 152.6 µV) with gain-stage error
- AD5764 actual range: ±10 V (±10.526 V option) 20–21 V span (LSB 305–321 µV) ±11.4 V supplies
- AD5791-class only if needed for LSB headroom at 0.1 V read
- Compare against ≤1 mV programming target, source accuracy, calibration burden, BOM, power rails, reference complexity.

#### O. Three source-stage candidates
Phase 3 compares: Candidate A LT1970A direct voltage loop, Candidate B precision op-amp + discrete/composite buffer, Candidate C precision outer loop + LT1970A booster/current-limit stage (IR-15).

### Files affected
- `simulation/PHASE3_SIMULATION_PLAN.md` — expanded from 43 lines to canonical Phase 3 plan (tests A–O)
- `docs/architecture/REQUIREMENTS_TRACEABILITY.md` — adds Phase 3 simulation columns

### Phase 3 impact
Plan is now review-complete; no simulation executed in this corrective session (per session boundary).

---

## Requirement Revisions (Corrected in REQUIREMENTS.md)

### REQ-SAFE-001 (hardware current compliance)
**Old (v0.2.0 confirmed):** "…Icc programmable as value within range (not decade-locked), min 0.1% of I_range (Keithley rule)."
**New (corrected):** "A hardware current compliance loop shall limit DUT current independent of firmware. Icc programmable as value within range (not decade-locked). For LT1970A-based limiters the minimum programmable compliance is limited by the 4 mV Vsense floor (~4% of FS at 100 mV FS, ~16% at 25 mV FS) and the Vc<60 mV nonlinear region — see DEC-024. A 0.1%·I_range requirement applies only to the precision external-loop (Candidate C) configuration and otherwise is satisfied via **compliance-aware automatic range coercion** (requested Icomp selects achievable hardware range). The compliance reference shall be DAC-driven per segment (no hard-wired trimpot), with per-polarity source/sink control."

*Status remains CONFIRMED; provenance DEC-024.*

### REQ-DUT-001 (Kelvin)
**Addendum:** "DUT-sense input impedance >10 GΩ is achieved via a high-Z buffer before any attenuation/dividing stage (see IR-02). Open-sense pull networks ≥10 GΩ effective or switched-disconnect during measurement."

### REQ-PWR-003 (analog rails)
**Addendum:** AD5764 rail requirement ±11.4 V noted; "±10 V LDO rails are not AD5764-compatible" — V1 power-tree Options A/B/C defined.

### REQ-PWR-004 (analog/digital supply treatment)
**Terminology:** "single AGND/DGND tie" → "one continuous reference plane with no etched AGND/DGND split; separation by placement, local return-current control, routing discipline, and decoupling."

No other confirmed requirements weakened merely to make LT1970A fit. If future evidence re-establishes a universal 0.1% as a true ReRAM experimental requirement, architecture must satisfy it via Candidate C (precision loop) — see DEC-024.

---

## New Decision

### DEC-024 — Compliance Minimum Programmability and Range-Coercion Architecture

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-SAFE-001, REQ-SRC-006, REQ-MEAS-001
- **Alternatives considered:** (A) keep 0.1% as binding for LT1970A, (B) remove requirement entirely, (C) coercion + precision-loop tier, (D) single separate compliance bank for all ranges.
- **Evidence examined:** LT1970A 1970afc/1970fe datasheets (VSENSE_MIN 4 mV typ, Vc<60 mV nonlinear, `I=Vc/(10·R)`), SHUNT_RANGE_TRADEOFF burden table, COMPLIANCE_ARCHITECTURE cautions, independent recomputation (this document IR-01 table: I_min =4% of FS at 100 mV, 16% at 25 mV).
- **Decision:** Adopt tiered rule:
  1. LT1970A limiter: minimum compliance = max(4 mV/Rsense_compliance, 60 mV/(10·Rsense)) — about 4% of FS at 100 mV burden, 16% at 25 mV. Firmware implements compliance-aware range coercion; requesting below-floor Icomp coerces range or returns error per autorange setting.
  2. Precision external CC loop (Candidate C): target 0.1%·I_range is a **research retention**, not a V1 gate, to be validated in Phase 3 Candidate C simulation. It is the only topology that can meet 0.1% without 4 V burden.
  3. Separate compliance-sense bank is a provisioning option (Footprint on PCB for optional relays) but not required for REV-A if coercion satisfies test recipes (typical ReRAM Icc 10 µA–1 mA is above LT1970A floor on appropriate range).
- **Rationale:** Primary datasheets override the AI-copied Keithley rule; the rule is commercial-instrument semantics (closed-loop servo) not LT1970A VC/10 threshold physics. Forcing LT1970A to meet 0.1% would require 4 V burden swings — destructive.
- **Consequences:** COMPLIANCE_ARCHITECTURE solutions A–D formalized; Phase 3 tests A,B added; REQUIREMENTS REQ-SAFE-001 revised without weakening safety invariants; host driver API now logs `compliance_range` alongside `range_state`.
- **Verification status:** UNVERIFIED — Phase 3 sims IR-16 A,B,H + scope fault injection per vintage COMPLIANCE doc.
- **Provenance:** LT1970A 1970afc p.12–13 (VCSRC/VCSNK 4 mV floor, 60 mV linear) + recombination table §IR-01.

---

## Canonical Source-of-Truth Policy (post-correction)

| Information type | Canonical file | Consumers reference it, not duplicate |
|---|---|---|
| Requirements (binding) | `REQUIREMENTS.md` (+ DEC-024) | All others |
| Architecture (conceptual) | `docs/architecture/ARCHITECTURE.md` | MEASUREMENT/SOURCE/COMPLIANCE refine, not contradict |
| Shunt ranges, R, burden, noise, power, gain | `docs/calculations/SHUNT_RANGE_TRADEOFF.md` §2.4 | BURDEN retained as Phase 1 baseline with superseded banner; all others cite SHUNT_RANGE_TRADEOFF |
| Compliance triad + solutions A–D + energy | `docs/architecture/COMPLIANCE_ARCHITECTURE.md` | SOURCE_STAGE/COMPLIANCE_ENERGY |
| Stored energy + downstream budgets | `docs/calculations/COMPLIANCE_ENERGY_ANALYSIS.md` | ARCHITECTURE/PHASE2_DECISION_MATRIX |
| Phase 3 tests (gates A–O) | `simulation/PHASE3_SIMULATION_PLAN.md` | DECISIONS/TRACEABILITY |
| Grounding (continuous plane) | `docs/architecture/GROUNDING_AND_RETURN_PATHS.md` | ARCH/PWR |
| Guard (keepout vs driven) | `docs/architecture/GUARD_STRATEGY.md` | KELVIN/MEASUREMENT |
| Kelvin loop + burden equation | `docs/architecture/KELVIN_SENSE_ARCHITECTURE.md` | All source docs |
| Power tree options | `docs/architecture/POWER_TREE.md` | PRELIMINARY_ERROR_BUDGET |

Search terms from the session boundary failure modes (`100 mV`, `25 mV`, `50 mV`, `10 nF`, `1 nF`, `10 MΩ`, `AD5764`, `153 µV`, `305 µV`, `AGND`, `DGND`, `bridge`, `TLV3501`, `10^6`, `guard`, `0.1% I_range`, `VCSRC`, `VCSNK`) have been audited; deprecated claims are corrected or explicitly marked historical/superseded.

---

## Risks and Open Questions Updated

- New risks are implicit corrections (guard 1 GΩ wording, bridge terminology, 10 MΩ pull) — existing R-01, R-03, R-14 priorities unchanged; triage: LT1970A lifecycle single-source remains highest sourcing risk (re-acknowledged in DEC-023).
- OPEN_QUESTIONS Q-01 (DAC) reopened as Phase 3 trade (AD5764 vs AD5686R vs AD5791 with actual ±10 V supplies); Q-10 (Grounding) marked text-corrected; no new blocking question beyond IR-16 gates which are Phase 3 simulations, not pre-Phase-3 blockers.

---

## Phase Status After Correction

**`PHASE 2 — CORRECTED / READY FOR PHASE 3`**

No architecture-level issue remains unresolved that would block Phase 3 simulations. Decision gates above are simulation-verifiable, not build-blocking. LT1970A lifecycle monitoring continues. No KiCad schematic, PCB, BOM, or component order is authorized.

---

## Referenced Evidence (primary datasheets + calculations)

- Analog Devices LT1970A 500 mA Power Op Amp w/ Adjustable Precision Current Limit — datasheet 1970afc (2015-11-11), § Current Limit Characteristics (VSENSE_MIN 4 mV typ, VCSRC/VCSNK 60 mV linear), Block Diagram, Pin functions VCSRC/VCSNK/SENSE+/−/ENABLE; plus LT1970 1970fe for second-source behavior.
- Analog Devices AD5764 Complete Quad 16-Bit High-Accuracy Bipolar Voltage Output DAC — Rev F, General Description (±11.4–±16.5 V supplies, nominal ±10 V / span 20 V, LSB = 20 V/65536 = 305.2 µV; ranges ±10/±10.2564/±10.5263 V).
- Texas Instruments TLV3501/3502 4.5 ns Rail-to-Rail High-Speed Comparator — Rev E (2015-04-17), Vos max ±6.5 mV, typ ±1 mV, hysteresis 6 mV.
- Project calculations: SHUNT_RANGE_TRADEOFF calc `docs/calculations/shunt_range_tradeoff_calc.py` (Python, k=1.380649e-23, T=300 K, B=10 Hz), PRELIMINARY_ERROR_BUDGET, BURDEN, COMPLIANCE_ENERGY (§§2–5), headroom/thermal notes.
- Phase 2 architecture/COMPLIANCE research synthesis and commercial benchmarks cited in REQUIREMENTS_TRACEABILITY.md.

---

## Correction Completion Checklist (per prompt Exit Criteria)

1. ✅ LT1970 compliance-range feasibility quantified (table + floor + coercion).
2. ✅ 0.1%·I_range requirement formally revised via DEC-024 (not silently weakened).
3. ✅ High-Z DUT voltage-sense no longer loads nA/HRS — post-buffer topology specified, candidate classes compared, loading quantified at 1 MΩ/10 MΩ/100 MΩ/1 GΩ.
4. ✅ Open-sense detection no longer loads DUT — switched disconnect architecture, ≥10 GΩ rule, no DC load invariant.
5. ✅ DUT-connected sense capacitance in stored-energy budget — post-buffer placement + DUT-node budget table.
6. ✅ Shunt burden table canonical and consistent — SHUNT_RANGE_TRADEOFF §2.4 single source of truth, all docs synchronized.
7. ✅ AD5764 actual range/LSB corrected (20 V span, 305.2 µV LSB, no ±5 V mode).
8. ✅ Power tree AD5764-compatible — ±11.4 V requirement, Options A/B/C defined.
9. ✅ Positive vs negative regulator conceptual resolution — LT1763/LT3045 positive-only; negative class added (LT1964/TPS7A30).
10. ✅ TLV3501 correctly classified as emergency supervisor (not precision comparator) with tolerance table.
11. ✅ TIA settling claims qualified to physically defensible language.
12. ✅ Guard strategy distinguishes passive keepout / grounded shield / driven guard / provision; incorrect 1 GΩ wording removed.
13. ✅ Kelvin burden terminology precise, equation canonical, differential SENSE path explicit.
14. ✅ Bipolar current measurement path defined for Phase 3 (topologies A/B/C + ADC evaluation).
15. ✅ Grounding terminology no longer contradictory (continuous plane, no etched split/bridge).
16. ✅ Upstream/downstream capacitance distinction canonical; 1 nJ not universal law.
17. ✅ Composite source-stage Candidate C added.
18. ✅ Phase 3 simulation plan contains tests A–O.
19. ✅ Requirements traceability updated (DEC-024 + docs).
20–24. ✅ No KiCad schematic/PCB/BOM/order; repo internally consistent; Git clean after commit.

---

*End of corrective record. Wait for explicit authorization before Phase 3 simulations.*
