# Implementation Specification — Stock Orca Plugin v1

This document is normative together with `AGENTS.md`, `docs/SPECIFICATION.md`, `docs/ARCHITECTURE.md`, and Accepted ADRs.

If repository evidence contradicts this contract, stop the affected implementation work and return to specification adjudication.

## 0. Implementation preconditions

Production source implementation MUST NOT start until:

1. the full consistency/technical audit is complete;
2. `docs/specs/adaptive-subedge-v1.md` references the audited canonical commit;
3. a review-only pass using `.codex/repository-review.md` records disposition `validated`;
4. a task record under `docs/implementation/` names the approved scope and verification plan.

Specification/design work and production implementation normally use separate PRs.

## 1. Audited external baseline

Technical assumptions in this document were rechecked against OrcaSlicer main commit:

`789f848694b955d293ca6b277d1c8046aa6f7436`

dated 2026-09-29.

This is an audit baseline, not automatically the production compatibility claim.

Actual injectable Orca releases/commits require golden fixtures and compatibility descriptors.

## 2. Canonical architecture

Use stock Orca + one Python plugin package.

Capabilities:
- SlicingPipeline:
  - `posSimplifyPath` -> analysis/plan creation;
  - `psGCodePostProcess` -> final validated injection.
- Script/UI capability:
  - preview/diagnostics.

No custom Orca C++ in v1.

Original Orca structural extrusion remains untouched.

## 3. Normative ADR set

Read all non-superseded ADRs relevant to the task.

As of this audit:
- ADR-0001 through ADR-0009;
- ADR-0010 is superseded by ADR-0015;
- ADR-0011 through ADR-0053, subject to explicit supersession notes.

Later ADRs override earlier clauses only where stated.

## 4. Required source layout

```text
adaptive_subedge/
  domain/
    geometry.py
    metrics.py
    plan.py
    settings.py
    status.py
    errors.py
  engine/
    bead_model.py
    flow_model.py
    error_estimator.py
    mesh_section.py
    material_side.py
    surface_band.py
    candidate_generator.py
    z_optimizer.py
    support.py
    collision.py
    cost_model.py
  application/
    analyzer.py
    plan_store.py
    execution_status.py
    serialization.py
    hashing.py
  ports/
    mesh_section_provider.py
    plan_repository.py
    cancellation.py

orca_plugin/
  adapters/
    geometry_snapshot.py
    orca_config.py
    transforms.py
    fingerprint.py
  compatibility/
    orca_contract.py
    bambu_contract.py
  capabilities/
    slicing.py
    preview.py
  ui/
    preview_model.py
    preview_renderer.py
  gcode/
    lexer.py
    parser.py
    state.py
    matcher.py
    execution_frame.py
    quantization.py
    retraction.py
    tool_clearance.py
    anchors.py
    validation.py
    emitter.py
    injector.py
    atomic_writer.py

tests/
  architecture/
  unit/
  analytic/
  integration/
  fixtures/
    orca/
    gcode/
    plans/
  regression/
  printer/
```

Do not introduce a generic `utils.py`.

## 5. Package/runtime metadata

Initial audited Orca plugin examples use Python >=3.12 and NumPy.

Phase 0.5 MUST verify the actual target Orca runtime before finalizing wheel metadata.

Dependencies are explicit and justified.

Do not add geometry/G-code libraries merely for convenience without dependency review.

## 6. SlicingPipeline execution model

### 6.1 posSimplifyPath

Use `posSimplifyPath`, not `posContouring`.

Reason:
- after Z Contouring;
- after `simplify_extrusion_path()`;
- available for freshly processed objects even when ZAA is not required.

Cache-loaded plugin-final objects may skip the geometry hook.

If no current-session matching plan exists at export, injection is skipped.

### 6.2 psGCodePostProcess

At this step:
- `ctx.print is None`;
- `ctx.object is None`;
- `ctx.gcode_path` is the working export;
- `ctx.config_value()` is available from the final full config;
- hook may run multiple times on separate working copies;
- standard Orca preview is pre-postprocess.

## 7. Snapshot eligibility gates

`geometry_snapshot.py` checks/copies the one-object v1 domain.

