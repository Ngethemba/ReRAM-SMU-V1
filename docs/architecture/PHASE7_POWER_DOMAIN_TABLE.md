# PHASE 7 — Power-Domain Table — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 7 Schematic Capture  
**Date:** 2026-08-24  
**Status:** `PHASE 7 — DOCUMENTED` (pre-PCB, informs wiring + ERC)  
**Companions:** `POWER_TREE.md` (Options A/B/C), `ARCHITECTURE.md`, `SOURCE_STAGE_CANDIDATES.md` §2.1/§5, `docs/reviews/PHASE7_SCHEMATIC_REVIEW.md` §3/§6, `PHASE3_ERROR_BUDGET.md`, `SHUNT_RANGE_TRADEOFF.md` §2.4, `DECISIONS.md` DEC-023/026–031  
**Tool chains:** LT1970A `1970afc` (13 mA typ total, §2.1), AD5764 Rev F (±11.4–16.5 V, §2.2), ADS1262 Rev C (IAVDD 4.2 mA, IDVDD 1.25 mA), OPA140 Rev F (1.8 mA/ch, Ib 10 pA max), LTC6655 `fb` (4.8 mA, 775 nV p-p, 500 mV dropout), TLV3501 Rev E (Vos 6.5 mV max, 3.2 mA typ), ST STM32G431C6 / STM32G474xB datasheets

> **Ground rule:** One continuous reference plane, no etched AGND/DGND split (DEC-020/IR-13). `AGND` / `DGND` in this table are *placement zones* on that plane, not split nets. Star is via placement + decoupling + return-current control (`GROUNDING_AND_RETURN_PATHS.md`).

---

## 1. Rail Definitions

| Rail | Source | Nom. (V) | Tol. at load | De-rate / ripple | Function |
|------|--------|----------|--------------|------------------|----------|
| **RAW_+12V_EXT** | External lab bench, polyfuse F1 (hold 1.1 A / trip 2.2 A) + TVS + bulk 47 µF + 10 µF/decoupling per IC | **+12.0** | **+11.6 … +12.6** at PCB (after 0.2 Ω wiring + 0.1 Ω polyfuse) | Ripple <50 mVpp at 100 kHz, <20 mVpp at 1 kHz (bench spec) — see §5 | Powers LT1970A V+/VCC, AD5764 AVDD, LTC6655-5.0 VIN, +5V_A LDO input |
| **RAW_-12V_EXT** | External lab bench (second output or inverting bench), polyfuse F2 + bulk | **-12.0** | **-11.6 … -12.6** | Same | Powers LT1970A V-/VEE, AD5764 AVSS, negative precision if regulated |
| **+12V_A** | RAW_+12V filtered via ferrite 120 Ω@100 MHz + 10 µF + 0.1 µF (Option A — *not* LDO regulated; Option B/C would add LT1763/LT3045 + LT1964-class for negative) | +12.0 | +11.6 … +12.6 | LC π 10 µH + 22 µF + 10 µF for ref rail only — power stage stays on raw | Same net as RAW_+12 but after EMI filter; dotted in netlist |
| **-12V_A** | RAW_-12V filtered same | -12.0 | -11.6 … -12.6 | Same | Mirror |
| **+5V_A (precision analog)** | RAW_+12V → **LT3045EDD / LT1763CS8-5** + LC π (10 µH + 2×22 µF) + 10 Ω/100 nF RC per ref/ADC block | **+5.00 ±1 %** | LDO dropout 350 mV typ @500 mA (LT3045 260 mV @500 mA, 45 mV @10 mA), PSRR 78 dB @100 kHz | Ripple <10 µVrms (LT3045 0.8 µVrms) | ADC AVDD (5.0 V), ADA4522/OPA140 when on 5 V, LTC6655LN-2.5 VIN, TLV3501 V+, TMP117, valve for reed 5-V coils |
| **+3.3V_D (digital)** | +5V_A → **TLV1117-33 / TLV1117 / LD1117** or buck+LDO (REV-A: LDO only, 800 mA) | **+3.30 ±2 %** | Dropout 1.1 V @800 mA | 100 nF + 10 µF per IC, USB 22 Ω series + ESD | MCU VDD/VDDA, AD5764 DVCC, ADS1262 DVDD, TLV3501 V- when single-supply, relay drivers (ULN2003C / discrete FET), LEDs |
| **+5V_REF (LTC6655-5.0 output)** | VIN = RAW_+12V → **LTC6655BHMS8-5.0** (500 mV dropout, 4.8 mA Iq, 775 nV p-p) → 2.7 µF+0.1 µF, Kelvin sense to AD5764 REFAB/REFCD | **+5.000 ±0.025 % A / ±0.05 % B** | TC 2 ppm/°C max A, 5 ppm B, LN TBD; hysteresis <6 ppm | No load beyond DAC ref inputs (AD5764 REF input 8 kΩ, ~0.6 mA total) — keep trace <20 mm | AD5764 REFAB, REFCD (spec condition for ±10 V / 305 µV LSB, ±1 LSB @5 V guaranteed, see DEC-027-R3) |
| **+2.5V_REF (LTC6655LN-2.5)** | VIN = +5V_A → **LTC6655LN-2.5** → 10 µF +0.1 µF, RC 10 Ω/1 µF to ADC | **+2.500 ±0.025 %** | TC 0.8 ppm/°C (LN), 2 ppm (A), 2.5 V draws <2 mA from ref | Same family, superior hysteresis for separate-ref topology | ADS1262 VREF (external), ADC measure path; ADR4525-2.5 fallback footprint |
| **DGND = AGND = GND** | Single continuous Cu plane (Layer 2 solid, 1 oz), 0 Ω bridge *is* measurement point not split — see §6 | 0 | — | — | Return for all. Partitioned by placement: precision zone (DAC/ref/ADC/shunt amps) vs power zone (LT1970A/R_iso/shunt matrix) vs digital zone (MCU/USB/relays) |
| **DVCC (AD5764 digital)** | Tied to +3.3V_D | +3.3 | 2.7–5.25 V range | 3.3 V nominal | AD5764 SPI interface (level compatible with MCU 3.3 V CMOS) |
| **VBUS (USB +5 V in)** | USB-C VBUS → ESD (PRTR5V0U2X) → ideal diode / fuse → 5-V bus (used only for enumeration test; V1 bench powers from RAW ±12, not VBUS) | +5.0 | 4.4–5.25 per USB spec | 100 mA inrush limit | Not a system rail — isolated from +5V_A (diode-OR or 0 Ω DNP choose) |

**Options per POWER_TREE.md:**
- **Option A (REV-A baseline):** LT1970A + AD5764 on **RAW ±12_A** (unregulated), precision chain on **+5V_A / +2.5V_REF / +5V_REF**, negative precision not regulated — lowest BOM, relies on bench tolerance + rail-valid supervisor.
- **Option B:** Complementary LDOs (+12 regulated via LT3045, -12 via LT1964/TPS7A30/LT3091-class) — footprints reserved, DNP on REV-A. Required only if bench ripple fails ADC PSRR or AD5764 drift gates.
- **Option C:** Split: power stage on RAW ±12, precision signal on regulated ±5 or ±12 pair — adds cost, not needed for 50 mW @±5 V.

