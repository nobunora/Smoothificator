# Independent conditional preview annotation review — 2026-10-18

Disposition: no material findings in the reviewed comment-only helper and its closed conditional-copy integration. This review does not assert Orca binary rendering or physical-print approval.

Reviewed `tools/conditional_preview_annotations.py`, the optional annotation composition/write-time reconstruction portions of `tools/conditional_nominal_copy.py`, `tests/unit/test_conditional_preview_annotations.py`, directly relevant conditional-copy tests, and the optional annotation amendment in `docs/specs/conditional-whole-job-recipes-review.md`. Pinned `artifacts/orca-source/GCodeProcessor.cpp` confirms the cited reserved FEATURE/LAYER_HEIGHT/LINE_WIDTH and Z_HEIGHT handlers; source observations are not source/binary equivalence proof.

The bounded decimal formatter emits ordinary finite decimals, rejects nonterminating or over-budget dimensions, and never emits Fraction slash syntax. Prior recognized metadata must be known, valid and bounded; restoration values are not invented. Per-path physical height and command Z, explicit outer-wall role and per-segment frozen E-implied width are generated inside insertion spans. Resource limits reject excess events/comments/line bytes/precision. Default annotation policy is disabled. The writer reconstructs the entire copy with the same policy, rejecting stale or missing policy before publication. Existing source bytes and machine commands remain unchanged.

Executed `.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_preview_annotations tests.unit.test_conditional_nominal_copy -v`: **13 tests passed**, 0.559 seconds. This includes ordinary/default parity, thin-first metadata, exact restoration, malformed/unknown state, resource limits and stale-policy atomic writer rejection.

An independent inline read-only actual-copy audit used:

- `artifacts/conditional-whole-job-review/annotated-v3/whole-job.UNVERIFIED_VIEW_ONLY.gcode`, SHA256 `1054e411b3bd2576c3be0bda30330a3e2a24f00301c451a6e1a04d07df9c1484`.
- Its `annotated-copy.UNVERIFIED.json` insertion spans and current compact compiler groups from `artifacts/conditional-whole-job-review/compact-v2/whole-job-compilation.UNVERIFIED.json`.
- Original f917 source SHA256 `f917caf88191253f22004d47545daa4e6f78f4b4132d61529101271e4d3ba288`.
- Prior motion-only output SHA256 `5200cc727e0c534913044f415894fc7470cd4b5f9a55ee3435a879acfe3a619d`.

Stripping only the four generated recognized annotation tags inside each of the 12 insertion spans reproduces each prior motion-only block and the complete 5200cc output **exactly**. Strict modal replay from all actual saved anchor states restores every state. For **all 2,853 positive XY extrusions**, the audit independently derives actual width from emitted deposited E, actual segment length and the existing flow owner, then verifies exact metadata height, Z, width and role. All **12 prior four-tag metadata content states restore exactly**. A separate fixture with mixed LF/CRLF source metadata confirms exact original byte recovery, stripped-block parity and metadata restoration; generated line endings may follow the inserted block style while original source bytes remain intact.

Reviewed owner pins:

- `tools/conditional_preview_annotations.py`: `33fb85177360942ef30d1137ac8c64b97c4836dd4870042374fd6d529ba83a30`.
- `tools/conditional_nominal_copy.py`: `aa182a3d00fcb9c5b344c7814860462f6300be39c29e84063be8ebd5cdb65cf3`.

No production, tool or test files were edited during this independent review. Actual Orca standard-3D rendering remained unverified by this reviewer; the parent's subsequent UI inspection is separate evidence. This comment-only audit does not expand nominal material-model scope, solve unknown stationary deposition, authorize contact regions, or certify a physical head envelope.
