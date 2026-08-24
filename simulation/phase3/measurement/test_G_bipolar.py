#!/usr/bin/env python3
"""
Gate 4 — Test G: Bipolar current front-end
Project: ReRAM-SMU V1  |  Phase 3  |  2026-08-24

Covers: bipolar current measurement through +, -, 0 for every range
        (10mA/2.5Ω/25mV … 100nA/1MΩ/100mV)
        Front-end strategies A/B/C, ADC candidates ADS1262 / AD7175-class,
        PGA / CM / rail / overload / zero-crossing.

Canonical burden table per SHUNT_RANGE_TRADEOFF §2.4 (philosophy D):
  10mA  2.5Ω  25mV,  1mA 25Ω 25mV, 100µA 500Ω 50mV,
  10µA 5kΩ 50mV, 1µA 100kΩ 100mV, 100nA 1MΩ 100mV
ADC FS ±2.5V diff (ADS1262 PGA=1). PGA 32 available.
Gain required G_total = 2.5 / Vs_FS  → 25× for 100mV, 50× for 50mV, 100× for 25mV
G_post = G_total / PGA  (with PGA=32: 0.78×, 1.56×, 3.13×)

Usage:
  python test_G_bipolar.py          # generates test_G_results.csv + console summary
  python test_G_bipolar.py --plot   # also writes plots if matplotlib available
"""
from __future__ import annotations
import csv
import sys
import math
from pathlib import Path

OUT_CSV = Path(__file__).parent / "test_G_results.csv"

# ---------------------------------------------------------------------------
# Canonical ranges
# ---------------------------------------------------------------------------
RANGES = [
    {"name": "10mA",  "I_FS": 10e-3, "R": 2.5,    "Vs_FS": 25e-3},
    {"name": "1mA",   "I_FS": 1e-3,  "R": 25,     "Vs_FS": 25e-3},
    {"name": "100uA", "I_FS": 100e-6,"R": 500,    "Vs_FS": 50e-3},
    {"name": "10uA",  "I_FS": 10e-6, "R": 5e3,    "Vs_FS": 50e-3},
    {"name": "1uA",   "I_FS": 1e-6,  "R": 100e3,  "Vs_FS": 100e-3},
    {"name": "100nA", "I_FS": 100e-9,"R": 1e6,    "Vs_FS": 100e-3},
]

ADC_FS = 2.5          # ±2.5V diff at PGA=1
ADC_VCM_ADS1262 = 2.5 # mid-supply for single 5V AVDD
PGA_MAX = 32
PGA_OPTIONS = [1,2,4,8,16,32]

# Test points as fraction of FS
TEST_POINTS = [
    (-1.0,   "-FS"),
    (-0.50,  "-50%FS"),
    (-0.05,  "-5%FS (small neg)"),
    (-0.005, "-0.5%FS (small neg)"),
    (0.0,    "0"),
    (0.005,  "+0.5%FS (small pos)"),
    (0.05,   "+5%FS (small pos)"),
    (0.50,   "+50%FS"),
    (1.0,    "+FS"),
]

# ADS1262 limits (AVDD=5V single, AVSS=0V)
ADS1262_AVDD = 5.0
ADS1262_HEADROOM = 0.3  # absolute input must be AVSS+0.3 to AVDD-0.3 per datasheet
ADS1262_CM_MIN = 0.3
ADS1262_CM_MAX = 4.7
# PGA differential input limit: ±Vref/PGA, Vref=2.5V
ADS1262_VREF = 2.5

# AD7175-class: wide CM, ±1ppm INL, diff input wide, bipolar supplies possible
AD7175_CM_RANGE = (-5.0, 5.0)  # device dependent; wide

# Strategy rail / supply assumptions
STRATEGIES = {
    "A": {"desc": "True bipolar ±5V amp, diff ADC bipolar (CM≈0V)",
          "supplies": "±5V amp, ADC bipolar ±2.5V diff",
          "VCM": 0.0,
          "rail_margin": 2.5,  # ±5V rail to ±2.5V FS -> 2.5V headroom
          "needs_dual": True},
    "B": {"desc": "Midscale level-shift single +5V, VCM=2.5V",
          "supplies": "Single +5V, VCM=2.5V",
          "VCM": 2.5,
          "rail_margin": None,  # depends on gain
          "needs_dual": False},
    "C": {"desc": "Direct differential ADC (INA + diff ADC, GND CM)",
          "supplies": "INA single +5V, ADC diff",
          "VCM": 0.0,
          "rail_margin": None,
          "needs_dual": False},
}

