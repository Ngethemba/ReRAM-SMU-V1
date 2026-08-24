# ReRAM-SMU V1 — Engineering Decision Log

**Purpose:** Traceable record of every significant architectural and component decision.  
**Rule:** No provisional architecture is a finalized decision. Decisions are added only after adequate evidence (datasheet, calculation, simulation, or measurement).

---

## Decision Record Format

Each decision uses this template:

```markdown
### DEC-XXX — <Subject>

- **Date:** YYYY-MM-DD
- **Status:** PROPOSED | ACCEPTED | REJECTED | SUPERSEDED
- **Requirement(s):** REQ-... 
- **Alternatives considered:**
- **Evidence examined:**
- **Decision:**
- **Rationale:**
- **Consequences:**
- **Verification status:** UNVERIFIED | SIMULATED | MEASURED | REVIEWED
- **Provenance:** (datasheet citations where applicable)
```

Copy the template for each new decision.

---

## Decisions

### DEC-000 — Workspace Structure and Project Governance

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-GEN-002, REQ-GEN-003
- **Alternatives considered:** Minimal flat structure vs full engineering hierarchy; ad-hoc docs vs numbered requirements.
- **Evidence examined:** Project charter, requirements draft, engineering rules, roadmap with 14 phases.
- **Decision:** Adopt the full hierarchy in `README.md` (docs/hardware/simulation/firmware/software/bom/manufacturing/measurements/tools/archive) with numbered requirements, phase-gated roadmap, and mandatory decision/risk/open-question logs.
- **Rationale:** Traceability and review gates are required for a precision instrument; flat structure would lose provenance.
- **Consequences:** Slightly higher upfront overhead; all future work must remain inside `E:/ReRAM-SMU V1`.
- **Verification status:** REVIEWED (inspected this session)
- **Provenance:** Charter + Engineering Rules v0.1.0

---

### Candidate Architecture — Explicitly NOT Decisions

The following have been **discussed** but are **not decided**. They remain `PROVISIONAL / REQUIRES VERIFICATION` and must not be treated as decisions:

| Candidate | Notes | Required Evidence Before Promotion |
|-----------|-------|--------------------------------------|
| MCU STM32G431 family | Needs clock, ADC/DAC, USB, package review | Reference manual + datasheet, errata |
| DAC AD5686R quad 16-bit | Output range, INL, reference, SPI timing | AD5686R datasheet rev |
| Amp ADA4522-2 zero-drift | Offset, drift, noise, supply range | ADA4522-2 datasheet |
| Power amp LT1970A | Bipolar, current, thermal, stability | LT1970A datasheet |
| ADC ADS1262 precision | Noise, INL, reference, SPI | ADS1262 datasheet |
| Regulator LT1763 | Dropout, noise, PSRR | LT1763 datasheet |
| Reference ADR4525-class | Drift, accuracy, load | ADR4525 datasheet |
| Shunts + relay range switching | Leakage, TC, contact resistance | Shunt + relay datasheets + leakage analysis |

No DEC entry will be created for these until Phase 2 evidence exists. Specs must not be propagated from memory.

---

## Decision Index

| ID | Subject | Status | Date |
|----|---------|--------|------|
| DEC-000 | Workspace structure and governance | ACCEPTED | 2026-08-24 |
| — | (next decision) | — | — |

---

*Append new decisions at the end. Never delete a decision — supersede it with a new DEC entry referencing the old one.*
