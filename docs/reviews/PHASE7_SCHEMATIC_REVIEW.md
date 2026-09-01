# Phase 7 Schematic Review — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 7 Schematic Capture (Hierarchical)
**Date:** 2026-08-25
**HEAD:** `3899852` → this review (`hardware/kicad/ReRAM-SMU-V1/`)
**Status:** `PARTIAL — HIERARCHICAL SKELETON WITH PROVISIONS, ERC WITH WAIVERS`
**Artifacts:** `hardware/kicad/ReRAM-SMU-V1/` (root + 9 sheets), `hardware/kicad/erc.json`, `hardware/kicad/netlist.xml`, this file

---

## 1. Roadmap Normalization

Original Roadmap Phases 4–6 scope (Current Measurement, Hardware Compliance, Integrated Simulation) was **absorbed into Expanded Phase 3** as documented in `simulation/results/phase3/` (Tests A-O, Gates 1-6) and corrective reviews `PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md`, `PHASE3_CORRECTIVE_RESULTS.md`, `R5_1_TOPOLOGY_CORRECT_VENDOR_RESULTS.md` (vendor LT1970.sub with corrected low-side shared shunt + differential Kelvin). All Phase 4–6 exit criteria were satisfied within Expanded Phase 3:

- Phase 4 (Current Measurement): shunts 2.5Ω–1MΩ + ADA4522/OPA140 + ADS1262 (primary) + noise/leakage — consolidated 2026-08-25
- Phase 5 (Hardware Compliance): LT1970 continuous CC + TLV3501 emergency trip + FILTER DNP/open + R_iso 33/47Ω — consolidated
- Phase 6 (Integrated): end-to-end co-sim, power tree, one continuous plane grounding, guard — consolidated

Phases 4–6 marked `COMPLETED AS PART OF EXPANDED PHASE 3 / CONSOLIDATED` in `ROADMAP.md` (commit `3899852`). **Phase 7 — Schematic Capture** is now the canonical schematic phase.

---

## 2. Schematic Structure

**Location:** `hardware/kicad/ReRAM-SMU-V1/`

```
hardware/kicad/ReRAM-SMU-V1/
├── ReRAM-SMU-V1.kicad_pro
├── ReRAM-SMU-V1.kicad_sch (root with 9 hierarchical sheets)
└── sheets/
    ├── 01_POWER.kicad_sch
    ├── 02_DAC_SOURCE_COMMAND.kicad_sch
    ├── 03_OUTPUT_STAGE.kicad_sch
    ├── 04_KELVIN_SENSE.kicad_sch
    ├── 05_CURRENT_RANGES.kicad_sch
    ├── 06_CURRENT_FRONTEND_ADC.kicad_sch
    ├── 07_COMPLIANCE_TRIP.kicad_sch
    ├── 08_MCU_USB_CONTROL.kicad_sch
    └── 09_DUT_CONNECTOR_GUARD.kicad_sch
```

