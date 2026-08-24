# ReRAM-SMU V1 — Tool Decisions

**Date:** 2026-08-24  
**Authority:** Phase 0 tooling decisions — not SMU architecture decisions. No hardware component is decided.

## DEC-TOOL-001 — Python environment manager (uv vs venv)

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-GEN-001, engineering reproducibility
- **Question:** How to provide a reproducible project-local Python environment for numerical engineering?
- **Alternatives:** (a) stdlib `venv` + `pip`, (b) `uv` (`uv venv` + `uv pip`), (c) conda/mamba, (d) pipx per-tool
- **Evidence:** `uv 0.12.5` already installed; `python 3.11.15` available via uv; `venv` works but is slower and lacks lock semantics; conda not installed, heavier; project root on `E:` while uv cache on `C:` causes hardlink `os error 17` — solved with `UV_LINK_MODE=copy`.
- **Decision:** Use `uv` as primary manager. Create `.venv` at project root with `uv venv --python 3.11`; install via `uv pip install --python .venv`; commit `pyproject.toml` + `requirements.txt` + `requirements-lock.txt`.
- **Rationale:** Fast, lockable, compatible with `pyproject.toml`/`pytest`, handles cross-drive via copy mode, already present.
- **Consequences:** `.venv/` is gitignored; reproducibility via lock file; contributors need `uv` (docs provided).
- **Verification:** `pytest` 6 passed; `requirements-lock.txt` 119 lines.
- **Reversibility:** High — `rm -rf .venv` + recreate with `python -m venv` if needed.

## DEC-TOOL-002 — SPICE workflow (LTspice vs ngspice)

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Requirement(s):** REQ-GEN-001 phase-2 architecture research; OPEN_QUESTIONS Q-15
- **Question:** Which SPICE simulator workflow for ReRAM-SMU V1?
- **Candidates:** ngspice-only, LTspice-only, hybrid
- **Evidence examined:**
  - ngspice 47 via portable `ngspice_con.exe`: batch `-b` works headless, `.control` scripts, `print`/`wrdata`, Python-friendly (wrap via `subprocess`), CI-suitable, KLU solver, KiCad `ngspice.dll` bundled at `E:\KiCad\bin\ngspice.dll`.
  - LTspice 26.0.2.1 via winget: installed at `C:\Users\...\ADI\LTspice\LTspice.exe`, batch `-b *.net` works (Operating Point log), best for vendor-provided Analog Devices/TI models (LT1970A, ADA4522, ADR4525 if provided as LTspice `.lib`), but waveform `.raw` is binary UTF-16 and automation is Windows-only.
  - KiCad integration: KiCad 10 bundles ngspice for interactive sim; both export SPICE netlists.
- **Decision:** **Hybrid workflow: ngspice is primary for automated/regression/batch simulation; LTspice is secondary for vendor-model validation when a manufacturer model is only available as LTspice.**
- **Rationale:** ngspice wins on automation, cross-platform, CI, and Python integration; LTspice wins on vendor model fidelity. Hybrid gives both without committing to one before Phase 2.
- **Advantages:** Regression can run headless on any CI; vendor models still validated.
- **Disadvantages:** Two simulators to maintain; netlist/model portability must be checked per-phase.
- **Reversibility:** High — can drop one later with no schematic impact.
- **Verification:** ngspice: divider 5.000V, RC tau 10ms transient, op-amp gain 1.99996V; LTspice: divider Operating Point 5V equivalent (log verified). Q-15 marked resolved via this decision (see OPEN_QUESTIONS update proposal).

## DEC-TOOL-003 — KiCad automation approach

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Question:** How should Hermes interact with KiCad? (native CLI vs scripting vs MCP)
- **Candidates:** (a) native `kicad-cli` (sch erc/export, pcb drc/export), (b) KiCad Python `pcbnew`/`eeschema` scripting, (c) KiCad MCP server (e.g., mixelpixx/KiCAD-MCP-Server)
- **Evidence:**
  - `kicad-cli` 10.0.5: `sch erc`, `sch export netlist/bom`, `pcb drc`, `pcb export` all work and were smoke-tested on `smoke.kicad_sch/pcb` (37 ERC issues due to missing library — expected for copied demo, but CLI executed; 17 DRC warnings).
  - KiCad Python scripting: available via `E:\KiCad\bin\_pcbnew.dll` + `E:\KiCad\bin\python.exe` (3.11.5) — viable for advanced footprint generation, but not needed for Phase 0.
  - MCP: `mixelpixx/KiCAD-MCP-Server` (1947 stars, MIT, Python, updated 2026-08-24) examined — offers LLM-to-KiCad direct manipulation but requests filesystem scope beyond `E:\ReRAM-SMU V1`, has broad `subprocess`/`file` access, and would add significant attack surface for minimal Phase 0 benefit. No other MCP in Hermes catalog is KiCad-specific.
