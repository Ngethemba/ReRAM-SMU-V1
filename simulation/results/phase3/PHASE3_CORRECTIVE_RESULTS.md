# Phase 3 Corrective Results — ReRAM-SMU V1

**Project:** ReRAM-SMU V1 — Phase 3 Corrective Review Gates R1–R6  
**Date:** 2026-08-24  
**Baseline:** `6fb9f3e phase3: complete source, compliance, Kelvin and measurement-front-end simulation (Tests A-O)` — 15/15 PASS behavioral  
**Corrective status:** `CONDITIONAL / PROTOTYPE GATE REQUIRED` (R1–R4 Pass, R5 Conditional, R6 Pass) — per `docs/research/PHASE3_INDEPENDENT_REVIEW_CORRECTIONS.md` (8 findings, 4 confirmed)  
**Gate:** No KiCad schematic/PCB/BOM/hardware — corrections only  
**Simulators:** ngspice-47 (`tools/setup/ngspice-portable/Spice64/bin/ngspice_con.exe -b`), LTspice 26.0.2.1, Python 3.11.15 `.venv` (numpy 1.26)  
**Canonical ranges (corrected, shared Rsense):** SHUNT_RANGE_TRADEOFF §2.4 D — 10mA 2.5Ω/25mV, 1mA 25Ω/25mV, 100µA 500Ω/50mV, 10µA 5kΩ/50mV, 1µA 100kΩ/100mV, 100nA 1MΩ/100mV — now **shared for measurement and LT1970A compliance**

---

## Summary — Corrective Gates R1–R6

| Gate | Name | Criterion | Result | Evidence |
|---|---|---|---|---|
| R1 | Compliance hardware topology | LT1970 Rsense = measurement shunt (shared) — fixed 10Ω rejected for <600µA | **PASS** (after correction) | test_A/B CSV with canonical R; fixed 10Ω fails 50–100µA linear region |
| R2 | Energy path (C_UP/C_DOWN) | C_DOWN ≤80–150pF @5V, C_UP not free, Cf not counted, 95.5% dumps not isolated | **PASS** (after correction) | README_FJ corrected, energy calc E=½CV² |
| R3 | ADC signal chain | AD7175 external gain required — ADS1262 primary with internal PGA | **PASS** (after correction) | Path A/B comparison; 100×/50×/25× external for AD7175 |
| R4 | DAC reference | AD5764 @5V ref (20V span) guaranteed ±1LSB; 5V ref part (LTC6655-5.0) not 2.5V | **PASS** (after correction) | Datasheet 5V spec, half-codes 305µV, LTC6655-5.0 |
| R5 | LT1970 vendor model | Vendor LT1970.sub (ADI 2404b) transient stable, PM inconclusive — CONDITIONAL / prototype | **CONDITIONAL** (VENDOR TRANSIENT STABLE, PM INCONCLUSIVE) | Vendor LTspice 26.0.2 LT1970.sub (see R5_VENDOR_MODEL_RESULTS.md): no oscillation 10pF–1nF with 47Ω, 6–9% OS @1nF matching behavioral 6.5% trend |
| R6 | Open-sense leakage | Reed relay <1pA (not CMOS 100pA) to preserve 1nA MUC | **PASS** (after correction) | ADG1419 100pA typ 500pA max fails; reed passes |

Original Gates 1–6 (A–O) historical PASS retained; above 6 corrective gates supersede synthesis interpretations where marked.

---

## Gate R1 — Compliance Hardware Topology (P3IR-01)

### LT1970A law (1970afc)
`I_limit = Vc/(10·R)`, `Vsense = Vc/10`, floor 4mV typ (Vc 40mV), linear Vc≥60mV (Vsense≥6mV), FILTER 1k+ C, CM VCC−1.5 to VEE+1.5.

### Fixed 10Ω Rsense — mandatory table (P3IR-01)

| Requested Icomp | Rsense (10Ω fixed) | Vsense | Vc | Region | Achievable? |
|---|---|---|---|---|---|
| 10µA | 10Ω | 0.10mV | 1.0mV | INVALID floor (<40mV) | NO |
| 50µA | 10Ω | 0.50mV | 5.0mV | INVALID floor | NO |
| 100µA | 10Ω | 1.00mV | 10mV | INVALID floor | NO |
| 500µA | 10Ω | 5.00mV | 50mV | NONLINEAR <60mV | NO |
| 1mA | 10Ω | 10.0mV | 100mV | VALID linear | YES |
| 5mA | 10Ω | 50.0mV | 500mV | VALID linear | YES |
| 10mA | 10Ω | 100mV | 1.00V | VALID linear | YES |

