# 09 DUT Connector & Guard Strategy — 4-Wire Kelvin + Shield/Guard + Keepout + TP Policy

**Project:** ReRAM-SMU V1 — Phase 7 Schematic Capture  
**Sheet:** `09_DUT_CONNECTOR_GUARD` (`hardware/kicad/ReRAM-SMU-V1/sheets/09_DUT_CONNECTOR_GUARD.kicad_sch` Rev 0.2)  
**Date:** 2026-08-25  
**Status:** `DETAILED — READY FOR LAYOUT REVIEW`  
**Companions:** `GUARD_STRATEGY.md` (taxonomy), `KELVIN_SENSE_ARCHITECTURE.md`, `GROUNDING_AND_RETURN_PATHS.md` (IR-13), `LOW_CURRENT_MEASUREMENT.md` §4, `DEC-019/022`, `P3IR-06` (reed <1 pA)  

---

## 1. DUT Stack & Connector Choice

### 1.1 Signal List

| Pin | Function | Direction | Path | Notes |
|-----|----------|-----------|------|-------|
| 1 | `FORCE_HI` | Source → DUT | Power (LT1970 OUT → `R_iso` 47 Ω → connector) | Trace 1 mm (2 oz), <20 mm to R_iso. Fuse/polyfuse not in FORCE path (supply rail only). |
| 2 | `FORCE_LO` | DUT → shunt top | Return (DUT → shared shunt 2.5 Ω–1 MΩ → GND) | Star Kelvin pick at jack lug for both shunt SENSE_P and SENSE_LO buffer. |
| 3 | `SENSE_HI` | DUT → buffer (>10 GΩ) | High-Z (OPA140 buffer, 10 pA max, 3 pF Cin) | 0.3 mm guarded, 15–20 mm to buffer. |
| 4 | `SENSE_LO` | DUT → buffer (>10 GΩ) | High-Z, matched to SENSE_HI | Differential pair with SENSE_HI, length-matched <2 mm. |
| 5 | `SHIELD` / `CHASSIS` | Enclosure → bleed | Shield (1 MΩ \|\| 10 nF + 1 nF HF to FORCE_LO) | Breaks ground loop, drains static, not a guard. |
| 6 | `GUARD` (provision) | Guard amp OUT → copper ring/plane | Guard (DNP in REV-A) | Top ring 0.5 mm + inner plane stitched every 5 mm. |

**DUT voltage:** `V_DUT = SENSE_HI − SENSE_LO` (buffered differential). Force corrects `I·R_lead + V_shunt` headroom per `V_FORCE = V_DUT + V_SHUNT + I·R_LEAD` (IR-11). Burden is outside SENSE.

### 1.2 Connector Strategy (two footprints, one stuffed)

**Primary (stuffed):** 4× isolated 4 mm banana jacks, 19.05 mm pitch, nylon washers (Keystone 575-4 / Hirschmann PKI10A).  
- Colors: red FORCE_HI, black FORCE_LO, green SENSE_HI, blue SENSE_LO.  
- Isolated from chassis — shield pin is separate solder lug on chassis wall, not jack body.  
- Rating 10 A, but Kelvin jacks see 10 mA max; key benefit is tooling availability + shielded cable compatibility (banana→BNC/coax adapters).

**Alternate footprint (DNP, layout-compatible):** 5-pin 3.5 mm screw terminal (Phoenix MC 1.5/5-G) + 2-pin 2.54 mm sense header, pitch 3.5 mm, for bare-die probe card. Silkscreen marks both.

> **Triax is V2** (REQ-DUT-003). No triax body in V1 — but guard ring/plane geometry leaves the **triax outer-shell footprint** as a keepout circle (12 mm) for V2 drop-in.

---

## 2. Shield vs Guard — Do Not Conflate

