# Full Consistency and Technical Feasibility Audit — 2026-10-08

Status: COMPLETE for renewed Phase 0.5 repository handoff
Audit class: current-Orca drift audit + numerical/model consistency + workflow evidence audit
Project branch: adaptive-subedge-design

## 1. Why this audit was required

The previous canonical audit baseline used OrcaSlicer main commit:

789f848694b955d293ca6b277d1c8046aa6f7436
(2026-09-29)

By 2026-10-08 Orca main had advanced to:

7d44b60ae4042b4de8c3844eb9dd2671c2d2d873

Key Orca source files used by Adaptive Sub-Edge had changed, so the old source audit could not simply be assumed current.

The repository also contained a workflow inconsistency:
the 2026-10-02 audit explicitly made the older Phase 0.5 review stale, but no corresponding 2026-10-02 review-only revalidation record existed.

This audit rechecks both technical and governance readiness.

## 2. Current-Orca contracts rechecked

Direct source review at current Orca main confirmed the core architecture still exists:

- SlicingPipeline remains research/experimental.
- posSimplifyPath remains available.
- psGCodePostProcess retains the intended working-file postprocess role.
- ctx.config_value() remains available for resolved configuration access.
- PluginHostSlicing still exposes live slicing graph objects with execute()-scoped lifetime and read-only 3D ExtrusionPath points.
- ZAA/ContourZ still stores path Z as a local relative offset d rather than absolute layer Z.
- GCode still converts local ZAA offset into emitted Z and local extrusion scaling.
- GCode point-to-machine conversion still has execution-frame effects not represented directly by plan coordinates.
- Orca process speeds remain mm/s while emitted G-code F is mm/min.

Therefore the stock-Orca analyzer -> immutable plan -> postprocess architecture remains feasible.

## 3. New Orca drift finding

### F-42 — Mixed-filament sublayer emission was not modeled
Severity: High

Current Orca GCode contains mixed-filament sublayer state including:
- m_sub_layer_flow_ratio
- m_sub_layer_height
- mixed_sub_layer_groups

That path can temporarily alter nominal Z and flow within a structural layer.

The previous v1 phrase "one tool / one filament" did not explicitly exclude virtual mixed-filament slot/sublayer semantics.

Resolution:
ADR-0042.
Printable v1 rejects mixed virtual filament / sublayer / gradient execution and fingerprints the relevant config.

## 4. Numerical/model findings

### F-43 — Rounded-rectangle area positivity did not fully define valid geometry
Severity: Medium-High

A positive area formula can still be used with width < height, while Orca's ordinary rounded extrusion model assumes width >= height in relevant Flow operations.

Resolution:
ADR-0043.
Candidate width/height bounds and width>=height are explicit Settings/invariants.

### F-44 — "Sufficient support" was implementation-defined
Severity: High

The previous support contract used terms such as sufficient overlap/contact without one authoritative metric.

Two implementations could accept different candidates.

Resolution:
ADR-0044.
SupportCoverageMetric is versioned and reports at minimum:
- supported area fraction;
- minimum contiguous support width;
- effective-height range.

Physical thresholds are fixture/calibration values, not invented constants.

### F-45 — E_max / E_p95 depended on unspecified sampling resolution
Severity: High

A coarse sampler can miss a local worst-case feature and produce a different tolerance decision from a fine sampler.

Resolution:
ADR-0045.
Hard error metrics require deterministic sample refinement and numerical convergence.

### F-46 — Inherited jerk/cornering was not bounded
Severity: Medium-High

v1 deliberately inherits machine acceleration/cornering state.
Acceleration had an explicit gate; jerk/cornering did not.

Current Orca has role-specific jerk settings.

Resolution:
ADR-0046.
The first fixture requires a known supported cornering state and a plugin jerk cap no greater than the fixture external-wall jerk contract.

### F-47 — One-sided surface error could miss absent material
Severity: Critical for geometry correctness

Predicted -> source sampling alone can miss a source patch when there is no predicted surface sample in that missing region.

Resolution:
ADR-0047.
Hard error is bidirectional:
- predicted -> source;
- source -> predicted.

Both directional maxima must pass tolerance.

### F-48 — Finite-bead "surface" did not yet define one 3D solid
Severity: High

Width, height and mm3/mm were defined, but corner sweep/end-cap/local transition geometry was not.

ZAA also creates an algebraic ambiguity if stale path.width, changed local height and scaled local volume are all imposed simultaneously.

Resolution:
ADR-0048.
NominalBeadSolidV1 defines:
- stadium cross-section;
- vertical placement;
- segment sweep/union;
- flat axial caps;
- ZAA effective width derived from local q/h.

### F-49 — Canonical hashing bytes were not defined
Severity: High and direct Phase 0.5 blocker

"Deterministic hash" without exact float/map/array encoding can diverge across implementations/platforms.

