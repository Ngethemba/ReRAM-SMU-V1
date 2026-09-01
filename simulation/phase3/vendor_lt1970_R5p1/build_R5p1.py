import pathlib

# LT1970 pin order with 19 nodes as deduced from example: VEE VMINUS OUT SENSEP FILTER SENSEM VCC NDIF IN NC10 NC11 VCSNK VCSRC COM EN N_ISRC N_ISNK NC18 VPLUS
# We'll use explicit names: VEE, VMINUS, OUT, SENSEP, FILTER, SENSEM, VCC, NDIF, IN, NC10, NC11, VCSNK, VCSRC, COM, EN, N_ISRC, N_ISNK, NC18, VPLUS

def write_bench(name, shunt, rdut, cdut, riso, vset, vc, rdut_val="1k"):
    # vc is current limit voltage (both VCSNK/VCSRC), shunt as above, vset is DAC drive (2V, -2V, 0.1V, etc.)
    # Topology: OUT -> R_iso -> FORCE_HI -> DUT -> FORCE_LO -> Rshunt -> GND
    # SENSEP = FORCE_LO, SENSEM = GND, FILTER cap to SENSEM, Kelvin diff: FORCE_HI vs FORCE_LO -> NDIF -> pole -> NDIF_F -> -IN
    # Use PULSE for Vset step: 0 to vset
    pulse = f"PULSE(0 {vset} 1u 0.1u 0.1u 20u 40u)" if vset>0 else f"PULSE(0 {vset} 1u 0.1u 0.1u 20u 40u)"
    # For compliance tests, Rdut small to force CC: use rdut as given (100 for 10mA case, etc.)
    # Cdut across DUT (between FORCE_HI and FORCE_LO)
    content = f"""* R5.1 vendor bench - CORRECTED TOPOLOGY (low-side shared shunt, differential Kelvin)
* {name} | shunt {shunt} Vc {vc} -> Ilim {vc/(10*float(shunt.replace('k','e3').replace('M','e6'))*1e6):.1f}uA equiv | DUT {rdut_val} C {cdut} Riso {riso} Vset {vset}
V1 VEE 0 -12
V2 VMINUS 0 -12
V3 VCC 0 12
V4 VPLUS 0 12
Vset IN 0 {pulse}
Vcsrc VCSRC 0 {vc}
Vcsnk VCSNK 0 {vc}
Vcom COM 0 0
Ven EN 0 5
XU1 VEE VMINUS OUT SENSEP FILTER SENSEM VCC NDIF_F IN NC10 NC11 VCSNK VCSRC COM EN N_ISRC N_ISNK NC18 VPLUS LT1970
* Power path
Riso OUT FORCE_HI {riso}
Rdut FORCE_HI FORCE_LO {rdut_val}
Cdut FORCE_HI FORCE_LO {cdut}
Rshunt FORCE_LO 0 {shunt}
Cshunt FORCE_LO 0 10p  ; parasitic
* Sense across shunt
* SENSEP already FORCE_LO via X mapping? Actually SENSEP net is FORCE_LO, SENSEM is 0 (GND) per X: SENSEP=FORCE_LO, SENSEM=0
* Filter cap
Cfilter FILTER SENSEM 220p
* Differential Kelvin: FORCE_HI vs FORCE_LO -> NDIF -> pole 1k/15p ~10MHz -> NDIF_F -> -IN
Ediff NDIF 0 FORCE_HI FORCE_LO 1
Rpole NDIF NDIF_F 1k
Cpole NDIF_F 0 15p
* Flags pullup
Risrc N_ISRC 0 10k
Risnk N_ISNK 0 10k
* NCs
Rnc10 NC10 0 1Meg
Rnc11 NC11 0 1Meg
Rnc18 NC18 0 1Meg
.lib C:\\Users\\azrai\\AppData\\Local\\LTspice\\lib\\cmp\\standard.dio
.tran 0 50u 0 10n
.meas tran Vpeak MAX V(FORCE_HI,FORCE_LO) FROM 0 TO 50u
.meas tran Vfinal AVG V(FORCE_HI,FORCE_LO) FROM 35u TO 50u
.meas tran Vmin MIN V(FORCE_HI,FORCE_LO) FROM 0 TO 50u
.meas tran Overshoot PARAM (Vpeak-Vfinal)/abs(Vfinal+1e-12)*100
.meas tran Undershoot PARAM (Vfinal-Vmin)/abs(Vfinal+1e-12)*100
.meas tran Iplateau AVG I(Rshunt) FROM 35u TO 50u
.meas tran Vshunt AVG V(FORCE_LO) FROM 35u TO 50u
.meas tran Ipeak MAX I(Rshunt) FROM 0 TO 50u
.meas tran Vdut_final AVG V(FORCE_HI,FORCE_LO) FROM 35u TO 50u
.lib LT1970.sub
.backanno
.end
"""
    # Note: V(FORCE_HI,FORCE_LO) is differential Vdut, I(Rshunt) is load current. SENSEP is FORCE_LO, SENSEM is 0, so Vsense = V(FORCE_LO)
    # For high-side sense confusion, we have SENSEP=FORCE_LO, but need to map X tokens correctly: token4 SENSEP = FORCE_LO, token6 SENSEM = 0
    # Our X line above maps SENSEP to FORCE_LO? Actually we wrote SENSEP as 4th token, but we set 4th token to SENSEP net which is? In X line we have "... OUT SENSEP FILTER SENSEM ..." where SENSEP is net name for pin4, SENSEM for pin6. We set SENSEP = FORCE_LO? Wait we wrote XU1 ... OUT SENSEP FILTER SENSEM ... where SENSEP is literal net name SENSEP, but we want SENSEP = FORCE_LO. So we need to replace SENSEP net with FORCE_LO in X line.
    # Correct X: ... OUT FORCE_LO FILTER 0 ...? Let's fix: SENSEP should be FORCE_LO, SENSEM should be 0
    # So change X line tokens 4 and 6 accordingly
    # Rebuild with correct nets
    content = content.replace("XU1 VEE VMINUS OUT SENSEP FILTER SENSEM", "XU1 VEE VMINUS OUT FORCE_LO FILTER 0")
    # Also need to keep FILTER net as FILTER
    path = pathlib.Path(f"E:/ReRAM-SMU V1/simulation/phase3/vendor_lt1970_R5p1/{name}.cir")
    path.write_text(content)
    print(f"Wrote {path} Ilim={vc/(10*float(str(shunt).replace('k','e3').replace('M','e6')))*1e6:.1f}uA")
    return path

