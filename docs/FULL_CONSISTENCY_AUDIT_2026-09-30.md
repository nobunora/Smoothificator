# Full Consistency and Technical Feasibility Audit — 2026-09-30

Status: COMPLETE for specification handoff
Audit class: full-document consistency + technical source audit
Project branch: adaptive-subedge-design

## 1. Scope

Reviewed as one dependency graph, not as isolated prose:

Repository governance / handoff:
- AGENTS.md
- DOCUMENT_CONTRACT.md
- ADR_PROCESS.md
- PROJECT_RULES_ADOPTION.md
- QUALITY_GATES.md
- REVIEW_PROCESS.md
- docs/specs workflow
- .codex review/implementation contracts
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
- SMOOTHIFICATOR_ANALYSIS.md
- README.md
- legacy Smoothificator scripts

Decision records:
- every ADR 0001 through 0031

External technical evidence:
- OrcaSlicer main source, primarily pinned audit commit 789f848694b955d293ca6b277d1c8046aa6f7436
- current official Orca plugin/Z Contouring documentation
- current Bambu profile inheritance/source relevant to the narrowed v1 contract

## 2. Final disposition

### Software implementation

Disposition: IMPLEMENTABLE WITHIN THE NARROWED v1 CONTRACT.

No currently known stock-Orca API or internal logical contradiction prevents implementation of:
- read-only post-ZAA planning at posSimplifyPath;
- plugin-owned preview;
- final psGCodePostProcess validation/injection;
- current-session immutable plan handoff;
- binary streaming G-code processing.

This is not a claim that the physical surface model is already experimentally proven.

### Physical injection

Disposition: NOT YET ENABLED.

Physical printing remains gated on:
- exact pinned Orca/machine/process/filament fixture;
- validated ToolClearanceProfile with documented physical source/measurement;
- software Gates A–W/X as defined by TEST_STRATEGY;
- primary + independent blind review;
- conservative coupon validation.

## 3. Critical/high technical findings and resolutions

### A-01 — posContouring could not support ZAA-off analysis
Severity: Critical

Finding:
posContouring callback is conditional on Orca need_z_contouring() and occurs before final simplification.

Resolution:
ADR-0001 -> posSimplifyPath.

### A-02 — ZAA path Z was not absolute
Severity: Critical

Finding:
ContourZ path-point Z is a layer-relative offset.

Resolution:
absolute centered-slice Z = layer.print_z + unscaled path offset.
ADR-0006.

### A-03 — ZAA also changes local extrusion target
Severity: Critical

Finding:
GCode.cpp applies local ratio:
(path.height + d) / path.height

Resolution:
baseline structural segment stores local effective height and ZAA geometry-directed volume behavior.
ADR-0006.

### A-04 — source mesh frame formula was incomplete
Severity: Critical

Finding:
PrintObject.trafo() @ volume.matrix() misses Orca center_offset.
Orca slices with trafo_centered().

Resolution:
reconstruct raw instance-no-offset bbox center and centered PrintObject frame, then parity-check.
ADR-0012.

### A-05 — manifold alone does not prove outward/material orientation
Severity: High

Finding:
material-side placement and signed error cannot blindly trust raw face normals; mirrored transforms also reverse orientation.

Resolution:
validate shared-edge orientation, derive deterministic global outward/material side, and independently check inside/outside.
ADR-0030.

### A-06 — mesh intersection was close to being treated as nozzle centerline
Severity: Critical

Finding:
mesh section is material boundary; printing it directly generally offsets/grows the part.

Resolution:
surface-band -> material-side centerline planner.
ADR-0005.

### A-07 — 0.08 mm constraint had wrong meaning
Severity: Critical

Finding:
minimum neighbor-Z spacing unnecessarily forbids shallow-band coverage and is not the physical quantity intended.

Resolution:
0.08 mm initial value = minimum effective deposited bead height above local support.
ADR-0004.

### A-08 — candidate path Z topology was ambiguous
Severity: High

Finding:
segment-local support fields accidentally allowed interpretation of continuously varying-Z added paths.

Resolution:
every v1 SubEdgePath is constant command-Z; different paths optimize Z independently.
ADR-0026.

### A-09 — candidate closed-loop seam could have changed after optimization
Severity: High

Finding:
choosing seam/gap only in postprocess would alter material geometry after preview/scoring.

Resolution:
candidate seam/start/gap is deterministic and frozen into the plan.
ADR-0029.