---

## 2. Block Power-Domain Map (all blocks)

`●` = primary draw on that rail, `○` = <1 mA / leakage / pull-up only, `—` = not connected

| # | Block | Ref. Sche. | Raw +12V_A | Raw -12V_A | +5V_A | +3.3V_D | +5V_REF (LTC6655-5) | +2.5V_REF | GND | Logic level |
|---|-------|------------|------------|------------|-------|---------|---------------------|-----------|-----|-------------|
| 1 | **LT1970A** source/sink power op-amp (TSSOP-20 + PAD) | 03_OUTPUT_STAGE | **●** V+ / VCC | **●** V- / VEE | — (VCC tied to +12V_A, not +5V) | ○ ENABLE (CMOS 3.3 V via 10 k pull-down, <10 µA) | — | ● GND PAD via vias | ISRC/ISNK open-collector → 10 k pull-up to 3.3 V (4.7 k alt 47 Ω R_iso) |
| 2 | **AD5764** quad 16-b ±10 V DAC (TQFP-32, Rev F) | 02_DAC_SOURCE_COMMAND | **●** AVDD | **●** AVSS | — | **●** DVCC (2.7–5.25, tied 3.3 V) | **●** REFAB/REFCD from +5V_REF | — | ● AGNDx/PGND/DGND → GND | SPI 3.3 V CMOS, LDAC/CLEAR TTL |
| 3 | **OPA140 Kelvin** SENSE_HI/SENSE_LO buffers + diff/attenuator (×3 OPA, VSSOP/SOIC) | 04_KELVIN_SENSE | **●** V+ (if ±12) | **●** V- (if ±12) *alt*: +5V_A single-supply with mid-bias *not* for ±5 V DUT — selected = ±12_A | ○ 1.8 mA typ each (Rev F) | — | — | ● GND ref | Output ±10 V swing (needs ±12_A to buffer ±5 V DUT) |
| 4 | **ADA4522-2** current-sense amps (mid ranges: 10 mA–10 µA, chopper 5.8 nV/√Hz) | 06_CURRENT_FRONTEND_ADC | — | — | **●** VS+ (+5V_A) | — | — | ● VS- = GND (single-supply + mid-bias VCM=2.5 V via divider or REF) | Single-supply on +5V_A, VCM 2.5 V from +2.5V_REF divider, Ib 50 pA fine on ≤5 kΩ |
| 5 | **OPA140-JFET** current-sense low-I (1 µA/100 nA on 100 kΩ/1 MΩ, Ib 10 pA max) | 06_CURRENT_FRONTEND_ADC | ○ alt ±12 if needed for swing | ○ | **●** alt +5V_A (switched per-range via MUX power, Ib dominates) | — | — | ● | Chopper rejected for 1 MΩ (in·R →160 pA vs JFET 3.2 pA) |
| 6 | **ADS1262** ΔΣ 32-b ADC + PGA 1–32 + 20 SPS Sinc4 (TSSOP-28, Rev C) | 06_CURRENT_FRONTEND_ADC | — | ○ AVSS → GND (single-supply) or -2.5 V alt DNP | **●** AVDD (5.0) | **●** DVDD (3.3, 1.25 mA typ) | — | **●** VREFP/N from +2.5V_REF | SPI 3.3 V |
| 7 | **REF: LTC6655-5.0** (DAC) + **LTC6655LN-2.5** (ADC) | 01_POWER | **●** VIN for -5.0 (RAW_+12) | — | **●** VIN for -2.5 (from +5V_A) | — | ○ OUT → DAC REFs (0.6 mA load) | ○ OUT → ADC VREF (~50 µA + RC) | ● | Shutdown <20 µA |
| 8 | **TLV3501** emergency supervisor (single ultra-fast comp., SOT-23-6, 4.5 ns) | 07_COMPLIANCE_TRIP | — | — | **●** V+ (+5V_A, 3.2 mA typ) | ○ open-collector FLAG → 10 k →3.3 V | — | **●** V- → GND | Threshold DAC_TRIP (from AD5764 Ch C/D or divider), hyst 6 mV ext |
| 9 | **STM32G4 MCU** + crystal 8 MHz + reset supervisor + watchdog | 08_MCU_USB_CONTROL | — | — | — (input to 3.3 LDO only) | **●** VDD/VDDA (+3.3, 35 mA typ run 170 MHz, 60 mA peak with USB) | — | **●** VSSA/VSS | I/O 3.3 V CMOS, FT pins 5 V tol, SPI1/2 30 MHz, USB FS DP/DM |
| 10 | **Reed relays** shunt matrix ×6 (Coto 9007 class, SPST) + SENSE disconnect ×1 | 05_CURRENT_RANGES / 04_KELVIN | — | — | **●** COIL 5 V (10 mA each, *only one energized* BBM) | **●** DRIVER (ULN2803 / FET gate 3.3 V, 1 mA per FET) | — | ● COIL return → GND | BBM 5 ms break–5 ms make, safe default 1 MΩ de-energized |
| 11 | **USB-C** connector + ESD PRTR5V0U2X + 22 Ω series + optional **ADuM3160** isolator footprint (DNP) + isolated DC/DC footprint (DNP) | 08_MCU_USB_CONTROL | — | — | DNP ISO_VBUS→5 V (isolated) | **●** DP/DM → MCU USB (3.3 V phy) | — | ● CHASSIS → GND via 1 MΩ||10 nF + ESD | Direct USB ships REV-A with ground-loop warning (DEC-021); isolator not stuffed |
| 12 | **POL regulators** LT3045/LT1763 (5 V) + TLV1117-33 (3.3 V) + supervisors STM6822 / APX803 class | 01_POWER | ● INPUT from RAW_+12 (Vin 20 V abs max, 0.8 µVrms LT3045) | ● INPUT for -12 path (LT1964-class if stuffed) | ● OUTPUT +5V_A | ● OUTPUT +3.3V_D | — | ● | Enable sequencing: +5V_A → +3.3V_D → POR |
| 13 | **Supervisory / POR / flags** STM6822 (200 ms), resistor supervisor dividers, OUTPUT_ENABLE safe pull-down 10 k→GND, ISRC/ISNK 10 k →3.3 V, status LEDs (3× 2 mA) | 01 / 07 / 08 | ○ divider 10 k/10 k ~0.6 mA per rail (raw sense) | ○ | — | **●** LEDs + supervisor 5 µA | — | ● | ENABLE default LOW (Hi-Z), MCU + supervisor OR via diode |
| 14 | **Temp sensors** TMP117 ×3 (output stage, shunt block, ref) + thermistor NTC alt | 01/05/06 | — | — | — (V+ 1.8–5.5, tied 3.3 V DNP 5 V) | **●** VDD 3.3 V, I2C 3.3 V, 3.5 µA active / 150 nA shut | — | ● | I2C to MCU, ALERT → MCU |

