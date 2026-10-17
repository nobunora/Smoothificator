# Exact nominal bead top kernel: implementation result

Disposition: bounded research primitive PASS; candidate width/Z provenance,
surface improvement and printability remain unproved.

Authority: `docs/specs/exact-nominal-bead-top-kernel-draft.md` at spec commit
`1fa45a8` (`SPEC_VALIDATED`), accepted ADR-0043/0048. Independent read-only
repository review against MAIN `dbea325` returned `validated` for the
shared support-cell owner and explicitly parameterized chord adapter.

The existing `support_cell` stadium-top arithmetic now has one exact Fraction
kernel. The old binary64 `_segment_top_bounds` path remains a normalization
wrapper, preserving the existing support and structural-top results. New
frozen DTOs and point/rectangle queries accept exact rational structural or
candidate segments with explicit width/height/Z, bounded coordinate bits,
source count and square-root precision. A proposed `ChordProposal` transfers
its exact XY endpoints without a float round trip. This adapter does not prove
that caller-supplied width/Z match the original proposal's settings.

Independent blind implementation review found no material defect. Extra
regression assertions cover duplicate IDs, bit overflow for point/source/cell,
and direct old/new sloped-source helper parity. No Plan, Settings, Orca,
G-code, printer or unrelated log file was changed.

Windows Python 3.12.10 validation:

- `-m compileall -q adaptive_subedge tests tools`: PASS.
- Architecture/import-boundary suite: 43 PASS.
- Exact nominal top plus existing support/structural top focused modules:
  32 PASS.
- Full `unittest discover -s tests -p test_*.py -q`: 608 PASS.
- Canonical manifest integrity at implementation commit `89191c6`: 85 Git
  blobs PASS (integrity only, not spec approval).
- `tools/build_validation_artifacts.py`: PASS, exact-head research ZIP SHA-256
  `d2f470175e8da98f4daba90e23b669a4b57e8cfc686cc78ca528a53574d19d98`;
  isolated extracted source import PASS. The ZIP is non-installable.
- `tools/build_preview_plugin.py --output-dir artifacts/package-check`:
  PASS, check wheel SHA-256
  `57cf00019fb9dba66e5883c486b8384f50ced3cc748ae9a0ec7920f4a1d7e081`;
  isolated `python -I` import of the new query PASS. This wheel was not
  installed or runtime-tested inside Orca.
- Lint/type analyzers: NOT CONFIGURED; no dependency added.

The next research unit may compare the same fully covered planar rectangle's
nominal baseline and augmented top-residual intervals, but cannot claim
ADR-0047 bidirectional surface error, ADR-0060 affected-domain closure,
actual Orca slice provenance or safe G-code output.
