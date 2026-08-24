# Isolation Strategy — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 2 / Agent E
**Date:** 2026-08-24
**Status:** `CONCEPTUAL — NO KICAD` — comparison of isolation classes with USB trade study and PCB hooks. No isolator part promoted.
**Requirements:** REQ-PWR-001/002/004, REQ-SAFE-007, REQ-DUT-001/002, REQ-SW-001, REQ-GEN-002; OPEN_QUESTIONS Q-09/Q-10/Q-14; RISKS R-10/R-11
**Companion:** `GROUNDING_AND_RETURN_PATHS.md` (T3 vs T4) · `POWER_TREE.md` · `GUARD_STRATEGY.md` · `docs/calculations/SOURCE_HEADROOM_THERMAL.md`

---

## 0. What “Isolation” Means Here and What It Does Not

**Means:** Galvanic separation that blocks **DC and low-frequency ground-loop current** between the USB host ground and the SMU measurement reference, or between mains-derived power and the analog front-end. Characterized by isolation capacitance `Ciso`, withstand voltage `Viso`, and common-mode transient immunity `CMTI`.

**Does not mean:** Safety isolation from 230 V mains — **V1 has no mains on the PCB** (REQ-PWR-001) and uses an external lab supply. Isolation here is **measurement integrity**, not shock protection. V1 will not claim reinforced/safety isolation ratings. If a future revision adds mains, a separate safety review is required.

**Rule:** Never claim an isolation voltage you have not verified by hi-pot and barrier-capacitance measurement. Published `Viso` is a component rating, not a system rating.

---

## 1. Why Isolation Is On the Table for a “Non-Isolated” Instrument

The dominant interference path on a bench SMU is rarely the op-amp — it is the **ground loop**:

```
Host PC GND ── USB cable shield/braid ── SMU digital GND ── SMU analog GND ── FORCE LO ── DUT ── bench supply COM ── mains earth ── host earth ── Host PC GND
```

Loop voltage: 10 mV (same outlet, good wiring) to 0.5–2 V (different outlets, noisy SMPS lab supply, building earth gradient).
Loop impedance: cable braid + plane ≈ 0.1–1 Ω → loop current 10 mA–2 A.
Even 10 mA through 10 mΩ of shared FORCE-LO wiring = 100 µV → on 100 nA range (1 MΩ shunt) = 100 pA error — **250× Johnson 0.41 pA** and comparable to V1's entire leakage budget (see `LOW_CURRENT_MEASUREMENT.md` §2.9).

Symptom that proves you need isolation: **noise floor shifts when touching the USB cable, moving the DUT cable, or switching host USB ports** — classic ground-loop microphonics.

Bench SMUs solve this two ways: (a) float the measurement LO (guard-isolated, `>10^9 Ω` to earth, e.g., Keithley 2400 “LO floating” 30 V max), or (b) isolate USB. V1 classifies both.

---

## 2. Isolation Classes — Required / Recommended / Optional / Future

| Class | Meaning (how this project uses it) | Where it applies in V1 | Consequence if deferred |
|---|---|---|---|
| **Required** | Must be implemented or V1 cannot be safely operated on a noisy bench without silent measurement error. Verified at bring-up. | None for power — REQ-PWR-001 already requires no mains on PCB. No isolation *component* is required for V1 to be built. But the **ground discipline** in `GROUNDING_AND_RETURN_PATHS.md` **is required** as the non-isolated cure for the loop. | — |
| **Recommended** | Strongly advised for V1 if schedule/BOM permits; defer only with measured proof that non-isolated performance meets `REQ-MEAS-002` noise MUC (≈1 nA quantitative) on a noisy-host test. | **External USB isolation** (off-board dongle) — recommended verification tool, not a PCB fixture. | You will spend bring-up time chasing hum that a $30 dongle removes instantly. No safety risk, but schedule risk. |
| **Optional (provision hooks)** | PCB/schematic reserves footprint/logic for future stuffing without re-spin. Costs near-zero (copper keepout + DNP pads) but saves a board turn. **V1 must provision these hooks.** | **On-board footprint** for USB digital isolator + isolated DC/DC module (DNP by default). Optional population in V1.1 if testing proves need. | If not provisioned, adding isolation requires a new PCB. |
| **Future** | Explicitly not V1; architecture must not preclude it but need not design for it now. | **Reinforced mains isolation** (on-board AC/DC), **LO floating with earth-rated barrier** (>30 V), **battery-powered floating head** | — |

