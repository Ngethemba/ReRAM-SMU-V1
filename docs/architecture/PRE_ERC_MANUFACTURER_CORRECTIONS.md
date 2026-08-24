# Pre-ERC Manufacturer Correction Gate — ReRAM-SMU V1 Phase 7

**Date:** 2026-08-25  
**Gate:** Pre-ERC manufacturer correction (STOP wiring) — Phase 7 point-to-point reconciliation öncesi  
**Source:** User pre-ERC directive 2026-08-25 (LT1970 physical pinout, ADS1262 package, MCU mismatch, MAX16054 latch, Kelvin CMRR, AD5764 rail, ADS1262 bipolar)  
**Status:** CORRECTED IN SCHEMATIC (KiCad rev0.3) — ERC closure resumes after this gate  

---

## 1. LT1970A Physical Pinout — CORRECTED

**Hata:** LTspice macro SpiceOrder (1 Vee, 2 V-, 3 OUT, 4 SENSE+, 5 FILTER, 6 SENSE− ...) paket pin numarası olarak kullanıldı. Fiziksel TSSOP-20 pinleri yanlıştı; 10/11/18 NC kabul edildi.

**Doğrusu (1970afc Rev 2015, Package TSSOP-20 + EP Phys Pin Table):**
| Pin | Name | Type | Domain | Not |
|---|---|---|---|---|
| 1 | VEE | power_in | -12V_A | - |
| 2 | V- | power_in | -12V_A | opamp -supply |
| 3 | OUT | power_out | FORCE_HI via R_iso | |
| 4 | SENSE+ | input | FORCE_LO Kelvin | |
| 5 | FILTER | passive | -> SENSE- via C | 1k internal |
| 6 | SENSE- | input | GND Kelvin | |
| 7 | VCC | power_in | +12V_A | |
| 8 | -IN | input | VDIFF_FB | Kelvin diff |
| 9 | +IN | input | VSET | DAC slew RC |
| 10 | VEE | power_in | -12V_A | **was NC10** |
| 11 | VEE | power_in | -12V_A | **was NC11** |
| 12 | VCSNK | input | 0–5V via 1k+5.1V Zener | sink limit |
| 13 | VCSRC | input | 0–5V via 1k+5.1V Zener | source limit |
| 14 | COMMON | power_in | GND | |
| 15 | ENABLE | input | ENABLE (47k PD) | HW safe |
| 16 | ISRC | open_collector | -> 10k to 3V3 | |
| 17 | ISNK | open_collector | -> 10k to 3V3 | |
| 18 | TSD | open_collector | -> 10k to 3V3 | **was NC18, now TSD thermal** |
| 19 | V+ | power_in | +12V_A | |
| 20 | VEE | power_in | -12V_A | **was EP_V- duplicate** |
| 21 | EP | power_in | VEE (-12V_A) | exposed pad -> VEE, 4 vias |

**Düzeltme:** `sheets/03_OUTPUT_STAGE.kicad_sch` embedded `ReRAM_SMU:LT1970A` symbol rebuilt — 10/11/20/21 VEE power_in, 18 TSD open_collector, EP21 eklendi. R306/R307 1M NC→GND kaldırıldı, VEE pinleri doğrudan -12V_A power symbol + PWR_FLAG'e bağlandı. R308 1M NC→ 10k TSD pull-up to 3V3. Sheet text "NC 10/11/18 1M" -> "VEE 10/11/20/21 -> -12V_A, TSD 10k->3V3". Never connect physical 10/11/18 as NC — kural proje kuralı olarak eklendi.

**Provenance:** Analog Devices 1970afc.pdf (LT1970/LT1970A TSSOP-20 pin table p.2, Thermal pad note), LTspice macro SpiceOrder vs physical mapping cross-checked — LTspice order ≠ package number.

---

## 2. ADS1262 Package — CORRECTED

**Hata:** TQFP-32 5×5 P0.65 footprint kullanıldı.

**Doğrusu (TI SBAS661C Rev C, ADS1262 PW TSSOP-28 9.7×4.4mm P0.65):** 28 pins, PW suffix = TSSOP-28, not TQFP-32. Thermal pad yok, pin 1 START, etc.