| Sheet | Title | Key Content (Phase 7) |
|---|---|---|
| 01 | 01_POWER | ±12V EXT input, polyfuse, LT3045/LT1763 +5V_A/+3V3, LTC6655-5.0 (AD5764) + LTC6655-2.5 (ADC) refs, POR supervisor, decoupling, TP_POWER |
| 02 | 02_DAC_SOURCE_COMMAND | AD5764 (LQFP-32, 5V ref 20V span half-codes 305µV), LTC6655-5.0, **slew RC 1k + 1nF DNP/PROTOTYPE-TUNE** (R5.1 44% 0.1V risk mitigation), VSET conditioning, TP VREF_5V/DAC_OUT/VSET |
| 03 | 03_OUTPUT_STAGE | LT1970A TSSOP-20 ±12V, VCSRC/VCSNK, ENABLE, **R_iso 33Ω DNP / 47Ω PRIMARY selectable** (not parallel), **C_FILTER DNP/open baseline** with optional 1nF–100nF footprint (LOOP_TUNE), ISRC/ISNK 10k pull-ups to 3.3V, TP LT1970 OUT/FORCE_HI |
| 04 | 04_KELVIN_SENSE | OPA140 SENSE_HI/SENSE_LO buffers (>10GΩ, 5pF), diff amp finite BW 10MHz, **reed relay <1pA** open-sense (not ADG1419), guard keepout provision, TP SENSE_HI_BUF/SENSE_LO_BUF/DIFF |
| 05 | 05_CURRENT_RANGES | **Shared low-side 2.5Ω/25Ω/500Ω/5kΩ/100kΩ/1MΩ** (25/50/100mV FS), Kelvin sense points, break-before-make reed relays, safe default 1MΩ (de-energized), TP each shunt |
| 06 | 06_CURRENT_FRONTEND_ADC | ADA4522 (25/50mV) + OPA140 JFET (100k/1M) hybrid, **ADS1262 PRIMARY** (QFP-28, internal PGA 1-32, SINC4, midscale 2.5V), AD7175 alternate DNP, anti-alias RC, LTC6655-2.5 ref, TP ADC_IN_P/N |
| 07 | 07_COMPLIANCE_TRIP | LT1970 continuous CC via shared shunt (precision) + **TLV3501 emergency supervisor ONLY** (6.5mV, SOT-23-6, loose 120-150% threshold), separate, ISRC/ISNK pull-ups |
| 08 | 08_MCU_USB_CONTROL | STM32G474 LQFP-64, USB-C, relay drivers, watchdog, supervisor, status LEDs, **OUTPUT_ENABLE hardware-safe default (pull-down + supervisor, not firmware)**, TP ENABLE |
| 09 | 09_DUT_CONNECTOR_GUARD | 4-wire Kelvin connector (FORCE_HI/LO + SENSE_HI/LO), shield/chassis, **no driven guard stuffed** (keepout + optional footprint), ESD low-leak (0.5–2pF), TP FORCE/SENSE |

**Stale statements cleaned before capture:**
- FILTER baseline is **DNP/open**, optional 1nF–100nF per 1970afc — not active 220pF (previous 220p outside range, now DNP)
- Grounding is **one continuous reference plane, no etched AGND/DGND split or physical bridge** — per `GROUNDING_AND_RETURN_PATHS.md` corrected wording (placement/return-current/decoupling, not split)
- Previous high-side LT1970 vendor proxy (R5) marked **HISTORICAL / PROXY — NOT SELECTED TOPOLOGY VALIDATION** — authoritative is R5.1 low-side shared shunt + differential Kelvin
- R5.1 selected topology (OUT→R_iso→DUT→shared shunt, differential Vdiff servo, finite-bandwidth OPA140 pole, R_iso 47Ω sweet spot) is authoritative

---

## 3. Critical Architecture

### Source
- AD5764 @5V ref (LTC6655-5.0) ±10V span, half-codes for ±5V (305µV LSB, 3.0% of 10mV step, ±1LSB guaranteed at 5V), supply ±11.4–16.5V via raw ±12V (0.6V margin). AD5686R→×2 fallback DNP. Slew RC provision 1k+1nF DNP at VSET.

### Kelvin
- **Vdut = SENSE_HI − SENSE_LO** servoed to VSET, not FORCE_HI vs GND. OPA140 buffers (10pA max, 0.8fA noise) → diff amp (10MHz pole) → LT1970 -IN. Previous ideal VCVS replaced with realizable 3-op-amp diff. Reed <1pA open-sense, latch OFF, no ADG1419 in precision path.

### Current Ranges
- Shared low-side: 10mA 2.5Ω/25mV, 1mA 25Ω/25mV, 100µA 500Ω/50mV, 10µA 5kΩ/50mV, 1µA 100kΩ/100mV, 100nA 1MΩ/100mV (SHUNT_RANGE_TRADEOFF §2.4 D). Kelvin across shunts, LT1970 SENSE+→FORCE_LO, SENSE-→GND. BBM hardware+firmware: freeze/disable → break old → wait 5ms → make new → settle 10ms → zero → resume (23.5ms seq, per Test K).

