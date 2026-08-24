#!/usr/bin/env python3
"""
Gate 5 Test K — Range switching faults
Models: break-before-make (correct), make-before-break (2 shunts parallel),
 stuck relay (short), open relay (infinite), contact bounce (1ms chatter),
 switching while output enabled vs disabled vs in compliance.

Evaluates: DUT current transient, ADC overload (shunt voltage wrong), compliance response (Vsense on wrong R), shunt overstress (I^2*R)

Determines safe sequence: freeze sweep -> reduce/disable output if required -> break -> wait 5ms -> make -> settle 10ms -> zero/offset -> resume
"""
import pathlib, csv, math

# Canonical ranges: 6 ranges but we test transitions between adjacent
RANGES = [
    {"name":"10mA", "R":2.5, "Vfs_mV":25, "Ifs_A":10e-3},
    {"name":"1mA",  "R":25, "Vfs_mV":25, "Ifs_A":1e-3},
    {"name":"100uA","R":500, "Vfs_mV":50, "Ifs_A":100e-6},
    {"name":"10uA", "R":5e3, "Vfs_mV":50, "Ifs_A":10e-6},
    {"name":"1uA",  "R":100e3,"Vfs_mV":100,"Ifs_A":1e-6},
    {"name":"100nA","R":1e6,"Vfs_mV":100,"Ifs_A":100e-9},
]

def eval_fault(from_range, to_range, fault, I_dut, Vsrc=2.0, output_enabled=True, in_compliance=False):
    """
    Returns dict of metrics:
     - R_effective (what Vsense sees)
     - Vshunt_actual = I_dut * R_eff
     - ADC_overload_factor = Vshunt_actual / Vfs_to (if >1.5 => overload)
     - Vsense_error_pct = (Reff - R_to)/R_to *100
     - DUT_current_transient_A (if open => 0, if short => maybe limited?)
     - compliance_error: if Vsense wrong, compliance will regulate to wrong I
     - shunt_overstress_W = I^2 * R (worst shunt sees)
    """
    R_from = from_range["R"]
    R_to = to_range["R"]
    if fault == "correct_BBM":
        # Break before make: during 5ms gap, shunt open => ADC sees Hi-Z, but output should be disabled or frozen
        # If output enabled during gap, I path open => Vcompliance rail? But we enforce disabled.
        if output_enabled:
            # hot switch with gap: I=0 during gap, then after make, normal
            R_eff_gap = float('inf')
            # transient: during gap no current => DUT sees maybe open? But if output enabled, source tries to drive I through open -> voltage rails to compliance.
            # We'll flag high transient risk.
            R_eff = R_to  # after settle
        else:
            R_eff = R_to
        R_eff_gap = R_eff if not output_enabled else float('inf')
    elif fault == "make_before_break":
        R_eff = (R_from*R_to)/(R_from+R_to)
    elif fault == "stuck_short":
        # relay stuck closed in old range: effectively old R still connected, maybe parallel with new if attempt to switch
        R_eff = R_from  # stuck at old
    elif fault == "open_relay":
        R_eff = float('inf')
    elif fault == "contact_bounce":
        # during 1ms chatter, R toggles between old, open, new => worst is intermittent open/parallel
        R_eff = R_to  # final after settle, but during bounce R_eff varies
    elif fault == "hot_switch_compliance":
        # switching while in compliance (current limited): I_dut = Icomp (e.g., 5mA) much larger than new range FS
        R_eff = R_to
    else:
        R_eff = R_to

    # Compute metrics after switch (steady)
    if math.isinf(R_eff):
        Vshunt = float('inf')  # open => no path, ADC overload due to saturation?
        overload = float('inf')
        vsense_err = float('inf')
        Idut_transient = 0
        compliance_err_pct = float('inf')
        overstress = 0
    else:
        Vshunt = I_dut * R_eff
        Vfs_to = to_range["Vfs_mV"]*1e-3
        overload = Vshunt / Vfs_to if Vfs_to>0 else float('inf')
        vsense_err = (R_eff - R_to)/R_to*100
        # If in compliance, source is current-limited: Vsense will be at Icomp*R_eff vs expected Icomp*R_to
        # Compliance loop sees wrong R, so actual Icomp_actual = Vsense_threshold / R_eff vs desired Vsense/R_to
        # If fault makes R_eff smaller (MBB), actual I will be higher than intended: I_actual = Vthr / R_eff > Vthr/R_to
        if in_compliance:
            Icomp_desired = to_range["Ifs_A"]  # assume compliance at FS of to_range
            Vthr = Icomp_desired * R_to
            I_actual = Vthr / R_eff if R_eff!=0 else float('inf')
            compliance_err_pct = (I_actual - Icomp_desired)/Icomp_desired*100
            Idut_transient = I_actual  # current spike if MBB reduces R
        else:
            compliance_err_pct = vsense_err  # Vsense misread same %
            Idut_transient = I_dut if not math.isinf(R_eff) else 0
        overstress = I_dut**2 * R_eff if not math.isinf(R_eff) else 0

    return {
        "R_eff": R_eff,
        "Vshunt_V": Vshunt,
        "overload_x": overload,
        "vsense_err_pct": vsense_err,
        "compliance_err_pct": compliance_err_pct,
        "overstress_mW": overstress*1e3,
        "Idut_transient_A": Idut_transient,
    }

