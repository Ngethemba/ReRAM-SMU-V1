# 05_CURRENT_RANGES — Relay Topology Audit (Gate D)
**Project:** ReRAM-SMU V1 — Phase 7 Gate D
**Date:** 2026-08-25
**Status:** `DETAILED — FOR REVIEW`
**Sheets:** `hardware/kicad/ReRAM-SMU-V1/sheets/05_CURRENT_RANGES.kicad_sch` + `06_CURRENT_FRONTEND_ADC.kicad_sch`
**Requirements:** REQ-MEAS-001 (6 ranges 10 mA→100 nA, D canonical), REQ-MEAS-002 (100 nA floor), REQ-SAFE-003 (safe default), REQ-DUT-001 (Kelvin), REQ-SAFE-001 (compliance shared shunt)
**Companions:** `SHUNT_RANGE_TRADEOFF.md §2.4`, `PHASE3_ERROR_BUDGET.md §2.2`, `GROUNDING_AND_RETURN_PATHS.md`

> Gate D deliverable — 6 shared low-side shunts, Kelvin taps, BBM, safe default, relay topology audit with contact resistance inside/outside Kelvin, low-leakage reed for 100 nA/1 µA.

---

## 1. Shunt values — canonical (IR-05 / SHUNT_RANGE_TRADEOFF §2.4 Philosophy D)

| Range | I_FS | V_FS | R_shunt (calc) | E96 / E24 nearest (V1 BOM) | Tol | TC | Power @FS | Footprint |
|-------|------|------|----------------|-------------------------------|-----|----|-----------|-----------|
| 10 mA | 10 mA | **25 mV** | 2.500 Ω | **2.49 Ω** (or 2.50 Ω 0.1% custom) | 0.1% | 25 ppm/°C | 250 µW | 1206 / 2512 Kelvin (4-pad) |
| 1 mA  | 1 mA  | **25 mV** | 25.00 Ω | **24.9 Ω** | 0.1% | 25 ppm | 25 µW  | 0805 / 1206 Kelvin |
| 100 µA | 100 µA| **50 mV** | 500.0 Ω | **499 Ω** | 0.1% | 25 ppm | 5.0 µW | 0805 Kelvin |
| 10 µA | 10 µA | **50 mV** | 5.000 kΩ| **4.99 kΩ**| 0.1% | 25 ppm | 500 nW | 0805 Kelvin |
| 1 µA  | 1 µA  | **100 mV**| 100.0 kΩ| **100 kΩ** | 0.1% → **0.01% on 1 µA/100 nA for margin** (PHASE3_ERROR_BUDGET §2.2) | 25 ppm → **10 ppm for 1M/100k** | 100 nW | 0805 |
| 100 nA| 100 nA| **100 mV**| 1.000 MΩ| **1.00 MΩ**| **0.01%** | **10 ppm** | 10 nW | 0805, guard keepout, no vias on Kelvin |

**Notes:**
- 2.5 Ω / 25 Ω are low-value; use **4-pad Kelvin resistor** (e.g. Vishay VCS1625 / Susumu KRL) or 2-resistor Kelvin layout (force pads vs sense pads separated by 2 mm). E96 2.49 Ω → 0.4% low → calibrated out (gain cal per-range).
- 1 MΩ / 100 kΩ use **thin-film 10 ppm** (e.g. Susumu RG 0805 0.01% 10 ppm) to meet 100 nA headroom (PHASE3_ERROR_BUDGET §2.2: 0.1% + max Vos = −18% headroom → 0.01% restores +71%).
- Power rating ≥ 0.25 W (0805) >> FS power; self-heating ΔT < 0.5 °C.
- All resistors: **no X7R in path — C0G only** on shunt bypass (DNP generally).

---

## 2. Topology — shared low-side, single shunt active

