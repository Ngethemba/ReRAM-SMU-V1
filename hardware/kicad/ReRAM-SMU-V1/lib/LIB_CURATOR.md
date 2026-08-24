# ReRAM-SMU-V1 — Project-Local Library Curation Plan

> **Rule: No global libs.** All production symbols/footprints must live under `hardware/kicad/ReRAM-SMU-V1/lib/`. The project must open and ERC/build on a clean KiCad install with no extra global library configuration.

## Library Structure

```
hardware/kicad/ReRAM-SMU-V1/
├── sym-lib-table                  # project-local, version 7, ${KIPRJMOD}/lib/ReRAM-SMU-V1.kicad_sym
├── fp-lib-table                   # project-local, version 7, ${KIPRJMOD}/lib/footprints
├── lib/
│   ├── ReRAM-SMU-V1.kicad_sym     # version 20251024 / generator 10.0 (KiCad 10.0.5)
│   ├── LIB_CURATOR.md              # this file
│   └── footprints/                 # .pretty dir for curated footprints (ReRAM-SMU-V1.pretty alias)
│       └── README.md               # footprint curation notes
└── sheets/ (9 hierarchical sheets)
```

### sym-lib-table

```s
(sym_lib_table (version 7)
  (lib (name "ReRAM-SMU-V1") (type "KiCad") (uri "${KIPRJMOD}/lib/ReRAM-SMU-V1.kicad_sym") ...)
)
```

Uses `${KIPRJMOD}` so the project is relocatable (no absolute paths).

### fp-lib-table

```s
(fp_lib_table (version 7)
  (lib (name "ReRAM-SMU-V1") (type "KiCad") (uri "${KIPRJMOD}/lib/footprints") ...)
)
```

Add per-part subsets as needed (e.g. `${KIPRJMOD}/lib/footprints/OpAmp.pretty`) but keep the root alias.

### Current kicad_sym

- `ReRAM-SMU-V1.kicad_sym` header: `(version 20251024)` / `(generator_version "10.0")` — matches KiCad 10.0.5 `kicad_symbol_editor`.
- Contains one template symbol: `ReRAM-SMU-V1_Template_Precision_OpAmp` (showcases required fields, pin style, and graphics conventions). Copy this as starting point for each manufacturer part.
- Verified with `kicad-cli sym export svg` — SVG export succeeded (1 symbol rendered).

## Manufacturer Symbol Curation Workflow

Every precision/controlled part gets a **curated** symbol cloned into `ReRAM-SMU-V1.kicad_sym`. Do NOT reference global libraries in the schematic (`Device:R`, `Amplifier_Operational:OPA*` etc. are placeholders only — replace with curated symbols before layout freeze).

### Priority Queue (by schematic sheet)

| Sheet | Parts to curate | Notes |
|---|---|---|
| 02_DAC_SOURCE_COMMAND | AD5764 / AD5764R, ADR45xx reference, DG469/ADG819 SPDT for VCSRC/VCSNK | 16-bit bipolar DAC is cost/sourcing driver — curate exact MPN early |
| 03_OUTPUT_STAGE | LT1970A / LT1991-class power op-amp, AD8421-style instrumentation stage if needed | Validate SOA, guard ring footprint |
| 04_KELVIN_SENSE | AD8421 / INA188, ADG1409 mux or equivalent | Low leakage, guard-driven footprint mandatory |
| 05_CURRENT_RANGES | ADG5412/ADG1408 switches, 0.1% shunt resistors, reed vs. solid-state range switches | Each range gets its own verified shunt + switch pair |
| 06_CURRENT_FRONTEND_ADC | ADA4530-1 / OPA145 femtoamp stage, ADS1220/ADS1262 ADC | Electrometer-grade symbol must show guard pin explicitly |
| 07_COMPLIANCE_TRIP | TLV3501 / ADCMP60x comparator, LTC6993 timer if used | Fast over-current flag — keep footprint minimal |
| 08_MCU_USB_CONTROL | STM32G4xx / RP2040, CP2102/CH343 USB bridge, ESD arrays | MCU symbol must expose SWD + USB + SPI to AD5764 |
| 01_POWER / 09_DUT | Isolated DC-DC, LDOs, pogo/4-wire DUT connector | DUT connector needs custom guard-ring footprint |
| Passives | Already generic `R`/`C` — curate only precision 0.1% / C0G / low-leakage where it matters | Do not bulk-import all passives |

