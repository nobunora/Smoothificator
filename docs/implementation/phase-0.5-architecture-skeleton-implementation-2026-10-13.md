# Phase 0.5 — Implementation Task Record — 2026-10-13

## Specification

- Handoff: `docs/specs/adaptive-subedge-v1.md`, Git blob `b9337971fc077f0c39793b87ecf0293b0b6a6c29`.
- Canonical manifest: `docs/AUDIT_REVISION_2026-10-13.md`, Git blob `ed32f47cc541443a52bc6abed289cc86b31d816b`.
- Validated review: `docs/implementation/phase-0.5-architecture-skeleton-review-2026-10-13.md`.
- Implementation base commit: `347098214979ff3efb5f669c6e3276c0c262d5a7`.
- Accepted ADRs particularly: 0037, 0049, 0061–0065; superseded ADR-0010 does not control flow.
- Production code lives only on `phase-0.5-skeleton-20261013`, not the design baseline.

## Repository Review Status

`validated` **for bounded Phase 0.5 architecture-skeleton contracts only**.

## Evidence and environment

- The referenced 81-file manifest matched the exact Git tree (81/81), checked before branch creation.
- Existing `Smoothificator.py` and `Smoothificator_Adaptive.py` are baseline scripts and MUST NOT be edited.
- No `adaptive_subedge/`, `orca_plugin/`, or `tests/` package code existed at the base.
- Running container: Python 3.13.5; this is **not** the Orca embedded Python. The actual target Orca runtime and optional NumPy binary compatibility have not been verified, so no wheel metadata, live adapters, plugin registration, or physical injection is authorized.
- No existing test runner/toolchain is configured for the package. Prefer Python standard-library `unittest` for basic contracts; report static analysis as NOT CONFIGURED without adding Ruff/mypy.

## Three bounded steps for this iteration

1. Precondition check, separate branch and record: verify audited handoff, ownership and phase boundary, record test cases first.
2. Create core package/types/validated Settings only. Introduce no Orca imports, printer physical constants, or G-code behavior.
3. Implement canonical byte/hash and process-local store contracts with focused tests, then review. Stop after reporting, even if more Phase 0.5 functionality remains.

## Scope explicitly forbidden

- Legacy script modification, optimizer/mesh algorithms, Orca runtime adapters, final-G-code parser/matcher/emitter, file replacement, physics calibration, physical print.
- Guessing fixture safety dimensions or claiming runtime parity from CPython validation.
- Silent new product-policy or schema definitions conflicting with accepted ADRs.

## Planned verification

- Source-tree/import path check and `python -m compileall` on relevant new packages.
- `python -m unittest discover -s tests -p 'test_*.py' -v` in an available Python 3.12/3.13 environment; when that environment is unavailable, mark BLOCKED rather than PASSED.
- Deterministic canonical bytes and hash independent from object ordering, finite/-0 handling, array shape/endianness and typed domains.
- DTO immutability, Settings evidence gates, PlanStore epoch/generation/retention, attempt transitions/parallel attempts, and architecture import boundary tests.

## Results

PENDING implementation and validation evidence. Initial task record authorizes no printer behavior.

## Next gate

Document exact source changes, tests/commands/results, remaining review findings and the smallest subsequent implementation milestone.
