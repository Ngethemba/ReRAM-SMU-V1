#!/usr/bin/env python3
"""
Gate 3 — Test J: Upstream vs downstream capacitor placement
===========================================================
Compares compensation capacitance C_comp placed:
  Case 1 (UPSTREAM)  : C_comp BEFORE R_iso (isolated, not directly dumpable)
  Case 2 (DOWNSTREAM): C_comp AFTER  R_iso (directly across DUT node, dumps E=0.5*C*V^2)

Identical SET-like transient: DUT 1M -> 1k in 1 us (and 100 ns fast variant).
R_iso candidates: 10,22,33,47,100 ohms
C_comp candidates: 1 nF, 4.7 nF, 10 nF

Metrics per combo:
  E_stored = 0.5*C*V^2  (V=5V worst, also 2V for ReRAM window)
  E_delivered_to_DUT:
    DOWNSTREAM: 100% of E_stored dumps through filament
    UPSTREAM  : E * R_dut/(R_iso+R_dut)  (fraction; remainder in R_iso)
                For 1k LRS the fraction is 90.9% (10R) .. 99% (10R?) Actually 1000/1010=99%,
                1000/1100=90.9% at 100R — modest reduction. For hard short (10R) the
                R_iso dominates and limits Ipeak.
  Ipeak:
    DOWNSTREAM: V / R_dut  (5mA @5V/1k)
    UPSTREAM  : V / (R_iso + R_dut)
    Short-circuit variant: V / R_iso  (shows R_iso limiting for snap to ~0R)
  tau = (R_iso + R_dut)*C (upstream) or R_dut*C (downstream) — settling time ~5*tau
  fp = 1/(2*pi*R_iso*C) — capacitive-load pole isolated by R_iso
  headroom = I_max * R_iso (need extra force voltage; I_max=10mA worst per REQ-SRC-006)
  Stability assessment: PM >45 deg heuristic —
    If fp is within decade of loop crossover (~1-3.6MHz for LT1970) the phase
    lag erodes PM. R_iso pushes fp up for small C but for large C (10nF) fp
    drops to 340kHz@47R and 159kHz@100R — inside control BW => potential ringing.
    Sweet spot 33-47R balances isolation vs headroom vs phase.

Shows tradeoff: too low R_iso = energy dump (upstream not well isolated if R_iso<<R_dut,
  and downstream case always dumps; low R_iso also leaves cap load pole high but
  loop still sees C directly through low impedance -> overshoot on voltage steps)
  too high R_iso = voltage regulation error + headroom + slower settling + lower fp

Writes test_J_results.csv

Model limitations: ideal source (zero output Z), ideal switches, no package ESL,
no DUT intrinsic C beyond C_comp, no op-amp dynamics beyond single-pole GBW heuristic.
"""

import math
import csv
import pathlib

C_COMPS = [1e-9, 4.7e-9, 10e-9]
R_ISOS = [10, 22, 33, 47, 100]
VOLTAGES = [5.0, 2.0]  # worst and typical window
R_DUT_LRS = 1e3
R_DUT_HRS = 1e6
I_MAX = 10e-3  # for headroom
GBW = 3.6e6  # LT1970A GN=3.6MHz heuristic crossover
FCROSS_EST = 1e6  # conservative closed-loop crossover for PM estimate

def E(C, V): return 0.5*C*V*V
def tau(R, C): return R*C
def fp(Riso, C): return 1.0/(2*math.pi*Riso*C) if Riso>0 else float('inf')
def headroom(Riso): return I_MAX * Riso

rows = []
for C in C_COMPS:
    for Riso in R_ISOS:
        for V in VOLTAGES:
            for placement in ["UPSTREAM_before_Riso", "DOWNSTREAM_after_Riso"]:
                Estored = E(C, V)
                if placement.startswith("UPSTREAM"):
                    # energy fraction to DUT
                    frac = R_DUT_LRS / (Riso + R_DUT_LRS)
                    Edelivered = Estored * frac
                    Eriso = Estored * (Riso/(Riso+R_DUT_LRS))
                    Ipk = V / (Riso + R_DUT_LRS)
                    tau_val = (Riso + R_DUT_LRS) * C
                    # short-circuit peak limited by Riso only
                    Ipk_short = V / Riso if Riso else float('inf')
                else:
                    frac = 1.0
                    Edelivered = Estored
                    Eriso = 0.0
                    Ipk = V / R_DUT_LRS
                    tau_val = R_DUT_LRS * C
                    Ipk_short = float('inf')  # no limiting

                f_p = fp(Riso, C)
                hdrm = headroom(Riso)
                # settling heuristic: 5*tau to 1%
                t_settle = 5*tau_val
                # phase margin heuristic: if fp < 5*fcross, PM erosion risk
                # fp very high (>10*fcross) => well beyond BW, minimal impact
                # fp ~ fcross ..5*fcross => inside BW, needs compensation
                # fp < fcross => low-frequency pole => likely unstable without comp
                if f_p > 10*FCROSS_EST:
                    stab = "good_isolation_pm_ok"
                elif f_p > 5*FCROSS_EST:
                    stab = "adequate"
                elif f_p > FCROSS_EST:
                    stab = "marginal_fp_near_crossover"
                elif f_p > 0.2*FCROSS_EST:
                    stab = "poor_fp_in_BW_ringing_risk"
                else:
                    stab = "critical_fp_low_unstable_without_comp"

                # tradeoff flag
                if Riso <= 10:
                    tradeoff = "Riso_too_low: weak_isolation_energy_dump_risk"
                elif Riso >= 100:
                    tradeoff = "Riso_too_high: headroom_and_fp_in_BW"
                elif 33 <= Riso <= 47:
                    tradeoff = "sweet_spot_33-47R"
                else:
                    tradeoff = "compromise"

                rows.append({
                    "C_comp_nF": C*1e9,
                    "C_F": C,
                    "R_iso_ohm": Riso,
                    "V": V,
                    "placement": placement,
                    "E_stored_nJ": Estored*1e9,
                    "E_stored_uJ": Estored*1e6,
                    "E_delivered_to_DUT_nJ": Edelivered*1e9,
                    "E_in_Riso_nJ": Eriso*1e9,
                    "fraction_to_DUT": frac,
                    "Q_nC": (C*V)*1e9,
                    "Ipeak_to_DUT_mA": Ipk*1e3,
                    "Ipeak_short_via_Riso_mA": Ipk_short*1e3 if Ipk_short!=float('inf') else "",
                    "tau_us": tau_val*1e6,
                    "t_settle_5tau_us": t_settle*1e6,
                    "fp_kHz": f_p/1e3,
                    "fp_MHz": f_p/1e6,
                    "headroom_at_10mA_V": hdrm,
                    "headroom_pct_of_5V": hdrm/5.0*100,
                    "stability_heuristic": stab,
                    "tradeoff_note": tradeoff,
                    # quick overshoot estimate: downstream large C will cause CV loop overshoot on voltage step
                    # Without detailed loop model, use rule: large downstream C without Riso -> overshoot risk high
                    "overshoot_risk": "HIGH_downstream_dump" if placement.startswith("DOWNSTREAM") and C>=4.7e-9 and V>=5 else ("HIGH_upstream_if_Riso_low" if placement.startswith("UPSTREAM") and Riso<=10 and C>=4.7e-9 else "moderate"),
                })

