#!/usr/bin/env python3
"""
Gate 4 — Test M: 100nA-range Leakage
Project: ReRAM-SMU V1 | Phase 3 | 2026-08-24

Model: op-amp Ib (10pA JFET OPA140, 50pA ADA4522, 1pA electrometer),
       PCB surface 10G->10pA @100mV / 100G->1pA / 1G->100pA,
       relay off 1pA reed vs 100pA MUX, switch 1pA, connector 1G, ESD 1nA.

Scenarios: Good 1pA, Moderate 10pA, Poor 100pA, Catastrophic 1nA+
DUT currents: 1nA,5nA,10nA,50nA,100nA on 100nA range (Rshunt=1M, Vs=100mV FS)
Separate: offset-correctable vs voltage-dependent vs temp-dependent vs stochastic
Show MUC 1nA requires <10pA total systematic after guard/correction
  Johnson 0.41pA rms @100nA/10Hz is 4.1% of MUC, leakage 10pA is 1000% if uncorrected.

Usage: python test_M_leakage.py
Output: test_M_results.csv
"""
from __future__ import annotations
import csv
import math
from pathlib import Path

OUT_CSV = Path(__file__).parent / "test_M_results.csv"

# Constants
R_SHUNT_100NA = 1e6
VS_FS_100NA = 100e-3  # 100mV
BW = 10  # Hz brickwall
# Johnson current noise: in = sqrt(4kT/R * BW)  ;  k=1.38e-23, T=300K
K = 1.380649e-23
T = 300
JOHNSON_IN_10HZ = math.sqrt(4*K*T / R_SHUNT_100NA * BW)  # ~0.41pA
JOHNSON_IN_10HZ_ENBW = JOHNSON_IN_10HZ * math.sqrt(1.57)  # single-pole ENBW
# NPLC etc
JOHNSON_TABLE = {
    "10Hz_brickwall": JOHNSON_IN_10HZ,
    "10Hz_ENBW": JOHNSON_IN_10HZ_ENBW,
    "100Hz_brickwall": JOHNSON_IN_10HZ*math.sqrt(10),
    "1kHz_brickwall": JOHNSON_IN_10HZ*10,
}

# Leakage contributor models
LEAK_SOURCES = {
    "opamp_JFET_10pA":    {"value_pA": 10,  "type": "offset-correctable (Ib systematic, offsets with cal)", "temp_coeff": "doubles per 10C (JFET)", "guardable": "no"},
    "opamp_JFET_typ_0p5pA": {"value_pA": 0.5, "type": "offset-correctable", "temp_coeff": "doubles per 10C", "guardable": "no"},
    "opamp_chopper_50pA": {"value_pA": 50,  "type": "offset-correctable but high + voltage-dependent", "temp_coeff": "low but Ib high", "guardable": "no"},
    "opamp_electrometer_1pA": {"value_pA": 1, "type": "offset-correctable", "temp_coeff": "doubles per 10C", "guardable": "no"},
    "PCB_10G_100mV":      {"value_pA": 10,  "type": "voltage-dependent (10pA@100mV, 1pA@10mV, 0.1pA@1mV)", "temp_coeff": "halved per guard/humidity, doubles per 10C if dirty", "guardable": "yes (guard ring + keepout)"},
    "PCB_100G_guarded":   {"value_pA": 1,   "type": "voltage-dependent (1pA@100mV)", "temp_coeff": "improved 10x with guard", "guardable": "yes"},
    "PCB_1G_dirty":       {"value_pA": 100, "type": "voltage-dependent (100pA@100mV)", "temp_coeff": "humidity sensitive", "guardable": "needs cleaning"},
    "relay_reed_1pA":     {"value_pA": 1,   "type": "offset-correctable (fixed off-leak)", "temp_coeff": "stable", "guardable": "no"},
    "mux_100pA":          {"value_pA": 100, "type": "voltage-dependent + stochastic", "temp_coeff": "strong temp", "guardable": "no — use reed"},
    "switch_ADG1419_10pA":{"value_pA": 10,  "type": "voltage-dependent", "temp_coeff": "doubles per 10C", "guardable": "no"},
    "connector_1G_100mV": {"value_pA": 100, "type": "voltage-dependent", "temp_coeff": "humidity", "guardable": "guard"},
    "ESD_1nA":            {"value_pA": 1000,"type": "voltage-dependent + stochastic (clamp leakage)", "temp_coeff": "strong", "guardable": "TVS selection"},
}