| Concept | REV-A status | What it is | How to wire |
|---------|--------------|------------|-------------|
| **Passive keepout / clean high-Z zone** | **Yes** | Exposed copper keepout, no mask, 0.5 mm gap to sense | Solder mask removed over ring+trace; keep ionic film on guard, not signal. |
| **Grounded shield** | **Yes** | Chassis/enclosure tied to `FORCE_LO` via `1 MΩ \|\| 10 nF + 1 nF HF` | 1 MΩ bleeds static, 10 nF breaks LF loop, 1 nF shunts HF. Not a guard — does not null `V_sense−V_guard`. |
| **Driven guard** | **Footprint only, DNP** | OPA140 follower, powered from **normal rails** (+5 V/±12 V), input tracks `SENSE_HI`, output drives guard ring/plane via `100 R + 1 nF` (stab for 10–50 pF plane) | SO-8 footprint, power not from SENSE_HI via 1 GΩ (corrected per IR-10). Stuff only if 100 nA leakage > spec. |
| **Guard copper provision** | **Yes** | Top ring 0.5 mm wide, gap 0.3 mm to sense, inner plane stitched every 5 mm, isolated from GND ≥0.5 mm | FR4 isolation >10 GΩ; verify with 5 V bias. |

**Critical rule:** **No grounded guard ring around `SENSE_HI` tied to GND plane.** A ground-tied guard injects leakage `I = (V_sense − 0)/R_surface` into `SENSE_HI`. Only keepout (floating) or correctly driven guard (tracks `SENSE_HI`) is allowed. `GND` keepout around `SENSE_HI` -> **fails leakage**; `GUARD` tracking `SENSE_HI` -> `ΔV ≈ mV` -> leakage drops 10–100×.

**Guard amplifier (if stuffed):**
- IC: OPA140 (or ADA4625) — Ib 10 pA max, Vos 120 µV, stable with 50 pF.  
- Input: `SENSE_HI` buffered node (after OPA140 sense buffer).  
- Output: guard copper via 100 R series + 1 nF to GND for phase margin.  
- REV-A: **DNP** — guard floats as passive keepout; measure leakage <10 pA at 100 nA range before stuffing.

---

## 3. Short Path & C_down Budget

### 3.1 Physical Rules

- `FORCE_HI` -> `R_iso` (47 Ω) -> connector: **<20 mm** total, 1 mm trace, no neck, not over guard plane.
- `SENSE_HI/LO`: **15–20 mm** to OPA140 buffers (sheet 04), 0.3 mm trace, **no vias** (top layer only to buffer input), guarded both sides + via fence, length-matched <2 mm for CM rejection.
- `FORCE_LO` star: jack lug is Kelvin node for **two** traces: (a) `LT1970_SENSE_P` to shunt top (shared 2.5 Ω–1 MΩ), (b) `SENSE_LO` buffer input. No daisy chain.
- Cable: downstream `C` budget **80 pF @5 V gentle (1 nJ) / 150 pF @5 V standard (2 nJ)** per IR-14. Only `C_down` (after `R_iso`, on DUT side) counts toward `E = ½·C·V²` dump; upstream `C_comp` (≤10 nF before `R_iso`) is isolated.  
- Downstream contributions (measure on first article with LCR @10 kHz):

| Element | Typical C | Notes |
|---------|-----------|-------|
| Jack body | 5–10 pF | Isolated banana; check with guard floating |
| PCB trace (20 mm, guarded) | 1–2 pF | 0.3 mm + 0.3 mm gap |
| Relay Coff (Coto 9007) | 1–3 pF | <1 pA leakage chosen per P3IR-06 |
| Buffer Cin (OPA140) | 3 pF | Per datasheet |
| ESD (FORCE only) | 0.5 pF | ESD7384 0.35 pF; SENSE ESD DNP |
| DUT + probe | 0.5–5 pF | Bare die 0.5 pF, packaged 5 pF |
| Cable (0.5 m low-C coax) | 25–50 pF | Limit cable to 0.5 m; advise ≤3 V forming at 5 V if longer |

Sum ~35–75 pF → **well within 80–150 pF budget**. If longer cable required, stuff series switch after `R_iso` + shunt discharge FET (both DNP in REV-A).

### 3.2 Capacitance Validation

- Mark `C_down` on layout as a schematic-driven net class (`C_down ≤ 80 pF`).  
- First-article measure: disconnect DUT, clip LCR between `FORCE_HI` and `FORCE_LO` at 10 kHz, 0 V bias — record in bring-up log.  
- Fail if >150 pF → reduce cable, remove ESD on SENSE, or shorten trace.

---

## 4. ESD & OVP — Low-C, Low-Leak