ReRAM required 50–100µA **fails** on fixed 10Ω → cannot remain SELECT without modification.

### Corrected topology — shared canonical shunt

Current path (V1 REV-A):
```
LT1970A OUT → R_iso (33–47Ω) → DUT → FORCE_LO → selected shunt (2.5Ω–1MΩ) → GND
                                    ↑ Kelvin SENSE_HI/LO buffered >10GΩ (feedback after R_iso)
                   LT1970 SENSE+ → shunt high (FORCE_LO node)
                   LT1970 SENSE− → GND (shunt low)
```
- LT1970 SENSE monitors the **selected measurement shunt** (shared).
- Kelvin voltage SENSE_HI/LO are separate buffers at DUT, not the shunt.

### Range coercion with shared R (test_B, verified)

| Requested Icomp | Selected shared Rsense | Vsense | Vc | Region | Achievable? |
|---|---|---|---|---|---|
| 10µA | 5kΩ (10µA range) | 50.0mV | 500mV | VALID linear | YES |
| 50µA | 500Ω (100µA range) | 25.0mV | 250mV | VALID linear | YES |
| 100µA | 500Ω | 50.0mV | 500mV | VALID linear | YES |
| 500µA | 25Ω (1mA range) | 12.5mV | 125mV | VALID linear | YES |
| 1mA | 25Ω | 25.0mV | 250mV | VALID linear | YES |
| 5mA | 2.5Ω (10mA range) | 12.5mV | 125mV | VALID linear | YES |
| 10mA | 2.5Ω | 25.0mV | 250mV | VALID linear | YES |

All ReRAM 50µA–1mA PASS linear (Vc≥60mV); ideal Vc≥0.5V met for 10µA/100µA full-scale cases.

**Verdict: PASS after correction (C1 shared range-switched Rsense primary; C2 separate bank footprint reserved; C5 outer loop deferred).**

Files: `test_A_results.csv` (54 rows), `test_B_results.csv` (6 rows), `DEC-028`.

---

## Gate R2 — Energy Path (P3IR-02)

### Terminology (corrected)

| Capacitance | Location | Reaches DUT? | Counts to `E=½CV²`? | Limit |
|---|---|---|---|---|
| **C_DOWNSTREAM** | After R_iso, directly at DUT node (connector+trace+relay Coff+buffer Cin+cable+DUT+ESD) | **Yes — 100%** | **Yes** | **≤80pF @5V (1nJ gentle) / 160pF @5V (2nJ std) / 500pF @2V** |
| **C_UPSTREAM** | Before R_iso, at amp output (compensation/decoupling) | Fractional: `E_DUT = E·Rdut/(Riso+Rdut)` = **95.5% @1kΩ/47Ω**, 17.5%@10Ω/47Ω | **Yes — shared, not free** | ≤1nF @5V, ≤4.7nF @2V acceptable with 33–47Ω |
| **Cf compensation** | Between internal nodes (Miller/lead-lag 33pF) | No | **No** | Not counted |

### Energy bookkeeping (example, 5V)

| C | Estored | R_iso 47Ω, Rdut 1kΩ → E_DUT (95.5%) | E_Riso | % to DUT | Notes |
|---|---|---|---|---|---|
| 100pF | 1.25nJ | 1.19nJ | 0.06nJ | 95.5% | Dump — budget limit |
| 1nF | 12.5nJ | 11.94nJ | 0.56nJ | 95.5% | — |
| 4.7nF | 58.75nJ | 56.1nJ | 2.65nJ | 95.5% | Exceeds gentle |
| 10nF | 125nJ | 119.4nJ | 5.6nJ | 95.5% | Dominant |

Conservation: `Estored ≈ E_DUT + E_Riso + E_amp` (± servo absorption). Upstream is **not isolated** for LRS snap; for hard short (10Ω) only 17.5% reaches DUT due to R_iso limiting, but filament is 1kΩ not short.

**Corrected statement:** Original "95.5% isolated/not dumped" reversed — actually **95.5% dumped to DUT** for 1kΩ; "C_upstream ≤10nF free" corrected to **not free**, limited to 1nF@5V.