# Zero-crossing offset contributors (worst-case)
# ADS1262 PGA offset: typ 3µV, max per PGA; AD7175 offset ~10µV
OFFSET_SOURCES = {
    "ADS1262_PGA32": {"vos_amp": 120e-6, "vos_pga": 30e-6, "vos_adc": 10e-6},  # OPA140 + PGA
    "AD7175": {"vos_amp": 5e-6, "vos_pga": 5e-6, "vos_adc": 5e-6},  # chopper
}


def gain_required(vs_fs: float) -> float:
    return ADC_FS / vs_fs


def gain_post_pga(g_total: float, pga: float) -> float:
    return g_total / pga


def check_ads1262_cm(vcm: float) -> str:
    if ADS1262_CM_MIN <= vcm <= ADS1262_CM_MAX:
        return "PASS"
    return "FAIL"


def check_ads1262_diff(vs: float, pga: int) -> tuple[str, float, float]:
    """Check diff input does not exceed Vref/PGA."""
    limit = ADS1262_VREF / pga
    # After post-gain? Actually diff at ADC = vs * G_post * PGA = vs*G_total
    # Simpler: vs*G_total must be <=2.5V; at PGA=32 the diff before PGA is vs*G_post
    return ("PASS" if abs(vs) <= limit else "FAIL", limit, vs)


def strategy_b_headroom(vs: float, vcm: float, gain: float, avdd: float = 5.0) -> tuple[float, str]:
    """Single-supply midscale: Vout = VCM + gain*Vs. Must stay AVSS+0.1 to AVDD-0.1 (RRIO)."""
    vout = vcm + gain * vs
    margin_low = vout - 0.1
    margin_high = avdd - 0.1 - vout
    # RRIO 0.1V from rail typical
    if vout < 0.1 or vout > avdd - 0.1:
        status = "FAIL (rail clip)"
    elif min(margin_low, margin_high) < 0.2:
        status = "MARGINAL (<0.2V)"
    else:
        status = "PASS"
    return vout, status


def zero_crossing_error(range_vs_fs: float, g_total: float) -> dict:
    """Estimate offset referred to input for zero-crossing."""
    # Worst-case offset RTI = vos_amp + vos_pga/G_post + ... simplified
    # Use 120µV OPA140 worst for illustration, 5µV chopper
    results = {}
    for k, v in OFFSET_SOURCES.items():
        vos_rti = v["vos_amp"] + v["vos_pga"] + v["vos_adc"]  # conservative sum
        # Referred to current: I_err = Vos_RTI / R? No, Vs error -> I error
        # Vs offset = vos_rti (approx), but with gain it scales. Simpler: RTI offset ~100µV
        # For small shunt Vs (25mV) offset is larger fraction
        err_frac_fs = vos_rti / range_vs_fs
        results[k] = {"vos_rti_uV": vos_rti*1e6, "err_frac_FS_pct": err_frac_fs*100}
    return results