### A-10 — path-wide flow was insufficient
Severity: High

Finding:
constant-Z path may cross support whose Z varies, so effective bead height can vary by segment.

Resolution:
SubEdgeSegment is authoritative local extrusion unit.
ADR-0014.

### A-11 — original candidate E formula was incomplete
Severity: Critical

Finding:
filament_flow_ratio alone does not reproduce Orca external-wall command flow.

Resolution:
commanded flow includes print_flow_ratio, filament_flow_ratio, and optional outer_wall_flow_ratio.
ADR-0015 supersedes ADR-0010.

### A-12 — calibration flow was conflated with physical bead geometry
Severity: High

Finding:
filament_flow_ratio=0.98 is not evidence that actual bead geometry is exactly 2% smaller.

Resolution:
separate geometric volume, commanded volume, and future empirical physical model.
ADR-0022.

### A-13 — final E cannot be frozen at geometry time
Severity: High

Finding:
machine mapping/XYZ quantization changes actual emitted short-segment length.

Resolution:
plan stores commanded mm3/mm; final E is derived after machine mapping and XYZ quantization.
ADR-0021.

### A-14 — final loop representation differs from posSimplifyPath
Severity: High

Finding:
Orca seam placement, normal seam-gap clipping, and subdivision alter final representation.

Resolution:
seam-invariant geometry matcher with configured gap allowance.
ADR-0016.

### A-15 — final G-code coordinates are not plan coordinates
Severity: Critical

Finding:
Orca adds instance/origin, extruder offset and machine Z offset effects.

Resolution:
derive one constant translation from matched final structural geometry.
ADR-0009.

### A-16 — Python rounding is not Orca formatter parity
Severity: High

Finding:
Orca emits XYZ/F to 3 decimals, E to 5, using std::round semantics.

Resolution:
single compatibility-owned quantizer + post-quantization validation.
ADR-0017.

### A-17 — layer marker does not imply physical new-layer Z
Severity: Critical

Finding:
Orca may defer physical Z synchronization after change_layer().

Resolution:
save and restore actual parsed emitted machine state; unchanged Orca G-code performs its own later transition.
ADR-0013.

### A-18 — blind configured retraction could double-retract
Severity: Critical

Finding:
Bambu filament overrides/wipe can produce a saved retraction state different from a naive configured-length command.

Resolution:
parse actual relative-E retraction debt; temporarily exact-unretract / print / exact-retract.
ADR-0018.

### A-19 — expected plugin rejection could abort a valid export
Severity: High

Finding:
RecoverableError/FatalError are not appropriate for normal unsupported cases in current Orca postprocess behavior.

Resolution:
expected validation/compatibility failures return Skipped and preserve original output.
ADR-0019.

### A-20 — plugin settings could stale a plan
Severity: High

Finding:
Orca config fingerprint alone does not cover plugin tolerance/h_min/seam/safety/speed settings.

Resolution:
mandatory PluginSettingsFingerprint equality at postprocess.
ADR-0023.

### A-21 — first layer requires a different physical model
Severity: High

Finding:
bed support/squish/first-layer flow semantics are outside the v1 material-support model.

Resolution:
no first-layer SubEdge refinement.
ADR-0024.

### A-22 — unreplicated dynamic extrusion features caused semantic divergence
Severity: High

Finding:
fuzzy skin intentionally changes geometry; filament adaptive volumetric speed changes execution limits not reproduced by v1.

Resolution:
both disabled for printable v1.
ADR-0028.

### A-23 — injected safe travel did not protect later Orca motion
Severity: Critical

Finding:
later original Orca travel/ZAA/extrusion was generated without candidate material and may collide with it.

Resolution:
mandatory downstream original-motion swept-clearance validation.
ADR-0025.

### A-24 — nozzle diameter does not define physical hotend clearance
Severity: Critical for physical claims

Finding:
Orca does not expose a full nozzle/hotend body envelope.

Resolution:
physical injection requires a versioned ToolClearanceProfile backed by manufacturer geometry, measurement, or another documented source.
ADR-0025.

### A-25 — standard Bambu/Orca features bypassed by injected paths
Severity: High

Finding:
injected paths do not traverse Orca normal role orchestration.

Resolution:
v1 rejects adaptive PA, role-change custom G-code, adaptive volumetric speed, arcs, and other unsupported features; uses conservative supported speed/state contract.
ADR-0020 / ADR-0028.

