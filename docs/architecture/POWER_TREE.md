# Power Tree — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2  
**Date:** 2026-08-24  
**Status:** Conceptual — external ±12 V bench supply baseline (REQ-PWR-002/003). No mains.

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

- **LT1763** — 0.5 A, 20 µVrms, good PSRR at 100 kHz; proven in Phase 0 tooling list.
- **LT3045** — 0.8 µVrms ultra-low noise for precision rail (if budget allows).

## Sequencing / reverse current / safe shutdown

- External bench is master — no on-board mains. On power ramp, source amp disabled via pull-down on enable until MCU heartbeat (watchdog). Reverse current from DUT (e.g., charged cap) is shunted by clamp diode to rail + bulk cap — not by regulator. Safe shutdown: bulk cap discharges via bleeder, MCU disables output before rail collapse (brown-out detector).
