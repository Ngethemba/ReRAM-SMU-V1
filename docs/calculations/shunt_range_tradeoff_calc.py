#!/usr/bin/env python3
"""
ReRAM-SMU V1 — Shunt Range Trade-off Calculations
Produces reproducible tables for docs/calculations/SHUNT_RANGE_TRADEOFF.md
Runs in .venv (numpy, pint optional). Primary source: datasheet-independent physics.

Formula:
  R = V_FS / I_FS
  P = I_FS^2 * R = I_FS * V_FS
  vn = sqrt(4*k*T*R*B)  [V rms, brickwall]
  in = vn / R           [A rms]
  ENBW factor: single-pole RC ENBW = 1.57 * fc -> vn_enbw = vn_brickwall * sqrt(1.57)
  Gain = V_ADC_FS / V_FS   (to map shunt FS to ADC FS)

Constants exact SI 2019.
"""
import math

k = 1.380649e-23  # J/K exact
T = 300.0  # K
q = 1.602176634e-19

ranges_A = [10e-3, 1e-3, 100e-6, 10e-6, 1e-6, 100e-9]  # 10 mA .. 100 nA
range_labels = ["10 mA", "1 mA", "100 uA", "10 uA", "1 uA", "100 nA"]
B_list = [10, 1000]  # Hz brickwall
burdens_mV = [100, 50, 25]

# ADC FS assumptions (differential, PGA=1)
V_ADC_FS_options = {
    "ADS1262 PGA=1 diff ±2.5V (5V span)": 2.5,  # magnitude
    "ADS1262 PGA=32 diff ±78mV": 0.078125,
    "STM32G4 internal 3.3V FS": 3.3,
}

def vn(R, B):
    return math.sqrt(4*k*T*R*B)

def calc_table(Vfs):
    rows=[]
    for label, Ifs in zip(range_labels, ranges_A):
        R = Vfs / Ifs
        P = Ifs * Vfs
        TC_err_ppm = 25 * 10  # 25 ppm/C * 10C = 250 ppm
        vn_dens = math.sqrt(4*k*T*R)  # V/sqrtHz
        vn_10 = vn(R, 10)
        vn_1k = vn(R, 1000)
        in_10 = vn_10 / R
        in_1k = vn_1k / R
        # currents in pA for readability
        rows.append((label, Ifs, R, P, vn_dens, vn_10, vn_1k, in_10, in_1k))
    return rows

def fmt_R(R):
    if R >= 1e6: return f"{R/1e6:.2f} MΩ"
    if R >= 1e3: return f"{R/1e3:.2f} kΩ"
    return f"{R:.1f} Ω"

def fmt_P(P):
    if P >= 1e-3: return f"{P*1e3:.2f} mW"
    if P >= 1e-6: return f"{P*1e6:.1f} µW"
    if P >= 1e-9: return f"{P*1e9:.0f} nW"
    return f"{P*1e12:.0f} pW"

# --- Print all burden tables ---
for Vfs_mV in burdens_mV:
    Vfs = Vfs_mV * 1e-3
    print(f"\n{'='*72}")
    print(f"Burden V_FS = {Vfs_mV} mV")
    print(f"{'Range':>8} | {'R_shunt':>10} | {'P@FS':>10} | {'vn dens':>12} | {'vn 10Hz':>10} | {'in 10Hz':>10} | {'in/FS 10Hz':>10} | Gain to 2.5V | Gain to 3.3V")
    print("-"*110)
    for label, Ifs, R, P, vn_d, vn10, vn1k, in10, in1k in calc_table(Vfs):
        in_ppm = in10/Ifs*1e6
        g25 = 2.5 / Vfs
        g33 = 3.3 / Vfs
        print(f"{label:>8} | {fmt_R(R):>10} | {fmt_P(P):>10} | {vn_d*1e9:6.2f} nV/rtHz | {vn10*1e6:6.3f} µV | {in10*1e12:7.2f} pA | {in_ppm:7.0f} ppm | {g25:6.1f}x | {g33:6.1f}x")

# --- Range-dependent burden philosophy ---
print("\n\nRANGE-DEPENDENT BURDEN CANDIDATE (hybrid, favoured):")
print("  10 mA / 1 mA : 25 mV FS  (keep headroom, keep dissipation low)")
print("  100 uA / 10 uA : 50 mV FS")
print("  1 uA / 100 nA  : 100 mV FS (maximise SNR where Johnson/leakage dominates)")
range_dep = [(10e-3, 25e-3),(1e-3, 25e-3),(100e-6, 50e-3),(10e-6, 50e-3),(1e-6, 100e-3),(100e-9, 100e-3)]
print(f"\n{'Range':>8} | {'VFS':>6} | {'R':>10} | {'P':>10} | {'vn dens':>12} | {'vn10':>10} | {'in10':>10} | {'ppm FS':>8}")
print("-"*90)
for (label, Ifs), (ifs2, Vfs) in zip(zip(range_labels, ranges_A), range_dep):
    assert Ifs==ifs2
    R = Vfs/Ifs
    P = Ifs*Vfs
    vn_d = math.sqrt(4*k*T*R)
    vn10 = vn(R,10)
    in10 = vn10/R
    print(f"{label:>8} | {Vfs*1e3:4.0f} mV | {fmt_R(R):>10} | {fmt_P(P):>10} | {vn_d*1e9:6.2f} nV/rtHz | {vn10*1e6:6.3f} µV | {in10*1e12:7.2f} pA | {in10/Ifs*1e6:6.0f} ppm")

