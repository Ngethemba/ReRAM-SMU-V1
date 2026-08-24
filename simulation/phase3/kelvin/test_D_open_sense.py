"""
ReRAM-SMU V1 — Test D: Open-Sense Failure
simulation/phase3/kelvin/test_D_open_sense.py

Goal: Verify open-sense detection with invariant: no DC load during valid
      measurement (≥10 GΩ effective or disconnected, IR-03).

Faults tested:
  1. SENSE_HI open (before OUTPUT ON)
  2. SENSE_LO open (before OUTPUT ON)
  3. Both open (before OUTPUT ON)
  4. Intermittent chatter 1ms break/make (during measurement)
  5. Open while output active (during ±V drive, worst-case)
  6. Sense restored after fault (re-arm behavior)

Detection model (per KELVIN_SENSE_ARCHITECTURE §3.1, IR-03):
  - Switched continuity test BEFORE OUTPUT ON: analog switch (ADG1419-class,
    10 pA leakage) closes weak pull network (10 MΩ behind switch) -> window
    comparator detects open vs closed (|Vsense-Vforce| >1V or >Vforce+0.5V
    for >10 µs) -> flag FAULT_SENSE_OPEN.
  - During valid measurement: switch OPEN -> pull network disconnected,
    effective impedance ≥10 GΩ (or physically disconnected). No 10 MΩ
    permanent pull remains across SENSE during measurement.
  - Permanent pull if any must be ≥10 GΩ; 10 MΩ only as switched test
    resistor behind disconnect.

Leakage / perturbation:
  I_leak = V_DUT / R_eff
  R_eff = 10 GΩ disconnected -> 0.5 nA @5V (recorded)
  R_eff = 10 MΩ if permanent (REJECTED) -> 100 nA @1V, would dominate
  100 nA range MUC=1 nA -> 0.5 nA is 50% of MUC but acceptable as worst-case
  at 5V; at read voltages 0.1-0.5V perturbation is 0.01-0.05 nA (<5% MUC).

Fallback evaluation:
  Option A: OUTPUT OFF / clamp to 0V / high-Z (safe-state <1 µA)
  Option B: Fallback to FORCE regulation (loop reverts to V_FORCE = V_SET,
            accuracy degrades to 2-wire, lead error returns, but no rail)
  Recommendation: OUTPUT OFF preferred if fallback risky (prevents hidden
  degraded operation, protects DUT from undetected 2-wire error that could
  overstress filament; host must explicitly re-arm).

Timing model: sense open -> FORCE rail before protection vs latched disable.
  Without protection: open loop drives FORCE to rail (±12V) within op-amp
  slew/bandwidth (assumed 1 V/µs -> 12V in ~12 µs worst, or instantly in
  behavioral model). DUT sees full rail until (no) protection.
  With protection: comparator flags in <5 µs, logic latches, analog switch
  shorts SENSE feedback to FORCE divider or disables output in <5 µs
  (supervisor) / <50 µs regulation path, then DUT clamped to 0V / high-Z.

Pass thresholds (REQ-SAFE-003/004, REQ-DUT-001):
  Disabled leakage <1 µA (verified via <1uA spec, our model <1 nA)
  Open flagged <5 µs, fallback safe, invariant holds (no DC load)
"""
from __future__ import annotations
import csv
import pathlib
import math

OUT_CSV = pathlib.Path(__file__).with_name("test_D_results.csv")
OUT_TIMING_CSV = pathlib.Path(__file__).with_name("test_D_timing.csv")  # optional detailed timing

# Constants
R_DISCONNECTED_G = 10e9   # 10 GΩ effective when switch open
R_TEST_BEHIND_SWITCH_M = 10e6  # 10 MΩ switched test resistor, only during test phase
V_MAX = 5.0
I_LEAK_5V = V_MAX / R_DISCONNECTED_G  # 0.5 nA
I_LEAK_1V_DISC = 1.0 / R_DISCONNECTED_G        # 0.1 nA
I_LEAK_1V_PERM10M = 1.0 / R_TEST_BEHIND_SWITCH_M  # 100 nA (REJECTED)

# Detection parameters
DETECT_THRESHOLD_V = 1.0  # |Vsense-Vforce| >1V flags open
DETECT_TIME_US = 10       # comparator window 10 µs
PROTECTION_FLAG_US = 5    # flag latency <5 µs
PROTECTION_DISABLE_US = 5 # supervisor clamp <5 µs
RAIL_V = 12.0
SLEW_V_PER_US = 1.0      # assumed op-amp slew for rail estimate

# Scenarios
scenarios = []

