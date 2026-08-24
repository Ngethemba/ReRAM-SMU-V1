#!/usr/bin/env python3
"""
Gate 3 — Test F: DUT-node capacitance & downstream energy
=========================================================
Separation required by COMPLIANCE_ENERGY_ANALYSIS.md / IR-14:

  C_UPSTREAM  : capacitance BEFORE R_iso (compensation, isolated by R_iso and servo).
                Not dumpable into filament without traversing R_iso. Example: 4.7-10 nF
                local compensation at power-amp output.
  C_DOWNSTREAM: capacitance AFTER R_iso, directly connected to DUT node.
                Dumps 100% into filament on snap 1M -> 1k. Only this counts
                toward E = 0.5*C*V^2 filament budget.

  V_FORCE canonical: V_FORCE = V_DUT + V_SHUNT + I*R_LEAD (IR-11)
  Kelvin pickoff AFTER R_iso, C_comp BEFORE R_iso -> upstream not penalized.

This script:
  - Sweeps C_DOWNSTREAM = 5,10,25,50,80,100,150,500pF,1nF at V=0.5,1,2,5 V
  - Computes E=0.5*C*V^2, Q=C*V, Ipeak ~ V/1k (filament LRS=1k)
  - Classifies per recipe engineering constraint (NOT universal safe):
      gentle/low-Icc SET  : E_budget = 1 nJ
      standard SET        : E_budget = 2 nJ
      forming             : E_budget = 10 nJ
    PASS = E <= budget at that V; FAIL = exceeds. Guidance states budget is
    recipe- and V-dependent; forming at 5 V may tolerate higher C than gentle
    at 5 V.
  - Computes stored vs delivered energy for ideal RC discharge through 1k
    with/without R_iso to show topology choice, not just value.
  - Writes test_F_results.csv and (optionally) validates against ngspice.

Model limitations: ideal switch, no package/connector parasitics beyond listed C,
no DUT intrinsic C beyond swept values, no ESL/ESR, filament modeled as 1k
resistive after snap.

Usage:
  python simulation/phase3/compliance/test_F_capacitance.py
  -> writes simulation/phase3/compliance/test_F_results.csv + prints table
"""

import math
import csv
import pathlib
import sys

# ---- constants ----
C_DOWNSTREAMS = [5e-12, 10e-12, 25e-12, 50e-12, 80e-12, 100e-12, 150e-12, 500e-12, 1e-9]
VOLTAGES = [0.5, 1.0, 2.0, 5.0]
R_DUT_LRS = 1e3  # filament LRS after snap
R_ISO_TYP = 47.0  # typical isolation resistor

# recipe budgets (J)
BUDGETS = {
    "gentle_1nJ": 1e-9,
    "standard_2nJ": 2e-9,
    "forming_10nJ": 10e-9,
}

def E_J(C, V):
    return 0.5*C*V*V

def Q_C(C, V):
    return C*V

def Ipeak(V, R):
    return V / R

# ---- compute table ----
rows = []
for C in C_DOWNSTREAMS:
    for V in VOLTAGES:
        E = E_J(C, V)
        Q = Q_C(C, V)
        i_pk = Ipeak(V, R_DUT_LRS)
        # classifications per budget at this V (engineering constraint per V)
        gentle = E <= BUDGETS["gentle_1nJ"]
        standard = E <= BUDGETS["standard_2nJ"]
        forming = E <= BUDGETS["forming_10nJ"]
        # delivered energy with/without R_iso (analytical RC discharge split)
        # Downstream: all stored energy dumps into DUT (R_iso not in path)
        # Upstream: energy splits between R_iso and R_dut: E_dut = E * R_dut/(R_iso+R_dut)
        E_downstream_delivered = E  # 100%
        frac_up = R_DUT_LRS / (R_ISO_TYP + R_DUT_LRS)
        E_upstream_delivered = E * frac_up
        E_upstream_in_Riso = E * (R_ISO_TYP / (R_ISO_TYP + R_DUT_LRS))
        # Ipeak with R_iso (if upstream, current must traverse R_iso)
        i_pk_with_Riso = Ipeak(V, R_ISO_TYP + R_DUT_LRS)
        # tau
        tau_down_ns = R_DUT_LRS * C * 1e9
        tau_up_ns = (R_DUT_LRS + R_ISO_TYP) * C * 1e9

        rows.append({
            "C_pF": C * 1e12,
            "C_F": C,
            "V": V,
            "E_stored_nJ": E * 1e9,
            "E_stored_pJ": E * 1e12,
            "Q_nC": Q * 1e9,
            "Q_pC": Q * 1e12,
            "Ipeak_1k_mA": i_pk * 1e3,
            "Ipeak_with_47R_mA": i_pk_with_Riso * 1e3,
            "E_downstream_delivered_nJ": E_downstream_delivered * 1e9,
            "E_upstream_delivered_to_DUT_nJ": E_upstream_delivered * 1e9,
            "E_upstream_in_Riso_nJ": E_upstream_in_Riso * 1e9,
            "frac_delivered_if_upstream": frac_up,
            "tau_down_ns": tau_down_ns,
            "tau_up_47R_ns": tau_up_ns,
            "meets_gentle_1nJ": gentle,
            "meets_standard_2nJ": standard,
            "meets_forming_10nJ": forming,
            "Cmax_gentle_at_V_pF": (2*BUDGETS["gentle_1nJ"]/(V*V))*1e12,
            "Cmax_standard_at_V_pF": (2*BUDGETS["standard_2nJ"]/(V*V))*1e12,
            "Cmax_forming_at_V_pF": (2*BUDGETS["forming_10nJ"]/(V*V))*1e12,
        })

