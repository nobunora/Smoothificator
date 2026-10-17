# Phase 1A nominal bead arithmetic

Reviewed contract: docs/specs/phase1a-bead-flow.md. Static Phase 0.5 prerequisites
passed at bc251a3, including Windows CI 38847445561 and 38847441203. The
implementation specialist added flow_model.py and 13 focused tests; the lead
independently read all production/test changes against the handoff and found no
actionable discrepancy. No dependency or canonical specification changed.

The five functions compute candidate stadium area, inverse width, local ZAA
height/volume/width, effective height above declared support, and external-role
commanded volume. Input types and bounds are explicit. Invalid or nonfinite
arithmetic rejects with typed failures. Global flow ratios do not resize nominal
geometry. No physical defaults or numerical clipping were added.

Verification on Windows Python 3.12.10:

- Syntax/import compilation: PASS.
- Architecture: 41 tests PASS.
- Focused arithmetic: 13 tests PASS, including independent area formulas,
  numeric extremes, boundary rejection, ZAA and flow separation.
- Full regression: 359 tests PASS.
- Lint/type: NOT CONFIGURED.

This is the arithmetic subset of Phase 1A. It is not a solid union, support
query, error estimator, optimizer or complete engine. No real Orca snapshot,
improved preview, G-code modification or physical output was performed here.
The separately drafted support design still needs canonical adjudication and
implementation review before any support acceptance path is added.
