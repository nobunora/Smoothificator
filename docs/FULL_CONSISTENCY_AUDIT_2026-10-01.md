# Full Consistency and Technical Feasibility Audit — 2026-10-01

Status: COMPLETE for Phase 0.5 implementation handoff
Audit class: full-document consistency + technical source audit + final convergence
Project branch: adaptive-subedge-design

## 1. Scope

Reviewed as one dependency graph:

Governance / workflow:
- AGENTS.md
- DOCUMENT_CONTRACT.md
- ADR_PROCESS.md
- PROJECT_RULES_ADOPTION.md
- QUALITY_GATES.md
- REVIEW_PROCESS.md
- docs/specs workflow
- docs/implementation workflow
- .codex repository-review / implementation contracts
- PR/workflow gates

Normative technical documents:
- SPECIFICATION.md
- ARCHITECTURE.md
- IMPLEMENTATION.md
- PLUGIN_REQUIREMENTS.md
- ERROR_MODEL.md
- ZAA_INTEGRATION.md
- TEST_STRATEGY.md
- ROADMAP.md

Evidence/history:
- ORCASLICER_PLUGIN_RESEARCH.md
- DEPENDENCY_AUDIT.md
- FULL_CONSISTENCY_AUDIT_2026-09-30.md
- SMOOTHIFICATOR_ANALYSIS.md
- README.md
- legacy Smoothificator scripts

Decision records:
- every ADR 0001 through 0031
- ADR-0010 is Superseded by ADR-0015
- all other current canonical ADR identifiers are unique

External technical evidence:
- OrcaSlicer main source audit baseline:
  789f848694b955d293ca6b277d1c8046aa6f7436
- current official Orca Python Plugin System / SlicingPipeline documentation
- current Bambu/Orca profile/source evidence relevant to narrowed v1

## 2. Final disposition

### Phase 0.5 software implementation

Disposition: IMPLEMENTABLE.

No currently known stock-Orca API, document-level, architecture-level, or source-level contradiction prevents implementation of the Phase 0.5 architecture skeleton:
- package boundaries;
- immutable DTOs;
- Settings;
- both fingerprints;
- ToolClearanceProfile schema;
- serialization/hash;
- PlanStore/status store;
- architecture tests.

### Full software pipeline

Disposition: TECHNICALLY IMPLEMENTABLE IN STAGED GATES.

The current stock-Orca contract supports the planned architecture:
- read-only post-ZAA planning at posSimplifyPath;
- plugin-owned preview;
- final psGCodePostProcess validation/injection;
- current-session immutable plan handoff;
- binary byte-preserving streaming postprocess.

Implementation remains gated by ROADMAP and TEST_STRATEGY.

### Physical injection

Disposition: NOT YET ENABLED.

Physical printing remains blocked until:
- exact supported Orca/Bambu machine/process/filament fixture exists;
- ToolClearanceProfile has documented physical evidence;
- parser/matcher/frame/quantizer/retraction/downstream-clearance gates pass;
- primary + independent blind review converge;
- conservative physical coupons pass.

This is intentional and is not a Phase 0.5 blocker.

## 3. Final canonical technical model

The audited v1 consistently states:

- stock Orca only;
- analyzer hook = posSimplifyPath;
- final executor = psGCodePostProcess;
- immutable plan shared by preview and injector;
- one PrintObject / one total ModelInstance / one positive ModelPart;
- finite/manifold source mesh plus validated orientation/material side;
- domain geometry = Orca centered PrintObject slice-space;
- source boundary != nozzle centerline;
- every added v1 SubEdgePath is constant-Z;
- different added paths may use independent Z values;
- candidate seam/gap is frozen before preview;
- 0.08 mm initial limit = effective bead height above local support, not neighboring path-Z separation;
- segment-local support/height/flow;
- geometric volume != commanded/calibrated volume;
- original Orca structural extrusion is unchanged;
- final E is derived only after machine mapping and XYZ quantization;
- final structural matching is seam-start/seam-gap/subdivision invariant;
- machine frame is a separately validated constant translation;
- actual emitted machine state is restored, not nominal inferred layer state;
- parsed retraction state is preserved exactly;
- plugin travel uses safe-ceiling motion;
- downstream original Orca motion is checked against injected bead material;
- physical ToolClearanceProfile is required for hardware mode;
- original G-code is handled as a binary byte-preserving line stream;
- expected unsupported/validation failures return Skipped;
- no physical printing before fixtures, software gates, and blind review.

