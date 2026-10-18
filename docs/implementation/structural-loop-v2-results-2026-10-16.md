# Standalone structural loop v2 results

Implemented the thirteen-field standalone reference from ADR-0067 and the
SPEC_VALIDATED phase05-structural-loop.md handoff (spec commit f09a785).
The schema specialist authored the closed contract; the implementation lead
reviewed it before source changes. A separate implementation review then checked
the resulting source against that contract and independently ran all 8 focused
tests: PASS, no actionable finding.

Checks include implicit closure, duplicate rejection after binary64 conversion,
exact point-extrema bounds, anchor containment and noncollinearity. Fraction from
the standard library supplies exact rational subtraction/products after conversion
to binary64, avoiding underflow and overflow in the predicate. This detects only
affine noncollinearity; almost-collinear values do not prove matcher conditioning.
Caller-declared winding, material policy, length and shape digest do not become
verified geometric facts. No new third-party dependency or canonical registration.

Windows Python 3.12.10 verification:
- Initial compile found a missing closing parenthesis; corrected immediately.
- Repeated compile and 41 architecture tests: PASS.
- Focused 8 tests: PASS, including subnormal/extreme/3D coordinates.
- Full suite: 313 PASS, including v1 identity vectors.
- Canonical integrity: 83 blobs PASS for the new handoff.
- git diff --check: PASS (existing LF/CRLF notices only).
- Lint/type tools remain NOT CONFIGURED, not PASS.

Source changes: domain/structural_loop_v2.py and focused tests. CI checks the new
handoff. No engine, Orca, G-code, printer, security setting or external deletion
changed. Reverting the standalone DTO/tests needs no persisted migration.

Remaining proof obligations and full implementation sequence are recorded in
completion-plan-2026-10-16-ja.md. This does not complete Phase 0.5 or a plugin.