**Classification applies per isolation boundary.** V1 has two boundaries:

1. **USB data+power boundary** (host ↔ MCU).
2. **Power boundary** (lab supply ±12 V ↔ analog rails).

They can be isolated independently. Table 3 selects per boundary.

---

## 3. USB Isolation — Three Implementations Compared

### 3.0 Functional Requirements for Any USB Isolation in V1

* Pass **USB FS (12 Mb/s)** with FC error <10⁻⁹ (no packet loss during 1 ms frames).
* Preserve **enumerated device class** (CDC or TMC) transparently — no driver change.
* Meet **USB-IF eye** after isolator (jitter <2 ns for FS).
* Survive **ESD ±8 kV contact** at connector shell (barrier ≥2.5 kV qualifies).
* Not degrade measurement noise: isolation switching noise must not couple into analog plane — separate analog power after barrier.

### 3.1 Option U1 — Direct Non-Isolated USB (Baseline)

```
Host ── USB cable ── ESD diodes ── MCU USB_DP/DM (FS) ── MCU GND (= analog/digital tie at ADC)
```

* **Barrier:** None (`Ciso` = cable + PCB plane ≈ nF, `Viso` = 0 V).
* **Ground loop:** Host GND and SMU measurement GND are **one node** through the tie. Any host earth—supply earth potential appears directly between DUT and SMU sense LO (see §1 loop). On the 100 nA range this is the dominant mains-hum path.
* **Power:** VBUS 5 V not used for analog (V1 is self-powered from lab supply); VBUS powers only USB transceiver + pull-up. No isolated supply needed — simplest load on 5 V.
* **Isolator noise:** None (no switching converter).
* **Verification:** Must pass `GND-V-03` (mains null test) on noisy host (PC + SMPS supply sharing one outlet strip). If `ΔIoffset < 5 pA` between isolated-hub and direct connection, baseline is adequate.
* **Pros:** Zero cost, zero BOM, zero switching ripple, lowest schedule risk. Entirely adequate **if** V1 ground discipline (T3) plus NPLC mains nulling handles hum — as many DIY SMUs demonstrate.
  50/60 Hz hum that remains after NPLC=1–10 is almost always this loop — re-evaluate isolation.
* **Cons:** Ground-loop interference is entirely dependent on bench wiring quality. A change of host PC, supply, or outlet can silently degrade 100 nA performance after shipment. Shield continuity depends on cable quality.
* **Classification:** **Baseline for V1 (required to be compared, recommended to measure against).** Ships as the default if isolation is not staffed.

### 3.2 Option U2 — External USB Isolator Dongle (Recommended Verification Tool)

```
Host ── USB cable ── [External isolator brick, e.g., ADuM3160/4160 or TI ISOUSB211 class in boxed product]
                    ── short USB cable ── SMU MCU
Barrier inside dongle: digital isolator + isolated DC/DC (5 V→5 V, 100–500 mA isolated)
Ciso ≈ 2–10 pF (per isolator datasheet) + DC/DC barrier 5–20 pF → total 10–30 pF
Viso ≈ 2.5–5 kVrms (reinforced-capable if specified), CMTI 25–100 kV/µs
```

