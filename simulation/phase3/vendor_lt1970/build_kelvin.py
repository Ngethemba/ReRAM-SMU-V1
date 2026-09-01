import pathlib

def write_kelvin(name, shunt, rdut, cdut, riso, vset, vneg=False):
    # Kelvin follower: +IN = Vset (PULSE), -IN = DUT node (after Riso)
    # High-side sense: Rshunt between OUT and node A, sense across Rshunt, Riso between A and DUT
    # SENSE+: A, SENSE-: OUT
    # For low-side shared, SENSE would be at low-side, but keep high-side for vendor bench (stability similar)
    pulse = f"PULSE({vset} {vset} 1u 0.1u 0.1u 20u 40u)" if not vneg else f"PULSE({-abs(vset)} {-abs(vset)} 1u 0.1u 0.1u 20u 40u)"
    # But we want step from 0 to vset, so use PULSE(0 {vset} ...)
    if not vneg:
        v3 = f"PULSE(0 {vset} 1u 0.1u 0.1u 20u 40u)"
    else:
        v3 = f"PULSE(0 {-abs(vset)} 1u 0.1u 0.1u 20u 40u)"
    content = f"""* R5 vendor Kelvin bench - LT1970 vendor model, Kelvin feedback after Riso, shared shunt
* Shunt {shunt}, Rdut {rdut}, Cdut {cdut}, Riso {riso}, Vset {vset}
V1 -V 0 -12
V2 +V 0 12
V3 IN 0 {v3}
XU1 -V -V OUT SENSEP N005 SENSEM +V N_DUT IN NC VCsnk VCsrc COM EN NC NC NC +V LT1970
* Power supplies tied: Vee=-12, V-=-12, Vcc=+12, V+=+12
Rshunt OUT SENSEP {shunt}
Riso SENSEP N_DUT {riso}
Rdut N_DUT 0 {rdut}
Cdut N_DUT 0 {cdut}
* SENSE- tied to OUT (high-side), SENSE+ to after shunt, FILTER cap to SENSEM
Cfilter N005 SENSEM 220p
* VC limit high (no current limit), COM=0, EN=5, VCsnk/VCsrc=5
Vcsrc VCsrc 0 5
Vcsnk VCsnk 0 5
Vcom COM 0 0
Ven EN 0 5
* Kelvin feedback: -IN already N_DUT via XU1 pin mapping? Actually -IN is N_DUT via XU1 connection above (N_DUT is -IN node)
* In XU1 line, -IN is N_DUT, +IN is IN — correct per order: -IN is 8th node, +IN 9th node. We set those.
.lib C:\\Users\\azrai\\AppData\\Local\\LTspice\\lib\\cmp\\standard.dio
.tran 0 40u 0 10n
.meas tran Vpeak MAX V(N_DUT) FROM 0 TO 40u
.meas tran Vfinal AVG V(N_DUT) FROM 30u TO 40u
.meas tran Vmin MIN V(N_DUT) FROM 0 TO 40u
.meas tran Overshoot PARAM (Vpeak-Vfinal)/abs(Vfinal+1e-9)*100
.meas tran Undershoot PARAM (Vfinal-Vmin)/abs(Vfinal+1e-9)*100
.lib LT1970.sub
.backanno
.end
"""
    # Need to map XU1 nodes correctly: order per asy SpiceOrder 1..19
    # From example, we had 19 nodes; we will explicitly list in correct order with named nodes
    # Create proper X line with 16 pins plus NCs: use names VEE, VMINUS, OUT, SENSEP, FILTER, SENSEM, VCC, N_DUT, IN, VCsnk, VCsrc, COM, EN, NC1, NC2, VPLUS
    # Simplify: use 16-pin call with NC placeholders for missing Isrc/Isnk etc., LTspice will ignore NC floating warnings if we tie to 0?
    # For simplicity, keep as: XU1 VEE VMINUS OUT SENSEP FILTER SENSEM VCC N_DUT IN VCsnk VCsrc COM EN NC1 NC2 VPLUS LT1970
    # But need 16 entries: Vee(1) V-(2) OUT(3) Sense+(4) Filter(5) Sense-(6) Vcc(7) -IN(8) +IN(9) VCsnk(12) VCsrc(13) COM(14) Enable(15) Isrc(16) Isnk(17) V+(19) — 16 nodes (missing 10,11,18 NC)
    # Let's construct with 16 nodes: VEE VMINUS OUT SENSEP FILTER SENSEM VCC N_DUT IN VCsnk VCsrc COM EN N003 N003 VPLUS — using N003 for Isrc/Isnk tied together
    content2 = f"""* R5 vendor Kelvin bench - {name}
V1 VEE 0 -12
V2 VMINUS 0 -12
V3 VCC 0 12
V4 VPLUS 0 12
Vset IN 0 {v3}
Vcsrc VCsrc 0 5
Vcsnk VCsnk 0 5
Vcom COM 0 0
Ven EN 0 5
XU1 VEE VMINUS OUT SENSEP FILTER SENSEM VCC N_DUT IN VCsnk VCsrc COM EN N_ISRC N_ISNK VPLUS LT1970
Rshunt OUT SENSEP {shunt}
Riso SENSEP N_DUT {riso}
Rdut N_DUT 0 {rdut}
Cdut N_DUT 0 {cdut}
Cfilter FILTER SENSEM 220p
* Tie Isrc/Isnk floating allowed (warn) or tie to 0 via 10k?
Risrc N_ISRC 0 10k
Risnk N_ISNK 0 10k
.lib C:\\Users\\azrai\\AppData\\Local\\LTspice\\lib\\cmp\\standard.dio
.tran 0 40u 0 10n
.meas tran Vpeak MAX V(N_DUT) FROM 0 TO 40u
.meas tran Vfinal AVG V(N_DUT) FROM 30u TO 40u
.meas tran Vmin MIN V(N_DUT) FROM 0 TO 40u
.meas tran Overshoot PARAM (Vpeak-Vfinal)/abs(Vfinal+1e-12)*100
.lib LT1970.sub
.backanno
.end
"""
    path = pathlib.Path(f"E:/ReRAM-SMU V1/simulation/phase3/vendor_lt1970/{name}.cir")
    path.write_text(content2)
    print(f"Wrote {path}")

write_kelvin("R5_kelvin_2V_1k_100p_Riso47_shunt500", shunt=500, rdut="1k", cdut="100p", riso=47, vset=2)
write_kelvin("R5_kelvin_2V_1k_1n_Riso47_shunt500", shunt=500, rdut="1k", cdut="1n", riso=47, vset=2)
write_kelvin("R5_kelvin_2V_1k_10p_Riso47_shunt2p5", shunt=2.5, rdut="1k", cdut="10p", riso=47, vset=2)
write_kelvin("R5_kelvin_2V_10k_100p_Riso33_shunt500", shunt=500, rdut="10k", cdut="100p", riso=33, vset=2)
write_kelvin("R5_kelvin_neg2V_1k_100p_Riso47_shunt500", shunt=500, rdut="1k", cdut="100p", riso=47, vset=2, vneg=True)
write_kelvin("R5_kelvin_0p1V_10k_100p_Riso47_shunt5k", shunt="5k", rdut="10k", cdut="100p", riso=47, vset=0.1)