### A-26 — standard Bambu process may not be injectable unchanged
Severity: Expected compatibility gate

Finding:
normal Bambu process inheritance may enable arc fitting.

Resolution:
plugin reports analysis-only requirement; it never silently changes profile settings.

### A-27 — source mesh damage/orientation could create ambiguous sections
Severity: High

Resolution:
finite/manifold/section validity + orientation/material-side gates.
ADR-0027 / ADR-0030.

### A-28 — text-mode G-code rewrite could alter unrelated bytes
Severity: High for reproducibility

Finding:
text decoding/newline normalization can mutate original G-code outside insertion.

Resolution:
binary line-stream parser/emitter, local newline preservation, byte-for-byte untouched content, same-directory atomic temp flow.
ADR-0031.

## 4. Governance/document findings

### D-01 — duplicate ADR identifiers
Severity: Critical governance defect

Two different ADR-0025 files existed during the audit.

Resolution:
consolidated the decisions into one canonical ADR-0025 and deleted the accidental duplicate.
Current ADR identifiers are unique.

### D-02 — earlier duplicate ADR-0001–0005 family
Historical critical governance defect.

Resolution:
previously consolidated into canonical sequence; ADR_PROCESS forbids id reuse.

### D-03 — stale final-E field
SPECIFICATION previously retained a line saying SubEdgeSegment stored final E after ADR-0021 prohibited it.

Resolution:
removed; final E is execution-derived.

### D-04 — keep-out model naming drift
NozzleClearanceModel / NozzleKeepoutProfile / ToolClearanceProfile names diverged.

Resolution:
canonical name = ToolClearanceProfile.

### D-05 — formula escape corruption
Some Markdown formula text contained control characters from escaped backslashes.

Resolution:
rewrote normative formulas in plain deterministic text and scanned core normative docs for control characters.

### D-06 — handoff ADR range stale
Handoff still referenced ADR-0011 while canonical decisions advanced.

Resolution:
must be updated/stamped after this audit commit before repository review.

## 5. Deliberately unresolved items that are NOT Phase 0.5 software blockers

These remain explicit later gates:

1. Exact first production-compatible Orca release/commit.
2. Exact first Bambu machine/process/filament fixture set.
3. Physical ToolClearanceProfile dimensions/evidence.
4. Empirical bead-geometry calibration.
5. Exact Python lint/type dependency/tool versions after embedded-runtime verification.
6. Performance/resource limits before production release.

They block the relevant later gate, not the architecture-skeleton/reference-engine implementation.

## 6. Final consistency invariants

The canonical v1 now consistently states:

- stock Orca only;
- posSimplifyPath planning;
- psGCodePostProcess execution;
- immutable plan shared by preview and injector;
- centered Orca slice-space domain geometry;
- one object / one total instance / one ModelPart;
- finite/manifold/oriented source geometry;
- boundary != nozzle centerline;
- constant-Z added path, independently optimized between paths;
- 0.08 mm = effective bead height, not neighbor-Z spacing;
- candidate seam/gap frozen before preview;
- geometric volume != commanded/calibrated volume;
- no structural-wall rewrite;
- final E derived after quantized machine mapping;
- actual emitted state restoration;
- exact parsed retraction preservation;
- safe-ceiling injected travel;
- downstream original-motion clearance;
- ToolClearanceProfile required for physical mode;
- binary byte-preserving streaming mutation;
- expected failures return Skipped;
- no physical printing before fixtures + full gates + blind review.

## 7. Implementation readiness

Specification/architecture readiness: PASS.

Stock-Orca API feasibility for narrowed v1: PASS based on audited source.

Physical-model proof: NOT YET — intentionally deferred to physical calibration gates.

Next required workflow step:
1. stamp docs/specs/adaptive-subedge-v1.md with the audited canonical commit;
2. run review-only repository validation;
3. if disposition is validated, start Phase 0.5 architecture skeleton implementation.

## 8. Audit evidence baseline

Primary source-level audit baseline:
OrcaSlicer main commit 789f848694b955d293ca6b277d1c8046aa6f7436.

Current public docs were also checked for:
- Python Plugin System availability;
- SlicingPipeline behavior;
- psGCodePostProcess semantics;
- Z Contouring behavior.

Any future supported Orca version requires compatibility revalidation rather than assuming this audit remains valid.
