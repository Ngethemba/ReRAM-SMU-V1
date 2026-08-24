# ReRAM-SMU V1 — Python Environment

**Date:** 2026-08-24  
**Manager:** `uv` 0.12.5 — project-local `.venv`  
**Python:** 3.11.15 (uv-managed `cpython-3.11-windows-x86_64-none`, at `C:\Users\azrai\AppData\Roaming\uv\python\...`)

## 1. Location and activation

```
E:\ReRAM-SMU V1\.venv\                  # gitignored (see .gitignore: .venv/ )
E:\ReRAM-SMU V1\.venv\Scripts\python.exe
E:\ReRAM-SMU V1\.venv\Scripts\activate.ps1   # PowerShell
E:\ReRAM-SMU V1\.venv\Scripts\activate.bat   # CMD
```

```powershell
Set-Location "E:\ReRAM-SMU V1"
.\.venv\Scripts\Activate.ps1
# or
uv pip list --python .venv
.\.venv\Scripts\python.exe -m pytest -q
```

## 2. Reproducibility files

| File | Purpose | Commit? |
|------|---------|---------|
| `pyproject.toml` | project metadata + pinned deps + `tool.pytest` config | YES |
| `requirements.txt` | 13 pinned direct deps (install surface) | YES |
| `requirements-lock.txt` | full `uv pip freeze` (119 packages, transitive pinned) | YES |
| `.venv/` | binaries, site-packages | NO (gitignored) |

Install/recreate:

```powershell
uv venv --python 3.11 .venv
# Cross-drive copy mode (E: vs C:): avoids hardlink os error 17
$env:UV_LINK_MODE = "copy"
uv pip sync requirements.txt --python .venv      # exact from requirements.txt
# or
uv pip install -r requirements-lock.txt --python .venv
uv pip list --python .venv
.\.venv\Scripts\python.exe -m pytest simulation/python/tests software/tests -v
```

## 3. Pinned dependencies (requirements.txt)

```
numpy==2.4.6
scipy==1.17.1
pandas==3.0.5
matplotlib==3.11.1
sympy==1.14.0
pint==0.25.3
uncertainties==3.2.3
pyvisa==1.16.2
pyvisa-py==0.8.1
pyserial==3.5
pytest==9.1.1
jupyter==1.1.1
ipykernel==7.1.0
```

Rationale per `DEC-TOOL-001` and simulation/software needs:

- **numpy/scipy/pandas/matplotlib/sympy** — transfer functions, Monte Carlo, filtering, fitting, plots
- **pint** — units (V, A, Ω with dimensionality checks)
- **uncertainties** — propagation for uncertainty budgets (REQ-CAL-003)
- **pyvisa/pyvisa-py/pyserial** — USB CDC/serial/VISA instrument control (graceful without hardware)
- **pytest** — calculation/software regression
- **jupyter/ipykernel** — interactive analysis (optional, not on critical path)

Full transitive lock in `requirements-lock.txt` includes `jupyterlab 4.6.3`, `ipython 9.16.1`, `requests 2.34.2`, etc.

## 4. Verification

```powershell
"E:\ReRAM-SMU V1\.venv\Scripts\python.exe" -c "import numpy,scipy,pandas,matplotlib,sympy,pint,uncertainties,pyvisa,serial; print('imports ok')"
"E:\ReRAM-SMU V1\.venv\Scripts\python.exe" -m pytest simulation/python/tests software/tests -v
# Result: 6 passed (test_arithmetic, numpy, scipy, pint; pyvisa resource enumeration)
```

## 5. Test infrastructure

```
simulation/python/tests/test_infra.py   # 4 tests
software/tests/test_software_infra.py   # 2 tests (incl. pyvisa @py)
pyproject.toml [tool.pytest.ini_options]
  testpaths = ["simulation/python/tests", "software/tests"]
  python_files = "test_*.py"
```

## 6. Known quirks

- `E:` (project) vs `C:` (uv cache) breaks hardlink → use `UV_LINK_MODE=copy` (warning otherwise: "Failed to hardlink... falling back to copy").
- `.venv/Scripts/pip` is not present when using `uv` venv without pip seed — use `uv pip` commands or `python -m pip` after ensuring pip.
- `pyvisa-py` TCPIP discovery warns if `zeroconf` not installed — harmless (captured in pytest warning).
