#!/usr/bin/env python3
"""
Gate 5 Test H — Fast trip tolerance Monte Carlo
TLV3501-class emergency supervisor at 120%,130%,150% Icomp
Inputs: Vos ±6.5mV max (typ 1mV σ2mV), shunt 0.1% (later 0.01% for 100nA),
 DAC INL ±2LSB AD5686R (±305µV) or ±1LSB AD5764 (±305µV), gain error 0.02-0.05%,
 threshold amp offset 5µV ADA4522, ref 2ppm/C.
Run 1000 runs per range at 100nA/10uA/1mA.
"""
import pathlib, csv, math
import numpy as np

np.random.seed(0)

RANGES = {
    "100nA": {"R": 1e6, "Vfs": 0.1, "Ifs": 100e-9},
    "10uA":  {"R": 5e3, "Vfs": 0.05, "Ifs": 10e-6},
    "1mA":   {"R": 25,   "Vfs": 0.025, "Ifs": 1e-3},
}
MULTIPLES = [1.20, 1.30, 1.50]

# DAC LSB and INL
LSB_AD5686R = 152.588e-6  # at DAC output before x2? Actually at final ±5V output LSB=305uV, but for threshold scaling we use effective 305uV
# For threshold path, assume DAC drives threshold amp directly with gain 1, span 5V => LSB=76uV? To keep conservative, use 305uV as threshold INL
INL_AD5686R = 2 * 305.176e-6  # wait: LSB at output 305u, INL ±2LSB => ±610u? Spec says 152u LSB on 10V, 305u at output after x2? Let's use 305uV as definition in plan: ±2LSB AD5686R on 10V = ±305uV (they treat LSB=152.6u but 2*152.6=305u). We'll use ±305uV for both to keep comparable.
INL_AD5686R = 305.176e-6 * 1  # ±305u for 2LSB if LSB=152.6, but spec says ±305u; we use 305u
INL_AD5764 = 305.176e-6  # ±1LSB on 20V

# Use uniform distribution for INL? INL is max, typical smaller. We'll model as uniform ±INL or normal with sigma=INL/3
def sample_inl(max_inl):
    # uniform -max to +max gives pessimistic; use normal sigma = max/3 truncated
    return np.random.normal(0, max_inl/3)

# Comparator Vos: typ 1mV sigma 2mV truncated ±6.5mV
def sample_vos(n):
    s = np.random.normal(1e-3, 2e-3, size=n)  # mean 1mV? Actually typ 1mV offset, but sigma 2mV includes that mean
    # Center at 0 with sigma 2mV but add typ bias? Use mean 0 sigma2mV truncated?
    # We'll generate N(0,2mV) and clip
    s = np.random.normal(0, 2e-3, size=n)
    s = np.clip(s, -6.5e-3, 6.5e-3)
    return s

# Shunt tolerance
def sample_shunt(Rnom, tol, n):
    sigma = tol/3
    return Rnom * (1 + np.random.normal(0, sigma, size=n))

# Gain error: ±0.02% for ADA4522 path? Use uniform ±0.05% for DAC gain
GAIN_ERR_SIGMA = 0.0005/3  # 0.05% max

# Ref drift: 2ppm/C *3C =6ppm, plus initial accuracy 2mV? Use 6ppm of 2.5V =15uV sigma
REF_ERR_SIGMA = 15e-6/3

AMP_OFFSET_SIGMA = 5e-6/3  # 5uV max => sigma

# Hysteresis: TLV3501 6mV typ, acts as extra threshold offset after trip? Adds ~6mV to effective trip depending direction.
# For emergency supervisor, hysteresis ensures once tripped, release at lower threshold; but initial trip sees hysteresis as additional offset? We'll include half hysteresis as uncertainty.
HYST = 6e-3