- **Decision:** **Native `kicad-cli` is the Phase 0 automation path; Python scripting is allowed for future specialized tasks; MCP is evaluated but DEFERRED until Phase 2+ when schematic exists and scoping can be tight.**
- **Rationale:** CLI is official, mature, limited privilege, reproducible, sufficient for ERC/DRC/export. MCP adds risk without measurable Phase 0 value.
- **Disadvantages:** CLI does not yet place components or route — that remains manual until scripting/MCP is revisited.
- **Verification:** ERC/DRC JSON outputs captured; see SMOKE_TEST_RESULTS.md.
- **Reversibility:** High — can add MCP later behind a scoped filesystem root.

## DEC-TOOL-004 — Hermes skill strategy

- **Date:** 2026-08-24
- **Status:** ACCEPTED
- **Question:** Which Hermes skills to install for ReRAM-SMU V1?
- **Candidates inspected:** `skills-sh/aklofas/kicad-happy/kicad` (≈800-line analyzer, requires `pcb`/`diodeinc` toolchain, Zener DSL, `digikey` API), `kicad-schematic`, `spice`, `spice-sim` (`diodeinc/pcb`), `datasheet-reader`, `pdf` (anthropics/openai), `python` variants, `jupyter`
- **Evidence:** `kicad-happy` skills assume Zener language and `pcb scan/sim` commands not used in this KiCad-native project; they pull `digikey`/`mouser`/`lcsc` handoffs that require API keys and add conceptual overhead. Built-in `pdf`, `docx`, `xlsx`, `arxiv`, `grounded-citations` already provide PDF/text handling. No skill provides authoritative datasheet citation — that remains a human/agent discipline per ENGINEERING_RULES 2.1–2.4.
- **Decision:** **Install no third-party skills in Phase 0; instead create a project-local skill `reram-smu-engineering` that encodes datasheet-first, calculation-verification, simulation-gate, uncertainty-budget, PCB-review-gate, and safe-bring-up discipline.**
- **Rationale:** Minimizes dependency sprawl and supply-chain risk; project skill is narrow, auditable, and does not encode unverified component claims (AD5686R/LT1970A etc. stay provisional).
- **Consequences:** Team relies on built-in PDF/web tools + project skill; can add a vetted community skill later if a concrete need appears.
- **Verification:** Local skill directory created; no `hermes skills install` executed in this session (intentional).
- **Reversibility:** High.

## DEC-TOOL-005 — MCP selection

- **Date:** 2026-08-24
- **Status:** ACCEPTED (with deferral)
- **Question:** Should any MCP server be installed in Phase 0?
- **Candidates:** Hermes catalog (20 servers: airtable, notion, figma, etc. — none KiCad/SPICE-specific) + GitHub search `kicad mcp server` (top: `mixelpixx/KiCAD-MCP-Server`, 1947★, MIT, Python, 20 open issues, 302 forks, active)
- **Evidence:** Catalog is productivity-oriented; KiCad-MCP server review (see SECURITY_REVIEW.md) — MIT license, active, but filesystem scope would need to be `E:\ReRAM-SMU V1` scoped and currently is not; subprocess execution present; no narrow-scope fork available; Hermes `computer_use` tool already provides safe background desktop control for KiCad GUI if needed.
- **Decision:** **No MCP installed in Phase 0. KiCad MCP is documented as DEFERRED/CANDIDATE for Phase 2 with required scope narrowing and re-audit.**
- **Rationale:** Phase 0 has no schematic to automate; adding an MCP would increase privilege without value.
- **Verification:** `hermes mcp list` shows 0 servers — intentional.
- **Reversibility:** High.

## Summary

| ID | Subject | Decision |
|----|---------|----------|
| DEC-TOOL-001 | Python manager | `uv`, `.venv` at `E:\ReRAM-SMU V1\.venv` |
| DEC-TOOL-002 | SPICE workflow | Hybrid: ngspice primary, LTspice secondary |
| DEC-TOOL-003 | KiCad automation | `kicad-cli` primary; MCP deferred |
| DEC-TOOL-004 | Skills | No third-party; local `reram-smu-engineering` |
| DEC-TOOL-005 | MCP | None in Phase 0; KiCad MCP candidate deferred |
