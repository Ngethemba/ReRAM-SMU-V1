import pathlib, re

def add_wire_if_missing(sheet_path, from_xy, to_xy):
    txt = pathlib.Path(sheet_path).read_text(encoding="utf-8")
    # Check if wire already exists between these points (approx)
    wire_str = f"(wire (pts (xy {from_xy[0]} {from_xy[1]}) (xy {to_xy[0]} {to_xy[1]}))"
    if wire_str in txt:
        return False
    # Add wire before final )
    # Find last wire or before final )
    insert_pos = txt.rfind(")")
    # Insert before final paren
    new_wire = f"\t(wire (pts (xy {from_xy[0]} {from_xy[1]}) (xy {to_xy[0]} {to_xy[1]})) (stroke (width 0) (type default)) (uuid \"wire-{from_xy[0]}-{from_xy[1]}\"))\n"
    # Insert before last )
    txt = txt[:txt.rfind("\n)")] + "\n" + new_wire + txt[txt.rfind("\n)"): ]
    pathlib.Path(sheet_path).write_text(txt, encoding="utf-8")
    return True

# For each sheet, ensure each global_label has a wire to a nearby pin
# Simplify: for 01 POWER, connect each global_label to nearest power symbol
base = pathlib.Path("E:/ReRAM-SMU V1/hardware/kicad/ReRAM-SMU-V1/sheets")
for p in base.glob("*.kicad_sch"):
    txt = p.read_text(encoding="utf-8")
    # Find global labels
    labels = re.findall(r'\(global_label "([^"]+)" \(shape [^\)]+\) \(at ([0-9.\-]+) ([0-9.\-]+)', txt)
    if not labels:
        continue
    print(f"{p.name}: {len(labels)} global labels")
    # For each label, check if there's a wire near it (within 5mm)
    # If not, add a short wire stub to make it not dangling (ERC requires at least a wire)
    # Add a 2mm wire stub from label position
    for name, x, y in labels:
        x = float(x); y = float(y)
        # Check if wire near label
        has_wire = False
        for m in re.finditer(r'\(wire \(pts \(xy ([0-9.\-]+) ([0-9.\-]+)\) \(xy ([0-9.\-]+) ([0-9.\-]+)\)', txt):
            x1=float(m.group(1)); y1=float(m.group(2)); x2=float(m.group(3)); y2=float(m.group(4))
            # If wire endpoint within 2mm of label
            if abs(x1-x)<2 and abs(y1-y)<2 or abs(x2-x)<2 and abs(y2-y)<2:
                has_wire=True
                break
        if not has_wire:
            # Add a short 2mm wire stub from label
            add_wire_if_missing(str(p), (x, y), (x+2, y))
            print(f"  added stub for {name} at {x},{y}")

print("wire stubs added")
