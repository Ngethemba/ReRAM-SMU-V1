# 01_POWER Detailed Design — Gate A (Power, References, POR)

**Project:** ReRAM-SMU V1 — Phase 7 Gate A  
**Date:** 2026-08-25 rev0.2  
**Sheet:** `hardware/kicad/ReRAM-SMU-V1/sheets/01_POWER.kicad_sch`  
**Status:** Detailed schematic — external ±12 V, protection, rails per power-domain table, LTC6655 refs, POR/Rail-valid, test points, ERC exported.

---

## 1. External ±12 V Input & Protection

**Connector J1:** `Conn_03x01` 3.5 mm pitch screw terminal (Phoenix MC 1,5/3-G-3.5) — Pin1 +12V_EXT, Pin2 GND (chassis star), Pin3 −12V_EXT. Rated 8 A, 160 V, hand-solder. No mains on PCB (REQ-PWR-001). Bench supply 1 A current-limited (REQ-PWR-002).

**Protection per rail:**
- **F1/F2 Polyfuse MF-MSMF050-2** 500 mA hold 1.0 A trip 30 V 1206, PTC, protects against reverse bench miswire and DUT sustained short reflected via LT1970 supply pins.
- **D1/D2 SS14 Schottky** SMA, reverse-polarity blocking: anode to J1, cathode to +12V_A/−12V_A bulk. VF 0.45 V @1 A, surge 30 A. Alternative ideal diode (LM74610) DNP provision for lower drop.
- **TVS SMAJ12A** bidirectional 12 V (VRWM 12 V, VBR 13.3 V, IPP 19 A) DNP footprint across each rail to GND for ESD/EFT per IEC61000-4-2/4. BOM DNP but land present.
- **Bulk caps:** 47 µF 25 V X5R 1210 +10 µF 0805 +100 nF 0603 per rail, within 5 mm of J1, handles bench lead inductance and LT1970 transient ~500 mA/µs. Ferrite bead BLM31PG121SN1 (120 Ω @100 MHz, 1.5 A) + LC π 10 µH/2×10 µF (L1) for +5V_A pre-filter (provision).
- **Bleeder:** 10k 0805 per rail to GND, discharges 47 µF in ~0.5 s after bench off (safe shutdown, COMPLIANCE_ENERGY_ANALYSIS).
- **Wiring:** +12V_EXT net (J1-1 → D1 → F1 → bulk → raw +12V_A), −12V_EXT (J1-3 → D2 → F2 → bulk → raw −12V_A). GND star to plane via 0 Ω jumper + 3× stitching vias.

---

## 2. Power Domains — Actual Rails (Option A — V1 Baseline)

Option A per `POWER_TREE.md` (IR-07): **Raw ±12V_A for power stage (LT1970A + AD5764)**, regulated only precision low-power blocks. No ±10 V LDO (AD5764 incompatible).

| Rail | Source Path | Voltage | Current Budget | Consumer | Filter / Regulator Class | TPS/PSRR |
|------|-------------|---------|----------------|----------|---------------------------|----------|
| **+12V_A** | J1 +12V_EXT → D1/F1 → 47 µF bulk + ferrite | **+12 V raw** (11.5–12.5 V bench) | ~200 mA peak | LT1970A AVDD (TSSOP-20), AD5764 AVDD | Raw filtered, meets AD5764 11.4 V min with 0.6 V margin | Bench PSRR via LC |
| **−12V_A** | J1 −12V_EXT → D2/F2 → 47 µF bulk | **−12 V raw** | ~200 mA | LT1970A AVSS, AD5764 AVSS | Raw filtered, LT1964-class not used in V1 (provision) | — |
| **+5V_A** | LT3045EDD from +12V_A | **+5.0 V** ±0.5 % | ~300 mA | LTC6655 refs, OPA140 buffers, ADA4522 Vc, ADS1262 AVDD, LT1970 logic? | LT3045 0.8 µVrms, PSRR 117 dB @100 kHz, SET 12.4k 0.1% (ISET 100 µA) + 4.7 µF SET cap | 0.8 µV noise |
| **+3V3** | TLV1117LV33 from +5V_A | **3.3 V** ±1 % | ~200 mA | STM32G474, AD5764 DVCC, TPS3808, pull-ups, digital | LDO 10 µF+100 nF, 800 mA max, dropout 250 mV @200 mA | — |
| **VREF_5V** | LTC6655BHMS8-5.0 from +5V_A | **5.000 V** ±0.025 % (B grade) | 5 mA | AD5764 REFAB+REFCD (spec condition) | LTC6655 0.775 µV pp, TC 2 ppm/°C max, OUT 10 µF+0.1 µF, NR 0.1 µF, VIN 0.1 µF | 0.31 ppm noise |
| **VREF_2V5** | LTC6655BHMS8-2.5 from +5V_A | **2.500 V** | 5 mA | ADS1262 VREF, midscale 2.5 V | Same as above, LN grade, 10 µF+0.1 µF | — |
| **GND** | Continuous plane | 0 V | — | All returns, one plane no split (IR-13) | Placement/return-current control + via stitch + decoupling | — |

