# Exact unscored convex chord proposals

ADR-0005 canonical adoption 53b1a0c and its validated handoff were imported at
44ca08b before production edits. Earlier candidate-generation review findings
were resolved for this bounded primitive; general exposed-band reconstruction
and scored candidate generation remain outside it.

domain/convex_chords.py owns immutable, closed unscored proposal results.
engine/convex_chords.py validates mesh embedding and exact section once, rejects
nonconvex sections, clips axis-aligned chords against the complete transverse
footprint halfplanes, trims their endpoints and verifies strict material inclusion.
The private segment classifier in material_side is shared by the existing public
API and the proposal engine. Rational endpoints never round through binary64.

For each CCW halfplane a*x+b*y+c>=0, an X-directed width-w chord at y=s requires
a*x+b*s+c-|b|*w/2>=0. Linearity makes this a whole rectangular-footprint check.
It is not an extrusion-volume, support or improvement proof. Singleton intervals
remain nonempty until trimming, then fail insufficient-span. Global unknown or
cancellation discards every row; individual empty/narrow positions remain explicit.

## Verification

Windows isolated Python 3.12.10; code-quality-audit gate order:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `.venv/Scripts/python -m unittest tests.unit.test_material_side tests.unit.test_mesh_segment tests.unit.test_section_stability -q`: 49 PASS.
- Independent `.venv/Scripts/python -m unittest tests.unit.test_convex_chords -v`: 15 PASS.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 503 PASS.
- `.venv/Scripts/python tools/check_canonical_manifest.py --handoff docs/specs/phase1b-convex-chord-proposals.md`: 83 canonical Git blobs PASS.
- Independent implementation review: no actionable findings. Reviewed exact
  clipping, convexity prerequisites, closed DTOs, budget precedence, cancellation
  and the preserved public segment-classification boundary.
- Clean extracted research-package imports include convex_chords; committed-head
  build hash and Windows CI receipts are recorded in Draft PR #8 after integration.
- Lint/type tools remain NOT CONFIGURED. No new dependencies or physical defaults.

Independent fixtures include unit triangle/cube prisms, exact endpoint 2/3,
concave L-prism rejection, both axes, collinear nodes, whole transverse width,
empty/singleton/trim limits, reversed/mirrored/translated geometry, normalized
duplicates, oversized malformed position tuples, fresh validation once, all
observed cancellation checkpoints and failure after earlier proposed rows.

## Remaining work

These are naturally open unscored proposals, not feasible SubEdgePath/Plan
instances. Exposed-band geometry, nesting, finite-bead support/error evaluation,
effective height/flow/speed/regularity, optimization, real Orca snapshot/preview
and verified atomic G-code output remain unfinished. Current packaging remains
a research archive, not an installable completed plugin.

No desktop capture/control, printer operation, G-code mutation, security change,
merge/release or deletion outside C: occurred. Untracked log_iotc.txt is untouched.
The user's resumed request superseded the previous 15-percent usage stop; the
user owns usage monitoring/reset, and no credits were purchased or redeemed here.
