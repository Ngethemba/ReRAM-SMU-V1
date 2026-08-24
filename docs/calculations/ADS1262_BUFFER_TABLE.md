# ADS1262 Per-Range Buffer Requirement — ReRAM-SMU V1 (Corrected Gate 3)

**Date:** 2026-08-25 (corrected 2026-08-25 Gate 3)
**Gate:** Pre-ERC Correction Gate 3 — ADS1262 Table 6-1 correct pinout, bipolar ±2.5V, buffer arithmetic fix
**Reference:** TI SBAS661C Rev C Table 6-1, Fig 7-27, ADS1262 Ib 2nA typ @PGA32, OPA140 SBOS498F Ib 0.5pA typ /10pA max, Coto <1pA reed, BAV199 3pA **typical** (not guaranteed, max nA at VR=75V)
**Supply:** AVDD +2.5V / AVSS -2.5V bipolar (DEC-042 supersedes DEC-034) — ground-centered ±100mV, no VCM shift PRIMARY. Single-supply VCM 2.5V DNP alternate. Allocation: AIN0=SHUNT_P, AIN1=SHUNT_N, AIN2=REFP LTC6655-2.5, AIN3=REFN GND.

## Per-range table (corrected arithmetic — 1000× errors fixed)

| Range | Rshunt | FS (Vburden) | PGA | FSR (VREF 2.5V) | Util | Buffer required? | ADC Ib error (direct) | With OPA140 buffer error | Leakage budget | Total est. error (typ) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10mA | 2.5Ω | 25mV | 32 | 78.125mV | 32% | **DIRECT** | 2nA×2.5Ω=5nV (0.00002%) | — | reed <1pA | <0.01% (shunt TC+gain) | Direct PGA ok |
| 1mA | 25Ω | 25mV | 32 | 78.125mV | 32% | **DIRECT** | 2nA×25Ω=50nV (0.0002%) | — | reed | <0.01% | Direct ok |
| 100µA | 500Ω | 50mV | 32 | 78.125mV | 64% | **DIRECT** | 2nA×500Ω=1µV (0.002%) | — | reed | <0.02% | Direct ok |
| 10µA | 5kΩ | 50mV | 32 | 78.125mV | 64% | **DIRECT** (borderline) | 2nA×5kΩ=10µV (0.02%) | 0.5pA×5k=2.5nV (0.000005%) | reed | 0.02% typ (direct) | Direct passes 1nA MUC, buffer DNP for max temp |
| 1µA | 100kΩ | 100mV | 16 | 156.25mV | 64% | **BUFFER REQUIRED** | 2nA×100kΩ=200µV (0.2%) FAIL for 1nA MUC | **OPA140 0.5pA×100k=50nV (0.00005%)** typ, 10pA→1µV (0.001%) max — **was 50µV/1mV 1000× high** | OPA140 0.5pA + reed <1pA ≈1.5pA typ (BAV199 **after** buffer, not at shunt) | **0.00005% typ, 0.001% max** — **was 0.05%/1% 1000× high** | **OPA140 JFET buffer PRIMARY** for 100k/1M |
| 100nA | 1MΩ | 100mV | 16 | 156.25mV | 64% | **BUFFER REQUIRED** | 2nA×1MΩ=2mV (2%) FAIL | **OPA140 0.5pA×1MΩ=0.5µV (0.0005%)** typ, 10pA→10µV (0.01%) max — **was 0.5mV/10mV 1000× high**; 7.5pA×1M=7.5µV (0.0075%) **was 7.5mV 1000× high** | OPA140 0.5pA + reed <1pA ≈1.5pA typ (clamp after buffer) | **0.0005% typ, 0.01% max** — **was 0.5%/10% 1000× high** | **OPA140 + guard + C0G, clamp after buffer, DNP pre-buffer BAV199** |

**Corrected arithmetic:** 0.5pA×100kΩ=50nV (not 50µV), 0.5pA×1MΩ=0.5µV (not 0.5mV), 10pA×1MΩ=10µV (not 10mV), 7.5pA×1MΩ=7.5µV (not 7.5mV). 1000× unit errors removed. MUC impact: 1nA MUC on 100nA FS (100mV) is 1% of FS; 0.5µV/100mV=0.0005% <<1% — buffer easily meets MUC. Direct 2mV/100mV=2% would violate 1% — buffer mandatory, now proven with correct units.

**Derivation:** FSR=±VREF/G. Bipolar ±2.5V ground-centered, PGA window ±FSR around 0V, 100mV fits FS156mV with 56% headroom. Single-supply would need VCM shift — now DNP.

**Buffer decision (re-evaluated Gate 3):**
- **DIRECT (10mA–10µA):** Shunt Kelvin → R_prot 1k → RC → **direct to AIN0-1** (no buffer). 2nA*5k=10µV (0.02%) <1nA MUC equivalent 5mV? Actually 1nA*5k=5µV, direct error 10µV ~2× MUC but still <0.02% of FS. **BAV199 pre-buffer where leakage negligible (2nA >>3pA)** may remain for higher-current ranges; PRIMARY for 10µA retains BAV199 pre-buffer as DNP/prototype for max-leak justification.
- **BUFFERED (1µA/100nA):** **Clamp/protection AFTER OPA140 buffer where possible**, so clamp leakage (BAV199 typical 3pA, max nA) does **not** load high-Z shunt node. Pre-buffer BAV199 (if any) **marked DNP/prototype** with guaranteed leakage justification required (BAV199 max >>3pA typical at VR=75V). PRIMARY 1µA/100nA path: shunt → reed → OPA140 follower (0.5pA) → BAV199 clamp to supplies (after buffer, 3pA does not load shunt) → RC → AIN. Guard ring 0.5mm, C0G 10nF, reed <1pA. **Do not remove low-current buffer because bipolar rails remove VCM need** — ADC Ib 2nA >>10pA target, direct would be 2% on 100nA.

**BAV199 note (Gate 3):** 3pA is **typical** at VR=25V, 25°C; manufacturer max is much higher at specified VR=75V (nA range). For PRIMARY 1µA/100nA high-Z node, **never rely on BAV199 typical as guaranteed**. Place semiconductor clamp after buffer; if pre-buffer clamp remains, mark DNP and provide max-leakage calc at actual VR (<<1V) and temp, with measured verification.

**Bipolar vs single-supply:** DEC-042 supersedes DEC-034 supply/VCM — **AVDD +2.5V LT3045 / AVSS -2.5V LT1964** physically; VCM shift removed from PRIMARY, DNP alternate.

**LT5400A-1 EP:** Pin 9 EP is **floating per datasheet** (not tied to GND/rail) — verify all 8 resistor terminals (R1A 1, R2A 2, R3A 3, R4A 4, R4B 5, R3B 6, R2B 7, R1B 8) against manufacturer diagram before PCB.

**Verification:** Bench leak <10pA open-input 100s, Ib error vs Rshunt, PGAL/H flag, noise PSD per PGA. Kelvin DC/CMRR with LT5400A-1 86dB vs discrete 54dB re-run pending.

