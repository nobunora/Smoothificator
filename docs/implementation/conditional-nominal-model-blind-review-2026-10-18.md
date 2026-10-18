# Conditional nominal model independent blind review

Date:2026-10-18. Read-only review of `tools/conditional_nominal_model.py` and direct tests against the amended whole-job model/raw-E/crop contract. No parent primary conclusions consulted. Source/tests unchanged; no baseline overwrite or physical operation.

## CM-1 Medium — public geometry extraction trusts replaceable trace contents

Location: `extract_conditional_nominal_model` input check and event loop; `reassociate_raw_nominal_geometry` current-model trust boundary.

The extractor verifies the trace/descriptor class and equality of the trace's descriptor fingerprint, but never rebuilds or verifies the events against the actual source/entry/motion inputs. Frozen dataclasses are still constructible/replaceable. An event's before/after states, raw bytes, parameters, scope, metadata or deposited E may be changed while the original descriptor identity remains intact. `fingerprint(event)` merely fingerprints the changed event; it does not establish original-source provenance.

Independent executable counterexample: obtain a genuine synthetic typed trace; replace its positive event's `before.xyz_mm` with `(777,888,999)`, retaining `G1 X2 Y2 E.1 F6000` raw bytes, all parameters, its after state, remaining trace and descriptor fingerprint. The extractor accepts a structural/support segment beginning at that impossible source position. Its returned model still names the original source/project and entry. The existing tests deliberately replace event debt/deposited fields to exercise pure arithmetic, but do not test source authentication.

The reassociation API accepts an arbitrary constructible `ConditionalNominalModel`, checks the old reference against its original-geometry fields, and does not validate current support/debt/event provenance or freshly rebuild current inputs. Thus it cannot repair the missing trust boundary. A mutable/stale or replaced DTO must not become evidence that it came from the named actual current body.

Violated invariant: current spans must derive from freshly reconstructed associated typed events; stale/forged DTO fields cannot establish source material/support. Concrete impact is an offline source-associated false support geometry, with all physical flags still false. Confidence: high. Disposition: confirmed, awaiting parent reconciliation.

Remediation direction: provide a public boundary accepting actual immutable source/project/producer/descriptor/entry/motion and rebuilding the trace/model, or validate supplied DTOs against an independently rebuilt trace before using them. Keep any pure trusted-event projection private/explicitly trust-scoped. Reassociation must similarly bind its current model to rebuilt current inputs rather than trusting the caller class or self-hash. Test replaced event XYZ/debt/metadata/scope, truncated/reordered/mutable traces and replaced current model support/identities.

## Checks and negative coverage

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_model -v` — PASS,3 tests,6.297 seconds, Python3.12.10. Actual14985 complete raw tuple reference,14253 feed differences and21 debt crops reproduce canonical digest `efc398515a96ba55c1935adda08e4641c05d1c35d54a717eca71e418ef940282`.

Additional genuine typed fixtures (without event replacement) changed the refill before a moving extrusion to leave known debt.05 or.2 and changed that move to simultaneous XYZ with Z3→3.2. Partial debt produces exact t1/2, deposited.05 and affine support start `(1.5,2,3.1)`; debt>=raw E gives t1, deposited0 and no support. Arithmetic is sound for these cases. Unknown debt remains no support in the direct test. Exact original geometry is retained separately.

Inspected strict metadata grammar/positivity, missing metadata/scope rejection, exact known nonnegative debt, finite flat-cap segment construction, resource limits and cancellation callback bool checks. Old source/project/rows hashes and embedded profile are checked; ordered old line numbers and command XYZ/raw E are checked using existing strict arithmetic, not another modal interpreter. The old rows are explicitly a nominal reference with declared starts, not a complete old firmware execution proof. No source/geometry authority transfer should be inferred.

The new function owns extraction/crop provenance rather than policy/geometry optimization and does not alter existing strict APIs. Resource/cancellation/schema coverage is currently narrow in tests; expand the association-boundary cases while fixing CM-1 rather than treating3 passing tests as convergence. No second independent material finding established within this bounded review.

All output remains conditional nominal, not a physical source anchor, full-job certificate or print authorization.

## CM-1 fix verification

Public extraction now accepts the complete immutable six-input source/project/producer/descriptor/entry/motion tuple and calls the actual interpreter itself; trusted event projection is private. Public reassociation freshly re-extracts the complete model and compares it before using any caller model fields. Exact known/unknown deposited-E consistency, positive exact feed and bit limits for debt/crop/deposited/feed were also added.

Independent original forged-XYZ trace is rejected by the public extraction API. Replaced current-model source identity and support geometry each reject at reassociation with stale/forged mismatch before old-row comparison. Genuine source-derived partial/full-debt simultaneous-Z fixtures retain exact t1/2 and t1 behavior. No public caller event-state field supplies material provenance now.

Command: `.\.venv\Scripts\python.exe -m unittest tests.unit.test_conditional_nominal_model -v` — PASS,4 tests,27.826 seconds, Python3.12.10. Covers known-None/deposited contradictions, bool/float values, over-budget feed/debt/crop, trace rejection and replaced model. Actual14985 raw bijection,14253 feed changes,21 crops and canonical digest remain unchanged. No new material defect established in this bounded correction.

Final CM-1 disposition: **confirmed / fixed / independently verified**. The private projection's trusted-input scope is explicit; source-bound public APIs establish current provenance. Physical authority remains false.
