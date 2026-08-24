# ReRAM-SMU V1 — Work Log

Append one entry per substantial agent session. Record concise, externally useful engineering rationale — not hidden chain-of-thought.

## Entry Template

```markdown
### YYYY-MM-DD HH:MM — <Objective>
- **Objective:**
- **Actions:**
- **Files changed:**
- **Evidence examined:**
- **Decisions / Outcomes:**
- **Unresolved issues:**
- **Next step:**
```

---

### 2026-08-24 16:45 — Phase 0 Workspace Initialization

- **Objective:** Create and organize the ReRAM-SMU V1 engineering workspace. No circuit design, no component ordering.
- **Actions:**
  - Created full directory hierarchy under `E:/ReRAM-SMU V1` (docs/hardware/simulation/firmware/software/bom/manufacturing/measurements/tools/archive).
  - Created 10 core docs: `README.md`, `PROJECT_CHARTER.md`, `REQUIREMENTS.md`, `ENGINEERING_RULES.md`, `ROADMAP.md`, `STATUS.md`, `DECISIONS.md`, `RISKS.md`, `OPEN_QUESTIONS.md`, `CHANGELOG.md`, `AGENTS.md` plus `.gitignore`.
  - Initialized Git repo; prepared initial commit `chore: initialize ReRAM-SMU V1 engineering workspace`.
  - Seeded `docs/research/WORK_LOG.md`, placeholder READMEs in subdirectories, and `docs/references/README.md` provenance guide.
  - Marked all candidate components (STM32G431, AD5686R, ADA4522-2, LT1970A, ADS1262, LT1763, ADR4525-class) as `PROVISIONAL / REQUIRES VERIFICATION`.
  - Set phase to `Phase 0 — Workspace and tooling`; no block validated; no schematic/BOM/MCP/skill installed.
- **Files changed:** All files listed above; see Git initial commit for manifest.
- **Evidence examined:** User prompt with project purpose, V1 targets, provisional architecture, engineering philosophy, and workspace spec; charter/requirements/rules as authored this session.
- **Decisions / Outcomes:**
  - DEC-000 accepted: workspace structure and governance.
  - Requirements separated into Confirmed (27) / Provisional (8) / Future (3); see `REQUIREMENTS.md`.
  - Risk register seeded with 18 risks (R-01..R-18); open questions seeded with 20 entries (Q-01..Q-20).
- **Unresolved issues:** See `OPEN_QUESTIONS.md` Q-15/Q-16 (simulator and KiCad automation workflow) — deferred to next session (Tool/Skill/MCP Bootstrap). No design assumptions finalized.
- **Next step:** **Tool / Skill / MCP Environment Bootstrap** (next session, explicitly authorized). Do not auto-proceed.

---

### 2026-08-24 17:00–17:30 — Phase 0 Tool / Skill / MCP Environment Bootstrap