# Compliance anchors: Icomp 50uA 500R Vc0.25, 100uA 500R 0.50, 1mA 25R 0.25, 10mA 2.5R 0.25 ; use Rdut to force CC
# For CV->CC, choose Rdut small: for 50uA @2V, Rdut=1k would draw 2mA >50uA, so CC; for 10mA @2V, Rdut=100 draws 20mA >10mA
write_bench("R5p1_50uA_src_2V", shunt="500", rdut="100p", cdut="100p", riso="47", vset=2, vc=0.25, rdut_val="1k")
write_bench("R5p1_100uA_src_2V", shunt="500", rdut="100p", cdut="100p", riso="47", vset=2, vc=0.5, rdut_val="1k")
write_bench("R5p1_1mA_src_2V", shunt="25", rdut="1n", cdut="100p", riso="47", vset=2, vc=0.25, rdut_val="100")
write_bench("R5p1_10mA_src_2V", shunt="2.5", rdut="1n", cdut="100p", riso="47", vset=2, vc=0.25, rdut_val="100")
write_bench("R5p1_10uA_src_2V", shunt="5k", rdut="10p", cdut="100p", riso="47", vset=2, vc=0.5, rdut_val="10k")
# Sink (negative)
write_bench("R5p1_50uA_sink_neg2V", shunt="500", rdut="100p", cdut="100p", riso="47", vset=-2, vc=0.25, rdut_val="1k")
write_bench("R5p1_10mA_sink_neg2V", shunt="2.5", rdut="1n", cdut="100p", riso="47", vset=-2, vc=0.25, rdut_val="100")
# Stability cases
write_bench("R5p1_stab_2V_1k_10p_Riso47", shunt="500", rdut="10p", cdut="10p", riso="47", vset=2, vc=5, rdut_val="1k")
write_bench("R5p1_stab_2V_1k_100p_Riso47", shunt="500", rdut="100p", cdut="100p", riso="47", vset=2, vc=5, rdut_val="1k")
write_bench("R5p1_stab_2V_1k_1n_Riso47", shunt="500", rdut="1n", cdut="1n", riso="47", vset=2, vc=5, rdut_val="1k")
write_bench("R5p1_stab_2V_1k_100p_Riso33", shunt="500", rdut="100p", cdut="100p", riso="33", vset=2, vc=5, rdut_val="1k")
write_bench("R5p1_stab_2V_100R_100p_Riso47", shunt="500", rdut="100p", cdut="100p", riso="47", vset=2, vc=5, rdut_val="100")
write_bench("R5p1_stab_2V_10k_100p_Riso33", shunt="5k", rdut="100p", cdut="100p", riso="33", vset=2, vc=5, rdut_val="10k")
write_bench("R5p1_stab_neg2V_1k_100p_Riso47", shunt="500", rdut="100p", cdut="100p", riso="47", vset=-2, vc=5, rdut_val="1k")
write_bench("R5p1_stab_0p1V_10k_100p_Riso47", shunt="5k", rdut="10p", cdut="100p", riso="47", vset=0.1, vc=5, rdut_val="10k")

print("Done")
