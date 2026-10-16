# Exact whole-segment material classification

Validated ADR-0030 and phase1b-mesh-segment.md were imported at ca60afd before
implementation. The existing material-side domain/engine owners now classify a
whole closed segment, and triangle_intersection owns its exact contact predicate.
Private point parity is shared with the unchanged public point API.

Every call freshly validates topology/embedding once, then tests every source
triangle for closed segment contact. Exact coplanar parameter clipping retains
singleton tangencies, edge overlap and endpoint contact. Contact-free segments
require both endpoint parity results to agree; disagreement remains incomplete.
This rejects the endpoint-only shortcut for concave solids: an interior-to-interior
segment can cross an external cavity. Boundary-contact means any contact, not
that the entire segment lies on the boundary.

## Verification

Isolated Windows Python 3.12.10, existing code-quality-audit gate order:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `.venv/Scripts/python -m unittest tests.unit.test_material_side tests.unit.test_section_stability -q`: 31 PASS.
- Independent `.venv/Scripts/python -m unittest tests.unit.test_mesh_segment -v`: 18 PASS.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 488 PASS.
- `.venv/Scripts/python tools/check_canonical_manifest.py --handoff docs/specs/phase1b-mesh-segment.md`: 83 canonical Git blobs PASS.
- Independent review found no actionable findings. An additional exact AABB
  oracle agreed with all 80 seeded cube segments; the independent suite includes
  concave nested cones, coplanar and vertex/edge contact, exact tiny/large inputs,
  fresh validation, resource limits, callback failures and all observed
  cancellation checkpoints. Private fault fixtures check inconsistent evidence.
- Clean extracted research package checks the segment API; same-head build and
  Windows CI receipts are recorded in Draft PR #8 after commit.
- Lint/type tools remain NOT CONFIGURED. No dependencies added.

## Limits and next step

This is a necessary segment containment predicate, not candidate generation or
finite-width bead containment. It does not provide an offset, surface band,
support, clearance, error improvement, Orca provenance or G-code authority.
Candidate construction/optimization, actual Orca snapshot/preview and validated
atomic output remain unfinished. No cross-call proof cache or identity authority.

No GUI capture/control, printer operation, G-code mutation, security change or
deletion outside C: occurred. Untracked log_iotc.txt remains untouched.