Resolution:
ADR-0049.
Canonical serialization now defines:
- SHA-256;
- exact finite binary64 encoding;
- -0 normalization;
- NaN/Inf rejection;
- mapping order;
- array dtype/shape/logical order;
- runtime-field exclusion.

### F-50 — Closest-surface correspondence could jump to the wrong nearby face
Severity: High

Thin walls/concavities can make an unrelated nearby surface Euclidean-closest.

Resolution:
ADR-0050.
Correspondence is restricted to a local interaction patch/neighborhood with normal compatibility and bounded search distance.

### F-51 — Orca slice compensation could conflict with the source-mesh target
Severity: High

Current Orca intentionally modifies slice contours using settings such as:
- xy_contour_compensation;
- xy_hole_compensation;
- elephant-foot compensation;
- make-overhang-printable;
- slicing/closing modes.

Treating the raw source mesh as the target while allowing those modifications can make the plugin counteract intentional Orca dimensional correction.

Resolution:
ADR-0051.
The first printable fixture gates relevant geometry modifiers or excludes affected layers.

### F-52 — Speed units were implicit at the emitter boundary
Severity: Critical implementation hazard

Orca config speeds are mm/s.
G-code F is mm/min.

Current Orca source explicitly multiplies extrusion/travel speed by 60 before F emission.

Resolution:
ADR-0052.
Only the execution adapter converts:
F_mm_min = speed_mm_s * 60.

### F-53 — Arbitrary-Z mesh sections lacked a deterministic degeneracy policy
Severity: High

Candidate planes passing through source vertices/horizontal facets can produce implementation-dependent duplicate/open/branched sections.

Resolution:
ADR-0053.
MeshSectionPolicy:
- excludes candidate Z degeneracy bands;
- defines classification/join tolerances;
- requires a single simple closed degree-2 relevant section;
- never silently nudges selected Z.

## 5. Minor document defect

### D-08 — Duplicate candidate-speed cap bullet
Severity: Low

SPECIFICATION contained the optional lower plugin speed cap twice.

Resolution:
removed during this audit.

## 6. Workflow/governance finding

### G-01 — Review evidence was stale after the 2026-10-02 audit
Severity: High for implementation authorization

FULL_CONSISTENCY_AUDIT_2026-10-02.md explicitly required repository revalidation against its new manifest, but docs/implementation contained only the older 2026-10-01 validated review.

Therefore Phase 0.5 could not correctly be treated as currently validated.

Resolution plan:
- create this 2026-10-08 audit;
- create a new exact blob manifest through ADR-0053;
- restamp the v1 handoff;
- run a fresh review-only Phase 0.5 repository revalidation;
- only that new review may authorize Phase 0.5 implementation.

## 7. Orca source drift conclusion

Current Orca main changed materially since the old baseline.

Core plugin/ZAA/postprocess contracts used by the architecture still exist, but new execution behavior appeared.

Therefore future compatibility policy is:

- do not infer compatibility from version number alone;
- each supported Orca release/commit has an explicit CompatibilityDescriptor;
- source-sensitive contracts are rechecked when the pinned baseline changes;
- newly introduced structural/G-code modes are analysis-only until modeled or gated.

The new current source audit reference is:

7d44b60ae4042b4de8c3844eb9dd2671c2d2d873
(2026-10-08)

## 8. Remaining risks that are not current logical contradictions

These remain empirical/physical later-phase risks:

1. Real bead geometry differs from NominalBeadSolidV1.
2. Segment-local commanded-flow steps may create pressure transients.
3. Cooling/fan/thermal state affects bead shape and bonding.
4. ToolClearanceProfile dimensions/margins require real hardware evidence.
5. Firmware bed compensation/input shaping can introduce physical effects not encoded as simple G-code geometry.
6. Start/stop seam blobs are not modeled by the nominal flat-cap solid.
7. Large-model optimizer/error/clearance computation cost is not yet benchmarked.
8. Postprocess-added time/material metadata limitations remain as documented by ADR-0041.

These do not authorize guessing.
They remain physical fixture/calibration/review gates.

## 9. Readiness disposition before new manifest/review

Canonical technical model after ADR-0053:
PASS for specification consistency.

Stock-Orca staged software architecture:
PASS, with the new current-Orca compatibility gates.

Phase 0.5 authorization:
PENDING until the 2026-10-08 manifest and fresh review-only validation are completed.

Physical printer injection:
NOT AUTHORIZED.

## 10. Next required workflow

1. update remaining normative docs/handoff to ADR-0053;
2. create AUDIT_REVISION_2026-10-08.md with exact current blobs;
3. verify every manifest entry and ADR uniqueness;
4. perform review-only Phase 0.5 repository validation;
5. if validated, Phase 0.5 may begin on a separate implementation branch/PR;
6. all later phases remain independently gated.
