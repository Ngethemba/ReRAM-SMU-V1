# Kelvin Sense Architecture — Force / Sense Loop, Burden Placement, Open-Sense

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**Status:** CANDIDATE ARCHITECTURE — no selection; promotes via DECISIONS.md  
**Requirements:** REQ-DUT-001 (4-wire Kelvin), REQ-SRC-001/002 (±5 V / ±2 V), REQ-MEAS-001/002, REQ-SAFE-001/003/004 (safe state), REQ-MEAS-003 (V accuracy)  
**Companion:** `docs/architecture/MEASUREMENT_FRONTEND_CANDIDATES.md`, `docs/calculations/SHUNT_RANGE_TRADEOFF.md`, `docs/research/SMU_ARCHITECTURE_SURVEY.md`
**Revision:** Corrected per IR-02/03/04/11: high-Z buffer first, no passive divider at DUT, switched open-sense, filter after buffer, V_FORCE equation canonical.
<!-- corrected per IR-02/03/04/11: high-Z buffer first, no passive divider at DUT, switched open-sense, filter after buffer, V_FORCE equation canonical -->

> **One-line rule:** Source **regulates SENSE**, not FORCE. Burden (shunt `I·R`) sits **outside** the Kelvin loop — SENSE encloses **DUT only**. Kelvin corrects lead `I·R_lead`, it does **not** eliminate burden; headroom `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD (V_FORCE=V_DUT+V_SHUNT+I*R_LEAD)` must be budgeted. (CAUTION 2: 100 mV = 5% of ±2 V.)

> **Canonical equation (IR-11):** Kelvin sensing does not physically eliminate shunt burden. It prevents the burden from becoming DUT-voltage error by forcing the source to provide additional headroom: `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD (V_FORCE=V_DUT+V_SHUNT+I*R_LEAD)` for the relevant polarity/topology.

---

## 1. Kelvin loop definition

```
                    ┌─ SENSE_HI → [high-Z buffer ≥10GΩ, ≤10pA] ─┐
                    │                                              │
Ref → DAC → error amp → power stage (LT1970A ±12 V) → FORCE_HI ── lead R_HI ── DUT_HI──DUT──DUT_LO ── lead R_LO ── FORCE_LO
                    │         │              │                          │                     │
                    │      [SHUNT]  (low-side, outside loop)           └─ SENSE_LO → [high-Z buffer ≥10GΩ, ≤10pA] ─┘
                    │         │              │                                              │
                    └──── compliance / limit ┘         star ground (single point at FORCE_LO / shunt return)

Shunt: low-side between DUT_LO and FORCE_LO, **outside** SENSE_HI/LO.
SENSE pair: each line first sees high-Z buffer (≥10 GΩ, ≤10 pA Ib) → differential attenuator → ADC/error amp.
FORCE loop drives V_SENSE → V_set; extra headroom covers V_burden + lead drop per V_FORCE equation.
Filter (RC) is AFTER buffer, not at DUT — DUT sees only buffer Cin (IR-04).
```

### 1.1 Does source regulate FORCE or SENSE?

* **FORCE is the power output** (low-Z, drives current, handles sink, compliance).
* **SENSE is the regulation feedback.** Outer voltage loop: `error = V_set − V_SENSE`; power stage forces `V_SENSE = V_set` regardless of `I·R_lead` and `V_burden` inside the force path.
* Inner loop (current compliance, REQ-SAFE-001) acts on `I_shunt` and overrides the voltage loop when `I → Icc` — it remains a hardware clamp independent of firmware.
* When Kelvin is **disabled** (2-wire mode, short leads, or open-sense fallback) the loop reverts to `V_FORCE = V_set` (internal divider).
* **Canonical headroom:** `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD (V_FORCE=V_DUT+V_SHUNT+I*R_LEAD)` — burden is headroom cost, not DUT error when Kelvin is active (IR-11).

### 1.2 Where is burden relative to SENSE? (critical)

