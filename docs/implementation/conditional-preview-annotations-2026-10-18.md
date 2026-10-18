# Conditional standard-preview annotations

Implemented the parent/independently validated optional annotation amendment in
`docs/specs/conditional-whole-job-recipes-review.md`. Owning module:
`tools/conditional_preview_annotations.py`; integration is opt-in keyword
`annotation_policy` on conditional compose/write only. Strict synthetic APIs and
default motion bytes remain unchanged. No machine command is added or modified.

Immutable `ConditionalPreviewAnnotationPolicy` declares metadata event/comment,
decimal-place and metadata-line-byte budgets. The owner reconstructs the last
recognized LAYER_HEIGHT/LINE_WIDTH/Z_HEIGHT/FEATURE comments before the actual
anchor. Unknown/malformed prior required state rejects; raw prior lexical comment
content is restored in local newline format before returning to original source.
Only fixed known tags/role and validated bounded nonnegative decimal numbers are
generated. No arbitrary caller comment text or Fraction slash formatting.

Each sorted path gets physical height, actual command top and external-wall role;
every positive XY/E segment gets its actual frozen E-implied width. Frozen E/path
coverage is checked. Tracked generated-line stripping must recover the exact
motion-only block. Full policy/prior/frozen-emission provenance participates in
identity. Atomic writing replays annotation construction from pinned originals;
omitting/changing policy cannot publish a previously annotated receipt.

Actual full28-path output under
`artifacts/conditional-whole-job-review/annotated-v3/` has SHA256
`1054e411b3bd2576c3be0bda30330a3e2a24f00301c451a6e1a04d07df9c1484`,
769447 bytes/12 cycles. Its per-span recognized-comment stripping recovers
motion-only SHA256 `5200cc727e0c534913044f415894fc7470cd4b5f9a55ee3435a879acfe3a619d`.
Original f917 source bytes, commands/E/F/XYZ and nominal state are unchanged.
The first attempted process had loaded the earlier comment-parser bug and
rejected before writing output; comment/blank handling was corrected and focused
tests passed before the successful actual rerun.

Parent audited actual source bytes/state/tag restoration and independently
verified all2853 annotations. Parent also loaded the actual file in installed
Orca; the standard height legend showed0.08..0.18 supplemental versus original0.2,
with curved-top bands visible. Native screenshots `orca-height-close.png` and
`front-large.png` are retained under annotated-v3. Audited Orca source tag support
and native preview do not establish firmware execution, contact or physical head
clearance. All physical/runtime/print authority remains false;27 stationary
source surplus events separately prevent whole actual-material completion.

Changed tests: `tests/unit/test_conditional_preview_annotations.py` verifies
thin-first different heights/tops, per-segment widths, decimal grammar, exact
restore, mixed LF/CRLF, unknown/malformed metadata, resource rejection, no-replace
writing and rebuild-policy identity. Required Python3.12.10 commands:

- `.\.venv\Scripts\python.exe -m py_compile tools/conditional_preview_annotations.py tools/conditional_nominal_copy.py`:PASS,exit0.
- `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_preview_annotations tests.unit.test_conditional_nominal_copy -q`:13PASS,1.140s,exit0.
- Combined annotation/copy/actual/strict-copy/hop regression:41PASS,30.906s,exit0.
- `.\.venv\Scripts\python.exe artifacts/conditional-whole-job-review/annotate_actual.py`:PASS,exit0.

Parent independent review passed13 focused tests and actual metadata probes.
No source/parser/profile/production changes, printer operations, dependency or
publication. Previous artifacts and unrelated dirty work remain preserved.