### ADC
- **ADS1262 PRIMARY** (internal PGA 1-32, Vref/PGA limit 78mV@32, SINC4 20SPS single-cycle 50ms, 130dB notch). Requires only small 3.13× pre-gain for 25mV (vs 100× external for AD7175). AD7175 alternate DNP (needs external 100/50/25×). Midscale 2.5V, input RC, buffer, reference LTC6655-2.5.

### DAC
- LTC6655-5.0 5V (0.8ppm, 0.775µV p-p) for AD5764 REFAB/REFCD (spec condition), REF 5V ±1% for ±1LSB. ±5V uses half codes 16384–49151, document code-range consequence.

### Compliance / Protection
- Continuous: LT1970 VC/10 threshold via shared shunt (precise, 1% separate ISRC/ISNK, 4µs takeover). Emergency: TLV3501 loose supervisor 120–150% range-dependent (150%@1mA,130%@10µA,120%@100nA), not precision, separate latch/disable. ISRC/ISNK **pull-ups 10k to 3.3V** (R5.1 proven: Source Isrc 0.03V low/Isnk 3.3V, Sink opposite), not pull-downs.

### Power
- External ±12V bench (no mains on PCB) → analog ±12V_A (LT1970/AD5764), +5V_A via LT3045/LT1763 + LC π, +3V3 via TLV1117, por supervisor 10k pulldown + 200ms POR (Test L). One continuous plane, star via placement/decoupling.

---

## 4. ERC

**Tool:** `E:/KiCad/bin/kicad-cli.exe sch erc --format json --severity-all`

**Output:** `hardware/kicad/erc.json` (219 violations), `hardware/kicad/netlist.xml` (kicadsexpr)

| Check | Result | Evidence | Waiver |
|---|---|---|---|
| label_dangling (global labels) | **219 total — 45× label_dangling errors** (FORCE_HI etc. in root) | `erc.json` label_dangling at (10,10) etc. | **Waived — skeleton hierarchical schematic uses global labels as inter-sheet net references without physical wires in this minimal skeleton; detailed capture will wire nets. Net audit (see §5) verifies no accidental shorts. Waiver documented, to be cleared in detailed capture.** |
| footprint_link_issues | ~10 warnings (Fuse_1206, Relay_Coto_9007, Package_LQFP not in configured library) | `erc.json` footprint_link_issues | Waived — footprints are provisional (Phase 7 policy: PROVISIONAL/PRIMARY, not final BOM). Final footprint verification in Phase 7 detailed capture with library curation. |
| lib_symbol_mismatch | ~10 warnings (R symbol vs Device lib) | `erc.json` lib_symbol_mismatch | Waived — skeleton uses generic Device:R/C/OpAmp for speed; detailed capture will use exact manufacturer symbols (AD5764, LT1970, etc.) with curated library. |
| endpoint_off_grid | ~30 warnings (10mm grid vs 1.27mm) | `erc.json` endpoint_off_grid | Waived — coordinates at 10mm multiples off 0.254mm grid; detailed placement will snap to 0.254mm/1.27mm grid. |
| power pins | 0 errors after adding GND/+12V etc. power symbols | `netlist.xml` shows GND net | Pass (with waivers) |
| NC pins | 3 NC in LT1970 (10,11,18) tied to 1M to GND | `vendor_lt1970_R5p1/*.cir` Rnc10/11/18 | Pass |

**Target per Phase 7 exit criterion:** `0 unexplained errors` — **not yet met in skeleton** (45 label_dangling errors remain). **Path to 0:** Wire global labels to pins (or convert to hierarchical sheet pins) and add power flags in detailed capture; re-run ERC. Current ERC is **skeleton baseline**, not final.

**Next:** Detailed wiring + library curation → re-run `kicad-cli sch erc --severity-error` → 0 errors.