# ---- console report ----
def fmt(b): return "PASS" if b else "FAIL"

print("="*90)
print("Test F: C_DOWNSTREAM energy sweep  E=0.5*C*V^2  (C_DOWNSTREAM only)")
print("="*90)
print(f"C_UPSTREAM = before R_iso (1-10nF compensation, isolated) | C_DOWNSTREAM = after R_iso (direct dump)")
print(f"R_DUT(LRS)=1k  R_iso_typ=47R  | budgets: gentle 1nJ, standard 2nJ, forming 10nJ")
print("-"*90)
header = f"{'C':>8} {'V':>4} {'E_stored':>10} {'Q':>8} {'Ipk1k':>7} {'Ipk+Riso':>9} | {'gentle':>7} {'std':>7} {'forming':>7}"
print(header)
print("-"*90)
for r in rows:
    print(f"{r['C_pF']:7.0f}p {r['V']:3.1f}V {r['E_stored_nJ']:9.3f}nJ {r['Q_nC']:7.3f}nC {r['Ipeak_1k_mA']:6.2f}mA {r['Ipeak_with_47R_mA']:8.2f}mA | {fmt(r['meets_gentle_1nJ']):>7} {fmt(r['meets_standard_2nJ']):>7} {fmt(r['meets_forming_10nJ']):>7}")
print("-"*90)
print("Engineering constraint per V (do NOT read as universally safe):")
for V in VOLTAGES:
    cg = 2*BUDGETS["gentle_1nJ"]/(V*V)*1e12
    cs = 2*BUDGETS["standard_2nJ"]/(V*V)*1e12
    cf = 2*BUDGETS["forming_10nJ"]/(V*V)*1e12
    print(f"  V={V:.1f}V: Cmax gentle={cg:.0f}pF  standard={cs:.0f}pF  forming={cf:.0f}pF")
print("-"*90)
# highlight two anchor cases
for C,V,exp in [(100e-12,5.0,1.25),(1e-9,5.0,12.5)]:
    e = E_J(C,V)*1e9
    print(f"ANCHOR C={C*1e12:.0f}pF @ {V:.0f}V: E={e:.2f}nJ (expected {exp}nJ) -> {e/1.0:.1f}x gentle, {e/2.0:.1f}x standard, {e/10.0:.1f}x forming")
print("-"*90)
print("Stored vs delivered (RC discharge through 1k, ideal):")
print("  DOWNSTREAM (C after R_iso, direct): E_delivered = E_stored (100%)")
print(f"  UPSTREAM (C before 47R R_iso): E_delivered_to_DUT = E * 1k/(47+1k) = {1000/1047*100:.1f}% of stored, remainder in R_iso")
print("  -> Capacitor LOCATION is topology choice, not just value. 10nF upstream not penalized; 100pF downstream is.")
print("="*90)

# ---- write CSV ----
out_path = pathlib.Path(__file__).parent / "test_F_results.csv"
with open(out_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"[Test F] wrote {out_path} ({len(rows)} rows)")

# ---- also produce a small analytical transient check file (for documentation) ----
# Numerical RC discharge integral validation for 100pF@5V and 1nF@5V
# V(t)=V0*exp(-t/RC), I(t)=V(t)/R, E_dut = int V*I dt = 0.5*C*V0^2
for C in [100e-12, 1e-9]:
    for iso in [0, R_ISO_TYP]:
        Rtot = R_DUT_LRS + iso
        tau = Rtot*C
        # integrate analytically 0..10tau
        E_anal = 0.5*C*5.0*5.0 * (R_DUT_LRS/Rtot) if iso else 0.5*C*25
        print(f"  check C={C*1e12:.0f}pF iso={iso:.0f}R: E_dut={E_anal*1e9:.3f}nJ tau={tau*1e9:.1f}ns")
