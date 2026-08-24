# Commercial SMU Benchmark — ReRAM-SMU V1 Context

**Project:** ReRAM-SMU V1 — Phase 1 / Subagent C  
**Date:** 2026-08-24  
**Status:** SCAFFOLD — provisional, from public datasheet snippets and web_search descriptions. Verify against primary datasheets before DECISIONS.md promotion.  
**Purpose:** Ground V1 targets against what commercial SMUs actually achieve — not marketing headlines, but the *conditions* under which they hold sub-nA specs (enclosure, guard, NPLC, warm-up).

---

## 1. How to Read Commercial Specs

Commercial SMU accuracy is always quoted as:

```
±(% reading + offset)  at 23 ±5 °C, NPLC=1, after warm-up, 4-wire, guard where noted
         plus deratings outside T, plus noise vs NPLC / bandwidth
```

The *offset* term dominates at low current. Example: ±(0.03% + 500 pA) on a 100 nA range → at 10 nA the offset alone is 5% error. Marketing "6½-digit" resolution does not mean 6½-digit *accuracy* at low current.

Key hidden conditions that enable low-current specs:

- **Guarded triaxial cabling + driven guard** (Keithley 6517B, 4200-SCS, Keysight B2900A).
- **Shielded, light-tight enclosure** — Keithley 4200-SCS AppNote: mandatory for <1 nA.
- **NPLC integration** (1–10 PLC) — trades speed for mains rejection and √N noise reduction.
- **Warm-up 30–60 min** before offset current meets spec.
- **Source capacitance / resistance limits** — noise gain rises if DUT source R is too low (Keithley specifies minimum source R per range).

Ignore these and the same instrument loses 10–100× its low-current performance.

---

## 2. Benchmark Table

Values are *representative* from public summaries / web_search extracts; confirm from the instrument's datasheet for any binding comparison.

| Instrument | Class | Current ranges | Lowest DC I range / resolution | Offset / noise floor (representative) | Burden voltage (I-measure) | Integration / NPLC | Guard / triax | Warm-up | Price tier | Relevance to V1 |
|------------|-------|---------------|-------------------------------|---------------------------------------|----------------------------|--------------------|---------------|---------|------------|-----------------|
| **Keithley 2450 SourceMeter** | Bench SMU (general) | 10 nA – 1 A (6 ranges) | 10 nA range, 1 pA resolution | ±(0.06% + 100 pA) on 10 nA; ~10 pA p-p noise @ NPLC=1 | ~ <100 mV shunt-style; feedback-assisted on low ranges | 0.01–10 NPLC | Guard terminal, triax option | 60 min | ~$6–8k | Baseline for 10 nA–10 mA; V1 100 nA floor is well above its floor |
| **Keithley 2461 (high-current SMU)** | Bench SMU (pulse/high-I) | 10 nA – 7 A (pulse) | 10 nA range | Similar low-I spec to 2450; optimized for 1–10 A pulse | Low burden on high-I (external sense) | 0.01–10 NPLC | Guard | 60 min | ~$8–12k | Shows 10 mA DC + pulse headroom — relevant to ReRAM forming compliance |
| **Keithley 6517B Electrometer** | Electrometer (high-R / low-I specialist) | 1 pA – 20 mA (with <20 fA option via preamp) | 20 fA sensitivity; 1 fA resolution with 6517B+humidity | <3 fA input bias; <20 µV burden on low ranges; noise ~1 fA p-p @ NPLC=10 | **<20 µV** feedback ammeter | 0.01–10 NPLC, electrometer integration | **Triaxial guard** (driven) — mandatory for fA | 60–120 min | ~$8–10k | The fA benchmark — demonstrates what V1 *cannot* do without electrometer techniques (Teflon standoffs, 10^14 Ω guard) |
| **Keithley 4200A-SCS (with 4200-PA preamp / RPM)** | Parametric analyzer (semiconductor) | fA – 1 A (with PA: 0.1 fA) | 0.1 fA resolution with 4200-PA remote preamp | Offset ~10 aA with PA (quoted); system leakage <1 fA in fixture | Feedback ammeter, <200 µV | 0.01–10 NPLC + averaging | **Remote preamp at DUT + triax + light-tight probe station** | 60 min | ~$80–150k (full) | CC-utility: not comparable on price; but its *fixture and guard discipline* is the lesson — sub-nA requires the full stack, not just an op-amp |
| **Keysight B2901B / B2912B Precision SMU** | Bench SMU | 100 pA – 3 A (B2901B) / 10 pA – 10 A (B2912B) | 100 pA range, 10 fA resolution (B2912B) | B2912B: ±(0.03% + 20 pA) on 100 nA; noise ~2 pA p-p @ NPLC=1 | ~20–100 mV on high-R, <1 mV feedback on low-R | 0.01–10 NPLC | Guard, 4-wire | 60 min | ~$7–12k | Strong V1 peer — similar 10 mA–100 nA sweet spot; shows 100 nA usable with proper PCB + firmware averaging |
| **Keysight B2985B / B2987B Electrometer** | Electrometer | 0.01 fA – 20 mA | 0.01 fA resolution | 0.01 fA noise floor; Ib <1 fA | <20 µV | Long integration (up to 100 NPLC) | Triax + interlock | 60–120 min | ~$10–15k | Like 6517B — fA V2 reference, not V1 target |
| **NI PXI-4139 / PXI-4022 + PXI-4071 DMM** | PXI SMU + amplifier + DMM | 100 nA – 1 A (with 4022) | 100 nA range, 0.5 pA sensitivity (with 4022) | 4022: <20 µV burden on 100 nA; system 0.5 pA | **<20 µV** (feedback) | DMM integration | Guard amplifier module | 30 min | ~$5–10k (chassis extra) | Direct feedback-ammeter example — our V2 TIA benchmark (NI AppNote kA03q000000x1AZCAY) |
| **Ossila Source Measure Unit (X200)** | Low-cost lab SMU | ~10 nA – 200 mA | ~10 nA range | ~±(0.5% + 1 nA) typical (unverified) | ~10–50 mV | Limited averaging | No triax (BNC) | ~30 min | ~$3–5k | Closest price to V1; shows what *unguarded* PCB SMU actually holds (~nA, not pA) — realistic V1 ceiling |

