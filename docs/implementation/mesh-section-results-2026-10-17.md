# Exact single-plane source sections

Validated ADR-0059 / phase1b-mesh-section.md was imported at 1d42087 before
production edits. domain/mesh_section.py and engine/mesh_section.py now produce
an exact rational single closed loop from an indexed triangle mesh. Mesh topology
is revalidated; caller-created topology is not trusted. Canonical source vertex
and edge IDs merge shared events before any geometric comparisons. Selected Z
and source coordinates are unchanged.

Ordinary cuts, true ON vertices and opposite-side shared ON edges contribute
segments. Tangential contacts contribute none. Coplanar facet tolerance has
precedence; nonzero near-ON distances remain incomplete. Distinct near nodes
reject instead of arbitrary snapping. Degree/component, crossing/touching and
collinear-backtracking checks precede exact CCW ordering. Required segment and
pair limits bound work; interruption never publishes a partial loop.

## Independent validation

Windows isolated Python 3.12.10:

- Syntax compilation and architecture 41 tests PASS.
- Independent `tests.unit.test_mesh_section` suite: 18 PASS.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 439 PASS.
- Fixtures: tetra/cube cuts, sloped vertex and shared-edge events, tangencies,
  coplanar/near-ON precedence, mirror/reversal, real multi-loop/branch/bow-tie
  meshes, adjacent overlap and nonadjacent endpoint contact, exact disjoint
  collinearity/tiny gaps, resource caps, every observed cancellation checkpoint,
  huge-coordinate arithmetic, frozen required DTO fields and identity exclusion.
- Independent review: no actionable findings; separate hand-derived rational
  tetrahedron, CCW/reversal, epsilon precedence and pair-budget checks passed.
- Lint/type tools: NOT CONFIGURED. No dependency added.

Full regression, canonical manifest, exact committed archive and Windows CI
receipts are recorded in Draft PR #8 after integration. The package builder now
imports both mesh modules from a clean archive extraction, and Windows CI checks
both validated handoffs.

## Meaning and remaining work

CCW is a planar convention. This result is neither a nozzle centerline nor a
material-side, embedded-solid or quantization-stability certificate. It cannot
be directly injected. Independent inside/outside checks, solid self-intersection,
section stability, candidate bands/paths, error optimization, real Orca snapshot,
preview and final matching/state/clearance/atomic output remain unfinished.

The user-facing goal remains actual improvement display and safe G-code output;
these two mesh steps supply real missing prerequisites, not a mock preview.
No GUI capture/input, printer connection, G-code mutation or security changes
were made. The existing diagnostic executable and saved coupon/export were
rechecked read-only; those old fixtures are not fresh runtime acceptance.
