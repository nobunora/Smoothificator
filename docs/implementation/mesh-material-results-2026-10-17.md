# Exact mesh embedding and material-point predicates

The independently validated ADR-0030 / phase1b-mesh-material.md was imported at
f8cd989 before production changes. domain/material_side.py defines two closed
result types; engine/material_side.py owns fresh validation and bounded parity;
engine/triangle_intersection.py owns exact closed triangle intersections and
point/ray predicates. No dependency or canonical identity registration was added.

Every pair of faces is checked, including adjacent faces. Coplanar polygon
clipping retains point/edge contacts; nonparallel plane slices intersect as exact
line intervals. Contact is allowed only inside the actual shared source vertex
or edge. The point classifier revalidates topology and embedding on every call,
checks boundary first, then tries deterministic exact rays. Edge/vertex/coplanar
ray ambiguities retry within the supplied limit; exhaustion stays incomplete.

## Verification

Windows isolated Python 3.12.10:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- Independent `.venv/Scripts/python -m unittest tests.unit.test_material_side -v`: 17 PASS.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 456 PASS.
- Independent implementation review: no actionable findings. Additional seeded
  exact checks covered 3,000 triangle pairs (1,500 coplanar): returned points
  belong to both triangles and swapping arguments preserves the convex hull.
  All 125 analytic tetrahedron grid points matched boundary/inside/outside.
  These finite checks supplement the algorithm, not a proof by sampling.
- Canonical handoff integrity: 83 Git blobs PASS; clean archive imports PASS.
- Analytic fixtures cover ordinary and reversed/mirrored tetra/cube, actual
  self-crossing and nonlocal coincident source vertices, legitimate concave
  geometry, triangle intersection in both argument orders, coplanar projection
  axes, exact boundary/inside/outside, ray retries/exhaustion, pair limits,
  subnormal/huge coordinates and cancellation at every observed checkpoint.
- Lint/type analyzers remain NOT CONFIGURED; no new dependency was installed.

Full regression, independent implementation review, manifest integrity and
same-commit archive/CI receipts are recorded in Draft PR #8 after integration.
Windows CI checks the new handoff; clean archive extraction imports material_side
and its triangle-intersection dependency.

## Limits

This establishes numerical geometry of the supplied normalized mesh, not Orca
provenance/frame parity, calibration, section quantization stability, toolpath
clearance or output permission. Boundary is not interior clearance. Pair work is
quadratic but explicitly capped; ray work is bounded separately. No cross-call
cache or caller-constructed result can bypass validation.

No GUI capture/input, printer connection, G-code mutation, security changes or
deletion outside C: occurred. Untracked log_iotc.txt remains untouched.
The next dependency is section stability and material-inside candidate path
construction, followed by error optimization and the actual Orca integration.
