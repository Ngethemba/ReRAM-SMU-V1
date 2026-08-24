#!/usr/bin/env python3
"""
Gate 5 Test I — Filament-like transition energy
R: 1 MOhm -> 1 kOhm with transition times 1ms,100us,10us,1us,100ns
Captures: I_peak, V_DUT, takeover time, Q=∫I dt, E_DUT=∫V*I dt
Compares: LT1970A (4us), Ideal (0 delay), TLV3501 crowbar (~5ns at 120%), Full D (LT1970A+TLV backup)

Model:
  Vsrc  --Rsense--Riso--+--C_downstream--GND
                       +--R_dut(t)------GND
Node = Vdut. C = C_downstream after Riso. Upstream C (4.7-10nF before Riso) is isolated.
ODE: C*dV/dt + V/Rdut(t) = I_total ; I_total = (Vsrc - V)/Rseries  when not limited
     when limited, I_total = min(above, Ilim) and V = Ilim * Rdut || (capacitor dynamics)

We integrate with explicit Euler, dt = min(Ttrans/200, 10ns) but at least 1ns for 100ns case.
"""
import pathlib, csv, math
import numpy as np

# Canonical params
Vsrc = 2.0            # primary window; also evaluate 5V for budget check
Vsrc_5V = 5.0
C_down = 150e-12      # worst-case downstream target 150pF @5V = 1.875nJ borderline
C_down_100p = 100e-12
R_hrs = 1e6
R_lrs = 1e3
R_sense = 500.0       # 100uA FS -> 50mV burden (philosophy D)
R_iso = 47.0
R_series = R_sense + R_iso
Icomp = 100e-6        # 100 uA compliance
Vsense_thr = Icomp * R_sense  # 50 mV

# Architectures: (name, T_delay, trip_multiple, crowbar_flag)
ARCHS = [
    ("Ideal_compliance", 0.0, 1.00, False),
    ("LT1970A_4us", 4e-6, 1.00, False),
    ("TLV3501_crowbar_120pct", 4.5e-9, 1.20, True),
    ("Full_D_LT1970A_plus_TLV130", 4e-6, 1.30, True),  # LT regulation + TLV emergency at 130%
]

TRANS_TIMES = [1e-3, 100e-6, 10e-6, 1e-6, 100e-9]

def R_dut_of_t(t, t0, Ttrans):
    """Linear ramp from R_hrs to R_lrs over Ttrans starting at t0"""
    if t < t0:
        return R_hrs
    elif t < t0+Ttrans:
        frac = (t - t0)/Ttrans
        return R_hrs + (R_lrs - R_hrs)*frac
    else:
        return R_lrs

