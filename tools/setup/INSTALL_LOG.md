# ReRAM-SMU V1 — Install Log

Record of modifications performed during the Phase 0 Tool/Skill/MCP Bootstrap session (2026-08-24). No secrets are included.

## 2026-08-24 17:00 — Python virtual environment (uv)

- **Tool:** Python 3.11 venv via `uv`
- **Action:** create project-local venv + install scientific stack
- **Method:** `uv venv --python 3.11 .venv` then `uv pip install --python .venv` with `UV_LINK_MODE=copy`
- **Version:** CPython 3.11.15 (uv managed), uv 0.12.5
- **Location:** `E:\ReRAM-SMU V1\.venv\` (gitignored)
- **Reason:** Reproducible numerical engineering (transfer-function, Monte Carlo, uncertainty, noise, calibration fitting, measurement handling, instrument control)
- **Result:** PASS — 6 pytest tests passed; `requirements.txt` + `requirements-lock.txt` + `pyproject.toml` committed
- **Rollback:** `rm -rf .venv` then `uv venv` + `uv pip sync requirements.txt`

## 2026-08-24 17:05 — ngspice portable extraction

- **Tool:** ngspice 47.0.0
- **Action:** extract portable binary without admin
- **Method:** Chocolatey cache already contained `ngspice-47_64.7z` at `C:\Users\azrai\AppData\Local\Temp\chocolatey\ChocolateyScratch\ngspice\47.0.0\tools\ngspice-47_64.7z` (download was cached from earlier `choco install` attempt). Extracted with `7z x ngspice-47_64.7z -o"E:\ReRAM-SMU V1\tools\setup\ngspice-portable"`
- **Version:** ngspice-47 (Creation date Aug 11 2026 13:55:25, KLU solver)
- **Location:** `E:\ReRAM-SMU V1\tools\setup\ngspice-portable\Spice64\bin\ngspice_con.exe` (not on system PATH, invoked explicitly)
- **Reason:** `choco install ngspice` failed with lock-file permission (`System.UnauthorizedAccessException: C:\ProgramData\chocolatey\lib-bad` — requires admin). Portable mode avoids system-wide install and preserves reproducibility.
- **Result:** PASS — `--version` and 3 batch netlists (divider, RC, op-amp) succeeded
- **Rollback:** `rm -rf tools/setup/ngspice-portable`

## 2026-08-24 17:05 — 7-Zip verification

- **Tool:** 7-Zip 26.02
- **Action:** verify (already installed via winget earlier, now 26.02)
- **Method:** `winget install --id 7zip.7zip -e --silent` (reported already installed)
- **Version:** 26.02
- **Location:** `C:\Program Files\7-Zip\7z.exe`
- **Reason:** archive extraction for ngspice portable
- **Result:** PASS
- **Rollback:** `winget uninstall 7zip.7zip`

## 2026-08-24 — LTspice (already installed)

- **Tool:** LTspice 26.0.2.1 (Analog Devices)
- **Action:** none — already present; verified
- **Method:** `winget install --id AnalogDevices.LTspice` returned "Successfully installed" then immediate re-invoke reported "No upgrade found" — package was already at latest. InstallLocation `C:\Users\azrai\AppData\Local\Programs\ADI\LTspice\`
- **Version:** 26.0.2.1
- **Reason:** vendor-model validation (complements ngspice)
- **Result:** PASS — batch `*.net` divider produced Operating Point log
- **Rollback:** `winget uninstall AnalogDevices.LTspice`

## 2026-08-24 — KiCad (already installed)

- **Tool:** KiCad 10.0.5
- **Action:** none — already present; verified
- **Method:** `winget install --id KiCad.KiCad` reported "No available upgrade found" — already at 10.0.5. Registry shows `InstallLocation E:\KiCad`.
- **Version:** 10.0.5 (`kicad-cli version` reports 10.0.5)
- **Reason:** schematic/PCB, ERC/DRC, BOM, Gerber
- **Result:** PASS — `kicad-cli sch erc` and `pcb drc` on smoke project succeeded (see SMOKE_TEST_RESULTS.md)
- **Rollback:** `winget uninstall KiCad.KiCad`

## 2026-08-24 — ripgrep (already installed)

- **Tool:** ripgrep 15.2.0
- **Action:** none
- **Method:** `rg --version` already present
- **Result:** PASS

## Not installed (intentionally deferred)

| Tool | Reason for deferral |
|------|---------------------|
| pipx, pnpm, jq, fd, Graphviz, Pandoc, CMake, Ninja, arm-none-eabi-gcc, OpenOCD, STM32CubeIDE/Programmer | Not required for Phase 0 exit criteria; STM32 family is provisional (Q-01/Q-03); installing multi-GB IDE before architecture decision violates minimal-privilege. Documented in TOOL_DECISIONS.md. |

## Admin privilege note

- Chocolatey system-wide install requires admin (`C:\ProgramData\chocolatey\lib-bad` access denied) — not used. Winget LTspice/KiCad upgrades were already installed so no elevation prompt was needed in this session. Portable ngspice avoids elevation entirely.
- `E:` vs `C:` cross-filesystem caused `uv` hardlink failure (`os error 17`) — mitigated with `UV_LINK_MODE=copy` (documented cross-drive).
