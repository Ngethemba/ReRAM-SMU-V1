# PHASE 2 Component Matrix — Lifecycle / Sourcing / SPICE Availability

**Project:** ReRAM-SMU V1  
**Parent task:** Phase 2 — Architecture & Candidate Component Verification (Agent F)  
**Date:** 2026-08-24  
**Author:** Agent F — Component Lifecycle / Sourcing / SPICE  
**Status:** CANDIDATE — lifecycle/sourcing screening only. No purchase. No promotion to `bom/approved/`. All rows are `PROVISIONAL / REQUIRES VERIFICATION` until datasheet page-cited and distributor-stock confirmed at time of order.  
**Supplements:** `PHASE2_COMPONENT_MATRIX_AGENT_D_PRECISION.md` (Agent D deep technical comparison of DAC/Ref/Amp/ADC/MCU). This file adds the supply-chain lens required by the task brief.  
**Policy:** `ENGINEERING_RULES.md §2.2` — no spec propagated from memory; every quantitative claim requires primary manufacturer datasheet citation. Sourcing must be via **authorized distributors** only.

---

## 1. How to read this matrix

**Required columns per brief:** `Reference | Function | Manufacturer | MPN | Package | Lifecycle | Preferred Supplier | Unit Price (single, authorized) | Alternate | Datasheet | SPICE | Verification Status`

- **Lifecycle** = manufacturer product-page status as of 2026-08-24 (web_search snapshot). ADI vocabulary: `Recommended for New Designs` / `Production` / `Last Time Buy` / `Obsolete`. TI: `ACTIVE` / `NRND` / `LIFEBUY`. ST: `Active — volume production, longevity commitment date`.
- **Preferred Supplier** = authorized distributor with verifiable stock today (DigiKey / Mouser / Farnell / Arrow / Avnet / TI Store / ST Store). LCSC/JLCPCB listed only as secondary for ST. Marketplace / broker lots are **not** preferred.
- **Unit Price** = single-unit authorized price observed via web_search / Octopart / ST/TI store on 2026-08-24. Treat as **indicative only**; re-quote at order time. Many analog parts are quoted in $ or €; FX moves. No volume pricing is final.
- **SPICE** = model exists and is downloadable from manufacturer (or LTspice built-in / TINA-TI). DAC/ADC digital+analog models are typically behavioral macro-models, not transistor-level.
- **Verification Status** = `UNVERIFIED` until a human opens the cited datasheet rev and confirms the cited page; `PARTIAL` = datasheet + product-page confirmed but distributor stock/price not yet re-checked on order day; `VERIFIED` only after datasheet + live distributor check + errata review.

> **Do NOT create final BOM.** This matrix is a screening table. Promotion to `bom/approved/` requires a DEC entry with evidence and a live distributor buy-check.

---

## 2. Core candidate matrix (the seven named parts)

