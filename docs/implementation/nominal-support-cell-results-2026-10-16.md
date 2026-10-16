# Actual nominal-bead support cell query

Prerequisite: independently validated phase1a-support-cell.md and its pinned
ADR-0044/0048 contract, imported separately at f05bcb8. Initial support draft
ambiguities were resolved before production edits: vertical eligibility uses
the existing effective-height limits, and source tops follow explicit stadium
cross-sections with flat axial caps and a linear normalized structural Z locus.

## Implementation

- domain/support_cell.py: four exact frozen/slotted input, policy and result
  types, with explicit chronology-related source constraints and signed rational
  bounds. No canonical identity registry or planning Settings changed.
- engine/support_cell.py: exact binary64-to-rational projection, whole-cell
  footprint bounds, outward square-root enclosures, and maximum-over-source top
  bounds. Any possible higher partial overlap contributes to the upper envelope.
- tests/unit/test_nominal_support_cell.py: independent analytic fixtures and
  malformed/extreme/resource/chronology regression cases.
- Windows CI checks the handoff; the research package builder now verifies the
  new engine module can import from a clean extracted archive.

No point-sampling test is used to grant support in production. A source fully
covering the cell supplies a lower top bound; all possible sources contribute
upper top bounds. Cells relying only on a union of partial sources stay
unresolved. Source-count exhaustion returns unresolved before source scanning;
no precision/resource default or physical threshold was introduced.

## Verification

Windows isolated Python 3.12.10:

- Syntax/import compilation PASS; architecture 41 tests PASS.
- Independent focused suite: 17 tests PASS.
- Full regression: 376 tests PASS.
- Canonical handoff integrity: 83 Git blobs PASS.
- Independent implementation review: no actionable findings.
- Reviewer falsification: 400 seeded random queries / 10,000 sampled points,
  checked against a separate 140-digit Decimal analytic top evaluation, PASS.
  Reproduction script: artifacts/verify_support_cell_decimal.py (local ignored
  evidence). This supplements exact interval reasoning, not a proof by sampling.
- Lint/type analyzers: NOT CONFIGURED. No third-party dependency added.

Analytic fixtures include rotated/reversed segments, curved sides, circular
sections, sloped ZAA loci, closed flat caps, partial higher obstructions, seam
partitioning, subnormal and extreme coordinates, exact radical enclosures,
resource precedence and unchanged canonical identity boundaries.

## Remaining work

This supplies actual nominal geometry to a later adaptive support controller.
It does not complete adaptive convergence, area/contiguous-width integration,
general union coverage, spatial acceleration, mesh/Orca snapshots, optimizer,
preview, G-code output or physical calibration. The source adapter must still
prove normalized coordinates and chronological ownership. Query-supported means
local mathematical vertical eligibility only, never an injectable Plan.

Build/exact-head CI receipts are recorded on the existing Draft PRs after the
implementation commit. No security setting, printer operation or file outside
C: was changed or deleted by this work.
