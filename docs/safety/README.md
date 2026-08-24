# Safety

## V1 Safety Posture

- **No direct 230 V mains on the SMU PCB.** Development uses an external lab supply (nominal ±12 V analog rails).
- **Output defaults to DISABLED** on power-on, brown-out, firmware reset, and watchdog timeout. Verify with power-cycle tests.
- **Current-limited bench supplies** for bring-up; never assume a rail is safe.
- **Dummy loads and precision resistors are the first DUT** — never a real ReRAM sample on a new revision.
- Exposed conductors, incorrect Kelvin wiring, or mis-set compliance can damage the DUT, the SMU, and test equipment.
- Future higher-voltage or mains-connected revisions require a **separate safety review** before design.

Store hazard analysis, checklists, and bring-up safety procedures here.