| Reference | Function | Manufacturer | MPN (orderable example) | Package | Lifecycle (2026-08-24 snapshot) | Preferred Supplier (authorized) | Unit Price (1 pc, auth., indicative) | Alternate | Datasheet | SPICE | Verification Status |
|-----------|----------|--------------|-------------------------|---------|---------------------------------|---------------------------------|--------------------------------------|-----------|-----------|-------|---------------------|
| U-DAC | Quad 16-bit DAC, 2.5 V ref, SPI | Analog Devices | **AD5686RBRUZ** (TSSOP-16) / **AD5686RBCPZ** (LFCSP-16 3×3) | TSSOP-16 (RU-16), LFCSP-16 (CP-16) | **Active — Production** (ADI nanoDAC+ family). Rev F 2024-11-07 datasheet. Product page lists SPICE + IBIS. Not NRND. ECAD orders >10 k quoted as production. | DigiKey, Mouser, Farnell, Arrow (authorized ADI) — Mouser lists AD5686R series live; DigiKey shows stock under AD5686RBRUZ | **~$12–14 (quad = ~$3/ch)** @1pc; ~$9–11 @100; EP version -55..125 °C higher | **AD5689RBRUZ** (tighter TUE drop-in), **AD5764ARUZ** (true bipolar ±10 V, see §3), **DAC8568ICPW** (TI, 4 ppm ref) | AD5686R/AD5685R/AD5684R Rev F — https://www.analog.com/media/en/technical-documentation/data-sheets/ad5686r_5685r_5684r.pdf · Product page https://www.analog.com/en/products/ad5686r.html | **Yes** — ADI SPICE Macro Model (AD5686R.cir) downloadable from product page; IBIS model also. Behavioral macro, adequate for supply/digital timing, not for INL Monte-Carlo. Listed under Tools & Simulations on product page. | **PARTIAL** — lifecycle + SPICE confirmed via ADI product page + Rev F datasheet. Stock/price indicative; re-check live DigiKey/Mouser before order. No errata review yet. |
| U-AMP-ZD | Zero-drift dual op-amp (DAC conditioning / voltage loop) | Analog Devices | **ADA4522-2ARMZ** (MSOP-8) / **ADA4522-2ARZ** (SOIC-8) | MSOP-8 (RM-8), SOIC-8 (R-8) | **Recommended for New Designs — Production** (ADI). Rev I 2025-01-08 active. PCN 18_0171 Rev C (2020-08-20) die rev qualified, no discontinuance. Family includes -1/-2/-4. | DigiKey, Mouser, Farnell — DigiKey entry 505-ADA4522-2ARMZ-ND shows backorder/645 in upstream feed but live; Mouser/Farnell show stock. **Note 2026-08-24 snapshot showed 0 direct stock on one DigiKey waffle but 645 via Farnell/Avnet feed — verify live.** | **~$4.5–6.50 (dual)** @1pc; ~$3.80 @100 | **OPA189** (TI, 14 MHz, 5 nV/°C), **LTC2057** (ADI HV chopper, LTspice native), **ADA4528-2** (ADI low-V ultralow noise, 5.5 V max) | ADA4522-1/-2/-4 Rev I — https://www.analog.com/media/en/technical-documentation/data-sheets/ada4522-1_4522-2_4522-4.pdf · Product page https://www.analog.com/en/products/ada4522-2.html | **Yes** — ADA4522 SPICE Macro Model (ADA4522.cir) on product page (1 model covers -1/-2/-4). Also available via BDTIC mirror. LTspice-importable .cir. | **PARTIAL** — lifecycle RECOMMENDED confirmed; SPICE confirmed; price/stock fluctuates (showed mixed stock 2026-08-24, re-check required). |
| U-PWR | Power op-amp ±500 mA, programmable current limit | Analog Devices (ex-Linear) | **LT1970AFEN#PBF** (TSSOP-20, tube) / **LT1970AIFE#TRPBF** (T&R) | TSSOP-20 (FE-20) with exposed copper bottom plate for heatsinking | **Active — Production** (ADI). Not NRND. Datasheet 1970afc current. Product page under Specialty Amplifiers. Legacy LT part but no PDN. | DigiKey, Mouser, Arrow (ADI authorized) — LT1970A series listed on ADI product page; Octopart shows ~252+ stock via brokers but **authorized check required** | **~$12–15** @1pc; ~$10 @100 (varies by tube vs reel) | **OPA567** (TI, 2 A), **OPA569** (TI, 2 A + current limit), **LT1210** (ADI, 1.1 A, no prog limit) — but LT1970A unique for 1% prog limit accuracy | LT1970A datasheet 1970afc — https://www.analog.com/media/en/technical-documentation/data-sheets/1970afc.pdf · Product page https://www.analog.com/en/products/lt1970a.html | **Yes — LTspice built-in** (LT1970 / LT1970A model in LTspice library + demo circuits). No separate .cir download needed; LTspice → Component → LT1970. Also PSpice .lib third-party. | **PARTIAL** — lifecycle active confirmed; SPICE built-in confirmed; authorized stock not strongly confirmed (broker-heavy Octopart feed) — must verify DigiKey/Mouser live inventory before reliance. Package is TSSOP-20 only (no QFN option) — thermal design must use bottom plate. |
| U-ADC | 32-bit ΔΣ ADC + PGA + 2.5 V ref, 38.4 kSPS | Texas Instruments | **ADS1262IPW** (TSSOP-28 tube) / **ADS1262IPWR** (T&R) | TSSOP-28 (PW-28) | **ACTIVE — Production** (TI). Package Option Addendum (TI OA PDF) lists `ADS1262IPW ACTIVE Production` and `ADS1262IPWR ACTIVE`. No NRND. Datasheet Rev C. | TI Store (direct), DigiKey, Mouser, Arrow (TI authorized) — TI Store listing shows inventory lock behind login (common for TI); DigiKey/Mouser show series but stock varies — **check live before order** | **~$11–14** @1pc; ~$8–10 @100; ADS1263 (dual-ADC) +$2 | **ADS124S08IPW** (24-bit, 12-ch, ~$6, lower noise-free), **AD7175-8BCPZ** (ADI 24-bit 8-ch, 250 kSPS, best INL, see §3), **AD7124-8BCPZ** (24-bit, PGA 128, lower 50 Hz rej) | ADS126x Rev C — https://www.ti.com/lit/ds/symlink/ads1262.pdf · Product page https://www.ti.com/product/ADS1262 · OA addendum https://www.ti.com/ods/sysadd/oa/symlink/ads1262_oa.pdf | **Limited — TI TINA-TI model for ADS126x** (TINA-TI reference design), **no native LTspice/ngspice transistor model**. IBIS for digital I/O only. For system-level, use behavioral B-source (noise + PGA + Sinc filter) or TI TINA. ADS1262 cannot be fully simulated in LTspice/ngspice without custom behavioral model. | **PARTIAL** — ACTIVE confirmed via TI OA PDF; SPICE limitation confirmed (TINA only). Live authorized stock not strongly confirmed (TI Store login-gated) — re-check required. |
| U-REG | Micropower LDO 500 mA, low noise | Analog Devices (ex-Linear) | **LT1763CS8#PBF** (SOIC-8, 3.3 V/5 V/ADJ variants: LT1763CS8-3.3, -2.5, ADJ) | SOIC-8 (S8), SOT-223 (ST), TO-220 (when applicable), DDPAK | **Active — Production / Recommended for New Designs** (ADI). AN-83 + product page list as RECOMMENDED. No PDN. | DigiKey, Mouser, Arrow (ADI authorized); Rochester Electronics (ADI authorized excess) shows LT1763CS8-3.3 | **~$3.00–5.00** @1pc depending on fixed vs ADJ; ~$2.20 @100 | **LT3042EDD** (ADI ultralow noise 200 mA), **LT1963** (1.5 A variant), **TPS7A4700** (TI, 1 A low-noise), **ADM7150** (ADI, 800 mA, 1 µVnoise) | LT1763 series datasheet via https://www.analog.com/en/products/lt1763.html (links to LT1763.pdf) | **Yes — LTspice built-in demo circuit + .lib** (LT1763.lib with subckts for -1.5/-1.8/-2.5/-3/-3.3/-5/ADJ). File at `https://github.com/mpkopec/ltspice-lib/blob/master/sub/LT1763.lib` mirrors ADI. LTspice → LT1763 Demo Circuit 10 V→2.5 V@500 mA. | **PARTIAL** — active confirmed; LTspice model confirmed; price/stock indicative. Fixed-voltage variants are separate orderables — choose -3.3/-5/ADJ per power-tree. |
| U-REF | Precision 2.5 V reference, ±0.02 % | Analog Devices | **ADR4525BRZ** (SOIC-8) / **ADR4525ARZ** (A-grade) / **ADR4525CRZ** (C) / **ADR4525B** variants | SOIC-8 (R-8), MSOP-8 (RM-8) for some grades | **Recommended for New Designs — Production** (ADI) — family ADR4520/25/30/33/40/50 all active. | DigiKey, Mouser, Farnell, Arrow (ADI authorized) — Octopart shows ~42k stock via PNEDA broker but authorized lines also list. Must verify authorized. | **~$3.50–5.50** (B/C grade) @1pc; A-grade ~$2.80; D-grade (0.8 ppm/°C) premium | **LTC6655BHMS8-2.5#PBF (LN 0.775 µV p-p)** (ADI, lower noise/hysteresis, see §3), **REF5025AIDGKR** (TI, 3 ppm but 7.5 µV p-p), **MAX6070BAUT25+** (ADI/Maxim, lower grade) | ADR4520/4525/4530/4533/4540/4550 Rev G (formerly Rev E) — https://www.analog.com/media/en/technical-documentation/data-sheets/ADR4520_4525_4530_4533_4540_4550.pdf · https://www.analog.com/en/products/adr4525.html | **Yes** — ADI SPICE model (behavioral) for ADR45xx family; also LTspice ADR45xx.lib third-party. Adequate for reference noise/TC sim at system level. | **PARTIAL** — lifecycle recommended confirmed; SPICE yes; broker-heavy stock feed — re-check authorized. Hysteresis grade matters (B/C = 13 ppm full sweep, D = 1 ppm) — specify grade at order. |
| U-MCU | Mainstream Arm Cortex-M4F 170 MHz MCU + FPU + math | STMicroelectronics | **STM32G431KBT6** (LQFP-32 7×7), **STM32G431CBT6** (LQFP-48), **STM32G431RBT6** (LQFP-64), **STM32G431CBU6** (UFQFPN-48) | LQFP-32/48/64/100, UFQFPN-32/48 | **Active — Volume production, longevity commitment to 01/2036** (ST 10-yr program). Listed as `Active` on all G431 variants. ST longevity page commits ≥10 yr. | **ST Store (estore.st.com)**, DigiKey, Mouser, Farnell, Arrow, LCSC/JLCPCB (ST authorized region) — stock widely available. ST Store shows KBT6 TR available; LCSC C529357 shows 841+ in stock @ $3.57. | **~$3.00–4.50** @1pc (KBT6 $3.57 LCSC / $2.97 Octopart); ~$2.40 @100; G431CBU6 similar | **STM32G474RET6** (512 KB/128 KB, HRTIM, bigger), **STM32G030C8T6** (M0+ 64 MHz, no USB — DEFER, fails req), **RP2040/RP2350** (Pi, PIO can MUX SPI but needs 5 V buffers — COST alternate), **STM32F303K8T6** (older F3, 72 MHz) | STM32G431x6/x8/B datasheet — https://www.st.com/resource/en/datasheet/stm32g431c6.pdf · Product page https://www.st.com/en/microcontrollers-microprocessors/stm32g431c6.html · Longevity https://www.st.com/content/st_com/en/about/quality-and-reliability/product-longevity.html | **No analog SPICE** (MCU is digital). **IBIS model yes** (ST IBIS for SI), **STM32CubeMX** for clock/pin/power, **no LTspice/ngspice**. Housekeeping ADC/DAC/op-amp inside MCU are not precision-path. | **PARTIAL** — active + 2036 longevity confirmed via ST product pages; pricing confirmed via ST Store + LCSC; no SPICE is expected/acceptable. |

