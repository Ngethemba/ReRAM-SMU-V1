# ReRAM-SMU V1 — Security Review

**Date:** 2026-08-24  
**Scope:** Third-party skills/MCPs/packages/tools examined, installed, rejected; filesystem/network/execution privileges; residual risks.

## 1. Third-party skills examined

| Skill | Source | Trust | Install? | Reason |
|-------|--------|-------|----------|--------|
| `kicad` (`aklofas/kicad-happy/kicad`) | skills.sh → GitHub `aklofas/kicad-happy` | community | **REJECT Phase 0** | Zener DSL mismatch, requires `pcb` CLI + Digikey API, adds attack surface; built-in `pdf`/KiCad CLI suffice. Package manifest would pull Node/Python deps; not audited for this project. |
| `kicad-schematic` (`kenchangh`) | skills.sh | community | REJECT | same mismatch |
| `spice` / `spice-sim` (`aklofas`, `diodeinc/pcb`) | skills.sh | community | REJECT/DEFER | ties to Zener `pcb sim`; portable ngspice + Python wrapper is smaller. |
| `datasheet-reader` (`diodeinc`) | skills.sh | community | DEFER | `pcb scan` Zener-coupled; built-in PDF text extraction + `docs/references/` provenance suffices in Phase 0 |
| `pdf` hub variants (25 hits, `anthropics/skills/pdf` etc.) | skills.sh/clawhub | trusted/community | DEFER | built-in `pdf`/`docx`/`ocr-and-documents` already cover text extraction; no new capability justifies extra dep |
| `python` hub variants | many | community | DEFER | pinned `.venv` + `pytest` already cover engineering Python |

**Security implications of hub skills:** community trust = not audited by Hermes; installs may run `postinstall` scripts, access filesystem (`~/.`), network (download deps, call APIs), and execute `python`/`node`. Rejecting them keeps supply chain to official vendor tools + pinned PyPI deps.

**Installed skills:** only project-local `reram-smu-engineering` (see HERMES_SKILLS.md) — auditable, no network, no `postinstall` scripts.

## 2. MCP servers examined

| MCP | Source | License | Install? | Reason |
|-----|--------|---------|----------|--------|
| Hermes catalog (20: airtable, notion, figma, linear, netlify, vercel, sentry, stripe, supabase, unreal, etc.) | Hermes builtin | — | **REJECT** (not installed) | No KiCad/SPICE relevance; each would request OAuth/network + filesystem per integration; unnecessary for Phase 0. |
| `mixelpixx/KiCAD-MCP-Server` | GitHub | MIT | **DEFER/CANDIDATE** | 1947★, active (pushed 2026-08-20), MIT OK, Python. But source review flags: broad filesystem scope default, subprocess spawns `kicad-cli`/`python`, shell execution paths, and potential for destructive `*.kicad_*` edits without safeguards. Requires scoped `filesystem_root = E:\ReRAM-SMU V1` and allowlisted commands before install. |

**Per-candidate MCP audit (KiCad MCP, checklist from Task 4):**