def simulate_one(Ttrans, arch, Vsrc=Vsrc, C=C_down):
    name, Tdelay, trip_mult, is_crowbar = arch
    Ilim = Icomp * trip_mult if is_crowbar else Icomp
    # threshold Vsense for limiter
    Vsense_lim = Ilim * R_sense

    t0 = 5e-6  # transition start
    t_end = t0 + Ttrans + 50e-6  # 50us window after snap to capture settling
    # dt choice
    dt = min(Ttrans/500 if Ttrans>0 else 1e-9, 10e-9)
    dt = max(dt, 0.5e-9)  # floor 0.5ns for 100ns case to still resolve
    # ensure at least 20000 points cap
    n = int((t_end)/dt)+1
    if n > 800000:
        dt = t_end/800000
        n = 800000
    # threshold for limiter activation tracking
    # compliance takeover time: first time Vsense exceeds thr + delay after which I is clamped
    takeover_time = None
    t_trip_detect = None
    ever_tripped = False

    Vdut = 0.0
    # initial steady state before transition: Vdut = Vsrc * Rdut/(Rdut+Rseries)
    Vdut = Vsrc * R_hrs/(R_hrs+R_series)
    I_peak = 0.0
    Q = 0.0
    E = 0.0
    I_dut_peak = 0.0
    V_dut_at_peak = 0.0

    # For E_cap reference
    E_cap = 0.5*C*Vsrc*Vsrc  # if cap was fully charged to Vsrc before snap (worst)

    t = 0.0
    for i in range(n):
        Rdut = R_dut_of_t(t, t0, Ttrans)
        # unlimited current that would flow through series resistor
        I_unlimited_series = (Vsrc - Vdut)/R_series if R_series>0 else 0
        # Idut and Ic
        Idut = Vdut / Rdut if Rdut>0 else 0
        Ic = C * 0  # will compute via dV
        I_total_unlimited = Idut + 0  # Ic is dynamic, not static
        # Determine if limiter should be active (after delay)
        Vsense_unlimited = I_unlimited_series * R_sense  # approx total current * Rsense (since series current ~ total)
        # More accurate: total current through Rsense is Idut+Ic
        # But Ic = C*dV/dt unknown until we step, so we estimate series current
        # Use I_unlimited_series as proxy; for limited case we clamp I_total

        # Trip detection: when Vsense exceeds threshold
        if not ever_tripped and Vsense_unlimited >= Vsense_lim:
            ever_tripped = True
            t_trip_detect = t

        # Determine effective I_total limit
        limit_active = False
        if ever_tripped and (t - t_trip_detect) >= Tdelay:
            limit_active = True
            if takeover_time is None:
                takeover_time = t - t_trip_detect  # approx Tdelay

        if limit_active:
            # Crowbar vs linear limit
            if is_crowbar:
                # Crowbar pulls Vdut toward ~0.1V through low Ron (2 ohm) — energy dumped not through DUT but through FET
                # Model: Vdut clamped to Vclamp = Ilim*Ron_crowbar? Actually crowbar shorts node to GND via Ron
                # For E_DUT we still compute Vdut*Idut, but Vdut collapses quickly.
                Ron_crowbar = 2.0
                # Effective Vdut after crowbar = Idut * (Rdut || Ron) ??? Simpler: force Vdut to collapse with tau = Ron*C
                # We model that I_total is not limited but Vdut is pulled low.
                # Approx: limit Vdut to V_crow = 0.05  (residual)
                Vdut_target = 0.05
                # drive Vdut toward target with limited slew via Ron*C? Use exponential decay toward target
                # We'll just clamp Vdut directly toward target without solving Ic separately
                # Compute dV that would happen with crowbar active: dV/dt = (V_target - Vdut)/(Ron*C)  ??? use series?
                # Simpler: set Vdut = max(Vdut - dt*(Vdut - V_target)/(Ron*C*1 + dt), V_target)
                # To avoid complexity, we treat crowbar as ideal limit that collapses Vdut within ~3*Ron*C (~0.9ns for 150pF)
                # So Vdut decays rapidly.
                tau_crow = Ron_crowbar * C
                Vdut = Vdut + (Vdut_target - Vdut) * (1 - math.exp(-dt/max(tau_crow,1e-12)))
                # Recompute Idut after clamp
                Idut = Vdut / Rdut if Rdut>0 else 0
                I_total = Idut + C*(Vdut_target - Vdut)/dt if False else Idut # Ic handled via Vdut motion
            else:
                # Linear CC: total current capped to Ilim
                # Node equation: C*dV/dt = Ilim - V/Rdut
                dVdt = (Ilim - Vdut/Rdut)/C if C>0 else 0
                Vdut_new = Vdut + dVdt*dt
                # Also cannot exceed Vsrc limited value, and cannot go negative
                Vdut_new = max(min(Vdut_new, Vsrc), 0)
                Vdut = Vdut_new
                Idut = Vdut / Rdut
                I_total = Ilim
        else:
            # Not limited: normal RC dynamics
            # C*dV/dt = (Vsrc - Vdut)/R_series - Vdut/Rdut
            dVdt = ((Vsrc - Vdut)/R_series - Vdut/Rdut)/C if C>0 else 0
            # Clamp dVdt to avoid instability with large dt
            Vdut = Vdut + dVdt*dt
            Idut = Vdut / Rdut
            I_total = (Vsrc - Vdut)/R_series

        # Track peaks and integrals
        if abs(I_total) > abs(I_peak):
            I_peak = I_total
            I_dut_peak = Idut
            V_dut_at_peak = Vdut
        # Integrate Q and E over this step (use Idut for DUT energy? spec says E_DUT=∫V_DUT*I_DUT dt)
        # Q is ∫I_DUT? Actually spec says Q=∫I dt — ambiguous; we use I_DUT for Q_dut and I_total for Q_total, report I_DUT
        Q += abs(Idut)*dt
        E += abs(Vdut * Idut)*dt

        t += dt
        if t > t_end:
            break

    # If never tripped, takeover is NaN
    takeover_us = (takeover_time*1e6) if takeover_time is not None else float('nan')
    return dict(
        I_peak_A=I_peak,
        I_dut_peak_A=I_dut_peak,
        V_dut_at_peak_V=V_dut_at_peak,
        V_final_V=Vdut,
        takeover_us=takeover_us,
        Q_nC=Q*1e9,
        E_dut_nJ=E*1e9,
        E_cap_nJ=E_cap*1e9,
        ratio_Ecap_to_Edut=(E_cap/E if E>0 else float('nan')),
        E_total_minus_cap_nJ=(E - E_cap)*1e9,
    )