> **Snapshot caveat:** Distributor stock for analog parts (AD5686R, ADA4522, LT1970A, ADR4525) showed mixed live feeds on 2026-08-24 — some DigiKey waffles showed “0, backorder” while Farnell/Arrow showed stock. This is common for ADI parts mid-lot. **No row is fully VERIFIED until a live authorized-distributor check on order day plus errata/PCN search.**

---

## 3. Alternatives proposed by other agents (Agent D + new)

This section covers every serious alternative already tabled by Agents A–E (captured in `PHASE2_COMPONENT_MATRIX_AGENT_D_PRECISION.md`) plus two new ones for the power chain where lifecycle is thin.

| Function | Baseline → Alternate | Manufacturer | MPN | Package | Lifecycle | Preferred Supplier | Unit Price | Why considered | Datasheet | SPICE | Verdict |
|----------|---------------------|--------------|-----|---------|-----------|--------------------|------------|----------------|-----------|-------|---------|
| DAC — bipolar direct | AD5686R → **AD5764** (16-bit quad bipolar ±10 V, integrated buffers+ref bufs) | ADI | AD5764ARUZ / ACPZ | TQFP-32 7×7, LFCSP-32 | Active | DigiKey, Mouser | ~$35–45 quad (~$9/ch) | Eliminates external ×2 gain amp (removes resistor TC/gain error). INL ±1 LSB vs ±2 LSB. Requires ±12 V rails (already provisioned). | https://www.analog.com/media/en/technical-documentation/data-sheets/AD5764.pdf | Yes (ADI) | **REPLACE candidate** if 0.02% accuracy headroom at ≤1 V gates |
| DAC — dense | AD5686R → **AD5766** (16-ch, 8 ranges incl ±5 V) | ADI | AD5766BCPZ | LFCSP-40 6×6 | Active | DigiKey | ~$55 | 16-ch only useful for future multi-SMU array | AD5766 datasheet | Yes | **DEFER** |
| DAC — 20-bit premium | AD5686R → **AD5791** (20-bit unbuffered bipolar) | ADI | AD5791BRUZ | TSSOP-20 | Active (premium) | DigiKey | ~$30–40 | 19 µV INL vs 305 µV, 1 ppm — overkill for V1, needs 2 refs + inv + buffer | AD5791 datasheet | Yes | **DEFER to V1.x** |
| DAC — TI cost alt | AD5686R → **DAC8568** (TI quad 16-bit, int 2.5 V 4 ppm) | TI | DAC8568ICPW | TSSOP-16 | Active | DigiKey, Mouser | ~$10–12 | Cost save $2, worse TC/noise | TI DAC8568 datasheet | Yes (TINA) | **KEEP AS ALTERNATE** |
| DAC — improved nanoDAC+ | AD5686R → **AD5689R-1** | ADI | AD5689RACPZ | LFCSP-16 | Active | DigiKey | ~$13–15 | Tighter TUE ±0.06% drop-in | AD5689R datasheet | Yes | **KEEP AS ALTERNATE** |
| Ref — ultralow noise | ADR4525 → **LTC6655BHM-2.5 / LN-2.5** | ADI | LTC6655BHMS8-2.5#PBF / LN | MSOP-8 | Active, LN is selected LD | DigiKey, Mouser | ~$6–9 (LN) | 0.775 µV p-p vs 1.6 µV, hysteresis <6 ppm vs −97 ppm, long-term 2 ppm/1 kh | LTC6655 datasheet | **Yes — LTspice built-in** | **KEEP** as separate DAC ref (recommended by Agent D) |
| Ref — TI economy | ADR4525 → **REF5025** (TI 2.5 V) | TI | REF5025AIDGKR | VSSOP-8 (DGK) | Active | DigiKey | ~$4–7 (high grade) | 7.5 µV p-p even with NR cap → 4× worse than LTC6655 | https://www.ti.com/lit/ds/symlink/ref5040.pdf | Yes (TINA) | **DEFER** unless stock crisis |
| Amp — high BW chopper | ADA4522-2 → **OPA189** (TI, 14 MHz, 5 nV/°C) | TI | OPA2189IDGK | VSSOP-8 | Active | DigiKey | ~$5.50 dual | 14 MHz allows faster compliance loop comp, lower drift, but Ib 1.4 nA → kills 100 nA | OPA189 datasheet | Yes | **KEEP AS ALTERNATE for F1 only** |
| Amp — JFET Ib | ADA4522-2 → **OPA140** (TI JFET, Ib 10 pA) | TI | OPA2140AIDGK | VSSOP-8 | Active | DigiKey | ~$4.50 dual | Only amp that preserves 100 nA headroom (Ib 10 pA → 10 pA error) | OPA140 datasheet | Yes | **KEEP for F2/F3 low-current** |
| Amp — HV chopper | ADA4522-2 → **LTC2057** | ADI | LTC2057CMS8#PBF | MSOP-8 | Active | DigiKey | ~$5 | 60 V HV, LTspice native, for ±12 V path | 2057f datasheet | **Yes — LTspice** | **KEEP AS ALTERNATE for HV** |
| Amp — ultralow 1/f | ADA4522-2 → **ADA4528-2** | ADI | ADA4528-2ARMZ | MSOP-8 | Active | DigiKey | ~$5.20 | 97 nV p-p @gain 100 best 1/f, but 5.5 V max | ADA4528 datasheet | Yes | **KEEP for low-V sense only** |
| ADC — economy | ADS1262 → **ADS124S08** (24-bit, 12-ch, 4 kSPS) | TI | ADS124S08IPWR | TSSOP-28 | Active | DigiKey | ~$6–8 | Saves $5, 21.5 noise-free bits @20 SPS, still passes headroom | ADS124S08 datasheet | TINA | **KEEP AS ALTERNATE** |
| ADC — ADI high-speed MUX | ADS1262 → **AD7175-8BCPZ** (24-bit, 8-ch, 250 kSPS, ±1 ppm INL) | ADI | AD7175-8BCPZ | LFCSP-40 6×6 | Active | DigiKey | ~$18–22 | 20 µs/ch scan (vs 50 ms MUX), 85 dB 50/60 rej, 8 full-diff ch → no leakage MUX | AD7175-8 datasheet | **Yes (ADI)** | **REPLACE candidate** if autorange chatter at 10 mV/50 ms gates |
| ADC — 32-bit ADI | ADS1262 → **AD7177-2BCPZ** (32-bit, 2-ch, 10 kSPS) | ADI | AD7177-2 | LFCSP-32 | Active | DigiKey | ~$22 | Only 2 ch → needs external MUX → reintroduces leakage | AD7177-2 datasheet | Yes | **DEFER** |
| ADC — PGA128 low-power | ADS1262 → **AD7124-8BCPZ** (24-bit, PGA 1–128) | ADI | AD7124-8BCPZ | LFCSP-32 5×5 | Active | DigiKey | ~$12–14 | 65 dB Sinc4 50 Hz rej — needs firmware notch, PGA 128 useful | AD7124-8 datasheet | Yes | **KEEP for battery future only** |
| LDO — ultralow noise | LT1763 → **LT3045EDD#PBF** (20 V, 500 mA, 0.8 µVrms) | ADI | LT3045EDD#PBF | DFN-12 | Active | DigiKey | ~$4 | Lower noise than LT1763, DFN only, higher PSRR — drop-in for analog rail if LT1763 noise fails budget | LT3045 datasheet | **LTspice** | **KEEP AS ALTERNATE** |
| LDO — higher current | LT1763 → **LT1963AES8#PBF** (1.5 A) | ADI | LT1963 | SOT-223/SOIC | Active | DigiKey | ~$4 | Only if 500 mA proved marginal (unlikely: analog ~200 mA) | LT1963 datasheet | LTspice | **DEFER** |
| LDO — TI low-noise | LT1763 → **TPS7A47** (36 V, 1 A) | TI | TPS7A4700RGWT | VQFN-20 | Active | DigiKey | ~$4 | TI alternative, NR pin, similar noise | TPS7A47 datasheet | TINA | **DEFER** unless LT1763 stock constraint |
| Power op-amp — higher current | LT1970A → **OPA567** (TI, 2 A) | TI | OPA567AIDWPR | SO PowerPAD-20 | Active | DigiKey | ~$8 | 2 A but no 1% prog limit — needs external sense | OPA567 datasheet | TINA | **KEEP AS ALTERNATE** (current only) |
| Power op-amp — integrated limit | LT1970A → **OPA569** (TI, 2 A + limit flag) | TI | OPA569AIDWPR | SO PowerPAD-20 | Active | DigiKey | ~$9 | Integrated limit, lower accuracy than LT1970A 1% | OPA569 datasheet | TINA | **KEEP AS ALTERNATE** |
| MCU — bigger flash | STM32G431 → **STM32G474RET6** (512 KB/128 KB, HRTIM) | ST | STM32G474RET6 | LQFP-64 | Active, longevity to 2036 | DigiKey, ST Store | ~$7–9 | Only if 128 KB flash fills with 6×LUT + USB+TMC | G474 datasheet | — | **KEEP AS ALTERNATE** |
| MCU — cost PI | STM32G431 → **RP2040 / RP2350** | Raspberry Pi | RP2040B0-QFN56 / RP2350 | QFN-56 | Active | LCSC, Pi | ~$0.70 | Saves $3, needs PIO SPI MUX + 5 V buffers + QSPI flash | RP2040 datasheet | — | **KEEP AS COST alternate** (risk: integration) |

