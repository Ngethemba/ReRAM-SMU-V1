"""
ReRAM-SMU V1 — instrument control sanity check (PyVISA, pyserial).

Requires .venv with pyvisa/pyvisa-py/pyserial.
No hardware needed — enumerates resources gracefully.
"""
import sys
try:
    import pyvisa
    import serial  # pyserial
    rm = pyvisa.ResourceManager("@py")
    print(f"pyvisa {pyvisa.__version__} / pyvisa-py {__import__('pyvisa_py').__version__ if 'pyvisa_py' in sys.modules else 'via @py'}")
    print(f"pyserial {serial.VERSION}")
    resources = rm.list_resources()
    print(f"VISA resources (@py): {list(resources) if resources else '(none — no hardware, expected)'}")
    print("instrument-control env: PASS (graceful without hardware)")
except Exception as e:
    print(f"instrument-control check failed: {e}", file=sys.stderr)
    sys.exit(1)
