# Exact continuous-span contact query

Parent-validated contract: `docs/specs/exact-contact-span-review.md`.
This additive engine API reuses the existing exact nominal geometry owner;
no geometry, source parser, planner, bead-pair audit or physical gate changed.

## Changes and proof meaning

- `adaptive_subedge/engine/support_cell.py`: public
  `query_exact_nominal_top_span` validates distinct immutable exact XY endpoints
  and delegates to `_exact_top_query`. Projection and signed lateral coordinates
  are affine over the entire straight segment; endpoint extrema therefore bound
  every parameter. Existing squared lateral distance, rounded-cap and varying-Z
  interval bounds apply throughout the span. No endpoint-sampling acceptance.
  Different sources covering different endpoints cannot supply a full lower
  bound unless an individual source covers the whole span, just as in the core.
- `adaptive_subedge/domain/support_cell.py`: the exact query result admits the
  additive full-bound reason `one-segment-covers-span`. Existing point/cell
  reasons and behavior remain unchanged.
- `tools/audit_continuous_path_contact.py`: optional explicit policy mode
  `exact-span`; default remains `padded-axis-box`. Exact span queries retain every
  actual queried parameter interval/endpoints, including nonterminal parents,
  and leaf witnesses have no fictitious enclosing cell. Reports separate
  `cells_queried`, `spans_queried` and total `query_count`. Existing default
  counts/behavior are preserved. Parameter partition, chronology exclusion,
  cancellation, resources and permanently false physical authority are unchanged.
- `tests/unit/test_exact_nominal_top_span.py`: six focused tests exercise whole
  oblique coverage; separate endpoint sources with a real interior gap; partial
  coverage; varying command-Z and rounded lateral profile; invalid/degenerate
  endpoints and duplicate sources; resource/cancellation handling; mode-specific
  queried geometry, full interval coverage, future-source exclusion and unchanged
  default box behavior. Existing kernel/contact tests also pass.

## Actual frozen source-offset candidate comparison

New receipt: `artifacts/exact-contact-span-review/source-offset64.UNVERIFIED.json`.
Reads the exact existing64-edge source-offset candidate without rebuilding or
changing its coordinates. All64 edges are nominal-centerline-contact-proven.

- Previous padded-axis-box receipt:24,860 queries.
- New exact-span audit:80 queries (310.75 times fewer),0.5s measured audit loop.
- Same maximum parameter depth14, sqrt128 bits, coordinate4096 bits and100,000
  global query budget; no weakened gate or lower precision. Padding1e-12 remains
  recorded for policy compatibility and conservative source-envelope pruning;
  the span kernel itself queries the exact line, not that padded box.
- Every actual span query and final interval witness is retained in the new
  receipt. Source chronology uses explicit extracted line order strictly before
  the first future4.4 model deposition. Spatially disjoint source envelopes and
  sources whose maximum top is below candidate bottom are conservatively
  excluded, matching the earlier comparison's input selection.

Verified current pins and original embedded/separate G-code association before
querying; all input hashes remain identical afterward:

- seam0 source: `fc1655086645ba1fd3758b4c5554fa3039044d6ba126457f473470d2d28eee60`;
- sliced project: `dd9a236689c0517057f14fc38d6ec36876c79777ed3a56307b17e32c55d0fc9b`;
- extracted source rows: `46c23686ef31072f9ba0dec968603325f55477fa966fd0414df9ad4340fddb1b`;
- existing candidate/box proof: `2b4af8efc9d1cba5dff24e4871096d4f3162ba4fcd941578cc98a79e2b922dbf`.

This comparison is exact nominal contact evidence only, not a new Plan,
source-association migration, full footprint, future-volume compatibility or
physical tool-clearance certificate. No actual source anchors are inferred.

## Verification

Only required `.venv\Scripts\python.exe` Python3.12.10 was used.

1. `& .\.venv\Scripts\python.exe -m py_compile adaptive_subedge/domain/support_cell.py adaptive_subedge/engine/support_cell.py tools/audit_continuous_path_contact.py tests/unit/test_exact_nominal_top_span.py`
   -> PASS,exit0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_exact_nominal_top_span tests.unit.test_continuous_path_contact tests.unit.test_top_contact_cells tests.unit.test_nominal_support_cell -q`
   -> PASS,38 tests,exit0.

Focused/syntax checks only as requested; full regression deferred until the main
planner stage is ready. New artifact generation used the same project interpreter
and existing frozen extracted-source/candidate JSON inputs with explicit pin
assertions. No source/geometry regeneration, printing, connection, dependency,
commit, push, merge or release. Existing dirty work and `log_iotc.txt` preserved.
Ready for primary and independent review before planner acceptance use.