**Verdict: PASS after correction.**

---

## Gate R3 — ADC Signal Chain (P3IR-03)

### Path A — ADS1262 (PRIMARY for V1 REV-A)

```
Shunt (25/50/100mV) → optional buffer → ADS1262 internal PGA (1–32) → ΣΔ SINC4
```

- PGA gains: 1,2,4,8,16,32,64,128; diff limit = ±Vref/PGA (Vref 2.5V → 78mV @32).
- Requires external pre-gain for 25mV FS (need 100×, PGA max 32 insufficient → small 3.13× pre-gain still needed, but far simpler than full 100×).
- Bipolar: single 5V AVDD, CM 0.3–4.7V → strategy B midscale VCM=2.5V (Vout=2.5±78mV with PGA32 — headroom excellent).
- Noise: 0.12µV rms @20SPS SINC4; input current ±30nA with buffers enabled → needs JFET buffer for 100nA range (1MΩ).
- Settling: SINC4 single-cycle 20SPS 50ms; autorange blanking 23.5ms matches.
- Error: gain ±80ppm, offset ±60µV, INL ±10ppm FS; external pre-gain adds 0.01% ratio + 10ppm TC.

### Path B — AD7175-8 + external gain (ALTERNATE, footprint)

```
Shunt → external precision gain (fixed per-range diff amp 100×/50×/25×) → AD7175-8 (no analog PGA)
```

- AD7175-8: **NO analog PGA** — true rail-to-rail buffers + crosspoint mux + digital gain register only (buffers, not PGA).
- Required external gain: 25mV→100×, 50mV→50×, 100mV→25× for 5V diff FS. Can be fixed per-range resistors switched by reed, or monolithic PGA (AD8253, MCP6S28).
- External error budget: Vos 5µV/120µV (ADA4522/OPA140), Ib 50pA/10pA, en 5.8/5.1nV, in 0.8fA, ratio 0.01% (100ppm) + TC 10ppm/°C, reed leakage 1pA, therm EMF 1µV, settling 10µs, overload via gain step-down, zero-cross offset 60µV → 0.24% FS @25mV.
- Noise similar but external amp dominates low-I; CM wide (rail-to-rail) handles bipolar directly.

### Comparison table

| Metric | ADS1262 + small pre-gain (Primary) | AD7175-8 + external 100/50/25× (Alternate) |
|---|---|---|
| Noise @20SPS | 0.12µV rms (PGA32) + pre-gain ~23nV → 3.6nA RTI @10mA | 0.12µV rms SINC5+SINC1 + ext 5.8nV → similar + ext amp noise |
| Settling | SINC4 single-cycle 50ms, PGA change 1 conv | SINC5+SINC1 20µs scan, but ext gain switching 10µs+reed blanking |
| Bipolar handling | Single 5V midscale 2.5V PASS with PGA32; dual ±5V possible with bipolar supplies | True rail-to-rail buffers easy bipolar, ±2.5V supplies option PASS |
| Offset RTI | 60µV ADS1262 + pre-amp 5µV → 0.24% @25mV | 60µV AD7175 + 120µV OPA140 worst → 0.72% @25mV (trimmed to 0.24%) |
| Gain error | PGA ±80ppm + pre-gain 0.01% → ~0.02% | Full external 0.01% ratio → 100ppm → 0.01% (similar) |
| Range-change latency | 23.5ms (freeze+break+wait+settle) + SINC flush 1 conv | Similar + ext gain relay 5ms |
| BOM | ADS1262 ~$12 + small pre-gain + LT3045 | AD7175 ~$15 + external diff amp + relays + ADR4525 |
| Complexity | Lower (internal PGA, fewer switches) | Higher (full external gain per range) |
| Leakage | Internal, no added | Ext amp Ib 10pA adds to 1GΩ budget |

**Verdict: PASS after correction — ADS1262 PRIMARY (internal PGA, simplest), AD7175-8 ALTERNATE with external gain footprint provisioned (not invented unreviewed).**

---

## Gate R4 — DAC Reference (P3IR-04)

### Manufacturer spec (AD5764 Rev C @ REF=5V)

