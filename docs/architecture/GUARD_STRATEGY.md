# Guard Strategy — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**Status:** Provisioned for 100 nA guard — not driven guard triax (V2). Complements `LOW_CURRENT_MEASUREMENT.md` §4 and `GROUNDING_AND_RETURN_PATHS.md`.
**Revision:** Corrected per IR-10 — taxonomy clarified, powered-from-SENSE_HI phrasing corrected.

---

## 1. What guard provision means for V1 (100 nA, ~1 nA MUC)

V1 does NOT claim electrometer-class guard (driven triax at 10⁻¹⁴ Ω). V1 provision means controlled keepout + optional footprint, no driven guard stuffed in REV-A.

### 1.1 Taxonomy (IR-10 canonical)

Four distinct concepts — do not conflate:

| Concept | What it is | Leakage mechanism | V1 REV-A |
|---|---|---|---|
| **Passive keepout / clean high-Z zone** | Exposed copper keepout, no-mask, 0.5 mm gap, no supply | Surface leakage shunted to floating copper; no active drive | **YES — implemented** |
| **Grounded shield** | Chassis/guard tied to FORCE_LO via 1 MΩ \|\| 10 nF bleed + ESD path | Drains charge, breaks ground loop, not nulling V_sense−V_guard | **YES — via 1 MΩ\|\|10 nF** |
| **Driven guard** | Low-leakage follower (e.g., OPA140-class) whose **output** drives guard ring/plane, **powered from normal rails** | Nulls V_sense−V_guard → I_leak=(V_sense−V_guard)/R_surface → ~0 | **Footprint only, NOT stuffed** |
| **Guard copper provision** | Top ring + inner guard plane stitched every 5 mm, kept isolated from GND plane (≥0.5 mm) | Provides low-impedance guard node when driven; otherwise passive keepout | **YES — ring + plane provision** |

### 1.2 V1 REV-A decision

- **No driven guard stuffed**
- **No arbitrary ground guard around SENSE_HI** — a ground-tied guard around SENSE_HI tied to wrong node injects leakage; only keepout or correctly-driven guard.
- **Controlled keepout + optional driven-guard footprint** — guard ring encircling high-Z nodes (shunt sense lines, 100 nA TIA feedback node if provisioned, DUT SENSE_HI/LO terminals), stitched guard plane on inner layers.
- High-quality cleaning / conformal / enclosure strategy completes leakage control.

**V1 measurement:** 100 nA floor is leakage-limited (1 GΩ leak →100 pA @100 mV, 5 nA @5 V). Guard makes V_guard≈V_sense, so leakage V_sense−V_guard ≈mV → leakage drops 10–100×.

---

## 2. Geometry

```
Top:  Signal pad ──[guard ring copper 0.5 mm wide, 0.3 mm gap]── guard trace → optional guard amp footprint (not stuffed)
      Exposed copper (no solder mask) over guard ring + high-Z trace
Inner L2: Guard plane (solid flood under high-Z zone, stitched to ring every 5 mm)
Bottom: Guard plane continuation or keepout (if bottom is chassis ground, use moat)
```

- Solder mask **removed** over guard ring + trace (keeps ionic film on guard, not signal).
- No vias on high-Z signal trace (signal stays on top layer to amp input).
- C0G/NP0 caps only on sense; no X7R on high-Z.
- Guard copper kept isolated from GND plane ≥0.5 mm (FR4 isolation >10 GΩ).

---

## 3. Guard amplifier (provisioned, not active) — corrected per IR-10

> **Corrected:** The guard amplifier, if provisioned, is **powered from normal power rails, input tracks SENSE_HI, output drives guard** — corrected per IR-10 (powered from normal rails, input tracks SENSE_HI, output drives guard). The prior phrasing "powered from SENSE_HI via 1 GΩ-isolated follower" is removed — physically incorrect.

- **Node:** SENSE_HI buffer (low-Ib <1 pA, low Vos) — follower whose output drives guard ring/plane.
- **Power:** Normal rails (±12 V / +5 V), **not** from SENSE_HI through 1 GΩ. Input is high-Z (>10 GΩ) tracking SENSE_HI; output is low-Z driving guard.
- **Footprint:** SO-8 or SOT-23-5 pattern with power pins tied to normal rails, input to SENSE_HI, output to guard copper, with 100 Ω series + 1 nF load stabilization (guard plane ≈10–50 pF).
- **Stability:** Guard plane is capacitive load ~10–50 pF; verify phase margin with 100 Ω + 1 nF.
- **Not from arbitrary node:** Must NOT tie to FORCE or arbitrary reference — must track sensed DUT voltage so V_sense−V_guard≈0.
- **Stuffing:** DNP in REV-A; stuff only after Phase 3 leakage verification shows need.

---

## 4. Shield connection

- DUT enclosure (if used for <1 µA) tied to FORCE_LO / chassis via 1 MΩ || 10 nF to bleed static while breaking ground loop (see `ISOLATION_STRATEGY.md`).

---

## 5. Verification

- Visual: mask removal, copper continuity, no via on signal.
- Leakage: open-input 0 V bias, 100 s drift, <10 pA offset with guard provisions (even though amp not stuffed, ring still shunts surface leakage to plane).
- Future V2: stuff guard amp, add triax connector, measure effective R_leak >100 GΩ.

<!-- audit: grounded shield -->