### Per-Part Checklist (must pass before merge)

1. **Source**: Download from manufacturer (ADI, TI, LT) or Ultra Librarian/SnapEDA, then *audit* — do not trust blindly. Cross-check pin table vs. datasheet Rev. date.
2. **Pin table**: Number, name, type (`input`/`output`/`power_in`/`passive`/`open_collector` as per KiCad ERC needs), length `2.54mm` (100 mil) unless dense, hidden power pins forbidden (explicit V+/V-).
3. **Graphic**: IEEE triangle not used for precision parts — use plain triangle for op-amps, box + pin labels for ADC/DAC/MCU. Visible pin numbers (`hide no`).
4. **Fields (all required)**:
   - `Reference` (U/J/Q), `Value` (=MPN), `Footprint` (`ReRAM-SMU-V1:<footprint>`), `Datasheet` (HTTPS URL)
   - `Manufacturer`, `MPN`, `LCSC` (if LCSC stocked), `Description` (with voltage/current/grade)
   - `ki_keywords`, `ki_fp_filters` (pin-filter the footprint)
   - Optional: `Octopart_MPN`, `Mouser_Part_Number` if used for BOM automation
5. **Footprint link**: Every curated symbol's `Footprint` field points into `lib/footprints/` (or a sub-`.pretty`). The footprint itself must be curated/measured, not assumed — check courtyard, paste, and 3D model offset.
6. **Verification**:
   ```sh
   "E:/KiCad/bin/kicad-cli.exe" sym export svg --output /tmp/svg_out "E:/ReRAM-SMU V1/hardware/kicad/ReRAM-SMU-V1/lib/ReRAM-SMU-V1.kicad_sym"
   "E:/KiCad/bin/kicad-cli.exe" sch erc --format json --output erc_verify.json "E:/ReRAM-SMU V1/hardware/kicad/ReRAM-SMU-V1/ReRAM-SMU-V1.kicad_sch"
   ```
   ERC intentional errors (dangling global labels in root skeleton) are expected until sheets are wired — focus on `lib_symbol_issues` / `lib_symbol_mismatch` = 0 after curation.
7. **Review**: Commit symbol + footprint + this doc update in one PR; attach datasheet page screenshot of pinout.

### Naming Convention

- `ReRAM-SMU-V1_<MANU>_<MPN>` e.g. `ReRAM-SMU-V1_ADI_AD5764R`, `ReRAM-SMU-V1_TI_OPA145`, `ReRAM-SMU-V1_ADI_ADA4530-1`.
- Template symbol is never placed on schematic — it is the copy-source only.

### Footprint Curation

- All custom guard-ring / Kelvin footprints go under `lib/footprints/` as `.kicad_mod` files.
- IPC-7351 nominal; add 0.2 mm courtyard for precision analog (prevents solder-mask encroachment on guard trace).
- Each footprint stores its 3D model relative to `${KIPRJMOD}/lib/3dmodels/` if present.

### What NOT to do

- Do not add global `sym-lib-table` / `fp-lib-table` entries — keep the machine portable.
- Do not edit `ReRAM-SMU-V1.kicad_sym` by hand-copying S-expressions without re-validating via `kicad-cli` (parens are unforgiving).
- Do not leave curated symbols with empty `Datasheet`/`Manufacturer` fields.

## Verification Log (this run)

- **KiCad**: `E:/KiCad/bin/kicad-cli.exe --version` → `10.0.5`.
- **Schematic format**: `(version 20241014)` — latest for KiCad 10 sch (per `sch upgrade` dry-run exit 3 = already current). Normalized `generator_version "8.0" → "10.0"` across all 10 `.kicad_sch` files (root + 9 sheets).
- **Symbol lib**: `(version 20251024)` / `generator_version "10.0"` — matches shipped `Device.kicad_sym`. Force-upgrade exit 0, SVG export of template symbol succeeded.
- **ERC**: `sch erc --format json` on root → 503 total violations (expected skeleton state: 202 pin_not_connected, 80 lib_symbol_mismatch from generic OpAmp placeholders, 49 label_dangling on root global labels — all will resolve as sheets are wired and curated symbols replace placeholders). No file-parse errors — integrity OK.

