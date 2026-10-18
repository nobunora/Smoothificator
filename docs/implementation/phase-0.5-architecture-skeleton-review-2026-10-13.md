# Phase 0.5 — Architecture Skeleton Repository Revalidation — 2026-10-13

## Disposition

`validated` **for Phase 0.5 architecture skeleton only**.

This is a repository/specification handoff review, not successful implementation tests, final G-code injection permission, Orca version certification, or printer-release clearance.

## Exact review inputs

- Repository / branch: `nobunora/Smoothificator` / `adaptive-subedge-design`
- Previous source-of-truth commit when this review packet began: `1e0580ae994112a2d56e3d7567f2e9d73d5fbb85`
- Handoff: `docs/specs/adaptive-subedge-v1.md`, blob `b9337971fc077f0c39793b87ecf0293b0b6a6c29`
- Canonical manifest: `docs/AUDIT_REVISION_2026-10-13.md`, blob `ed32f47cc541443a52bc6abed289cc86b31d816b`
- Canonical source bundle: 16 governance/normative/audit documents + 65 ADRs, 81 entries
- Change-specific accepted ADRs: ADR-0061/0062/0063/0064/0065, with earlier ADR-0037/0049/0011/0023/0032/0033/0048 as applicable
- Product/document precedence: `AGENTS.md` and `docs/DOCUMENT_CONTRACT.md`
- Review contract: `.codex/repository-review.md`
- Previous Orca drift evidence: `docs/FULL_CONSISTENCY_AUDIT_2026-10-08.md` (Orca source commit `7d44b60ae4042b4de8c3844eb9dd2671c2d2d873`); NOT independently rerun here.

## Read-only repository evidence and checks

1. **Manifest integrity: PASS.** The first 2026-10-13 manifest had 81/81 direct GitHub file-blob SHA matches. Subsequent scoped correction cycles changed only five of those normative blobs (IMPLEMENTATION, ROADMAP, PLUGIN_REQUIREMENTS, ADR-0064, TEST_STRATEGY); all five were directly re-fetched and checked against their updated blobs. The other 76 retain the same previously verified blob SHA. The final manifest was checked against the complete current Git tree, 81/81 matches, no missing entries.
2. **ADR identifiers: PASS.** 65 distinct tracked ADR paths with exact numeric IDs 0001–0065; no duplicate or missing numbers. ADR-0010's directly read header is `Superseded` by ADR-0015; new ADR-0064/0065 are `Accepted`.
3. **Handoff provenance: PASS.** The handoff references the final exact manifest blob `ed32f47cc541443a52bc6abed289cc86b31d816b`; the handoff itself is excluded from that manifest to avoid a circular SHA contract. This review records the exact handoff blob separately.
4. **Phase 0.5 boundaries: PASS at documentation level.** Domain/engine keep out live Orca, G-code parsing/emission, UI, and machine-space translation. Immutable plan content goes through one application serialization owner and one hash owner; the injector does not optimize.
5. **Plan identity: PASS at documentation level.** ADR-0064 fixes plan hash self-reference, typed root field names and initial version strings, and the exact canonical array-token representation. ADR-0062 remains the byte/domain/hash owner; no alternative serializer is authorized.
6. **Plan lifetime/status: PASS at documentation level.** ADR-0065 distinguishes PluginSessionEpoch from AnalysisGenerationId, permits uniquely matching older *retained* current-epoch plans, excludes stale/restarted/cache-only plans, and gives attempt-scoped runtime evidence a single owner. The obsolete analyzer step that wrote mutable PLANNED status to PlanStore has been corrected.
7. **Segment safety and concurrent commit: PASS at contract level.** ADR-0063's fixture-specific segment regularity enters Settings and PluginSettingsFingerprint and later post-quantization validation, with no invented physical defaults. ADR-0061's same-path final commit lock is required in the later G-code execution owner, not prematurely implemented in Phase 0.5.
8. **Source/root scope: PASS.** The original `Smoothificator.py` and `Smoothificator_Adaptive.py` exist unchanged as legacy references. No production `adaptive_subedge/`, `orca_plugin/` or `tests/` package source exists yet; Phase 0.5 will create these in a separate implementation change.

