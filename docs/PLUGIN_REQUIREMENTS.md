# Plugin Requirements — Stock Orca Printable v1

## 1. Compatibility baseline

Initial technical audit baseline:
OrcaSlicer main 789f848694b955d293ca6b277d1c8046aa6f7436 (2026-09-29).

Supplementary drift audit:
OrcaSlicer main 1a5f91d727f43d455b40ab475a00d622b34648e0 (2026-10-02).

The Python SlicingPipeline binding files audited for the core plugin seam remain compatible across those checks, while Orca G-code generation and profile content continue to evolve. Production injection support is therefore always pinned to an exact Orca + machine/process/filament fixture family.

Unknown API/source/profile behavior => analysis-only.

## 2. Python/runtime

Current audited bundled Python remains 3.12.13.

Target package initially requires Python >=3.12 and NumPy, subject to Phase 0.5 runtime verification.

No unreviewed runtime dependency may be added.

## 3. Capabilities

One pure-Python plugin package provides:
- SlicingPipeline capability: posSimplifyPath analyzer and psGCodePostProcess injector.
- Script/UI capability: preview and diagnostics.

No UI calls from slicing workflow callbacks.

## 4. Required Orca data/bindings

Compatible Orca must expose enough data for:
- Print / PrintObject / Layer / LayerRegion;
- Print-owned Model snapshot;
- ModelObject / ModelInstance / ModelVolume;
- source mesh vertices/triangles and manifold state;
- instance/volume/PrintObject transforms;
- PrintObject bounding box;
- simplified 3D ExtrusionPath points;
- width/height/mm3_per_mm/role;
- geometry-time resolved config;
- ctx.config_value() during postprocess;
- current plugin get_config() during both hooks.

Missing required contract disables the affected capability.

## 5. Printable source topology

Physical injection requires:
- one PrintObject;
- one total source ModelInstance;
- one positive ModelPart volume;
- exactly one connected closed triangle shell;
- no NegativeVolume / ParameterModifier / helper CSG volume;
- finite valid vertices/triangle indices;
- manifold topology;
- deterministic orientation/material-side resolution;
- independent inside/outside parity;
- centered-frame parity;
- each printable target interaction section has one simple relevant outer loop;
- no target-region hole/disconnected/branched/self-intersecting section topology.

Unsupported topology may remain analysis-only.

## 6. Geometry semantics

All domain geometry uses centered Orca PrintObject slice-space.

Adapter:
- reconstructs centered frame per ADR-0012;
- validates orientation/material side per ADR-0030;
- unscales path XY;
- reconstructs ZAA absolute Z;
- reconstructs local ZAA geometry-directed volume behavior;
- copies data before live Orca references expire.

## 7. Fingerprints

Each immutable plan stores:
- ExecutionConfigFingerprint;
- PluginSettingsFingerprint.

At postprocess both are rebuilt and must match.

ExecutionConfigFingerprint includes resolved semantics for geometry/seam behavior, flow/material, retraction, motion/modal state, timelapse/wrapping/wipe-tower behavior, object-exclusion behavior, custom G-code, dynamic extrusion features, and profile compatibility.

At minimum it covers:
- nozzle diameter, seam settings, scarf/fuzzy/spiral/ironing/support/raft state;
- print_flow_ratio, filament_flow_ratio, set_other_flow_ratios, outer_wall_flow_ratio, filament diameter;
- fixed filament max volumetric speed and adaptive-volumetric-speed state;
- extrusion-rate smoothing / Pressure Equalizer state;
- relative E, firmware retraction, effective retract length/speeds, restart extra and relevant wipe semantics;
- units/XYZ/E mode assumptions, M200/M220/M221 compatibility;
- outer-wall speed and external-wall acceleration limit;
- XY/Z travel speeds, Z hop, printable-height limits, z_offset and active extruder XY offset;
- timelapse_type, farthest_point_timelapse, time_lapse_gcode identity, wrapping detection, actual wipe/prime tower semantics;
- exclude_object and object-label diagnostics;
- adaptive PA, role-change custom G-code, before/layer-change G-code, classic post_process, slicing-pipeline capability set.

