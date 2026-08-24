#!/usr/bin/env python3
"""
Gate 1 — Test B: Compliance-aware range coercion algorithm
Project: ReRAM-SMU V1 Phase3 Gate1

Canonical ranges §2.4 D: 10mA 2.5Ω/25mV, 1mA 25Ω/25mV, 100uA 500Ω/50mV, 10uA 5kΩ/50mV, 1uA 100kΩ/100mV, 100nA 1MΩ/100mV
LT1970A thresholds: Vc 40mV floor (4mV), Vc 60mV linear (6mV), ideal Vc>=0.5V

Algorithm concept (Solution A adopted for V1 REV-A):
  Given user-requested Icomp, firmware selects the tightest hardware range where:
    1) Icomp <= I_FS  (no shunt overload, no Vsense > FS)
    2) Vc = Icomp*R*10 >=60mV (linear region, ideally >=0.5V)
  Among feasible candidates, pick smallest I_FS that satisfies both (largest R that fits)
  => maximizes Vc while keeping measurement within FS.
  If no candidate meets Vc>=60mV, report error / require Candidate C precision loop.
  If Icomp > max I_FS (10mA), clamp to 10mA range and flag overload.

Test cases per task: 10uA,50uA,100uA,500uA,1mA,5mA

Outputs: test_B_results.csv
Run: .venv python simulation/phase3/compliance/test_B_range_coercion.py
"""
import csv, pathlib, math

RANGES = [
    {"label": "10mA",  "I_fs": 10e-3,  "V_fs": 25e-3,  "R": 2.5,   "gain_to_2p5": 100,  "johnson_pA_10Hz": 257.4}, # approx from tradeoff calc
    {"label": "1mA",   "I_fs": 1e-3,   "V_fs": 25e-3,  "R": 25.0,  "gain_to_2p5": 100,  "johnson_pA_10Hz": 81.4},
    {"label": "100uA", "I_fs": 100e-6, "V_fs": 50e-3,  "R": 500.0, "gain_to_2p5": 50,   "johnson_pA_10Hz": 18.2},
    {"label": "10uA",  "I_fs": 10e-6,  "V_fs": 50e-3,  "R": 5000.0,"gain_to_2p5": 50,   "johnson_pA_10Hz": 5.76},
    {"label": "1uA",   "I_fs": 1e-6,   "V_fs": 100e-3, "R": 100000.0,"gain_to_2p5": 25, "johnson_pA_10Hz": 1.29},
    {"label": "100nA", "I_fs": 100e-9, "V_fs": 100e-3, "R": 1000000.0,"gain_to_2p5":25, "johnson_pA_10Hz": 0.41},
]

# More precise johnson via formula: vn = sqrt(4kTRB) /R, B=10Hz brickwall, T=300K
k=1.380649e-23
T=300.0
def johnson_pA(R, B=10):
    vn = math.sqrt(4*k*T*R*B)
    return vn / R * 1e12

for r in RANGES:
    r["johnson_pA_10Hz"] = johnson_pA(r["R"])
    r["johnson_pA_ENBW"] = r["johnson_pA_10Hz"]*1.253 # single-pole

TEST_ICOMP = [10e-6, 50e-6, 100e-6, 500e-6, 1e-3, 5e-3]

VC_LINEAR = 60e-3
VC_IDEAL = 0.5
VS_FLOOR = 4e-3

def select_range(Icomp):
    """Coercion: tightest range where Icomp<=I_FS and Vc>=60mV; prefer Vc>=0.5V."""
    # candidates feasible
    candidates = []
    for r in sorted(RANGES, key=lambda x: x["I_fs"]): # ascending
        Vs = Icomp * r["R"]
        Vc = Vs *10
        feasible = (Icomp <= r["I_fs"]+1e-15) and (Vc >= VC_LINEAR-1e-12)
        overload = (Icomp > r["I_fs"])
        candidates.append((r, Vs, Vc, feasible, overload))
    # feasible list
    feasible = [c for c in candidates if c[3]]
    if not feasible:
        return None, candidates, "NO FEASIBLE LINEAR RANGE"
    # prefer ideal Vc>=0.5V among feasible
    ideal = [c for c in feasible if c[2] >= VC_IDEAL]
    # pick tightest (smallest I_FS) among ideal if exists, else smallest I_FS among feasible
    pool = ideal if ideal else feasible
    # smallest I_FS is first when sorted ascending; among pool pick min I_fs
    best = min(pool, key=lambda x: x[0]["I_fs"])
    return best, candidates, ("IDEAL" if ideal else "LINEAR")

HERE = pathlib.Path(__file__).parent
CSV_B = HERE / "test_B_results.csv"

