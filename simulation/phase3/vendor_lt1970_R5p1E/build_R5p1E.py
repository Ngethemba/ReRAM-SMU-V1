import pathlib, textwrap, subprocess, json

base = pathlib.Path("E:/ReRAM-SMU V1/simulation/phase3/vendor_lt1970_R5p1E")
base.mkdir(parents=True, exist_ok=True)

opa_lib = "E:/ReRAM-SMU V1/simulation/phase3/opa140_model/OPAx140.LIB"
lt1970_sub = "LT1970.sub"  # will be found via LTspice lib search path, also use full path fallback

# Note: LTspice .lib resolution: if LT1970.sub not found via search, use absolute path C:/Users/azrai/AppData/Local/LTspice/lib/sub/LT1970.sub
lt1970_full = "C:/Users/azrai/AppData/Local/LTspice/lib/sub/LT1970.sub"

def write_gateE(name, vset, rdut, cdut, riso, shunt, vc):
    # vset: string like "2" or "-2" or "0.1"
    # rdut: string like "10k" or "100"
    # shunt: string like "500" or "2.5"
    # vc: string like "5" or "0.25"
    pulse = f"PULSE(0 {vset} 1u 0.1u 0.1u 30u 60u)"
    # For negative, pulse still 0 to negative
    content = f"""* R5.1E GATE-E vendor LT1970 + REAL OPA140 K1 Kelvin diff - {name}
* Vset {vset}V Rdut {rdut} Cdut {cdut} Riso {riso} shunt {shunt} Vc {vc}
V1 VEE 0 -12
V2 VMINUS 0 -12
V3 VCC 0 12
V4 VPLUS 0 12
Vset IN 0 {pulse}
Vcsrc VCSRC 0 {vc}
Vcsnk VCSNK 0 {vc}
Vcom COM 0 0
Ven EN 0 5
* Power path: OUT -> Riso -> FORCE_HI -> DUT//Cdut -> FORCE_LO -> Rshunt -> GND
Riso OUT FORCE_HI {riso}
Rdut FORCE_HI FORCE_LO {rdut}
Cdut FORCE_HI FORCE_LO {cdut}
Rshunt FORCE_LO 0 {shunt}
Cshunt FORCE_LO 0 10p
* LT1970 senses low-side shunt Kelvin: SENSE+ = FORCE_LO, SENSE- = GND (0)
* Filter open baseline
* Real Kelvin: SENSE_HI_BUF from FORCE_HI, SENSE_LO_BUF from FORCE_LO -> diff -> VDIFF -> LT1970 -IN
* Buffers: OPAx140 followers
XBUF_HI FORCE_HI FB_HI VCC VEE BUF_HI OPAx140
Rshort_HI FB_HI BUF_HI 0
XBUF_LO FORCE_LO FB_LO VCC VEE BUF_LO OPAx140
Rshort_LO FB_LO BUF_LO 0
* Diff amp: 10k 0.1% 4-resistor, gain 1, C across feedback 15p
R1 BUF_HI N_DIFF_N 10k
R2 N_DIFF_N VDIFF 10k
R3 BUF_LO N_DIFF_P 10k
R4 N_DIFF_P 0 10k
Ccomp N_DIFF_N VDIFF 15p
XDIFF N_DIFF_P N_DIFF_N VCC VEE VDIFF OPAx140
* LT1970 instantiation - 19 nodes: VEE VMINUS OUT SENSEP FILTER SENSEM VCC -IN +IN NC10 NC11 VCSNK VCSRC COM EN ISRC ISNK NC18 VPLUS
* We map SENSEP=FORCE_LO, SENSEM=0, FILTER=open, -IN=VDIFF, +IN=IN
XU1 VEE VMINUS OUT FORCE_LO FILTER 0 VCC VDIFF IN NC10 NC11 VCSNK VCSRC COM EN N_ISRC N_ISNK NC18 VPLUS LT1970
Risrc N_ISRC 0 10k
Risnk N_ISNK 0 10k
Rnc10 NC10 0 1Meg
Rnc11 NC11 0 1Meg
Rnc18 NC18 0 1Meg
.lib "{opa_lib}"
.lib "{lt1970_full}"
.tran 0 80u 0 10n
.options gmin=1e-12 abstol=1e-12 reltol=0.001
.meas tran Vpeak MAX V(FORCE_HI,FORCE_LO) FROM 0 TO 80u
.meas tran Vfinal AVG V(FORCE_HI,FORCE_LO) FROM 50u TO 80u
.meas tran Vmin MIN V(FORCE_HI,FORCE_LO) FROM 0 TO 80u
.meas tran Overshoot PARAM (Vpeak-Vfinal)/abs(Vfinal+1e-12)*100
.meas tran Iplateau AVG I(Rshunt) FROM 50u TO 80u
.meas tran Vshunt AVG V(FORCE_LO) FROM 50u TO 80u
.meas tran Ipeak MAX I(Rshunt) FROM 0 TO 80u
.meas tran Vdut_final AVG V(FORCE_HI,FORCE_LO) FROM 50u TO 80u
.meas tran Vbuf_HI AVG V(BUF_HI) FROM 50u TO 80u
.meas tran Vbuf_LO AVG V(BUF_LO) FROM 50u TO 80u
.meas tran Vdiff_avg AVG V(VDIFF) FROM 50u TO 80u
.backanno
.end
"""
    path = base / f"{name}.cir"
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")
    return path

# CV cases - no current limit (Vc=5 high)
write_gateE("R5p1E_0p1V_CV_10k_100p_R47", vset="0.1", rdut="10k", cdut="100p", riso="47", shunt="5k", vc="5")
write_gateE("R5p1E_0p1V_CV_10k_1n_R47", vset="0.1", rdut="10k", cdut="1n", riso="47", shunt="5k", vc="5")
write_gateE("R5p1E_2V_CV_10k_100p_R47", vset="2", rdut="10k", cdut="100p", riso="47", shunt="500", vc="5")
write_gateE("R5p1E_2V_CV_10k_1n_R47", vset="2", rdut="10k", cdut="1n", riso="47", shunt="500", vc="5")
write_gateE("R5p1E_neg2V_CV_10k_100p_R47", vset="-2", rdut="10k", cdut="100p", riso="47", shunt="500", vc="5")
write_gateE("R5p1E_neg2V_CV_10k_1n_R47", vset="-2", rdut="10k", cdut="1n", riso="47", shunt="500", vc="5")
# CC cases - force limit (Vc 0.25 with shunt 2.5 for 10mA, 0.25 with 500 for 50uA)
write_gateE("R5p1E_2V_CC_100R_100p_R47", vset="2", rdut="100", cdut="100p", riso="47", shunt="2.5", vc="0.25")
write_gateE("R5p1E_2V_CC_100R_1n_R47", vset="2", rdut="100", cdut="1n", riso="47", shunt="2.5", vc="0.25")
write_gateE("R5p1E_neg2V_CC_100R_100p_R47", vset="-2", rdut="100", cdut="100p", riso="47", shunt="2.5", vc="0.25")
write_gateE("R5p1E_2V_CC_1k_100p_R47_50uA", vset="2", rdut="1k", cdut="100p", riso="47", shunt="500", vc="0.25")
write_gateE("R5p1E_0p1V_CV_100R_100p_R47_CC10mA", vset="0.1", rdut="100", cdut="100p", riso="47", shunt="2.5", vc="0.25")
print("All R5.1E gate-E circuits written")