def timing_model():
    """
    Returns safe sequence timing t0 reference
    Steps: freeze sweep (0ms) -> reduce/disable output if required (0.5ms) -> break (relay open 1ms) -> wait 5ms -> make (1ms) -> settle 10ms -> zero/offset 5ms -> resume
    Total blanking ~21.5ms
    """
    seq = [
        ("Freeze sweep / hold DAC", 0.0, 0.5, "Hold DAC, inhibit autorange, freeze compliance flag"),
        ("Reduce/disable output if |I|>10% FS_new or hot-switch risk", 0.5, 0.5, "If I_dut > 0.5*Ifs_new or in_compliance, set Vc=0 or disable (LT1970 ENABLE low)"),
        ("Break old relay (open)", 1.0, 1.0, "Coil de-energize 1ms, contact open"),
        ("Wait 5ms after break (BBM gap)", 2.0, 5.0, "Ensures break-before-make, coil settle, charge injection decay"),
        ("Make new relay (close)", 7.0, 1.0, "Coil energize 1ms"),
        ("Settle 10ms (relay + RC + DA blanking)", 8.0, 10.0, "Contact bounce 1ms + shunt RC Esd + ADC input RC + dielectric absorption"),
        ("Zero/offset calibrate (auto-zero)", 18.0, 5.0, "Measure shunt offset with input shorted (optional), store offset"),
        ("Resume sweep / re-enable output", 23.0, 0.5, "Re-enable LT1970, ramp DAC at slew limit 0.1V/ms"),
    ]
    return seq