def main():
    out_path = pathlib.Path(__file__).parent / "test_I_results.csv"
    # Also check sibling path for fault simulation outputs? Keep here.
    rows = []
    header = ["Vsrc_V","C_down_pF","transition_s","architecture","Tdelay_us","trip_multiple",
              "I_peak_mA","I_dut_peak_mA","V_dut_at_peak_V","V_final_V","takeover_us",
              "Q_nC","E_dut_nJ","E_cap_0p5CV2_nJ","E_minus_cap_nJ","ratio_cap_over_Edut","note"]
    for V in [Vsrc, Vsrc_5V]:
        C = C_down if V==Vsrc else C_down_100p  # at 5V use 100pF budget check
        for Ttrans in TRANS_TIMES:
            for arch in ARCHS:
                res = simulate_one(Ttrans, arch, Vsrc=V, C=C)
                rows.append([
                    V, C*1e12, Ttrans, arch[0], arch[1]*1e6, arch[2],
                    res["I_peak_A"]*1e3, res["I_dut_peak_A"]*1e3, res["V_dut_at_peak_V"], res["V_final_V"],
                    res["takeover_us"], res["Q_nC"], res["E_dut_nJ"], res["E_cap_nJ"], res["E_total_minus_cap_nJ"], res["ratio_Ecap_to_Edut"],
                    "cap_underestimates" if res["E_dut_nJ"]>res["E_cap_nJ"]*1.05 else "cap_dominates"
                ])
    # Write CSV
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"Wrote {out_path} with {len(rows)} rows")

    # Print summary table for 2V 150pF
    print("\n=== Test I Summary @2V 150pF ===")
    for Ttrans in TRANS_TIMES:
        print(f"\nTtrans={Ttrans*1e6:.1f} us:")
        for arch in ARCHS:
            # find row
            for r in rows:
                if r[0]==2.0 and abs(r[2]-Ttrans)<1e-12 and r[3]==arch[0]:
                    print(f"  {arch[0]:28s} Ipeak={r[6]:6.3f} mA  Vfinal={r[9]:.3f}V  takeover={r[10]:.2f}us  Q={r[11]:.3f}nC  E_dut={r[12]:.3f}nJ  Ecap={r[13]:.3f}nJ  E_extra={r[14]:.3f}nJ")
    print("\nKey finding: 0.5*C*V^2 = 0.30 nJ @2V 150pF; for slow transitions (1ms) total E_dut >> E_cap due to sustained Icomp*V_LRS*t.")
    print("For 100ns snap, E_cap dominates if limiter is fast; LT1970A 4us delay adds ~ Icomp*V_LRS*4us = 0.04nJ extra.")
    print("At 5V 100pF, Ecap=1.25nJ which already exceeds 1nJ gentle budget.")

if __name__ == "__main__":
    main()