* **Ground loop:** **Broken.** Host GND and SMU GND are separated by `Ciso`. At 50 Hz, `Zc = 1/(2πfCiso) ≈ 1/(2π·50·15 pF) ≈ 212 MΩ` → loop current `≈ Vloop / Zc` → with 1 V earth gradient, Ileak ≈ 4.7 nA common-mode — negligible vs 100 nA range, and it is common-mode (rejected by differential sense). During 12 MHz signalling, displacement current `I = Ciso·dV/dt` ≈ 15 pF·5 V/2 ns = 37 mA burst for 2 ns per edge — flows at isolator barrier, not through sense node, and is filtered by isolated DC/DC output caps.
* **Power:** Dongle's isolated DC/DC powers the MCU-side VBUS transceiver and often the MCU itself if VBUS-powered; for V1 self-powered, only D- and transceiver are loaded (<30 mA). External brick's switching noise stays **outside** the enclosure.
* **Isolator noise:** Brick switching 100–500 kHz ripple appears across barrier but is outside SMU — cable inductance + connector loss attenuates it heavily before reaching analog. Lowest impact of any isolated option.
* **Pros:** Zero PCB change; leaves V1 PCB maximally simple; can be A/B tested in minutes (“with dongle vs without”). Commercial dongles are ESD/surge tested products ($25–60). Breaks the loop definitively without design effort.
* **Cons:** Extra box and cable; dongle's isolated supply current limit (~100 mA USB-class) is not relevant to V1 (lab supply still powers analog). Some dongles support only USB FS, not HS — V1 uses FS so fine. Does not float measurement LO relative to isolated analog supply earth — that loop (supply earth → FORCE LO) remains if supply is earth-referenced; an earth-lift on the lab supply (or floating supply) is the complementary fix.
* **Classification:** **RECOMMENDED** — buy one and use it as test equipment during every bench noise characterization. Not required to ship with every unit, but **required to own** for V1 development. Document which dongle model is the reference (provenance: isolator IC datasheet, Ciso/Viso/CMTI page).

### 3.3 Option U3 — On-Board Isolated DC/DC + Digital Isolator (Provision Footprint, DNP by Default)

```
Host ── USB connector ── [Optional series 0 Ω at D+/D- and VBUS]
       ├─ Primary side: USB GND (= chassis/DGND), ESD diodes, VBUS 5 V → isolated DC/DC primary
       ├─ Isolation barrier: ADuM3160/3166 (USB FS isolator, integrated PHY) or ADuM4160/4166, or TI ISOUSB211
       └─ Secondary side: MCU side GND (= DGND but isolated from host), MCU USB_DP/DM via isolator, secondary supply from iso DC/DC
            Secondary GND ties to analog/digital tie at ADC via 0 Ω / split bead (now “isolated secondary common”)
Isolated DC/DC candidates (mount as footprint, not commitment):
  5 V→5 V 0.5–1 W isolated module (e.g., Murata NME0505SC, Traco TMR-0511, RECOM R05P05S) — Ciso 10–30 pF, fsw 100–300 kHz
  or Vin-wide (9–36 V) isolated if lab supply is the primary feeding digital as well
```

* **Ground loop at USB:** Same break as U2 — `Ciso` ~10–30 pF per isolator + DC/DC.
* **Power analog boundary implication:** This U3 as drawn isolates **only USB data**, not analog power. If analog rails are still derived from the same lab supply whose COM is earth-referenced, loop supply-earth → FORCE LO → host earth still exists through that supply earth. **Full isolation** would require a second barrier: analog supply derived from lab supply through an **isolated DC/DC (±12 V → ±12 V isolated, or +12 V → ±12 V flyback)** so analog GND floats vs both host and supply earth. That is the T4 in `GROUNDING_AND_RETURN_PATHS.md` — classified as **optional provision** (analog isolator footprint) alongside USB isolator footprint, but not required to stuff.
* **Ripple and PSRR impact:** Isolated DC/DC outputs have 10–50 mVpp ripple (100–300 kHz) + switching spikes (10–20 MHz). That ripple now feeds directly into the digital LDO and, if an analog isolated DC/DC is provisioned, into analog LDOs. Requirement from `POWER_TREE.md`: PSRR ≥80 dB at ripple frequency AND post-LDO LC π-filter — otherwise isolation **worsens** measurement noise despite breaking ground loop. Filtering cost: one LC + feedthrough per rail.
* **Layout cost:** Barrier needs **creepage ≥1.6 mm** for 250 Vrms basic (IEC 60950 class — not safety, but EMI/ESD hygiene) and a **barrier keepout** (no copper/route across gap except through isolator + DC/DC). Guard must stay entirely on the isolated-secondary side — no guard trace may cross barrier. That keepout is the PCB hook V1 must reserve.
* **Pros:** One-board solution (no dongle dependence), integrated ESD+barrier spec, can be made “LO floating” with measured isolation (`>100 MΩ` @ 50 Hz). Demonstrates T4-class cleanliness.
* **Cons:** Adds BOM ($20–50), switching ripple design burden, bring-up isolation verification gate, debugging difficulty (isolated JTAG/SWD needed or secondary-side UART probe), and power efficiency loss (70–85%) → heat.
* **Classification:** **OPTIONAL (footprint required, population optional).** PCB reserves a rectangular barrier zone (≥10 × 15 mm per module+isolator) with mounting keepout and two silkscreen options (bypass: 0 Ω strapping for non-isolated bypass; barrier: isolator + DC/DC DNP). A single DNP footprint makes U1 the default and U3 a field upgrade without re-spin.