PluginSettingsFingerprint includes:
- quality/error tolerance;
- optimizer/search/cost settings;
- h_min;
- candidate seam/gap policy;
- ToolClearanceProfile id/version/margins;
- candidate speed cap;
- max_subedge_acceleration_mm_s2;
- safety/validation tolerances;
- other plugin-owned execution policy.

Missing/mismatched value => Skipped.

## 8. Candidate path contract

Printable SubEdgePath:
- constant command Z;
- explicit open path;
- deterministic planned seam/start/gap;
- ordered SubEdgeSegments;
- deterministic execution order;
- acyclic support dependency graph.

SubEdgeSegment contains local support Z, effective height, geometric mm3/mm, commanded mm3/mm, and speed-limit intent.

Final E and machine coordinates are not plan-owned.

## 9. Flow/E contract

For supported candidate extrusion:

q_cmd = q_geom * print_flow_ratio * filament_flow_ratio * role_factor

where role_factor is the applicable outer-wall ratio under the pinned Orca semantics.

Final E is derived only after final machine XYZ quantization.

Global calibration ratios are not directly treated as physical bead-geometry multipliers.

## 10. Printable geometry gates

Requires:
- no first-layer refinement;
- nested/self-supported top-facing target;
- chronological support only from already-printed material;
- no cyclic support dependency;
- no bridge/support-dependent target;
- no unresolved candidate crossing/clearance;
- fuzzy skin off for target;
- unambiguous simple target section.

## 11. Modal execution envelope

At every physical injection anchor:
- millimeter units;
- absolute XYZ;
- relative E;
- firmware volumetric-E mode off;
- M220 = 100%;
- M221 = 100%;
- no unsupported G92 XYZ-origin remap;
- logical E and physical retraction debt separately tracked.

G92 E must not erase physical retraction state.

Feed and supported acceleration state are modal and restored exactly.

Physical validation assumes live printer speed/flow override remains 100%. Changing live overrides invalidates the validated run.

## 12. Printable process/runtime gates

Initial v1 requires:
- one tool / one physical filament execution context;
- no mixed-filament virtual slot/sublayer/gradient execution;
- relative E;
- firmware retract off;
- restart extra = 0;
- unambiguous positive saved retraction;
- known retract/deretract speeds;
- line numbers/checksums off;
- arc fitting off;
- adaptive PA off;
- filament adaptive volumetric speed off;
- extrusion-rate smoothing / Pressure Equalizer off;
- role-change custom G-code empty;
- spiral vase off;
- unsupported ironing off;
- scarf/sloped seam off;
- support/raft off;
- smooth timelapse off;
- farthest_point_timelapse off;
- wrapping detection off;
- no generated prime/wipe tower;
- exclude_object off;
- traditional timelapse only when exact fixture behavior is fully parser-supported;
- no classic post_process;
- no other slicing-pipeline capability;
- verbose G-code/comments on for initial physical fixture;
- supported layer-change custom code;
- normal non-calibration print;
- fresh matching plan;
- positive Z hop;
- printable-height margin;
- exact golden fixture.

The plugin reports unsupported settings; it never silently changes them.

## 13. Seam / final structural matching

Matcher tolerates normal Orca representation changes:
- cyclic seam start;
- seam split;
- collinear subdivision;
- one expected seam-gap clip;
- final translation/quantization.

Raw ordered path equality is insufficient.

Exactly one structural match is required.

## 14. Final structural deposition revalidation

After matching, reconstruct local actual final positive-E structural deposition around candidates.

Revalidate:
- lower support after real seam-gap clipping;
- h_min;
- hard candidate/structural overlap/clearance;
- hard tolerance where final deposition differs materially;
- relevant nearby inner/perimeter material.

Final candidate speed is also capped by the minimum relevant actual matched final external-wall feed.

Failure => Skipped; no reoptimization.

## 15. Execution-frame mapping

Plan geometry remains centered print-space.

Final matcher derives one constant (dx, dy, dz) from multiple references.

Reject nonconstant mapping, scale, rotation, shear, or ambiguity.

Only G-code layer applies the translation.

## 16. Formatter parity

For the currently audited Orca formatter:
- XYZ/F = 3 decimals;
- E = 5 decimals;
- midpoint rounding matches C++ std::round.