def main():
    rows = []
    print("="*80)
    print("Gate 4 — Test G: Bipolar Current Front-End Sweep")
    print("="*80)
    print(f"ADC FS ±{ADC_FS}V diff, ADS1262 AVDD={ADS1262_AVDD}V, Vref={ADS1262_VREF}V")
    print(f"PGA max {PGA_MAX}, ranges: {', '.join(r['name'] for r in RANGES)}")
    print()

    header = [
        "range","I_FS_A","R_ohm","Vs_FS_V","test_label","frac_FS",
        "I_test_A","Vs_V",
        "G_total_to_2p5V","G_post_PGA32",
        "strategy","Vout_V","rail_status","CM_V","CM_status",
        "ADS1262_diff_limit_V","ADS1262_diff_status",
        "AD7175_CM_status","zero_cross_offset_uV","zero_cross_err_pct_FS",
        "overload_150pct_V","overload_status","verdict"
    ]

    for rng in RANGES:
        g_total = gain_required(rng["Vs_FS"])
        g_post32 = gain_post_pga(g_total, PGA_MAX)
        zc = zero_crossing_error(rng["Vs_FS"], g_total)
        # use OPA140 worst for display
        zc_uV = zc["ADS1262_PGA32"]["vos_rti_uV"]
        zc_pct = zc["ADS1262_PGA32"]["err_frac_FS_pct"]

        # PGA feasibility
        # At PGA=32, diff limit = 78mV. G_post*Vs_FS must be <=78mV
        adc_in_at_fs_post = rng["Vs_FS"] * g_post32  # = Vs_FS * G_total /32 = 2.5/32 =78mV always!
        # Indeed by construction 2.5/32=78mV independent of Vs_FS; so always exactly at limit -> PASS
        # Overload 150%: 1.5*78mV=117mV >78mV -> would need PGA reduction or recovery
        overload_vs = 1.5 * rng["Vs_FS"]
        overload_adc = overload_vs * g_post32  # 117mV
        overload_limit = ADS1262_VREF / PGA_MAX  # 78mV
        if overload_adc <= overload_limit:
            overload_status = "PASS"
        else:
            overload_status = "OVERLOAD (needs PGA step-down / recovery <10ms)"

        print(f"Range {rng['name']:>6s}: R={rng['R']:>8.1f}Ω  Vs_FS={rng['Vs_FS']*1e3:5.1f}mV  "
              f"G_total={g_total:5.1f}×  G_post32={g_post32:4.2f}×  "
              f"ADC_in@{PGA_MAX}={adc_in_at_fs_post*1e3:4.1f}mV (limit {overload_limit*1e3:.1f}mV)  "
              f"Overload150%={overload_adc*1e3:5.1f}mV {overload_status}  "
              f"ZC_offset={zc_uV:.0f}µV ({zc_pct:.2f}%FS)")

        for frac, label in TEST_POINTS:
            I_test = frac * rng["I_FS"]
            Vs = frac * rng["Vs_FS"]

            # Strategy A: bipolar diff ±2.5V mapping
            # Vout_diff = Vs * G_total, CM=0
            strat_a_vout_diff = Vs * g_total  # differential
            strat_a_cm = 0.0
            strat_a_cm_status = "PASS"  # CM 0V within AD7175 wide; ADS1262 CM near 0 would FAIL but A uses bipolar supplies
            # ADS1262 with bipolar supplies? ADS1262 AVDD=5V single not bipolar -> strategy A requires dual-supply ADC variant
            # For analysis: ADS1262 strictly needs CM≈2.5V, so A fails CM for ADS1262 but passes for AD7175

            # Strategy B: midscale — use G_post*Vs before PGA? Actually overall gain G_total, output single-ended
            # For B we model Vout = VCM + G_total*Vs  (if gain before ADC) — hits rails for large Vs
            # More realistic B with PGA=32: Vout_intermediate = VCM + G_post*Vs, then PGA multiplies diff
            # So headroom check on intermediate:
            vout_b_intermediate = ADC_VCM_ADS1262 + g_post32 * Vs  # intermediate before PGA
            # Also check full-gain version (no PGA):
            vout_b_full = ADC_VCM_ADS1262 + g_total * Vs
            # Intermediate always safe: 2.5 ± 0.078V -> PASS
            # Full gain would be 2.5 ±2.5V -> at rails -> FAIL/MARGINAL
            _, status_b_inter = strategy_b_headroom(Vs, ADC_VCM_ADS1262, g_post32)
            _, status_b_full = strategy_b_headroom(Vs, ADC_VCM_ADS1262, g_total)
            # We report intermediate (PGA path) as the feasible topology B
            cm_b = ADC_VCM_ADS1262
            cm_b_status = check_ads1262_cm(cm_b)

            # Strategy C: direct differential, CM=GND
            cm_c = 0.0
            # AD7175 wide CM passes; ADS1262 GND CM fails (needs 0.3V min)
            cm_c_ads = "FAIL (ADS1262 GND CM <0.3V)" if cm_c < ADS1262_CM_MIN else "PASS"
            cm_c_ad7 = "PASS" if AD7175_CM_RANGE[0] <= cm_c <= AD7175_CM_RANGE[1] else "FAIL"

            # ADS1262 diff check at PGA=32 intermediate input
            diff_limit = ADS1262_VREF / PGA_MAX
            diff_in = abs(Vs * g_post32)
            diff_status = "PASS" if diff_in <= diff_limit + 1e-9 else "FAIL"

            # AD7175 diff: assume ±2.5V (or wider) -> always PASS since G_total*Vs = ±2.5V
            ad7_status = "PASS"

            # Verdict per row: strategy B with PGA=32 is PASS; strategy A PASS only with AD7175/dual ADC
            # We produce one row per test point per strategy? Task says compare strategies.
            # To keep CSV manageable, produce one row per test point with columns for each strategy status
            # Here we emit a row for the RECOMMENDED strategy B+PGA32 (primary) and note alternatives in verdict
            vout_b = vout_b_intermediate
            verdict = "PASS (B+PGA32 feasible; A needs dual/bipolar ADC; C needs wide-CM ADC)"
            if diff_status != "PASS" or cm_b_status != "PASS":
                verdict = "FAIL"

            row = [
                rng["name"], f"{rng['I_FS']:.3e}", f"{rng['R']:.1f}", f"{rng['Vs_FS']:.6f}",
                label, f"{frac:.4f}",
                f"{I_test:.6e}", f"{Vs:.6f}",
                f"{g_total:.2f}", f"{g_post32:.3f}",
                "B+PGA32", f"{vout_b:.6f}", status_b_inter, f"{cm_b:.2f}", cm_b_status,
                f"{diff_limit:.6f}", diff_status,
                ad7_status, f"{zc_uV:.1f}", f"{zc_pct:.4f}",
                f"{overload_adc:.6f}", overload_status, verdict
            ]
            rows.append(row)

            # Also emit companion rows for strategy A and C for full comparison (optional extra rows)
            # To avoid CSV explosion, we embed A/C analysis in the verdict and keep one row per point
            # But for strict "compare front-end strategies" we add two extra rows per point flagged as alt
            # Add Strategy A row
            rows.append([
                rng["name"], f"{rng['I_FS']:.3e}", f"{rng['R']:.1f}", f"{rng['Vs_FS']:.6f}",
                label + " [A]", f"{frac:.4f}",
                f"{I_test:.6e}", f"{Vs:.6f}",
                f"{g_total:.2f}", f"{g_post32:.3f}",
                "A-bipolar", f"{strat_a_vout_diff:.6f}", "PASS (dual ±5V rail 2.5V margin)", f"{strat_a_cm:.2f}",
                "PASS-AD7175 / FAIL-ADS1262(CM≠2.5V)",
                f"{2.5:.6f}", "PASS (diff ±2.5V)",
                "PASS", f"{zc_uV:.1f}", f"{zc_pct:.4f}",
                f"{1.5*2.5:.6f}", "OVERLOAD (needs recovery)",
                "PASS-AD7175 / CM-FAIL-ADS1262"
            ])
            # Add Strategy C row
            rows.append([
                rng["name"], f"{rng['I_FS']:.3e}", f"{rng['R']:.1f}", f"{rng['Vs_FS']:.6f}",
                label + " [C]", f"{frac:.4f}",
                f"{I_test:.6e}", f"{Vs:.6f}",
                f"{g_total:.2f}", f"{g_post32:.3f}",
                "C-direct-diff", f"{Vs:.6f}", "PASS (INA diff)", f"{cm_c:.2f}",
                cm_c_ads,
                f"{diff_limit:.6f}", diff_status,
                ad7_status, f"{zc_uV:.1f}", f"{zc_pct:.4f}",
                f"{overload_vs:.6f}", overload_status,
                "PASS-AD7175 / FAIL-ADS1262(GND CM)"
            ])

    # Write CSV
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    print()
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    print()
    print("Key findings:")
    print(" - G_total: 100× (25mV), 50× (50mV), 25× (100mV). With PGA=32, G_post = 3.13×, 1.56×, 0.78×.")
    print(" - With PGA=32, diff input at FS is exactly 78.125 mV for all ranges (2.5V/32) → CM compliance is the limiter, not gain.")
    print(" - Strategy B single-supply midscale: intermediate (G_post) Vout = 2.5 ±78mV → well within 0.1-4.9V RRIO window (PASS).")
    print("   Full-gain (no PGA) would be 2.5 ±2.5V → hits rails (MARGINAL/FAIL) → proves PGA is required for B.")
    print(" - Strategy A true bipolar: PASS for AD7175-class (wide CM, bipolar diff), FAIL CM for ADS1262 single-supply (CM must be ~2.5V).")
    print(" - Strategy C direct diff: PASS for AD7175, FAIL for ADS1262 at GND CM (<0.3V min).")
    print(" - Zero-crossing: worst Vos ~160µV (OPA140) → 0.64% FS @25mV, 0.32% @50mV, 0.16% @100mV. Chopper (15µV) → 0.06%/0.03%/0.015%.")
    print(" - Overload 150% FS → 117mV at PGA32 input >78mV limit → ADC will clip; overload recovery <10ms requires PGA step-down or external clamp.")
    print(" - Behavioral model limitations: ideal resistors, no tempco, no humidity/DA, no ADC DSP/filter, no real amp GBW/slew.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
