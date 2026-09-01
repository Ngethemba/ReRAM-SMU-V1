import math
VREF=2.5
ranges=[("10mA",10e-3,25e-3),("1mA",1e-3,25e-3),("100uA",100e-6,50e-3),("10uA",10e-6,50e-3),("1uA",1e-6,100e-3),("100nA",100e-9,100e-3)]
gains=[1,2,4,8,16,32]
for name,I,Vfs in ranges:
    R=Vfs/I
    ideal=VREF/Vfs
    # pick best PGA <= ideal else max 32 if ideal>32, but for 100mV ideal25 -> pick 16 not 32 (since 32 clips)
    # rule: PGA must satisfy Vfs <= VREF/PGA (=FSR)
    candidates=[g for g in gains if Vfs <= VREF/g]
    best = max(candidates) if candidates else 1
    FSR=VREF/best
    util=Vfs/FSR*100
    head=FSR/Vfs
    preg=FSR/Vfs  # to fill
    print(f"{name:6s} R={R:>9.1f} Vfs={Vfs*1e3:5.1f}mV idealGain={ideal:5.1f} -> PGA={best:2d} FSR={FSR*1e3:6.2f}mV util={util:4.1f}% head={head:.2f}x preGain={preg:.2f}x")