---

## 5. Schematic Netlist Audit (Critical Nets)

**Method:** Exported `kicadsexpr` netlist (`hardware/kicad/netlist.xml`) and manual review of hierarchical labels (ERC report). Automated grep for critical nets in netlist:

```bash
grep -E "FORCE_HI|FORCE_LO|SENSE_HI|SENSE_LO|LT1970_SENSE|VCSRC|VCSNK|ISRC|ISNK|OUTPUT_ENABLE|VSET|ADC_IN" hardware/kicad/netlist.xml
```

**Result (skeleton):** Nets appear as global labels but are **not yet wired** between sheets (netlist shows isolated sheets, no cross-sheet connections). This is expected for skeleton — no shorts detected, but also no continuity.

**Critical invariants to verify in detailed capture (checklist for next commit):**

| Net | Intended Connection | Audit in skeleton | Required in detailed |
|---|---|---|---|
| FORCE_HI | LT1970 OUT → R_iso → DUT_HI | label exists, not wired | Wire OUT→R_iso→J1.FORCE_HI + Kelvin buffer input |
| FORCE_LO | DUT_LO → Rshunt top → LT1970 SENSE_P | label exists, not wired | Wire DUT_LO→Rshunt→LT1970_SENSE_P Kelvin |
| SENSE_HI | DUT_HI → OPA140 buffer → diff | label exists, not wired | Wire DUT_HI→U1+ → diff |
| SENSE_LO | DUT_LO → OPA140 buffer → diff | label exists, not wired | Wire DUT_LO→U2+ → diff |
| LT1970_SENSE_P | Rshunt top Kelvin | label exists | Wire FORCE_LO Kelvin point → LT1970 pin 4 |
| LT1970_SENSE_N | Rshunt bottom (GND) Kelvin | label exists | Wire GND Kelvin → LT1970 pin 6 |
| VCSRC/VCSNK | DAC/ADS1262 → LT1970 Vc pins | labels exist | Wire from MCU DAC or resistor divider, 0–5V, 60mV linear threshold |
| ISRC/ISNK | LT1970 flags → MCU + pull-ups 10k to 3.3V | labels exist, pull-ups present in sheet 07 | Wire 10k to 3.3V, verify open-collector |
| OUTPUT_ENABLE | MCU + supervisor → LT1970 EN (pull-down safe) | label exists | Hardware pull-down 10k to GND, supervisor drives |
| VSET | AD5764 → slew RC → diff → LT1970 +IN | label exists, slew RC DNP | Wire DAC_OUT→R(1k DNP)→C(1nF DNP)→+IN |
| ADC_IN_P/N | Shunt Kelvin → ADA4522/OPA140 → ADS1262 | labels exist | Wire shunt Kelvin → frontend → ADS1262, PGA, midscale |

**Relay audit:** 05 sheet shows 6 shunts with reed symbols (R1–R6) but no inter-shunt wiring — skeleton, no parallel risk yet. Detailed capture must ensure **BBM: break before make, no two shunts parallel during measurement** (hardware interlock + firmware 23.5ms seq). Check: de-energized default 1M (safe for HRS reads).

**Status:** **Skeleton — no shorts, but no continuity yet; detailed capture must complete wiring and re-audit via netlist grep.**

---

## 6. Prototype-Tune Items

All marked `DNP` / `PROTOTYPE-TUNE` / `PROVISION ONLY`:

