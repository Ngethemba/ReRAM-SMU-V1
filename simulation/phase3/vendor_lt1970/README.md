# R5 Vendor LT1970 Bench — README

**Project:** ReRAM-SMU V1 — R5 LT1970A Manufacturer-Model Validation (Closure)
**Date:** 2026-08-24
**Model source:** Analog Devices LTspice 26.0.2.1 official distribution
**Model file:** `C:/Users/azrai/AppData/Local/LTspice/lib/sub/LT1970.sub` (2404 bytes, dated 2026-03-23 19:23, extracted from `C:/Users/azrai/AppData/Local/Programs/ADI/LTspice/lib.zip`)
**Symbol:** `C:/Users/azrai/AppData/Local/LTspice/lib/sym/OpAmps/LT1970.asy` (SpiceOrder 1 Vee,2 V-,3 OUT,4 Sense+,5 Filter,6 Sense-,7 Vcc,8 -IN,9 +IN,12 VCsnk,13 VCsrc,14 COM,15 Enable,16 Isrc,17 Isnk,19 V+)
**Part:** LT1970 (LT1970A model not separately distributed; LTspice lists "LT1970" as the available model for both LT1970/LT1970A per analog.com/tools LTspice page — LT1970A is selected 1% grade, die identical, accuracy difference is test grade)
**Revision:** LTspice models updated Mar 12 2026 (per Download page) — no separate revision file; model is encrypted binary (v6.CR HSPICE encrypted)
**Redistribution:** Vendor model is copyright Analog Devices, encrypted — **not committed** to repo per ENGINEERING_RULES §2.2. Documented how to obtain: install LTspice 26.0.2.1 from https://www.analog.com/ltspice → model auto-installed to `lib/sub/LT1970.sub`; or unzip `lib.zip`.

## Corrected Architecture Under Test (per P3IR-01/02)

```
DAC Vset ──> +IN (LT1970) ──> OUT ──> R_iso (33/47Ω) ──> FORCE_HI ──> DUT (100Ω–1MΩ, C 10pF–1nF) ──> FORCE_LO ──> Rshunt (selected shared 2.5Ω/25Ω/500Ω/5kΩ/100kΩ/1MΩ) ──> GND
                              LT1970 SENSE+ ──> FORCE_LO (Rshunt top, Kelvin)
                              LT1970 SENSE- ──> GND (Rshunt bottom)
                              LT1970 FILTER ──> 220pF to SENSE- (or open, 1nF–100nF range per datasheet 1970afc)
                              Feedback (−IN) ──> DUT SENSE_HI buffered (ideal wire for bench; actual OPA140 >10GΩ, Cin 2–5pF)
```

* Rsense is **shared low-side shunt**, not fixed 10Ω high-side placeholder (P3IR-01 corrected)
* R_iso isolates C_upstream (amp output) from C_downstream (DUT node)
* C_downstream ≤1nF tested (10p–1nF); C_upstream 4.7–10nF not on DUT node, placed before R_iso or as Miller Cc (not ½CV² dump) per P3IR-02
* DUT sense feedback is Kelvin after R_iso (correct topology IR-11)

## Bench Files

| File | Description |
|---|---|
| `R5_bench_2V_1k_100p_Riso47.asc` | First attempt bench (wiring placeholder, now superseded — kept for log) |
| `template.asc` | Copy of ADI example LT1970.asc (gain-of-2 example, R1 1Ω sense, 5Ω load) |
| `R5_vendor_bench_shared_ASC/*.asc` | Vendor benches reusing example topology with corrected values (Rshunt = shared, Riso sweep, Cdut sweep) |
| `LT1970.sub` | **Not committed** — obtain via LTspice installer as above |

All benches use LTspice batch: `"C:/Users/azrai/AppData/Local/Programs/ADI/LTspice/LTspice.exe" -b <file>.asc`

## Limitations of Official Model (per datasheet 1970afc)

* Encrypted Level-1 macromodel: models Aol, GBW 3.6MHz, SR 1.6V/µs, Rout, Vos, Ib, FILTER 1k, Vsense=Vc/10 with 4mV floor, Vc<60mV hockey-stick, ISRC/ISNK flags, ENABLE, thermal shutdown — **does not model** package L/C, ESD diode leakage, supply slew ≤6V/µs limit details, Ib tempco vs T, en/in PSRR vs freq, DA, humidity, flux leakage, reed/coil EMF, cable L 10–100nH beyond explicit L added.
* Loop-gain injection: macro does not expose explicit loop-break node; PM/GM via Middlebrook is **unreliable** without internal node access — transient OS/settling is primary evidence (per P3IR-05 spec, allowed to report INCONCLUSIVE — TRANSIENT STABILITY ONLY).
* LT1970 vs LT1970A: model is LT1970 (2% accuracy grade); LT1970A (1%) difference is test limit, not topology — transient behavior is identical for stability.

## How to Reproduce

1. Install LTspice 26.0.2.1 from analog.com/ltspice.
2. Verify `lib/sub/LT1970.sub` exists (2404 bytes) and `lib/sym/OpAmps/LT1970.asy` exists.
3. Open any `R5_vendor_bench*.asc` in LTspice → Run → View waveform V(DUT).
4. Batch: `LTspice.exe -b R5_vendor_bench.asc` → produces `.raw` + `.log` with `.meas` (Vpeak, Vfinal, Overshoot).
5. Do **not** copy `LT1970.sub` into repo if license prohibits redistribution — reference path only.

