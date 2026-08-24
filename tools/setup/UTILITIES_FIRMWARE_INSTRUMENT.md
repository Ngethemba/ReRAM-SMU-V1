# ReRAM-SMU V1 — Utilities, Firmware Toolchain, Instrument Control

**Date:** 2026-08-24 (Phase 0)

## Utilities (Task 9)

| Utility | Installed | Needed? | Action |
|---------|-----------|---------|--------|
| ripgrep 15.2.0 | YES (`rg`) | YES — codebase search | keep |
| 7-Zip 26.02 | YES | YES — ngspice portable extract | keep |
| jq | NO | YES — JSON (ERC/DRC) inspection via `jq` | DEFER — Python `json.tool` suffices in Phase 0 |
| fd | NO | optional — file find | DEFER — `find`/`search_files` covers |
| CMake / Ninja | NO | firmware build | DEFER until MCU selected |
| Graphviz / Pandoc | NO | docs diagrams | DEFER |

Principle: smallest reliable toolchain. No tool accumulated for its own sake.

## Firmware Toolchain Preparation (Task 10)

STM32G431 is **PROVISIONAL** per Q-01/Q-03/Q-17/Q-18/Q-20. No STM32 toolchain is installed / committed in Phase 0.

| Tool | Required if G431 confirmed | Status Phase 0 |
|------|----------------------------|----------------|
| STM32CubeIDE (~2 GB) | editor + build | DEFER — install after architecture DEC |
| STM32CubeProgrammer | flash | DEFER |
| arm-none-eabi-gcc | build | DEFER — `gcc 6.3.0` present is too old for ARM |
| OpenOCD / ST-LINK tools | debug | DEFER |
| CMake + Ninja | build | DEFER |

Documentation of what exists: registry `HKLM\...\Uninstall` has no STMicroelectronics entry; `where arm-none-eabi-gcc` not found; `C:/ST/` absent — confirmed not installed.

Rationale: installing a multi-GB IDE before Phase 2 architecture review would violate ENGINEERING_RULES minimal-privilege and create unverified assumptions.

Next: In Phase 2 after compliance/shunt/range-switch architecture DECs, install `arm-none-eabi-gcc` via `winget` or `xPack` and document in INSTALL_LOG.md.

## Instrument Control Preparation (Task 11)

Protocol stack: USB CDC / serial / VISA / SCPI-like / future GPIB adapter.

Verification with no hardware:

\`\`\`powershell
.\.venv\Scripts\python.exe tools/scripts/check_instruments.py
# → pyvisa 1.16.2 / pyvisa-py 0.8.1, pyserial 3.5
# → VISA resources (@py): ['ASRL3::INSTR','ASRL4::INSTR'] (serial ports, no SMU yet — graceful)
\`\`\`

\`pyvisa.ResourceManager("@py").list_resources()\` handles absence of instruments — no crash (tested in `software/tests/test_software_infra.py`).

No SMU firmware needs to exist — correct for Phase 0.
