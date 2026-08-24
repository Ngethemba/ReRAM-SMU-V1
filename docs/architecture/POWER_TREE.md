# Power Tree — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**Status:** Conceptual — external ±12 V bench supply baseline (REQ-PWR-002/003). No mains.
**Revision:** Corrected per IR-07 — AD5764 supply compatibility clarified, Options A/B/C defined, negative regulator class corrected.

```
External bench ±12 V (current-limited, 1 A)
          │
    ┌─────┴─────┐
    │ Sequencing│ (ideal diode + RC, no relay yet)
    └─────┬─────┘
          │
 ┌────────┼────────┬──────────┐
 │        │        │          │
 ▼        ▼        ▼          ▼
Source   Prec.    ADC/Ref   Digital
analog   analog   domain    domain
±12→±10  ±12→+5   ±12→+5/3.3 +12→+5→3.3
(LDO)    (LDO)    (LDO)      (Buck+LDO)
LT1763   LT3045   LT1763    STM32 LDO
or 3045  ADR4525  etc       + USB
```

## Rail headroom (conceptual, Phase 3 to size)

- Source stage needs ±5 V + 100 mV burden + dropout (LDO ~300 mV + amp headroom ~1 V) → ±12 V gives ~5–6 V headroom — adequate for LT1970A or composite without high-voltage rail.
- If ±10 V outer ever needed (rejected for V1), ±12 V would be insufficient — reinforces DEC to stay at ±5 V.
- Precision analog (DAC/ADC/ref) needs quietest rail: LT3045 (0.8 µVrms) or LT1763 post-filtered with LC π (10 µH + 2×10 µF) + 10 Ω/100 nF RC for reference.

## LDO choices (conceptual)

- **LT1763** — 0.5 A, 20 µVrms, good PSRR at 100 kHz; proven in Phase 0 tooling list. **Positive regulator only.**
- **LT3045** — 0.8 µVrms ultra-low noise for precision rail (if budget allows). **Positive regulator only.**
- **Negative regulators are NOT LT1763/LT3045** — negative rail requires complementary class: LT1964 / TPS7A30 / LT3091-class (placeholder families, no MPN promotion).

> **AD5764 supply note (IR-07):** AD5764 requires **±11.4 V to ±16.5 V** (Rev F). A ±10 V LDO rail (11.0 V with 300 mV dropout from 12 V, or exact 10.0 V) **cannot** host AD5764. Any document stating "LT1763/LT3045 for ±10 V" for AD5764 is corrected — positive uses LT1763/LT3045-class, negative uses LT1964-class. See Options below.

---

## Power-Tree Options (IR-07 canonical)

### Option A raw ±12 for power stage, regulated only precision low-power blocks (V1 baseline)

- **Power stage (LT1970A)** runs directly from raw external ±12 V (11.4 V spec satisfied with ~0.6 V margin before LDO). No ±10 V LDO in power path.
- Precision rail **+5 V** is post-regulated via LT1763/LT3045 + LC π + RC; bench ripple handled there.
- Simplest for V1 REV-A; AD5764 (if selected) also runs from raw ±12 V — its ±11.4 V minimum is met.
- Negative precision rail (if needed for bipolar DAC/ADC) derived separately or not required if Option A uses raw negative.

### Option B complementary (LT1763 positive + LT1964/TPS7A30 negative) (positive + negative LDO)

- Positive rail via **LT1763/LT3045-class**, **negative rail via true negative regulator class** (e.g., LT1964, TPS7A30, LT3091 — placeholder families, no MPN promotion).
- Requires negative LDO footprint and sequencing (positive before negative or simultaneous, verify with RC/diode).
- Provides lowest ripple for both polarities; adds BOM and thermal.
- Note: Setting LDO to **±10 V is not AD5764-compatible** — if AD5764 is used, regulators must be set to ≥±11.4 V (practically ±12 V raw or ±12 V regulated with dropout accounted) or AD5764 must stay on raw rail.

### Option C separate power vs precision rails for power amplifier vs precision signal chain

- **Power stage (LT1970A)** on raw ±12 V; **precision signal (DAC/ADC/ref/shunt amps)** on post-regulated rails (positive + negative regulators) or on single-supply + charge-pump negative for the DAC alone.
- Isolates switching/large-signal noise of power stage from precision chain.
- Post-regulation can be ±12 V regulated (positive + negative regs) or precision +5 V only with DAC running from raw.

### Regulator-compatibility table (IR-07)

| Rail | Valid regulator class | Invalid (corrected) | AD5764 compatible? |
|------|----------------------|---------------------|-------------------|
| Positive (+5 V, +10 V, +12 V) | LT1763, LT3045, LT1763-class | — | LT1763 OK for +5 V prec; +10 V NOT OK for AD5764 |
| Negative (−5 V, −10 V, −12 V) | LT1964, TPS7A30, LT3091-class | LT1763/LT3045 **cannot** regulate negative | Need LT1964-class ≥−11.4 V |
| AD5764 AVDD/AVSS | Raw ±12 V (Option A) or complementary regulated ≥±11.4 V (Options B/C) | ±10 V LDO | **Only raw ±12 V or ≥±11.4 V regulated** |

---

## Sequencing / reverse current / safe shutdown

- External bench is master — no on-board mains. On power ramp, source amp disabled via pull-down on enable until MCU heartbeat (watchdog). Reverse current from DUT (e.g., charged cap) is shunted by clamp diode to rail + bulk cap — not by regulator. Safe shutdown: bulk cap discharges via bleeder, MCU disables output before rail collapse (brown-out detector).
- For Option B/C with negative LDO, sequence negative rail after positive or verify both ramp within 10 ms to avoid latch-up on bipolar op-amps.

AD5764 ±11.4V min incompatible with ±10V LDO

negative regs not LT1763/LT3045
