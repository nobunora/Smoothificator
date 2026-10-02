# Plugin Requirements — Stock Orca Printable v1

## 1. Compatibility baseline

Technical audit baseline:
OrcaSlicer main commit 789f848694b955d293ca6b277d1c8046aa6f7436, dated 2026-09-29.

Production injection support is enabled only for explicitly tested Orca release/commit + Bambu machine/process/filament fixture families.

Unknown plugin/API/source behavior => analysis-only.

## 2. Python/runtime

Initial audited Orca plugin examples require Python >= 3.12 and use NumPy.

Phase 0.5 verifies the actual target embedded runtime before wheel metadata is finalized.

## 3. Plugin capabilities

One package provides:
- SlicingPipeline capability:
  - posSimplifyPath analyzer;
  - psGCodePostProcess injector.
- Script/UI capability:
  - preview/diagnostics.

No UI calls from slicing workflow callbacks.

## 4. Required Orca bindings/data

Compatible Orca must expose enough data for:
- Print / PrintObject / Layer / LayerRegion;
- Print-owned Model snapshot;
- ModelObject / ModelInstance / ModelVolume;
- source mesh vertices/triangles and manifold diagnostics;
- instance/volume/PrintObject transforms;
- PrintObject bounding box;
- simplified 3D ExtrusionPath points;
- width/height/mm3_per_mm/role;
- resolved config in geometry callback;
- ctx.config_value() at postprocess;
- capability self.get_config() at both hooks.

Missing required contract disables the affected capability.

## 5. Printable source topology

Physical injection requires:
- one PrintObject;
- one total source ModelInstance;
- one positive ModelPart volume;
- exactly one connected closed triangle shell;
- no NegativeVolume/ParameterModifier/helper CSG volume;
- finite valid triangle mesh;
- current bound ModelVolume manifold;
- deterministic closed-mesh orientation/material-side validation, including mirrored transforms;
- centered-frame parity;
- every printable target interaction section has one simple relevant outer loop, with no hole/disconnected/branched/self-intersecting target topology.

Unsupported source topology remains analysis-only.

## 6. Geometry semantics

All domain geometry uses centered Orca PrintObject slice-space.

Adapter responsibilities:
- reconstruct centered frame per ADR-0012;
- unscale path XY;
- reconstruct ZAA absolute Z from relative path offsets;
- reconstruct ZAA local geometry-directed height/volume behavior;
- copy all data before live Orca references expire.

## 7. Fingerprints

Every plan stores:
- ExecutionConfigFingerprint;
- PluginSettingsFingerprint.

At psGCodePostProcess both are recomputed and must match exactly before final plan selection.

ExecutionConfigFingerprint covers resolved Orca semantics for:
- geometry/seam behavior;
- flow/material;
- retraction;
- motion/Zsafe/printable height;
- feature gates;
- custom layer/role G-code;
- plugin/postprocess environment.

PluginSettingsFingerprint covers plugin-owned values including:
- tolerance/cost/search policy;
- h_min;
- candidate seam/gap;
- ToolClearanceProfile id/version and margins;
- optional speed cap;
- execution safety margins/policy.

Missing or mismatched value => Skipped.

## 8. Candidate-path contract

Printable v1 SubEdgePath:
- constant command Z;
- explicit open path;
- deterministic planned seam/start/gap;
- ordered segment-local support/flow properties.

Postprocess may derive execution commands but may not change candidate geometry/seam/flow intent.

## 9. Flow contract

The plan separates:
- geometric mm3/mm for nominal bead prediction;
- commanded mm3/mm for G-code/material limits.

For supported external-surface semantics:

q_cmd = q_geom * print_flow_ratio * filament_flow_ratio * role_factor

role_factor = outer_wall_flow_ratio only when set_other_flow_ratios is enabled, else 1.

Final E is derived after machine-coordinate XYZ quantization.

## 10. Printable geometry gates

Injection requires:
- no first-layer refinement;
- nested/self-supported top-facing target;
- no bridge/support-dependent target;
- no unresolved candidate crossing/clearance;
- fuzzy skin disabled for target;
- no ambiguous mesh section.

## 11. Printable process/execution gates

Initial physical v1 requires:
- one tool / one filament execution context;
- relative E;
- firmware retract off;
- zero ordinary restart extra;
- unambiguous positive saved retraction at insertion boundary;
- known effective retract/deretract speeds;
- line numbering/checksum off;
- arc fitting off;
- adaptive pressure advance off;
- filament adaptive volumetric speed off;
- extrusion-role-change custom G-code empty;
- spiral vase off;
- scarf/sloped seam off;
- unsupported ironing off;
- support/raft off;
- no classic post_process;
- no other slicing-pipeline capability besides this plugin;
- verbose G-code/comments enabled for initial physical fixture;
- supported motion-neutral layer-change custom G-code;
- normal non-calibration print;
- fresh current-session plan;
- positive active Z hop;
- printable-height margin;
- exact golden-fixtured profile family;
- source working-file identity remains unchanged during the attempt.

