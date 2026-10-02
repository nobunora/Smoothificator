# Supplementary Consistency and Failure-Mode Audit — 2026-10-02

Status: COMPLETE for Phase 0.5 handoff after re-stamp/revalidation
Audit class: failure-prone implementation boundaries + current-Orca drift
Supersedes for readiness decisions: 2026-10-01 audit revision, while retaining it as historical evidence.

## 1. Why this audit was performed

After the 2026-10-01 consistency audit and principle/design review, the project was technically coherent enough for Phase 0.5.

A further review deliberately targeted failure-prone implementation boundaries rather than broad architecture:
- final structural deposition versus planning geometry;
- hidden G-code modal state;
- dynamic Orca/Bambu runtime features;
- repeated/concurrent postprocess attempts;
- topology that is legal as one ModelPart but ambiguous for v1;
- dynamic extrusion post-processing;
- inherited acceleration;
- postprocess time/material/progress metadata;
- compatibility drift between audited Orca baseline and current main.

## 2. Current Orca drift

Original source baseline:
`789f848694b955d293ca6b277d1c8046aa6f7436` — 2026-09-29.

Current main checked:
`1a5f91d727f43d455b40ab475a00d622b34648e0` — 2026-10-02.

Current main was approximately 150 commits ahead.

Direct file comparison found:
- SlicingPipeline capability binding unchanged;
- PluginHostSlicing binding unchanged;
- bundled Python still 3.12.13;
- GCode.cpp changed;
- Print.cpp changed;
- Bambu/profile data continued to evolve.

Conclusion:
stock-Orca plugin feasibility remains intact, but compatibility must be fixture-pinned. The old baseline is not a blanket claim about current main.

## 3. New material findings

### S-01 — Planning-time structural support could disappear at final seam gap
Severity: Critical
Resolution: ADR-0034.

posSimplifyPath exposes the simplified structural loop before final seam placement/gap clipping.

A candidate near the lower-wall seam could appear supported during planning but lose that support in final G-code.

Fix:
build a local FinalStructuralDepositionContext after final structural matching and revalidate support/hard geometry against actual final positive-E deposition. No postprocess replanning.

### S-02 — Configured outer-wall speed was not sufficient as the final candidate speed reference
Severity: High
Resolution: ADR-0034.

Cooling/overhang/resonance/final G-code transforms can reduce the actual wall feed after geometry planning.

Fix:
candidate speed is also capped by the minimum relevant actual matched final-G-code external-wall feed.

### S-03 — G-code modal state contract was incomplete
Severity: Critical
Resolution: ADR-0035.

Candidate meaning can change under:
- G20/G21;
- G90/G91;
- M82/M83;
- M200;
- M220;
- M221;
- G92.

Fix:
printable v1 requires G21 + G90 + M83, firmware volumetric-E off, M220=100%, M221=100%, no unsupported G92 XYZ remap.

Logical E coordinate and physical retraction debt are separate states. G92 E must not erase physical retraction debt.

### S-04 — Live printer speed/flow overrides cannot be validated offline
Severity: High limitation
Resolution: ADR-0035.

A user can change printer-side speed/flow override after G-code creation.

Fix:
physical validation claim is conditional on live speed/flow overrides remaining 100% for the validated print. Changing them voids the validated execution envelope.

### S-05 — Timelapse/wrapping/wipe-tower behavior was too broadly covered by "normal print"
Severity: High
Resolution: ADR-0036.

Current Orca includes additional timelapse paths, including farthest-point behavior. Traditional timelapse is not globally motion-free.

Fix:
- smooth timelapse off;
- farthest_point_timelapse off;
- wrapping detection off;
- no generated wipe/prime tower;
- traditional timelapse only via exact parser-supported fixture.

### S-06 — Object cancellation could skip the object but not the injected block
Severity: High
Resolution: ADR-0036.

Injected G-code does not yet implement Orca/firmware skip-object semantics.

Fix:
exclude_object must be disabled for printable v1. Object-label comments may remain.

### S-07 — One ModelPart did not guarantee one simple v1 topology
Severity: High
Resolution: ADR-0038.

A single manifold ModelPart can contain disconnected shells or target cross-sections with holes/multiple loops.

Fix:
printable v1 requires one connected closed shell and one simple relevant outer target loop in each interaction region.

### S-08 — Runtime status model could race across export/upload attempts
Severity: High
Resolution: ADR-0037.

One mutable status per plan could be overwritten by simultaneous/repeated attempts.

Fix:
- AnalysisGenerationId;
- InjectionAttemptId;
- InjectionAttemptRecord;
- immutable plan snapshots per attempt;
- monotonic attempt transitions.

