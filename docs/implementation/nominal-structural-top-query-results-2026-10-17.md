# Nominal structural top query implementation — 2026-10-17

Implementation basis: `docs/specs/nominal-structural-top-query-draft.md` at
specification commit `684e282`, `SPEC_VALIDATED` by independent repository
review against main `2257bd1`. Canonical audited basis is
`docs/AUDIT_REVISION_2026-10-16.json`; ADR-0048 supplies the one nominal
stadium sweep and closed flat-cap model.

## Scope and result

- `adaptive_subedge/domain/support_cell.py`: added a frozen/slotted outcome DTO
  that admits only the specified state/reason and rational-bound combinations.
- `adaptive_subedge/engine/support_cell.py`: added exact Fraction point and
  finite-binary64 cell queries for the union of horizontal structural source
  tops. Both call the existing `_segment_top_bounds` and `_sqrt_bounds` bead
  implementation, with no new flow or surface equation. Count/coordinate-bit
  preflight, exact input validation and cancellation fail closed.
- `tests/unit/test_nominal_structural_top.py`: independently checks closed
  point boundaries, circular limit, irrational enclosure, union max/order,
  full/partial/absent cells, source and coordinate budgets, cancellation and
  invalid inputs. Existing `query_nominal_support_cell` remains unchanged.

This is a research-only nominal top bound. It does not certify mesh coverage,
improvement, physical contact, Orca parity or G-code eligibility. No Plan,
Settings, Orca or G-code code was changed.

## Checks

Environment: `.venv/Scripts/python.exe --version` -> Python 3.12.10.

- `.venv/Scripts/python.exe -m compileall -q adaptive_subedge/domain/support_cell.py adaptive_subedge/engine/support_cell.py tests/unit/test_nominal_structural_top.py` — PASS.
- `.venv/Scripts/python.exe -m unittest discover -s tests/architecture -p 'test_*.py'` — 43 PASS.
- Lint, type and dependency-use tools — NOT CONFIGURED in this project; no
  tool or dependency was added for this bounded implementation.
- `.venv/Scripts/python.exe -m unittest tests.unit.test_nominal_structural_top tests.unit.test_nominal_support_cell` — 24 PASS.
- `.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*.py'` — 600 PASS.

Independent blind review: PASS for the bounded research query. It checked
union max, conservative full/partial/absent outcomes, bit/count preflights,
typed input/reason validation, cancellation and the unchanged existing support
API. The existing fixed `_segment_top_bounds` arithmetic has no internal
interrupt hook, as the validated specification states. A nominal top result
is not proof of actual extrusion or safe printing.
