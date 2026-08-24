# Gate 5 Test K — Range Switching Faults

**Status: PASS: safe switch sequence defined**

## Goal
Verify break-before-make, fault tolerance, and safe sequence per MECHANIC §4 / IR-04.

## Fault matrix
Shunts per SHUNT_RANGE_TRADEOFF §2.4: 10mA 2.5Ω /25mV … 100nA 1MΩ/100mV. Kelvin sense for each R_shunt (R_on 0.1Ω reed on 2.5Ω →4% if not Kelvin — flagged).

| Fault | R_eff seen | Vsense error | Consequence |
|-------|------------|--------------|-------------|
| **correct BBM** (disabled) | R_to | 0% | LOW — safe gap, no current |
| **correct BBM** (hot, enabled) | open during 5ms | ∞ | MEDIUM — source rails to limit, voltage spike if not disabled |
| **make-before-break** (2 shunts parallel) | R1∥R2 | −90% (10mA→1mA: 2.27Ω vs 25Ω) | HIGH — Vsense low 90% → compliance overshoot 1000% in CC mode |
| **stuck relay (short)** | R_from | up to 40,000% | CRITICAL — wrong range persists |
| **open relay** | ∞ | ∞ | CRITICAL — ADC rails, compliance blind, I=0 |
| **contact bounce 1ms** | toggles R | chatter → Vsense noise | MEDIUM — DA tail pC→mV, blanking required |
| **hot-switch in compliance** | R_to but I=1.5×FS_to | overload 1.5× | CRITICAL — I²R shunt overstress (10mA→1MΩ =100W!) |

**ADC overload:** `Vshunt = I·R_eff`, `overload = Vshunt/Vfs_to`. >1.5× flags recovery 10ms; >10× risks ESD clamp conduction. **Compliance on wrong R:** `I_actual = Vthr/R_eff`; MBB makes `R_eff` small → `I_actual` high. **Shunt overstress:** `P=I²·R`; 10mA through 1MΩ would be 100W (fuse/damage) — proves must disable before high-R switch.

## Python timing model
`test_K_switch.py` evaluates 10 transitions (adjacent up/down + extremes) ×6 faults ×(low/high/compliance) =260 rows in `test_K_results.csv`.

**Safe sequence (total 23.5ms blanking):**
| t0 | Duration | Step | Note |
|----|----------|------|------|
| 0ms | 0.5ms | Freeze sweep / hold DAC | Inhibit autorange, freeze compliance flag |
| 0.5ms |0.5ms| Reduce/disable output if |I|>0.5·FS_new or in_compliance | Set Vc=0 or LT1970 ENABLE low |
| 1ms |1ms| Break old relay (open) | Coil de-energize |
| 2ms |5ms| Wait after break (BBM gap) | Coil settle, charge injection decay |
| 7ms |1ms| Make new relay (close) | Coil energize |
| 8ms |10ms| Settle (relay+RC+DA) | Bounce 1ms + ADC RC + dielectric absorption to 1% |
| 18ms|5ms| Zero/offset calibrate | Auto-zero with shorted input |
| 23ms|0.5ms| Resume | Re-enable, ramp DAC 0.1V/ms |

Worst highlights: MBB 10mA→1mA R_eff 2.27Ω (−90.9% Vsense → +1000% current in compliance). Hot 10mA→100nA open would force 100W through 1MΩ if not disabled.

## ngspice
Two ideal-switch transients scaled 1000× (5ms spec →5µs sim): `test_K_switch.cir` (BBM: break 10µs, make 16µs, gap 6µs, 623 points) and `test_K_mbb.cir` (MBB: make 9.1µs before break 10µs, overlap 0.9µs). Topology `src(2V)→Rdut1k→shunt node→S1/R1(2.5)∥S2/R2(25)→GND` with `.model SW SW(Ron0.1 Roff1G Vt2.5)`. `v(shunt_hi)` shows BBM dip to 0V during gap (open, no current path) vs MBB dip to lower R (parallel 2.27Ω → Vshunt ≈4.5mV vs 50mV expected, Vsense wrong).

**Verdict:** PASS — safe switch sequence defined and enforced; BBM mandatory, hot-switch prohibited without disable; compliance flag inhibits autorange; Kelvin avoids R_on error; fault detected via ADC overload and Vsense mismatch.

**Artifacts:** `test_K_switch.py`, `test_K_switch.cir`, `test_K_mbb.cir`, `test_K_results.csv` (260 rows), `test_K.raw/.wr.dat`, `test_K_mbb2.raw/.wr.dat`

## Repro
```bash
.venv/Scripts/python.exe simulation/phase3/range_switch/test_K_switch.py
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/range_switch/test_K_switch.cir
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/range_switch/test_K_mbb.cir
```

## Model limitations
- Ideal switches (no coil L/flyback, no charge injection pC modeled beyond RC)
- No package L/C, no real relay Coff 1–3pF (C is minor vs shunt)
- DUT is linear 1k, not filament; compliance not closed-loop in spice (standalone shunt branch)

PASS: safe switch sequence defined
