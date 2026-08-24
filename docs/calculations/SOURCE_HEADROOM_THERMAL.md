# Source Headroom & Thermal — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**External supply:** ±12 V bench, DUT capability ±5 V / ±10 mA, burden 100 mV FS (max).

---

## 1. Headroom

- **Rails:** ±12 V → headroom to ±5 V = 7 V per rail before regulator/loss. After LDO dropout (0.3 V) and amp saturation (~1–1.5 V) → ~5–6 V net — ample.
- **Burden:** 100 mV FS is outside DUT-sense loop (SENSE encloses DUT only, see `KELVIN_SENSE_ARCHITECTURE.md`). Source must supply V_DUT + V_burden → need +5.1 V for +5 V DUT at 10 mA FS (10 Ω shunt). With ±12 V rails, still 5.9 V headroom → OK.
- **If burden were inside SENSE loop** (some topologies), SENSE would correct burden — but then compliance sense point shifts — tradeoff documented in CAUTION 2. V1 keeps burden outside SENSE, headroom budgeted.

## 2. Thermal — amplifier dissipation vs DUT power

**DUT power (what paper quotes):** `P_DUT = V_DUT·I` (50 mW @5 V·10 mA). **NOT** amp dissipation.

**Amp dissipation (what heats package):**

- Sourcing +5 V @+10 mA from +12 V: `Pd = (12 - 5)·0.01 = 70 mW` (+ quiescent ~10 mW) → ~80 mW.
- Sinking +5 V @–10 mA (DUT pushes –10 mA back): low-side absorbs `Pd = (5 - (–12))·0.01 = 170 mW` (worst).
- Short to GND (0 V @10 mA): `Pd = 12·0.01 = 120 mW`.
- Worst-case across quadrants: **70–170 mW**.

For DFN/TSSOP with θJA ~40–90 °C/W (no heatsink) → ΔT ≈ 70 mW·90 = 6.3 °C to 170 mW·40 = 6.8 °C — negligible, no heatsink needed. At 500 mA (LT1970A max) not used, Pd would be 3.5 W — would need heatsink, but V1 caps at 10 mA so not relevant.

**Sensor placement:** Output stage (near power amp), shunt resistor block, voltage reference — 1 per zone (REQ-SAFE-006). No need for MCU ambient sensor beyond reference zone.

## 3. Calculation script

`shunt_range_tradeoff_calc.py` covers burden; headroom/thermal above uses simple `Pd=(Vsupply-Vout)·I` for source, `Pd=(Vout-V- supply)·|I|` for sink. Phase 3 to add SOA derating vs temperature.