### 3.4 Comparison — USB Isolation Options

| Criterion | U1 Direct | U2 External dongle | U3 On-board isolator + iso DC/DC |
|---|---|---|---|
| Ground-loop break | None | **Yes** (~212 MΩ @50 Hz) | **Yes** (same Ciso, if stuffed) |
| BOM on PCB | $0 | $0 | $15–50 + layout keepout |
| Schedule risk | **Best** | **Best** (off-the-shelf) | Medium (EMI filter tuning, creepage review) |
| Noise added to measurement | None added; ground-loop noise remains | None added to PCB (noise stays in dongle) | Switching ripple added — needs LC + PSRR design |
| Bench hum at 100 nA (noisy host) | Depends on wiring — may be 10–500 pA shift | **Proven low** (validated per unit) | **Proven low** (if filtered) |
| ESD robustness at USB shell | Relies on board ESD diodes + chassis tie | Dongle's tested 8 kV | Same as direct plus isolator's 2.5 kV barrier |
| Debuggability | Full SWD via MCU | Full SWD (MCU side is still reachable) | **Reduced** (isolated barrier blocks default SWD unless secondary connector provided) |
| Upgrade path | Dongle posteriori | Dongle posteriori | PCB must have reserved zone from day 1 |
| Recommendation | **Default** verified baseline | **Buy and use during every bench test** | **Reserve footprint (DNP)** — stuff only if bench tests prove U1 inadequate on 100 nA range |

---

## 4. Power-Supply Isolation Boundary — Separate Question From USB

Lab supply → SMU analog rails is a different loop from USB. Options:

| Option | What is isolated | When it matters | V1 class |
|---|---|---|---|
| **P1 Lab supply COM = earth-referenced** (most bench supplies: output COM bonded to earth via rear strap) | Nothing — SMU analog COM is earth | Default bench condition. Ground loop exists via mains earth (same as §1). Matters most when DUT fixture is also earth-referenced (e.g., probe station chuck). | **Default — measure and lift earth strap as experiment** |
| **P2 Lab supply COM floating** (remove earth strap → float ±12 V outputs vs earth) | Analog COM floats vs earth (still referenced to FORCE LO) — leakage capacitance supply-to-earth (~100 pF–1 nF) + supply Y-caps define float impedance | Breaks earth-loop through supply without any on-board isolator. **Try this first.** Many SMU benches run supplies floated with a 1 MΩ bleed to earth. | **Recommended bench discipline** — no PCB change, lab procedure |
| **P3 On-board isolated DC/DC for analog rails** (±12 V in → ±12 V_iso out → analog LDOs) | Full galvanic — analog GND floating vs supply earth *and* vs USB | When even floating the lab supply leaves switching noise coupled from supply SMPS through Y-caps (nF) → analog. Definitive but costly. | **Optional (footprint)** — same barrier zone as U3, shared or separate module. Future if 100 nA floor not met after P1/P2 + USB isolation |

**Rule:** Do not attempt P3 before trying P2 + U2 — floating the lab supply plus external USB dongle breaks both sides of the loop with zero PCB change and is the standard audit that commercial SMU manuals prescribe (“remove earth link, use isolated interface”).

---