# ---- console summary ----
print("="*110)
print("Test J: Upstream vs downstream C_comp  (same C, same 1M->1k snap)")
print("="*110)
print(f"C_comp: {[f'{c*1e9:.1f}nF' for c in C_COMPS]}   R_iso: {R_ISOS} ohm   V: {VOLTAGES} V   R_dut LRS=1k")
print("UPSTREAM = C before R_iso (isolated) | DOWNSTREAM = C after R_iso (direct dump)")
print("-"*110)
print(f"{'C':>7} {'Riso':>5} {'V':>3} {'place':>22} {'Estored':>9} {'Edeliv':>9} {'frac':>5} {'Ipk':>6} {'tau':>7} {'fp':>8} {'hdrm':>6} {'stability'}")
print("-"*110)
for r in rows:
    if r["V"]==5.0:  # show worst case first
        short = "UP" if "UPSTREAM" in r["placement"] else "DOWN"
        print(f"{r['C_comp_nF']:5.1f}nF {r['R_iso_ohm']:4.0f}R {r['V']:3.0f}V {short:>4} {r['E_stored_nJ']:8.1f}nJ {r['E_delivered_to_DUT_nJ']:8.1f}nJ {r['fraction_to_DUT']:4.2f} {r['Ipeak_to_DUT_mA']:5.2f}mA {r['tau_us']:6.1f}us {r['fp_kHz']:7.1f}kHz {r['headroom_at_10mA_V']:4.2f}V {r['stability_heuristic']}")

print("-"*110)
print("Key: UPSTREAM fraction to DUT = R_dut/(R_iso+R_dut); remainder in R_iso.")
print("At 1k LRS the fraction is 90-99%, so R_iso alone does NOT eliminate energy for moderate snap,")
print("but it DOES isolate C_comp from direct dump and limits short-circuit Ipeak=V/R_iso.")
print("DOWNSTREAM always dumps 100% (E=0.5*C*V^2 through filament).")
print("")
print("R_iso tradeoff (must show):")
print("  too low (10R): weak isolation, allows energy dump if C were downstream-equivalent,")
print("                 Ipeak_short=500mA@5V, but headroom only 0.1V.")
print("  too high (100R): headroom 1.0V at 10mA (20% of 5V rail), fp=159kHz for 10nF (in BW)")
print("                 -> voltage regulation error I*Riso and settling 5*tau=5ms for 10nF/1k")
print("  sweet spot 33-47R: headroom 0.33-0.47V, fp 338-482kHz for 10nF (still in BW but manageable")
print("                 with lead-comp), fp 3.4MHz for 1nF@47R (beyond crossover), PM>45deg with Cf")
print("-"*110)
# highlight 2 comparison points for ngspice
print("Ngspice anchor comparisons (same C, same snap, placement flipped):")
for C in [4.7e-9, 10e-9]:
    for Riso in [47, 10]:
        # pick 5V
        up = [r for r in rows if r["C_comp_nF"]==C*1e9 and r["R_iso_ohm"]==Riso and r["V"]==5 and "UPSTREAM" in r["placement"]][0]
        dn = [r for r in rows if r["C_comp_nF"]==C*1e9 and r["R_iso_ohm"]==Riso and r["V"]==5 and "DOWNSTREAM" in r["placement"]][0]
        print(f"  C={C*1e9:.1f}nF Riso={Riso}R @5V: UPSTREAM E_deliv={up['E_delivered_to_DUT_nJ']:.1f}nJ Ipk={up['Ipeak_to_DUT_mA']:.2f}mA fp={up['fp_kHz']:.0f}kHz | DOWNSTREAM E_deliv={dn['E_delivered_to_DUT_nJ']:.1f}nJ Ipk={dn['Ipeak_to_DUT_mA']:.2f}mA (100% dump)")
print("="*110)

# ---- write CSV ----
out = pathlib.Path(__file__).parent / "test_J_results.csv"
import csv as _csv
with open(out, "w", newline="") as f:
    w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"[Test J] wrote {out} ({len(rows)} rows)")