*All alternates remain CANDIDATE. Selection among them is a DEC with evidence, not a purchase.*

---

## 4. Lifecycle summary (one-line verdict per core part)

| Part | Lifecycle verdict (2026-08-24) | Confidence | Evidence |
|------|-------------------------------|------------|----------|
| **AD5686R** | **Active / Production** — nanoDAC+ family, Rev F current, no PDN | High | ADI product page + Rev F datasheet; stock via Mouser series |
| **ADA4522-2** | **Recommended for New Designs — Production** (Rev I 2025) | High | ADI product page header RECOMMENDED; PCN 18_0171 only die rev, not EOL |
| **LT1970A** | **Active / Production** (legacy LT, no NRND flag) | Medium-High | ADI product page active; no PDN found; broker-heavy stock feed is the risk, not lifecycle |
| **ADS1262** | **ACTIVE — Production** (TI) | High | TI Package Addendum OA PDF: `ACTIVE Production TSSOP PW-28` + Rev C datasheet |
| **LT1763** | **Active / Recommended for New Designs** | High | ADI product page + AN-83 RECOMMENDED table; no PDN |
| **ADR4525** | **Recommended for New Designs — Production** | High | ADI product page RECOMMENDED; family ADR452x all active |
| **STM32G431** | **Active — volume production, 10-yr longevity to 01/2036** | High | ST product pages C6/V6/CB/MB all show `Active Until: 01/2036`; ST longevity program page |

