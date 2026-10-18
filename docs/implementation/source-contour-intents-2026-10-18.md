# Generic source-contour proposals and shared numeric freezing

Parent-validated contract: `docs/specs/source-contour-intents-review.md`.
Continuing full-job planner work, not completed print readiness. No parser,
source-state or anchor bypass; projection engine/domain held unchanged during
their independent review.

## Changes

- `tools/prepare_source_contour_intents.py`: generic immutable source-contour
  proposal factory. Inputs explicitly bind source/project digests, ordered exact
  structural segment IDs/geometry, floor/upper, physical width/height/remaining,
  inward offset, pre-freeze minimum segment length and bounded construction.
  It validates closed connected constant-floor simple contours, nonzero edges,
  unique IDs, exact types, resource limits and boolean cancellation. Zero offset
  and zero minimum length are legal. Concave simple contours are supported;
  collinear adjacent positive-offset lines and degenerate/reversed/self-crossing
  constructions reject explicitly.
- Positive offset uses orientation-aware shifted supporting lines and adjacent
  line intersection as a floating proposal only. Serialize at explicit decimal
  construction precision, then exact existing XYZ quantization. Deterministically
  remove grid duplicates and declared short edges before freezing; every removed
  original vertex/source identity and reason is retained. Revalidate exact
  simplicity/orientation/nonzero geometry, coordinate bits and source-edge
  direction before publication. Never alter an already frozen intent.
- `tools/freeze_supplemental_emission.py`: one shared numeric owner freezes
  quantized XYZ, nearest E, downward-capped F, per-segment E-implied physical
  widths and volume rates using authoritative flow functions. Its shared exact
  dimension validator directly enforces physical bounds, minimum remaining,
  overlap0..30% and planner floor/top grid consistency. Original constant-Z intent
  is validated before quantization so varying top planes cannot silently merge.
- `tools/prepare_executable_ring_intents.py`: retained `_emission` API/radial
  guard and tuple return shape, delegating numeric arithmetic to the shared owner.
  Legacy ring E/F/min-max widths/volume rates match the original saved artifact
  exactly for all30 ordered IDs. No composer/planner optimization was added.
- `tests/unit/test_source_contour_intents.py`: seven meaningful tests cover zero
  offset/minimum0, both orientations/translations, provenance of grid/short-edge
  regularization, malformed/concave/unsupported/degenerate contours, resources,
  cancellation, remaining/overlap/height/nearest-E width failures, direct shared
  freeze dimension/original-Z rejection and exact30-ring legacy tuple parity.

Factory outputs retain complete provenance and policy identity, with accepted,
contact, future-volume and printable authority permanently false. No hardcoded
ring IDs, source coordinates or printer-profile values in the factory.

## Actual six contours, six groups, seven paths

New reproducible research evidence:

- `artifacts/source-contour-intent-review/reproduce.py`
- `artifacts/source-contour-intent-review/six-groups-seven-paths.UNVERIFIED.json`

Exact pinned fresh seam0 source/project association verified through the existing
profile reader and embedded/separate G-code equality. Source rows and both
reference recipe files are hash-pinned; receipt retains all hashes. All inputs
remain unchanged after the review.

Factory regenerates six source-contour proposals: floor4.2 offset0.212,width0.251,
height0.18,remaining0.126 and five single-lane zero-offset source-follow paths.
All six frozen point sequences, nearest E tuples and E-implied physical width
tuples match prior research exactly. Floor4.2 outer contour removes one declared
short source vertex before freezing and has64 edges; five other contours retain
65 edges and use minimum segment0. The separately retained inner circle has192
edges and receives fresh checks; it is not silently counted as a factory contour.
Thus **6 source contours,6 groups,7 paths**, with581 total path edges.

Fresh exact-span contact and public whole-solid projection results:

- All7 paths have complete nominal centerline-bottom contact proofs.
- 735 contact-span queries.
- 2,210,519 candidate/future-model bead pairs strictly separated on outward
  projection intervals, with no unknown pair hidden.
- 15,885 cached public projection queries;48.406s measured review loop.

Existing owners perform all proof acceptance. Cardinal axes are tested first;
additional axis proposals can use floating heuristics, but strict separation is
accepted only from exact public-owner outward bounds. Dot margins are not head
clearance millimetres. Chronology is explicit extracted source-line order; no
startup/firmware state is inferred.

The receipt remains an **unselected research proposal review**. Fresh finite
triangle spill, inter-path packing, all remaining groups, source anchors and full
tool/downstream/physical validation remain pending before selection/printing.
Old circle geometry has an explicit original-source provenance and is freshly
checked against the new source; no old executable Plan approval is transferred.

## Verification

Only `.venv\Scripts\python.exe` Python3.12.10 used:

1. `& .\.venv\Scripts\python.exe -m py_compile tools/freeze_supplemental_emission.py tools/prepare_source_contour_intents.py tools/prepare_executable_ring_intents.py tests/unit/test_source_contour_intents.py artifacts/source-contour-intent-review/reproduce.py`
   -> PASS,exit0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_source_contour_intents tests.unit.test_executable_ring_intents tests.unit.test_supplemental_z_hop -q`
   -> PASS,30 tests,exit0.
3. Final strengthened parity/concave tests:
   `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_source_contour_intents -q`
   -> PASS,7 tests,exit0.
4. `& .\.venv\Scripts\python.exe artifacts/source-contour-intent-review/reproduce.py`
   -> PASS,exit0; outputs listed above.

An initial proposed0.01-mm nearest-E failure fixture was actually legal; replaced
it with a verified0.003-mm undersized-width regression. Acceptance rules were not
changed to make it fail/pass. Parent primary audit requested shared dimension
validation, original-Z validation and explicit legacy count/order assertions;
all were addressed before declaring this revision stable.
Parent also identified untyped float conversion overflow for exact translated
geometry (X=10**400, still within the4096-bit input limit). Shared numeric freeze
now converts that specific OverflowError to explicit ValueError/nonfinite geometry;
the public-factory regression verifies rejection. Ordinary numeric outputs and
existing actual receipt bytes are unchanged.
Final post-overflow-fix syntax passed and
`& .\.venv\Scripts\python.exe -m unittest tests.unit.test_source_contour_intents tests.unit.test_executable_ring_intents -q`
passed15 tests,exit0. Factory/shared/ring files are held stable for independent
review after this revision.

Full suite deferred as requested. No source profile, parser, projection engine,
pair auditor, original artifact, printer connection, print, dependency, commit,
push, merge or release changed. Existing dirty work and `log_iotc.txt` preserved.
Ready for primary/independent audit; continuing group selection work remains.