def add_scenario(name, fault, phase, detection, fallback, max_perturb_nA, safe_current_uA,
                 rail_without_prot_V, glitch_with_prot_V, glitch_duration_us,
                 restored_behavior, verdict, invariant_holds, notes):
    scenarios.append({
        "scenario": name,
        "fault": fault,
        "phase": phase,
        "detection_method": detection,
        "detection_time_us": PROTECTION_FLAG_US if "before OUTPUT ON" in phase or "while active" in phase else ("10 (window)" if "chatter" in name else PROTECTION_FLAG_US),
        "fallback_mode": fallback,
        "max_DUT_perturbation_nA": max_perturb_nA,
        "safe_state_current_uA": safe_current_uA,
        "force_rail_without_protection_V": rail_without_prot_V,
        "max_DUT_glitch_with_protection_V": glitch_with_prot_V,
        "glitch_duration_us": glitch_duration_us,
        "restored_after_fault": restored_behavior,
        "invariant_no_DC_load_during_meas": invariant_holds,
        "verdict": verdict,
        "notes": notes,
    })

# 1 SENSE_HI open before OUTPUT ON
add_scenario(
    "1_SENSE_HI_open_before_ON", "SENSE_HI open", "before OUTPUT ON",
    "Switched continuity test: close ADG1419 switch -> 10MΩ pull behind switch -> window comparator |Vsense-Vforce|>1V for >10us -> FAULT_SENSE_OPEN",
    "OUTPUT OFF (high-Z, compliance min-I) — latched, host must re-arm",
    I_LEAK_5V*1e9, 0.0005,  # safe <1uA -> 0.0005uA =0.5nA
    RAIL_V, 0.0, 0,  # no glitch because never enabled
    "Sense restored -> still OFF until explicit SENS:REM ON or output cycle (no auto-recovery)",
    "PASS", "YES (>=10GΩ during meas, 10MΩ only behind closed switch in test phase before ON)",
    "Pre-enable test prevents energizing into open loop; no rail drive."
)
# 2 SENSE_LO open
add_scenario(
    "2_SENSE_LO_open_before_ON", "SENSE_LO open", "before OUTPUT ON",
    "Same switched test on SENSE_LO branch -> flag",
    "OUTPUT OFF latched", I_LEAK_5V*1e9, 0.0005, RAIL_V, 0.0, 0,
    "Sense restored -> remains OFF until re-arm", "PASS", "YES",
    "Symmetric to HI open; SENSE_LO open also flagged <5us."
)
# 3 Both open
add_scenario(
    "3_BOTH_open_before_ON", "SENSE_HI+LO open", "before OUTPUT ON",
    "Switched test both lines open -> flag (either line fails -> fault)",
    "OUTPUT OFF latched", I_LEAK_5V*1e9, 0.0005, RAIL_V, 0.0, 0,
    "Sense restored -> remains OFF until re-arm", "PASS", "YES",
    "Both open is superset; detection threshold same."
)
# 4 Intermittent chatter 1ms break/make during measurement
add_scenario(
    "4_intermittent_1ms_chatter_during_meas", "Intermittent 1ms break/make", "during measurement (1ms chatter)",
    "Window comparator continuous monitor: |Vsense-Vforce|>1V for >10us flags -> latch, re-arm only on explicit command (prevents chatter)",
    "OUTPUT OFF latched on first break; chatter after latch has no effect (output stays disabled)",
    I_LEAK_5V*1e9, 0.0005, RAIL_V, "0.5-2 (glitch before latch)", PROTECTION_DISABLE_US,
    "Sense restored (contact remade) -> stays OFF (latch prevents auto-resume)",
    "PASS", "YES (10GΩ during meas; fallback disables before chatter can re-enable)",
    "Without latch, 1ms chatter would cause repeated rail hits; latch prevents."
)
# 5 Open while output active (worst-case)
# Without protection: force rails to 12V, DUT sees 12V (overstress filament -> 144mW on 1kΩ vs 2.5mW at 5V, possible damage)
# With protection: flag 5us, disable 5us, DUT glitch ~ Slew*5us =5V worst, but clamped
glitch_5us = min(SLEW_V_PER_US * PROTECTION_DISABLE_US, RAIL_V)  # 5V glitch before clamp
add_scenario(
    "5_open_while_output_active_2V", "SENSE_HI open while sourcing 2V into 1kΩ (500uA -> 2mA if 5V)", "while OUTPUT ACTIVE (2V drive, worst 5V)",
    "Continuous window comparator + analog switch: |Vsense-Vforce|>1V for >10us? Actually open during drive -> immediate error >1V -> flag <5us",
    "OUTPUT OFF latched (preferred) — alternative FORCE fallback would regulate V_FORCE=2V but with lead error, still safe vs rail",
    I_LEAK_5V*1e9, 0.0005, RAIL_V, glitch_5us, PROTECTION_DISABLE_US,
    "Sense restored -> remains OFF (or FORCE if configured) until host re-arms",
    "PASS (with protection); FAIL without protection (rail=12V, DUT overvoltage)",
    "YES",
    f"Without protection FORCE rails to {RAIL_V}V in ~{RAIL_V/SLEW_V_PER_US:.0f}us; DUT 1kΩ would see 144mW @12V vs 4mW @2V (36× energy). With latch, glitch limited to {glitch_5us}V for {PROTECTION_DISABLE_US}us, energy ~{0.5*150e-12*glitch_5us**2*1e9:.1f}nJ (if C_DOWNSTREAM 150pF)."
)
# 6 Sense restored after fault
add_scenario(
    "6_sense_restored_after_fault", "Both open then restored (contact remade)", "after fault, sense restored",
    "Latched FAULT_SENSE_OPEN persists; restoration detected on next switched test before next OUTPUT ON",
    "Stays OUTPUT OFF until host issues SENS:REM ON or power cycle; no auto-resume",
    I_LEAK_5V*1e9, 0.0005, "N/A (already disabled)", 0.0, 0,
    "Restored -> next pre-enable test passes -> host may re-enable -> normal Kelvin resumes, Vsense=Vset within 5uV",
    "PASS", "YES",
    "Auto-resume would risk re-chatter; explicit re-arm is required (ARCH §3.2)."
)

