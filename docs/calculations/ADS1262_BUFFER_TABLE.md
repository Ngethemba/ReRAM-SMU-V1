# ADS1262 Per-Range Buffer Requirement — ReRAM-SMU V1

**Date:** 2026-08-25
**Gate:** Pre-ERC Correction Gate 2 — ADS1262 bipolar ±2.5V after DEC-042
**Reference:** TI SBAS661C Rev C Table 7-1, Fig 7-27, ADS1262 Ib 2nA typ @PGA32, OPA140 SBOS498F Ib 0.5pA typ /10pA max, Coto <1pA reed, BAV199 3pA
**Supply:** AVDD +2.5V / AVSS -2.5V bipolar (DEC-042, DEC-034 superseded) — ground-centered ±100mV shunt, no VCM shift PRIMARY. Single-supply VCM 2.5V DNP alternate.

## Per-range table

| Range | Rshunt | FS (Vburden) | PGA | FSR (VREF 2.5V) | Util | Buffer required? | ADC Ib error (direct) | With OPA140 buffer error | Leakage budget | Total est. error (typ) | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10mA | 2.5Ω | 25mV | 32 | 78.125mV | 32% | **DIRECT** | 2nA×2.5Ω=5nV (0.00002%) | — | reed <1pA | <0.01% (shunt TC+gain) | Direct PGA ok, no buffer need |
| 1mA | 25Ω | 25mV | 32 | 78.125mV | 32% | **DIRECT** | 2nA×25Ω=50nV (0.0002%) | — | reed | <0.01% | Direct ok |
| 100µA | 500Ω | 50mV | 32 | 78.125mV | 64% | **DIRECT** | 2nA×500Ω=1µV (0.002%) | — | reed | <0.02% | Direct ok, PGAL margin ok |
| 10µA | 5kΩ | 50mV | 32 | 78.125mV | 64% | **DIRECT** (borderline) | 2nA×5kΩ=10µV (0.02%) | 0.5pA×5k=2.5µV | reed | 0.03% typ, 0.15% max (Ib max) | Direct passes 1nA MUC with margin, buffer DNP provision for max temp |
| 1µA | 100kΩ | 100mV | 16 | 156.25mV | 64% | **BUFFER REQUIRED** | 2nA×100kΩ=200µV (0.2%) FAIL for 1nA MUC | **OPA140 0.5pA×100k=50µV (0.05%)** typ, 10pA→1mV 1% max -> needs guard/binned | OPA140 0.5pA + BAV199 3pA + reed <1pA ≈7.5pA typ | 0.06% typ, 1.1% max (needs temp guard) | **OPA140 JFET buffer PRIMARY** for 100k/1M |
| 100nA | 1MΩ | 100mV | 16 | 156.25mV | 64% | **BUFFER REQUIRED** | 2nA×1MΩ=2mV (2%) FAIL | **OPA140 0.5pA×1MΩ=0.5mV (0.5%)** typ, 10pA→10mV 10% max -> guard mandatory | same 7.5pA typ → 7.5mV? Wait Ib*1M=0.5mV, plus leakage 7.5pA*1M=7.5mV? Actually ADC Ib is isolated by buffer, so only OPA140 Ib + leakage through shunt: 0.5pA*1M=0.5mV, 7.5pA total*1M=7.5mV worst -> need guard to <2pA | 0.5% typ, 8% max without guard → **guard + C0G + no TVS** reduces to <2pA → 0.7% max | **OPA140 + guard ring + BAV199 (not TVS) + reed <1pA** PRIMARY, C0G only |

**Derivation:** FSR=±VREF/G. With VREF 2.5V bipolar, absolute 0.3V headroom not needed for ground-centered — PGA window is ±FSR around 0V, so 100mV fits FS156mV with 56% headroom. For single-supply case, PGAL would clip, requiring VCM shift — now removed from PRIMARY.

**Buffer decision:**
- **DIRECT (10mA–10µA):** No active VCM shift, shunt Kelvin → R_prot 1k → BAV199 (3pA, not TVS 1µA) → RC → direct to AIN0-3. Input current 2nA creates <0.02% error, within 1nA MUC (0.1% of 10µA FS is 10nA, error 10µV/50mV=0.02% → 2nA error 0.02% <0.1% budget). **Keep single-supply VCM topology only as DNP alternate** — PRIMARY is bipolar direct.
- **BUFFERED (1µA/100nA):** OPA140-class low-Ib (0.5pA typ, 10pA max) JFET follower before ADS1262, reed mux <1pA, guard ring 0.5mm exposed copper, stitched inner plane DNP, C0G 10nF, BAV199 clamp 3pA. **Do not remove buffer merely because bipolar rails remove VCM need** — ADC Ib is orders larger than <10pA target. Direct would be 2nA/100nA=2% error on 100nA range, invalid.

**Bipolar vs single-supply:** DEC-042 supersedes DEC-034 analog-supply portion — **AVDD +2.5V via LT3045, AVSS -2.5V via LT1964** physically on 06 sheet; VCM 2.5V level-shift (opamp + divider) removed from PRIMARY, kept as DNP alternate footprint for prototype comparison. Bipolar reduces leakage/complexity, eliminates 2 opamps and divider drift.

**Verification:** Bench leak <10pA open-input 100s, Ib error vs Rshunt scope, PGAL/H flag, noise PSD per PGA.

