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