def measurement_consequence(Icomp, sel_range):
    """Describe measurement impact when compliance range = measurement range."""
    if sel_range is None:
        return "N/A — no valid range; would require Candidate C precision loop"
    I_fs = sel_range["I_fs"]
    V_fs = sel_range["V_fs"]
    R = sel_range["R"]
    # How much of measurement FS is used for a typical ReRAM read?
    # Example HRS 1GΩ @0.1V => 100pA? Actually use Icomp's FS context
    # For consequence, consider: if you coerce to high-R range for low Icomp, your Imeas FS becomes small,
    # so any subsequent LRS current would overload. Conversely high-Icomp forces large FS, losing nA resolution.
    pct = Icomp / I_fs *100
    gain = sel_range["gain_to_2p5"]
    johnson = sel_range["johnson_pA_10Hz"]
    johnson_enbw = sel_range["johnson_pA_ENBW"]
    # Describe
    if I_fs >= 1e-3:
        tier = "high-current: Johnson negligible (<0.1nA), gain 100x, headroom dominates"
    elif I_fs >= 10e-6:
        tier = f"mid-current: Johnson {johnson:.1f}pA (ENBW {johnson_enbw:.1f}pA), gain {gain}x"
    else:
        tier = f"low-current: Johnson {johnson:.2f}pA (ENBW {johnson_enbw:.2f}pA), gain {gain}x, leakage budget critical"
    # overload risk for opposite extreme
    if pct >= 90:
        overload_note = "At 100% FS — no margin for transient snap; any overshoot trips range compliance"
    elif pct <= 10:
        overload_note = "Small Icomp leaves most FS unused — but forces high-R range, limits max measurable LRS"
    else:
        overload_note = "Moderate FS utilization"
    # ReRAM specific: SET->LRS may be mA while HRS is nA; tying ranges loses dual-extreme capability
    if I_fs <= 10e-6 and Icomp <= 10e-6:
        dual = "Cannot simultaneously measure mA LRS without autorange; OK for HRS reads"
    elif I_fs >= 1e-3:
        dual = "Covers LRS up to mA; nA HRS below 0.01% FS — needs separate low-I range for reads"
    else:
        dual = "Balances mid-range; still needs autorange for HRS<1uA or LRS>1mA"
    return f"{tier}; {overload_note}. {dual}. Icomp is {pct:.0f}% of Imeas FS."