| Option | Sense points | What Kelvin corrects | Consequence |
|---|---|---|---|
| **A — SENSE encloses DUT only (RECOMMENDED)** | SENSE_HI at DUT_HI, SENSE_LO at DUT_LO; shunt **outside** | Lead `I·R_lead` only | `V_DUT` is accurate; `V_burden` is **not** corrected — appears as headroom cost on FORCE: `V_FORCE = V_DUT + V_burden + I·R_lead`. Output stage must have rail margin for worst `V_burden` (25–100 mV range-dep). Clean separation of V and I measurement. |
| B — SENSE encloses DUT+shunt | SENSE_LO at FORCE_LO (across shunt+DUT) | Lead + burden | Kelvin would "correct" burden — but `V_SENSE` then mixes DUT voltage with `I·R_shunt`; I and V measurements become coupled; not recommended. |
| C — SENSE encloses FORCE terminals | No Kelvin | Nothing | Lead and burden both appear as DUT error (up to 10% @ LRS reads — see SHUNT doc §3). Only for 2-wire fallback. |

**V1 choice is A.** Rationale: burden is a *measurement* voltage, not a lead error — correcting it in the force loop would hide it and corrupt the I·V dataset (compliance flag vs range compliance distinction in REQ-SAFE-001 also assumes separate V and I paths).

**LT1970A note (IR-11):** LT1970A's internal SENSE+/− is the **compliance sense across Rsense**, distinct from SMU Kelvin SENSE_HI/LO. Remote sense requires **external** differential feedback driving the source — not an inherent LT1970A four-terminal servo.

---

## 2. Lead resistance limits + DUT-node capacitance budget

Kelvin corrects lead drop, but correction has limits: finite loop gain, bandwidth, and headroom.

* **Headroom limit:** `V_FORCE = V_DUT + I·R_lead + V_burden ≤ V_rail − margin`. With ±12 V rails and ±5 V DUT, `R_lead,max ≈ (7 V − V_burden − V_DUT)/I`. For worst `I=10 mA, V_DUT=5 V, V_burden=25 mV` → `R_lead,max ≈ 197 Ω` — generous. Practical limit is contact/cable (banana ≈ 10–30 mΩ, Kelvin clip ≈ 50 mΩ) — Kelvin easily handles it.
* **Loop-gain error:** Residual error `≈ (I·R_lead)/A_OL`. With `A_OL≈100 dB` (10^5), 100 mV lead drop → 1 µV residual — negligible vs 0.5 mV V accuracy.
* **Bandwidth / stability:** Kelvin sense lines are high-Z and pick up noise; RC filter is **after high-Z buffer** (IR-04): `DUT → high-Z buffer → RC/filter → ADC`. Filter cap 100 Ω + 1 nF is post-buffer, 0 pF at DUT. Sense trace length matched, twisted or shielded.
* **Practical bound:** keep `R_lead ≤ 1 Ω` per lead (4-wire cable ≤0.5 m, 20 AWG). Above ~10 Ω, sense input bias current × R_lead creates offset; use electrometer-grade sense buffer.

### 2.1 DUT-node capacitance budget (IR-04)

Only capacitance directly connected to DUT **before isolation/buffer** counts toward `E = ½C_DOWNSTREAM·V²`. Filter after buffer contributes **0 pF** at DUT.

| Contributor | Typical V1 | Location vs isolation | Counts to C_DOWNSTREAM? |
|---|---|---|---|
| Connector (banana/BNC + Kelvin clip) | 5–10 pF | DUT-side | Yes |
| PCB trace (FORCE+SENSE, 1 cm each) | 1–3 pF | DUT-side | Yes |
| Relay/switch off-capacitance (Coto 9007) | 1–3 pF | DUT-side (when open) | Yes |
| Sense input (buffer input C) | 2–5 pF | DUT-side | Yes |
| ESD/protection diode (low-leakage) | 0.5–2 pF | DUT-side (if present) | Yes |
| Cable (if used, 0.5 m low-C) | 25–50 pF | DUT-side — length-limited | Yes |
| DUT package + pad | 0.5–5 pF | DUT | Yes |
| Optional diff filter cap | **0 pF at DUT** — placed **after buffer** (0 pF DUT-side) | Upstream of buffer | **No** |
| **Total C_DOWNSTREAM target** | **≤80–150 pF** (IR-14 recipe-dependent) | — | — |

Target per IR-14: ≤80 pF @5 V (1 nJ gentle), ≤500 pF @2 V; see COMPLIANCE_ENERGY_ANALYSIS §5.

