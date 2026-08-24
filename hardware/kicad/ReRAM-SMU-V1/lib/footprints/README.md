# ReRAM-SMU-V1 Footprints — `lib/footprints/`

Project-local footprint library. Registered as `ReRAM-SMU-V1` in `fp-lib-table`:

```
(lib (name "ReRAM-SMU-V1") (type "KiCad") (uri "${KIPRJMOD}/lib/footprints") ...)
```

- Place curated `.kicad_mod` files directly in this directory (it is a `.pretty` library).
- Naming: `<Package>_<MPN>` e.g. `SOIC-8_ADA4530-1.kicad_mod`, `QFN-32_STM32G431.kicad_mod`.
- Guard-ring footprints get suffix `_GUARD` and must expose the guard copper on F.Cu with solder-mask opening.
- Verify each footprint with `kicad-cli pcb` or footprint editor before use; add 3D model under `lib/3dmodels/` if available.

Currently empty — footprints will be added alongside their symbol curation (see `../LIB_CURATOR.md`).