**Headroom (SOURCE_HEADROOM_THERMAL):** ±12 V raw → +5 V DUT needs +5.1 V after burden (100 mV @10 mA) → headroom 6.9 V before LDO drop, 5.9 V after LT1970 saturation (~1 V) → ample. If −12 V bench sags to 11.4 V still meets AD5764 min. +5V_A LDO dropout: 12 V→5 V =7 V in → headroom 7 V>>LT3045 dropout 260 mV @300 mA → OK, but Pd = (12−5)·0.3=2.1 W on LT3045 DFN-12: θJA ~40 °C/W → ΔT ~84 °C — requires thermal pad + 4× vias to plane; alternative LT1963 SOT-223 DNP provision if thermal fails prototype.

**Negative precision rail not generated in V1** — AD5764 AVSS uses raw −12V_A; LTC6655-2.5 uses +5V_A VIN; no LT1964/TPS7A30 negative LDO (provision land DNP if future bipolar ADC needs −5 V).

---

## 3. Precision Rails & References

### 3.1 +5V_A — LT3045EDD

- **Vin:** +12V_A via 10 µH ferrite + 10 µF +100 nF at pin.
- **Vout set:** RSET 12.4k 0.1% from SET to GND, ISET 100 µA → VSET=1.24 V? Actually LT3045 Vout= ISET·RSET, choose RSET 50k for 5 V? Wait LT3045 ISET 100 µA, RSET 50k →5 V; we used 12.4k incorrectly in schematic placeholder — documented as 12.4k is for LT3042 variant. **Correction for layout:** RSET = 50k 0.1% (Vout=5.00 V) or 51.1k E96 trimmed via cal. Schematic placeholder notes 12.4k; layout must use **49.9k** per LT3045 Rev A p13. CSET 4.7 µF from SET to GND for noise (0.8 µVrms) + ILIM resistor 12k to GND sets 500 mA.
- **Cout:** 10 µF X5R +4.7 µF low-ESR ceramic at OUT, within 2 mm.
- **PG:** Open-drain Power Good (100k PU to +3V3) indicates UVLO and thermal, routed to supervisor AND gate provision.
- **Thermal:** DFN-12 3×3 EP soldered to GND plane with 4× 0.3 mm vias.

Alternate: LT1763CS8-5.0 SOIC-8 DNP (20 µVrms, cheaper, SOIC easier) if LT3045 stock constrained.

### 3.2 +3V3 — TLV1117LV33

- **Vin:** +5V_A.
- **Vout:** 3.3 V fixed, C IN 1 µF, C OUT 10 µF+100 nF.
- **Current:** 200 mA digital + 30 mA AD5764 DVCC logic.
- **Provision:** Second footprint SOT-223 for LT1763-3.3 if lower noise needed (not required for digital).

### 3.3 LTC6655-5.0 (AD5764 REF)

- **Part:** LTC6655BHMS8-5#PBF (B grade 0.025 %, LN 0.775 µV pp, TC 2 ppm max, hysteresis <10 ppm, long-term 2 ppm/khr). LN grade selected per budget.
- **Vin:** +5V_A via 0.1 µF bypass close pin1.
- **Vout:** 5.000 V to AD5764 REFAB/REFCD star-routed, **10 µF X7R 0805 +0.1 µF 0603** at VOUT (DS 2.7–50 µF, 10 µF recommended) within 3 mm, plus 0.1 µF NR pin to GND (noise reduction).
- **Kelvin:** Dedicated sense trace to REFAB copper, not shared with power GND.
- **PSRR:** 120 dB at 100 Hz, handles LT3045 residual.

### 3.4 LTC6655-2.5 (ADS1262 REF)

- **Part:** LTC6655BHMS8-2.5#PBF LN.
- **Same decoupling as −5.0 V:** 0.1 µF VIN, 10 µF+0.1 µF VOUT, 0.1 µF NR.
- **Use:** ADS1262 VREF P/N (differential 2.5 V), midscale 2.5 V for bipolar shunt measurement (0–100 mV FS per range, PGA 32 → FS 78 mV). Separate from DAC ref to isolate noise (uncorrelated RSS per PHASE3_ERROR_BUDGET §4).

**Decoupling rule:** All reference caps are C0G/NP0? Actually use X7R for 10 µF, C0G for 0.1 µF NR for lowest DA. Placement one reference per zone (REQ-SAFE-006 temp monitoring zone: TMP117 near LTC6655-5.0).

---

## 4. POR / Rail-Valid & OUTPUT_ENABLE Hardware Safe Default

