# ReRAM-SMU V1 — Risk Register

**Version:** 0.1.0 — Phase 0  
**Date:** 2026-08-24  
**Usage:** Review at every phase transition. Severity × Likelihood guides priority; verification method must be concrete.

**Severity:** H=High (safety / DUT damage / project-threatening), M=Medium (performance shortfall, rework), L=Low (minor inconvenience)  
**Likelihood:** H/M/L (before mitigation)

---

| # | Risk | Severity | Likelihood | Mitigation | Verification Method |
|---|------|----------|------------|------------|---------------------|
| R-01 | **Low-current PCB leakage** — flux residue, moisture, creepage, wrong soldermask, via leakage defeats nA floor | H | H | Guard traces, careful stack-up, no-clean flux + cleaning procedure, conformal coat evaluation, high-impedance layout rules | Leakage test with floating input; guard effectiveness measurement; IPC-class cleaning log |
| R-02 | **Analog instability** — output stage / compliance loop oscillates with capacitive DUT | H | M | Phase-margin simulation, compensation network, capacitive-load testing, step-response characterization | SPICE stability sim + measured step response into R + C loads |
| R-03 | **Insufficient compliance-loop performance** — too slow, overshoots and damages ReRAM | H | M | Independent hardware loop, fast comparator/amp, overshoot simulation, clamp design | Fault injection: short + low-R step; scope current overshoot |
| R-04 | **Inaccurate range switching** — relay charge injection, contact resistance/thermal EMF, timing glitches | M | H | Relay selection (low thermal EMF, low leakage), make-before-break vs break-before-make analysis, dwell/hysteresis in autorange, calibration per range | Per-range calibration + range-transition test; relay characterization |
| R-05 | **Thermal drift** — reference, shunt TC, amp offset drift, self-heating shifts accuracy | M | H | Low-TC shunts, low-drift reference (ADR4525-class), zero-drift amps, thermal layout, temp monitoring + compensation | Temp chamber / temp-step test; drift vs temp measurement |
| R-06 | **Reference drift** — voltage reference ages/drifts, corrupting both source and measure | M | M | Precision reference with documented drift, burn-in, periodic recalibration, ratiometric checks where possible | Long-term drift log vs calibrated DMM; reference comparison |
| R-07 | **Relay leakage** — relay off-leakage dominates 100 nA range | M | M | Low-leakage relay selection (e.g., reed, Coto), leakage budgeting, guard, alternative solid-state evaluation | Leakage measurement per relay/position; range floor verification |
| R-08 | **ADC noise** — ADS1262 (or alternative) noise limits nA floor | M | M | Noise budgeting, averaging/oversampling strategy, analog filtering, separate analog supply, layout | Noise-floor measurement vs datasheet; ENOB verification |
| R-09 | **DAC INL / DNL** — AD5686R (or alternative) INL creates source non-linearity in ±2 V region | M | M | INL budgeting, calibration LUT, post-correction, DAC selection review | Linearity sweep vs calibrated DMM; INL plot |
| R-10 | **Ground-loop problems** — USB ground + supply ground + DUT ground interact, inject hum/offset | M | H | Star-ground strategy, analog/digital partition, optional isolation, wiring discipline | Hum/offset measurement with different grounding; USB-connected vs isolated comparison |
| R-11 | **USB / digital interference** — MCU clocks, USB switching couple into analog front-end | M | H | Partition, filtering, shielding, careful return paths, spread-spectrum awareness, measurement during USB traffic | Noise spectrum with/without USB activity; near-field probe if available |
| R-12 | **DUT damage** — incorrect compliance, EOS, ESD, or wiring damages ReRAM sample | H | M | Safe default disabled, hardware compliance, DUT connection checklist, dummy-load first, current-limited bring-up | Pre-connection checklist + dummy-load gate; post-fault DUT inspection |
| R-13 | **Counterfeit precision components** — fake references/shunts/amps from unreliable sourcing | M | M | Authorized distributors only, lot traceability, visual/functional screening | Sourcing record in `bom/sourcing/`; incoming inspection |
| R-14 | **Incorrect AI-derived datasheet interpretation** — AI hallucinated spec propagated into design | H | M | Rule: primary datasheet overrides AI; independent verification; two-person review for critical specs | Datasheet citation audit; provenance check in review |
| R-15 | **Obsolete / NRND components** — candidate part goes EOL before V1 release | M | L | Prefer active-production parts, check lifecycle, second-source awareness | Lifecycle check at BOM promotion; PCN monitoring |
| R-16 | **Calibration uncertainty underestimated** — calibration stands on uncalibrated references | M | M | Traceable reference standards, documented uncertainty budget, periodic recal | Uncertainty budget review; comparison with external calibrated instrument |
| R-17 | **Dielectric absorption / soakage** — capacitor DA causes hysteresis in sweeps | M | L | C0G/NP0 where critical, avoid high-DA dielectrics in signal path, DA-aware design | Sweep hysteresis test; capacitor DA characterization |
| R-18 | **ESD / handling damage to high-Z nodes** — handling during assembly degrades low-current performance | M | M | ESD controls, minimal handling of high-Z nodes, cleaning, no-touch guidance in assembly docs | Leakage before/after handling; assembly ESD log |

---

## Risk Review Cadence

- Reviewed at every phase gate (see `ROADMAP.md`).
- New risks appended; closed risks marked `RETIRED` with date and evidence — never deleted.
- Top risks (H×H, H×M) drive `OPEN_QUESTIONS.md` priority.

**Current top risks (Phase 0):** R-01, R-12, R-14 — leakage, DUT damage, and AI spec hallucination. These shape Phase 1–2 priorities.

---

*This register is intentionally pessimistic. A risk not written down is a risk not managed.*
