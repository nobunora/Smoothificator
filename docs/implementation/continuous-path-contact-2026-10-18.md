# Continuous nominal centerline contact audit

Contract: `docs/specs/continuous-path-contact-review.md`; parent repository
disposition validated for this tools-only pure function and focused tests.
No production parser, support kernel, geometry intent or source file changed.

## Changes and proof boundary

- `tools/audit_continuous_path_contact.py`: frozen chronological source/path,
  explicit finite audit policy, interval witnesses and report. Exact rational
  candidate XY must lie on the declared grid. Source identities and execution
  orders are explicit/unique. Only source orders strictly before candidate order
  participate, regardless of layer Z; same-order/future segments are excluded.
- Each original path segment is partitioned in rational parameter space.
  Positive rational padding gives its conservative closed XY box positive
  extents. Existing `query_exact_nominal_top_cell` bounds the complete box. Full
  lower bound >= bottom proves nominal contact for that entire parameter piece;
  absent support or strict upper bound < bottom proves a whole-piece gap.
  Otherwise bisect the original segment parameter interval. No off-line child
  box can become a false path gap witness.
- Reports retain every leaf interval, source/query/leaf counts and all explicit
  limits. Exact partition assertions ensure [0,1] coverage with no holes for
  every original segment, including unresolved leaves. Proven gaps coexist with
  unresolved counts instead of discarding uncertainty. Query/depth/input/kernel
  resource limits and latched cancellation never establish complete contact.
- `tests/unit/test_continuous_path_contact.py`: ten tests use the real exact
  support kernel for axis-aligned and oblique supported paths, multi-segment
  coverage, supported endpoints with an interior gap, exact top touching, a
  side-boundary case requiring unresolved, chronology exclusion, query/depth/
  input/kernel limits, cancellation, gap plus unresolved remainder, and invalid
  identifiers/orders/types/grid/policy. No sample-only acceptance or kernel mock.

Rejected alternatives: layer-height filtering as chronology; positive point
samples as a continuous certificate; subdividing enclosing boxes instead of
line parameters; replacing the geometry kernel; promoting nominal centerline
results into footprint, physical contact or tool clearance authority.

## Commands and results

All commands use project `C:\VSC\Smoothificator\.venv\Scripts\python.exe`;
`& .\.venv\Scripts\python.exe --version` -> Python 3.12.10, exit 0.

1. `& .\.venv\Scripts\python.exe -m py_compile tools/audit_continuous_path_contact.py tests/unit/test_continuous_path_contact.py`
   -> PASS, exit 0.
2. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_continuous_path_contact -q`
   -> PASS, 10 tests, exit 0.
3. `& .\.venv\Scripts\python.exe -m unittest tests.unit.test_continuous_path_contact tests.unit.test_top_contact_cells -q`
   -> PASS, 15 tests, exit 0.

Parent requested focused checks/syntax only while revisions settle; no full
regression or package build run for this step. No new dependencies, printer
connection, printing, commit, push, merge or release. Existing dirty work,
restored baseline, ring intent and unrelated `log_iotc.txt` were preserved.

## Limits and next step

Ready for parent source/test audit and independent review. Pure DTO input has no
source parser, firmware inference or automatic real-source chronology adapter.
Certificates concern a constant nominal centerline-bottom plane and allow
penetration; they do not establish full bead footprint/contact area, deformation,
head envelope, downstream collision or physical printability. Padding can cause
conservative unresolved outcomes at exact support edges. Every report has false
physical-print authority, including successful nominal-contact reports.