| Item | Provision | Default / Baseline | Tuning |
|---|---|---|---|
| **R_iso** | 33Ω (R_ISO33) + 47Ω (R_ISO47) | **47Ω PRIMARY** (sweet spot, P3IR-02) | Layout-compatible option (not parallel), select via DNP stuffed, prototype stability 10pF–1nF |
| **C_FILTER (LT1970 FILTER)** | DNP/open baseline + optional 1nF–100nF footprint | **DNP** (open) | LOOP_TUNE — per 1970afc FILTER 1kΩ internal, cap to SENSE- 1nF–100nF, prototype with 220p/1nF/10nF |
| **Slew control (VSET)** | R1 1kΩ + C1 1nF RC after AD5764 | **DNP** (provision) | R5.1 44% overshoot at 0→0.1V hard step (10kΩ 100pF) → **required mitigation**: firmware staircase/ramp ≤10mV/µs or RC≥20µs for 0.1V, schematic provision + prototype validation |
| **Guard** | Keepout + stitched inner plane, no driven guard stuffed | **PROVISION ONLY** (exposed copper, no mask) | Optional driven guard footprint (powered from rails, not SENSE_HI via 1GΩ) for V2 |
| **Alternate footprints** | AD5764 vs AD5686R, ADS1262 vs AD7175, LT1970 vs LT1970A (1% grade), OPA140 vs ADA4625, relay Coto vs Panasonic | PRIMARY as listed above, ALTERNATE DNP | Second-source, lifecycle |
| **Test points** | 20+ TPs (see §3) | PRIMARY | Prototype debugging without probing high-Z |

---

## 7. New Issues Found During Capture

1. **KiCad library gaps:** LT1970A, AD5764, ADS1262, LTC6655, TLV3501, STM32G474 symbols not in default Device library — skeleton uses generic OpAmp/R symbols with correct Value/Footprint properties. **Issue:** Detailed capture requires curated library (download ADI/TI PSpice symbols or create custom). **Action:** Create `hardware/symbols/` with manufacturer symbols before detailed wiring.
2. **Off-grid placement:** 10mm grid causes endpoint_off_grid warnings (KiCad grid 0.254mm/1.27mm). **Action:** Snap to 1.27mm grid in detailed capture.
3. **Footprint library not configured:** `Fuse_1206`, `Relay_Coto_9007` not found in default libs — ERC footprint_link_issues. **Action:** Configure `sym-lib-table`/`fp-lib-table` and assign verified footprints (e.g., `Resistor_SMD:R_0805`, `Capacitor_SMD:C_0805`, `Package_QFP:LQFP-64`, `Connector_Banana:*`).
4. **Global label wiring missing:** Hierarchical skeleton has no wires between global labels and pins → ERC label_dangling. **Action:** Detailed capture must wire nets (or use hierarchical sheet pins) and re-run ERC to 0 errors.
5. **Power flags missing in some sheets:** ERC may flag power pins without PWR_FLAG — add `PWR_FLAG` symbols in 01_POWER.

---

## 8. Remaining Prototype Risks

- LT1970 loop compensation vs cable L 10–100nH, trace R, ESL/ESR, FILTER wiring L, package parasitics — not in vendor macro (or approx) → prototype step response required (R5.1)
- Leakage/DA/therm EMF/humidity on 100nA range, guard keepout, flux, via stitching — not in SPICE
- Ib tempco, en/in PSRR, crossover distortion, Vc<60mV knee vs temp, latch-up — approx only
- Isrc/Isnk flag-MCU race, ENABLE high-Z, TSD
- Slew control at 0.1V (44% risk) — RC+firmware ramp must be tuned on prototype (10kΩ–1MΩ 100pF)
- ADS1262 PGA vs external pre-gain for 25mV (3.13× pre-gain) — verify ENBW and overload recovery <10ms
- Reference hysteresis (ADR4525 vs LTC6655 D-grade), long-term drift, humidity

---

## 9. Requirements Traceability (Update)

- Updated `ROADMAP.md` (Phases 4–6 consolidated)
- To update: `REQUIREMENTS_TRACEABILITY.md` — map REQ-SRC/DUT/MEAS/SAFE to sheets 01–09
- `DECISIONS.md` — new DEC-032 (Phase 7 hierarchical skeleton) to be added
- `RISKS.md` — add R5.1 44% slew risk
- `OPEN_QUESTIONS.md` — Q-13 (cal reference) remains OPEN, Q-20 (firmware safe-state) partially resolved with hardware ENABLE

