# Exact nominal bead-pair volume audit

Parent-validated contract: `docs/specs/nominal-bead-volume-review.md`. This is
tools-only nominal solid intersection evidence, not physical tool clearance.
Caller owns source association, chronology and which pairs belong to a job.

## Changes and invariants

- `tools/audit_nominal_bead_overlap.py`: reusable pure pair function over two
  immutable `ExactNominalTopSegment`s and frozen explicit resource policy.
  Conservative XYZ envelopes first exclude separated/touching interiors. Known
  axis-aligned flat caps have no axial extension; oblique envelopes retain the
  larger conservative radius-expanded box. These are exclusion envelopes only.
- Every remaining positive-area XY cell queries each bead and its vertical
  reflection through existing `query_exact_nominal_top_cell`. Reflection uses
  commandZ=height-originalZ; reflected top=-original bottom. No replacement
  cap/joint/float-distance model. This also handles linear varying-Z structural
  segments using the existing kernel.
- A cell is disjoint when support is absent or topUpper<=otherBottomLower.
  Overlap requires both full XY coverage and strict positive vertical interior
  max(bottomUpper)<min(topLower). Otherwise bisect the longer XY axis. All leaf
  areas sum exactly to the original overlap box; subdivision preserves shared
  exact boundaries without holes. Exact touching is not positive volume.
- Reports freeze pair IDs, policy, state, every cell/reason, exact positive-volume
  witnesses, query/count totals, cancellation and false physical authority.
  Query/depth/input-bit/kernel exhaustion cannot pass. Cancellation must return
  exact bool and is latched. Explicit `stop_after_overlap` policy (default true)
  retains all remaining XY cells unresolved after a positive witness; it never
  silently declares those cells processed or the full job safe.
- `tests/unit/test_nominal_bead_overlap.py`: nine real-kernel tests cover
  identical/partial overlap, separated XY/Z, touching, oblique/reversed segments,
  oblique disjoint pairs requiring kernel refinement, flat caps, varying-Z
  reflection, cancellation/resource outcomes, malformed input and exact positive
  witnesses. Input-bit checks occur before reflection arithmetic.

## Actual outward-ring25 / future4.4 regression

New research receipt:
`artifacts/nominal-bead-overlap-review/outward-ring25-future44.UNVERIFIED.json`.
Generation used the same pinned fixture constructor as the unit regression and
the pure pair function under review, with project Python3.12.10.

Provenance retained:

- Original source SHA256:
  `8d7b530bc351826f496182c6c080c5f8f379e0eb22f01e7ccea4a26966811b95`.
- Original manifest SHA256:
  `dbeabdef2570d25d9f9546443e9e0d3970ec17016f840c7d2ef1b6154278ecf0`.
- Geometry research diagnostic SHA256:
  `dd2e359477fef64794f52cdbcf5949f93fd92b0073a0a501399a0ed3ae22f0de`.
- Future source line14787 is independently retained as
  `(98.405,90.413,4.4)->(98.405,89.602,4.4)`, width0.42,height0.2.
  Exact raw original source lines14786/14787 are checked against the pinned file.
- Candidate: existing ring25 radius+0.04, original nominal width, physicalh0.18,
  remaining0.126 (top4.326), first original-phase chord at the displaced radius,
  then XYZ3. Existing ring-vertex recipe is used only to build this labeled
  regression input; the audit itself receives exact rational endpoints.

Result: **overlap-proven**,440 kernel calls, one exact positive-area/positive-Z
intersection cell and27 explicitly unresolved remaining cells under early-stop
policy. This refutes compatibility for that pair despite higher future nozzle
tipZ. It does not certify any other pair, source-parallel alternative, chronology,
or tool envelope. No original or restored artifact was changed.

## Executed verification

Required `C:\VSC\Smoothificator\.venv\Scripts\python.exe`, Python3.12.10:

1. `& .\.venv\Scripts\python.exe -m py_compile tools/audit_nominal_bead_overlap.py tests/unit/test_nominal_bead_overlap.py`
   -> PASS,exit0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_nominal_bead_overlap tests.unit.test_top_contact_cells tests.unit.test_continuous_path_contact -q`
   -> PASS,24 tests,exit0.

Focused checks only; full suite held as requested pending core-stage review.
No dependencies, source parser, geometry kernel, production module, printer
connection, printing, commit, push, merge or release. Existing dirty work and
`log_iotc.txt` preserved. Ready for parent primary and independent review before
the function is used to accept planner alternatives. All physical gates remain
closed; nominal touching is not a physical clearance or permitted-contact policy.