| Net | ESD strategy | Part | C added | Leakage @25 °C | Status |
|-----|--------------|------|---------|----------------|--------|
| `FORCE_HI/LO` | Primary clamp + series R | ESD7384 (0.35 pF, 6 V) or PESD5V0S1BSF + 10 R series | 0.5 pF | <1 µA (acceptable on 10 mA power path) | **Stuffed** |
| `SENSE_HI/LO` | **DNP** — no ESD in precision path | Footprint ESD7384 DNP; if handling ESD required, use `BAT54S` to **guard** (not GND) or external dongle | 0 pF (0.35 pF if stuffed) | <10 pA budget; 1 nA @85 °C **fails** 1 nA MUC → DNP unless characterized | **DNP** (REV-A) |
| Shield | Chassis TVS | SMAJ5.0A DNP, bidirectional 5 V | 100 pF (DNP) | — | DNP |

- Connector pins have adjacent TVS footprints (SOD-123), but SENSE TVS is **not populated** until leakage characterized on 1 MΩ range (apply 5 V guard-to-sense, measure <10 pA).  
- FORCE series 10 R (thin-film) also limits ESD dump current into `R_iso`.

---

## 5. Keepout & Layout Rules (enforce in PCB)

| Rule | Value | How to enforce |
|------|-------|----------------|
| **GW-01** Guard ring width / gap | Ring 0.5 mm, gap 0.3 mm to sense | Layout rule: keepout 0.5 mm from sense trace; mask expansion 0.3 mm removed over ring+trace. |
| **GW-02** Inner guard plane | Solid flood under high-Z zone (SENSE + 1 MΩ shunt + TIA if any), stitched to ring every 5 mm via 0.3 mm drill | Polygon pour `GUARD`, net tie to `FORCE_LO` via `1 M\|\|10 nF` (or driven amp if stuffed). Isolated from `GND` ≥0.5 mm. |
| **GW-03** No vias on SENSE | SENSE_HI/LO stay on top layer to buffer | Layout DRC: via forbidden on nets `SENSE_HI`, `SENSE_LO`. |
| **GW-04** Dielectric | C0G/NP0 only on high-Z; no X7R on sense | BOM rule; SENSE dividers use 0.01% thin-film + C0G. |
| **GW-05** Mask | No mask over guard ring + sense trace (exposed copper, ENIG) | Footprint property: `mask_expansion 0.3 mm`, or zone `No Mask`. |
| **GW-06** Cleaning | No-clean flux **prohibited** within 10 mm of guard; wash Vigon A200, de-ionized rinse | Assembly drawing note. |
| **GW-07** Isolation test | Guard-to-sense >10 GΩ at 5 V | First-article test: 5 V bias guard vs sense, measure <0.5 nA (10 GΩ). |
| **GW-08** FORCE/SENSE clearance | FORCE to SENSE 1 mm min (creepage) | DRC net clearance class `HV_Guard = 1 mm`. |
| **GW-09** Connector center to buffer | <20 mm | Schematic note + layout constraint line. |
| **GW-10** Moisture | Conformal coat masked over guard ring (or coat guard only after leakage PASS) | Option: Humiseal 1B73 masked rectangle 15×10 mm over guard; keep ring exposed until coat. |

---

## 6. Test Point Policy

### 6.1 Normal Impedance TPs (through-hole, scope-friendly)

Each **Keystone 5002** loop (2.54 mm drill) + adjacent 100 mil header pad for DuPont, labelled `TPxx` on silkscreen:

