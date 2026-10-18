# Two-tier copy/material independent blind review — 2026-10-18

Initial disposition: **one Medium copy resource-budget finding, TTC-1**. No parent copy/material findings were provided before this report. Actual fixture evidence remains a separate review; the earlier CURRENT job audit was not repeated. No reusable source/test edits, original artifact mutation or printer operation.

Authority: `docs/specs/two-tier-supplemental-review.md` and its repository review/canonical references, including explicit opaque terminal positive-material obligations. Reviewed full frozen copy/material owners, direct tests and targeted existing source association/anchor, numeric cycle, annotation and exact overlap owners.

Frozen `copy-material-freeze-v2.json` hashes: copy `9f53fbf0b97d7ee10b8ad854af60c7548b00ef7620746da4f65f8adba5d6201e`, material `a6ebf5c38aa9cd18b680f54f44c9a4ae7ec102054346cb0bcb6f626487318dfa`, tests `a659de77ecc11987bafa914c9f53c5c41b4fadfe4a50bf79938ff05c6c7d06cf` / `e2521a226134597ce2d3d1167159babf3c5972df11634af8eda0fcbcd4b8a413`. Both pure-v2 and copy/material manifests were checked against actual file hashes around review.

## TTC-1 — Medium — LF count does not bound admitted source events

Location: `tools/compose_two_tier_copy.py`, initial `source.count(b'\n') > copy_policy.max_source_events` admission check before body interpretation.

The interpreter uses `splitlines(keepends=True)` and accepts CR-terminated internal comments. Counting LF bytes is therefore not a bound on admitted parsed events. There is no actual trace-event count check afterward. A source can exceed the explicit policy and still produce a successful supported copy.

Independently executed counterexample: start with the direct copy test fixture; insert1000 `b'; budget event\r'` comments at its body start, preserving original LF body boundaries. Freshly rebuild embedded source/project/descriptor pins, shifted body/anchor bounds, motion identities, interpreted context, frozen graph, shifted actual root witness lines, source associations and anchor. With `max_source_events=source.count(b'\n')=75`, the compositor succeeds although the actual typed body contains1021 events. Source size is16712 bytes, below its separate byte cap. No original file was changed. This is an admitted mixed-line source, not the rejected all-CR body-boundary case.

Invariant: finite event limits must apply to the same source/event grammar that is interpreted. The byte limit provides a separate bound but does not honor this caller's75-event work limit. Severity Medium for offline resource/policy failure; no physical authority exists.

Remediation direction: count the actual supported line/event grammar before expensive replay, or explicitly reject unsupported terminators, and verify actual typed-event count against the declared policy. Keep original bytes intact. Add a mixed-terminator regression that proves rejection before unbounded interpretation work, not just a normal LF fixture. Confidence high. Initial disposition pending parent reconciliation.

## Checks and negative coverage

Command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_two_tier_sections tests.unit.test_two_tier_intents tests.unit.test_two_tier_copy tests.unit.test_two_tier_material -v` — PASS,16 tests,10.007 seconds, Python3.12.10. Includes7 directly new copy/material tests, plus the corrected9 pure tests. TTR-1 verified disposition is appended to the separate pure report.

Source/profile/producer/body inputs are freshly interpreted; original-floor root associations are freshly reconstructed and require actual earlier positive-E external-wall witnesses. Saved profile-owned policy fields and source-floor speed caps are checked, as is the90% saved layer-height cap despite permissive caller bounds. Raised children bind actual parent frozen identities, not fabricated source walls at the raised plane. Original next-layer plane must match the first actual future material plane after the insertion. Existing markers, duplicate paths, foreign context, stale/forged root/plan identities and malformed bounds fail closed in the examined routes.

The graph is rebuilt before formatting; frozen E/F are replay-compared. Existing one-path retracted cycles restore source XYZ/feed/logicalE/debt/modal state, and optional annotation restores prior recognized metadata around each path. Insertion spans preserve all other source bytes. Writer re-reads inputs and recomposes the entire immutable receipt, refuses overwrite/alias/stale/forged results and publishes a verified temporary file through an atomic no-replace hard link, cleaning its own temporary file on failure. No physical flags turn true.

Material audit rebuilds the graph/slabs rather than trusting a caller's slab object. Every unordered candidate pair is accounted once. Only exact declared immediate-parent pairs inherit their checked vertical support slab; all others use the exact nominal overlap owner. A genuine unrelated positive-volume intersection fails, separated unrelated pairs pass, and exhausted pair/query/cancellation budgets cannot claim completeness. This is candidate-pair material scope, not original-material, tool sweep, full-footprint support or opaque execution proof.

No second material defect established within this initial bounded copy/material review. Actual source mapping, actual emitted contact/spill/future/causal tip certificates, low-Z travels, complete source byte/preview evidence and legacy full-copy parity remain separate integration gates. Positive original material in an opaque suffix remains unresolved; whole-original-job completeness is fixed false. Physical/runtime/print authority remains false.

## TTC-1 correction independently verified

Parent confirmed TTC-1 after the initial report. Frozen v3 copy SHA `ee0e9c9f95b1a0ad2c960b9fd8d3847d1f0f472dc6c5b94d6d5d92733c9d9c0d`; direct copy tests `74b606117571f92e5539d72960e06b57a5c846df98dc9640e48d576477179763`. Material owner/tests unchanged. Admission now counts `source.splitlines()` before body parsing and additionally checks actual `len(trace.events)` afterward.

Command `.\.venv\Scripts\python.exe -m unittest tests.unit.test_two_tier_copy tests.unit.test_two_tier_material -v` — PASS,8 tests,.518 seconds, Python3.12.10. The added regression mocks the interpreter to require preparse rejection, then supplies the true grammar-aware line budget and verifies exact source recovery.

Independent additional probe uses the original1000 `; budget event\r` padding: actual1021 body events versus75 LF bytes. A patched interpreter that would raise if entered is not reached; the75-event copy rejects with the event-budget error. Raising the limit to the actual split-line count accepts, and deleting insertion spans recovers exact original source bytes. All four v3 file hashes match the frozen manifest afterward. Disposition: **confirmed, fixed and independently verified**. No further material defect established in this delta. Actual fixture/geometry/tool/preview gates remain separate and physical authority remains false.