## 5. Recommended V1 Plan — Hooks That Cost Zero Today and Save a Re-Spin

### 5.1 PCB Hooks To Reserve (DNP Footprints)

1. **USB barrier rectangle** on PCB edge near USB connector: two rows of unmasked copper + silkscreen line labelled `ISOLATION BARRIER — no trace across except U-ISO`. Inside: footprint for **ADuM3160/4160 or TI ISOUSB211** (QFN/SSOP) with bypass option: populate 0 Ω series resistors on D+/D- and tie primary-GND to secondary-GND via 0 Ω at the barrier position — so the same PCB builds as U1 (bypass) or U3 (isolator stuffed). Include test points on both sides of barrier.
2. **Isolated DC/DC site** adjacent to barrier: generic 7-pin SIM / DIP-6 footprint compatible with Murata NME / Traco TMR / RECOM Rxx series (5 V→5 V for USB Vbus; or 12 V→12 V for analog iso if sharing barrier). Input from VBUS (or from lab 12 V, jumper-selected) — secondary output to MCU 5 V rail (or analog LDO input). Include LC π on output (`10 µH + 2×10 µF` footprint, DNP if not needed).
3. **Analog iso site (optional, same zone or second zone):** 12 V→±12 V flyback/forward module footprint (e.g., Traco THL-5 or RECOM R2S) if analog floating is ever required. Can be left unstuffed in perpetuity; presence does not degrade non-isolated build because barrier keepout is air.
4. **LO-float tie option:** FORCE LO ↔ analog GND ↔ chassis earth: three pads — direct 0 Ω (default: LO = analog GND), alternative `1 MΩ || 4.7 nF` + `100 kΩ` bleed footprint, and `DNP` (float). Supports later “LO floating 30 V” fixture mode without rework. Label clearly.

> **Cost of hooks:** 2 cm² keepout + ~10 DNP pads + silkscreen. No effect on non-isolated build if left bypassed. Failing to reserve them forces a full re-spin when bench tests later reveal ground-loop dominance on the 100 nA range.

### 5.2 Bring-Up Isolation Decision Flow

```
Build V1 with U1 (direct) + analog T3 ground (partitioned plane + tie at ADC)
  └─ Characterize 100 nA noise floor per GND-V-03 (with vs without USB traffic, with supply earth strap IN vs OUT)
       ├─ Δ offset < 5 pA and mains spur < spec at NPLC=1
       │     → isolation not required for spec — ship as U1; keep external dongle as lab accessory
       ├─ Δ offset 5–50 pA but disappears with external dongle (U2) and/or supply earth-lift (P2)
       │     → document bench requirements (floating supply, dongle) — reserve U3 footprint for V1.1
       └─ Δ offset > 50 pA or analog supply SMPS ripple couples even after earth-lift
             → stuff on-board isolators (U3 + analog P3) — re-characterize ripple filter
```

### 5.3 Verification — How Isolation Claims Are Proven

| Test ID | Method | Pass criterion | Applies to |
|---|---|---|---|
| ISO-V-01 | **Barrier Ciso measurement** (LCR at 100 kHz, ±10 V bias) + hi-pot 500 VDC for 1 min (if claiming Viso) | `Ciso` within datasheet max; no breakdown/leakage >1 µA | U2/U3 analog isolator builds |
| ISO-V-02 | **CMTI immunity:** Apply 10 V/ns common-mode step (function generator into barrier via 50 Ω) while logging ADC offset at 100 nA range | Offset transient <1 LSB of 100 nA ADC code, recovers within 1 conversion | U3 only |
| ISO-V-03 | **48-hour drift with/without host:** Log 100 nA offset drift (NPLC=10, shielded enclosure) while cycling host USB (enumeration/suspend/bulk transfer) on a noisy PC | Drift difference <3× Johnson (1.2 pA rms @10 Hz) | All — decides U1 vs U2/U3 |
| ISO-V-04 | **Ripple impact:** With on-board isolated DC/DC stuffed, measure analog LDO output ripple at 100 kHz–2 MHz (20 MHz BW scope, 10× probe, 50 Ω termination) at full digital load | Ripple <10 µVpp in measurement BW (10 Hz–1 kHz after LDO+LC) | U3/P3 stuffed builds |
| ISO-V-05 | **Chassis leakage/ESD:** 8 kV contact ESD at USB shell and FORCE connector (ESD gun per IEC 61000-4-2), functional check + post-ESD leakage at 100 nA range | No latch-up, leakage within spec, no barrier breakdown | All |

