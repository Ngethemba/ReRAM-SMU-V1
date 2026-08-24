# ReRAM-SMU V1 — Open Questions

**Purpose:** Explicit parking lot for unresolved engineering issues. Every question here must be resolved or formally deferred by its target phase.  
**Rule:** Agents must add new unresolved issues here rather than silently assuming an answer.
**Priority:** P0 = blocks next phase · P1 = blocks schematic · P2 = blocks PCB · P3 = future/V2

---

## Seed Questions (Phase 0–2)

| # | Question | Priority | Target Phase | Status |
|---|----------|----------|--------------|--------|
| Q-01 | **Final DAC choice** — AD5686R vs AD5764 (±1 LSB) vs others? | P0 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-023) — AD5764-class preferred (post-cal @1 V +8.8% headroom vs AD5686R -11%), AD5686R kept as alternate; needs Phase 3 error-budget sim |
| Q-02 | **Final ADC choice** — ADS1262 vs AD7175/AD7177/AD7124? | P0 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-023) — ADS1262 vs AD7175 both CANDIDATE (noise-free bits @50 Hz, PGA latency); needs NPLC sweep sim |
| Q-03 | **Is LT1970A the best V1 output stage?** | P0 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-014) — LT1970A primary (500 mA, 1% limit, LTspice model) + precision+discrete alternate; needs Phase 3 cap-load sim |
| Q-04 | **Compliance architecture** | P0 | Phase 2 | RESOLVED (2026-08-24, DEC-011/018) — dual continuous+trip/SOA, per-segment/polarity programmable |
| Q-05 | **Current shunt topology** — Values for 6 ranges? Kelvin sensing? Placement? | P0 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-015/016/017) — hybrid shunts 10 mA→1 µA + TIA provision, low-side outside SENSE, range-dependent FS 100→50→25 mV; values still need Phase 3 headroom sim |
| Q-06 | **Low-current range switching technology** | P0 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-015) — reed for 100 nA/1 µA (1 pA leak), PhotoMOS/signal relay for higher; one tech for all rejected |
| Q-07 | **Achievable V1 noise floor** — “several nA” quantified? | P0 | Phase 1 | RESOLVED (2026-08-24, DEC-009) — detection 3σ 1.5–6 pA, practical 1 nA |
| Q-08 | **Achievable V1 measurement uncertainty** | P0 | Phase 1 | RESOLVED (2026-08-24, UNCERTAINTY framework) |
| Q-09 | **Analog / digital isolation strategy** | P1 | Phase 2 | RESOLVED (2026-08-24, DEC-021) — OPTIONAL/RECOMMENDED, footprint provisioned, direct USB ships with warning |
| Q-10 | **Grounding architecture** | P1 | Phase 2 | RESOLVED (2026-08-24, DEC-020) — single continuous plane partitioned, single bridge (not split/star) |
| Q-11 | **Guard strategy** | P1 | Phase 2 | RESOLVED (2026-08-24, DEC-012/022) — 100 nA guard ring provisioned, driven guard on SENSE_HI, triax V2 |
| Q-12 | **Connector strategy** — Banana vs BNC vs triax? | P1 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-022) — banana 4 mm + BNC provision, triax V2; Phase 3 may finalize manufacturer |
| Q-13 | **Calibration reference requirements** | P1 | Phase 2 | OPEN — philosophy in PHASE1/2, but class still needs Phase 2 DEC (pending ADC/DAC choice) |
| Q-14 | **Appropriate PCB layer stack** — 2 vs 4 layer? | P2 | Phase 8 | DEFERRED TO PHASE 8 (Phase 2 provisioning does not decide) |
| Q-15 | **LTspice vs ngspice workflow** | P0 | Phase 0 | RESOLVED (2026-08-24, DEC-TOOL-002) — hybrid |
| Q-16 | **KiCad automation approach** | P0 | Phase 0 | RESOLVED (2026-08-24, DEC-TOOL-003) — kicad-cli |
| Q-17 | **Shunt relay drive and protection** | P1 | Phase 5 | OPEN — flyback/sequencing still needs Phase 3 schematic (break-before-make, coil current) |
| Q-18 | **Temperature sensor placement and count** | P1 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, SOURCE_HEADROOM) — 1 per zone (output stage, shunt block, ref) |
| Q-19 | **SCPI subset definition** | P1 | Phase 2 | OPEN — minimum still TBD (Phase 2 research not yet started) |
| Q-20 | **Firmware safe-state implementation** | P0 | Phase 2 | PARTIALLY RESOLVED (2026-08-24, DEC-018/020 + safe-state analysis) — pull-down + supervisor + output relay open + DAC safe code; needs Phase 3 fault sim |

---

## How to Add a New Question

Append a row:

```markdown
| Q-XX | <Question> | P? | Phase ? | OPEN |
```

When resolved, change `OPEN` → `RESOLVED (YYYY-MM-DD, DEC-XXX)` with a pointer to the decision. Never delete a question.

---

## Resolved

| # | Question | Resolution |
|---|----------|------------|
| Q-04 | Compliance architecture | RESOLVED (2026-08-24, DEC-011/018) |
| Q-07 | V1 noise floor / several nA | RESOLVED (2026-08-24, DEC-009) |
| Q-08 | Measurement uncertainty | RESOLVED (2026-08-24, UNCERTAINTY) |
| Q-15 | LTspice vs ngspice | RESOLVED (2026-08-24, DEC-TOOL-002) |
| Q-16 | KiCad automation | RESOLVED (2026-08-24, DEC-TOOL-003) |
| Q-11 | Guard strategy | RESOLVED (2026-08-24, DEC-012/022) |
| Q-09 | Isolation | RESOLVED (2026-08-24, DEC-021) |
| Q-10 | Grounding | RESOLVED (2026-08-24, DEC-020) |

---

*If you are an AI agent and you encounter an assumption that could be a question, add it here.*
