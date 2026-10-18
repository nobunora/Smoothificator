# Conditional whole-job compiler independent blind review

Date:2026-10-18. Independent read-only review of `compile_nominal_recipe.py`, `compile_conditional_job.py`, direct recipe/whole-job tests and actual pinned reproduction inputs. No parent primary conclusions consulted. Moving annotation modules excluded. No source/tests/baseline edits.

## CR-1 Medium — final displaced/cut graph does not receive complete simplicity validation

Location: `compile_nominal_recipe.py`, final edge/intersection loop after recipe construction.

The closed contour owner validates its original proposal, but subsequent vertex displacements are checked only for zero-length edges and intersections between nonadjacent edges. Adjacent backtracking, zero closed area and orientation are not checked after changes. Independent genuine triangular contour `(0,0),(1,0),(0,1)` with displacement of vertex2 by `(.5,-1)` compiles to closed `(0,0)→(1,0)→(.5,0)→(0,0)`, with positive E for all3 edges despite zero area and overlapping adjacent edges. A public ExplicitPatchRecipe `(0,0)→(1,0)→(0,0)` also compiles with full backtracking.

Invariant: approved source-contour/recipe contract requires exact final nonzero/simple graph validation after displacement/cuts, before final freezing. A valid closed reference does not validate a changed final path. Such input can become a purported compiled recipe with geometry that fails the construction contract, even though later geometry selection remains false.

Remediation: validate adjacent overlap/reversal for open and closed paths; closed paths require nonzero signed area and the required orientation after modification. Restrict explicit patches to their approved finite-segment scope or validate their full open graph. Reuse the authoritative geometric checks rather than another incomplete test. Confidence high; disposition confirmed, pending remediation.

## CR-2 Medium — fractional source identities are silently truncated

Location: `compile_conditional_job.py`, source-contour old/current source-line decoding and other integer-reference conversions.

`int(i)` accepts fractional JSON numbers and silently changes their meaning. Independent actual experiment changed the floor3.4 first contour references from old10486/current9605 to JSON10486.9/current9605.9, then regenerated manifest and coverage identity. Compiler accepted all28 paths after truncating both references. Output is identical to the actual baseline SHA `5200cc727e0c534913044f415894fc7470cd4b5f9a55ee3435a879acfe3a619d`, confirming this is schema reinterpretation rather than a rejected malformed reference.

Invariant: exact source provenance/schema references must name actual integer lines; a source line10486.9 does not exist and must not be treated as10486. Applying the same lossy coercion to both sides of a mapping does not establish that the declared IDs agree. Similar boolean/fractional integer-role fields should be audited together.

Remediation: validate exact integer category/canonical integer-string grammar and range before conversion; reject bool, nonintegral numbers and noncanonical numeric coercion. Validate all current/original line IDs, detour IDs, patch witnesses, edge indices and count fields consistently. Confidence high; disposition confirmed, pending remediation.

## CR-3 Low — direct recipe API omits common upper-interval validation

Location: `compile_nominal_recipe.py`, common dimension admission before recipe branches.

Circle recipe with floor3, top3.08 and `upper_z_mm=3.01` is accepted and returned with its declared upper below the path. Contour construction rejects this interval through its existing owner, but circle/patch/pinned recipes lack a common floor/upper/top check. The whole-job copy composer rejects an emitted top above upper later, limiting the observed impact to an inconsistent public recipe proposal API.

Remediation: require exact ordered `floor < upper` and `floor < top <= upper` for every recipe before construction, rather than depending on one branch/downstream compositor. Confidence high; disposition confirmed, pending remediation.

## Checks and actual negative coverage

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_compile_nominal_recipe tests.unit.test_conditional_whole_job -v` — PASS,7 tests,149.581 seconds, Python3.12.10. No test edits.

Actual reproduction/test covers all16 original targets (12 groups/four explicit exclusions),28 unique emitted paths,2853 segments, exact regenerated reference XYZ/E/width parity, source byte recovery and false print flags. The independent CR-2 actual run additionally composes the entire job and matches existing compact-v2 output bytes exactly without overwrite. Its altered recipe is intentionally malformed and should reject; matching geometry does not excuse incorrect schema acceptance.

Reviewed source-bound model replay/reassociation reconstruction and forged DTO rejection; embedded actual source/project policy and all-floor feed cap; current M624 scoped anchors after lower floor and before immediate upper source geometry; authoritative ring-factory rebuilding from pinned original source/project/manifest; explicit legal emitted IDs; contiguous open arc cuts without reconnection; protected detour/coalescing ownership; regenerated E/F rather than copied reference emissions; complete target geometry/exclusion comparisons; manifest/coverage/reference/owner digest checks; group/path/segment and construction budgets; cancellation exact bool; source state restoration through existing conditional compositor. Existing rejection tests pass for missing groups, duplicate IDs, unknown family, wrong triangle, stale content, forged current model and wrong bijection.

No additional material defect established in these bounded checks. The three confirmed cases expose missing negative admission checks despite passing fixtures, not failure of the actual pinned2853-segment reproduction.

## Limits and next step

Compiled state is explicitly `compiled-UNVERIFIED-no-geometry-selection`; full cropped-source contact, spill/quality/material/tool chronology and actual preview metadata are pending separately. This review does not transfer research acceptance or certify whole-job nominal selection, physical startup/suffix, head geometry, support calibration, runtime injection or printing. Resolve confirmed findings through implementation and independently reverify; source-copy parity alone is not convergence.

## CR-1/2/3 correction verification

Independently reviewed frozen corrections and reran original counterexamples: displaced zero-area triangle, patch backtracking and top3.08 above upper3.01 now reject. Final graph is XYZ-quantized before zero-length, adjacent reversal/overlap, nonzero closed area, orientation and nonadjacent-intersection checks. Circle values receive bit/finite checks before float construction. Strict canonical source-line parsing rejects10486.9/9605.9, bool, decimal/exponent/signed/leading-zero string variants; exact count/index parsing rejects bool/float/Fraction/string categories. Actual source and count decoding use these validators rather than lossy int casts.

Parent-added original-target pin check was independently inspected: only manifest-declared validated bytes enter the digest authority map; an extra caller-supplied shortened target corpus cannot replace the original corpus even with a matching new coverage hash. The new rejection test passes. Removed arc IDs and selected ring endpoint indices are also checked against fresh construction provenance.

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_compile_nominal_recipe tests.unit.test_conditional_whole_job -v` — PASS,9 tests,145.232 seconds, Python3.12.10. Includes all16 target/28 path/2853 reference parity, original-byte recovery and malformed/stale/forged target/model/bijection failures. Additional direct original counterexamples and strict ID/count-category probes pass. A fresh complete fixed-compiler invocation independently matches exact compact-v2 bytes and output SHA `5200cc727e0c534913044f415894fc7470cd4b5f9a55ee3435a879acfe3a619d`.

Final CR-1, CR-2 and CR-3 dispositions: **confirmed / fixed / independently verified**. No new material compiler defect established in this bounded correction. Stationary-material AG-1 and later chronology/preview/geometry gates remain separate; no physical authority changed.
