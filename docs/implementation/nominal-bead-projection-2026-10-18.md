# Exact whole-solid nominal bead projections

Parent-validated contract: `docs/specs/nominal-bead-projection-review.md`.
Engine/domain edits began only after parent confirmed exact-span primary and
independent reviews complete with no findings. This is additive geometry API
work; source/chronology and full-job acceptance remain caller-owned.

## Changes and mathematical owner

- `adaptive_subedge/domain/support_cell.py`: immutable
  `ExactNominalProjectionBounds` retains source identity, exact unnormalized XYZ
  axis, state/reason and ordered outward dot-product bounds. Resource/cancel
  outcomes contain no bounds; invalid states/axes/types reject.
- `adaptive_subedge/engine/support_cell.py`: public
  `query_exact_nominal_bead_projection` uses the existing `_sqrt_bounds` owner.
  With D=dx²+dy², q=(axisX*dy-axisY*dx)²/D, f=(width-height)/2 and r=height/2,
  outward support extent is f*sqrtUpper(q)+r*sqrtUpper(q+axisZ²).
  Endpoint centerline dot products use (x,y,commandZ-height/2); expand min/max by
  that outward extent. This is the canonical finite flat-capped stadium sweep,
  including linear varying-Z structural segments. No endpoint capsule or new
  cap/joint model. No float acceptance or axis normalization.
- Explicit coordinate/sqrt limits and exact boolean cancellation are validated;
  cancellation latches. Malformed input rejects; exhausted input-bit limits or
  cancellation return incomplete without numerical bounds.
- `tests/unit/test_nominal_bead_projection.py`: six meaningful tests cover known
  cardinal/oblique/axial-cap bounds, reversed endpoints and axes/scaling, vertical
  and varying-Z extents, outward rounded support, immutable outcomes, malformed/
  zero axes, limits/cancellation and all341 actual saved pair-axis certificates.

Existing point/cell/span APIs, pair-overlap auditor, parser, planner, nominal
geometry recipes and physical gates are unchanged. No dependencies added.

## Actual341 certificates through the public API

New receipt:
`artifacts/nominal-bead-projection-review/source-offset341.UNVERIFIED.json`.
All341 previously proposed exact rational axes were passed to the new public
owner for both candidate and future-source beads. Every pair has strictly
separated outward intervals; all exact margins reproduce the independently
checked research reference. Unknown pairs retained explicitly: empty list.
341 certificates took approximately0.156s in the generation loop.

Current source/project association and pins verified before generation; embedded
and separate source G-code agree, and every input hash remains unchanged:

- Source: `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`.
- Sliced project: `dd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b`.
- Extracted source rows: `46c23686ef31072f9ba0dec968603325f55477fa966fd0414df9ad4340fddb1b`.
- Frozen candidate: `2b4af8efc9d1cba5dff24e4871096d4f3162ba4fcd941578cc98a79e2b922dbf`.
- Independently checked axis reference: `cc70ab46be497d8c170914acd6e5278568399acd313f6ca85717511448866cad`.

The341 nearby pairs are the nontrivial subset of the prior315,136-pair research
job. This generation does not claim to recompute its314,795 broad-phase excluded
pairs; that count is explicitly historical in the new receipt. It does not
declare the full print safe. Proposed axes may originate in a research search;
certificate acceptance here uses exact rational outward intervals only.

All margins are **unnormalized axis-dot units**, not millimetres of nozzle/head
clearance. Overlapping intervals would be inconclusive, not overlap proof.
Every artifact has false print/physical-clearance authority. Original artifacts,
existing dirty work and unrelated `log_iotc.txt` preserved.

## Verification and next gate

Only project `.venv\Scripts\python.exe` Python3.12.10 used:

1. `& .\.venv\Scripts\python.exe -m py_compile adaptive_subedge/domain/support_cell.py adaptive_subedge/engine/support_cell.py tests/unit/test_nominal_bead_projection.py`
   -> PASS,exit0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_nominal_bead_projection tests.unit.test_exact_nominal_top_span tests.unit.test_nominal_support_cell -q`
   -> PASS,29 tests,exit0,including all341 actual certificate regressions.

Full suite deferred as requested until core stages/main planner integrate.
Ready for parent primary and independent review before planner acceptance use.
No printer connection/printing, G-code output, commit, push, merge or release.