**Düzeltme:** `sheets/06_CURRENT_FRONTEND_ADC.kicad_sch` Custom:ADS1262 symbol footprint `Package_QFP:TQFP-28_5x5mm_P0.65mm` -> `Package_SO:TSSOP-28_9.7x4.4mm_P0.65mm`, value `ADS1262IPW TSSOP-28 PW (was TQFP-28, SBAS661C)`. Footprint link corrected before wiring. Symbol pin table SR doğru ADS1262 PW pin definitions ile rebuild edilecek (lib/ReRAM-SMU-V1.kicad_sym'ye curated symbol eklenecek).

---

## 3. MCU/Package Mismatch — RESOLVED

**Hata:** STM32G431KBT6 (LQFP32, 32 pins) ile LQFP64 footprint eşleştirildi. I/O tablosu olmadan G474 terfisi.

**Doğrusu:** KBT6 = 32-pin LQFP (5×5), RBT6 = 64-pin LQFP (10×10, 128KB). Proje relay 6 + SPI×2 (AD5764 + ADS1262) + ENABLE/ISRC/ISNK/TSD/FAST_TRIP + USB + SWD + watchdog = LQFP32'de pin sıkışması.

**I/O Allocation (G431 family):**
| Function | Pins | Notes |
|---|---|---|
| SPI1 AD5764 (SCLK/MOSI/MISO/CS/LDAC/CLR) | 6 | |
| SPI2 ADS1262 (SCLK/DIN/DOUT/DRDY/START/CS) | 6 | |
| Relay drivers (6 shunts) | 6 | |
| ENABLE + ISRC + ISNK + TSD + FAST_TRIP + FAULT_Q | 6 | |
| USB DP/DM + SWD 2 | 4 | |
| Power/osc/NRST/boot | 4 | Toplam 32 net >25 usable GPIO on KBT6 (PC13-15 limited) |

**Karar (DEC-033):** **STM32G431RBT6 LQFP64 10×10 P0.5 PRIMARY** (128KB, G4 family kept, KBT6 superseded). `sheets/08_MCU_USB_CONTROL.kicad_sch` G474RET6 -> G431RBT6 (was KBT6 LQFP32 mismatch) corrected. DEC-032 (G474 PRIMARY) superseded. LQFP32 KBT6 alternate olarak saklanabilir ancak schematic 64-pin ile devam.

---

## 4. MAX16054 FAST_TRIP Latch — CORRECTED

**Hata:** MAX16054 pushbutton debouncer (IN debounced ~50ms typ) FAST_TRIP fault path'te kullanıldı — 50ms gecikme kabul edilemez.

**Doğrusu (MAX16054 datasheet):** Normal IN path debounced 50ms (typ), only _RST output is undelayed for POR. FAST_TRIP must disable LT1970 independently of firmware and without debounce delay; latch only stores fault.

**Düzeltme (DEC-034):** **FAST_TRIP direct hardware kill path:** TLV3501 window comparator (4.5ns) -> diode-OR -> `74LVC1G74` D-FF async SET (ns/µs, not MAX16054) + aynı anda `74LVC1G08 AND` ile ENABLE LOW (direkt). MAX16054 sadece POR debounce için kalır. Architecture: `FAST_TRIP OR SENSE_OPEN OR POR -> 74LVC1G74 SET (async) -> FAULT_Q -> ENABLE = MCU_REQ AND NOT(Q)` + `FAST_TRIP -> inverter -> ENABLE OFF` bypass. Latch FW_CLEAR ancak fault temiz +10ms + I<0.9Itrip iken.

`sheets/07_COMPLIANCE_TRIP.kicad_sch` text "MAX16054" -> "MAX16054 (POR debounce only, NOT FAST_TRIP — FAST_TRIP uses 74LVC1G74 async)" + FAULT_LATCH note eklendi.

---

## 5. Kelvin K1 Accuracy — REOPENED & PROMOTED

**Hata:** 4× bağımsız 10k 0.1%/25ppm ile 54dB CMRR ≤0.5mV Kelvin hata hedefini karşılamaz (common-mode 5V ve sıcaklıkta).

**Hesap:** Discrete diff: CMRR ≈ 20log(1/(4×tolerance)) ≈ 54dB @0.1% (mismatch worst). 5V CM * 10^(-54/20)=5V/501=10mV error >>0.5mV. TC 25ppm×50°C=1250ppm drift ~6.25mV on 5V.

**Doğrusu (LT5400 datasheet):** Matched network 0.01% tracking, 0.2ppm/°C tracking -> CMRR 86dB (20log 1/0.00005), 5V/19952=0.25mV <0.5mV, TC 0.2ppm×50°C=10ppm ->0.05mV.

**Karar (DEC-035):** **LT5400 matched network (LT5400A-3 0.01% 0.2ppm) PROMOTED to PRIMARY**, 4× discrete 10k 0.1% DNP alternate olarak kaldı. `sheets/04_KELVIN_SENSE.kicad_sch` K1 54dB -> "PROMOTED LT5400 86dB PRIMARY (K1 DNP alternate)". DC common-mode/ratio-TC error + targeted LTspice (vendor LT1970 + real LT5400 + Riso47 + 100pF/1nF @+0.1/+2/-2V) rerun before final PRIMARY freeze.

---

## 6. AD5764 Rail Margin — REVISITED

**Hata:** ±12V ±5% -> 11.4V minimum tam AD5764 AVDD min (11.4V) ile eşit, drop/ripple marjı yok.

**Doğrusu (AD5764 Rev C p.4):** AVDD 11.4–16.5V, AVSS -11.4–-16.5V abs, recommended 12V nominal but min 11.4V at IC. Connector drop 50mV + wiring 100mV + ripple 20mV = 11.23V -> fail.

**Karar (DEC-036):** **Guaranteed supply-at-IC requirement:** AT IC pins AVDD ≥11.8V, AVSS ≤-11.8V under worst load/transient. Bench supply **nominal +12.5V ±2% (12.25–12.75V)** veya **±12V ±2% (11.76V) + rail-valid comparator 11.6V** ile sağlanacak. PCB connector'dan sonra <50mV drop, <20mV ripple (LC π ferrite). Rail-valid (TPS3808 threshold 11.6V via divider) ENABLE'i tutar. Absolute/thermal limit 16.5V <12.8V safe. `sheets/01_POWER.kicad_sch` 11.4V min note -> "REQUIRED Guaranteed at IC >=11.8V -> bench 12.5V ±2% or rail-valid 11.6V".

---

## 7. ADS1262 Supply Configuration — COMPARED

**Hata:** +2.5V VCM level shifting dondurulmak üzereydi (single-supply AVDD5/AVSS0 + VCM 2.5V + extra opamps).

**Doğrusu (SBAS661C Rev C §7):** ADS1262 supports **±2.5V bipolar analog supplies (AVDD +2.5V, AVSS -2.5V)** for direct ground-centered ±shunt measurement (±100mV shunt centered at 0V) without level shifting. Can also run AVDD 5V/AVSS 0V with VCM 2.5V.

**Karşılaştırma (DEC-037):**

| Topoloji | Sızıntı/Offset/Karmaşıklık | 100nA için | Karar |
|---|---|---|---|
| Single +5V/0V + VCM 2.5V shift | Ekstra 2 opamp + VCM gen, Ib 10pA×2, offset, leakage | Daha yüksek sızıntı, 2× bias | REJECT for 100nA |
| **Bipolar ±2.5V (AVDD +2.5V via LT3045, AVSS -2.5V via LT1964)** | Shunt 0V merkezli direkt ±100mV, PGA 16/32, no level shift, tek ADC differential, düşük offset | **<5pA input, simpler, lower leakage** | **PREFER** |

**Karar:** Bipolar ±2.5V tercih — AVDD +2.5V LT3045EDD, AVSS -2.5V LT1964ES8 (already for -12V_A alternative), decoupling 10µF+0.1µF. `sheets/06` note eklendi "PREFER bipolar ±2.5V for 100nA low-leakage". Single-supply VCM DNP alternate.

---

## 8. Impact

All 7 gates corrected in schematic text/footprints (rev0.3) before point-to-point wiring. ERC closure resumes after this gate. No PCB started. No suppressing ERC errors.

**Provenance:** 1970afc.pdf, SBAS661C Rev C (ADS1262 PW TSSOP-28), STM32G431 datasheet (KBT6 32-pin vs RBT6 64-pin), MAX16054 datasheet (50ms debounce), LT5400 Rev B (0.01% 0.2ppm), AD5764 Rev C (11.4V min).



**Related:** `docs/calculations/ADS1262_BUFFER_TABLE.md` — per-range buffer decision (DIRECT for 10mA–10µA, BUFFERED for 1µA/100nA with OPA140) and `docs/architecture/PRE_ERC_MANUFACTURER_CORRECTIONS.md` §6 single baseline.