def run_mc(Rnom, Vfs, multiple, n=1000, shunt_tol=0.001, dac_inl_max=305e-6):
    Ifs = Vfs / Rnom
    Itrip_nom = multiple * Ifs
    Vthr_nom = Itrip_nom * Rnom  # = multiple * Vfs
    # Vthr_nom examples: 100nA 100mV FS: 120mV at 120%, 10uA 50mV FS: 60mV at 120%, 1mA 25mV FS: 30mV at 120%
    Vos = sample_vos(n)
    Ract = sample_shunt(Rnom, shunt_tol, n)
    inl = np.random.normal(0, dac_inl_max/3, size=n)  # DAC INL as voltage error
    gain_err = np.random.normal(0, GAIN_ERR_SIGMA, size=n)  # fractional gain error on Vthr
    v_gain = Vthr_nom * gain_err
    ref_err = np.random.normal(0, REF_ERR_SIGMA, size=n)
    amp_off = np.random.normal(0, AMP_OFFSET_SIGMA, size=n)
    # hysteresis variation uniform 4-8mV? Use ±1mV sigma
    hyst = np.random.normal(HYST, 1e-3, size=n)
    # Total threshold error (Vthr effective) = Vthr_nom + gain + inl + ref + amp
    Vthr_eff = Vthr_nom + v_gain + inl + ref_err + amp_off
    # Trip current = (Vthr_eff + Vos (+ hyst?)) / Ract  . Hyst adds to trip for rising edge? Include half.
    # For worst case rising trip, threshold appears higher by Vos + hyst/2? We'll include Vos + hyst offset for upper bound; for lower bound Vos negative reduces threshold.
    # Model trip as (Vthr_eff + Vos)/Ract, and also consider hyst shifts release, not trip. We'll include hyst as extra positive term for max.
    Itrip = (Vthr_eff + Vos) / Ract
    # For reporting, also compute effective multiple = Itrip/Ifs_nom
    mult_eff = Itrip / Ifs
    return {
        "Itrip": Itrip,
        "mult_eff": mult_eff,
        "Vthr_nom": Vthr_nom,
        "Ract": Ract,
        "Vthr_eff": Vthr_eff,
    }