Printable eligibility requires:
- exactly one PrintObject;
- exactly one total source ModelInstance;
- exactly one positive ModelPart volume;
- exactly one connected closed triangle shell;
- no NegativeVolume/ParameterModifier or equivalent CSG/modifier volume;
- finite valid triangle coordinates/indices;
- manifold topology plus deterministic orientation/material-side validation;
- one tool / one filament execution context;
- target geometry nested/self-supported;
- every printable target section has one simple relevant outer loop with no target-region hole/disconnected/branched topology;
- target not bridge/support-dependent.

Unsupported models may produce analysis-only diagnostics but no injectable plan.

## 8. Centered source-mesh reconstruction

Implement ADR-0012 exactly.

Inputs:
- source ModelInstance matrix;
- source ModelVolume matrix/mesh;
- PrintObject.trafo();
- PrintObject.bounding_box();
- simplified path geometry.

Algorithm:
1. copy instance matrix;
2. remove affine XYZ translation to reproduce the no-offset instance transform;
3. transform ModelPart vertices by instance_no_offset @ volume transform;
4. compute raw transformed bbox center XY;
5. build centered PrintObject source transform using that center offset + PrintObject.trafo();
6. transform source mesh;
7. validate/construct the non-mutating consistent orientation view and deterministic material side per ADR-0030;
8. verify footprint/bounds/path parity.

Do not assume matrix storage/multiplication order; prove with fixtures.

Any parity failure => non-injectable.

## 9. Path coordinate normalization

For every Orca path point:
- XY = unscaled centered PrintObject path coordinates;
- ZAA raw Z component = relative offset.

Absolute centered-slice Z:

[
Z_{abs}=layer.print_z+unscale(z_{raw})
]

Store raw offset only for diagnostics/parity.

No engine module may call Orca `unscale`.

## 10. Structural segment flow normalization

For ZAA non-ironing segment endpoint offset (d):

[
h_{local}=path.height+d
]

[
r_{zaa}=h_{local}/path.height
]

The adapter records:
- nominal path width/height;
- local effective height;
- local geometric ZAA volume target;
- resolved global command-flow modifiers separately.

The engine never reads raw Orca config.

## 11. Resolved configuration adapter

orca_config.py is the single owner of raw Orca key/override resolution.

It produces typed resolved semantic configuration. No other module independently chooses machine-vs-filament override precedence.

Required semantic groups include:

Geometry / slicing:
- nozzle diameter;
- xy_contour_compensation / xy_hole_compensation;
- slicing_mode;
- slice_closing_radius or pinned equivalent morphology setting;
- make_overhang_printable semantics;
- elephant-foot compensation value/layer count;
- ZAA state/config used by snapshot diagnostics;
- seam gap and seam/scarf mode;
- spiral, ironing, support/raft, fuzzy-skin gates;
- source topology and print-sequence assumptions.

Flow:
- print_flow_ratio;
- mixed-filament virtual-slot/sublayer/gradient state required by ADR-0042;
- filament_flow_ratio;
- set_other_flow_ratios;
- outer_wall_flow_ratio;
- filament diameter;
- fixed filament max volumetric speed;
- filament adaptive-volumetric-speed gate.

Retraction:
- effective retract-on-layer-change state;
- effective retraction length;
- retraction speed;
- deretraction speed;
- restart extra;
- firmware-retraction state;
- wipe / retract-before-wipe / retract-after-wipe values required by the supported parser contract.

Motion:
- outer-wall speed;
- external-wall jerk / supported cornering semantics;
- resolved external-wall acceleration;
- dynamic acceleration feature state needed by fixture;
- XY travel speed;
- Z travel speed;
- active Z hop/lift;
- printable height / active-extruder printable height.

Execution feature gates:
- units / XYZ / E-mode assumptions;
- M200 volumetric-E state;
- M220/M221 runtime override assumptions;
- timelapse_type;
- farthest_point_timelapse;
- time_lapse_gcode identity;
- wrapping detection;
- wipe/prime tower presence;
- exclude_object / object labeling diagnostics;
- extrusion-rate smoothing / Pressure Equalizer state;
- relative-E state;
- arc fitting;
- line numbering/checksum;
- verbose G-code/comments;
- adaptive PA;
- static PA diagnostics;
- machine/filament/process extrusion-role-change G-code;
- before/layer-change G-code;
- classic post_process;
- selected slicing-pipeline capability list;
- calibration/profile-family invariants required by fixtures.

Exact raw-key mapping and override precedence are pinned in compatibility tests.