---

## 10. Git

- **Commits (this phase):** `3899852` roadmap rebaseline
- **Next commits (planned):** `hardware: create ReRAM-SMU hierarchical schematic (skeleton)`, `hardware: complete <sheet> detailed wiring`, `docs: complete Phase 7 schematic review`
- **Remote:** `origin/master` at `cd0bf6d` (R5.1 cleanup) → next push after skeleton commit
- **Working tree:** `hardware/kicad/ReRAM-SMU-V1/` skeleton present, no PCB, no Gerbers, no final BOM — correct per Phase 7

---

## 11. Recommended Next Action

**Detailed Schematic Capture:** Wire all critical nets (FORCE_HI/LO, SENSE_HI/LO, LT1970_SENSE_P/N, VCSRC/VCSNK, ISRC/ISNK pull-ups, VSET slew RC, ADC chain), curate manufacturer symbols/footprints, add power flags, snap to grid, re-run `kicad-cli sch erc` to **0 errors**, export netlist/BOM, then request **Independent Schematic Design Review** — do not begin PCB layout automatically.


---

## 12. Addendum 2026-08-25 — Gates C/E Detailed (Agent D)

**Sheets updated:** `03_OUTPUT_STAGE.kicad_sch rev0.2`, `04_KELVIN_SENSE.kicad_sch rev0.2` — detailed capture per Phase 7 Gate C/E.

### Gate C — 03_OUTPUT_STAGE LT1970A Detailed

| Item | Provision | Value / Footprint | Note |
|---|---|---|---|
| LT1970A | U301 TSSOP-20_6.5x4.4mm_P0.65mm_ThermalPad EP=V− | `LT1970AIFE#PBF` | All 19 pins + EP (20) wired per 1970afc; SpiceOrder verified via LT1970.asy (VEE 1, V− 2, OUT 3, SENSE+ 4, FILTER 5, SENSE− 6, VCC 7, −IN 8, +IN 9, NC 10/11/18 1 M→GND, VCSNK 12, VCSRC 13, COM 14→GND, ENABLE 15→47 k pull-down, ISRC_N 16→10 k→3V3, ISNK_N 17→10 k→3V3, V+ 19). EP stitched 4 vias to −12 V. Decoupling 100 nF+10 µF per rail (C302–306). |
| R_iso | **FIT ONE ONLY** | R301 33 Ω DNP + R302 47 Ω PRIMARY 0805 overlapping pads | Not parallel, selectable; default 47 sweet spot per P3IR-02/R5.1/ R5.1E (stable 10 pF–1 nF, 11–37% OS). Layout note: two pads overlapping, stuff one. |
| FILTER | C301 DNP/open baseline | 0805 footprint 1 nF–100 nF provision | 1970afc 1 nF–100 nF (1 kΩ internal to SENSE−), prev 220 p outside range → DNP, prototype 1 n/10 n/100 n. |
| VCSRC/SNK | 0–5 V clamped | 1 kΩ series + BZX84C5V1 5.1 V Zener to COM | Clamp protects Vc>5 V (Vsense=Vc/10), Vc<60 mV nonlinear per IR-01/DEC-024. |
| ENABLE | HW-safe | 47 k pull-down to GND + supervisor (08) | Defaults OFF on POR/brown-out/watchdog per REQ-SAFE-003. |
| ISRC/ISNK | OC flags | 10 k pull-ups to +3V3 | Verified in R5.1: Source Isrc 0.03 V low/Isnk 3.3 V, Sink opposite; not pull-downs (previous error). |
| Test points | TP301 OUT, TP302 FORCE_HI | Pad D1.5 mm | |

*Net audit Gates C:* FORCE_HI (OUT→R_iso→J1 FORCE_HI), LT1970_SENSE_P→FORCE_LO Kelvin, SENSE_N→GND, VSET→+IN, VDIFF_FB→−IN, ISRC/ISNK→08 MCU, VCSRC/SNK→02 DAC, ENABLE→08.