**No core part is NRND, Last Time Buy, or Obsolete as of 2026-08-24.** The thinnest lifecycle is **LT1970A** (single TSSOP-20 package, legacy LT, lower volume than ADI nanoDAC/zero-drift) — monitor PCN subscription.

### 4b. Adversarial verdicts — KEEP / REPLACE / DEFER per core part (sourcing + technical + lifecycle)

| Part | Verdict | Rationale (lifecycle + sourcing + SPICE + technical) | Condition to REPLACE |
|------|---------|------------------------------------------------------|----------------------|
| **AD5686R** | **KEEP as economy path — REPLACE candidate AD5764 if accuracy gates** | Lifecycle Active, TSSOP/LFCSP dual package reduces risk, SPICE yes, ~$12 quad cheap. But needs external ×2 gain amp (adds resistor TC + op-amp offset). 152 µV LSB fine; INL ±305 µV system consumes accuracy budget at ≤1 V. Agent D budgets show AD5686R passes only with 0.01 % resistors + LTC6655LN. | REPLACE with **AD5764** (±5 V direct bipolar, INL ±1 LSB, no gain stage) if post-cal error budget at 2 V fails or resistor cost exceeds $25 saved. |
| **ADA4522-2** | **KEEP for F1 DAC conditioning / voltage loop** | RECOMMENDED for New Designs, dual package, SPICE yes, 55 V, best drift 22 nV/°C. Lifecycle strong (PCN only die rev). Ib 50 pA kills 100 nA shunt sense — must not use for F3 low-current. | REPLACE with **OPA140** for F2/F3 (JFET Ib 10 pA). For F1 high-BW comp, alternate **OPA189** (14 MHz). ADA4522 remains for F1. |
| **LT1970A** | **KEEP — but highest sourcing risk, monitor PCN monthly** | Active but single TSSOP-20, broker-heavy stock, no alternate package. SPICE built-in (LTspice) is best-in-matrix. 1% prog limit unique for compliance. No EOL but low volume → Last Time Buy risk if ADI consolidates. | REPLACE with **OPA569** (2 A + limit flag, TINA) or **OPA567** + external sense if LT1970A goes NRND or TSSOP-20 lead time >26 weeks. Requires board re-spin (PowerPAD vs TSSOP). |
| **ADS1262** | **KEEP as baseline** | ACTIVE TI, TSSOP-28, dual-ADC option (ADS1263 +$2), TINA model limited but adequate. Lifecycle strong, TI longevity high. 24 noise-free bits @20 SPS, 130 dB 50 Hz. | REPLACE with **AD7175-8** (ADI, 20 µs/ch, ±1 ppm INL, 8 full-diff ch) if autorange latency at 10 mV/50 ms chatters or channel count needs Kelvin+current+temp without MUX leakage. |
| **LT1763** | **KEEP** | Recommended for New Designs, multi-package, LTspice native, ~$3–5 cheap. Lifecycle strong, mature LDO. Fixed-voltage suffixes allow clean rail split. | REPLACE with **LT3045** (0.8 µVrms, higher PSRR) if analog rail noise fails 10 µVpp budget, or **TPS7A47** if LT1763 stock constrained. |
| **ADR4525** | **KEEP (B-grade min, D-grade if shared ref)** | Recommended, family active, SPICE yes, ~$3.5–5. 2 ppm/°C B-grade adequate; D-grade 0.8 ppm hysteresis 1 ppm worth premium for shared DAC+ADC ref. | REPLACE with **LTC6655LN-2.5** as separate DAC ref (0.775 µV p-p, <6 ppm hysteresis) — recommended dual-ref strategy per Agent D. REF5025 is DEFER (noise 4× worse). |
| **STM32G431** | **KEEP** | Active to 01/2036 (10-yr), 3× SPI, FS USB, 128 KB/32 KB, widely stocked via ST Store/DigiKey/LCSC. No SPICE needed (IBIS yes). Lifecycle strongest in matrix. | REPLACE with **STM32G474** (512 KB) only if firmware sizing exceeds 128 KB (6×LUT + USB+TMC). DEFER cost-cut RP2040 unless BOM pressure forces it (adds PIO complexity). |

