# Continuous path contact — independent blind review, 2026-10-18

## Independence and result

Reviewed docs/specs/continuous-path-contact-review.md, tools/audit_continuous_path_contact.py, tests/unit/test_continuous_path_contact.py, and the actual exact-kernel/domain contracts in adaptive_subedge/{engine,domain}/support_cell.py. Did not read parent or implementation conclusions for this stage. No code/test edits, source mutation, slicing, printer access or subagents. Only this report was written.

No actionable material defect identified in the bounded continuous nominal centerline-bottom audit. This is a negative review with explicit coverage below, not physical contact or print approval.

## Proof path and invariants traced

The candidate has immutable exact Fraction XY points and one exact bottom plane. Policy validates positive rational grid/padding, exact bounded maximum depth and explicit positive resource limits. Exact source type/order and unique identities/orders are checked; candidate XY must lie on the declared grid. Source admission is strictly execution_order < candidate.execution_order, with same-order/future sources excluded independently of Z.

Each original segment begins as [0,1]. Every unresolved split bisects its exact rational parameter interval, creates both children and retains their original segment index. The padded closed box contains every point on that nonempty segment piece, including axis-aligned paths. Bounds come directly from query_exact_nominal_top_cell on that box and all admitted sources. A kernel full-cell lower bound >= bottom implies the centerline property for the entire piece; absent support or upper < bottom similarly proves a gap for the entire piece. It never queries child regions of the box to locate a gap and never treats off-line box absence as an on-line witness. Ambiguous box coverage is bisected only along the original line parameters.

Kernel review confirms that full lower bounds require a covering source for the complete cell, absent requires no intersecting source, and upper bounds include all intersecting sources. Incomplete/cancelled/resource-limited results contain no bounds and are checked before geometric admission. Thus an incomplete kernel result cannot create a support or gap certificate. The kernel's conservative union coverage can leave genuine contact unresolved but does not justify accepting it.

All returned leaves are sorted and checked for exact contiguous [0,1] coverage of every original segment, no holes, zero intervals or silently missing original segments. A positive point sample is never sufficient. Gaps may coexist with unresolved leaves and refute complete contact; the report retains both rather than calling the entire audit complete. No-gap unresolved reports stay incomplete. Only all-supported leaf coverage sets nominal_centerline_contact_proven.

## Failure, cancellation and bounds

Input/source/path limits, query budget, kernel coordinate/source bounds, maxdepth and cancellation produce unresolved intervals covering all affected pending pieces. Cancellation is latched and exact-bool checked; once observed it cannot later revert. A query cancelled during kernel evaluation cannot publish geometry as a new proof. Existing proven gap leaves are retained alongside the cancelled/resource-limited remainder as required. Duplicate IDs/orders, mutable inputs, invalid grid/precision/policy, zero segments and malformed callback return values reject.

Limits bound the audit queries/subdivision and kernel work. Validation/initial pending allocation still scale with supplied input size; this is not a hard process-memory sandbox against adversarially allocated Python objects. That is outside the pure-function resource contract and does not grant physical authority.

## Executed evidence

Exact repository Python3.12.10, previously verified in this independent session.

`.\.venv\Scripts\python.exe -m unittest tests.unit.test_continuous_path_contact -v` → exit0, all10 tests pass (0.034 seconds). Real exact kernel is used for geometric cases, not mocked result certificates. Coverage includes axis/oblique paths, exact touching top, multi-segment partition, supported endpoints with interior gap, earlier/same/future chronology, boundary uncertainty, all explicit resource modes, cancellation before/during kernel, mixed gap/unresolved results and malformed inputs.

Additional read-only `@' ... '@ | .\.venv\Scripts\python.exe -` → exit0. Independently exercised five line slopes (horizontal, vertical, both diagonals, shallow slope), each forward/reversed, with collinear covering nominal sources: all ten proved complete contact, zero gap leaves, exact contiguous parameter partitions. Also checked strict whole-piece upper-below-bottom gap in one query and kernel source-cap exhaustion remaining incomplete despite a sufficient individual source. No source/test/artifact was changed.

## Residuals and authority

The proven property is exactly the handoff's top-bound criterion along the nominal centerline bottom, with penetration permitted. It is not full bead footprint/contact-area support, firmware execution, deformation, underside/solid intersection validation, head clearance, downstream safety or printable compatibility. Fixed padding can preserve uncertainty indefinitely at a support boundary; this is conservative and explicitly tested. No real-source adapter or candidate source provenance is established by this pure function: callers must supply immutable exact segments and truthful execution orders, and physical source association remains a separate gate. No CLI/restoration/parser behavior changed.

Both authority flags are init=False false; reports and nested inputs are immutable. No physical enablement or production convergence is declared. Parent owns architecture/full-suite gates beyond this focused independent check. No finding requires disposition.