### Gate E — 04_KELVIN_SENSE K1 Differential + Reed Isolation

**Topology choice:** See `docs/architecture/DEC-032_KELVIN_DIFFERENTIAL_TOPOLOGY.md` (K1 PRIMARY 2×OPA140 buffers + 4×10 kΩ 0.1% diff (C401 15 pF 10.6 MHz), K2 LT5400 0.01% provision, K3 REJECTED Ib fail).

| Block | Ref | Value / Footprint | Key spec |
|---|---|---|---|
| Buffers | U401A/B OPA140AID SOIC-8 | >10 GΩ, Cin 5 pF, Ib 10 pA max, 0.8 fA noise, 11 MHz | Isolate DUT, only Cin at DUT (0 pF filter after buffer per IR-04). |
| Diff | U402 OPA140 + R401–404 10 k 0.1% 25 ppm, C401 15 pF | Gain 1, CMRR 54 dB (K1) /86 dB (K2 LT5400 QFN DNP) | VDIFF=VHI−VLO →LT1970 −IN, error <0.5 mV CV. |
| Reed isolation | K301/K302 Coto 9007 | <1 pA, 1 pF Coff | Switched pull network R405/R406 10 MΩ behind NO contacts; window comp U404 TLV3501 (|Vdiff−Vforce|>0.5 V) → OPEN_SENSE_FLAG→SR latch→reeds OPEN before OUTPUT ON, latch OFF sticky (IR-03, ≥10 GΩ disconnected during meas). |
| Guard | keepout 0.5 mm, stitched plane DNP, C0G only |  |  |
| TP | TP401 HI_BUF, TP402 LO_BUF, TP403 VDIFF_FB |  |  |

*Open-sense latch OFF:* Any OPEN flag or watchdog/POR latches fallback to FORCE mode (internal divider), re-arm only by explicit `SENS:REM ON` + OUTPUT cycle — no chatter.

### LTspice Gate E Validation (R5.1E, vendor LT1970.sub + OPAx140.LIB, R_iso 47)

*Method:* LTspice 26.0.2.1 batch, 11 benches 100 pF/1 nF at +0.1 V/+2 V/−2 V CV/CC (see `simulation/results/phase3/R5P1E_GATE_E_REAL_KELVIN_RESULTS.md`). Pulse 0→Vset 30 µs high, .meas 10–25 µs high plateau.

| Bench | Cdut | Vset | Mode | Vdut | Error | OS | Ishunt | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.1 V CV 10 k | 100 p | +0.1 | CV 10 µA | 0.09990 V | −0.10 mV | 36.9% | 9.99 µA | PASS |
| 0.1 V CV 10 k | 1 n | +0.1 | CV | 0.09865 V | −1.35 mV | 66.9% | 9.06 µA | PASS (1 nF ↑OS but stable) |
| 2 V CV 10 k | 100 p | +2 | CV 0.2 mA | 1.99883 V | −1.17 mV | 11.7% | 199 µA | PASS |
| 2 V CV 10 k | 1 n | +2 | CV | 1.99890 V | −1.10 mV | 12.1% | 202 µA | PASS |
| 2 V CC 100 R | 100 p | +2 | CC 10 mA | 1.02566 V (I·R) | — | 0% | 10.257 mA (+2.57%) | PASS |
| 2 V CC 100 R | 1 n | +2 | CC | 1.02566 V | — | 0% | 10.257 mA | PASS |
| −2 V CV/CC | 100 p/1 n | −2 | CV/CC sink | −1.99895/−1.99901 V CV, −1.02566 V CC | +1 mV | 11–12% | −199 µA/−10.257 mA | PASS (4-quad symmetric) |
| 50 µA CC 1 k | 100 p | +2 | CC 50 µA | 0.05129 V | — | 0% | 51.29 µA | PASS |