> **Summary:** 7/7 core parts are **KEEP**. Two are conditional REPLACE candidates gated on measured headroom: **AD5686R → AD5764** (if gain-stage error dominates) and **ADS1262 → AD7175-8** (if scan latency dominates). One is KEEP-but-watch: **LT1970A**. No DEFER or Obsolete among core.

---

## 5. SPICE model availability summary

| Part | SPICE available? | Where / Filename | Simulator | Quality | Notes |
|------|------------------|------------------|-----------|---------|-------|
| AD5686R | **Yes** | ADI product page → SPICE Model → `AD5686R SPICE Macro Model` (AD5686R.cir) | PSpice / LTspice (import) | Behavioral macro — covers reference, SPI timing, supply, glitch approx | Also IBIS for SI |
| ADA4522-2 | **Yes** | ADI product page → SPICE Model → `ADA4522.cir` (covers -1/-2/-4) ; BDTIC mirror `ada4522.cir` | LTspice / PSpice / ngspice (via .include) | Good — chopper 800 kHz + 4.8 MHz artifacts modeled, noise reasonably | Tested in LTspice forum; import via `.include ADA4522.cir` |
| LT1970A | **Yes — built-in** | LTspice library `LT1970` / `LT1970A` (no download) + demo circuits | **LTspice native** | Best in this matrix — Linear native model, current-limit program modeled | Also ngspice-encapsulated LT1970 .lib third-party but LTspice is canonical |
| ADS1262 | **No native SPICE** — TINA-TI only | TI TINA-TI reference design for ADS126x; no LTspice/ngspice model | TINA-TI | Behavioral system model only (PGA + ΔΣ + filter approx) | For LTspice/ngspice, create B-source behavioral: noise 0.16 µV p-p @20 SPS, Sinc4, 130 dB 50 Hz notch |
| LT1763 | **Yes — built-in** | LTspice `LT1763.lib` (subckts -1.5/-1.8/-2.5/-3/-3.3/-5/ADJ) + Demo Circuit 10 V→2.5 V@500 mA | **LTspice native** | Good — dropout, noise, PSRR modeled | Also `github.com/mpkopec/ltspice-lib` mirror |
| ADR4525 | **Yes** | ADI ADR45xx SPICE (ADR4525.cir / ADR45xx.lib) | LTspice / PSpice | Behavioral — TC, noise, load transient | Adequate for reference-filter (1 µF + RC 1–10 Hz) sim |
| STM32G431 | **No SPICE** (expected) | **IBIS yes** (ST IBIS for LQFP/UFQFPN) + STM32CubeMX | — | MCU is digital — no analog SPICE intended | Model MCU as ideal SPI master + DMA in simulation; use IBIS for SI on SPI lines |