---

## 6. How Isolation Interacts With the Other Domains

* **Grounding (`GROUNDING_AND_RETURN_PATHS.md`):** If isolated, the partitioned-plane tie becomes the isolation barrier. The “tie voltage” measurement (GND-V-01) is meaningless across isolation (no DC tie) — replaced by `Ciso·dV/dt` displacement current measurement.
* **Guard (`GUARD_STRATEGY.md`):** Guard buffer lives **on the measurement (secondary) side** and is never routed across the barrier. Guard cable shield (inner) is secondary-side; outer shield is chassis/earth.
* **Power tree (`POWER_TREE.md`):** Isolated DC/DC outputs feed LDOs on the secondary; LDO PSRR + LC filtering requirements tighten (see §3.3 ripple row). Analog references (ADR4525) are on secondary — primary has its own reference (often just VBUS) — do not share reference across barrier.
* **Connector:** If LO is floated, the connector's outer shell is chassis; inner guard is secondary. No guard or LO wire may reference primary GND.

---

## 7. Classification Summary Table (Task Deliverable)

| Isolation domain | Options evaluated | V1 classification | PCB hook required? | Verified by |
|---|---|---|---|---|
| **USB data (host ↔ MCU)** | Direct (U1), external dongle (U2), on-board ADuM/TI + iso DC/DC (U3) | **U1 baseline + U2 recommended accessory + U3 footprint (DNP)** | **Yes — barrier rectangle + bypass 0-Ω** | ISO-V-03 (48-h drift A/B), sheet-bring-up comparison |
| **USB power (VBUS → MCU rail)** | Direct VBUS vs isolated 5 V→5 V module | Same as USB data — co-provisioned with isolator | **Yes — shared site with USB isolator** | ISO-V-04 |
| **Analog power (lab ±12 V → analog ±rail)** | Direct (P1 earth-ref), floating supply (P2 earth-lift), on-board ±iso (P3) | **P1/P2 default; P3 optional footprint** | **Yes — second iso site (can share barrier)** | GND-V-03 + POWER_TREE ripple/PSRR |
| **Measurement LO isolation (FORCE LO vs earth)** | Hard-tied, 1 MΩ||4.7 nF, float (DNP) | **Hard-tied default**; footprint for RC + float option | **Yes — 3-pad tie at FORCE LO** | ISO-V-03 + leakage test (open-input 100 s) |
| **Mains isolation (230 V AC on PCB)** | — | **FUTURE / NOT V1** — REQ-PWR-001 prohibits | No | Schematic/PCB review gate |

---

## 8. References

* ADI ADuM3160/4160 and TI ISOUSB211 datasheets — USB FS isolator Ciso/Viso/CMTI specs, eye/jitter — cited as provenance for `Ciso≈2–10 pF` class; verify page/section before promotion.
* Murata NME, Traco TMR/THL, RECOM Rxx isolated DC/DC datasheets — barrier capacitance, fsw, ripple — same class reference.
* `GROUNDING_AND_RETURN_PATHS.md` §1/§2 (ground-loop magnitude) — loop voltage/current estimates reused here.
* Keithley Low Level Measurements Handbook §3 (LO floating, earth-lift discipline).
* IEC 60950/62368-1 creepage tables (informative for barrier keepout sizing; not safety-claimed for V1 low-voltage).
* `docs/research/LOW_CURRENT_MEASUREMENT.md` §2.9 (mains/tribo/EMI magnitudes bounding isolation need).

---

*Phase 2 hook gate: PCB fab must include barrier keepout and DNP footprints as non-optional artwork — their presence is verified at schematic review (ERC keepout) and at PCB review (visual barrier line). No isolator IC is approved until datasheet + ISO-V-0x verification passes.*