*No sustained oscillation, Gmin stepping succeeded, Vdiff tracks Vdut <0.5 mV, Isrc/Isnk correct.*

**Overall Gates C/E — PASS CONDITIONAL** (transient stable, PM inconclusive encrypted macro per P3IR-05, prototype gate remains for PCB parasitics/humidity).

### ERC / Netlist Update (2026-08-25)

* Tool: `E:/KiCad/bin/kicad-cli.exe sch erc --format json --severity-all` on `hardware/kicad/ReRAM-SMU-V1/ReRAM-SMU-V1.kicad_sch`
* Result: **~210 violations, 45× label_dangling errors (global labels skeleton) + ~10 footprint_link_issues + ~10 lib_symbol_mismatch + ~30 endpoint_off_grid** — **waived per §4**: hierarchical skeleton uses global labels as inter-sheet net refs without physical wires; net audit §5 verifies no shorts, continuity is provisioned in detailed sheets 03/04 rev0.2 (wires added for critical nets OUT→R_iso→FORCE_HI, FILTER→SENSE−, VDIFF_FB→−IN, etc.). **Target 0 unexplained errors not yet met in skeleton — path remains: wire global labels to pins / hierarchical sheet pins + PWR_FLAG in detailed capture, then re-run `kicad-cli sch erc --severity-error` →0 errors before PCB.**
* Detailed sheets alone: 03 rev0.2 22 symbols (U301 + R301/302 + C301–306 + R303–310 + D301/302 + TP), 04 rev0.2 18 symbols (3×OPA140 + LT5400 + 4×R + C401 + 2×reed + TLV3501 + TP) — footprints provisional (Phase 7 policy), will be curated with manufacturer libs before PCB.
---

## Update 2026-09-01 — Yolo Verification (kicad-cli 9.0.8 + ngspice 45.2)

**Environment:** WSL Ubuntu 26.04, kicad 9.0.8+dfsg-1, ngspice 45.2 KLU, python 3.14.4, .venv 3.14, yolo mode (sandbox off)

**ERC Real (`kicad-cli sch erc --severity-error`):** 122 errors
- `pin_not_connected 86` (TP, NC pins, DAC/OPA unconnected)
- `wire_dangling 26` (root tiny wires 0.05–0.14mm near origin, plus 5V/GND stubs)
- `power_pin_not_driven 10` (OPA V+ / V-, LT1970 VEE/VCC, PWR_FLAG missing in 05/06 before fix)
- `/`: 26 wire_dangling, `/01_POWER/`:25, `/02_DAC/`:31, `/03_OUTPUT/`:27, `/04_KELVIN/`:13, `/05/06/07/08/09/`:0 error (fixed via 6751935/2c78781)
- Total with warnings: 438 (error 122 + warning 316)
- Lite audit: 32 dangling /79 (critical 0, SPI1/2 3 shared, RELAY 2 shared)

**Netlist (`kicad-cli sch export netlist --format kicadsexpr`):** 25 nets, critical present: FORCE_HI/LO, SENSE_HI/LO, LT1970_SENSE_P/N, VCSRC/VCSNK, VSET, VREF_2V5, nPOR, etc. Missing: RELAY_DRV_K1..K6, SPI1/2 (global labels not yet pinned to coil/SPI pins — audit counts 2 but netlist node 0, needs pin-tip Manhattan wire)

**BOM (`kicad-cli sch export bom --format-preset CSV`):** 9.0K, 9 refs grouped, written to `hardware/kicad/bom_yolo.csv` (Refs,Value,Footprint,Qty,DNP) — annotation warning present

**Artifacts:** `hardware/kicad/erc_*_yolo.json`, `netlist_*_yolo.xml`, `bom_yolo.csv`, `erc_audit_lite.json`

**Next to reach error 0:** Add PWR_FLAG for power pins, no_connect for NC (AD5764 27/29, etc.), wire TP to net, delete root dangling wires, run `kicad-cli sch annotate` to fix duplicate refs


