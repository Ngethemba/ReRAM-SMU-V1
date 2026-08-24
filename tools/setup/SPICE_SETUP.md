# ReRAM-SMU V1 — SPICE Setup

**Date:** 2026-08-24  
**Decision:** DEC-TOOL-002 — Hybrid: **ngspice primary (automated/regression)**, **LTspice secondary (vendor-model validation)**

## 1. ngspice (primary)

| Field | Value |
|-------|-------|
| Version | ngspice-47 (KLU Direct Linear Solver, build Aug 11 2026 13:55:25) |
| Binary (portable) | `E:\ReRAM-SMU V1\tools\setup\ngspice-portable\Spice64\bin\ngspice_con.exe` (console) and `ngspice.exe` |
| Also bundled | `E:\KiCad\bin\ngspice.dll` (KiCad interactive sim) |
| Install method | Portable extraction from Chocolatey cache `ngspice-47_64.7z` via `7z` to `tools/setup/ngspice-portable/` — avoids admin lock (`C:\ProgramData\chocolatey\lib-bad` requires admin) |
| CLI | `ngspice_con.exe --help` / `-b <file.cir> [-o log]` / `-v` |
| Python integration | `subprocess.run(["E:/.../ngspice_con.exe","-b",path])` — no pip dep |
| Model compat | SPICE 3f5, behavioral `B` sources, `LAPLACE`, subcircuits |

**Automation examples:**

```powershell
& "E:\ReRAM-SMU V1\tools\setup\ngspice-portable\Spice64\bin\ngspice_con.exe" -b "E:\ReRAM-SMU V1\tools\setup\smoke-tests\spice\test_A_divider.cir"
& "E:\ReRAM-SMU V1\.venv\Scripts\python.exe" tools/scripts/run_spice.py simulation/spice/my_circuit.cir
```

**Python wrapper (`tools/scripts/run_spice.py`):**

```python
import subprocess, pathlib
NGSPICE = pathlib.Path(r"E:\ReRAM-SMU V1\tools\setup\ngspice-portable\Spice64\bin\ngspice_con.exe")
def run(cir: pathlib.Path, extra_args=None):
    return subprocess.run([str(NGSPICE), "-b", str(cir)] + (extra_args or []), capture_output=True, text=True, timeout=60)
```

## 2. LTspice (secondary)

| Field | Value |
|-------|-------|
| Version | 26.0.2.1 (Analog Devices) |
| Binary | `C:\Users\azrai\AppData\Local\Programs\ADI\LTspice\LTspice.exe` |
| Install | `winget install --id AnalogDevices.LTspice -e --silent` (already installed, winget reports "No upgrade found") |
| CLI batch | `LTspice.exe -b <file.net>` — creates `<file>.log` and `<file>.raw` (binary, UTF-16) |
| Model compat | Excellent for ADI/LT models (LT1970A etc. if `.lib` provided), but Windows-only and raw is not text-parseable without tool |

**Batch example:**

```powershell
& "C:\Users\azrai\AppData\Local\Programs\ADI\LTspice\LTspice.exe" -b "E:\ReRAM-SMU V1\tools\setup\smoke-tests\spice\ltspice_test.net"
Get-Content "E:\ReRAM-SMU V1\tools\setup\smoke-tests\spice\ltspice_test.log" | Select-Object -First 30
```

## 3. Smoke tests (disposable, not ReRAM-SMU source stage)

Location: `tools/setup/smoke-tests/spice/`

| Test | File | ngspice command | Expected | Result |
|------|------|-----------------|----------|--------|
| A — resistor divider | `test_A_divider.cir` | `ngspice_con -b test_A_divider.cir` | `v(mid)=5.000000e+00` | PASS (`v(mid)=5.0` printed) |
| B — RC transient | `test_B_rc_transient.cir` | `ngspice_con -b test_B_rc_transient.cir -o test_B.log` | τ=10 ms, 63.2% at 10 ms (~3.16 V), ~4.91 V at 40 ms | PASS (423 rows, verified monotonically rising) |
| C — op-amp (ideal VCVS gain 2×) | `test_C_opamp.cir` | `ngspice_con -b test_C_opamp.cir` | `v(out)≈1.99996` | PASS (`1.99996e+00`) |
| D — batch execution (variant) | `test_D_batch.cir` | same batch path | batch completes without GUI | PASS (exit 0, "Simulation executed from .control") |
| LT — divider via LTspice | `ltspice_test.net` | `LTspice.exe -b ltspice_test.net` | Operating Point converged | PASS (`Direct Newton iteration succeeded`) |

Evidence: `test_B.log`, `ltspice_test.log`, `ltspice_test.raw` preserved.

## 4. Workflow recommendation (hybrid)

- **Regression / CI / Python:** ngspice with `ngspice_con -b` + Python wrapper; netlists in `simulation/spice/`, results/plots in `simulation/results/` with date+tool-version per ENGINEERING_RULES §4.
- **Vendor model:** LTspice when a manufacturer only ships LTspice `.lib`/`.asc`. Validate key specs (dropout, stability, noise) there, then port behavioral equivalent to ngspice for regression.

## 5. What was NOT simulated (per ENGINEERING_RULES)

Low-current leakage, contamination, dielectric absorption, PCB creepage, relay leakage, and layout-dependent effects — simulation does **not** prove low-current performance (Rule 5). Those require physical measurement on dummy loads.

## 6. Scripts

- `tools/scripts/run_spice.py` — wrapper above (created).
- `simulation/spice/README.md` — placeholder; future netlists go there.
