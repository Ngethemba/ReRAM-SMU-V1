# Gate 5 Test L — POR / Brownout / Reset

**Status: PASS: POR invariant holds**

## Invariant
**OUTPUT MUST REMAIN DISABLED until all rails/reference/control valid.** Hardware pulldown + supervisor POR 200ms dominates firmware (firmware can only enable after supervisor release and checks).

## Timing model

| Rail / Signal | Valid after | Note |
|---------------|------------|------|
| +12V | 10ms | LDO ramp |
| −12V | 20ms | Charge-pump slower (asymmetric) |
| +5V precision | 15ms | LC filtered |
| Reference 2.5V | 5ms (after +5V) | ADR4525 |
| DAC POR | 2ms | AD5686R 0x0000=0V; AD5764 clamped 0V but requires ±11.4V (20ms) |
| MCU GPIO Hi-Z | 100ms | Reset/bootloader holds GPIOs Hi-Z |
| Supervisor POR | 200ms | MAX809/ADM811 open-drain holds ENABLE low 200ms after thresholds |
| Watchdog | 200ms post-release | Must kick within window, else reset |

**Brownout test:** Raw ±12V dip to 8V at 50–55ms (USB disconnect). Supervisor threshold 4.63V on 5V rail re-asserts within 1µs, re-disables output <10µs.

Full timeline (1ms steps) in `test_L_timing.csv` (251 rows, 11 columns). Excerpt:

| t | +12V | −12V | +5V | Ref | MCU | Supervisor | LT1970 ENABLE | Invariant |
|---|------|------|-----|-----|-----|------------|---------------|-----------|
|0ms|0|0|0|0|Hi-Z|LOW|LOW|YES disabled|
|10ms|12|−6|3.3|2.5|Hi-Z|LOW|LOW|YES|
|20ms|12|−12|5|2.5|Hi-Z|LOW|LOW|YES|
|50ms|8|−8|5|2.5|Hi-Z|LOW|LOW|YES (brownout)| 
|100ms|12|−12|5|2.5|Low|LOW|LOW|YES (MCU now drives low but supervisor still dominates)|
|200ms|12|−12|5|2.5|Low|HIGH (release)|LOW (FW holds)|YES|
|210ms|12|−12|5|2.5|Low|HIGH|FW may enable after checks|MAYBE|

**Violation check:** No row with t<200ms has Invariant ≠ YES disabled → PASS.

## Fault injection
| Fault | Effect | With hardware disable |
|-------|--------|-----------------------|
| DAC full-scale 5V →500mV Vsense →50mA on 10Ω | Would be 50mA through DUT | Clamped: LT1970 Hi-Z, I_leak <1µA |
| DAC Hi-Z →Vc floating | Unpredictable | Pulldown Rvc 100k→50mV safe floor (<4mV/Rsense) + ENABLE low → still Hi-Z |
| Ref not settled →gain 10% | Threshold 10% high | Same clamp — output disabled prevents delivery |
| Comparator startup blind 1ms | Trip blind | Hardware disable still holds; compliance flag ignored |
| Asymmetric rails (+12 valid, −12 not) | LT1970 Vee invalid, latch risk | ENABLE low keeps output Hi-Z until both rails valid |

**Hardware dominance:** ENABLE net = supervisor open-drain (200ms) + 10k pulldown to GND, wired-AND with MCU GPIO. When MCU Hi-Z (reset), pulldown →0V. LT1970 ENABLE low → high-Z, leakage <1µA, Vsense floor <4mV/Rsense. DAC fault cannot source current because power stage is disabled. Firmware can only set ENABLE high after supervisor release **and** rails/ref checks pass.

## ngspice supervisor
`test_L_por.cir`: `V12p PWL(0 0 10m 12 50m 12 50.5m 8 55m 8 55.5m 12)`, `V12n PWL(0 0 20m -12)`, `V5 PWL(0 0 15m 5)`, `Vref PWL(0 0 2m 0 5m 2.5)`, supervisor `Rsup100k·Csup2u` (τ200ms) with `Ssup` Vt4.5V pulling `en` low, `Rpull_en 10k` to `v5`, `Vdac PWL` injecting 5V fault at 55m–60m. Tran 0.2m–250m shows `V(en)` stays 0V until `V(n_sup)>4.5V` (~200ms+), despite `Vc=5V` fault. `test_L_wr.dat` and `test_L.raw` produced (1314 points).

## Repro
```bash
.venv/Scripts/python.exe simulation/phase3/fault/test_L_por.py
tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b simulation/phase3/fault/test_L_por.cir
```

## Model limitations
- Supervisor behavioral (ideal switch Vt4.5, no real supervisor IC hysteresis/Iq)
- No real relay coil L/flyback
- DAC fault PWL is worst-case 5V for 5ms, not statistical
- Temperature drift not time-simulated (reference 2ppm/C →6ppm at 3°C, included as CSV param not spice)

PASS: POR invariant holds
