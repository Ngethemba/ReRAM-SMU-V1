import pathlib

def write_bench(name, shunt, rdut, cdut, riso=None):
    content = f"""* R5 vendor bench - shared high-side shunt approx, LT1970 vendor model
* Shunt {shunt} (shared), Rdut {rdut}, Cdut {cdut}, Riso {riso or 'none'}
V1 -V 0 -12
V2 +V 0 12
V3 IN 0 PULSE(0 2 1u 0.1u 0.1u 20u 40u)
XU1 -V -V N004 N004 N005 OUT +V N006 IN N001 N001 N001 N001 0 +V N003 N003 N003 +V LT1970
Rshunt OUT N004 {shunt}
"""
    if riso:
        content += f"Riso N004 N007 {riso}\n"
        content += f"Rdut N007 0 {rdut}\n"
        content += f"Cdut N007 0 {cdut}\n"
    else:
        content += f"Rdut N004 0 {rdut}\n"
        content += f"Cdut N004 0 {cdut}\n"
    content += """R2 +V N002 3K
R3 OUT N006 10K
R4 N006 0 10K
D1 N002 N003 QTLP690C
V4 N001 0 5
.model D D
.lib C:\\Users\\azrai\\AppData\\Local\\LTspice\\lib\\cmp\\standard.dio
.tran 0 40u 0 10n
.meas tran Vpeak MAX V(N007) FROM 0 TO 40u
.meas tran Vfinal AVG V(N007) FROM 30u TO 40u
.meas tran Overshoot PARAM (Vpeak-Vfinal)/Vfinal*100
.lib LT1970.sub
.backanno
.end
"""
    # Adjust meaus node if no Riso, measure N004
    if not riso:
        content = content.replace("V(N007)", "V(N004)")
    path = pathlib.Path(f"E:/ReRAM-SMU V1/simulation/phase3/vendor_lt1970/{name}.cir")
    path.write_text(content)
    print(f"Wrote {path}")
    return path

p1 = write_bench("R5_vendor_2V_1k_100p_Riso47_shunt500", shunt=500, rdut="1k", cdut="100p", riso=47)
p2 = write_bench("R5_vendor_2V_1k_1n_Riso47_shunt500", shunt=500, rdut="1k", cdut="1n", riso=47)
p3 = write_bench("R5_vendor_2V_1k_10p_shunt2p5", shunt=2.5, rdut="1k", cdut="10p", riso=None)
p4 = write_bench("R5_vendor_neg2V_1k_100p_Riso47_shunt500", shunt=500, rdut="1k", cdut="100p", riso=47)
