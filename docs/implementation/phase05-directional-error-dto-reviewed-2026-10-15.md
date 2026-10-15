# Phase 0.5 — ADR-0047 bounded immutable directional-error DTO implementation review

**2026-10-15 | Primary review disposition: VALIDATED for standalone immutable directional summary vocabulary only; not the full Plan v2 projection, not production error-estimator implementation.**

## Accepted source and scope
- Accepted `docs/adr/0047-bidirectional-surface-error-and-coverage.md` requires separate pred->src and src->pred `E_max`, `E_p95`, `E_rms` and separate tolerance checks per direction. Accepted ADR-0045 requires numeric convergence but this field-only DTO cannot establish or certify convergence.
- Base `docs/SPECIFICATION.md` §16 already defines public `E_max = max(E_max_pred_to_src,E_max_src_to_pred)` and equal-direction RMS summary. Existing `ErrorMetrics` has only four aggregated summary fields, and `PlanSemanticContent` v1 embeds it. Do not change either.
- Existing `domain/metrics.py` owns frozen numeric metric vocabulary; `application/serialization.py::_FIELDS` is the only canonical registration. Physical print/optimizer/Orca code and v1 plan settings/hash remain untouched.

## Narrow implementation
- Add `BidirectionalSurfaceErrorMetrics` frozen/slots DTO with six explicitly named millimeter fields `e_max_pred_to_src_mm`, `e_max_src_to_pred_mm`, `e_p95_pred_to_src_mm`, `e_p95_src_to_pred_mm`, `e_rms_pred_to_src_mm`, `e_rms_src_to_pred_mm`.
- All values must be finite binary64, >=0, and each directional p95 and rms <= the matching directional max. Wrong types, bool, NaN, Inf, negative, and invalid directional bounds reject with existing `ContractError(ReasonCode.INVALID_GEOMETRY)`.
- Register exactly six fields in `application/serialization.py::_FIELDS`; standalone serialization only. Do not add it to `PlanSemanticContent`, change the `subedge-plan` root, convert it into a physical acceptance claim or record an unverified convergence result.
- Add tests: exact names + frozen DTO, zero/bounds, invalid numeric/type/negative, each directional mismatch, deterministic canonical bytes and sensitivity, Plan v1 identity unaffected.

## Explicit version gate
Future Plan v2 inclusion and typed convergence proof require Proposed ADR-0067 adjudication and review. This DTO is not an estimator or validator of surface correspondence, does not claim global physical support, and is not automatically sufficient for injection.

## Verification and rollback
Push source/test commits to Draft implementation PR #2 and require matching-head Python 3.12 GitHub Actions: `python -m compileall -q adaptive_subedge orca_plugin tests` and `python -m unittest discover -s tests -p 'test_*.py' -v`. Preserve independently checked v1 canonical golden tests. No Ruff/mypy/wheel is configured. If any fail, do not mark the tranche validated/completed. Revert only this DTO/registry/test/review addition to roll back; existing v1 code untouched.