## 4. Critical/high findings resolved in the final audit

### F-01 — Conditional/too-early analyzer hook
Resolution: ADR-0001 -> posSimplifyPath.

### F-02 — ZAA path Z was relative, not absolute
Resolution: ADR-0006.

### F-03 — ZAA local extrusion target changed with local Z
Resolution: ADR-0006.

### F-04 — Source mesh transform missed Orca center offset
Resolution: ADR-0012 reconstructs centered slice frame.

### F-05 — Manifold status did not prove usable outward/material orientation
Resolution: ADR-0030 validates/derives orientation/material side and inside/outside parity.

### F-06 — Mesh section was being conflated with nozzle centerline
Resolution: ADR-0005 surface-band/centerline separation.

### F-07 — 0.08 mm was attached to the wrong physical quantity
Resolution: ADR-0004 effective bead height.

### F-08 — Candidate path Z topology was ambiguous
Resolution: ADR-0026 constant-Z SubEdgePath.

### F-09 — Candidate seam/gap could have changed after optimization
Resolution: ADR-0029 freezes candidate seam/gap in the immutable plan.

### F-10 — Path-wide flow was insufficient for varying support
Resolution: ADR-0014 segment-local extrusion intent.

### F-11 — Orca external-wall E formula was incomplete
Resolution: ADR-0015 supersedes ADR-0010 complete formula.

### F-12 — Global calibration flow was conflated with physical bead geometry
Resolution: ADR-0022 separates geometric, commanded, and future empirical volume.

### F-13 — Final E could not be frozen at geometry time
Resolution: ADR-0021 derives E after final machine XYZ quantization.

### F-14 — Final G-code loop representation differs from posSimplifyPath
Resolution: ADR-0016 seam/subdivision/gap-invariant structural matcher.

### F-15 — Plan coordinates were not final machine coordinates
Resolution: ADR-0009 execution-frame translation.

### F-16 — Python rounding does not guarantee Orca formatter parity
Resolution: ADR-0017 dedicated quantizer.

### F-17 — Layer marker did not guarantee physical new-layer Z
Resolution: ADR-0013 restores actual parsed emitted state.

### F-18 — Naive configured retract could double-retract
Resolution: ADR-0018 exact parsed retraction debt/state.

### F-19 — Expected plugin rejection could abort otherwise valid export
Resolution: ADR-0019 maps normal unsupported/validation failures to Skipped.

### F-20 — Plugin settings could stale a valid-looking plan
Resolution: ADR-0023 PluginSettingsFingerprint.

### F-21 — First layer required a different physical model
Resolution: ADR-0024 excludes first-layer refinement.

### F-22 — Unreplicated dynamic features changed execution/geometry semantics
Resolution: ADR-0028 rejects fuzzy skin and adaptive volumetric speed in printable v1.

### F-23 — Safe injected travel did not protect later original Orca motion
Resolution: ADR-0025 downstream original-motion clearance.

### F-24 — Nozzle diameter did not define physical hotend keep-out
Resolution: ADR-0025 requires explicit ToolClearanceProfile with physical evidence.

### F-25 — Injected paths bypass normal Orca role orchestration
Resolution: ADR-0020 narrows adaptive PA/role/custom motion features and uses conservative supported speed/state contracts.

### F-26 — Source G-code mutation through text mode could change unrelated bytes/newlines
Resolution: ADR-0031 binary byte-preserving streaming contract.

### F-27 — Duplicate ADR-0025 identifier existed during convergence
Resolution: decisions consolidated into one canonical ADR-0025; duplicate file deleted.

### F-28 — Keep-out naming drift
Resolution: canonical name is ToolClearanceProfile.

### F-29 — Formula escape/control-character corruption existed in Markdown
Resolution: affected normative formula text rewritten in plain deterministic text; core/ADR control-character checks passed.

