# Continuous supplied-interval section stability

Validated ADR-0059 and phase1b-section-stability.md were imported at 42a709e
before implementation. Independent repository review corrected the triangulated
cube fixture: moving diagonal intersection nodes make the conservative bound
twice the halfwidth, although its actual XY boundary is stationary.

domain/section_stability.py owns the closed immutable result;
engine/section_stability.py freshly checks embedding and topology, partitions
the supplied interval at every source vertex height, checks event continuity and
accumulates exact affine slab displacement bounds. The extra unit in each speed
factor includes Z, bounding continuous symmetric 3D Euclidean Hausdorff distance.
Unrepresented tangent vertices and same-side ON edges remain unproven. Excessive
upper bounds return displacement-unproven, not a false claim of instability.

Private section tolerances are now explicit; the existing public wrapper passes
its unchanged configured values. The exact interval route passes rational zeros
without constructing an invalid policy. Private embedding returns its same-call
topology as well as triangles; the existing point classifier retains behavior.
No dependency, identity authority, Orca callback or G-code output was added.

## Verification

Isolated Windows Python 3.12.10; code-quality-audit applied before tests:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `.venv/Scripts/python -m unittest tests.unit.test_mesh_section tests.unit.test_material_side -q`: 35 PASS.
- Independent `.venv/Scripts/python -m unittest tests.unit.test_section_stability -v`: 14 PASS.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 470 PASS.
- `.venv/Scripts/python tools/check_canonical_manifest.py --handoff docs/specs/phase1b-section-stability.md`: 83 Git blobs PASS.
- Independent implementation review: no actionable findings. Additional refined
  tetrahedron checks confirmed crossing a vertex event, analytic bound 3/4,
  inclusive tolerance and exact query cap while public near-ON behavior remains.
  Review identified missing distinct ON-edge coverage; a sloped-roof cube test
  now proves both ON endpoints are represented before the same-side edge guard
  refuses the interval. All regression tests were rerun after this addition.
- Research archive clean extraction/import includes the stability module; exact
  committed-head artifact and CI receipts are published in Draft PR #8.
- Lint/type tools remain NOT CONFIGURED. No dependency installation.

Fixtures include analytic cube/tetra bounds, ordinary vertex crossings, orphan
tangency, multiple loops, horizontal facets, exact intervals narrower than float
spacing, interval bounds beyond binary64 range, reversal/mirror/translation,
budget boundaries and cancellation at every observed checkpoint. These tests
support the continuous proof; they do not replace it with sampling.

## Remaining work

The caller supplies the interval; actual Orca formatter/frame uncertainty has
not been derived. Triangulation can make the bound conservative and reject
usable intervals. General candidate centerlines, bands, improvement objectives,
optimization, actual Orca snapshot/preview and final G-code validation/atomic
output remain unfinished. This is not an installable completed plugin.

No GUI capture/control, printer operations, G-code mutation, security changes or
deletion outside C: occurred. Untracked log_iotc.txt remains untouched.
