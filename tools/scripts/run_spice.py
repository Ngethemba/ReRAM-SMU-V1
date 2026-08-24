"""
ReRAM-SMU V1 — headless ngspice wrapper (hybrid workflow primary).

Usage:
  .venv/Scripts/python.exe tools/scripts/run_spice.py simulation/spice/my.cir
  .venv/Scripts/python.exe tools/scripts/run_spice.py tools/setup/smoke-tests/spice/test_A_divider.cir --raw my.raw

Requires portable ngspice at tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe
"""
from __future__ import annotations
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
NGSPICE = ROOT / "tools" / "setup" / "ngspice-portable" / "Spice64" / "bin" / "ngspice_con.exe"
# Fallback to E:/KiCad bundled if portable missing (not preferred)
FALLBACK = pathlib.Path(r"E:\KiCad\bin\ngspice.dll")  # indicates KiCad presence

def run(cir: pathlib.Path, raw: pathlib.Path | None = None, log: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    if not NGSPICE.exists():
        print(f"ngspice not found at {NGSPICE}", file=sys.stderr)
        print(f"Hint: ensure tools/setup/ngspice-portable exists or set NGSPICE env", file=sys.stderr)
        sys.exit(2)
    args = [str(NGSPICE), "-b", str(cir)]
    if raw:
        args += ["-r", str(raw)]
    if log:
        args += ["-o", str(log)]
    return subprocess.run(args, capture_output=True, text=True, timeout=120)

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cir = pathlib.Path(sys.argv[1])
    if not cir.exists():
        print(f"cir not found: {cir}", file=sys.stderr)
        sys.exit(1)
    # simple flag parsing for --raw / --log
    raw = None
    log = None
    if "--raw" in sys.argv:
        raw = pathlib.Path(sys.argv[sys.argv.index("--raw") + 1])
    if "--log" in sys.argv:
        log = pathlib.Path(sys.argv[sys.argv.index("--log") + 1])
    cp = run(cir, raw, log)
    print(cp.stdout)
    if cp.stderr:
        print(cp.stderr, file=sys.stderr)
    sys.exit(cp.returncode)

if __name__ == "__main__":
    main()