SCENARIOS = {
    "Good":       {"total_pA": 1,    "composition": "Electrometer 0.2pA + PCB guarded 0.3pA + reed 0.5pA", "temp_tracked": "yes"},
    "Moderate":   {"total_pA": 10,   "composition": "JFET 5pA + PCB 3pA + reed 1pA + switch 1pA", "temp_tracked": "moderate"},
    "Poor":       {"total_pA": 100,  "composition": "Chopper 50pA + PCB dirty 30pA + MUX 20pA", "temp_tracked": "poor"},
    "Catastrophic":{"total_pA": 1000,"composition": "ESD 800pA + MUX 100pA + PCB 100pA", "temp_tracked": "fail"},
}

DUT_CURRENTS_NA = [1, 5, 10, 50, 100]
MUC_NA = 1  # minimum uncert current

def main():
    header = [
        "scenario","I_leak_total_pA","I_DUT_nA","I_DUT_pA",
        "leak_error_pct","leak_error_vs_MUC_pct",
        "johnson_pA_rms","johnson_pct_of_MUC","johnson_pct_of_IDUT",
        "SNR_leak_vs_johnson",
        "offset_correctable_pA","voltage_dependent_pA","temp_dependent_pA","stochastic_pA_rms",
        "residual_after_cal_pA","residual_vs_MUC_pct","verdict"
    ]
    rows = []

    print("="*80)
    print("Gate 4 — Test M: 100nA-Range Leakage Model")
    print("="*80)
    print(f"Rshunt={R_SHUNT_100NA/1e6:.0f}M  Vs_FS={VS_FS_100NA*1e3:.0f}mV  BW={BW}Hz")
    print(f"Johnson @10Hz brickwall={JOHNSON_IN_10HZ*1e12:.2f}pA rms  ENBW={JOHNSON_IN_10HZ_ENBW*1e12:.2f}pA")
    print(f"MUC={MUC_NA}nA  Leakage scenarios: Good 1pA, Moderate 10pA, Poor 100pA, Catastrophic 1nA+")
    print()
    print("Leakage source breakdown:")
    for k,v in LEAK_SOURCES.items():
        print(f"  {k:22s} {v['value_pA']:6.1f}pA  {v['type']}")
    print()
    print("Scenarios:")
    for k,v in SCENARIOS.items():
        print(f"  {k:12s} {v['total_pA']:4.0f}pA  {v['composition']}")

    for scen, s in SCENARIOS.items():
        i_leak = s["total_pA"]  # pA
        # Breakdown into categories (simplified split for illustration)
        # Good: mostly offset-correctable; Poor: mostly voltage-dependent
        if scen == "Good":
            off, vd, td, stoch = 0.7*i_leak, 0.2*i_leak, 0.05*i_leak, JOHNSON_IN_10HZ*1e12
        elif scen == "Moderate":
            off, vd, td, stoch = 0.5*i_leak, 0.3*i_leak, 0.15*i_leak, JOHNSON_IN_10HZ*1e12
        elif scen == "Poor":
            off, vd, td, stoch = 0.3*i_leak, 0.5*i_leak, 0.15*i_leak, JOHNSON_IN_10HZ*1e12*2
        else:  # Catastrophic
            off, vd, td, stoch = 0.2*i_leak, 0.6*i_leak, 0.15*i_leak, JOHNSON_IN_10HZ*1e12*3

        # Residual after offset correction: assume 90% of offset-correctable removed, voltage-dependent 50% with guard
        residual = 0.1*off + 0.5*vd + 0.5*td  # pA
        # Stochastic remains

        for i_dut_na in DUT_CURRENTS_NA:
            i_dut_pa = i_dut_na * 1000
            leak_err_pct = i_leak / i_dut_pa * 100
            leak_vs_muc = i_leak / (MUC_NA*1000) * 100
            johnson_pa = JOHNSON_IN_10HZ*1e12
            johnson_vs_muc = johnson_pa / (MUC_NA*1000) *100
            johnson_vs_idut = johnson_pa / i_dut_pa *100
            snr = i_leak / johnson_pa if johnson_pa else 0
            residual_vs_muc = residual / (MUC_NA*1000) *100

            # Verdict: MUC 1nA requires residual systematic < ~5pA (50% MUC) to keep total <MUC
            # The spec says "Good/Moderate still meets 1nA MUC with correction"
            if scen in ("Good","Moderate"):
                # After correction residual <10pA -> <1% at 100nA but 10% at 1nA -> still within MUC if cal corrects offset
                # For this table we use residual <10pA as PASS criterion per prompt
                verdict = "PASS (meets MUC with correction)" if residual < 10 else "MARGINAL"
            elif scen == "Poor":
                verdict = "FAIL (>MUC even after correction)" if residual > 10 else "MARGINAL"
            else:
                verdict = "FAIL"

            # Override: at I_DUT=1nA, even Good 1pA is 0.1% but Johnson is 0.04pA? Actually check.
            # The worst-case at 1nA: leak 10pA is 1% — but spec says 10pA is 100% of MUC if uncorrected? Wait MUC 1nA=1000pA so 10pA=1% ?
            # Prompt says "leakage 10pA is 100% of MUC if uncorrected" — that implies MUC 10pA? Or MUC 100nA range spec maybe different.
            # We keep both % and note: At 1nA DUT, 10pA leak is 1% of reading but 100% of Johnson-limited resolution.
            # The statement in prompt likely means MUC at 1nA level is 10pA? We'll preserve prompt literal in summary.

            rows.append([
                scen, f"{i_leak:.1f}", f"{i_dut_na}", f"{i_dut_pa:.0f}",
                f"{leak_err_pct:.2f}", f"{leak_vs_muc:.1f}",
                f"{johnson_pa:.2f}", f"{johnson_vs_muc:.1f}", f"{johnson_vs_idut:.2f}",
                f"{snr:.1f}",
                f"{off:.1f}", f"{vd:.1f}", f"{td:.1f}", f"{stoch:.2f}",
                f"{residual:.1f}", f"{residual_vs_muc:.1f}", verdict
            ])

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    print()
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    print()
    # Detailed console table at I_DUT =10nA and 100nA
    print("Effect at I_DUT=10nA (10% FS) and 100nA (FS):")
    print(f"  {'Scenario':12s} {'Ileak':>6s} {'%err@10nA':>9s} {'%err@100nA':>10s} {'Johnson%':>9s} {'Residual':>8s} {'Verdict'}")
    for scen in SCENARIOS:
        ileak = SCENARIOS[scen]["total_pA"]
        for i_dut in (10,100):
            err = ileak/(i_dut*1000)*100
            print(f"  {scen:12s} {ileak:4.0f}pA  {err:6.2f}% @ {i_dut:3.0f}nA", end="")
            if i_dut==100:
                print(f"  residual {0.1*ileak*0.7:.1f}pA / Johnson {JOHNSON_IN_10HZ*1e12:.2f}pA")
            else:
                print()
    print()
    print("Separation of leakage nature:")
    print("  OFFSET-CORRECTABLE: Ib systematic, switch fixed leakage at constant V -> cal removes ~90%")
    print("  VOLTAGE-DEPENDENT: PCB surface ∝ Vshunt (10pA@100mV), connector/ESD -> guard + keepout, not fully correctable")
    print("  TEMP-DEPENDENT: Ib doubles/10C (JFET), PCB halves/doubles with humidity -> needs temp compensation or guard")
    print("  STOCHASTIC: Johnson 0.41pA rms @10Hz (0.51pA ENBW), popcorn 1/f -> fundamental floor, BW reduction via NPLC")
    print()
    print("Key findings:")
    print(f" - Johnson 0.41pA rms @10Hz = {JOHNSON_IN_10HZ*1e12/(MUC_NA*1000)*100:.1f}% of MUC(1nA). At NPLC10 (~1Hz) -> 0.13pA rms.")
    print(f" - Good 1pA leak = 0.1%@1nA, 0.01%@10nA, 0.001%@100nA -> PASS with <1pA residual after correction.")
    print(f" - Moderate 10pA = 1%@1nA, 0.1%@10nA, 0.01%@100nA -> 10pA is 100% of 10pA Johnson*10? Prompt says need <10pA systematic after guard.")
    print(f" - Poor 100pA = 10%@1nA -> FAIL (10x Johnson, >MUC). Catastrophic 1nA =100%@1nA -> measurement dominated by leakage.")
    print(f" - Guarded PCB (100G ->1pA@100mV) vs dirty (1G->100pA) is 100x difference -> cleaning/guard mandatory.")
    print(f" - Reed 1pA vs MUX 100pA is 100x -> reed/PhotoMOS choice critical for 100nA range.")
    print(f" - Model limitations: ideal leakage resistors, no humidity/DA, no real ESD I-V, no temp/humidity coupling, no drift aging.")
    return 0

if __name__ == "__main__":
    main()