## 12. Execution and plugin settings fingerprints

During analysis:
1. build a versioned ExecutionConfigFingerprint from resolved Orca semantics;
2. validate Adaptive Sub-Edge Settings;
3. build a versioned PluginSettingsFingerprint from every plugin-owned value that can affect geometry, optimization, candidate seam/gap, ToolClearanceProfile, margins, speed cap, max_subedge_acceleration_mm_s2, max_subedge_jerk_mm_s, candidate bead width/height bounds, support-coverage metric thresholds/tolerances, error-estimator sampling/refinement/convergence, or execution policy.

At psGCodePostProcess:
- rebuild ExecutionConfigFingerprint with ctx.config_value();
- rebuild PluginSettingsFingerprint from the capability current get_config() value.

Injection requires exact equality for both fingerprints.

Missing/invalid/mismatched required semantics => PluginResult.Skipped.

Raw map order MUST NOT affect either canonical fingerprint.

PlanStore invalidation is useful but does not replace the final equality checks.

## 13. Immutable domain DTOs

Use frozen dataclasses or equivalent immutable typed structures.

ErrorMetrics:
- e_max_mm;
- e_rms_mm;
- e_p95_mm;
- signed_mean_mm.

ToolClearanceProfile:
- profile id/version;
- conservative radial keep-out as a function of height above nozzle tip;
- modeled axial height;
- radial and vertical margins;
- hardware fixture identity/evidence reference.

StructuralPathSegment:
- centered print-space start/end XYZ;
- width;
- nominal/effective local height;
- local geometric ZAA volume;
- command-flow modifier summary;
- role/layer metadata.

StructuralLoopReference:
- canonical closed geometry;
- length/bounds/orientation metadata;
- resolved seam-gap allowance;
- representative non-collinear anchors;
- canonical shape hash.

SurfaceBand:
- target material boundary;
- residual error region;
- support/nesting metadata.

SubEdgeSegment:
- high-precision print-space start/end XY;
- parent path constant command_z_mm;
- local support Z;
- effective bead height;
- width;
- geometric_mm3_per_mm;
- commanded_mm3_per_mm;
- speed limit/request metadata;
- support/validation metadata.

SubEdgeSegment does NOT contain authoritative final machine XYZ or final emitted E.

SubEdgePath:
- path id;
- interval/error-region id;
- immutable constant command_z_mm;
- explicit open execution polyline;
- planned seam/start and gap metadata;
- ordered segments;
- path ordering/travel metadata.

InsertionAnchor:
- target structural interval;
- supported Bambu layer-boundary signature;
- associated StructuralLoopReference ids;
- matching tolerances/profile contract.

SubEdgePlan:
- schema/plugin version;
- plan id/hash;
- compatibility descriptor;
- source geometry hash;
- ExecutionConfigFingerprint;
- PluginSettingsFingerprint;
- baseline references;
- candidate paths;
- anchors;
- metrics;
- geometric/commanded volume and time estimates;
- injectability/reason.

Exclude timestamp, runtime ObjectID, final machine translation, final E, and runtime status from plan hash.

AnalysisGenerationId:
- process-local lifecycle identifier;
- excluded from deterministic plan hash.

InjectionAttemptId:
- unique per psGCodePostProcess invocation.

InjectionAttemptRecord:
- attempt id;
- selected plan hash;
- source working-file identity;
- compatibility/fingerprint results;
- monotonic state transition;
- terminal outcome/reason.

There is no single overwrite-prone mutable per-plan status as the authoritative runtime record.

## 13A. Canonical serialization and hashing

Phase 0.5 follows ADR-0049 exactly.

Canonical identity rules:
- SHA-256, lowercase full 64-hex authoritative digest;
- one versioned tagged UTF-8 canonical grammar;
- mapping keys sorted lexicographically;
- enums use stable documented string values;
- finite binary64 floats encoded by exact hexadecimal form;
- -0.0 normalized to +0.0;
- NaN/Inf rejected;
- arrays use explicit semantic dtype/shape/logical C-order canonical digest;
- runtime-only fields excluded by schema;
- Python repr/pickle/default JSON float formatting are forbidden identity mechanisms.

application/serialization.py and application/hashing.py are the only owners.

All NumPy arrays crossing the adapter boundary:
- are copied into plugin ownership;
- are marked non-writeable;
- have no Orca-backed base/reference.

