# Adaptive nominal support coverage

Prerequisite: SPEC_VALIDATED phase1a-support-controller.md, ADR-0058,
and canonical manifest imported separately at f1acf32 before implementation.

## Change and intent

The frozen support coverage DTOs and controller integrate actual nominal-bead
cell queries over a constant-width, constant-Z straight candidate. Rational
local partitions map through outward-rounded world bounds. Only unresolved
leaves are subdivided; proven leaves are retained. A cumulative query budget
is checked before allocation, and cancellation returns the last completed
snapshot. Two stable completed passes and zero unresolved area are required
before a supported/rejected conclusion. Unknown coverage never grants support.

The internal support_width module computes the minimum longest connected
lateral union using a compressed interval tree and batched longitudinal events.
Disconnected support widths are not added together. This avoids a quadratic
rescan of every rectangle for each slab. No dependency or canonical identity
registration was added; these results do not grant Plan injection authority.

Changed production files: domain/support_coverage.py,
engine/support_coverage.py, engine/support_width.py. Their two focused test
modules, Windows handoff gate and clean archive import check accompany them.

## Verification

Windows isolated Python 3.12.10; all commands below exited 0:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- `.venv/Scripts/python -m unittest tests.unit.test_support_coverage -v`: 17 PASS.
- Width specialist suite: 11 PASS, including 80 seeded arrangements checked
  against an independent exact union oracle.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 404 PASS.

Independent controller review found no actionable findings. The reviewer also
checked 300 seeded arbitrary-rotation corner bounds against 100-digit Decimal
calculations, preserved proof/query counts, early resource rejection and
cancellation. Numeric falsification supplements the conservative construction;
it is not proof of physical support. Lint/type tools remain NOT CONFIGURED.

Fixtures cover full support, seams, narrow gaps, equal-area disconnected
support, rotation/reversal, higher obstruction, empty support, cumulative
budgets, minimum cell size, extreme refinement factors, subnormal/overflow
coordinates, source chronology and interruption during a refinement pass.

## Boundaries and next work

General union coverage may stay unresolved, especially on closed boundaries or
conservative rotated world enclosures. Minimum cell size/resource exhaustion
does not authorize a successful result. Source normalization and chronology
still require a real adapter. Mesh/error/optimizer, Orca snapshot/preview and
safe G-code output remain unfinished. The archive remains non-installable
research code. No physical printing, G-code mutation or security change occurred.

No desktop capture or input was used in this implementation pass. The persistent
control kernel was reset on request; disappearance of the OS/app control
indicator was not verified. Control should be connected only when needed for
an actual GUI check.

The next useful implementation step is the remaining geometry contract and
fixtures needed to connect this controller to candidate paths. No user decision
is currently required. Build/manifest and exact-head CI receipts are recorded
in the existing Draft PRs after committing this milestone.