- README: describes LLM-to-KiCad via MCP stdio, no TLS/network exfiltration by default.
- package manifest: `pyproject.toml` / `requirements.txt` present (to be re-audited on clone).
- startup: stdio server, invoked via `python server.py`.
- filesystem: reads/writes `*.kicad_*` — **must be constrained to `E:\ReRAM-SMU V1`**; reject blanket `C:\`/`E:\`/user profile scope.
- subprocess: spawns `kicad-cli` — **must allowlist**.
- network: none by default (stdio); check no telemetry.
- shell: potential `shell=True` in helpers — flag for review.
- deps: audit via `hermes security` / `osv.dev` on clone.
- issues/releases: active (20 open, 302 forks).
- license: MIT — **PASS**.

**Disposition:** Not installed in Phase 0; no filesystem/network privilege granted; no residual MCP risk.

## 3. Packages/tools with execution privileges

| Tool | Execution | Filesystem | Network | Reason/Review |
|------|-----------|------------|---------|---------------|
| `uv` 0.12.5 | spawns `python`, `pip` compile | `.venv/`, `C:\Users\...\uv\cache` | PyPI (wheels for 119 packages) | Official Astral tool, pinned deps, checksums via wheel metadata. |
| `.venv` deps: numpy, scipy, pandas, matplotlib, sympy, pint, uncertainties, pyvisa, pyserial, pytest, jupyter | Python import-time code | project `E:\ReRAM-SMU V1` only | import-time generally no network; `pyvisa` enumerates resources locally | All official PyPI; `requirements-lock.txt` pins w/ hashes via wheel provenance; no `postinstall` shell scripts. |
| `ngspice_con.exe` 47 portable | spawns as subprocess from Python `run_spice.py` | reads `*.cir`, writes `*.log`/`*.raw` in `tools/setup/smoke-tests/spice/` and future `simulation/` | none | SourceForge official; binary extracted via `7z` from Chocolatey cache (hash verified via Chocolatey nupkg metadata). Not on PATH. |
| `kicad-cli.exe` 10.0.5 | spawns from `subprocess` or shell | reads `*.kicad_*` in `hardware/kicad/` and `tools/setup/smoke-tests/kicad-test/`, writes `erc.json`/`drc.json`/`netlist`/`gerbers` | none | Official KiCad vendor binary, `E:\KiCad\bin\kicad-cli.exe`. |
| `LTspice.exe` 26.0.2.1 | spawns `LTspice -b` | reads `*.net`, writes `*.log`/`*.raw` | none (local sim) | Official ADI installer via winget. |
| `7z.exe` 26.02 | extraction of `ngspice-47_64.7z` | as above | none | Official 7-Zip. |

**Rejected/without privilege:** no `postinstall` Node `npm` packages, no `docker`, no `scoop`.

## 4. Filesystem permissions

- All automation constrained to `E:\ReRAM-SMU V1` (project root). No MCP/tool granted `C:\`, `E:\` root, Documents, Desktop, browser profiles, or credential directories.
- Hermes `computer_use` is available but not used to automate KiCad GUI in Phase 0 — avoids broad desktop automation.
- `.gitignore` excludes `.venv/`, `*.raw`, `*.log`, `build/`, `out/`, `*.key`, `*.pem`, `.env*` (see Git section).

## 5. Network permissions

- PyPI (https) for `uv pip install` — 119 wheels downloaded once; `requirements-lock.txt` freezes.
- No MCP server with network egress installed; Hermes `web` tool is available for primary-source datasheet download when needed (Phase 1+), but not used in Phase 0.
- LTspice updater (`updater.exe`) not invoked; ngspice portable has no telemetry.

## 6. Rejected and why

- Chocolatey system-wide `choco install ngspice` — rejected at runtime due to admin `C:\ProgramData\chocolatey\lib-bad` access denied; portable extraction used instead (smaller privilege).
- Third-party hub skills (kicad-happy family, pdf hub) — rejected for Zener mismatch and supply-chain width.
- All 20 catalog MCPs — rejected for lack of relevance.

## 7. Installed and why

| Installed | Reason | Verification |
|-----------|--------|--------------|
| Python `.venv` + 13 pinned deps | numerical engineering, reproducible | `pytest 6 passed` |
| KiCad 10.0.5 (pre-existing, verified) | schematic/PCB/ERC/DRC | `kicad-cli version`, ERC/DRC JSON |
| ngspice 47 portable | batch headless sim | `ngspice_con -b` 3 netlists |
| LTspice 26.0.2.1 (pre-existing, verified) | vendor-model validation | `LTspice -b` divider |

## 8. Residual risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| PyPI supply-chain for scientific stack | Low | pinned `requirements-lock.txt`, `uv` hash check, no auto-upgrade; revisit with `hermes security` / `pip-audit` before Phase 1 |
| Portable ngspice binary from community cache | Low | from official SourceForge via Chocolatey nupkg cache; no admin; hash via `nupkg.sha512`; future re-download should use official `ngspice.sourceforge.io` |
| KiCad MCP if installed later without scoping | Medium | gate: clone audit, set `filesystem_root=E:\ReRAM-SMU V1`, allowlist `kicad-cli.exe`, test on disposable project |

**No high-severity residual risk in Phase 0.**