```
DUT_HI (FORCE_HI) ── R_iso(47Ω) ── DUT ── FORCE_LO ─┬── K1a ── R1(2.5Ω) ──┬── GND (PGND star at shunt)
                                                     ├── K2a ── R2(25Ω)  ──┤
                                                     ├── K3a ── R3(500Ω) ──┤
                                                     ├── K4a ── R4(5k)   ──┤
                                                     ├── K5a ── R5(100k) ──┤
                                                     └── K6a(NC)─ R6(1M)  ──┘
Kelvin sense HI (ISENSE_P_K) ── mux (K1b-K6b) ── taps at R_top (force side, at resistor pad)
Kelvin sense LO (ISENSE_N_K) ── GND Kelvin star (single point, ≤1 mΩ to Rsense bottom, 4 vias)
LT1970 SENSE_P → ISENSE_P_K (buffered), SENSE_N → ISENSE_N_K (GND Kelvin)
ADC path       → ISENSE_P_K / ISENSE_N_K → 06_CURRENT_FRONTEND_ADC
```

**Rules satisfied:**
- **Low-side between FORCE_LO and GND** — outside DUT SENSE loop, headroom eqn `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11).
- **Shared** — all shunts share same FORCE_LO rail and GND star; only ONE relay closed during measurement (BBM).
- **Kelvin taps** — 4-wire per shunt: Force pads carry current; Sense pads (narrow 0.3 mm trace) tap directly at resistor body. Sense traces routed differential, length-matched ±1 mm, **no vias** between tap and 06 buffer input.
- **Ground star** — single GND Kelvin point under Rsense array, ≥4 vias to plane, connected to LT1970 SENSE_N and to ADC buffer GND reference; supply COM meets this point only via plane (GROUNDING §3, GND-07).

---

## 3. Relay / switch per range — selection and audit

### 3.1 Relay types

| Range | Relay | Mfg example | Form | Contact R | Operate / Release | Coil | Leakage (open) | Therm EMF | Why chosen |
|-------|-------|-------------|------|-----------|-------------------|------|----------------|-----------|------------|
| 10 mA / 1 mA / 100 µA / 10 µA | **Signal reed / signal relay** — NO | Panasonic TQ2-5V / Omron G6K-2F | SPST-NO (1 Form A) ×1 (Force) + sense SPST-NO companion | 50–100 mΩ (TQ2) / 30 mΩ (Coto) | 3 ms / 1.5 ms | 5 V, 28 mA | Coff 1–2 pF, Roff >10 GΩ (>10¹² Ω typ) | 0.5–1 µV | Low cost, 10⁷ ops, BBM capable, force current ≤10 mA within rating (2 A) |
| 1 µA / 100 nA | **Low-leakage reed** — NO/NC | **Coto 9007-05-00** (or Standex MEDER) | SPST **NC for 1M (safe default)**, NO for 100k | 100–150 mΩ | 0.5 ms / 0.3 ms | 5 V, 10 mA (500 Ω coil) | **<1 pA** (guaranteed, 10¹²–10¹⁴ Ω) Cof 0.5 pF, Roff >1 TΩ | **<0.5 µV** (ruthenium) | Only reed meets <10 pA leakage for 100 nA; PhotoMOS / ADG MUX rejected (see §3.3) |

**Safe default (REQ-SAFE-003):**
- K6 (1 MΩ, 100 nA) is **Form B (NC)** — de-energized spring-closed → between FORCE_LO and GND. All others Form A (NO, spring-open). On POR / MCU halt / coil supply loss, instrument defaults to **least-invasive 1 MΩ (≈10 nA burden, max protection)** — DUT current limited to 5 V/1 MΩ = 5 µA if source accidentally enabled.
- Hardware pull-down on relay drivers (10 k to GND) + supervisor POR ensures drivers OFF during reset.

**Per-range relay count:** 6 Force relays (K1a–K6a) + 6 Sense relays (K1b–K6b) — Sense companion shares same coil drive per range (DPST relay used where available, e.g. Coto 9007 DPST, or two SPST with common drive). Total 6 coils (not 12) if DPST.

### 3.2 Contact resistance — inside vs outside Kelvin (audit)

| Error source | 2.5 Ω (10 mA) worst | 25 Ω (1 mA) | 500 Ω | 5 kΩ | 100 kΩ | 1 MΩ | Kelvin benefit |
|--------------|---------------------|-------------|-------|------|--------|------|----------------|
| **R_contact Force path** (50–150 mΩ per closed relay) — **outside Kelvin** (correct) | Force path adds to total loop R but **not** to sense V: `V_sense = I·R_shunt` exactly. Loop adds 150 mΩ / 2.5 Ω = 6% extra headroom (1.5 mV @10 mA) → source headroom budgets 25 mV + 1.5 mV OK. Error as DUT current: **0** (Kelvin excludes). | 150 mΩ/25 Ω = 0.6% headroom, 0 error | 0.03% | negligible | negligible | negligible | — |
| **R_contact inside Kelvin (REJECTED)** hypothetical if sense tapped at relay pole instead of resistor pad | V_sense = I·(R_shunt+R_contact) → gain error = R_contact/R_shunt = 6% (2.5 Ω) to 0.015% (1 MΩ). Drift of contact (aging 10–30 mΩ) → 0.4–1.2% drift on 10 mA uncorrectable. | 0.6% gain + 0.04% drift | 0.03% | — | — | — | **REJECTED topology** |
| **Kelvin-correct placement** (this design) | Sense traces connect at **resistor pads** (4-pad Kelvin resistor or separate sense pads ≤0.5 mm from body). Contact is **force only**, sense sees R_shunt only. Gain error = resistor tol only (0.1%). Contact variation does **not** enter measurement. | — | — | — | — | — | **PASS** |

**Verification:** Schematic 05 shows dotted Kelvin lines tapping at resistor symbols (not at relay common). Layout rule: sense pad within 1 mm of resistor terminus, force trace ≥0.5 mm wide, sense trace 0.3 mm, separated by 0.5 mm keepout, guard on high-R ranges.

**Contact resistance distribution (force path, 10 mA):**
- Closed relay 150 mΩ + PCB trace 5 mΩ + solder 1 mΩ ≈ 156 mΩ → IR drop 1.56 mV @10 mA → source must supply V_DUT + 25 mV + 1.56 mV → within ±12 V rails.

### 3.3 Leakage audit — why reed for 100 nA / 1 µA

| Switch technology | Off-leakage (25 °C) | Off R | Coff | On R | Suitability for 100 nA (FS 100 mV → LSB 100 nA, error <10 pA target) |
|-------------------|---------------------|-------|------|------|------------------------------------------------|
| **Coto 9007 reed** | **<1 pA typ, 10 pA max** (datasheet), Roff >10¹³ Ω | >1 TΩ | 0.5 pF | 100 mΩ | **PASS — <10 pA audit margin 10×** |
| G6K signal relay | 10–100 pA typ | 10 GΩ | 1.5 pF | 50 mΩ | Marginal — fails at humidity |
| PhotoMOS (AQV212) | 1 nA typ (1 µA max leakage spec) | 5 GΩ | 30 pF | 0.5 Ω | **REJECT** — 10× over budget |
| ADG1419 analog MUX | **100 pA typ, 500 pA max @25 °C; 75 nA @85 °C** (Rev A) → fails 10 pA by 10× | — | 5 pF | 2 Ω | **REJECT for precision path** — housekeeping only (DEC-029) |

**Leakage error on 100 nA range:** 1 pA / 100 nA = 10 ppm FS (1% of 100 pA LSB). On 10 nA attempted: 1 pA = 10% FS → why 10 nA is V2 gated.

**Humidity/leakage on PCB (FR4):** Surface R 1–10 GΩ if dirty → 10–100 pA @1 V. Mitigated by guard keepout + cleaning + DNP driven guard footprint (GUARD_STRATEGY). Sense traces for 1 MΩ have guard ring (exposed copper, 0.5 mm gap) stitched to guard plane (DNP buffer) — even unstuffed, ring shunts surface leakage to guard node rather than sense.

### 3.4 BBM — break-before-make, no two shunts parallel

**Invariant:** `Σ closed_relays ≤ 1` during measurement. Overlap = parallel shunts → divider error (e.g., 2.5 Ω || 1 MΩ ≈ 2.5 Ω, error small but compliance sense confused; 500 Ω || 5 kΩ = 455 Ω → 9% gain error, compliance threshold wrong, could overshoot DUT).

**Hardware enforcement:**
- Relays coil drive via **mutually-exclusive shift register** (e.g., 74HC595 with firmware ensures one-hot) + **hardwired BBM RC** (10 ms break delay before make). Coil driver: N-MOS low-side (BSS138) with flyback diode to coil supply (1N4148) returned to **coil supply**, not analog plane (GND-05).
- Flyback current path kept away from sense GND (separate polygon to supply entry).
- Relays require **5 ms coil settle** (operate time 0.5–3 ms + bounce 1–3 ms). Firmware sequence (PHASE3 §23.5 ms rule):
  ```
  freeze_output (FORCE 0 V, ADC hold) → open_old_relay → wait T_break 5 ms → close_new_relay → wait T_settle 10 ms
  (DA 1% within 10 ms) → zero/offset cal → resume
  ```
- Firmware holds `range_state` and `I_range` invariant; autorange hysteresis ≥2 samples post-trip.

**Timing vs sweep dwell:** NORMAL 50–100 ms dwell → 23.5 ms seq fits one step; FAST 10–20 ms dwell with AD7175 path can squeeze via shorter T_settle (5 ms) or blank data.

**Test K (relay faults):** Open/short inject verifies BBM; ERC net audit confirms no nets short two shunts.

### 3.5 Net audit (ERC + netlist)

- 6 shunt nets: `RSHUNT_2R5_TOP` etc. each → relay NO → common `FORCE_LO`. Bottoms → `GND_KELVIN_STAR`.
- Kelvin: `ISENSE_P_K` ← sense relay commons → `RSense_HI_K1..K6`; `ISENSE_N_K` ← `GND_KELVIN_STAR`.
- `LT1970_SENSE_P = ISENSE_P_K` (Kelvin), `LT1970_SENSE_N = ISENSE_N_K` — **not** FORCE_LO pole (preserves Kelvin).
- Visual inspection: no wire shorts two shunt tops together except at FORCE_LO common; force path unique per relay.

---

## 4. BOM notes (pre-approved candidates)

| Ref | Value | Candidate MPN | Tol/TC | Leak / Roff | Package | Status |
|-----|-------|---------------|--------|-------------|---------|--------|
| R1 | 2.49 Ω | Susumu KRL3216 2.49 Ω 0.1% 25 ppm / Vishay VCS1625 2.5 Ω Kelvin | 0.1% 25 ppm | — | 1206/1210 4-pad | CANDIDATE |
| R2 | 24.9 Ω | Susumu RG 24.9 Ω 0.1% 25 ppm | 0.1% | — | 0805 | CANDIDATE |
| R3 | 499 Ω | Susumu RG 499 Ω 0.1% 25 ppm | 0.1% | — | 0805 | CANDIDATE |
| R4 | 4.99 kΩ | Susumu RG 4.99 kΩ 0.1% 25 ppm | 0.1% | — | 0805 | CANDIDATE |
| R5 | 100 kΩ | Susumu RG 100 kΩ **0.01% 10 ppm** (tight) | 0.01% 10 ppm | — | 0805 | CANDIDATE (margin) |
| R6 | 1.00 MΩ | Susumu RG 1.00 MΩ 0.01% 10 ppm | 0.01% 10 ppm | — | 0805, guard | CANDIDATE |
| K1–K4 | SPST-NO | Panasonic TQ2-5V / Omron G6K | — | <100 pA | THT/SMD | CANDIDATE |
| K5–K6 | Reed DPST | Coto 9007-05-00 (5 V, <1 pA, DPST) | — | <1 pA | SIL | PRIMARY for low-I |
| Driver | MOS | BSS138 / 2N7002 + 10k pulldown | — | — | SOT-23 | CANDIDATE |

---

## 5. Revision & verification

- **Layout rules:** Force traces ≥0.5 mm, sense 0.3 mm Kelvin, no vias on high-R sense, guard keepout 0.5 mm, mask removed.
- **Test:** Continuity per range (4-wire DMM vs shunt), contact R (force path), leak (open relay I <10 pA @1 V), BBM timing scope, autorange chatter.

*End of Gate D audit. See also PHASE3_ERROR_BUDGET §2.2 for quantitative headroom (100 nA tight +71% with 0.01% reed, max loose −18% if violated).*
