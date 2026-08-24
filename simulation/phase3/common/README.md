# Phase 3 Common — Models & Helpers

See `simulation/phase3/MODEL_LIMITATIONS.md` for model provenance.

- ngspice primary: `E:/ReRAM-SMU V1/tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`
- LTspice secondary: `C:/Users/azrai/AppData/Local/Programs/ADI/LTspice/LTspice.exe -b`
- Python venv: `E:/ReRAM-SMU V1/.venv/Scripts/python.exe`
- All tests use canonical range table per SHUNT_RANGE_TRADEOFF §2.4: 10mA 2.5Ω/25mV, 1mA 25Ω/25mV, 100µA 500Ω/50mV, 10µA 5kΩ/50mV, 1µA 100kΩ/100mV, 100nA 1MΩ/100mV
