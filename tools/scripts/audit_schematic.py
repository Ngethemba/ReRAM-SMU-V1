#!/usr/bin/env python3
"""
Phase 7 Schematic Audit — ERC-lite without KiCad

Parses KiCad S-expr .kicad_sch files (light parser) and reports:
- global_label inventory per sheet
- wire count, missing power flags, off-grid endpoints
- dangling global labels (single occurrence)
- critical net continuity (FORCE_HI etc.)

Usage: python tools/scripts/audit_schematic.py
"""
import pathlib, re, collections, json, sys

ROOT = pathlib.Path("hardware/kicad/ReRAM-SMU-V1")
SHEETS = list((ROOT / "sheets").glob("*.kicad_sch"))
if not SHEETS:
    print("No sheets found")
    sys.exit(1)

CRITICAL_NETS = ["FORCE_HI","FORCE_LO","SENSE_HI","SENSE_LO",
                 "LT1970_SENSE_P","LT1970_SENSE_N","VCSRC","VCSNK",
                 "ISRC","ISNK","OUTPUT_ENABLE","VSET","ADC_IN_P","ADC_IN_N",
                 "ISENSE_P_K","ISENSE_N_K","VREF_2V5","VREF_5V","GND","GND_KELVIN_STAR"]

# light regexes — KiCad S-expr is LISPy, we avoid full parser
re_global = re.compile(r'\(global_label\s+"([^"]+)"')
re_wire = re.compile(r'\(wire\s+\(pts\s+\(xy\s+([0-9.\-]+)\s+([0-9.\-]+)\)\s+\(xy\s+([0-9.\-]+)\s+([0-9.\-]+)\)')
re_symbol = re.compile(r'\(symbol\s+\(lib_id\s+"([^"]+)"')
re_power_flag = re.compile(r'power:PWR_FLAG')
re_grid_check = re.compile(r'\(at\s+([0-9.\-]+)\s+([0-9.\-]+)')

def is_on_grid(val, grid=0.254):
    # KiCad default grids 0.254mm (10mil) or 1.27mm; we check 0.254
    # allow epsilon
    v = float(val)
    return abs(round(v/grid)*grid - v) < 1e-6

all_globals = collections.Counter()
sheet_report = {}

for p in SHEETS + [ROOT / "ReRAM-SMU-V1.kicad_sch"]:
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    globs = re_global.findall(text)
    wires = re_wire.findall(text)
    symbols = re_symbol.findall(text)
    has_pwr_flag = bool(re_power_flag.search(text))
    # grid audit — collect all (at x y)
    off_grid = 0
    for m in re_grid_check.finditer(text):
        x,y = m.groups()
        if not (is_on_grid(x) and is_on_grid(y)):
            off_grid += 1
    all_globals.update(globs)
    sheet_report[str(p.relative_to(ROOT))] = {
        "global_labels": sorted(set(globs)),
        "global_count": len(globs),
        "wire_count": len(wires),
        "symbol_types": collections.Counter(symbols),
        "has_pwr_flag": has_pwr_flag,
        "off_grid_endpoints": off_grid,
    }

print("=== Phase 7 Schematic Audit (ERC-lite) ===\n")
print(f"Sheets scanned: {len(sheet_report)}")
for s, r in sheet_report.items():
    print(f"\n{s}:")
    print(f"  globals ({r['global_count']}): {', '.join(r['global_labels'][:8])}{' ...' if len(r['global_labels'])>8 else ''}")
    print(f"  wires: {r['wire_count']}  PWR_FLAG: {r['has_pwr_flag']}  off_grid(endpoints): {r['off_grid_endpoints']}")
    top_syms = r['symbol_types'].most_common(4)
    if top_syms:
        print(f"  top symbols: {', '.join(f'{k}×{v}' for k,v in top_syms)}")

print("\n--- Global label occurrences (dangling = 1) ---")
for net, cnt in sorted(all_globals.items()):
    mark = " <-- DANGLING" if cnt==1 else ""
    crit = " [CRITICAL]" if net in CRITICAL_NETS else ""
    print(f"  {net:20s} {cnt:2d}{mark}{crit}")

dangling = [k for k,v in all_globals.items() if v==1]
critical_missing = [n for n in CRITICAL_NETS if n not in all_globals]
critical_dangling = [n for n in CRITICAL_NETS if all_globals.get(n,0)==1]

print(f"\nSummary: {len(dangling)} dangling / {len(all_globals)} total global labels")
if critical_dangling:
    print(f"CRITICAL dangling (needs wiring): {', '.join(critical_dangling)}")
if critical_missing:
    print(f"CRITICAL missing entirely: {', '.join(critical_missing)}")

# ERC-like JSON for tools
out = {"sheets": sheet_report, "globals": dict(all_globals), "dangling": dangling,
       "critical_dangling": critical_dangling, "critical_missing": critical_missing}
path = pathlib.Path("hardware/kicad/erc_audit_lite.json")
path.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"\nWrote {path}")