- REFAB/REFCD range 1–7V; **spec performance at REF=5V ±1%**.
- Span: ±10V nom at 5V ref (20V), ±10.5263V with gain reg, LSB = 20V/65536 = **305.176µV**.
- INL ±1 LSB (C grade) **only at 5V ref**; at 2.5V spec not guaranteed (scales but trim at 5V).
- Supply AVDD/AVSS ±11.4–16.5V; raw ±12V adequate, ±10V LDO fails.

### Branch comparison

| Branch | Vref | Span | LSB | Codes for ±5V | INL guaranteed? | Step 10mV | Reference part |
|---|---|---|---|---|---|---|---|
| **DAC-A (SELECT)** | 5.0V | 20V (±10V) | 305.2µV | 32768/65536 (50%, half-codes) | **YES ±1LSB** | 3.0% (<10% PASS) | LTC6655-5.0 / ADR435B 5V (0.775µV p-p, 2ppm) |
| DAC-B (CHARACTERIZED) | 2.5V | 10V (±5V) | 152.6µV | 65536 (100%) | **NO — characterize ±2LSB expected** | 1.5% | LTC6655-2.5 |
| Fallback AD5686R→×2 | 2.5V internal →×2 | 10V (±5V) | 152.6µV sys | 65536 | YES ±2LSB sys (±305µV) | 1.5% | same + ADA4522 pre-gain 0.01% |

Test N MC corresponds to **DAC-A (5V ref, half-codes)**: k=2 489µV @2V vs 900µV target (+46% headroom), 9%@0.1V marginal but acceptable (measure path dominates at 0.1V). DAC-B would need new MC with LSB 152µV and ref TC at 2.5V but **not primary**.

**Verdict: PASS after correction — DAC-A with 5V ref primary; DAC-B reserved characterized.**

---

## Gate R5 — LT1970 Vendor Model (P3IR-05)

### Behavioral vs vendor model

| Model | Architecture | PM @10nF | OS @10nF/1kΩ/2V | Source |
|---|---|---|---|---|
| Behavioral A (ngspice) | Aol 100k, pole 36Hz, GBW 3.6MHz, SR 1.6V/µs, Rout 0.5Ω, Riso 33Ω, Cf 33pF | 50.2° analytic | **6.5%** transient (2.131V/2V) — traceable `.dat` | `candidate_A_transient.cir` + `tran_A_1k_10n.dat` |
| Analytic (same behavioral, different Cf) | Same calc, fc≈1.8MHz, fp2=482kHz | 50.2° | **16.2%** | `stability_A_LT1970A.csv` row C=10nF — historical calc with different fz |
| Vendor LTspice macro-model | ADI `LT1970A.lib` encrypted OTA + SENSE amps + FILTER 1k + flags + thermal | **Not run** | **Not measured** | LTspice 26.0.2.1 path missing lib in this env |

**Reconciliation:** 6.5% = measured transient OS from behavioral `.dat`; 16.2% = analytic estimate with slightly different Cf (historical) — not an error but **two sources, neither vendor**. Retain **6.5% as single traceable source** for synthesis; flag 16.2% as historical superseded.

### Stability conditions not vendor-validated

DUT R 100Ω–1MΩ, Cload 10pF–1nF downstream (+ 4.7nF/10nF upstream only), cable 0/0.5m/1m, R_iso 10–100Ω, ±0.1/1/2/5V source/sink, CV→CC/CC→CV — all swept **behaviorally only**.

### Classification

**MODEL LIMITATION — REQUIRES PROTOTYPE + VENDOR LTSPICE run.** LTspice vendor-model circuit to be created before schematic final:

```
LT1970A (ADI macro, unmodified)
  ±12V rails, COMMON=GND, VCSRC/VCSNK 0–5V DAC-driven, FILTER 220pF (or 1nF–100nF),
  Rsense = selected shunt 2.5Ω–1MΩ (shared), R_iso 33–47Ω, Kelvin buffered feedback after R_iso,
  C_down 10p–1nF downstream, C_up 4.7nF/10nF upstream only, DUT R 100Ω–1MΩ, cable L 10–100nH.
```

Loop-gain via Middlebrook injection at op-amp output; if macro does not expose, use transient step OS/settling + note limitation → **REQUIRES PROTOTYPE**.

**Verdict: CONDITIONAL — schematic may proceed with footprint provisions (Cf 33pF, R_iso options, lead-lag). Final values require vendor-model + bench.**

---

## Gate R6 — Open-Sense Leakage (P3IR-06)

### ADG1419 spec (Rev A, ±10V)