### F-30 — Audit/handoff revision became stale after the final technical fixes
Resolution: this 2026-10-01 audit and a new 2026-10-01 blob manifest replace the old readiness revision. Historical 2026-09-30 evidence remains preserved.

## 5. Technical feasibility review

### Stock Orca plugin architecture
PASS.

Current official Orca plugin docs/source confirm:
- Python plugins do not require rebuilding Orca;
- one plugin may register multiple capability classes;
- SlicingPipeline has posSimplifyPath and psGCodePostProcess;
- geometry hooks expose live Print context only during execute();
- psGCodePostProcess exposes the working G-code path and final config_value access;
- slicing-pipeline callbacks are not a UI-safe place for host UI calls.

### Centered geometry reconstruction
PASS for narrowed v1 contract.

Required source inputs are exposed to reconstruct/verify the one-instance/one-volume centered frame.

### Plan -> final G-code matching
IMPLEMENTABLE, HIGH RISK.

Representation changes from seam placement/gap/subdivision are explicitly modeled; exact fixtures are still required before physical mode.

### Machine-state restoration
IMPLEMENTABLE, HIGH RISK.

v1 is deliberately relative-E, firmware-retract-off, golden-fixtured, parser-state driven.

### Downstream collision validation
IMPLEMENTABLE AS A SOFTWARE GATE.

Physical completeness depends on ToolClearanceProfile evidence and conservative margins; therefore no generic collision-safety claim is made before hardware validation.

### Binary postprocess
PASS architecturally.

ADR-0031 makes byte preservation and atomic replacement explicit; platform-specific rename/fsync behavior remains a fixture-stage compatibility gate.

### Physical bead prediction
NOT YET EMPIRICALLY PROVEN.

The nominal finite-bead model is suitable as a reference/optimizer model, but real deposited geometry requires Phase 5/6 calibration before production-quality claims.

## 6. Deliberately deferred items

These are not Phase 0.5 blockers:

- exact first production-supported Orca release/commit;
- exact first Bambu machine/process/filament fixture;
- measured/manufacturer ToolClearanceProfile dimensions;
- empirical bead-shape correction model;
- final lint/type tool versions;
- production performance/resource budgets;
- broader multi-object/CSG/support/overhang/absolute-E/arc/PA/tool support.

Each is owned by a later ROADMAP gate.

## 7. Documentation consistency result

After final convergence:
- ADR identifiers: unique 0001–0031;
- ADR-0010: Superseded by ADR-0015;
- canonical hook: posSimplifyPath;
- canonical executor: psGCodePostProcess;
- canonical hardware clearance name: ToolClearanceProfile;
- canonical source geometry frame: centered PrintObject slice-space;
- canonical candidate topology: explicit open constant-Z SubEdgePath;
- canonical flow fields: geometric_mm3_per_mm + commanded_mm3_per_mm;
- final emitted E: execution-derived, not plan-owned;
- canonical G-code mutation mode: binary byte-preserving streaming;
- physical mode remains fail-closed.

No known material contradiction remains in the normative v1 documents at this audit point.

## 8. Readiness

Specification/architecture readiness: PASS.

Phase 0.5 implementation readiness: PASS pending revision-manifest re-stamp and review-only repository revalidation against that new manifest.

Physical printer readiness: FAIL / intentionally gated.

## 9. Required next workflow

1. write AUDIT_REVISION_2026-10-01.md with current normative blob SHAs;
2. update docs/specs/adaptive-subedge-v1.md to reference that manifest;
3. rerun the Phase 0.5 review-only repository validation against the new manifest;
4. if still validated, Phase 0.5 architecture-skeleton implementation may begin on a separate implementation branch/PR;
5. before implementation code is written, perform the requested principle/architecture explanation as an additional human design review.

## 10. Source baseline

Primary source audit baseline:
OrcaSlicer main commit 789f848694b955d293ca6b277d1c8046aa6f7436.

Current official Orca documentation was also checked for:
- Python Plugin System architecture;
- SlicingPipeline behavior;
- psGCodePostProcess;
- multiple capability registration.

Future compatibility MUST be revalidated rather than assuming this audit remains valid.