---

## 3. Open-sense detection, fallback, safety

Open SENSE (unplugged clip, broken wire) would drive FORCE to the rail trying to servo an open loop — unsafe for DUT and output stage. Must detect and fall back to FORCE regulation automatically, hardware-first.

### 3.1 Detection (hardware, µs) — corrected per IR-03

**Rule:** No low-value DC pull network shall remain connected across SENSE_HI/SENSE_LO during a valid DUT measurement. ≥10GΩ or disconnected invariant.

**Primary (A+E): switched continuity before OUTPUT ON + analog switch disconnect during measurement (switched continuity before OUTPUT ON):**

- **Firmware sequence:** With output disabled, close analog switch (e.g., ADG1419-class, 10 pA leakage) connecting weak pull network → window comparator detects open vs closed → log `sense_continuity` → **open the switch** before enabling output. During valid measurement the pull network is **galvanically disconnected** by the switch/relay.
- **Permanent pull, if any:** Must be **≥10 GΩ** effective and characterized at 40 °C/humidity. 10 MΩ is retained only as a **switched test resistor behind the disconnect**, never as a permanent rail.
- **No 10 MΩ permanent pull:** The prior "SENSE_HI weak pull to V_FORCE/2 via 10 MΩ + SENSE_LO weak pull to ground via 10 MΩ (high-Z so normal operation unaffected)" is **corrected** — 10 MΩ at 1 V = 100 nA, dominating HRS current; it is not high-Z at nA scaling.
- Window comparator on `|V_SENSE − V_FORCE|` still flags open during test phase (>1 V or >V_FORCE+0.5 V for >10 µs).

*Alternative equivalent:* Very-high-value switched network (1–10 GΩ) with series switch, test-current injection only while output disabled, or FORCE-SENSE tracking monitor without DC loading — all logically equivalent to "no DC load during measurement."

### 3.2 Fallback (hardware, no firmware dependency)

1. **Flag → analog switch** shorts SENSE feedback to FORCE divider (internal `V_FORCE` sense) — loop now regulates `V_FORCE = V_set`.
2. **Firmware notified** via fault pin + SCPI `SENS:REM OFF` sticky flag; front-panel LED / log.
3. **Accuracy degraded** to 2-wire (lead error returns) but safe — no rail drive.
4. **Re-arm:** fallback clears only on explicit `SENS:REM ON` or output disable/enable cycle — prevents chatter on intermittent contact.

### 3.3 Safe state

* Power-on default = output disabled, Kelvin loop disabled (FORCE regulation), compliance at minimum I-range (REQ-SAFE-003).
* Any watchdog / brown-out / over-temp → output disabled; Kelvin flag latched; re-enable requires host command.

---

## 4. Interaction with burden, compliance, guarding

* **Burden headroom is not Kelvin-corrected** — budget it in power/rail design (POWER_TREE.md). Range-dep burden (SHUNT doc D) reduces worst headroom from 100 → 25 mV on 10 mA. Canonical: `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD (V_FORCE=V_DUT+V_SHUNT+I*R_LEAD)`.
* **Compliance (HW current limit)** senses `I_shunt` **outside** Kelvin — it limits current regardless of Kelvin state. Kelvin open does not defeat compliance.
* **Guarding:** 100 nA range guard ring driven to `SENSE_LO` (or to virtual ground for TIA) — not to FORCE. Keep SENSE pair guarded, shunt node guarded on low-I range.

---

## 5. Wiring & connector provision

* 4 banana + Kelvin clip or 4-wire terminal block; FORCE uses 4 mm banana (high current), SENSE uses high-Z guarded contacts (low leakage).
* Provision guard pin (triax-ready, DNP) per REQ-DUT-003 / Q-11 — copper guard ring on PCB, not yet triax.
* Cable: FORCE 18–20 AWG, SENSE twisted/shielded 26 AWG, shield to guard.

---

*Traceability: REQ-DUT-001, REQ-SRC-001/002, REQ-MEAS-003, REQ-SAFE-001/003, DEC-012 (guard provision), Q-05/Q-11, SHUNT_RANGE_TRADEOFF (headroom), MEASUREMENT_FRONTEND_CANDIDATES (placement). Corrected per IR-02/03/04/11.*