No live pybind object survives `execute(ctx)`.

## 15. Analyzer workflow

At posSimplifyPath:

1. check cancellation;
2. validate one-object/one-total-instance/one-ModelPart topology;
3. validate finite/manifold source mesh, shared-edge orientation/global material side, mirrored-transform semantics, and candidate-section assumptions;
4. resolve semantic Orca config;
5. validate plugin Settings and ToolClearanceProfile metadata;
6. build ExecutionConfigFingerprint and PluginSettingsFingerprint;
7. reconstruct centered source mesh;
8. copy/normalize final simplified structural paths;
9. build ZAA-aware structural baseline;
10. discard live Orca references;
11. build nominal finite-bead baseline;
12. estimate residual error;
13. exclude first-layer/fuzzy/unsupported regions from printable planning;
14. derive residual surface bands;
15. generate constant-Z centerline candidates;
16. resolve deterministic candidate seam/gap before scoring;
17. resolve local support/effective height;
18. compute geometric segment volume;
19. compute commanded segment volume separately;
20. enforce support/candidate collision/geometry/speed feasibility;
21. optimize candidate set deterministically;
22. create StructuralLoopReferences and insertion intent;
23. create immutable plan;
24. store plan + PLANNED status in PlanStore.

Expensive loops poll cancellation at bounded intervals.

UI is never called here.

## 16. Geometric flow model

For supported non-bridge rounded-rectangle v1 beads:

q_geom = h * (w - h * (1 - pi/4))

The nominal finite-bead predictor uses geometric volume/height, not global calibration multipliers.

## 17. Commanded flow model

For v1 external-surface candidate:

q_cmd = q_geom * print_flow_ratio * filament_flow_ratio * role_factor

role_factor = outer_wall_flow_ratio when set_other_flow_ratios is enabled, otherwise 1.

Global flow ratios affect G-code/material commands and volumetric-speed limits, not the nominal geometric bead envelope.

## 18. Local support / minimum height / coverage metric

For each candidate segment:

h_eff = nozzle_z - support_z

Initial 0.4 mm-nozzle minimum = 0.08 mm.

Do not enforce pairwise candidate-Z spacing of 0.08 mm.

Local support, bead overlap, clearance, path crossing, and final quantization determine feasibility.

Support acceptance uses only the versioned ADR-0044 SupportCoverageMetric owned by the engine and the conservative convergence policy from ADR-0058.

Hard acceptance uses conservative bounds:
- supported_area_fraction_lower_bound;
- minimum_contiguous_support_width_lower_bound_mm;
- minimum_effective_height_lower_bound_mm;
- maximum_effective_height_upper_bound_mm.

Unresolved footprint cells are deterministically refined. Unresolved cells at the maximum refinement level count as unsupported. Area/contiguous-width/effective-height metrics must converge under the versioned support refinement settings before a candidate can be injectable.

Thresholds and refinement/convergence settings are validated Settings and participate in PluginSettingsFingerprint. Do not implement ad-hoc "sufficient overlap" logic in candidate_generator/support/collision modules.

## 19. Surface-band planning

Mesh intersection is boundary geometry only.

`surface_band.py` derives centerlines inside material.

Planner supports:
- multiple same-Z centerlines;
- multiple different-Z centerlines;
- segment-local support/flow.

Printable v1 requires nested/self-supported target bands.

## 19A. Mesh section policy

mesh_section.py owns ADR-0053 MeshSectionPolicy as refined by ADR-0059.

Do not build broad positive-width forbidden bands around every ordinary source vertex Z.

For each section Z:
- classify vertices with one explicit section_predicate_epsilon_mm;
- merge intersections using canonical source edge/vertex topology identity before geometric snapping;
- handle vertex-on-plane and coplanar-edge events using manifold incident topology;
- reject unresolved coplanar facet patches only at the explicit numeric event tolerance;
- join with mesh_section_join_tolerance_mm;
- require one simple closed degree-2 relevant component;
- validate orientation/material side;
- reject unresolved open/branched/hole/self-intersecting ambiguity.

Before plan finalization, prove section topology/material-side/geometry stability across the possible final Orca Z-quantization uncertainty interval. Dense mesh vertex Z values alone must not erase the candidate search space.

The sectioner MUST NOT perturb selected command Z after optimization.

All predicate/join/quantization-stability tolerances participate in PluginSettingsFingerprint.