> **Disclaimer:** Rows above are synthesized from public summaries and web_search result descriptions (Keithley Low Level Handbook 7th Ed., Tek 200SCS AppNote, NI kA03q000000x1AZCAY, AD RAQ-133, TI SBOA597). Datasheets move; verify *page/section* before citing in DECISIONS.md. No row is a substitute for the primary datasheet.

---

## 3. What the Benchmark Tells V1

### 3.1 V1 floor of 100 nA is conservative and defensible

Every bench SMU above holds ±0.03–0.06% + tens of pA on the 100 nA range — so *measuring* 100 nA is easy for them. But they all do it with:

- Guarded triax + shielded fixture,
- NPLC=1–10 (20–200 ms per point),
- Specified warm-up.

An unguarded PCB SMU (Ossila-class) typically quotes ±0.5% + 1 nA on its lowest range — meaning 100 nA ±1.5 nA. V1 targeting *"several nA useful floor"* with a PCB + modest enclosure is **ambitious but not fantasy** — it sits between Ossila and Keysight B2901B, and requires at least the following to be credible:

- Guard ring on the 100 nA range,
- Chopper/zero-drift front-end,
- NPLC-style averaging in firmware,
- Shielded DUT cabling (coax at minimum, triax if budget allows).

### 3.2 Burden voltage: commercial instruments cheated (in a good way)

V1 baseline 100 mV FS looks high vs commercial feedback ammeters at <1 mV. But commercial SMUs use **feedback ammeters on low ranges and shunt on high ranges**, switching topology per range — a complexity V1 deliberately defers. With **Kelvin force/sense** compensating burden in firmware (REQ-MEAS-003), 100 mV is acceptable for V1; document the correction and its TC.

### 3.3 Speed vs noise: NPLC is the universal trade

| NPLC @ 50 Hz (20 ms) | Time per point | Relative noise (√N) | Mains rejection |
|----------------------|----------------|---------------------|-----------------|
| 0.01 (0.2 ms) | 0.2 ms | 10× baseline | None |
| 0.1 (2 ms) | 2 ms | 3.2× | Partial |
| 1 (20 ms) | 20 ms | 1× (reference) | Null at 50 Hz |
| 10 (200 ms) | 200 ms | 0.32× | Null at 50 Hz + harmonics |

