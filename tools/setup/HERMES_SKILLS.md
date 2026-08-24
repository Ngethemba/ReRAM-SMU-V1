# ReRAM-SMU V1 — Hermes Skills

**Date:** 2026-08-24  
**Hermes:** v0.20.5 — 72 builtin + 8 local = 80 enabled, 0 disabled, 0 hub-installed (`hermes skills list`)

## 1. Discovery

Searches performed: `kicad`, `spice`, `pdf`, `datasheet`, `electronics`, `python`, `jupyter` via `hermes skills search`.

### Candidate skills (hub)

| Skill | Source | Trust | Identifier | Summary |
|-------|--------|-------|------------|---------|
| kicad | skills.sh from aklofas/kicad-happy | community | `skills-sh/aklofas/kicad-happy/kicad` | KiCad project analyzer for .kicad_sch/pcb, Gerber, netlist, DRC/ERC, power-tree. Requires `pcb` CLI + Zener DSL, 800+ line report workflow. |
| kicad-schematic | kenchangh/kicad-schematic | community | `skills-sh/kenchangh/kicad-schematic/kicad-schematic` | Schematic-focused variant |
| spice | aklofas/kicad-happy/spice | community | `skills-sh/aklofas/kicad-happy/spice` | SPICE testbench generator on top of kicad analyzer; consumes analyzer JSON, runs ngspice/LTspice/Xyce |
| spice-sim | diodeinc/pcb | community | `skills-sh/diodeinc/pcb/spice-sim` | Zener `pcb sim` ngspice testbench for `.zen` designs |
| datasheet-reader | diodeinc/pcb | community | `skills-sh/diodeinc/pcb/datasheet-reader` | `pcb scan <pdf/url>` → cached Markdown, for device datasheets |
| bom, jlcpcb, lcsc | kicad-happy | community | — | BOM enrichment / fab ordering |
| pdf (anthropics/openai, 25 hits) | skills.sh / trusted | trusted/community | `skills-sh/anthropics/skills/pdf` etc. | PDF read/create/review |
| python / jupyter variants | many | community | — | generic Python guidance, Jupyter Live Kernel (`nousresearch/hermes-agent/jupyter-live-kernel`) |

### Built-in skills already covering needs

- `pdf` (builtin productivity) + `docx` + `xlsx` + `ocr-and-documents` — textual PDF handling
- `arxiv` — academic paper discovery
- `grounded-citations` — citation discipline
- `engineering-workspace` / `task-orchestration` — project scaffolding
- `github-*` / `codebase-inspection` — repo/CI inspection
- `systematic-debugging`, `test-driven-development`, `hermes-agent-skill-authoring` — dev hygiene

## 2. Evaluation (per-instruction: source, capabilities, overlap, security)

- **kicad-happy family:** audit shows heavy coupling to `pcb`/`diodeinc` toolchain and Zener DSL (`*.zen`), not native KiCad S-expr used by ReRAM-SMU V1. Would require installing `pcb` binary, `digikey` API keys (`DIGIKEY_CLIENT_ID`), and adds a non-trivial abstraction layer. Report contract demands `datasheets/` sync and strict review steps — valuable but mismatched for Phase 0 (no schematic). **Reject** for Phase 0 (revisit if team adopts Zener).
- **datasheet-reader / spice-sim:** same Zener coupling — **Defer**.
- **Generic pdf/python/jupyter skills:** overlap with built-in `pdf`/`arxiv` and project Python workflow — **Defer** (built-ins sufficient).
- **Supply-chain:** all hub skills are `community` trust (not `trusted`), pull from external GitHub repos, request filesystem/network. Minimal-privilege rule prefers fewer unpinned community skills.

## 3. Decision (DEC-TOOL-004)

**Install no third-party hub skills in Phase 0.** Instead create a **project-local skill `reram-smu-engineering`** that encodes the engineering rules without unverified component claims.

### Rejected

| Skill | Reason |
|-------|--------|
| kicad, kicad-schematic, spice, spice-sim, datasheet-reader, bom, jlcpcb | Zener DSL mismatch, API-key overhead, no Phase 0 schematic to analyze |
| pdf hub variants (25) | Built-in `pdf`/`docx`/`ocr-and-documents` already cover PDF text extraction; no new capability |
| python hub variants | Project already has pinned scientific Python + `pytest`; built-ins cover guidance |

### Deferred (revisit Phase 2)

- `kicad-happy/kicad` if a real schematic exists and automated design-review proves valuable.
- A vetted `pdf` hub skill if built-in extraction hits limits on scanned image-heavy datasheets (then prefer `ocr-and-documents` path).

### Installed

- **(local) `reram-smu-engineering`** — see below. No `hermes skills install <hub-id>` executed (intentional).

## 4. Custom project skill — `reram-smu-engineering`

**Location:** `tools/skills/reram-smu-engineering/SKILL.md` (project-local) and mirrored to Hermes local skills `C:\Users\azrai\AppData\Local\hermes\skills\reram-smu-engineering\SKILL.md` for Hermes discovery.

**Purpose:** Enforce datasheet-first validation, calculation verification, simulation gates, uncertainty budgeting, precision-PCB rules, provenance, design-review gates, and safe bring-up — without encoding AD5686R/LT1970A/etc. as mandatory.

**What it does:**

- Workflow checklists for datasheet citation (manufacturer | MPN | doc title/rev/date | page/section | URL or `docs/references/<file>.pdf`)
- Calculation recalculation gate (commit Python script under `docs/calculations/` or `simulation/python/`)
- Simulation gate (ngspice primary, LTspice secondary; store in `simulation/spice/` + `simulation/results/` with tool version)
- PCB review gate (ERC 0 errors, DRC 0, leakage/guard review, no mains)
- Calibration gate (dummy-load first, uncertainty budget, raw append-only)
- Output-disabled safe-state invariant and bring-up order
- Traceability template `Requirements → Decisions → Evidence`

**What it does NOT do:**

- No component specs from memory; no `STM32G431/AD5686R/ADA4522/LT1970A/ADS1262/LT1763/ADR4525` defaults.
- No hidden chain-of-thought; only concise externally useful rationale.
- No duplication of `AGENTS.md` — references it.

## 5. Next step

Phase 1 — if a need for automated datasheet table extraction or schematic BOM enrichment arises, re-evaluate `pcb scan` / `kicad-happy` against the narrow task and document why built-ins are insufficient before installing.