## 20. Optimizer

Initial implementation may use deterministic bounded grid/beam search.

Inputs:
- source boundary/error field;
- structural nominal bead envelope;
- support envelope;
- candidate physical bounds;
- error tolerance;
- cost weights;
- speed/volumetric constraints.

For each candidate set:
- simulate chronological support in immutable execution order using the authoritative SupportCoverageMetric;
- reject any future-material or cyclic support dependency;
- validate candidate geometry/collision;
- predict the separate completed FinalSurfaceEnvelope;
- compute required error metrics;
- score cost;
- choose minimum-cost feasible set.

No G-code dependency.

## 20A. Bidirectional converged error estimator

Hard tolerance decisions use ADR-0045 + ADR-0047 + ADR-0050.

The estimator computes both predicted->source and source->predicted directional metrics. Missing target material is therefore a hard error, not an absent sample.

Surface correspondence is restricted to the paired interaction region and configured normal/distance compatibility, while ADR-0060 expands that local domain to a conservative AffectedSurfaceDomain containing every exposed source/predicted surface that the candidate bead solid can change. No candidate-created or occluded exposed material may fall outside scoring. No global nearest-surface shortcut.

The versioned ErrorEstimatorConfig includes:
- initial_error_sample_spacing_mm;
- error_refinement_factor;
- error_metric_convergence_mm;
- max_error_refinement_levels;
- closest/sign tolerance version;
- max_surface_correspondence_distance_mm;
- min_surface_normal_dot;
- interaction-neighborhood tolerance/version;
- normal-ray/fallback policy version;
- explicit directional optimizer weights.

The estimator refines deterministic samples until every hard metric used by acceptance converges within the configured threshold.

Hard tolerance applies independently to both directional maxima.

Public summaries use ADR-0047 aggregation, not concatenated sample-count weighting.

Non-convergence, an unclosed affected domain, or unresolved/ambiguous correspondence => candidate infeasible / final revalidation Skipped.

Optimizer and FinalStructuralDepositionContext revalidation use identical estimator/correspondence semantics; neither may silently choose its own sampling resolution or nearest-surface policy.

## 21. PlanStore and attempt store

PlanStore is process-local, thread-safe, bounded.

Plans are fully constructed before atomic publication. No partial plan is visible.

Postprocess takes an immutable candidate-plan snapshot under lock and releases the lock before long parsing.

InjectionAttemptStore is the single owner of attempt-scoped runtime evidence and monotonic attempt-state transitions.

On each fresh applicable analysis generation:
- store immutable plan;
- mark current session/generation;
- invalidate or age stale incompatible candidates deterministically.

At export:
1. allocate InjectionAttemptId and snapshot candidate plans;
2. require current PluginSettingsFingerprint equality;
3. require current ExecutionConfigFingerprint equality;
3. filter to current-session injectable plans;
4. use final G-code structural matcher;
5. exactly one plan must survive.

Zero or multiple matches => Skipped.

Never rerun optimizer from G-code.

## 22. Preview

Script/UI capability reads immutable plan + status.

Display:
- centered source/structural baseline;
- residual boundary/surface band;
- candidate paths/segments;
- geometric versus commanded flow;
- local bead-height range;
- support/nesting and candidate dependency/order diagnostics;
- error metrics;
- compatibility gates;
- plan hash/status.

Preview may not mutate or regenerate the plan.

## 23. Binary streaming G-code parser

No regex-only mutation.

Read the working file as a binary line stream. Preserve raw line bytes. Parse only the ASCII-compatible command/token subset required by the supported fixture. Do not decode with errors=replace and do not normalize newlines.

Track at minimum:
- G20/G21 units;
- G90/G91;
- M82/M83;
- actual X/Y/Z;
- relative E moves;
- active tool;
- feed;
- M220 firmware feed override;
- M221 firmware flow override;
- retraction state;
- supported acceleration/modal state;
- layer/reserved tags;
- object/type/comment context;
- supported Bambu custom layer-change markers;
- idempotence markers.

Printable v1 additionally requires actual anchor state G21-equivalent millimeters, G90 absolute XYZ, M83 relative E, M220=100%, and M221=100%. Unknown/non-unity mode or override state => Skipped.

Parser must scale to large files without loading the full G-code into memory. It operates on binary lines, preserves untouched raw bytes, parses only the supported ASCII-compatible command/token subset, and never uses errors=replace or universal-newline normalization.