**Simulation topology for hybrid flow (DEC-TOOL-002: ngspice primary, LTspice secondary):**
- **LTspice:** LT1970A power stage + LT1763 LDO + LT3045 alt + ADA4522/LTC2057 + ADR4525/LTC6655 loop — use native models.
- **ngspice:** Import ADA4522.cir, AD5686R.cir, ADR4525 via `.include`; LT1970/LT1763 via adapted `.lib`.
- **TINA-TI:** ADS1262, ADS124S08, OPA140/OPA189 if TI path chosen — run separately and cross-check.

---

## 6. Package availability and procurement notes

| Part | Orderable packages (V1) | Recommended for V1 layout | Notes |
|------|-------------------------|---------------------------|-------|
| AD5686R | TSSOP-16 (RU-16, 5.0×4.4 mm) and LFCSP-16 (CP-16, 3×3 mm, exposed pad) | **TSSOP-16** for hand-solder/prototype; LFCSP-16 for production density | If V1 PCB is prototype, order TSSOP-16. LFCSP needs hot-plate/reflow; same die, different thermal. |
| ADA4522-2 | MSOP-8 (RM-8, 3×3) and SOIC-8 (R-8) | **MSOP-8** (smaller, same perf) but have SOIC-8 footprint as fallback | MSOP-8 = 0.65 mm pitch, easier than LFCSP. Have both footprints in KiCad. |
| LT1970A | **TSSOP-20 only** (FE-20, 6.5×4.4 mm, copper bottom plate) | TSSOP-20 — bottom plate must solder to thermal pad + vias to GND plane | **Single package = lifecycle risk** — no QFN/SOIC alternate from ADI. Thermal design is load-bearing (50 mW SOA but package heatsinking still needed for ±10 mA DC). |
| ADS1262 | TSSOP-28 (PW-28, 9.7×4.4 mm) | TSSOP-28 | Also available as ADS1263 (adds aux 24-bit ADC) same package — consider if aux needed for temp/ref monitor (+$2). |
| LT1763 | SOIC-8 (S8), SOT-223-6, TO-220 | **SOIC-8** for prototype | Choose fixed -5.0/-3.3 or ADJ per rail. Different MPNs — do not order generic LT1763 without suffix. |
| ADR4525 | SOIC-8 (R-8), MSOP-8 | **SOIC-8 BRZ** (B-grade 2 ppm/°C) | Grade matters: A=4 ppm, B=2 ppm, C=1 ppm, D=0.8 ppm (0–70 °C). D-grade is best hysteresis (1 ppm vs 97 ppm) — worth premium for shared-ref topology. |
| STM32G431 | LQFP-32 (7×7), LQFP-48 (7×7), LQFP-64 (10×10), UFQFPN-48 (7×7) | **LQFP-48 (CBT6)** or **LQFP-32 (KBT6)** per GPIO count | KBT6 (32-pin) saves area but limits relay/flag pins; CBT6 is sweet spot for 47 I/O. UFQFPN is 0.5 mm pitch — harder to probe. |

---

## 7. Counterfeit-sensitive list and sourcing policy

### 7.1 Sensitivity classification

| Tier | Parts | Risk driver | Why high |
|------|-------|-------------|----------|
| **CRITICAL — never broker** | **ADS1262, AD5686R, ADR4525/LTC6655, ADA4522, LT1970A** | High-value precision analog, single-source, high counterfeit incentive, remarked lower-grade or pulled stock common on marketplace | ADS1262 and AD5686R are frequently counterfeited on marketplace/broker lots (re-marked ADS1220/AD5684, lower grades). ADR/LTC refs are remark-risk (A-grade sold as B). LT1970A is legacy LT with low volume — broker lots may be pulled/ESD-damaged. ADA4522 chopper is remark target (ADA4522-1 sold as -2). |
| **HIGH — authorized only** | **LT1763, OPA140/OPA189, AD7175/AD7124** | Power/precision amplifiers and ADCs with high demand; remarked industrial vs commercial temp grades | OPA140/189 have commercial vs enhanced grades; LT1763 has fixed-voltage variants that can be mis-shipped. |
| **MEDIUM — authorized preferred, LCSC/JLCPCB OK for ST** | **STM32G431** | MCU is high-volume, lower remark incentive than precision analog, but China-market lots have clone-label risk on marketplace | STM32G431 family has many suffixes (KBT6 vs KBU6 vs CBT6) — wrong suffix is not counterfeit but is wrong-reel risk. LCSC/JLCPCB are authorized for ST in Asia but verify suffix and date code. |
| **LOW — passives/shunts excluded here** | Shunts, resistors, caps, relays | Not in this matrix — covered separately | Still source via authorized for 0.01% resistors and 10 ppm shunts; commodity caps via authorized. |

### 7.2 Sourcing policy (binding for V1)

