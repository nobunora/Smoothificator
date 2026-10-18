# Exact planned-path numerical regularity

Validated ADR-0063 adoption 1e71beb and phase1c-path-regularity.md were imported at
032be96 before implementation. domain/path_regularity.py defines the closed
diagnostic result; engine/path_regularity.py evaluates the immutable planned path.
Existing path/policy DTO construction, serialization and v1 hashes are unchanged.

The engine normalizes operands to binary64 then exact Fraction. Squared length
must strictly exceed the plan minimum; squared length must be at least squared
speed times minimum duration. No rounded square root is used. After all segments
pass those checks, adjacent pairs are checked in commanded volumetric rate,
width and effective-height order. Limits are inclusive. The first failure carries
its exact segment index or consecutive index pair. There is no cyclic last/first
comparison, mutation, repair or physical-evidence inference.

Cancellation is checked before the segment budget, during both passes and before
every expected return. Cancellation supersedes failure indices; no partial success
escapes. Work/storage are bounded by the explicit segment count limit.

## Verification

Isolated Windows Python 3.12.10; established code-quality gate order:

- `.venv/Scripts/python -m compileall -q adaptive_subedge tools tests`: PASS.
- `.venv/Scripts/python -m unittest discover -s tests/architecture -p 'test_*.py' -q`: 41 PASS.
- Independent `.venv/Scripts/python -m unittest tests.unit.test_path_regularity -v`: 13 PASS.
- `.venv/Scripts/python -m unittest discover -s tests -p 'test_*.py' -q`: 516 PASS.
- `.venv/Scripts/python tools/check_canonical_manifest.py --handoff docs/specs/phase1c-path-regularity.md`: 83 canonical Git blobs PASS.
- Independent source/proof review: no actionable findings. Review did not repeat
  the test owner's behavioral work.
- Research archive clean-extraction imports include path_regularity. Same-commit
  build hash and exact-head Windows CI receipts are recorded in Draft PR #8.
- Lint/type analyzers remain NOT CONFIGURED; no new dependencies.

Independent fixtures distinguish exact comparisons from rounded products/square
roots, cover threshold equality and adjacent binary64 values, overflowing float
differences/products and underflowing subnormal squares, two-pass precedence,
all observed cancellation checkpoints including failure returns, and immutable
result/identity exclusion.

## Limits

Regular means only these numerical checks passed. It does not prove path
openness, seam correctness, bead bounds/flow consistency, material containment,
support, improvement, calibrated machine behavior or final quantized G-code.
Physical fixture references are not validated by this evaluator.

Exposed-band reconstruction, finite-bead support/error scoring, optimization,
actual Orca snapshots/preview and validated atomic output remain unfinished.
No desktop capture/control, printer operation, G-code mutation, security changes,
merge/release or deletion outside C:. Untracked log_iotc.txt remains untouched.
