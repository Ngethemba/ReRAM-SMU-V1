# ReRAM-SMU V1 — KiCad Setup

**Date:** 2026-08-24  
**Version:** KiCad 10.0.5 (`kicad-cli version` confirms 10.0.5)  
**InstallLocation:** `E:\KiCad\` (registry `HKLM\...\Uninstall\ KiCad 10.0`)  
**Binaries:** `E:\KiCad\bin\kicad.exe`, `E:\KiCad\bin\kicad-cli.exe` (2 698 592 bytes), `E:\KiCad\bin\ngspice.dll`, embedded `python.exe 3.11.5`

## 1. Capability

| Capability | Status | Method |
|------------|--------|--------|
| Schematic capture | PASS | `kicad.exe` GUI; file `*.kicad_sch` (S-expr, version 20231120) |
| PCB layout | PASS | `pcbnew` via GUI; `*.kicad_pcb` |
| ERC | PASS | `kicad-cli sch erc <input> --output erc.json --format json` (smoke ran) |
| DRC | PASS | `kicad-cli pcb drc <input> --output drc.json --format json` (smoke ran) |
| BOM generation | PASS | `kicad-cli sch export bom` / `netlist` / `python-bom` (CLI advertises) |
| Netlist inspection | PASS | `sch export netlist` |
| Gerber generation | PASS (deferred) | `pcb export gerbers` (CLI advertises; not exercised in Phase 0) |
| Scripting/automation | PASS (CLI primary) | `kicad-cli` + KiCad Python (`_pcbnew.dll`, `_eeschema.dll`, `kipython`) |
| Footprint/symbol handling | PASS | `fp` subcommand, library at `E:\KiCad\share\kicad\{footprints,symbols}` |
| Hierarchy | PASS | demo `complex_hierarchy` exists |
| Version management | PASS | winget `KiCad.KiCad`; project files version 20231120 |

## 2. Automation approach (DEC-TOOL-003)

- **Primary:** native `kicad-cli` — official, minimal privilege, reproducible.
- **Secondary (allowed):** KiCad Python scripting via `E:\KiCad\bin\python.exe` for footprint generation or batch tweaks.
- **MCP:** evaluated (`mixelpixx/KiCAD-MCP-Server`) but **DEFERRED** — insufficient scoping, adds attack surface with no Phase 0 schematic to automate. See `MCP_SETUP.md` / `SECURITY_REVIEW.md`.

## 3. Smoke test (disposable, not ReRAM-SMU design)

**Location:** `tools/setup/smoke-tests/kicad-test/`  
**Source:** copied `E:\KiCad\share\kicad\demos\ecc83\ecc83-pp.{kicad_pro,kicad_sch,kicad_pcb}` → `smoke.{pro,sch,pcb}`

Commands (quoted for space in path):

```powershell
"E:\KiCad\bin\kicad-cli.exe" sch erc "E:\ReRAM-SMU V1\tools\setup\smoke-tests\kicad-test\smoke.kicad_sch" --output "E:\ReRAM-SMU V1\tools\setup\smoke-tests\kicad-test\erc.json" --format json
"E:\KiCad\bin\kicad-cli.exe" pcb drc "E:\ReRAM-SMU V1\tools\setup\smoke-tests\kicad-test\smoke.kicad_pcb" --output "E:\ReRAM-SMU V1\tools\setup\smoke-tests\kicad-test\drc.json" --format json
```

Results:

- `erc.json` — 37 issues, all `warning`/`lib_symbol_issues`/`footprint_link_issues` due to missing copied-demo libraries (expected) — but CLI executed, produced valid JSON schema `https://schemas.kicad.org/erc.v1.json`, `kicad_version 10.0.5`, no crash, file reopenable.
- `drc.json` — 17 violations (`silk_edge_clearance`, `lib_footprint_issues`) — warnings only, JSON schema `drc.v1.json`, no crash.

**Evidence preserved:** `erc.json`, `drc.json` in smoke-test directory (not deleted).

## 4. Reproducibility

- KiCad 10.0.5 is latest stable per winget/chocolatey (10.0.5 approved). No upgrade needed.
- Project will live at `hardware/kicad/` (currently empty — correct for Phase 0, no schematic created).
- `*.kicad_prl`, `*-backups/`, `fp-info-cache`, `*.lck`, `~*.kicad_sch/pcb` are gitignored via `.gitignore`.

## 5. Next steps (Phase 2+)

- Define footprint/symbol library curation under `hardware/symbols/` and `hardware/footprints/` when architecture is chosen.
- Revisit MCP only if bulk symbol/footprint placement automation proves worthwhile and a narrow-scope fork exists.