# --- ADC amplitude and LSB ---
print("\n\nADC AMPLITUDE & LSB ANALYSIS")
for adc_name, Vadc in V_ADC_FS_options.items():
    print(f"\n  ADC FS = {Vadc*1e3:.1f} mV ({adc_name}):")
    for Vfs_mV in burdens_mV:
        Vfs = Vfs_mV*1e-3
        G = Vadc / Vfs
        print(f"    Burden {Vfs_mV:3d} mV -> Gain {G:5.1f}x  (atten <1 means direct without gain)")
    # range-dependent
    print(f"    Range-dependent -> gains: ", end="")
    for (label, Ifs), (ifs2, Vfs) in zip(zip(range_labels, ranges_A), range_dep):
        G = Vadc/Vfs
        print(f"{label}:{G:.0f}x ", end="")
    print()

# ADC LSB vs Johnson
print("\n\nADC LSB vs Johnson (ADS1262-like 32-bit ΔΣ, but ENOB matters)")
for bits in [16, 18, 24, 32]:
    for Vfs_mV in [100]:
        Vfs = Vfs_mV*1e-3
        lsb = Vfs / (2**bits)  # ideal LSB at shunt FS
        # referred to current on 100nA range
        R_100nA = Vfs / 100e-9
        lsb_i = lsb / R_100nA
        print(f"  {bits:2d}-bit LSB @ {Vfs_mV} mV FS = {lsb*1e9:.2f} nV = {lsb_i*1e15:.1f} fA on 100nA (R={fmt_R(R_100nA)})  vs Johnson in_10Hz={vn(R_100nA,10)/R_100nA*1e12:.2f} pA")

# DUT impact table
print("\n\nDUT BURDEN IMPACT (fractional error if not Kelvin-corrected)")
print(f"{'DUT R':>10} | {'I @0.5V':>10} | {'Vburden 100mV/10mA':>18} | {'Vburden 25mV/2.5Ω':>18} | {'Err 100mV':>8} | {'Err 25mV':>8}")
print("-"*90)
for Rdut in [1e3, 10e3, 100e3, 1e6, 10e6, 100e6]:
    I = 0.5 / Rdut
    # pick shunt that autorange would select (ceil to next range)
    # Determine autorange: smallest FS >= I
    # For 100 mV FS, R values as above; for 25 mV hybrid we use range-dep R for that range
    # Simplification: for 100 mV fixed
    # Find range index
    chosen = None
    for idx, Ifs in enumerate(ranges_A):
        if I <= Ifs:
            chosen = idx
    if chosen is None:
        chosen = 0  # clamp to 10 mA if >10 mA (overrange)
        # but I for 1k at 0.5V is 500uA <10mA so found
    # reverse: ranges are descending, find tightest that fits
    # Actually ranges_A is [10m,1m,100u,10u,1u,100n]; tightest means smallest FS >= I
    best = None
    for idx in range(len(ranges_A)-1, -1, -1):
        if I <= ranges_A[idx]:
            best = idx
            break
    if best is None:
        best = 0
    # 100 mV R for that range
    R100 = 100e-3 / ranges_A[best]
    Vb100 = I * R100
    # range-dep
    Vfs_dep = range_dep[best][1]
    Rdep = Vfs_dep / ranges_A[best]
    Vbdep = I * Rdep
    print(f"{Rdut/1e3:6.0f} kΩ | {I*1e6:7.2f} uA | {Vb100*1e3:10.3f} mV (R={fmt_R(R100):>7}) | {Vbdep*1e3:10.3f} mV (R={fmt_R(Rdep):>7}) | {Vb100/0.5*100:6.2f}% | {Vbdep/0.5*100:6.2f}%")

# Power dissipation extra
print("\n\nSELF-HEATING: ΔT = P * θJA (θJA typ  40–100 K/W for 0805/1206 on FR4)")
for theta in [50, 125]:
    print(f"\n  theta={theta} K/W:")
    for label, Ifs, R, P, *_ in calc_table(100e-3):
        dT = P * theta
        # TC 25 ppm/C -> gain error = dT * 25 ppm
        ge = dT * 25  # ppm
        print(f"    {label:>8} P={fmt_P(P):>8} dT={dT*1e3:6.2f} mK  gain err {ge:5.1f} ppm")

# Johnson ENBW correction
print("\n\nENBW CORRECTION: single-pole RC ENBW=1.57*fc -> multiply brickwall vn by sqrt(1.57)=1.253")
for R_test in [10, 1e3, 100e3, 1e6]:
    v_brick_10 = vn(R_test, 10)
    v_enbw_10 = v_brick_10 * math.sqrt(1.57)
    print(f"  R={fmt_R(R_test):>8} vn@10Hz brick {v_brick_10*1e9:.1f} nV -> ENBW {v_enbw_10*1e9:.1f} nV  (in {v_enbw_10/R_test*1e12:.2f} pA)")