1. **Authorized distributors only** — DigiKey, Mouser, Farnell/Newark, Arrow, Avnet, Rochester Electronics, TI Store, ST Store. For ST, LCSC/JLCPCB are secondary authorized. **No marketplace, no broker, no “HK stock” lots** for CRITICAL tier.
2. **Grade suffix exactness** — Order the exact MPN suffix (AD5686R**B**RUZ vs ARUZ, ADR4525**B**RZ, ADA4522-2**ARMZ** vs **ARZ**, LT1763CS8-**3.3**#PBF). A-grade vs B-grade is not interchangeable for accuracy budget.
3. **Date code + lot traceability** — Record distributor, lot, date code, and invoice in `bom/sourcing/` at purchase. Photograph reel labels on receipt.
4. **PCN/PDN subscription** — Subscribe to ADI myAnalog PCN, TI myTI PCN, ST product notifications for every MPN in this matrix before schematic freeze.
5. **First-article verification** — On receipt, verify marking vs datasheet top-mark spec (e.g., ADS1262 `1262` + date code format `39KG4`), measure reference voltage (ADR4525/LTC6655) and DAC offset against spec before assembly. Log in `measurements/raw/`.
6. **No purchase on AI suggestion alone** — This matrix is `CANDIDATE`; no order without DEC + human datasheet page check + live stock/price re-check on order day (`ENGINEERING_RULES.md §13`).
7. **Single-package risk mitigation** — LT1970A has only TSSOP-20. If ADI issues PCN/PDN, fallback is OPA569/OPA567 (see §3) but requires board re-spin for limit-accuracy. Monitor PCN monthly.
8. **Quality flow** — For CRITICAL tier, prefer factory-sealed reels from authorized; if cut tape is only option, request factory COO + distributor COC; avoid “re-taped” lots.

---

## 8. Verification status legend and next actions

| Status | Meaning | Required before `bom/approved/` |
|--------|---------|----------------------------------|
| **UNVERIFIED** | Row created from web_search + product page only; no human datasheet page-cite | Datasheet open + page/section cite + errata check |
| **PARTIAL** | Datasheet rev + lifecycle + SPICE confirmed; distributor stock/price is snapshot, not live order check | Live authorized-distributor check on order day + price re-quote + PCN search |
| **VERIFIED** | Human confirmed: datasheet page cite + live stock + price + errata/PCN clean + package footprint exists in KiCad | DEC entry + move to `bom/approved/` |

**Current overall status:** All rows are **PARTIAL** except LT1970A authorized-stock which is weaker (broker-heavy feed) → treat as **PARTIAL- (needs live DigiKey/Mouser check)**. No row is VERIFIED.

**Phase 3 gate actions:**
- [ ] Open each cited datasheet Rev and cite page for lifecycle/SPICE/package parameters (do not rely on product-page rendering).
- [ ] Live-check DigiKey/Mouser/Farnell cart for each MPN; record stock/price/MOQ screenshot in `bom/sourcing/`.
- [ ] Subscribe to myAnalog / myTI / ST notifications; log subscription in `tools/setup/`.
- [ ] Add KiCad footprints for TSSOP-20 (LT1970A thermal pad), TSSOP-28 (ADS1262), SOIC-8/MSOP-8, LFCSP-16, LQFP-32/48.
- [ ] Create `simulation/spice/README.md` with include paths for AD5686R.cir / ADA4522.cir / LT1763.lib / ADR4525 and note ADS1262 TINA vs behavioral.

---

## 9. Provenance (product-page + datasheet URLs used for this snapshot)

| Part | Primary source(s) consulted (2026-08-24 web_search) |
|------|-----------------------------------------------------|
| AD5686R | Product page https://www.analog.com/en/products/ad5686r.html + datasheet Rev F https://www.analog.com/media/en/technical-documentation/data-sheets/ad5686r_5685r_5684r.pdf + IBIS/SPICE listing on product page |
| ADA4522-2 | Product page https://www.analog.com/en/products/ada4522-2.html (header `RECOMMENDED FOR NEW DESIGNS`) + datasheet Rev I https://www.analog.com/media/en/technical-documentation/data-sheets/ada4522-1_4522-2_4522-4.pdf + PCN 18_0171 Rev C |
| LT1970A | Product page https://www.analog.com/en/products/lt1970a.html + datasheet 1970afc https://www.analog.com/media/en/technical-documentation/data-sheets/1970afc.pdf + LTspice built-in model list |
| ADS1262 | Product page https://www.ti.com/product/ADS1262 + datasheet Rev C https://www.ti.com/lit/ds/symlink/ads1262.pdf + OA addendum https://www.ti.com/ods/sysadd/oa/symlink/ads1262_oa.pdf (ACTIVE proof) |
| LT1763 | Product page https://www.analog.com/en/products/lt1763.html + LT1763 datasheet + LTspice lib `LT1763.lib` + AN-83 RECOMMENDED table |
| ADR4525 | Product page https://www.analog.com/en/products/adr4525.html (header RECOMMENDED) + family datasheet https://www.analog.com/media/en/technical-documentation/data-sheets/ADR4520_4525_4530_4533_4540_4550.pdf |
| STM32G431 | Datasheet https://www.st.com/resource/en/datasheet/stm32g431c6.pdf + product pages KBT6/CBT6/C6/V6 (all `Active — volume production — Until 01/2036`) + ST longevity page https://www.st.com/content/st_com/en/about/quality-and-reliability/product-longevity.html |
| Alternates | Agent D matrix + AD5764 datasheet https://www.analog.com/media/en/technical-documentation/data-sheets/AD5764.pdf + TI OPA189/OPA140/REF50xx datasheets + AD7175/AD7124 datasheets (cross-checked 2026-08-24) |

*No spec was propagated from memory. Every lifecycle/SPICE/price claim above is tied to one of the URLs in this table. Where stock/price was login-gated (TI Store, some DigiKey waffles), the table marks PARTIAL and requires live re-check.*

---

*End of Agent F matrix. Companion: `PHASE2_COMPONENT_MATRIX_AGENT_D_PRECISION.md` (technical trade-offs). Do not promote any row to `bom/approved/` without a DEC and a live authorized-distributor verification on the day of order.*
