# ReRAM-SMU V1 — Environment Report

**Date:** 2026-08-24  
**Phase:** Phase 0 — Workspace and Tooling (tooling session)  
**Scope:** Tooling only — no circuit design. All candidate SMU components remain `PROVISIONAL / REQUIRES VERIFICATION`.

## 1. Summary

| Tool | Version | Path | Purpose | Status | Verification |
|------|---------|------|---------|--------|--------------|
| Windows | 11 Pro 10.0.26200 | — | OS | PASS | `Get-CimInstance Win32_OperatingSystem` |
| PowerShell | 5.1.26100.9168 | `powershell.exe` | automation | PASS | `Get-CimInstance` executed |
| Git | 2.51.0.windows.2 | `C:\Program Files\Git\cmd\git.exe` / `/mingw64/bin/git` | version control | PASS | `git --version` |
| Python (system) | 3.14.0 | `C:\Python314\python.exe` | available | PASS (not primary) | `python --version` |
| Python (project) | 3.11.15 | `E:\ReRAM-SMU V1\.venv\Scripts\python.exe` | scientific env | PASS | `pytest 6 passed` |
| uv | 0.12.5 | `C:\Users\azrai\AppData\Local\hermes\bin\uv` | venv manager | PASS | `uv --version` |
| pipx | not installed | — | optional | DEFER | not required |
| Node.js | v22.23.2 | — | hermes / tooling | PASS | `node --version` |
| npm | 12.0.2 | — | package manager | PASS | `npm --version` |
| pnpm | not installed | — | optional | DEFER | — |
| CMake | not installed | — | firmware build | DEFER | deferred until MCU selection |
| Ninja | not installed | — | firmware build | DEFER | — |
| GCC (MinGW) | 6.3.0 (MinGW.org) | — | legacy | DEFER | too old for arm; use arm-none-eabi-gcc later |
| arm-none-eabi-gcc | not installed | — | STM32 firmware | DEFER | deferred (see FIRMWARE notes) |
| KiCad | 10.0.5 | `E:\KiCad\bin\kicad.exe` + `kicad-cli.exe` | schematic/PCB, ERC/DRC | PASS | `kicad-cli version` 10.0.5, ERC/DRC smoke ran |
| ngspice | 47 (2026-08-11 build) | `E:\ReRAM-SMU V1\tools\setup\ngspice-portable\Spice64\bin\ngspice_con.exe` | automated simulation | PASS | `ngspice_con --version`, divider 5V, RC transient, op-amp 2x |
| LTspice | 26.0.2.1 | `C:\Users\azrai\AppData\Local\Programs\ADI\LTspice\LTspice.exe` | vendor-model validation | PASS | `winget list LTspice`, batch netlist succeeded |
| STM32CubeIDE | not installed | — | STM32G431 provisional | DEFER | deferred until architecture Phase 2 |
| STM32CubeProgrammer | not installed | — | — | DEFER | — |
| OpenOCD / ST-LINK | not installed | — | — | DEFER | — |
| VS Code | 1.133.0 | `code` | editor | PASS | `code --version` |
| Hermes Agent | v0.20.5 (upstream 057dcdf2) | `C:\Users\azrai\AppData\Local\hermes\hermes-agent` | agent orchestration | PASS | `hermes --version` |
| ripgrep | 15.2.0 | `rg` | code search | PASS | `rg --version` |
| jq | not installed | — | JSON utility | DEFER | optional |
| 7-Zip | 26.02 | `C:\Program Files\7-Zip\7z.exe` | archives | PASS | `7z` |
| Hermes built-in tools | enabled: web, browser, terminal, file, code_execution, vision, tts, skills, todo, memory, session_search, clarify, delegation, cronjob, computer_use | — | agent tools | PASS | `hermes tools list` |
| Hermes skills | 72 builtin + 8 local (80 enabled) | — | workflow skills | PASS | `hermes skills list` |
| MCP servers | 0 configured | — | automation | DEFER | evaluated, none installed (see MCP_SETUP.md) |
| Scientific Python | numpy 2.4.6, scipy 1.17.1, pandas 3.0.5, matplotlib 3.11.1, sympy 1.14.0, pint 0.25.3, uncertainties 3.2.3, pyvisa 1.16.2, pyvisa-py 0.8.1, pyserial 3.5, pytest 9.1.1, jupyter+ipykernel | `E:\ReRAM-SMU V1\.venv` | engineering calculations | PASS | 6 pytest tests passed |
| KiCad MCP | evaluated, deferred | — | agent automation | DEFER | see TOOL_DECISIONS.md |

**Overall Phase 0 toolchain status:** `PASS — minimum viable toolchain ready, STM32 toolchain intentionally deferred`.

## 2. Path Handling

Project root contains a space: `E:\ReRAM-SMU V1`. All smoke tests and scripts quote the path. `uv` with `UV_LINK_MODE=copy` is used because `E:` and `C:` are different filesystems — hardlink mode fails across drives (documented in INSTALL_LOG.md). No tool has failed solely due to the space.

## 3. Notes

- KiCad is installed at `E:\KiCad` (not `C:\Program Files\KiCad`) — discovered via registry `HKLM\...\Uninstall`. Winget reports `KiCad.KiCad 10.0.5` as installed.
- ngspice is not on `PATH`; portable extraction is used at `tools/setup/ngspice-portable/` to avoid admin-chocolatey lock failure (see INSTALL_LOG.md, SECURITY_REVIEW.md).
- LTspice on Windows stores user data with UTF-16 raw files; batch `*.net` netlists work in headless mode via `LTspice.exe -b`.
- ARM toolchain deferred: `STM32G431` is provisional per OPEN_QUESTIONS Q-01; installing 1–2 GB CubeIDE before architecture decision would violate minimal-privilege principle.