## 24. Structural-loop matcher

Do not compare ordered raw point lists.

For each planned StructuralLoopReference, matcher accepts only geometry consistent with:
- cyclic seam start change;
- seam split;
- collinear subdivision;
- one expected seam-gap clipping interval.

Resolve seam-gap mm using the pinned Orca semantics (for audited source, `seam_gap.get_abs_value(nozzle_diameter)`).

Scarf and G2/G3 target paths remain unsupported.

Geometry match must provide:
- unique candidate;
- bounded distance error;
- compatible length loss;
- multiple non-collinear anchor correspondences.

Comments/tags are supporting evidence only.

## 24A. Final structural deposition revalidation

After structural-loop matching but before candidate execution derivation, reconstruct FinalStructuralDepositionContext from the actual final G-code around each candidate region.

Include relevant:
- lower/upper external wall;
- nearby positive-E structural material within support/collision distance;
- seam-gap clipping;
- quantized coordinates;
- actual feed.

Revalidate against immutable plan/reference geometry:
- chronological support;
- h_min;
- hard overlap/overbuild;
- hard tolerance where final seam/quantization materially changes the region.

Any mismatch => whole injection Skipped. No re-optimization.

The minimum relevant actual matched final external-wall feed is a mandatory candidate speed ceiling.

## 25. Execution-frame resolver

After unique structural matching:

1. derive candidate ((dx,dy,dz)) translations from multiple matched references;
2. require one constant translation within compatibility tolerance;
3. reject rotation/scale/shear/non-constant mapping;
4. store immutable `ExecutionFrameTranslation` for the postprocess attempt.

Only G-code code may apply it.

## 26. Orca-compatible quantizer

`quantization.py` owns formatter parity.

Audited compatibility contract:
- XYZ/F: 3 decimals;
- E: 5 decimals;
- half-away-from-zero semantics matching C++ `std::round`.

Do not use Python built-in `round()` as the parity implementation.

## 27. Execution command derivation

The immutable plan does NOT store final E.

For each SubEdgeSegment:

1. apply execution-frame translation;
2. quantize machine XYZ;
3. compute 3D emitted segment length from quantized coordinates;
4. use stored `commanded_mm3_per_mm`;
5. calculate:

[
E_{raw}
=
L_{quantized}
cdot q_{cmd}
/ A_{filament}
]

6. quantize E;
7. reconstruct quantized execution geometry/material;
8. rerun execution-critical validity checks.

Any invalidity => whole injection Skipped.

## 28. Speed and acceleration limits

For each segment:

v_vol = filament_max_volumetric_speed / q_cmd

v_segment must not exceed:
- resolved outer-wall speed;
- v_vol;
- optional lower plugin speed cap;
- minimum relevant actual matched final-G-code external-wall feed in the target neighborhood.

q_cmd is the Orca-compatible commanded volumetric line flow.

Missing/non-positive safety bound => non-injectable.

Do not silently raise Orca speed.

Printable v1 does not emit acceleration commands.

At the insertion anchor:
- parsed active acceleration must be known, finite, and positive;
- active acceleration <= max_subedge_acceleration_mm_s2;
- max_subedge_acceleration_mm_s2 <= the exact fixture's resolved external-wall acceleration limit;
- active cornering state is parser-known for the pinned fixture;
- for classic jerk semantics, active XY jerk is finite/non-negative and <= max_subedge_jerk_mm_s;
- max_subedge_jerk_mm_s <= the exact fixture's resolved external-wall jerk limit.

Unknown/excessive acceleration or unsupported/excessive jerk/cornering semantics => Skipped.

## 29. v1 advanced-feature gates

Printable injection is disabled if:
- target is first-layer refinement;
- source/target topology violates the one-connected-shell/simple-section contract;
- smooth timelapse is enabled;
- farthest_point_timelapse is enabled;
- wrapping detection is enabled;
- generated prime/wipe tower execution is present;
- exclude_object is enabled;
- calibration/tower mode is detected;
- fuzzy skin is active for the target;
- filament adaptive volumetric speed is enabled;
- any mixed-filament virtual slot/sublayer/gradient execution is active;
- max_volumetric_extrusion_rate_slope > 0 (Pressure Equalizer / extrusion-rate smoothing enabled);
- adaptive pressure advance is enabled;
- machine/filament/process extrusion-role-change G-code is non-empty;
- firmware retraction is enabled;
- line numbering/checksum mode is enabled;
- arc fitting is enabled;
- spiral vase is enabled;
- unsupported ironing is enabled;
- scarf/sloped seam is enabled;
- support/raft is active;
- multitool/multifilament execution is present;
- classic post_process is non-empty;
- another slicing-pipeline capability is active;
- traditional timelapse behavior is not exactly fixture-known/parser-supported;
- verbose G-code/comments are disabled for the initial physical-fixture contract.