The plugin reports unmet settings but never silently changes them.

## 12. Seam matching

Normal nonzero Orca seam gap is supported.

Final structural matcher handles:
- cyclic seam start;
- seam split;
- collinear subdivision;
- one expected contiguous seam-gap clip;
- final translation and formatter quantization.

Raw ordered path equality is not sufficient.

Exactly one structural match is required.

## 14. Execution-frame mapping

Plan geometry is not machine G-code geometry.

Final matcher derives one constant translation (dx, dy, dz) from multiple references.

Reject non-constant mapping, rotation, scale, shear, or ambiguity.

Only G-code code applies machine translation.

## 15. Orca formatter parity

For the audited compatibility descriptor:
- XYZ/F = 3 decimals;
- E = 5 decimals;
- midpoint rounding = C++ std::round, half away from zero.

Do not use Python default round for parity.

Unknown formatter contract => no injection.

## 16. Speed / volumetric limit

Candidate speed is bounded by:
- resolved outer-wall speed;
- fixed filament max volumetric speed / q_cmd;
- optional lower plugin cap;
- fixture-required lower matched structural-wall feed.

Filament adaptive volumetric speed is disabled in v1.

## 17. Retraction/state behavior

Parser reconstructs actual final-G-code state.

Candidate cycle preserves saved relative-E retraction exactly:
- travel while saved-retracted;
- temporary exact unretract at candidate;
- print;
- exact re-retract;
- finish in original saved state.

The plugin does not reproduce wipe for its temporary cycle.

Unknown state => Skipped.

## 18. Safe-ceiling travel

All plugin-generated non-extruding XY travel occurs at Zsafe.

Zsafe uses:
- actual parsed saved Z;
- target upper machine Z;
- positive active Z hop.

Zsafe must remain inside active tool printable-height limit.

## 19. Final chronological tool-clearance validation

Every physical candidate requires one final chronological swept-volume validation covering:
- all plugin-generated candidate/travel/return motions;
- unchanged original Orca motion after each insertion point.

The validator advances printed material in execution order and distinguishes final-surface material from material that actually exists at that moment.

Use a versioned ToolClearanceProfile whose dimensions come from documented manufacturer geometry, measurement, or another explicit physical source.

Validate swept tool keep-out against chronological printed material for:
- plugin vertical raise/descent;
- plugin Zsafe travel;
- plugin candidate extrusion body clearance;
- later plugin candidate motion versus earlier candidate material;
- downstream travel;
- downstream extrusion including ZAA lowered paths;
- relevant pure-Z and modal/motion commands.

Unknown motion or insufficient clearance => Skipped.

No ToolClearanceProfile => analysis/preview only.

v1 does not replan unsafe plugin or later original motion in postprocess; validation only accepts or rejects.

## 20. File processing

Postprocess is:
- binary-line streaming;
- byte-preserving for all untouched original content;
- parser/state-machine based;
- validation-first;
- idempotent;
- temp-file based;
- sanity-checked;
- atomic;
- all-or-nothing;
- line-ending preserving;
- original file mode/permissions preserving where required by the supported platform workflow.

Expected unsupported/validation condition:
- stable internal reason;
- PluginResult.Skipped;
- original file unchanged byte-for-byte on failure;
- source identity/digest revalidated across passes;
- PluginSettingsFingerprint rechecked immediately before commit.

Successful injection or validated already-injected no-op:
- Success.

## 21. Preview

Orca standard preview is pre-postprocess.

Plugin preview uses the exact immutable plan and separate runtime status.

It shows unmet injection gates explicitly.

## 22. Packaging

Target pure-Python wheel.

No native/custom-Orca dependency in v1.

## 23. Golden fixture requirement

No printer/profile family becomes injectable until fixtures record:
- exact Orca version/commit;
- exact machine/process/filament identity;
- resolved semantic config;
- plugin settings fingerprint;
- ToolClearanceProfile id/evidence;
- source G-code;
- final structural deposition/seam-gap support expectations;
- actual matched final wall feed expectations;
- parser/modal/retraction state, including M220/M221/G92 semantics;
- structural matching;
- execution-frame translation;
- quantization;
- speed/Zsafe bounds;
- chronological plugin/downstream tool-clearance expectations;
- candidate support dependency/order expectations;
- expected injected output;
- idempotence;
- timelapse/wrapping/wipe/exclude-object gate fixtures;
- attempt concurrency/source-TOCTOU fixtures;
- representative failure cases.

No fixture => analysis-only.

## 24. Compatibility default

Unknown Orca source/API, profile, config, modal state, custom code, physical tool envelope, source orientation/material side, coordinate mapping, formatter behavior, binary token/newline semantics, filesystem atomic-replace behavior, or machine limit => injection disabled.

Never best-effort mutate.