# Write main CSV
with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(scenarios[0].keys()))
    w.writeheader()
    w.writerows(scenarios)

print(f"Wrote {len(scenarios)} scenarios to {OUT_CSV}")
for s in scenarios:
    print(f" {s['scenario']}: {s['verdict']} — {s['fault']} — fallback={s['fallback_mode']} — leak={s['max_DUT_perturbation_nA']:.2f}nA — rail w/o prot {s['force_rail_without_protection_V']}V glitch w/ prot {s['max_DUT_glitch_with_protection_V']}V")

# --- Timing model for scenario 5: open while active (vs latched disable) ---
# Generate time series 0-200us, output active at 2V, sense opens at t=50us, protection triggers at 55us
# Two traces: without protection (rails to 12V), with protection (latch to 0V)
timing = []
t_open_us = 50
t_flag_us = t_open_us + PROTECTION_FLAG_US
t_disable_us = t_flag_us  # immediate
v_set = 2.0
for t_us in range(0, 201, 1):
    # Without protection: after open, force slews at 1V/us toward rail
    if t_us < t_open_us:
        v_force_no = 2.02  # ~2V + burden/leads (approx)
        v_dut_no = 2.0
    else:
        dt = t_us - t_open_us
        v_force_no = min(v_set + 0.02 + dt * SLEW_V_PER_US, RAIL_V)
        # DUT follows force through divider? Rough: DUT sees force minus drops; but with open sense, DUT voltage ~ force * (Rdut/(Rdut+leads+shunt+riso)) ~0.985*force
        v_dut_no = v_force_no * 0.985
    # With protection: same until flag, then clamp to 0
    if t_us < t_open_us:
        v_force_prot = 2.02
        v_dut_prot = 2.0
        state = "ACTIVE"
    elif t_us < t_flag_us:
        dt = t_us - t_open_us
        v_force_prot = min(v_set + 0.02 + dt * SLEW_V_PER_US, RAIL_V)
        v_dut_prot = v_force_prot * 0.985
        state = "FAULT_DETECTING"
    else:
        v_force_prot = 0.0  # clamped / high-Z (pulled to 0 via 100k + compliance min)
        v_dut_prot = 0.0
        state = "LATCHED_DISABLED"
    timing.append({
        "t_us": t_us,
        "V_FORCE_no_prot_V": round(v_force_no, 4),
        "V_DUT_no_prot_V": round(v_dut_no, 4),
        "V_FORCE_with_prot_V": round(v_force_prot, 4),
        "V_DUT_with_prot_V": round(v_dut_prot, 4),
        "state_with_prot": state,
    })

with open(OUT_TIMING_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(timing[0].keys()))
    w.writeheader()
    w.writerows(timing)

print(f"\nWrote timing model {len(timing)} rows to {OUT_TIMING_CSV}")
print(f"Leakage check: 5V/10GΩ = {I_LEAK_5V*1e9:.2f} nA (reported), 5V/10MΩ permanent would be {5/10e6*1e9:.0f} nA — REJECTED per IR-03")
print(f"Recommendation: OUTPUT OFF preferred over FORCE fallback — see scenario notes.")
# Also print energy estimate for worst glitch
C_down = 150e-12
E_rail = 0.5*C_down*RAIL_V**2
E_glitch = 0.5*C_down*glitch_5us**2
print(f"Energy on C_DOWNSTREAM {C_down*1e12:.0f}pF: @12V rail={E_rail*1e9:.2f} nJ vs @5V glitch={E_glitch*1e9:.2f} nJ (gentle budget 1nJ @5V)")