def main():
    print("="*72)
    print("Gate 1 Test B — Compliance-aware range coercion")
    print("Canonical D ranges; LT1970A Vc>=60mV linear, ideal >=0.5V, floor 4mV")
    print("="*72)

    rows = []
    for Icomp in TEST_ICOMP:
        best, all_candidates, tag = select_range(Icomp)
        if best is None:
            sel_label = "NONE"
            R = Vfs = Ifs = Vs = Vc = float('nan')
            head_mV = head_pct = float('nan')
            region = "NO FEASIBLE"
            ideal_flag = "FAIL"
            consequence = measurement_consequence(Icomp, None)
            passed = "FAIL"
            sel_range = None
        else:
            r, Vs, Vc, _, _ = best
            sel_label = r["label"]
            R = r["R"]
            Vfs = r["V_fs"]
            Ifs = r["I_fs"]
            head_mV = (Vfs - Vs)*1e3
            head_pct = (1 - Vs/Vfs)*100 if Vfs>0 else 0
            if Vc >= 0.5:
                region = "VALID linear (ideal >=0.5V)"
                ideal_flag = "YES (>=0.5V)"
            elif Vc >= 0.06:
                region = "VALID linear (>=60mV)"
                ideal_flag = "NO (<0.5V but linear)"
            elif Vc >= 0.04:
                region = "NONLINEAR <60mV"
                ideal_flag = "NO"
            else:
                region = "INVALID floor"
                ideal_flag = "NO"
            sel_range = r
            consequence = measurement_consequence(Icomp, r)
            # PASS if Vc linear and no overload
            passed = "PASS" if (Vc >= VC_LINEAR and Icomp <= Ifs) else "FAIL"
            # Also check headroom not negative
            if head_mV < -0.01:
                passed = "FAIL (overload)"

        rows.append({
            "User_Icomp_A": Icomp,
            "User_Icomp_str": f"{Icomp*1e6:.0f}uA" if Icomp<1e-3 else f"{Icomp*1e3:.0f}mA",
            "Selected_range": sel_label,
            "R_Ohm": R,
            "V_FS_mV": Vfs*1e3 if isinstance(Vfs,float) and not math.isnan(Vfs) else "",
            "I_FS_A": Ifs if isinstance(Ifs,float) and not math.isnan(Ifs) else "",
            "Vsense_mV": Vs*1e3 if isinstance(Vs,float) and not math.isnan(Vs) else "",
            "Required_Vc_mV": Vc*1e3 if isinstance(Vc,float) and not math.isnan(Vc) else "",
            "Vsense_pct_FS": Vs/Vfs*100 if isinstance(Vs,float) and not math.isnan(Vs) else "",
            "Headroom_mV": head_mV if not math.isnan(head_mV) else "",
            "Headroom_pct": head_pct if not math.isnan(head_pct) else "",
            "Vc_region": region,
            "Vc_ideal": ideal_flag,
            "Measurement_consequence": consequence,
            "PASS": passed,
            "Tag": tag,
        })
        print(f"\nIcomp {Icomp*1e6:.0f}uA -> {sel_label} (R={R}Ω, Vfs={Vfs*1e3 if not math.isnan(Vfs) else 0:.0f}mV): Vs={Vs*1e3 if not math.isnan(Vs) else 0:.2f}mV Vc={Vc*1e3 if not math.isnan(Vc) else 0:.0f}mV "
              f"head {head_mV:.1f}mV ({head_pct:.0f}%) region:{region} {passed}")
        print(f"  -> {consequence}")

    # Write CSV
    fieldnames = ["User_Icomp_A","User_Icomp_str","Selected_range","R_sense_Ohm","V_FS_mV","I_FS_A","Vsense_mV","Required_Vc_V","Required_Vc_mV","Vsense_pct_FS","Headroom_mV","Headroom_pct","Vc_region","Vc_ideal_ge_0p5V","Measurement_consequence","PASS","Selector_tag"]
    with open(CSV_B, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({
                "User_Icomp_A": f"{r['User_Icomp_A']:.6e}" if isinstance(r['User_Icomp_A'], float) else r['User_Icomp_A'],
                "User_Icomp_str": r['User_Icomp_str'],
                "Selected_range": r['Selected_range'],
                "R_sense_Ohm": f"{r['R_Ohm']:.1f}" if isinstance(r['R_Ohm'], float) and not math.isnan(r['R_Ohm']) else r['R_Ohm'],
                "V_FS_mV": f"{r['V_FS_mV']:.0f}" if isinstance(r['V_FS_mV'], float) else r['V_FS_mV'],
                "I_FS_A": f"{r['I_FS_A']:.6e}" if isinstance(r['I_FS_A'], float) and not math.isnan(r['I_FS_A']) else r['I_FS_A'],
                "Vsense_mV": f"{r['Vsense_mV']:.3f}" if isinstance(r['Vsense_mV'], float) and not math.isnan(r['Vsense_mV']) else r['Vsense_mV'],
                "Required_Vc_V": f"{r['Vsense_mV']/100:.6f}" if isinstance(r['Vsense_mV'], float) and not math.isnan(r['Vsense_mV']) else "",
                "Required_Vc_mV": f"{r['Required_Vc_mV']:.1f}" if isinstance(r['Required_Vc_mV'], float) and not math.isnan(r['Required_Vc_mV']) else r['Required_Vc_mV'],
                "Vsense_pct_FS": f"{r['Vsense_pct_FS']:.1f}" if isinstance(r['Vsense_pct_FS'], float) else r['Vsense_pct_FS'],
                "Headroom_mV": f"{r['Headroom_mV']:.2f}" if isinstance(r['Headroom_mV'], float) and not math.isnan(r['Headroom_mV']) else r['Headroom_mV'],
                "Headroom_pct": f"{r['Headroom_pct']:.1f}" if isinstance(r['Headroom_pct'], float) and not math.isnan(r['Headroom_pct']) else r['Headroom_pct'],
                "Vc_region": r['Vc_region'],
                "Vc_ideal_ge_0p5V": r['Vc_ideal'],
                "Measurement_consequence": r['Measurement_consequence'],
                "PASS": r['PASS'],
                "Selector_tag": r['Tag'],
            })
    print(f"\n[OK] Wrote {CSV_B} ({len(rows)} rows)")

    # Summary verdict
    print("\n" + "="*72)
    print("Coercion verdict for ReRAM recipes (typical Icc 50uA-1mA):")
    passes = sum(1 for r in rows if r["PASS"]=="PASS")
    print(f"  {passes}/{len(rows)} coercion cases PASS linear Vc>=60mV")
    ideal_cnt = sum(1 for r in rows if "YES" in r['Vc_ideal'])
    print(f"  {ideal_cnt}/{len(rows)} achieve ideal Vc>=0.5V")
    # Check 50uA-1mA subset
    subset = [r for r in rows if 50e-6 <= r["User_Icomp_A"] <= 1e-3]
    subset_pass = sum(1 for r in subset if r["PASS"]=="PASS")
    print(f"  ReRAM window 50uA-1mA: {subset_pass}/{len(subset)} PASS")
    if subset_pass==len(subset):
        print("  -> Coercion alone SUFFICES for typical Icc 50uA-1mA (all linear)")
        print("  -> Limitations: at 50uA Vc=250mV (0.5x ideal), at 500uA Vc=125mV (2x knee, 0.25x ideal), at 1mA 0% headroom")
    else:
        print("  -> Coercion alone INSUFFICIENT")

    print("\nWhen Candidate C (precision CC loop) required:")
    print("  - Icomp <8uA on 100uA range or <160uA on 1mA range (below floor) -> coercion helps but ties measurement")
    print("  - Need <0.1% FS compliance (e.g., 10nA on 10uA) -> LT1970A floor 8% FS, needs amplified shunt + external loop")
    print("  - Simultaneous nA HRS read + mA LRS write without autorange glitch -> decoupled CC loop avoids range mismatch")
    print("  - MLC ladder requiring 1% CC accuracy -> LT1970A 1% + Rs tolerance coarser than external 0.02% loop")

if __name__ == "__main__":
    main()