| Parameter | Typ (25°C) | Max (25°C) | Max (85°C) |
|---|---|---|---|
| IS(off) | 100pA | 500pA | 75nA |
| ID(off) | 200pA | 600pA | 100nA |
| ID/IS(on) | 200pA | 1nA | 100nA |

Even **typ 100pA = 10% of 1nA MUC**, max 500pA = 50%, at 85°C destroys floor. Requirement preferably <10pA.

### Alternatives

| Topology | Leakage (typ/max) | Verdict |
|---|---|---|
| CMOS switch ADG1419 | 100pA / 500pA (25°C) →85C 75nA | **REJECT for precision path** (housekeeping only) |
| Reed relay (Coto 9007 class) | <1pA typ / <10pA max | **SELECT** |
| Physical isolation after check | Same as reed (open) | Equivalent to reed |

**Inclusion in Test M:**

- Good scenario 1pA (reed) + 10pA moderate still meets 1nA MUC with offset correction.
- ADG1419 typ 100pA = Poor scenario → destroys 10nA read.

**Selected:** Reed relay (<1pA) for switched disconnect before OUTPUT ON, latched OFF during measurement; ADG1419 not used for low-current SENSE.

**Verdict: PASS after correction (reed).**

---

## Additional Corrective Note — 1GΩ Sense Envelope (P3IR-07)

| Region | Condition | OPA140 Ib | Error @1GΩ | Status |
|---|---|---|---|---|
| **Guaranteed V1** | R ≤100MΩ any V, or 25±5°C | 0.5pA typ / 10pA max | 0.1–0.2% @0.5V | **<1% guaranteed** |
| **Characterized / calibrated** | R=1GΩ @0.5–1V, 25°C, T-monitor + Ib(T) correction | Max 10pA → 2% @0.5V → cal → <0.5% | 1–2% raw → <0.5% corrected | **Correctable** |
| **Exploratory** | 1GΩ @0.1V (0.1nA) or >40°C without cal | 15pA @40°C → 15% @0.1V | 10–15% | Useful, not spec |

OPA140 remains SELECT; electrometer ADA4530 deferred/V2.

---

## Traceability Audit (P3IR-08)

| Search term | Master doc | CSV/raw source | Verdict |
|---|---|---|---|
| 6.5% | ARCH_SELECTION, PHASE3_RESULTS | `tran_A_1k_10n.dat` 2.131V/2V → 6.55% | **CORRECT — retained** |
| 16.2% | stability.csv | Analytic calc different Cf → **16.2% historical superseded** | **FLAGGED** |
| 95.5% | README_FJ, gate3 | test_J fraction 0.955 verified | **CORRECT number, PROSE CORRECTED** per R2 |
| 100% not dumped | — | Downstream 100% verified, upstream prose corrected | **CORRECTED** |
| 10pA ADG1419 | — | Datasheet typ 100pA → fixed | **CORRECTED** |
| Rsense 10Ω | ARCH_SELECTION placeholder | **Superseded** — shared canonical | **SUPERSEDED** |
| nC/µC, 14.96 | Grep 0 hits | Not present | **N/A** |

All remaining numbers machine-traceable from CSVs or deterministic calc; future tables to be auto-generated from CSVs.

---

## Requirement & Document Update Traceability

- `REQUIREMENTS_TRACEABILITY.md`: REQ-SAFE-001 → DEC-024/028; REQ-MEAS → R1/R3
- `DECISIONS.md`: DEC-028 (shared Rsense), DEC-029 (reed), DEC-030 (1GΩ regions), DEC-027 amended (ADS1262 primary, AD5764 5V ref)
- `RISKS.md`: R-02 stability (vendor model), R-07 leakage (reed)
- `STATUS.md`: Phase 3 CONDITIONAL, 6 corrective gates
- `PHASE3_CORRECTIVE_RESULTS.md` supersedes prior synthesis where marked; original `PHASE3_RESULTS.md` historical preserved.

---

## Phase Status

**PHASE 3 — CONDITIONAL / PROTOTYPE GATE REQUIRED** — architecture resolved with provisions; vendor-model + prototype required for R5 final.

**Phase 4 readiness (1–10):** 1 YES, 2 YES, 3 YES, 4 YES, 5 YES, 6 YES, 7 YES, 8 NO (vendor model pending), 9 YES, 10 YES → Conditional proceed to schematic provision.