def main():
    out_path = pathlib.Path(__file__).parent / "test_K_results.csv"
    # Transition matrix: evaluate adjacent up/down and cross ranges
    transitions = [
        (0,1), (1,0), (1,2), (2,1), (2,3), (3,2), (4,5), (5,4), (0,5), (5,0)
    ]
    faults = ["correct_BBM","make_before_break","stuck_short","open_relay","contact_bounce","hot_switch_compliance"]
    # I_dut cases: low (10% FS_to), mid (50%), high (100%), overload (200% if in compliance)
    header = ["from_range","to_range","from_R","to_R","fault","I_dut_A","I_dut_pct_FS_to","output_enabled","in_compliance",
              "R_eff","Vshunt_V","overload_x","vsense_err_pct","compliance_err_pct","overstress_mW","Idut_transient_A","risk","safe_seq_required"]
    rows=[]
    for (fi, ti) in transitions:
        fr = RANGES[fi]; tr = RANGES[ti]
        for fault in faults:
            for I_factor, enabled, in_comp in [
                (0.1, False, False),
                (0.1, True, False),
                (1.0, False, False),
                (1.0, True, False),
                (1.5, True, True),  # in compliance overload
            ]:
                I_dut = I_factor * tr["Ifs_A"]
                # hot_switch_compliance only relevant when in_comp True, skip otherwise to reduce rows
                if fault=="hot_switch_compliance" and not in_comp:
                    continue
                if fault!="hot_switch_compliance" and in_comp and I_factor!=1.5:
                    # Keep one compliance row per other faults too
                    pass
                m = eval_fault(fr, tr, fault, I_dut, output_enabled=enabled, in_compliance=in_comp)
                # Risk classification
                overload = m["overload_x"]
                vs_err = m["vsense_err_pct"]
                if math.isinf(overload):
                    risk="CRITICAL open - ADC rails, compliance blind"
                elif overload>10:
                    risk="CRITICAL ADC severe overload, input ESD clamp may conduct"
                elif overload>1.5:
                    risk="HIGH ADC overload, recovery 10ms"
                elif abs(vs_err)>5:
                    risk="HIGH Vsense wrong, compliance mis-regulates, shunt overstress"
                elif fault=="correct_BBM" and enabled:
                    risk="MEDIUM hot BBM gap - voltage spike if not disabled"
                elif fault=="correct_BBM" and not enabled:
                    risk="LOW safe when disabled"
                elif fault=="make_before_break":
                    risk="HIGH parallel shunt, Vsense low by 4-50% (Kelvin would still be wrong)"
                else:
                    risk="MEDIUM"
                safe = "BBM+disable+21ms blank" if ("CRITICAL" in risk or "HIGH" in risk) else "BBM+10ms"
                rows.append([fr["name"], tr["name"], fr["R"], tr["R"], fault, f"{I_dut:.3e}", f"{I_factor*100:.0f}%", str(enabled), str(in_comp),
                             f"{m['R_eff']:.3e}" if not math.isinf(m["R_eff"]) else "inf",
                             f"{m['Vshunt_V']:.3e}" if not math.isinf(m["Vshunt_V"]) else "inf",
                             f"{m['overload_x']:.2f}" if not math.isinf(m["overload_x"]) else "inf",
                             f"{m['vsense_err_pct']:.1f}" if not math.isinf(m["vsense_err_pct"]) else "inf",
                             f"{m['compliance_err_pct']:.1f}" if not math.isinf(m["compliance_err_pct"]) else "inf",
                             f"{m['overstress_mW']:.3f}", f"{m['Idut_transient_A']:.3e}", risk, safe])

    with open(out_path,"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"Wrote {out_path} {len(rows)} rows")

    # Print timing
    print("\n=== Safe sequence timing (ms) ===")
    for name, t0, dur, note in timing_model():
        print(f"{t0:4.1f} +{dur:4.1f}ms : {name:45s} | {note}")
    print("Total blanking ~23.5ms from freeze to resume")

    # Highlight worst cases
    print("\n=== Worst fault highlights ===")
    for r in rows:
        if "CRITICAL" in r[16] and r[0]=="10mA" and r[1]=="100nA":
            print(r)
        if r[4]=="make_before_break" and r[0]=="10mA" and r[1]=="1mA":
            print(f"MBB 10mA->1mA R_eff={r[9]} vs expected 25 ohm => {r[12]}% Vsense low -> compliance will overshoot by {r[13]}%")
    # Shunt overstress check: I=10mA through 2.5R =0.25mW safe, but 10mA through 1M =>100W impossible, but hot-switch assumes current forced through wrong R
    print("\nShunt overstress: 10mA through 1MΩ -> I^2*R =100W -> immediate fuse/damage; hence MUST disable output before switching to high-R range.")
    print("10mA through 2.5R =0.25mW safe; 100nA through 2.5R negligible.")
    print("Recommendation: Firmware must enforce I_dut < 0.5*Ifs_new before switch, else force disable; Kelvin sense alone does not save from wrong R.")

if __name__ == "__main__":
    main()
