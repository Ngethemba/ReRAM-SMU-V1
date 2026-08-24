# ReRAM-SMU V1 — Open Questions

**Purpose:** Explicit parking lot for unresolved engineering issues. Every question here must be resolved or formally deferred by its target phase.  
**Rule:** Agents must add new unresolved issues here rather than silently assuming an answer.
**Priority:** P0 = blocks next phase · P1 = blocks schematic · P2 = blocks PCB · P3 = future/V2

---

## Seed Questions (Phase 0–1)

| # | Question | Priority | Target Phase | Status |
|---|----------|----------|--------------|--------|
| Q-01 | **Final DAC choice** — Is AD5686R the right V1 DAC? Alternatives (reference, INL, settling, availability)? | P0 | Phase 2 | OPEN |
| Q-02 | **Final ADC choice** — Is ADS1262 the right V1 ADC? Alternatives (noise, INL, channels, SPI, cost)? | P0 | Phase 2 | OPEN |
| Q-03 | **Is LT1970A the best V1 output stage?** — Current, thermal, stability into capacitive DUT, alternatives (e.g., OPAx, composite)? | P0 | Phase 2 | OPEN |
| Q-04 | **Compliance architecture** — Series pass vs shunt clamp vs comparator-driven limit? Trip time target? Independent of MCU? | P0 | Phase 2 | RESOLVED (2026-08-24, DEC-011) — research triad regulation vs trip defined; timing <50 µs reg / <5 µs trip; topology deferred to Phase 2 DEC but concept resolved |
| Q-05 | **Current shunt topology** — Values for 6 ranges? Kelvin sensing of shunts? Power/TC tradeoff? Placement (high-side vs low-side)? | P0 | Phase 2 | OPEN — ranges confirmed (DEC-008), values not yet fixed (Phase 3) |
| Q-06 | **Low-current range switching technology** — Reed relay vs signal relay vs analog switch vs photo-MOS? Leakage/charge injection/thermal EMF budget? | P0 | Phase 2 | OPEN — 100 nA leakage 1 pA vs 100 pA discussed (LOW_CURRENT §2.7); choice deferred to Phase 2 |
| Q-07 | **Achievable V1 noise floor** — What does “several nA” mean quantitatively? pA/√Hz target? Averaging strategy? | P0 | Phase 1 | RESOLVED (2026-08-24, DEC-009) — quantified: detection 3σ 1.5–6 pA, quantitative 10σ 5–20 pA, practical MUC≈1 nA @100 nA range (100 mV FS, 10 Hz BW) |
| Q-08 | **Achievable V1 measurement uncertainty** — Per-range accuracy targets? Calibration reference class required? | P0 | Phase 1 | RESOLVED (2026-08-24, REQ-MEAS-007/008 + UNCERTAINTY framework) — accuracy targets ±(0.02–0.3% + offset) provisional; budget framework with GUM |
| Q-09 | **Analog / digital isolation strategy** — Is isolation needed for V1? USB isolation? Supply isolation? Cost/noise tradeoff? | P1 | Phase 2 | OPEN |
| Q-10 | **Grounding architecture** — Star ground point? Analog/digital partition? Return path for compliance loop? | P1 | Phase 2 | OPEN |
| Q-11 | **Guard strategy** — Guard needed for V1 “several nA” floor? Driven guard vs passive guard trace? Connector guard pin? | P1 | Phase 2 | RESOLVED (2026-08-24, DEC-012) — 100 nA guard recommended/required, but triax/electrometer deferred to V2; provision guard-ring copper in V1 |
| Q-12 | **Connector strategy** — FORCE/SENSE connector type? Banana vs BNC vs terminal block vs Kelvin clip? Shield continuity? | P1 | Phase 2 | OPEN — must support guard provision (REQ-DUT-002) |
| Q-13 | **Calibration reference requirements** — What class of DMM/voltage reference is sufficient to calibrate V1? Traceability path? | P1 | Phase 2 | OPEN — calibration philosophy in PHASE1 §11 (6½-digit DMM + 0.01% resistors + 2.5 V ref) |
| Q-14 | **Appropriate PCB layer stack** — 2 vs 4 layer for V1? Layer assignment for guard/shield? Cost vs performance? | P2 | Phase 8 | OPEN |
| Q-15 | **LTspice vs ngspice workflow** — Which simulator is primary? Model availability for LT1970A/ADA4522/ADS1262? Co-sim with Python? | P0 | Phase 0 (next session) | RESOLVED (2026-08-24, DEC-TOOL-002) — hybrid: ngspice primary, LTspice secondary |
| Q-16 | **KiCad automation approach** — Scripting, DRC/ERC automation, BOM generation, version? | P0 | Phase 0 (next session) | RESOLVED (2026-08-24, DEC-TOOL-003) — kicad-cli primary, MCP deferred |
| Q-17 | **Shunt relay drive and protection** — Flyback, sequencing, MCU pin safety? | P1 | Phase 5 | OPEN |
| Q-18 | **Temperature sensor placement and count** — Which nodes need monitoring? Sensor type (NTC, digital)? | P1 | Phase 2 | OPEN — principle confirmed (REQ-SAFE-006) 1 per zone; count deferred |
| Q-19 | **SCPI subset definition** — Which commands are V1-minimum? Error handling? | P1 | Phase 2 | OPEN |
| Q-20 | **Firmware safe-state implementation** — Hardware pull-down vs MCU config vs external supervisor? | P0 | Phase 2 | OPEN |

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
| Q-04 | Compliance architecture | RESOLVED (2026-08-24, DEC-011) — see COMPLIANCE_RESEARCH.md |
| Q-07 | V1 noise floor / several nA | RESOLVED (2026-08-24, DEC-009) — see LOW_CURRENT_MEASUREMENT.md + PHASE1 §6 |
| Q-08 | Measurement uncertainty | RESOLVED (2026-08-24, UNCERTAINTY_BUDGET_FRAMEWORK.md + REQ-MEAS-007/008) |
| Q-15 | LTspice vs ngspice | RESOLVED (2026-08-24, DEC-TOOL-002) — hybrid |
| Q-16 | KiCad automation | RESOLVED (2026-08-24, DEC-TOOL-003) — kicad-cli |
| Q-11 | Guard strategy | RESOLVED (2026-08-24, DEC-012) — 100 nA guard recommended/required, triax V2 |

---

*If you are an AI agent and you encounter an assumption that could be a question, add it here.*
