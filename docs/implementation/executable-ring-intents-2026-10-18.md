# Quantization-aware immutable ring intent preparation

Parent-validated contract: `docs/specs/executable-ring-intent-review.md`.
Scope is offline numeric intent preparation only; geometric quality improvement
remains deferred. No real-source anchor, source mutation or printer operation.

## Changes and design

- `tools/prepare_executable_ring_intents.py` verifies full source, sliced project
  and manifest pins plus embedded G-code association through the existing saved
  profile reader. It validates unique ring IDs, complete chord indices/closure,
  orphan/disconnected graphs and original nine-decimal XY endpoints.
- Quantize top first; freeze physical height as `(top-floor)/(1-overlap)`.
  Preserve all original radii/nominal widths and overlap. Validate remaining
  minimum, saved layer-height90% cap, next-layer ceiling, stadium dimensions and
  exact per-rectangle radial triangle intersection/spill via existing owner.
- Search original chord-count divisors largest first; retain only existing
  endpoint subsets with unchanged phase/closure. Exact rational squared norms
  of endpoints and clipped closest projection enforce the full-segment radial
  band. No square-root estimate, epsilon, widened rectangle or fresh circle.
- Use authoritative geometric/command-flow functions, existing nearest E
  quantization and actual quantized segment lengths. Remove commanded multipliers
  before deriving effective geometric widths using the existing inverse flow
  function. Check positive E, user width bounds, positive emitted feed and actual
  quantized-E volume-rate cap. Reject the whole job with per-ring reasons if no
  divisor is legal; no automatic candidate omission.
- Frozen outputs retain immutable `SupplementalPath`s, input and settings
  identities, precision policy, radial budget, original/intent dimensions,
  selected indices, rejected divisors and per-segment E/F diagnostics. Existing
  composer receives unchanged prepared intent, with independent synthetic replay.
- `tests/unit/test_executable_ring_intents.py`: 8 actual-fixture tests cover all
  30 paths, deterministic divisor search, original fixed-height failures, E192
  width failures, exact radial band, pins/graph failures, bounds/overlap/spill,
  positive emitted E/width/rate and exact composer E/F/restoration agreement.

Rejected alternatives: ID-specific chord rules, epsilon-bound relaxation,
ceil-E overrides, silently missing rings, changes to packed radii or widths,
invented source anchors and weakening production safety gates.

## Actual receipt

Executed `& .\.venv\Scripts\python.exe -m tools.prepare_executable_ring_intents`
-> exit 0. New output:
`artifacts/revolved-exponential-execution/ring-intents.UNVERIFIED.json`.
No G-code file emitted. No restored-baseline or preexisting preview/source bytes
changed. The JSON contains all 30 frozen paths and synthetic replay receipts.

Association pins:

- Source: `8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95`.
- Placed sliced project: `0f4d85b55a2c3e1f579cc013d722f755a657f17dadb840d8a020792099aa3d61`.
- Original manifest: `dbeabdef2570d25d9f9546443e9e0d3970ec17016f840c7d2ef1b6154278ecf0`.

Result: all 30 radii/nominal widths retained; 5,568 chords. Deterministic search
selects 96 for ring-2/ring-3 and 192 for the others, independently reproducing
the earlier investigation. Seven original fixed-height blocks fail XYZ3 bounds
before preparation; corrected intent freezes legal grid heights rather than
changing emitter acceptance. Synthetic replay covers every original-layer batch
and restores exact anchor state. Per-ring tests additionally compare every
composer-emitted E/F pair against the frozen diagnostics.

## Verification

Required interpreter: `.venv\Scripts\python.exe`, Python 3.12.10. Final commands:

1. `& .\.venv\Scripts\python.exe -m py_compile tools/prepare_executable_ring_intents.py tests/unit/test_executable_ring_intents.py tools/restore_saved_print_profile.py tests/unit/test_restore_saved_print_profile.py`
   -> PASS, exit 0.
2. `& .\.venv\Scripts\python.exe -m unittest discover -s tests/architecture -q`
   -> PASS, 45 tests, exit 0.
3. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_executable_ring_intents tests.unit.test_restore_saved_print_profile tests.unit.test_supplemental_copy tests.unit.test_supplemental_z_hop tests.unit.test_print_source_inspection -q`
   -> PASS, 60 tests, exit 0.

Parent owns final full regression and source/independent review. No dependencies,
production modules, parser behavior, runtime hooks or physical gates changed.

## Limits and next gate

Research output remains explicitly non-print-authorized; execution, support,
tool clearance and real-source anchors remain false. These rings are associated
with the original review source, not automatically rebound to the newly restored
saved-program baseline. Exact radial band proves only quantized center-segment
deviation, not circumferential material support or tool-body clearance. Emission
parity uses the existing research formatter policy and is not a firmware/parity
certificate. Synthetic anchors are labeled assertions, never actual printer
state. Ready for parent and independent audit; not ready for physical printing.