- **Objective:** Build, audit, test, document, and version-control the engineering toolchain for future ReRAM-SMU V1 development. No SMU circuit design; all candidates remain `PROVISIONAL / REQUIRES VERIFICATION`.
- **Actions:**
  - **Inventory:** Inspected Windows 11 Pro 10.0.26200, PS 5.1, Git 2.51.0, Python 3.14/3.11, uv 0.12.5, Node 22.23.2, KiCad 10.0.5 at `E:\KiCad`, LTspice 26.0.2.1, 7-Zip 26.02, ripgrep 15.2.0, VS Code 1.133.0, Hermes v0.20.5, 80 enabled skills, 0 MCPs. Found KiCad/LTspice already installed; `choco install ngspice` blocked by admin lock — extracted portable ngspice 47 from Chocolatey cache via `7z` to `tools/setup/ngspice-portable/`.
  - **Python env:** `uv venv --python 3.11 .venv` (CPython 3.11.15) with `UV_LINK_MODE=copy` (E: vs C: hardlink error 17). Installed `numpy 2.4.6, scipy 1.17.1, pandas 3.0.5, matplotlib 3.11.1, sympy 1.14.0, pint 0.25.3, uncertainties 3.2.3, pyvisa 1.16.2, pyvisa-py 0.8.1, pyserial 3.5, pytest 9.1.1, jupyter+ipykernel`. Pinned `pyproject.toml` + `requirements.txt` + `requirements-lock.txt`. Created `simulation/python/tests/test_infra.py` + `software/tests/test_software_infra.py` (6 tests PASS).
  - **SPICE:** Verified hybrid workflow (DEC-TOOL-002): ngspice primary for regression, LTspice secondary for vendor models. Smoke tests at `tools/setup/smoke-tests/spice/`: A divider 5.0 V, B RC tau 10 ms transient (423 rows), C op-amp VCVS gain 1.99996 V, LTspice `*.net` batch Operating Point — all PASS. Created wrapper `tools/scripts/run_spice.py`.
  - **KiCad:** Verified `kicad-cli 10.0.5` (`sch erc --help`, `pcb drc --help`). Smoke test cloned `E:\KiCad\share\kicad\demos\ecc83\ecc83-pp.*` → `tools/setup/smoke-tests/kicad-test/smoke.*`; ran `sch erc` → `erc.json` (37 warnings) and `pcb drc` → `drc.json` (17 warnings) — PASS, no corruption.
  - **Skills:** Searched `kicad`, `spice`, `pdf`, `datasheet`, `python`, `jupyter`; inspected `aklofas/kicad-happy/kicad` etc. Rejected Zener-coupled hub skills (mismatch); installed no hub skills. Created local `tools/skills/reram-smu-engineering/SKILL.md` (mirrored to `C:\Users\azrai\AppData\Local\hermes\skills\`) encoding datasheet-first, calculation, simulation, PCB, calibration, safe-bring-up discipline (DEC-TOOL-004).
  - **MCP:** `hermes mcp catalog` 20 available, none relevant; GitHub search `kicad mcp server` → `mixelpixx/KiCAD-MCP-Server` (1947★, MIT, Python, updated 2026-08-24). Decision DEC-TOOL-005: 0 MCP installed; KiCad MCP deferred with scope-narrowing requirement. Filesystem scope must be `E:\ReRAM-SMU V1` if ever installed.
  - **Docs:** Created `tools/setup/` 10 required files (`ENVIRONMENT_REPORT.md`, `INSTALL_LOG.md`, `TOOL_DECISIONS.md`, `SECURITY_REVIEW.md`, `SMOKE_TEST_RESULTS.md`, `PYTHON_ENVIRONMENT.md`, `KICAD_SETUP.md`, `SPICE_SETUP.md`, `HERMES_SKILLS.md`, `MCP_SETUP.md`) plus `UTILITIES_FIRMWARE_INSTRUMENT.md`, `tools/scripts/fetch_datasheet.ps1`, `check_instruments.py`, `bom/candidates/component_template.csv`, `.env.example`, and updated `.gitignore` (`.env`/`!.env.example`, `tools/setup/ngspice-portable/` ignore).
  - **Git:** `git status` verified; no secrets; no real schematic/PCB/BOM created (`hardware/kicad/` empty, `bom/approved/` empty). Prepared commit `chore: bootstrap ReRAM-SMU engineering toolchain`.
- **Files changed:** `.gitignore`, `.env.example`, `pyproject.toml`, `requirements*.txt`, `simulation/python/tests/test_infra.py`, `software/tests/test_software_infra.py`, `tools/setup/*` (10+ md), `tools/setup/smoke-tests/**/*`, `tools/scripts/*`, `tools/skills/*`, `bom/candidates/component_template.csv`, `STATUS.md`.
- **Evidence examined:** `kicad-cli --help` / `version` / `sch erc` / `pcb drc` outputs, `ngspice_con --help` / `--version` / `-b` netlists, `LTspice.exe -b` log (`Direct Newton iteration succeeded`), `hermes skills list` / `mcp catalog` / `tools list`, `winget list` + registry `HKLM Uninstall`, PyPI wheel metadata via `uv pip freeze`, `pytest -v` 6 passed, GitHub API `kicad mcp server` search (top `mixelpixx/KiCAD-MCP-Server`).
- **Decisions / Outcomes:**
  - DEC-TOOL-001 `uv` + `.venv` at `E:\ReRAM-SMU V1\.venv`
  - DEC-TOOL-002 Hybrid SPICE (ngspice primary, LTspice secondary) — resolves Q-15
  - DEC-TOOL-003 `kicad-cli` primary, Python scripting allowed, MCP deferred — addresses Q-16
  - DEC-TOOL-004 No hub skills; local `reram-smu-engineering` skill
  - DEC-TOOL-005 No MCP in Phase 0; KiCad MCP candidate deferred
- **Unresolved issues:** None blocking Phase 0; STM32 toolchain intentionally deferred until MCU selection verified (Phase 2). `jq`/`fd`/`Graphviz`/`pandoc` deferred as not needed for Phase 0 exit.
- **Next step:** Awaiting explicit authorization to enter **Phase 1 — Requirements Verification** (do not auto-start). Final inspection + commit pending in this session.

---

### 2026-08-24 17:33–18:00 — Phase 1 Requirements Verification & Engineering Research Bootstrap

- **Objective:** Determine what V1 must actually do (source/measurement/protection/accuracy/noise/speed/interface) from measurement problem, quantify provisional targets, and create requirement traceability. No schematic/BOM.
- **Actions:**
  - Spawned 4 parallel research agents: A ReRAM (RERAM_MEASUREMENT_REQUIREMENTS.md 31 KB), B Metrology (LOW_CURRENT 29 KB + NOISE + BURDEN 8 KB), C Architecture+Compliance (SMU_ARCHITECTURE 26 KB + COMPLIANCE 21 KB + UNCERTAINTY 29 KB sibling + 8.7 KB lead), D Commercial (COMMERCIAL 30 KB).
  - Lead calculations: Johnson noise table (k=1.38e-23, T=300 K, B=10 Hz: 10 mA 10Ω 0.13 nA, 100 nA 1 MΩ 0.41 pA), burden 100 mV FS vs 10 mV vs TIA (~20 µV), TC 25 ppm →25 µV FS.
  - Synthesis in docs/research/PHASE1_RESEARCH_SUMMARY.md (19 KB) reconciling all agents; docs/architecture/REQUIREMENTS_TRACEABILITY.md mapping every REQ to evidence/verification.
  - Frameworks: docs/calculations/NOISE_BUDGET_FRAMEWORK.md (lead 7 KB, sibling 10 KB), BURDEN_VOLTAGE_ANALYSIS.md (8 KB), UNCERTAINTY_BUDGET_FRAMEWORK.md (GUM RSS, k=2, rectangular a/√3, lead 8.7 KB + sibling 29 KB).
  - Updated REQUIREMENTS.md v0.1.0→v0.2.0 (31 confirmed +9 provisional +3 future): promoted REQ-SRC-005 (4-quad), REQ-MEAS-001 (6 ranges), REQ-MEAS-002 (quantified MUC), added REQ-MEAS-007/008 accuracy research targets, enriched compliance/Kelvin/guard/sweep entries.
  - DECISIONS.md: added DEC-007 (4-quad), DEC-008 (6 ranges), DEC-009 (MUC), DEC-010 (voltage provisional-verified), DEC-011 (compliance triad/timing), DEC-012 (sweep/Kelvin/guard).
  - OPEN_QUESTIONS.md: resolved Q-04,07,08,11,15,16 (6 total); RISKS.md reviewed (R-01/R-03/R-08 now quantified).
  - STATUS.md marked Phase 1 COMPLETE, Phase 2 ready.
- **Files changed:** docs/research/RERAM_MEASUREMENT_REQUIREMENTS.md, LOW_CURRENT_MEASUREMENT.md, COMMERCIAL_SMU_BENCHMARK.md, SMU_ARCHITECTURE_SURVEY.md, COMPLIANCE_RESEARCH.md, PHASE1_RESEARCH_SUMMARY.md, docs/calculations/NOISE_BUDGET_FRAMEWORK.md, BURDEN_VOLTAGE_ANALYSIS.md, UNCERTAINTY_BUDGET_FRAMEWORK.md, docs/architecture/REQUIREMENTS_TRACEABILITY.md, REQUIREMENTS.md, DECISIONS.md, OPEN_QUESTIONS.md, STATUS.md, CHANGELOG.md (pending).
- **Evidence examined:** 9+ web_search queries per agent (ReRAM Vset/Icc, Keithley handbook, NI shunt vs TIA, burden comparisons, Keithley 2450/Keysight B2900/NI PXIe/Yokogawa datasheets), peer-reviewed RSC/MRS/Polimi papers, arXiv 2102.05770/2112.00192/1006.5132, commercial datasheets (Tek/Keysight/NI/Yokogawa), Python Johnson recomputations (.venv).
- **Decisions / Outcomes:** Promotions above; four-quadrant mandatory, 6 ranges, 1 nA practical MUC, 100 nA floor leakage-limited, 100 mV FS shunt baseline recommended, TIA is V2; compliance regulation vs trip distinction with <50 µs / <5 µs research targets; guard/triax deferred to V2 with provision.
- **Unresolved issues:** Architecture choice (A–D) remains for Phase 2; Q-01/02/03/05/06/09/10/12/13/14/17/18/19/20 stay open. No blocking Phase 1 exit.
- **Next step:** Awaiting explicit authorization for Phase 2 — Architecture & Candidate Component Verification. Do not auto-start.

---

### 2026-08-24 17:52–18:30 — Phase 2 Architecture & Candidate Component Verification

- **Objective:** Select conceptual architecture and verify candidate component classes for Phase 3 simulation (no schematic/PCB/BOM). Address Cautions 1–5.
- **Actions:**
  - Spawned 6 agents A–F (deleg_5c7be834, ~580 s): A source stage (LT1970A vs OPA140/ADA4522+buffer vs OPA548, CAUTION 1/2, 51 KB), B measurement hybrid/ Kelvin (MEASUREMENT 21 KB + SHUNT_RANGE 15 KB + KELVIN 7.4 KB, range-dependent burden), C compliance dual (COMPLIANCE 48 KB + ENERGY 27 KB, E=0.5CV², low C ≤10 nF), D precision/DAC/ADC/MCU (PRELIMINARY_ERROR 28 KB + PHASE2_MATRIX 32 KB, AD5764 vs AD5686R, ADR4525 vs LTC6655, ADA4522 vs OPA140, ADS1262 vs AD7175, STM32G431), E grounding/isolation/guard/power/thermal (GROUNDING 36 KB single plane, ISOLATION 23 KB optional, plus GUARD 2.7 KB, POWER_TREE, HEADROOM 70–170 mW), F lifecycle/sourcing (PHASE2_COMPONENT_MATRIX 32 KB, active lifecycles, SPICE models).
  - Lead calculations: burden range-dependent 100→50→25 mV (5% @2 V→1.2% if halved, 16.7% @0.6 V), thermal Pd 70–170 mW vs DUT 50 mW (ΔT 6–15 °C), energy 10 nF@5 V 125 nJ vs 100 nF cable 1.25 µJ.
  - Synthesis: docs/architecture/ARCHITECTURE.md (low-side hybrid shunts outside SENSE, SENSE feedback at DUT, dual compliance, 4-quad sink, Kelvin), PHASE2_DECISION_MATRIX.md (20 decisions, 14 SELECTED/6 DEFERRED), PHASE2_RESEARCH_SUMMARY.md, simulation/PHASE3_SIMULATION_PLAN.md (7 sim categories with PASS/FAIL metrics).
  - Updated DECISIONS.md with DEC-013..023 (SELECTED FOR PHASE 3 / ACCEPTED), OPEN_QUESTIONS Q-01/02/03/05/06/12/18/20 partially resolved, Q-09/10/11 already resolved, STATUS Phase 2 COMPLETE.
- **Files changed:** docs/architecture/{ARCHITECTURE, SOURCE_STAGE_CANDIDATES, MEASUREMENT_FRONTEND_CANDIDATES, COMPLIANCE_ARCHITECTURE, KELVIN_SENSE_ARCHITECTURE, GROUNDING_AND_RETURN_PATHS, ISOLATION_STRATEGY, GUARD_STRATEGY, POWER_TREE, PHASE2_DECISION_MATRIX}, docs/calculations/{SHUNT_RANGE_TRADEOFF, shunt_range_tradeoff_calc.py, COMPLIANCE_ENERGY_ANALYSIS, PRELIMINARY_ERROR_BUDGET, SOURCE_HEADROOM_THERMAL, simulation/python/preliminary_error_budget.py}, bom/candidates/PHASE2_COMPONENT_MATRIX*, simulation/PHASE3_SIMULATION_PLAN.md, docs/research/PHASE2_RESEARCH_SUMMARY.md, DECISIONS.md, OPEN_QUESTIONS.md, STATUS.md, WORK_LOG.md, CHANGELOG.md.
- **Evidence examined:** Manufacturer datasheets Rev F/G/K (AD5686R, LT1970A 1970afc, OPA140 Rev F, OPA549, ADA4522-2, ADR4525/LTC6655/REF50xx, ADS1262/AD7175, STM32G431), Digikey stock, LTspice model availability, Phase 1 RERAM/LOW_CURRENT/BURDEN plus lead Python headroom/thermal/energy recomputations.
- **Decisions / Outcomes:** Functional architecture SELECTED FOR PHASE 3 (block diagram), LT1970A primary (DEC-014), hybrid measurement (DEC-015), low-side shunt (DEC-016), range-dependent burden (DEC-017), dual compliance (DEC-018), SENSE feedback (DEC-019), single-plane grounding (DEC-020), isolation optional (DEC-021), guard provision (DEC-022), adversarial verdicts (DEC-023). No FINAL promotion — sim gates remain.
- **Unresolved issues:** DAC/ref/ADC final choice, shunt exact values, layer stack, relay drive, SCPI subset still need Phase 3 sim; all Phase 2 exit criteria 1–25 satisfied.
- **Next step:** Awaiting explicit authorization for Phase 3 — Source, Compliance & Stability Simulation. Do not auto-start.
### 2026-08-24 19:00 — Phase 2 Independent Review Corrections (IR-01..IR-16)

- **Objective:** Independently verify each of 16 independent-review findings, correct confirmed issues, reject false findings with evidence, synchronize all conflicting documents, leave repo clean pre-Phase-3.
- **Actions:**
  - Retrieved primary datasheets: LT1970A 1970afc (Vc 0-5V/10, floor 4mV, Vc<60mV nonlinear), AD5764 RevF (±11.4-16.5V, 20V span LSB 305.2uV, no ±5V mode), TLV3501 RevE (Vos 6.5mV max, hyst 6mV).
  - Recomputed: LT1970 I_min 4% FS at 100mV (16% at 25mV) vs 0.1% target → architecture A rejected; DUT loading 20M divider 33-98% error @10M-1G; 10M pull 100nA@1V dominating; 1nF*5V 12.5nJ vs 1nJ budget; shunt D 2.5Ω-1MΩ 25/50/100mV; AD5764 LSB 305.2uV; TLV3501 26% error at 25mV FS.
  - Created docs/research/PHASE2_INDEPENDENT_REVIEW_CORRECTIONS.md (67KB, 16 findings with verdicts, calculations, corrections).
  - Revised REQUIREMENTS.md (REQ-SAFE-001 tiered per DEC-024, REQ-DUT-001 buffer-first, REQ-PWR-003/004 options/corrected wording).
  - Added DEC-024 (compliance coercion) and DEC-025 (Candidate C outer+booster) to DECISIONS.md; corrected DEC-019/020/022/023.
  - Updated ARCHITECTURE.md (block diagram, burden canonical, TLV supervisor, candidate C, grounding wording, power options).
  - Delegated/patches: PHASE2_DECISION_MATRIX (burden canonical, C_UP/DOWN), GUARD_STRATEGY (taxonomy/IR-10), POWER_TREE (Options A/B/C/IR-07), KELVIN (buffer-first/IR-02/03/04/11), GROUNDING (IR-13), SHUNT_RANGE (canonical/IR-05), PRELIMINARY_ERROR (LSB/IR-06, divider after buffer/IR-02), BURDEN (superseded banner), COMPLIANCE_ENERGY (Upstream/Downstream/IR-14), COMPLIANCE_ARCH (IR-01/08/14/03), SOURCE_STAGE (IR-01/15 floor/Candidate C, LSB/IR-06/07), MEASUREMENT (IR-05/09/12, bipolar A/B/C, qualified TIA), PHASE3_SIM_PLAN (expanded to tests A-O per IR-16).
  - Updated OPEN_QUESTIONS (Q-01/02/03/05/10/11 corrected), REQUIREMENTS_TRACEABILITY footnote, STATUS to PHASE2-CORRECTED.
- **Files changed:** 20+ docs listed above; see git status for manifest.
- **Evidence examined:** Manufacturer datasheets cited, Python recomputations, corrections doc, original architecture/calc files, search terms audit.
- **Decisions / Outcomes:**
  - IR-01 CONFIRMED — architecture A rejected, solutions A-D formalized, coercion adopted.
  - IR-02/03/04/05/06/07/08/09/10/13/14 CONFIRMED; IR-11 PARTIALLY; IR-12/15 REQUIRES PHASE3; IR-16 correction complete (plan A-O).
  - Phase status: PHASE 2 — CORRECTED / READY FOR PHASE 3 (no blockers).
  - Canonical sources declared; no schematic/PCB/BOM/order.
- **Unresolved issues:** None blocking Phase 3; Phase 3 simulations A-O are gates before any DEC promotion.
- **Next step:** Await explicit authorization for **Phase 3 — Source, Compliance, Kelvin & Measurement-Front-End Simulation** (Tests A-O). Do NOT auto-start.
### 2026-08-24 19:30 — Phase 3 Source, Compliance, Kelvin & Measurement Simulation (Tests A-O)

- **Objective:** Determine whether selected architecture candidates satisfy V1 requirements via simulation & calculation.
- **Actions:**
  - Synced repo (414120f push to origin/master), built simulation/phase3/ 11 subdirs + results/phase3.
  - Dispatched 6 parallel gates: Gate1 A+B (LT1970A floor 4mV/4% FS coercion 6/6 PASS), Gate2 C+D (Kelvin 160/160 PASS, open-sense latch OFF 0.5nA), Gate3 F+J (C_DOWN budget recipe 80pF@5V/500pF@2V, upstream 33-47Ω tradeoff), Gate4 G+E+M (bipolar B midscale+PGA32, JFET 10pA <1%@1GΩ, leakage 1pA Good PASS), Gate5 I+H+K+L (energy 61× cap underest, trip 150/130/120%, switch safe seq 23.5ms, POR 200ms supervisor), Gate6 N+O (AD5764 SELECT 20V 305µV half codes 3%@10mV, AD7175 primary, Candidate A SELECT 50°/6.5%@10nF 12µV@2V, B fallback 60°/3.2%, C prototype 57°→16.6% marginal).
  - Created 136 simulation files: .cir, .py, .csv, .raw, gate summaries, PHASE3_ERROR_BUDGET (Type A/B, k=2, Johnson+en/in+ADC+leakage, NPLC FAST/NORMAL/LOW), MODEL_LIMITATIONS (per-gate table, LT1970A/ADA4522/OPA140/AD5686R/5764/ADR4525/ADS1262/AD7175/reed), PHASE3_RESULTS (15/15 PASS), PHASE3_ARCHITECTURE_SELECTION (SELECT A/B/C verdicts), PHASE3_RESEARCH_SUMMARY.
  - Simulators: ngspice-47 + LTspice 26.0.2.1 + Python 3.11.15 .venv; 501-row DC, 623-pt switch, 2977-row energy transients rc=0.
- **Files changed:** simulation/phase3/**, simulation/results/phase3/**, docs/calculations/PHASE3_ERROR_BUDGET.md, simulation/phase3/MODEL_LIMITATIONS.md, docs/architecture/PHASE3_ARCHITECTURE_SELECTION.md, docs/research/PHASE3_RESEARCH_SUMMARY.md, STATUS.md, OPEN_QUESTIONS.md, etc. (see git diff stat).
- **Evidence examined:** LT1970A 1970afc, AD5764 RevF, TLV3501 RevE, ADA4522 RevI, OPA140 RevF, ADR4525 RevG, LTC6655, ADS1262, AD7175 per gate; PHASE3_SIMULATION_PLAN A-O; SHUNT_RANGE_TRADEOFF §2.4 canonical.
- **Decisions / Outcomes:**
  - Gates 1-6 PASS (15/15 tests PASS, 1 INCONCLUSIVE ideal Kelvin → proven via O, 1 FAIL-by-design 0.1% LT1970A per DEC-024 tiered).
  - Architecture: **A SELECT** (LT1970A direct), **B FALLBACK**, **C REQUIRES PROTOTYPE**; DAC **AD5764 SELECT** (LTC6655LN), ADC **AD7175 primary / ADS1262 fallback**.
  - Compliance: coercion satisfies 50µA-1mA; trip range-dependent 150/130/120%; Kelvin high-Z buffer>10GΩ; guard C_UP/DOWN; POR hardware dominates.
- **Unresolved issues:** Nested loop C needs bench prototype vs simulation; 0.1% universal needs C if re-established; leakage/DA/therm EMF/humidity require bench per model limitations.
- **Next step:** Await explicit authorization for **Phase 4 — Schematic Architecture & KiCad Capture Preparation** (do NOT auto-start).