V1 firmware should expose NPLC as a user setting (default 1) and state noise specs *per NPLC*, as commercial datasheets do.

### 3.4 What V1 explicitly does NOT match

| Capability | Commercial (electrometer/preamp) | V1 PCB SMU |
|------------|----------------------------------|------------|
| 10 nA / 1 nA / pA | Yes — with triax, Teflon, fA op-amp (ADA4530-1), humidity control | **No** — V2 track |
| Input bias <1 fA | ADA4530-1, LMC662 — with air-wiring | No — PCB leakage ~pA |
| 10^14 Ω effective insulation | Triaxial guard + ceramic | ~10^10–10^12 Ω PCB (clean + guard) |
| Sub-pA noise at 10 Hz | 0.01–0.1 fA/√Hz front-ends | ~0.4 pA Johnson alone on 1 MΩ at 10 Hz |

Claiming 10 nA on a first PCB without electrometer measures reproduces the classic *"datasheet says the op-amp has 1 fA bias, so the board has 1 fA"* fallacy. V1 must not conflate part spec with system performance (ENGINEERING_RULES.md §8).

---

## 4. Suggested V1 Spec Language (provisional, for REQUIREMENTS.md refinement)

Borrow commercial style — honest, condition-bound:

```text
Current measurement (provisional, T=23±5 °C, 60 min warm-up, NPLC=1, shielded coax):

Range 10 mA : ±(0.05% reading + 5 µA)   noise 0.2 nA rms (1 kHz BW)
Range  1 mA : ±(0.05% reading + 500 nA)  noise 40 pA rms (10 Hz)
Range 100 µA: ±(0.08% reading + 50 nA)  noise 13 pA rms (10 Hz)
Range  10 µA: ±(0.10% reading + 10 nA)  noise 4 pA rms (10 Hz), guard recommended
Range   1 µA: ±(0.15% reading + 2 nA)   noise 1.3 pA + 5 pA leak est. (10 Hz)
Range 100 nA: ±(0.30% reading + 1 nA)  noise 0.4 pA Johnson + ADC + leak (10 Hz, guard required)

Burden voltage: ~100 mV FS (shunt), Kelvin-corrected at DUT via force/sense.
Speed: NPLC 0.1–10 selectable; specs above at NPLC=1 (20 ms @ 50 Hz mains).
```

These numbers are **placeholders** pending measured verification — but they are in the right decade and follow commercial offset-dominated structure, which is the point of this benchmark.

---

## 5. References

- Keithley *Low Level Measurements Handbook* 7th Ed. — instrument definitions, deratings, offset/leakage, guard/shield discipline. Download: `https://download.tek.com/document/LowLevelHandbook_7Ed.pdf`.
- Tek/Keithley 200SCS AppNote — *Optimizing Low Current Measurements with the Model 4200-SCS* — remote preamp 0.1 fA, source R/C vs noise, shielding. PDF: `https://download.tek.com/document/200SCS%20Low%20Current%20Application%20Note.pdf`.
- NI Knowledge Article kA03q000000x1AZCAY — shunt vs feedback ammeter, burden <20 µV on 100 nA with PXI-4022. Page: `https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x1AZCAY`.
- Analog Devices RAQ-133 — *Common Sense for Current Sensing* — TIA burden→virtual ground, amplifier selection. Page: `https://www.analog.com/en/resources/analog-dialogue/raqs/raq-issue-133.html`.
- TI SBOA597 — resistive vs coulombmeter, 1 TΩ cost/noise, Ω·F leakage product. PDF: `https://www.ti.com/lit/an/sboa597/sboa597.pdf`.
- Manufacturer datasheets (primary before promotion): Keithley 2450/2461/6517B, Keithley 4200A-SCS, Keysight B2901B/B2912B/B2985B, NI PXI-4139/4022/4071 — consult `https://www.tek.com`, `https://www.keysight.com`, `https://www.ni.com` for current revisions.

---

*Scaffold — replace representative numbers with page-cited datasheet values and measured NPLC/noise curves before DECISIONS.md promotion. Keep price tier indicative only.*