Static pressure advance may remain enabled. The plugin does not modify PA state.

The plugin reports unmet gates and never silently changes Orca settings.

## 30. Insertion anchor

Use supported Bambu layer-boundary marker/profile contract.

Do NOT assume physical Z already equals the upper nominal layer.

At the exact insertion point, parser snapshots `SavedMachineState`.

Calibration blocks or unknown motion custom code invalidate the anchor.

## 31. Retraction-state contract

Printable v1 requires:
- M83/relative E;
- firmware retract off;
- unambiguous positive saved retraction;
- ordinary restart-extra = 0;
- known effective retract/deretract speeds.

Candidate cycle:
1. safe travel while saved-retracted;
2. at candidate start unretract exactly saved amount;
3. print candidate;
4. retract exactly saved amount;
5. safe travel while retracted.

After final candidate, retraction state equals saved state.

Do not emulate wipe during temporary cycle.

## 32. Zsafe and travel

Use resolved active Z-hop/lift as initial v1 safe-ceiling lift.

Require:
- lift > 0;
- `Zsafe = max(saved_actual_Z, target_upper_machine_Z) + lift`;
- Zsafe within active extruder printable-height limit.

Use resolved:
- XY travel speed;
- Z travel speed.

For all injected travel:
- vertical raise first;
- no non-extruding XY below Zsafe;
- vertical descend at destination.

## 33. Actual state restoration

After the last candidate:

1. remain retracted;
2. rise to Zsafe;
3. return to saved X/Y at Zsafe;
4. descend to saved **actual emitted Z**;
5. restore feed and every plugin-changed supported modal state;
6. verify E/retraction equivalence;
7. resume original G-code unchanged.

Do NOT force nominal upper-layer Z or reproduce deferred Orca lift logic.

## 34. Idempotence

Markers:

```text
; ADAPTIVE_SUBEDGE_BEGIN plan=<hash> version=<plugin-version>
...
; ADAPTIVE_SUBEDGE_END plan=<hash>
```

If a complete matching block for the same plan is already present and validates, return Success/already-injected without duplicating.

Malformed/partial plugin markers => do not overwrite blindly; fail according to integrity policy.

## 35. Streaming all-or-nothing postprocess

Pass 1 — validation:
- allocate InjectionAttemptId and record STARTED;
- snapshot immutable candidate plans;
- record SourceFileIdentity including size/mtime/digest;
- validate PluginSettingsFingerprint;
- validate ExecutionConfigFingerprint;
- stream-parse actual machine/modal/retraction state;
- identify and seam-invariant-match all planned StructuralLoopReferences;
- reconstruct final structural deposition and revalidate support/hard geometry;
- derive one execution-frame translation;
- quantize and derive all candidate execution commands;
- validate speed/Zsafe/retraction;
- validate the complete quantized plugin-motion schedule plus unchanged downstream original motions using tool_clearance.py, the chronological printed-material state, and the versioned ToolClearanceProfile.

No file mutation.

Pass 2 — temp emission:
- re-open original in binary mode;
- recompute source digest while copying and require Pass-1 equality;
- create temp in the same directory;
- copy original raw bytes/line endings exactly;
- inject only fully prevalidated blocks at exact anchors using the validated local newline convention;
- preserve required original file mode/permissions.

Pass 3 — sanity:
- binary-stream parse temp;
- verify marker count/hash;
- verify injection count/order;
- verify state restoration and integrity;
- verify untouched original byte sequences remain identical outside insertion ranges;
- flush/fsync as supported before atomic replace.

Immediately before replace, re-read current plugin settings and require PluginSettingsFingerprint equality again; require source working-file identity/metadata unchanged. Only then atomically replace ctx.gcode_path and commit the attempt record.

Any earlier failure leaves original unchanged.

