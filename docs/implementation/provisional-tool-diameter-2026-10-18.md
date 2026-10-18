# Configurable provisional planar tip diameter

User instruction: proceed provisionally with0.4mm and make it changeable later.
Parent-validated contract: `docs/specs/provisional-tool-diameter-review.md`.
Interpretation is an assumed **diameter**, not radius or measured whole head.

## Changes

- `tools/provisional_tool_geometry.py`: immutable tools-owned
  `ProvisionalPlanarTip` with positive exact Fraction diameter, default2/5mm,
  derived radius1/5mm, explicit model/version and deterministic SHA256 identity.
  Equivalent rationals have identical identities. Shared sweep owner computes
  radius-expanded XY bounds from exact segment endpoints; Z uses only endpoint
  extrema. Full-polyline owner unions every segment envelope, including interior
  extrema, using the same one-leg owner. No invented axial extension.
- `tools/review_supplemental_hops.py`: keyword
  `assumed_tool_diameter_mm` and CLI `--assumed-tool-diameter-mm` feed the actual
  geometry calculation. Reports include assumption/identity, separate saved
  nozzle-orifice diameter and inequality diagnostic; these are different
  quantities and inequality is explicitly not a profile error. Review identity
  binds source/project/manifest, geometry and precision. All complete-head,
  clearance and physical authorization fields are false.
- All three legs of each actual raise/XY/descent bridge use quantized command
  endpoints and the assumed radius. Added ID-retaining envelopes for every
  complete quantized supplemental polyline plus centerline hashes. No command,
  Z-hop, source setting, line width, extrusion or production profile is changed.
- `tests/unit/test_provisional_tool_geometry.py`: five meaningful tests cover
  exact positive diameter/default/radius/identity, invalid/nonfinite input,
  immutability, pure-Z and oblique negative-coordinate bounds, exact touching
  limits, full-polyline interior extrema, quantized endpoint/command agreement,
  equivalent and distinct assumptions, unchanged commands/hops/input hashes and
  false authority. Existing hop tests retain exact expected command strings.

## Actual pinned evidence

Created new `artifacts/provisional-tool-diameter-review/` only:

- `assumed-tool-diameter-0.4mm.UNVERIFIED.json`
- `assumed-tool-diameter-0.6mm.UNVERIFIED.json`
- `generation-receipt.json`

Actual CLI invocations captured as separate JSON files (exit0 each):

```powershell
& .\.venv\Scripts\python.exe -m tools.review_supplemental_hops --folder artifacts/revolved-exponential-review --assumed-tool-diameter-mm 0.4
& .\.venv\Scripts\python.exe -m tools.review_supplemental_hops --folder artifacts/revolved-exponential-review --assumed-tool-diameter-mm 0.6
```

Before/after hashes matched pinned original source
`8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95`,
placed sliced project
`0f4d85b55a2c3e1f579cc013d722f755a657f17dadb840d8a020792099aa3d61`
and manifest
`dbeabdef2570d25d9f9546443e9e0d3970ec17016f840c7d2ef1b6154278ecf0`.
Each report contains30 complete path envelopes and18 bridges with54 leg bounds.
Bridge command strings agree across assumptions. Radii are0.2 and0.3mm; review
identities differ:

- 0.4 mm: `e499fe0103aece9b3c54ca696d5381f6d3d5c542f6487a40acd51bbedb6fe2a3`.
- 0.6 mm: `736cf55503ac05e172d4bad1d00c90aac55becfa605ba4776dae7097f91deadc`.

Existing original/research/restored artifacts and `log_iotc.txt` were preserved.

## Checks and limits

Required interpreter `.venv\Scripts\python.exe`, Python3.12.10:

1. `& .\.venv\Scripts\python.exe -m py_compile tools/provisional_tool_geometry.py tools/review_supplemental_hops.py tests/unit/test_provisional_tool_geometry.py`
   -> PASS,exit0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_provisional_tool_geometry tests.unit.test_supplemental_z_hop -q`
   -> PASS,20 tests,exit0.

Focused checks only as requested; parent/independent review precedes full suite.
No dependencies, source planner, domain/runtime contract, firmware interpretation,
printer connection or print changed. This is a conservative broad-phase planar
bounding diagnostic only. No obstacles are queried, and no complete head,
physical contact, collision-free path or downstream clearance is certified.
No axial height, uncertainty margin or physical ToolClearanceProfile invented.
Ready for parent and independent review; physical gates remain closed.

## Parent verification and reconciliation

Parent audited full source/tests and independently checked actual 30 path
envelopes and 54 bridge legs. Independent blind review reproduced both API/CLI
reports and found no material geometric defect. Parent Low finding for repeated
default literals was fixed with one shared exact default; independent reviewer
verified default and explicit 0.4/0.6 output remains byte-equivalent in JSON
structure to the existing artifacts. No remaining finding in this bounded scope.

Final Python 3.12.10 checks: syntax PASS, architecture 45 PASS, related tests
20 PASS, full discovery **818 PASS** (142.854 s). Evidence logs:
`artifacts/print-development-loop/provisional-final-*.log` and
`provisional-focused.log`. These results cover provisional analysis configuration,
not physical print or collision certification.

Parent primary audit identified duplicated default ownership (Low). Corrected
with one exported exact `DEFAULT_ASSUMED_TOOL_DIAMETER_MM` in the geometry owner,
reused by the model, review API and CLI. CLI help derives its displayed default
from that same owner. Behavior and geometry/review identities remain unchanged;
existing artifacts were not regenerated. Required Python3.12 syntax and focused
20 tests passed again, exit0.