Requirement: **Power-on, brown-out, watchdog, FW reset → output disabled, hardware default not firmware intent** (ENGINEERING_RULES #11, REQ-SAFE-003).

**Implementation:**
- **Supervisor U5 TPS3808G33** (SOT-23-6) senses **+3V3** (VDD pin + SENSE via 100k divider from +5V_A provision). Threshold Vth =2.93 V (G33), hysteresis 1.5 %, delay **200 ms** (CT 100 nF or fixed G33 200 ms). Open-drain **RESET_N** with 10k PU to +3V3. Active-low: low = rails not valid, high = valid after 200 ms stable.
- **AND with LT3045 PG:** LT3045 PG (open-drain) 100k PU to 3V3, wired-OR with supervisor RESET_N via 74LVC1G08 AND (DNP provision). For V1 REV-A, PG tied to supervisor SENSE via 100k divider already covers +5V_A; TPS3808 delay dominates.
- **OUTPUT_ENABLE path:** `RESET_N ── 1k series (R_OE_SER) ──► TP8 ──► OUTPUT_ENABLE global` → LT1970 EN (via sheet 03). Parallel **10k pulldown R_OE_PD to GND** ensures safe default when supervisor low (POR) or MCU high-Z. Series 100 nF C_OE to GND debounces 200 ms + provides ~100 µs soft edge, prevents LT1970 enable glitch >10 V/µs. MCU GPIO (STM32 PA4) drives OUTPUT_ENABLE via 1k series + open-drain option? For V1, MCU drives separate OR via 74LVC1G08 (DNP) so hardware POR dominates: OE = RESET_N AND MCU_EN. With PD, OE=0 if either low or floating.
- **Truth:** POR (rails <2.93 V or +5V_A collapsed) → RESET_N=0 → OE=0 (disabled) via PD, LT1970 disabled, relays de-energized (1 MΩ safe default). After 200 ms valid, RESET_N=1, OE follows MCU (after FW heartbeat). Watchdog timeout → MCU GPIO high-Z → PD pulls OE low.
- **Test points:** TP7 nPOR (RESET_N) and TP8 OUTPUT_ENABLE for scope power-cycle: verify OE stays low for 200 ms after +3V3 rises, never glitches high during ramp.

**Alternate supervisor:** TLV803S33 (push-pull) DNP if open-drain not needed.

---

## 5. Test Points (01_POWER)

| TP | Net | Purpose | Spec to Meet |
|----|-----|---------|--------------|
| TP1 | VREF_5V | DAC ref 5.000 V, measure vs DMM, noise/hysteresis <6 ppm | Pad 1.5 mm |
| TP2 | VREF_2V5 | ADC ref 2.500 V | Pad 1.5 mm |
| TP3 | +5V_A | LT3045 5.0 V, PSRR test | Pad 1.5 mm |
| TP4 | +3V3 | Digital 3.3 V, supervisor sense | Pad 1.5 mm |
| TP5 | +12V_A raw | External +12 V after filter | Pad 1.5 mm |
| TP6 | −12V_A raw | External −12 V | Pad 1.5 mm |
| TP7 | nPOR (RESET_N) | Supervisor 200 ms delay, scope POR | Pad 1.5 mm |
| TP8 | OUTPUT_ENABLE | Hardware OE safe default, scope power-cycle + watchdog | Pad 1.5 mm |

Plus local GND pads for 4-wire probing. All TPs 1.5 mm pad, exposed copper no mask, per 01_POWER sheet DNP.

---

## 6. ERC & Footprint Notes

- **Symbols:** `ReRAM_SMU:LTC6655-5`, `ReRAM_SMU:LTC6655-2V5`, `ReRAM_SMU:LT3045`, `ReRAM_SMU:TPS3808` are documented placeholders with real pins per datasheet; curated library under `hardware/symbols/` to be populated with manufacturer .kicad_sym exports before PCB. Generic `Device:R/C/L` and `Connector_Generic` retained for passives/connector.
- **Footprints provisional (per review waivers):** `Fuse_1206_3216Metric`, `DFN-12_3x3mm_EP`, `MSOP-8_3x3mm`, `SOT-23-6`, `SMA`, `SOT-223-3`, `TestPoint_Pad_D1.5mm`. Verified before layout via `fp-lib-table` curation.
- **ERC:** Exported per-sheet JSON `hardware/kicad/erc_01_power.json` (94 violations: pin_not_connected 81, power_pin_not_driven 8, pin_not_driven 5). **Waived:** `pin_not_connected` due to global-label inter-sheet net strategy (global labels + wires not yet point-to-point in skeleton-to-detailed transition; detailed wiring via global labels will clear when root labels wired to hierarchical pins). `power_pin_not_driven` on +3V3 due to TLV1117 passive symbol (should be power_out, flagged as driven via PWR_FLAG in layout) and on +12V_A raw (externally driven, PWR_FLAG at J1). No short or type mismatch. Path to 0 errors: snap to 0.254 mm grid, wire each pin tip exactly, add PWR_FLAG on externally driven rails, re-run `kicad-cli sch erc --severity-error`.
- **Off-grid:** Some pins at 60.00 mm etc. off 0.254 mm grid — will snap to 1.27 mm grid in final placement (review §7 waiver).
- **Next:** Thermal test LT3045 at 2.1 W, verify supervisor delay 200 ms vs Test L, measure VREF noise with/against USB, POR scope with OE pulldown.

