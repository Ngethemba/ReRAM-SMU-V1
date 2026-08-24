# ReRAM-SMU V1 — Agent Instructions

**Audience:** Hermes and any future AI agents working inside this repository.  
**Authority:** This file instructs agent behavior. `ENGINEERING_RULES.md` is the engineering truth; this file is the operational protocol.

---

## Mandatory Pre-Read

Before **any** engineering work, read these five files in order:

1. `PROJECT_CHARTER.md` — purpose, scope, non-goals, success criteria
2. `REQUIREMENTS.md` — confirmed vs provisional vs future; REQ-* identifiers
3. `STATUS.md` — current phase and dashboard
4. `DECISIONS.md` — what has been decided and why
5. `ENGINEERING_RULES.md` — binding engineering rules

Do not begin design, research, or tool installation without completing this pre-read.

---

## Core Prohibitions

- **Never invent component specifications.** If you have not cited a primary manufacturer datasheet, you do not know the spec.
- **Never use primary datasheets from memory.** Re-verify every important parameter in the actual document; record provenance (manufacturer, part, doc title/rev, page/section, URL or `docs/references/` path).
- **Never silently change requirements.** Provisional targets stay provisional until a `DECISIONS.md` entry with evidence promotes them.
- **Never delete `measurements/raw/` data.** Raw is append-only.
- **Do not modify unrelated system files** or scatter project files outside `E:/ReRAM-SMU V1` without explicit user authorization.
- **Do not install tools, skills, or MCP servers without documenting** what, why, and which version in `tools/setup/` and `CHANGELOG.md`.
- **Do not manufacture or order components without explicit user authorization.**

---

## Discipline

- Distinguish **fact** (measured/cited), **calculation** (derived with steps), **assumption** (explicitly stated), and **recommendation** (judgment). Label them.
- Important equations must be independently recalculated; commit the script.
- Simulation is required before PCB where practical — but simulation does not prove low-current performance.
- Resolution ≠ accuracy. Nominal specs ≠ system performance.

---

## Traceability Protocol

- Requirements → Decisions → Evidence must be traceable.
- Architectural decisions go to `DECISIONS.md` **only after adequate evidence** — not on speculation.
- Use REQ-* identifiers when referencing requirements.
- Preserve provenance for every datasheet-derived statement.

---

## Housekeeping

- **After meaningful work:** update `STATUS.md`.
- **Unresolved engineering issues:** append to `OPEN_QUESTIONS.md` (do not silently assume).
- **New decisions with evidence:** append to `DECISIONS.md` using the template there.
- **Risks discovered:** append to `RISKS.md`.
- **Substantial sessions:** append to `docs/research/WORK_LOG.md` (date/time, objective, actions, files changed, evidence examined, unresolved issues, next step).
- Preserve reproducibility: commit scripts, keep tool versions, never hide chain-of-thought as engineering rationale — record only concise, externally useful reasoning.

---

## Safety

- Output **disabled** is the safe state. Every firmware path that touches the output must be reviewed for this invariant.
- First tests use dummy loads / precision resistors. A real ReRAM sample is never the first DUT.
- No direct 230 V mains on the SMU PCB for V1 — flag any proposal that violates this.

---

## Workspace Location

All work remains inside `E:/ReRAM-SMU V1` unless a later task explicitly authorizes otherwise. Do not create files elsewhere.

---

*An agent that follows these rules is a useful junior engineer. One that does not is a liability.*