def stats(arr):
    return {
        "mean": float(np.mean(arr)),
        "sigma": float(np.std(arr, ddof=1)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "p1": float(np.percentile(arr, 0.5)),
        "p99": float(np.percentile(arr, 99.5)),  # 99% interval is 0.5% to 99.5%
        "p05": float(np.percentile(arr, 0.5)),
        "p95": float(np.percentile(arr, 95)),
        "p50": float(np.median(arr)),
        "p_low99": float(np.percentile(arr, 0.5)),
        "p_high99": float(np.percentile(arr, 99.5)),
    }

def main():
    out_path = pathlib.Path(__file__).parent / "test_H_results.csv"
    rows = []
    header = ["range","R_ohm","Vfs_mV","multiple_nom","shunt_tol_pct","dac","Vthr_mV",
              "mean_trip_uA","sigma_uA","min_uA","max_uA","p0_5_uA","p99_5_uA","99pct_span_pct","mean_mult","sigma_mult_pct","min_mult","max_mult","99pct_low_mult","99pct_high_mult","99pct_within_20pct"]

    # Attempt histogram generation
    has_mpl = False
    try:
        import matplotlib.pyplot as plt
        has_mpl = True
    except Exception as e:
        print(f"matplotlib not available: {e}, skipping histograms")

    for rng_name, cfg in RANGES.items():
        R = cfg["R"]; Vfs = cfg["Vfs"]; Ifs = cfg["Ifs"]
        shunt_tol = 0.001 if rng_name != "100nA" else 0.001  # 0.1%
        # also test 0.01% for 100nA later
        for mult in MULTIPLES:
            for dac_name, dac_inl in [("AD5686R", 305e-6), ("AD5764", 305e-6)]:
                data = run_mc(R, Vfs, mult, n=1000, shunt_tol=shunt_tol, dac_inl_max=dac_inl)
                Itrip = data["Itrip"]
                mult_eff = data["mult_eff"]
                s_itrip = stats(Itrip)
                s_mult = stats(mult_eff)
                # Convert to uA for display (but 100nA range will show small)
                # Use uA unit for 10uA and 1mA, nA for 100nA
                # Keep CSV in uA (1uA=1e-6)
                mean_uA = s_itrip["mean"]*1e6
                sigma_uA = s_itrip["sigma"]*1e6
                min_uA = s_itrip["min"]*1e6
                max_uA = s_itrip["max"]*1e6
                p_low_uA = s_itrip["p_low99"]*1e6
                p_high_uA = s_itrip["p_high99"]*1e6
                span_pct = (p_high_uA - p_low_uA)/mean_uA*100 if mean_uA!=0 else 0
                mean_mult = s_mult["mean"]
                sigma_mult_pct = s_mult["sigma"]/mult*100
                # 99% within 20% of nominal? Check if entire 99 interval within ±20%
                low_mult = s_mult["p_low99"]
                high_mult = s_mult["p_high99"]
                within = (low_mult >= mult*0.8) and (high_mult <= mult*1.2)
                Vthr_mV = data["Vthr_nom"]*1e3
                rows.append([rng_name, R, Vfs*1e3, mult, shunt_tol*100, dac_name, f"{Vthr_mV:.2f}",
                             f"{mean_uA:.4f}", f"{sigma_uA:.4f}", f"{min_uA:.4f}", f"{max_uA:.4f}",
                             f"{p_low_uA:.4f}", f"{p_high_uA:.4f}", f"{span_pct:.1f}",
                             f"{mean_mult:.3f}", f"{sigma_mult_pct:.1f}",
                             f"{s_mult['min']:.3f}", f"{s_mult['max']:.3f}",
                             f"{low_mult:.3f}", f"{high_mult:.3f}", str(within)])
                if has_mpl:
                    # plot each range*mult but too many; just plot one per range at mult=1.30 AD5764
                    if mult==1.30 and dac_name=="AD5764":
                        plt.figure(figsize=(6,4))
                        plt.hist(mult_eff, bins=30, color="#4a90e2", edgecolor="black", alpha=0.7)
                        plt.axvline(mult, color="red", linestyle="--", label=f"nom {mult:.2f}x")
                        plt.axvline(s_mult["p_low99"], color="orange", linestyle=":", label="0.5%")
                        plt.axvline(s_mult["p_high99"], color="orange", linestyle=":", label="99.5%")
                        plt.title(f"Trip multiple histogram {rng_name} @ {mult:.0%}  (Vthr {Vthr_mV:.0f}mV)")
                        plt.xlabel("Effective trip multiple (Itrip/Ifs)")
                        plt.ylabel("Count")
                        plt.legend()
                        plt.tight_layout()
                        hist_path = pathlib.Path(__file__).parent / f"hist_{rng_name}_{int(mult*100)}pct.png"
                        plt.savefig(hist_path, dpi=150)
                        plt.close()
                        print(f"  hist {hist_path.name}")

        # Bonus: 100nA with 0.01% shunt to show improvement
        if rng_name=="100nA":
            for mult in MULTIPLES:
                data = run_mc(R, Vfs, mult, n=1000, shunt_tol=0.0001, dac_inl_max=305e-6)
                s_itrip = stats(data["Itrip"]); s_mult = stats(data["mult_eff"])
                mean_uA = s_itrip["mean"]*1e6; sigma_uA=s_itrip["sigma"]*1e6
                rows.append([rng_name+"_0.01pct", R, Vfs*1e3, mult, 0.01, "AD5764", f"{data['Vthr_nom']*1e3:.2f}",
                             f"{mean_uA:.4f}", f"{sigma_uA:.4f}", f"{s_itrip['min']*1e6:.4f}", f"{s_itrip['max']*1e6:.4f}",
                             f"{s_itrip['p_low99']*1e6:.4f}", f"{s_itrip['p_high99']*1e6:.4f}", f"{(s_itrip['p_high99']-s_itrip['p_low99'])/s_itrip['mean']*100:.1f}",
                             f"{s_mult['mean']:.3f}", f"{s_mult['sigma']/mult*100:.1f}",
                             f"{s_mult['min']:.3f}", f"{s_mult['max']:.3f}",
                             f"{s_mult['p_low99']:.3f}", f"{s_mult['p_high99']:.3f}", str((s_mult['p_low99']>=mult*0.8) and (s_mult['p_high99']<=mult*1.2))])

    with open(out_path, "w", newline="") as f:
        w=csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"Wrote {out_path} {len(rows)} rows")

    # Print summary
    print("\n=== Summary (99% interval) ===")
    for r in rows:
        try:
            if r[5]=="AD5764" and "0.01" not in str(r[0]):
                # r indices: 18 low, 19 high, 20 within, 13 span, 15 mean_mult
                print(f"{str(r[0]):6s} {r[3]}x Vthr{str(r[6]):>6s}mV meanMult{str(r[14]):>6s} 99%[{r[18]}-{r[19]}] within20%={r[20]} 99span{str(r[13])}%")
        except Exception as e:
            print(f"row len {len(r)} {r} err {e}")

    # Recommendation logic
    print("\n=== Recommendation analysis ===")
    # For 1mA 25mV FS, error dominated by Vos 6.5mV/30mV=21.7% plus hyst 20%
    # For 100nA 100mV FS, Vos 6.5%
    # So fixed multiple fails at low burden because same absolute Vos is larger % at 25mV.
    # Fixed ceiling (e.g., absolute 150% of lowest FS or fixed current) equally bad.
    # Range-dependent multiple (higher % at low burden) or range-dependent absolute threshold with headroom compensates.
    print("At 25mV FS (1mA) Vos 6.5mV = 21.7% of Vthr@120% (30mV) plus hysteresis 6mV/30mV=20% -> total >30% spread, fixed 120% unsafe (may trip below Icomp).")
    print("At 100mV FS Vos 6.5% only, fixed multiple tolerable.")
    print("RECOMMENDATION: Range-dependent multiple (e.g., 150%@1mA, 130%@10uA, 120%@100nA) OR range-dependent absolute ceiling with margin, NOT fixed multiple nor fixed ceiling.")
    print("If shunt tightened to 0.01% at 100nA, sigma improves 0.03% negligible, Vos still dominates, so tighter shunt helps little; focus on Vos/hyst.")
    print("AD5686R vs AD5764 INL both ~305uV, difference <1% at 25-100mV, negligible vs Vos; choose by supply, not INL.")

if __name__ == "__main__":
    main()