Unknown formatter contract => no injection.

Quantized zero-length segments or nonzero-material segments quantizing to unusable E are rejected.

## 17. Speed / volumetric / acceleration / jerk limits

Candidate speed is bounded by:
- resolved outer-wall speed;
- fixed filament max volumetric speed / q_cmd;
- minimum relevant actual matched final-wall feed;
- optional lower plugin speed cap.

Printable v1 does not emit acceleration or jerk/cornering commands.

At anchor:
- active acceleration must be parser-known, finite, positive;
- active acceleration <= plugin max_subedge_acceleration_mm_s2;
- plugin acceleration cap <= exact fixture external-wall acceleration limit;
- active fixture-supported cornering/jerk state must be known;
- for classic jerk semantics, active XY jerk <= plugin max_subedge_jerk_mm_s;
- plugin jerk cap <= exact fixture external-wall jerk limit.

Unknown/excessive acceleration or unsupported/excessive cornering state => Skipped.

## 18. Retraction/state behavior

Parser reconstructs actual final state.

Candidate cycle:
- travel while saved-retracted;
- exact temporary unretract;
- print;
- exact re-retract;
- return in identical saved retraction state.

The plugin does not reproduce wipe during its temporary cycle.

## 19. Safe-ceiling travel

All plugin non-extruding XY moves occur at Zsafe.

Zsafe uses actual saved Z, target upper machine Z, and positive active Z hop.

Zsafe must remain within active tool printable height.

## 20. Final chronological tool clearance

Physical v1 validates all relevant plugin-generated and resumed original Orca motions.

The validator uses chronological printed material, not future material.

One versioned ToolClearanceProfile is authoritative.

Its dimensions come from documented manufacturer geometry, measurement, or another explicit physical source.

Any uncertain/forbidden swept-volume intersection => Skipped.

No ToolClearanceProfile => analysis-only.

## 21. Attempt-scoped execution / TOCTOU

Every postprocess invocation has a unique InjectionAttemptId and separate attempt record.

Plans are atomically published immutable objects.

Postprocess:
- snapshots candidate plans under lock;
- records SourceFileIdentity/digest in validation pass;
- rechecks digest during copy;
- rechecks source metadata/identity before replace;
- rechecks PluginSettingsFingerprint immediately before commit.

Concurrent/repeated export/upload attempts keep separate evidence.

A single mutable status per plan is not authoritative.

## 22. Binary file processing

Postprocessor:
- binary line stream;
- untouched raw bytes preserved;
- local newline convention preserved;
- unsupported command bytes fail closed;
- same-directory temp;
- validated permission/atomic-replace behavior;
- validation first;
- sanity scan;
- idempotent;
- all-or-nothing.

Expected unsupported/validation condition:
- stable reason;
- PluginResult.Skipped;
- original file byte-for-byte unchanged.

## 23. Preview / estimate limitations

Standard Orca preview is pre-postprocess.

Plugin preview uses exact immutable plan plus attempt-derived runtime summary.

Orca original print time, filament/material statistics, and progress/M73 metadata may under-report the modified file.

v1 does not rewrite those metadata.

Plugin reports deterministic added path/material/time estimates separately.

## 24. Packaging

Pure-Python wheel; no custom Orca dependency.

## 25. Golden fixture requirement

No physical profile is injectable until fixtures record:
- exact Orca version/commit;
- exact machine/process/filament profiles;
- resolved semantic config;
- plugin settings;
- ToolClearanceProfile/evidence;
- source topology/section expectations;
- source G-code bytes/newline behavior;
- final structural deposition/seam-gap support;
- actual matched wall feed;
- parser/modal/retraction/acceleration state;
- timelapse/wrapping/wipe/exclude-object behavior;
- execution-frame mapping;
- quantization;
- speed/Zsafe limits;
- chronological tool-clearance expectations;
- attempt/source-identity behavior;
- expected output;
- idempotence;
- failure fixtures.

No fixture => analysis-only.

## 26. Compatibility default

Unknown source/API/profile/config/modal/timelapse/cancellation/tool-envelope/topology/coordinate/formatter/filesystem behavior => injection disabled.

Never best-effort mutate.
