#!/usr/bin/env python3
"""
preliminary_error_budget.py — reproduction for PRELIMINARY_ERROR_BUDGET.md
Computes Johnson noise, RSS source U at 2/1/0.1 V, and per-range current U vs targets.
"""

import math

k = 1.380649e-23
T = 300.0
B = 10.0
ENBW_factor = math.pi/2  # single-pole
sqrt3 = math.sqrt(3)

def u_rect(a):
    return a / sqrt3

def johnson_v(R):
    return math.sqrt(4*k*T*R*B)

def johnson_v_enbw(R):
    return johnson_v(R) * math.sqrt(ENBW_factor)

# Source budget post-cal at points
def source_budget(point_v, use_ad5764=False, resistor_tol=0.01):  # tol in %
    # contributions 1sigma
    if use_ad5764:
        inl = 152e-6 / sqrt3  # ±152µV @ ±5V mode
    else:
        inl = 305e-6 / sqrt3 /2  # Actually 152µV on 5V FS but system x2 → 305µV /√3 =176µV ; keep 176
        inl = 176e-6
    gain_resid = (0.01/100 * 5.0) / sqrt3  # 0.01% of 5V FS =500uV /√3=289uV (system 10V span but gain residual scales)
    # Actually at point_v reading, gain error is proportional to reading? Simplify: gain residual 0.01% of reading + ratio error
    offset_resid = 100e-6 / sqrt3  # ±100uV trimmed
    ref_drift = (2e-6 * 3 * point_v) / sqrt3  # 2ppm/C *3C *point
    # resistor ratio error for AD5686R only
    if not use_ad5764:
        ratio = (resistor_tol/100 * point_v) / sqrt3
        ratio_tc = (10e-6 * 3 * point_v) / sqrt3 if resistor_tol==0.01 else (25e-6*3*point_v)/sqrt3
    else:
        ratio = 0
        ratio_tc = 0
    amp_vos = 5e-6 / sqrt3
    power = 300e-6 / sqrt3 if not use_ad5764 else 150e-6 / sqrt3  # cal residual
    uc = math.sqrt(inl**2 + gain_resid**2 + offset_resid**2 + ref_drift**2 + ratio**2 + ratio_tc**2 + amp_vos**2 + power**2)
    return uc, 2*uc

print("=== Source voltage budget post-cal (1σ, k=2) ===")
for pt in [2.0, 1.0, 0.1]:
    for ad5764 in [False, True]:
        uc, U = source_budget(pt, use_ad5764=ad5764, resistor_tol=0.01 if not ad5764 else 0.01)
        target = 0.0002*pt + 0.0001*5  # 0.02% reading +0.01%FS (5V)
        head = (target - U)/target*100
        print(f"  {'AD5764' if ad5764 else 'AD5686R'} @ {pt:4.1f} V: uc={uc*1e6:6.1f} µV U={U*1e6:6.1f} µV target={target*1e6:.0f} µV headroom={head:+.1f}%")
print()

# Johnson table
print("=== Johnson noise at B=10 Hz brickwall (and ENBW) ===")
for label, R in [("10mA",10), ("1mA",100), ("100uA",1000), ("10uA",1e4), ("1uA",1e5), ("100nA",1e6)]:
    v = johnson_v(R)
    ven = johnson_v_enbw(R)
    i = v / R
    ien = ven / R
    print(f"  {label:5s} R={R:>7.0f}Ω v={v*1e9:6.2f} nV ven={ven*1e9:6.2f} nV i={i*1e12:6.2f} pA i_en={ien*1e12:6.2f} pA")
print()

# Per-range current budget — FIX: 0.1% =0.001 fraction, 0.01% =0.0001
print("=== Per-range current budget post-cal (at 50% FS) — docs numbers use 0.1% shunt ===")
targets = {
    "10mA": (5e-3, 0.0003*5e-3 + 10e-6),
    "1mA": (500e-6, 0.0003*500e-6 + 1e-6),
    "100uA": (50e-6, 0.0005*50e-6 + 200e-9),
    "10uA": (5e-6, 0.0008*5e-6 + 20e-9),
    "1uA": (500e-9, 0.001*500e-9 + 5e-9),
    "100nA": (50e-9, 0.003*50e-9 + 60e-12),
}
fs_map = {"10mA":10e-3, "1mA":1e-3, "100uA":100e-6, "10uA":10e-6, "1uA":1e-6, "100nA":100e-9}
for label, R in [("10mA",10), ("1mA",100), ("100uA",1000), ("10uA",1e4), ("1uA",1e5), ("100nA",1e6)]:
    reading = targets[label][0]
    target_k2 = targets[label][1]
    # 0.1% shunt default, 0.01% tight option shown for 100nA/1uA
    shunt_frac = 0.001  # 0.1%
    if label in ("1uA","100nA"):
        shunt_frac_tight = 0.0001  # 0.01%
    shunt_tol = shunt_frac * reading / sqrt3
    tc = 25e-6*3 * reading / sqrt3
    if label in ("10mA", "1mA", "100uA", "10uA"):
        vos = 5e-6  # ADA4522
        amp = vos / R
    else:
        vos_max = 120e-6  # OPA140 max
        vos_typ = 30e-6
        amp_max = vos_max / R
        amp_typ = vos_typ / R
        amp = amp_max  # worst; typ shown alternate below
    ileak = 1e-12 / sqrt3  # reed; MUX would be 100pA/√3=58pA
    adc = 10e-6 * fs_map[label] / sqrt3
    uc = math.sqrt(shunt_tol**2 + tc**2 + amp**2 + ileak**2 + adc**2)
    U = 2*uc
    head = (target_k2 - U)/target_k2*100
    # also compute tight 0.01% + typ Vos for low ranges
    if label in ("1uA","100nA"):
        shunt_tight = shunt_frac_tight * reading / sqrt3
        uc_tight = math.sqrt(shunt_tight**2 + tc**2 + amp_typ**2 + ileak**2 + adc**2)
        U_tight = 2*uc_tight
        head_tight = (target_k2 - U_tight)/target_k2*100
        print(f"  {label:5s} @ {reading*1e9:6.0f} nA: uc={uc*1e12:6.1f} pA U={U*1e12:6.1f} pA target={target_k2*1e12:.0f} pA headroom={head:+.1f}%  [tight 0.01%+typ {uc_tight*1e12:.1f}/{U_tight*1e12:.0f} head {head_tight:+.1f}%]")
    else:
        print(f"  {label:5s} @ {reading*1e9:6.0f} nA: shunt={shunt_tol*1e12:6.0f}pA tc={tc*1e12:5.1f}pA amp={amp*1e12:6.1f}pA adc={adc*1e12:5.1f}pA -> uc={uc*1e12:6.0f}pA U={U*1e12:6.0f}pA target={target_k2*1e12:.0f}pA headroom={head:+.1f}%")