### S-09 — Multi-pass postprocess had TOCTOU exposure
Severity: High
Resolution: ADR-0037.

The working file or plugin settings could change between validation and atomic commit.

Fix:
- Pass-1 source digest/identity;
- Pass-2 digest equality;
- precommit source metadata/identity check;
- precommit PluginSettingsFingerprint recheck.

### S-10 — Pressure Equalizer / extrusion-rate smoothing would be bypassed by inserted paths
Severity: High quality/parity risk
Resolution: ADR-0039.

Positive max_volumetric_extrusion_rate_slope causes Orca to postprocess extrusion-rate transitions before Adaptive Sub-Edge injection.

Fix:
printable v1 requires extrusion-rate smoothing disabled.

### S-11 — Candidate acceleration could inherit an inappropriate travel/infill state
Severity: High
Resolution: ADR-0040.

v1 does not emit role-specific acceleration commands.

Fix:
active acceleration must be parser-known and <= plugin max_subedge_acceleration_mm_s2, which itself must be <= exact fixture external-wall acceleration limit.

Unknown/high state => Skipped.

### S-12 — Orca preview/time/material/progress remains stale after injection
Severity: Medium user-facing correctness
Resolution: ADR-0041.

SubEdge is inserted after Orca estimates time/material and emits progress metadata.

Fix:
- do not claim standard Orca estimates include SubEdge;
- plugin reports deterministic added path/material/time delta separately;
- v1 does not rewrite M73/progress/stat metadata;
- physical benchmark uses final G-code / actual printer evidence.

### S-13 — Quantization can collapse short candidate segments
Severity: High boundary case, covered by existing ADR-0017/0021.

Final XYZ/E quantization can create:
- zero-length emitted segment;
- nonzero planned material with E quantized to zero.

Fix:
make these explicit reject cases in TEST_STRATEGY. No new architecture decision required.

## 4. Findings rechecked but not changed

### Cooling/fan state
Candidate inherits actual validated fan/thermal state.

This can affect physical bead quality but is not a logical contradiction.

It remains an empirical physical-calibration risk.

### Static pressure advance
May remain enabled if the plugin does not change it and the exact fixture validates inherited behavior.

Adaptive PA remains disabled.

### G-code formatter
Audited current source still uses the same active 3-decimal XYZ/F and 5-decimal E formatter branch.

### Bundled Python
Current main still uses Python 3.12.13.

## 5. Canonical ADR state after this audit

Canonical ADR identifiers are now:
- ADR-0001 through ADR-0041;
- ADR-0010 is Superseded by ADR-0015;
- all identifiers unique.

New in this audit:
- 0034 final structural deposition revalidation;
- 0035 modal/runtime override envelope;
- 0036 timelapse/wrapping/object-cancellation gates;
- 0037 attempt-scoped state / TOCTOU protection;
- 0038 simple connected topology;
- 0039 disable extrusion-rate smoothing;
- 0040 inherited acceleration gate;
- 0041 postprocess estimate/progress limitation.

## 6. Phase 0.5 impact

Phase 0.5 schema/infrastructure must now include:
- AnalysisGenerationId;
- InjectionAttemptId;
- InjectionAttemptRecord / InjectionAttemptStore;
- one connected-shell/simple-topology reason taxonomy;
- existing immutable plan DTOs/fingerprints/ToolClearanceProfile.

Phase 0.5 still does NOT implement:
- final structural deposition reconstruction;
- modal parser;
- timelapse parser;
- G-code mutation;
- pressure-equalizer logic;
- acceleration execution;
- physical printing.

Thus the new findings change the contracts but do not create a Phase 0.5 API blocker.

## 7. Readiness conclusion

Phase 0.5 architecture-skeleton implementation remains technically feasible after the new findings.

However, the prior 2026-10-01 audited manifest and repository-review disposition are stale for readiness because canonical contracts changed.

Required closure:
1. build a new 2026-10-02 blob manifest;
2. stamp the handoff to that manifest;
3. re-run review-only Phase 0.5 repository validation;
4. require 0 unresolved Critical/High findings in Phase 0.5 scope.

Physical injection remains intentionally NOT READY.

## 8. Residual risks that remain later-phase/empirical

No additional architecture change is justified yet for:
- real bead geometry versus nominal model;
- fan/cooling/thermal effects;
- pressure transients from segment-local flow changes;
- physical ToolClearanceProfile measurement error;
- optimizer/clearance computational cost;
- experimental Orca plugin/API drift;
- inaccurate standard Orca progress/time/material metadata beyond the explicit limitation.

These remain owned by later gates.