## Approved Phase 0.5 implementation scope

Package skeleton, frozen typed domain DTOs and validated Settings (including regularity policy schema but no physical fixture values), ToolClearanceProfile schema, final-vs-chronological material/support and dependency/order metadata, two typed fingerprints, canonical serializer/hash, PlanStore epoch/generation/eviction/snapshots, independent InjectionAttemptStore, stable reasons/errors, and architecture/import tests.

Phase 0.5 MUST NOT implement live Orca adapters, finite-bead prediction/optimizer, streaming G-code parser/matcher/emitter, working-file commit lock runtime, actual injection, or physical printing.

## Required verification after Phase 0.5 implementation

Focused tests must prove:
- package imports and forbidden dependency boundaries;
- frozen DTOs with no live Orca references;
- Settings/fingerprint validation and ADR-0063 fixture-vs-research configuration;
- ADR-0062/0064 independently derived exact canonical bytes and typed plan hash (including no self-reference, array layout/endianness parity and rejection cases);
- ADR-0065 session epoch, generation, deduplication, retention/eviction, snapshot and attempt-store concurrency;
- ToolClearanceProfile/schema semantics without fabricated hardware defaults;
- file-level ADR uniqueness and contract check;
- package/build only after verifying actual target Orca embedded Python/runtime metadata.

No Python test suite, package build, firmware fixture, physical tool-clearance test or printer test was executed during this **review-only** pass because the relevant production package/tests do not yet exist. No claim is made about runtime success.

## Conflict dispositions

- F-01 stale manifest/handoff: **confirmed -> resolved** by exact 2026-10-13 manifest/restamp.
- F-02 ADR-0063 Settings and tests: **confirmed -> resolved** in canonical docs and future tests.
- F-03 ADR-0061 commit-lock handoff: **confirmed -> resolved as later-stage execution contract**, not implemented.
- F-04 hash self-reference: **confirmed -> resolved** by ADR-0064.
- F-05 array-digest parent token: **confirmed -> resolved** by ADR-0064.
- F-06 latest-generation/current-session ambiguity: **confirmed -> resolved** by ADR-0065.
- F-07 PlanStore PLANNED/status dual ownership: **confirmed -> resolved** in IMPLEMENTATION and ARCHITECTURE.
- Historical 2026-10-01 review: **superseded** for implementation authority.

## Remaining gates / risk / rollback

The current Orca SlicingPipeline contract is experimental, and the version-specific runtime, exact host API, G-code semantics, profile fixtures, independent golden tests and physical calibration are **not verified by this Phase 0.5 review**. They remain mandatory later-stage gates. Hardware ToolClearanceProfile and candidate regularity limits remain unknown until backed by physical evidence.

No Critical/High **documentation-level** contradiction was found remaining inside the Phase 0.5 architecture-skeleton scope after the above corrections. This does not establish global physical correctness.

This review changes no printer behavior or legacy code. If later implementation/repository evidence contradicts a required schema, stop and return to ADR/specification adjudication; Phase 0.5 changes should remain separately revertible.

## Recorded operations

- GitHub connector read of AGENTS, document precedence, handoff and selected accepted ADRs.
- GitHub branch/PR metadata and recursive Git Trees to identify the current source set and changed-file deltas.
- Direct GitHub file-content reads with blob SHA verification, and scoped manual semantic cross-check.
- No shell commands, package imports, tests, build commands or actual printer operations were run.

## Next gate

With current audited blobs and this review disposition, **Phase 0.5 implementation may begin only on a separately reviewable implementation change** after the exact runtime and task-record preconditions are checked. Physical injection remains forbidden.