## 36. PluginResult mapping

Capability boundary follows ADR-0019.

Expected unsupported/validation failures:
- record stable SKIPPED reason;
- return `PluginResult.Skipped`;
- preserve original file.

Successful injection or valid already-injected no-op:
- return `Success`.

Unexpected exception with original provably untouched:
- record failure;
- return Skipped.

Cannot guarantee file integrity:
- FatalError.

Do not use RecoverableError for routine compatibility/validation failures.

## 37. Logging/observability

Structured compact diagnostics:
- plan hash;
- plugin version;
- Orca compatibility descriptor;
- config fingerprint;
- phase durations;
- candidate/segment counts;
- min/max effective height;
- geometric/commanded volume;
- structural match error;
- execution translation;
- quantization deltas;
- speed/volumetric margin;
- Zsafe margin;
- saved/restored state digest;
- final reason/status.

Do not log complete user models/G-code.

## 37A. Estimate/progress limitation

Because injection occurs after Orca's standard time/material/progress generation:
- standard Orca preview/time/material statistics are pre-postprocess;
- M73/progress/stat headers are not rewritten in v1;
- plugin reports deterministic added path/material/time estimates separately;
- physical benchmark truth comes from final modified G-code and/or printer measurement.

Do not present Orca's original estimate as the final SubEdge-modified estimate.

## 38. Postprocess time/cooling/metadata behavior

The injector does not rerun Orca CoolingBuffer/time-estimation/progress generation.

It:
- preserves original metadata bytes under ADR-0031;
- treats original total time/progress/filament-use metadata as pre-injection estimates;
- computes plugin-added path/travel/material/time estimates separately;
- does not alter fan/temperature/cooling commands in v1.

Fixture/physical tests must record thermal/cooling settings and compare estimated versus measured added time.

## 39. Architecture and quality gates

Before behavioral suites:
- syntax/import/package;
- architecture boundaries;
- configured lint/static/type/dependency checks.

Tests accompany behavior changes.

No physical printing until all software/fixture gates and independent review requirements pass.

## 40. Coding-agent hard rules

- read `AGENTS.md` first;
- no implementation without validated repository-review handoff;
- no custom Orca C++ in v1;
- use `posSimplifyPath`, not `posContouring`;
- no live Orca refs outside adapter callback;
- no direct `PrintObject.trafo @ volume.matrix` source transform;
- no mesh-boundary-as-nozzle-centerline;
- no pairwise 0.08 mm Z-gap assumption;
- no global-flow-ratio-as-geometric-bead-size assumption;
- no path-wide flow assumption when support varies;
- no final-E field in immutable plan;
- no candidate seam/gap changes in postprocess;
- no first-layer candidate injection;
- no blind trust in raw triangle normals/material side;
- no text-mode G-code rewrite or newline normalization;
- no injection without validated chronological plugin + downstream-original tool clearance and ToolClearanceProfile;
- no support from future material or cyclic candidate dependencies;
- no ordered raw-loop hash final matching;
- no direct print-space coordinate emission;
- no Python default rounding for Orca G-code;
- no precomputed authoritative final E in plan;
- no blind configured retraction;
- no nominal-layer-Z restoration assumption;
- no original structural flow rewrite in v1;
- no regex-only injector;
- no mandatory full-file in-memory rewrite;
- no partial output commit;
- no text-mode G-code rewrite or newline normalization;
- no raw-source-normal material-side assumption;
- no hidden settings changes;
- no implicit G20/G91 support in printable v1;
- no non-unity M220/M221 execution in printable v1;
- no assumption that one ModelPart implies one target loop;
- no unsupported-profile guessing;
- no mixed-sublayer structural emission in printable v1;
- no hidden bead geometry outside explicit width/height bounds;
- no geometry-target comparison while unsupported Orca slice-boundary modifiers are active;
- no hidden mesh-section epsilon or silent candidate-Z nudging;
- no mm/s value emitted directly as G-code F;
- no ad-hoc support threshold or unconverged error metric;
- no one-sided error metric that can hide missing material;
- no whole-model unconstrained nearest-surface correspondence;
- no alternate bead-solid implementation outside NominalBeadSolidV1;
- no non-canonical object/float/array hashing;
- no inherited jerk/cornering state outside the fixture contract;
- deterministic output for identical validated inputs;
- new safety/architecture semantics require ADR first.
