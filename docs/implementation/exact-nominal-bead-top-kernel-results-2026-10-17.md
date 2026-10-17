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
- Lint/type analyzers: NOT CONFIGURED; no dependency added.

Exact-head package and CI results are recorded separately after commit.
The next research unit may compare the same fully covered planar rectangle's
nominal baseline and augmented top-residual intervals, but cannot claim
ADR-0047 bidirectional surface error, ADR-0060 affected-domain closure,
actual Orca slice provenance or safe G-code output.