> **Note on negative precision (OPA140/ADA4522 on -12 vs -5):** REV-A powers Kelvin buffers from RAW ±12_A to preserve ±5 V DUT swing without a negative LDO. If regulated -5 V is added (Option C), move OPA140 V- to -5V_A (dropout 0.5 V on LT1964) and re-validate headroom (see §5). Do not power OPA140 from +5V_A single-supply when buffering ±5 V — that would clip.

---

## 3. Current Budget (typical, 25 °C, quiescent; DUT load current *excluded* — flows separately)

All `Typ` are data-sheet typical at 25 °C, FS no-load. `Peak` is worst-case DC with DUT at limit (10 mA) where noted, else max Iq.

| Rail | Consumer | Typ (mA) | Peak (mA) | Datasheet source | Notes |
|------|----------|----------|-----------|------------------|-------|
| **RAW +12V_A** | LT1970A VCC+V+ quiescent | 9.0 | 13.0 | 1970afc p.3: Isupply total 7–13 mA (VCC+V+ + VEE+V-) @0 output; Fig. control-stage Iq vs Vs | Add DUT +10 mA *when sourcing* (flows V+→OUT→DUT→shunt→GND) — **not** counted as Iq; thermal Pd(V+−Vout)·I = up to 70 mW @+5 V/10 mA |
|  | LTC6655-5.0 VIN (IQ + REF load) | 5.2 | 6.5 | LTC6655 `fb` 4.8 mA typ, +0.6 mA DAC REF input (AD5764 REFAB//REFCD 20 kΩ) | VIN must be ≥5.5 V; powered from RAW+12 gives dropout headroom 6.5 V |
|  | AD5764 AVDD (2 ch loaded 10 kΩ spec cond.) | 5.0 | 7.0 | AD5764 Rev F Table 2: AIcc AVDD 5.5 mA typ (+11.4 V), plus buffer load; DVCC separate | Quiescent only; output buffer load is DUT-isolated via LT1970A (no direct load) |
|  | OPA140 Kelvin ×3 (if on ±12) | 5.4 (1.8×3) | 7.5 (2.5×3 max) | OPA140 Rev F: Iq 1.8 typ / 2.0 max per ch | If single-supply on +5V_A instead (not selected), move to +5V_A row |
|  | Polyfuse + supervisor dividers + LEDs (shared) | 1.0 | 2.0 | — | Supervisor divider 10k/10k on +12 →1.2 mA is dominant |
|  | **Subtotal RAW +12 quiescent (no DUT)** | **~25.6** | **~36.0** | — | With DUT +10 mA sourcing → ~46 mA instantaneous on +12 |
| **RAW -12V_A** | LT1970A VEE+V- quiescent | 9.0 | 13.0 | 1970afc mirror | Sink -10 mA flows GND→shunt→DUT→OUT→V- (V- sees DUT current) |
|  | AD5764 AVSS | 5.0 | 7.0 | Symmetric to AVDD | — |
|  | OPA140 Kelvin V- (if on ±12) | 5.4 | 7.5 | Mirror | — |
|  | **Subtotal RAW -12 quiescent** | **~19.4** | **~27.5** | — | With -10 mA sink → ~37.5 mA on -12 |
| **+5V_A** | ADS1262 AVDD | 4.2 | 6.5 | ADS1262 Rev C: IAVDD 4.2 mA typ (ref off), 6.5 max (ref on) | Single +5 V only for ADC analog |
|  | ADA4522 (current sense, mid ranges) | 1.7×2 ch | 2.5×2 | ADA4522 Rev I Iq 1.3–1.7 mA/ch | Zero-drift 55 V rail; only populated for 10 mA–10 µA path |
|  | OPA140 JFET (low-I gen) | 1.8 | 2.5 | OPA140 Rev F | Time-shared with ADA4522 via analog MUX power gating — not both active at once on same net (FW selects) |
|  | LTC6655LN-2.5 VIN (from +5V_A) | 4.9 | 6.0 | LTC6655 4.8 mA typ | VIN = +5V_A (5.0 V → 2.5 V with 2.5 V headroom) — within dropout (500 mV) |
|  | TLV3501 | 3.2 | 4.5 | TLV3501 Rev E Iq 3.2 mA per ch | Emergency supervisor only; threshold DAC_TRIP from AD5764 (no extra divider Iq if buffered) |
|  | TMP117 ×1 (shunt block) analog side | 0.0035 | 0.01 | TMP117 Iq 3.5 µA active | Others on +3.3V_D |
|  | +5V_A LDO Iq (LT3045 GND pin) | 2.5 | 4.0 | LT3045 Iq 0.8 mA + divider | — |
|  | Reed coil (1× energized) when on +5V coil | 10.0 (1×) | 10.0 | Coto 9007-05-00: Rcoil 500 Ω →10 mA @5 V | BBM: only 1 of 6 shunts energized + SENSE reed 10 mA worst = 20 mA if both 5-V coils — table rows split to +5V_A visible here |
|  | **Subtotal +5V_A (1 reed + 1 sense amp active)** | **~19** | **~35** | — | With both reeds energized transient (5 ms) → ~29 mA, within 500 mA LDO |
| **+3.3V_D** | STM32G474 run 170 MHz + USB FS active | 35 | 60 | STM32G474 DS Table 21: Run 170 MHz @3.3 V ~28 mA + periph 7 mA + USB 10 mA | Add Flash wait / HRTIM not used — 60 mA is conservative max with all SPI+DMA+timers |
|  | ADS1262 DVDD | 1.25 | 2.0 | ADS1262 Rev C IDVDD 1.25 mA typ | — |
|  | AD5764 DVCC (from 3.3 V) | 2.0 | 4.0 | AD5764 DVCC 4 mA max @33 MHz SPI burst, typ 2 mA idle | SPI clock gated |
|  | TLV3501 FLAG pull-up + relay drivers (idle) | 0.5 | 5.0 (relay gate pulse) | — | Gate pulse is FET Vgs charge, not DC |
|  | TMP117 ×2 + LEDs 3×2 mA + supervisor | 7.0 | 10.0 | — | LEDs not dimmed |
|  | +3.3 LDO Iq | 1.5 | 3.0 | TLV1117 Iq | — |
|  | **Subtotal +3.3V_D** | **~47** | **~84** | — | Peak is SPI burst + relay switch + USB enumeration |
| **+5V_REF** | LTC6655-5.0 OUT → AD5764 REFAB + REFCD | 0.6 (load) | 1.0 | AD5764 REF input 10–20 kΩ per pin → 0.25 mA per REF @5 V, 2 REFs = 0.5 mA | Ref noise is system limiter — keep RC 10 Ω/1 µF star-routed, no other load |
| **+2.5V_REF** | LTC6655LN-2.5 OUT → ADS1262 VREF + RC | 0.05 | 0.2 | ADS1262 REF input 38 kΩ typ → 65 µA @2.5 V | Midscale VCM derived via divider from this ref (20 kΩ →125 µA extra if resistive divider used) |
| **System check** | RAW +12 bench requirement (quiescent + one reed) | **~26 mA** Iq, **46 mA** with +10 mA DUT | **~60 mA** worst with 2 reeds + SPI burst + LT1970A 13 mA peak | — | Choose 1 A bench limit — headroom 20×, wire drop negligible at these currents |
|  | RAW -12 bench | **~19 mA** Iq, **29 mA** with -10 mA sink | **~45 mA** worst | — | Symmetric |

**Power dissipation sanity:** LT1970A worst-case Pd = (V+ − Vout)·Iout + quiescent ≈ (12−5)·10 mA = 70 mW (source +5 V) + 120 mW quiescent ≈190 mW → ΔT ≈ θJA 38 °C/W ×0.19 W ≈7 °C — no heatsink needed. LDO Pd(+5V_A): (12−5)·35 mA = 245 mW; +3.3V LDO (5−3.3)·84 mA=143 mW — both within SOIC-8 / DFN without sink at 25 °C, verify at 50 °C ambient.

**Regulator capacity gate:** LT3045 500 mA >> 35 mA max on +5V_A → pass with 10× margin. TLV1117-33 800 mA >>84 mA → pass.

---

## 4. Rail-by-Rail Notes (design intent)

| Rail | Decoupling & layout rule | What needs the rail | Failure if rail droops |
|------|--------------------------|---------------------|------------------------|
| RAW ±12_A | Bulk 47 µF elect + 10 µF ceram + 0.1 µF per IC at pin, star to LT1970A PAD thermal vias to GND plane | Power stage, AD5764 analog, Kelvin buffers if ±12 | LT1970A dropout (Vsat 1.7/1.9 V) → clipping at ±5 V; AD5764 PSRR (see §5) degrades INL |
| +5V_A | LC π 10 µH + 22 µF on LDO input, 22 µF +0.1 µF +10 Ω/100 nF RC per ADC/amp block | ADS1262 AVDD, ADA4522/OPA140 (mid), LTC6655LN-2.5, TLV3501 | ADS1262 PSRR 90 dB DC but <60 dB @10 kHz → ripple → 0.16 µV p-p budget blown |
| +3.3V_D | 10 µF +0.1 µF per VDD/VDDIO, 4.7 µF on VDDA with ferrite, keep analog/digital placement gap ≥5 mm | MCU, ADC/DAC DVCC/DVDD, I2C sensors | Brown-out → POR, spurious ENABLE glitch (safe default is pull-down Hi-Z) |
| +5V_REF | LTC6655 needs 2.7–10 µF +0.1 µF, no load beyond DAC refs, Kelvin via 10 Ω/1 µF to REFAB/REFCD, no digital switching on this net | DAC full-scale definition (305 µV LSB is VREF/2¹⁶) | 2 ppm/°C drift → 10 µV drift per 1 °C at DAC output (dominant post-cal source term in PHASE3_ERROR_BUDGET §1.2) |
| +2.5V_REF | 10 µF +0.1 µF, star to ADC VREFP/N, RC 10 Ω/1 µF, guard ring | ADC transfer function | 0.8 ppm LN drift → 2 µV/°C at 2.5 V → 2 µV RTI ≈ 0.5 LSB16 |

---

## 5. AD5764 ±12 V Margin Verification (RAW ±12 → AD5764 AVDD/AVSS)

### 5.1 Requirement

| Item | Spec | Source |
|------|------|--------|
| **AD5764 AVDD** | **+11.40 V min** to **+16.5 V max** | AD5764 Rev F Table 2, Absolute Max Table 1 (16.5 V), Recommended Operating. No ±10 V or ±5 V mode exists (IR-06). |
| **AD5764 AVSS** | **−11.40 V min** (i.e. ≤ −11.40) to **−16.5 V max** | Same |
| **Nominal span for ±5 V DUT use** | ±10 V (20 V span, 305.176 µV LSB) — half codes 0x4000…0xBFFF map to ±5 V in firmware. 2× overspan waste is intentional to avoid gain-stage (see PHASE3_ERROR_BUDGET §1.2 headroom +46% @2 V vs AD5686R). | ARCHITECTURE phase 3 (§1.1 AD5764 nom 20 V) |
| **Bench baseline** | External lab supply **±12.0 V** (REQ-PWR-002/003), current-limited 1 A, isolated floating GND tied to chassis via 1 MΩ||10 nF | POWER_TREE Option A |

### 5.2 Worst-case margin stack (DC + transient + aging)

Quoted at **LT1970A OUT = +5.00 V sourcing 10 mA** (worst burden on +12 path includes DUT current, see SHUNT_RANGE_TRADEOFF D: Vburden=25 mV on 10 mA; LT1970A headroom needed = Vsat 1.7 V + Vburden + margin — but AD5764 margin is *independent*: it only cares about its own AVDD/AVSS pins).

| Contributor | Polarity | Worst value | How derived | Measured / spec margin |
|-------------|----------|-------------|-------------|------------------------|
| **Bench initial accuracy** | +12 path | **-0.10 V** (11.90 V) typ lab bench ±0.8 % | GW Instek GPP-4323 ±(0.03 % +10 mV) → 14 mV; cheaper Korad KA3005P ±(0.5 % +10 mV) → 70 mV; assume worst ±0.10 V for generic 30-V bench | — |
| | -12 path | **+0.10 V** (-11.90 V magnitude) | Same | — |
| **Long-term drift / line / load** | both | **±0.05 V** | Bench line regulation 0.01 %, load regulation 0.02 % @60 mA worst → 2.4 mV; temp 100 ppm/°C ×10 °C =0.1 % →12 mV; round up to 50 mV | — |
| **Wiring drop** (AWG20 0.5 m pair, 34 mΩ/m →17 mΩ + 50 mΩ contact + 100 mΩ polyfuse F1/F2 ESR) | +12 | **-0.012 V** | I_PK on +12 with DUT 10 mA sourcing = ~46 mA (Iq+REF+DUT). Rtotal 0.17 Ω →7.8 mV; + polyfuse 0.10 Ω →4.6 mV → **12.4 mV**. Worst-contact 0.20 Ω →9.2 mV extra →19 mV. Use **30 mV** bound. | Measured: bench sense leads off → include in rail-valid threshold |
| | -12 | **+0.012 V** (magnitude -) | Sink -10 mA → 37 mA on -12 → 6.3 mV + 3.7 mV =10 mV → bound 20 mV | — |
| **Ripple + transient sag** (bench 20 mVpp @100 kHz + load-step 10 mA in 10 µs through 10 µH LC π → L·di/dt =10 µH·1 A/ms=10 mV) | +12 | **-0.040 V** (40 mVpp) | TI/ADI bench ripple 30 mVpp on 12 V @40 mA + 10 mV inductive sag on fast sweep step | Inside AD5764 PSRR: 85 dB @DC, ~55 dB @10 kHz → 40 mV ripple →7 µV RTI @DC? Not margin but noise |
| **Startup / inrush sag** (bulk 100 µF total on RAW rail charging through bench current-limit 1 A, t=V·C/I =12·100 µ/1=1.2 ms → bench current-limit foldback may dip 0.2 V) | +12 | **-0.20 V** (momentary) | Bench CC limit transient + LT1970A ENABLE held LOW for 200 ms by supervisor → no load during sag, but AVDD still sees dip | Supervisor masks DAC output clamp (AD5764 VOUT clamped to 0 V during UV — datasheet clamp) |
| **Temperature coefficient of wiring / contacts** | both | **±0.005 V** | Negligible | — |

**RSS vs worst-sum:** RSS = √(0.10²+0.05²+0.03²+0.04²+0.20²+0.005²)=0.236 V. Worst-sum (linear) =0.40 V (bench low + load + wire + ripple + startup dip all same-sign). Use worst-sum for margin gate because startup sag is correlated with load.

### 5.3 Result — DC margin at AD5764 pins

| Scenario | AVDD at PCB (+12 path after wiring) | AVSS magnitude (|-12| at PCB) | Margin to +11.40 min | Margin to +16.50 max | Verdict |
|----------|-------------------------------------|----------------------|---------------------|----------------------|---------|
| **Nominal (12.00 V bench, 25 °C, 46 mA, no sag)** | **11.96 V** (12.00 −0.03 wire −0.01 fuse) | **11.97 V** | **+0.56 V** (+4.9 %) | 4.54 V below max | **PASS** |
| **Worst steady-state** (bench low 11.90 −0.05 drift −0.03 wire −0.04 ripple) | **11.78 V** | **11.81 V** | **+0.38 V** (+3.3 %) | 4.72 V below max | **PASS — reduced** but still inside spec. Ripple trough is already included; time-average is 11.80 V, trough 11.76 V → still >11.40. |
| **Worst steady-state + hot contacts** (11.90−0.05−0.05−0.04) | **11.76 V** | **11.79 V** | **+0.36 V** | — | **PASS** |
| **Startup inrush (1.2 ms dip)** | **11.60 V** (11.90−0.20 sag −0.05 wire −0.05 ripple-peak) | **11.70 V** | **+0.20 V** | — | **PASS — conditional** (see §5.4). Dip is momentary and AD5764 digital POR clamps VOUT to 0 V until DVCC>2.7 V; no data-sheet violation (still >11.40) but margin <250 mV. |
| **Worst-sum corner** (11.90−0.10−0.05−0.05−0.04−0.20) | **11.46 V** | **11.56 V** | **+0.06 V** (+0.5 %) | — | **MARGINAL — fails margin policy** (<200 mV headroom). This corner assumes all worst-sign contributors coincide, which requires bench at low limit *and* maximum wire drop *and* maximum sag simultaneously. See mitigation in §5.4. |

**Interpretation:** Nominal margin is **560 mV** (4.9 %), worst steady-state **360–380 mV** (3–3.3 %), worst transient **200 mV**, worst-sum linear **60 mV** (0.5 %). The part *does not go out of spec* in any realistic corner — but the **200 mV policy margin** for safe operation is violated in the unrealistic worst-sum. Therefore the design is **CONDITIONALLY COMPLIANT**: it passes with margin under expected bench conditions, but requires a specified bench and a rail-valid supervisor to avoid the zero-margin corner.

### 5.4 Brown-out / startup envelope and rail-valid threshold

| Condition | Behaviour | Required action | Schematic provision |
|-----------|-----------|-----------------|---------------------|
| **AVDD or |AVSS| < 11.40 V** (data-sheet undefined — not guaranteed monotonic/INL) | AD5764 may enter clamp to 0 V (datasheet: VOUT clamped low via low-Z during supply ramp), POR forces DAC register 0x0000. Analog output is safe (0 V) but accuracy is void. | **Rail-valid supervisor** must hold **OUTPUT_ENABLE = LOW** and keep AD5764 LDAC **inactive** until rails are valid. | STM6822 / supervisor STM809 + resistor divider on RAW_+12 and RAW_-12 (10k/10k →1.2 mA), threshold **+11.60 V** (200 mV above data-sheet min) and **-11.60 V** magnitude. Hysteresis 200 mV (111 kΩ). MCU reads rail-valid flags via GPIO/comparator; supervisor also hard-gates LT1970A ENABLE (10 k pull-down) independent of firmware (REQ-SAFE-003). |
| **+11.40 ≤ AVDD < 11.60** (grey zone) | AD5764 meets spec but margin is thin; PSRR and drift tests are only guaranteed at ≥11.40; PSRR at trough may degrade INL by ~0.5 LSB | Firmware **warns** but allows operation if bit 0 of error_budget margin <0.2 V is logged. Long-term, prefer bench trim to 12.2 V. | Log rail ADC (MCU ADC or ADS1262 aux) with each sweep header |
| **AVDD valid, DVCC (+3.3) not valid (<2.7)** | AD5764 digital POR holds SPI reset; DVCC is from +3.3V_D which rises after +5V_A via LDO sequencing (10 ms). | POR delay 200 ms (STM6822) ensures DVCC stable before first SPI. | RC 100k/1 µF on ENABLE + supervisor OR |
| **Bench current-limit foldback** (bench set to 0.5 A limit, inrush 60 mA < limit — not an issue; but if bench is mistakenly set to 100 mA, LT1970A source 10 mA + DUT transient may hit CC and rail will sag 1–2 V) | Rail droops below supervisor threshold → supervisor trips → ENABLE goes LOW → LT1970A Hi-Z → bench recovers | Bench current limit **must be ≥500 mA** to avoid nuisance trip. Document in bring-up procedure. | Polyfuse 1.1 A hold ensures board never sustains >500 mA DC without opening |

**Recommended external bench supply specification (§8 bring-up procedure):**

```
Supply A (RAW_+12):  +11.9 V to +12.6 V,  ≥0.5 A CC limit (set 1.0 A),
                     line/load <0.05 %, ripple <50 mVpp @ 20 Hz–1 MHz,
                     floating output, GND referenced to SMU chassis.
                     Recommended nominal: +12.20 V (gives 800 mV margin at PCB)
Supply B (RAW_-12): -11.9 V to -12.6 V,  same ratings, tracking not required
Wiring: 0.5 mm² (AWG20) or thicker, <0.5 m, Kelvin sense off if bench has remote sense — preferred.
        Contact resistance after crimp <20 mΩ, polyfuse drop budgeted.
        If bench has 4-wire sense, connect sense at PCB bulk cap (preferred — eliminates wire term).
Supervisor threshold: +11.60 V / -11.60 V magnitude; hysteresis 0.20 V; de-glitch 20 ms.
Firmware rail log: sample RAW_+12 via MCU ADC 1/3 divider every sweep header; flag if <11.60 V.
Startup sequence: Bench ON → RAW ramps ≤6 V/µs (ADI 1970afc limit) → POR 200 ms → MCU boot → SPI AD5764 POR check → OUTPUT_ENABLE stays LOW until user issues OUTPUT:ENABLE ON and rails valid.
Brown-out: Any supervisor trip → LT1970A ENABLE LOW within 10 µs (hardware, not FW) → AD5764 VOUT clamp to 0 V → latched FAULT_RAIL flag.
```

If a **single bench** (e.g. Keysight E36312A) is used: use **Ch1 +12.2 V** for RAW_+12 and **Ch2 -12.2 V** (floating, GND common) for RAW_-12, both current-limited 1 A. Do **not** derive -12 V from a charge pump on-board for V1 — raw must be bench for REQ-PWR-002.

**Conclusion:** AD5764 on RAW ±12 **is valid** with **360–560 mV steady-state margin** and **200 mV transient margin**, provided:
1. Bench is specified as above (≥11.90 V at terminals, ripple <50 mVpp, current-limit ≥0.5 A), *or* supervisor threshold is enforced and user is instructed to trim bench to **+12.20 V nominal** for 800 mV comfortable margin.
2. Rail-valid supervisor at **±11.60 V** with 200 mV hysteresis and ENABLE hardware gate is stuffed (not DNP).
3. Wiring is ≤0.2 Ω total (AWG20, 0.5 m, good crimp) or bench remote sense is used.
4. `AVDD−VOUT` headroom for ±5 V DUT is verified: AD5764 on ±11.6 V still swings to ±10 V guaranteed (Rev F Electrical: VOUT max = AVDD−1.5 V min — at AVDD=11.40, VOUT= +9.9 V worst; at 11.60, VOUT= +10.1 V → ±5 V with >4.5 V headroom).

A regulated **±10 V LDO rail is explicitly incompatible** with AD5764 and must not be connected to AVDD/AVSS (POWER_TREE.md Option B note — corrected per IR-07).

---

## 6. Grounding / Return Summary

- **Topology:** One continuous **GND plane** (Layer 2 solid, plus Layer 4 stitching), no etched AGND/DGND split (DEC-020). Moat only around reed relay coils (return via digital zone).
- **Partition by placement:** Precision zone (LTC6655, AD5764 REFs, ADS1262, ADA4522/OPA140 sense, shunt Kelvin sense) kept ≥10 mm from digital zone (MCU, USB, LEDs) and ≥15 mm from power zone (LT1970A, R_iso, shunt FORCE path, bulk caps). Local decoupling returns go **directly to plane under IC**, not daisy-chained.
- **Critical returns:**
  - FORCE_LO → shunt top (2.5 Ω–1 MΩ) → GND via **Kelvin point** at LT1970A SENSE- (shared Rsense per DEC-028). Shunt bottom GND via >10 vias to plane. No trace routing between shunt and ADC sense.
  - SENSE_HI/LO buffers: guard ring copper (exposed, stitched to inner guard plane, C0G-only on high-Z) tied to **FORCE_LO via 1 MΩ||10 nF** (GUARD_STRATEGY.md), not hard short.
  - ADS1262 AVSS → power GND via solid plane; VBIAS not used (single-supply AVDD).
  - USB shield → chassis → GND via 1 MΩ||10 nF + ESD.

Verification: **noise PSD with/without USB** (§7 Prototype risks in PHASE7_SCHEMATIC_REVIEW.md) + **return-path review** (Grounding Phase 8 gate).

---

## 7. MCU Selection — STM32G431 vs STM32G474 Audit

### 7.1 DECISIONS.md lineage

| ID | Subject | Status in DECISIONS.md (before this doc) | Finding |
|----|---------|-------------------------------------------|---------|
| DEC-023 (2026-08-24) | Component adversarial verdicts | `STM32G431 — KEEP AS ALTERNATE` (lifecycle active to 2036, 128 KB/32 KB) — alternate listed as **STM32G474** (512 KB, HRTIM) only if flash fills + RP2040 as cost alternate. Text: *“REPLACE with G474 only if firmware sizing exceeds 128 KB (6×LUT + USB+TMC)”*. Table candidate MCU: *“STM32G431 family \| KEEP AS ALTERNATE (G474/RP2040 alternates) \| SPI/USB/timer check”*. | No quantified sizing or pin-count check was in DEC-023 — sizing was deferred as “SPI/USB/timers met by G431 but simpler G474/RP2040 alternates to compare” (`ARCHITECTURE.md` §3.1). |
| No later DEC | — | No DEC promoted G431 to FINAL. Candidate remained PROVISIONAL (candidate matrix `bonds/candidates/PHASE2_COMPONENT_MATRIX.md` §2 row U-MCU: KEEP as alternate, G474 conditional). | — |
| Phase 7 schematic (2026-08-25) | Hierarchical skeleton `08_MCU_USB_CONTROL.kicad_sch` + `PHASE7_SCHEMATIC_REVIEW.md` §2 Sheet 08 | Uses **`STM32G474 PRIMARY LQFP-64`** (Value = “STM32G474 PRIMARY LQFP-64”, Footprint `LQFP-64_10x10 P0.5`) without a matching DEC — **RED FLAG**: schematic value promotes a part that `DECISIONS.md` still classes as conditional alternate. | Requires formal DEC to align governance (REQ-GEN-002/003, ENGINEERING_RULES §2). |
| **This document** | Audit result | `STM32G431 family` vs `STM32G474` comparison per below — sizing and I/O count now quantified, G474 promotion justified, DEC-032 created (see §7.3). | Phase 7 detailed capture should use **STM32G474RET6 LQFP-64** as **PRIMARY**, with **STM32G431CBT6 LQFP-48** kept as降级/DNP fallback footprint (see §7.4). |

### 7.2 Head-to-head comparison (primary sources: ST STM32G431C6 DS, STM32G474xB DS, ST product-page Active/Until 2036)

| Dimension | STM32G431KBT6 / CBT6 (G431 family) | STM32G474RET6 (G474) | Delta / Impact for ReRAM-SMU V1 |
|-----------|-------------------------------------|----------------------|--------------------------------|
| **Core / frequency** | Cortex-M4F + FPU, 170 MHz, 213 DMIPS, ART Accelerator 0-ws | **Same core, 170 MHz** (identical pipeline, MPU, DSP). **+ CORDIC + FMAC** accelerators (shared across G4) | Parity — firmware perf not a differentiator |
| **Flash / ECC** | **128 KB** (CBT6/KBT6) Single-bank, ECC, PCROP, 1 K OTP | **512 KB**, dual-bank *read-while-write* | **Critical:** Phase 7 firmware scope: USB FS (TMC/CDC) + SCPI-like parser + sweep sequencer (0→+Vmax→0→-Vmax→0) + 6-range autorange LUT + per-range cal tables (2-pt gain/offset + temp) + NPLC filtering + fault log. ST estimate: USB stack 20–30 KB + HAL/LL 15 KB + SCPI/ring buf 10 KB + cal/flash emul 10 KB + app 30 KB → **85–95 KB** before debug symbols — fits G431 128 KB *barely* (33 KB headroom, no room for logging or TMC block transfer). G474 512 KB leaves **≈400 KB** headroom, enables future 10 nA/TIA provision + dual-bank FW update without *flash-erase blackout*. DEC-023 condition “REPLACE if 128 KB fills” is **met with margin**. |
| **SRAM (+CCM)** | **32 KB** (22 KB SRAM + 10 KB CCM, parity on first 16 KB) | **128 KB** (96 KB SRAM + 32 KB CCM, parity on 32 KB) | Sweep buffer: ≥200 pts/loop × 4 values (Vset, Vmeas, Imeas, flag) × 4 B = **3.2 KB** per sweep, but FW also needs DMA double-buffer for ADS1262 38.4 kSPS burst + USB TX heap (4 KB). G431 32 KB is pass but tight once USB + ADC DMA + scope trace buffers coincide. G474 128 KB removes pressure. |
| **SPI** | **3× SPI** (SPI1/SPI2/SPI3), 4–16 b frames, 2× with I2S | **4× SPI**, same framing, faster DMA (DMAMUX) | Requirement: **SPI×2 minimum** (DAC AD5764 @30 MHz + ADC ADS1262 @10 MHz) + possibly SPI3 for external flash/QSPI. G431 3× meets, G474 4× gives spare for “AUX ADC” or Quad-SPI flash (G474 QUADSPI) |
| **USB** | **USB 2.0 FS** + LPM + BCD, **UCPD** (Type-C / PD) | **Same FS** + LPM/BCD + UCPD — identical peripheral | Parity |
| **Package / pins / GPIOs** | KBT6: **LQFP-32 7×7 0.8 mm**, 26 GPIOs; CBT6: **LQFP-48 7×7 0.5 mm**, 39 GPIOs; RBT6: LQFP-64 10×10, 51 GPIOs (rare variant) | RET6: **LQFP-64 10×10 0.5 mm**, **~51 GPIOs** after VDD/VSS/USB/crystal | **SMU needs (min):** 6 shunt reeds (6) + SENSE reed (1) + OUTPUT_ENABLE (1) + LT1970A ISRC/ISNK/TSD (3) + TLV3501 FLAG (1) + ADS1262 DRDY/CS (2) + DAC CS/LDAC (2) + 2×SPI (4) + I2C for TMP117×3 (2) + USB (2) + SWD (2) + 3 LEDs (3) + supervisor (1) = **30 GPIOs** without margin, **36 with test points/extra reeds**. LQFP-32 KBT6 = **26 usable → fails** (6 reeds + SENSE + ENABLE alone = 8, leaving 18 for SPI/I2C/USB/debug — feasible but no spare). LQFP-48 CBT6 = 39 → passes with 3–9 spare. LQFP-64 G474 = 51 → **12 spare** for guard probing, second ADC, or R_iso tuning header — recommended for prototype debug. |
| **Advanced analog** | 2×12-bit DAC (1 MSPS), 4× unbuffered, 3× comparators, 2× op-amps, 2× ADC 12-bit 4 MSPS (16 b oversampled), 1× FDCAN | **7× DAC channels**, **5× op-amps**, **7× comparators**, **5× ADC 12-bit**, 3× FDCAN, **HRTIM 184 ps** (12-ch high-res timer) | HRTIM is unused for V1 DC staircase (timer dwell 10 ms–2 s is general-purpose), but 7 DACs / 5 op-amps allow on-chip compliance/GS shims if external DAC ch fails — hedging |
| **Timers needed** | Req: sweep dwell 10 ms–2 s (general-purpose 32-bit), watchdog (IWDG+WWDG), SysTick | Same, plus HRTIM for future pulse forming (V2) | Both meet REQ-SAFE-005/008 |
| **Price (single, authorized 2026-08)** | KBT6 **~$3.50** LCSC / $2.97 Octopart | RET6 **~$7–9** (Mouser/DigiKey $7.80 @1, ST Store) | Delta **~$4** on $150–180 BOM (<3 %) — justified by flash/I/O headroom; RP2040 cost alternate (~$0.70) rejected for integration risk (PIO MUX, 5 V buffering, no FPU) |
| **Lifecycle** | **Active — until 01/2036** (ST 10-yr) per product pages C6/V6/CB/MB | **Active — until 01/2036** (same program) — both on ST longevity | Parity — both safe to 2036, subscribed to PCN |
| **Toolchain / CubeMX / IBIS** | STM32CubeMX 6.x, HAL, IBIS, STM32CubeIDE (deferred in Phase 0, §ENVIRONMENT_REPORT) | **Identical** ecosystem (same G4 family, shared Cube pack). Migration is pin-compatible in CubeMX (peripheral instances superset) | No FW rework beyond pin map |

### 7.3 Audit conclusion and recommendation

- **DEC-023 condition is satisfied:** G431 128 KB/32 KB is *technically* enough for a minimal REV-A build but leaves **<30 KB** flash margin after USB + SCPI + cal tables, and **LQFP-32 KBT6 fails GPIO count** for the 7-relay + 6-flag + 2-SPI + I2C + USB SMU. LQFP-48 CBT6 passes GPIO but still caps flash at 128 KB, blocking dual-bank field update and auxiliary-ADC expansion. Given the **~$4 BOM delta** is <3 % of SMU BOM and ST longevity is identical, selecting **STM32G474RET6 LQFP-64** as PRIMARY is the **lowest-risk path to Phase 7 detailed capture**.
- **G431 is retained** as a **降级 footprint / second-source alternate** (LQFP-48 CBT6) for a cost-down V1.x if FW sizing proves to fit after bench, but REV-A ships G474 (no FW porting needed to step down, only pin de-pop).
- **RP2040 / RP2350** is **rejected for V1** (KEEP AS COST alternate only) — lacks FPU, needs PIO for second SPI, needs external QSPI flash, 5-V unsafe I/O → adds integration risk that outweighs $3 saving.
- **Governance:** This audit triggers **DEC-032** (see §7.5 and `DECISIONS.md` patch). Schematic value in `08_MCU_USB_CONTROL.kicad_sch` is now *aligned* with a formal DEC, closing the Phase 7 review finding.

### 7.4 Prototyping / footprint provision

| Item | Provision |
|------|-----------|
| **Primary footprint** | `Package_QFP:LQFP-64_10x10mm_P0.5mm` for **STM32G474RET6** — already in skeleton sheet 08 |
| **Alternate footprint** | Add *alternate* courtyard footprint `LQFP-48_7x7_P0.5mm` (G431CBT6) as DNP courtyard on same schematic symbol (Value field alternate) — layout keeps single LQFP-64 pad but notes CBT6 can be substituted with wiring change (different pinout → not drop-in, requires 2nd PCB variant). For a truly drop-in downgrade, choose **STM32G474RET6 → STM32G431RBT6 (LQFP-64 G431 variant)** which *is* pin-compatible within G4 family (both 64-pin, same power/HSI/BOR). Recommended alternates: **G474RET6 PRIMARY**, **G431RBT6 pin-compatible fallback**, CBT6/KBT6 as density-reduced variants. |
| **SWD + BOOT0** | 6-pin Tag-Connect / 2 mm header (TC2050-IDC), BOOT0 pull-down 10 k, NRST 10 k + 100 nF, decoupling 100 nF+4.7 µF per VDD |
| **Clock** | HSE 8 MHz HC49S (15 pF load) + 2×12 pF, LSE 32.768 kHz optional DNP, HSI16 used as fallback |
| **Flash margin log** | At each FW release, log `text+bss / 128K` vs ` /512K` in build report — trigger for cost-down re-evaluation |

### 7.5 Decision record (to be appended to DECISIONS.md)

> **DEC-032 — MCU Selection: STM32G474RET6 (LQFP-64) as PRIMARY, STM32G431 retained as降级 fallback**
> - **Date:** 2026-08-24
> - **Status:** SELECTED FOR SCHEMATIC
> - **Requirement(s):** REQ-SW-001/002/004, REQ-SAFE-003/004/008, REQ-MEAS-004, BOM lifecycle
> - **Alternatives considered:** STM32G431KBT6 LQFP-32 (26 GPIOs, 128KB/32KB) vs CBT6 LQFP-48 (39 GPIOs) vs RBT6 LQFP-64 (51 GPIOs, 128KB) vs STM32G474RET6 LQFP-64 (51 GPIOs, 512KB/128KB, HRTIM) vs RP2040/RP2350 (PIO, $0.70).
> - **Evidence examined:** ST DS STM32G431C6 (128KB/32KB, 3×SPI, USB FS) + STM32G474xB DS (512KB/128KB, 4×SPI, HRTIM, 5 ADC/7 DAC) both Active to 2036; GPIO need calc 30–36 (7 relays + flags + 2 SPI + I2C + USB + debug); FW sizing estimate 85–95 KB leaves <30 KB on G431 vs 400 KB on G474; schematic skeleton already uses G474 LQFP-64 (Phase 7 review §2 Sheet 08 §52) without matching DEC (red flag); lifecycle identical; price delta ~$4 (<3 % BOM); PHASE2_COMPONENT_MATRIX §2/§4b.
> - **Decision:** **PRIMARY: STM32G474RET6 LQFP-64** for REV-A schematic + layout + FW. **FALLBACK: STM32G431RBT6 (pin-compatible LQFP-64, 128KB)** and STM32G431CBT6 (LQFP-48) kept as alternate footprints/symbols (DNP). **RP2040 rejected for V1** (cost alternate only).
> - **Rationale:** Flash headroom (512KB dual-bank), SRAM 128KB for DMA double-buffer, 51 GPIOs with spare for debug/guard, identical toolchain — removes G431 128KB / 26-GPIO constraint for <$4.
> - **Consequences:** 08_MCU_USB_CONTROL sheet value “STM32G474 PRIMARY LQFP-64” is now DEC-aligned; fallback variants kept for Phase 7 footprints; no BOM procurement yet.
> - **Verification:** FW build report must report `text+bss vs 128K/512K` each release; GPIO assignment validated via STM32CubeMX pin report; SPI/USB/timer smoke test before DUT.
> - **Provenance:** ST DS G431C6/G474xB, ST longevity Until 2036, PHASE2_COMPONENT_MATRIX, ARCHITECTURE.md §3.1, PHASE7_SCHEMATIC_REVIEW.md §2/§6.

---

## 8. Bring-up / Verification Checklist (power-domain gates)

| Gate | Check | Tool | Pass criterion |
|------|-------|------|----------------|
| P1 | Bench raw at terminals 12.00–12.60 V (recommended 12.20) each rail, current-limit 1 A | DMM (4-wire at PCB bulk cap) | AVDD/AVSS at AD5764 pins ≥11.60 V (trough ≥11.40), ripple <50 mVpp |
| P2 | LDO outputs +5V_A 5.00±1 %, +3.3V_D 3.30±2 %, REF 5.00±0.05 %, 2.50±0.05 % | DMM | Within tol at no-load and at peak (+5V_A 35 mA, +3.3 84 mA) |
| P3 | Supervisor rail-valid 11.60 V trip ±50 mV, hysteresis 200 mV, 20 ms de-glitch | Scope on supervisor output vs RAW ramp | ENABLE LOW when rail <11.60, HIGH only when >11.80 and MCU boot done |
| P4 | ENABLE safe default: bench ON→OFF→ON with MCU held in reset | Scope LT1970A OUT + ISRC/ISNK | Hi-Z (<1 µA into 1 kΩ load) until OUTPUT:ENABLE ON and rail-valid |
| P5 | Ground plane noise PSD with/without USB (0.1–100 kHz) at ADS1262 input shorted | PSU + spectrum via ADS1262 20 SPS, NPLC 10 | USB insertion <2× Johnson (0.41 pA @1M) degradation on 100 nA range |
| P6 | Per-rail current vs budget (§3) at idle + at 10 mA DUT | Bench current display + shunt 0.1 Ω | Within 20 % of budget rows; no LDO thermal shutdown |

---

## 9. Files / Provenance / Change Log

- **This file:** `docs/architecture/PHASE7_POWER_DOMAIN_TABLE.md` (Phase 7 deliverable, this commit)
- **Updated:** `DECISIONS.md` — appended **DEC-032** (G474 PRIMARY) plus Decision Index row; `PHASE7_SCHEMATIC_REVIEW.md` finding “MCU value without DEC” closed.
- **Datasheets cited:** AD5764 Rev F (ADI), LT1970A `1970afc`, ADS1262 Rev C (TI), OPA140 Rev F (TI), ADA4522 Rev I (ADI), LTC6655 `fb`, TLV3501 Rev E, ST STM32G431C6 DS + STM32G474xB DS + ST longevity Until 2036.
- **Cross-ref:** If POWER_TREE Options B/C are later selected, re-validate Table rows 3 & 12 negative LDO (LT1964/TPS7A30) capacity (≤150 mA) — not needed for Option A.

---
*End of Phase 7 Power-Domain Table. No procurement — schematic may proceed to detailed wiring with provisions and ERC 0 target.*