| TP | Net | Series | Filter | Purpose |
|----|-----|--------|--------|---------|
| `TP_FORCE_HI` | `FORCE_HI` after `R_iso` | direct (0 Ω) | — | Scope filament snap, `C_down` measure |
| `TP_FORCE_LO` | `FORCE_LO` star Kelvin | direct | — | Kelvin ref, dummy-load short |
| `TP_SENSE_HI_BUF` | `SENSE_HI` buffer output (sheet 04) | 100 Ω | — | Verify Kelvin servo, not raw pad |
| `TP_SENSE_LO_BUF` | `SENSE_LO` buffer output | 100 Ω | — | — |
| `TP_VSET` | `VSET` after slew RC (sheet 02) | 100 Ω | 100 pF | Source staircase vs filtered |
| `TP_DAC_OUT` | `AD5764` ChA raw | 100 Ω | — | DAC INL spot check |
| `TP_ADC_IN_P/N` | `ADC_IN_P` to `ADS1262` | 1 kΩ each | 1 nF | Frontend gain / overload recovery |
| `TP_ENABLE` | `ENABLE` | **1 kΩ** | **100 pF** | Verify latch (don't load LT1970) |
| `TP_ISRC/ISNK` | `ISRC/ISNK` | 1 kΩ | — | Continuous compliance flag timing |
| `TP_POR` | `POR` | 1 kΩ | — | Supervisor timing 240 ms |
| `TP_FAULT_Q` | `FAULT_LATCH_Q` | 1 kΩ | — | Latched fault state |
| `TP_3V3/5V/±12V` | Power rails | 0 Ω | 100 nF at TP | Power integrity |
| `TP_GND` | `GND` star near shunt | 0 Ω | — | Kelvin ground reference (not chassis) |

> **Rule:** every normal TP has a `TP_GND` within 15 mm for short ground spring.

### 6.2 Low-Capacitance Pads for `SENSE_HI/LO`

| Pad | Footprint | Added C | Probe method | When to use |
|-----|-----------|---------|--------------|-------------|
| `TP_SENSE_HI_PAD` | **1 mm bare copper circular pad**, guard ring around, **no via, no mask**, labelled | ~1.5–2 pF pad-to-guard (budgeted in `C_down`) | Active probe (>1 GΩ, 0.5 pF) or flying lead electrometer; **never** 10× 100 pF passive probe during nA measure | Debugging Kelvin offset / open-sense |
| `TP_SENSE_LO_PAD` | same | ~1.5–2 pF | same | — |
| Disconnect jumper | **0 Ω 0603 DNP** in series between pad and sense trace | — | Remove jumper for ultimate leak test (pad fully isolated) | First-article leakage |

- Pad placed **within guard ring**, 3 mm from connector, on top layer only.  
- Probe ground: adjacent `GUARD` pad, not `GND` — measuring `SENSE` vs guard nulls surface leakage during debug.  
- **Forbidden:** clipping standard scope probe (10 MΩ, 12–100 pF) directly across `SENSE_HI`–`SENSE_LO` during 100 nA verification — the probe is the DUT (10 MΩ leak = 50 nA @0.5 V). Use buffered TPs above for normal debug.

### 6.3 Calibration Tie Jumper

- `JP9A` — 2-pin header (2.54 mm) + **0 Ω DNP** between `SENSE_HI ↔ FORCE_HI` and separate `SENSE_LO ↔ FORCE_LO`.  
- **Closed only for 2-wire calibration** (force vs sense shorted, compare DMM at jack). Measure `2-wire vs 4-wire` delta on 10 Ω / 1 kΩ dummy to verify Kelvin benefit.  
- **Open for all DUT measurements** — verify open (>10 GΩ) with shunt on 1 MΩ range (leak test).

---

## 7. Bring-Up Checks (before ReRAM)

- [ ] Visual: mask removal verified, guard ring continuity, no via on sense, 0.5 mm guard-to-GND isolation.  
- [ ] Isolation: 5 V guard-to-sense >10 GΩ (0.5 nA max). Clean if fail.  
- [ ] `C_down` LCR <80 pF gentle (150 pF max). Remove ESD if over.  
- [ ] Dummy 1 kΩ 4-wire: `2-wire − 4-wire` = `I·R_lead` within 10% (Kelvin correctness).  
- [ ] Open-sense: disconnect `SENSE_HI`, arm `ENABLE` → `SENSE_OPEN` latch, `ENABLE=0` within 10 µs, stays latched.  
- [ ] Shield continuity: `FORCE_LO ↔ chassis` via `1 M\|\|10 nF` — verify 1 MΩ DC, 10 nF at 10 kHz.

---

*Provenance: `DEC-019/022/029` Kelvin/Guard/Reed, `GUARD_STRATEGY.md` IR-10 corrected taxonomy, `GROUNDING_AND_RETURN_PATHS.md` IR-13 single plane, `PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md` IR-06 reed <1 pA, IR-14 C_down budget, `COMPLIANCE_ENERGY_ANALYSIS.md` E=½CV².*
